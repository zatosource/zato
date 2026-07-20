# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from time import monotonic

# gevent
from gevent import joinall, sleep, spawn
from gevent.subprocess import run as subprocess_run

# humanize
from humanize import intcomma

# Zato
from common import get_min_delivery_rate, get_min_publish_rate, set_progress_context, Min_Cleanup_Rate_Per_Second
from load import consume_until_stopped
from seeding import connect_native, seed_backlog
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.util.time_ import datetime_to_ms, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# How many topics the seeded backlog spreads over, each with its own subscriber.
_topic_count = 100

# How many messages each topic holds.
_messages_per_topic = 10_000

# The seeded topics split into three bands - expired pending messages the expiry
# sweep must remove, delivered traces aged past retention the age sweep must remove,
# and live pending messages the sweep must never touch, with live traffic
# running against the live band throughout.
_expired_topic_count = 40
_aged_topic_count = 40

# How many publisher greenlets pump concurrently into the live band while the sweep runs.
_publisher_greenlet_count = 20

# How many messages one publisher greenlet publishes between yields.
_publish_burst_size = 100

# How long one blocking fetch waits inside a consumer greenlet, in milliseconds.
_consumer_block_ms = 500

# How far in the past the aged traces are placed - well past the default retention of days.
_aged_days = 30

# How many milliseconds one second and one day have.
_ms_per_second = 1000
_ms_per_day = 24 * 60 * 60 * _ms_per_second

# ################################################################################################################################
# ################################################################################################################################

def _prepare_bands() -> 'None':
    """ Turns the first band of seeded topics into expired pending messages
    and the second band into delivered traces aged past retention - set-based
    statements through the native driver, like the seeding itself.
    """
    connection, placeholder = connect_native()
    cursor = connection.cursor()

    now_ms = int(datetime_to_ms(utcnow()))

    expired_ms = now_ms - _ms_per_second
    aged_ms = now_ms - _aged_days * _ms_per_day

    # The seeded topic names sort by their zero-padded index, so band edges are name comparisons.
    expired_cutoff = f'perf.topic.{_expired_topic_count - 1:04d}'
    aged_cutoff = f'perf.topic.{_expired_topic_count + _aged_topic_count - 1:04d}'

    # The first band expires with its delivery rows still in place -
    # removing both is exactly the expiry sweep's job ..
    _ = cursor.execute(
        f'update pubsub_message set expiration_ms = {placeholder} where topic_name <= {placeholder}',
        (expired_ms, expired_cutoff))

    # .. the second band becomes fully delivered traces aged past retention -
    # .. a NULL payload with no delivery rows is what full delivery leaves behind ..
    aged_update = f'update pubsub_message set payload = null, pub_time_ms = {placeholder}'
    aged_update += f' where topic_name > {placeholder} and topic_name <= {placeholder}'

    _ = cursor.execute(aged_update, (aged_ms, expired_cutoff, aged_cutoff))

    _ = cursor.execute(
        f'delete from pubsub_delivery where topic_name > {placeholder} and topic_name <= {placeholder}',
        (expired_cutoff, aged_cutoff))

    connection.commit()
    connection.close()

# ################################################################################################################################

def _count_band_messages(low_cutoff:'str', high_cutoff:'str') -> 'int':
    """ Counts the message rows whose topic falls between the two cutoff names.
    """
    connection, placeholder = connect_native()
    cursor = connection.cursor()

    query = f'select count(*) from pubsub_message where topic_name > {placeholder} and topic_name <= {placeholder}'
    _ = cursor.execute(query, (low_cutoff, high_cutoff))
    row = cursor.fetchone()

    connection.close()

    out = row[0]
    return out

# ################################################################################################################################

def _count_band_deliveries(low_cutoff:'str', high_cutoff:'str') -> 'int':
    """ Counts the delivery rows whose topic falls between the two cutoff names.
    """
    connection, placeholder = connect_native()
    cursor = connection.cursor()

    query = f'select count(*) from pubsub_delivery where topic_name > {placeholder} and topic_name <= {placeholder}'
    _ = cursor.execute(query, (low_cutoff, high_cutoff))
    row = cursor.fetchone()

    connection.close()

    out = row[0]
    return out

# ################################################################################################################################

def _publish_traffic(backend:'SQLPubSubBackend', topic_names:'strlist', stop:'anydict', counts:'anydict') -> 'None':
    """ What one publisher greenlet runs - fresh traffic into the live band,
    round-robin over its topics, until the sweep is over.
    """
    message_index = 0

    while not stop['is_set']:

        for _burst_index in range(_publish_burst_size):
            topic_name = topic_names[message_index % len(topic_names)]
            _ = backend.publish(topic_name, f'retention-live-{message_index}')
            counts['published'] += 1
            message_index += 1

        # Yield after each burst so the consumers and the wind-down check get their turns.
        sleep(0)

# ################################################################################################################################

