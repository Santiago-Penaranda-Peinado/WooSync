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
    Soporta automáticamente enlaces permanentes "Simples" (query params) y "Bonitos" (path).
    """
    def __init__(self, base_url, username, app_password):
        self.site_url = base_url.rstrip('/')
        self.auth = HTTPBasicAuth(username, app_password)
        self.headers = {'Content-Type': 'application/json'}
        self.default_timeout = 60
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update(self.headers)
        self.max_retries = 3
        self.retry_delay = 1  # segundos
        
        # Flags de configuración
        self.use_legacy_permalinks = False # Se detectará automáticamente en check_connection

    def _build_url(self, endpoint, is_wp_api=False):
        """
        Construye la URL completa adaptándose a la configuración de permalinks.
        endpoint: ej. 'products', 'media', 'products/batch'
        """
        # Prefijos para rutas "Bonitas" (Pretty Permalinks)
        wc_path = "wp-json/wc/v3"
        wp_path = "wp-json/wp/v2"
        
        # Prefijos para rutas "Simples" (Legacy/Plain Permalinks)
        wc_query = "?rest_route=/wc/v3"
        wp_query = "?rest_route=/wp/v2"

        if not self.use_legacy_permalinks:
            # Modo Estándar: https://site.com/wp-json/wc/v3/products
            prefix = wp_path if is_wp_api else wc_path
            return f"{self.site_url}/{prefix}/{endpoint}"
        else:
            # Modo Legacy: https://site.com/?rest_route=/wc/v3/products
            prefix = wp_query if is_wp_api else wc_query
            # Nota: Si el endpoint ya tiene query params, esto podría requerir ajuste, 
            # pero la mayoría de endpoints base no los tienen.
            # Los frameworks suelen manejar ?rest_route=...&other_param=...
            separator = "&" if "?" in prefix else "?"
            return f"{self.site_url}/{prefix}/{endpoint}"

    def _request_with_retry(self, method, url, **kwargs):
        """Ejecuta petición HTTP con reintentos y backoff exponencial."""
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(method, url, **kwargs)
                # Si es 404, no reintentamos (es error de cliente, no de red), 
                # a menos que estemos en check_connection donde manejamos esto explícitamente.
                if response.status_code == 404:
                    response.raise_for_status() # Lanza excepción para ser capturada
                
                response.raise_for_status()
                return response
            except (RequestException, Timeout) as e:
                # No reintentar en errores 4xx (excepto timeouts) o si es el último intento
                is_client_error = isinstance(e, RequestException) and e.response is not None and 400 <= e.response.status_code < 500
                
                if is_client_error and e.response.status_code != 404:
                     # Errores 401, 403, 400 no se arreglan reintentando
                    raise 

                if attempt < self.max_retries - 1 and not (is_client_error and e.response.status_code == 404):
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Intento {attempt + 1} falló: {e}. Reintentando en {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise  # Último intento o error no recuperable, propagar excepción
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
        """
        Verifica la conexión y detecta automáticamente el tipo de Permalinks.
        """
        # 1. Intentar método estándar (Pretty Permalinks)
        self.use_legacy_permalinks = False
        url = self._build_url("products")
        logger.info(f"Probando conexión estándar: {url}")
        
        try:
            self._request_with_retry('GET', url, params={'per_page': 1}, timeout=self.default_timeout)
            logger.info("¡Conexión exitosa con Permalinks Estándar!")
            return True
        except RequestException as e:
            # Si falla con 404, probamos el método Legacy
            if e.response is not None and e.response.status_code == 404:
                logger.info("Fallo con 404. Probando modo Legacy (Query Params)...")
                self.use_legacy_permalinks = True
                url_legacy = self._build_url("products")
                logger.info(f"Probando conexión legacy: {url_legacy}")
                
                try:
                    self._request_with_retry('GET', url_legacy, params={'per_page': 1}, timeout=self.default_timeout)
                    logger.info("¡Conexión exitosa con Permalinks Legacy!")
                    return True
                except (RequestException, Timeout) as e2:
                    self._handle_error(e2, "Fallo también en modo Legacy")
                    return False
            else:
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
                url = self._build_url("products")
                
                # Manejo especial para query params en URL legacy si ya tiene '?'
                if self.use_legacy_permalinks and '?' in url:
                    # requests maneja params uniendo con & si ya hay query string? 
                    # Generalmente requests lo hace bien, pero asegurémonos.
                    # En requests, si pasas params={'a':1} y la url es http://...?x=y, lo convierte a ...?x=y&a=1
                    pass 

                response = self._request_with_retry(
                    'GET',
                    url,
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
            url = self._build_url("products/batch")
            response = self._request_with_retry(
                'POST',
                url,
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
            
            url = self._build_url("media", is_wp_api=True)
            
            response = self._request_with_retry(
                'POST',
                url,
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
            url = self._build_url("products")
            response = self._request_with_retry(
                'POST',
                url,
                json=product_data,
                timeout=self.default_timeout
            )
            return response.json()
        except (RequestException, Timeout) as e:
            return self._handle_error(e, "Error al CREAR el producto")

    def update_product(self, product_id, product_data):
        """Actualiza un producto existente en WooCommerce."""
        try:
            url = self._build_url(f"products/{product_id}")
            # Nota: En modo legacy, products/123 se convierte en ?rest_route=/wc/v3/products/123
            
            response = self._request_with_retry(
                'PUT',
                url,
                json=product_data,
                timeout=self.default_timeout
            )
            return response.json()
        except (RequestException, Timeout) as e:
            return self._handle_error(e, f"Error al ACTUALIZAR el producto ID {product_id}")

    def delete_product(self, product_id):
        """Elimina permanentemente un producto por su ID."""
        try:
            url = self._build_url(f"products/{product_id}")
            
            response = self._request_with_retry(
                'DELETE',
                url,
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
