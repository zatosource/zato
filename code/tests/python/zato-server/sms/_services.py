# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The test services of the SMS suite - the target service of every channel, the service that sends through
# the outgoing connections and the services that return the recorded events.

# stdlib
from time import monotonic

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The refusal count at which the target refuses every event
_refuse_everything = -1

# The error the target raises for a refused event
_refused_error_text = 'The target refuses this event'

# Every event the target received, in order of arrival
_received:'anylist' = []

# The number of events the target refuses before accepting
_refusal:'anydict' = {
    'remaining': 0,
}

# ################################################################################################################################
# ################################################################################################################################

class Target(Service):
    """ The target service of every channel. Records each event with the channel's headers and refuses
    the configured number of events.
    """
    name = 'test.sms.target'

    def handle(self) -> 'None':

        remaining = _refusal['remaining']

        if remaining == _refuse_everything:
            is_accepted = False

        elif remaining > 0:
            _refusal['remaining'] = remaining - 1
            is_accepted = False

        else:
            is_accepted = True

        record:'stranydict' = {
            'time': monotonic(),
            'cid': self.cid,
            'headers': dict(self.request.headers),
            'event': self.request.payload,
            'is_accepted': is_accepted,
        }

        _received.append(record)

        if not is_accepted:
            raise Exception(_refused_error_text)

        self.response.payload = {'is_ok': True, 'cid': self.cid}

# ################################################################################################################################
# ################################################################################################################################

class Send(Service):
    """ Sends one message through an outgoing connection and returns the result.
    """
    name = 'test.sms.send'

    def handle(self) -> 'None':

        request = self.request.raw_request

        conn_name = request['conn_name']
        to = request['to']
        body = request['body']

        from_ = ''
        if 'from_' in request:
            from_ = request['from_']

        try:
            result = self.out.sms[conn_name].send(to, body, from_=from_)
        except Exception as e:
            self.response.payload = {'is_ok': False, 'error': str(e)}
            return

        self.response.payload = {'is_ok': True, 'result': result.to_dict()}

# ################################################################################################################################
# ################################################################################################################################

class Ping(Service):
    """ Pings one outgoing connection through the facade and returns whether the ping succeeded.
    """
    name = 'test.sms.ping'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        try:
            self.out.sms[conn_name].ping()
        except Exception as e:
            self.response.payload = {'is_ok': False, 'error': str(e)}
            return

        self.response.payload = {'is_ok': True}

# ################################################################################################################################
# ################################################################################################################################

class SetRefusalCount(Service):
    """ Sets the number of events the target refuses. Recorded events are kept.
    """
    name = 'test.sms.set-refusal-count'

    def handle(self) -> 'None':
        _refusal['remaining'] = self.request.raw_request['refuse_count']
        self.response.payload = {'remaining': _refusal['remaining']}

# ################################################################################################################################
# ################################################################################################################################

class GetReceived(Service):
    """ Every event the target received since the last clear, oldest first.
    """
    name = 'test.sms.get-received'

    def handle(self) -> 'None':
        self.response.payload = {'received': list(_received)}

# ################################################################################################################################
# ################################################################################################################################

class Clear(Service):
    """ Clears the recorded events and sets the refusal count to zero.
    """
    name = 'test.sms.clear'

    def handle(self) -> 'None':
        _refusal['remaining'] = 0
        _received.clear()
        self.response.payload = {'is_ok': True}

# ################################################################################################################################
# ################################################################################################################################
