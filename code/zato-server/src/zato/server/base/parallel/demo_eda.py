# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import random
import uuid
from json import dumps as json_dumps
from typing import TYPE_CHECKING

# gevent
from gevent import sleep, spawn

# zato-broker-core (Rust extension)
from zato_broker_core import broker_stream_xadd

# ################################################################################################################################
# ################################################################################################################################

if TYPE_CHECKING:
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Target publish rates (messages per minute) per topic. The shape is
# intentionally non-uniform so the main chart has visible texture.
# Total across all topics: ~50 msg/min (~0.83 msg/sec).

Topic_Rates = {
    'orders.created':             12,
    'orders.fulfilled':           10,
    'billing.payments.received':   8,
    'billing.invoices.issued':     7,
    'crm.contacts.updated':        6,
    'crm.leads.created':           4,
    'system.audit.events':         3,
}

# How much the inter-message sleep is randomly jittered around the target
# interval: 0.5 .. 1.5 x the nominal value. Keeps traffic looking alive
# instead of metronomic.
Jitter_Min = 0.5
Jitter_Max = 1.5

# The stream message metadata shape matches what `zato.broker.topic.publish`
# sends today (see zato.server.service.internal.broker.TopicPublish). This
# keeps consumers that already read these streams unaffected.
Default_Priority = 5
Default_Expiration_Seconds = 86400
Mime_Type_Json = 'application/json'

# ################################################################################################################################
# ################################################################################################################################

def _random_customer_id() -> 'str':
    return 'CUST-{:05d}'.format(random.randint(1, 99999))

def _random_contact_id() -> 'str':
    return 'CONT-{:05d}'.format(random.randint(1, 99999))

def _random_amount_cents() -> 'int':
    return random.randint(100, 500_000)

def _random_currency() -> 'str':
    return random.choice(['EUR', 'USD', 'GBP', 'CHF'])

def _random_order_id() -> 'str':
    return 'ORD-{:06d}'.format(random.randint(1, 999999))

def _random_invoice_id() -> 'str':
    return 'INV-{:06d}'.format(random.randint(1, 999999))

def _random_lead_source() -> 'str':
    return random.choice(['web', 'referral', 'inbound-call', 'event', 'partner'])

def _random_channel() -> 'str':
    return random.choice(['card', 'sepa', 'wire', 'ach'])

def _random_audit_actor() -> 'str':
    return random.choice(['svc.auth', 'svc.billing', 'svc.orders', 'svc.crm', 'admin.console'])

def _random_audit_action() -> 'str':
    return random.choice(['login.ok', 'permission.granted', 'record.updated', 'record.created', 'policy.changed'])

# ################################################################################################################################
# ################################################################################################################################

def _build_payload(topic_name:'str') -> 'dict':
    """ Builds a small, domain-realistic payload for a given demo topic. All
    values are randomised per call so the stream looks alive.
    """

    if topic_name == 'crm.contacts.updated':
        return {
            'contact_id': _random_contact_id(),
            'customer_id': _random_customer_id(),
            'fields_changed': random.sample(['email', 'phone', 'address', 'company', 'title'], k=random.randint(1, 3)),
        }

    if topic_name == 'crm.leads.created':
        return {
            'lead_id': 'LEAD-{:06d}'.format(random.randint(1, 999999)),
            'source': _random_lead_source(),
            'est_value_cents': _random_amount_cents(),
            'currency': _random_currency(),
        }

    if topic_name == 'billing.invoices.issued':
        return {
            'invoice_id': _random_invoice_id(),
            'customer_id': _random_customer_id(),
            'amount_cents': _random_amount_cents(),
            'currency': _random_currency(),
            'due_in_days': random.choice([7, 14, 30]),
        }

    if topic_name == 'billing.payments.received':
        return {
            'payment_id': 'PAY-{:06d}'.format(random.randint(1, 999999)),
            'invoice_id': _random_invoice_id(),
            'customer_id': _random_customer_id(),
            'amount_cents': _random_amount_cents(),
            'currency': _random_currency(),
            'channel': _random_channel(),
        }

    if topic_name == 'orders.created':
        return {
            'order_id': _random_order_id(),
            'customer_id': _random_customer_id(),
            'total_cents': _random_amount_cents(),
            'currency': _random_currency(),
            'item_count': random.randint(1, 8),
        }

    if topic_name == 'orders.fulfilled':
        return {
            'order_id': _random_order_id(),
            'fulfilled_at_source': random.choice(['warehouse-eu', 'warehouse-us', 'dropship']),
            'carrier': random.choice(['DHL', 'UPS', 'FedEx', 'GLS']),
        }

    if topic_name == 'system.audit.events':
        return {
            'event_id': uuid.uuid4().hex,
            'actor': _random_audit_actor(),
            'action': _random_audit_action(),
            'target_id': _random_customer_id(),
        }

    return {'note': 'demo-eda', 'topic': topic_name}

