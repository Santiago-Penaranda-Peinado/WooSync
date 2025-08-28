# VERSIÓN FINAL CON TIMEOUTS -
# src/api_client.py

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException, Timeout

class WooCommerceAPI:
    """
    Gestiona toda la comunicación con la API REST de WooCommerce.
    """
    def __init__(self, base_url, username, app_password):
        self.base_url = f"{base_url}/wp-json/wc/v3"
        self.wp_base_url = f"{base_url}/wp-json/wp/v2"
        self.auth = HTTPBasicAuth(username, app_password)
        self.headers = {'Content-Type': 'application/json'}
        # Timeout por defecto en segundos para la mayoría de las peticiones
        self.default_timeout = 60 

    def _handle_error(self, e, context_message):
        """Función centralizada para manejar y formatear errores de requests."""
        if isinstance(e, Timeout):
            error_details = f"{context_message}: La petición tardó demasiado en responder (Timeout)."
        else:
            error_details = f"{context_message}: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_json = e.response.json()
                    message = error_json.get('message', e.response.text)
                    error_details += f" | Mensaje de la API: {message}"
                except ValueError:
                    error_details += f" | Respuesta del servidor: {e.response.text}"
        
        print(error_details) # Para debugging en consola
        return {'error': error_details}

    def check_connection(self):
        """Verifica si la conexión y las credenciales con la API son correctas."""
        try:
            response = requests.get(f"{self.base_url}/products", auth=self.auth, params={'per_page': 1}, timeout=self.default_timeout)
            response.raise_for_status()
            print("¡Conexión con la API de WooCommerce exitosa!")
            return True
        except (RequestException, Timeout) as e:
            self._handle_error(e, "Error de conexión con la API")
            return False

    def get_all_products(self):
        """Obtiene una lista completa de todos los productos de la tienda."""
        all_products = []
        page = 1
        per_page = 100
        while True:
            try:
                params = {'per_page': per_page, 'page': page, 'status': 'any'}
                response = requests.get(f"{self.base_url}/products", auth=self.auth, params=params, timeout=120) 
                response.raise_for_status()
                products = response.json()
                if not products: break
                all_products.extend(products)
                if len(products) < per_page: break
                page += 1
            except (RequestException, Timeout) as e:
                # Modificado para devolver el diccionario de error en lugar de None
                return self._handle_error(e, f"Error al obtener la pág {page} de productos")
        return all_products

    def process_batch(self, batch_data):
        """Procesa un lote de productos para crear, actualizar o eliminar."""
        if not any(batch_data.values()): return None
        try:
            response = requests.post(f"{self.base_url}/products/batch", auth=self.auth, headers=self.headers, json=batch_data, timeout=180)
            response.raise_for_status()
            return response.json()
        except (RequestException, Timeout) as e:
            return self._handle_error(e, "Error al procesar el lote de productos")

    def upload_image(self, image_path, image_name):
        """Sube una imagen a la Biblioteca de Medios de WordPress."""
        try:
            with open(image_path, 'rb') as f:
                headers = {'Content-Disposition': f'attachment; filename={image_name}'}
                response = requests.post(f"{self.wp_base_url}/media", auth=self.auth, headers=headers, files={'file': (image_name, f)}, timeout=self.default_timeout)
            response.raise_for_status()
            return response.json()
        except FileNotFoundError:
            return self._handle_error(FileNotFoundError(f"No se encontró el archivo: {image_path}"), f"Error al subir '{image_name}'")
        except (RequestException, Timeout) as e:
            return self._handle_error(e, f"Error al subir la imagen '{image_name}'")

    def create_product(self, product_data):
        """Crea un nuevo producto en WooCommerce."""
        try:
            response = requests.post(f"{self.base_url}/products", auth=self.auth, headers=self.headers, json=product_data, timeout=self.default_timeout)
            response.raise_for_status()
            return response.json()
        except (RequestException, Timeout) as e:
            return self._handle_error(e, "Error al CREAR el producto")

    def update_product(self, product_id, product_data):
        """Actualiza un producto existente en WooCommerce."""
        try:
            response = requests.put(f"{self.base_url}/products/{product_id}", auth=self.auth, headers=self.headers, json=product_data, timeout=self.default_timeout)
            response.raise_for_status()
            return response.json()
        except (RequestException, Timeout) as e:
            return self._handle_error(e, f"Error al ACTUALIZAR el producto ID {product_id}")

    def delete_product(self, product_id):
        """Elimina permanentemente un producto por su ID."""
        try:
            response = requests.delete(f"{self.base_url}/products/{product_id}", auth=self.auth, params={'force': True}, timeout=self.default_timeout)
            response.raise_for_status()
            return True
        except (RequestException, Timeout) as e:
            self._handle_error(e, f"Error al ELIMINAR el producto ID {product_id}")
            return False
