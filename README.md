# WooSync v2.1

WooSync is a powerful desktop application developed in Python, designed to facilitate massive product synchronization between a CSV file and a WooCommerce store. The tool allows for creating, updating, and deleting products through an intuitive graphical user interface, including advanced handling of local images and different processing modes for maximum flexibility and safety.

This project was developed to address the inefficiencies of manual import methods, offering a robust, secure, and customizable solution for managing WooCommerce catalogs.

---

---
## Main Features

-   **Secure Connection:** Uses WordPress's "Application Passwords" system for secure authentication with the REST API.
-   **Batch Processing (Batch API):** Synchronizes products at high speed using WooCommerce's batch API, ideal for large catalogs.
-   **Compatibility Mode:** Offers a "one-by-one" synchronization mode, which is slower but extremely safe and compatible with shared hosting servers with limited resources.
-   **Intelligent Field Mapping:**
    -   Automatically detects columns from any CSV file.
    -   Intelligently attempts to map CSV columns to WooCommerce fields (including Name, SKU, Prices, Dimensions, etc.).
    -   Provides quick mapping presets ("Basic," "Map All," "Clear") to speed up the process.
    -   Supports mapping for custom fields (`meta_data`).
-   **Advanced Image Handling:** Uploads images from a local folder and assigns them to new or existing products, a key feature not easily handled by native tools.
-   **Two Synchronization Modes:**
    -   **Safe Mode (Default):** Creates new products and updates existing ones based on their SKU. It never deletes products from the store.
    -   **Mirror Mode (Destructive):** Synchronizes the store to be an exact reflection of the CSV file. It **deletes** any product from the store that is not found in the file. Includes multiple security warnings to prevent accidents.
-   **Template Generator:** Allows downloading an optimized CSV file with the most common columns to facilitate the creation of new catalogs from scratch.
-   **Real-Time Feedback:** A log box in the interface displays the detailed progress of the synchronization, successes, and errors in real-time, making it easy to debug any issues.

## Requirements

-   Python 3.8 or higher.
-   A WordPress store with the WooCommerce plugin activated.
-   Administrator permissions in the store to generate "Application Passwords."

## Installation (Windows)

1.  **Clone the Repository:**
    ```bash
    git clone [YOUR-GITHUB-REPO-URL]
    cd WooSync
    ```

2.  **Install Python:**
    If you don't have Python, download it from [python.org](https://www.python.org/downloads/). **Important:** During installation, make sure to check the "Add Python to PATH" box.

3.  **Create and Activate the Virtual Environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
    If PowerShell blocks script execution, open it as an Administrator and run: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Project Files

-   `src/app_gui.py`: Contains all the logic for the graphical user interface (CustomTkinter) and the processing engine.
-   `src/api_client.py`: Contains the `WooCommerceAPI` class that manages all communication with WordPress in a robust and secure manner.
-   `requirements.txt`: Lists the necessary Python libraries.
-   `main.py`: A development/test CLI script. Not intended for production use.

## How to Use

1.  **Run the Application:**
    ```bash
    python src/app_gui.py
    ```
2.  **Connect to the Store:** Enter your site's URL, your WordPress username, and an "Application Password".
3.  **Prepare for Synchronization:**
    -   **Step 1:** Select your CSV file. The mapping interface will be generated instantly.
    -   **Step 2 (Optional):** Select the folder on your PC that contains the product images.
    -   **Step 3:** Review the column mapping. Adjust the dropdown menus as needed. **The `SKU` field is mandatory.**
4.  **Select Mode and Synchronize:**
    -   Choose "Safe Mode" or "Mirror Mode."
    -   Enable "Compatibility Mode" if you are on a server with limited resources.
    -   Click "Start Synchronization" and watch the progress in the log.

## Future Improvements (Roadmap)

-   [ ] **Attribute Support:** Add mapping for product attributes (e.g., Color, Size), which is essential for selling varied products.
-   [ ] **Full Support for Variable Products:** Implement the logic to create and synchronize variable products with their respective variations (each with its own SKU, price, and attributes).
-   [ ] **Improved Batch Feedback:** Parse the response from the batch API to report exactly which products failed and why.
-   [ ] **Application Packaging:** Create an `.exe` executable with PyInstaller for easy distribution on computers without Python installed.

## Contact and Support

If you wish to contact me or voluntarily contribute to the project, you can do so through:

