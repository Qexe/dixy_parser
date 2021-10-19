import scrapy
import re
from scrapy import Request
from DixyDostavka.items import Product


class DixyDostavkaSpider(scrapy.Spider):
    name = 'dixy_dostavka'
    allowed_domains = ['dostavka.dixy.ru']
    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8',
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOAD_TIMEOUT': 90,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400,
        }
    }

    def start_requests(self):
        url = 'https://dostavka.dixy.ru/catalog/moloko_syr_yaytsa/'
        yield Request(url=url, callback=self.parse_product_urls)

    def parse_product_urls(self, response):
        urls = response.xpath('//div[@class="item_info"]/div[@class="item-title"]/a/@href').getall()
        for url in urls:
            yield response.follow(url=url, callback=self.parse)
        next_page = response.xpath(
            '//ul[@class="flex-direction-nav"]/li[@class="flex-nav-next colored_theme_hover_text"]/a/@href').get()
        current_page = response.xpath('//div[@class="nums"]/span[@class="cur"]/text()').get()
        if next_page and int(current_page) < 10:
            yield response.follow(url='https://dostavka.dixy.ru' + next_page, callback=self.parse_product_urls)


    def parse(self, response):
        item = Product()
        item['product_url'] = response.url
        item['price'] = response.xpath(
            "//div[@class='price_value_block values_wrapper']/span[@class='price_value']/text()").get()
        item['title'] = response.xpath('//div[@class="topic__heading"]/h1/text()').get()
        img_url = response.xpath(
            "//div[@class='product-detail-gallery__item product-detail-gallery__item--middle text-center']/a/@href").getall()
        item["img_url"] = list(map(lambda img_url: 'https://dostavka.dixy.ru' + img_url, img_url))
        stock = response.xpath(
            '//div[@class="button_block "]//i[@class="svg inline  svg-inline-fw ncolor colored"]/@title').get()
        if stock:
            item['stock'] = 'True'
        else:
            item['stock'] = 'False'
        yield item
