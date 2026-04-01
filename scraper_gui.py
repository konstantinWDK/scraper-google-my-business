#!/usr/bin/env python3
# Google My Business Scraper v1.3.1
# Cambios en v1.3.1:
# - Organización de archivos en subcarpetas dentro de data/
# - Mejora en la visualización de archivos en la GUI
#
# Cambios en v1.3.0:
# - Búsquedas múltiples automáticas (campo multilínea)
# - Superar límite de 60 resultados con múltiples keywords
# - Sistema inteligente anti-duplicados entre búsquedas
# - Soporte para separadores: newline, comas, punto y coma
# - Logs detallados del progreso de cada búsqueda
# - Resumen consolidado de todas las búsquedas
# - Advertencias actualizadas sobre límite de API
# - Popup informativo mejorado con ejemplos de uso
#
# Cambios en v1.2.0:
# - Sistema de logging en archivo con rotación automática
# - Validación de API Key antes de iniciar scraping
# - Manejo de Rate Limiting (429 errors) con reintentos automáticos
# - Contador de API calls y costos estimados en tiempo real
# - Sistema de Checkpoint cada 10 registros para reanudar scraping
# - Mejora inteligente en scraping de emails (páginas de contacto, footer, cache)
# - Botón Reiniciar mejorado con tracking de threads
# - Gestión de errores mejorada con logs específicos
#
# Cambios en v1.1.0:
# - Guardado seguro y cifrado de API Key
# - Persistencia automática de API Key entre sesiones
# - Compatibilidad multiplataforma (Windows/Linux)

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import csv
import os
import sys
import threading
import requests
import time
import random
import re
import webbrowser
from dataclasses import dataclass
from typing import List, Optional, Dict
import unicodedata
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import platform
import logging
from logging.handlers import RotatingFileHandler

def normalize_filename(filename):
    """Normaliza nombres de archivos: espacios -> guiones, minúsculas, sin caracteres especiales"""
    # Convertir a minúsculas
    filename = filename.lower()
    # Reemplazar espacios con guiones
    filename = filename.replace(' ', '-')
    # Normalizar caracteres unicode (quitar acentos)
    filename = unicodedata.normalize('NFD', filename)
    filename = ''.join(c for c in filename if not unicodedata.combining(c))
    # Remover caracteres no válidos para nombres de archivo
    filename = re.sub(r'[^a-z0-9\-_.]', '', filename)
    # Evitar guiones múltiples
    filename = re.sub(r'-+', '-', filename)
    # Quitar guiones al inicio/final
    filename = filename.strip('-')
    return filename

def parse_keywords(text):
    """Parsea texto con múltiples keywords y retorna lista limpia"""
    # Reemplazar comas y punto y coma por saltos de línea
    text = text.replace(',', '\n').replace(';', '\n')

    # Dividir por líneas y limpiar
    keywords = []
    for line in text.split('\n'):
        line = line.strip()
        if line:  # Ignorar líneas vacías
            keywords.append(line)

    return keywords

def setup_logging():
    """Configura el sistema de logging con rotación de archivos"""
    # Obtener directorio del script o ejecutable
    if getattr(sys, 'frozen', False):
        # Si está compilado con PyInstaller
        script_dir = os.path.dirname(sys.executable)
    else:
        # Si se ejecuta como script Python
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    log_file = os.path.join(script_dir, 'scraper.log')

    # Configurar logging con rotación (max 5 archivos de 1MB cada uno)
    handler = RotatingFileHandler(
        log_file,
        maxBytes=1024*1024,  # 1MB
        backupCount=5,
        encoding='utf-8'
    )

    # Formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    # Configurar logger
    logger = logging.getLogger('GMBScraper')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger

# Configuración por defecto
DEFAULT_API_KEY_FILE = '.gmb_config.enc'  # Archivo cifrado
URL_TEXT_SEARCH = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
URL_PLACE_DETAILS = 'https://maps.googleapis.com/maps/api/place/details/json'
APP_VERSION = "1.3.1"

class SecureConfig:
    """Gestión segura de configuración con cifrado"""

    def __init__(self):
        # Usar ruta absoluta basada en el directorio del script o ejecutable
        if getattr(sys, 'frozen', False):
            # Si está compilado con PyInstaller
            script_dir = os.path.dirname(sys.executable)
        else:
            # Si se ejecuta como script Python
            script_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.config_file = os.path.join(script_dir, DEFAULT_API_KEY_FILE)
        self._key = self._get_machine_key()
        self.fernet = Fernet(self._key)

    def _get_machine_key(self):
        """Genera una clave de cifrado única basada en la máquina"""
        # Obtener un identificador único de la máquina
        machine_id = platform.node() + platform.system() + os.path.expanduser("~")

        # Derivar una clave de cifrado usando PBKDF2HMAC
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'gmb_scraper_salt_v1',  # Salt fijo para consistencia
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
        return key

    def save_api_key(self, api_key: str) -> bool:
        """Guarda la API Key cifrada"""
        try:
            encrypted_key = self.fernet.encrypt(api_key.encode())
            with open(self.config_file, 'wb') as f:
                f.write(encrypted_key)
            return True
        except Exception as e:
            print(f"Error guardando API Key: {e}")
            return False

    def load_api_key(self) -> Optional[str]:
        """Carga y descifra la API Key"""
        try:
            if not os.path.exists(self.config_file):
                return None

            with open(self.config_file, 'rb') as f:
                encrypted_key = f.read()

            decrypted_key = self.fernet.decrypt(encrypted_key)
            return decrypted_key.decode()
        except Exception as e:
            print(f"Error cargando API Key: {e}")
            return None

    def delete_api_key(self) -> bool:
        """Elimina el archivo de configuración"""
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            return True
        except Exception as e:
            print(f"Error eliminando API Key: {e}")
            return False

@dataclass
class BusinessData:
    title: str
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    place_id: Optional[str] = None
    rating: Optional[float] = None
    total_ratings: Optional[int] = None
    opening_hours: Optional[str] = None
    price_level: Optional[int] = None
    email: Optional[str] = None

class GoogleMyBusinessScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Google My Business Scraper v{APP_VERSION}")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')

        # Variables
        self.api_key = None
        self.is_scraping = False
        self.scraped_data = []
        self.secure_config = SecureConfig()
        self.scraping_thread = None
        self.api_calls_count = 0
        self.estimated_cost = 0.0
        self.visited_websites_no_email = set()  # Cache de URLs sin email

        # Inicializar logger
        self.logger = setup_logging()

        self.setup_ui()
        self.load_api_key()
        self.refresh_json_files()
        
    def setup_ui(self):
        # Frame principal con pestañas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pestaña de scraping
        self.scraping_frame = ttk.Frame(notebook)
        notebook.add(self.scraping_frame, text="Scraper")
        
        # Pestaña de gestión de archivos
        self.files_frame = ttk.Frame(notebook)
        notebook.add(self.files_frame, text="Gestión de Archivos")

        # Pestaña de configuración
        self.config_frame = ttk.Frame(notebook)
        notebook.add(self.config_frame, text="Configuración")

        self.setup_scraping_tab()
        self.setup_files_tab()
        self.setup_config_tab()
        self.setup_credits_section()
    
    def setup_scraping_tab(self):
        # Título
        title_label = tk.Label(self.scraping_frame, text="Google My Business Scraper", 
                              font=('Arial', 16, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=10)
        
        # Frame para entrada de datos
        input_frame = ttk.LabelFrame(self.scraping_frame, text="Configuración de Búsqueda", padding=10)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        # Entrada de palabras clave (múltiples líneas)
        keyword_label_frame = tk.Frame(input_frame)
        keyword_label_frame.grid(row=0, column=0, sticky='nw', pady=5)

        tk.Label(keyword_label_frame, text="Palabras clave para buscar:").pack(anchor='w')
        tk.Label(keyword_label_frame, text="(una por línea)", font=('Arial', 8), fg='#666666').pack(anchor='w')

        self.keyword_entry = scrolledtext.ScrolledText(input_frame, width=50, height=4, font=('Arial', 10))
        self.keyword_entry.grid(row=0, column=1, columnspan=2, sticky='ew', pady=5, padx=(5,0))
        
        # Nombre del archivo de salida
        tk.Label(input_frame, text="Nombre del archivo:").grid(row=1, column=0, sticky='w', pady=5)
        self.filename_entry = tk.Entry(input_frame, width=30, font=('Arial', 10))
        self.filename_entry.grid(row=1, column=1, sticky='ew', pady=5)
        
        # Formato de salida
        tk.Label(input_frame, text="Formato:").grid(row=1, column=2, sticky='w', padx=(10,5), pady=5)
        self.format_var = tk.StringVar(value="json")
        format_combo = ttk.Combobox(input_frame, textvariable=self.format_var, 
                                   values=["json", "csv"], state="readonly", width=8)
        format_combo.grid(row=1, column=3, sticky='w', pady=5)
        
        # Frame para campos a extraer
        fields_frame = ttk.LabelFrame(self.scraping_frame, text="Campos a Extraer", padding=10)
        fields_frame.pack(fill='x', padx=10, pady=5)
        
        # Checkboxes para campos
        self.field_vars = {
            'title': tk.BooleanVar(value=True),
            'phone': tk.BooleanVar(value=True),
            'website': tk.BooleanVar(value=True),
            'address': tk.BooleanVar(value=True),
            'place_id': tk.BooleanVar(value=False),
            'rating': tk.BooleanVar(value=True),
            'total_ratings': tk.BooleanVar(value=True),
            'opening_hours': tk.BooleanVar(value=False),
            'price_level': tk.BooleanVar(value=False),
            'email': tk.BooleanVar(value=False)
        }
        
        field_labels = {
            'title': 'Título',
            'phone': 'Teléfono',
            'website': 'Sitio Web',
            'address': 'Dirección',
            'place_id': 'Place ID',
            'rating': 'Rating',
            'total_ratings': 'Total Reseñas',
            'opening_hours': 'Horarios',
            'price_level': 'Nivel de Precios',
            'email': 'Email (desde web)'
        }
        
        row = 0
        col = 0
        for field, var in self.field_vars.items():
            cb = tk.Checkbutton(fields_frame, text=field_labels[field], variable=var)
            if field == 'email':
                cb.config(fg='#FF6600')  # Color naranja para indicar que es experimental
            cb.grid(row=row, column=col, sticky='w', padx=10, pady=2)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        # Advertencia para email
        email_warning = tk.Label(fields_frame, text="⚠️ Email: Función experimental, puede ser lenta", 
                                fg='#FF6600', font=('Arial', 8))
        email_warning.grid(row=row+1, column=0, columnspan=3, sticky='w', padx=10, pady=2)
        
        # Frame para configuración de API
        api_frame = ttk.LabelFrame(self.scraping_frame, text="Configuración de API", padding=10)
        api_frame.pack(fill='x', padx=10, pady=5)
        
        # Controles de velocidad
        tk.Label(api_frame, text="Delay entre peticiones (seg):").grid(row=0, column=0, sticky='w', pady=2)
        self.min_delay_var = tk.DoubleVar(value=1.5)
        self.max_delay_var = tk.DoubleVar(value=3.0)
        
        tk.Label(api_frame, text="Mín:").grid(row=0, column=1, sticky='w', padx=(10,0))
        tk.Spinbox(api_frame, from_=0.5, to=10.0, increment=0.5, width=8, 
                  textvariable=self.min_delay_var).grid(row=0, column=2, sticky='w', padx=5)
        
        tk.Label(api_frame, text="Máx:").grid(row=0, column=3, sticky='w', padx=(10,0))
        tk.Spinbox(api_frame, from_=1.0, to=20.0, increment=0.5, width=8,
                  textvariable=self.max_delay_var).grid(row=0, column=4, sticky='w', padx=5)
        
        # Tamaño de lote
        tk.Label(api_frame, text="Tamaño de lote:").grid(row=1, column=0, sticky='w', pady=2)
        self.batch_size_var = tk.IntVar(value=5)
        tk.Spinbox(api_frame, from_=1, to=20, width=8,
                  textvariable=self.batch_size_var).grid(row=1, column=1, sticky='w', padx=5)
        
        # Delay entre lotes
        tk.Label(api_frame, text="Delay entre lotes (seg):").grid(row=1, column=2, sticky='w', padx=(10,0))
        self.batch_delay_var = tk.DoubleVar(value=10.0)
        tk.Spinbox(api_frame, from_=5.0, to=60.0, increment=5.0, width=8,
                  textvariable=self.batch_delay_var).grid(row=1, column=3, sticky='w', padx=5)
        
        # Límite de resultados
        results_label_frame = tk.Frame(api_frame)
        results_label_frame.grid(row=2, column=0, sticky='w', pady=2)

        tk.Label(results_label_frame, text="Máx resultados:").pack(side='left')

        # Botón de información
        info_button = tk.Button(results_label_frame, text="ℹ️", font=('Arial', 8),
                               command=self.show_60_limit_info, bg='#2196F3', fg='white',
                               cursor='hand2', padx=2, pady=0, relief='flat')
        info_button.pack(side='left', padx=5)

        self.max_results_var = tk.StringVar(value="")
        max_results_spinbox = tk.Spinbox(api_frame, from_=1, to=200, width=8,
                                        textvariable=self.max_results_var)
        max_results_spinbox.grid(row=2, column=1, sticky='w', padx=5)
        tk.Label(api_frame, text="(vacío = todos)").grid(row=2, column=2, sticky='w', padx=5)

        # Advertencia del límite de 60
        warning_label = tk.Label(api_frame, text="⚠️ Límite: 60 resultados por palabra clave | 💡 Usa múltiples líneas para más resultados",
                                fg='#FF9800', font=('Arial', 8))
        warning_label.grid(row=3, column=0, columnspan=4, sticky='w', pady=(2, 5))
        
        # Botones de control
        control_frame = tk.Frame(self.scraping_frame, bg='#f0f0f0')
        control_frame.pack(pady=10)
        
        self.start_button = tk.Button(control_frame, text="Iniciar Scraping", 
                                     command=self.start_scraping, bg='#4CAF50', fg='white',
                                     font=('Arial', 12, 'bold'), padx=20)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = tk.Button(control_frame, text="Detener", 
                                    command=self.stop_scraping, bg='#f44336', fg='white',
                                    font=('Arial', 12, 'bold'), padx=20, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        self.refresh_button = tk.Button(control_frame, text="Reiniciar", 
                                       command=self.refresh_scraper, bg='#FF9800', fg='white',
                                       font=('Arial', 12, 'bold'), padx=20)
        self.refresh_button.pack(side='left', padx=5)
        
        # Área de log
        log_frame = ttk.LabelFrame(self.scraping_frame, text="Registro de Actividad", padding=5)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True)
        
        # Barra de progreso
        self.progress_var = tk.StringVar(value="Listo para comenzar")
        progress_label = tk.Label(self.scraping_frame, textvariable=self.progress_var,
                                 bg='#f0f0f0', font=('Arial', 10))
        progress_label.pack(pady=5)

        self.progress_bar = ttk.Progressbar(self.scraping_frame, mode='determinate')
        self.progress_bar.pack(fill='x', padx=10, pady=5)

        # Contador de API calls y costos
        api_stats_frame = tk.Frame(self.scraping_frame, bg='#f0f0f0')
        api_stats_frame.pack(pady=5)

        self.api_stats_var = tk.StringVar(value="API Calls: 0 | Costo estimado: $0.00")
        api_stats_label = tk.Label(api_stats_frame, textvariable=self.api_stats_var,
                                   bg='#f0f0f0', font=('Arial', 9), fg='#666666')
        api_stats_label.pack()
        
    def setup_files_tab(self):
        # Título
        title_label = tk.Label(self.files_frame, text="Gestión de Archivos JSON", 
                              font=('Arial', 16, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=10)
        
        # Frame para lista de archivos
        files_list_frame = ttk.LabelFrame(self.files_frame, text="Archivos JSON Existentes", padding=10)
        files_list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Lista de archivos
        self.files_listbox = tk.Listbox(files_list_frame, font=('Arial', 10))
        self.files_listbox.pack(fill='both', expand=True, pady=5)
        self.files_listbox.bind('<Double-1>', self.view_json_file)
        
        # Botones para gestión de archivos
        files_buttons_frame = tk.Frame(files_list_frame, bg='#f0f0f0')
        files_buttons_frame.pack(pady=10)
        
        tk.Button(files_buttons_frame, text="Actualizar Lista", command=self.refresh_json_files,
                 bg='#2196F3', fg='white', padx=15).pack(side='left', padx=5)
        
        tk.Button(files_buttons_frame, text="Ver Contenido", command=self.view_selected_file,
                 bg='#FF9800', fg='white', padx=15).pack(side='left', padx=5)
        
        tk.Button(files_buttons_frame, text="Eliminar Archivo", command=self.delete_selected_file,
                 bg='#f44336', fg='white', padx=15).pack(side='left', padx=5)
        
        tk.Button(files_buttons_frame, text="Exportar", command=self.export_file,
                 bg='#9C27B0', fg='white', padx=15).pack(side='left', padx=5)
        
        # Área de vista previa
        preview_frame = ttk.LabelFrame(self.files_frame, text="Vista Previa", padding=5)
        preview_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=8, font=('Consolas', 9))
        self.preview_text.pack(fill='both', expand=True)

    def setup_config_tab(self):
        # Título
        title_label = tk.Label(self.config_frame, text="Configuración de API Key",
                              font=('Arial', 16, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=10)

        # Frame para configuración de API
        api_config_frame = ttk.LabelFrame(self.config_frame, text="Google Places API Key", padding=20)
        api_config_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Estado actual de la API
        status_frame = tk.Frame(api_config_frame, bg='white', relief='solid', bd=1)
        status_frame.pack(fill='x', pady=10)

        tk.Label(status_frame, text="Estado:", font=('Arial', 11, 'bold'), bg='white').pack(side='left', padx=10, pady=10)
        self.api_status_label = tk.Label(status_frame, text="No configurada", font=('Arial', 11), bg='white', fg='red')
        self.api_status_label.pack(side='left', pady=10)

        # Instrucciones
        instructions_text = """
Para usar esta aplicación necesitas una API Key de Google Places.

Pasos para obtener tu API Key:
1. Ve a: https://console.cloud.google.com/
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita "Places API" en el proyecto
4. Ve a "Credenciales" y crea una API Key
5. Copia la API Key y pégala abajo
        """

        instructions_label = tk.Label(api_config_frame, text=instructions_text,
                                     justify='left', font=('Arial', 9), bg='#f0f0f0')
        instructions_label.pack(pady=10, padx=5, anchor='w')

        # Entrada de API Key
        tk.Label(api_config_frame, text="Ingresa tu API Key:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10,5))

        self.api_key_entry = tk.Entry(api_config_frame, width=60, font=('Arial', 10), show='*')
        self.api_key_entry.pack(fill='x', pady=5)

        # Checkbox para mostrar/ocultar API Key
        self.show_api_var = tk.BooleanVar(value=False)
        show_api_check = tk.Checkbutton(api_config_frame, text="Mostrar API Key",
                                       variable=self.show_api_var, command=self.toggle_api_visibility)
        show_api_check.pack(anchor='w', pady=5)

        # Botones de acción
        buttons_frame = tk.Frame(api_config_frame, bg='#f0f0f0')
        buttons_frame.pack(pady=20)

        tk.Button(buttons_frame, text="Guardar API Key", command=self.save_api_key,
                 bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'), padx=20, pady=5).pack(side='left', padx=5)

        tk.Button(buttons_frame, text="Cargar desde archivo", command=self.load_api_from_file,
                 bg='#2196F3', fg='white', font=('Arial', 11, 'bold'), padx=20, pady=5).pack(side='left', padx=5)

        tk.Button(buttons_frame, text="Limpiar", command=self.clear_api_key,
                 bg='#f44336', fg='white', font=('Arial', 11, 'bold'), padx=20, pady=5).pack(side='left', padx=5)

        # Actualizar el estado inicial
        self.update_api_status()

    def toggle_api_visibility(self):
        """Muestra u oculta la API Key en el campo de entrada"""
        if self.show_api_var.get():
            self.api_key_entry.config(show='')
        else:
            self.api_key_entry.config(show='*')

    def update_api_status(self):
        """Actualiza el estado visual de la API Key"""
        if self.api_key and len(self.api_key) > 0:
            self.api_status_label.config(text="✅ Configurada correctamente", fg='green')
            # Mostrar los primeros y últimos caracteres de la API key
            if len(self.api_key) > 10:
                masked_key = f"{self.api_key[:8]}...{self.api_key[-4:]}"
            else:
                masked_key = "***"
            self.api_key_entry.delete(0, tk.END)
            self.api_key_entry.insert(0, self.api_key)
        else:
            self.api_status_label.config(text="❌ No configurada", fg='red')

    def save_api_key(self):
        """Guarda la API Key ingresada de forma segura y cifrada"""
        api_key = self.api_key_entry.get().strip()

        if not api_key:
            messagebox.showerror("Error", "Por favor ingresa una API Key")
            return

        if len(api_key) < 20:
            result = messagebox.askyesno("Advertencia",
                                        "La API Key parece muy corta. ¿Estás seguro que es correcta?")
            if not result:
                return

        try:
            # Guardar en archivo cifrado
            success = self.secure_config.save_api_key(api_key)

            if success:
                # Actualizar en memoria
                self.api_key = api_key
                self.update_api_status()

                messagebox.showinfo("Éxito",
                                   "✅ API Key guardada correctamente\n\n"
                                   "Tu API Key se ha guardado de forma segura y cifrada.\n"
                                   "Se cargará automáticamente al iniciar la aplicación.")
                self.log("✅ API Key configurada y guardada de forma segura")
            else:
                messagebox.showerror("Error", "No se pudo guardar la API Key")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la API Key:\n{e}")

    def load_api_from_file(self):
        """Carga la API Key desde un archivo seleccionado"""
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo con API Key",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )

        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    api_key = f.read().strip()

                if api_key:
                    self.api_key_entry.delete(0, tk.END)
                    self.api_key_entry.insert(0, api_key)
                    messagebox.showinfo("Éxito", "API Key cargada desde archivo")
                else:
                    messagebox.showerror("Error", "El archivo está vacío")

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")

    def clear_api_key(self):
        """Limpia la API Key"""
        result = messagebox.askyesno("Confirmar",
                                     "¿Estás seguro de que quieres eliminar la API Key guardada?")
        if result:
            try:
                success = self.secure_config.delete_api_key()

                if success:
                    self.api_key = None
                    self.api_key_entry.delete(0, tk.END)
                    self.update_api_status()
                    self.log("❌ API Key eliminada")
                    messagebox.showinfo("Éxito", "API Key eliminada correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la API Key")

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la API Key:\n{e}")

    def load_api_key(self):
        """Carga la API key desde diferentes fuentes (variables de entorno, archivo cifrado, etc.)"""
        try:
            # Prioridad 1: Variable de entorno
            api_key = os.environ.get('GOOGLE_PLACES_API_KEY')
            if api_key:
                self.api_key = api_key.strip()
                self.log("✅ API Key cargada desde variable de entorno")
                self.update_api_status()
                return

            # Prioridad 2: Archivo cifrado
            api_key = self.secure_config.load_api_key()
            if api_key:
                self.api_key = api_key
                self.log("✅ API Key cargada desde configuración guardada")
                self.update_api_status()
                return

            # Prioridad 3: Archivo de texto plano legacy (compatibilidad con versiones anteriores)
            legacy_file = 'google_api_key.txt'
            if os.path.isfile(legacy_file):
                with open(legacy_file, 'r', encoding='utf-8') as f:
                    api_key = f.read().strip()
                    if api_key:
                        self.api_key = api_key
                        self.log("⚠️ API Key cargada desde archivo legacy")
                        self.log("💡 Se recomienda guardar la API Key desde la pestaña Configuración para usar cifrado")
                        self.update_api_status()
                        return

            # No se encontró API key
            self.log("ℹ️ No se encontró API Key configurada")
            self.log("💡 Por favor, configura tu API Key en la pestaña 'Configuración'")

        except Exception as e:
            self.log(f"❌ Error cargando API Key: {e}")
            print(f"Error completo: {e}")
            
    def log(self, message):
        """Log message to both GUI and file"""
        timestamp = time.strftime('%H:%M:%S')
        formatted_message = f"{timestamp} - {message}"

        # Log en GUI
        self.log_text.insert(tk.END, f"{formatted_message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

        # Log en archivo
        # Quitar emojis para el archivo de log
        clean_message = message.encode('ascii', 'ignore').decode('ascii')
        self.logger.info(clean_message)

    def increment_api_calls(self, call_type='details'):
        """Incrementa contador de API calls y actualiza costo"""
        self.api_calls_count += 1

        # Costos de Places API (por llamada)
        # Text Search: $0.017
        # Details: $0.017
        cost_per_call = 0.017
        self.estimated_cost += cost_per_call

        # Actualizar GUI
        self.api_stats_var.set(
            f"API Calls: {self.api_calls_count} | Costo estimado: ${self.estimated_cost:.3f}"
        )
        self.root.update_idletasks()

    def validate_api_key(self):
        """Valida la API key haciendo una petición de prueba"""
        if not self.api_key:
            return False

        try:
            self.log("🔍 Validando API Key...")
            params = {
                'query': 'test',
                'key': self.api_key
            }

            response = requests.get(URL_TEXT_SEARCH, params=params, timeout=10)
            data = response.json()

            status = data.get('status', 'UNKNOWN')

            if status == 'REQUEST_DENIED':
                error_msg = data.get('error_message', 'API Key inválida o sin permisos')
                self.log(f"❌ API Key inválida: {error_msg}")
                return False
            elif status == 'INVALID_REQUEST' or status == 'ZERO_RESULTS' or status == 'OK':
                # Estos estados significan que la API key es válida
                self.log("✅ API Key válida")
                return True
            else:
                self.log(f"⚠️ Estado inesperado: {status}")
                return False

        except requests.RequestException as e:
            self.log(f"❌ Error validando API Key: {e}")
            return False

    def save_checkpoint(self, filename, processed_count):
        """Guarda checkpoint del progreso actual"""
        if getattr(sys, 'frozen', False):
            # Si está compilado con PyInstaller
            script_dir = os.path.dirname(sys.executable)
        else:
            # Si se ejecuta como script Python
            script_dir = os.path.dirname(os.path.abspath(__file__))
        
        checkpoint_file = os.path.join(script_dir, '.scraper_checkpoint.json')

        checkpoint_data = {
            'filename': filename,
            'processed_count': processed_count,
            'timestamp': time.time(),
            'scraped_data_count': len(self.scraped_data)
        }

        try:
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"⚠️ Error guardando checkpoint: {e}")

    def clear_checkpoint(self):
        """Elimina el archivo de checkpoint"""
        if getattr(sys, 'frozen', False):
            # Si está compilado con PyInstaller
            script_dir = os.path.dirname(sys.executable)
        else:
            # Si se ejecuta como script Python
            script_dir = os.path.dirname(os.path.abspath(__file__))
        
        checkpoint_file = os.path.join(script_dir, '.scraper_checkpoint.json')

        try:
            if os.path.exists(checkpoint_file):
                os.remove(checkpoint_file)
        except Exception as e:
            self.log(f"⚠️ Error eliminando checkpoint: {e}")

    def show_60_limit_info(self):
        """Muestra información sobre cómo obtener más de 60 resultados"""
        info_message = """Google Places API limita cada búsqueda a 60 resultados máximos.

✅ BÚSQUEDAS MÚLTIPLES AUTOMÁTICAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Escribe una palabra clave por línea en el campo de búsqueda:

   restaurantes Madrid Centro
   restaurantes Madrid Norte
   restaurantes Madrid Sur

El sistema buscará automáticamente en cada una y
combinará los resultados sin duplicados.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔹 Ejemplo por ubicación específica:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Escribe cada línea:
      restaurantes Madrid Centro
      restaurantes Madrid Norte
      restaurantes Madrid Sur
      restaurantes Madrid Este

   Resultado: 240 resultados únicos

🔹 Ejemplo por tipo de negocio:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Escribe cada línea:
      restaurantes italianos Madrid
      restaurantes japoneses Madrid
      restaurantes mexicanos Madrid

   Resultado: 180 resultados únicos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 También puedes separar por comas:
   "restaurantes Madrid, cafeterías Madrid, bares Madrid"

💡 El sistema detecta automáticamente duplicados
   entre búsquedas y con el archivo existente."""

        messagebox.showinfo("Cómo obtener más de 60 resultados", info_message)
        
    def refresh_json_files(self):
        self.files_listbox.delete(0, tk.END)
        try:
            data_dir = 'data'
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            # Listar archivos en data y sus subcarpetas
            files = []
            for root, dirs, filenames in os.walk(data_dir):
                for f in filenames:
                    if f.endswith(('.json', '.csv')):
                        # Obtener ruta relativa desde 'data/'
                        rel_path = os.path.relpath(os.path.join(root, f), data_dir)
                        files.append(rel_path)
            
            for file in sorted(files):
                self.files_listbox.insert(tk.END, file)
        except Exception as e:
            messagebox.showerror("Error", f"Error al listar archivos: {e}")
            
    def view_selected_file(self):
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un archivo para ver")
            return
        
        filename = self.files_listbox.get(selection[0])
        self.view_json_file_content(filename)
        
    def view_json_file(self, event):
        selection = self.files_listbox.curselection()
        if selection:
            filename = self.files_listbox.get(selection[0])
            self.view_json_file_content(filename)
            
    def view_json_file_content(self, filename):
        try:
            filepath = os.path.join('data', filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            self.preview_text.delete(1.0, tk.END)
            
            if file_ext == '.csv':
                # Leer archivo CSV
                with open(filepath, 'r', encoding='utf-8') as f:
                    csv_reader = csv.reader(f)
                    content = []
                    for i, row in enumerate(csv_reader):
                        if i == 0:  # Header
                            content.append(' | '.join(row))
                            content.append('-' * len(content[0]))
                        else:
                            content.append(' | '.join(row))
                        if i >= 20:  # Limitar vista previa
                            content.append('... (archivo truncado para vista previa)')
                            break
                    self.preview_text.insert(1.0, '\n'.join(content))
            else:
                # Leer archivo JSON
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.preview_text.insert(1.0, json.dumps(data, indent=2, ensure_ascii=False))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al leer el archivo: {e}")
            
    def delete_selected_file(self):
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un archivo para eliminar")
            return
        
        filename = self.files_listbox.get(selection[0])
        result = messagebox.askyesno("Confirmar", f"¿Eliminar el archivo {filename}?")
        
        if result:
            try:
                filepath = os.path.join('data', filename)
                os.remove(filepath)
                self.refresh_json_files()
                self.preview_text.delete(1.0, tk.END)
                messagebox.showinfo("Éxito", f"Archivo {filename} eliminado")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar archivo: {e}")
                
    def export_file(self):
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un archivo para exportar")
            return
        
        filename = self.files_listbox.get(selection[0])
        # Determinar extensión del archivo original
        file_ext = os.path.splitext(filename)[1]
        if file_ext == '.csv':
            default_ext = ".csv"
            filetypes = [("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        else:
            default_ext = ".json"
            filetypes = [("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        
        dest = filedialog.asksaveasfilename(
            title="Guardar archivo como",
            defaultextension=default_ext,
            filetypes=filetypes
        )
        
        if dest:
            try:
                filepath = os.path.join('data', filename)
                # Determinar la codificación apropiada según el tipo de archivo
                if dest.lower().endswith('.csv'):
                    # Para archivos CSV, usar UTF-8 con BOM para compatibilidad con Excel
                    with open(filepath, 'r', encoding='utf-8') as src:
                        with open(dest, 'w', encoding='utf-8-sig', newline='') as dst:
                            dst.write(src.read())
                else:
                    # Para otros archivos (JSON), usar UTF-8 estándar
                    with open(filepath, 'r', encoding='utf-8') as src:
                        with open(dest, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                messagebox.showinfo("Éxito", f"Archivo exportado a {dest}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {e}")
                
    def start_scraping(self):
        # Obtener texto del widget de múltiples líneas
        keywords_text = self.keyword_entry.get("1.0", tk.END).strip()
        filename = self.filename_entry.get().strip()

        if not keywords_text:
            messagebox.showerror("Error", "Ingresa al menos una palabra clave")
            return

        # Parsear keywords
        keywords = parse_keywords(keywords_text)

        if not keywords:
            messagebox.showerror("Error", "Ingresa al menos una palabra clave válida")
            return
            
        # Obtener formato seleccionado
        output_format = self.format_var.get()
        
        if not filename:
            # Usar la primera keyword para el nombre de archivo
            filename = f"{normalize_filename(keywords[0])}-data"
        else:
            # Normalizar nombre de archivo
            filename = normalize_filename(filename)
            
        # Agregar extensión apropiada
        if output_format == "csv":
            if not filename.endswith('.csv'):
                filename += '.csv'
        else:
            if not filename.endswith('.json'):
                filename += '.json'
            
        if not self.api_key:
            messagebox.showerror("Error", "No se ha cargado la API Key")
            return

        # Validar API Key antes de iniciar
        if not self.validate_api_key():
            messagebox.showerror("Error",
                               "La API Key no es válida o no tiene los permisos necesarios.\n\n"
                               "Verifica que:\n"
                               "1. La API Key sea correcta\n"
                               "2. Places API esté habilitada en tu proyecto\n"
                               "3. La facturación esté activada")
            return

        # Validar que al menos un campo esté seleccionado
        if not any(var.get() for var in self.field_vars.values()):
            messagebox.showerror("Error", "Selecciona al menos un campo para extraer")
            return
            
        self.is_scraping = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.scraped_data = []

        # Iniciar scraping en hilo separado con lista de keywords
        self.scraping_thread = threading.Thread(target=self.scrape_data, args=(keywords, filename, output_format))
        self.scraping_thread.daemon = True
        self.scraping_thread.start()
        
    def stop_scraping(self):
        self.is_scraping = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_var.set("Detenido por el usuario")
        self.log("🛑 Scraping detenido por el usuario")
    
    def refresh_scraper(self):
        """Reinicia el estado del scraper y limpia la interfaz"""
        # Detener cualquier scraping en progreso
        if self.is_scraping:
            self.stop_scraping()

            # Esperar a que el thread termine (máximo 5 segundos)
            if self.scraping_thread and self.scraping_thread.is_alive():
                self.log("⏳ Esperando a que termine el scraping actual...")
                self.scraping_thread.join(timeout=5.0)

                if self.scraping_thread.is_alive():
                    self.log("⚠️ El thread de scraping no terminó, pero se reiniciará la interfaz")

        # Reiniciar variable de thread
        self.scraping_thread = None

        # Limpiar log
        self.log_text.delete(1.0, tk.END)

        # Reiniciar barra de progreso
        self.progress_bar['value'] = 0
        self.progress_var.set("Listo para comenzar")

        # Limpiar datos scrapeados
        self.scraped_data = []

        # Reiniciar contadores de API
        self.api_calls_count = 0
        self.estimated_cost = 0.0
        self.api_stats_var.set("API Calls: 0 | Costo estimado: $0.00")

        # Limpiar cache de emails
        self.visited_websites_no_email.clear()

        # Reiniciar estado de botones
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

        # Actualizar lista de archivos
        self.refresh_json_files()

        # Limpiar vista previa
        self.preview_text.delete(1.0, tk.END)

        # Log de reinicio
        self.log("🔄 Aplicación reiniciada - Lista para nuevo scraping")
    
    def load_existing_place_ids(self, filename, output_format):
        """Carga place_ids existentes del archivo para evitar duplicados"""
        # El archivo ahora está en data/nombre-archivo/nombre-archivo.ext
        folder = os.path.splitext(filename)[0]
        filepath = os.path.join('data', folder, filename)
        existing_place_ids = set()
        
        if not os.path.exists(filepath):
            return existing_place_ids
        
        try:
            if output_format == "csv":
                with open(filepath, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        if 'place_id' in row and row['place_id']:
                            existing_place_ids.add(row['place_id'])
            else:  # JSON
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        if 'place_id' in item and item['place_id']:
                            existing_place_ids.add(item['place_id'])
        except (json.JSONDecodeError, IOError, csv.Error) as e:
            self.log(f"⚠️ Error leyendo archivo existente: {e}")
            return set()
        
        return existing_place_ids
    
    def extract_email_from_website(self, website_url):
        """Extrae emails del sitio web del negocio con búsqueda inteligente mejorada"""
        # Verificar si ya intentamos buscar en esta URL sin éxito
        if website_url in self.visited_websites_no_email:
            return None

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        # Patrón de email mejorado que incluye más TLDs
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,10}\b'
        
        # Filtros menos restrictivos - solo excluir emails claramente no válidos
        exclude_patterns = [
            'noreply', 'no-reply', 'donotreply', 'example.com', 'test.com',
            'placeholder', 'yourname', 'youremail', 'sample', 'demo'
        ]

        def filter_emails(emails_list):
            """Filtra emails no válidos con criterios menos restrictivos"""
            filtered = []
            for email in emails_list:
                email_lower = email.lower()
                # Solo excluir si contiene patrones claramente no válidos
                if not any(pattern in email_lower for pattern in exclude_patterns):
                    # Validar que tenga formato básico correcto
                    if '@' in email and '.' in email.split('@')[1]:
                        filtered.append(email)
            return filtered

        def extract_from_soup(soup):
            """Extrae emails de BeautifulSoup object con estrategias mejoradas"""
            found_emails = []
            
            # 1. Buscar mailto: links (más confiable)
            mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.I))
            for link in mailto_links:
                email = link['href'].replace('mailto:', '').split('?')[0].split('&')[0]
                found_emails.append(email)

            # 2. Buscar en elementos específicos de contacto (prioridad alta)
            contact_selectors = [
                'footer', '.footer', '#footer',
                '.contact', '#contact', '.contact-info', '.contact-details',
                '.email', '.email-address', '.mail',
                '.info', '.information', '.datos-contacto',
                'address', '.address', '.direccion'
            ]
            
            for selector in contact_selectors:
                try:
                    elements = soup.select(selector)
                    for elem in elements:
                        emails = re.findall(email_pattern, elem.get_text())
                        found_emails.extend(emails)
                except:
                    continue

            # 3. Buscar en meta tags y structured data
            meta_tags = soup.find_all('meta', attrs={'name': re.compile(r'email|contact', re.I)})
            for meta in meta_tags:
                content = meta.get('content', '')
                emails = re.findall(email_pattern, content)
                found_emails.extend(emails)

            # 4. Buscar en JSON-LD structured data
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        # Buscar email en diferentes campos
                        for key in ['email', 'contactPoint', 'contact']:
                            if key in data:
                                if isinstance(data[key], str):
                                    emails = re.findall(email_pattern, data[key])
                                    found_emails.extend(emails)
                except:
                    continue

            # 5. Buscar en texto completo (última opción)
            if not found_emails:
                text_content = soup.get_text()
                emails = re.findall(email_pattern, text_content)
                found_emails.extend(emails)

            # Filtrar y devolver el mejor email
            filtered = filter_emails(found_emails)
            if filtered:
                # Priorizar emails que no sean de servicios gratuitos
                business_emails = [e for e in filtered if not any(domain in e.lower() 
                                 for domain in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'])]
                return business_emails[0] if business_emails else filtered[0]
            
            return None

        try:
            # Parse base URL
            from urllib.parse import urlparse, urljoin
            parsed_url = urlparse(website_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

            # 1. Intentar páginas de contacto ampliadas (timeout 8s)
            contact_pages = [
                '/contact', '/contacto', '/contact-us', '/contactenos', '/en/contact',
                '/contact.html', '/contacto.html', '/contact.php', '/contacto.php',
                '/about', '/sobre-nosotros', '/about-us', '/acerca-de',
                '/info', '/informacion', '/information',
                '/team', '/equipo', '/staff', '/personal'
            ]

            self.log(f"   🔍 Buscando email en páginas de contacto...")
            for contact_path in contact_pages:
                try:
                    contact_url = urljoin(base_url, contact_path)
                    response = requests.get(contact_url, headers=headers, timeout=8)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        email = extract_from_soup(soup)
                        if email:
                            self.log(f"   ✅ Email encontrado en {contact_path}: {email}")
                            return email
                except:
                    continue

            # 2. Buscar en página principal con análisis más profundo
            self.log(f"   🔍 Buscando email en página principal...")
            response = requests.get(website_url, headers=headers, timeout=12)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            email = extract_from_soup(soup)

            if email:
                self.log(f"   ✅ Email encontrado en página principal: {email}")
                return email
            else:
                # Agregar a cache de URLs sin email
                self.visited_websites_no_email.add(website_url)
                self.log(f"   ❌ No se encontró email válido en {website_url}")
                return None

        except Exception as e:
            # Agregar a cache en caso de error
            self.visited_websites_no_email.add(website_url)
            self.log(f"   ⚠️ Error extrayendo email de {website_url}: {str(e)[:100]}")
            return None
        
    def search_businesses(self, business_name: str) -> List[Dict]:
        """Busca múltiples negocios y retorna lista de place_ids con nombres"""
        all_results = []
        next_page_token = None
        
        try:
            max_results = getattr(self, 'max_results_var', None)
            limit_str = max_results.get().strip() if max_results else ""
            if limit_str == "":
                limit = None  # Sin límite si está vacío
            else:
                limit = int(limit_str)
                if limit <= 0:
                    limit = None  # Sin límite si es 0 o negativo
        except (tk.TclError, ValueError):
            limit = None  # Sin límite si hay error
        
        
        while limit is None or len(all_results) < limit:
            params = {
                'query': business_name,
                'key': self.api_key,
                'fields': 'place_id,name'
            }
            
            if next_page_token:
                params['pagetoken'] = next_page_token
            
            try:
                response = requests.get(URL_TEXT_SEARCH, params=params, timeout=10)

                # Manejar Rate Limiting (429)
                if response.status_code == 429:
                    self.log("⚠️ Rate limit alcanzado en búsqueda. Esperando 60 segundos...")
                    time.sleep(60)
                    # Reintentar la misma petición
                    response = requests.get(URL_TEXT_SEARCH, params=params, timeout=10)

                response.raise_for_status()
                data = response.json()

                # Incrementar contador de API calls
                self.increment_api_calls('search')

                results = data.get('results', [])

                for result in results:
                    if result.get('place_id'):
                        all_results.append({
                            'place_id': result.get('place_id'),
                            'name': result.get('name', 'Sin nombre')
                        })

                # Verificar si hay más páginas
                next_page_token = data.get('next_page_token')
                if not next_page_token:
                    break

                # Delay requerido antes de usar next_page_token
                time.sleep(2)

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    self.log(f"❌ Error 403: API Key sin permisos o Places API no habilitada")
                else:
                    self.log(f"❌ Error HTTP {e.response.status_code}: {e}")
                break
            except requests.RequestException as e:
                self.log(f"⚠️ Error buscando '{business_name}': {e}")
                break
                
        return all_results
            
    def get_business_details(self, place_id: str) -> Optional[BusinessData]:
        # Construir campos basados en selección del usuario
        fields = ['name']
        if self.field_vars['phone'].get():
            fields.append('formatted_phone_number')
        if self.field_vars['website'].get():
            fields.append('website')
        if self.field_vars['address'].get():
            fields.append('formatted_address')
        if self.field_vars['rating'].get():
            fields.extend(['rating', 'user_ratings_total'])
        if self.field_vars['opening_hours'].get():
            fields.append('opening_hours')
        if self.field_vars['price_level'].get():
            fields.append('price_level')
            
        params = {
            'place_id': place_id,
            'key': self.api_key,
            'fields': ','.join(fields)
        }
        
        try:
            response = requests.get(URL_PLACE_DETAILS, params=params, timeout=10)

            # Manejar Rate Limiting (429)
            if response.status_code == 429:
                self.log("⚠️ Rate limit alcanzado en detalles. Esperando 60 segundos...")
                time.sleep(60)
                # Reintentar la misma petición
                response = requests.get(URL_PLACE_DETAILS, params=params, timeout=10)

            response.raise_for_status()
            result = response.json().get('result', {})

            # Incrementar contador de API calls
            self.increment_api_calls('details')

            # Construir objeto con solo los campos seleccionados
            business_data = BusinessData(
                title=result.get('name', ''),
                phone=result.get('formatted_phone_number') if self.field_vars['phone'].get() else None,
                website=result.get('website') if self.field_vars['website'].get() else None,
                address=result.get('formatted_address') if self.field_vars['address'].get() else None,
                place_id=place_id if self.field_vars['place_id'].get() else None,
                rating=result.get('rating') if self.field_vars['rating'].get() else None,
                total_ratings=result.get('user_ratings_total') if self.field_vars['total_ratings'].get() else None,
                opening_hours=str(result.get('opening_hours', {}).get('weekday_text', [])) if self.field_vars['opening_hours'].get() else None,
                price_level=result.get('price_level') if self.field_vars['price_level'].get() else None,
                email=None  # Se llenará después si está habilitado
            )

            return business_data

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                self.log(f"❌ Error 403: API Key sin permisos")
            elif e.response.status_code == 404:
                self.log(f"⚠️ Place ID no encontrado: {place_id}")
            else:
                self.log(f"❌ Error HTTP {e.response.status_code} para '{place_id}'")
            return None
        except requests.RequestException as e:
            self.log(f"⚠️ Error obteniendo detalles para place_id '{place_id}': {e}")
            return None
            
    def scrape_data(self, keywords, filename, output_format="json"):
        if isinstance(keywords, str):
            keywords = [keywords]  # Compatibilidad con llamadas antiguas

        total_keywords = len(keywords)
        if total_keywords == 1:
            self.log(f"🔍 Iniciando scraping para: {keywords[0]}")
        else:
            self.log(f"🔍 Iniciando scraping para {total_keywords} palabras clave")
            for idx, kw in enumerate(keywords, 1):
                self.log(f"   {idx}. {kw}")
        
        # Cargar place_ids ya existentes para evitar duplicados
        existing_place_ids = self.load_existing_place_ids(filename, output_format)
        if existing_place_ids:
            self.log(f"📋 Se encontraron {len(existing_place_ids)} registros existentes en el archivo")
        
        # Verificar límite de resultados
        try:
            limit_str = self.max_results_var.get().strip()
            if limit_str == "":
                self.log(f"📋 Configurado para extraer TODOS los resultados disponibles")
                self.log(f"⚠️ Nota: Google Places API limita a 60 resultados por búsqueda")
                self.log(f"💡 Tip: Para más resultados, usa búsquedas específicas (ej: 'restaurantes Madrid Centro')")
            else:
                limit_val = int(limit_str)
                self.log(f"📋 Configurado para extraer hasta {limit_val} resultados")
                if limit_val > 60:
                    self.log(f"⚠️ Nota: Google Places API limita a 60 resultados por búsqueda")
                    self.log(f"💡 Tip: Para más resultados, usa búsquedas específicas por ubicación o tipo")
                    self.log(f"   Ejemplo: 'restaurantes Madrid Centro', 'restaurantes Madrid Norte', etc.")
        except (ValueError, tk.TclError):
            self.log(f"📋 Configurado para extraer TODOS los resultados disponibles")
            self.log(f"⚠️ Nota: Google Places API limita a 60 resultados por búsqueda")
        
        self.progress_var.set("Buscando negocios...")

        # Acumular todos los negocios de todas las búsquedas
        all_businesses_combined = []
        total_found = 0

        for idx, keyword in enumerate(keywords, 1):
            if not self.is_scraping:
                break

            if total_keywords > 1:
                self.log(f"\n🔎 Búsqueda {idx}/{total_keywords}: '{keyword}'")

            # Buscar negocios para esta keyword
            keyword_businesses = self.search_businesses(keyword)
            total_found += len(keyword_businesses)

            if not keyword_businesses:
                self.log(f"❌ No se encontraron resultados para '{keyword}'")
                continue

            # Filtrar duplicados
            new_businesses = [b for b in keyword_businesses if b['place_id'] not in existing_place_ids]
            duplicates = len(keyword_businesses) - len(new_businesses)

            if duplicates > 0:
                self.log(f"   📋 Encontrados: {len(keyword_businesses)} negocios ({duplicates} duplicados omitidos)")
            else:
                self.log(f"   📋 Encontrados: {len(keyword_businesses)} negocios nuevos")

            # Agregar place_ids nuevos al set para evitar duplicados en siguientes búsquedas
            for b in new_businesses:
                existing_place_ids.add(b['place_id'])

            all_businesses_combined.extend(new_businesses)

        if not all_businesses_combined:
            if total_found == 0:
                self.log(f"\n❌ No se encontraron negocios para ninguna búsqueda")
            else:
                self.log(f"\nℹ️ Todos los negocios encontrados ya existen en el archivo")
            self.progress_var.set("No hay nuevos resultados")
            self.stop_scraping()
            return

        businesses = all_businesses_combined

        self.log(f"\n📊 Resumen de búsquedas:")
        self.log(f"   Total encontrado: {total_found} negocios")
        self.log(f"   Nuevos únicos: {len(businesses)} negocios")
        self.log(f"✨ Procesando {len(businesses)} negocios...")

        self.progress_bar.config(maximum=len(businesses))
        self.progress_bar['value'] = 0
        
        # Procesar cada negocio
        processed_count = 0
        batch_count = 0
        
        for i, business in enumerate(businesses):
            if not self.is_scraping:
                break
                
            self.progress_var.set(f"Procesando {i+1}/{len(businesses)}: {business['name']}")
            self.log(f"🔍 Procesando [{i+1}/{len(businesses)}]: {business['name']}")
            
            # Obtener detalles
            business_data = self.get_business_details(business['place_id'])
            
            if business_data:
                # Extraer email del sitio web si está habilitado
                if self.field_vars['email'].get() and business_data.website:
                    self.log(f"   🔍 Buscando email en: {business_data.website}")
                    email = self.extract_email_from_website(business_data.website)
                    if email:
                        business_data.email = email
                        self.log(f"   📧 Email encontrado: {email}")
                    else:
                        self.log(f"   ❌ No se encontró email en el sitio web")
                
                self.scraped_data.append(business_data)
                processed_count += 1

                # Guardar checkpoint cada 10 registros
                if processed_count % 10 == 0:
                    self.save_checkpoint(filename, processed_count)
                    self.log(f"💾 Checkpoint guardado: {processed_count} registros procesados")

                # Mostrar datos extraídos
                self.log(f"✅ Datos extraídos para '{business_data.title}'")
                if business_data.phone:
                    self.log(f"   📞 Teléfono: {business_data.phone}")
                if business_data.website:
                    self.log(f"   🌐 Sitio web: {business_data.website}")
                if business_data.address:
                    self.log(f"   📍 Dirección: {business_data.address}")
                if business_data.rating:
                    self.log(f"   ⭐ Rating: {business_data.rating} ({business_data.total_ratings or 0} reseñas)")
                if business_data.email:
                    self.log(f"   📧 Email: {business_data.email}")
            else:
                self.log(f"❌ No se pudieron obtener detalles para '{business['name']}'")
            
            # Actualizar barra de progreso
            self.progress_bar['value'] = i + 1
            
            # Aplicar delay entre peticiones
            try:
                min_delay = self.min_delay_var.get() or 1.5
                max_delay = self.max_delay_var.get() or 3.0
                delay = random.uniform(min_delay, max_delay)
            except (tk.TclError, ValueError):
                delay = 2.0
            time.sleep(delay)
            
            # Aplicar delay entre lotes
            batch_count += 1
            try:
                batch_size = self.batch_size_var.get() or 5
                batch_delay_base = self.batch_delay_var.get() or 10.0
            except (tk.TclError, ValueError):
                batch_size = 5
                batch_delay_base = 10.0
                
            if batch_count >= batch_size and i < len(businesses) - 1:
                batch_delay = random.uniform(batch_delay_base, batch_delay_base + 5.0)
                self.log(f"⏳ Pausa entre lotes: {batch_delay:.1f}s")
                time.sleep(batch_delay)
                batch_count = 0
        
        # Guardar todos los datos (combinando con existentes)
        if self.scraped_data:
            # El archivo se guarda en data/nombre-archivo/nombre-archivo.ext
            folder = os.path.splitext(filename)[0]
            filepath = os.path.join('data', folder, filename)
            if output_format == "csv":
                self.save_data_to_csv(filepath, merge_with_existing=True)
            else:
                self.save_data_to_json(filepath, merge_with_existing=True)
            
            total_in_file = len(existing_place_ids) + processed_count
            folder = os.path.splitext(filename)[0]
            self.log(f"💾 Datos guardados en: data/{folder}/{filename}")
            self.log(f"🏁 Completado: {processed_count} negocios nuevos procesados")
            self.log(f"📊 Total en archivo: {total_in_file} negocios")

            # Limpiar checkpoint al finalizar exitosamente
            self.clear_checkpoint()
        else:
            self.log(f"❌ No se obtuvieron nuevos datos para '{keyword}'")

        self.progress_var.set(f"Completado: {processed_count} negocios")
        self.is_scraping = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.refresh_json_files()
        
    def save_data_to_json(self, filepath, merge_with_existing=False):
        # Asegurar que el directorio data existe
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        json_data = []
        
        # Si merge_with_existing=True, cargar datos existentes primero
        if merge_with_existing and os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                json_data = []
        
        # Agregar nuevos datos
        for business in self.scraped_data:
            data_dict = {}
            
            # Solo incluir campos seleccionados
            if self.field_vars['title'].get():
                data_dict['titulo'] = business.title
            if self.field_vars['phone'].get() and business.phone:
                data_dict['telefono'] = business.phone
            if self.field_vars['website'].get() and business.website:
                data_dict['sitio_web'] = business.website
            if self.field_vars['address'].get() and business.address:
                data_dict['direccion'] = business.address
            if self.field_vars['place_id'].get() and business.place_id:
                data_dict['place_id'] = business.place_id
            if self.field_vars['rating'].get() and business.rating:
                data_dict['rating'] = business.rating
            if self.field_vars['total_ratings'].get() and business.total_ratings:
                data_dict['total_ratings'] = business.total_ratings
            if self.field_vars['opening_hours'].get() and business.opening_hours:
                data_dict['horarios'] = business.opening_hours
            if self.field_vars['price_level'].get() and business.price_level:
                data_dict['nivel_precios'] = business.price_level
            if self.field_vars['email'].get() and business.email:
                data_dict['email'] = business.email
                
            json_data.append(data_dict)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    def save_data_to_csv(self, filepath, merge_with_existing=False):
        # Asegurar que el directorio data existe
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Crear lista de campos seleccionados
        fieldnames = []
        field_mapping = {
            'title': 'titulo',
            'phone': 'telefono', 
            'website': 'sitio_web',
            'address': 'direccion',
            'place_id': 'place_id',
            'rating': 'rating',
            'total_ratings': 'total_ratings',
            'opening_hours': 'horarios',
            'price_level': 'nivel_precios',
            'email': 'email'
        }
        
        for field, csv_name in field_mapping.items():
            if self.field_vars[field].get():
                fieldnames.append(csv_name)
        
        # Preparar nuevas filas
        new_rows = []
        for business in self.scraped_data:
            row = {}
            
            if self.field_vars['title'].get():
                row['titulo'] = business.title or ''
            if self.field_vars['phone'].get() and business.phone:
                row['telefono'] = business.phone
            if self.field_vars['website'].get() and business.website:
                row['sitio_web'] = business.website
            if self.field_vars['address'].get() and business.address:
                row['direccion'] = business.address
            if self.field_vars['place_id'].get() and business.place_id:
                row['place_id'] = business.place_id
            if self.field_vars['rating'].get() and business.rating:
                row['rating'] = business.rating
            if self.field_vars['total_ratings'].get() and business.total_ratings:
                row['total_ratings'] = business.total_ratings
            if self.field_vars['opening_hours'].get() and business.opening_hours:
                row['horarios'] = business.opening_hours
            if self.field_vars['price_level'].get() and business.price_level:
                row['nivel_precios'] = business.price_level
            if self.field_vars['email'].get() and business.email:
                row['email'] = business.email
            
            new_rows.append(row)
        
        # Si merge_with_existing=True y el archivo existe, anexar datos
        if merge_with_existing and os.path.exists(filepath):
            # Anexar al archivo existente
            with open(filepath, 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                for row in new_rows:
                    writer.writerow(row)
        else:
            # Escribir archivo CSV nuevo
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in new_rows:
                    writer.writerow(row)

    def setup_credits_section(self):
        """Añade sección de créditos en la parte inferior"""
        credits_frame = tk.Frame(self.root, bg='#f0f0f0', relief='sunken', bd=1)
        credits_frame.pack(side='bottom', fill='x', padx=5, pady=2)
        
        # Texto del creador
        creator_label = tk.Label(credits_frame, text="Creado por: Konstantin Koshkarev - ", 
                                font=('Arial', 9), bg='#f0f0f0', fg='#666666')
        creator_label.pack(side='left', padx=5)
        
        # Enlace clickeable
        link_label = tk.Label(credits_frame, text="webdesignerk.com", 
                             font=('Arial', 9, 'underline'), bg='#f0f0f0', 
                             fg='#0066cc', cursor='hand2')
        link_label.pack(side='left')
        link_label.bind("<Button-1>", self.open_website)
        
        # Cambio de color al hacer hover
        def on_enter(event):
            link_label.config(fg='#004499')
        def on_leave(event):
            link_label.config(fg='#0066cc')
            
        link_label.bind("<Enter>", on_enter)
        link_label.bind("<Leave>", on_leave)
    
    def open_website(self, event):
        """Abre el sitio web en el navegador predeterminado"""
        webbrowser.open("https://webdesignerk.com")

def main():
    # Cambiar al directorio del script o ejecutable
    if getattr(sys, 'frozen', False):
        # Si está compilado con PyInstaller
        script_dir = os.path.dirname(sys.executable)
    else:
        # Si se ejecuta como script Python
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    os.chdir(script_dir)
    
    root = tk.Tk()
    app = GoogleMyBusinessScraperGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()