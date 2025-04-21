# coding: utf-8

import base64
import datetime
import unittest
from urllib.parse import parse_qsl, urlsplit

from mock import Mock, MagicMock, patch

import payjp

from payjp.test.helper import PayjpUnitTestCase

VALID_API_METHODS = ('get', 'post', 'delete')


class GMT1(datetime.tzinfo):

    def utcoffset(self, dt):
        return datetime.timedelta(hours=1)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "Europe/Prague"


class APIHeaderMatcher(object):
    EXP_KEYS = ['X-Payjp-Client-User-Agent', 'User-Agent', 'Authorization']
    METHOD_EXTRA_KEYS = {"post": ["Content-Type"]}

    def __init__(self, api_key=None, extra={}, request_method=None):
        self.request_method = request_method
        if api_key is not None:
            self.api_key = self._encode(api_key)
        else:
            self.api_key = self._encode(payjp.api_key)
        self.extra = extra

    def __eq__(self, other):
        return (self._keys_match(other) and
                self._auth_match(other) and
                self._extra_match(other))

    def _encode(self, api_key):
        return str(
            base64.b64encode(
                bytes(''.join([api_key, ':']), 'utf-8')), 'utf-8')

    def _keys_match(self, other):
        expected_keys = self.EXP_KEYS + list(self.extra.keys())
        if self.request_method is not None and self.request_method in \
                self.METHOD_EXTRA_KEYS:
            expected_keys.extend(self.METHOD_EXTRA_KEYS[self.request_method])

        return (sorted(other.keys()) == sorted(expected_keys))

    def _auth_match(self, other):
        return other['Authorization'] == "Basic %s" % (self.api_key,)

    def _extra_match(self, other):
        for k, v in self.extra.items():
            if other[k] != v:
                return False

        return True


class QueryMatcher(object):
    def __init__(self, expected):
        self.expected = sorted(expected)

    def __eq__(self, other):
        query = urlsplit(other).query or other

        parsed = parse_qsl(query)
        return self.expected == sorted(parsed)


class UrlMatcher(object):
    def __init__(self, expected):
        self.exp_parts = urlsplit(expected)

    def __eq__(self, other):
        other_parts = urlsplit(other)

        for part in ('scheme', 'netloc', 'path', 'fragment'):
            expected = getattr(self.exp_parts, part)
            actual = getattr(other_parts, part)
            if expected != actual:
                print((('Expected %s "%s" but got "%s"') % (
                    part, expected, actual)))
                return False

        q_matcher = QueryMatcher(parse_qsl(self.exp_parts.query))
        return q_matcher == other


