# -*- coding: utf-8 -*-
import re
import scrapy
from lxml import etree
from ..items import PptItem


class PptSpider(scrapy.Spider):
    name = 'ppt'
    allowed_domains = ['www.1ppt.com']
    start_urls = ['http://www.1ppt.com/']

    def parse(self, response):
        """一级页面函数:获取下载ppt页面的url"""
        html = response.text
        xpath_one = '//*[@id="navMenu"]/ul/li[7]/a/@href'
        one_html = etree.HTML(html)
        link_list = one_html.xpath(xpath_one)
        two_url = 'http://www.1ppt.com' + link_list[0]
        yield scrapy.Request(url=two_url, callback=self.parse_two_page)

    def parse_two_page(self, response):
        """二级页面函数:获取每个类别的一个URL+目录
        并通过Request中meta参数把目录名传到下一个函数,最终交给item对象
        """
        html = response.text
        regex = "<li><a href='(.*?)'>(.*?)</a></li>"
        pattern = re.compile(regex, re.S)
        ppt_list = pattern.findall(html)
        # print(ppt_list)
        for ppt in ppt_list:
            # print(ppt)
            # ppt = ("链接","目录名称")
            if ppt[1][-1:] == '>':
                continue
            elif ppt[1][-1:] == '页':
                continue
            else:
                ppt_title = ppt[1]
                three_url = 'http://www.1ppt.com' + ppt[0]
                yield scrapy.Request(url=three_url,
                                     meta={'url': three_url, 'title': ppt_title},
                                     callback=self.all_parse_page)

    def all_parse_page(self, response):
        """获取每个类别的所有页URL"""
        html = response.text
        url = response.meta['url']
        ppt_title = response.meta['title']
        # print(url) # http://www.1ppt.com/xiazai/donghua/
        xpath_all = './/div[@class="w center mt4"]/dl[@class="dlbox"]/dd/div/ul/li/a/@href'
        parse_html = etree.HTML(html)
        page_list = parse_html.xpath(xpath_all)
        # print(page_list) # ['ppt_gongsi_2.html', 'ppt_gongsi_3.html', 'ppt_gongsi_4.html',...]
        """获取所有页的思路是:在第一页的响应中有所有页的URL,我就把每个类别所有的URL匹配出来,
           然后取最后一个,再把最后一个URL的那个数字通过切片取出来,然后做循环"""
        page = page_list[-1]
        # print(page) # ppt_donghua_9.html
        pa = page.split('.')[0].split('_')[0]  # ppt
        ge = page.split('.')[0].split('_')[1]  # donghua
        num = int(page.split('.')[0].split('_')[2])
        for i in range(num):
            all_url = url + pa + '_' + ge + '_' + str(i) + ".html"
            # print(all_url) # http://www.1ppt.com/xiazai/huiben/ppt_huiben_32.html
            yield scrapy.Request(url=all_url, meta={'title': ppt_title}, callback=self.parse_three_page)

    def parse_three_page(self, response):
        """三级页面函数:
        获取每个PPT详细信息URL并根据规则拼接每个PPT的下载页URL
        每个PPT的下载页URL就是PPT详细URL+#xiazai
        """
        html = response.text
        ppt_title = response.meta['title']
        regex = '<h2><a href="(.*?)" target="_blank">(.*?)</a></h2>'
        pattern = re.compile(regex, re.S)
        file_list = pattern.findall(html)
        for file in file_list:
            four_url = 'http://www.1ppt.com' + file[0] + '#xiazai'
            yield scrapy.Request(url=four_url, meta={'title': ppt_title}, callback=self.parse_four_page)

    def parse_four_page(self, response):
        """四级页面函数:获取文件下载URL+PPT名称
        并把文件下载URL+PPT名称+目录传给item"""
        item = PptItem()
        item['ppt_title'] = response.meta['title']
        html = response.text
        reg = '<h2 class="lab_title"><a name="xiazai"></a>(.*?) 下载地址:</h2>'
        p = re.compile(reg, re.S)
        title = p.findall(html)
        item['file_name'] = title[0]
        regex = '<li><a href="(.*?)" target="_blank">'
        pattern = re.compile(regex, re.S)
        link = pattern.findall(html)
        item['file_link'] = link[0]
        yield item
