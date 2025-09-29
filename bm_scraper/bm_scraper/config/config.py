"""
Configuration constants for the BM Supermercados Beverage Scraper.

"""

# API URLs for fetching product and promotion data
BEVERAGES_API_URL = "https://www.online.bmsupermercados.es/api/rest/V1.0/catalog/product?page={page}&limit=20&offset={offset}&orderById=1&showRecommendations=false&categories=1690"
MXN_PROMO_API_URL = "https://www.online.bmsupermercados.es/api/rest/V1.0/catalog/product?page=1&limit=20&offset=0&orderById=1&filters=filter.offerMxN%3Atrue&showRecommendations=false&categories=1690"
SECOND_UNIT_PROMO_API_URL = "https://www.online.bmsupermercados.es/api/rest/V1.0/catalog/product?page=1&limit=20&offset=0&orderById=1&filters=filter.offerSecondUnitDiscount%3Atrue&showRecommendations=false&categories=1690"
OFFER_PRICE_PROMO_API_URL = "https://www.online.bmsupermercados.es/api/rest/V1.0/catalog/product?page={page}&limit=20&offset={offset}&orderById=1&filters=filter.offerPrice%3Atrue&showRecommendations=false&categories=1690"
OFFER_DEFERRED_PROMO_API_URL = "https://www.online.bmsupermercados.es/api/rest/V1.0/catalog/product?page=1&limit=20&offset=0&orderById=1&filters=filter.offerDeferred%3Atrue&showRecommendations=false&categories=1690"

# Pagination and retry settings
MAX_PAGES = 45  # Maximum pages to scrape for main beverages API
OFFER_PRICE_MAX_PAGES = 7  # Maximum pages for OfferPrice promotions
MAX_EMPTY_PAGES = 3  # Stop after this many consecutive empty pages
MAX_RETRIES = 3  # Maximum retries for failed API requests
REQUEST_TIMEOUT = 15  # Timeout for API requests in seconds
RETRY_DELAY = 2  # Delay between retry attempts in seconds
PAGE_DELAY = 1  # Delay between page requests in seconds
OUTPUT_DIR = r"C:\Users\richa\Downloads\comexsoft-challengue\bm_scraper\output"
OUTPUT_FILE = "bm_productos_bebidas.json"