# -*- coding: utf-8 -*-
import scrapy


class PisoficrawlerSpider(scrapy.Spider):
    name = 'pisoficrawler'
    allowed_domains = ['https://pisofiph.com']
    start_urls = ['http://https://pisofiph.com/login/']

    def parse(self, response):
        pass
