# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from http.client import CONFLICT, INTERNAL_SERVER_ERROR, OK

# Zato
from pubsub_exactly_once.traffic_report import Latencies
from pubsub_exactly_once.rest import post_json
from pubsub_perf.config import PerfConfig, Receipts_Topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from concurrent.futures import Future, ThreadPoolExecutor
    from threading import Event
    from pubsub_perf.config import Credentials, credentialslist
    from zato.common.typing_ import anydict, anylist, strfloatdict, strlist

    Credentials = Credentials
    Future = Future
    ThreadPoolExecutor = ThreadPoolExecutor
    credentialslist = credentialslist

# ################################################################################################################################
# ################################################################################################################################

floatlist      = list[float]
futurelist     = list['Future[None]']
publisherlist  = list['Publisher']
subscriberlist = list['Subscriber']

# ################################################################################################################################
# ################################################################################################################################

# How long a request that did not reach the server waits before it is sent again, in seconds
_retry_seconds = 0.2

# How long a subscriber waits after a pull that returned nothing, in seconds
_idle_seconds = 0.05

# How long beyond the lease a subscriber waits for messages that a lost response handed out, in seconds
_lease_margin = 0.5

# How many messages one pull asks for
_batch_size = 100

# ################################################################################################################################
# ################################################################################################################################

def get_lease_wait() -> 'float':
    """ Returns how long it takes until a pulled message is handed out again, in seconds.
    """
    out = PerfConfig.lease_seconds + _lease_margin
    return out

# ################################################################################################################################

def get_receipt_key(key:'str', subscriber_name:'str') -> 'str':
    """ Returns the key of the receipt that a subscriber publishes for one message.
    """
    out = f'{key}.{subscriber_name}'
    return out

# ################################################################################################################################
# ################################################################################################################################

class Publisher:
    """ An API client that publishes messages under its own keys, one after another, as fast as the server confirms them.
    Each message has its key as the message ID, so a request sent again after an error stores nothing new.
    """

    def __init__(self, credentials:'Credentials', topic_name:'str', key_prefix:'str') -> 'None':
        self.credentials = credentials
        self.key_prefix = key_prefix
        self.path = f'/pubsub/topic/{topic_name}'

        self.keys:'strlist' = []
        self.sent_times:'floatlist' = []

# ################################################################################################################################

    def _publish_until_stored(self, key:'str') -> 'None':
        """ Publishes one message, repeating the request until the server confirms it.
        """
        payload:'anydict' = {
            'data': {'key': key},
            'msg_id': key,
            'correl_id': key,
        }

        sent_at = time.monotonic()

        while True:

            # A request whose connection a killed worker closed is sent again ..
            try:
                result = post_json(self.path, self.credentials.username, self.credentials.password, payload)
            except OSError:
                time.sleep(_retry_seconds)
                continue

            # .. as is one that the server did not complete ..
            if result.status_code >= INTERNAL_SERVER_ERROR:
                time.sleep(_retry_seconds)
                continue

            # .. while anything else is the response to the publication.
            assert result.status_code == OK, result

            self.keys.append(key)
            self.sent_times.append(sent_at)

            break

# ################################################################################################################################

    def run(self, deadline:'float') -> 'None':
        """ Publishes messages until the deadline.
        """
        sequence = 0

        while time.monotonic() < deadline:
            key = f'{self.key_prefix}{sequence:07d}'
            self._publish_until_stored(key)
            sequence += 1

# ################################################################################################################################
# ################################################################################################################################

class Subscriber:
    """ An API client with a pull subscription of its own. It acknowledges each batch with the delivery attempt
    of each of its messages and publishes one receipt per message in the same transaction. The server rejects
    the batch with a conflict if any of its messages was handed out again in the meantime.
    """

    def __init__(self, credentials:'Credentials') -> 'None':
        self.credentials = credentials
        self.name = credentials.username

        self.received_keys:'strlist' = []
        self.received_times:'floatlist' = []

# ################################################################################################################################

    def _pull(self) -> 'anylist':
        """ Returns the messages of one pull, or none if the response did not arrive, in which case the messages
        that it handed out are handed out again once their lease runs out.
        """
        payload = {'max_messages': _batch_size}

        try:
            result = post_json('/pubsub/messages/get', self.credentials.username, self.credentials.password, payload)
        except OSError:
            time.sleep(get_lease_wait())
            return []

        if result.status_code >= INTERNAL_SERVER_ERROR:
            time.sleep(get_lease_wait())
            return []

        assert result.status_code == OK, result

        out = result.body['messages']
        return out

