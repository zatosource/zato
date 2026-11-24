# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The production traffic of a pub/sub suite through the REST interface of a server - API clients publishing
# the production documents at a controlled rate to the queues of pull partners and to a broadcast topic
# whose subscribers the server pushes to, with mixed priorities and expirations.

# stdlib
import os
from collections import Counter
from dataclasses import dataclass, field
from time import monotonic

# gevent
from gevent import sleep, spawn
from gevent.lock import RLock

# Zato
from pubsub_rest.documents import get_production_documents
from pubsub_rest.receiver import PushReceiver
from pubsub_rest.transport import RESTClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_rest.definition import Definition
    from pubsub_rest.latency import latency_list
    from pubsub_rest.receiver import Push
    from pubsub_rest.server import PubSubServer
    from pubsub_rest.transport import credentials_list
    from zato.common.typing_ import anydict, anylist, strlist, strset

    strcounter = Counter[str]
    rest_client_list = list[RESTClient]

# ################################################################################################################################
# ################################################################################################################################

# What separates the key of a broadcast at the start of its data from the document that follows it.
_broadcast_key_separator = '\n'

# How many messages one pull of a partner asks for and how many bytes it may return at most, which are
# the maximums of the REST interface, and how long a partner waits before it pulls again from an empty queue, in seconds.
_pull_max_messages = 1000
_pull_max_len = 5_000_000
_pull_poll_seconds = 0.2

# How long a partner waits after a pull that failed, in seconds.
_pull_error_seconds = 1

# The priorities of the publications, cycled through by the API clients.
_priorities = [5, 5, 5, 7, 3, 9, 5, 1]

# The expirations of the publications, in seconds, of which zero is the default expiration of the server.
Default_Expiration = 0
Production_Expirations = [Default_Expiration, 86_400, 3_600, 7 * 86_400]

# Documents above this size are published once per cycle of the traffic and the others this many times,
# which keeps the large documents as rare as they are in production.
_large_document_size = 1_000_000
_small_document_repeats = 20

# How many error messages of one minute are kept, and how long each of them is at most.
_max_error_messages = 5
_max_error_length = 300

# How often the drain of the traffic is checked, in seconds.
_drain_check_seconds = 0.5

# The variable of the publication rate of the traffic.
_env_rate = 'Zato_Test_Stability_Rate'

# The path of the push endpoint of each broadcast subscriber.
_push_path_prefix = '/push/'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
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

@dataclass(init=False)
class MinuteCounters:
    """ What happened in one minute of traffic.
    """
    published: 'int' = 0
    published_bytes: 'int' = 0
    pulled: 'int' = 0
    pushed: 'int' = 0
    errors: 'int' = 0

    # Each latency is the moment its publication began, by the monotonic clock, and the seconds it took
    # to be published, pulled or pushed.
    publish_seconds: 'latency_list' = field(default_factory=list)
    pull_seconds: 'latency_list' = field(default_factory=list)
    push_seconds: 'latency_list' = field(default_factory=list)
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

def _new_minute() -> 'MinuteCounters':
    out = MinuteCounters()
    out.publish_seconds = []
    out.pull_seconds = []
    out.push_seconds = []
    out.error_messages = []

    return out

# ################################################################################################################################
# ################################################################################################################################

