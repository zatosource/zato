# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The purchase orders, the submission of orders to the queued REST channel and the checks of the order-to-cash
# integration that the pub/sub service suites share.

# stdlib
import os
import time
from base64 import b64encode
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from http.client import OK
from json import dumps
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from urllib.request import Request, urlopen
from uuid import uuid4

# PyYAML
import yaml

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_table
from zato.common.db_env.database import get_database_engine
from zato.common.test.conftest_base_pubsub import render_template
from zato.common.test.order_to_cash.models import Buyer_GLN_Fabrikam, Buyer_GLN_Northwind, LedgerKind, ServiceName, \
    SKU_Book, SKU_Paper, SKU_Toner, Step, Topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import any_, anydict, anylist, callable_, dictlist, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

line_spec      = tuple[str, int, int]
line_spec_list = list[line_spec]
steps_dict     = dict[str, 'strlist']
counter_dict   = dict[str, Counter]

# ################################################################################################################################
# ################################################################################################################################

_here = os.path.dirname(os.path.abspath(__file__))

# ################################################################################################################################
# ################################################################################################################################

class Partner:
    """ The trading partner that submits purchase orders to the channel.
    """
    Username = 'order-to-cash.partner'

# ################################################################################################################################

class Channel:
    """ The queued REST channel of the intake.
    """
    Name     = 'order-to-cash.order-intake'
    URL_Path = '/order-to-cash/order'
    Type     = 'rest-channel'

# ################################################################################################################################

class Module:
    """ The file names under which the modules of the integration are written to the pickup directory.
    The two versions of the fulfillment share one file name, so that the second one replaces the first.
    """
    Core        = 'order_to_cash.py'
    Fulfillment = 'order_to_cash_fulfillment.py'
    Receivables = 'order_to_cash_receivables.py'
    Read_Trail  = 'order_to_cash_read_trail.py'

# ################################################################################################################################

class Source:
    """ The files of the shared library that the modules of the integration are read from.
    """
    Core                = os.path.join(_here, 'services.py')
    Fulfillment         = os.path.join(_here, 'services_fulfillment.py')
    Fulfillment_Carrier = os.path.join(_here, 'services_fulfillment_carrier.py')
    Receivables         = os.path.join(_here, 'services_receivables.py')
    Read_Trail          = os.path.join(_here, 'services_read_trail.py')
    Enmasse             = os.path.join(_here, 'enmasse.yaml')

# ################################################################################################################################

class Outcome:
    """ How the chain ends for an order.
    """
    Invoiced = 'invoiced'
    Rejected = 'rejected'

# ################################################################################################################################
# ################################################################################################################################

# The services of the chain that have a push subscription
Chain_Services = (ServiceName.Credit_Check, ServiceName.Fulfillment, ServiceName.Invoicing, ServiceName.Receivables)

# All the topics of the chain
Chain_Topics = (Topic.Order_Accepted, Topic.Order_Approved, Topic.Order_Rejected, Topic.Order_Shipped, Topic.Invoice_Issued)

# The steps that the trail of an order records, in the order of the chain
Expected_Steps = {
    Outcome.Invoiced: [Step.Intake, Step.Credit_Approved, Step.Fulfillment, Step.Invoicing, Step.Ledger_Invoice],
    Outcome.Rejected: [Step.Intake, Step.Credit_Rejected, Step.Ledger_Rejection],
}

# The step that concludes the chain of an order
Terminal_Step = {
    Outcome.Invoiced: Step.Ledger_Invoice,
    Outcome.Rejected: Step.Ledger_Rejection,
}

# The topics that hold one message of an order, all other topics of the chain holding none
Expected_Topics = {
    Outcome.Invoiced: {Topic.Order_Accepted, Topic.Order_Approved, Topic.Order_Shipped, Topic.Invoice_Issued},
    Outcome.Rejected: {Topic.Order_Accepted, Topic.Order_Rejected},
}

# The kind of the ledger entry of an order
Expected_Ledger_Kind = {
    Outcome.Invoiced: LedgerKind.Invoice,
    Outcome.Rejected: LedgerKind.Rejection,
}

