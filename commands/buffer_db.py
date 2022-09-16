#!/usr/bin/env python
#-*- coding:utf-8 -*-
import mysql.connector
import sys

reload(sys)
sys.setdefaultencoding('UTF-8')

def not_empty(s):
    return s and s.strip()

##buffer创建表
def init_db():
    db = mysql.connector.connect(host='10.8.129.87', port=3306, user='root', password='wx@SH', database='hrdb', charset='utf8')
    cursor = db.cursor()
    create_sql1 = """DROP TABLE IF EXISTS `docker`;"""
    createdb_sql = """CREATE TABLE IF NOT EXISTS `docker` (
                 `id` int(11) NOT NULL AUTO_INCREMENT,
                 `fullName` varchar(45) NOT NULL COMMENT 'fullName',
                 `dataCenter` varchar(45) NOT NULL COMMENT 'dataCenter',
                 `cpuTotal` int(11) NOT NULL COMMENT 'cpuTotal',
                 `cpuUsed` int(11) NOT NULL COMMENT 'cpuTotal',
                 `cpuBuffer` int(11) NOT NULL COMMENT 'cpuBuffer',            
                  PRIMARY KEY (`id`),
                  KEY `id-fullname` (`fullName`)
                  ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARACTER SET=utf8 COMMENT='taskid';
                    """
    cursor.execute(create_sql1)
    cursor.execute(createdb_sql)
    db.close()

def insertdb(fullName, dataCenter, cpuTotal, cpuUsed, cpuBuffer):
    db = mysql.connector.connect(host='10.8.129.87', port=3306, user='root', password='wx@SH', database='hrdb', charset='utf8')
    cursor = db.cursor()
    insert_sql2 = """INSERT IGNORE INTO docker (fullName,dataCenter,cpuTotal,cpuUsed,cpuBuffer)
                    VALUES('%s','%s','%d','%d','%d');
                """ % (fullName, dataCenter, cpuTotal, cpuUsed, cpuBuffer)
    cursor.execute(insert_sql2)
    db.commit()
    db.close()