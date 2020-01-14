# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random
from os import path

from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class UserAgentMiddleware(UserAgentMiddleware):

    def __init__(self, settings, user_agent='Mozilla/5.0 (X11; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0'):
        user_agent_list_file = settings.get('USER_AGENT_LIST')
        if path.exists(user_agent_list_file):
            with open(user_agent_list_file, 'r') as f:
                ua = random.choice([line.strip() for line in f])
        else:
            ua = settings.get('USER_AGENT', user_agent)
        super().__init__(user_agent=ua)

    @classmethod
    def from_crawler(cls, crawler):
        obj = cls(crawler.settings)
        crawler.signals.connect(obj.spider_opened,
                                signal=signals.spider_opened)
        return obj
