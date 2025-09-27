# BM Supermercados Scraper

Scraper para extraer información de productos de BM Supermercados.

## Características

- **Arquitectura Modular**: Separación clara de responsabilidades
- **Configuración Segura**: Credenciales en variables de entorno
- **Rate Limiting**: Control de velocidad para no sobrecargar el servidor

## Estructura del Proyecto

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

## Configuración

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

## Uso

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

## Datos Extraídos

El scraper extrae la siguiente información de cada producto:

- **Identificación**: ID, EAN, marca
- **Descripción**: Nombre, categoría, URL
- **Precios**: Precio regular, precio oferta, precio unitario
- **Promociones**: Texto de promociones
- **Información Nutricional**: Fabricante, ingredientes
- **Imágenes**: Enlaces a imágenes del producto
