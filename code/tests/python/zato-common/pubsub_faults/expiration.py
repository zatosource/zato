# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Item 15.9 - messages published while the clock of the server is skewed expire neither early nor late.
# The true time is what the test that started the server read from the clock of the host before the fault,
# advanced by the monotonic clock of the host, which the fault does not change and which every process shares.

# stdlib
import os
from time import monotonic

# gevent
from gevent import sleep, spawn

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.pubsub.sql.schema import message_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.typing_ import any_, intlist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The variable through which the test passes the true time and the monotonic time it was read at.
Env_Clock_Anchor = 'Zato_Test_Fault_Clock_Anchor'

# The topics of the probe - one pulled before its messages expire and one pulled after they expire.
_early_topic = 'faults.expiration.early'
_late_topic = 'faults.expiration.late'
_early_sub_key = 'zpsk.faults-expiration-early'
_late_sub_key = 'zpsk.faults-expiration-late'

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

# ################################################################################################################################
# ################################################################################################################################

def is_probe_enabled() -> 'bool':
    out = Env_Clock_Anchor in os.environ
    return out

# ################################################################################################################################
# ################################################################################################################################

class ExpirationProbe:
    """ Publishes messages during the fault, compares the expirations that the server stores with the true ones
    and pulls the messages before and after they expire.
    """

    def __init__(self, backend:'SQLPubSubBackend') -> 'None':
        self.backend = backend

        anchor_ms, anchor_monotonic = os.environ[Env_Clock_Anchor].split()
        self.anchor_ms = int(anchor_ms)
        self.anchor_monotonic = float(anchor_monotonic)

        # The differences between the stored and the true expirations, and how many messages each pull received.
        self.expiration_errors_ms:'intlist' = []
        self.early_received = 0
        self.late_received = 0

        self._greenlet:'any_' = None

# ################################################################################################################################

    def _get_true_ms(self) -> 'int':
        elapsed = monotonic() - self.anchor_monotonic
        elapsed_ms = int(elapsed * _ms_per_second)

        out = self.anchor_ms + elapsed_ms
        return out

# ################################################################################################################################

    def subscribe(self) -> 'None':
        self.backend.subscribe(_early_sub_key, _early_topic)
        self.backend.subscribe(_late_sub_key, _late_topic)

# ################################################################################################################################

    def _publish(self, topic_name:'str') -> 'strlist':
        out:'strlist' = []

        for _ in range(_message_count):
            result = self.backend.publish(topic_name, 'Expiration probe', expiration=_expiration_seconds)
            out.append(result.msg_id)

        return out

# ################################################################################################################################

    def _read_expiration_errors(self, msg_ids:'strlist', true_expiration_ms:'int') -> 'None':
        query = select(message_table.c.expiration_ms)
        query = query.where(message_table.c.msg_id.in_(msg_ids))

        with get_pubsub_engine().connect() as connection:
            rows = connection.execute(query).fetchall()

        for row in rows:
            error_ms = row.expiration_ms - true_expiration_ms
            self.expiration_errors_ms.append(error_ms)

# ################################################################################################################################

    def _pull(self, sub_key:'str') -> 'int':
        max_messages = _message_count * 2
        messages = self.backend.pull_messages(sub_key, max_messages=max_messages)

        msg_ids:'strlist' = []

        for message in messages:
            msg_ids.append(message['msg_id'])

        if msg_ids:
            _ = self.backend.ack_pulled(sub_key, msg_ids)

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
        true_now_ms = self._get_true_ms()
        true_expiration_ms = true_now_ms + _expiration_seconds * _ms_per_second

        early_msg_ids = self._publish(_early_topic)
        late_msg_ids = self._publish(_late_topic)
        msg_ids = early_msg_ids + late_msg_ids

        # .. their expirations are compared with the true one ..
        self._read_expiration_errors(msg_ids, true_expiration_ms)

        # .. and they are pulled before and after they expire.
        self._sleep_until(published_at + _early_pull_after_seconds)
        self.early_received = self._pull(_early_sub_key)

        self._sleep_until(published_at + _late_pull_after_seconds)
        self.late_received = self._pull(_late_sub_key)

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
