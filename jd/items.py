# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdItem(scrapy.Item):
    id = scrapy.Field()
    picture = scrapy.Field()
    price = scrapy.Field()
    info = scrapy.Field()
    comment_num = scrapy.Field()


class Message(scrapy.Item):
    id = scrapy.Field()
    people = scrapy.Field()
    content = scrapy.Field()
    buy_time = scrapy.Field()
    ref_name = scrapy.Field()
