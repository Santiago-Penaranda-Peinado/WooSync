import os
import pandas as pd

def parse_decimal(value):
    """Convierte valores numéricos (precio, dimensiones) a string decimal segura."""
    if value is None:
        return '0'
    if isinstance(value, (int, float)):
        return str(value)
    try:
        v = str(value).strip().replace(',', '.')
        return str(float(v))
    except (ValueError, TypeError):
        return '0'

def parse_int(value):
    """Convierte valores numéricos que deben ser enteros (stock)."""
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    try:
        v = str(value).strip().replace(',', '.')
        return int(float(v))
    except (ValueError, TypeError):
        return 0

def build_product_payload(row: pd.Series,
                          user_mapping: dict,
                          api_field_map: dict,
                          image_folder_path: str = None,
                          upload_image_func=None,
                          image_cache: dict = None,
                          log=None) -> dict:
    """
    Construye el diccionario product_data listo para enviar a la API, a partir de:
    - row: fila del DataFrame
    - user_mapping: mapeo GUI_field -> csv_column
    - api_field_map: mapa de nombres GUI a claves API
    - image_folder_path: carpeta donde buscar imágenes locales
    - upload_image_func: función para subir una imagen (path, nombre) -> {id: int} | {error: str}
    - image_cache: dict filename -> id para evitar subidas duplicadas
    - log: función para registrar mensajes (nivel, texto)
    """

    product_data = {'type': 'simple'}
    meta_data = []
    dimensions = {}

    for gui_field, csv_column in user_mapping.items():
        value = row.get(csv_column, '')
        if pd.isna(value) or value == '':
            continue
        api_key = api_field_map.get(gui_field)

        # Campos meta
        if gui_field.startswith('meta:'):
            meta_key = gui_field.split(':', 1)[1].strip().replace('[', '').replace(']', '')
            if meta_key:
                meta_data.append({'key': meta_key, 'value': value})
            continue

        # Categorías / Tags
        if api_key in ['categories', 'tags']:
            entries = []
            if isinstance(value, str):
                entries = [v.strip() for v in value.split(',') if v.strip()]
            elif isinstance(value, list):
                entries = [str(v).strip() for v in value if str(v).strip()]
            if entries:
                product_data[api_key] = [{'name': e} for e in entries]
            continue

        # Dimensiones
        if api_key in ['length', 'width', 'height']:
            dimensions[api_key] = parse_decimal(value)
            continue

        # Imágenes
        if api_key == 'images':
            if not image_folder_path or not upload_image_func:
                continue
            image_ids = []
            for img_name in str(value).split(','):
                img_name = img_name.strip()
                if not img_name or img_name.lower().startswith('http'):
                    continue
                # Cache
                cached_id = image_cache.get(img_name) if image_cache else None
                if cached_id:
                    image_ids.append({'id': cached_id})
                    continue
                image_path = os.path.join(image_folder_path, img_name)
                uploaded = upload_image_func(image_path, img_name)
                if uploaded and 'id' in uploaded:
                    image_ids.append({'id': uploaded['id']})
                    if image_cache is not None:
                        image_cache[img_name] = uploaded['id']
                elif uploaded and 'error' in uploaded and log:
                    log('ERROR', f"Subiendo '{img_name}': {uploaded['error']}")
            if image_ids:
                product_data['images'] = image_ids
            continue

        # Precios, stock u otros campos básicos
        if api_key:
            if api_key in ['regular_price', 'sale_price']:
                product_data[api_key] = parse_decimal(value)
            elif api_key == 'stock_quantity':
                product_data[api_key] = parse_int(value)
            else:
                product_data[api_key] = value

    if dimensions:
        product_data['dimensions'] = dimensions
    if meta_data:
        product_data['meta_data'] = meta_data
    return product_data
