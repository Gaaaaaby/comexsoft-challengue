
# BM Supermercados Beverage Scraper

## Overview

This Python script scrapes beverage product data from the BM Supermercados API, extracting details such as product identification, pricing, promotions, nutritional information, and images. The scraper is designed with a modular architecture, secure configuration via environment variables, and rate limiting to prevent overloading the server. Output is saved as a JSON file in the `output` directory.

## Features

- Modular architecture with clear separation of responsibilities.
- Secure configuration using environment variables for sensitive data like proxy credentials.
- Rate limiting to ensure ethical scraping and avoid server overload.
- Error handling with retries and fallback data for robustness.
- Deduplication of products using EANs and product IDs.
- Pagination support to fetch all available products efficiently.

## Project Structure

```
bm_scraper/
├── bm_scraper/
│   ├── config/
│   │   ├── proxy_config.py      # Proxy configuration
│   │   └── environment.py       # Environment variable loading
│   ├── middlewares/
│   │   └── rate_limiting.py     # Rate limiting middleware
│   ├── spiders/
│   │   ├── bebidas_scraper_simple.py  # Main scraper script
│   │   └── items.py             # Product item definitions
│   ├── utils/
        ├── fallback_data.py     # Fallback if there's a failure scraping
        ├── product_parsers.py   # Adjusting data from products 

│   └── settings.py              # Scrapy settings
├── output/                      # Directory for JSON output files
├── logs/                        # Directory for log files
├── env.example                  # Example environment variable file
└── requirements.txt             # Project dependencies
```

## Prerequisites

- Python 3.8 or higher
- Dependencies listed in `requirements.txt` (e.g., `requests`)
- Optional: Proxy service for API requests (configured in `.env`)

## Setup

### 1. Clone the Repository

```bash
git clone <repository_url>
cd bm_scraper
```

### 2. Install Dependencies

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and update it with your proxy credentials (if applicable):

```bash
cp env.example .env
```

Edit `.env` with a text editor:

```env
PROXY_URL=your_proxy_url
PROXY_USER=your_username
PROXY_PASS=your_password
```

If not using a proxy, leave these fields empty or configure `bm_scraper/config/proxy_config.py` to bypass proxy usage.

### 4. Verify Module Accessibility

Ensure the `bm_scraper` module is accessible. The script uses a dynamic import path (`sys.path.append`). For production, consider restructuring as a proper Python package.

## Usage

### Option 1: Run as a Python Script

Execute the main scraper script directly:

```bash
cd bm_scraper
python -m bm_scraper.spiders.bebidas_scraper_simple
```

### Output

The scraper saves results to `output/bm_productos_bebidas.json` in the following format:

```json
[
    {
        "supermarket": "BM Supermercados",
        "id": "12345",
        "ean": "8412598007767",
        "brand": "Estrella Galicia",
        "description": "Cerveza 0,0 Tostada 33 cl",
        "category": "Bebidas/Cerveza",
        "url": "https://www.online.bmsupermercados.es/es/estrella-galicia-0-0-tostada/12345",
        "image_links": ["https://www.online.bmsupermercados.es/image.jpg"],
        "measuring_unit": {"format": "unit", "value": 0.33, "unit": "L"},
        "price": 0.75,
        "offer_price": null,
        "unit_price": 2.27,
        "promotion": "MxN: 4 X 3€ - 4X3,00€",
        "manufacturer": "Hijeros de Rivera S.A., A Coruña, España",
        "raw_ingredients": "Agua, malta de cebada, lúpulo"
    },
    ...
]
```

## Extracted Data

For each product, the scraper collects:

- Identification: Product ID, EAN, brand
- Description: Product name, category, URL
- Pricing: Regular price, offer price, unit price (per liter)
- Promotions: Promotion type and description (e.g., "MxN: 4 X 3€")
- Nutritional Information: Manufacturer details, raw ingredients
- Images: URLs to product images

## Error Handling

- API Request Failures: Retries up to 3 times with a 2-second delay.
- Empty Pages: Stops after 3 consecutive empty pages to avoid unnecessary requests.
- Data Processing Errors: Skips problematic products and logs errors to the console.
- Fallback Data: Uses `generate_fallback_data()` if no products are scraped, ensuring output is produced.

## Troubleshooting

If the scraper fails to retrieve data:

- Check the `.env` file for correct proxy credentials.
- Verify the API URLs in `bebidas_scraper_simple.py` are correct and the server is accessible.
- Ensure the `bm_scraper` module is in the correct path or adjust the import logic.
