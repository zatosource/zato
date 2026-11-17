# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Item 15.9 - messages published while the clock of the server is skewed expire neither early nor late.
# The true time is the clock of the test process, which the fault does not change.

# stdlib
from time import monotonic, time

# gevent
from gevent import sleep, spawn

# Zato
from pubsub_rest.transport import RESTClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_rest.definition import Definition
    from pubsub_rest.server import PubSubServer
    from pubsub_rest.transport import Credentials
    from zato.common.typing_ import any_, intlist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The topics of the probe - one pulled before its messages expire and one pulled after they expire -
# each with a subscriber of the same name, and the publisher of both.
_early_topic = 'faults.expiration.early'
_late_topic = 'faults.expiration.late'
_publisher = 'faults.expiration.publisher'

# How many messages each topic receives and how long they live, in seconds.
_message_count = 20
_expiration_seconds = 50

# When the messages are published after the fault is applied, which falls in a period in which a jumping clock
# is behind, and when each topic is pulled after the publication, which falls in a period in which it is ahead,
# and which a slow clock reaches before it reaches the expiration, all in seconds.
_publish_after_seconds = 25
_early_pull_after_seconds = 30
_late_pull_after_seconds = 60

# How far the expiration that the server stores may be from the true one, in milliseconds.
_tolerance_ms = 2000

_ms_per_second = 1000

# The size budget of one pull, in bytes.
_max_len = 5_000_000

# ################################################################################################################################
# ################################################################################################################################

class ExpirationProbe:
    """ Publishes messages during the fault, compares the expirations that the server stores with the true ones
    and pulls the messages before and after they expire.
    """

    def __init__(self) -> 'None':

        self.server:'PubSubServer | None' = None

        self.publisher_credentials:'Credentials | None' = None
        self.early_credentials:'Credentials | None' = None
        self.late_credentials:'Credentials | None' = None

        # The differences between the stored and the true expirations, and how many messages each pull received.
        self.expiration_errors_ms:'intlist' = []
        self.early_received = 0
        self.late_received = 0

        self._greenlet:'any_' = None

# ################################################################################################################################

    def define(self, server:'PubSubServer', definition:'Definition') -> 'None':
        """ Adds the topics, the publisher and the subscribers of the probe to the definition of the server.
        """
        self.publisher_credentials = definition.add_publisher(_publisher, [_early_topic, _late_topic])
        self.early_credentials = definition.add_pull_subscriber(_early_topic, [_early_topic])
        self.late_credentials = definition.add_pull_subscriber(_late_topic, [_late_topic])

        self.server = server

# ################################################################################################################################

    def _get_server(self) -> 'PubSubServer':
        server = self.server
        assert server is not None, 'The probe is not defined'
        return server

# ################################################################################################################################

    def _new_client(self, credentials:'Credentials | None') -> 'RESTClient':
        assert credentials is not None, 'The probe is not defined'

        out = RESTClient(self._get_server().base_url, credentials)
        return out

# ################################################################################################################################

    def _publish(self, client:'RESTClient', topic_name:'str') -> 'strlist':
        out:'strlist' = []

        for _ in range(_message_count):
            response = client.publish(topic_name, {'data': 'Expiration probe', 'expiration': _expiration_seconds})
            out.append(response['msg_id'])

        return out

# ################################################################################################################################

    def _read_expiration_errors(self, msg_ids:'strlist', true_expiration_ms:'int') -> 'None':

        expirations = self._get_server().get_expirations(msg_ids)

        for expiration_ms in expirations.values():
            error_ms = expiration_ms - true_expiration_ms
            self.expiration_errors_ms.append(error_ms)

# ################################################################################################################################

    def _pull(self, credentials:'Credentials | None') -> 'int':

        client = self._new_client(credentials)

        max_messages = _message_count * 2
        response = client.pull(max_messages, _max_len)

        msg_ids:'strlist' = []

        for message in response['messages']:
            msg_ids.append(message['meta']['msg_id'])

        if msg_ids:
            _ = client.ack(msg_ids)

        client.close()

        out = len(msg_ids)
        return out

# ################################################################################################################################

    def _sleep_until(self, deadline:'float') -> 'None':
        remaining = deadline - monotonic()
        remaining = max(remaining, 0)
        sleep(remaining)

# ################################################################################################################################

    def _run(self) -> 'None':

        # The messages are published once the clock was moved ..
        sleep(_publish_after_seconds)

        published_at = monotonic()
        true_now_ms = int(time() * _ms_per_second)
        true_expiration_ms = true_now_ms + _expiration_seconds * _ms_per_second

        client = self._new_client(self.publisher_credentials)

        early_msg_ids = self._publish(client, _early_topic)
        late_msg_ids = self._publish(client, _late_topic)
        msg_ids = early_msg_ids + late_msg_ids

        client.close()

        # .. their expirations are compared with the true one ..
        self._read_expiration_errors(msg_ids, true_expiration_ms)

        # .. and they are pulled before and after they expire.
        self._sleep_until(published_at + _early_pull_after_seconds)
        self.early_received = self._pull(self.early_credentials)

        self._sleep_until(published_at + _late_pull_after_seconds)
        self.late_received = self._pull(self.late_credentials)

# ################################################################################################################################

    def start(self) -> 'None':
        self._greenlet = spawn(self._run)

# ################################################################################################################################

    def wait(self) -> 'None':
        _ = self._greenlet.get()

# ################################################################################################################################

    def check(self) -> 'None':
        """ Every stored expiration is the true one, every message is received before it expires
        and none is received after.
        """
        wrong:'intlist' = []

        for error_ms in self.expiration_errors_ms:
            if abs(error_ms) > _tolerance_ms:
                wrong.append(error_ms)

        published = _message_count * 2

        assert len(self.expiration_errors_ms) == published, self.expiration_errors_ms
        assert not wrong, f'Expirations differ from the true ones by {wrong} ms'
        assert self.early_received == _message_count, f'Received {self.early_received} of {_message_count} before expiration'
        assert self.late_received == 0, f'Received {self.late_received} messages after their expiration'

# ################################################################################################################################
# ################################################################################################################################
