# coding: utf-8

import json
import pickle
import sys
import time
import datetime
import unittest

import payjp
import payjp.resource

from payjp.test.helper import (
    PayjpUnitTestCase, PayjpApiTestCase,
    MyListable, MyCreatable, MyUpdateable, MyDeletable,
    MyResource, NOW, DUMMY_CARD, DUMMY_CHARGE,
    DUMMY_PLAN)


class PayjpObjectTests(PayjpUnitTestCase):

    def test_initializes_with_parameters(self):
        obj = payjp.resource.PayjpObject(
            'foo', 'bar', myparam=5, yourparam='boo')

        self.assertEqual('foo', obj.id)
        self.assertEqual('bar', obj.api_key)

    def test_access(self):
        obj = payjp.resource.PayjpObject('myid', 'mykey', myparam=5)

        # Empty
        self.assertRaises(AttributeError, getattr, obj, 'myattr')
        self.assertRaises(KeyError, obj.__getitem__, 'myattr')
        self.assertEqual('def', obj.get('myattr', 'def'))
        self.assertEqual(None, obj.get('myattr'))

        # Setters
        obj.myattr = 'myval'
        obj['myitem'] = 'itval'
        self.assertEqual('sdef', obj.setdefault('mydef', 'sdef'))

        # Getters
        self.assertEqual('myval', obj.setdefault('myattr', 'sdef'))
        self.assertEqual('myval', obj.myattr)
        self.assertEqual('myval', obj['myattr'])
        self.assertEqual('myval', obj.get('myattr'))

        self.assertEqual(['id', 'myattr', 'mydef', 'myitem'],
                         sorted(obj.keys()))
        self.assertEqual(['itval', 'myid', 'myval', 'sdef'],
                         sorted(obj.values()))

        # Illegal operations
        self.assertRaises(ValueError, setattr, obj, 'foo', '')
        self.assertRaises(TypeError, obj.__delitem__, 'myattr')

    def test_refresh_from(self):
        obj = payjp.resource.PayjpObject.construct_from({
            'foo': 'bar',
            'trans': 'me',
        }, 'mykey')

        self.assertEqual('mykey', obj.api_key)
        self.assertEqual('bar', obj.foo)
        self.assertEqual('me', obj['trans'])
        self.assertEqual(None, obj.payjp_account)

        obj.refresh_from({
            'foo': 'baz',
            'johnny': 5,
        }, 'key2', payjp_account='acct_foo')

        self.assertEqual(5, obj.johnny)
        self.assertEqual('baz', obj.foo)
        self.assertRaises(AttributeError, getattr, obj, 'trans')
        self.assertEqual('key2', obj.api_key)
        self.assertEqual('acct_foo', obj.payjp_account)

        obj.refresh_from({
            'trans': 4,
            'metadata': {'amount': 42}
        }, 'key2', True)

        self.assertEqual('baz', obj.foo)
        self.assertEqual(4, obj.trans)

    def test_passing_nested_refresh(self):
        obj = payjp.resource.PayjpObject.construct_from({
            'foos': {
                'type': 'list',
                'data': [
                    {'id': 'nested'}
                ],
            }
        }, 'key', payjp_account='acct_foo')

        nested = obj.foos.data[0]

        self.assertEqual('key', obj.api_key)
        self.assertEqual('nested', nested.id)
        self.assertEqual('key', nested.api_key)
        self.assertEqual('acct_foo', nested.payjp_account)

    def check_invoice_data(self, data):
        # Check rough structure
        self.assertEqual(20, len(data.keys()))
        self.assertEqual(3, len(data['lines'].keys()))
        self.assertEqual(0, len(data['lines']['invoiceitems']))
        self.assertEqual(1, len(data['lines']['subscriptions']))

        # Check various data types
        self.assertEqual(1338238728, data['date'])
        self.assertEqual(None, data['next_payment_attempt'])
        self.assertEqual(False, data['livemode'])
        self.assertEqual('month',
                         data['lines']['subscriptions'][0]['plan']['interval'])

    def test_repr(self):
        obj = payjp.resource.PayjpObject(
            'foo', 'bar', myparam=5)

        obj['object'] = u'\u4e00boo\u1f00'

        res = repr(obj)

        if sys.version_info[0] < 3:
            res = unicode(repr(obj), 'utf-8')

        self.assertTrue(u'<PayjpObject \u4e00boo\u1f00' in res)
        self.assertTrue(u'id=foo' in res)

    def test_pickling(self):
        obj = payjp.resource.PayjpObject(
            'foo', 'bar', myparam=5)

        obj['object'] = 'boo'
        obj.refresh_from({'fala': 'lalala'}, api_key='bar', partial=True)

        self.assertEqual('lalala', obj.fala)

        pickled = pickle.dumps(obj)
        newobj = pickle.loads(pickled)

        self.assertEqual('foo', newobj.id)
        self.assertEqual('bar', newobj.api_key)
        self.assertEqual('boo', newobj['object'])
        self.assertEqual('lalala', newobj.fala)


