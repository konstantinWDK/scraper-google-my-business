#!/bin/bash

echo "================================================"
echo "  Compilador para Google My Business Scraper"
echo "  Plataforma: Linux"
echo "================================================"
echo ""

echo "[1/5] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no está instalado"
    exit 1
fi
python3 --version
echo ""

echo "[2/5] Creando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudo crear el entorno virtual"
        echo "Intenta: sudo apt install python3-venv python3-full"
        exit 1
    fi
    echo "Entorno virtual creado"
else
    echo "Usando entorno virtual existente"
fi
echo ""

# Activar entorno virtual
source venv/bin/activate

echo "[3/5] Instalando dependencias..."
# Verificar si estamos en Windows (Git Bash, WSL, etc.)
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # En Windows, usar ruta absoluta o verificar ubicación
    if [ -f "../requirements.txt" ]; then
        pip install -r ../requirements.txt
    elif [ -f "../../requirements.txt" ]; then
        pip install -r ../../requirements.txt
    else
        echo "ERROR: No se pudo encontrar requirements.txt"
        echo "Asegúrate de que el archivo requirements.txt esté en el directorio padre"
        exit 1
    fi
else
    # En Linux, usar ruta relativa normal
    pip install -r ../requirements.txt
fi

if [ $? -ne 0 ]; then
    echo "ERROR: No se pudieron instalar las dependencias"
    exit 1
fi
echo ""

echo "[4/5] Instalando PyInstaller..."
pip install pyinstaller
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo instalar PyInstaller"
    exit 1
fi
echo ""

echo "[5/5] Compilando aplicación..."
# Verificar si estamos en Windows
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # En Windows, usar ruta absoluta para el archivo spec
    if [ -f "scraper.spec" ]; then
        pyinstaller scraper.spec --clean
    elif [ -f "../scraper_gui.py" ]; then
        # Si no hay spec, crear uno automáticamente
        pyinstaller --onefile --name GoogleMyBusinessScraper --clean ../scraper_gui.py
    else
        echo "ERROR: No se pudo encontrar scraper_gui.py"
        exit 1
    fi
else
    # En Linux, usar configuración normal
    pyinstaller scraper.spec --clean
fi

if [ $? -ne 0 ]; then
    echo "ERROR: Falló la compilación"
    deactivate
    exit 1
fi
echo ""

# Desactivar entorno virtual
deactivate

echo "================================================"
echo "  COMPILACIÓN EXITOSA!"
echo "================================================"
echo ""
echo "El ejecutable se encuentra en:"
echo "$(pwd)/dist/GoogleMyBusinessScraper"
echo ""
echo "Puedes distribuir este ejecutable a cualquier PC Linux"
echo "sin necesidad de instalar Python o dependencias."
echo ""
echo "Para ejecutarlo, usa: ./dist/GoogleMyBusinessScraper"
echo ""
