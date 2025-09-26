import json
import time
import re
import requests
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys  # Currently unused
# from selenium.webdriver.support.ui import WebDriverWait  # Currently unused
# from selenium.webdriver.support import expected_conditions as EC  # Currently unused
from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException  # Currently unused


from items import BmProductItem 


# --- URLs DE LA API ---

# 1. URL Ultra-Filtrada para capturar TODAS las promociones (M+N, 2ª unidad, precio oferta, diferidas)
FILTERED_API_URL_TEMPLATE = "https://www.online.bmsupermercados.es/api/rest/V1.0/catalog/product?page={page}&limit=20&offset=0&orderById=6&filters=filter.offerMxN%3Atrue%3Bfilter.offerSecondUnitDiscount%3Atrue%3Bfilter.offerPrice%3Atrue%3Bfilter.offerDeferred%3Atrue&showRecommendations=false&categories=1690"

# 2. URL Genérica para obtener TODOS los productos de la categoría (Fuente Principal)
GENERIC_API_URL_TEMPLATE = "https://www.online.bmsupermercados.es/api/rest/V1.0/catalog/product?page={page}&limit=20&offset=0&orderById=7&showRecommendations=false&categories=1690"


# --- CONFIGURACIÓN DE PROXY/HEADERS ---

PROXY_URL = "brd.superproxy.io:33335"
PROXY_USER = "brd-customer-hl_60f0fc08-zone-datacenter_proxy1-country-es"
PROXY_PASS = "nfm9jwtumvpo"
PROXY_WITH_AUTH = f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}'
PROXIES = {'http': PROXY_WITH_AUTH, 'https': PROXY_WITH_AUTH}

API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.online.bmsupermercados.es/es/c/bebidas/1690',
    'Accept': 'application/json, text/plain, */*'
}


# --- FUNCIONES AUXILIARES ---

def get_nutritional_data(ean):
    """Intenta obtener los datos nutricionales para un EAN dado."""
    nutritional_url = f"https://cdn-bm.aktiosdigitalservices.com/tol/bm/media/product/nutritional-info/{ean}.json"
    try:
        response = requests.get(nutritional_url, timeout=10)
        response.raise_for_status()
        return response.json() if response.status_code == 200 else None
    except RequestException:
        return None
    except Exception:
        return None

def setup_driver():
    """Configura el driver de Selenium con opciones para modo headless. (Mantenido sin cambios)"""
    chrome_options = Options()
    chrome_options.add_argument('--headless=new') 
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--log-level=3') 
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(45) 
    driver.implicitly_wait(5) 
    return driver

def get_location_cookies(driver):
    """Obtiene las cookies de ubicación de la sesión de Selenium. (Mantenido sin cambios)"""
    initial_url = "https://www.online.bmsupermercados.es/es/c/bebidas/1690"
    
    try:
        driver.get(initial_url)
        print(f"📄 Navegando a: {initial_url} para configurar ubicación.")
        
        time.sleep(10) # Simular tiempo de carga/configuración
        selenium_cookies = driver.get_cookies()
        requests_cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
        
        if not requests_cookies:
            print("No se pudieron obtener cookies completas. Intentando con las disponibles...")

        return requests_cookies

    except Exception as e:
        print(f" Error en la configuracion de ubicacion: {type(e).__name__}: {e}")
        return None


