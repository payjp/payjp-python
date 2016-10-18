# coding: utf-8


class Subscription(object):

    resource = 'subscriptions'

    def __init__(self, requestor):
        self.requestor = requestor

    def list(self, query={}):
        return self.requestor.request('GET', '{}'.format(self.resource), query)

    def create(self, query={}):
        return self.requestor.request('POST', '{}'.format(self.resource), query)

    def retrieve(self, id):
        return self.requestor.request('GET', '{}/{}'.format(self.resource, id))

    def update(self, id, query={}):
        return self.requestor.request('POST', '{}/{}'.format(self.resource, id), query)

    def pause(self, id, query={}):
        return self.requestor.request('POST', '{}/{}/pause'.format(self.resource, id), query)

    def resume(self, id, query={}):
        return self.requestor.request('POST', '{}/{}/resume'.format(self.resource, id), query)

    def cancel(self, id, query={}):
        return self.requestor.request('POST', '{}/{}/cancel'.format(self.resource, id), query)

    def delete(self, id):
        return self.requestor.request('DELETE', '{}/{}'.format(self.resource, id))
