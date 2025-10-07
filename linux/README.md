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

- Linux (Ubuntu, Debian, Fedora, Arch, etc.)
- Python 3.7 o superior
- Conexión a internet (para descargar dependencias)

## 🚀 Cómo Compilar

### Método Simple (Recomendado)

```bash
# Navega a esta carpeta
cd scraper-google-my-business/linux

# Ejecuta el script de compilación
./build_linux.sh
```

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
- `dist/GoogleMyBusinessScraper` - Ejecutable listo para distribuir
- `build/` - Carpeta temporal (puedes eliminarla)

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

### Error: Permission denied
```bash
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
- Es normal, PyInstaller incluye Python y todas las librerías
- El tamaño típico es 40-80 MB
- Para reducir tamaño, usa `upx`: `sudo apt install upx`

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

El ejecutable es compatible con:
- ✅ Ubuntu 18.04+
- ✅ Debian 10+
- ✅ Fedora 30+
- ✅ Arch Linux
- ✅ Linux Mint 19+
- ✅ Pop!_OS 20.04+

**Nota:** El ejecutable debe ser compilado en la misma arquitectura del sistema objetivo (x86_64, ARM64, etc.)

## 📖 Más Información

Para documentación completa del proyecto, consulta el README principal en:
`../README.md`

---

**Nota:** Este ejecutable solo funciona en Linux. Para Windows, usa la carpeta `windows/`.
