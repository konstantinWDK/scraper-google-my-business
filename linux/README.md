# Google My Business Scraper - Compilación para Linux

## ⚠️ Proyecto Open Source

**Los binarios NO están incluidos en el repositorio.**

Este proyecto es open source y los usuarios deben compilar la aplicación ellos mismos para:
- ✅ Transparencia total del código
- ✅ Seguridad (verificas lo que ejecutas)
- ✅ Adaptación a tu arquitectura específica

**Instrucciones de compilación abajo** 👇

---

Esta carpeta contiene los archivos necesarios para compilar la aplicación en un ejecutable de Linux.

## 📋 Requisitos Previos

- **Sistema Operativo:** Linux (Ubuntu, Debian, Fedora, Arch, etc.)
- **Python:** 3.7 o superior (probado con Python 3.12.3)
- **Arquitectura:** x86_64 (64-bit)
- **Conexión a internet** (para descargar dependencias durante la compilación)
- **Espacio en disco:** ~200 MB para el proceso de compilación

## 🚀 Cómo Compilar

### Método Simple (Recomendado)

```bash
# Navega a esta carpeta
cd scraper-google-my-business/linux

# Si el script tiene problemas de formato (CRLF de Windows):
sed -i 's/\r$//' build_linux.sh && chmod +x build_linux.sh

# Ejecuta el script de compilación
./build_linux.sh
```

**Proceso automático del script:**
1. ✅ Verifica Python 3
2. ✅ Crea entorno virtual
3. ✅ Instala dependencias (requests, pillow, beautifulsoup4, cryptography)
4. ✅ Instala PyInstaller
5. ✅ Compila la aplicación
6. ✅ Genera el ejecutable en `dist/GoogleMyBusinessScraper`

### Método Manual

```bash
# Instalar dependencias
pip3 install -r ../requirements.txt

# Instalar PyInstaller
pip3 install pyinstaller

# Compilar
pyinstaller scraper.spec
```

## 📦 Resultado de la Compilación

Después de la compilación encontrarás:

### Archivos Generados:
- `dist/GoogleMyBusinessScraper` - **Ejecutable principal** (~19-20 MB)
- `build/` - Carpeta temporal de compilación (puedes eliminarla)
- `venv/` - Entorno virtual Python (puedes eliminarlo después de compilar)

### Características del Binario:
- **Tipo:** ELF 64-bit LSB executable, x86-64
- **Tamaño:** ~19.4 MB
- **Incluye:** Python 3.12.3 + todas las dependencias
- **Interfaz:** GUI completa con Tkinter
- **Seguridad:** Sistema de cifrado para API Keys
- **No requiere:** Python ni librerías adicionales en el sistema destino

## 🎯 Cómo Usar el Ejecutable

### Ejecutar localmente
```bash
./dist/GoogleMyBusinessScraper
```

### Distribuir a otros PCs Linux
1. Copia el archivo `GoogleMyBusinessScraper` a otro PC Linux
2. Dale permisos de ejecución: `chmod +x GoogleMyBusinessScraper`
3. Ejecútalo: `./GoogleMyBusinessScraper`
4. No necesitas instalar Python ni librerías

**Nota importante:** El ejecutable debe ser compilado en la misma arquitectura (x64, ARM, etc.) del sistema donde se ejecutará.

## ⚙️ Configurar API Key

Hay 3 formas de configurar tu API Key de Google Places:

### Opción 1: Desde la Interfaz (Recomendado)
1. Abre la aplicación
2. Ve a la pestaña "Configuración"
3. Ingresa tu API Key y haz clic en "Guardar API Key"

### Opción 2: Crear archivo de texto
```bash
# En la misma carpeta del ejecutable
echo "TU_API_KEY_AQUI" > google_api_key.txt
```

### Opción 3: Variable de entorno
```bash
# Temporal (solo para esta sesión)
export GOOGLE_PLACES_API_KEY="TU_API_KEY_AQUI"
./dist/GoogleMyBusinessScraper

# Permanente (añadir al ~/.bashrc o ~/.zshrc)
echo 'export GOOGLE_PLACES_API_KEY="TU_API_KEY_AQUI"' >> ~/.bashrc
source ~/.bashrc
```

## 🔧 Solución de Problemas

### ⚠️ Problema Resuelto: Caracteres CRLF de Windows

**Error encontrado durante la compilación:**
```
zsh: ./build_linux.sh: bad interpreter: /bin/bash^M: no existe el archivo o el directorio
```

**Causa:** El archivo `build_linux.sh` fue creado o editado en Windows y contiene caracteres de fin de línea CRLF (`\r\n`) en lugar de LF (`\n`) que usa Linux.

**Solución aplicada:**
```bash
# Eliminar caracteres CR (^M) del archivo
sed -i 's/\r$//' build_linux.sh

# Dar permisos de ejecución
chmod +x build_linux.sh

# Ahora el script funciona correctamente
./build_linux.sh
```

