# 🪟 Compilación en Windows - Google My Business Scraper v1.1.0

## ⚠️ Proyecto Open Source

**Los binarios NO están incluidos en el repositorio.**

Este proyecto es open source y los usuarios deben compilar la aplicación ellos mismos para:
- ✅ Transparencia total del código
- ✅ Seguridad (verificas lo que ejecutas)
- ✅ Adaptación a tu sistema específico

**Instrucciones de compilación abajo** 👇

---

Este documento explica cómo compilar la aplicación en un PC con Windows para generar el ejecutable `.exe`.

---

## 📋 Requisitos Previos

Antes de compilar, asegúrate de tener instalado:

1. **Python 3.11 o superior** (recomendado 3.11.9)
   - Descarga: https://www.python.org/downloads/
   - ⚠️ Durante la instalación, marca la opción **"Add Python to PATH"**

2. **Git** (opcional, si clonas desde GitHub)
   - Descarga: https://git-scm.com/download/win

---

## 🚀 Pasos para Compilar

### Paso 1: Preparar el Entorno

Abre **PowerShell** o **CMD** como Administrador y navega a la carpeta del proyecto:

```cmd
cd C:\ruta\a\tu\proyecto\scraper-google-my-business\windows
```

### Paso 2: Instalar Dependencias

Instala las librerías necesarias:

```cmd
pip install -r ..\requirements.txt
```

Esto instalará:
- `requests` - Para hacer peticiones HTTP
- `pillow` - Para manejo de imágenes
- `beautifulsoup4` - Para parsear HTML
- `cryptography` - Para cifrado seguro de API Key (**NUEVO en v1.1.0**)

### Paso 3: Instalar PyInstaller

Instala PyInstaller para crear el ejecutable:

```cmd
pip install pyinstaller
```

### Paso 4: Compilar el Ejecutable

Ejecuta el script de compilación:

```cmd
build_windows.bat
```

O manualmente con PyInstaller:

```cmd
pyinstaller scraper.spec
```

### Paso 5: Resultado

El ejecutable se creará en:

```
scraper-google-my-business\windows\dist\GoogleMyBusinessScraper.exe
```

**Tamaño esperado:** ~17-20 MB (incluye Python, librerías y cifrado)

---

## 📦 Distribución del Ejecutable

### Opción 1: Copiar a `compilado/`

Para mantener consistencia con la versión Linux:

```cmd
copy dist\GoogleMyBusinessScraper.exe compilado\
```

### Opción 2: Crear ZIP para GitHub Release

```cmd
cd dist
tar -a -c -f GoogleMyBusinessScraper-v1.1.0-windows-x64.zip GoogleMyBusinessScraper.exe
```

O usa 7-Zip/WinRAR para crear un archivo comprimido.

---

## ✅ Verificación

Para verificar que el ejecutable funciona correctamente:

1. Navega a la carpeta `dist\`
2. Haz doble clic en `GoogleMyBusinessScraper.exe`
3. Debería abrirse la interfaz gráfica
4. Ve a la pestaña **"Configuración"** y verifica que puedes guardar una API Key

---

## 🔧 Solución de Problemas

### Error: "pip no se reconoce como un comando"

**Solución:**
- Reinstala Python y marca la opción **"Add Python to PATH"**
- O añade manualmente Python a las variables de entorno:
  1. Panel de Control → Sistema → Configuración avanzada
  2. Variables de entorno → Path → Editar
  3. Añadir: `C:\Users\TuUsuario\AppData\Local\Programs\Python\Python311\`
  4. Añadir: `C:\Users\TuUsuario\AppData\Local\Programs\Python\Python311\Scripts\`

### Error: "ModuleNotFoundError: No module named 'cryptography'"

**Solución:**
```cmd
pip install cryptography
```

### Error: "tkinter module not found"

**Solución:**
- Reinstala Python asegurándote de marcar la opción **"tcl/tk and IDLE"** durante la instalación

### Antivirus bloquea PyInstaller o el .exe

**Solución:**
- Esto es un **falso positivo** común con PyInstaller
- Añade excepciones en Windows Defender:
  1. Windows Security → Protección contra virus y amenazas
  2. Administrar configuración → Exclusiones → Agregar exclusión
  3. Añadir la carpeta del proyecto y `dist\`

### El ejecutable es muy grande (>50 MB)

**Solución:**
- Esto es normal, PyInstaller empaqueta Python completo y todas las librerías
- Para reducir tamaño, usa UPX (opcional):
  ```cmd
  pip install upx
  ```

---

## 🆕 Cambios en v1.1.0

La nueva versión incluye:

✅ **Guardado seguro de API Key con cifrado**
- La API Key se guarda cifrada en `.gmb_config.enc`
- Usa criptografía AES-256 basada en el identificador único de tu PC
- Compatible con Windows y Linux

✅ **Persistencia automática**
- La API Key se carga automáticamente al iniciar la aplicación
- No necesitas volver a ingresarla cada vez

✅ **Compatibilidad con versiones anteriores**
- Si tienes un archivo `google_api_key.txt` antiguo, la app lo detecta
- Te sugiere migrar al sistema cifrado

---

## 📁 Estructura de Archivos Después de Compilar

```
scraper-google-my-business\
├── windows\
│   ├── build\                          # Archivos temporales (puede eliminarse)
│   ├── dist\                           # Ejecutable final
│   │   └── GoogleMyBusinessScraper.exe # ← Distribuir este archivo
│   ├── build_windows.bat               # Script de compilación
│   ├── scraper.spec                    # Configuración de PyInstaller
│   ├── INSTRUCCIONES_COMPILACION_WINDOWS.md  # Este archivo
│   └── README.md                       # Guía rápida de compilación
├── linux\                              # Compilación para Linux
├── scraper_gui.py                      # Código fuente principal
└── requirements.txt                    # Dependencias del proyecto
```

---

## 🎯 Recomendaciones

1. **Compilar en la misma versión de Windows** que usarán tus usuarios
   - Ej: Si tus usuarios usan Windows 10, compila en Windows 10

2. **Probar el ejecutable** antes de distribuirlo:
   - Pruébalo en otro PC sin Python instalado
   - Verifica que la API Key se guarde y cargue correctamente

3. **Firmar digitalmente el .exe** (opcional pero recomendado):
   - Reduce advertencias de Windows Defender
   - Requiere certificado de firma de código

4. **Versionar tus releases**:
   - Renombra el exe: `GoogleMyBusinessScraper-v1.1.0-windows-x64.exe`
   - Mantén un CHANGELOG con cambios de cada versión

---

## 📖 Documentación Adicional

- [Código fuente](../scraper_gui.py)
- [README principal](../README.md)
- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)

---

## ❓ Preguntas Frecuentes

**P: ¿Puedo compilar en Windows 11 y ejecutar en Windows 7?**
R: Sí, pero es mejor compilar en la versión más antigua que quieras soportar.

**P: ¿El .exe funciona en sistemas de 32 bits?**
R: No, está compilado para 64 bits. Para 32 bits necesitas Python de 32 bits y recompilar.

**P: ¿Puedo compilar desde Linux con Wine?**
R: Sí, pero no es recomendado. Pueden haber problemas de compatibilidad. Mejor compilar directamente en Windows.

**P: ¿Dónde se guarda la API Key cifrada?**
R: En el mismo directorio del ejecutable, archivo `.gmb_config.enc`

---

**Creado por:** Konstantin Koshkarev
**Web:** [webdesignerk.com](https://webdesignerk.com)
**Versión:** 1.1.0
**Fecha:** 2025-10-06