class Traffic:
    """ Runs the production traffic of one profile against the REST interface of a server.
    """

    def __init__(self, profile:'TrafficProfile') -> 'None':
        self.profile = profile
        self.documents = _weight_documents(get_production_documents())

        self.rate = profile.publish_rate
        self.expirations = Production_Expirations

        # How many publications the API clients make in total, if a suite limits them, and how many they began.
        self.publish_limit:'int | None' = None
        self.publish_started = 0
        self.is_publishing = False
        self.is_consuming = False

        self.lock = RLock()
        self.minute = _new_minute()

        # The totals of the whole run, which the final checks compare.
        self.total_published = 0
        self.total_broadcast = 0
        self.total_pulled = 0
        self.total_pushed = 0
        self.total_errors = 0

        # When each message for a pull partner was published, by its identifier.
        self.publish_times:'anydict' = {}

        # When each broadcast began to be published and how many of its pushes are still to arrive, by its key.
        # The time is taken before the publication, because the server may push a broadcast before its publisher
        # receives the response, and a broadcast leaves the dict once each of its subscribers received it.
        self.broadcast_times:'anydict' = {}
        self.broadcast_pending:'strcounter' = Counter()

        # The partners that do not pull for now, those whose delivery latency is not measured,
        # and the deliveries that a suite placed in the queues itself less those it removed, apart from the publications.
        self.paused_sub_keys:'strset' = set()
        self.unmeasured_sub_keys:'strset' = set()
        self.extra_deliveries = 0

        # Whether the traffic records each delivery, which lets a suite account for every publication - how many partner
        # messages were acknowledged to their API clients, the acknowledged ones not pulled yet and the pulled ones
        # not acknowledged yet, by msg_id, and the broadcasts acknowledged to their API clients and how many times
        # each was pushed, by the key that each broadcast begins with. A partner message leaves both sets
        # once it is both acknowledged and pulled, which keeps their size bounded by the messages in flight.
        self.tracks_deliveries = False
        self.acknowledged_partner_count = 0
        self.unpulled_partner_msg_ids:'strset' = set()
        self.unacknowledged_pulled_msg_ids:'strset' = set()
        self.acknowledged_broadcast_keys:'strset' = set()
        self.pushed_broadcast_keys:'strcounter' = Counter()

        # The topics, the credentials of the API clients, partners and broadcast subscribers, and the subscription keys
        # of the partners and of the broadcast subscribers, which the server assigns.
        prefix = profile.topic_prefix

        self.partner_topics:'strlist' = []
        self.broadcast_topic = f'{prefix}.broadcast'

        self.publisher_credentials:'credentials_list' = []
        self.partner_credentials:'credentials_list' = []
        self.broadcast_credentials:'credentials_list' = []

        self.partner_sub_keys:'strlist' = []
        self.broadcast_sub_keys:'strlist' = []

        self.publishers:'rest_client_list' = []
        self.partners:'rest_client_list' = []

        self._publisher_greenlets:'anylist' = []
        self._consumer_greenlets:'anylist' = []

# ################################################################################################################################

    def get_partner_name(self, partner_index:'int') -> 'str':
        """ The name of the topic of a partner, which is also the name of its security definition.
        """
        out = f'{self.profile.topic_prefix}.partner.{partner_index:04d}'
        return out

# ################################################################################################################################

    def define(self, server:'PubSubServer', definition:'Definition') -> 'None':
        """ Adds the topics, the API clients, the partners and the broadcast subscribers to the definition
        of the server, and starts the endpoint that the server pushes the broadcasts to.
        """
        profile = self.profile
        prefix = profile.topic_prefix

        for partner_index in range(profile.partner_count):
            self.partner_topics.append(self.get_partner_name(partner_index))

        # The API clients may publish to every topic of the traffic ..
        publisher_topics = self.partner_topics + [self.broadcast_topic]

        for publisher_index in range(profile.publisher_count):
            username = f'{prefix}.publisher.{publisher_index:04d}'
            credentials = definition.add_publisher(username, publisher_topics)
            self.publisher_credentials.append(credentials)

        # .. each partner pulls from its topic ..
        for topic_name in self.partner_topics:
            credentials = definition.add_pull_subscriber(topic_name, [topic_name])
            self.partner_credentials.append(credentials)

        # .. and the server pushes each broadcast to the endpoint of each broadcast subscriber.
        receiver = PushReceiver(self.on_push)
        server.add_receiver(receiver)

        for subscriber_index in range(profile.broadcast_subscriber_count):
            username = f'{prefix}.broadcast.{subscriber_index:04d}'
            url_path = f'{_push_path_prefix}{subscriber_index:04d}'
            credentials = definition.add_push_subscriber(username, [self.broadcast_topic], receiver.port, url_path)
            self.broadcast_credentials.append(credentials)

        server.ready_callbacks.append(lambda: self.attach(server))

