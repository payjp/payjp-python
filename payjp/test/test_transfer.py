import unittest

from .base import PayjpTest


class TransferTest(PayjpTest):

    def test_transfer_list(self):
        self.payjp.transfers.list()

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'transfers', {})

    def test_transfer_retrieve(self):
        self.payjp.transfers.retrieve('tra_xxx')

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'transfers/tra_xxx')

    def test_transfer_charges(self):
        self.payjp.transfers.charges('tra_xxx')

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'transfers/tra_xxx/charges')


if __name__ == '__main__':
    unittest.main()
