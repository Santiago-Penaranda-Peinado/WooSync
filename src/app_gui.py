# src/app_gui.py

import customtkinter
from tkinter import filedialog
import pandas as pd
import os
import threading # <-- Importante para no congelar la interfaz
from api_client import WooCommerceAPI

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("WooSync - Sincronizador para WooCommerce")
        self.geometry("700x650")

        # --- Variables de estado ---
        self.api_client = None
        self.csv_path = ""
        self.image_folder_path = ""
        self.mapping_widgets = []
        self.is_syncing = False # Para evitar doble clic

        # --- Marcos (pantallas) ---
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
        store_url = self.url_entry.get()
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
        self.csv_path_label = customtkinter.CTkLabel(file_frame, text="Paso 1: Selecciona el archivo CSV")
        self.csv_path_label.pack()
        csv_button = customtkinter.CTkButton(file_frame, text="Seleccionar Archivo CSV", command=self.select_csv_file)
        csv_button.pack(pady=5)
        self.image_folder_label = customtkinter.CTkLabel(file_frame, text="Paso 2: Selecciona la carpeta de imágenes")
        self.image_folder_label.pack()
        image_button = customtkinter.CTkButton(file_frame, text="Seleccionar Carpeta de Imágenes", command=self.select_image_folder)
        image_button.pack(pady=5)
        presets_frame = customtkinter.CTkFrame(self.main_frame)
        presets_frame.pack(pady=10, padx=10, fill="x")
        presets_label = customtkinter.CTkLabel(presets_frame, text="Plantillas de Mapeo Rápido:")
        presets_label.pack(side="left", padx=10)
        basic_button = customtkinter.CTkButton(presets_frame, text="Básico", command=self.apply_basic_mapping)
        basic_button.pack(side="left", padx=5)
        clear_button = customtkinter.CTkButton(presets_frame, text="Limpiar Todo", command=self.clear_mapping)
        clear_button.pack(side="left", padx=5)
        self.mapping_frame = customtkinter.CTkScrollableFrame(self.main_frame, label_text="Paso 3: Mapea las columnas")
        self.mapping_frame.pack(pady=10, padx=10, fill="both", expand=True)
        sync_frame = customtkinter.CTkFrame(self.main_frame)
        sync_frame.pack(pady=10, padx=10, fill="x")
        self.start_sync_button = customtkinter.CTkButton(sync_frame, text="Iniciar Sincronización", command=self.start_synchronization_thread)
        self.start_sync_button.pack(pady=10)
        self.log_textbox = customtkinter.CTkTextbox(self.main_frame, height=150)
        self.log_textbox.pack(pady=10, padx=10, fill="x", expand=True)


    def select_csv_file(self):
       
        filepath = filedialog.askopenfilename(filetypes=(("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")))
        if not filepath: return
        self.csv_path = filepath
        filename = os.path.basename(filepath)
        self.csv_path_label.configure(text=f"Archivo: {filename}")
        try:
            df_headers = pd.read_csv(self.csv_path, nrows=0).columns.tolist()
            self.create_mapping_widgets(df_headers)
        except Exception as e:
            self.log_textbox.insert("end", f"Error al leer el CSV: {e}\n")

    def select_image_folder(self):
       
        folderpath = filedialog.askdirectory()
        if not folderpath: return
        self.image_folder_path = folderpath
        self.image_folder_label.configure(text=f"Carpeta: {folderpath}")
        
    def create_mapping_widgets(self, csv_columns):
       
        for widget in self.mapping_frame.winfo_children(): widget.destroy()
        self.mapping_widgets = []
        woocommerce_fields = [ "No importar", "ID", "Name", "SKU", "Regular price", "Sale price", "Short description", "Description", "Stock", "Categories", "Images" ]
        self.mapping_frame.configure(label_text=f"Paso 3: Mapea las {len(csv_columns)} columnas")
        for column in csv_columns:
            row_frame = customtkinter.CTkFrame(self.mapping_frame)
            row_frame.pack(fill="x", padx=5, pady=5)
            label = customtkinter.CTkLabel(row_frame, text=column, width=200, anchor="w")
            label.pack(side="left", padx=10)
            combo = customtkinter.CTkComboBox(row_frame, values=woocommerce_fields)
            combo.pack(side="right", padx=10)
            best_guess = "No importar"
            column_lower = column.lower().replace("_", " ").replace("-", " ")
            for field in woocommerce_fields:
                if field.lower() in column_lower:
                    best_guess = field
                    break
            combo.set(best_guess)
            self.mapping_widgets.append({'csv_column': column, 'combo': combo})

    def apply_basic_mapping(self):
       
        essential_fields = ["Name", "SKU", "Regular price", "Images"]
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

    def log(self, message):
        """Función centralizada para escribir en el cuadro de log."""
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end") # Auto-scroll hacia el final
        self.update_idletasks()

    def start_synchronization_thread(self):
        """Inicia el proceso de sincronización en un hilo separado para no congelar la GUI."""
        if self.is_syncing:
            self.log("Ya hay una sincronización en proceso.")
            return
        
        # Usamos un hilo para que la interfaz siga respondiendo
        sync_thread = threading.Thread(target=self.start_synchronization)
        sync_thread.start()

    def start_synchronization(self):
        """El motor de procesamiento, ahora conectado a la interfaz."""
        self.is_syncing = True
        self.start_sync_button.configure(state="disabled", text="Sincronizando...")
        self.log_textbox.delete("1.0", "end")
        self.log("================================")
        self.log("INICIANDO SINCRONIZACIÓN")
        self.log("================================")
        
        # 1. Validaciones
        if not self.csv_path or not self.image_folder_path:
            self.log("Error: Debes seleccionar un archivo CSV y una carpeta de imágenes.")
            self.is_syncing = False
            self.start_sync_button.configure(state="normal", text="Iniciar Sincronización")
            return

        # 2. Recopilar mapeo
        user_mapping = {item['combo'].get().lower().replace(" ", "_"): item['csv_column'] for item in self.mapping_widgets if item['combo'].get() != "No importar"}
        if 'sku' not in user_mapping:
            self.log("Error: El campo 'SKU' es obligatorio para la sincronización. Por favor, mapéalo.")
            self.is_syncing = False
            self.start_sync_button.configure(state="normal", text="Iniciar Sincronización")
            return

        # 3. Leer el CSV completo
        try:
            df = pd.read_csv(self.csv_path, dtype=str).fillna('')
            self.log(f"Archivo CSV cargado. Se procesarán {len(df)} productos.")
        except Exception as e:
            self.log(f"Error fatal al leer el CSV: {e}")
            self.is_syncing = False
            self.start_sync_button.configure(state="normal", text="Iniciar Sincronización")
            return

        # 4. Bucle de procesamiento
        for index, row in df.iterrows():
            sku = row.get(user_mapping['sku'], '').strip()
            product_name = row.get(user_mapping.get('name', ''), sku)
            
            if not sku:
                self.log(f"Fila {index + 2}: Omitida (SKU vacío).")
                continue

            self.log(f"--- Procesando: {product_name} (SKU: {sku}) ---")
            
            # Construir el payload dinámicamente
            product_data = {'type': 'simple'} # O añadir lógica para tipo variable
            for woo_field, csv_column in user_mapping.items():
                if woo_field not in ['images', 'sku']: # El SKU ya lo tenemos
                    product_data[woo_field] = row.get(csv_column, '')

            # Manejo de imágenes
            if 'images' in user_mapping:
                image_cell = row.get(user_mapping['images'], '')
                if image_cell and not image_cell.lower().startswith('http'):
                    image_path = os.path.join(self.image_folder_path, image_cell)
                    uploaded_image = self.api_client.upload_image(image_path, image_cell)
                    if uploaded_image:
                        product_data['images'] = [{'id': uploaded_image['id']}]
                else:
                    self.log("  -> Imagen es URL o está vacía. Se ignora.")

            # Lógica de creación/actualización
            existing_product = self.api_client.get_product_by_sku(sku)
            if existing_product:
                result = self.api_client.update_product(existing_product['id'], product_data)
                if result: self.log(f"  -> ÉXITO: Producto ID {existing_product['id']} actualizado.")
            else:
                product_data['sku'] = sku # Asegurarnos de que el SKU va en la creación
                result = self.api_client.create_product(product_data)
                if result: self.log(f"  -> ÉXITO: Producto creado con ID {result['id']}.")
        
        self.log("================================")
        self.log("SINCRONIZACIÓN COMPLETADA")
        self.log("================================")
        self.is_syncing = False
        self.start_sync_button.configure(state="normal", text="Iniciar Sincronización")

if __name__ == "__main__":
    import os
    app = App()
    app.mainloop()