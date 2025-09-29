
import json
import os
import sys
import time
import re
import requests
import logging
from requests.exceptions import RequestException

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from bm_scraper.spiders.items import BmProductItem
from bm_scraper.config.proxy_config import PROXIES, API_HEADERS
from bm_scraper.utils.product_parsers import (
    parse_measuring_unit, 
    get_hierarchical_category,
    get_nutritional_data, 
    get_value_or_not_found
)
from bm_scraper.utils.fallback_data import generate_fallback_data
from bm_scraper.config.config import (
    BEVERAGES_API_URL,
    MXN_PROMO_API_URL,
    OUTPUT_DIR,
    OUTPUT_FILE,
    SECOND_UNIT_PROMO_API_URL,
    OFFER_PRICE_PROMO_API_URL,
    OFFER_DEFERRED_PROMO_API_URL,
    MAX_PAGES,
    OFFER_PRICE_MAX_PAGES,
    MAX_EMPTY_PAGES,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    RETRY_DELAY,
    PAGE_DELAY
)
from bm_scraper.utils.logging_config import configure_logging


configure_logging()

def fetch_promotion_products(api_url, promo_type):
    """
    Fetch promotional products from a specified BM Supermercados API URL.

    Iterates through pages of the API response (up to a maximum, depending on promo_type),
    extracts promotional data for products, and maps EANs to promotion details. Handles
    pagination, retries for failed requests, and stops early if consecutive empty pages are
    encountered.

    Args:
        api_url: The API URL to fetch promotions from, with optional `{page}` and `{offset}`
            placeholders for pagination (string).
        promo_type: The type of promotion, e.g., 'MxN', 'SecondUnitDiscount', 'OfferPrice',
            or 'OfferDeferred' (string).

    Returns:
        A dictionary mapping product EANs to promotion details, where each entry contains
        'minDescription', 'shortDescription', and 'type'.
    """
    promo_map = {}
    seen_eans = set()
    max_pages = 1 if promo_type != "OfferPrice" else OFFER_PRICE_MAX_PAGES
    consecutive_empty_pages = 0

    logging.info(f"Fetching {promo_type} promotions from {api_url}...")

    for page_number in range(1, max_pages + 1):
        offset = (page_number - 1) * 20
        current_url = api_url.format(page=page_number, offset=offset) if "{page}" in api_url else api_url

        retries = 0
        while retries < MAX_RETRIES:
            try:
                response = requests.get(current_url, proxies=PROXIES, headers=API_HEADERS, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                data = response.json()
                
                products = data.get('products', [])
                total_count = data.get('totalCount', 0)
                has_more = data.get('hasMore', False)
                
                new_count = 0
                for product in products:
                    ean = product.get('ean')
                    if ean in seen_eans:
                        continue
                    
                    offers = product.get('offers', [])
                    if offers:
                        offer = offers[0]
                        min_desc = offer.get('minDescription', '').strip()
                        short_desc = offer.get('shortDescription', '').strip()
                        if min_desc or short_desc:
                            promo_map[ean] = {
                                'minDescription': min_desc,
                                'shortDescription': short_desc,
                                'type': promo_type
                            }
                            seen_eans.add(ean)
                            new_count += 1

                if new_count == 0:
                    consecutive_empty_pages += 1
                    if consecutive_empty_pages >= MAX_EMPTY_PAGES:
                        break
                else:
                    consecutive_empty_pages = 0

                if not has_more or promo_type != "OfferPrice":
                    break

                break  

            except RequestException as e:
                retries += 1
                logging.error(f"Error fetching {promo_type} page {page_number}, try {retries}/{MAX_RETRIES}: {e}")
                if retries >= MAX_RETRIES:
                    break
                time.sleep(RETRY_DELAY)
            except Exception as e:
                logging.error(f"Error processing {promo_type} page {page_number}: {e}")
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= MAX_EMPTY_PAGES:
                    logging.info(f"Stopping: {consecutive_empty_pages} consecutive empty pages {promo_type}")
                    break
                break  

        if retries >= MAX_RETRIES or consecutive_empty_pages >= MAX_EMPTY_PAGES:
            break  

        time.sleep(PAGE_DELAY)
    
    return promo_map

def process_product_data_from_api(product, mxn_promo_map, second_unit_promo_map, offer_price_promo_map, offer_deferred_promo_map):
    """
    Process a single product's data from the BM Supermercados API response into a structured item.

    Extracts product details (EAN, brand, description, etc.), pricing information, and promotional
    data. Prioritizes promotions from provided maps (MxN > SecondUnit > OfferPrice > OfferDeferred)
    and falls back to API offers if no map entry is found. Also retrieves nutritional data and
    manufacturer information if available.

    Args:
        product: The raw product data from the API, containing 'productData', 'priceData',
            and 'offers' (dictionary).
        mxn_promo_map: Map of EANs to MxN promotion details (dictionary).
        second_unit_promo_map: Map of EANs to SecondUnitDiscount promotion details (dictionary).
        offer_price_promo_map: Map of EANs to OfferPrice promotion details (dictionary).
        offer_deferred_promo_map: Map of EANs to OfferDeferred promotion details (dictionary).

    Returns:
        A BmProductItem object with product details, or None if processing fails.
    """
    try:
        bm_item = BmProductItem()

        product_data = product.get('productData', {})
        price_data = product.get('priceData', {})
        prices = price_data.get('prices', [])
        ean = product.get('ean')
        
        bm_item['supermarket'] = 'BM in 20012'
        bm_item['id'] = product.get('id')
        bm_item['ean'] = ean
        bm_item['brand'] = product_data.get('brand', {}).get('name')
        bm_item['description'] = product_data.get('name')
        bm_item['category'] = get_hierarchical_category(product.get('categories', []))
        bm_item['url'] = product_data.get('url')
        image_url = product_data.get('imageURL')
        bm_item['image_links'] = [image_url] if image_url else ['No encontrado']
        
        description = product_data.get('name', '')
        bm_item['measuring_unit'] = get_value_or_not_found(parse_measuring_unit(description))

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

        updated_promo = 'No encontrado'
        if ean in mxn_promo_map:
            promo_data = mxn_promo_map[ean]
            updated_promo = f"{promo_data['type']}: {promo_data['minDescription']} - {promo_data['shortDescription']}"
        elif ean in second_unit_promo_map:
            promo_data = second_unit_promo_map[ean]
            updated_promo = f"{promo_data['type']}: {promo_data['minDescription']} - {promo_data['shortDescription']}"
        elif ean in offer_price_promo_map:
            promo_data = offer_price_promo_map[ean]
            updated_promo = f"{promo_data['type']}: {promo_data['minDescription']} - {promo_data['shortDescription']}"
        elif ean in offer_deferred_promo_map:
            promo_data = offer_deferred_promo_map[ean]
            updated_promo = f"{promo_data['type']}: {promo_data['minDescription']} - {promo_data['shortDescription']}"
        else:
            offers = product.get('offers', [])
            if offers:
                offer = offers[0]
                min_desc = offer.get('minDescription', '').strip()
                short_desc = offer.get('shortDescription', '').strip()
                promo_type = 'OfferDeferred' if 'Deferred' in short_desc else \
                            'OfferPrice' if offer.get('promotionType') == 1 else \
                            'MxN' if '2X1' in min_desc else \
                            'SecondUnitDiscount' if '2ª al' in min_desc else 'Unknown'
                if min_desc or short_desc:
                    updated_promo = f"{promo_type}: {min_desc} - {short_desc}"

                    offer_amount = offer.get('amount')
                    if offer_amount is not None and offer_price is None:
                        offer_price = float(offer_amount)
                        regular_price = regular_price if regular_price is not None else offer_price

        bm_item['promotion'] = updated_promo

        if offer_price is not None:
            bm_item['price'] = offer_price
            bm_item['offer_price'] = regular_price if regular_price != offer_price else None
            bm_item['unit_price'] = unit_price_offer if unit_price_offer is not None else unit_price_regular
        else:
            bm_item['price'] = regular_price
            bm_item['offer_price'] = 'No encontrado'
            bm_item['unit_price'] = get_value_or_not_found(unit_price_regular)

        bm_item['manufacturer'] = 'No encontrado'
        bm_item['raw_ingredients'] = 'No encontrado'
        if ean:
            nutritional_data = get_nutritional_data(ean)
            if nutritional_data:
                nutrilabel = nutritional_data.get('nutrilabel', {})
                product_info = nutrilabel.get('productInformation', {})
                manufacturer_info = product_info.get('manufacturer', {})
                if manufacturer_info:
                    manufacturer_name = manufacturer_info.get('name')
                    manufacturer_address = manufacturer_info.get('address')
                    bm_item['manufacturer'] = f"{manufacturer_name} - {manufacturer_address}" if manufacturer_name and manufacturer_address else manufacturer_name
                
                ingredients_info = product_info.get('ingredientsInformation', [])
                if ingredients_info and len(ingredients_info) > 0:
                    ingredients_text = ingredients_info[0].get('ingredientsList', '')
                    if ingredients_text:
                        clean_ingredients = re.sub('<.*?>', '', ingredients_text)
                        bm_item['raw_ingredients'] = clean_ingredients

        return bm_item
        
    except Exception as e:
        logging.error(f"Error processing product data for EAN {ean}: {e}")
        return None

def scrape_beverages_api_only():
    """
    Scrape beverage product data from the BM Supermercados API.

    Fetches product data from the main beverages API, processes each product, and applies
    promotional data from separate promotion APIs. Handles pagination up to a maximum number
    of pages, deduplicates products using product IDs, and stops early if consecutive empty
    pages are encountered. Returns a list of processed product items.

    Returns:
        A list of BmProductItem objects containing processed product data.
    """
    scraped_products = []
    seen_product_ids = set()
    consecutive_empty_pages = 0
    
    mxn_promo_map = fetch_promotion_products(MXN_PROMO_API_URL, "MxN")
    second_unit_promo_map = fetch_promotion_products(SECOND_UNIT_PROMO_API_URL, "SecondUnitDiscount")
    offer_price_promo_map = fetch_promotion_products(OFFER_PRICE_PROMO_API_URL, "OfferPrice")
    offer_deferred_promo_map = fetch_promotion_products(OFFER_DEFERRED_PROMO_API_URL, "OfferDeferred")

    for page_number in range(1, MAX_PAGES + 1):
        logging.info(f"Processing page {page_number} of {MAX_PAGES}...")
        
        offset = (page_number - 1) * 20
        api_url = BEVERAGES_API_URL.format(page=page_number, offset=offset)

        try:
            response = requests.get(api_url, 
                                 proxies=PROXIES, 
                                 headers=API_HEADERS, 
                                 timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            products = data.get('products', [])
            has_more = data.get('hasMore', False)
            total_count = data.get('totalCount', 0)
            
            if not products:
                logging.info(f"No products found in API page {page_number}.")
                break
            
            logging.info(f"Found {len(products)} products on page {page_number}.")

            new_products_count = 0
            for product in products:
                product_id = product.get('id')
                
                if product_id in seen_product_ids:
                    continue
                
                bm_item = process_product_data_from_api(product, mxn_promo_map, second_unit_promo_map, offer_price_promo_map, offer_deferred_promo_map)
                if bm_item:
                    scraped_products.append(bm_item)
                    seen_product_ids.add(product_id)
                    new_products_count += 1
                    
                    logging.info("\n" + "="*50)
                    logging.info(f"PRODUCT {product.get('id')} - Page {page_number}")
                    logging.info("="*50)
                    logging.info(json.dumps(dict(bm_item), indent=4, ensure_ascii=False))
                    logging.info("="*50 + "\n")
                else:
                    logging.error(f"Failed to process product {product_id}")

            if new_products_count == 0:
                consecutive_empty_pages += 1
                logging.info(f"No new products found on page {page_number} (consecutive empty pages: {consecutive_empty_pages})")
                
                if consecutive_empty_pages >= MAX_EMPTY_PAGES:
                    logging.info(f"Stopping: {consecutive_empty_pages} consecutive pages with no new products")
                    break
            else:
                consecutive_empty_pages = 0
                logging.info(f"Found {new_products_count} new products on page {page_number}")

            if not has_more:
                logging.info(f"API indicates no more pages available")
                break

        except RequestException as e:
            logging.error(f"Error getting product data (Page {page_number}): {e}")
            break 
        except Exception as e:
            logging.error(f"Error processing data from page {page_number}: {e}")
            continue
        
        if page_number < MAX_PAGES:
            time.sleep(PAGE_DELAY)

    logging.info(f"Scraping completed. Total scraped products: {len(scraped_products)}")
    
    return scraped_products

def scrape_beverages_master():
    try:
        logging.info("Starting product query process with API only...")
        
        scraped_products = scrape_beverages_api_only()
        
        if not scraped_products or len(scraped_products) == 0:
            logging.info("No products scraped. Using fallback data...")
            scraped_products = generate_fallback_data()
        
        if scraped_products:
            output_dir = r"C:\Users\richa\Downloads\comexsoft-challengue\bm_scraper\output"
            output_file = os.path.join(output_dir, "bm_productos_bebidas.json")
            
            try:
                os.makedirs(output_dir, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump([dict(product) for product in scraped_products], f, indent=4, ensure_ascii=False)
                logging.info(f"Data saved to: {output_file}")
            except OSError as e:
                logging.error(f"Error saving data to {output_file}: {e}")
                raise
        
        return scraped_products

    except Exception as e:
        logging.error(f"Using fallback data due to error: {e}")
        return generate_fallback_data()

if __name__ == "__main__":
    scrape_beverages_master()