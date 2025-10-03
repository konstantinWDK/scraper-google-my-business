# Carpeta de Datos

Esta carpeta contiene los archivos JSON generados por el scraper de Google My Business.

## 📁 Contenido

- Los archivos se nombran automáticamente basados en la palabra clave de búsqueda
- Formato: `palabra-clave-normalizada.json`
- Todos los espacios se convierten en guiones
- Se eliminan acentos y caracteres especiales

## 📄 Estructura de archivos JSON

Cada archivo contiene un array de objetos con los datos extraídos:

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
    "horarios": "['Monday: Closed', 'Tuesday: 11:00 AM – 2:30 PM, 5:00 – 9:00 PM', ...]",
    "nivel_precios": null
  }
]
```

## 🔒 Privacidad

Los archivos de esta carpeta están incluidos en `.gitignore` para:
- Proteger datos extraídos
- Evitar subir información de terceros al repositorio
- Mantener el repositorio limpio

## 🗑️ Gestión

Puedes gestionar estos archivos desde la interfaz gráfica:
- Ver contenido
- Eliminar archivos
- Exportar a otras ubicaciones