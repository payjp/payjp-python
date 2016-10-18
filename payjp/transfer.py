# coding: utf-8


class Transfer(object):

    resource = 'transfers'

    def __init__(self, requestor):
        self.requestor = requestor

    def list(self, query={}):
        return self.requestor.request('GET', self.resource, query)

    def retrieve(self, id):
        return self.requestor.request('GET', '{}/{}'.format(self.resource, id))

    def charges(self, id):
        return self.requestor.request('GET', '{}/{}/charges'.format(self.resource, id))
