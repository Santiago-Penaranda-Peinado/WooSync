# src/api_client.py

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException, Timeout
import logging
import time

# Logger con nombre para evitar conflictos
logger = logging.getLogger('woosync.api')
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class WooCommerceAPI:
    """
    Gestiona toda la comunicación con la API REST de WooCommerce.
    """
    def __init__(self, base_url, username, app_password):
        self.base_url = f"{base_url}/wp-json/wc/v3"
        self.wp_base_url = f"{base_url}/wp-json/wp/v2"
        self.auth = HTTPBasicAuth(username, app_password)
        self.headers = {'Content-Type': 'application/json'}
        self.default_timeout = 60
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update(self.headers)
        self.max_retries = 3
        self.retry_delay = 1  # segundos

    def _request_with_retry(self, method, url, **kwargs):
        """Ejecuta petición HTTP con reintentos y backoff exponencial."""
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except (RequestException, Timeout) as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Intento {attempt + 1} falló: {e}. Reintentando en {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise  # Último intento, propagar excepción
        return None

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
        
        logger.error(error_details)
        return {'error': error_details}

    def check_connection(self):
        """Verifica si la conexión y las credenciales con la API son correctas."""
        try:
            response = self._request_with_retry(
                'GET',
                f"{self.base_url}/products",
                params={'per_page': 1},
                timeout=self.default_timeout
            )
            logger.info("¡Conexión con la API de WooCommerce exitosa!")
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
                response = self._request_with_retry(
                    'GET',
                    f"{self.base_url}/products",
                    params=params,
                    timeout=120
                )
                products = response.json()
                if not products: break
                all_products.extend(products)
                if len(products) < per_page: break
                page += 1
            except (RequestException, Timeout) as e:
                return self._handle_error(e, f"Error al obtener la pág {page} de productos")
        return all_products

    def process_batch(self, batch_data):
        """Procesa un lote de productos para crear, actualizar o eliminar."""
        if not any(batch_data.values()): return None
        try:
            response = self._request_with_retry(
                'POST',
                f"{self.base_url}/products/batch",
                json=batch_data,
                timeout=180
            )
            return response.json()
        except (RequestException, Timeout) as e:
            return self._handle_error(e, "Error al procesar el lote de productos")

    def upload_image(self, image_path, image_name):
        """Sube una imagen a la Biblioteca de Medios de WordPress."""
        try:
            with open(image_path, 'rb') as f:
                file_content = f.read()
            headers = {'Content-Disposition': f'attachment; filename={image_name}'}
            headers.update(self.session.headers)
            response = self._request_with_retry(
                'POST',
                f"{self.wp_base_url}/media",
                headers=headers,
                files={'file': (image_name, file_content)},
                timeout=self.default_timeout
            )
            return response.json()
        except FileNotFoundError:
            return self._handle_error(FileNotFoundError(f"No se encontró el archivo: {image_path}"), f"Error al subir '{image_name}'")
        except (RequestException, Timeout) as e:
            return self._handle_error(e, f"Error al subir la imagen '{image_name}'")

    def create_product(self, product_data):
        """Crea un nuevo producto en WooCommerce."""
        try:
            response = self._request_with_retry(
                'POST',
                f"{self.base_url}/products",
                json=product_data,
                timeout=self.default_timeout
            )
            return response.json()
        except (RequestException, Timeout) as e:
            return self._handle_error(e, "Error al CREAR el producto")

    def update_product(self, product_id, product_data):
        """Actualiza un producto existente en WooCommerce."""
        try:
            response = self._request_with_retry(
                'PUT',
                f"{self.base_url}/products/{product_id}",
                json=product_data,
                timeout=self.default_timeout
            )
            return response.json()
        except (RequestException, Timeout) as e:
            return self._handle_error(e, f"Error al ACTUALIZAR el producto ID {product_id}")

    def delete_product(self, product_id):
        """Elimina permanentemente un producto por su ID."""
        try:
            response = self._request_with_retry(
                'DELETE',
                f"{self.base_url}/products/{product_id}",
                params={'force': True},
                timeout=self.default_timeout
            )
            return True
        except (RequestException, Timeout) as e:
            self._handle_error(e, f"Error al ELIMINAR el producto ID {product_id}")
            return False

    def close(self):
        """Cierra la sesión HTTP."""
        if self.session:
            self.session.close()
