import os
from datetime import datetime

import scrapy
from scrapy.shell import inspect_response

from pisocrawler.spiders import site_accounts
from pisocrawler.items import PisoFiCrawlerItemLoader
from pisocrawler.settings import SCRAPED_ITEMS_DIR


class PisoficrawlerSpider(scrapy.Spider):
    '''
    Spider for parsing basic vendo details including remote link to be used
    in portalcrawler spider. Scraped items will be stored in the
    scraped_items/vendo.json file. Previously scraped items will be overriden
    every crawl.
    '''
    
    name = 'pisoficrawler'
    allowed_domains = site_accounts.PISOFIPH_ALLOWED_DOMAINS
    start_urls = [site_accounts.PISOFIPH_LOGIN_URL]

    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': os.path.join(SCRAPED_ITEMS_DIR, 'vendo.json'),
        'FEED_EXPORT_INDENT': 4,
        'ITEM_PIPELINES': {'pisocrawler.pipelines.PisoFiCrawlerPipeline': 300}
    }

    def parse(self, response):
        '''
        Takes care of login and redirection to Dashboard.
        '''
        token = response.xpath(
            '//input[@name="_token"]/@value').extract_first()

        yield scrapy.FormRequest.from_response(
            response=response,
            formdata={
                '_token': token,
                **site_accounts.PISOFIPH_LOGIN_CREDENTIALS
            },
            callback=self.after_login
        )

    def after_login(self, response):
        '''
        Redirect to device page after login
        '''
        yield scrapy.Request(
            url=site_accounts.PISOFIPH_DEVICES_URL,
            callback=self.parse_device_id
        )

    def parse_device_id(self, response):
        '''
        Parse basic device details most importantly the device_id which will
        be used in extracting the device remote link.
        '''

        for device in response.xpath('//table/tbody/tr'):
            device_id = device.xpath('td/text()').extract_first()
            loader = PisoFiCrawlerItemLoader(selector=device)
            loader.add_value('device_id', device_id)
            loader.add_xpath('name', 'td/text()')
            loader.add_xpath('ip', 'td/text()')
            loader.add_xpath('description', 'td/text()')
            loader.add_xpath(
                'lic', 'td/span[@class="badge badge-success"]/text()')

            # Next request to parse remote link
            url = 'https://pisofiph.com/dashboard/my-devices/{}/remote'.format(
                device_id.strip())
            request = scrapy.Request(
                url=url,
                callback=self.parse_remote_link
            )
            request.cb_kwargs['loader'] = loader
            yield request

    def parse_remote_link(self, response, loader):
        '''
        Parses remote link of the device and completes the item loading
        process from previous callback. Also added crawl timestamp.
        '''
        remote = response.xpath('//a[@class="btn-link"]/@href').extract_first()
        loader.add_value('remote', remote)
        loader.add_value(
            'updated_at', datetime.now().strftime('%m/%d/%y %H:%M:%S'))
        yield loader.load_item()

        # inspect_response(response, self)
