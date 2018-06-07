# coding = utf-8
import scrapy
from scrapy.http import Request
import re

from CNN.items import CnnItem


class cnnSpider(scrapy.spiders.Spider):
    name = "CNNspider"   #爬虫名，供命令scrapy crawl cnnspider使用
    allowed_domains = ["cnn.com"]   #允许爬虫运行的域
    start_urls = ["https://edition.cnn.com/","http://money.cnn.com/"]  #爬取起始的url

    # 请求头
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'cache-control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'
    }

    # 重写方法，设置请求头（其实有更简单的方法，在settings里设置default-headers就行了
    def make_requests_from_url(self, url):
        return Request(url, headers=self.headers, dont_filter=True)


    # 主页面解析函数，这里必须为parse()
    def parse(self,response):
        #首页最新新闻 返回的json
        jsonstr = response.xpath('/html/body/script[1]').extract()[0]
        match = "/2018/\d{2}/\d{2}/[a-zA-Z]+/[a-zA-Z0-9-]+/index.html"
        urls = re.findall(match,jsonstr)
        # print(urls)
        for url in urls:
            url = "https://edition.cnn.com" +  url    #拼接每个新闻的链接
            yield Request(url, callback=self.parseNews)  # 对每个新闻分别发请求


        #首页每个模块链接
        links10 = response.xpath('//*[@id="nav"]/div[2]/div[2]/a[re:test(@href,"^/[a-zA-Z]")]/@href').extract()
        links10 = links10[:-2]
        print("hhjhjhjhjhjh")
        print(links10)
        links = response.xpath('/html/body/footer/div[2]/div/div[1]//a[contains(@class,"m-footer__link")]/@href').extract()
        #第一类 不需要拼接的链接
        links11 = links[0:14]
        links12 = links[18:22]
        links13 = links[28:55]

        links1 = links10 + links11 + links12 + links13
        for link1 in links1:
            link1 = "https://edition.cnn.com" +  link1    #第一种需要拼接每个模块的链接
            print("模块的链接: " + link1)
            yield Request(link1, callback=self.parseLink)  #对每个模块分别发请求

        links20 = response.xpath('//*[@id="nav"]/div[2]/div[2]/a[contains(@href,"http://money.cnn.com/")]/@href').extract()
        # 第二类 需要拼接的链接
        links21 = links[14:18]
        links22 = links[22:28]

        links2 = links20 + links21 + links22
        for link2 in links2:
            print("模块的链接: " + link2)                    #第二种不需要拼接每个模块的链接
            yield Request(link2, callback=self.parseLink)  # 对每个模块分别发请求


    # 解析每个模块
    def parseLink(self,response):
        print("进入parseLink函数 》》》")
        # 模块内的新闻
        path1 = response.xpath('//a[re:test(@href,"^/2018/\d{2}/\d{2}/[a-zA-Z]+/[a-zA-Z0-9-]+/index.html")]/@href').extract()
        path2 = response.xpath('//a[re:test(@href,"^/[a-zA-Z]+/article/[a-zA-Z0-9-]+/index.html")]/@href').extract()

        jsonstr = response.xpath('/html/body/script[1]').extract()[0]
        match = "/2018/\d{2}/\d{2}/[a-zA-Z]+/[a-zA-Z-]+/index.html"
        path3 = re.findall(match, jsonstr)

        paths = path1 + path2 + path3
        paths = list(set(paths))
        for path in paths:
            path = "https://edition.cnn.com" + path
            yield Request(path, callback=self.parseNews)  # 对每个新闻分别发请求

        path4 = response.xpath('//a[re:test(@href,"^//money.cnn.com/2018/\d{2}/\d{2}/[a-zA-Z]+/[a-zA-Z0-9-]+/index.html")]/@href').extract()
        for path in path4:
            path = "http:" + path
            yield Request(path, callback=self.parseNews)  # 对每个新闻分别发请求

        path5 = response.xpath('//a[re:test(@href,"^http://money.cnn.com/2018/\d{2}/\d{2}/[a-zA-Z]+/[a-zA-Z0-9-]+/index.html?[a-zA-Z=_]+")]/@href').extract()
        for path in path5:
            yield Request(path, callback=self.parseNews)  # 对每个新闻分别发请求



    #解析每条新闻
    def parseNews(self,response):
        item = CnnItem()
        print("开始处理新闻 >>>")
        # 对新闻内容的处理
        # 决定是否留存item的标记
        self.gooditem = True

        # 处理文章标题
        try:
            title = response.xpath('//h1[@class="pg-headline"]/text()').extract()
            if not title:
                title = response.xpath('//h1[@class="Article__title"]/text()').extract()
            if not title:
                title = response.xpath('//h1[@class="article-title speakable"]/text()').extract()
            if not title:
                title = response.xpath('//h1[@class="PageHead__title"]/text()').extract()

            item['title'] = title[0]
            print("title------title")
            print(item['title'])
        except IndexError:
            # 丢弃文章
            self.gooditem = False


        # 处理文章概要
        try:
            summary = response.xpath('//p[@class="zn-1 speakable"]').xpath('string( )').extract()
            if not summary:
                summary = response.xpath('//h2[@class="speakable"]').xpath('string( )').extract()
            if not summary:
                summary = response.xpath('//div[@class="Paragraph__component BasicArticle__paragraph BasicArticle__pad Paragraph__isDropCap"]').xpath('string( )').extract()
            if summary:
                item['summary'] = '、'.join(summary[0:])
            else:
                highlights = response.xpath('//ul[contains(@class, "el__storyhighlights__list")]/li/text()').extract()
                if highlights:
                    item['summary'] = '、'.join(highlights[0:])
                else:
                    item['summary'] = ''
            print("summary----------summary")
            print(item['summary'])
        except IndexError:
            # 丢弃文章
            self.gooditem = False

        # 处理文章主体
        # 正常模式
        try:
            body = response.xpath('//div[contains(@class, "zn-body__paragraph")]').xpath('string( )').extract()
            if not body:
                response.xpath('//div[@class="Article__body"]/div[@class="Article__body "]').xpath('string( )').extract()
            if not body:
                body = response.xpath('//*[@id="storytext"]//p').xpath('string( )').extract()
            if not body:
                body = response.xpath('//p[contains(@class, "speakable")]').xpath('string( )').extract()
            if not body:
                body = response.xpath('//div[@class="Paragraph__component BasicArticle__paragraph BasicArticle__pad"]').xpath('string( )').extract()

            item['content'] =summary + body
        except IndexError:
            # 丢弃文章
            self.gooditem = False

        # 处理分类

        # 方法：从URL中提取
        try:
            item['type'] = response.url.split('/')[-3]
            if item['type'] == 'article' :
                item['type'] = response.url.split('/')[-4]
        except IndexError:
            # 疑难杂类
            item['type'] = 'news'

        # 处理文章图片
        try:
            item['pic'] = response.xpath('//*[@id="ie_dottop"]/img/@src').extract()[0]
            item['picDesc'] = response.xpath('//h2[@class="speakable"]').xpath('string( )').extract()[0]
        except IndexError:
            try:
                item['pic'] = response.xpath('//*[@id="large-media"]/div/img[contains(@class, "media__image media__image--responsive")]/@data-src-mini').extract()[0]
                item['pic'] = "https:"+ item['pic']
                item['picDesc'] = response.xpath('//*[@id="large-media"]/div/div[2]/div/text()').extract()[0]
            except IndexError:
                try:
                    # 视频封面
                    item['pic'] = response.xpath('//img[@class="media__image"]/@src').extract()[0]
                    item['pic'] = "https:" + item['pic']
                    item['picDesc'] = response.xpath('//img[@class="media__image"]/@alt').extract()[0]
                except IndexError:
                    self.gooditem = False

        # 处理 Reference URL
        item['URL'] = response.url

        # 处理发布时间

        try:
             update = response.xpath('//p[contains(@class, "update-time")]/text()').extract()[0]
             item['update'] = update.split(')')[-1]
        except IndexError:
            try:
                update = response.xpath('//span[@class="cnnDateStamp"]/text()').extract()[0]
            except IndexError:
                # 丢弃文章
                self.gooditem = False

        # 将爬取好的文章对象yield
        if self.gooditem: yield item
