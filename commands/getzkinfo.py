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
import logging
import paramiko
import csv

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = logging.FileHandler(filename='output.log', mode='a')
formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(module)s - %(message)s')
handler.setFormatter(formater)
logger.addHandler(handler)


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

def get_pass(IpAddr):
    timestamp = int(time.time())
    ticket = "normaltest"
    token = "normaltest"
    data = "ticket="+ticket+"&token="+token+"&timestamp="+str(timestamp)
    sign = aces_encrypt(data)
    IpName = IpAddr
    post_data = [{"ticket":ticket,"token":token,"timestamp":str(timestamp),"sign":str(sign)},IpName]
    headers = {'Content-Type':'application/json'}
    url = 'http://g1.jsf.jd.local/com.front.ops.soa.Services.AcesService/cmo/getByIp/30362/jsf'
    req = requests.post(url,data=json.dumps(post_data),headers=headers,timeout=1.5)
    result = json.loads(req.text)
    result1 = str(result)
    result2 = json.loads(result1)
    result3 = result2['data'][IpName]['root']
    result4 = str(result3)
    passwd = aces_decrypt(result4)
    return(passwd)

def SearchCmdb(hostip):
    CmdbEs = Elasticsearch(hosts='jiesi-cmdb.jd.local:80', http_auth=('jiesi-cmdb','D6A5F61A2E9F3229'))
    curtime = "20210421"
    cmdblist = ['betacmdb', curtime]
    cmdbesindex = '_'.join(cmdblist)

    SearchCmdb = {
    "_source": {
        "includes": [
            "app_code",
            "use_dep"
        ]
    },
    'query': {
        'bool': {
            'must': [{
                'term': {
                    'inner_ip': hostip
                }
            }]
        }
    },
    'size': '1',
    }
    hostcmdbres = CmdbEs.search(index=cmdbesindex, doc_type="device", body=SearchCmdb)['hits']['hits'][0]["_source"]
    return hostcmdbres



with open('newzkinfo.txt', 'r') as f:
    for line in f.readlines():
        DockerIp = line.split()[0]
        ZkConf = line.split()[1]
        RemoteCommand1 = "cat {}|grep -w server|awk -F= '{{print $2}}'|awk -F: '{{print $1}}'".format(ZkConf)
        RemoteCommand2 = "cat {}|grep clientPort|egrep -v '^#'|awk -F= '{{print $2}}'".format(ZkConf)
        try:
            trans = paramiko.Transport((DockerIp, 22))
            trans.connect(username='root', password=get_pass(DockerIp))
            ssh = paramiko.SSHClient()
            ssh._transport = trans
            # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            stdin, stdout, stderr = ssh.exec_command(RemoteCommand1)
            Command1Stdout = stdout.read().decode()
            stdin, stdout, stderr = ssh.exec_command(RemoteCommand2)
            Command2Stdout = stdout.read().decode()
            IpAppcode = SearchCmdb(DockerIp)['app_code']
            IpDep = SearchCmdb(DockerIp)['use_dep']
            with open('zk.csv', 'w+') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([DockerIp,IpAppcode,IpDep,Command2Stdout,Command1Stdout])
            print(DockerIp,IpAppcode,IpDep,Command2Stdout,Command1Stdout)
        except:
            print('connect error')
        trans.close()