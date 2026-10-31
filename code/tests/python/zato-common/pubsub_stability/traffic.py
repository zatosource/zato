# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The production traffic of the stability suites - API clients publishing the production documents at a controlled rate
# to the queues of pull partners and to a broadcast topic with push subscribers, with mixed priorities and expirations.

# stdlib
import os
from dataclasses import dataclass, field
from time import monotonic

# gevent
from gevent import sleep, spawn
from gevent.lock import RLock

# Zato
from production_documents import get_production_documents
from zato.common.api import PubSub
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.typing_ import cast_
from zato.server.base.parallel.delivery import PushDelivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

# The service that the push subscribers of the broadcast topic invoke.
_push_service_name = 'stability.push.target'

# How many messages one pull of a partner asks for, which is the maximum of the REST API,
# and how long a partner waits before it pulls again from a queue that was empty, in seconds.
_pull_max_messages = 1000
_pull_poll_seconds = 0.2

# The priorities and expirations of the publications, cycled through by the API clients.
_priorities = [5, 5, 5, 7, 3, 9, 5, 1]
_expirations = [PubSub.Message.Default_Expiration, 86_400, 3_600, 7 * 86_400]

# Documents above this size are published once per cycle of the traffic and the others this many times,
# which keeps the large documents as rare as they are in production.
_large_document_size = 1_000_000
_small_document_repeats = 20

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class TrafficProfile:
    """ The shape of the production traffic - the API clients, the partners and the broadcast subscribers.
    """
    publisher_count: 'int' = 200
    partner_count: 'int' = 50
    broadcast_subscriber_count: 'int' = 200
    publish_rate: 'float' = 100.0
    broadcast_every: 'int' = 20
    topic_prefix: 'str' = 'stability'

# ################################################################################################################################

@dataclass
class MinuteCounters:
    """ What happened in one minute of traffic.
    """
    published: 'int' = 0
    published_bytes: 'int' = 0
    pulled: 'int' = 0
    pushed: 'int' = 0
    errors: 'int' = 0
    publish_seconds: 'list[float]' = field(default_factory=list)
    delivery_seconds: 'list[float]' = field(default_factory=list)
    error_messages: 'strlist' = field(default_factory=list)

# ################################################################################################################################
# ################################################################################################################################

def _weight_documents(documents:'strlist') -> 'strlist':
    """ One cycle of the traffic, in which each large document appears once and each other one many times,
    the repetitions spread over the cycle.
    """
    out:'strlist' = []

    for repeat in range(_small_document_repeats):
        for document in documents:
            is_large = len(document) > _large_document_size
            if repeat == 0 or not is_large:
                out.append(document)

    return out

# ################################################################################################################################
# ################################################################################################################################

class _StubConfigManager:
    """ Holds the push subscriptions the way the configuration manager of a server does.
    """
    def __init__(self) -> 'None':
        self._push_subs:'anydict' = {}

# ################################################################################################################################

class _StubServer:
    """ Receives the push deliveries in place of a server's services, counting each one.
    """
    def __init__(self, traffic:'Traffic') -> 'None':
        self.config_manager = _StubConfigManager()
        self.traffic = traffic

    def invoke(self, service_name:'str', payload:'any_', data_format:'strnone'=None) -> 'None':
        self.traffic.on_pushed()

        # A real invocation yields on its network I/O, which lets the other greenlets run.
        sleep(0)

# ################################################################################################################################
# ################################################################################################################################

