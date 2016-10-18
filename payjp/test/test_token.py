import unittest

from .base import PayjpTest


class TokenTest(PayjpTest):

    def test_token_create(self):
        params = {
            'card': {
                'number': 4242424242424242,
                'exp_month': 12,
                'exp_year': 2035,
            }
        }
        self.payjp.tokens.create(params)

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('POST', 'tokens', params)

    def test_token_retrieve(self):
        self.payjp.tokens.retrieve('tok_xxx')

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'tokens/tok_xxx')


if __name__ == '__main__':
    unittest.main()