# The date of every purchase order of the tests
Order_Date = '2026-11-02'

# The CID of each invocation of a service in a test without a server
Unit_CID = 'order-to-cash-unit-cid'

# The states of the messages of a subscription that its browse lists
State_All     = 'all'
State_Pending = 'pending'

# The delivery page of a channel that lists its DLQ
Kind_DLQ = 'dlq'

# The lines of a regular order - 10 x 4.50 + 2 x 89.99 + 3 x 35.00 = 329.98 net
Standard_Lines:'line_spec_list' = [
    (SKU_Paper, 10, 4_50),
    (SKU_Toner, 2, 89_99),
    (SKU_Book, 3, 35_00),
]

# Ten toner cartridges are worth 899.90, more than the 500.00 of credit that Fabrikam has left
Over_Limit_Lines:'line_spec_list' = [
    (SKU_Toner, 10, 89_99),
]

# Sixty reams of paper weigh 150 kg, which ships by freight
Freight_Lines:'line_spec_list' = [
    (SKU_Paper, 60, 4_50),
]

# A SKU that no warehouse stocks
Unknown_SKU = 'SKU-DISCONTINUED'

Unknown_SKU_Lines:'line_spec_list' = [
    (SKU_Paper, 1, 4_50),
    (Unknown_SKU, 1, 1_00),
]

# ################################################################################################################################
# ################################################################################################################################

# How long an HTTP call to the channel may take, in seconds
_http_timeout = 30

# How long the orders of a test may take to complete, in seconds
_orders_timeout = 180

# How long a condition may take to become true, in seconds
_condition_timeout = 60

# How often the trail and the queues are read while waiting, in seconds
_poll_interval = 0.5

# How many orders are submitted at the same time
_submit_workers = 10

# A page that holds every message of a subscription
_browse_page_size = 100_000

# The length of the random part of a purchase order number
_po_suffix_length = 12

# ################################################################################################################################
# ################################################################################################################################

def read_source(path:'str') -> 'str':
    with open(path) as source_file:
        out = source_file.read()

    return out

# ################################################################################################################################

def render_definitions(partner_password:'str', *, is_receivables_active:'bool') -> 'str':
    """ The enmasse definitions of the integration. Without is_receivables_active the subscription of the receivables
    holds its messages until it is activated.
    """
    placeholders = {
        'partner_password': partner_password,
        'receivables_delivery_active': 'true' if is_receivables_active else 'false',
    }

    out = render_template(Source.Enmasse, placeholders)
    return out

# ################################################################################################################################

def get_subscription_definitions(definitions:'str') -> 'str':
    """ The subscriptions of the integration alone, out of its full enmasse definitions.
    """
    loaded = yaml.safe_load(definitions)

    subscriptions = {
        'pubsub_subscription': loaded['pubsub_subscription'],
    }

    out = yaml.safe_dump(subscriptions, sort_keys=False)
    return out

# ################################################################################################################################
# ################################################################################################################################

def new_po_number(label:'str') -> 'str':
    """ A purchase order number that no other test uses.
    """
    suffix = uuid4().hex[:_po_suffix_length].upper()

    out = f'PO-{label}-{suffix}'
    return out

# ################################################################################################################################

def new_order(po_number:'str', buyer_gln:'str', lines:'line_spec_list') -> 'anydict':
    """ A purchase order as the trading partner submits it, with the lines given as SKU, quantity and unit price.
    """
    order_lines:'dictlist' = []

    for idx, (sku, quantity, unit_price_minor) in enumerate(lines, 1):
        order_lines.append({
            'line_number': idx,
            'sku': sku,
            'quantity': quantity,
            'unit_price_minor': unit_price_minor,
        })

    out = {
        'po_number': po_number,
        'buyer_gln': buyer_gln,
        'currency': 'EUR',
        'order_date': Order_Date,
        'lines': order_lines,
    }

    return out

# ################################################################################################################################

def new_standard_order(po_number:'str', buyer_gln:'str'=Buyer_GLN_Northwind) -> 'anydict':
    out = new_order(po_number, buyer_gln, Standard_Lines)
    return out

