# coding: utf-8


class Plan(object):

    resource = 'plans'

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

    def delete(self, id):
        return self.requestor.request('DELETE', '{}/{}'.format(self.resource, id))