class APIRequestorRequestTests(PayjpUnitTestCase):
    ENCODE_INPUTS = {
        'dict': {
            'astring': 'bar',
            'anint': 5,
            'anull': None,
            'adatetime': datetime.datetime(2013, 1, 1, tzinfo=GMT1()),
            'atuple': (1, 2),
            'adict': {'foo': 'bar', 'boz': 5},
            'alist': ['foo', 'bar'],
        },
        'list': [1, 'foo', 'baz'],
        'string': 'boo',
        'unicode': u'\u1234',
        'datetime': datetime.datetime(2013, 1, 1, second=1, tzinfo=GMT1()),
        'none': None,
    }

    ENCODE_EXPECTATIONS = {
        'dict': [
            ('%s[astring]', 'bar'),
            ('%s[anint]', 5),
            ('%s[adatetime]', 1356994800),
            ('%s[adict][foo]', 'bar'),
            ('%s[adict][boz]', 5),
            ('%s[alist][]', 'foo'),
            ('%s[alist][]', 'bar'),
            ('%s[atuple][]', 1),
            ('%s[atuple][]', 2),
        ],
        'list': [
            ('%s[]', 1),
            ('%s[]', 'foo'),
            ('%s[]', 'baz'),
        ],
        'string': [('%s', 'boo')],
        'unicode': [('%s', u'\u1234')],
        'datetime': [('%s', 1356994801)],
        'none': [],
    }

    def setUp(self):
        super(APIRequestorRequestTests, self).setUp()

        self.http_client = Mock(payjp.http_client.HTTPClient)
        self.http_client.name = 'mockclient'

        self.requestor = payjp.api_requestor.APIRequestor(
            client=self.http_client)

    def mock_response(self, return_body, return_code, requestor=None):
        if not requestor:
            requestor = self.requestor

        self.http_client.request = Mock(
            return_value=(return_body, return_code))

    def check_call(self, meth, abs_url=None, headers=None,
                   post_data=None, requestor=None):
        if not abs_url:
            abs_url = 'https://api.pay.jp%s' % (self.valid_path,)
        if not requestor:
            requestor = self.requestor
        if not headers:
            headers = APIHeaderMatcher(request_method=meth)

        self.http_client.request.assert_called_with(
            meth, abs_url, headers, post_data)

    @property
    def valid_path(self):
        return '/foo'

    def encoder_check(self, key):
        stk_key = "my%s" % (key,)

        value = self.ENCODE_INPUTS[key]
        expectation = [(k % (stk_key,), v) for k, v in
                       self.ENCODE_EXPECTATIONS[key]]

        stk = []
        fn = getattr(payjp.api_requestor.APIRequestor, "encode_%s" % (key,))
        fn(stk, stk_key, value)

        if isinstance(value, dict):
            expectation.sort()
            stk.sort()

        self.assertEqual(expectation, stk)

    def _test_encode_naive_datetime(self):
        stk = []

        payjp.api_requestor.APIRequestor.encode_datetime(
            stk, 'test', datetime.datetime(2013, 1, 1))

        # Naive datetimes will encode differently depending on your system
        # local time.  Since we don't know the local time of your system,
        # we just check that naive encodings are within 24 hours of correct.
        self.assertTrue(60 * 60 * 24 > abs(stk[0][1] - 1356994800))

    def test_param_encoding(self):
        self.mock_response('{}', 200)

        self.requestor.request('get', '', self.ENCODE_INPUTS)

        expectation = []
        for type_, values in self.ENCODE_EXPECTATIONS.items():
            expectation.extend([(k % (type_,), str(v)) for k, v in values])

        self.check_call('get', QueryMatcher(expectation))

    def test_dictionary_list_encoding(self):
        params = {
            'foo': {
                '0': {
                    'bar': 'bat',
                }
            }
        }
        encoded = list(payjp.api_requestor._api_encode(params))
        key, value = encoded[0]

        self.assertEqual('foo[0][bar]', key)
        self.assertEqual('bat', value)

    def test_url_construction(self):
        CASES = (
            ('https://api.pay.jp?foo=bar', '', {'foo': 'bar'}),
            ('https://api.pay.jp?foo=bar', '?', {'foo': 'bar'}),
            ('https://api.pay.jp', '', {}),
            (
                'https://api.pay.jp/%20spaced?foo=bar%24&baz=5',
                '/%20spaced?foo=bar%24',
                {'baz': '5'}
            ),
            (
                'https://api.pay.jp?foo=bar&foo=bar',
                '?foo=bar',
                {'foo': 'bar'}
            ),
        )

        for expected, url, params in CASES:
            self.mock_response('{}', 200)

            self.requestor.request('get', url, params)

            self.check_call('get', expected)

    def test_empty_methods(self):
        for meth in VALID_API_METHODS:
            self.mock_response('{}', 200)

            body, key = self.requestor.request(meth, self.valid_path, {})

            if meth == 'post':
                post_data = ''
            else:
                post_data = None

            self.check_call(meth, post_data=post_data)
            self.assertEqual({}, body)

    def test_methods_with_params_and_response(self):
        for meth in VALID_API_METHODS:
            self.mock_response('{"foo": "bar", "baz": 6}', 200)

            params = {
                'alist': [1, 2, 3],
                'adict': {'frobble': 'bits'},
                'adatetime': datetime.datetime(2013, 1, 1, tzinfo=GMT1())
            }
            encoded = ('adict%5Bfrobble%5D=bits&adatetime=1356994800&'
                       'alist%5B%5D=1&alist%5B%5D=2&alist%5B%5D=3')

            body, key = self.requestor.request(meth, self.valid_path,
                                               params)
            self.assertEqual({'foo': 'bar', 'baz': 6}, body)

            if meth == 'post':
                self.check_call(
                    meth,
                    post_data=QueryMatcher(parse_qsl(encoded)))
            else:
                abs_url = "https://api.pay.jp%s?%s" % (
                    self.valid_path, encoded)
                self.check_call(meth, abs_url=UrlMatcher(abs_url))

    def test_uses_headers(self):
        self.mock_response('{}', 200)
        self.requestor.request('get', self.valid_path, {}, {'foo': 'bar'})
        self.check_call('get', headers=APIHeaderMatcher(extra={'foo': 'bar'}))

    def test_uses_instance_key(self):
        key = 'fookey'
        requestor = payjp.api_requestor.APIRequestor(key,
                                                     client=self.http_client)

        self.mock_response('{}', 200, requestor=requestor)

        body, used_key = requestor.request('get', self.valid_path, {})

        self.check_call('get', headers=APIHeaderMatcher(key,
                        request_method='get'), requestor=requestor)
        self.assertEqual(key, used_key)

    def test_passes_api_version(self):
        payjp.api_version = 'fooversion'

        self.mock_response('{}', 200)

        body, key = self.requestor.request('get', self.valid_path, {})

        self.check_call('get', headers=APIHeaderMatcher(
            extra={'Payjp-Version': 'fooversion'}, request_method='get'))

    def test_uses_instance_account(self):
        account = 'acct_foo'
        requestor = payjp.api_requestor.APIRequestor(account=account,
                                                      client=self.http_client)

        self.mock_response('{}', 200, requestor=requestor)

        requestor.request('get', self.valid_path, {})

        self.check_call(
            'get',
            requestor=requestor,
            headers=APIHeaderMatcher(
                extra={'Payjp-Account': account},
                request_method='get'
            ),
        )

    def test_fails_without_api_key(self):
        payjp.api_key = None

        self.assertRaises(payjp.error.AuthenticationError,
                          self.requestor.request,
                          'get', self.valid_path, {})

    def test_not_found(self):
        self.mock_response('{"error": {}}', 404)

        self.assertRaises(payjp.error.InvalidRequestError,
                          self.requestor.request,
                          'get', self.valid_path, {})

    def test_authentication_error(self):
        self.mock_response('{"error": {}}', 401)

        self.assertRaises(payjp.error.AuthenticationError,
                          self.requestor.request,
                          'get', self.valid_path, {})

    def test_card_error(self):
        self.mock_response('{"error": {}}', 402)

        self.assertRaises(payjp.error.CardError,
                          self.requestor.request,
                          'get', self.valid_path, {})

    def test_too_many_request_error(self):
        self.mock_response('{"error": {}}', 429)

        self.assertRaises(payjp.error.APIError,
                          self.requestor.request,
                          'get', self.valid_path, {})

    def test_server_error(self):
        self.mock_response('{"error": {}}', 500)

        self.assertRaises(payjp.error.APIError,
                          self.requestor.request,
                          'get', self.valid_path, {})

    def test_invalid_json(self):
        self.mock_response('{', 200)

        self.assertRaises(payjp.error.APIError,
                          self.requestor.request,
                          'get', self.valid_path, {})

    def test_invalid_method(self):
        self.assertRaises(payjp.error.APIConnectionError,
                          self.requestor.request,
                          'foo', 'bar')

