# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the MLLP listener needs of the world around it when a test drives it - a socket that
# records what was written to it rather than one that is really connected anywhere, a route
# standing for one channel, and a wrapper built around a configuration rather than around a
# running server. Everything a message goes through afterwards is the real thing, framing and
# acknowledgment building included.

# stdlib
from json import dumps
from unittest.mock import MagicMock

# Zato
from zato.common.api import HL7
from zato.common.destination.constants import Default_Delivery_Mode, DestinationType, Respond_From_Service
from zato.common.hl7.mllp.router import ChannelRoute
from zato.common.hl7.mllp.server import ConnectionContext, HL7MLLPServer
from zato.common.hl7.mllp.settings import Default_End_Sequence, Default_Start_Sequence, ListenerConfig, RouteSettings
from zato.common.typing_ import cast_
from zato.server.generic.api.channel_hl7_mllp import ChannelHL7MLLPWrapper

from service_stub import ServerStub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, callable_, stranydict
    from zato.server.base.parallel import ParallelServer

    anylist = anylist
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The channel every test here runs over
Channel_Name = 'hl7.test.destinations'

# Where the listener the tests drive would bind, which nothing here connects to
Listener_Address = '127.0.0.1:29100'

# The sender every message is taken to have come from
Client_IP = '10.1.2.3'
Client_Port = 45678

# The message that arrives on the channel
Request_Message = 'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FACILITY|20260101120000||ADT^A01|MSG00001|P|2.5'

# The correlation id the channel recorded the message's arrival under, which everything
# the message leads to is recorded under as well
Message_CID = 'cid-channel-message-1'

# The connections the destinations of the tests point at
MLLP_Connection = 'hl7.forward.ehr'
REST_Connection = 'rest.billing'

# ################################################################################################################################
# ################################################################################################################################

class SocketRecorder:
    """ A socket that keeps what was sent through it instead of sending it anywhere, which is
    where a test reads the acknowledgment the sender would have received.
    """
    def __init__(self) -> 'None':
        self.sent:'list[bytes]' = []

# ################################################################################################################################

    def sendall(self, data:'bytes') -> 'None':
        self.sent.append(data)

# ################################################################################################################################

    def setsockopt(self, *ignored:'any_') -> 'None':
        pass

# ################################################################################################################################

    def get_replies(self) -> 'list[str]':
        """ Returns each reply the sender received, out of the framing it went out in.
        """
        out:'list[str]' = []

        for item in self.sent:
            payload = item.removeprefix(Default_Start_Sequence).removesuffix(Default_End_Sequence)
            out.append(payload.decode('utf-8'))

        return out

# ################################################################################################################################
# ################################################################################################################################

def new_stored_list() -> 'anylist':
    """ Returns a destination list the way the Dashboard stores one.
    """
    out = [
        {
            'name': MLLP_Connection,
            'type': DestinationType.MLLP,
            'connection': MLLP_Connection,
            'is_active': True,
            'options': {},
        },
        {
            'name': REST_Connection,
            'type': DestinationType.REST,
            'connection': REST_Connection,
            'is_active': True,
            'options': {'method': 'POST'},
        },
    ]

    return out

# ################################################################################################################################

def new_channel_item(
    destinations:'anylist | str',
    respond_from:'str' = Respond_From_Service,
    delivery_mode:'str' = Default_Delivery_Mode,
    ) -> 'stranydict':
    """ Returns a channel item the way the MLLP wrapper hands one over.
    """
    if destinations:
        if not isinstance(destinations, str):
            destinations = dumps(destinations)

    out = {
        'id': 1,
        'name': Channel_Name,
        'is_internal': False,
        'data_format': HL7.Const.Version.v2.id,
        'destinations': destinations,
        'respond_from': respond_from,
        'delivery_mode': delivery_mode,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def new_route(callback:'callable_', *, service_name:'str'='', has_destinations:'bool'=True) -> 'ChannelRoute':
    """ Returns the route one channel is registered under, with the framing and the tolerances
    every channel starts out with.
    """
    out = ChannelRoute()

    out.channel_name     = Channel_Name
    out.callback         = callback
    out.service_name     = service_name
    out.has_destinations = has_destinations

    out.msh3_sending_application   = ''
    out.msh4_sending_facility      = ''
    out.msh5_receiving_application = ''
    out.msh6_receiving_facility    = ''
    out.msh9_message_type          = ''
    out.msh9_trigger_event         = ''
    out.msh11_processing_id        = ''
    out.msh12_version_id           = ''

    out.is_default          = True
    out.is_audit_log_active = False
    out.settings            = RouteSettings(should_parse_on_input=False)

    return out

# ################################################################################################################################

def new_server() -> 'HL7MLLPServer':
    """ Returns a listener that was never bound to anything - what the tests drive one message
    at a time rather than over a connection of its own.
    """
    router = MagicMock()

    out = HL7MLLPServer(ListenerConfig(Listener_Address), router)
    return out

# ################################################################################################################################

def new_connection_context() -> 'ConnectionContext':
    """ Returns the sender every message of the tests arrives from.
    """
    out = ConnectionContext(Client_IP, Client_Port, '')
    return out

# ################################################################################################################################

def handle_one_message(route:'ChannelRoute', message:'str'=Request_Message) -> 'list[str]':
    """ Puts one message through the listener as though it had arrived on a connection and
    returns what the sender was answered with.
    """
    server = new_server()
    active_socket = SocketRecorder()

    server._handle_message(
        active_socket,             # type: ignore[arg-type]
        message.encode('utf-8'),
        new_connection_context(),
        route,
        route.settings,
    )

    out = active_socket.get_replies()
    return out

# ################################################################################################################################
# ################################################################################################################################

def new_parallel_server() -> 'ParallelServer':
    """ Returns the server a channel runs on, which a delivery with no service between the channel
    and its destinations reaches only for the name each hop is recorded under.
    """
    out = cast_('ParallelServer', ServerStub())
    return out

# ################################################################################################################################

def get_invoker(wrapper:'ChannelHL7MLLPWrapper') -> 'MagicMock':
    """ Returns the stand-in the wrapper reaches the rest of the server through.
    """
    out = cast_('MagicMock', wrapper.server)
    return out

# ################################################################################################################################
# ################################################################################################################################

def new_wrapper(**overrides:'any_') -> 'ChannelHL7MLLPWrapper':
    """ Returns a wrapper around a channel's configuration, with nothing of the server it would
    otherwise run on - what each test that reads a wrapper's own decisions is built from.
    """
    config:'stranydict' = {
        'id': 1,
        'name': Channel_Name,
        'service': 'test.hl7.mllp.echo',
        'is_active': True,
        'is_internal': False,
        'data_format': HL7.Const.Version.v2.id,
        'destinations': '',
        'respond_from': Respond_From_Service,
        'delivery_mode': Default_Delivery_Mode,
    }

    config.update(overrides)

    wrapper = ChannelHL7MLLPWrapper.__new__(ChannelHL7MLLPWrapper)

    wrapper.config = MagicMock()
    for key, value in config.items():
        setattr(wrapper.config, key, value)

    wrapper.server = MagicMock()

    return wrapper

# ################################################################################################################################
# ################################################################################################################################
