import json
import os
import time
import re
import requests
from requests.exceptions import RequestException

from bm_scraper.bm_scraper.spiders.items import BmProductItem
from bm_scraper.bm_scraper.config.proxy_config import PROXIES, API_HEADERS
from bm_scraper.bm_scraper.utils.selenium_driver import setup_driver
from bm_scraper.bm_scraper.utils.cookie_manager import get_location_cookies

GENERIC_API_URL_TEMPLATE = "https://www.online.bmsupermercados.es/api/rest/V1.0/catalog/product?page={page}&limit=20&offset=0&orderById=7&showRecommendations=false&categories=1690"


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

def scrape_bebidas_api_with_cookies(requests_cookies):
    scraped_products = []
    MAX_PAGES = 45 
    
    print("Extrayendo datos de la API Genérica (Fuente Principal)...")

    for page in range(1, MAX_PAGES + 1):
        print(f"Procesando página {page} de la API Genérica...")
        
        api_url = GENERIC_API_URL_TEMPLATE.format(page=page)

        try:
            response = requests.get(api_url, 
                                     proxies=PROXIES, 
                                     headers=API_HEADERS, 
                                     cookies=requests_cookies,
                                     timeout=15)
            response.raise_for_status() 
            
            data = response.json()
            products = data.get('products', [])
            has_more = data.get('hasMore', False)

            if not products:
                print(f"No se encontraron productos en la API de la página {page}.")
                break
            
            print(f"Se encontraron {len(products)} productos en la pagina {page}.")

            for product in products:
                bm_item = BmProductItem()

                product_data = product.get('productData', {})
                price_data = product.get('priceData', {})
                prices = price_data.get('prices', [])
                ean = product.get('ean')
                
                bm_item['supermarket'] = 'BM Supermercados'
                bm_item['id'] = product.get('id')
                bm_item['ean'] = ean
                bm_item['brand'] = product_data.get('brand', {}).get('name')
                bm_item['description'] = product_data.get('name')
                bm_item['category'] = 'Bebidas'
                bm_item['url'] = product_data.get('url')
                image_url = product_data.get('imageURL')
                bm_item['image_links'] = [image_url] if image_url else []
                bm_item['measuring_unit'] = price_data.get('unitPriceUnitType', None)

                regular_price = None
                offer_price = None
                unit_price_regular = None
                unit_price_offer = None
                
                for price_obj in prices:
                    price_id = price_obj.get('id')
                    value_data = price_obj.get('value', {})
                    
                    price_value = value_data.get('centAmount')
                    unit_amount_value = value_data.get('centUnitAmount')

                    try:
                        final_price = float(price_value) if price_value is not None else None
                        final_unit_amount = float(unit_amount_value) if unit_amount_value is not None else None
                    except (TypeError, ValueError):
                        final_price = None
                        final_unit_amount = None

                    if price_id == 'PRICE':
                        regular_price = final_price
                        unit_price_regular = final_unit_amount
                    elif price_id == 'OFFER_PRICE':
                        offer_price = final_price
                        unit_price_offer = final_unit_amount

                if offer_price is not None:
                    bm_item['price'] = offer_price 
                    bm_item['offer_price'] = regular_price if regular_price != offer_price else None
                    bm_item['unit_price'] = unit_price_offer
                else:
                    bm_item['price'] = regular_price
                    bm_item['offer_price'] = None
                    bm_item['unit_price'] = unit_price_regular

                promotion_text = None
                product_offers = product.get('offers')
                if isinstance(product_offers, list) and len(product_offers) > 0:
                    promotion_text = product_offers[0].get('minDescription', '').strip()
                    if not promotion_text and len(product_offers) > 1:
                        promotion_text = product_offers[1].get('minDescription', '').strip()
                
                if not promotion_text:
                    promotion_text = price_data.get('promotion', {}).get('text')

                bm_item['promotion'] = promotion_text

                bm_item['manufacturer'] = None
                bm_item['raw_ingredients'] = None
                if ean:
                    nutritional_data = get_nutritional_data(ean)
                    if nutritional_data:
                        nutrilabel = nutritional_data.get('nutrilabel', {})
                        product_info = nutrilabel.get('productInformation', {})
                        manufacturer_info = product_info.get('manufacturer', {})
                        if manufacturer_info:
                            name = manufacturer_info.get('name')
                            address = manufacturer_info.get('address')
                            bm_item['manufacturer'] = f"{name} - {address}" if name and address else name
                        
                        ingredients_info = product_info.get('ingredientsInformation', [])
                        if ingredients_info and len(ingredients_info) > 0:
                            ingredients_text = ingredients_info[0].get('ingredientsList', '')
                            if ingredients_text:
                                clean_ingredients = re.sub('<.*?>', '', ingredients_text)
                                bm_item['raw_ingredients'] = clean_ingredients

                scraped_products.append(bm_item)
                
                print("\n" + "="*50)
                print(f"PRODUCTO {product.get('id')} - Página {page}")
                print("="*50)
                print(json.dumps(dict(bm_item), indent=4, ensure_ascii=False))
                print("="*50 + "\n")

            if not has_more:
                break

        except RequestException as e:
            print(f"Error obteniendo datos de los productos(Página {page}): {e}. Deteniendo la paginación.")
            break 
        except Exception as e:
            print(f"Error al procesar datos de la página {page}: {e}")
            continue
        
        if page < MAX_PAGES:
            time.sleep(1) 

    print(f"Total de productos scrapeados: {len(scraped_products)}")

    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "bm_productos_bebidas.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump([dict(product) for product in scraped_products], f, indent=4, ensure_ascii=False)

    print(f"Datos guardados en: {output_file}")
    
    return scraped_products


def scrape_bebidas_master():
    driver = None
    try:
        driver = setup_driver()
        requests_cookies = get_location_cookies(driver)

        if not requests_cookies:
            print("No se pudieron obtener las cookies de ubicación. Intentando scraping sin cookies...")
            requests_cookies = {}

        print("\nIniciando proceso de consulta de productos...")
        return scrape_bebidas_api_with_cookies(requests_cookies)

    except Exception as e:
        print(f"ERROR.: {e}")
        return []

    finally:
        if driver:
            driver.quit()
            print("Navegador cerrado.")

if __name__ == "__main__":
    scrape_bebidas_master()