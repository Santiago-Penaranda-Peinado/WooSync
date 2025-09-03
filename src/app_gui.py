# src/app_gui.py

import customtkinter
from tkinter import filedialog, simpledialog
import pandas as pd
import os
import threading
import json
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
        
        self.translations = {
            "es": {
                "window_title": "WooSync v3.0 - Sincronizador para WooCommerce",
                "connect_to_store": "Conectar a la Tienda",
                "store_url_placeholder": "URL de la tienda (https://...)",
                "username_placeholder": "Nombre de Usuario de WordPress",
                "app_password_placeholder": "Contraseña de Aplicación",
                "connect_button": "Conectar",
                "connecting_status": "Conectando...",
                "error_all_fields_required": "Todos los campos son obligatorios.",
                "error_connection_failed": "Error: Revisa la URL y las credenciales.",
                "starting_from_scratch": "¿Empezando desde cero?",
                "download_template_button": "Descargar Plantilla Mejorada",
                "already_have_file": "¿Ya tienes un archivo?",
                "select_csv_button": "Seleccionar Archivo CSV",
                "step2_images_label": "Paso 2: Selecciona la carpeta de imágenes (Opcional)",
                "select_images_folder_button": "Seleccionar Carpeta de Imágenes",
                "mapping_presets_label": "Plantillas de Mapeo Rápido:",
                "basic_preset_button": "Básico",
                "map_all_preset_button": "Mapear Todo",
                "clear_all_preset_button": "Limpiar Todo",
                "step3_mapping_label": "Paso 3: Mapea las columnas",
                "step3_mapping_label_with_count": "Paso 3: Mapea las {count} columnas",
                "sync_mode_label": "Modo de Sincronización:",
                "safe_mode_radio": "Modo Seguro (Crear y Actualizar)",
                "mirror_mode_radio": "Modo Espejo (Sincronización Completa)",
                "compatibility_mode_check": "Modo Compatible (Lento y Seguro)",
                "mirror_mode_warning": "¡ADVERTENCIA! El Modo Espejo eliminará permanentemente de la tienda\ntodos los productos que NO estén en tu archivo CSV.",
                "start_sync_button": "Iniciar Sincronización",
                "syncing_button": "Sincronizando...",
                "csv_file_label": "Archivo: {filename}",
                "image_folder_label": "Carpeta: {folderpath}",
                "do_not_import": "No importar",
                "meta_field_template": "meta: [Escribe el nombre del campo]",
                "log_applying_basic_mapping": "Aplicando plantilla de mapeo 'Básico'...",
                "log_clearing_mapping": "Limpiando todo el mapeo...",
                "log_applying_full_mapping": "Intentando mapear todas las columnas automáticamente...",
                "log_creating_template": "Creando plantilla mejorada...",
                "save_template_dialog_title": "Guardar plantilla como...",
                "log_template_saved": "Plantilla guardada exitosamente en: {filepath}",
                "log_template_save_error": "Error al guardar la plantilla: {e}",
                "log_sync_starting": "INICIANDO SINCRONIZACIÓN EN MODO: {mode}",
                "log_error_no_csv": "Debes seleccionar un archivo CSV.",
                "log_error_no_sku": "El campo 'SKU' es obligatorio.",
                "log_csv_loaded": "Archivo CSV cargado. Contiene {count} productos.",
                "log_fatal_csv_error": "Error fatal al leer el CSV: {e}",
                "log_getting_inventory": "Obteniendo inventario actual de la tienda...",
                "log_store_products_found": "Se encontraron {count} productos con SKU en la tienda.",
                "delete_confirmation_dialog_title": "CONFIRMACIÓN DE ELIMINACIÓN PERMANENTE",
                "delete_confirmation_dialog_text": "Estás a punto de ELIMINAR PERMANENTEMENTE {count} productos.\nEsta acción no se puede deshacer.\n\nPara confirmar, escribe 'ELIMINAR' en mayúsculas:",
                "delete_confirmation_keyword": "ELIMINAR",
                "log_mirror_sync_continue": "Confirmación recibida. Eliminando {count} productos por lotes...",
                "log_mirror_sync_delete_batch": "Enviando lote de ELIMINACIÓN de {count} productos...",
                "log_mirror_sync_cancelled": "Eliminación cancelada por el usuario.",
                "log_processing_compatible": "Iniciando procesamiento en Modo Compatible (uno por uno)...",
                "log_processing_batch": "Iniciando procesamiento en Modo Rápido (por lotes)...",
                "log_sync_completed_success": "SINCRONIZACIÓN COMPLETADA",
                "log_sync_aborted_error": "SINCRONIZACIÓN ABORTADA POR ERRORES",
                "log_processing_sku": "({current}/{total}) Procesando SKU: {sku}",
                "log_warn_empty_sku": "Fila {row}: Omitida (SKU vacío).",
                "log_success_product_updated": "Producto Actualizado: {sku} (ID: {id})",
                "log_error_product_update": "Error al actualizar {sku}: {error}",
                "log_success_product_created": "Producto Creado: {sku} (ID: {id})",
                "log_error_product_create": "Error al crear {sku}: {error}",
                "log_batch_create_ready": "Preparado para crear: {count} productos.",
                "log_batch_update_ready": "Preparado para actualizar: {count} productos.",
                "log_batch_create_sending": "Enviando lote de CREACIÓN de {count} productos...",
                "log_batch_update_sending": "Enviando lote de ACTUALIZACIÓN de {count} productos...",
                "log_process_summary": "Proceso completado. Creados: {created}, Actualizados: {updated}.",
                "language_toggle_button": "EN/ES",
                "save_mapping_button": "Guardar Mapeo",
                "load_mapping_button": "Cargar Mapeo",
                "warn_no_mapping_to_save": "No hay un mapeo activo para guardar.",
                "warn_load_csv_first": "Por favor, carga un archivo CSV antes de cargar un mapeo.",
                "log_mapping_saved": "Mapeo guardado exitosamente en: {filepath}",
                "log_mapping_loaded": "Mapeo cargado exitosamente desde: {filepath}",
                "error_loading_mapping": "Error al cargar el archivo de mapeo. Asegúrate de que es un JSON válido.",
                "warn_duplicate_skus_found": "¡ATENCIÓN! Se encontraron los siguientes SKUs duplicados en el CSV. Se procesará la última aparición de cada uno:"
            },
            "en": {
                "window_title": "WooSync v3.0 - WooCommerce Synchronizer",
                "connect_to_store": "Connect to Store",
                "store_url_placeholder": "Store URL (https://...)",
                "username_placeholder": "WordPress Username",
                "app_password_placeholder": "Application Password",
                "connect_button": "Connect",
                "connecting_status": "Connecting...",
                "error_all_fields_required": "All fields are required.",
                "error_connection_failed": "Error: Check URL and credentials.",
                "starting_from_scratch": "Starting from scratch?",
                "download_template_button": "Download Enhanced Template",
                "already_have_file": "Already have a file?",
                "select_csv_button": "Select CSV File",
                "step2_images_label": "Step 2: Select the image folder (Optional)",
                "select_images_folder_button": "Select Image Folder",
                "mapping_presets_label": "Quick Mapping Presets:",
                "basic_preset_button": "Basic",
                "map_all_preset_button": "Map All",
                "clear_all_preset_button": "Clear All",
                "step3_mapping_label": "Step 3: Map the columns",
                "step3_mapping_label_with_count": "Step 3: Map the {count} columns",
                "sync_mode_label": "Synchronization Mode:",
                "safe_mode_radio": "Safe Mode (Create and Update)",
                "mirror_mode_radio": "Mirror Mode (Full Synchronization)",
                "compatibility_mode_check": "Compatibility Mode (Slow & Safe)",
                "mirror_mode_warning": "WARNING! Mirror Mode will permanently delete all products from your store\nthat are NOT in your CSV file.",
                "start_sync_button": "Start Synchronization",
                "syncing_button": "Syncing...",
                "csv_file_label": "File: {filename}",
                "image_folder_label": "Folder: {folderpath}",
                "do_not_import": "Do not import",
                "meta_field_template": "meta: [Enter field name]",
                "log_applying_basic_mapping": "Applying 'Basic' mapping preset...",
                "log_clearing_mapping": "Clearing all mapping...",
                "log_applying_full_mapping": "Attempting to auto-map all columns...",
                "log_creating_template": "Creating enhanced template...",
                "save_template_dialog_title": "Save template as...",
                "log_template_saved": "Template saved successfully to: {filepath}",
                "log_template_save_error": "Error saving template: {e}",
                "log_sync_starting": "STARTING SYNC IN MODE: {mode}",
                "log_error_no_csv": "You must select a CSV file.",
                "log_error_no_sku": "The 'SKU' field is mandatory.",
                "log_csv_loaded": "CSV file loaded. Contains {count} products.",
                "log_fatal_csv_error": "Fatal error reading CSV: {e}",
                "log_getting_inventory": "Getting current store inventory...",
                "log_store_products_found": "Found {count} products with SKU in the store.",
                "delete_confirmation_dialog_title": "PERMANENT DELETION CONFIRMATION",
                "delete_confirmation_dialog_text": "You are about to PERMANENTLY DELETE {count} products.\nThis action cannot be undone.\n\nTo confirm, type 'DELETE' in all caps:",
                "log_mirror_sync_continue": "Confirmation received. Deleting {count} products in batches...",
                "log_mirror_sync_delete_batch": "Sending DELETE batch of {count} products...",
                "log_mirror_sync_cancelled": "Deletion cancelled by user.",
                "log_processing_compatible": "Starting processing in Compatibility Mode (one by one)...",
                "log_processing_batch": "Starting processing in Fast Mode (batch processing)...",
                "log_sync_completed_success": "SYNCHRONIZATION COMPLETED",
                "log_sync_aborted_error": "SYNCHRONIZATION ABORTED DUE TO ERRORS",
                "log_processing_sku": "({current}/{total}) Processing SKU: {sku}",
                "log_warn_empty_sku": "Row {row}: Skipped (empty SKU).",
                "log_success_product_updated": "Product updated: {sku}",
                "log_error_product_update": "Error updating {sku}: {error}",
                "log_success_product_created": "Product created: {sku}",
                "log_error_product_create": "Error creating {sku}: {error}",
                "log_batch_create_ready": "Prepared to create: {count} products.",
                "log_batch_update_ready": "Prepared to update: {count} products.",
                "log_batch_create_sending": "Sending CREATE batch of {count} products...",
                "log_batch_update_sending": "Sending UPDATE batch of {count} products...",
                "delete_confirmation_keyword": "DELETE",
                "log_process_summary": "Process completed. Created: {created}, Updated: {updated}.",
                "language_toggle_button": "EN/ES",
                "save_mapping_button": "Save Mapping",
                "load_mapping_button": "Load Mapping",
                "warn_no_mapping_to_save": "There is no active mapping to save.",
                "warn_load_csv_first": "Please load a CSV file before loading a mapping.",
                "log_mapping_saved": "Mapping saved successfully to: {filepath}",
                "log_mapping_loaded": "Mapping loaded successfully from: {filepath}",
                "error_loading_mapping": "Error loading mapping file. Ensure it is a valid JSON.",
                "warn_duplicate_skus_found": "WARNING! The following duplicate SKUs were found in the CSV. The last occurrence of each will be processed:"
            }
        }
        
        self.language = "es"
        self.title(self._("window_title"))
        self.geometry("800x850")
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
        self.load_config()

    def _(self, key):
        return self.translations[self.language].get(key, key)

    def toggle_language(self):
        self.language = "en" if self.language == "es" else "es"
        self.update_ui_text()

    def update_ui_text(self):
        self.title(self._("window_title"))
        
        if hasattr(self, 'welcome_label') and self.login_frame.winfo_ismapped():
            self.welcome_label.configure(text=self._("connect_to_store"))
            self.url_entry.configure(placeholder_text=self._("store_url_placeholder"))
            self.user_entry.configure(placeholder_text=self._("username_placeholder"))
            self.password_entry.configure(placeholder_text=self._("app_password_placeholder"))
            self.connect_button.configure(text=self._("connect_button"))
            self.lang_toggle_button.configure(text=self._("language_toggle_button"))

        if hasattr(self, 'template_label') and self.main_frame.winfo_ismapped():
            self.template_label.configure(text=self._("starting_from_scratch"))
            self.template_button.configure(text=self._("download_template_button"))
            self.csv_button.configure(text=self._("select_csv_button"))
            self.image_button.configure(text=self._("select_images_folder_button"))
            self.presets_label.configure(text=self._("mapping_presets_label"))
            self.basic_button.configure(text=self._("basic_preset_button"))
            self.full_button.configure(text=self._("map_all_preset_button"))
            self.clear_button.configure(text=self._("clear_all_preset_button"))
            self.save_mapping_button.configure(text=self._("save_mapping_button"))
            self.load_mapping_button.configure(text=self._("load_mapping_button"))
            self.mode_label.configure(text=self._("sync_mode_label"))
            self.safe_radio.configure(text=self._("safe_mode_radio"))
            self.mirror_radio.configure(text=self._("mirror_mode_radio"))
            self.compatibility_mode_check.configure(text=self._("compatibility_mode_check"))
            if not self.is_syncing:
                self.start_sync_button.configure(text=self._("start_sync_button"))
            self.lang_toggle_button_main.configure(text=self._("language_toggle_button"))
            self.on_sync_mode_change()

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                self.url_entry.insert(0, config.get("store_url", ""))
                self.user_entry.insert(0, config.get("username", ""))
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save_config(self, store_url, username):
        try:
            with open("config.json", "w") as f:
                json.dump({"store_url": store_url, "username": username}, f)
        except Exception as e:
            self.log("ERROR", f"Error saving config: {e}")

    def save_mapping(self):
        if not self.mapping_widgets:
            self.log("WARN", self._("warn_no_mapping_to_save"))
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title=self._("save_mapping_button"))
        if not filepath: return
        mapping_to_save = {item['csv_column']: item['combo'].get() for item in self.mapping_widgets}
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(mapping_to_save, f, indent=4, ensure_ascii=False)
        self.log("SUCCESS", self._("log_mapping_saved").format(filepath=filepath))

    def load_mapping(self):
        if not self.mapping_widgets:
            self.log("WARN", self._("warn_load_csv_first"))
            return
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], title=self._("load_mapping_button"))
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded_mapping = json.load(f)
            for item in self.mapping_widgets:
                csv_col = item['csv_column']
                if csv_col in loaded_mapping and loaded_mapping[csv_col] in item['combo'].cget("values"):
                    item['combo'].set(loaded_mapping[csv_col])
            self.log("SUCCESS", self._("log_mapping_loaded").format(filepath=filepath))
        except (FileNotFoundError, json.JSONDecodeError):
            self.log("ERROR", self._("error_loading_mapping"))
    
    def create_login_widgets(self):
        lang_frame = customtkinter.CTkFrame(self.login_frame)
        lang_frame.pack(anchor="ne", padx=10, pady=10)
        self.lang_toggle_button = customtkinter.CTkButton(lang_frame, text=self._("language_toggle_button"), command=self.toggle_language, width=50)
        self.lang_toggle_button.pack()
        
        self.welcome_label = customtkinter.CTkLabel(self.login_frame, text=self._("connect_to_store"), font=("Arial", 20))
        self.welcome_label.pack(pady=20)
        self.url_entry = customtkinter.CTkEntry(self.login_frame, placeholder_text=self._("store_url_placeholder"))
        self.url_entry.pack(pady=10, padx=20, fill="x")
        self.user_entry = customtkinter.CTkEntry(self.login_frame, placeholder_text=self._("username_placeholder"))
        self.user_entry.pack(pady=10, padx=20, fill="x")
        self.password_entry = customtkinter.CTkEntry(self.login_frame, placeholder_text=self._("app_password_placeholder"), show="*")
        self.password_entry.pack(pady=10, padx=20, fill="x")
        self.connect_button = customtkinter.CTkButton(self.login_frame, text=self._("connect_button"), command=self.connect_to_store)
        self.connect_button.pack(pady=20)
        self.status_label = customtkinter.CTkLabel(self.login_frame, text="", font=("Arial", 12))
        self.status_label.pack(pady=10)

    def connect_to_store(self):
        store_url = self.url_entry.get().strip().rstrip('/')
        username = self.user_entry.get()
        password = self.password_entry.get()
        if not all([store_url, username, password]):
            self.status_label.configure(text=self._("error_all_fields_required"), text_color="orange")
            return
        self.status_label.configure(text=self._("connecting_status"), text_color="gray")
        self.update_idletasks()
        self.api_client = WooCommerceAPI(store_url, username, password)
        if self.api_client.check_connection():
            self.save_config(store_url, username)
            self.login_frame.pack_forget()
            self.create_main_widgets()
            self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        else:
            self.api_client = None
            self.status_label.configure(text=self._("error_connection_failed"), text_color="red")
    
    def create_main_widgets(self):
        lang_frame = customtkinter.CTkFrame(self.main_frame)
        lang_frame.pack(anchor="ne", padx=10, pady=0, fill="x")
        self.lang_toggle_button_main = customtkinter.CTkButton(lang_frame, text=self._("language_toggle_button"), command=self.toggle_language, width=50)
        self.lang_toggle_button_main.pack(anchor="ne")

        file_frame = customtkinter.CTkFrame(self.main_frame)
        file_frame.pack(pady=10, padx=10, fill="x")
        template_frame = customtkinter.CTkFrame(file_frame)
        template_frame.pack(side="left", padx=20, pady=10, expand=True)
        self.template_label = customtkinter.CTkLabel(template_frame, text=self._("starting_from_scratch"))
        self.template_label.pack()
        self.template_button = customtkinter.CTkButton(template_frame, text=self._("download_template_button"), command=self.download_template)
        self.template_button.pack(pady=5)
        
        upload_frame = customtkinter.CTkFrame(file_frame)
        upload_frame.pack(side="left", padx=20, pady=10, expand=True)
        self.upload_label = customtkinter.CTkLabel(upload_frame, text=self._("already_have_file"))
        self.upload_label.pack()
        self.csv_button = customtkinter.CTkButton(upload_frame, text=self._("select_csv_button"), command=self.select_csv_file)
        self.csv_button.pack(pady=5)
        
        self.image_folder_label = customtkinter.CTkLabel(self.main_frame, text=self._("step2_images_label"))
        self.image_folder_label.pack(pady=10)
        self.image_button = customtkinter.CTkButton(self.main_frame, text=self._("select_images_folder_button"), command=self.select_image_folder)
        self.image_button.pack(pady=5)
        
        presets_frame = customtkinter.CTkFrame(self.main_frame)
        presets_frame.pack(pady=5, padx=10, fill="x")
        self.presets_label = customtkinter.CTkLabel(presets_frame, text=self._("mapping_presets_label"))
        self.presets_label.pack(side="left", padx=10)
        self.basic_button = customtkinter.CTkButton(presets_frame, text=self._("basic_preset_button"), command=self.apply_basic_mapping)
        self.basic_button.pack(side="left", padx=5)
        self.full_button = customtkinter.CTkButton(presets_frame, text=self._("map_all_preset_button"), command=self.apply_full_mapping)
        self.full_button.pack(side="left", padx=5)
        self.clear_button = customtkinter.CTkButton(presets_frame, text=self._("clear_all_preset_button"), command=self.clear_mapping)
        self.clear_button.pack(side="left", padx=5)
        self.save_mapping_button = customtkinter.CTkButton(presets_frame, text=self._("save_mapping_button"), command=self.save_mapping)
        self.save_mapping_button.pack(side="left", padx=(20, 5))
        self.load_mapping_button = customtkinter.CTkButton(presets_frame, text=self._("load_mapping_button"), command=self.load_mapping)
        self.load_mapping_button.pack(side="left", padx=5)

        self.mapping_frame = customtkinter.CTkScrollableFrame(self.main_frame, label_text=self._("step3_mapping_label"))
        self.mapping_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        sync_mode_frame = customtkinter.CTkFrame(self.main_frame)
        sync_mode_frame.pack(pady=10, padx=10, fill="x")
        self.mode_label = customtkinter.CTkLabel(sync_mode_frame, text=self._("sync_mode_label"))
        self.mode_label.pack(side="left", padx=10)
        self.sync_mode = customtkinter.StringVar(value="safe")
        self.safe_radio = customtkinter.CTkRadioButton(sync_mode_frame, text=self._("safe_mode_radio"), variable=self.sync_mode, value="safe", command=self.on_sync_mode_change)
        self.safe_radio.pack(side="left", padx=5)
        self.mirror_radio = customtkinter.CTkRadioButton(sync_mode_frame, text=self._("mirror_mode_radio"), variable=self.sync_mode, value="mirror", command=self.on_sync_mode_change)
        self.mirror_radio.pack(side="left", padx=5)
        self.compatibility_mode_var = customtkinter.StringVar(value="off")
        self.compatibility_mode_check = customtkinter.CTkCheckBox(sync_mode_frame, text=self._("compatibility_mode_check"), variable=self.compatibility_mode_var, onvalue="on", offvalue="off")
        self.compatibility_mode_check.pack(side="left", padx=10)
        
        self.warning_label = customtkinter.CTkLabel(self.main_frame, text="", text_color="orange")
        self.warning_label.pack(pady=5, padx=10)
        
        sync_frame = customtkinter.CTkFrame(self.main_frame)
        sync_frame.pack(pady=10, padx=10, fill="x")
        self.start_sync_button = customtkinter.CTkButton(sync_frame, text=self._("start_sync_button"), command=self.start_synchronization_thread)
        self.start_sync_button.pack(pady=10)
        
        self.progress_bar = customtkinter.CTkProgressBar(self.main_frame, orientation="horizontal")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(5, 10), padx=10, fill="x")
        self.log_textbox = customtkinter.CTkTextbox(self.main_frame, height=200)
        self.log_textbox.pack(pady=10, padx=10, fill="both", expand=True)

    def update_progress(self, value):
        self.after(0, self.progress_bar.set, value)

    def select_csv_file(self):
        filepath = filedialog.askopenfilename(filetypes=(("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")))
        if not filepath: 
            return
        self.csv_path = filepath
        filename = os.path.basename(filepath)
        self.upload_label.configure(text=self._("csv_file_label").format(filename=filename))
        try:
            df_headers = pd.read_csv(self.csv_path, nrows=0).columns.tolist()
            self.create_mapping_widgets(df_headers)
        except Exception as e:
            self.log("ERROR", f"Error al leer el CSV: {e}")

    def select_image_folder(self):
        folderpath = filedialog.askdirectory()
        if not folderpath: 
            return
        self.image_folder_path = folderpath
        self.image_folder_label.configure(text=self._("image_folder_label").format(folderpath=folderpath))
        
    def create_mapping_widgets(self, csv_columns):
        for widget in self.mapping_frame.winfo_children(): 
            widget.destroy()
        self.mapping_widgets = []
        self.woocommerce_fields = [
            self._("do_not_import"), 
            "Name", "SKU", "Regular price", "Sale price", "Description", "Short description", 
            "Stock", "Weight", "Length", "Width", "Height", "Categories", "Tags", "Images", 
            "Purchase note", "Menu order", 
            self._("meta_field_template")
        ]
        self.mapping_frame.configure(label_text=self._("step3_mapping_label_with_count").format(count=len(csv_columns)))
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
            combobox_widget.set(self._("do_not_import"))
            return
        column_lower = column_name.lower().replace("_", " ").replace("-", " ").strip()
        for field in self.woocommerce_fields:
            if field.lower() == column_lower:
                combobox_widget.set(field)
                return
        best_guess = self._("do_not_import")
        if "tag" in column_lower or "etiqueta" in column_lower: 
            best_guess = "Tags"
        elif "categor" in column_lower: 
            best_guess = "Categories"
        elif "peso" in column_lower or "weight" in column_lower: 
            best_guess = "Weight"
        elif "ancho" in column_lower or "width" in column_lower: 
            best_guess = "Width"
        combobox_widget.set(best_guess)
        
    def apply_basic_mapping(self):
        essential_fields = ["Name", "SKU", "Regular price", "Images", "Short description", "Description", "Categories"]
        self.log("INFO", self._("log_applying_basic_mapping"))
        self.clear_mapping()
        for essential in essential_fields:
            for item in self.mapping_widgets:
                if essential.lower() in item['csv_column'].lower():
                    item['combo'].set(essential)
                    break
                    
    def clear_mapping(self):
        self.log("INFO", self._("log_clearing_mapping"))
        for item in self.mapping_widgets: 
            item['combo'].set(self._("do_not_import"))
        
    def apply_full_mapping(self):
        self.log("INFO", self._("log_applying_full_mapping"))
        for item in self.mapping_widgets:
            self.auto_guess_mapping(item['csv_column'], item['combo'])

    def download_template(self):
        self.log("INFO", self._("log_creating_template"))
        template_headers = {
            'SKU': ['SKU-EJEMPLO-1'], 
            'Name': ['Producto de Ejemplo'], 
            'Regular price': [99.99], 
            'Sale price': [79.99], 
            'Short description': ['Descripción corta y atractiva.'], 
            'Description': ['Descripción completa del producto.'], 
            'Images': ['imagen1.jpg, imagen2.png'], 
            'Categories': ['Categoría Principal, Subcategoría'], 
            'Tags': ['tag1, tag2, tag3'], 
            'Stock': [100], 
            'Weight': [0.5], 
            'Length': [20], 
            'Width': [15], 
            'Height': [10]
        }
        df = pd.DataFrame(template_headers)
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv", 
            filetypes=[("Archivos CSV", "*.csv")], 
            title=self._("save_template_dialog_title"), 
            initialfile="plantilla_productos_avanzada.csv"
        )
        if filepath:
            try:
                df.to_csv(filepath, index=False, encoding='utf-8')
                self.log("SUCCESS", self._("log_template_saved").format(filepath=filepath))
            except Exception as e:
                self.log("ERROR", self._("log_template_save_error").format(e=e))

    def on_sync_mode_change(self):
        if self.sync_mode.get() == "mirror":
            self.warning_label.configure(text=self._("mirror_mode_warning"))
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
            self.progress_bar.set(0)
            thread = threading.Thread(target=self.start_synchronization)
            thread.daemon = True
            thread.start()

    def finalize_sync(self, success=True):
        if success:
            self.update_progress(1.0)
            self.log("SUCCESS", "================================")
            self.log("SUCCESS", self._("log_sync_completed_success"))
            self.log("SUCCESS", "================================")
        else:
            self.log("ERROR", "================================")
            self.log("ERROR", self._("log_sync_aborted_error"))
            self.log("ERROR", "================================")
        
        self.is_syncing = False
        self.start_sync_button.configure(state="normal", text=self._("start_sync_button"))
        self.on_sync_mode_change()

    def start_synchronization(self):
        self.is_syncing = True
        self.start_sync_button.configure(state="disabled", text=self._("syncing_button"))
        self.log_textbox.delete("1.0", "end")
        self.log("INFO", self._("log_sync_starting").format(mode=self.sync_mode.get().upper()))

        if not self.csv_path:
            self.log("ERROR", self._("log_error_no_csv"))
            self.finalize_sync(False)
            return

        user_mapping = {item['combo'].get(): item['csv_column'] for item in self.mapping_widgets if item['combo'].get() != self._("do_not_import")}
        if 'SKU' not in user_mapping:
            self.log("ERROR", self._("log_error_no_sku"))
            self.finalize_sync(False)
            return

        try:
            df = pd.read_csv(self.csv_path, dtype=str).fillna('')
            self.log("INFO", self._("log_csv_loaded").format(count=len(df)))
        except Exception as e:
            self.log("ERROR", self._("log_fatal_csv_error").format(e=e))
            self.finalize_sync(False)
            return

        # NUEVO: validación de SKUs duplicados
        sku_column_name = user_mapping.get('SKU')
        if sku_column_name:
            duplicated_skus = df[df.duplicated(subset=[sku_column_name], keep=False)]
            if not duplicated_skus.empty:
                self.log("WARN", "--------------------------------------------")
                self.log("WARN", self._("warn_duplicate_skus_found"))
                for sku in duplicated_skus[sku_column_name].unique():
                    self.log("WARN", f"  - SKU: {sku}")
                self.log("WARN", "--------------------------------------------")

        # Obtener productos de la tienda
        self.log("INFO", self._("log_getting_inventory"))
        store_products = self.api_client.get_all_products()
        if 'error' in store_products:
            self.log("ERROR", store_products['error'])
            self.finalize_sync(success=False)
            return
        
        store_sku_to_id_map = {prod['sku']: prod['id'] for prod in store_products if prod.get('sku')}
        self.log("INFO", self._("log_store_products_found").format(count=len(store_sku_to_id_map)))

        # Lógica Modo Espejo
        if self.sync_mode.get() == "mirror":
            csv_skus = set(df[user_mapping['SKU']].dropna().unique())
            skus_to_delete = set(store_sku_to_id_map.keys()) - csv_skus

            if skus_to_delete:
                self.after(0, self.ask_for_deletion_confirmation, list(skus_to_delete), store_sku_to_id_map, df, user_mapping)
                return # Detenemos aquí, el resto se ejecuta después de la confirmación
        
        # Si es Modo Seguro, o Modo Espejo sin nada que borrar, procesamos directamente
        if self.compatibility_mode_var.get() == "on":
            self.log("INFO", self._("log_processing_compatible"))
            self.process_products_one_by_one(df, user_mapping, store_sku_to_id_map)
        else:
            self.log("INFO", self._("log_processing_batch"))
            self.process_products_batch(df, user_mapping, store_sku_to_id_map)
        self.finalize_sync()

    def ask_for_deletion_confirmation(self, skus_to_delete, store_sku_to_id_map, df, user_mapping):
        """Muestra el diálogo y luego continúa el proceso en un nuevo hilo."""
        confirmation_text = simpledialog.askstring(
            self._("delete_confirmation_dialog_title"),
            self._("delete_confirmation_dialog_text").format(count=len(skus_to_delete))
        )
        
        # Iniciamos el resto del proceso en un nuevo hilo para no bloquear la UI
        thread = threading.Thread(target=self.continue_mirror_sync, args=(confirmation_text, skus_to_delete, store_sku_to_id_map, df, user_mapping))
        thread.daemon = True
        thread.start()

    def continue_mirror_sync(self, confirmation, skus_to_delete, store_sku_to_id_map, df, user_mapping):
        """Se ejecuta después de la confirmación del usuario para terminar el Modo Espejo."""
        if confirmation == self._("delete_confirmation_keyword"):
            self.log("INFO", self._("log_mirror_sync_continue").format(count=len(skus_to_delete)))
            ids_to_delete = [store_sku_to_id_map[sku] for sku in skus_to_delete]
            
            # BORRADO POR LOTES
            for chunk in chunks(ids_to_delete, 50):
                self.log("INFO", self._("log_mirror_sync_delete_batch").format(count=len(chunk)))
                result = self.api_client.process_batch({'delete': chunk})
                if result and 'error' in result:
                    self.log("ERROR", result['error'])
        else:
            self.log("WARN", self._("log_mirror_sync_cancelled"))
            
        # Continuamos con la creación/actualización
        if self.compatibility_mode_var.get() == "on":
            self.log("INFO", self._("log_processing_compatible"))
            self.process_products_one_by_one(df, user_mapping, store_sku_to_id_map)
        else:
            self.log("INFO", self._("log_processing_batch"))
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
                self.log("WARN", self._("log_warn_empty_sku").format(row=index + 2))
                continue
            
            # Preparar datos del producto
            product_data = {'type': 'simple'}
            meta_data = []
            dimensions = {}
            
            for gui_field, csv_column in user_mapping.items():
                value = row.get(csv_column, '')
                if pd.isna(value) or value == '': 
                    continue
                api_key = self.API_FIELD_MAP.get(gui_field)
                if gui_field.startswith("meta:"):
                    meta_key = gui_field.split(":", 1)[1].strip()
                    if meta_key: 
                        meta_data.append({'key': meta_key, 'value': value})
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
                    if not self.image_folder_path: 
                        continue
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

            self.log("INFO", self._("log_processing_sku").format(current=index + 1, total=total_products, sku=sku))

            # Lógica de envío individual
            if sku in sku_to_id_map:
                product_id = sku_to_id_map[sku]
                result = self.api_client.update_product(product_id, product_data)
                if result and 'error' not in result: 
                    updated_count += 1
                    self.log("SUCCESS", self._("log_success_product_updated").format(sku=sku))
                elif result and 'error' in result:
                    self.log("ERROR", self._("log_error_product_update").format(sku=sku, error=result['error']))
            else:
                product_data['sku'] = sku
                result = self.api_client.create_product(product_data)
                if result and 'error' not in result: 
                    created_count += 1
                    self.log("SUCCESS", self._("log_success_product_created").format(sku=sku))
                elif result and 'error' in result:
                    self.log("ERROR", self._("log_error_product_create").format(sku=sku, error=result['error']))
    
        self.log("INFO", self._("log_process_summary").format(created=created_count, updated=updated_count))

    def process_products_batch(self, df, user_mapping, sku_to_id_map):
        products_to_create = []
        products_to_update = []
        
        # 1. Preparar las listas de productos para crear y actualizar
        for index, row in df.iterrows():
            sku = row.get(user_mapping.get('SKU'), '').strip()
            if not sku:
                self.log("WARN", self._("log_warn_empty_sku").format(row=index + 2))
                continue
            
            # Lógica para construir el `product_data` a partir de la fila del CSV
            product_data = {'type': 'simple'}
            meta_data = []
            dimensions = {}
            
            for gui_field, csv_column in user_mapping.items():
                value = row.get(csv_column, '')
                if pd.isna(value) or value == '': continue
                api_key = self.API_FIELD_MAP.get(gui_field)
                if gui_field.startswith("meta:"):
                    meta_key = gui_field.split(":", 1)[1].strip().replace(']', '').replace('[', '')
                    if meta_key: meta_data.append({'key': meta_key, 'value': value})
                elif api_key in ['categories', 'tags']:
                    product_data[api_key] = [{'name': item.strip()} for item in str(value).split(',')]
                elif api_key in ['length', 'width', 'height']:
                    try: dimensions[api_key] = str(float(str(value).replace(',', '.')))
                    except (ValueError, TypeError): dimensions[api_key] = '0'
                elif api_key == 'images':
                    if not self.image_folder_path: continue
                    image_ids = []
                    for img_name in str(value).split(','):
                        img_name = img_name.strip()
                        if img_name and not img_name.lower().startswith('http'):
                            image_path = os.path.join(self.image_folder_path, img_name)
                            uploaded = self.api_client.upload_image(image_path, img_name)
                            if uploaded and 'id' in uploaded: image_ids.append({'id': uploaded['id']})
                            elif uploaded and 'error' in uploaded: self.log("ERROR", f"Subiendo '{img_name}': {uploaded['error']}")
                    if image_ids: product_data['images'] = image_ids
                elif api_key:
                    if api_key in ['regular_price', 'sale_price']:
                        try: product_data[api_key] = str(float(str(value).replace(',', '.')))
                        except (ValueError, TypeError): product_data[api_key] = '0'
                    elif api_key == 'stock_quantity':
                        try: product_data[api_key] = int(float(str(value).replace(',', '.')))
                        except (ValueError, TypeError): product_data[api_key] = 0
                    else: product_data[api_key] = value
            
            if dimensions: product_data['dimensions'] = dimensions
            if meta_data: product_data['meta_data'] = meta_data
            
            if sku in sku_to_id_map:
                product_data['id'] = sku_to_id_map[sku]
                products_to_update.append(product_data)
            else:
                product_data['sku'] = sku
                products_to_create.append(product_data)
        
        self.log("INFO", self._("log_batch_create_ready").format(count=len(products_to_create)))
        self.log("INFO", self._("log_batch_update_ready").format(count=len(products_to_update)))
        
        # 2. Procesar los lotes con la nueva lógica de feedback y progreso
        total_chunks = len(list(chunks(products_to_create, 50))) + len(list(chunks(products_to_update, 50)))
        chunk_count = 0

        # Bucle para CREAR productos
        for chunk in chunks(products_to_create, 50):
            self.log("INFO", self._("log_batch_create_sending").format(count=len(chunk)))
            result = self.api_client.process_batch({'create': chunk})
            
            if result and 'create' in result:
                # Si la API devuelve la lista de creaciones, la recorremos
                for item in result['create']:
                    sku = item.get('sku', 'N/A')
                    if item.get('error'):
                        # Si este item específico tiene un error, lo logueamos
                        self.log("ERROR", f"Creando SKU {sku}: {item['error']['message']}")
                    else:
                        # Si no hay error, logueamos el éxito
                        self.log("SUCCESS", self._("log_success_product_created").format(sku=sku, id=item.get('id')))
            elif result and 'error' in result:
                # Si toda la petición falló, logueamos el error general
                self.log("ERROR", f"Error en lote de creación: {result['error']}")

            chunk_count += 1
            if total_chunks > 0:
                self.update_progress(chunk_count / total_chunks)
        
        # Bucle para ACTUALIZAR productos 
        for chunk in chunks(products_to_update, 50):
            self.log("INFO", self._("log_batch_update_sending").format(count=len(chunk)))
            result = self.api_client.process_batch({'update': chunk})
            
            if result and 'update' in result:
                for item in result['update']:
                    sku = item.get('sku', 'N/A')
                    if item.get('error'):
                        self.log("ERROR", f"Actualizando SKU {sku}: {item['error']['message']}")
                    else:
                        self.log("SUCCESS", self._("log_success_product_updated").format(sku=sku, id=item.get('id')))
            elif result and 'error' in result:
                self.log("ERROR", f"Error en lote de actualización: {result['error']}")

            chunk_count += 1
            if total_chunks > 0:
                self.update_progress(chunk_count / total_chunks)

if __name__ == "__main__":
    app = App()
    app.after(100, app.process_log_queue)
    app.mainloop()