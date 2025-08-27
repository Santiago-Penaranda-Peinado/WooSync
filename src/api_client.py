# src/api_client.py

import requests
from requests.auth import HTTPBasicAuth

class WooCommerceAPI:
    """
    Gestiona toda la comunicación con la API REST de WooCommerce.
    """
    def __init__(self, base_url, username, app_password):
        self.base_url = f"{base_url}/wp-json/wc/v3"
        self.wp_base_url = f"{base_url}/wp-json/wp/v2"
        # Usamos HTTPBasicAuth con el usuario y la contraseña de aplicación
        self.auth = HTTPBasicAuth(username, app_password)
        self.headers = {'Content-Type': 'application/json'}

    def check_connection(self):
        """Verifica si la conexión y las credenciales con la API son correctas."""
        try:
            # Usamos self.auth que ahora es HTTPBasicAuth
            response = requests.get(f"{self.base_url}/products", auth=self.auth, params={'per_page': 1})
            response.raise_for_status()
            print("¡Conexión con la API de WooCommerce exitosa!")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión con la API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Detalles del error: {e.response.text}")
            return False

    def get_product_by_sku(self, sku):
        """Busca un producto en WooCommerce por su SKU."""
        try:
            response = requests.get(f"{self.base_url}/products", auth=self.auth, params={'sku': sku})
            response.raise_for_status()
            products = response.json()
            return products[0] if products else None
        except requests.exceptions.RequestException as e:
            print(f"Error al buscar el producto con SKU {sku}: {e}")
            return None

    def create_product(self, product_data):
        """Crea un nuevo producto en WooCommerce."""
        try:
            response = requests.post(
                f"{self.base_url}/products",
                auth=self.auth,
                headers=self.headers,
                json=product_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al CREAR el producto: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Detalles del error: {e.response.text}")
            return None

    def update_product(self, product_id, product_data):
        """Actualiza un producto existente en WooCommerce."""
        try:
            response = requests.put(
                f"{self.base_url}/products/{product_id}",
                auth=self.auth,
                headers=self.headers,
                json=product_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al ACTUALIZAR el producto con ID {product_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Detalles del error: {e.response.text}")
            return None

    def upload_image(self, image_path, image_name):
        """
        Sube una imagen a la Biblioteca de Medios de WordPress.
        Usa autenticación HTTP Basic Auth.
        """
        media_url = f"{self.wp_base_url}/media"
        
        try:
            with open(image_path, 'rb') as f:
                headers = {
                    'Content-Disposition': f'attachment; filename={image_name}'
                }
                # Usamos self.auth (HTTPBasicAuth) en lugar de parámetros de query string
                response = requests.post(
                    media_url,
                    auth=self.auth,
                    headers=headers,
                    files={'file': (image_name, f)}
                )
            response.raise_for_status()
            print(f"  -> Imagen '{image_name}' subida exitosamente.")
            return response.json()
        except FileNotFoundError:
            print(f"  -> ERROR: No se encontró el archivo de imagen en la ruta: {image_path}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"  -> ERROR al subir la imagen: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  -> Detalles del error: {e.response.text}")
            return None

    def get_all_products(self):
        """
        Obtiene una lista completa de todos los productos de la tienda.
        Maneja la paginación para obtener más de 100 productos.
        """
        all_products = []
        page = 1
        per_page = 100 # Máximo que permite la API por página
        
        while True:
            try:
                params = {'per_page': per_page, 'page': page}
                response = requests.get(f"{self.base_url}/products", auth=self.auth, params=params)
                response.raise_for_status()
                products = response.json()
                
                if not products:
                    break # Si no hay más productos, salimos del bucle
                
                all_products.extend(products)
                page += 1
            except requests.exceptions.RequestException as e:
                print(f"Error al obtener la página {page} de productos: {e}")
                return None # Devolvemos None si hay un error
        
        return all_products

    def delete_product(self, product_id):
        """
        Elimina permanentemente un producto por su ID.
        
        Args:
            product_id (int): El ID del producto a eliminar.
            
        Returns:
            bool: True si se eliminó con éxito, False si no.
        """
        try:
            # force=true es para eliminar permanentemente en vez de enviar a la papelera
            response = requests.delete(f"{self.base_url}/products/{product_id}", auth=self.auth, params={'force': True})
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error al ELIMINAR el producto con ID {product_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Detalles del error: {e.response.text}")
            return False