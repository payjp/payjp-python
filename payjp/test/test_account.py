import unittest

from .base import PayjpTest


class AccountTest(PayjpTest):

    def test_account_retrieve(self):
        self.payjp.accounts.retrieve()

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'accounts')


if __name__ == '__main__':
    unittest.main()
