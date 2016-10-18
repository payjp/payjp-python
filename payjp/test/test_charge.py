import unittest

from .base import PayjpTest


class ChargeTest(PayjpTest):

    def test_charge_list(self):
        self.payjp.charges.list()

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'charges', {})

    def test_charge_create(self):
        params = {
            'amount': 1000,
            'currency': 'jpy',
            'card': {
                'number': 4242424242424242,
                'exp_month': 12,
                'exp_year': 2035,
            },
            'capture': False
        }
        self.payjp.charges.create(params)

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('POST', 'charges', params)

    def test_charge_retrieve(self):
        self.payjp.charges.retrieve('ch_xxx')

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'charges/ch_xxx')

    def test_charge_update(self):
        params = {
            'name': 'super hyper premium charge'
        }
        self.payjp.charges.update('ch_xxx', params)

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('POST', 'charges/ch_xxx', params)

    def test_charge_capture(self):
        params = {
            'amount': 1000
        }
        self.payjp.charges.capture('ch_xxx', params)

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('POST', 'charges/ch_xxx/capture', params)

    def test_charge_refund(self):
        params = {
            'refund_reason': 'PPAP'
        }
        self.payjp.charges.refund('ch_xxx', params)

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('POST', 'charges/ch_xxx/refund', params)


if __name__ == '__main__':
    unittest.main()
