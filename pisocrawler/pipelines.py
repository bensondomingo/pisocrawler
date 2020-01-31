# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os

from scrapy.exceptions import DropItem
from pisocrawler.settings import SCRAPED_ITEMS_DIR


class PisoFiCrawlerPipeline(object):

    def __init__(self):
        super().__init__()
        self.device_ids = set()  # for duplicate item finding

    def open_spider(self, spider):
        '''
        Overwrite previously scraped items
        '''
        with open(os.path.join(SCRAPED_ITEMS_DIR, 'vendo.json'), 'w+') as f:
            pass

    def process_item(self, item, spider):
        '''
        Drop duplicate items and items with no device_id.
        '''
        if not item['device_id']:
            raise DropItem('Item with no device id found: %s' % item)

        if item['device_id'] in self.device_ids:
            raise DropItem('Duplicate item found: %s' % item)

        self.device_ids.add(item['device_id'])
        return item


class SalesTransactionPipeline(object):

    def open_spider(self, spider):
        '''
        Overwrite previously scraped items
        '''
        with open(os.path.join(SCRAPED_ITEMS_DIR, 'transactions.json'), 'w+') as f:
            pass

    def process_item(self, item, spider):
        '''
        Drop items with no mac_addr.
        '''
        if not item['mac_addr']:
            raise DropItem('Item with no mac address found: %s' % item)
        
        return item

            
