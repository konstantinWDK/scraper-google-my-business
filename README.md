# Google My Business Scraper

Extrae datos de perfiles de Google My Business utilizando la API de Google Places con interfaz gráfica amigable.

## 🎯 Características

- **Interfaz gráfica intuitiva** con pestañas organizadas
- **Múltiples resultados**: Extrae todos los negocios disponibles o limita la cantidad
- **Campos configurables**: Elige qué datos extraer (teléfono, sitio web, dirección, etc.)
- **Control de velocidad**: Evita límites de API con delays configurables
- **Gestión de archivos**: Ve, elimina y exporta archivos JSON
- **Seguridad mejorada**: Soporte para variables de entorno

## 📊 Datos Extraídos

- ✅ **Título**: Nombre del negocio
- 📞 **Teléfono**: Número formateado
- 🌐 **Sitio Web**: URL oficial
- 📍 **Dirección**: Dirección completa
- ⭐ **Rating**: Calificación promedio
- 👥 **Total Reseñas**: Número de reseñas
- 🆔 **Place ID**: Identificador único (opcional)
- 🕒 **Horarios**: Horarios de apertura (opcional)
- 💰 **Nivel de Precios**: Escala de precios (opcional)

## 🔐 Configuración de API Key (SEGURA)

### Opción 1: Variable de Entorno (Recomendado)
```bash
# Linux/Mac
export GOOGLE_PLACES_API_KEY="tu_api_key_aqui"

# Windows
set GOOGLE_PLACES_API_KEY=tu_api_key_aqui
```

### Opción 2: Archivo Local
```bash
# Copia el archivo de ejemplo
cp google_api_key.txt.example google_api_key.txt

# Edita y agrega tu API key
nano google_api_key.txt
```

### Opción 3: .env File (Para desarrollo)
```bash
echo "GOOGLE_PLACES_API_KEY=tu_api_key_aqui" > .env
```

## 🚀 Instalación y Uso

### Requisitos
```bash
pip install -r requirements.txt
```

### Ejecutar la aplicación
```bash
python3 scraper_gui.py
```

### Script de lanzamiento
```bash
./launch_gui.sh
```

## 🎮 Cómo Usar la Interfaz

### Pestaña Scraper
1. **Palabra clave**: Introduce el término de búsqueda (ej: "museos en madrid")
2. **Nombre archivo**: Nombre del JSON (opcional, se auto-genera)
3. **Campos**: Selecciona qué datos extraer
4. **Configuración API**: Ajusta velocidad y límites
5. **Máx resultados**: Número máximo (vacío = todos)

### Pestaña Gestión de Archivos
- **Ver archivos**: Lista todos los JSON generados
- **Vista previa**: Examina el contenido
- **Eliminar**: Borra archivos innecesarios
- **Exportar**: Guarda en otra ubicación

## ⚙️ Configuración de API

### Para uso normal
- **Min delay**: 1.5 seg
- **Max delay**: 3.0 seg
- **Tamaño lote**: 5
- **Delay entre lotes**: 10 seg
- **Máx resultados**: 20 (o vacío para todos)

### Para uso intensivo (más seguro)
- **Min delay**: 2.0 seg
- **Max delay**: 4.0 seg
- **Tamaño lote**: 3
- **Delay entre lotes**: 15 seg
- **Máx resultados**: 50

## 📁 Estructura del Proyecto

```
scraper-google-my-business/
├── scraper_gui.py              # 🎯 Aplicación principal
├── google_api_key.txt.example  # 📋 Plantilla para API key
├── data/                       # 📁 Archivos JSON generados
├── .gitignore                  # 🔒 Excluye archivos sensibles
├── requirements.txt            # 📦 Dependencias
├── launch_gui.sh              # 🚀 Script de lanzamiento
└── README.md                  # 📖 Esta documentación
```

## 🔒 Seguridad

### ✅ Buenas Prácticas
- **API Key protegida**: No se incluye en el repositorio
- **Variables de entorno**: Método más seguro
- **gitignore configurado**: Excluye archivos sensibles
- **Plantilla incluida**: Para facilitar configuración

### ❌ Evitar
- No commitear archivos `.txt` con API keys
- No hardcodear API keys en el código
- No compartir archivos con credenciales

## 🎯 Ejemplos de Uso

### Buscar todos los museos de una ciudad
- **Palabra clave**: `"museos en valencia"`
- **Máx resultados**: `(vacío)`
- **Archivo**: `museos-valencia`

### Buscar restaurantes específicos
- **Palabra clave**: `"restaurantes japoneses madrid"`
- **Máx resultados**: `15`
- **Campos**: Título, Teléfono, Dirección, Rating

### Buscar tiendas de una marca
- **Palabra clave**: `"zara españa"`
- **Máx resultados**: `30`
- **Campos**: Todos los campos

## 📋 Formato de Salida

Los datos se guardan en `data/nombre-archivo.json`:

