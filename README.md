# PAY.JP for Python

[![Build Status](https://travis-ci.org/payjp/payjp-python.svg?branch=master)](https://travis-ci.org/payjp/payjp-python)

## Installation

Install from PyPi using [pip](http://www.pip-installer.org/en/latest/), a
package manager for Python.

```
pip install payjp
```

Or, you can [download the source code
(ZIP)](https://github.com/payjp/payjp-python/zipball/master "payjp-python
source code") for `payjp-python`, and then run:

```
python setup.py install
```

## Dependencies

- requests
- six

Install dependencies from using [pip](http://www.pip-installer.org/en/latest/):

    pip install -r requirements.txt

## Documentation

Please see our official [documentation](https://pay.jp/docs/api).

## Example

```python
from payjp import Payjp
payjp = Payjp('sk_test_c62fade9d045b54cd76d7036')
payjp.customers.list()
```

### Charge

```python
payjp.charges.retrieve(id)
payjp.charges.create(query={})
payjp.charges.update(id, query={})
payjp.charges.list(query={})
payjp.charges.capture(id, query={})
payjp.charges.refund(id, query={})
```

### Customer

```python
payjp.customers.retrieve(id)
payjp.customers.create(query={})
payjp.customers.update(id, query={})
payjp.customers.delete(id)
payjp.customers.list(query={})
```

### Card

```python
payjp.customers.cards.retrieve(customer_id, card_id)
payjp.customers.cards.create(customer_id, query={})
payjp.customers.cards.update(customer_id, card_id, query={})
payjp.customers.cards.delete(customer_id, card_id)
payjp.customers.cards.list(customer_id, query={})
```

### Plan

```python
payjp.plans.retrieve(id)
payjp.plans.create(query={})
payjp.plans.update(id, query={})
payjp.plans.delete(id)
payjp.plans.list(query={})
```

### Subscription

```python
payjp.subscriptions.retrieve(id)
payjp.subscriptions.create(query={})
payjp.subscriptions.update(id, query={})
payjp.subscriptions.delete(id)
payjp.subscriptions.list(query={})
payjp.subscriptions.pause(id)
payjp.subscriptions.resume(id, query={})
payjp.subscriptions.cancel(id)
payjp.subscriptions.delete(id)
payjp.customers.subscriptions.list(customer_id, query={})
payjp.customers.subscriptions.retrieve(customer_id, subscription_id)
```

### Token

```python
payjp.tokens.create(query={})
payjp.tokens.retrieve(id)
```

### Transfer

```python
payjp.transfers.list(query={})
payjp.transfers.retrieve(id)
payjp.transfers.charges(id, query={})
```

### Event

```python
payjp.events.retrieve(id)
payjp.events.list(query={})
```

### Account

```python
payjp.accounts.retrieve()
```