# ################################################################################################################################

def new_over_limit_order(po_number:'str') -> 'anydict':
    out = new_order(po_number, Buyer_GLN_Fabrikam, Over_Limit_Lines)
    return out

# ################################################################################################################################

def new_unknown_sku_order(po_number:'str') -> 'anydict':
    out = new_order(po_number, Buyer_GLN_Northwind, Unknown_SKU_Lines)
    return out

# ################################################################################################################################

def new_freight_order(po_number:'str') -> 'anydict':
    out = new_order(po_number, Buyer_GLN_Northwind, Freight_Lines)
    return out

# ################################################################################################################################

def get_invalid_gln(gln:'str') -> 'str':
    """ The GLN with a check digit that does not match its other digits.
    """
    check_digit = int(gln[-1])
    wrong_digit = (check_digit + 1) % 10

    out = f'{gln[:-1]}{wrong_digit}'
    return out

# ################################################################################################################################

def new_invalid_order(po_number:'str') -> 'anydict':
    """ An order that the intake refuses on every attempt, because the check digit of its buyer GLN is wrong.
    """
    out = new_order(po_number, get_invalid_gln(Buyer_GLN_Northwind), Standard_Lines)
    return out

# ################################################################################################################################
# ################################################################################################################################

def submit_order(channel_url:'str', partner_password:'str', order:'anydict') -> 'None':
    """ Submits a purchase order to the queued REST channel the way the trading partner does.
    """
    credentials = f'{Partner.Username}:{partner_password}'.encode('utf8')
    credentials = b64encode(credentials).decode('ascii')

    request = Request(
        channel_url,
        data=dumps(order).encode('utf8'),
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Basic {credentials}',
        },
    )

    with urlopen(request, timeout=_http_timeout) as response:
        if response.status != OK:
            raise Exception(f'The channel answered {response.status} to PO `{order["po_number"]}`')

# ################################################################################################################################

def submit_orders(channel_url:'str', partner_password:'str', orders:'dictlist') -> 'None':
    """ Submits purchase orders concurrently.
    """
    def _submit(order:'anydict') -> 'None':
        submit_order(channel_url, partner_password, order)

    with ThreadPoolExecutor(max_workers=_submit_workers) as executor:
        for _ in executor.map(_submit, orders):
            pass

# ################################################################################################################################
# ################################################################################################################################

def new_unit_service(class_:'any_', base_dir:'str', payload:'any_') -> 'any_':
    """ A service of the integration for a test without a server, with its request set, its publications captured
    and its invocations of other services refused.
    """
    out = class_.__new__(class_)
    out.cid = Unit_CID
    out.server = SimpleNamespace(base_dir=base_dir)
    out.request = SimpleNamespace(input=payload)
    out.pubsub = MagicMock()
    out.invoke = MagicMock(side_effect=AssertionError('A service of the integration must not invoke another one'))

    return out

# ################################################################################################################################

def get_publications(service:'any_') -> 'anylist':
    """ The topic, the data and the keyword arguments of each publication of a service built by new_unit_service.
    """
    out = [(call.args[0], call.args[1], call.kwargs) for call in service.pubsub.publish.call_args_list]
    return out

# ################################################################################################################################
# ################################################################################################################################

