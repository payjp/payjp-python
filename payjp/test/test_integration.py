# coding: utf-8

import unittest

import payjp
from payjp.test.helper import DUMMY_CARD, NOW, PayjpTestCase


class AuthenticationErrorTest(PayjpTestCase):
    def test_invalid_credentials(self):
        key = payjp.api_key
        try:
            payjp.api_key = "invalid"
            payjp.Customer.create()
        except payjp.error.AuthenticationError as e:
            self.assertEqual(401, e.http_status)
            self.assertTrue(isinstance(e.http_body, str))
            self.assertTrue(isinstance(e.json_body, dict))
        finally:
            payjp.api_key = key


class CardErrorTest(PayjpTestCase):
    def test_invalid_card_props(self):
        EXPIRED_CARD = DUMMY_CARD.copy()
        EXPIRED_CARD["exp_month"] = NOW.month
        EXPIRED_CARD["exp_year"] = NOW.year
        try:
            payjp.Charge.create(amount=100, currency="jpy", card=EXPIRED_CARD)
        except payjp.error.InvalidRequestError as e:
            self.assertEqual(400, e.http_status)
            self.assertTrue(isinstance(e.http_body, str))
            self.assertTrue(isinstance(e.json_body, dict))


class InvalidRequestErrorTest(PayjpTestCase):
    def test_nonexistent_object(self):
        try:
            payjp.Charge.retrieve("invalid")
        except payjp.error.InvalidRequestError as e:
            self.assertEqual(404, e.http_status)
            self.assertTrue(isinstance(e.http_body, str))
            self.assertTrue(isinstance(e.json_body, dict))

    def test_invalid_data(self):
        try:
            payjp.Charge.create()
        except payjp.error.InvalidRequestError as e:
            self.assertEqual(400, e.http_status)
            self.assertTrue(isinstance(e.http_body, str))
            self.assertTrue(isinstance(e.json_body, dict))


if __name__ == "__main__":
    unittest.main()
