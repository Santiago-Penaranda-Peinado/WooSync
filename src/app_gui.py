# src/app_gui.py

import customtkinter
from tkinter import filedialog, simpledialog
import pandas as pd
import os
import threading
from api_client import WooCommerceAPI
from queue import Queue

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

def chunks(lst, n):
    """Divide una lista en trozos de tamaño n."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("WooSync v2.1 (Optimized) - Sincronizador para WooCommerce")
        self.geometry("800x800")
        self.api_client = None
        self.csv_path = ""
        self.image_folder_path = ""
        self.mapping_widgets = []
        self.is_syncing = False
        self.log_queue = Queue()
        self.API_FIELD_MAP = {"ID": "id", "Name": "name", "SKU": "sku", "Regular price": "regular_price", "Sale price": "sale_price", "Description": "description", "Short description": "short_description", "Stock": "stock_quantity", "Weight": "weight", "Length": "length", "Width": "width", "Height": "height", "Categories": "categories", "Tags": "tags", "Images": "images", "Purchase note": "purchase_note", "Menu order": "menu_order"}
        self.login_frame = customtkinter.CTkFrame(self)
        self.main_frame = customtkinter.CTkFrame(self)
        self.create_login_widgets()
        self.login_frame.pack(padx=20, pady=20, fill="both", expand=True)

    def create_login_widgets(self):
        welcome_label = customtkinter.CTkLabel(self.login_frame, text="Conectar a la Tienda", font=("Arial", 20))
        welcome_label.pack(pady=20)
        self.url_entry = customtkinter.CTkEntry(self.login_frame, placeholder_text="URL de la tienda (https://...)")
        self.url_entry.pack(pady=10, padx=20, fill="x")
        self.user_entry = customtkinter.CTkEntry(self.login_frame, placeholder_text="Nombre de Usuario de WordPress")
        self.user_entry.pack(pady=10, padx=20, fill="x")
        self.password_entry = customtkinter.CTkEntry(self.login_frame, placeholder_text="Contraseña de Aplicación", show="*")
        self.password_entry.pack(pady=10, padx=20, fill="x")
        connect_button = customtkinter.CTkButton(self.login_frame, text="Conectar", command=self.connect_to_store)
        connect_button.pack(pady=20)
        self.status_label = customtkinter.CTkLabel(self.login_frame, text="", font=("Arial", 12))
        self.status_label.pack(pady=10)

    def connect_to_store(self):
        store_url = self.url_entry.get().strip().rstrip('/')
        username = self.user_entry.get()
        password = self.password_entry.get()
        if not all([store_url, username, password]):
            self.status_label.configure(text="Todos los campos son obligatorios.", text_color="orange")
            return
        self.status_label.configure(text="Conectando...", text_color="gray")
        self.update_idletasks()
        self.api_client = WooCommerceAPI(store_url, username, password)
        if self.api_client.check_connection():
            self.login_frame.pack_forget()
            self.create_main_widgets()
            self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        else:
            self.api_client = None
            self.status_label.configure(text="Error: Revisa la URL y las credenciales.", text_color="red")
    
    def create_main_widgets(self):
        file_frame = customtkinter.CTkFrame(self.main_frame)
        file_frame.pack(pady=10, padx=10, fill="x")
        template_frame = customtkinter.CTkFrame(file_frame)
        template_frame.pack(side="left", padx=20, pady=10, expand=True)
        template_label = customtkinter.CTkLabel(template_frame, text="¿Empezando desde cero?")
        template_label.pack()
        template_button = customtkinter.CTkButton(template_frame, text="Descargar Plantilla Mejorada", command=self.download_template)
        template_button.pack(pady=5)
        upload_frame = customtkinter.CTkFrame(file_frame)
        upload_frame.pack(side="left", padx=20, pady=10, expand=True)
        upload_label = customtkinter.CTkLabel(upload_frame, text="¿Ya tienes un archivo?")
        upload_label.pack()
        csv_button = customtkinter.CTkButton(upload_frame, text="Seleccionar Archivo CSV", command=self.select_csv_file)
        csv_button.pack(pady=5)
        self.image_folder_label = customtkinter.CTkLabel(self.main_frame, text="Paso 2: Selecciona la carpeta de imágenes (Opcional)")
        self.image_folder_label.pack(pady=10)
        image_button = customtkinter.CTkButton(self.main_frame, text="Seleccionar Carpeta de Imágenes", command=self.select_image_folder)
        image_button.pack(pady=5)
        presets_frame = customtkinter.CTkFrame(self.main_frame)
        presets_frame.pack(pady=5, padx=10, fill="x")
        presets_label = customtkinter.CTkLabel(presets_frame, text="Plantillas de Mapeo Rápido:")
        presets_label.pack(side="left", padx=10)
        basic_button = customtkinter.CTkButton(presets_frame, text="Básico", command=self.apply_basic_mapping)
        basic_button.pack(side="left", padx=5)
        full_button = customtkinter.CTkButton(presets_frame, text="Mapear Todo", command=self.apply_full_mapping)
        full_button.pack(side="left", padx=5)
        clear_button = customtkinter.CTkButton(presets_frame, text="Limpiar Todo", command=self.clear_mapping)
        clear_button.pack(side="left", padx=5)
        self.mapping_frame = customtkinter.CTkScrollableFrame(self.main_frame, label_text="Paso 3: Mapea las columnas")
        self.mapping_frame.pack(pady=10, padx=10, fill="both", expand=True)
        sync_mode_frame = customtkinter.CTkFrame(self.main_frame)
        sync_mode_frame.pack(pady=10, padx=10, fill="x")
        mode_label = customtkinter.CTkLabel(sync_mode_frame, text="Modo de Sincronización:")
        mode_label.pack(side="left", padx=10)
        self.sync_mode = customtkinter.StringVar(value="safe")
        safe_radio = customtkinter.CTkRadioButton(sync_mode_frame, text="Modo Seguro (Crear y Actualizar)", variable=self.sync_mode, value="safe", command=self.on_sync_mode_change)
        safe_radio.pack(side="left", padx=5)
        mirror_radio = customtkinter.CTkRadioButton(sync_mode_frame, text="Modo Espejo (Sincronización Completa)", variable=self.sync_mode, value="mirror", command=self.on_sync_mode_change)
        mirror_radio.pack(side="left", padx=5)
        
        # Implementación solicitada: Checkbox para Modo Compatible
        self.compatibility_mode_var = customtkinter.StringVar(value="off")
        self.compatibility_mode_check = customtkinter.CTkCheckBox(sync_mode_frame, text="Modo Compatible (Lento y Seguro)",
                                                                  variable=self.compatibility_mode_var, onvalue="on", offvalue="off")
        self.compatibility_mode_check.pack(side="left", padx=10)
        
        self.warning_label = customtkinter.CTkLabel(self.main_frame, text="", text_color="orange")
        self.warning_label.pack(pady=5, padx=10)
        sync_frame = customtkinter.CTkFrame(self.main_frame)
        sync_frame.pack(pady=10, padx=10, fill="x")
        self.start_sync_button = customtkinter.CTkButton(sync_frame, text="Iniciar Sincronización", command=self.start_synchronization_thread)
        self.start_sync_button.pack(pady=10)
        self.log_textbox = customtkinter.CTkTextbox(self.main_frame, height=200)
        self.log_textbox.pack(pady=10, padx=10, fill="both", expand=True)

    def select_csv_file(self):
        filepath = filedialog.askopenfilename(filetypes=(("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")))
        if not filepath: return
        self.csv_path = filepath
        filename = os.path.basename(filepath)
        upload_label = self.main_frame.winfo_children()[0].winfo_children()[1].winfo_children()[0]
        upload_label.configure(text=f"Archivo: {filename}")
        try:
            df_headers = pd.read_csv(self.csv_path, nrows=0).columns.tolist()
            self.create_mapping_widgets(df_headers)
        except Exception as e:
            self.log("ERROR", f"Error al leer el CSV: {e}")

    def select_image_folder(self):
        folderpath = filedialog.askdirectory()
        if not folderpath: return
        self.image_folder_path = folderpath
        self.image_folder_label.configure(text=f"Carpeta: {folderpath}")
        
    def create_mapping_widgets(self, csv_columns):
        for widget in self.mapping_frame.winfo_children(): widget.destroy()
        self.mapping_widgets = []
        self.woocommerce_fields = ["No importar", "Name", "SKU", "Regular price", "Sale price", "Description", "Short description", "Stock", "Weight", "Length", "Width", "Height", "Categories", "Tags", "Images", "Purchase note", "Menu order", "meta: [Escribe el nombre del campo]"]
        self.mapping_frame.configure(label_text=f"Paso 3: Mapea las {len(csv_columns)} columnas")
        for column in csv_columns:
            row_frame = customtkinter.CTkFrame(self.mapping_frame)
            row_frame.pack(fill="x", padx=5, pady=5)
            label = customtkinter.CTkLabel(row_frame, text=column, width=250, anchor="w")
            label.pack(side="left", padx=10)
            combo = customtkinter.CTkComboBox(row_frame, values=self.woocommerce_fields, width=250)
            combo.pack(side="right", padx=10, expand=True, fill="x")
            self.auto_guess_mapping(column, combo)
            self.mapping_widgets.append({'csv_column': column, 'combo': combo})

    def auto_guess_mapping(self, column_name, combobox_widget):
        if "Unnamed:" in column_name:
            combobox_widget.set("No importar")
            return
        column_lower = column_name.lower().replace("_", " ").replace("-", " ").strip()
        for field in self.woocommerce_fields:
            if field.lower() == column_lower:
                combobox_widget.set(field)
                return
        best_guess = "No importar"
        if "tag" in column_lower or "etiqueta" in column_lower: best_guess = "Tags"
        elif "categor" in column_lower: best_guess = "Categories"
        elif "peso" in column_lower or "weight" in column_lower: best_guess = "Weight"
        elif "ancho" in column_lower or "width" in column_lower: best_guess = "Width"
        combobox_widget.set(best_guess)
        
    def apply_basic_mapping(self):
        essential_fields = ["Name", "SKU", "Regular price", "Images", "Short description", "Description", "Categories"]
        self.log("INFO", "Aplicando plantilla de mapeo 'Básico'...")
        self.clear_mapping()
        for essential in essential_fields:
            for item in self.mapping_widgets:
                if essential.lower() in item['csv_column'].lower():
                    item['combo'].set(essential)
                    break
                    
    def clear_mapping(self):
        self.log("INFO", "Limpiando todo el mapeo...")
        for item in self.mapping_widgets: item['combo'].set("No importar")
        
    def apply_full_mapping(self):
        self.log("INFO", "Intentando mapear todas las columnas automáticamente...")
        for item in self.mapping_widgets:
            self.auto_guess_mapping(item['csv_column'], item['combo'])

    def download_template(self):
        self.log("INFO", "Creando plantilla mejorada...")
        template_headers = {'SKU': ['SKU-EJEMPLO-1'], 'Name': ['Producto de Ejemplo'], 'Regular price': [99.99], 'Sale price': [79.99], 'Short description': ['Descripción corta y atractiva.'], 'Description': ['Descripción completa del producto.'], 'Images': ['imagen1.jpg, imagen2.png'], 'Categories': ['Categoría Principal, Subcategoría'], 'Tags': ['tag1, tag2, tag3'], 'Stock': [100], 'Weight': [0.5], 'Length': [20], 'Width': [15], 'Height': [10]}
        df = pd.DataFrame(template_headers)
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Archivos CSV", "*.csv")], title="Guardar plantilla como...", initialfile="plantilla_productos_avanzada.csv")
        if filepath:
            try:
                df.to_csv(filepath, index=False, encoding='utf-8')
                self.log("SUCCESS", f"Plantilla guardada exitosamente en: {filepath}")
            except Exception as e:
                self.log("ERROR", f"Error al guardar la plantilla: {e}")

    def on_sync_mode_change(self):
        if self.sync_mode.get() == "mirror":
            self.warning_label.configure(text="¡ADVERTENCIA! El Modo Espejo eliminará permanentemente de la tienda\n"
                                               "todos los productos que NO estén en tu archivo CSV.")
            self.start_sync_button.configure(fg_color="red", hover_color="darkred")
        else:
            self.warning_label.configure(text="")
            self.start_sync_button.configure(fg_color=("#3B8ED0", "#1F6AA5"), hover_color=("#36719F", "#144870"))

    def log(self, level, message):
        self.log_queue.put(f"[{level}] {message}")

    def process_log_queue(self):
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.log_textbox.insert("end", message + "\n")
            self.log_textbox.see("end")
        self.after(100, self.process_log_queue)

    def start_synchronization_thread(self):
        if not self.is_syncing:
            thread = threading.Thread(target=self.start_synchronization)
            thread.daemon = True
            thread.start()

    def finalize_sync(self, success=True):
        """Función centralizada para terminar la sincronización y reactivar la UI."""
        if success:
            self.log("SUCCESS", "================================")
            self.log("SUCCESS", "SINCRONIZACIÓN COMPLETADA")
            self.log("SUCCESS", "================================")
        else:
            self.log("ERROR", "================================")
            self.log("ERROR", "SINCRONIZACIÓN ABORTADA POR ERRORES")
            self.log("ERROR", "================================")
        
        self.is_syncing = False
        self.start_sync_button.configure(state="normal", text="Iniciar Sincronización")
        self.on_sync_mode_change()

    def start_synchronization(self):
        """Orquesta el proceso de sincronización, manejando hilos y diálogos."""
        self.is_syncing = True
        self.start_sync_button.configure(state="disabled", text="Sincronizando...")
        self.log_textbox.delete("1.0", "end")
        self.log("INFO", f"INICIANDO SINCRONIZACIÓN EN MODO: {self.sync_mode.get().upper()}")
        
        # --- Validaciones y carga de CSV ---
        if not self.csv_path:
            self.log("ERROR", "Debes seleccionar un archivo CSV."); self.finalize_sync(success=False); return
        user_mapping = {item['combo'].get(): item['csv_column'] for item in self.mapping_widgets if item['combo'].get() != "No importar"}
        if 'SKU' not in user_mapping:
            self.log("ERROR", "El campo 'SKU' es obligatorio."); self.finalize_sync(success=False); return

        try:
            df = pd.read_csv(self.csv_path, dtype=str).fillna('')
            self.log("INFO", f"Archivo CSV cargado. Contiene {len(df)} productos.")
        except Exception as e:
            self.log("ERROR", f"Error fatal al leer el CSV: {e}"); self.finalize_sync(success=False); return

        # --- Obtener productos de la tienda ---
        self.log("INFO", "Obteniendo inventario actual de la tienda...")
        store_products = self.api_client.get_all_products()
        if 'error' in store_products:
            self.log("ERROR", store_products['error']); self.finalize_sync(success=False); return
        
        store_sku_to_id_map = {prod['sku']: prod['id'] for prod in store_products if prod.get('sku')}
        self.log("INFO", f"Se encontraron {len(store_sku_to_id_map)} productos con SKU en la tienda.")

        # --- Lógica Modo Espejo ---
        if self.sync_mode.get() == "mirror":
            csv_skus = set(df[user_mapping['SKU']].dropna().unique())
            skus_to_delete = set(store_sku_to_id_map.keys()) - csv_skus

            if skus_to_delete:
                self.after(0, self.ask_for_deletion_confirmation, list(skus_to_delete), store_sku_to_id_map, df, user_mapping)
                return # Detenemos aquí, el resto se ejecuta después de la confirmación
        
        # Si es Modo Seguro, o Modo Espejo sin nada que borrar, procesamos directamente
        if self.compatibility_mode_var.get() == "on":
            self.log("INFO", "Iniciando procesamiento en Modo Compatible (uno por uno)...")
            self.process_products_one_by_one(df, user_mapping, store_sku_to_id_map)
        else:
            self.log("INFO", "Iniciando procesamiento en Modo Rápido (por lotes)...")
            self.process_products_batch(df, user_mapping, store_sku_to_id_map)
        self.finalize_sync()

    def ask_for_deletion_confirmation(self, skus_to_delete, store_sku_to_id_map, df, user_mapping):
        """Muestra el diálogo y luego continúa el proceso en un nuevo hilo."""
        confirmation_text = simpledialog.askstring("CONFIRMACIÓN DE ELIMINACIÓN PERMANENTE", f"Estás a punto de ELIMINAR PERMANENTEMENTE {len(skus_to_delete)} productos.\nEsta acción no se puede deshacer.\n\nPara confirmar, escribe 'ELIMINAR' en mayúsculas:")
        
        # Iniciamos el resto del proceso en un nuevo hilo para no bloquear la UI
        thread = threading.Thread(target=self.continue_mirror_sync, args=(confirmation_text, skus_to_delete, store_sku_to_id_map, df, user_mapping))
        thread.daemon = True
        thread.start()

    def continue_mirror_sync(self, confirmation, skus_to_delete, store_sku_to_id_map, df, user_mapping):
        """Se ejecuta después de la confirmación del usuario para terminar el Modo Espejo."""
        if confirmation == "ELIMINAR":
            self.log("INFO", f"Confirmación recibida. Eliminando {len(skus_to_delete)} productos por lotes...")
            ids_to_delete = [store_sku_to_id_map[sku] for sku in skus_to_delete]
            
            # --- BORRADO POR LOTES ---
            for chunk in chunks(ids_to_delete, 50):
                self.log("INFO", f"Enviando lote de ELIMINACIÓN de {len(chunk)} productos...")
                result = self.api_client.process_batch({'delete': chunk})
                if result and 'error' in result:
                    self.log("ERROR", result['error'])
        else:
            self.log("WARN", "Eliminación cancelada por el usuario.")
            
        # Continuamos con la creación/actualización
        if self.compatibility_mode_var.get() == "on":
            self.log("INFO", "Iniciando procesamiento en Modo Compatible (uno por uno)...")
            self.process_products_one_by_one(df, user_mapping, store_sku_to_id_map)
        else:
            self.log("INFO", "Iniciando procesamiento en Modo Rápido (por lotes)...")
            self.process_products_batch(df, user_mapping, store_sku_to_id_map)
        self.finalize_sync()

    def process_products_one_by_one(self, df, user_mapping, sku_to_id_map):
        """
        Procesa productos uno por uno. Es más lento pero más compatible con servidores limitados.
        """
        created_count = 0
        updated_count = 0
        total_products = len(df)

        for index, row in df.iterrows():
            sku = row.get(user_mapping['SKU'], '').strip()
            if not sku: 
                self.log("WARN", f"Fila {index + 2}: Omitida (SKU vacío).")
                continue
            
            # Preparar datos del producto (igual que en process_products_batch)
            product_data = {'type': 'simple'}
            meta_data = []
            dimensions = {}
            
            for gui_field, csv_column in user_mapping.items():
                value = row.get(csv_column, '')
                if pd.isna(value) or value == '': continue
                api_key = self.API_FIELD_MAP.get(gui_field)
                if gui_field.startswith("meta:"):
                    meta_key = gui_field.split(":", 1)[1].strip()
                    if meta_key: meta_data.append({'key': meta_key, 'value': value})
                elif api_key in ['categories', 'tags']:
                    if isinstance(value, str):
                        product_data[api_key] = [{'name': item.strip()} for item in value.split(',')]
                    elif isinstance(value, list):
                        product_data[api_key] = [{'name': item} for item in value]
                elif api_key in ['length', 'width', 'height']:
                    try: 
                        dimensions[api_key] = str(float(value))
                    except (ValueError, TypeError): 
                        dimensions[api_key] = '0'
                elif api_key == 'images':
                    if not self.image_folder_path: continue
                    image_ids = []
                    for img_name in value.split(','):
                        img_name = img_name.strip()
                        if img_name and not img_name.lower().startswith('http'):
                            image_path = os.path.join(self.image_folder_path, img_name)
                            uploaded = self.api_client.upload_image(image_path, img_name)
                            if uploaded and 'id' in uploaded: 
                                image_ids.append({'id': uploaded['id']})
                            elif uploaded and 'error' in uploaded: 
                                self.log("ERROR", f"Subiendo '{img_name}': {uploaded['error']}")
                    if image_ids: 
                        product_data['images'] = image_ids
                elif api_key:
                    if api_key in ['regular_price', 'sale_price']:
                        try: 
                            product_data[api_key] = str(float(value))
                        except (ValueError, TypeError): 
                            product_data[api_key] = '0'
                    elif api_key == 'stock_quantity':
                        try: 
                            product_data[api_key] = int(float(value))
                        except (ValueError, TypeError): 
                            product_data[api_key] = 0
                    else: 
                        product_data[api_key] = value
            
            if dimensions: 
                product_data['dimensions'] = dimensions
            if meta_data: 
                product_data['meta_data'] = meta_data

            self.log("INFO", f"({index + 1}/{total_products}) Procesando SKU: {sku}")

            # Lógica de envío individual
            if sku in sku_to_id_map:
                product_id = sku_to_id_map[sku]
                result = self.api_client.update_product(product_id, product_data)
                if result and 'error' not in result: 
                    updated_count += 1
                    self.log("SUCCESS", f"Producto actualizado: {sku}")
                elif result and 'error' in result:
                    self.log("ERROR", f"Error al actualizar {sku}: {result['error']}")
            else:
                product_data['sku'] = sku
                result = self.api_client.create_product(product_data)
                if result and 'error' not in result: 
                    created_count += 1
                    self.log("SUCCESS", f"Producto creado: {sku}")
                elif result and 'error' in result:
                    self.log("ERROR", f"Error al crear {sku}: {result['error']}")
    
        self.log("INFO", f"Proceso completado. Creados: {created_count}, Actualizados: {updated_count}.")

    def process_products_batch(self, df, user_mapping, sku_to_id_map):
        products_to_create = []
        products_to_update = []
        
        for index, row in df.iterrows():
            sku = row.get(user_mapping['SKU'], '').strip()
            if not sku: 
                self.log("WARN", f"Fila {index + 2}: Omitida (SKU vacío).")
                continue
            
            product_data = {'type': 'simple'}
            meta_data = []
            dimensions = {}
            
            for gui_field, csv_column in user_mapping.items():
                value = row.get(csv_column, '')
                if pd.isna(value) or value == '': continue
                api_key = self.API_FIELD_MAP.get(gui_field)
                if gui_field.startswith("meta:"):
                    meta_key = gui_field.split(":", 1)[1].strip()
                    if meta_key: meta_data.append({'key': meta_key, 'value': value})
                elif api_key in ['categories', 'tags']:
                    if isinstance(value, str):
                        product_data[api_key] = [{'name': item.strip()} for item in value.split(',')]
                    elif isinstance(value, list):
                        product_data[api_key] = [{'name': item} for item in value]
                elif api_key in ['length', 'width', 'height']:
                    try: 
                        dimensions[api_key] = str(float(value))
                    except (ValueError, TypeError): 
                        dimensions[api_key] = '0'
                elif api_key == 'images':
                    if not self.image_folder_path: continue
                    image_ids = []
                    for img_name in value.split(','):
                        img_name = img_name.strip()
                        if img_name and not img_name.lower().startswith('http'):
                            image_path = os.path.join(self.image_folder_path, img_name)
                            uploaded = self.api_client.upload_image(image_path, img_name)
                            if uploaded and 'id' in uploaded: 
                                image_ids.append({'id': uploaded['id']})
                            elif uploaded and 'error' in uploaded: 
                                self.log("ERROR", f"Subiendo '{img_name}': {uploaded['error']}")
                    if image_ids: 
                        product_data['images'] = image_ids
                elif api_key:
                    if api_key in ['regular_price', 'sale_price']:
                        try: 
                            product_data[api_key] = str(float(value))
                        except (ValueError, TypeError): 
                            product_data[api_key] = '0'
                    elif api_key == 'stock_quantity':
                        try: 
                            product_data[api_key] = int(float(value))
                        except (ValueError, TypeError): 
                            product_data[api_key] = 0
                    else: 
                        product_data[api_key] = value
            
            if dimensions: 
                product_data['dimensions'] = dimensions
            if meta_data: 
                product_data['meta_data'] = meta_data
            
            if sku in sku_to_id_map:
                product_data['id'] = sku_to_id_map[sku]
                products_to_update.append(product_data)
            else:
                product_data['sku'] = sku
                products_to_create.append(product_data)
        
        self.log("INFO", f"Preparado para crear: {len(products_to_create)} productos.")
        self.log("INFO", f"Preparado para actualizar: {len(products_to_update)} productos.")
        
        for chunk in chunks(products_to_create, 50):
            self.log("INFO", f"Enviando lote de CREACIÓN de {len(chunk)} productos...")
            result = self.api_client.process_batch({'create': chunk})
            if result and 'error' in result: 
                self.log("ERROR", result['error'])
        
        for chunk in chunks(products_to_update, 50):
            self.log("INFO", f"Enviando lote de ACTUALIZACIÓN de {len(chunk)} productos...")
            result = self.api_client.process_batch({'update': chunk})
            if result and 'error' in result: 
                self.log("ERROR", result['error'])

if __name__ == "__main__":
    app = App()
    app.after(100, app.process_log_queue)
    app.mainloop()