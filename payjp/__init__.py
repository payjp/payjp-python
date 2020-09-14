# PAY.JP Python bindings

# Configuration variables

api_key = None
api_base = 'https://api.pay.jp'
api_version = None

max_retry = 0
retry_interval = 2

# TODO include Card?
__all__ = ['Account', 'Card', 'Charge', 'Customer', 'Event', 'Plan', 'Subscription', 'Token', 'Transfer']

# Resource
from payjp.resource import (  # noqa
    Account, Charge, Customer, Event, Plan, Subscription, Token, Transfer)

