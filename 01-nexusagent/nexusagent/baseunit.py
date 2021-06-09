from abc import ABCMeta, abstractmethod

import requests


class ServiceUnit(metaclass=ABCMeta):
    def __init__(self):
        pass

    #@abstractmethod

    def send_sms(self, m):
        data = {
            'username': 'oapi',
            'password': 'c3Zncy1nN3NhOTdAIyRAXiQK',
            'message': m,
            'arn': 'arn:aws:sns:ap-northeast-1:817865174630:sp',
        }
        r = requests.post('https://ap.lmops.com/oapi/sms/', data=data, timeout=5)
