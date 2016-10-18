# coding: utf-8

from .card import Card


class CustomerSubscription(object):

    resource = 'subscriptions'

    def __init__(self, requestor):
        self.requestor = requestor

    def list(self, customer_id, query={}):
        return self.requestor.request('GET', 'customers/{customer_id}/{resource}'.format(
            customer_id=customer_id, resource=self.resource), query)

    def retrieve(self, customer_id, id):
        return self.requestor.request('GET', 'customers/{customer_id}/{resource}/{id}'.format(
            customer_id=customer_id, resource=self.resource, id=id))


class Customer(object):

    resource = 'customers'

    def __init__(self, requestor):
        self.requestor = requestor
        self.cards = Card(self.requestor)
        self.subscriptions = CustomerSubscription(self.requestor)

    def list(self, query={}):
        return self.requestor.request('GET', '{}'.format(self.resource), query)

    def create(self, query={}):
        return self.requestor.request('POST', '{}'.format(self.resource), query)

    def retrieve(self, id):
        return self.requestor.request('GET', '{}/{}'.format(self.resource, id))

    def update(self, id, query={}):
        return self.requestor.request('POST', '{}/{}'.format(self.resource, id), query)

    def delete(self, id):
        return self.requestor.request('DELETE', '{}/{}'.format(self.resource, id))