class ListObjectTests(PayjpApiTestCase):

    def setUp(self):
        super(ListObjectTests, self).setUp()

        self.lo = payjp.resource.ListObject.construct_from({
            'id': 'me',
            'url': '/my/path',
        }, 'mykey')

        self.mock_response([{
            'object': 'charge',
            'foo': 'bar',
        }])

    def assertResponse(self, res):
        self.assertTrue(isinstance(res[0], payjp.Charge))
        self.assertEqual('bar', res[0].foo)

    def test_all(self):
        res = self.lo.all(myparam='you')

        self.requestor_mock.request.assert_called_with(
            'get', '/my/path', {'myparam': 'you'}, None)

        self.assertResponse(res)

    def test_create(self):
        res = self.lo.create(myparam='eter')

        self.requestor_mock.request.assert_called_with(
            'post', '/my/path', {'myparam': 'eter'}, None)

        self.assertResponse(res)

    def test_retrieve(self):
        res = self.lo.retrieve('myid', myparam='cow')

        self.requestor_mock.request.assert_called_with(
            'get', '/my/path/myid', {'myparam': 'cow'}, None)

        self.assertResponse(res)


class APIResourceTests(PayjpApiTestCase):

    def test_retrieve_and_refresh(self):
        self.mock_response({
            'id': 'foo2',
            'bobble': 'scrobble',
        })

        res = MyResource.retrieve('foo*', myparam=5)

        url = '/v1/myresources/foo%2A'
        self.requestor_mock.request.assert_called_with(
            'get', url, {'myparam': 5}, None
        )

        self.assertEqual('scrobble', res.bobble)
        self.assertEqual('foo2', res.id)
        self.assertEqual('reskey', res.api_key)

        self.mock_response({
            'frobble': 5,
        })

        res = res.refresh()

        url = '/v1/myresources/foo2'
        self.requestor_mock.request.assert_called_with(
            'get', url, {'myparam': 5}, None
        )

        self.assertEqual(5, res.frobble)
        self.assertRaises(KeyError, res.__getitem__, 'bobble')

    def test_convert_to_payjp_object(self):
        sample = {
            'foo': 'bar',
            'adict': {
                'object': 'charge',
                'id': 42,
                'amount': 7,
            },
            'alist': [
                {
                    'object': 'customer',
                    'name': 'chilango'
                }
            ]
        }

        converted = payjp.resource.convert_to_payjp_object(
            sample, 'akey', None)

        # Types
        self.assertTrue(isinstance(converted, payjp.resource.PayjpObject))
        self.assertTrue(isinstance(converted.adict, payjp.Charge))
        self.assertEqual(1, len(converted.alist))
        self.assertTrue(isinstance(converted.alist[0], payjp.Customer))

        # Values
        self.assertEqual('bar', converted.foo)
        self.assertEqual(42, converted.adict.id)
        self.assertEqual('chilango', converted.alist[0].name)

        # Stripping
        # TODO: We should probably be stripping out this property
        # self.assertRaises(AttributeError, getattr, converted.adict, 'object')


class ListableAPIResourceTests(PayjpApiTestCase):

    def test_all(self):
        self.mock_response([
            {
                'object': 'charge',
                'name': 'jose',
            },
            {
                'object': 'charge',
                'name': 'curly',
            }
        ])

        res = MyListable.all()

        self.requestor_mock.request.assert_called_with(
            'get', '/v1/mylistables', {})

        self.assertEqual(2, len(res))
        self.assertTrue(all(isinstance(obj, payjp.Charge) for obj in res))
        self.assertEqual('jose', res[0].name)
        self.assertEqual('curly', res[1].name)


