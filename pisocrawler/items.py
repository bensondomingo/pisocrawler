# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader import processors


def strip_whitespace(self, values):
    return map(str.strip, values)


def name_output_processor(self, values):
    return values[1]


def ip_output_processor(self, values):
    return values[2]


def description_output_processor(self, values):
    return values[5]


class PisoFiCrawlerItem(scrapy.Item):
    device_id = scrapy.Field()
    name = scrapy.Field()
    ip = scrapy.Field()
    lic = scrapy.Field()
    description = scrapy.Field()
    remote = scrapy.Field()
    updated_at = scrapy.Field()


class PisoFiCrawlerItemLoader(ItemLoader):
    default_item_class = PisoFiCrawlerItem

    # Input processors
    default_input_processor = strip_whitespace

    # Output processors
    default_output_processor = processors.TakeFirst()
    name_out = name_output_processor
    ip_out = ip_output_processor
    description_out = description_output_processor
