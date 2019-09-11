# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from scrapy.utils.project import get_project_settings

from jd.items import *


class JdPipeline(object):
    def open_spider(self, spider):
        # 建立数据库连接， 获取数据
        settings = get_project_settings()
        db_user = settings.get("DB_USER")
        db_password = settings.get("DB_PASSWORD")
        db_host = settings.get("DB_HOST")
        db_database = settings.get("DB_DATABASE")
        self.conn = pymysql.connect(user=db_user, password=db_password, host=db_host,
                                    database=db_database, )

        print(self.conn)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):

        if isinstance(item, JdItem):
            # 执行插入代码
            item = dict(item)
            columns = (", ").join(list(item.keys()))
            values = (", ").join(["'%s'"] * len(item.values()))
            sql = f"insert into goods({columns}) values ({values})" % tuple([data for data in item.values()])
            try:
                self.cursor.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()

        elif isinstance(item ,  Message):
            item = dict(item)
            columns = (", ").join(list(item.keys()))
            values = (", ").join(["'%s'"] * len(item.values()))
            sql = f"insert into message({columns}) values ({values})" % tuple([data for data in item.values()])
            try:
                self.cursor.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()

        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()
