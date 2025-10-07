# Changelog

Todos los cambios notables del proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

---

## [1.4.0] - 2025-01-XX

### 🔧 Arreglado
- **Compatibilidad con PyInstaller mejorada**
  - Corregido problema de persistencia de API Key en ejecutables compilados
  - Arreglada ubicación de archivos generados en ejecutables
  - Solucionado problema de rutas de archivos en entornos compilados
  - Funciones afectadas: `SecureConfig.__init__`, `setup_logging`, `save_checkpoint`, `clear_checkpoint`, `main`
  - Detección automática de entorno compilado vs desarrollo

- **Codificación CSV mejorada**
  - Corregido problema de caracteres especiales en archivos CSV (ej: "Ã­" → "í")
  - Implementado UTF-8 with BOM (`utf-8-sig`) para compatibilidad con Excel
  - Afecta tanto guardado como exportación de archivos CSV
  - Mantiene UTF-8 estándar para archivos JSON

- **Sistema de extracción de emails completamente renovado**
  - **Búsqueda ampliada en páginas de contacto**: Ahora busca en 14 variaciones diferentes
    - Páginas básicas: `/contact`, `/contacto`, `/contact-us`, `/contactenos`, `/en/contact`
    - Extensiones: `.html`, `.php` para páginas de contacto
    - Páginas adicionales: `/about`, `/sobre-nosotros`, `/info`, `/team`, `/equipo`
  - **Filtros menos restrictivos**: Ya no excluye automáticamente Gmail, Yahoo, Hotmail
    - Solo excluye emails claramente no válidos: `noreply`, `example.com`, `placeholder`
    - Permite capturar emails legítimos de negocios que usan servicios gratuitos
  - **Estrategias de búsqueda mejoradas**:
    - Prioridad 1: Enlaces `mailto:` (más confiables)
    - Prioridad 2: Elementos específicos de contacto (footer, .contact, .email, etc.)
    - Prioridad 3: Meta tags y datos estructurados JSON-LD
    - Prioridad 4: Búsqueda en texto completo
  - **Priorización inteligente**: Prefiere emails corporativos sobre servicios gratuitos
  - **Timeouts optimizados**: 8s para páginas de contacto, 12s para página principal
  - **Logging detallado**: Muestra exactamente dónde encuentra cada email
  - **Patrón de email mejorado**: Acepta TLDs de hasta 10 caracteres

### ⚡ Mejorado
- **Robustez del sistema de archivos**
  - Mejor detección de directorio de trabajo en ejecutables
  - Rutas absolutas consistentes en todas las operaciones de archivo
  - Compatibilidad mejorada entre desarrollo y producción

- **Experiencia de usuario**
  - Logs más informativos durante extracción de emails
  - Mejor feedback sobre el progreso de búsqueda de emails
  - Indicadores visuales claros de éxito/fallo en extracción

### 🔧 Técnico
- Implementada detección de `sys.frozen` para entornos PyInstaller
- Uso de `sys.executable` para determinar directorio base en ejecutables
- Codificación `utf-8-sig` implementada en `save_data_to_csv()` y `export_file()`
- Refactorización completa de `extract_email_from_website()` con nuevas estrategias
- Mejoras en manejo de excepciones para operaciones de archivo

---

## [1.3.0] - 2025-10-07

### 🆕 Añadido
- **Búsquedas múltiples automáticas**
  - Campo de búsqueda multilínea (4 líneas con scrollbar)
  - Permite escribir una palabra clave por línea
  - Soporta separadores: saltos de línea, comas, punto y coma
  - Procesamiento automático secuencial de todas las búsquedas
  - Combinación de resultados en un solo archivo de salida

- **Sistema para superar límite de 60 resultados**
  - Búsquedas automáticas para cada keyword
  - Acumulación inteligente de resultados únicos
  - Hasta 60 resultados por keyword sin límite de keywords
  - Ejemplo: 3 keywords = hasta 180 resultados únicos

- **Sistema inteligente anti-duplicados mejorado**
  - Detecta duplicados entre múltiples búsquedas
  - Mantiene set de place_ids en memoria durante ejecución
  - Evita duplicados con registros existentes en archivo
  - Actualización en tiempo real del set entre búsquedas

- **Logs detallados de progreso de búsquedas**
  - Muestra progreso: "Búsqueda 2/5: 'restaurantes Madrid Norte'"
  - Contador de resultados por búsqueda
  - Indicador de duplicados omitidos por búsqueda
  - Resumen consolidado al finalizar todas las búsquedas

- **Resumen estadístico de búsquedas múltiples**
  ```
  📊 Resumen de búsquedas:
     Total encontrado: 175 negocios
     Nuevos únicos: 163 negocios
  ```

### ⚡ Mejorado
- **Advertencia del límite de API actualizada**
  - Nuevo texto: "⚠️ Límite: 60 resultados por palabra clave | 💡 Usa múltiples líneas para más resultados"
  - Más claro y orientado a la nueva funcionalidad

