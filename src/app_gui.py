# src/app_gui.py

import customtkinter
from tkinter import filedialog, simpledialog
import pandas as pd
import os
import sys
import threading
import json
from api_client import WooCommerceAPI
from product_payload import build_product_payload
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
        
        self.translations = {}
        self.load_translations()
        
    def load_translations(self):
        """Carga las traducciones desde archivos JSON externos ubicados en la carpeta 'locales'."""
        # Detectar si estamos corriendo como exe empaquetado o en desarrollo
        if getattr(sys, 'frozen', False):
            # Corriendo como ejecutable empaquetado
            base_path = sys._MEIPASS
        else:
            # Corriendo en desarrollo
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        locales_dir = os.path.join(base_path, 'locales')
        
        # Asegurarse de que la carpeta locales exista
        if not os.path.exists(locales_dir):
            print(f"ADVERTENCIA: No se encontró la carpeta 'locales' en: {locales_dir}")
            # Fallback a traducciones mínimas en español
            self.translations = {
                "es": {"window_title": "WooSync v3.2", "connect_to_store": "Conectar a la Tienda"},
                "en": {"window_title": "WooSync v3.2", "connect_to_store": "Connect to Store"}
            }
            return

        for lang in ['es', 'en']:
            file_path = os.path.join(locales_dir, f'{lang}.json')
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                else:
                    print(f"ADVERTENCIA: Archivo de traducción no encontrado: {file_path}")
                    self.translations[lang] = {}
            except Exception as e:
                print(f"ERROR: Fallo al cargar traducción {lang}: {e}")
                self.translations[lang] = {}
        
        self.language = "es"
        self.title(self._("window_title"))
        self.geometry("800x850")
        self.api_client = None
        self.csv_path = ""
        self.image_folder_path = ""
        self.mapping_widgets = []
        self.is_syncing = False
        self.log_queue = Queue()
        self.image_cache = {}  # Cache simple para evitar re-subir imágenes ya procesadas
        self.API_FIELD_MAP = {"ID": "id", "Name": "name", "SKU": "sku", "Regular price": "regular_price", "Sale price": "sale_price", "Description": "description", "Short description": "short_description", "Stock": "stock_quantity", "Weight": "weight", "Length": "length", "Width": "width", "Height": "height", "Categories": "categories", "Tags": "tags", "Images": "images", "Purchase note": "purchase_note", "Menu order": "menu_order"}
        
        self.login_frame = customtkinter.CTkFrame(self)
        self.main_frame = customtkinter.CTkScrollableFrame(self)
        
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
            
            # Logic for Upload Label
            if self.csv_path:
                filename = os.path.basename(self.csv_path)
                self.upload_label.configure(text=self._("csv_file_label").format(filename=filename))
            else:
                self.upload_label.configure(text=self._("already_have_file"))
            
            self.export_button.configure(text=self._("export_csv_button"))
            self.csv_button.configure(text=self._("select_csv_button"))
            
            # Logic for Image Folder Label
            if self.image_folder_path:
                self.image_folder_label.configure(text=self._("image_folder_label").format(folderpath=self.image_folder_path))
            else:
                self.image_folder_label.configure(text=self._("step2_images_label"))

            self.image_button.configure(text=self._("select_images_folder_button"))
            self.presets_label.configure(text=self._("mapping_presets_label"))
            self.basic_button.configure(text=self._("basic_preset_button"))
            self.full_button.configure(text=self._("map_all_preset_button"))
            self.clear_button.configure(text=self._("clear_all_preset_button"))
            self.save_mapping_button.configure(text=self._("save_mapping_button"))
            self.load_mapping_button.configure(text=self._("load_mapping_button"))
            
            # Logic for Mapping Frame Label
            if self.mapping_widgets:
                self.mapping_frame.configure(label_text=self._("step3_mapping_label_with_count").format(count=len(self.mapping_widgets)))
            else:
                self.mapping_frame.configure(label_text=self._("step3_mapping_label"))

            self.mode_label.configure(text=self._("sync_mode_label"))
            self.safe_radio.configure(text=self._("safe_mode_radio"))
            self.mirror_radio.configure(text=self._("mirror_mode_radio"))
            self.dry_run_radio.configure(text=self._("dry_run_mode_radio"))
            self.compatibility_mode_check.configure(text=self._("compatibility_mode_check"))
            
            if not self.is_syncing:
                self.start_sync_button.configure(text=self._("start_sync_button"))
            else:
                 self.start_sync_button.configure(text=self._("syncing_button"))

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
        self.template_button = customtkinter.CTkButton(template_frame, text=self._("download_template_button"), command=self.download_template)
        self.template_button.pack(pady=5)
        
        self.export_button = customtkinter.CTkButton(template_frame, text=self._("export_csv_button"), command=self.export_products_thread, fg_color="#2B8C5A", hover_color="#1F6D42")
        self.export_button.pack(pady=5)
        
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
        
        # --- Frame de Presets (Centrado y Organizado) ---
        presets_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        presets_frame.pack(pady=10, padx=10, fill="x")
        
        # Fila 1: Etiqueta (Centrada)
        self.presets_label = customtkinter.CTkLabel(presets_frame, text=self._("mapping_presets_label"), font=("Arial", 12, "bold"))
        self.presets_label.pack(pady=(0, 5))
        
        # Fila 2: Botones de Acción (Centrados)
        action_buttons_frame = customtkinter.CTkFrame(presets_frame, fg_color="transparent")
        action_buttons_frame.pack(pady=2)
        self.basic_button = customtkinter.CTkButton(action_buttons_frame, text=self._("basic_preset_button"), command=self.apply_basic_mapping, width=120)
        self.basic_button.pack(side="left", padx=5)
        self.full_button = customtkinter.CTkButton(action_buttons_frame, text=self._("map_all_preset_button"), command=self.apply_full_mapping, width=120)
        self.full_button.pack(side="left", padx=5)
        self.clear_button = customtkinter.CTkButton(action_buttons_frame, text=self._("clear_all_preset_button"), command=self.clear_mapping, width=120, fg_color="#C0392B", hover_color="#922B21")
        self.clear_button.pack(side="left", padx=5)
        
        # Fila 3: Guardar/Cargar (Centrados)
        file_buttons_frame = customtkinter.CTkFrame(presets_frame, fg_color="transparent")
        file_buttons_frame.pack(pady=5)
        self.save_mapping_button = customtkinter.CTkButton(file_buttons_frame, text=self._("save_mapping_button"), command=self.save_mapping, width=120)
        self.save_mapping_button.pack(side="left", padx=5)
        self.load_mapping_button = customtkinter.CTkButton(file_buttons_frame, text=self._("load_mapping_button"), command=self.load_mapping, width=120)
        self.load_mapping_button.pack(side="left", padx=5)

        self.mapping_frame = customtkinter.CTkScrollableFrame(self.main_frame, label_text=self._("step3_mapping_label"), height=250)
        self.mapping_frame.pack(pady=10, padx=10, fill="both")
        
        # --- Frame de Modo de Sincronización (Centrado) ---
        sync_mode_frame = customtkinter.CTkFrame(self.main_frame)
        sync_mode_frame.pack(pady=10, padx=10, fill="x")
        
        # Fila 1: Etiqueta
        self.mode_label = customtkinter.CTkLabel(sync_mode_frame, text=self._("sync_mode_label"), font=("Arial", 12, "bold"))
        self.mode_label.pack(pady=(10, 5))
        
        # Fila 2: Radio Buttons
        radios_frame = customtkinter.CTkFrame(sync_mode_frame, fg_color="transparent")
        radios_frame.pack(pady=5)
        
        self.sync_mode = customtkinter.StringVar(value="safe")
        self.safe_radio = customtkinter.CTkRadioButton(radios_frame, text=self._("safe_mode_radio"), variable=self.sync_mode, value="safe", command=self.on_sync_mode_change)
        self.safe_radio.pack(side="left", padx=15)
        self.mirror_radio = customtkinter.CTkRadioButton(radios_frame, text=self._("mirror_mode_radio"), variable=self.sync_mode, value="mirror", command=self.on_sync_mode_change)
        self.mirror_radio.pack(side="left", padx=15)
        self.dry_run_radio = customtkinter.CTkRadioButton(radios_frame, text=self._("dry_run_mode_radio"), variable=self.sync_mode, value="dry_run", command=self.on_sync_mode_change)
        self.dry_run_radio.pack(side="left", padx=15)
        
        # Fila 3: Compatibilidad (Centrado debajo de radios)
        self.compatibility_mode_var = customtkinter.StringVar(value="off")
        self.compatibility_mode_check = customtkinter.CTkCheckBox(sync_mode_frame, text=self._("compatibility_mode_check"), variable=self.compatibility_mode_var, onvalue="on", offvalue="off")
        self.compatibility_mode_check.pack(pady=(5, 10))
        
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
            # Intentar UTF-8 primero, luego Latin-1 (común en Excel de Windows)
            try:
                df_headers = pd.read_csv(self.csv_path, nrows=0, encoding='utf-8').columns.tolist()
            except UnicodeDecodeError:
                df_headers = pd.read_csv(self.csv_path, nrows=0, encoding='latin-1').columns.tolist()
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

    def export_products_thread(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")],
            title=self._("export_csv_button"),
            initialfile="productos_exportados.csv"
        )
        if not filepath:
            return

        thread = threading.Thread(target=self.export_products, args=(filepath,))
        thread.daemon = True
        thread.start()

    def export_products(self, filepath):
        if not self.api_client:
            self.log("ERROR", self._("error_connection_failed"))
            return

        self.log("INFO", self._("log_export_starting"))
        try:
            # 1. Obtener todos los productos
            products = self.api_client.get_all_products()
            
            # 2. Aplanar datos para CSV
            flattened_products = []
            for p in products:
                # Convertir listas a strings separados por coma
                categories = ", ".join([c['name'] for c in p.get('categories', [])])
                tags = ", ".join([t['name'] for t in p.get('tags', [])])
                images = ", ".join([i['src'] for i in p.get('images', [])])
                
                # Extraer dimensiones
                dims = p.get('dimensions', {})
                
                # Extraer meta data
                meta_fields = {}
                for m in p.get('meta_data', []):
                    # Solo exportamos meta keys que no sean "privadas" (empiezan con _)
                    if not m['key'].startswith('_'):
                        meta_fields[f"meta: {m['key']}"] = m['value']

                item = {
                    'ID': p.get('id'),
                    'Name': p.get('name'),
                    'SKU': p.get('sku'),
                    'Regular price': p.get('regular_price'),
                    'Sale price': p.get('sale_price'),
                    'Description': p.get('description'),
                    'Short description': p.get('short_description'),
                    'Stock': p.get('stock_quantity'),
                    'Weight': p.get('weight'),
                    'Length': dims.get('length'),
                    'Width': dims.get('width'),
                    'Height': dims.get('height'),
                    'Categories': categories,
                    'Tags': tags,
                    'Images': images,
                    **meta_fields # Añadir campos meta dinámicos
                }
                flattened_products.append(item)

            # 3. Guardar con Pandas
            df = pd.DataFrame(flattened_products)
            
            # Reordenar columnas para que las importantes estén primero
            first_cols = ['ID', 'SKU', 'Name', 'Regular price', 'Sale price', 'Stock']
            existing_cols = [c for c in first_cols if c in df.columns]
            other_cols = [c for c in df.columns if c not in first_cols]
            df = df[existing_cols + other_cols]

            df.to_csv(filepath, index=False, encoding='utf-8-sig')  # BOM para Excel
            self.log("SUCCESS", self._("log_export_success").format(filepath=filepath))
            
        except PermissionError:
            self.log("ERROR", f"No se puede escribir el archivo. Asegúrate de que no esté abierto en Excel u otra aplicación: {filepath}")
        except Exception as e:
            self.log("ERROR", self._("log_export_error").format(e=e))

    def on_sync_mode_change(self):
        if self.sync_mode.get() == "mirror":
            self.warning_label.configure(text=self._("mirror_mode_warning"))
            self.start_sync_button.configure(fg_color="red", hover_color="darkred")
        elif self.sync_mode.get() == "dry_run":
            self.warning_label.configure(text=self._("dry_run_mode_info"), text_color="cyan")
            self.start_sync_button.configure(fg_color=("#2B8C5A", "#1B5C3A"), hover_color=("#1F6D42", "#0F3D22"))
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
            # Intentar UTF-8 primero, luego Latin-1 (común en Excel de Windows)
            try:
                df = pd.read_csv(self.csv_path, dtype=str, encoding='utf-8').fillna('')
            except UnicodeDecodeError:
                self.log("INFO", "CSV no está en UTF-8, intentando con Latin-1...")
                df = pd.read_csv(self.csv_path, dtype=str, encoding='latin-1').fillna('')
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

        # Lógica Modo Dry Run
        if self.sync_mode.get() == "dry_run":
            self.run_dry_run_simulation(df, user_mapping, store_sku_to_id_map)
            return

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

    def run_dry_run_simulation(self, df, user_mapping, store_sku_to_id_map):
        """Simula la sincronización sin hacer cambios reales, mostrando resumen."""
        self.log("INFO", "="*50)
        self.log("INFO", self._("dry_run_summary_title"))
        self.log("INFO", "="*50)
        
        csv_skus = set()
        products_to_create = []
        products_to_update = []
        images_to_upload = set()
        
        for index, row in df.iterrows():
            sku = row.get(user_mapping.get('SKU'), '').strip()
            if not sku:
                continue
            csv_skus.add(sku)
            
            # Simular construcción de payload
            product_data = build_product_payload(
                row=row,
                user_mapping=user_mapping,
                api_field_map=self.API_FIELD_MAP,
                image_folder_path=None,  # No subir imágenes en dry run
                upload_image_func=None,
                image_cache=None,
                log=None
            )
            
            # Detectar imágenes que se subirían
            for gui_field, csv_column in user_mapping.items():
                if self.API_FIELD_MAP.get(gui_field) == 'images':
                    value = row.get(csv_column, '')
                    if value and not pd.isna(value):
                        for img_name in str(value).split(','):
                            img_name = img_name.strip()
                            if img_name and not img_name.lower().startswith('http'):
                                images_to_upload.add(img_name)
            
            if sku in store_sku_to_id_map:
                products_to_update.append(sku)
            else:
                products_to_create.append(sku)
        
        # Calcular productos a eliminar (solo en modo espejo)
        products_to_delete = []
        if self.sync_mode.get() == "mirror":
            products_to_delete = list(set(store_sku_to_id_map.keys()) - csv_skus)
        
        # Mostrar resumen
        self.log("SUCCESS", self._("dry_run_products_to_create").format(count=len(products_to_create)))
        if products_to_create[:5]:
            for sku in products_to_create[:5]:
                self.log("INFO", f"  - {sku}")
            if len(products_to_create) > 5:
                self.log("INFO", f"  ... y {len(products_to_create) - 5} más")
        
        self.log("SUCCESS", self._("dry_run_products_to_update").format(count=len(products_to_update)))
        if products_to_update[:5]:
            for sku in products_to_update[:5]:
                self.log("INFO", f"  - {sku}")
            if len(products_to_update) > 5:
                self.log("INFO", f"  ... y {len(products_to_update) - 5} más")
        
        if products_to_delete:
            self.log("WARN", self._("dry_run_products_to_delete").format(count=len(products_to_delete)))
            for sku in products_to_delete[:5]:
                self.log("WARN", f"  - {sku}")
            if len(products_to_delete) > 5:
                self.log("WARN", f"  ... y {len(products_to_delete) - 5} más")
        else:
            self.log("INFO", self._("dry_run_products_to_delete").format(count=0))
        
        if self.image_folder_path:
            self.log("INFO", self._("dry_run_images_to_upload").format(count=len(images_to_upload)))
            if len(images_to_upload) > 0:
                for img in list(images_to_upload)[:5]:
                    self.log("INFO", f"  - {img}")
                if len(images_to_upload) > 5:
                    self.log("INFO", f"  ... y {len(images_to_upload) - 5} más")
        
        self.log("INFO", "="*50)
        self.log("SUCCESS", self._("dry_run_completed"))
        self.log("INFO", "="*50)
        self.finalize_sync(success=True)

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

            product_data = build_product_payload(
                row=row,
                user_mapping=user_mapping,
                api_field_map=self.API_FIELD_MAP,
                image_folder_path=self.image_folder_path,
                upload_image_func=self.api_client.upload_image,
                image_cache=self.image_cache,
                log=self.log
            )

            self.log("INFO", self._("log_processing_sku").format(current=index + 1, total=total_products, sku=sku))

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

            product_data = build_product_payload(
                row=row,
                user_mapping=user_mapping,
                api_field_map=self.API_FIELD_MAP,
                image_folder_path=self.image_folder_path,
                upload_image_func=self.api_client.upload_image,
                image_cache=self.image_cache,
                log=self.log
            )

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