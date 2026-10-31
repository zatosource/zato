# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The traffic of the replication suites - publishers that repeat a publication under its own msg_id until it is
# acknowledged, a pull partner, a push subscriber and a cleanup process, each recording when it failed and when it
# resumed, so that a test can account for every acknowledged publication across a fault of the database.

# stdlib
from dataclasses import dataclass, field
from time import monotonic

# gevent
from gevent import sleep, spawn
from gevent.lock import RLock

# Zato
from zato.common.api import PubSub
from zato.common.crypto.api import CryptoManager
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.cleanup import PubSubCleanup
from zato.common.typing_ import cast_
from zato.server.base.parallel.delivery import PushDelivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

# The topics and subscribers of the workload.
Pull_Topic    = 'replication.pull'
Pull_Sub_Key  = 'zpsk.replication.pull'
Push_Topic    = 'replication.push'
Push_Sub_Key  = 'zpsk.replication.push'

# The service that the push subscriber invokes.
_push_service_name = 'replication.push.target'

# How many publishers run at once, and how long each waits between two of its publications, in seconds.
_publisher_count = 8
_publish_interval = 0.02

# How long a component waits before it repeats an operation that failed, in seconds.
_retry_sleep = 0.1

# What separates the msg_id at the start of a payload from the padding that follows it.
_payload_separator = ':'

# How many bits of randomness one hex digit of the padding holds.
_bits_per_hex_digit = 4

# How many messages one pull asks for, how long the partner waits after an empty pull, in seconds,
# and how often the cleanup process sweeps, in seconds.
_pull_max_messages = 100
_pull_poll_seconds = 0.1
_cleanup_interval = 1.0

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ComponentState:
    """ The failures of one component and the moments at which it succeeded.
    """
    errors: 'int' = 0
    success_times: 'list[float]' = field(default_factory=list)
    error_messages: 'strlist' = field(default_factory=list)

    def resumed_after(self, restore_time:'float') -> 'float':
        """ How long after the database became available again the component first succeeded, in seconds.
        """
        for success_time in self.success_times:
            if success_time > restore_time:
                out = round(success_time - restore_time, 3)
                return out

        out = -1.0
        return out

# ################################################################################################################################
# ################################################################################################################################

class _StubConfigManager:
    def __init__(self) -> 'None':
        self._push_subs:'anydict' = {}

# ################################################################################################################################

class _StubServer:
    """ Receives the push deliveries in place of a server's services. The payload of each message is its msg_id.
    """
    def __init__(self, workload:'Workload') -> 'None':
        self.config_manager = _StubConfigManager()
        self.workload = workload

    def invoke(self, service_name:'str', payload:'any_', data_format:'strnone'=None) -> 'None':
        msg_id = payload.split(_payload_separator, 1)[0]
        self.workload.on_pushed(msg_id)
        sleep(0)

# ################################################################################################################################
# ################################################################################################################################

class Workload:
    """ Runs the publishers, the pull partner, the push subscriber and the cleanup process of one test.
    """

    def __init__(self, label:'str', padding_size:'int'=0) -> 'None':
        self.label = label
        self.backend = SQLPubSubBackend()

        # Each payload is its msg_id, followed by random padding when the test needs large payloads.
        if padding_size:
            self.padding = _payload_separator + CryptoManager.generate_hex_string(padding_size * _bits_per_hex_digit)
        else:
            self.padding = ''
        self.lock = RLock()

        self.is_publishing = False
        self.is_consuming = False

        # Every publication acknowledged to a publisher, by its msg_id, with the moment of the acknowledgement.
        self.acknowledged:'dict[str, float]' = {}

        # How many attempts each publication needed, and the publications that needed more than one.
        self.repeated_publications:'strlist' = []

        # What the partner pulled and what the push subscriber received, in order and with repetitions.
        self.pulled:'strlist' = []
        self.pushed:'strlist' = []

        # The moments at which a pull was sent whose response did not arrive.
        self.failed_pull_times:'list[float]' = []

        self.publisher_state = ComponentState()
        self.pull_state = ComponentState()
        self.push_state = ComponentState()
        self.cleanup_state = ComponentState()

        self.cleanup = PubSubCleanup()

        self.server = _StubServer(self)
        self.push_delivery = PushDelivery(cast_('any_', self.server), self.backend)

        self._greenlets:'anylist' = []
        self._publisher_greenlets:'anylist' = []

# ################################################################################################################################

    def subscribe(self) -> 'None':
        self.backend.subscribe(Pull_Sub_Key, Pull_Topic)
        self.backend.subscribe(Push_Sub_Key, Push_Topic)

        self.server.config_manager._push_subs[Push_Sub_Key] = [{
            'topic_name': Push_Topic,
            'push_type': PubSub.Push_Type.Service,
            'push_service_name': _push_service_name,
        }]

# ################################################################################################################################

    def _on_error(self, state:'ComponentState', error:'Exception') -> 'None':
        with self.lock:
            state.errors += 1
            if len(state.error_messages) < 5:
                state.error_messages.append(f'{error.__class__.__name__}: {error}'[:300])

# ################################################################################################################################

    def _on_success(self, state:'ComponentState') -> 'None':
        state.success_times.append(monotonic())

# ################################################################################################################################

    def on_pushed(self, msg_id:'str') -> 'None':
        with self.lock:
            self.pushed.append(msg_id)
        self._on_success(self.push_state)

