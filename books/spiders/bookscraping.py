import scrapy
from scrapy.http import Response


class BookscrapingSpider(scrapy.Spider):
    name = 'bookscraping'
    allowed_domains = ['books.toscrape.com']
    BASE_URL = "https://books.toscrape.com/"

    def start_requests(self):
        yield scrapy.Request(
            url=self.BASE_URL,
            callback=self._go_over_pages,
        )

    def _go_over_pages(self, response):
        page_count = int(response.css(".pager .current::text").get().strip().split()[-1])
        urls = [f"{self.BASE_URL}catalogue/page-{str(n_page)}.html"
                for n_page in range(1, page_count + 1)]

        for url in urls:
            yield scrapy.Request(url=url, callback=self._go_over_books_info)

    def _go_over_books_info(self, response):
        products_links = response.css(".product_pod > h3 a::attr(href)").getall()
        for link in products_links:
            current_full_url = self.BASE_URL + "catalogue/" + link
            yield scrapy.Request(current_full_url)

    def parse(self, response: Response, **kwargs):
        title = response.css(".breadcrumb .active::text").get()
        price = response.css(".product_main .price_color::text").get().replace("£", "")
        amount_in_stock = response.css(".product_main .instock").get().split("(")[-1].split()[0]
        rating = response.css(".product_main .star-rating").xpath("@class").extract_first().split()[1]
        category = response.css(".breadcrumb li:nth-last-child(2) a::text").get()
        description = response.css(".product_page > p::text").get()
        upc = response.css(".table-striped tr:nth-child(1) td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
