# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import pymysql
import time

class CnnPipeline(object):
    # 在构造函数中连接数据库
    def __init__(self):
        config = {
            'host': '127.0.0.1',  # 默认本地连接
            'user': 'root',
            'password': 'root',
            'port': 3306,  # 默认端口号3306
            'database': 'newstest',
            'charset': 'utf8',  # 默认即为utf8
        }

        try:
            self.sqlconn = pymysql.connect(**config)
        except pymysql.Error as e:
            print('connect fails!{}'.format(e))

    # 处理函数
    def process_item(self, item, spider):
        count = 0
        cur = self.sqlconn.cursor()

        sql_0 = "select NewsID from newstitle WHERE Title = %s, Url = %s"
        params_0 = (item['title'], item['URL'])
        cur.execute(sql_0, params_0)
        print("进入数据库库存储阶段》》》")
        if not cur.fetchall():
            creatTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            Sql1 = 'INSERT INTO newstitle(Title, Category, DescCn, Url, Pic, PicDesc, CreatTime, PublishTime, newsfrom) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
            params1 = (item['title'],item['type'],item['summary'],item['URL'],item['pic'],item['picDesc'],creatTime,item['update'],'CNN')
            cur.execute(Sql1,params1)
            self.sqlconn.commit()
            rows = cur.rowcount
            if rows == 0: raise DropItem("Already in the database.")

            Sql2 = 'select NewsId from newstitle where Title = %s'
            params2 = (item['title'])
            cur.execute(Sql2,params2)
            newsID = cur.fetchall()[0]

            Sql3 = "insert into newstext(NewsID,ImgPath,ImgDesc) values (%s,%s,%s)"
            params3 = (newsID, item['pic'], item['picDesc'])
            cur.execute(Sql3, params3)
            self.sqlconn.commit()

            for para in item['content']:
                count = count+1
                Sql4 = 'INSERT INTO newstext(NewsId, ParaId, Sentence) VALUES (%s, %s, %s)'
                params4 = (newsID,count,para)
                cur.execute(Sql4,params4)
                self.sqlconn.commit()
            return item

    # 断开连接
    def __del__(self):
        self.sqlconn.close()