class Traffic:
    """ Runs the production traffic of one profile against the pub/sub database of the environment.
    """

    def __init__(self, profile:'TrafficProfile') -> 'None':
        self.profile = profile
        self.backend = SQLPubSubBackend()
        self.documents = _weight_documents(get_production_documents())

        self.rate = profile.publish_rate
        self.is_publishing = False
        self.is_consuming = False

        self.lock = RLock()
        self.minute = MinuteCounters()

        # The totals of the whole run, which the final checks compare.
        self.total_published = 0
        self.total_broadcast = 0
        self.total_pulled = 0
        self.total_pushed = 0
        self.total_errors = 0

        # When each message for a pull partner was published, by its identifier.
        self.publish_times:'anydict' = {}

        # The partners that do not pull for now, those whose delivery latency is not measured,
        # and the deliveries that a suite placed in the queues itself less those it removed, apart from the publications.
        self.paused_sub_keys:'set[str]' = set()
        self.unmeasured_sub_keys:'set[str]' = set()
        self.extra_deliveries = 0

        self.partner_topics:'strlist' = []
        self.partner_sub_keys:'strlist' = []
        self.broadcast_topic = f'{profile.topic_prefix}.broadcast'
        self.broadcast_sub_keys:'strlist' = []

        self.server = _StubServer(self)
        self.push_delivery = PushDelivery(cast_('any_', self.server), self.backend)

        self._publisher_greenlets:'anylist' = []
        self._consumer_greenlets:'anylist' = []

# ################################################################################################################################

    def subscribe_all(self) -> 'None':
        """ Subscribes the pull partners to their queues and the push subscribers to the broadcast topic.
        """
        prefix = self.profile.topic_prefix

        for partner_index in range(self.profile.partner_count):

            topic_name = f'{prefix}.partner.{partner_index:04d}'
            sub_key = f'zpsk.{prefix}.partner.{partner_index:04d}'

            self.partner_topics.append(topic_name)
            self.partner_sub_keys.append(sub_key)
            self.backend.subscribe(sub_key, topic_name)

        for subscriber_index in range(self.profile.broadcast_subscriber_count):

            sub_key = f'zpsk.{prefix}.broadcast.{subscriber_index:04d}'

            self.broadcast_sub_keys.append(sub_key)
            self.backend.subscribe(sub_key, self.broadcast_topic)

            self.server.config_manager._push_subs[sub_key] = [{
                'topic_name': self.broadcast_topic,
                'push_type': PubSub.Push_Type.Service,
                'push_service_name': _push_service_name,
            }]

# ################################################################################################################################

    def on_pushed(self) -> 'None':
        with self.lock:
            self.minute.pushed += 1
            self.total_pushed += 1

# ################################################################################################################################

    def _record_error(self, error:'Exception') -> 'None':
        with self.lock:
            self.minute.errors += 1
            self.total_errors += 1
            if len(self.minute.error_messages) < 5:
                self.minute.error_messages.append(f'{error.__class__.__name__}: {error}'[:300])

# ################################################################################################################################

    def _publish_loop(self, publisher_index:'int') -> 'None':
        """ What one API client runs - a publication at its share of the rate, cycling through the documents,
        the partners, the priorities and the expirations.
        """
        position = publisher_index

        # The clients start spread over one interval, as independent clients do, rather than all at the same instant.
        first_interval = self.profile.publisher_count / self.rate
        sleep(first_interval * publisher_index / self.profile.publisher_count)

        while self.is_publishing:

            # Each client publishes at its share of the current rate ..
            interval = self.profile.publisher_count / self.rate
            started = monotonic()

            document = self.documents[position % len(self.documents)]
            priority = _priorities[position % len(_priorities)]
            expiration = _expirations[position % len(_expirations)]

            # .. every so often to the broadcast topic and otherwise to the queue of one partner.
            is_broadcast = position % self.profile.broadcast_every == 0

            if is_broadcast:
                topic_name = self.broadcast_topic
            else:
                topic_name = self.partner_topics[position % len(self.partner_topics)]

            try:
                result = self.backend.publish(topic_name, document, priority=priority, expiration=expiration)
            except Exception as e:
                self._record_error(e)
            else:
                elapsed = monotonic() - started

                with self.lock:
                    self.minute.published += 1
                    self.minute.published_bytes += len(document)
                    self.minute.publish_seconds.append(elapsed)
                    self.total_published += 1

                    if is_broadcast:
                        self.total_broadcast += 1
                    else:
                        self.publish_times[result.msg_id] = started

            position += self.profile.publisher_count

            # The client waits for the rest of its interval, which a slow publication shortens.
            remaining = interval - (monotonic() - started)

            if remaining > 0:
                sleep(remaining)
            else:
                sleep(0)

