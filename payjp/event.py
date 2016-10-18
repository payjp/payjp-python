# coding: utf-8


class Event(object):

    resource = 'events'

    def __init__(self, requestor):
        self.requestor = requestor

    def list(self, query={}):
        return self.requestor.request('GET', self.resource, query)

    def retrieve(self, id):
        return self.requestor.request('GET', '{}/{}'.format(self.resource, id))
