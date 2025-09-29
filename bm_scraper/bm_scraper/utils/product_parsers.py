import re

import requests
from requests.exceptions import RequestException




def get_value_or_not_found(value):
            if value is None:
                return "No encontrado"
            if isinstance(value, (list,str,dict)) and not value:
                return "No encontrado"
            return value 
            
def get_nutritional_data(ean):
    
    nutritional_url = f"https://cdn-bm.aktiosdigitalservices.com/tol/bm/media/product/nutritional-info/{ean}.json"
    try:
        response = requests.get(nutritional_url, timeout=10)
        response.raise_for_status()
        return response.json() if response.status_code == 200 else None
    except RequestException:
        return None
    except Exception:
        return None

def parse_measuring_unit(description):
    
    if not description:
        return {"format": "unit", "value": 1.0, "unit": "L"}
    
    desc_lower = description.lower()
    
    # Patterns to detect decimals and commas
    pack_match = re.search(r'(\d+)x(\d+[,.]?\d*)\s*([cm]?l)\b', desc_lower)  # 12x33cl, 6x1,5L
    unit_match = re.search(r'(\d+[,.]?\d*)\s*([cm]?l)\b', desc_lower)        # 33cl, 1,5L, 2.5L
    
    if pack_match:
        # Pack format: 12x33cl → 3.96L
        units_count = int(pack_match.group(1))
        volume_str = pack_match.group(2).replace(',', '.') 
        volume = float(volume_str)
        unit = pack_match.group(3).upper()
        
        liters_per_unit = volume * (0.01 if unit == 'CL' else 0.001 if unit == 'ML' else 1.0)
        total_liters = liters_per_unit * units_count
        
        return {
            "format": "pack",
            "value": round(total_liters, 2),
            "unit": "L"
        }
    
    elif unit_match:
        # Unit format
        volume_str = unit_match.group(1).replace(',', '.') 
        volume = float(volume_str)
        unit = unit_match.group(2).upper()
        
        liters = volume * (0.01 if unit == 'CL' else 0.001 if unit == 'ML' else 1.0)
        
        return {
            "format": "unit", 
            "value": round(liters, 2),
            "unit": "L"
        }
    
    return {
        "format": "unit",
        "value": 1.0,
        "unit": "L"
    }


def get_hierarchical_category(categories):
    if not categories:
        return "Bebidas"
    
    relevant_categories = [cat for cat in categories if cat.get('type') == 1]
    
    if not relevant_categories:
        return "Bebidas"
    
    relevant_categories.sort(key=lambda x: x.get('id', 0))
    
    category_names = [cat['name'] for cat in relevant_categories if cat.get('name')]
    
    return " > ".join(category_names) if category_names else "Bebidas"
