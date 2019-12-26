# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PptItem(scrapy.Item):
    # define the fields for your item here like:
    ppt_title = scrapy.Field()
    file_name = scrapy.Field()
    file_link = scrapy.Field()
