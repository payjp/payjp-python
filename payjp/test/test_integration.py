# coding: utf-8

import unittest
import payjp

from six import string_types

from payjp.test.helper import (PayjpTestCase, NOW, DUMMY_CARD)


class AuthenticationErrorTest(PayjpTestCase):

    def test_invalid_credentials(self):
        key = payjp.api_key
        try:
            payjp.api_key = 'invalid'
            payjp.Customer.create()
        except payjp.error.AuthenticationError as e:
            self.assertEqual(401, e.http_status)
            self.assertTrue(isinstance(e.http_body, string_types))
            self.assertTrue(isinstance(e.json_body, dict))
        finally:
            payjp.api_key = key


class CardErrorTest(PayjpTestCase):

    def test_expired_card_props(self):
        EXPIRED_CARD = DUMMY_CARD.copy()
        EXPIRED_CARD['exp_month'] = NOW.month - 2
        EXPIRED_CARD['exp_year'] = NOW.year - 2
        try:
            payjp.Charge.create(amount=100, currency='jpy', card=EXPIRED_CARD)
        except payjp.error.CardError as e:
            self.assertEqual(402, e.http_status)
            self.assertTrue(isinstance(e.http_body, string_types))
            self.assertTrue(isinstance(e.json_body, dict))


class InvalidRequestErrorTest(PayjpTestCase):

    def test_nonexistent_object(self):
        try:
            payjp.Charge.retrieve('invalid')
        except payjp.error.InvalidRequestError as e:
            self.assertEqual(404, e.http_status)
            self.assertTrue(isinstance(e.http_body, string_types))
            self.assertTrue(isinstance(e.json_body, dict))

    def test_invalid_data(self):
        try:
            payjp.Charge.create()
        except payjp.error.InvalidRequestError as e:
            self.assertEqual(400, e.http_status)
            self.assertTrue(isinstance(e.http_body, string_types))
            self.assertTrue(isinstance(e.json_body, dict))


if __name__ == '__main__':
    unittest.main()
