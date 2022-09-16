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

with open('iplist.txt', 'r') as f:
    for line in f.readlines():
        OneIp = line.split()[0]
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=OneIp, port=22, username='root', password=get_pass(OneIp))
            logger.info(OneIp + ' root password is ' + get_pass(OneIp))
            stdin, stdout, stderr = ssh.exec_command('cd /usr/local/src/ && /bin/rm portproc-scan.sh && sed -i "/portproc-scan/d" /var/spool/cron/root && crontab -l -u root')
            logger.info(stdout.read().decode())
            logger.info(stderr.read().decode())
        except:
            logger.info('connect error')
        ssh.close()