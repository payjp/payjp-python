import unittest

from .base import PayjpTest


class CustomerTest(PayjpTest):

    def test_customer_list(self):
        self.payjp.customers.list()

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'customers', {})

    def test_customer_create(self):
        params = {
            'email': 'payjp-python@example.com'
        }
        self.payjp.customers.create(params)

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('POST', 'customers', params)

    def test_customer_retrieve(self):
        self.payjp.customers.retrieve('cus_xxx')

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'customers/cus_xxx')

    def test_customer_update(self):
        params = {
            'email': 'payjp-python-updated@example.com'
        }
        self.payjp.customers.update('cus_xxx', params)

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('POST', 'customers/cus_xxx', params)

    def test_customer_delete(self):
        self.payjp.customers.delete('cus_xxx')

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('DELETE', 'customers/cus_xxx')


if __name__ == '__main__':
    unittest.main()
