# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import random
import time
from concurrent.futures import ThreadPoolExecutor
from http.client import CONFLICT, INTERNAL_SERVER_ERROR, OK
from threading import Event

# Zato
from pubsub_exactly_once.harness import get_engine, new_keys
from pubsub_exactly_once.rest import ack, drain, get_correl_ids, post_json, publish
from pubsub_exactly_once.server import kill_worker
from zato.common.test.exactly_once.config import TestConfig
from zato.common.test.exactly_once.control import Input_Topic
from zato.common.test.exactly_once.verify import assert_exactly_once, count_topic_deliveries, read_correl_ids, \
    wait_for_outputs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# How many messages each load test publishes
_message_count = 20_000

# How many input messages of the relay are published per second
_publication_rate = 100

# How many times the worker is killed while the relay is under load
_worker_kills = 3

# How many clients compete for the messages of one queue
_consumer_count = 4

# How many messages one pull of a competing client asks for
_consumer_batch_size = 50

# The share of the batches that a competing client acknowledges only after their lease ran out
_late_batch_share = 0.1

# How long beyond the lease a client waits, in seconds
_lease_margin = 0.5

# How long a request that did not reach the server waits before it is sent again,
# and how often the progress of a test is read, in seconds
_retry_seconds = 0.2
_poll_seconds  = 1.0

# How long a load test may take to settle once everything was published, in seconds
_load_timeout = 600.0

# The topics of the cycle of a pull client
_orders_topic   = 'orders'
_invoices_topic = 'invoices'

# ################################################################################################################################
# ################################################################################################################################

def _get_lease_seconds() -> 'float':
    """ Returns how long a pulled message stays reserved for its client, in seconds.
    """
    value = TestConfig.extra_server_env['Zato_PubSub_Pull_Lease_Seconds']

    out = float(value)
    return out

# ################################################################################################################################

def _publish_until_stored(username:'str', password:'str', topic_name:'str', key:'str') -> 'None':
    """ Publishes one message under its key as the message ID, repeating the request until the server confirms it,
    which is safe because a repeated publication with the same message ID stores nothing new.
    """
    payload:'anydict' = {
        'data': {'key': key},
        'msg_id': key,
        'correl_id': key,
    }

    is_stored = False

    while not is_stored:

        # A request whose connection the killed worker closed is sent again ..
        try:
            result = publish(username, password, topic_name, payload)
        except OSError:
            time.sleep(_retry_seconds)
            continue

        # .. as is one that the server did not complete, while anything else is a response to the publication.
        if result.status_code >= INTERNAL_SERVER_ERROR:
            time.sleep(_retry_seconds)
        else:
            assert result.status_code == OK, result
            is_stored = True

# ################################################################################################################################
# ################################################################################################################################

class _OutputReader:
    """ A pull client of the output topic of the relay that reads throughout a load test and never fails itself.
    """

    def __init__(self, prefix:'str') -> 'None':
        self.prefix = prefix
        self.received:'strlist' = []

# ################################################################################################################################

    def _pull(self) -> 'anylist':
        """ Returns the messages of one pull, or none if the response did not arrive, in which case the messages
        that it handed out are handed out again once their lease runs out, ahead of any later message.
        """
        payload = {'max_messages': _consumer_batch_size}

        try:
            result = post_json('/pubsub/messages/get', TestConfig.reader_username, TestConfig.reader_password, payload)
        except OSError:
            time.sleep(_get_lease_seconds() + _lease_margin)
            return []

        if result.status_code >= INTERNAL_SERVER_ERROR:
            time.sleep(_get_lease_seconds() + _lease_margin)
            return []

        assert result.status_code == OK, result

        out = result.body['messages']
        return out