def run_retention_scenario() -> 'None':
    """ The cleanup process against a million-message table, run the way production
    runs it - as its own operating system process sweeping the shared database while
    the backend keeps publishing and delivering against it. The expiry and aged-trace
    sweeps each remove a deep band, the live band keeps its full throughput and its
    accounting stays exact, and the deletion rate clears the floor.
    """
    live_topic_count = _topic_count - _expired_topic_count - _aged_topic_count

    set_progress_context('retention', _publisher_greenlet_count, live_topic_count)

    seeding_seconds = seed_backlog(topic_count=_topic_count, messages_per_topic=_messages_per_topic)
    _prepare_bands()

    total_messages = _topic_count * _messages_per_topic
    print(f'Retention: seeded {intcomma(total_messages)} messages in {seeding_seconds:.1f}s')

    expired_message_count = _expired_topic_count * _messages_per_topic
    aged_message_count = _aged_topic_count * _messages_per_topic
    live_message_count = live_topic_count * _messages_per_topic

    # The band edges, as in _prepare_bands.
    expired_cutoff = f'perf.topic.{_expired_topic_count - 1:04d}'
    aged_cutoff = f'perf.topic.{_expired_topic_count + _aged_topic_count - 1:04d}'
    live_high_cutoff = f'perf.topic.{_topic_count - 1:04d}'

    # The live band's topics and subscribers, as seed_backlog names them.
    live_topic_names:'strlist' = []
    live_sub_keys:'strlist' = []

    for topic_index in range(_expired_topic_count + _aged_topic_count, _topic_count):
        live_topic_names.append(f'perf.topic.{topic_index:04d}')
        live_sub_keys.append(f'zpsk.perf.{topic_index:04d}')

    backend = SQLPubSubBackend()

    # The live band drains and receives fresh traffic throughout the sweep ..
    stop = {'is_set': False}
    publish_counts:'anydict' = {'published': 0}
    per_sub_delivered:'anydict' = {}

    greenlets:'anylist' = []

    for sub_key in live_sub_keys:
        per_sub_delivered[sub_key] = 0
        greenlets.append(spawn(consume_until_stopped, backend, sub_key, per_sub_delivered, stop, _consumer_block_ms))

    for _publisher_index in range(_publisher_greenlet_count):
        greenlets.append(spawn(_publish_traffic, backend, live_topic_names, stop, publish_counts))

    # .. the sweep runs as its own process against the very database the traffic above is hitting ..
    sweep_args = [sys.executable, '-m', 'zato.common.pubsub.sql.cleanup', '--once']

    start = monotonic()
    completed = subprocess_run(sweep_args, capture_output=True)
    elapsed = monotonic() - start

    assert completed.returncode == 0, completed.stderr

    # .. the sweep is over, so the traffic may now wind down ..
    stop['is_set'] = True
    _ = joinall(greenlets)

    published = publish_counts['published']

    delivered = 0
    for sub_key in live_sub_keys:
        delivered += per_sub_delivered[sub_key]

    # .. the expired and aged bands went in full ..
    remaining_expired = _count_band_messages('', expired_cutoff)
    assert remaining_expired == 0, f'Expected no expired-band rows, got {intcomma(remaining_expired)}'

    remaining_aged = _count_band_messages(expired_cutoff, aged_cutoff)
    assert remaining_aged == 0, f'Expected no aged-band rows, got {intcomma(remaining_aged)}'

    # .. the live band's accounting stays exact under the concurrent sweep ..
    live_messages = _count_band_messages(aged_cutoff, live_high_cutoff)
    expected_live_messages = live_message_count + published

    assert live_messages == expected_live_messages, \
        f'Expected {intcomma(expected_live_messages)} live-band rows, got {intcomma(live_messages)}'

    live_deliveries = _count_band_deliveries(aged_cutoff, live_high_cutoff)
    expected_live_deliveries = live_message_count + published - delivered

    assert live_deliveries == expected_live_deliveries, \
        f'Expected {intcomma(expected_live_deliveries)} live-band deliveries, got {intcomma(live_deliveries)}'

    # .. the sweep rate must clear the floor ..
    deleted_rows = expired_message_count * 2 + aged_message_count
    sweep_rate = deleted_rows / elapsed

    # .. and so must the live traffic that ran beside it.
    publish_rate = published / elapsed
    delivery_rate = delivered / elapsed

    message = f'Retention: swept {intcomma(deleted_rows)} rows in {elapsed:.1f}s at {intcomma(int(sweep_rate))}/s'
    message += f' with {intcomma(int(publish_rate))} publishes/s'
    message += f' and {intcomma(int(delivery_rate))} deliveries/s concurrently'
    print(message)

    assert sweep_rate >= Min_Cleanup_Rate_Per_Second, \
        f'Cleanup rate too low: {intcomma(int(sweep_rate))}/s over {intcomma(deleted_rows)} rows'

    assert publish_rate >= get_min_publish_rate(), \
        f'Publish rate too low during the sweep: {intcomma(int(publish_rate))}/s'

    assert delivery_rate >= get_min_delivery_rate(), \
        f'Delivery rate too low during the sweep: {intcomma(int(delivery_rate))}/s'

# ################################################################################################################################
# ################################################################################################################################
