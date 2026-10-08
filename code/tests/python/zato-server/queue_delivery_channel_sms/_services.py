# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The test services of the SMS channel suite - the target the channels point to and what the tests read
# the recordings back through. An SMS channel hands its service one event, whose body is the document a test
# sent as the text of a simulated incoming message.

# stdlib
from json import loads
from time import monotonic

# Zato
from zato.common.pubsub.outgoing import InboundType
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
_refused_error_text = 'The target refuses this invocation'

# Every invocation of the target, in the order they were made
_invocations:'anylist' = []

# Every instantiation of the hooked service since the last clear
_hooked_instances:'anylist' = []

# How many more invocations the target refuses before it accepts again
_behaviour:'anydict' = {
    'refuse_left': 0,
}

# The header an SMS channel names itself in
_header_channel = 'zato-sms-channel'

# ################################################################################################################################
# ################################################################################################################################

class Target(Service):
    """ What the channels point to - it records every event, with the document the event's body holds as the payload,
    and refuses as many invocations as it was told to.
    """

    name = 'test.queue-delivery.channel.target'

    def before_handle(self) -> 'None':

        event = self.request.payload
        headers = dict(self.request.headers)

        self.record:'stranydict' = {
            'time': monotonic(),
            'cid': self.cid,
            'headers': headers,
            'event': event,
            'payload': loads(event['body']),
            'channel_type': InboundType.SMS,
            'channel_name': headers[_header_channel],
            'hooks': ['before_handle'],
            'is_accepted': True,
        }

        _invocations.append(self.record)

    def handle(self) -> 'None':

        self.record['hooks'].append('handle')
        self.record['handle_started_at'] = monotonic()

        refuse_left = _behaviour['refuse_left']

        if refuse_left == _refuse_everything:
            is_accepted = False

        elif refuse_left > 0:
            _behaviour['refuse_left'] = refuse_left - 1
            is_accepted = False

        else:
            is_accepted = True

        self.record['is_accepted'] = is_accepted

        if not is_accepted:
            raise Exception(_refused_error_text)

        self.response.payload = {
            'is_ok': True,
            'cid': self.cid,
            'echo': self.record['payload']['order_id'],
        }

    def after_handle(self) -> 'None':
        self.record['hooks'].append('after_handle')

# ################################################################################################################################
# ################################################################################################################################

class Hooked(Target):
    """ The target under the name the hooked channels of the template point to.
    """

    name = 'test.queue-delivery.channel.hooked'

    def __init__(self) -> 'None':
        super().__init__()
        _hooked_instances.append(1)

# ################################################################################################################################
# ################################################################################################################################

class SlowHook(Target):
    """ The target under the name the slow-hook channel of the template points to.
    """

    name = 'test.queue-delivery.channel.slow-hook'

# ################################################################################################################################
# ################################################################################################################################

class GetConnection(Service):
    """ Answers with the id and the queue type of an SMS channel, which is what the shared services look up.
    """

    name = 'test.queue-delivery.get-connection'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        channels = self.server.config_manager.channel_sms

        if conn_name not in channels:
            raise Exception(f'No such SMS channel `{conn_name}`')

        channel = channels[conn_name]

        self.response.payload = {
            'id': channel['id'],
            'conn_type': InboundType.SMS,
        }

# ################################################################################################################################
# ################################################################################################################################

class SetBehaviour(Service):
    """ Tells the target how many of the coming invocations to refuse - what it recorded so far stays.
    """

    name = 'test.queue-delivery.channel.set-behaviour'

    def handle(self) -> 'None':

        _behaviour['refuse_left'] = self.request.raw_request['refuse_count']

        self.response.payload = {'refuse_left': _behaviour['refuse_left']}

# ################################################################################################################################
# ################################################################################################################################

class GetReceived(Service):
    """ Every invocation the target has seen since it was last cleared, oldest first.
    """

    name = 'test.queue-delivery.channel.get-received'

    def handle(self) -> 'None':
        self.response.payload = {'invocations': list(_invocations)}

# ################################################################################################################################
# ################################################################################################################################

class Clear(Service):
    """ Forgets every invocation and every instantiation recorded so far and leaves the target accepting.
    """

    name = 'test.queue-delivery.channel.clear'

    def handle(self) -> 'None':

        _behaviour['refuse_left'] = 0
        _invocations.clear()
        _hooked_instances.clear()

        _ = self.invoke('test.queue-delivery.channel.clear-counting', {})

        self.response.payload = {'is_ok': True}

# ################################################################################################################################
# ################################################################################################################################

class GetCounts(Service):
    """ How many times the counting service and the hooked service were instantiated since the last clear.
    """

    name = 'test.queue-delivery.channel.get-counts'

    def handle(self) -> 'None':

        counting = self.invoke('test.queue-delivery.channel.get-counting', {})

        self.response.payload = {
            'counting': counting['count'],
            'hooked': len(_hooked_instances),
        }

# ################################################################################################################################
# ################################################################################################################################
