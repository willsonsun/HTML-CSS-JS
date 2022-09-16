#!/usr/bin/env python
#-*- coding:utf-8 -*-
import requests
import json
import time


with open('/Users/sunwei/PycharmProjects/bvdn/devopsplatform/management/commands/erplist.txt') as file:
    for oneerp in file.readlines():
        oneerp=oneerp.splitlines()[0]
        httpurl="http://monitor.m.jd.com/api/user/get_user_extend_info_by_name?username={}".format(oneerp)
        r=requests.get(url=httpurl)
        rsp=r.text
        rsp=json.loads(rsp)
        FullorganName = rsp['responsebody']['organizationFullName']
        print(oneerp,FullorganName)




