import unittest

from .base import PayjpTest


class PlanTest(PayjpTest):

    def test_plan_list(self):
        self.payjp.plans.list()

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'plans', {})

    def test_plan_create(self):
        params = {
            'amount': 1000,
            'currency': 'jpy',
            'interval': 'month',
            'name': 'premium plan'
        }
        self.payjp.plans.create(params)

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('POST', 'plans', params)

    def test_plan_retrieve(self):
        self.payjp.plans.retrieve('pln_xxx')

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'plans/pln_xxx')

    def test_plan_update(self):
        params = {
            'name': 'super hyper premium plan'
        }
        self.payjp.plans.update('pln_xxx', params)

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('POST', 'plans/pln_xxx', params)

    def test_plan_delete(self):
        self.payjp.plans.delete('pln_xxx')

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('DELETE', 'plans/pln_xxx')


if __name__ == '__main__':
    unittest.main()
