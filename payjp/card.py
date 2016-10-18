# coding: utf-8


class Card(object):

    resource = 'cards'

    def __init__(self, requestor):
        self.requestor = requestor

    def list(self, customer_id, query={}):
        return self.requestor.request(
            'GET', 'customers/{customer_id}/{resource}'.format(
                customer_id=customer_id,
                resource=self.resource), query)

    def create(self, customer_id, query={}):
        return self.requestor.request(
            'POST', 'customers/{customer_id}/{resource}'.format(
                customer_id=customer_id, resource=self.resource), query)

    def retrieve(self, customer_id, id):
        return self.requestor.request(
            'GET', 'customers/{customer_id}/{resource}/{id}'.format(
                customer_id=customer_id, resource=self.resource, id=id))

    def update(self, customer_id, id, query={}):
        return self.requestor.request(
            'POST', 'customers/{customer_id}/{resource}/{id}'.format(
                customer_id=customer_id, resource=self.resource, id=id), query)

    def delete(self, customer_id, id):
        return self.requestor.request(
            'DELETE', 'customers/{customer_id}/{resource}/{id}'.format(
                customer_id=customer_id, resource=self.resource, id=id))
