# src/main.py

import pandas as pd
import os
import getpass  # Para pedir contraseñas de forma segura
from api_client import WooCommerceAPI # Importamos nuestra nueva clase

def load_products_from_csv(file_path):
    """Carga un archivo CSV en un DataFrame de pandas."""
    if not os.path.exists(file_path):
        print(f"Error: El archivo no se encontró en la ruta: {file_path}")
        return None
    try:
        df = pd.read_csv(file_path)
        print("¡Archivo CSV cargado exitosamente!")
        return df
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo: {e}")
        return None

def main():
    """Función principal del script."""
    print("Iniciando WooSync...")
    
    # --- Configuración de la API ---
    store_url = input("Introduce la URL de tu tienda (ej. https://tienda.com): ")
    consumer_key = input("Introduce tu Clave de Consumidor (CK): ")
    # getpass oculta lo que escribes para mayor seguridad
    consumer_secret = getpass.getpass("Introduce tu Secreto de Consumidor (CS): ")

    # --- Inicializar y verificar API ---
    api = WooCommerceAPI(store_url, consumer_key, consumer_secret)
    if not api.check_connection():
        print("No se pudo conectar a la tienda. Revisa la URL y las credenciales.")
        return # Termina el script si no hay conexión

    # --- Cargar el CSV ---
    csv_file_path = os.path.join('data', 'productos.csv')
    products_df = load_products_from_csv(csv_file_path)
    
    if products_df is None:
        return

    print(f"\nSe encontraron {len(products_df)} productos en el archivo. Iniciando simulación de sincronización...")
    
    # --- Iterar y aplicar lógica ---
    # Iteramos sobre las primeras 5 filas para una prueba rápida
    for index, row in products_df.head(5).iterrows():
        # Asegúrate de que el nombre de la columna 'SKU' sea correcto
        # Si tu columna se llama diferente, ajústalo aquí.
        sku = row.get('SKU')
        product_name = row.get('Name', 'Sin Nombre') # Usamos 'Name' como fallback
        
        if pd.isna(sku) or sku == '':
            print(f"  - Fila {index+2}: Omitida. El SKU está vacío para el producto '{product_name}'.")
            continue

        print(f"\nProcesando producto: '{product_name}' (SKU: {sku})")
        
        existing_product = api.get_product_by_sku(sku)
        
        if existing_product:
            # El producto ya existe
            product_id = existing_product['id']
            print(f"  -> Resultado: El producto EXISTE (ID: {product_id}). Se debería ACTUALIZAR.")
        else:
            # El producto es nuevo
            print(f"  -> Resultado: El producto es NUEVO. Se debería CREAR.")

if __name__ == "__main__":
    main()