```json
[
  {
    "titulo": "MACA Contemporary Art Museum of Alicante",
    "telefono": "965 21 31 56",
    "sitio_web": "http://www.maca-alicante.es/",
    "direccion": "Pl. Sta. María, 3, 03002 Alicante (Alacant), Alicante, Spain",
    "rating": 4.5,
    "total_ratings": 2240,
    "place_id": "ChIJrSMK3IIoQg0Rav9ooGbsHMY",
    "horarios": "['Monday: Closed', 'Tuesday: 11:00 AM – 2:30 PM, 5:00 – 9:00 PM', 'Wednesday: 11:00 AM – 2:30 PM, 5:00 – 9:00 PM', 'Thursday: 11:00 AM – 2:30 PM, 5:00 – 9:00 PM', 'Friday: 11:00 AM – 2:30 PM, 5:00 – 9:00 PM', 'Saturday: 11:00 AM – 2:30 PM, 5:00 – 9:00 PM', 'Sunday: 11:00 AM – 2:30 PM']",
    "nivel_precios": null
  },
  {
    "titulo": "Museo de Bellas Artes Gravina",
    "telefono": "965 14 67 80",
    "sitio_web": "https://www.museobbaa.com/",
    "direccion": "C/ Gravina, 13-15, 03002 Alicante, Spain",
    "rating": 4.3,
    "total_ratings": 1256,
    "place_id": "ChIJBVEFn6KipBIRzU1sb_VhEJQ",
    "horarios": "['Monday: 10:00 AM – 8:00 PM', 'Tuesday: 10:00 AM – 8:00 PM', 'Wednesday: 10:00 AM – 8:00 PM', 'Thursday: 10:00 AM – 8:00 PM', 'Friday: 10:00 AM – 8:00 PM', 'Saturday: 10:00 AM – 8:00 PM', 'Sunday: 10:00 AM – 3:00 PM']",
    "nivel_precios": 1
  },
  {
    "titulo": "Centro Cultural Las Cigarreras",
    "telefono": "965 14 20 25",
    "sitio_web": "https://www.lascigarreras.com/",
    "direccion": "C/ San Carlos, 78, 03013 Alicante, Spain",
    "rating": 4.1,
    "total_ratings": 892,
    "place_id": "ChIJc-SvJtmipBIRKX04XlrNzTo",
    "horarios": "['Monday: 9:00 AM – 2:00 PM, 5:00 – 9:00 PM', 'Tuesday: 9:00 AM – 2:00 PM, 5:00 – 9:00 PM', 'Wednesday: 9:00 AM – 2:00 PM, 5:00 – 9:00 PM', 'Thursday: 9:00 AM – 2:00 PM, 5:00 – 9:00 PM', 'Friday: 9:00 AM – 2:00 PM, 5:00 – 9:00 PM', 'Saturday: 10:00 AM – 2:00 PM', 'Sunday: Closed']",
    "nivel_precios": 0
  }
]
```

## 🏷️ Descripción de Campos

- **titulo**: Nombre oficial del negocio/museo
- **telefono**: Número de teléfono formateado internacionalmente
- **sitio_web**: URL oficial del sitio web
- **direccion**: Dirección completa con código postal y país
- **rating**: Calificación promedio (1.0 - 5.0)
- **total_ratings**: Número total de reseñas de usuarios
- **place_id**: Identificador único de Google Places (opcional)
- **horarios**: Array de horarios semanales en formato string (opcional)
- **nivel_precios**: Escala de precios 0-4 (0=gratis, 4=muy caro) (opcional)

## 🆘 Solución de Problemas

### Error de API Key
```
❌ No se encontró API Key
```
**Solución**: Configura la API key usando una de las opciones mencionadas arriba.

### No se encuentran resultados
```
❌ No se encontraron negocios para 'término'
```
**Solución**: 
- Prueba términos más específicos
- Incluye la ciudad en la búsqueda
- Verifica que el término esté bien escrito

### Límites de API
```
⚠️ Error: Quota exceeded
```
**Solución**:
- Aumenta los delays entre peticiones
- Reduce el tamaño de lote
- Verifica tu cuota en Google Cloud Console

### Archivo no se guarda en data/
**Solución**: La aplicación crea automáticamente la carpeta `data/` y guarda ahí todos los archivos.

## 🔧 Desarrollo

### Contribuir
1. Fork del repositorio
2. Crea rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Add nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crea Pull Request

### Variables de Entorno de Desarrollo
```bash
# .env (para desarrollo local)
GOOGLE_PLACES_API_KEY=tu_api_key_de_desarrollo
DEBUG=true
MAX_RESULTS_DEFAULT=10
```

## 📄 Licencia

Este proyecto es de código abierto. Usa responsablemente y respeta los términos de uso de la API de Google Places.

## ⚠️ Disclaimer

Este scraper utiliza la API oficial de Google Places. Asegúrate de:
- Cumplir con los términos de uso de Google
- No exceder los límites de tu plan de API
- Usar los datos de manera ética y legal