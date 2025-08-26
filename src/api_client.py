# src/api_client.py

import requests

class WooCommerceAPI:
    """
    Gestiona toda la comunicación con la API REST de WooCommerce.
    """
    def __init__(self, base_url, consumer_key, consumer_secret):
        """
        Inicializa el cliente de la API.

        Args:
            base_url (str): La URL de tu tienda (ej. "https://tienda.com").
            consumer_key (str): La clave de consumidor de la API de WooCommerce.
            consumer_secret (str): El secreto de consumidor de la API de WooCommerce.
        """
        self.base_url = f"{base_url}/wp-json/wc/v3"
        self.auth = (consumer_key, consumer_secret)

    def check_connection(self):
        """
        Verifica si la conexión y las credenciales con la API son correctas.
        """
        try:
            response = requests.get(f"{self.base_url}/products", auth=self.auth, params={'per_page': 1})
            # Lanza un error si la respuesta es 4xx o 5xx
            response.raise_for_status()
            print("¡Conexión con la API de WooCommerce exitosa!")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión con la API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Detalles del error: {e.response.text}")
            return False

    def get_product_by_sku(self, sku):
        """
        Busca un producto en WooCommerce por su SKU.

        Args:
            sku (str): El SKU del producto a buscar.

        Returns:
            dict: Los datos del producto si se encuentra, o None si no se encuentra.
        """
        try:
            response = requests.get(f"{self.base_url}/products", auth=self.auth, params={'sku': sku})
            response.raise_for_status()
            products = response.json()
            # Si la lista de productos no está vacía, devuelve el primero
            if products:
                return products[0]
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error al buscar el producto con SKU {sku}: {e}")
            return None