# ################################################################################################################################

    def _publish_loop(self, publisher_index:'int') -> 'None':
        """ One publisher - each publication is repeated under its own msg_id until it is acknowledged,
        as a client does when the outcome of a publication is unknown.
        """
        sequence = 0

        while self.is_publishing:

            msg_id = f'{self.label}.{publisher_index:02d}.{sequence:07d}'

            if sequence % 2 == 0:
                topic_name = Pull_Topic
            else:
                topic_name = Push_Topic

            attempts = 0
            data = msg_id + self.padding

            while True:
                attempts += 1
                try:
                    result = self.backend.publish(topic_name, data, msg_id=msg_id)
                except Exception as e:
                    self._on_error(self.publisher_state, e)
                    sleep(_retry_sleep)
                else:
                    break

            assert result.msg_id == msg_id

            with self.lock:
                self.acknowledged[msg_id] = monotonic()
                if attempts > 1:
                    self.repeated_publications.append(msg_id)

            self._on_success(self.publisher_state)

            sequence += 1
            sleep(_publish_interval)

# ################################################################################################################################

    def _pull_loop(self) -> 'None':
        """ The pull partner - each pull hands the messages over and removes them from the queue.
        """
        while self.is_consuming:

            started = monotonic()

            try:
                messages = self.backend.pull_messages(Pull_Sub_Key, max_messages=_pull_max_messages)
            except Exception as e:
                self._on_error(self.pull_state, e)
                with self.lock:
                    self.failed_pull_times.append(started)
                sleep(_retry_sleep)
                continue

            self._on_success(self.pull_state)

            if not messages:
                sleep(_pull_poll_seconds)
                continue

            with self.lock:
                for message in messages:
                    self.pulled.append(message['msg_id'])

            sleep(0)

# ################################################################################################################################

    def _cleanup_loop(self) -> 'None':
        """ The cleanup process - a guarded sweep every so often.
        """
        while self.is_consuming:
            try:
                _ = self.cleanup.run_guarded_sweep()
            except Exception as e:
                self._on_error(self.cleanup_state, e)
            else:
                self._on_success(self.cleanup_state)

            sleep(_cleanup_interval)

# ################################################################################################################################

    def start(self, with_consumers:'bool'=True) -> 'None':
        """ Starts the publishers, and the consumers too unless the test lets a backlog build up first.
        """
        self.is_publishing = True
        _running_workloads.append(self)

        if with_consumers:
            self.start_consumers()

        for publisher_index in range(_publisher_count):
            self._publisher_greenlets.append(spawn(self._publish_loop, publisher_index))

# ################################################################################################################################

    def start_consumers(self) -> 'None':
        """ Starts the pull partner, the push subscriber and the cleanup process.
        """
        self.is_consuming = True

        self._greenlets.append(spawn(self._pull_loop))
        self._greenlets.append(spawn(self._cleanup_loop))
        self.push_delivery.start_sub_key(Push_Sub_Key)

# ################################################################################################################################

    def stop_publishing(self) -> 'None':
        self.is_publishing = False

        for greenlet in self._publisher_greenlets:
            _ = greenlet.join()

        self._publisher_greenlets = []

# ################################################################################################################################

    def acknowledged_on(self, topic_name:'str') -> 'set[str]':
        """ The acknowledged publications to one topic - the publishers alternate the topics, even sequences first.
        """
        if topic_name == Pull_Topic:
            remainder = 0
        else:
            remainder = 1

        out:'set[str]' = set()

        with self.lock:
            for msg_id in self.acknowledged:
                sequence = int(msg_id.rsplit('.', 1)[1])
                if sequence % 2 == remainder:
                    out.add(msg_id)

        return out

# ################################################################################################################################

    def wait_until_delivered(self, timeout_seconds:'float', pull_allowance:'int', lost:'set[str]') -> 'None':
        """ Waits until the push subscriber received every acknowledged push publication and the partner pulled
        every acknowledged pull publication, apart from at most pull_allowance handed out to pulls that failed
        and apart from the publications that the database lost.
        """
        deadline = monotonic() + timeout_seconds

        expected_pull = self.acknowledged_on(Pull_Topic) - lost
        expected_push = self.acknowledged_on(Push_Topic) - lost

        while True:
            with self.lock:
                missing_pull = expected_pull - set(self.pulled)
                missing_push = expected_push - set(self.pushed)

            if len(missing_pull) <= pull_allowance and not missing_push:
                return

            assert monotonic() < deadline, f'Not delivered after {timeout_seconds}s, pull {len(missing_pull)} ' + \
                f'(allowance {pull_allowance}), push {len(missing_push)}, pull errors {self.pull_state.error_messages}, ' + \
                f'push sample {sorted(missing_push)[:5]}'

            sleep(0.5)

# ################################################################################################################################

    def stop(self) -> 'None':
        self.stop_publishing()
        self.is_consuming = False

        for greenlet in self._greenlets:
            _ = greenlet.join()

        self._greenlets = []
        self.push_delivery.stop()

        _running_workloads.remove(self)

# ################################################################################################################################
# ################################################################################################################################

# The workloads started and not stopped yet, which a test that failed leaves behind.
_running_workloads:'list[Workload]' = []

def stop_running_workloads() -> 'None':
    """ Stops each workload that a test left running, before the environment of the test is restored.
    """
    for workload in list(_running_workloads):
        workload.stop()

# ################################################################################################################################
# ################################################################################################################################