- **Popup informativo (botón ℹ️) completamente renovado**
  - Sección dedicada a búsquedas múltiples automáticas
  - Ejemplos prácticos de uso multilínea
  - Cálculos de resultados esperados (240, 180 resultados)
  - Instrucciones sobre separadores alternativos (comas)
  - Énfasis en detección automática de duplicados

- **Interfaz de usuario más intuitiva**
  - Label descriptivo: "Palabras clave para buscar: (una por línea)"
  - Altura óptima de 4 líneas con scroll automático
  - Mejor feedback visual durante múltiples búsquedas

### 🔧 Técnico
- Nueva función global: `parse_keywords(text)` - Parsea y limpia múltiples keywords
- Widget cambiado: `tk.Entry` → `scrolledtext.ScrolledText` para campo de búsqueda
- Método modificado: `scrape_data()` ahora acepta lista de keywords
- Método modificado: `start_scraping()` parsea y valida múltiples keywords
- Parámetro modificado: `keyword` → `keywords` (lista) en `scrape_data()`
- Compatibilidad: `scrape_data()` acepta string o lista para retrocompatibilidad
- Lógica de acumulación: Loop sobre keywords con set compartido de place_ids
- Logs contextuales: Mensajes diferenciados para búsqueda única vs múltiple

### 📚 Documentación
- Actualizado encabezado de `scraper_gui.py` con changelog de v1.3.0
- Documentación inline de `parse_keywords()`
- Comentarios explicativos en lógica de búsquedas múltiples

### 💡 Casos de uso
```
Búsqueda simple (1 keyword):
   restaurantes Madrid
   → Hasta 60 resultados

Búsqueda múltiple por ubicación:
   restaurantes Madrid Centro
   restaurantes Madrid Norte
   restaurantes Madrid Sur
   → Hasta 180 resultados únicos

Búsqueda múltiple por tipo:
   restaurantes italianos Madrid
   restaurantes japoneses Madrid
   pizzerías Madrid
   → Hasta 180 resultados únicos

Búsqueda con separadores:
   restaurantes Madrid, cafeterías Barcelona, bares Valencia
   → Hasta 180 resultados únicos
```

---

## [1.2.0] - 2025-10-07

### 🆕 Añadido
- **Sistema de logging en archivo con rotación automática**
  - Archivo `scraper.log` con rotación automática
  - Mantiene últimos 5 archivos de 1MB cada uno
  - Logs con timestamps y niveles (INFO, ERROR, WARNING)
  - Logs limpios sin emojis para facilitar análisis

- **Validación de API Key antes de scraping**
  - Verifica que la API Key sea válida antes de iniciar
  - Detecta errores de permisos, facturación, y configuración
  - Mensajes de error claros y específicos
  - Ahorra tiempo detectando problemas temprano

- **Contador de API calls y costos en tiempo real**
  - Muestra en interfaz: "API Calls: X | Costo estimado: $Y"
  - Calcula costos: $0.017 por llamada (Text Search + Details)
  - Se actualiza en tiempo real durante el scraping
  - Se reinicia correctamente con el botón Reiniciar

- **Sistema de Checkpoint cada 10 registros**
  - Guarda progreso automáticamente en `.scraper_checkpoint.json`
  - Permite reanudar scraping si se interrumpe
  - Se limpia automáticamente al finalizar exitosamente
  - Incluye timestamp y contadores de progreso

- **Scraping inteligente de emails mejorado**
  - Búsqueda prioritaria en páginas `/contact`, `/contacto`, `/contact-us`
  - Extracción específica de emails en `<footer>`
  - Búsqueda en elementos con clases "contact" o "email"
  - Cache de URLs sin email para evitar revisitas
  - Timeout adaptativo (5s contact pages, 10s principal)

- **Manejo de Rate Limiting (HTTP 429)**
  - Detecta automáticamente cuando Google bloquea temporalmente
  - Espera 60 segundos y reintenta automáticamente
  - Logs claros informando al usuario del reintento
  - Implementado en búsqueda y detalles

### 🔧 Arreglado
- **Botón Reiniciar completamente funcional**
  - Ahora espera correctamente a que termine el thread de scraping (timeout 5s)
  - Limpia todos los contadores: API calls, costos, cache de emails
  - Reinicia correctamente la barra de progreso y estado
  - No arrastra datos del scraping anterior

- **Robustez del guardado de API Key**
  - Usa rutas absolutas basadas en directorio del script
  - Funciona correctamente al mover la aplicación de directorio
  - Mejor manejo de errores de permisos de archivo

### ⚡ Mejorado
- **Gestión de errores específicos**
  - HTTP 403: Detecta falta de permisos o API deshabilitada
  - HTTP 404: Informa Place ID no encontrado
  - HTTP 429: Manejo automático con reintentos
  - Logs informativos para cada tipo de error
  - No satura el log con errores repetitivos

- **Extracción de emails más efectiva**
  - Busca primero en páginas dedicadas de contacto
  - Prioriza `mailto:` links (más confiables)
  - Filtra emails genéricos (noreply, gmail, etc.)
  - Búsqueda en orden: contact pages → footer → elementos contact → todo el HTML

### 📚 Documentación
- Actualizado encabezado de `scraper_gui.py` con changelog completo de v1.2.0
- Documentación inline de nuevas funciones y mejoras

