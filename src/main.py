import pandas as pd
import os

def load_products_from_csv(file_path):
    """
    Carga un archivo CSV en un DataFrame de pandas.
    """
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
    """
    Función principal del script.
    """
    print("Iniciando WooSync...")
    
    # Construimos la ruta al archivo de datos de forma relativa
    # Esto asume que ejecutas el script desde la carpeta raíz 'woosync/'
    csv_file_path = os.path.join('data', 'productos.csv') # Asegúrate de que el nombre coincida

    products_df = load_products_from_csv(csv_file_path)
    
    if products_df is not None:
        print("\nMostrando las primeras 5 filas del archivo:")
        # Usamos .head() para ver una vista previa de los datos
        print(products_df.head())
        
        print(f"\nSe encontraron {len(products_df)} productos en el archivo.")

if __name__ == "__main__":
    main()