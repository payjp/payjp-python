# coding: utf-8

import json
import unittest

import mock

import payjp
from .base import PayjpTest


class TestRequestor(unittest.TestCase):

    def setUp(self):
        super(TestRequestor, self).setUp()
        self.requestor = payjp.Requestor('sk_xxx', 'https://api.pay.jp/v1')

    def test_build_header(self):
        ua_keys = {'bindings_version', 'lang', 'publisher', 'httplib', 'lang_version', 'platform', 'uname'}
        header_keys = {'X-Payjp-Client-User-Agent', 'User-Agent', 'httplib'}

        result = self.requestor.build_header('GET')
        assert set(result.keys()) == header_keys
        assert set(json.loads(result['X-Payjp-Client-User-Agent']).keys()) == ua_keys

        result = self.requestor.build_header('POST')
        header_keys.update({'Content-Type'})
        assert set(result.keys()) == header_keys
        assert set(json.loads(result['X-Payjp-Client-User-Agent']).keys()) == ua_keys

    def test_build_url(self):
        assert self.requestor.build_url('charges/xxx') == '{}/charges/xxx'.format(self.requestor.apibase)

    def test_build_query_plain(self):
        query = {
            'amount': 1000,
            'email': 'example@example.com'
        }

        assert self.requestor.build_query(query) == query

    def test_build_query_card(self):
        query = {
            'amount': 1000,
            'card': {
                'number': 4242424242424242,
                'exp_month': 12,
                'exp_year': 2020,
            }
        }

        result = {
            'amount': 1000,
            'card[number]': 4242424242424242,
            'card[exp_month]': 12,
            'card[exp_year]': 2020,
        }

        assert self.requestor.build_query(query) == result

    def test_build_query_metadata(self):
        query = {
            'amount': 1000,
            'email': 'example@example.com',
            'metadata': {
                'key1': 'val1',
                'key2': 'val2',
            }
        }

        result = {
            'amount': 1000,
            'email': 'example@example.com',
            'metadata[key1]': 'val1',
            'metadata[key2]': 'val2',
        }

        assert self.requestor.build_query(query) == result

        query = {
            'metadata': {
                'key1': 'val1',
                'key1': 'val1',
            }
        }

        result = {
            'metadata[key1]': 'val1',
        }

        assert self.requestor.build_query(query) == result


class TestRequestorRequest(unittest.TestCase):

    def setUp(self):
        super(TestRequestorRequest, self).setUp()
        self._pa = mock.patch('payjp.requests.request')
        self._pa.start()
        self.requestor = payjp.Requestor('sk_xxx', 'https://api.pay.jp/v1')

    def tearDown(self):
        self._pa.stop()

    def test_request(self):
        self.requestor.request('GET', 'charges/xxx', query={'key': 'val'})
        payjp.requests.request.assert_called_once()

        res = payjp.requests.request.call_args_list[0][1]

        assert 'headers' in res
        assert res['url'] == 'https://api.pay.jp/v1/charges/xxx'
        assert res['params'] == {'key': 'val'}
        assert 'data' not in res
        assert res['method'] == 'GET'
        assert res['auth'] == ('sk_xxx', '')

    def test_request_post(self):
        self.requestor.request('POST', 'charges', query={'key': 'val'})
        payjp.requests.request.assert_called_once()

        res = payjp.requests.request.call_args_list[0][1]

        assert 'headers' in res
        assert res['data'] == {'key': 'val'}
        assert 'params' not in res
        assert res['method'] == 'POST'

    def test_request_delete(self):
        self.requestor.request('DELETE', 'charges/xxx')
        payjp.requests.request.assert_called_once()

        res = payjp.requests.request.call_args_list[0][1]

        assert 'headers' in res
        assert 'params' not in res
        assert 'data' not in res
        assert res['method'] == 'DELETE'
