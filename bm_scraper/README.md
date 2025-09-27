# BM Supermercados Scraper

Scraper ético para extraer información de productos de BM Supermercados.

## 🚀 Características

- ✅ **Scraping Ético**: Respeta robots.txt y implementa rate limiting
- ✅ **Arquitectura Modular**: Separación clara de responsabilidades
- ✅ **Configuración Segura**: Credenciales en variables de entorno
- ✅ **Logging Completo**: Sistema de logs para monitoreo
- ✅ **Rate Limiting**: Control de velocidad para no sobrecargar el servidor

## 📁 Estructura del Proyecto

```
bm_scraper/
├── bm_scraper/
│   ├── config/
│   │   ├── proxy_config.py      # Configuración de proxy
│   │   └── environment.py       # Variables de entorno
│   ├── middlewares/
│   │   └── rate_limiting.py     # Middlewares éticos
│   ├── spiders/
│   │   ├── bebidas_spider.py    # Spider principal
│   │   └── items.py             # Definición de items
│   ├── utils/
│   │   ├── cookie_manager.py    # Gestión de cookies
│   │   ├── selenium_driver.py   # Configuración del driver
│   │   └── logging_config.py    # Configuración de logs
│   └── settings.py              # Configuración de Scrapy
├── output/                      # Archivos de salida
├── logs/                        # Archivos de log
└── env.example                  # Ejemplo de variables de entorno
```

## ⚙️ Configuración

### 1. Variables de Entorno

Copia `env.example` a `.env` y configura tus credenciales:

```bash
cp env.example .env
```

Edita `.env`:
```env
PROXY_URL=tu_proxy_url
PROXY_USER=tu_usuario
PROXY_PASS=tu_password
```

### 2. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Uso

### Ejecutar el Scraper

```bash
cd bm_scraper
scrapy crawl bebidas_spider
```

### Ejecutar con Python

```bash
cd bm_scraper
python -m bm_scraper.spiders.bebidas_spider
```

## 📊 Datos Extraídos

El scraper extrae la siguiente información de cada producto:

- **Identificación**: ID, EAN, marca
- **Descripción**: Nombre, categoría, URL
- **Precios**: Precio regular, precio oferta, precio unitario
- **Promociones**: Texto de promociones
- **Información Nutricional**: Fabricante, ingredientes
- **Imágenes**: Enlaces a imágenes del producto

## 🔒 Consideraciones Éticas

- ✅ Respeta el archivo `robots.txt` del sitio
- ✅ Implementa delays entre requests (1-2 segundos)
- ✅ Usa User-Agent identificable
- ✅ Limita concurrencia a 1 request por dominio
- ✅ Implementa retry automático para errores temporales
- ✅ Incluye headers de identificación del scraper

## 📝 Logs

Los logs se guardan en `logs/scraper.log` e incluyen:
- Estadísticas de scraping
- Errores y warnings
- Tiempo de ejecución
- Velocidad de procesamiento

## ⚠️ Importante

Este scraper está diseñado para uso educativo y de investigación. Asegúrate de:

1. Respetar los términos de servicio del sitio web
2. No sobrecargar el servidor con requests excesivos
3. Usar los datos extraídos de manera responsable
4. Cumplir con las leyes de protección de datos aplicables

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Mantén el código ético y responsable
2. Sigue las mejores prácticas de web scraping
3. Actualiza la documentación según sea necesario