# ################################################################################################################################

    def attach(self, server:'PubSubServer') -> 'None':
        """ Creates the REST clients of the running server and reads the subscription keys that it assigned.
        """
        sub_keys = server.get_sub_keys()

        for credentials in self.publisher_credentials:
            self.publishers.append(RESTClient(server.base_url, credentials))

        for credentials in self.partner_credentials:
            self.partners.append(RESTClient(server.base_url, credentials))
            self.partner_sub_keys.append(sub_keys[credentials.username])

        for credentials in self.broadcast_credentials:
            self.broadcast_sub_keys.append(sub_keys[credentials.username])

# ################################################################################################################################

    def on_push(self, push:'Push') -> 'bool':
        """ Counts a broadcast that the server pushed, which each broadcast subscriber accepts,
        and records the time the broadcast took to reach the subscriber.
        """
        now = monotonic()

        data = push.envelope['data']
        key = data.split(_broadcast_key_separator, 1)[0]

        with self.lock:
            self.minute.pushed += 1
            self.total_pushed += 1

            # A push that repeats a delivery after each subscriber already received the broadcast is not measured again ..
            if key in self.broadcast_times:
                started = self.broadcast_times[key]
                self.minute.push_seconds.append((started, now - started))

                # .. and the broadcast stops being tracked once its last subscriber received it.
                self.broadcast_pending[key] -= 1
                if self.broadcast_pending[key] == 0:
                    del self.broadcast_times[key]
                    del self.broadcast_pending[key]

            if self.tracks_deliveries:
                self.pushed_broadcast_keys[key] += 1

        return True

# ################################################################################################################################

    def record_error(self, error:'Exception') -> 'None':
        with self.lock:
            self.minute.errors += 1
            self.total_errors += 1

            if len(self.minute.error_messages) < _max_error_messages:
                message = f'{error.__class__.__name__}: {error}'
                self.minute.error_messages.append(message[:_max_error_length])

# ################################################################################################################################

    def _publish_loop(self, publisher_index:'int') -> 'None':
        """ What one API client runs - a publication at its share of the rate, cycling through the documents,
        the partners, the priorities and the expirations.
        """
        profile = self.profile
        client = self.publishers[publisher_index]
        position = publisher_index

        # The clients start spread over one interval, as independent clients do, rather than all at the same instant.
        first_interval = profile.publisher_count / self.rate
        sleep(first_interval * publisher_index / profile.publisher_count)

        while self.is_publishing:

            # A client stops once all the API clients together began as many publications as the suite allows ..
            if self.publish_limit is not None:
                with self.lock:
                    if self.publish_started == self.publish_limit:
                        break
                    self.publish_started += 1

            # .. and otherwise it publishes at its share of the current rate ..
            interval = profile.publisher_count / self.rate
            started = monotonic()

            document = self.documents[position % len(self.documents)]
            priority = _priorities[position % len(_priorities)]
            expiration = self.expirations[position % len(self.expirations)]

            # .. every so often to the broadcast topic and otherwise to the queue of one partner ..
            is_broadcast = position % profile.broadcast_every == 0

            if is_broadcast:
                topic_name = self.broadcast_topic
            else:
                topic_name = self.partner_topics[position % len(self.partner_topics)]

            # .. a broadcast begins with its key, which is its position, unique across all the API clients ..
            broadcast_key = f'{position}'

            if is_broadcast:
                document = broadcast_key + _broadcast_key_separator + document

                with self.lock:
                    self.broadcast_times[broadcast_key] = started
                    self.broadcast_pending[broadcast_key] = profile.broadcast_subscriber_count

            payload:'anydict' = {
                'data': document,
                'priority': priority,
            }

            if expiration != Default_Expiration:
                payload['expiration'] = expiration

            try:
                result = client.publish(topic_name, payload)
            except Exception as e:
                self.record_error(e)
            else:
                elapsed = monotonic() - started
                msg_id = result['msg_id']

                with self.lock:
                    self.minute.published += 1
                    self.minute.published_bytes += len(document)
                    self.minute.publish_seconds.append((started, elapsed))
                    self.total_published += 1

                    if is_broadcast:
                        self.total_broadcast += 1
                        if self.tracks_deliveries:
                            self.acknowledged_broadcast_keys.add(broadcast_key)
                    else:
                        self.publish_times[msg_id] = started
                        if self.tracks_deliveries:
                            self.acknowledged_partner_count += 1
                            if msg_id in self.unacknowledged_pulled_msg_ids:
                                self.unacknowledged_pulled_msg_ids.remove(msg_id)
                            else:
                                self.unpulled_partner_msg_ids.add(msg_id)

            position += profile.publisher_count

            # .. and the client waits for the rest of its interval, which a slow publication shortens.
            remaining = interval - (monotonic() - started)

            if remaining > 0:
                sleep(remaining)
            else:
                sleep(0)