def get_confirmed_promotions(requests_cookies):
    """
    Realiza un barrido de la API filtrada para construir un diccionario 
    {EAN: 'Texto de la promoción'}.
    """
    confirmed_promotions = {}
    
    MAX_PAGES = 10 
    
    print("\n🔍 Fase 1: Extrayendo promociones confirmadas de la API filtrada...")
    
    for page in range(1, MAX_PAGES + 1):
        api_url = FILTERED_API_URL_TEMPLATE.format(page=page)
        
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
                break
            
            for product in products:
                ean = product.get('ean')
                product_offers = product.get('offers')
                promotion_text = None
                
                if isinstance(product_offers, list) and len(product_offers) > 0:
                    promotion_text = product_offers[0].get('minDescription', '').strip()
                    if not promotion_text and len(product_offers) > 1:
                         promotion_text = product_offers[1].get('minDescription', '').strip()

                if ean and promotion_text:
                    confirmed_promotions[ean] = promotion_text

            if not has_more:
                break

        except RequestException as e:
            print(f"   Error en la Fase 1 (Página {page}): {e}. Continuamos...")
            time.sleep(3)
            continue
        except Exception as e:
            print(f"   Error inesperado en la Fase 1 (Página {page}): {e}. Continuamos...")
            continue
        
        time.sleep(1) 
        
    print(f"✅ Fase 1 completada. Se obtuvieron {len(confirmed_promotions)} promociones únicas.")
    return confirmed_promotions


# --- FUNCIÓN PRINCIPAL DE SCRAPING ---

def scrape_bebidas_api_with_cookies(requests_cookies):
    """
    Fase 2: Scrapea la API Genérica y enriquece los datos de promoción con el diccionario 
    de promociones confirmadas.
    """
    confirmed_promotions = get_confirmed_promotions(requests_cookies)
    
    scraped_products = []
    MAX_PAGES = 45 
    
    print("\n🚀 Fase 2: Extrayendo datos de la API Genérica y aplicando promociones...")

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

            for i, product in enumerate(products):
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
                for price_obj in prices:
                    price_id = price_obj.get('id')
                    value_data = price_obj.get('value', {})
                    if price_id == 'PRICE':
                        regular_price = value_data.get('centAmount')
                    elif price_id == 'OFFER_PRICE':
                        offer_price = value_data.get('centAmount')

                if offer_price is not None:
                    bm_item['price'] = offer_price
                    bm_item['offer_price'] = regular_price if regular_price else None
                else:
                    bm_item['price'] = regular_price if regular_price else None
                    bm_item['offer_price'] = None

                unit_price_amount = price_data.get('unitPrice', {}).get('amount')
                bm_item['unit_price'] = unit_price_amount
                
                # *** LÓGICA DE ASIGNACIÓN DE PROMOCIÓN (CORREGIDA) ***
                promotion_text_generic = None
                promotion_text_filtered = confirmed_promotions.get(ean)

                product_offers = product.get('offers')
                if isinstance(product_offers, list) and len(product_offers) > 0:
                    promotion_text_generic = product_offers[0].get('minDescription', '').strip()
                    if not promotion_text_generic and len(product_offers) > 1:
                        promotion_text_generic = product_offers[1].get('minDescription', '').strip()

                if promotion_text_generic and promotion_text_filtered:
                    if promotion_text_generic.upper() == "OFERTA" and promotion_text_filtered.upper() == "OFERTA":
                        promotion_text = "OFERTA"
                    elif promotion_text_generic.upper() == "OFERTA" and promotion_text_filtered.upper() != "OFERTA":
                        promotion_text = promotion_text_filtered
                    elif promotion_text_filtered.upper() == "OFERTA" and promotion_text_generic.upper() != "OFERTA":
                        promotion_text = promotion_text_generic
                    else:
                        promotion_text = promotion_text_filtered
                else:
                    promotion_text = promotion_text_generic or promotion_text_filtered

                if not promotion_text:
                    promotion_text = price_data.get('promotion', {}).get('text')

                bm_item['promotion'] = promotion_text
                # ------------------------------------------------------------------

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

                print(f"Promoción: {bm_item['promotion']}")
            
            if not has_more:
                break

        except RequestException as e:
            print(f"Error en la Fase 2 (Página {page}): {e}. Deteniendo la paginación.")
            break 
        except Exception as e:
            print(f"Error al procesar datos de la página {page}: {e}")
            continue
        
        if page < MAX_PAGES:
            time.sleep(1) 

    print(f"\n📊 Total de productos scrapeados: {len(scraped_products)}")

    output_file = "bm_productos_bebidas.json"
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

        print("\nIniciando proceso de doble consulta para productos y promociones...")
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
