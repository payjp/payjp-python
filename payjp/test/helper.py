import datetime
import json
import os
import random
import re
import string
import unittest

from mock import patch, Mock

from six import string_types

import payjp

NOW = datetime.datetime.now()

DUMMY_CARD = {
    'number': '4242424242424242',
    'exp_month': NOW.month,
    'exp_year': NOW.year + 4
}

DUMMY_CHARGE = {
    'amount': 100,
    'currency': 'jpy',
    'card': DUMMY_CARD
}

DUMMY_PLAN = {
    'amount': 2000,
    'interval': 'month',
    'name': 'Amazing Gold Plan',
    'currency': 'jpy',
    'id': ('payjp-test-gold-' +
           ''.join(random.choice(string.ascii_lowercase) for x in range(10)))
}

DUMMY_TRANSFER = {
    'amount': 400,
    'currency': 'jpy',
    'recipient': 'self'
}

class PayjpTestCase(unittest.TestCase):
    RESTORE_ATTRIBUTES = ('api_version', 'api_key')

    def setUp(self):
        super(PayjpTestCase, self).setUp()

        self._payjp_original_attributes = {}

        for attr in self.RESTORE_ATTRIBUTES:
            self._payjp_original_attributes[attr] = getattr(payjp, attr)

        api_base = os.environ.get('PAYJP_API_BASE')
        if api_base:
            payjp.api_base = api_base
        payjp.api_key = os.environ.get(
            'PAYJP_API_KEY', 'sk_test_c62fade9d045b54cd76d7036')

    def tearDown(self):
        super(PayjpTestCase, self).tearDown()

        for attr in self.RESTORE_ATTRIBUTES:
            setattr(payjp, attr, self._payjp_original_attributes[attr])

    # Python < 2.7 compatibility
    def assertRaisesRegexp(self, exception, regexp, callable, *args, **kwargs):
        try:
            callable(*args, **kwargs)
        except exception as err:
            if regexp is None:
                return True

            if isinstance(regexp, string_types):
                regexp = re.compile(regexp)
            if not regexp.search(str(err)):
                raise self.failureException('"%s" does not match "%s"' %
                                            (regexp.pattern, str(err)))
        else:
            raise self.failureException(
                '%s was not raised' % (exception.__name__,))


class PayjpUnitTestCase(PayjpTestCase):
    REQUEST_LIBRARIES = ['requests']

    def setUp(self):
        super(PayjpUnitTestCase, self).setUp()

        self.request_patchers = {}
        self.request_mocks = {}
        for lib in self.REQUEST_LIBRARIES:
            patcher = patch("payjp.http_client.%s" % (lib,))

            self.request_mocks[lib] = patcher.start()
            self.request_patchers[lib] = patcher

    def tearDown(self):
        super(PayjpUnitTestCase, self).tearDown()

        for patcher in self.request_patchers.values():
            patcher.stop()


class PayjpApiTestCase(PayjpTestCase):

    def setUp(self):
        super(PayjpApiTestCase, self).setUp()

        self.requestor_patcher = patch('payjp.api_requestor.APIRequestor')
        self.requestor_class_mock = self.requestor_patcher.start()
        self.requestor_mock = self.requestor_class_mock.return_value

    def tearDown(self):
        super(PayjpApiTestCase, self).tearDown()

        self.requestor_patcher.stop()

    def mock_response(self, res):
        self.requestor_mock.request = Mock(return_value=(res, 'reskey'))


class MyResource(payjp.resource.APIResource):
    pass


class MyListable(payjp.resource.ListableAPIResource):
    pass


class MyCreatable(payjp.resource.CreateableAPIResource):
    pass


class MyUpdateable(payjp.resource.UpdateableAPIResource):
    pass


class MyDeletable(payjp.resource.DeletableAPIResource):
    pass


class MyComposite(payjp.resource.ListableAPIResource,
                  payjp.resource.CreateableAPIResource,
                  payjp.resource.UpdateableAPIResource,
                  payjp.resource.DeletableAPIResource):
    pass
