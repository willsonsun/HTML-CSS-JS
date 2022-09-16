from elasticsearch import Elasticsearch
import json
import datetime
import time
import re
import logging


###ES连接
def ES_connect():
    try:
        es = Elasticsearch(hosts='jiesi-app-info.jd.local:80', http_auth=('jiesi-app-info','06F1CA1C6B2293A7'))
    except Exception as ex:
        print("error:", ex)
    return es

def ProcTotalApi(): 
###必要变量字段
    Curtime = '2021-04-21'
    index_time = Curtime.replace('-', '')
    hostinfolist = ['hostinfo', index_time]
    hostinfoindex = '_'.join(hostinfolist)
    dtStart = Curtime + ' ' + '02:00:00'
    dtEnd = Curtime + ' ' + '02:20:00'
    timeArray1 = time.strptime(dtStart, "%Y-%m-%d %H:%M:%S")
    timeArray2 = time.strptime(dtEnd, "%Y-%m-%d %H:%M:%S")
    TimeStampStart = int(time.mktime(timeArray1))
    TimeStampStop = int(time.mktime(timeArray2))

###定义ES查询结构体
    DataShow = {   
        "_source": {
            "includes": [
                "HostIp",
                "ProcCmdLine",
            ]
        },
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "datetime": {
                                "gt": TimeStampStart,
                                "lt": TimeStampStop
                            }
                        }
                    },
                    {
                        "match_phrase": {
                            "CmdLineText": "zoo.cfg"
                        }
                    }
                ]
            }
        },
        "size": "10000"
    }

###统计总进程
    TotalResult = ES_connect().search(index=hostinfoindex, doc_type="hostinfo", body=DataShow)
    print(TotalResult)
    zkinfo = TotalResult['hits']['hits']
    with open('/Users/sunwei/PycharmProjects/bvdn/devopsplatform/management/commands/zkinfo.txt','w+') as f:
        for one in zkinfo:
            f.write(one['_source']['HostIp'] + '|' + one['_source']['ProcCmdLine'] + '\n')    



    # applist = TotalResult['aggregations']['each_hostip']['buckets']
    # with open('/Users/sunwei/PycharmProjects/bvdn/devopsplatform/management/commands/iplist.txt','a+') as f:
    #     for one in applist:
    #         f.write(one['key'] + '\n')

ProcTotalApi()