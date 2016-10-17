# coding: utf-8

import datetime
import json
import logging
import sys

from six import string_types
from six.moves.urllib.parse import quote_plus

from . import (
    api_requestor,
    error,
    util,
)

logger = logging.getLogger('payjp')

def convert_to_payjp_object(resp, api_key, account, api_base=None):
    types = {'account': Account, 'card': Card,
             'charge': Charge, 'customer': Customer,
             'event': Event, 'plan': Plan,
             'subscription': Subscription, 'token': Token,
             'transfer': Transfer, 'list': ListObject}

    if isinstance(resp, list):
        return [convert_to_payjp_object(i, api_key, account, api_base) for i in resp]
    elif isinstance(resp, dict) and not isinstance(resp, PayjpObject):
        resp = resp.copy()
        klass_name = resp.get('object')
        if isinstance(klass_name, string_types):
            klass = types.get(klass_name, PayjpObject)
        else:
            klass = PayjpObject
        return klass.construct_from(resp, api_key, payjp_account=account, api_base=api_base)
    else:
        return resp

def _compute_diff(current, previous):
    if isinstance(current, dict):
        previous = previous or {}
        diff = current.copy()
        for key in set(previous.keys()) - set(diff.keys()):
            diff[key] = ""
        return diff
    return current if current is not None else ""

def _serialize_list(array, previous):
    array = array or []
    previous = previous or []
    params = {}

    for i, v in enumerate(array):
        previous_item = previous[i] if len(previous) > i else None
        if hasattr(v, 'serialize'):
            params[str(i)] = v.serialize(previous_item)
        else:
            params[str(i)] = _compute_diff(v, previous_item)

    return params


