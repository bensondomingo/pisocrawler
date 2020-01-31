import os
from urllib.parse import urljoin

import scrapy
from scrapy.shell import inspect_response

from pisocrawler.spiders import site_accounts
from pisocrawler.items import SalesTransactionCrawlerItemLoader
from pisocrawler.settings import SCRAPED_ITEMS_DIR


class PortalCrawlerSpider(scrapy.Spider):
    name = 'portalcrawler'

    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': os.path.join(SCRAPED_ITEMS_DIR, 'transactions.json'),
        'FEED_EXPORT_INDENT': 4,
        'ITEM_PIPELINES': {'pisocrawler.pipelines.SalesTransactionPipeline': 300}
    }

    def __init__(self, url, *args, **kwargs):
        super(PortalCrawlerSpider, self).__init__(*args, **kwargs)
        self.base_url = url
        self.start_urls = [url, ]

    def parse(self, response):
        '''
        Takes care of login and redirection to System Status page.
        '''

        csrf_name = response.xpath(
            '//input[@id="csrf_name"]/@value').extract_first()
        csrf_vlaue = response.xpath(
            '//input[@id="csrf_value"]/@value').extract_first()

        yield scrapy.FormRequest.from_response(
            response=response,
            formid='frm',
            formdata={
                'csrf_name': csrf_name,
                'csrf_value': csrf_vlaue,
                'url': None,
                **site_accounts.PORTAL_LOGIN_CREDENTIALS
            },
            callback=self.after_login
        )

    def after_login(self, response):
        '''
        Redirect to sales page after login
        '''
        yield scrapy.Request(
            url=urljoin(self.base_url, 'admin/sales/detailed'),
            callback=self.parse_sales
        )

    def parse_sales(self, response):
        title = response.xpath('//title/text()').extract_first()
        print('=============================================')
        print(title)
        print('=============================================')

        for transaction in response.xpath('//tbody/tr'):
            loader = SalesTransactionCrawlerItemLoader(selector=transaction)
            loader.add_xpath('transaction_date', 'td/text()')
            loader.add_xpath('mac_addr', 'td/text()')
            loader.add_xpath('transaction_type', 'td/text()')
            loader.add_xpath('vendo', 'td/text()')
            loader.add_xpath('amount', 'td/text()')

            yield loader.load_item()

        # inspect_response(response, self)
