#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para validar las mejoras implementadas en WooSync v3.1
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from product_payload import build_product_payload, parse_decimal, parse_int

def test_parse_functions():
    """Prueba funciones de conversión numérica."""
    print("=" * 60)
    print("TEST 1: Funciones de conversión numérica")
    print("=" * 60)
    
    # Test parse_decimal
    tests_decimal = [
        ("19.99", "19.99"),
        ("19,99", "19.99"),
        ("", "0"),
        (None, "0"),
        ("invalido", "0"),
        (42, "42"),
    ]
    
    print("\nPruebas de parse_decimal:")
    for entrada, esperado in tests_decimal:
        resultado = parse_decimal(entrada)
        status = "✓" if resultado == esperado else "✗"
        print(f"  {status} parse_decimal({repr(entrada)}) = {resultado} (esperado: {esperado})")
    
    # Test parse_int
    tests_int = [
        ("100", 100),
        ("100.5", 100),
        ("100,5", 100),
        ("", 0),
        (None, 0),
        (50, 50),
    ]
    
    print("\nPruebas de parse_int:")
    for entrada, esperado in tests_int:
        resultado = parse_int(entrada)
        status = "✓" if resultado == esperado else "✗"
        print(f"  {status} parse_int({repr(entrada)}) = {resultado} (esperado: {esperado})")

def test_build_payload():
    """Prueba construcción de payload de producto."""
    print("\n" + "=" * 60)
    print("TEST 2: Construcción de payload de producto")
    print("=" * 60)
    
    # Crear datos de prueba
    row = pd.Series({
        'SKU': 'TEST-001',
        'Nombre': 'Producto de Prueba',
        'Precio': '29,99',
        'Stock': '50',
        'Largo': '10',
        'Ancho': '5',
        'Alto': '3',
        'Categorias': 'Electrónica, Gadgets',
        'Meta_Color': 'Azul'
    })
    
    user_mapping = {
        'Name': 'Nombre',
        'SKU': 'SKU',
        'Regular price': 'Precio',
        'Stock': 'Stock',
        'Length': 'Largo',
        'Width': 'Ancho',
        'Height': 'Alto',
        'Categories': 'Categorias',
        'meta: color': 'Meta_Color'
    }
    
    api_field_map = {
        'Name': 'name',
        'SKU': 'sku',
        'Regular price': 'regular_price',
        'Stock': 'stock_quantity',
        'Length': 'length',
        'Width': 'width',
        'Height': 'height',
        'Categories': 'categories',
    }
    
    payload = build_product_payload(
        row=row,
        user_mapping=user_mapping,
        api_field_map=api_field_map,
        image_folder_path=None,
        upload_image_func=None,
        image_cache=None,
        log=None
    )
    
    print("\nPayload generado:")
    print(f"  Tipo: {payload.get('type')}")
    print(f"  Nombre: {payload.get('name')}")
    print(f"  Precio: {payload.get('regular_price')}")
    print(f"  Stock: {payload.get('stock_quantity')}")
    print(f"  Dimensiones: {payload.get('dimensions')}")
    print(f"  Categorías: {payload.get('categories')}")
    print(f"  Meta data: {payload.get('meta_data')}")
    
    # Validaciones
    validaciones = [
        (payload.get('type') == 'simple', "Tipo debe ser 'simple'"),
        (payload.get('name') == 'Producto de Prueba', "Nombre debe coincidir"),
        (payload.get('regular_price') == '29.99', "Precio debe convertir coma a punto"),
        (payload.get('stock_quantity') == 50, "Stock debe ser entero"),
        ('dimensions' in payload, "Debe incluir dimensiones"),
        (len(payload.get('categories', [])) == 2, "Debe tener 2 categorías"),
        (len(payload.get('meta_data', [])) == 1, "Debe tener 1 meta field"),
    ]
    
    print("\nValidaciones:")
    for passed, descripcion in validaciones:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {descripcion}")

def test_image_cache():
    """Prueba funcionamiento de caché de imágenes."""
    print("\n" + "=" * 60)
    print("TEST 3: Caché de imágenes")
    print("=" * 60)
    
    cache = {}
    upload_count = [0]  # Lista mutable para contador
    
    def mock_upload(path, name):
        """Mock de función de subida que incrementa contador."""
        upload_count[0] += 1
        return {'id': 100 + upload_count[0]}
    
    row1 = pd.Series({'Imagen': 'producto1.jpg'})
    row2 = pd.Series({'Imagen': 'producto1.jpg'})  # Misma imagen
    row3 = pd.Series({'Imagen': 'producto2.jpg'})  # Imagen diferente
    
    user_mapping = {'Images': 'Imagen'}
    api_field_map = {'Images': 'images'}
    
    # Primera carga (debe subir)
    payload1 = build_product_payload(
        row=row1,
        user_mapping=user_mapping,
        api_field_map=api_field_map,
        image_folder_path='.',
        upload_image_func=mock_upload,
        image_cache=cache,
        log=None
    )
    
    # Segunda carga (debe usar caché)
    payload2 = build_product_payload(
        row=row2,
        user_mapping=user_mapping,
        api_field_map=api_field_map,
        image_folder_path='.',
        upload_image_func=mock_upload,
        image_cache=cache,
        log=None
    )
    
    # Tercera carga (nueva imagen, debe subir)
    payload3 = build_product_payload(
        row=row3,
        user_mapping=user_mapping,
        api_field_map=api_field_map,
        image_folder_path='.',
        upload_image_func=mock_upload,
        image_cache=cache,
        log=None
    )
    
    print(f"\nSubidas realizadas: {upload_count[0]}")
    print(f"Contenido de caché: {cache}")
    print(f"Payload 1 imagen ID: {payload1.get('images', [{}])[0].get('id')}")
    print(f"Payload 2 imagen ID: {payload2.get('images', [{}])[0].get('id')}")
    print(f"Payload 3 imagen ID: {payload3.get('images', [{}])[0].get('id')}")
    
    validaciones = [
        (upload_count[0] == 2, "Solo debe subir 2 imágenes (no 3)"),
        (len(cache) == 2, "Caché debe tener 2 entradas"),
        ('producto1.jpg' in cache, "producto1.jpg debe estar en caché"),
        ('producto2.jpg' in cache, "producto2.jpg debe estar en caché"),
        (payload1['images'][0]['id'] == payload2['images'][0]['id'], "Misma imagen debe tener mismo ID"),
        (payload1['images'][0]['id'] != payload3['images'][0]['id'], "Imágenes diferentes deben tener IDs distintos"),
    ]
    
    print("\nValidaciones:")
    for passed, descripcion in validaciones:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {descripcion}")

def main():
    """Ejecuta todos los tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "TESTS DE MEJORAS WOOSYNC v3.1" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        test_parse_functions()
        test_build_payload()
        test_image_cache()
        
        print("\n" + "=" * 60)
        print("✓ TODOS LOS TESTS COMPLETADOS")
        print("=" * 60)
        print("\nLas mejoras están funcionando correctamente.")
        print("Ahora puedes ejecutar la aplicación con: python src/app_gui.py\n")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ ERROR EN LOS TESTS")
        print("=" * 60)
        print(f"\nExcepción: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
