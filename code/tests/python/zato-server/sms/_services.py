# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The test services of the SMS suite - the target every channel points to, the sender that uses the outgoing
# connections the way a user's service does, and what the tests read the recordings back through.

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

# A refusal count meaning that the target refuses everything until it is told otherwise
_refuse_everything = -1

# The error the target raises while it refuses
_refused_error_text = 'The target refuses this event'

# Every event the target received, in order of arrival
_received:'anylist' = []

# How many more events the target refuses before it accepts again
_behaviour:'anydict' = {
    'refuse_left': 0,
}

# ################################################################################################################################
# ################################################################################################################################

class Target(Service):
    """ What every channel points to - it records each event along with the headers the channel set
    and refuses as many events as it was told to.
    """
    name = 'test.sms.target'

    def handle(self) -> 'None':

        refuse_left = _behaviour['refuse_left']

        if refuse_left == _refuse_everything:
            is_accepted = False

        elif refuse_left > 0:
            _behaviour['refuse_left'] = refuse_left - 1
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
    """ Sends one message through an outgoing connection the way a user's service does and answers with the result.
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
    """ Pings one outgoing connection through the facade and answers with whether it went through.
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

class SetBehaviour(Service):
    """ Tells the target how many of the coming events to refuse - what it recorded so far stays.
    """
    name = 'test.sms.set-behaviour'

    def handle(self) -> 'None':
        _behaviour['refuse_left'] = self.request.raw_request['refuse_count']
        self.response.payload = {'refuse_left': _behaviour['refuse_left']}

# ################################################################################################################################
# ################################################################################################################################

class GetReceived(Service):
    """ Every event the target has seen since it was last cleared, oldest first.
    """
    name = 'test.sms.get-received'

    def handle(self) -> 'None':
        self.response.payload = {'received': list(_received)}

# ################################################################################################################################
# ################################################################################################################################

class Clear(Service):
    """ Forgets every event recorded so far and leaves the target accepting.
    """
    name = 'test.sms.clear'

    def handle(self) -> 'None':
        _behaviour['refuse_left'] = 0
        _received.clear()
        self.response.payload = {'is_ok': True}

# ################################################################################################################################
# ################################################################################################################################