# ################################################################################################################################
# ################################################################################################################################

def _publish_one(cfg:'object', topic_name:'str') -> 'None':
    """ Publishes a single demo message to `topic_name` via the Rust
    broker extension. Errors are logged but never re-raised so one topic's
    failure cannot kill the whole greenlet.
    """

    payload_dict = _build_payload(topic_name)
    payload_bytes = json_dumps(payload_dict).encode('utf-8')

    meta = {
        'priority': Default_Priority,
        'expiration': Default_Expiration_Seconds,
        'data_size': len(payload_bytes),
        'mime_type': Mime_Type_Json,
        'publisher': 'demo.eda.publisher',
    }

    try:
        msg_id = broker_stream_xadd(cfg, topic_name, json_dumps(meta), payload=payload_bytes)
        logger.info('Demo EDA publish: topic=%s msg_id=%s size=%d', topic_name, msg_id, len(payload_bytes))
    except Exception as e:
        logger.warning('Demo EDA publish to `%s` failed: %s', topic_name, e)

# ################################################################################################################################
# ################################################################################################################################

def _topic_loop(cfg:'object', topic_name:'str', rate_per_minute:'int') -> 'None':
    """ Long-running greenlet body for one topic. Sleeps for a jittered
    interval around the nominal period between publishes, then publishes
    one message. Intentionally runs forever; stopping requires a server
    restart (demo-scope).
    """

    nominal_interval = 60.0 / float(rate_per_minute)

    logger.info('Demo EDA publisher started: topic=%s rate=%d/min interval=%.2fs',
        topic_name, rate_per_minute, nominal_interval)

    while True:
        jitter = random.uniform(Jitter_Min, Jitter_Max)
        sleep(nominal_interval * jitter)
        _publish_one(cfg, topic_name)

# ################################################################################################################################
# ################################################################################################################################

def start_publisher(server:'ParallelServer') -> 'bool':
    """ Spawns one greenlet per demo topic. Idempotent: once started on a
    server instance, subsequent calls are no-ops regardless of how many
    times the "Import demo config" button is clicked. Returns True if the
    publisher was started by this call, False if it was already running.
    """

    existing = getattr(server, '_demo_eda_publisher_greenlets', None)
    if existing:
        logger.info('Demo EDA publisher already running with %d greenlets', len(existing))
        return False

    cfg = server.broker_client._cfg

    greenlets = []
    for topic_name, rate_per_minute in Topic_Rates.items():
        g = spawn(_topic_loop, cfg, topic_name, rate_per_minute)
        greenlets.append(g)

    server._demo_eda_publisher_greenlets = greenlets

    logger.info('Demo EDA publisher started: %d topics, total_target=%d msg/min',
        len(greenlets), sum(Topic_Rates.values()))

    return True

# ################################################################################################################################
# ################################################################################################################################