* **Instagram:** [@santiago.penaranda.75](https://www.instagram.com/santiago.penaranda.75?igsh=aGxzYTRlNnZoaHZh)
* **PayPal:** [Support the project here](https://paypal.me/santielpilo)

## Características Principales

-   **Conexión Segura:** Utiliza el sistema de "Contraseñas de Aplicación" de WordPress para una autenticación segura con la API REST.
-   **Procesamiento por Lotes (Batch API):** Sincroniza productos a alta velocidad utilizando la API de lotes de WooCommerce, ideal para catálogos grandes.
-   **Modo Compatible:** Ofrece un modo de sincronización "uno por uno", más lento pero extremadamente seguro y compatible con servidores de hosting con recursos limitados.
-   **Mapeo de Campos Inteligente:**
    -   Detecta automáticamente las columnas de cualquier archivo CSV.
    -   Intenta mapear inteligentemente las columnas del CSV con los campos de WooCommerce (incluyendo Nombre, SKU, Precios, Dimensiones, etc.).
    -   Ofrece plantillas de mapeo rápido ("Básico", "Mapear Todo", "Limpiar") para acelerar el proceso.
    -   Soporte para mapear campos personalizados (`meta_data`).
-   **Manejo Avanzado de Imágenes:** Sube imágenes desde una carpeta local y las asigna a productos nuevos o existentes, una funcionalidad clave que las herramientas nativas no manejan fácilmente.
-   **Dos Modos de Sincronización:**
    -   **Modo Seguro (Por defecto):** Crea productos nuevos y actualiza los existentes basándose en el SKU. Nunca elimina productos de la tienda.
    -   **Modo Espejo (Destructivo):** Sincroniza la tienda para que sea un reflejo exacto del CSV. **Elimina** de la tienda cualquier producto que no se encuentre en el archivo. Incluye múltiples advertencias de seguridad para prevenir accidentes.
-   **Generador de Plantillas:** Permite descargar un archivo CSV optimizado con las columnas más comunes para facilitar la creación de nuevos catálogos desde cero.
-   **Feedback en Tiempo Real:** Un cuadro de log en la interfaz muestra el progreso detallado de la sincronización, los éxitos y los errores en tiempo real, facilitando la depuración de cualquier problema.

## Requisitos

-   Python 3.8 o superior.
-   Una tienda WordPress con el plugin WooCommerce activado.
-   Permisos de administrador en la tienda para generar "Contraseñas de Aplicación".

## Instalación (Windows)

1.  **Clonar el Repositorio:**
    ```bash
    git clone [URL-de-tu-repositorio-en-GitHub]
    cd WooSync
    ```

2.  **Instalar Python:**
    Si no tienes Python, descárgalo desde [python.org](https://www.python.org/downloads/). **Importante:** Durante la instalación, asegúrate de marcar la casilla "Add Python to PATH".

3.  **Crear y Activar el Entorno Virtual:**
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
    Si PowerShell bloquea la ejecución del script, ábrelo como Administrador y ejecuta: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

4.  **Instalar las Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Archivos del Proyecto

-   `src/app_gui.py`: Contiene toda la lógica de la interfaz gráfica (CustomTkinter) y el motor de procesamiento.
-   `src/api_client.py`: Contiene la clase `WooCommerceAPI` que gestiona toda la comunicación con WordPress de forma robusta y segura.
-   `requirements.txt`: Lista las librerías de Python necesarias.
-   `main.py`: Script CLI de desarrollo/prueba. No es para uso en producción.

## Modo de Uso

1.  **Ejecutar la Aplicación:**
    ```bash
    python src/app_gui.py
    ```
2.  **Conectar a la Tienda:** Introduce la URL de tu sitio, tu nombre de usuario de WordPress y una "Contraseña de Aplicación".
3.  **Preparar la Sincronización:**
    -   **Paso 1:** Selecciona tu archivo CSV. La interfaz de mapeo se generará al instante.
    -   **Paso 2 (Opcional):** Selecciona la carpeta de tu PC que contiene las imágenes de los productos.
    -   **Paso 3:** Revisa el mapeo de columnas. Ajusta los menús desplegables. **El campo `SKU` es obligatorio.**
4.  **Seleccionar Modo y Sincronizar:**
    -   Elige el "Modo Seguro" o el "Modo Espejo".
    -   Activa el "Modo Compatible" si estás en un servidor con recursos limitados.
    -   Haz clic en "Iniciar Sincronización" y observa el progreso en el log.

## Próximas Mejoras (Roadmap)

-   [ ] **Soporte para Atributos:** Añadir mapeo para atributos de producto (ej. Color, Talla), fundamental para la venta de productos variados.
-   [ ] **Soporte Completo para Productos Variables:** Implementar la lógica para crear y sincronizar productos variables con sus respectivas variaciones (SKU, precio y atributos propios).
-   [ ] **Feedback de Lotes Mejorado:** Analizar la respuesta de la API de lotes para informar exactamente qué productos fallaron y por qué.
-   [ ] **Empaquetado de la Aplicación:** Crear un ejecutable `.exe` con PyInstaller para una fácil distribución en equipos sin Python instalado.

## Contacto y Soporte

Si deseas contactarme o aportar voluntariamente al proyecto, puedes hacerlo a través de:

* **Instagram:** [@santiago.penaranda.75](https://www.instagram.com/santiago.penaranda.75?igsh=aGxzYTRlNnZoaHZh)
* **PayPal:** [Apoya el proyecto aquí](https://paypal.me/santielpilo)

