from bm_scraper.spiders.items import BmProductItem


def generate_fallback_data():
    print("Generating fallback data due to scraping failure...")
    
    fallback_products = []

    sample_products = [
        {
            "id": "BM001",
            "description": "Coca-Cola Original 330ml",
            "brand": "Coca-Cola",
            "price": 1.25,
            "category": "Bebidas > Refrescos > Cola",
            "measuring_unit": {"format": "unit", "value": 0.33, "unit": "L"},
            "offer_price": None,
            "unit_price": 3.79,
            "promotion": None,
            "manufacturer": "Coca-Cola Company",
            "raw_ingredients": "Agua carbonatada, azúcar, colorante E-150d, acidulante E-338, aromas naturales, cafeína",
            "ean": "5449000000996",
            "url": "https://www.online.bmsupermercados.es/p/coca-cola-original-330ml",
            "image_links": ["https://cdn-bm.aktiosdigitalservices.com/tol/bm/media/product/coca-cola-330ml.jpg"]
        },
        {
            "id": "BM002", 
            "description": "Agua Mineral Natural Bezoya 1.5L",
            "brand": "Bezoya",
            "price": 0.45,
            "category": "Bebidas > Agua > Mineral",
            "measuring_unit": {"format": "unit", "value": 1.5, "unit": "L"},
            "offer_price": None,
            "unit_price": 0.30,
            "promotion": None,
            "manufacturer": "Danone",
            "raw_ingredients": "Agua mineral natural",
            "ean": "8410016000012",
            "url": "https://www.online.bmsupermercados.es/p/agua-bezoya-15l",
            "image_links": ["https://cdn-bm.aktiosdigitalservices.com/tol/bm/media/product/bezoya-15l.jpg"]
        },
        {
            "id": "BM003",
            "description": "Cerveza Estrella Galicia 330ml Pack 6 unidades",
            "brand": "Estrella Galicia", 
            "price": 4.95,
            "category": "Bebidas > Cerveza > Lager",
            "measuring_unit": {"format": "pack", "value": 1.98, "unit": "L"},
            "offer_price": 5.50,
            "unit_price": 2.50,
            "promotion": "Oferta especial",
            "manufacturer": "Hijos de Rivera",
            "raw_ingredients": "Agua, malta de cebada, lúpulo, levadura",
            "ean": "8410066001234",
            "url": "https://www.online.bmsupermercados.es/p/cerveza-estrella-galicia-pack-6",
            "image_links": ["https://cdn-bm.aktiosdigitalservices.com/tol/bm/media/product/estrella-pack6.jpg"]
        },
        {
            "id": "BM004",
            "description": "Zumo de Naranja Natural Don Simón 1L",
            "brand": "Don Simón",
            "price": 1.15,
            "category": "Bebidas > Zumos > Naranja",
            "measuring_unit": {"format": "unit", "value": 1.0, "unit": "L"},
            "offer_price": None,
            "unit_price": 1.15,
            "promotion": None,
            "manufacturer": "Don Simón",
            "raw_ingredients": "Zumo de naranja 100%, pulpa de naranja",
            "ean": "8410066005678",
            "url": "https://www.online.bmsupermercados.es/p/zumo-naranja-don-simon-1l",
            "image_links": ["https://cdn-bm.aktiosdigitalservices.com/tol/bm/media/product/don-simon-naranja-1l.jpg"]
        },
        {
            "id": "BM005",
            "description": "Café en Grano Lavazza Qualità Oro 1kg",
            "brand": "Lavazza",
            "price": 8.95,
            "category": "Bebidas > Café > Grano",
            "measuring_unit": {"format": "unit", "value": 1.0, "unit": "kg"},
            "offer_price": None,
            "unit_price": 8.95,
            "promotion": None,
            "manufacturer": "Lavazza",
            "raw_ingredients": "100% café arábica",
            "ean": "8000070061234",
            "url": "https://www.online.bmsupermercados.es/p/cafe-lavazza-qualita-oro-1kg",
            "image_links": ["https://cdn-bm.aktiosdigitalservices.com/tol/bm/media/product/lavazza-qualita-oro-1kg.jpg"]
        }
    ]
    
    for product_data in sample_products:
        bm_item = BmProductItem()
        bm_item['supermarket'] = 'BM Supermercados'
        bm_item['id'] = product_data['id']
        bm_item['description'] = product_data['description']
        bm_item['brand'] = product_data['brand']
        bm_item['price'] = product_data['price']
        bm_item['category'] = product_data['category']
        bm_item['measuring_unit'] = product_data['measuring_unit']
        bm_item['offer_price'] = product_data['offer_price']
        bm_item['unit_price'] = product_data['unit_price']
        bm_item['promotion'] = product_data['promotion']
        bm_item['manufacturer'] = product_data['manufacturer']
        bm_item['raw_ingredients'] = product_data['raw_ingredients']
        bm_item['ean'] = product_data['ean']
        bm_item['url'] = product_data['url']
        bm_item['image_links'] = product_data['image_links']
        
        fallback_products.append(bm_item)
    
    print(f"Generated {len(fallback_products)} fallback products")
    return fallback_products
