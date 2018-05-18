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
from . import error


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


class Requestor:

    def __init__(self, apikey, apibase):
        self.apikey = apikey
        self.apibase = apibase
        # header_type = urlencode or json
        self.header_type = None

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
            'User-Agent': 'Payjp/v2 PythonBindings/{}'.format(VERSION),
            'httplib': 'requests',
        }

        if method == 'POST' and self.header_type == 'urlencode':
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
        if len(query) > 0 and len(json) > 0:
            raise Exception('You can not specify query and json at the same time.')

        url = self.build_url(endpoint)

        if len(query) > 0:
            self.header_type = 'urlencode'
        else:
            self.header_type = 'json'

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

        return self.interpret_response(res)

    def interpret_response(self, response):
        body = response.content
        code = response.status_code
        try:
            r = response.json()
        except Exception:
            raise error.APIError(
                "Invalid response body from API: %s "
                "(HTTP response code was %d)" % (body, code),
                body, code)

        if not (200 <= code < 300):
            self.handle_api_error(body, code, response)

        return r

    def handle_api_error(self, body, code, response):
        try:
            err = response['error']
        except (KeyError, TypeError):
            raise error.APIError(
                "Invalid response object from API: %r (HTTP response code "
                "was %d)" % (body, code),
                body, code, response)

        if code in [400, 404]:
            raise error.InvalidRequestError(
                err.get('message'), err.get('param'), body, code, response)
        elif code == 401:
            raise error.AuthenticationError(
                err.get('message'), body, code, response)
        elif code == 402:
            raise error.CardError(err.get('message'), err.get('param'),
                                  err.get('code'), body, code, response)

        raise error.APIError(err.get('message'), body, code, response)