# ################################################################################################################################

    def _build_ack(self, messages:'anylist') -> 'anydict':
        """ Returns the acknowledgement of a batch with the delivery attempt of each message and the receipt of each.
        """
        consumed:'anylist' = []
        receipts:'anylist' = []

        for message in messages:
            meta = message['meta']
            data = message['data']

            msg_id = meta['msg_id']
            delivery_attempt = meta['delivery_attempt']

            consumed_message = {
                'msg_id': msg_id,
                'delivery_attempt': delivery_attempt,
            }
            consumed.append(consumed_message)

            # A receipt committed by an earlier attempt would be stored again under another ID, which verification finds.
            receipt_key = get_receipt_key(data['key'], self.name)

            receipt = {
                'topic_name': Receipts_Topic,
                'data': {'key': receipt_key},
                'msg_id': f'{msg_id}.{self.name}.{delivery_attempt}',
                'correl_id': receipt_key,
            }
            receipts.append(receipt)

        out:'anydict' = {
            'consumed': consumed,
            'publish': receipts,
        }

        return out

# ################################################################################################################################

    def _ack(self, payload:'anydict') -> 'None':
        """ Sends one acknowledgement, repeating the same request until the server either commits it or rejects it.
        """
        while True:

            # The outcome of a request whose connection was closed is unknown, so the same request is sent again ..
            try:
                result = post_json('/pubsub/messages/ack', self.credentials.username, self.credentials.password, payload)
            except OSError:
                time.sleep(_retry_seconds)
                continue

            if result.status_code >= INTERNAL_SERVER_ERROR:
                time.sleep(_retry_seconds)
                continue

            # .. a batch handed out again is rejected with nothing committed ..
            if result.status_code == CONFLICT:
                break

            # .. and a committed one is complete, with its receipts counted in the database.
            assert result.status_code == OK, result

            break

# ################################################################################################################################

    def run(self, stop:'Event') -> 'None':
        """ Pulls and acknowledges messages until the test stops the subscriber.
        """
        while not stop.is_set():

            messages = self._pull()

            if not messages:
                time.sleep(_idle_seconds)
                continue

            received_at = time.monotonic()

            for message in messages:
                data = message['data']
                self.received_keys.append(data['key'])
                self.received_times.append(received_at)

            payload = self._build_ack(messages)
            self._ack(payload)

# ################################################################################################################################

    def get_first_receipts(self) -> 'strfloatdict':
        """ Returns the time that each key was first received at.
        """
        out:'strfloatdict' = {}

        for key, received_at in zip(self.received_keys, self.received_times):
            if key not in out:
                out[key] = received_at

        return out

# ################################################################################################################################
# ################################################################################################################################

class PublisherGroup:
    """ Publishers that publish to one topic concurrently, each under its own credentials and its own keys.
    """

    def __init__(self, credentials_list:'credentialslist', topic_name:'str', prefix:'str') -> 'None':

        self.publishers:'publisherlist' = []

        for index, credentials in enumerate(credentials_list):
            key_prefix = f'{prefix}{index:03d}.'
            publisher = Publisher(credentials, topic_name, key_prefix)
            self.publishers.append(publisher)

# ################################################################################################################################

    def submit(self, executor:'ThreadPoolExecutor', deadline:'float') -> 'futurelist':
        """ Starts every publisher, each of which publishes until the deadline.
        """
        out:'futurelist' = []

        for publisher in self.publishers:
            future = executor.submit(publisher.run, deadline)
            out.append(future)

        return out

# ################################################################################################################################

    def count_published(self) -> 'int':
        out = 0

        for publisher in self.publishers:
            out += len(publisher.keys)

        return out

# ################################################################################################################################

    def get_keys(self) -> 'strlist':
        """ Returns the keys of all the publishers.
        """
        out:'strlist' = []

        for publisher in self.publishers:
            out.extend(publisher.keys)

        return out

# ################################################################################################################################

    def get_sent_times(self) -> 'strfloatdict':
        """ Returns the time that the publication of each key was first sent at.
        """
        out:'strfloatdict' = {}

        for publisher in self.publishers:
            for key, sent_at in zip(publisher.keys, publisher.sent_times):
                out[key] = sent_at

        return out

# ################################################################################################################################
# ################################################################################################################################

class SubscriberGroup:
    """ Subscribers to one topic, each with a subscription of its own, so that each receives every message.
    """

    def __init__(self, credentials_list:'credentialslist') -> 'None':

        self.subscribers:'subscriberlist' = []

        for credentials in credentials_list:
            subscriber = Subscriber(credentials)
            self.subscribers.append(subscriber)

# ################################################################################################################################

    def submit(self, executor:'ThreadPoolExecutor', stop:'Event') -> 'futurelist':
        """ Starts every subscriber, each of which runs until the test stops it.
        """
        out:'futurelist' = []

        for subscriber in self.subscribers:
            future = executor.submit(subscriber.run, stop)
            out.append(future)

        return out

# ################################################################################################################################

    def get_names(self) -> 'strlist':
        out:'strlist' = []

        for subscriber in self.subscribers:
            out.append(subscriber.name)

        return out

# ################################################################################################################################

    def get_latencies(self, sent_times:'strfloatdict') -> 'Latencies':
        """ Returns the time from the publication of each message to its first receipt by each subscriber.
        """
        out = Latencies('Publication to delivery')

        for subscriber in self.subscribers:
            receipts = subscriber.get_first_receipts()

            for key, received_at in receipts.items():
                out.add(received_at - sent_times[key])

        return out

# ################################################################################################################################
# ################################################################################################################################
