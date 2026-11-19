# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from http.client import CONFLICT, INTERNAL_SERVER_ERROR, OK

# Zato
from pubsub_perf.config import PerfConfig, Receipts_Topic
from pubsub_perf.figures import Latencies
from pubsub_perf.payloads import build_documents
from pubsub_perf.rest import post_json

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from concurrent.futures import Future, ThreadPoolExecutor
    from threading import Event
    from pubsub_perf.config import Credentials, credentialslist
    from zato.common.typing_ import anydict, anylist, dictlist, strfloatdict, strlist, strstrdict

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

# How many messages one pull of a subscriber asks for, and how many receipts one pull of the receipt reader asks for,
# which is the most that the server hands out at once
_batch_size = 100
_receipt_batch_size = 1000

# ################################################################################################################################
# ################################################################################################################################

def _pull(credentials:'Credentials', max_messages:'int') -> 'anylist':
    """ Returns the messages of one pull, or none if the response did not arrive, in which case the messages
    that it handed out are handed out again once their lease runs out.
    """
    payload = {'max_messages': max_messages}

    try:
        result = post_json('/pubsub/messages/get', credentials.username, credentials.password, payload)
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

def get_lease_wait() -> 'float':
    """ Returns how long it takes until a pulled message is handed out again, in seconds.
    """
    out = PerfConfig.lease_seconds + _lease_margin
    return out

# ################################################################################################################################

def _get_key_prefix(prefix:'str', index:'int') -> 'str':
    """ Returns the prefix of the keys of the publisher of the given index.
    """
    out = f'{prefix}{index:03d}.'
    return out

# ################################################################################################################################

def _get_key(key_prefix:'str', sequence:'int') -> 'str':
    """ Returns the key of the message of the given sequence number of a publisher.
    """
    out = f'{key_prefix}{sequence:07d}'
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
    Each message carries the next of the documents of the run, starting from the offset of the publisher.
    """

    def __init__(
        self,
        credentials:'Credentials',
        topic_name:'str',
        key_prefix:'str',
        documents:'dictlist',
        offset:'int',
        ) -> 'None':
        self.credentials = credentials
        self.key_prefix = key_prefix
        self.path = f'/pubsub/topic/{topic_name}'
        self.documents = documents
        self.offset = offset

        self.keys:'strlist' = []
        self.sent_times:'floatlist' = []

        # How long the publication of each message took, from the first request until the server confirmed it
        self.publish_durations:'floatlist' = []

# ################################################################################################################################

    def _publish_until_stored(self, key:'str', document:'anydict') -> 'None':
        """ Publishes one message, repeating the request until the server confirms it.
        """
        payload:'anydict' = {
            'data': {'key': key, 'document': document},
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
            self.publish_durations.append(time.monotonic() - sent_at)

            break

# ################################################################################################################################

    def run(self, deadline:'float') -> 'None':
        """ Publishes messages until the deadline.
        """
        sequence = 0
        document_count = len(self.documents)

        while time.monotonic() < deadline:
            key = _get_key(self.key_prefix, sequence)

            document_index = (self.offset + sequence) % document_count
            document = self.documents[document_index]

            self._publish_until_stored(key, document)
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

            # .. and a committed one is complete, with its receipts published.
            assert result.status_code == OK, result

            break

# ################################################################################################################################

    def run(self, stop:'Event') -> 'None':
        """ Pulls and acknowledges messages until the test stops the subscriber.
        """
        while not stop.is_set():

            messages = _pull(self.credentials, _batch_size)

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
    """ Publishers that publish to one topic concurrently, each under its own credentials and its own keys,
    and each with the documents of the run from an offset of its own, spread evenly over the documents.
    """

    def __init__(self, credentials_list:'credentialslist', topic_name:'str', prefix:'str') -> 'None':

        self.publishers:'publisherlist' = []

        # Every key of the run has the same length, which the size of each message accounts for.
        first_key = _get_key(_get_key_prefix(prefix, 0), 0)
        documents = build_documents(len(first_key))

        document_count = len(documents)
        publisher_count = len(credentials_list)

        for index, credentials in enumerate(credentials_list):
            key_prefix = _get_key_prefix(prefix, index)
            offset = index * document_count // publisher_count
            publisher = Publisher(credentials, topic_name, key_prefix, documents, offset)
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

    def get_publish_latencies(self) -> 'Latencies':
        """ Returns how long the publication of each message took, from the first request until the server confirmed it.
        """
        out = Latencies()

        for publisher in self.publishers:
            for duration in publisher.publish_durations:
                out.add(duration)

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
        out = Latencies()

        for subscriber in self.subscribers:
            receipts = subscriber.get_first_receipts()

            for key, received_at in receipts.items():
                out.add(received_at - sent_times[key])

        return out

# ################################################################################################################################
# ################################################################################################################################

class ReceiptReader:
    """ An API client subscribed to the receipts of every subscriber. It pulls and acknowledges them throughout
    a run and keeps those of the run by their message IDs, so that a receipt handed out to it again is counted once.
    """

    def __init__(self, credentials:'Credentials', prefix:'str') -> 'None':
        self.credentials = credentials
        self.prefix = prefix

        # The key of each receipt of the run, by the message ID of the receipt
        self.receipts:'strstrdict' = {}

# ################################################################################################################################

    def _ack(self, msg_ids:'strlist') -> 'None':
        """ Acknowledges the receipts of one pull, repeating the request until the server confirms it.
        """
        payload = {'msg_ids': msg_ids}

        while True:

            try:
                result = post_json('/pubsub/messages/ack', self.credentials.username, self.credentials.password, payload)
            except OSError:
                time.sleep(_retry_seconds)
                continue

            if result.status_code >= INTERNAL_SERVER_ERROR:
                time.sleep(_retry_seconds)
                continue

            assert result.status_code == OK, result

            break

# ################################################################################################################################

    def run(self, stop:'Event') -> 'None':
        """ Pulls and acknowledges receipts until the test stops the reader.
        """
        while not stop.is_set():

            messages = _pull(self.credentials, _receipt_batch_size)

            if not messages:
                time.sleep(_idle_seconds)
                continue

            msg_ids:'strlist' = []

            for message in messages:
                meta = message['meta']
                data = message['data']

                msg_id = meta['msg_id']
                receipt_key = data['key']

                msg_ids.append(msg_id)

                # Receipts of earlier runs are acknowledged and not kept.
                if receipt_key.startswith(self.prefix):
                    self.receipts[msg_id] = receipt_key

            self._ack(msg_ids)

# ################################################################################################################################

    def get_receipt_keys(self) -> 'strlist':
        """ Returns the key of each receipt of the run, once per receipt that the subscribers committed.
        """
        out = list(self.receipts.values())
        return out

# ################################################################################################################################
# ################################################################################################################################
