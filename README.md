# WooSync v1.0

WooSync es una aplicación de escritorio desarrollada en Python que facilita la sincronización masiva de productos entre un archivo CSV y una tienda WooCommerce. La herramienta permite crear, actualizar y eliminar productos, incluyendo el manejo avanzado de imágenes locales, a través de una interfaz gráfica de usuario intuitiva.

Este proyecto fue desarrollado para solucionar las ineficiencias de los métodos de importación manuales, ofreciendo una solución robusta, segura y personalizable para la gestión de catálogos de WooCommerce.

## Características Principales

- **Conexión Segura:** Utiliza el sistema de "Contraseñas de Aplicación" de WordPress para una autenticación segura con la API REST.
- **Mapeo de Campos Inteligente:**
    - Detecta automáticamente las columnas de cualquier archivo CSV.
    - Intenta mapear inteligentemente las columnas del CSV con los campos de WooCommerce.
    - Ofrece plantillas de mapeo rápido ("Básico", "Mapear Todo", "Limpiar") para acelerar el proceso.
    - El usuario tiene control total para ajustar el mapeo manualmente.
- **Manejo Avanzado de Imágenes:** Sube imágenes desde una carpeta local y las asigna a productos nuevos o existentes, algo que las herramientas nativas no permiten fácilmente.
- **Dos Modos de Sincronización:**
    - **Modo Seguro (Por defecto):** Crea productos nuevos y actualiza los existentes basándose en el SKU. Nunca elimina productos.
    - **Modo Espejo (Destructivo):** Sincroniza la tienda para que sea un reflejo exacto del CSV. **Elimina** de la tienda cualquier producto que no se encuentre en el archivo. Incluye múltiples advertencias de seguridad.
- **Generador de Plantillas:** Permite descargar un archivo CSV simplificado con las columnas esenciales para facilitar la creación de nuevos productos desde cero.
- **Feedback en Tiempo Real:** Un cuadro de log en la interfaz muestra el progreso de la sincronización, los éxitos y los errores en tiempo real.

## Captura de Pantalla

*(Aquí puedes añadir la captura de pantalla que me enviaste: `image_3d7b53.png`)*
![Interfaz de WooSync](https://i.imgur.com/your-image-url.png)

## Requisitos

- Python 3.8 o superior
- Una tienda WordPress con el plugin WooCommerce activado.
- Permisos de administrador en la tienda para generar "Contraseñas de Aplicación".

## Instalación (Para Windows)

1.  **Clonar el Repositorio:**
    ```bash
    git clone [URL-de-tu-repositorio-en-GitHub]
    cd WooSync
    ```

2.  **Instalar Python:**
    Si no tienes Python, descárgalo desde [python.org](https://www.python.org/downloads/). **Importante:** Durante la instalación, asegúrate de marcar la casilla "Add Python.exe to PATH".

3.  **Crear y Activar el Entorno Virtual:**
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
    Si PowerShell bloquea la ejecución del script, ábrelo como Administrador una vez y ejecuta:
    `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

4.  **Instalar las Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Archivos del Proyecto

- `src/app_gui.py`: Contiene toda la lógica de la interfaz gráfica y el motor de procesamiento.
- `src/api_client.py`: Contiene la clase `WooCommerceAPI` que gestiona toda la comunicación con WordPress.
- `requirements.txt`: Lista las librerías de Python necesarias para el proyecto.

## Modo de Uso

1.  **Ejecutar la Aplicación:**
    ```bash
    python src/app_gui.py
    ```

2.  **Conectar a la Tienda:**
    - Introduce la URL completa de tu sitio (ej: `https://tienda.com`).
    - Introduce tu nombre de usuario de WordPress (el que tiene rol de Administrador).
    - Pega la "Contraseña de Aplicación" que generaste en tu perfil de usuario de WordPress.
    - Haz clic en "Conectar".

3.  **Preparar la Sincronización:**
    - **Paso 1:** Selecciona tu archivo CSV de productos. La interfaz de mapeo se generará automáticamente.
    - **Paso 2:** Selecciona la carpeta de tu PC que contiene las imágenes de los productos.
    - **Paso 3:** Revisa el mapeo de columnas. Ajusta los menús desplegables según sea necesario o usa los botones de plantillas rápidas. **El campo `SKU` es obligatorio.**

4.  **Seleccionar Modo y Sincronizar:**
    - Elige el "Modo Seguro" o el "Modo Espejo". Presta atención a las advertencias si eliges el Modo Espejo.
    - Haz clic en "Iniciar Sincronización" y observa el progreso en el cuadro de log.

## Próximas Mejoras (Roadmap)

- [ ] **Versión 2.0:** Implementar la API de Lotes (Batch API) de WooCommerce para mejorar drásticamente la velocidad de sincronización en catálogos grandes.
- [ ] **Versión 2.1:** Añadir soporte para Productos Variables.
- [ ] **Versión 2.2:** Hacer que la aplicación "aprenda" de la tienda, obteniendo categorías y atributos existentes para un mapeo y validación de datos más inteligentes.
- [ ] **Versión 3.0:** Empaquetar la aplicación en un archivo `.exe` con PyInstaller para su distribución en equipos sin Python.