class CreateableAPIResourceTests(PayjpApiTestCase):

    def test_create(self):
        self.mock_response({
            'object': 'charge',
            'foo': 'bar',
        })

        res = MyCreatable.create()

        self.requestor_mock.request.assert_called_with(
            'post', '/v1/mycreatables', {})

        self.assertTrue(isinstance(res, payjp.Charge))
        self.assertEqual('bar', res.foo)

    def test_idempotent_create(self):
        self.mock_response({
            'object': 'charge',
            'foo': 'bar',
        })

        res = MyCreatable.create()

        self.requestor_mock.request.assert_called_with(
            'post', '/v1/mycreatables', {})

        self.assertTrue(isinstance(res, payjp.Charge))
        self.assertEqual('bar', res.foo)


class UpdateableAPIResourceTests(PayjpApiTestCase):

    def setUp(self):
        super(UpdateableAPIResourceTests, self).setUp()

        self.mock_response({
            'thats': 'it'
        })

        self.obj = MyUpdateable.construct_from({
            'id': 'myid',
            'foo': 'bar',
            'baz': 'boz',
            'metadata': {
                'size': 'l',
                'score': 4,
                'height': 10
            }
        }, 'mykey')

    def checkSave(self):
        self.assertTrue(self.obj is self.obj.save())

        self.assertEqual('it', self.obj.thats)
        # TODO: Should we force id to be retained?
        # self.assertEqual('myid', obj.id)
        self.assertRaises(AttributeError, getattr, self.obj, 'baz')

    def test_idempotent_save(self):
        self.obj.baz = 'updated'
        self.obj.save()

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/myupdateables/myid',
            {
                'metadata': {},
                'baz': 'updated',
            },
            None
        )

    def test_save(self):
        self.obj.baz = 'updated'
        self.obj.other = 'newval'
        self.obj.metadata.size = 'm'
        self.obj.metadata.info = 'a2'
        self.obj.metadata.height = None

        self.checkSave()

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/myupdateables/myid',
            {
                'baz': 'updated',
                'other': 'newval',
                'metadata': {
                    'size': 'm',
                    'info': 'a2',
                    'height': '',
                }
            },
            None
        )

    def test_add_key_to_nested_object(self):
        acct = MyUpdateable.construct_from({
            'id': 'myid',
            'legal_entity': {
                'size': 'l',
                'score': 4,
                'height': 10
            }
        }, 'mykey')

        acct.legal_entity['first_name'] = 'bob'

        self.assertTrue(acct is acct.save())

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/myupdateables/myid',
            {
                'legal_entity': {
                    'first_name': 'bob',
                }
            },
            None
        )

    def test_save_nothing(self):
        acct = MyUpdateable.construct_from({
            'id': 'myid',
            'metadata': {
                'key': 'value',
            }
        }, 'mykey')

        self.assertTrue(acct is acct.save())
        self.assertTrue(self.requestor_mock.request.called)

    def test_replace_nested_object(self):
        acct = MyUpdateable.construct_from({
            'id': 'myid',
            'legal_entity': {
                'last_name': 'smith',
            }
        }, 'mykey')

        acct.legal_entity = {
            'first_name': 'bob',
        }

        self.assertTrue(acct is acct.save())

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/myupdateables/myid',
            {
                'legal_entity': {
                    'first_name': 'bob',
                    'last_name': '',
                }
            },
            None
        )

    def test_array_setting(self):
        acct = MyUpdateable.construct_from({
            'id': 'myid',
            'legal_entity': {}
        }, 'mykey')

        acct.legal_entity.additional_owners = [{'first_name': 'Bob'}]

        self.assertTrue(acct is acct.save())

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/myupdateables/myid',
            {
                'legal_entity': {
                    'additional_owners': [
                        {'first_name': 'Bob'}
                    ]
                }
            },
            None
        )

    def test_array_none(self):
        acct = MyUpdateable.construct_from({
            'id': 'myid',
            'legal_entity': {
                'additional_owners': None,
            }
        }, 'mykey')

        acct.foo = 'bar'

        self.assertTrue(acct is acct.save())

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/myupdateables/myid',
            {
                'foo': 'bar',
                'legal_entity': {},
            },
            None
        )

    def test_array_insertion(self):
        acct = MyUpdateable.construct_from({
            'id': 'myid',
            'legal_entity': {
                'additional_owners': []
            }
        }, 'mykey')

        acct.legal_entity.additional_owners.append({'first_name': 'Bob'})

        self.assertTrue(acct is acct.save())

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/myupdateables/myid',
            {
                'legal_entity': {
                    'additional_owners': {
                        '0': {'first_name': 'Bob'},
                    }
                }
            },
            None
        )

    def test_array_update(self):
        acct = MyUpdateable.construct_from({
            'id': 'myid',
            'legal_entity': {
                'additional_owners': [
                    {'first_name': 'Bob'},
                    {'first_name': 'Jane'}
                ]
            }
        }, 'mykey')

        acct.legal_entity.additional_owners[1].first_name = 'Janet'

        self.assertTrue(acct is acct.save())

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/myupdateables/myid',
            {
                'legal_entity': {
                    'additional_owners': {
                        '0': {},
                        '1': {'first_name': 'Janet'}
                    }
                }
            },
            None
        )

    def test_array_noop(self):
        acct = MyUpdateable.construct_from({
            'id': 'myid',
            'legal_entity': {
                'additional_owners': [{'first_name': 'Bob'}]
            },
            'currencies_supported': ['jpy', 'cad']
        }, 'mykey')

        self.assertTrue(acct is acct.save())

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/myupdateables/myid',
            {
                'legal_entity': {'additional_owners': {'0': {}}}
            },
            None
        )

    def test_hash_noop(self):
        acct = MyUpdateable.construct_from({
            'id': 'myid',
            'legal_entity': {
                'address': {'line1': '1 Two Three'}
            }
        }, 'mykey')

        self.assertTrue(acct is acct.save())

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/myupdateables/myid',
            {'legal_entity': {'address': {}}},
            None
        )

    def test_save_replace_metadata_with_number(self):
        self.obj.baz = 'updated'
        self.obj.other = 'newval'
        self.obj.metadata = 3

        self.checkSave()

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/myupdateables/myid',
            {
                'baz': 'updated',
                'other': 'newval',
                'metadata': 3,
            },
            None
        )

    def test_save_overwrite_metadata(self):
        self.obj.metadata = {}
        self.checkSave()

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/myupdateables/myid',
            {
                'metadata': {
                    'size': '',
                    'score': '',
                    'height': '',
                }
            },
            None
        )

    def test_save_replace_metadata(self):
        self.obj.baz = 'updated'
        self.obj.other = 'newval'
        self.obj.metadata = {
            'size': 'm',
            'info': 'a2',
            'score': 4,
        }

        self.checkSave()

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/myupdateables/myid',
            {
                'baz': 'updated',
                'other': 'newval',
                'metadata': {
                    'size': 'm',
                    'info': 'a2',
                    'height': '',
                    'score': 4,
                }
            },
            None
        )


