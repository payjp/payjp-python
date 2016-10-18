import unittest

import mock

import payjp


class PayjpTest(unittest.TestCase):

    def setUp(self):
        super(PayjpTest, self).setUp()
        self._pa = mock.patch('payjp.Requestor.request')
        self._pa.start()
        self.payjp = payjp.Payjp('sk_xxx', 'https://api.pay.jp/v1')

    def tearDown(self):
        self._pa.stop()