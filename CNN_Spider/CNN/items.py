# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CnnItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    update = scrapy.Field()   #更新／发布时间
    title = scrapy.Field()    #标题
    type = scrapy.Field()     #类型
    summary = scrapy.Field()  #总结
    content = scrapy.Field()  #内容
    URL = scrapy.Field()      #链接
    pic = scrapy.Field()      #图片链接
    picDesc = scrapy.Field()  #图片描述