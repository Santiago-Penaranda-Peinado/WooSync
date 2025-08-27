# src/app_gui.py

import customtkinter
from tkinter import filedialog, simpledialog
import pandas as pd
import os
import threading
from api_client import WooCommerceAPI

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        # ... (el resto de __init__ sin cambios)
        self.title("WooSync - Sincronizador para WooCommerce")
        self.geometry("700x750")
        self.api_client = None
        self.csv_path = ""
        self.image_folder_path = ""
        self.mapping_widgets = []
        self.is_syncing = False
        self.login_frame = customtkinter.CTkFrame(self)
        self.main_frame = customtkinter.CTkFrame(self)
        self.create_login_widgets()
        self.login_frame.pack(padx=20, pady=20, fill="both", expand=True)

    # ... (create_login_widgets y connect_to_store no tienen cambios)
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
        template_button = customtkinter.CTkButton(template_frame, text="Descargar Plantilla Simplificada", command=self.download_template)
        template_button.pack(pady=5)
        upload_frame = customtkinter.CTkFrame(file_frame)
        upload_frame.pack(side="left", padx=20, pady=10, expand=True)
        upload_label = customtkinter.CTkLabel(upload_frame, text="¿Ya tienes un archivo?")
        upload_label.pack()
        csv_button = customtkinter.CTkButton(upload_frame, text="Seleccionar Archivo CSV", command=self.select_csv_file)
        csv_button.pack(pady=5)
        self.image_folder_label = customtkinter.CTkLabel(self.main_frame, text="Paso 2: Selecciona la carpeta de imágenes")
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
        self.warning_label = customtkinter.CTkLabel(self.main_frame, text="", text_color="orange")
        self.warning_label.pack(pady=5, padx=10)
        sync_frame = customtkinter.CTkFrame(self.main_frame)
        sync_frame.pack(pady=10, padx=10, fill="x")
        self.start_sync_button = customtkinter.CTkButton(sync_frame, text="Iniciar Sincronización", command=self.start_synchronization_thread)
        self.start_sync_button.pack(pady=10)
        self.log_textbox = customtkinter.CTkTextbox(self.main_frame, height=150)
        self.log_textbox.pack(pady=10, padx=10, fill="both", expand=True)

    # ... (select_csv_file, select_image_folder, create_mapping_widgets, presets y otros no cambian)
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
            self.log(f"Error al leer el CSV: {e}")

    def select_image_folder(self):
        folderpath = filedialog.askdirectory()
        if not folderpath: return
        self.image_folder_path = folderpath
        self.image_folder_label.configure(text=f"Carpeta: {folderpath}")
        
    def create_mapping_widgets(self, csv_columns):
        for widget in self.mapping_frame.winfo_children(): widget.destroy()
        self.mapping_widgets = []
        self.woocommerce_fields = [ "No importar", "ID", "Name", "SKU", "Regular price", "Sale price", "Short description", "Description", "Stock", "Categories", "Images" ]
        self.mapping_frame.configure(label_text=f"Paso 3: Mapea las {len(csv_columns)} columnas")
        for column in csv_columns:
            row_frame = customtkinter.CTkFrame(self.mapping_frame)
            row_frame.pack(fill="x", padx=5, pady=5)
            label = customtkinter.CTkLabel(row_frame, text=column, width=200, anchor="w")
            label.pack(side="left", padx=10)
            combo = customtkinter.CTkComboBox(row_frame, values=self.woocommerce_fields)
            combo.pack(side="right", padx=10)
            self.auto_guess_mapping(column, combo)
            self.mapping_widgets.append({'csv_column': column, 'combo': combo})

    def auto_guess_mapping(self, column_name, combobox_widget):
        best_guess = "No importar"
        column_lower = column_name.lower().replace("_", " ").replace("-", " ")
        for field in self.woocommerce_fields:
            if field.lower() == column_lower:
                best_guess = field
                break
            if field.lower() in column_lower and len(field) > 2:
                best_guess = field
        combobox_widget.set(best_guess)
        
    def apply_basic_mapping(self):
        essential_fields = ["Name", "SKU", "Regular price", "Images", "Short description", "Description"]
        self.log("Aplicando plantilla de mapeo 'Básico'...")
        self.clear_mapping()
        for essential in essential_fields:
            for item in self.mapping_widgets:
                if essential.lower() in item['csv_column'].lower():
                    item['combo'].set(essential)
                    break
                    
    def clear_mapping(self):
        self.log("Limpiando todo el mapeo...")
        for item in self.mapping_widgets: item['combo'].set("No importar")
        
    def apply_full_mapping(self):
        self.log("Intentando mapear todas las columnas automáticamente...")
        for item in self.mapping_widgets:
            self.auto_guess_mapping(item['csv_column'], item['combo'])

    def download_template(self):
        self.log("Creando plantilla simplificada...")
        template_headers = {'SKU': ['SKU-EJEMPLO-1', 'SKU-EJEMPLO-2'], 'Name': ['Nombre del Producto de Ejemplo 1', 'Nombre del Producto de Ejemplo 2'], 'Regular price': [99.99, 150.00], 'Short description': ['Descripción corta y atractiva aquí.', 'Otra descripción corta.'], 'Description': ['Descripción larga y detallada del producto aquí.', 'Más detalles sobre el producto 2.'], 'Images': ['nombre-de-imagen1.jpg', 'nombre-de-imagen2.jpg']}
        df = pd.DataFrame(template_headers)
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Archivos CSV", "*.csv")], title="Guardar plantilla como...", initialfile="plantilla_productos_nuevos.csv")
        if filepath:
            try:
                df.to_csv(filepath, index=False, encoding='utf-8')
                self.log(f"Plantilla guardada exitosamente en: {filepath}")
            except Exception as e:
                self.log(f"Error al guardar la plantilla: {e}")

    def on_sync_mode_change(self):
        if self.sync_mode.get() == "mirror":
            self.warning_label.configure(text="¡ADVERTENCIA! El Modo Espejo eliminará permanentemente de la tienda\n"
                                               "todos los productos que NO estén en tu archivo CSV.")
            self.start_sync_button.configure(fg_color="red", hover_color="darkred")
        else:
            self.warning_label.configure(text="")
            self.start_sync_button.configure(fg_color=("#3B8ED0", "#1F6AA5"), hover_color=("#36719F", "#144870"))

    def log(self, message):
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")
        self.update_idletasks()

    def start_synchronization_thread(self):
        if self.is_syncing:
            self.log("Ya hay una sincronización en proceso.")
            return
        sync_thread = threading.Thread(target=self.start_synchronization)
        sync_thread.start()

    # --- FUNCIÓN CORREGIDA ---
    def start_synchronization(self):
        self.is_syncing = True
        self.start_sync_button.configure(state="disabled", text="Sincronizando...")
        self.log_textbox.delete("1.0", "end")
        self.log("================================")
        self.log(f"INICIANDO SINCRONIZACIÓN EN MODO: {self.sync_mode.get().upper()}")
        self.log("================================")
        
        if not self.csv_path or not self.image_folder_path:
            self.log("Error: Debes seleccionar un archivo CSV y una carpeta de imágenes.")
            self.is_syncing = False; self.start_sync_button.configure(state="normal", text="Iniciar Sincronización"); return
        
        user_mapping = {item['combo'].get().lower().replace(" ", "_"): item['csv_column'] for item in self.mapping_widgets if item['combo'].get() != "No importar"}
        if 'sku' not in user_mapping:
            self.log("Error: El campo 'SKU' es obligatorio."); self.is_syncing = False; self.start_sync_button.configure(state="normal", text="Iniciar Sincronización"); return

        try:
            df = pd.read_csv(self.csv_path, dtype=str).fillna('')
            self.log(f"Archivo CSV cargado. Contiene {len(df)} productos.")
        except Exception as e:
            self.log(f"Error fatal al leer el CSV: {e}"); self.is_syncing = False; self.start_sync_button.configure(state="normal", text="Iniciar Sincronización"); return

        if self.sync_mode.get() == "mirror":
            self.log("Modo Espejo activado. Obteniendo datos de la tienda...")
            csv_skus = set(df[user_mapping['sku']].dropna().unique())
            store_products = self.api_client.get_all_products()
            if store_products is None:
                self.log("Error: No se pudieron obtener los productos de la tienda."); self.is_syncing = False; self.start_sync_button.configure(state="normal", text="Iniciar Sincronización"); return
            
            store_skus = {prod['sku']: prod['id'] for prod in store_products if prod['sku']}
            skus_to_delete = set(store_skus.keys()) - csv_skus

            if skus_to_delete:
                # CORRECCIÓN: Llamamos al diálogo de forma segura usando self.after
                self.after(0, self.ask_for_deletion_confirmation, skus_to_delete, store_skus)
                return # Detenemos la ejecución aquí; el resto se reanudará después de la confirmación
            else:
                self.log("No se encontraron productos para eliminar.")
        
        # Si no estamos en modo espejo o no hay nada que borrar, continuamos directamente
        self.process_products(df, user_mapping)

    def ask_for_deletion_confirmation(self, skus_to_delete, store_skus):
        """Muestra el diálogo de confirmación en el hilo principal."""
        confirmation_text = simpledialog.askstring(
            "CONFIRMACIÓN DE ELIMINACIÓN PERMANENTE",
            f"Estás a punto de ELIMINAR PERMANENTEMENTE {len(skus_to_delete)} productos de tu tienda.\n"
            "Esta acción no se puede deshacer.\n\n"
            "Para confirmar, escribe la palabra 'ELIMINAR' en mayúsculas:"
        )
        
        if confirmation_text == "ELIMINAR":
            self.log(f"Confirmación recibida. Eliminando {len(skus_to_delete)} productos...")
            for sku in skus_to_delete:
                product_id = store_skus[sku]
                self.log(f"  -> Eliminando producto SKU: {sku} (ID: {product_id})")
                if not self.api_client.delete_product(product_id): self.log(f"  -> ERROR al eliminar SKU: {sku}")
        else:
            self.log("Eliminación cancelada por el usuario.")
        
        # Ahora, continuamos con el resto de la sincronización
        user_mapping = {item['combo'].get().lower().replace(" ", "_"): item['csv_column'] for item in self.mapping_widgets if item['combo'].get() != "No importar"}
        df = pd.read_csv(self.csv_path, dtype=str).fillna('')
        self.process_products(df, user_mapping)

    def process_products(self, df, user_mapping):
        """Bucle principal que crea y actualiza productos."""
        for index, row in df.iterrows():
            sku = row.get(user_mapping['sku'], '').strip()
            product_name = row.get(user_mapping.get('name', ''), sku)
            if not sku: self.log(f"Fila {index + 2}: Omitida (SKU vacío)."); continue

            self.log(f"--- Procesando: {product_name} (SKU: {sku}) ---")
            
            # CORRECCIÓN: Excluimos 'id' del payload
            product_data = {'type': 'simple'}
            for woo_field, csv_column in user_mapping.items():
                if woo_field not in ['images', 'sku', 'id']: # Excluimos 'id' aquí
                    product_data[woo_field] = row.get(csv_column, '')

            if 'images' in user_mapping:
                image_cell = row.get(user_mapping['images'], '')
                if image_cell and not image_cell.lower().startswith('http'):
                    image_path = os.path.join(self.image_folder_path, image_cell)
                    uploaded_image = self.api_client.upload_image(image_path, image_cell)
                    if uploaded_image: product_data['images'] = [{'id': uploaded_image['id']}]
                else: self.log("  -> Imagen es URL o está vacía. Se ignora.")
            
            existing_product = self.api_client.get_product_by_sku(sku)
            if existing_product:
                result = self.api_client.update_product(existing_product['id'], product_data)
                if result: self.log(f"  -> ÉXITO: Producto ID {existing_product['id']} actualizado.")
            else:
                product_data['sku'] = sku
                result = self.api_client.create_product(product_data)
                if result: self.log(f"  -> ÉXITO: Producto creado con ID {result['id']}.")

        self.log("================================")
        self.log("SINCRONIZACIÓN COMPLETADA")
        self.log("================================")
        self.is_syncing = False
        self.start_sync_button.configure(state="normal", text="Iniciar Sincronización")
        self.on_sync_mode_change()


if __name__ == "__main__":
    import os
    app = App()
    app.mainloop()