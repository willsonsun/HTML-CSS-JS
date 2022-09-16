#!/export/servers/python/bin/python3.6
# -*- coding: utf-8 -*-
import os
import time
import requests
import json
from pyaces import pyaces

TDEClient = pyaces.TDEClient
base64_token = "eyJzaWciOiJEelA4dmwvU2lGSUtiNDBka1VCYlZ0NHpEQmRaUVp0RHpKc3BiWjdmRFl6aGpWMjZISkt0b2M3SVF2MUlTOW5DK254RjhkeTNOOGZVRmxUSk5Td1IzM0QxNXY5SCt3V0JvM0h1Mm9oeXcyRlVOUm1NakJsemNDS3c1VmErN3F3YmRYUi9wRlBDRDNtMVNxM0ZpQjcrTXZUL3dpQzZySVdsTFdUbDFHWTZLWGZvT0o2RXYwTmtkYkxCVHIvT1ljdXBGVlJNMlJaRDYvSnhMVUdmaE1wN25CbzU0Mk9neHJ0bThsWmtxZWxXK0NvUWdNRlF1WnlpOXVlQVZIbkJnK1JOS1BORTUvSkNVc2FOVWhnRURYWkt4ZDg3UHJGVVpQSEY5SVN2WjJFMGF2Z2oxcDA4Y3g5emExdXpnSmlGbkxXc1dNYk1yM1hEeVJmM2pMMGs1VlI2RXc9PSIsImRhdGEiOnsiYWN0IjoiY3JlYXRlIiwiZWZmZWN0aXZlIjoxNTQzNDIwODAwMDAwLCJleHBpcmVkIjoxNjA2NTc5MjAwMDAwLCJpZCI6IlltSmxOMkl3TURndE5XWTJaaTAwTjJJeUxUZzBOVFl0TnpZNU9XVXlORFV3T1RReiIsImtleSI6ImlXT2NnaTQ0aXNJU0xVRjI4eUN4S1J0U1FVbTdPK09CQjF3SWxUOUJ4Q1k9Iiwic2VydmljZSI6Im5vcm1hbHRlc3RfZEdKd204TEUiLCJzdHlwZSI6MX0sImV4dGVybmFsRGF0YSI6eyJ6b25lIjoiQ04tMCJ9fQ=="
Aces_Client = TDEClient.getInstance(base64_token,True)

ip_list = ['10.191.10.138', '10.191.132.105']
def get_pass(ip):
    timestamp = int(time.time())
    ticket = "normaltest"
    token = "normaltest"
    data = "ticket="+ticket+"&token="+token+"&timestamp="+str(timestamp)
    sign = Aces_Client.encryptString(data)
    ip = ip
    post_data = [{"ticket":ticket,"token":token,"timestamp":str(timestamp),"sign":str(sign)},ip]
    headers = {'Content-Type':'application/json'}
    url = 'http://g1.jsf.jd.local/com.front.ops.soa.Services.AcesService/cmo/getByIp/30362/jsf'
    req = requests.post(url,data=json.dumps(post_data),headers=headers)
    result = json.loads(req.text)
    result1 = str(result)
    result2 = json.loads(result1)
    result3 = result2['data'][ip]['root']
    result4 = str(result3)
#    aaa =  Aces_Client.isDecryptable(result4)
    passwd = Aces_Client.decryptString(result4)
    print(passwd)
    return passwd

get_pass("10.191.48.45")
