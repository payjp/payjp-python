import unittest

from .base import PayjpTest


class EventTest(PayjpTest):

    def test_event_list(self):
        self.payjp.events.list()

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'events', {})

    def test_event_retrieve(self):
        self.payjp.events.retrieve('evnt_xxx')

        self.payjp.requestor.request.assert_called_once()
        self.payjp.requestor.request.assert_called_with('GET', 'events/evnt_xxx')


if __name__ == '__main__':
    unittest.main()
