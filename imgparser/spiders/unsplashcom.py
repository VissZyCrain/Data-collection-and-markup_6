import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from ..items import ImgparserItem


class UnsplashcomSpider(scrapy.Spider):
    name = 'unsplashcom'   # название паука
    allowed_domains = ['unsplash.com']   # разрешенные домены
    start_urls = ['https://unsplash.com']   # стартовая страница


    def parse(self, response: HtmlResponse):
        # список ссылок на категории изображений
        category_links = response.xpath("(//ul)[last()]//a[not(text()='Unsplash+') and not(text()='Editorial')]/@href").getall()
        for category_link in category_links:
            # запросы на страницу категории
            yield response.follow(url=category_link, callback=self.parse)

        # список ссылок на картинки
        img_links = response.xpath("//a[@itemprop='contentUrl']/@href").getall()
        # ссылки дублируются (вместо 20 получаем 60)
        for img_link in set(img_links):
            yield response.follow(img_link, callback=self.img_parse)


    def img_parse(self, response):
        loader = ItemLoader(item=ImgparserItem(), response=response)   # элемент loader
        loader.add_xpath('category', '//h3/..//a/text()')
        loader.add_xpath('name', '//h1/text()')
        loader.add_value('url', response.url)
        loader.add_xpath('image', '//button//img/@srcset')
        yield loader.load_item()