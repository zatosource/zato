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
from zato_broker_core import (
    broker_stream_xadd,
    broker_stream_xgroup_create,
    broker_stream_xreadgroup,
    broker_stream_xack,
)

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
# Total across all topics: ~250 msg/min (~4.16 msg/sec). Combined with
# the ~1.57x average fan-out across subscribers this should yield
# roughly 250 publishes and 390 deliveries per minute at steady state.

Topic_Rates = {
    'orders.created':             60,
    'orders.fulfilled':           50,
    'billing.payments.received':  40,
    'billing.invoices.issued':    35,
    'crm.contacts.updated':       30,
    'crm.leads.created':          20,
    'system.audit.events':        15,
}

# How much the inter-message sleep is randomly jittered around the target
# interval. Tight band (0.9 .. 1.1 x) keeps publishers near their nominal
# cadence so the per-minute chart line is smooth instead of bursty, while
# still avoiding a perfectly metronomic look.
Jitter_Min = 0.9
Jitter_Max = 1.1

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

# ################################################################################################################################
# ################################################################################################################################
#
# Consumer (demo) configuration
# -----------------------------
#
# Each entry mirrors `pubsub_subscription` in demo-eda-enmasse.yaml:
# the sub_key is reused as the broker consumer-group name and as a
# stable identity across restarts. We talk to the broker directly via
# the Python broker API (broker_stream_xgroup_create / xreadgroup /
# xack), exactly the way PubSubBackend does, so no HTTP/REST layer is
# involved.
#
# Each greenlet:
#   1) Calls broker_stream_xgroup_create once per topic (idempotent;
#      "already exists" is swallowed).
#   2) Loops forever: xreadgroup a batch, ack a random subset
#      (~Consumer_Ack_Ratio of them) so the rest stay pending. That
#      keeps queue depths visibly non-zero on the dashboard, which is
#      the whole point of the demo.

# How many messages to pull per request. Kept small so each poll
# delivers a trickle instead of a single large batch -- the latter
# turns the deliveries chart into step-bursts that don't visually
# correlate with the smooth publisher line.
Consumer_Pull_Batch = 3

# Fraction of pulled messages we acknowledge. The remainder is left
# pending so the dashboard's "Queue depth" tile actually moves.
# 0.0 = nothing acked, 1.0 = everything acked.
Consumer_Ack_Ratio = 0.7

# Sleep between consumer iterations. Short, tight band so deliveries
# spread evenly across each minute-bucket instead of arriving in
# clumps. Combined with a small pull batch this gives a continuous
# flow rather than a step function.
Consumer_Pull_Interval_Min = 0.3
Consumer_Pull_Interval_Max = 0.5

# Subscriber roster. Trimmed to keep the pub-vs-deliver ratio at
# roughly 1:1.5 (~11 subscriptions across 7 topics). Each entry
# corresponds to a YAML pubsub_subscription block; we don't need
# username/password here because the Python broker API runs in-process
# and bypasses the broker's HTTP auth path.
Demo_Subscribers = [
    {'sub_key': 'demo.eda.crm-sync',
     'topics':   ['crm.leads.created']},
    {'sub_key': 'demo.eda.audit-tap',
     'topics':   ['billing.invoices.issued', 'system.audit.events']},
    {'sub_key': 'demo.eda.marketing-automation',
     'topics':   ['crm.leads.created']},
    {'sub_key': 'demo.eda.billing-reports',
     'topics':   ['billing.invoices.issued']},
    {'sub_key': 'demo.eda.reconciliation',
     'topics':   ['billing.payments.received']},
    {'sub_key': 'demo.eda.order-fulfillment',
     'topics':   ['orders.created', 'orders.fulfilled']},
    {'sub_key': 'demo.eda.customer-notifications',
     'topics':   ['orders.fulfilled']},
    {'sub_key': 'demo.eda.compliance-archive',
     'topics':   ['system.audit.events', 'crm.contacts.updated']},
]

# ################################################################################################################################
# ################################################################################################################################