class DeletableAPIResourceTests(PayjpApiTestCase):

    def test_delete(self):
        self.mock_response({
            'id': 'mid',
            'deleted': True,
        })

        obj = MyDeletable.construct_from({
            'id': 'mid'
        }, 'mykey')

        self.assertTrue(obj is obj.delete())

        self.assertEqual(True, obj.deleted)
        self.assertEqual('mid', obj.id)


class PayjpResourceTest(PayjpApiTestCase):

    def setUp(self):
        super(PayjpResourceTest, self).setUp()
        self.mock_response({})


class ChargeTest(PayjpResourceTest):

    def test_charge_list_all(self):
        payjp.Charge.all(created={'lt': NOW})

        self.requestor_mock.request.assert_called_with(
            'get',
            '/v1/charges',
            {
                'created': {'lt': NOW},
            }
        )

    def test_charge_list_create(self):
        payjp.Charge.create(**DUMMY_CHARGE)

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/charges',
            DUMMY_CHARGE,
        )

    def test_charge_list_retrieve(self):
        payjp.Charge.retrieve('ch_test_id')

        self.requestor_mock.request.assert_called_with(
            'get',
            '/v1/charges/ch_test_id',
            {},
            None
        )

    def test_charge_list_retrieve_with_api_key_and_api_base(self):
        payjp.Charge.retrieve('ch_test_id', api_key='KEY', api_base='BASE')
        self.requestor_class_mock.assert_called_with(key='KEY', api_base='BASE', account=None)
        self.requestor_mock.request.assert_called_with(
            'get',
            '/v1/charges/ch_test_id',
            {},
            None
        )

    def test_create_with_source_param(self):
        payjp.Charge.create(amount=100, currency='jpy',
                             source='btcrcv_test_receiver')

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/charges',
            {
                'amount': 100,
                'currency': 'jpy',
                'source': 'btcrcv_test_receiver'
            },
        )


