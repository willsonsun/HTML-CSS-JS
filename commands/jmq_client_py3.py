# -*- coding: utf-8 -*-
# JMQ proxy方式消费 python实现
import os
import requests
import time
import logging
import json
import random
import hashlib

logger = logging.getLogger('jmq')

# 缓存获取到到认证信息，避免重启时总是连接不同的服务器
_jmq_server_file = '.jmq_server'


class JMQClient(object):
    def __init__(self, app, user, password, proxy_url, topic):
        self._proxy_url = proxy_url
        self._app = app
        self._user = user
        self._password = password
        self._topic = topic
        self._headers = {
            "User-agent": "JMQ-Python/0.0.1",
            "Content-Type": "application/json",
            "Accept": "text/plain",
            "Timestamp": str(time.time()),
            "Host": self._proxy_url,
            "Authid": ""}
        self.get_auth()

    def build_data(self, consume_info, exception=None):
        messages = consume_info['messages']
        locations = []
        for msg in messages:
            location = {
                "journalOffset": msg['journalOffset'],
                "queueId": msg['queueId'],
                "queueOffset": msg['queueOffset'],
                "topic": msg['topic']
            }
            locations.append(location)
        data = {
            "topic": consume_info['topic'],
            "app": consume_info['app'],
            "address": consume_info['address'],
            "brokerGroup": consume_info['brokerGroup'],
            "consumerId": consume_info['consumerId'],
            "locations": locations
        }
        if (exception):
            data["exception"] = exception
        return data

    def _invoke_api(self, url, data):
        try:
            response = requests.post(
                url, data=json.dumps(data), headers=self._headers,
                timeout=10000)
            return response.content

        except Exception as e:
            logging.error(
                'Access JMQ API %s with exception %s' % (url, str(e)))
            raise

        finally:
            if 'response' in locals().keys():
                response.close()

    def get_auth(self, retries=3):
        data = {
            "user": self._user,
            "password": self._password,
            "topic": self._topic,
            "app": self._app
        }
        url = "http://" + self._proxy_url + "/1.0/auth"
        logging.debug(
            "app %s, topic %s, url %s" % (data["app"], data["topic"], url))
        retry = 0
        while (retry < retries):
            resData = self._invoke_api(url, data)
            content = json.loads(resData.decode("utf-8"))
            if (content['status']['code'] == 0):
                authid = content['result']['authid']
                servers = content['result']['servers']
                if (not servers or not authid):
                    logging.info((
                        'JMQ auth API get null authid and servers! '
                        'Retry %s ...') % retry)
                    retry = retry + 1
                    time.sleep(1)
                    continue

                server = _load_server()
                if (not server) or not (server in servers):
                    serverIndex = random.randint(0, len(servers) - 1)
                    server = servers[serverIndex]
                _dump_server(server)
                self._server_ip = server
                self._headers["Authid"] = authid
                return

            logging.error(
                'JMQ auth API error: code=%s errMsg=%s! Retry %s...' % (
                    content['status']['code'],
                    content['status']['msg'], retry))
            retry += 1
            time.sleep(1)

        raise Exception("JMQAuthError: Get invalid authid and servers")

    def produce(self, msg_body):
        data = {
            "topic": self._topic,
            "app": self._app,
            "messages": [{
                # 线上的业务ID强烈建议唯一 用来查询归档
                "businessId":
                hashlib.md5(msg_body.encode('utf-8')).hexdigest(),
                "text": msg_body
            }]
        }
        url = "http://" + self._server_ip + "/1.0/produce"
        return self._invoke_api(url, data)

    def receive_messages(self):
        data = {
            "topic": self._topic,
            "app": self._app
        }
        url = "http://" + self._server_ip + "/1.0/consume"
        logger.debug('receive_messages_url: {}'.format(url))
        return self._invoke_api(url, data)

    def ack_message(self, data):
        url = "http://" + self._server_ip + "/1.0/ack"
        logger.debug('ack_message_url: {}'.format(url))
        return self._invoke_api(url, data)

    def retry_message(self, data):
        url = "http://" + self._server_ip + "/1.0/retry"
        return self._invoke_api(url, data)

    def consumer(self):
        while True:
            resp = None
            try:
                resp = self.receive_messages()
                resp = json.loads(resp.decode("utf-8"))
                if resp["status"]["code"] == 2:
                    self.get_auth()
                    resp = self.receive_messages()
                    resp = json.loads(resp)

                content = resp["result"]
                if not content.get('messages'):
                    time.sleep(5)
                    continue

                logger.debug('response message: {}'.format(resp))
                ack_data = self.build_data(content, '')
                self.ack_message(ack_data)
                for msg in resp["result"].get('messages', []):
                    yield msg["text"]

            except Exception as e:
                logger.error(e, exc_info=True)
                if resp:
                    retry_data = self.build_data(content, 'Exception')
                    self.retry_message(retry_data)


def _load_server():
    mode = 'r+'
    # 没有文件创建文件，有文件直接读
    if not os.path.exists(_jmq_server_file):
        mode = 'w+'
    with open(_jmq_server_file, mode) as f:
        return f.read()


def _dump_server(server_ip):
    with open(_jmq_server_file, 'w+') as f:
        return f.write(server_ip)


def _check_consumer():
    jmq_client = JMQClient(
        user="costexcep", app="costexcep", proxy_url="proxy.jmq.jd.com",
        password="7860D1E8", topic="AppProc")

    for msg in jmq_client.consumer():
        print('消费消息：{}'.format(msg))


def _check_producer():
    jmq_client = JMQClient(
        user="costexcep", app="costexcep", proxy_url="proxy.jmq.jd.com",
        password="7860D1E8", topic="AppProc")

    for i in range(10):
        try:
            msg = "第 {} 条消息！".format(i + 1)
            jmq_client.produce(msg)
            print("{} 发送消息: {}".format(str(time.ctime()), msg))

        except Exception as e:
            print(str(time.ctime()) + str(e))


def _real_main():
    _check_producer()
    _check_consumer()


if __name__ == '__main__':
    _real_main()