def wait_until(condition:'callable_', description:'str', timeout:'float'=_condition_timeout) -> 'None':
    """ Waits until a condition is true, or raises an exception that names it.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if condition():
            return
        time.sleep(_poll_interval)

    raise Exception(f'{description} did not happen within {timeout}s')

# ################################################################################################################################

def read_trail(client:'AdminClient') -> 'anydict':
    """ The steps that the services recorded and the entries of the ledger.
    """
    out = client.invoke(ServiceName.Read_Trail, {})
    return out

# ################################################################################################################################

def get_steps(trail:'anydict') -> 'steps_dict':
    """ The steps of each order, in the order in which the services recorded them.
    """
    out:'steps_dict' = {}

    for item in trail['trail']:
        steps = out.setdefault(item['po_number'], [])
        steps.append(item['step'])

    return out

# ################################################################################################################################

def get_trail_items(trail:'anydict', po_number:'str', step:'str') -> 'dictlist':
    """ The items that the services recorded for one step of one order.
    """
    out:'dictlist' = []

    for item in trail['trail']:
        if item['po_number'] == po_number and item['step'] == step:
            out.append(item)

    return out

# ################################################################################################################################

def get_ledger_entries(trail:'anydict', po_number:'str') -> 'dictlist':
    out:'dictlist' = []

    for entry in trail['ledger']:
        if entry['po_number'] == po_number:
            out.append(entry)

    return out

# ################################################################################################################################

def wait_for_orders(client:'AdminClient', expectations:'strstrdict', timeout:'float'=_orders_timeout) -> 'anydict':
    """ Waits until the trail of each order has the terminal step of its expected outcome, and returns the trail.
    """
    deadline = time.monotonic() + timeout

    while True:

        trail = read_trail(client)
        steps = get_steps(trail)

        missing:'strlist' = []

        for po_number, outcome in expectations.items():
            if Terminal_Step[outcome] not in steps.get(po_number, []):
                missing.append(po_number)

        if not missing:
            return trail

        if time.monotonic() > deadline:
            details = {po_number: steps.get(po_number, []) for po_number in missing}
            raise Exception(f'{len(missing)} of {len(expectations)} orders did not complete within {timeout}s -> {details}')

        time.sleep(_poll_interval)

# ################################################################################################################################
# ################################################################################################################################

def get_sub_keys(client:'AdminClient') -> 'strlist':
    """ The sub keys of the push subscriptions of the chain.
    """
    subscriptions, _ = client.get_list('zato.pubsub.subscription.get-list')

    out:'strlist' = []

    for subscription in subscriptions:
        if subscription['push_service_name'] in Chain_Services:
            out.append(subscription['sub_key'])

    return out

# ################################################################################################################################

def get_sub_key(client:'AdminClient', service_name:'str') -> 'str':
    """ The sub key of the push subscription of a service of the chain.
    """
    subscriptions, _ = client.get_list('zato.pubsub.subscription.get-list')

    for subscription in subscriptions:
        if subscription['push_service_name'] == service_name:
            return subscription['sub_key']

    raise Exception(f'No subscription of service `{service_name}`')

# ################################################################################################################################

def get_channel_dlq(client:'AdminClient', query:'str') -> 'anydict':
    """ The messages of the DLQ of the queued channel that contain the query, as its delivery page lists them.
    """
    channel = client.invoke('zato.http-soap.get', {'name': Channel.Name})

    out = client.invoke('zato.pubsub.outgoing.get-message-list', {
        'conn_type': Channel.Type,
        'conn_id': channel['id'],
        'kind': Kind_DLQ,
        'query': query,
    })

    return out

# ################################################################################################################################

def browse_subscription(client:'AdminClient', sub_key:'str', state:'str') -> 'anydict':
    out = client.invoke('zato.pubsub.subscription.browse-queue', {
        'sub_key': sub_key,
        'state': state,
        'page_size': _browse_page_size,
    })

    return out

# ################################################################################################################################

def get_topic_messages(client:'AdminClient') -> 'anylist':
    """ Every message of every topic of the chain, as the browse of the subscriptions lists them.
    """
    out:'anylist' = []

    for sub_key in get_sub_keys(client):
        page = browse_subscription(client, sub_key, State_All)
        out.extend(page['rows'])

    return out

# ################################################################################################################################

def count_messages_by_topic(client:'AdminClient') -> 'counter_dict':
    """ How many messages each topic of the chain holds for each purchase order.
    """
    out:'counter_dict' = {topic_name: Counter() for topic_name in Chain_Topics}

    for row in get_topic_messages(client):
        out[row['topic_name']][row['correl_id']] += 1

    return out

# ################################################################################################################################

def get_msg_ids(client:'AdminClient', topic_name:'str', po_number:'str') -> 'strlist':
    """ The message IDs of the messages of an order in a topic of the chain.
    """
    out:'strlist' = []

    for row in get_topic_messages(client):
        if row['topic_name'] == topic_name and row['correl_id'] == po_number:
            out.append(row['msg_id'])

    return out

# ################################################################################################################################

def get_pending_count(client:'AdminClient') -> 'int':
    """ How many messages the subscriptions of the chain have yet to deliver.
    """
    out = 0

    for sub_key in get_sub_keys(client):
        page = browse_subscription(client, sub_key, State_Pending)
        out += page['total']

    return out

# ################################################################################################################################

def count_audit_events(database_env:'strstrdict', msg_id:'str', event_type:'str') -> 'int':
    """ How many events of one type the audit log of an environment holds about one message.
    """
    query = select(event_table.c.id)
    query = query.where(event_table.c.msg_id == msg_id)
    query = query.where(event_table.c.event_type == event_type)

    with patch.dict(os.environ, database_env):
        engine = get_database_engine()

        with engine.connect() as connection:
            rows = connection.execute(query).fetchall()

    out = len(rows)
    return out

# ################################################################################################################################
# ################################################################################################################################

def check_terminal_state(trail:'anydict', expectations:'strstrdict') -> 'None':
    """ Every order reached the terminal step of its outcome, and the ledger has exactly one entry of it.
    """
    steps = get_steps(trail)

    for po_number, outcome in expectations.items():

        assert Terminal_Step[outcome] in steps[po_number], (po_number, steps[po_number])

        entries = get_ledger_entries(trail, po_number)

        assert len(entries) == 1, (po_number, entries)
        assert entries[0]['kind'] == Expected_Ledger_Kind[outcome], (po_number, entries)

# ################################################################################################################################

def check_one_message_per_order(client:'AdminClient', expectations:'strstrdict') -> 'None':
    """ Every topic of the chain holds exactly one message of each order that passed through it, and none of any other.
    """
    counts = count_messages_by_topic(client)

    for po_number, outcome in expectations.items():
        for topic_name in Chain_Topics:

            if topic_name in Expected_Topics[outcome]:
                expected = 1
            else:
                expected = 0

            actual = counts[topic_name][po_number]
            assert actual == expected, (po_number, topic_name, actual, expected)

# ################################################################################################################################

def check_empty_queues(client:'AdminClient') -> 'None':
    """ No subscription of the chain has messages that it has yet to deliver.
    """
    def _is_empty() -> 'bool':
        out = get_pending_count(client) == 0
        return out

    wait_until(_is_empty, 'The delivery of all the pending messages of the chain')

# ################################################################################################################################

def check_step_order(trail:'anydict', expectations:'strstrdict') -> 'None':
    """ The steps of each order, each at the time it was first recorded, follow the order of the chain.
    """
    steps = get_steps(trail)

    for po_number, outcome in expectations.items():

        first_steps = list(dict.fromkeys(steps[po_number]))
        assert first_steps == Expected_Steps[outcome], (po_number, steps[po_number])

# ################################################################################################################################

def check_repeats_only_in_flight(trail:'anydict', expectations:'strstrdict', in_flight:'set[str]') -> 'None':
    """ A step repeats only for an order that was in flight during a fault.
    """
    steps = get_steps(trail)

    for po_number in expectations:

        po_steps = steps[po_number]

        if len(po_steps) != len(set(po_steps)):
            assert po_number in in_flight, (po_number, po_steps)

# ################################################################################################################################

def check_orders(client:'AdminClient', expectations:'strstrdict', in_flight:'set[str] | None'=None) -> 'anydict':
    """ Waits for the orders and runs every check of the chain on them. Returns the trail.
    """
    if in_flight is None:
        in_flight = set()

    trail = wait_for_orders(client, expectations)

    check_empty_queues(client)
    check_terminal_state(trail, expectations)
    check_one_message_per_order(client, expectations)
    check_step_order(trail, expectations)
    check_repeats_only_in_flight(trail, expectations, in_flight)

    return trail

# ################################################################################################################################
# ################################################################################################################################
