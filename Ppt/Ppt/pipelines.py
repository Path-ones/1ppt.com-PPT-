# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.files import FilesPipeline


class PptPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        print('正在下载:', item['file_name'])
        yield scrapy.Request(url=item['file_link'],
                             meta={'name': item['file_name'], 'title': item['ppt_title']})

    def file_path(self, request, response=None, info=None):
        filename = '/%s/%s' % (request.meta['title'], request.meta['name'] + '.' + request.url.split('.')[-1])
        return filename
