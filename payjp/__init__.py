# coding: utf-8

import json
import platform

import requests

from .version import VERSION
from .account import Account
from .charge import Charge
from .customer import Customer
from .plan import Plan
from .token import Token
from .subscription import Subscription
from .transfer import Transfer
from .event import Event


__all__ = ['Payjp', 'Requestor']


class Payjp:

    def __init__(self, apikey, apibase=None):
        self.apikey = apikey
        self.apibase = apibase if apibase else 'https://api.pay.jp/v1'

        self.requestor = Requestor(self.apikey, self.apibase)

        self.accounts = Account(self.requestor)
        self.charges = Charge(self.requestor)
        self.customers = Customer(self.requestor)
        self.plans = Plan(self.requestor)
        self.tokens = Token(self.requestor)
        self.subscriptions = Subscription(self.requestor)
        self.transfers = Transfer(self.requestor)
        self.events = Event(self.requestor)


class Requestor(object):

    def __init__(self, apikey, apibase):
        self.apikey = apikey
        self.apibase = apibase

    def build_header(self, method):
        ua = {
            'bindings_version': VERSION,
            'lang': 'python',
            'publisher': 'payjp',
            'httplib': 'requests',
        }

        for attr, func in [['lang_version', platform.python_version],
                           ['platform', platform.platform],
                           ['uname', lambda: ' '.join(platform.uname())]]:
            try:
                val = func()
            except Exception as e:
                val = '!! %s' % (e,)
            ua[attr] = val

        headers = {
            'X-Payjp-Client-User-Agent': json.dumps(ua),
            'User-Agent': 'Payjp/v1 PythonBindings/{}'.format(VERSION),
            'httplib': 'requests',
        }

        if method == 'POST':
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        return headers

    def build_url(self, endpoint):
        return '{}/{}'.format(self.apibase, endpoint)

    def build_query(self, query):
        if len(query) > 0:
            for target in {'card', 'metadata'}:
                if target in query and isinstance(query[target], dict):
                    for key, val in query[target].items():
                        query['{}[{}]'.format(target, key)] = val
                    del query['{}'.format(target)]
        return query

    def request(self, method, endpoint, query={}, json={}):
        url = self.build_url(endpoint)
        headers = self.build_header(method)

        kwargs = dict(
            method=method,
            url=url,
            headers=headers,
            auth=(self.apikey, '')
        )

        query = self.build_query(query)

        if method == 'GET':
            kwargs['params'] = query
        elif method == 'POST':
            kwargs['data'] = query

        try:
            res = requests.request(**kwargs)
        except Exception as e:
            raise e

        return res.json()
