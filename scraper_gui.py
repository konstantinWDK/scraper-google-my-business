#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import csv
import os
import threading
import requests
import time
import random
import re
from dataclasses import dataclass
from typing import List, Optional, Dict
import unicodedata

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

# Configuración por defecto
DEFAULT_API_KEY_FILE = 'google_api_key.txt'
URL_TEXT_SEARCH = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
URL_PLACE_DETAILS = 'https://maps.googleapis.com/maps/api/place/details/json'

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

class GoogleMyBusinessScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Google My Business Scraper")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.api_key = None
        self.is_scraping = False
        self.scraped_data = []
        
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
        
        self.setup_scraping_tab()
        self.setup_files_tab()
    
    def setup_scraping_tab(self):
        # Título
        title_label = tk.Label(self.scraping_frame, text="Google My Business Scraper", 
                              font=('Arial', 16, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=10)
        
        # Frame para entrada de datos
        input_frame = ttk.LabelFrame(self.scraping_frame, text="Configuración de Búsqueda", padding=10)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        # Entrada de palabra clave
        tk.Label(input_frame, text="Palabra clave para buscar:").grid(row=0, column=0, sticky='w', pady=5)
        self.keyword_entry = tk.Entry(input_frame, width=50, font=('Arial', 10))
        self.keyword_entry.grid(row=0, column=1, columnspan=2, sticky='ew', pady=5)
        
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
            'price_level': tk.BooleanVar(value=False)
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
            'price_level': 'Nivel de Precios'
        }
        
        row = 0
        col = 0
        for field, var in self.field_vars.items():
            cb = tk.Checkbutton(fields_frame, text=field_labels[field], variable=var)
            cb.grid(row=row, column=col, sticky='w', padx=10, pady=2)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
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
        tk.Label(api_frame, text="Máx resultados:").grid(row=2, column=0, sticky='w', pady=2)
        self.max_results_var = tk.StringVar(value="")
        max_results_spinbox = tk.Spinbox(api_frame, from_=1, to=200, width=8,
                                        textvariable=self.max_results_var)
        max_results_spinbox.grid(row=2, column=1, sticky='w', padx=5)
        tk.Label(api_frame, text="(vacío = todos)").grid(row=2, column=2, sticky='w', padx=5)
        
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
        
    def load_api_key(self):
        """Carga la API key desde diferentes fuentes (variables de entorno, archivo, etc.)"""
        try:
            # Prioridad 1: Variable de entorno
            api_key = os.environ.get('GOOGLE_PLACES_API_KEY')
            if api_key:
                self.api_key = api_key.strip()
                self.log("✅ API Key cargada desde variable de entorno")
                return
            
            # Prioridad 2: Archivo local
            if os.path.isfile(DEFAULT_API_KEY_FILE):
                with open(DEFAULT_API_KEY_FILE, 'r', encoding='utf-8') as f:
                    self.api_key = f.read().strip()
                self.log("✅ API Key cargada desde archivo local")
                return
            
            # No se encontró API key
            self.log("❌ No se encontró API Key")
            messagebox.showerror("Error de API Key", 
                               f"No se encontró la API Key. Opciones:\n\n"
                               f"1. Crear archivo: {DEFAULT_API_KEY_FILE}\n"
                               f"2. Variable de entorno: GOOGLE_PLACES_API_KEY\n"
                               f"3. Usar el archivo de ejemplo como plantilla")
        except Exception as e:
            self.log(f"❌ Error cargando API Key: {e}")
            messagebox.showerror("Error", f"Error al cargar API Key: {e}")
            
    def log(self, message):
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def refresh_json_files(self):
        self.files_listbox.delete(0, tk.END)
        try:
            data_dir = 'data'
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            files = [f for f in os.listdir(data_dir) if f.endswith(('.json', '.csv'))]
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
                with open(filepath, 'r', encoding='utf-8') as src:
                    with open(dest, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                messagebox.showinfo("Éxito", f"Archivo exportado a {dest}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {e}")
                
    def start_scraping(self):
        keyword = self.keyword_entry.get().strip()
        filename = self.filename_entry.get().strip()
        
        if not keyword:
            messagebox.showerror("Error", "Ingresa una palabra clave")
            return
            
        # Obtener formato seleccionado
        output_format = self.format_var.get()
        
        if not filename:
            filename = f"{normalize_filename(keyword)}-data"
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
            
        # Validar que al menos un campo esté seleccionado
        if not any(var.get() for var in self.field_vars.values()):
            messagebox.showerror("Error", "Selecciona al menos un campo para extraer")
            return
            
        self.is_scraping = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.scraped_data = []
        
        # Iniciar scraping en hilo separado
        thread = threading.Thread(target=self.scrape_data, args=(keyword, filename, output_format))
        thread.daemon = True
        thread.start()
        
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
        
        # Limpiar log
        self.log_text.delete(1.0, tk.END)
        
        # Reiniciar barra de progreso
        self.progress_bar['value'] = 0
        self.progress_var.set("Listo para comenzar")
        
        # Limpiar datos scrapeados
        self.scraped_data = []
        
        # Reiniciar estado de botones
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        # Actualizar lista de archivos
        self.refresh_json_files()
        
        # Limpiar vista previa
        self.preview_text.delete(1.0, tk.END)
        
        # Log de reinicio
        self.log("🔄 Aplicación reiniciada - Lista para nuevo scraping")
        
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
                response.raise_for_status()
                data = response.json()
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
            response.raise_for_status()
            result = response.json().get('result', {})
            
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
                price_level=result.get('price_level') if self.field_vars['price_level'].get() else None
            )
            
            return business_data
            
        except requests.RequestException as e:
            self.log(f"⚠️ Error obteniendo detalles para place_id '{place_id}': {e}")
            return None
            
    def scrape_data(self, keyword, filename, output_format="json"):
        self.log(f"🔍 Iniciando scraping para: {keyword}")
        
        # Verificar límite de resultados
        try:
            limit_str = self.max_results_var.get().strip()
            if limit_str == "":
                self.log(f"📋 Configurado para extraer TODOS los resultados disponibles")
            else:
                limit_val = int(limit_str)
                self.log(f"📋 Configurado para extraer hasta {limit_val} resultados")
        except (ValueError, tk.TclError):
            self.log(f"📋 Configurado para extraer TODOS los resultados disponibles")
        
        self.progress_var.set("Buscando negocios...")
        
        # Buscar múltiples negocios
        businesses = self.search_businesses(keyword)
        if not businesses:
            self.log(f"❌ No se encontraron negocios para '{keyword}'")
            self.progress_var.set("No se encontraron resultados")
            self.stop_scraping()
            return
            
        self.log(f"📋 Se encontraron {len(businesses)} negocios")
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
                self.scraped_data.append(business_data)
                processed_count += 1
                
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
        
        # Guardar todos los datos
        if self.scraped_data:
            filepath = os.path.join('data', filename)
            if output_format == "csv":
                self.save_data_to_csv(filepath)
            else:
                self.save_data_to_json(filepath)
            self.log(f"💾 Datos guardados en: data/{filename}")
            self.log(f"🏁 Completado: {processed_count} negocios procesados de {len(businesses)} encontrados")
        else:
            self.log(f"❌ No se obtuvieron datos para '{keyword}'")
            
        self.progress_var.set(f"Completado: {processed_count} negocios")
        self.is_scraping = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.refresh_json_files()
        
    def save_data_to_json(self, filepath):
        # Asegurar que el directorio data existe
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        json_data = []
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
                
            json_data.append(data_dict)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    def save_data_to_csv(self, filepath):
        # Asegurar que el directorio data existe
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if not self.scraped_data:
            return
        
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
            'price_level': 'nivel_precios'
        }
        
        for field, csv_name in field_mapping.items():
            if self.field_vars[field].get():
                fieldnames.append(csv_name)
        
        # Escribir archivo CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
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
                
                writer.writerow(row)

def main():
    # Cambiar al directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    root = tk.Tk()
    app = GoogleMyBusinessScraperGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()