class PayjpObject(dict):

    def __init__(self, id=None, api_key=None, payjp_account=None, api_base=None, **kwargs):
        super(PayjpObject, self).__init__()

        self._unsaved_values = set()
        self._transient_values = set()

        self._retrieve_params = kwargs
        self._previous = None
        self._api_base = api_base

        object.__setattr__(self, 'api_key', api_key)
        object.__setattr__(self, 'payjp_account', payjp_account)

        if id:
            self['id'] = id

    def __setattr__(self, k, v):
        if k[0] == '_' or k in self.__dict__:
            return super(PayjpObject, self).__setattr__(k, v)
        else:
            self[k] = v

    def __getattr__(self, k):
        if k[0] == '_':
            raise AttributeError(k)

        try:
            return self[k]
        except KeyError as err:
            raise AttributeError(*err.args)

    def __setitem__(self, k, v):
        if v == "":
            raise ValueError(
                "You cannot set %s to an empty string. "
                "We interpret empty strings as None in requests."
                "You may set %s.%s = None to delete the property" % (
                    k, str(self), k))

        super(PayjpObject, self).__setitem__(k, v)

        # Allows for unpickling in Python 3.x
        if not hasattr(self, '_unsaved_values'):
            self._unsaved_values = set()

        self._unsaved_values.add(k)

    def __getitem__(self, k):
        try:
            return super(PayjpObject, self).__getitem__(k)
        except KeyError as err:
            if k in self._transient_values:
                raise KeyError(
                    "%r.  HINT: The %r attribute was set in the past."
                    "It was then wiped when refreshing the object with "
                    "the result returned by PAY.JP's API, probably as a "
                    "result of a save().  The attributes currently "
                    "available on this object are: %s" %
                    (k, k, ', '.join(self.keys())))
            else:
                raise err

    def __delitem__(self, k):
        raise TypeError(
            "You cannot delete attributes on a PayjpObject. "
            "To unset a property, set it to None.")

    @classmethod
    def construct_from(cls, values, key, payjp_account=None, api_base=None):
        instance = cls(values.get('id'), api_key=key,
                       payjp_account=payjp_account)
        instance.refresh_from(values, api_key=key,
                              payjp_account=payjp_account,
                              api_base=api_base)
        return instance

    def refresh_from(self, values, api_key=None, partial=False,
                     payjp_account=None, api_base=None):
        self.api_key = api_key or getattr(values, 'api_key', None)
        self.payjp_account = \
            payjp_account or getattr(values, 'payjp_account', None)
        if self.api_base is not None:
            self._api_base = api_base

        # Wipe old state before setting new.  This is useful for e.g.
        # updating a customer, where there is no persistent card
        # parameter.  Mark those values which don't persist as transient
        if partial:
            self._unsaved_values = (self._unsaved_values - set(values))
        else:
            removed = set(self.keys()) - set(values)
            self._transient_values = self._transient_values | removed
            self._unsaved_values = set()
            self.clear()

        self._transient_values = self._transient_values - set(values)

        for k, v in values.items():
            super(PayjpObject, self).__setitem__(
                k, convert_to_payjp_object(v, api_key, payjp_account, api_base))

        self._previous = values

    def serialize(self, previous):
        params = {}
        unsaved_keys = self._unsaved_values or set()
        previous = previous or self._previous or {}

        for k, v in self.items():
            if k == 'id' or (isinstance(k, str) and k.startswith('_')):
                continue
            elif isinstance(v, APIResource):
                continue
            elif hasattr(v, 'serialize'):
                params[k] = v.serialize(previous.get(k, None))
            elif k in unsaved_keys:
                params[k] = _compute_diff(v, previous.get(k, None))
            elif k == 'additional_owners' and v is not None:
                params[k] = _serialize_list(v, previous.get(k, None))

        return params

    def api_base(self):
        return self._api_base

    def request(self, method, url, params=None, headers=None):
        if params is None:
            params = self._retrieve_params
        requestor = api_requestor.APIRequestor(
            key=self.api_key, api_base=self.api_base(),
            account=self.payjp_account)
        response, api_key = requestor.request(method, url, params, headers)

        return convert_to_payjp_object(response, api_key, self.payjp_account, self.api_base())

    def __repr__(self):
        ident_parts = [type(self).__name__]

        if isinstance(self.get('object'), string_types):
            ident_parts.append(self.get('object'))

        if isinstance(self.get('id'), string_types):
            ident_parts.append('id=%s' % (self.get('id'),))

        unicode_repr = '<%s at %s> JSON: %s' % (
            ' '.join(ident_parts), hex(id(self)), str(self))

        if sys.version_info[0] < 3:
            return unicode_repr.encode('utf-8')
        else:
            return unicode_repr

    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2)


class ListObject(PayjpObject):

    def all(self, **params):
        return self.request('get', self['url'], params)

    def create(self, **params):
        # TODO divide into another parent class
        if hasattr(self, 'object') and self.object == 'list' and \
                hasattr(self, 'count') and self.count > 0 and \
                isinstance(self.data[0], Subscription):
                    raise NotImplementedError(
                        "Can't create a subscription via customer object. "
                        "Use payjp.Subscription.create({'customer_id'}) instead.")
        return self.request('post', self['url'], params)

    def retrieve(self, id, **params):
        base = self.get('url')
        id = util.utf8(id)
        extn = quote_plus(id)
        url = "%s/%s" % (base, extn)

        return self.request('get', url, params)


class APIResource(PayjpObject):

    @classmethod
    def class_name(cls):
        return str(quote_plus(cls.__name__.lower()))

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return '/v1/{0}s'.format(cls_name)

    def instance_url(self):
        id = self.get('id')
        if not id:
            raise error.InvalidRequestError

        base = self.class_url()
        ext = quote_plus(id)
        return '{0}/{1}'.format(base, ext)

    @classmethod
    def retrieve(cls, id, api_key=None, payjp_account=None, api_base=None, **kwargs):
        instance = cls(id, api_key, payjp_account, api_base, **kwargs)
        instance.refresh()
        return instance

    def refresh(self):
        self.refresh_from(self.request('get', self.instance_url()))
        return self


