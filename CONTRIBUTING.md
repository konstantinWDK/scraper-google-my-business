# 🤝 Guía de Contribución

¡Gracias por tu interés en contribuir a Google My Business Scraper!

## 🌟 Formas de Contribuir

- 🐛 Reportar bugs
- 💡 Sugerir nuevas funcionalidades
- 📝 Mejorar documentación
- 🔧 Enviar código (bug fixes, features)
- 🌍 Traducir la aplicación
- ⭐ Dar estrella al proyecto

---

## 🚀 Comenzar a Desarrollar

### 1. Fork y Clone

```bash
# Fork el repositorio en GitHub, luego:
git clone https://github.com/TU_USUARIO/google-my-business-scraper.git
cd google-my-business-scraper
```

### 2. Configurar Entorno

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
cd src
pip install -r requirements.txt
```

### 3. Configurar API Key de Prueba

```bash
# Opción 1: Variable de entorno (recomendado)
export GOOGLE_PLACES_API_KEY="tu_api_key_de_prueba"

# Opción 2: Archivo local (NO commitear)
echo "tu_api_key_de_prueba" > google_api_key.txt
```

### 4. Ejecutar la Aplicación

```bash
python scraper_gui.py
```

---

## 📋 Proceso de Contribución

### 1. Crear una Issue

Antes de empezar a codear, **abre una issue** describiendo:
- El problema o feature que quieres resolver
- Por qué es importante
- Cómo planeas implementarlo (opcional)

Esto evita trabajo duplicado y alinea expectativas.

### 2. Crear una Rama

```bash
git checkout -b feature/nombre-descriptivo
# o
git checkout -b fix/nombre-del-bug
```

**Convenciones de nombres:**
- `feature/` - Nueva funcionalidad
- `fix/` - Corrección de bugs
- `docs/` - Documentación
- `refactor/` - Refactorización de código
- `test/` - Tests

### 3. Hacer Cambios

- ✅ Escribe código limpio y comentado
- ✅ Sigue el estilo del proyecto (PEP 8 para Python)
- ✅ Prueba tus cambios manualmente
- ✅ Actualiza la documentación si es necesario
- ✅ NO incluyas tu API Key en commits

### 4. Commit

Usa mensajes descriptivos en español:

```bash
git add .
git commit -m "feat: Agregar exportación a Excel

- Implementada exportación a formato XLSX
- Añadida librería openpyxl a requirements
- Actualizada interfaz con botón de exportación
- Tests manuales OK"
```

**Formato de commits:**
- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bug
- `docs:` - Documentación
- `refactor:` - Refactorización
- `test:` - Tests
- `chore:` - Tareas de mantenimiento

### 5. Push y Pull Request

```bash
git push origin feature/nombre-descriptivo
```

Luego en GitHub:
1. Crea un Pull Request
2. Describe qué cambios hiciste
3. Referencia la issue relacionada (#número)
4. Agrega capturas de pantalla si aplica

---

## ✅ Checklist antes de Pull Request

- [ ] El código funciona sin errores
- [ ] He probado la funcionalidad manualmente
- [ ] La documentación está actualizada
- [ ] No he incluido API Keys o datos sensibles
- [ ] Los commits tienen mensajes descriptivos
- [ ] He actualizado CHANGELOG.md si corresponde
- [ ] El código sigue el estilo del proyecto

---

## 🐛 Reportar Bugs

Usa la plantilla de issues en GitHub e incluye:

1. **Descripción**: ¿Qué está pasando?
2. **Pasos para reproducir**: ¿Cómo recrear el bug?
3. **Comportamiento esperado**: ¿Qué debería pasar?
4. **Screenshots**: Si aplica
5. **Entorno**:
   - Sistema operativo y versión
   - Versión de Python
   - Versión de la aplicación

---

## 💡 Sugerir Funcionalidades

Abre una issue con la etiqueta `enhancement` e incluye:

1. **Problema**: ¿Qué problema resuelve?
2. **Solución propuesta**: ¿Cómo lo implementarías?
3. **Alternativas**: ¿Consideraste otras opciones?
4. **Casos de uso**: ¿Quién se beneficiaría?

---

## 🎨 Estilo de Código

### Python (PEP 8)

```python
# ✅ Bueno
def get_business_details(place_id: str) -> Optional[BusinessData]:
    """
    Obtiene detalles de un negocio desde la API.

    Args:
        place_id: ID único del lugar en Google

    Returns:
        Objeto BusinessData o None si hay error
    """
    pass

# ❌ Malo
def getBusiness(id):
    pass
```

### Nombres descriptivos

```python
# ✅ Bueno
total_businesses_found = 42
is_scraping_active = True

# ❌ Malo
x = 42
flag = True
```

### Comentarios útiles

```python
# ✅ Bueno
# Delay para evitar rate limiting de la API (3-5 seg)
time.sleep(random.uniform(3.0, 5.0))

# ❌ Malo
# Esperar
time.sleep(4)
```

---

## 🧪 Testing

Por ahora el testing es manual. Para el futuro planeamos:
- [ ] Tests unitarios con pytest
- [ ] Tests de integración
- [ ] CI/CD con GitHub Actions

**Mientras tanto:**
- Prueba todos los casos de uso
- Prueba en diferentes sistemas operativos
- Verifica que no rompiste funcionalidad existente

---

## 📚 Estructura del Proyecto

```
google-my-business-scraper/
├── src/                    # Código fuente principal
│   ├── scraper_gui.py      # Aplicación principal
│   └── requirements.txt    # Dependencias
├── build-scripts/          # Scripts de compilación
├── docs/                   # Documentación
├── .github/               # GitHub Actions (futuro)
└── README.md              # Documentación principal
```

---

## 🤔 ¿Necesitas Ayuda?

- 📧 Abre una issue con la etiqueta `question`
- 💬 Comenta en issues existentes
- 🌐 Visita [webdesignerk.com](https://webdesignerk.com)

---

## 📜 Código de Conducta

- **Sé respetuoso** con otros contribuidores
- **Acepta críticas constructivas** de code reviews
- **Ayuda a nuevos contribuidores**
- **Reporta comportamiento inapropiado**

---

## 🎉 Reconocimientos

Todos los contribuidores serán reconocidos en:
- README.md
- CHANGELOG.md
- Release notes

---

**¡Gracias por hacer este proyecto mejor! 🚀**

---

**Mantenido por:** Konstantin Koshkarev
**Web:** [webdesignerk.com](https://webdesignerk.com)
