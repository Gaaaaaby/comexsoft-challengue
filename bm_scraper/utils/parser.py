import re
from urllib.parse import urljoin

def extract_category_breadcrumb(response):
    links = response.css('nav.breadcrumb a::text').getall()
    cleaned = [t.strip() for t in links if t.strip() and t.strip().lower() != 'inicio']
    return " > ".join(cleaned) if cleaned else "Bebidas"

def extract_measuring_unit(description: str):
    format_type = "pack"
    total_liters = None
    unit = "L"

    # Match patterns like "12x33 cl", "6x250 ml", "1.5 L"
    match = re.search(r'(\d+)\s*x\s*(\d+(?:\.\d+)?)\s*(ml|cl|l)', description, re.IGNORECASE)
    if match:
        count = int(match.group(1))
        size = float(match.group(2))
        size_unit = match.group(3).lower()
        if size_unit == 'ml':
            total_liters = (count * size) / 1000
        elif size_unit == 'cl':
            total_liters = (count * size) / 100
        elif size_unit == 'l':
            total_liters = count * size
    else:
        liter_match = re.search(r'(\d+(?:\.\d+)?)\s*[lL]', description)
        if liter_match:
            total_liters = float(liter_match.group(1))

    return {
        "format": format_type,
        "value": round(total_liters, 3) if total_liters is not None else None,
        "unit": unit
    }

def clean_price(text):
    if not text:
        return None
    return float(re.sub(r'[^\d,\.]', '', text).replace(',', '.'))