def _subscribe_one(cfg:'object', sub_key:'str', topic_name:'str') -> 'bool':
    """ Creates the consumer group for `(topic_name, sub_key)`. Idempotent:
    "already exists" errors from a previous run are swallowed. Returns
    True if the group exists after the call (created or pre-existing).
    """

    # Start ID '$' = "from the current tip" so a fresh demo does not
    # backfill thousands of historical messages on first connect.
    # That backfill was the source of the runaway pub:del ratio:
    # ~4.5K messages on disk -> ~9K deliveries spread across
    # subscribers in a single burst. With '$' the subscriber sees only
    # what publishers produce from now on.
    try:
        broker_stream_xgroup_create(cfg, topic_name, sub_key, '$', True)
    except Exception as e:
        if 'already exists' not in str(e).lower():
            logger.warning('Demo EDA subscribe failed: sub_key=%s topic=%s -> %s',
                sub_key, topic_name, e)
            return False
    logger.info('Demo EDA subscribe: sub_key=%s topic=%s', sub_key, topic_name)
    return True

# ################################################################################################################################
# ################################################################################################################################

def _consume_one_topic(
    cfg:'object',
    sub_key:'str',
    topic_name:'str',
) -> 'tuple[int, int]':
    """ Pulls one batch from `topic_name` for `sub_key`, acks a random
    subset and returns (pulled, acked). Suppresses transport errors so
    one bad topic cannot stop the consumer's other topics this tick.
    """

    try:
        entries = broker_stream_xreadgroup(
            cfg, topic_name, sub_key, sub_key, Consumer_Pull_Batch,
        )
    except Exception as e:
        logger.warning('Demo EDA xreadgroup failed: sub_key=%s topic=%s -> %s',
            sub_key, topic_name, e)
        return 0, 0

    if not entries:
        return 0, 0

    seq_ids_to_ack = []
    for seq_id, _fields_json in entries:
        if random.random() < Consumer_Ack_Ratio:
            seq_ids_to_ack.append(seq_id)

    if seq_ids_to_ack:
        try:
            broker_stream_xack(cfg, topic_name, sub_key, seq_ids_to_ack)
        except Exception as e:
            logger.warning('Demo EDA xack failed: sub_key=%s topic=%s n=%d -> %s',
                sub_key, topic_name, len(seq_ids_to_ack), e)

    return len(entries), len(seq_ids_to_ack)

# ################################################################################################################################
# ################################################################################################################################

def _consumer_loop(cfg:'object', sub:'dict') -> 'None':
    """ Long-running greenlet body for one demo subscriber. Subscribes
    to all of its topics once, then loops: pull a batch from each
    topic, ack a random subset, sleep, repeat. Errors are logged and
    the loop keeps going so one transient broker hiccup does not
    silence the consumer.
    """

    sub_key = sub['sub_key']
    topics = sub['topics']

    for topic_name in topics:
        _subscribe_one(cfg, sub_key, topic_name)

    logger.info('Demo EDA consumer started: sub_key=%s topics=%s ack_ratio=%.2f',
        sub_key, ','.join(topics), Consumer_Ack_Ratio)

    while True:
        sleep(random.uniform(Consumer_Pull_Interval_Min, Consumer_Pull_Interval_Max))

        total_pulled = 0
        total_acked = 0
        for topic_name in topics:
            pulled, acked = _consume_one_topic(cfg, sub_key, topic_name)
            total_pulled += pulled
            total_acked += acked

        if total_pulled:
            logger.info(
                'Demo EDA consumer %s: pulled=%d acked=%d pending_left=%d',
                sub_key, total_pulled, total_acked, total_pulled - total_acked,
            )

# ################################################################################################################################
# ################################################################################################################################

def start_consumer(server:'ParallelServer') -> 'bool':
    """ Spawns one greenlet per demo subscriber. Idempotent like
    `start_publisher`: subsequent calls on the same server instance
    are no-ops. Returns True if the consumer was started by this call,
    False if it was already running. """

    existing = getattr(server, '_demo_eda_consumer_greenlets', None)
    if existing:
        logger.info('Demo EDA consumer already running with %d greenlets', len(existing))
        return False

    cfg = server.broker_client._cfg

    greenlets = []
    for sub in Demo_Subscribers:
        g = spawn(_consumer_loop, cfg, sub)
        greenlets.append(g)

    server._demo_eda_consumer_greenlets = greenlets

    logger.info('Demo EDA consumer started: %d subscribers, ack_ratio=%.2f',
        len(greenlets), Consumer_Ack_Ratio)

    return True

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
