# coding: utf-8


class Token(object):

    resource = 'tokens'

    def __init__(self, requestor):
        self.requestor = requestor

    def create(self, query={}):
        return self.requestor.request('POST', self.resource, query)

    def retrieve(self, id):
        return self.requestor.request('GET', '{}/{}'.format(self.resource, id))