# ################################################################################################################################

    def _on_pulled(self, sub_key:'str', msg_ids:'strlist') -> 'None':
        """ Records the messages that a partner received and the time each of them took to reach it.
        """
        now = monotonic()
        is_measured = sub_key not in self.unmeasured_sub_keys

        with self.lock:
            for msg_id in msg_ids:
                if msg_id in self.publish_times:
                    started = self.publish_times.pop(msg_id)
                    if is_measured:
                        self.minute.pull_seconds.append((started, now - started))

            self.minute.pulled += len(msg_ids)
            self.total_pulled += len(msg_ids)

            if self.tracks_deliveries:
                for msg_id in msg_ids:
                    if msg_id in self.unpulled_partner_msg_ids:
                        self.unpulled_partner_msg_ids.remove(msg_id)
                    else:
                        self.unacknowledged_pulled_msg_ids.add(msg_id)

# ################################################################################################################################

    def _pull_loop(self, partner_index:'int') -> 'None':
        """ What one pull partner runs - pulls that lease the messages, each followed by an acknowledgment
        that removes them from the queue, polling again shortly when the queue was empty.
        """
        client = self.partners[partner_index]
        sub_key = self.partner_sub_keys[partner_index]

        while self.is_consuming:

            if sub_key in self.paused_sub_keys:
                sleep(_pull_poll_seconds)
                continue

            try:
                result = client.pull(_pull_max_messages, _pull_max_len)
            except Exception as e:
                self.record_error(e)
                sleep(_pull_error_seconds)
                continue

            messages = result['messages']

            if not messages:
                sleep(_pull_poll_seconds)
                continue

            msg_ids:'strlist' = []

            for message in messages:
                msg_ids.append(message['meta']['msg_id'])

            self._on_pulled(sub_key, msg_ids)

            # The partner acknowledges what it received - messages whose acknowledgment fails
            # are handed out again once their lease runs out.
            try:
                _ = client.ack(msg_ids)
            except Exception as e:
                self.record_error(e)

            sleep(0)

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the partners and the API clients. The server pushes to the broadcast subscribers itself.
        """
        self.is_consuming = True
        self.is_publishing = True

        for partner_index in range(len(self.partners)):
            self._consumer_greenlets.append(spawn(self._pull_loop, partner_index))

        for publisher_index in range(len(self.publishers)):
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

    def get_backlog(self) -> 'int':
        out = self.expected_deliveries() - self.delivered()
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
            sleep(_drain_check_seconds)

        out = monotonic() - start
        return out

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the API clients and the partners.
        """
        self.stop_publishing()
        self.is_consuming = False

        for greenlet in self._consumer_greenlets:
            _ = greenlet.join()

        self._consumer_greenlets = []

        for client in self.publishers + self.partners:
            client.close()

# ################################################################################################################################

    def take_minute(self) -> 'MinuteCounters':
        """ Returns the counters of the minute that ends now and starts a new one.
        """
        with self.lock:
            out = self.minute
            self.minute = _new_minute()

        return out

# ################################################################################################################################

    def get_totals(self) -> 'anydict':
        out = {
            'published': self.total_published,
            'broadcast': self.total_broadcast,
            'pulled': self.total_pulled,
            'pushed': self.total_pushed,
            'errors': self.total_errors,
        }

        return out

# ################################################################################################################################
# ################################################################################################################################

def get_traffic_profile() -> 'TrafficProfile':
    """ The production profile, with the rate that Zato_Test_Stability_Rate may override.
    """
    out = TrafficProfile()

    if rate := os.environ.get(_env_rate, ''):
        out.publish_rate = float(rate)

    return out

# ################################################################################################################################
# ################################################################################################################################