### 🔧 Técnico
- Añadida dependencia: `logging.handlers.RotatingFileHandler`
- Nueva función global: `setup_logging()`
- Nuevos métodos de clase:
  - `validate_api_key()`: Validación de API Key con petición de prueba
  - `increment_api_calls()`: Contador de llamadas API y costos
  - `save_checkpoint()`: Guardado de progreso
  - `clear_checkpoint()`: Limpieza de checkpoint
- Mejoras en métodos existentes:
  - `extract_email_from_website()`: Búsqueda inteligente con cache
  - `search_businesses()`: Manejo de Rate Limiting
  - `get_business_details()`: Manejo de Rate Limiting y errores específicos
  - `refresh_scraper()`: Tracking de threads y limpieza completa
  - `log()`: Logging dual (GUI + archivo)
- Nuevas variables de instancia:
  - `self.scraping_thread`: Referencia al thread activo
  - `self.api_calls_count`: Contador de llamadas API
  - `self.estimated_cost`: Costo estimado acumulado
  - `self.visited_websites_no_email`: Cache de URLs sin email
  - `self.logger`: Instancia del logger de archivo

---

## [1.1.0] - 2025-10-06

### 🆕 Añadido
- **Cifrado seguro de API Key con AES-256**
  - La API Key ahora se guarda cifrada en `.gmb_config.enc`
  - Utiliza criptografía basada en identificador único de la máquina
  - Compatible con Windows y Linux

- **Persistencia automática de configuración**
  - La API Key se carga automáticamente al iniciar la aplicación
  - No es necesario volver a introducir la clave en cada sesión

- **Pestaña de Configuración mejorada**
  - Interfaz visual para gestionar la API Key
  - Botón para mostrar/ocultar la clave
  - Indicador de estado (configurada/no configurada)
  - Opción para importar desde archivo .txt

- **Compatibilidad retroactiva**
  - Detecta archivos `google_api_key.txt` legacy
  - Sugiere migración al sistema cifrado
  - Mantiene funcionamiento con archivos antiguos

### 🔒 Seguridad
- Implementado cifrado AES-256 para almacenamiento de API Key
- Derivación de clave usando PBKDF2 con 100,000 iteraciones
- Protección basada en características únicas de la máquina

### 📚 Documentación
- Actualizado README.md con instrucciones de v1.1.0
- Creado INSTRUCCIONES_COMPILACION_WINDOWS.md
- Añadido este CHANGELOG

### 🔧 Técnico
- Añadida dependencia: `cryptography>=41.0.0`
- Nueva clase `SecureConfig` para gestión de configuración cifrada
- Métodos actualizados: `save_api_key()`, `load_api_key()`, `clear_api_key()`

---

## [1.0.0] - 2025-05-11

### 🎉 Versión Inicial

#### Características principales
- **Interfaz gráfica con Tkinter**
  - Pestaña de Scraper con configuración completa
  - Pestaña de Gestión de Archivos
  - Sistema de pestañas organizado

- **Scraping de Google My Business**
  - Búsqueda mediante Google Places API
  - Extracción de múltiples campos configurables
  - Soporte para múltiples resultados y paginación

- **Gestión de datos**
  - Exportación a JSON y CSV
  - Detección automática de duplicados por place_id
  - Scraping incremental
  - Vista previa de archivos

- **Campos extraíbles**
  - Título/Nombre del negocio
  - Teléfono
  - Sitio web
  - Dirección
  - Rating
  - Total de reseñas
  - Place ID
  - Horarios de apertura
  - Nivel de precios
  - Email (experimental, desde sitio web)

- **Control de scraping**
  - Delays configurables entre peticiones
  - Sistema de lotes para evitar límites
  - Límite máximo de resultados
  - Botones Iniciar/Detener/Reiniciar

- **Seguridad básica**
  - Soporte para variables de entorno
  - Archivo de configuración local
  - .gitignore para proteger credenciales

- **Normalización de nombres**
  - Nombres de archivo automáticos
  - Conversión a minúsculas
  - Eliminación de caracteres especiales
  - Reemplazo de espacios por guiones

---

## Roadmap Futuro

### [1.4.0] - Planificado
- [ ] Soporte para múltiples cuentas de API
- [ ] Programación de scraping automático
- [ ] Exportación a Excel (.xlsx)
- [ ] Filtros avanzados de búsqueda
- [ ] Dashboard con estadísticas

### [1.5.0] - Planificado
- [ ] Base de datos SQLite integrada
- [ ] Búsqueda en archivos guardados
- [ ] Comparación entre scraping diferentes
- [ ] Gráficas de análisis de datos

---

## Tipos de cambios
- `Añadido` para funcionalidades nuevas.
- `Cambiado` para cambios en funcionalidades existentes.
- `Obsoleto` para funcionalidades que se eliminarán en próximas versiones.
- `Eliminado` para funcionalidades eliminadas.
- `Arreglado` para corrección de errores.
- `Seguridad` en caso de vulnerabilidades.

---

**Mantenido por:** Konstantin Koshkarev
**Web:** [webdesignerk.com](https://webdesignerk.com)
