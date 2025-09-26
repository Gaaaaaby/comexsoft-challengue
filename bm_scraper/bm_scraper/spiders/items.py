# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BmScraperItem(scrapy.Item):
    pass

class BmProductItem(scrapy.Item):
    supermarket = scrapy.Field()
    ean = scrapy.Field()
    id = scrapy.Field()
    brand = scrapy.Field()
    description = scrapy.Field()
    category = scrapy.Field()
    url = scrapy.Field()
    image_links = scrapy.Field()
    measuring_unit = scrapy.Field()
    price = scrapy.Field()
    unit_price = scrapy.Field()
    offer_price = scrapy.Field()
    promotion = scrapy.Field()
    manufacturer = scrapy.Field()
    raw_ingredients = scrapy.Field()