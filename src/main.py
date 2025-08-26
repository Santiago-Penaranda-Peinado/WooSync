# src/main.py

import pandas as pd
import os
import getpass
from api_client import WooCommerceAPI

def load_products_from_csv(file_path):
    """Carga un archivo CSV en un DataFrame de pandas."""
    if not os.path.exists(file_path):
        print(f"Error: El archivo no se encontró en la ruta: {file_path}")
        return None
    try:
        df = pd.read_csv(file_path, dtype=str).fillna('')
        print("¡Archivo CSV cargado exitosamente!")
        return df
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo: {e}")
        return None

def main():
    """Función principal del script."""
    print("Iniciando WooSync...")
    
    # --- Pedimos credenciales de usuario ---
    store_url = input("Introduce la URL de tu tienda (ej. https://tienda.com): ")
    username = input("Introduce tu nombre de usuario de WordPress: ")
    app_password = getpass.getpass("Pega tu Contraseña de Aplicación: ")

    # --- Inicializamos el cliente con las nuevas credenciales ---
    api = WooCommerceAPI(store_url, username, app_password)
    if not api.check_connection():
        print("No se pudo conectar. Revisa la URL, tu usuario y la contraseña de aplicación.")
        return

    csv_file_path = os.path.join('data', 'productos.csv')
    products_df = load_products_from_csv(csv_file_path)
    if products_df is None:
        return
        
    # ---  Pedir la carpeta de imágenes ---
    image_folder_path = input("Introduce la ruta a la carpeta que contiene tus imágenes: ")
    if not os.path.isdir(image_folder_path):
        print("La ruta proporcionada no es una carpeta válida. Operación cancelada.")
        return

 
    num_products_to_process = 1
    print(f"\nATENCIÓN: Este script está a punto de modificar datos en tu tienda.")
    print(f"Se procesará el PRIMER producto del archivo CSV.")
    first_product_name = products_df.head(1)['Name'].iloc[0]
    first_product_sku = products_df.head(1)['SKU'].iloc[0]
    print(f"  -> Producto de prueba: '{first_product_name}' (SKU: {first_product_sku})")
    
    user_confirmation = input("¿Estás seguro de que quieres continuar? (escribe 'si' para confirmar): ")
    if user_confirmation.lower() != 'si':
        print("Operación cancelada por el usuario.")
        return

    # --- Iterar y aplicar lógica ---
    for index, row in products_df.head(num_products_to_process).iterrows():
        sku = row.get('SKU', '').strip()
        product_name = row.get('Name', 'Sin Nombre')
        
        if not sku:
            print(f"  - Fila {index+2}: Omitida. SKU vacío.")
            continue

        print(f"\nProcesando producto: '{product_name}' (SKU: {sku})")
        
        # --- LÓGICA DE IMÁGENES ---
        image_id = None
        image_cell_content = row.get('Images', '')

        if image_cell_content.lower().startswith(('http://', 'https://')):
            print("  -> La imagen es una URL. Se ignorará y se mantendrá la imagen actual.")
        elif image_cell_content: # Si la celda no está vacía y no es una URL
            local_image_path = os.path.join(image_folder_path, image_cell_content)
            uploaded_image = api.upload_image(local_image_path, image_cell_content)
            if uploaded_image:
                image_id = uploaded_image['id']

        # --- Preparamos el payload ---
        product_data = {
            'name': product_name,
            'sku': sku,
            'regular_price': row.get('Regular price', ''),
            'short_description': row.get('Short description', ''),
            'type': 'simple'
        }
        
        # Solo añadimos la clave 'images' si hemos subido una nueva imagen
        if image_id:
            product_data['images'] = [{'id': image_id}]


        existing_product = api.get_product_by_sku(sku)
        
        if existing_product:
            product_id = existing_product['id']
            print(f"  -> El producto EXISTE (ID: {product_id}). Actualizando...")
            result = api.update_product(product_id, product_data)
            if result:
                print(f"  -> ¡ÉXITO! Producto actualizado.")
        else:
            print(f"  -> El producto es NUEVO. Creando...")
            result = api.create_product(product_data)
            if result:
                print(f"  -> ¡ÉXITO! Producto creado con ID: {result['id']}.")

if __name__ == "__main__":
    main()