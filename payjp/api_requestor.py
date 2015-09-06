# coding: utf-8

import base64
import calendar
import datetime
import json
import logging
import platform
import time

from six import PY3
from six.moves.urllib.parse import urlencode, urlsplit, urlunsplit

import payjp
from . import (
    error,
    http_client,
    util,
    version,
)

logger = logging.getLogger('payjp')


class APIRequestor(object):

    def __init__(self, key=None, client=None, api_base=None, account=None):
        if api_base:
            self.api_base = api_base
        else:
            self.api_base = payjp.api_base
        self.api_key = key
        self.payjp_account = account

        self._client = client or http_client.new_default_http_client()

    def request(self, method, url, params=None, headers=None):
        body, code, my_api_key = self.request_raw(
            method.lower(), url, params, headers)
        response = self.interpret_response(body, code)
        return response, my_api_key

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
        else:
            raise error.APIError(err.get('message'), body, code, response)

    def request_raw(self, method, url, params=None, supplied_headers=None):

        from payjp import api_version

        if self.api_key:
            my_api_key = self.api_key
        else:
            from payjp import api_key
            my_api_key = api_key

        if my_api_key is None:
            raise error.AuthenticationError(
                'No API key provided. (HINT: set your API key using '
                '"payjp.api_key = <API-KEY>"). You can generate API keys '
                'from the Payjp web interface.  See https://docs.pay.jp'
                'for details, or email support@pay.jp if you have any '
                'questions.')

        abs_url = '%s%s' % (self.api_base, url)

        encoded_params = urlencode(list(_api_encode(params or {})))

        if method in ('get', 'delete'):
            if params:
                abs_url = _build_api_url(abs_url, encoded_params)
            post_data = None
        elif method == 'post':
            post_data = encoded_params
        else:
            raise error.APIConnectionError(
                'Unrecognized HTTP method %r.' % (method,))

        ua = {
            'bindings_version': version.VERSION,
            'lang': 'python',
            'publisher': 'payjp',
            'httplib': self._client.name,
        }

        for attr, func in [['lang_version', platform.python_version],
                           ['platform', platform.platform],
                           ['uname', lambda: ' '.join(platform.uname())]]:
            try:
                val = func()
            except Exception as e:
                val = '!! %s' % (e,)
            ua[attr] = val

        if PY3:
            encoded_api_key = str(
                base64.b64encode(
                    bytes(''.join([my_api_key, ':']), 'utf-8')), 'utf-8')
        else:
            encoded_api_key = base64.b64encode(''.join([my_api_key, ':']))

        headers = {
            'X-Payjp-Client-User-Agent': json.dumps(ua),
            'User-Agent': 'Payjp/v1 PythonBindings/%s' % (version.VERSION,),
            'Authorization': 'Basic %s' % encoded_api_key
        }

        if self.payjp_account:
            headers['Payjp-Account'] = self.payjp_account

        if method == 'post':
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        if api_version is not None:
            headers['Payjp-Version'] = api_version

        if supplied_headers is not None:
            for key, value in supplied_headers.items():
                headers[key] = value

        body, code = self._client.request(
            method, abs_url, headers, post_data)

        logger.info('%s %s %d', method.upper(), abs_url, code)
        logger.debug(
            'API request to %s returned (response code, response body) of '
            '(%d, %r)',
            abs_url, code, body)

        return body, code, my_api_key

    def interpret_response(self, body, code):
        try:
            if hasattr(body, 'decode'):
                body = body.decode('utf-8')
            response = json.loads(body)
        except Exception:
            raise error.APIError(
                "Invalid response body from API: %s "
                "(HTTP response code was %d)" % (body, code),
                body, code)
        if not (200 <= code < 300):
            self.handle_api_error(body, code, response)

        return response

def _encode_datetime(dttime):
    if dttime.tzinfo and dttime.tzinfo.utcoffset(dttime) is not None:
        utc_timestamp = calendar.timegm(dttime.utctimetuple())
    else:
        utc_timestamp = time.mktime(dttime.timetuple())

    return int(utc_timestamp)

def _api_encode(data):
    for key, value in data.items():
        key = util.utf8(key)
        if value is None:
            continue
        elif hasattr(value, 'payjp_id'):
            yield (key, value.payjp_id)
        elif isinstance(value, list) or isinstance(value, tuple):
            for subvalue in value:
                yield ("%s[]" % (key,), util.utf8(subvalue))
        elif isinstance(value, dict):
            subdict = dict(('%s[%s]' % (key, subkey), subvalue) for
                           subkey, subvalue in value.items())
            for subkey, subvalue in _api_encode(subdict):
                yield (subkey, subvalue)
        elif isinstance(value, datetime.datetime):
            yield (key, _encode_datetime(value))
        else:
            yield (key, util.utf8(value))

def _build_api_url(url, query):
    scheme, netloc, path, base_query, fragment = urlsplit(url)

    if base_query:
        query = '%s&%s' % (base_query, query)

    return urlunsplit((scheme, netloc, path, query, fragment))

