@echo off
echo ================================================
echo   Compilador para Google My Business Scraper
echo   Plataforma: Windows
echo ================================================
echo.

echo [1/4] Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    pause
    exit /b 1
)
echo.

echo [2/4] Instalando dependencias...
pip install -r ../requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo.

echo [3/4] Instalando PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: No se pudo instalar PyInstaller
    pause
    exit /b 1
)
echo.

echo [4/4] Compilando aplicacion...
pyinstaller scraper.spec --clean
if errorlevel 1 (
    echo ERROR: Fallo la compilacion
    pause
    exit /b 1
)
echo.

echo ================================================
echo   COMPILACION EXITOSA!
echo ================================================
echo.
echo El ejecutable se encuentra en:
echo %cd%\dist\GoogleMyBusinessScraper.exe
echo.
echo Puedes distribuir este ejecutable a cualquier PC Windows
echo sin necesidad de instalar Python o dependencias.
echo.
pause