# ################################################################################################################################

    def _ack(self, messages:'anylist') -> 'None':
        """ Acknowledges the messages of one pull, repeating the request until the server confirms it,
        before anything else is pulled.
        """
        msg_ids:'strlist' = []

        for message in messages:
            meta = message['meta']
            msg_ids.append(meta['msg_id'])

        payload = {'msg_ids': msg_ids}
        is_acknowledged = False

        while not is_acknowledged:

            try:
                result = ack(TestConfig.reader_username, TestConfig.reader_password, payload)
            except OSError:
                time.sleep(_retry_seconds)
                continue

            if result.status_code >= INTERNAL_SERVER_ERROR:
                time.sleep(_retry_seconds)
            else:
                assert result.status_code == OK, result
                is_acknowledged = True

# ################################################################################################################################

    def run(self, stop:'Event') -> 'None':
        """ Reads and acknowledges the outputs of the relay until the test stops it.
        """
        while not stop.is_set():

            messages = self._pull()

            if not messages:
                time.sleep(_retry_seconds)
                continue

            correl_ids = get_correl_ids(messages, self.prefix)
            self.received.extend(correl_ids)

            self._ack(messages)

# ################################################################################################################################
# ################################################################################################################################

class _CompetingConsumer:
    """ A pull client of the orders queue that publishes one invoice per order in the transaction of its acknowledgement,
    and that acknowledges some of its batches only after their lease ran out.
    """

    def __init__(self) -> 'None':
        self.conflict_count = 0

# ################################################################################################################################

    def _build_ack(self, messages:'anylist') -> 'anydict':
        """ Returns the acknowledgement of a batch, with the invoice of each order under a message ID derived
        from the message ID of the order.
        """
        consumed:'anylist' = []
        invoices:'anylist' = []

        for message in messages:
            meta = message['meta']
            data = message['data']

            consumed_message = {
                'msg_id': meta['msg_id'],
                'delivery_attempt': meta['delivery_attempt'],
            }

            invoice = {
                'topic_name': _invoices_topic,
                'data': {'key': data['key']},
                'msg_id': meta['msg_id'] + '.invoice',
                'correl_id': data['key'],
            }

            consumed.append(consumed_message)
            invoices.append(invoice)

        out:'anydict' = {
            'consumed': consumed,
            'publish': invoices,
        }

        return out

# ################################################################################################################################

    def run(self, stop:'Event') -> 'None':
        """ Consumes orders until the test stops it.
        """
        payload = {'max_messages': _consumer_batch_size}

        while not stop.is_set():

            result = post_json('/pubsub/messages/get', TestConfig.orders_username, TestConfig.orders_password, payload)
            assert result.status_code == OK, result

            messages = result.body['messages']

            if not messages:
                time.sleep(_retry_seconds)
                continue

            ack_payload = self._build_ack(messages)

            # A late batch is handed out to another client in the meantime ..
            if random.random() < _late_batch_share:
                time.sleep(_get_lease_seconds() + _lease_margin)

            ack_result = ack(TestConfig.orders_username, TestConfig.orders_password, ack_payload)

            # .. which concludes it, so the acknowledgement of this client is rejected with nothing published.
            if ack_result.status_code == CONFLICT:
                self.conflict_count += 1
            else:
                assert ack_result.status_code == OK, ack_result

# ################################################################################################################################
# ################################################################################################################################

def _kill_worker_at_random(duration:'float') -> 'None':
    """ Kills the worker at random moments within the given number of seconds from now.
    """
    start = time.monotonic()
    kill_times:'list[float]' = []

    for _ in range(_worker_kills):
        offset = random.uniform(0, duration)
        kill_times.append(offset)

    kill_times.sort()

    for offset in kill_times:
        delay = start + offset - time.monotonic()

        if delay > 0:
            time.sleep(delay)

        kill_worker()

# ################################################################################################################################

def _wait_for_received(reader:'_OutputReader', count:'int') -> 'None':
    """ Waits until the reader received the given number of outputs, and then for one more lease,
    in which a repeated output would arrive.
    """
    deadline = time.monotonic() + _load_timeout

    while len(reader.received) < count:
        assert time.monotonic() < deadline, f'Received {len(reader.received)} of {count} outputs'
        time.sleep(_poll_seconds)

    time.sleep(_get_lease_seconds() + _lease_margin)

