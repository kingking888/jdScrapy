# -*- coding: utf-8 -*-
import json

import jsonpath
import scrapy

from jd.items import *
from urllib.parse import urlparse, parse_qs


class IpadSpider(scrapy.Spider):
    name = 'ipad'
    allowed_domains = ['www.jd.com', "club.jd.com", "item.jd.com", "search.jd.com"]
    start_urls = [
        'https://search.jd.com/Search?keyword=ipad&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&bs=1&wq=ipad&ev=exbrand_Apple%5E&page=1']

    def parse(self, response):
        page = parse_qs(urlparse(response.url).query).get("page")[0]

        lis = response.xpath("//div[@class='ml-wrap']/div[@id='J_goodsList']/ul/li")
        for li in lis:
            # 要求爬取图片,价格,描述,店名,评论数.10页,一张表. 首页30分
            id = li.xpath("./@data-sku").extract_first()
            picture = "http:" + li.xpath(".//div[@class='p-img']//img/@source-data-lazy-img").extract_first()
            price = li.xpath(".//div[@class='p-price']/strong/i/text()").extract_first()
            info = li.xpath("string(.//div[contains(@class, 'p-name')])").extract_first().replace(" ", "").replace("\n",
                                                                                                                   "").strip()
            good = JdItem()
            good["id"] = id
            good["picture"] = picture
            good["price"] = price
            good["info"] = info

            # 开始解析评论信息。
            self.request_message(id, 0)

            # 解析评论点击数
            url = "https://club.jd.com/comment/productCommentSummaries.action?referenceIds=" + id
            yield scrapy.Request(url=url, callback=self.get_comment, meta={"good": good})

        # 获取下一页的内容
        tmp_url = "https://search.jd.com/Search?keyword=ipad&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&bs=1&wq=ipad&ev=exbrand_Apple%5E&page="
        yield scrapy.Request(url=tmp_url + str(int(page) + 1), callback=self.parse)

    def get_comment(self, response):
        good = response.meta.get("good")
        message = json.loads(response.text)
        good["comment_num"] = jsonpath.jsonpath(message, "$..CommentCountStr")[0]

        yield good

    def comment_desc(self, response):
        data = json.loads(response.text)

        # 原来商品的id
        id = parse_qs(urlparse(response.url).query).get("productId")[0]
        page = parse_qs(urlparse(response.url).query).get("page")[0]

        lists = jsonpath.jsonpath(data, "$..comments.*")
        for item in lists:
            message = Message()

            people = jsonpath.jsonpath(item, "$.nickname")[0]
            content = jsonpath.jsonpath(item, "$.content")[0]
            buy_time = jsonpath.jsonpath(item, "$.creationTime")[0]
            ref_name = jsonpath.jsonpath(item, "$.referenceName")[0]

            message['id'] = id
            message['people'] = people
            message['content'] = content
            message['buy_time'] = buy_time
            message['buy_time'] = buy_time
            message['ref_name'] = ref_name
            yield message

        # desc_url = "https://item.jd.com/" + id + ".html"
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0',
        #     'Accept-Encoding': 'gzip, deflate, sdch',
        #     'Accept-Language': 'zh-CN,zh;q=0.8',
        #     "callback": "fetchJSON_comment98vv14203",
        #     "Referer": desc_url
        # }
        # yield scrapy.Request(
        #     url="https://club.jd.com/comment/skuProductPageComments.action?productId=" + id + "&score=0&sortType=5&page=" + str(
        #         int(page) + 1) + "&pageSize=10&isShadowSku=0&fold=1",
        #     callback=self.comment_desc, headers=headers)
        self.request_message(id, page)

    # 封装请求评论的方法：
    def request_message(self, id, page):
        print("调用了评论接口")
        desc_url = "https://item.jd.com/" + id + ".html"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            "callback": "fetchJSON_comment98vv14203",
            "Referer": desc_url
        }
        yield scrapy.Request(
            url="https://club.jd.com/comment/skuProductPageComments.action?productId=" + id + "&score=0&sortType=5&page=" + str(
                int(page) + 1) + "&pageSize=10&isShadowSku=0&fold=1",
            callback=self.comment_desc, headers=headers)
