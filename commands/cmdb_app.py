#!/export/servers/Python-3.6.4/bin/python3
# -*- coding:utf-8 -*-

import os
import sys
import json
from elasticsearch import Elasticsearch
import datetime
import time
import requests
from pyaces import pyaces

def ES_connect():
    try:
        es = Elasticsearch(hosts='jiesi-cmdb.jd.local:80', http_auth=('jiesi-cmdb','D6A5F61A2E9F3229'), sniffer_timeout=10)
    except Exception as ex:
        print("error:", ex)
    return es

def get_cmdb_app():
    data = {
        'query': {
            'bool': {
                'must': [
                    {
                        'term': {
                            'use_dep': "京东集团-京东零售-平台业务中心-平台业务研发部-创新业务研发部-1号店业务研发组"
                        }
                    },
                    {
                        'match_phrase': {
                            'c0_name': "平台业务研发部"
                        }
                    }
                ]
            }
        },
        'size': '0',
        "aggs": {
            "each_appname" : {
                "terms" : {
                    "field" : "app_code",
                    "size" : "10000"
                }
            }
        }
    }

###时间获取
    results = []
    today = datetime.date.today()
    mdate = int(today.strftime('%Y%m%d'))
    Timelist = ['betacmdb', str(mdate)]
    SearchTime = '_'.join(Timelist)

###ES查询
    AppRes = ES_connect().search(index=SearchTime, doc_type="device", body=data)
    results = AppRes['aggregations']['each_appname']['buckets']
    for i in results:
        print(i['key'])

get_cmdb_app()