class AccountTest(PayjpResourceTest):

    def test_retrieve_account(self):
        payjp.Account.retrieve('acct_foo')
        self.requestor_mock.request.assert_called_with(
            'get',
            '/v1/accounts/acct_foo',
            {},
            None
        )

    def test_retrieve_account_with_api_key_and_api_base(self):
        payjp.Account.retrieve('acct_foo', api_key='KEY', api_base='BASE')
        self.requestor_class_mock.assert_called_with(key='KEY', api_base='BASE', account=None)
        self.requestor_mock.request.assert_called_with(
            'get',
            '/v1/accounts/acct_foo',
            {},
            None
        )


class CustomerTest(PayjpResourceTest):

    def test_list_customers(self):
        payjp.Customer.all()
        self.requestor_mock.request.assert_called_with(
            'get',
            '/v1/customers',
            {},
        )

    def test_list_customers_with_api_key_and_api_base(self):
        payjp.Customer.all(api_key='KEY', api_base='BASE')
        self.requestor_class_mock.assert_called_with('KEY', account=None, api_base='BASE')
        self.requestor_mock.request.assert_called_with(
            'get',
            '/v1/customers',
            {},
        )

    def test_create_customer(self):
        payjp.Customer.create(description="foo bar", card=DUMMY_CARD)
        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/customers',
            {
                'description': 'foo bar',
                'card': DUMMY_CARD
            },
        )

    def test_unset_description(self):
        customer = payjp.Customer(id="cus_unset_desc")
        customer.description = "Hey"
        customer.save()

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/customers/cus_unset_desc',
            {
                'description': 'Hey',
            },
            None
        )

    def test_cannot_set_empty_string(self):
        customer = payjp.Customer()
        self.assertRaises(ValueError, setattr, customer, "description", "")

    def test_customer_add_card(self):
        customer = payjp.Customer.construct_from({
            'id': 'cus_add_card',
            'cards': {
                'object': 'list',
                'url': '/v1/customers/cus_add_card/cards',
            },
        }, 'api_key')
        customer.cards.create(card=DUMMY_CARD)

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/customers/cus_add_card/cards',
            {
                'card': DUMMY_CARD,
            },
            None
        )


class TransferTest(PayjpResourceTest):

    def test_list_transfers(self):
        payjp.Transfer.all()
        self.requestor_mock.request.assert_called_with(
            'get',
            '/v1/transfers',
            {}
        )


class CustomerSubscriptionTest(PayjpResourceTest):

    def test_create_customer(self):
        payjp.Customer.create(plan=DUMMY_PLAN['id'], card=DUMMY_CARD)

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/customers',
            {
                'card': DUMMY_CARD,
                'plan': DUMMY_PLAN['id'],
            },
        )
    
    
    def test_list_customer_subscription(self):
        customer = payjp.Customer.construct_from({
            'id': 'cus_foo',
            'subscriptions': {
                'object': 'list',
                'url': '/v1/customers/cus_foo/subscriptions',
            }
        }, 'api_key')
        
        customer.subscriptions.all()
        
        self.requestor_mock.request.assert_called_with(
            'get',
            '/v1/customers/cus_foo/subscriptions',
            {},
            None
        )
    
    def test_retrieve_customer_subscription(self):
        customer = payjp.Customer.construct_from({
            'id': 'cus_foo',
            'subscriptions': {
                'object': 'list',
                'url': '/v1/customers/cus_foo/subscriptions',
            }
        }, 'api_key')

        customer.subscriptions.retrieve('sub_cus')

        self.requestor_mock.request.assert_called_with(
            'get',
            '/v1/customers/cus_foo/subscriptions/sub_cus',
            {},
            None
        )