class ListableAPIResource(APIResource):

    @classmethod
    def all(cls, api_key=None, payjp_account=None, api_base=None, **params):
        requestor = api_requestor.APIRequestor(api_key, account=payjp_account, api_base=api_base)
        url = cls.class_url()
        response, api_key = requestor.request('get', url, params)
        return convert_to_payjp_object(response, api_key, payjp_account, api_base)


class CreateableAPIResource(APIResource):

    @classmethod
    def create(cls, api_key=None, payjp_account=None, **params):
        requestor = api_requestor.APIRequestor(api_key, account=payjp_account)
        url = cls.class_url()
        response, api_key = requestor.request('post', url, params)
        return convert_to_payjp_object(response, api_key, payjp_account)


class UpdateableAPIResource(APIResource):

    def save(self):
        updated_params = self.serialize(None)

        if updated_params:
            self.refresh_from(self.request('post', self.instance_url(),
                                           updated_params))
        else:
            logger.debug("Trying to save already saved object %r", self)
        return self


class DeletableAPIResource(APIResource):

    def delete(self, **params):
        self.refresh_from(self.request('delete', self.instance_url(), params))
        return self

# resources

class Token(CreateableAPIResource):
    pass


class Charge(CreateableAPIResource, ListableAPIResource,
             UpdateableAPIResource):

    def capture(self, **kwargs):
        url = self.instance_url() + '/capture'
        self.refresh_from(self.request('post', url, kwargs))
        return self

    def refund(self, **kwargs):
        url = self.instance_url() + '/refund'
        self.refresh_from(self.request('post', url, kwargs))
        return self


class Event(ListableAPIResource):
    pass


class Customer(CreateableAPIResource, UpdateableAPIResource,
               ListableAPIResource, DeletableAPIResource):

    def charges(self, **params):
        params['customer'] = self.id
        charges = Charge.all(self.api_key, params)
        return charges


class Plan(CreateableAPIResource, DeletableAPIResource,
           UpdateableAPIResource, ListableAPIResource):
    pass


class Account(APIResource):

    @classmethod
    def retrieve(cls, id=None, api_key=None, payjp_account=None, api_base=None, **params):
        instance = cls(id, api_key, payjp_account, api_base, **params)
        instance.refresh()
        return instance

    def instance_url(self):
        id = self.get('id')
        if not id:
            return "/v1/accounts"
        id = util.utf8(id)
        base = self.class_url()
        extn = quote_plus(id)
        return "%s/%s" % (base, extn)


class Card(UpdateableAPIResource, DeletableAPIResource):

    def instance_url(self):
        self.id = util.utf8(self.id)
        extn = quote_plus(self.id)
        if (hasattr(self, 'customer')):
            self.customer = util.utf8(self.customer)

            base = Customer.class_url()
            owner_extn = quote_plus(self.customer)

        else:
            raise error.InvalidRequestError(
                "Could not determine whether card_id %s is "
                "attached to a customer "
                "or a recipient." % self.id, 'id')

        return "%s/%s/cards/%s" % (base, owner_extn, extn)

    @classmethod
    def retrieve(cls, id, api_key=None, payjp_account=None, api_base=None, **params):
        raise NotImplementedError(
            "Can't retrieve a card without a customer ID."
            "Use customer.cards.retrieve('card_id') or "
            "recipient.cards.retrieve('card_id') instead.")


class Subscription(CreateableAPIResource, DeletableAPIResource,
                   UpdateableAPIResource, ListableAPIResource):

    def pause(self, **kwargs):
        url = self.instance_url() + '/pause'
        self.refresh_from(self.request('post', url, kwargs))
        return self

    def resume(self, **kwargs):
        url = self.instance_url() + '/resume'
        self.refresh_from(self.request('post', url, kwargs))
        return self

    def cancel(self, **kwargs):
        url = self.instance_url() + '/cancel'
        self.refresh_from(self.request('post', url, kwargs))
        return self


class Transfer(ListableAPIResource):
    pass

