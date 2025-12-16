# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import TYPE_CHECKING

# Zato
from zato.common.typing_ import callable_, optional

# Local
from .exc import NATSError
from .model import Msg

if TYPE_CHECKING:
    from .client import NATSClient

# ################################################################################################################################
# ################################################################################################################################

class Subscription:
    """ Represents a subscription to a NATS subject.
    """
    def __init__(
        self,
        client:'NATSClient',
        sid:'int',
        subject:'str',
        queue:'str'='',
        callback:'optional[callable_]'=None,
        max_msgs:'int'=0,
    ) -> None:
        self._client = client
        self._sid = sid
        self._subject = subject
        self._queue = queue
        self._callback = callback
        self._max_msgs = max_msgs
        self._received = 0
        self._closed = False

    @property
    def subject(self) -> 'str':
        return self._subject

    @property
    def queue(self) -> 'str':
        return self._queue

    @property
    def delivered(self) -> 'int':
        return self._received

    def next_msg(self, timeout:'optional[float]'=None) -> 'Msg':
        """ Waits for the next message on this subscription.
        """
        if self._closed:
            raise NATSError('Subscription is closed')
        return self._client._wait_for_msg(self._sid, timeout=timeout)

    def unsubscribe(self, max_msgs:'int'=0) -> None:
        """ Unsubscribes from the subject.
        """
        self._client._send_unsubscribe(self._sid, max_msgs)
        if max_msgs == 0:
            self._closed = True
            self._client._remove_subscription(self._sid)

    def drain(self) -> None:
        """ Drains the subscription.
        """
        self.unsubscribe()

# ################################################################################################################################
# ################################################################################################################################
