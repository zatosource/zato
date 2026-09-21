# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The endpoint of an outgoing connection, as far as every type of connection has one - it records what arrives and answers
# as scripted. A type's own receiver speaks its protocol on top of this and says what accepting and refusing mean there.

# stdlib
import logging
import threading
import time
from dataclasses import dataclass, field

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.queue_delivery.receiver')

_default_wait_timeout_seconds = 60
_poll_interval_seconds = 0.1

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class RecordedRequest:
    """ One request as the endpoint of an outgoing connection saw it, in the terms every type shares.
    """

    # What the sender put on the wire, as text
    body: str

    # What the endpoint answered with, in the type's own terms
    outcome: 'any_'

    # Whether the outcome is one the sender takes as a success
    is_accepted: bool

    # Whether this was a read or a ping rather than a delivery
    is_read: bool

    # On the monotonic clock
    received_at: float = field(default_factory=time.monotonic)

# ################################################################################################################################

request_list = list[RecordedRequest]

# ################################################################################################################################
# ################################################################################################################################

class RecordingReceiver:
    """ The endpoint of an outgoing connection - what a type's own receiver builds on.
    """

    # What the endpoint answers with when it accepts and when it refuses, in the type's own terms
    Accept_Outcome:'any_' = None
    Refuse_Outcome:'any_' = None

    def __init__(self, port:'int') -> 'None':
        self.port = port

        # Every request received, accepted or not
        self.requests:'request_list' = []

        # The outcomes the next requests are answered with, one per request
        self._scripted:'anylist' = []

        # The outcome once the script has run out
        self._default_outcome = self.Accept_Outcome

        self._lock = threading.Lock()

# ################################################################################################################################

    def is_accepted(self, outcome:'any_') -> 'bool':
        """ Whether the sender takes this outcome as a success.
        """
        out = outcome == self.Accept_Outcome
        return out

# ################################################################################################################################

    def next_outcome(self) -> 'any_':
        """ What the request arriving now is answered with - the next scripted outcome or the default one.
        """
        with self._lock:

            if self._scripted:
                out = self._scripted.pop(0)
            else:
                out = self._default_outcome

        return out

# ################################################################################################################################

    def add_request(self, request:'RecordedRequest') -> 'None':
        """ Stores one request a type's receiver built.
        """
        with self._lock:
            self.requests.append(request)

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts listening on the port - a type's receiver says how.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops listening - a type's receiver says how.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def clear(self) -> 'None':
        """ Forgets every recorded request, drops the script and accepts everything again.
        """
        with self._lock:
            self.requests = []
            self._scripted = []
            self._default_outcome = self.Accept_Outcome

# ################################################################################################################################

    def answer_next(self, outcomes:'anylist') -> 'None':
        """ Answers the next requests with these outcomes, one each, in this order.
        """
        with self._lock:
            self._scripted = list(outcomes)

# ################################################################################################################################

    def refuse_next(self, count:'int') -> 'None':
        """ Refuses that many next requests and accepts from then on.
        """
        self.answer_next([self.Refuse_Outcome] * count)

# ################################################################################################################################

    def refuse_then_accept(self, refused_count:'int') -> 'None':
        """ Refuses that many next requests, accepts the one after and answers as before from then on.
        """
        self.answer_next([self.Refuse_Outcome] * refused_count + [self.Accept_Outcome])

# ################################################################################################################################

    def refuse_all(self) -> 'None':
        """ Refuses every request from now on.
        """
        with self._lock:
            self._default_outcome = self.Refuse_Outcome

# ################################################################################################################################

    def accept_all(self) -> 'None':
        """ Accepts every request from now on.
        """
        with self._lock:
            self._default_outcome = self.Accept_Outcome

# ################################################################################################################################

    def accepted(self) -> 'request_list':
        """ The requests the endpoint accepted, in the order they arrived.
        """
        with self._lock:
            out = [request for request in self.requests if request.is_accepted]

        return out

# ################################################################################################################################

    def outcomes(self) -> 'anylist':
        """ What the endpoint answered each request with, in the order they arrived.
        """
        with self._lock:
            out = [request.outcome for request in self.requests]

        return out

# ################################################################################################################################

    def acceptance(self) -> 'list[bool]':
        """ Whether each request was accepted, in the order they arrived.
        """
        with self._lock:
            out = [request.is_accepted for request in self.requests]

        return out

# ################################################################################################################################

    def reads(self) -> 'request_list':
        """ The reads and pings the endpoint saw, in the order they arrived.
        """
        with self._lock:
            out = [request for request in self.requests if request.is_read]

        return out

# ################################################################################################################################

    def wait_for_requests(
        self,
        expected_count:'int'=1,
        timeout:'float'=_default_wait_timeout_seconds,
        ) -> 'request_list':
        """ Blocks until that many requests have arrived, accepted or not, then returns all of them.
        """
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:

            with self._lock:
                out = list(self.requests)

            if len(out) >= expected_count:
                return out

            time.sleep(_poll_interval_seconds)

        with self._lock:
            out = list(self.requests)

        return out

# ################################################################################################################################

    def wait_for_accepted(
        self,
        expected_count:'int'=1,
        timeout:'float'=_default_wait_timeout_seconds,
        ) -> 'request_list':
        """ Blocks until that many requests have been accepted, then returns the accepted ones.
        """
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:

            out = self.accepted()

            if len(out) >= expected_count:
                return out

            time.sleep(_poll_interval_seconds)

        out = self.accepted()
        return out

# ################################################################################################################################
# ################################################################################################################################
