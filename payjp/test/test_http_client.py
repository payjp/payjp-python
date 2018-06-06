# coding: utf-8

import unittest

from mock import Mock

import payjp

from payjp.test.helper import PayjpUnitTestCase

VALID_API_METHODS = ('get', 'post', 'delete')


class HttpClientTests(PayjpUnitTestCase):

    def setUp(self):
        super(HttpClientTests, self).setUp()

        self.original_filters = payjp.http_client.warnings.filters[:]
        payjp.http_client.warnings.simplefilter('ignore')

    def tearDown(self):
        payjp.http_client.warnings.filters = self.original_filters

        super(HttpClientTests, self).tearDown()

    def check_default(self, none_libs, expected):
        for lib in none_libs:
            setattr(payjp.http_client, lib, None)

        inst = payjp.http_client.new_default_http_client()

        self.assertTrue(isinstance(inst, expected))

    def test_new_default_http_client_requests(self):
        self.check_default((),
                           payjp.http_client.RequestsClient)


class ClientTestBase():

    @property
    def request_mock(self):
        return self.request_mocks[self.request_client.name]

    @property
    def valid_url(self, path='/foo'):
        return 'https://api.pay.jp%s' % (path,)

    def make_request(self, method, url, headers, post_data):
        client = self.request_client()
        return client.request(method, url, headers, post_data)

    def mock_response(self, body, code):
        raise NotImplementedError(
            'You must implement this in your test subclass')

    def mock_error(self, error):
        raise NotImplementedError(
            'You must implement this in your test subclass')

    def check_call(self, meth, abs_url, headers, params):
        raise NotImplementedError(
            'You must implement this in your test subclass')

    def test_request(self):
        self.mock_response(self.request_mock, '{"foo": "baz"}', 200)

        for meth in VALID_API_METHODS:
            abs_url = self.valid_url
            data = ''

            if meth != 'post':
                abs_url = '%s?%s' % (abs_url, data)
                data = None

            headers = {'my-header': 'header val'}

            body, code = self.make_request(
                meth, abs_url, headers, data)

            self.assertEqual(200, code)
            self.assertEqual('{"foo": "baz"}', body)

            self.check_call(self.request_mock, meth, abs_url,
                            data, headers)

    def test_exception(self):
        self.mock_error(self.request_mock)
        self.assertRaises(payjp.error.APIConnectionError,
                          self.make_request,
                          'get', self.valid_url, {}, None)


class RequestsClientTests(PayjpUnitTestCase, ClientTestBase):
    request_client = payjp.http_client.RequestsClient

    def mock_response(self, mock, body, code):
        result = Mock()
        result.content = body
        result.status_code = code

        mock.request = Mock(return_value=result)

    def mock_error(self, mock):
        mock.exceptions.RequestException = Exception
        mock.request.side_effect = mock.exceptions.RequestException()

    def check_call(self, mock, meth, url, post_data, headers):
        mock.request.assert_called_with(meth, url,
                                        headers=headers,
                                        data=post_data,
                                        timeout=80)


if __name__ == '__main__':
    unittest.main()