# ################################################################################################################################

def _wait_for_invoices(prefix:'str', count:'int') -> 'None':
    """ Waits until no order remains in the queue and the given number of invoices exists.
    """
    engine = get_engine()
    deadline = time.monotonic() + _load_timeout

    while True:
        pending_count = count_topic_deliveries(engine, _orders_topic)
        invoice_keys = read_correl_ids(engine, _invoices_topic, prefix)
        invoice_count = len(invoice_keys)

        if not pending_count:
            if invoice_count >= count:
                break

        assert time.monotonic() < deadline, f'Pending orders:{pending_count}, invoices:{invoice_count}'
        time.sleep(_poll_seconds)

# ################################################################################################################################
# ################################################################################################################################

def test_crashes_under_continuous_publication(zato_server:'any_') -> 'None':
    """ Input messages are published at a constant rate while the worker is killed three times at random moments.
    The relay commits each output once and in order, and a pull client of the outputs receives each of them
    once and in order.
    """
    _ = drain(TestConfig.reader_username, TestConfig.reader_password)

    prefix, keys = new_keys(_message_count)
    duration = _message_count / _publication_rate
    interval = 1 / _publication_rate

    stop = Event()
    reader = _OutputReader(prefix)

    with ThreadPoolExecutor() as executor:

        # The reader reads throughout, and the worker is killed while the inputs are published ..
        reader_future = executor.submit(reader.run, stop)
        killer_future = executor.submit(_kill_worker_at_random, duration)

        try:
            start = time.monotonic()

            for index, key in enumerate(keys):
                delay = start + index * interval - time.monotonic()

                if delay > 0:
                    time.sleep(delay)

                _publish_until_stored(TestConfig.publisher_username, TestConfig.publisher_password, Input_Topic, key)

            killer_future.result()

            # .. the relay commits each output once and in order ..
            engine = get_engine()
            check = wait_for_outputs(engine, keys, prefix, _load_timeout)
            assert_exactly_once(check, keys)

            # .. and the reader receives each of them once and in order.
            _wait_for_received(reader, _message_count)

        finally:
            stop.set()

        reader_future.result()

    assert reader.received == keys

# ################################################################################################################################

def test_competing_consumers_with_lease_expiry(zato_server:'any_') -> 'None':
    """ Four clients consume the orders of one queue, each publishing one invoice per order in the transaction of its
    acknowledgement and acknowledging a tenth of its batches only after their lease ran out. Every order is acknowledged,
    and each order has exactly one invoice.
    """
    _ = drain(TestConfig.orders_username, TestConfig.orders_password)
    _ = drain(TestConfig.verifier_username, TestConfig.verifier_password)

    prefix, keys = new_keys(_message_count)

    stop = Event()
    consumers:'list[_CompetingConsumer]' = []

    with ThreadPoolExecutor() as executor:

        futures:'anylist' = []

        for _ in range(_consumer_count):
            consumer = _CompetingConsumer()
            future = executor.submit(consumer.run, stop)

            consumers.append(consumer)
            futures.append(future)

        # The orders are published while the clients consume them ..
        try:
            for key in keys:
                _publish_until_stored(TestConfig.publisher_username, TestConfig.publisher_password, _orders_topic, key)

            _wait_for_invoices(prefix, _message_count)

        finally:
            stop.set()

        for future in futures:
            future.result()

    # .. every order is acknowledged with exactly one invoice ..
    engine = get_engine()
    invoice_keys = read_correl_ids(engine, _invoices_topic, prefix)
    invoice_keys.sort()

    assert count_topic_deliveries(engine, _orders_topic) == 0
    assert invoice_keys == keys

    # .. and the clients competed for the same orders.
    conflict_count = 0

    for consumer in consumers:
        conflict_count += consumer.conflict_count

    assert conflict_count > 0

# ################################################################################################################################
# ################################################################################################################################