class SubscriptionTest(PayjpResourceTest):

    def test_create_subscription(self):
        customer = payjp.Customer.construct_from({'id': 'cus_foo',}, 'api_key')
        payjp.Subscription.create(customer=customer.id, plan=DUMMY_PLAN['id'])

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/subscriptions',
            {'customer': customer.id,
            'plan': DUMMY_PLAN['id']},
        )

    def test_delete_subscriptions(self):
        sub = payjp.Subscription.construct_from(
            {'id': "sub_delete",
            'customer': "cus_foo",}
            , 'api_key')
        sub.delete()

        self.requestor_mock.request.assert_called_with(
            'delete',
            '/v1/subscriptions/sub_delete',
            {},
            None
        )

    def test_update_subscription(self):
        sub = payjp.Subscription.construct_from(
            {'id': "sub_update",
            'customer': "cus_foo",
            'plan': 'plan_foo'}
            , 'api_key')
        sub.plan = DUMMY_PLAN['id']
        sub.save()

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/subscriptions/sub_update',
            {
                'plan': DUMMY_PLAN['id'],
            },
            None
        )
    
    def test_pause_subscriptions(self):
        sub = payjp.Subscription.construct_from(
            {'id': "sub_delete",
            'customer': "cus_foo",
            'status': 'active'}
            , 'api_key')
        sub.pause()
        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/subscriptions/sub_delete/pause',
            {},
            None
        )
    
    def test_cancel_subscriptions(self):
        sub = payjp.Subscription.construct_from(
            {'id': "sub_delete",
            'customer': "cus_foo",
            'status': 'active'}
            , 'api_key')
        sub.cancel()
        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/subscriptions/sub_delete/cancel',
            {},
            None
        )


class PlanTest(PayjpResourceTest):

    def test_create_plan(self):
        payjp.Plan.create(**DUMMY_PLAN)

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/plans',
            DUMMY_PLAN,
        )

    def test_delete_plan(self):
        p = payjp.Plan(id="pl_delete")
        p.delete()

        self.requestor_mock.request.assert_called_with(
            'delete',
            '/v1/plans/pl_delete',
            {},
            None
        )

    def test_update_plan(self):
        p = payjp.Plan(id="pl_update")
        p.name = "Plan Name"
        p.save()

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/plans/pl_update',
            {
                'name': 'Plan Name',
            },
            None
        )


class RefundTest(PayjpResourceTest):

    def test_non_recursive_save(self):
        charge = payjp.Charge.construct_from({
            'id': 'ch_nested_update',
            'customer': {
                'object': 'customer',
                'description': 'foo',
            },
            'refunds': {
                'object': 'list',
                'url': '/v1/charges/ch_foo/refunds',
                'data': [{
                    'id': 'ref_123',
                }],
            },
        }, 'api_key')

        charge.customer.description = 'bar'
        charge.refunds.has_more = True
        charge.refunds.data[0].description = 'bar'
        charge.save()

        self.assertTrue(self.requestor_mock.request.called)

    def test_fetch_refund(self):
        charge = payjp.Charge.construct_from({
            'id': 'ch_get_refund',
            'refunds': {
                'object': 'list',
                'url': '/v1/charges/ch_get_refund/refunds',
            }
        }, 'api_key')

        charge.refunds.retrieve("ref_get")

        self.requestor_mock.request.assert_called_with(
            'get',
            '/v1/charges/ch_get_refund/refunds/ref_get',
            {},
            None
        )

    def test_list_refunds(self):
        charge = payjp.Charge.construct_from({
            'id': 'ch_get_refund',
            'refunds': {
                'object': 'list',
                'url': '/v1/charges/ch_get_refund/refunds',
            }
        }, 'api_key')

        charge.refunds.all()

        self.requestor_mock.request.assert_called_with(
            'get',
            '/v1/charges/ch_get_refund/refunds',
            {},
            None
        )


class MetadataTest(PayjpResourceTest):

    def test_noop_metadata(self):
        charge = payjp.Charge(id='ch_foo')
        charge.description = 'test'
        charge.save()

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/charges/ch_foo',
            {
                'description': 'test',
            },
            None
        )

    def test_unset_metadata(self):
        charge = payjp.Charge(id='ch_foo')
        charge.metadata = {}
        charge.save()

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/charges/ch_foo',
            {
                'metadata': {},
            },
            None
        )

    def test_whole_update(self):
        charge = payjp.Charge(id='ch_foo')
        charge.metadata = {'whole': 'update'}
        charge.save()

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/charges/ch_foo',
            {
                'metadata': {'whole': 'update'},
            },
            None
        )

    def test_individual_delete(self):
        charge = payjp.Charge(id='ch_foo')
        charge.metadata = {'whole': None}
        charge.save()

        self.requestor_mock.request.assert_called_with(
            'post',
            '/v1/charges/ch_foo',
            {
                'metadata': {'whole': None},
            },
            None
        )

if __name__ == '__main__':
    unittest.main()
