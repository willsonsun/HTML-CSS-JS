#!/usr/bin/python
#-*- coding:utf-8 -*-
import requests
import json
import mysql.connector
import buffer_db
import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

buffer_db.init_db()

#一级部门使用情况
#查询0级部门和一级部门组织架构
def querydb():
    db = mysql.connector.connect(host='10.8.129.87', port=3306, user='root', password='wx@SH', database='hrdb', charset='utf8')
    cursor = db.cursor()
    query_sql0 = """SELECT organCode,organName FROM organ where organLevel=0;"""
    query_sql1 = """SELECT organCode,organName FROM organ where organLevel=1;"""
    try:
        cursor.execute(query_sql0)
        results0 = cursor.fetchall()
    except IOError:
        print "Error:unable fetch data"
    db.commit()
    try:
        cursor.execute(query_sql1)
        results1 = cursor.fetchall()
    except IOError:
    db.close()
        print "Error:unable fetch data"
    db.commit()
    return results0, results1

response0, response1 = querydb()

Dep0 = response0
Dep1 = response1


combineCodelist=[]
combineNamelist=[]
for i in Dep0:
    firstcode=i[0]
    firstName=i[1]
    for j in Dep1:
        secondcode=j[0]
        secondName=j[1]
        combineCodelist.append(secondcode+'/'+firstcode)
        combineNamelist.append(firstName+'-'+secondName)
neworgan=dict(zip(combineNamelist, combineCodelist))

for fullname, organ in neworgan.items():
    httpurl = "http://10.191.63.188/monitor-jsf/cap/getDeptBuff/%s" % (organ)
    r = requests.get(url=httpurl)
    response = json.loads(r.text)
    print fullname, organ
    print httpurl
    resinfo = response['info']
    if resinfo == None or resinfo == []:
        print "invalid code"
    else:
        for center in resinfo:
            dataCenter = center['dataCenterName']
            cpuTotal = center['cpuTotal']
            cpuUsed = center['cpuUsed']
            cpuBuffer = cpuTotal-cpuUsed
            print fullname, dataCenter, cpuTotal, cpuUsed, cpuBuffer
            buffer_db.insertdb(fullName=fullname, dataCenter=dataCenter, cpuTotal=cpuTotal, cpuUsed=cpuUsed, cpuBuffer=cpuBuffer)
#            with open('dockerbuffer', 'a+') as f:
#                f.write(str(fullname)+'\t'+str(dataCenter)+'\t'+str(cpuTotal)+'\t'+str(cpuUsed)+'\t'+str(cpuBuffer)+'\n')

#二级部门使用情况
#查询一级部门和二级部门组织架构
def querydb1():
    db = mysql.connector.connect(host='10.8.129.87', port=3306, user='root', password='wx@SH', database='hrdb', charset='utf8')
    cursor = db.cursor()
    query_sql1 = """SELECT organCode,organName FROM organ where organLevel=1;"""
    query_sql2 = """SELECT organCode,organName FROM organ where organLevel=2;"""
    try:
        cursor.execute(query_sql1)
        results1 = cursor.fetchall()
    except IOError:
        print "Error:unable fetch data"
    db.commit()
    try:
        cursor.execute(query_sql2)
        results2 = cursor.fetchall()
    except IOError:
        print "Error:unable fetch data"
    db.commit()
    db.close()
    return results1, results2

response1, response2 = querydb1()

Dep1 = response1
Dep2 = response2


combineCodelist=[]
combineNamelist=[]
for i in Dep1:
    firstcode=i[0]
    firstName=i[1]
    for j in Dep2:
        secondcode=j[0]
        secondName=j[1]
        combineCodelist.append(secondcode+'/'+firstcode)
        combineNamelist.append(firstName+'-'+secondName)
neworgan=dict(zip(combineNamelist, combineCodelist))

for fullname, organ in neworgan.items():
    httpurl = "http://10.191.63.188/monitor-jsf/cap/getDeptBuff/%s" % (organ)
    r = requests.get(url=httpurl)
    response = json.loads(r.text)
    print fullname, organ
    print httpurl
    resinfo = response['info']
    if resinfo == None or resinfo == []:
        print "invalid code"
    else:
        for center in resinfo:
            dataCenter = center['dataCenterName']
            cpuTotal = center['cpuTotal']
            cpuUsed = center['cpuUsed']
            cpuBuffer = cpuTotal-cpuUsed
            print fullname, dataCenter, cpuTotal, cpuUsed, cpuBuffer
            buffer_db.insertdb(fullName=fullname, dataCenter=dataCenter, cpuTotal=cpuTotal, cpuUsed=cpuUsed, cpuBuffer=cpuBuffer)
#            with open('dockerbuffer', 'a+') as f:
#                f.write(str(fullname)+'\t'+str(dataCenter)+'\t'+str(cpuTotal)+'\t'+str(cpuUsed)+'\t'+str(cpuBuffer)+'\n')
