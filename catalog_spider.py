import scrapy

class ProductsSpider(scrapy.Spider):
    name = "products_spider"
    allowed_domains = ["order-nn.ru"]
    start_urls = ["https://order-nn.ru/kmo/catalog/5999/"]

    def parse(self, response):
        for product in response.xpath('//div[@class="horizontal-product-item-container"]'):
            name = product.xpath(
                './/div[@class="horizontal-product-item-block_3_2"]/a/span[@itemprop="name"]/text()').get()
            price = product.xpath('.//span[@itemprop="price" and contains(@class, "span-price-number")]/text()').get()
            product_url = product.xpath('.//div[@class="horizontal-product-item-block_3_2"]/a/@href').get()

            # Формируем абсолютный URL для перехода на страницу товара
            product_url = response.urljoin(product_url)

            # Переходим на страницу товара для извлечения описания и характеристик
            yield scrapy.Request(url=product_url, callback=self.parse_product_details,
                                 meta={'name': name, 'price': price})

    def parse_product_details(self, response):
        name = response.meta['name']
        price = response.meta['price']
        description = response.xpath('//div[@id="block-description"]/div[@id="for_parse"]/p//text()').getall()
        description = ' '.join(description).strip()
        harac = response.xpath("./td[@class='table-character-text']/text()").get()
        # Сбор характеристик
        characteristics = {}
        rows = response.xpath("//div[@class='table-character']//tr")
        for row in rows:
            key = row.xpath("./td[@class='table-character-text']/text()").get()
            value = row.xpath("./td[@class='table-character-value']/text()").get()
            if key and value:
                characteristics[key.strip()] = value.strip()

        yield {
            'name': name,
            'price': price,
            'description': description,
            'characteristics': harac
        }
