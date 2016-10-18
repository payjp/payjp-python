# coding: utf-8


class Account(object):

    resource = 'accounts'

    def __init__(self, requestor):
        self.requestor = requestor

    def retrieve(self):
        return self.requestor.request('GET', '{}'.format(self.resource))
