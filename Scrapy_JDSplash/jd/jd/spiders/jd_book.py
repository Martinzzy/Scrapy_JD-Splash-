# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from scrapy import Request
from ..items import JdItem

lua_script = '''
function main(splash)
    splash:go(splash.args.url)
    splash:wait(2)
    splash:runjs("document.getElementsByClassName('page')[0].scrollIntoView(true)")
    splash:wait(2)
    return splash:html()
end
'''


class JdBookSpider(scrapy.Spider):
    name = 'jd_book'
    allowed_domains = ['search.jd.com']
    base_url = 'https://search.jd.com/Search?keyword=Python&enc=utf-8&book=y&wq=Python'

    def start_requests(self):
        yield Request(self.base_url,callback=self.parse_urls,dont_filter=True)

    def parse_urls(self,response):
        total = response.css("span.fp-text i::text").extract_first()
        for i in range(int(total)):
            url = '{}&page={}'.format(self.base_url,2*i+1)
            yield SplashRequest(url,endpoint="execute",args={"lua_source":lua_script,"images":0},cache_args=["lua_source"],dont_filter=True)


    def parse(self, response):
        JD = JdItem()
        # print('正在爬取第{}页'.format(response.meta["page"]))
        result = response.css("ul.gl-warp.clearfix li.gl-item")
        print(len(result))
        for sel in response.css("ul.gl-warp.clearfix li.gl-item"):
            name = sel.css("div.p-name").xpath("string(.//em)").extract_first()
            author = sel.css("div.p-bookdetails span.p-bi-name a::text").extract_first()
            price = sel.css("div.p-price i::text").extract_first()
            shop = sel.css("div.p-shopnum a.curr-shop::text").extract_first()
            comments = sel.css("div.p-commit a::text").extract_first()

            JD["name"] = name
            JD["author"] = author
            JD["price"] = price
            JD["shop"] = shop
            JD["comments"] = comments
            yield JD