class APIRequestorRetryTest(PayjpUnitTestCase):

    def setUp(self):
        super(APIRequestorRetryTest, self).setUp()
        self.return_values = []
        def return_value_generator():
            for status in self.return_values:
                yield ('{{"error": {{"status": {status}, "message": "test"}}}}'.format(status=status), status, 'sk_live_aaa')
        gen = return_value_generator()
        def request_raw(*args, **kw):
            return next(gen)

        self.request_raw_patch = patch('payjp.api_requestor.APIRequestor.request_raw', request_raw)

        self.requestor = payjp.api_requestor.APIRequestor()

    def test_retry_disabled(self):
        payjp.max_retry = 0
        payjp.retry_initial_delay = 0.1
        self.return_values = [499, 599]  # returns 599 at 2nd try
        with self.request_raw_patch:
            with self.assertRaises(payjp.error.APIError) as error:
                self.requestor.request('get', '/test', {})

            self.assertEqual(error.exception.http_status, 499)

    def test_no_retry(self):
        payjp.max_retry = 2
        payjp.retry_initial_delay = 0.1
        self.return_values = [599, 429, 429, 429]  # returns 599 at first try
        with self.request_raw_patch:
            with self.assertRaises(payjp.error.APIError) as error:
                self.requestor.request('get', '/test', {})

            self.assertEqual(error.exception.http_status, 599)

    def test_full_retry(self):
        """Returns 429 after exceeds max retry"""
        payjp.max_retry = 2
        payjp.retry_initial_delay = 0.1
        self.return_values = [429, 429, 429, 200]  # first try + 2 retries + unexpected 200
        with self.request_raw_patch:
            with self.assertRaises(payjp.error.APIError) as error:
                self.requestor.request('get', '/test', {})

            self.assertEqual(error.exception.http_status, 429)

    def test_success_at_halfway_of_retries(self):
        payjp.max_retry = 5
        payjp.retry_initial_delay = 0.1
        self. return_values = [429, 599, 429, 429, 429]  # returns not 429 status at 2nd try
        with self.request_raw_patch:
            with self.assertRaises(payjp.error.APIError) as error:
                self.requestor.request('get', '/test', {})

            self.assertEqual(error.exception.http_status, 599)


class APIRequestorRetryIntervalTest(PayjpUnitTestCase):

    def setUp(self):
        super(APIRequestorRetryIntervalTest, self).setUp()
        self.requestor = payjp.api_requestor.APIRequestor()

    def test_retry_initial_delay(self):
        payjp.retry_initial_delay = 2
        self.assertTrue(1 <= self.requestor._get_retry_delay(0) <= 2)
        self.assertTrue(2 <= self.requestor._get_retry_delay(1) <= 4)
        self.assertTrue(4 <= self.requestor._get_retry_delay(2) <= 8)
        # cap
        self.assertTrue(16 <= self.requestor._get_retry_delay(4) <= 32)
        self.assertTrue(16 <= self.requestor._get_retry_delay(10) <= 32)




if __name__ == '__main__':
    unittest.main()
