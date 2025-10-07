# Google My Business Scraper - Compilación para Windows

Esta carpeta contiene los archivos necesarios para compilar la aplicación en un ejecutable de Windows (.exe).

## 📋 Requisitos Previos

- Windows 7 o superior
- Python 3.7 o superior instalado
- Conexión a internet (para descargar dependencias)

## 🚀 Cómo Compilar

### ⚡ Método Simple (Recomendado)

1. Abre la carpeta `scraper-google-my-business\windows` en el Explorador de Windows
2. **Haz doble clic en `build_windows.bat`**
3. Espera a que termine la compilación (puede tardar 2-5 minutos)
4. ✅ El ejecutable estará en la carpeta **`dist/GoogleMyBusinessScraper.exe`**

### 🔧 Método Manual (Avanzado)

Abre CMD o PowerShell en esta carpeta y ejecuta:

```cmd
# Instalar dependencias
pip install -r ..\requirements.txt

# Instalar PyInstaller
pip install pyinstaller

# Compilar con limpieza automática
pyinstaller scraper.spec --clean
```

## 📦 Resultado de la Compilación

Después de la compilación encontrarás:
- **`dist/GoogleMyBusinessScraper.exe`** - ✅ Ejecutable listo para distribuir (único archivo necesario)
- `build/` - Carpeta temporal (puedes eliminarla después de compilar)

## 🎯 Cómo Usar el Ejecutable

1. Copia `GoogleMyBusinessScraper.exe` a cualquier PC con Windows
2. No necesitas instalar Python ni librerías
3. Simplemente haz doble clic en el ejecutable
4. La primera vez puede tardar unos segundos en abrir

## ⚙️ Configurar API Key

Hay 3 formas de configurar tu API Key de Google Places:

### Opción 1: Desde la Interfaz (Recomendado)
1. Abre la aplicación
2. Ve a la pestaña "Configuración"
3. Ingresa tu API Key y haz clic en "Guardar API Key"

### Opción 2: Crear archivo de texto
1. Crea un archivo llamado `google_api_key.txt` en la misma carpeta que el .exe
2. Pega tu API Key dentro del archivo (solo la key, sin espacios extras)
3. Guarda el archivo

### Opción 3: Variable de entorno
1. Presiona Win + R y escribe `sysdm.cpl`
2. Ve a "Variables de entorno"
3. Crea una nueva variable: `GOOGLE_PLACES_API_KEY`
4. Pega tu API Key como valor

## 🔧 Solución de Problemas

### ❌ Error al compilar: "Python no está instalado"
- Instala Python desde [python.org](https://python.org)
- Durante la instalación, marca "Add Python to PATH"

### ❌ El ejecutable no abre
- Verifica que no esté bloqueado por Windows Defender
- Haz clic derecho > Propiedades > Desbloquear
- Abre el archivo desde la carpeta `dist/GoogleMyBusinessScraper.exe`

### ⚠️ Error de antivirus / Windows Defender
- Algunos antivirus marcan ejecutables de PyInstaller como falsos positivos
- Añade el ejecutable a la lista de excepciones de tu antivirus
- Es un falso positivo común con aplicaciones empaquetadas con PyInstaller

### 🐛 La aplicación se cierra inmediatamente o muestra errores
- Ahora la aplicación mostrará una ventana de terminal junto con la GUI
- Si hay errores, los verás en la ventana de terminal
- Verifica que tengas la API Key configurada en la pestaña "Configuración"

### 📝 Error: "PBKDF2 no se puede importar"
- Este error ya está **CORREGIDO** en la versión actual
- Si lo ves, asegúrate de estar usando los archivos actualizados

## 📁 Estructura de Archivos

```
scraper-google-my-business/
├── windows/
│   ├── build_windows.bat          # ⚡ Script de compilación (ejecutar este)
│   ├── scraper.spec               # Configuración de PyInstaller
│   ├── requirements-build.txt     # Dependencias de build
│   ├── README.md                  # Este archivo
│   ├── .gitignore                 # Archivos ignorados por git
│   └── dist/                      # ✅ Carpeta con el ejecutable (después de compilar)
│       └── GoogleMyBusinessScraper.exe  # 🎯 Ejecutable final
├── linux/                         # Compilación para Linux
├── scraper_gui.py                 # Código fuente principal
└── requirements.txt               # Dependencias del proyecto
```

## 🔍 ¿Qué hace el script de compilación?

El archivo `build_windows.bat` automáticamente:

1. ✅ Verifica que Python esté instalado
2. 📥 Instala todas las dependencias necesarias
3. 📦 Instala PyInstaller
4. 🔨 Compila la aplicación en un solo ejecutable
5. 🧹 Limpia archivos temporales
6. ✅ Genera el ejecutable en la carpeta `dist/`

## 📖 Más Información

Para documentación completa del proyecto, consulta el README principal en:
`../README.md`

---

**Nota:** Este ejecutable solo funciona en Windows. Para Linux, usa la carpeta `linux/`.
