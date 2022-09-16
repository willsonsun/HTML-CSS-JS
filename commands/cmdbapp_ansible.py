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

def get_cmdbip(AppName):
    data = {
        "_source": {
            "includes": [
                "inner_ip"
            ]
        },
        'query': {
            'bool': {
                'must': [
                    {
                        'match_phrase': {
                            'c0_name': "平台业务研发部"
                        }
                    },
                    {
                        'match_phrase': {
                            'app_code': AppName
                        }
                    }
                ]
            }
        },
        'size': '10000',
    }

###时间获取
    results = []
    today = datetime.date.today()
    mdate = int(today.strftime('%Y%m%d'))
    Timelist = ['betacmdb', str(mdate)]
    SearchTime = '_'.join(Timelist)

###ES查询
    AppRes = ES_connect().search(index=SearchTime, doc_type="device", body=data)
    Hits = AppRes['hits']['hits']
    for hit in Hits:
        results.append(hit["_source"]["inner_ip"])
        print(hit["_source"]["inner_ip"])
    return results

def aces_encrypt(datastring):
    url = "http://api.gw.jd.com/anapi/api/passwd/encryption/?apikey=6681c2a975ab45dc86546b901100b39a"
    headers = {'Content-Type':'application/json'}
    postdata = {'passwd': datastring, 'type': 1}
    req = requests.post(url,data=json.dumps(postdata),headers=headers,timeout=1.5)
    result = json.loads(req.text)['data']
    return result

def aces_decrypt(datastring):
    url = "http://api.gw.jd.com/anapi/api/passwd/encryption/?apikey=6681c2a975ab45dc86546b901100b39a"
    headers = {'Content-Type':'application/json'}
    postdata = {'passwd': datastring, 'type': 2}
    req = requests.post(url,data=json.dumps(postdata),headers=headers,timeout=1.5)
    result = json.loads(req.text)['data']
    return result

def get_pass(AppName):
    timestamp = int(time.time())
    ticket = "normaltest"
    token = "normaltest"
    data = "ticket="+ticket+"&token="+token+"&timestamp="+str(timestamp)
    sign = aces_encrypt(data)
    AppName = AppName
    post_data = [{"ticket":ticket,"token":token,"timestamp":str(timestamp),"sign":str(sign)},AppName]
    headers = {'Content-Type':'application/json'}
    url = 'http://g1.jsf.jd.local/com.front.ops.soa.Services.AcesService/cmo/getByAppcode/32270/jsf'
    req = requests.post(url,data=json.dumps(post_data),headers=headers,timeout=1.5)
    result = json.loads(req.text)
    result1 = str(result)
    result2 = json.loads(result1)
    result3 = result2['data']['localhost']['root']
    result4 = str(result3)
    passwd = aces_decrypt(result4)
    return(passwd)


get_cmdbip('front-ops')