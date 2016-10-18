# coding: utf-8


class Charge(object):

    resource = 'charges'

    def __init__(self, requestor):
        self.requestor = requestor

    def list(self, query={}):
        return self.requestor.request('GET', self.resource, query)

    def create(self, query={}):
        return self.requestor.request('POST', self.resource, query)

    def retrieve(self, id):
        return self.requestor.request('GET', '{}/{}'.format(self.resource, id))

    def update(self, id, query={}):
        return self.requestor.request('POST', '{}/{}'.format(self.resource, id), query)

    def refund(self, id, query={}):
        return self.requestor.request('POST', '{}/{}/refund'.format(self.resource, id), query)

    def capture(self, id, query={}):
        return self.requestor.request('POST', '{}/{}/capture'.format(self.resource, id), query)
