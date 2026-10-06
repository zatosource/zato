# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What every group of channel scenarios builds on. A transport's suite subclasses ChannelScenarios and names its type,
# pytest collects the inherited test methods and each runs through the transport's channels and services.

# Zato
from zato.common.typing_ import cast_

# Test support
from queue_delivery.channel.type_under_test import get_type_under_test
from queue_delivery.client import get_queue
from queue_delivery.dlq import invoke
from queue_delivery.scenarios.browse import Get_Message_List, Kind_Queue

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import any_, anydict, anylist, strdict, strlist
    from queue_delivery.channel.client import ChannelResponse
    from queue_delivery.channel.type_under_test import ChannelTypeUnderTest

# ################################################################################################################################
# ################################################################################################################################

# The document most scenarios send - the channels' URL paths carry the order id as a path parameter too
Order_ID = 'ord-7'

# ################################################################################################################################
# ################################################################################################################################

def order(seq:'int') -> 'anydict':
    """ The document of one order in a run of them.
    """
    out = {
        'order_id': Order_ID,
        'seq': seq,
    }

    return out

# ################################################################################################################################

def sequences_of(invocations:'anylist') -> 'list[int]':
    """ The sequence numbers of a run of recorded invocations, in the order the target saw them.
    """
    out = []

    for invocation in invocations:
        seq = invocation['payload']['seq']

        # A SOAP target records the text of the element
        if isinstance(seq, str):
            seq = int(seq)

        out.append(seq)

    return out

# ################################################################################################################################

def acceptance_of(invocations:'anylist') -> 'list[bool]':
    """ Whether each of a run of recorded invocations was accepted, in the order the target saw them.
    """
    out = []

    for invocation in invocations:
        out.append(invocation['is_accepted'])

    return out

# ################################################################################################################################
# ################################################################################################################################

class ChannelScenarioBase:
    """ The transport under test and the shortcuts every scenario reaches for.
    """

    # A transport's suite sets this, the session fixture points TestConfig at the same object
    type_under_test:'ChannelTypeUnderTest' = cast_('ChannelTypeUnderTest', None)

# ################################################################################################################################

    @property
    def t(self) -> 'ChannelTypeUnderTest':
        """ The transport under test, as the session fixture knows it.
        """
        out = get_type_under_test()
        return out

# ################################################################################################################################

    def conn(self, key:'str') -> 'str':
        """ The name of the channel under that key.
        """
        out = self.t.connections[key]
        return out

# ################################################################################################################################

    def call(self, key:'str', document:'anydict', headers:'strdict | None'=None, params:'strdict | None'=None) -> 'ChannelResponse':
        """ Calls a channel the way a client of the transport does.
        """
        out = self.t.call(key, document, headers, params)
        return out

# ################################################################################################################################

    def ack_of(self, response:'ChannelResponse') -> 'anydict':
        """ The acknowledgement a 200 response carries.
        """
        assert response.status == 200, (response.status, response.text)

        out = self.t.read_ack(response)
        assert out['is_ok'] is True, out

        return out

# ################################################################################################################################

    def conn_id(self, client:'AdminClient', key:'str') -> 'int':
        """ The id of a channel.
        """
        out = get_queue(client, self.conn(key))['conn_id']
        return out

# ################################################################################################################################

    def browse(self, client:'AdminClient', key:'str', kind:'str'=Kind_Queue, **extra:'any_') -> 'anydict':
        """ One page of a channel's queue or DLQ, as the delivery page reads it.
        """
        request:'anydict' = {
            'conn_type': self.t.conn_type,
            'conn_id': self.conn_id(client, key),
            'kind': kind,
        }
        request.update(extra)

        out = invoke(client, Get_Message_List, request)
        return out

# ################################################################################################################################

    def queued_msg_ids(self, client:'AdminClient', key:'str') -> 'strlist':
        """ The ids of the messages a channel's queue holds, as the server lists them.
        """
        out = []

        for message in get_queue(client, self.conn(key))['messages']:
            out.append(message['msg_id'])

        return out

# ################################################################################################################################
# ################################################################################################################################