# ################################################################################################################################

    def _pull_loop(self, sub_key:'str') -> 'None':
        """ What one pull partner runs - pulls through the path of the REST API, each of which hands the messages
        over and removes them from the queue, polling again shortly when the queue was empty.
        """
        while self.is_consuming:

            if sub_key in self.paused_sub_keys:
                sleep(_pull_poll_seconds)
                continue

            try:
                messages = self.backend.pull_messages(sub_key, max_messages=_pull_max_messages)

            except Exception as e:
                self._record_error(e)
                sleep(1)
                continue

            if not messages:
                sleep(_pull_poll_seconds)
                continue

            msg_ids:'strlist' = []

            for message in messages:
                msg_ids.append(message['msg_id'])

            now = monotonic()
            is_measured = sub_key not in self.unmeasured_sub_keys

            with self.lock:
                for msg_id in msg_ids:
                    started = self.publish_times.pop(msg_id, None)
                    if started is not None and is_measured:
                        self.minute.delivery_seconds.append(now - started)

                self.minute.pulled += len(msg_ids)
                self.total_pulled += len(msg_ids)

            sleep(0)

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the partners, the push subscribers and the API clients.
        """
        self.is_consuming = True
        self.is_publishing = True

        for sub_key in self.partner_sub_keys:
            self._consumer_greenlets.append(spawn(self._pull_loop, sub_key))

        for sub_key in self.broadcast_sub_keys:
            self.push_delivery.start_sub_key(sub_key)

        for publisher_index in range(self.profile.publisher_count):
            self._publisher_greenlets.append(spawn(self._publish_loop, publisher_index))

# ################################################################################################################################

    def set_rate(self, rate:'float') -> 'None':
        self.rate = rate

# ################################################################################################################################

    def stop_publishing(self) -> 'None':
        self.is_publishing = False

        for greenlet in self._publisher_greenlets:
            _ = greenlet.join()

        self._publisher_greenlets = []

# ################################################################################################################################

    def expected_deliveries(self) -> 'int':
        """ How many deliveries the publications so far require, one per partner message and one per broadcast subscriber.
        """
        partner_messages = self.total_published - self.total_broadcast
        broadcast_deliveries = self.total_broadcast * len(self.broadcast_sub_keys)

        out = partner_messages + broadcast_deliveries + self.extra_deliveries
        return out

# ################################################################################################################################

    def delivered(self) -> 'int':
        out = self.total_pulled + self.total_pushed
        return out

# ################################################################################################################################

    def wait_until_drained(self, timeout_seconds:'float') -> 'float':
        """ Waits until every publication was delivered and returns how long it took, in seconds.
        """
        start = monotonic()
        deadline = start + timeout_seconds

        while self.delivered() < self.expected_deliveries():
            assert monotonic() < deadline, f'Delivered {self.delivered()} of {self.expected_deliveries()} ' + \
                f'after {timeout_seconds}s, published {self.total_published}, broadcast {self.total_broadcast}, ' + \
                f'pulled {self.total_pulled}, pushed {self.total_pushed}, errors {self.total_errors}'
            sleep(0.5)

        out = monotonic() - start
        return out

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the API clients, the partners and the push subscribers.
        """
        self.stop_publishing()
        self.is_consuming = False

        for greenlet in self._consumer_greenlets:
            _ = greenlet.join()

        self._consumer_greenlets = []
        self.push_delivery.stop()

# ################################################################################################################################

    def take_minute(self) -> 'MinuteCounters':
        """ Returns the counters of the minute that ends now and starts a new one.
        """
        with self.lock:
            out = self.minute
            self.minute = MinuteCounters()

        return out
# ################################################################################################################################
# ################################################################################################################################

def get_traffic_profile() -> 'TrafficProfile':
    """ The production profile, with the rate that Zato_Test_Stability_Rate may override.
    """
    out = TrafficProfile()

    if rate := os.environ.get('Zato_Test_Stability_Rate', ''):
        out.publish_rate = float(rate)

    return out

# ################################################################################################################################
# ################################################################################################################################
