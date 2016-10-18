import unittest

from .base import PayjpTest


class SubscriptionTest(PayjpTest):

    def test_subscription_list(self):
        self.payjp.subscriptions.list()

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'subscriptions', {})

    def test_subscription_create(self):
        params = {
            'email': 'payjp-python@example.com'
        }
        self.payjp.subscriptions.create(params)

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('POST', 'subscriptions', params)

    def test_subscription_retrieve(self):
        self.payjp.subscriptions.retrieve('sub_xxx')

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'subscriptions/sub_xxx')

    def test_subscription_update(self):
        params = {
            'email': 'payjp-python-updated@example.com'
        }
        self.payjp.subscriptions.update('sub_xxx', params)

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('POST', 'subscriptions/sub_xxx', params)

    def test_subscription_delete(self):
        self.payjp.subscriptions.delete('sub_xxx')

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('DELETE', 'subscriptions/sub_xxx')

    def test_subscription_pause(self):
        self.payjp.subscriptions.pause('sub_xxx')

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('POST', 'subscriptions/sub_xxx/pause', {})

    def test_subscription_resume(self):
        self.payjp.subscriptions.resume('sub_xxx')

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('POST', 'subscriptions/sub_xxx/resume', {})

    def test_subscription_cancel(self):
        self.payjp.subscriptions.cancel('sub_xxx')

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('POST', 'subscriptions/sub_xxx/cancel', {})

    def test_customer_subscription_list(self):
        self.payjp.customers.subscriptions.list('cus_xxx')

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'customers/cus_xxx/subscriptions', {})

    def test_customer_subscription_retrieve(self):
        self.payjp.customers.subscriptions.retrieve('cus_xxx', 'sub_xxx')

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'customers/cus_xxx/subscriptions/sub_xxx')


if __name__ == '__main__':
    unittest.main()
