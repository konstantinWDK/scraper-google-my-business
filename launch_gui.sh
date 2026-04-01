#!/bin/bash
# Google My Business Scraper - Launcher
cd "$(dirname "$0")"
echo "🚀 Iniciando Google My Business Scraper..."

if [ -f "./venv/bin/python3" ]; then
    ./venv/bin/python3 scraper_gui.py
else
    python3 scraper_gui.py
fi