**Comando combinado:**
```bash
sed -i 's/\r$//' build_linux.sh && chmod +x build_linux.sh && ./build_linux.sh
```

### Error: Permission denied
```bash
# Dar permisos de ejecución
chmod +x build_linux.sh
chmod +x dist/GoogleMyBusinessScraper
```

### Error: python3 not found
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip

# Arch
sudo pacman -S python python-pip
```

### Error con tkinter
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

### La aplicación no abre en modo gráfico
- Verifica que estés usando un entorno de escritorio (GNOME, KDE, XFCE, etc.)
- Si usas SSH, habilita X11 forwarding: `ssh -X usuario@servidor`
- Para servidores sin GUI, usa la versión de línea de comandos

### Ejecutable muy grande
- **Es normal:** PyInstaller incluye Python 3.12.3 y todas las librerías
- **Tamaño esperado:** ~19-20 MB (optimizado)
- **Para reducir tamaño:** Usa `upx` (compresión adicional):
  ```bash
  sudo apt install upx
  # El script ya incluye compresión UPX por defecto
  ```

## 📁 Estructura de Archivos

```
scraper-google-my-business/
├── linux/
│   ├── build_linux.sh             # Script de compilación
│   ├── scraper.spec               # Configuración de PyInstaller
│   ├── README.md                  # Este archivo
│   └── dist/                      # Carpeta con el ejecutable (después de compilar)
│       └── GoogleMyBusinessScraper
├── windows/                       # Compilación para Windows
├── scraper_gui.py                 # Código fuente principal
└── requirements.txt               # Dependencias del proyecto
```

## 🐧 Compatibilidad

### Sistemas Compatibles:
- ✅ **Ubuntu** 18.04+ (probado en Ubuntu 22.04/24.04)
- ✅ **Debian** 10+ (probado en Debian 11/12)
- ✅ **Fedora** 30+ (probado en Fedora 38/39)
- ✅ **Arch Linux** (probado en Arch rolling release)
- ✅ **Linux Mint** 19+
- ✅ **Pop!_OS** 20.04+

### Arquitectura:
- ✅ **x86_64** (64-bit Intel/AMD) - **Principalmente compatible**
- ⚠️ **ARM64** - Requiere compilación específica
- ❌ **i386** (32-bit) - No compatible

### Dependencias del Sistema:
- **Tkinter:** Para la interfaz gráfica
- **libc6:** Versión estándar de Linux
- **X11:** Para entorno gráfico

**Nota importante:** El ejecutable debe ser compilado en la misma arquitectura del sistema objetivo.

## 🚀 Características de la Versión 1.3.0

### Nuevas Funcionalidades:
- ✅ **Búsquedas múltiples automáticas** (campo multilínea)
- ✅ **Superar límite de 60 resultados** con múltiples keywords
- ✅ **Sistema inteligente anti-duplicados** entre búsquedas
- ✅ **Soporte para separadores:** newline, comas, punto y coma
- ✅ **Logs detallados** del progreso de cada búsqueda
- ✅ **Resumen consolidado** de todas las búsquedas

### Mejoras de Seguridad:
- ✅ **API Key cifrada** automáticamente
- ✅ **Persistencia segura** entre sesiones
- ✅ **Validación de API Key** antes de iniciar scraping

### Optimizaciones:
- ✅ **Rate limiting** con reintentos automáticos
- ✅ **Contador de API calls** y costos estimados
- ✅ **Sistema de checkpoint** cada 10 registros
- ✅ **Extracción mejorada de emails** desde sitios web

## 📖 Más Información

Para documentación completa del proyecto, consulta el README principal en:
`../README.md`

### Archivos de Configuración:
- `scraper_gui.py` - Código fuente principal
- `requirements.txt` - Dependencias del proyecto
- `scraper.spec` - Configuración de PyInstaller
- `build_linux.sh` - Script de compilación automatizado

### Estructura del Proyecto:
```
scraper-google-my-business/
├── linux/                          # Compilación para Linux
│   ├── build_linux.sh              # Script de compilación
│   ├── scraper.spec                # Configuración de PyInstaller
│   ├── README.md                   # Este archivo
│   ├── dist/                       # Ejecutable generado
│   │   └── GoogleMyBusinessScraper
│   └── venv/                       # Entorno virtual (temporal)
├── windows/                        # Compilación para Windows
├── scraper_gui.py                  # Código fuente principal
├── requirements.txt                # Dependencias
└── README.md                       # Documentación principal
```

---

**💡 Tip:** El ejecutable generado es completamente independiente y puede distribuirse a otros sistemas Linux sin necesidad de instalar Python o dependencias.

---

**Nota:** Este ejecutable solo funciona en Linux. Para Windows, usa la carpeta `windows/`.
