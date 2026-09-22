# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What an HL7 live suite creates in Zato, as enmasse definitions - each function returns one definition in
# the shape the YAML file takes and render() turns a set of them into that file.

# stdlib
from contextlib import contextmanager
from typing import NamedTuple

# PyYAML
import yaml

# Zato
from zato.common.destination.constants import Default_Delivery_Mode, DestinationType, Respond_From_Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from live_environment.quickstart import ZatoEnvironment
    from zato.common.typing_ import anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The file the definitions are imported from
Definitions_File_Name = 'hl7-live.yaml'

# The file one channel is re-imported from while its service is switched
Switch_File_Name = 'hl7-live-switch.yaml'

# How long an outgoing connection waits for an acknowledgment, in milliseconds
Default_Receive_Timeout_MS = 15000

# How long a channel keeps a connection open with nothing on it, in seconds, unless a suite says otherwise
Default_Idle_Timeout = 300

# ################################################################################################################################
# ################################################################################################################################

class TLSClient(NamedTuple):
    """ What an outgoing connection verifies the far side with and presents to it.
    """
    ca_path: 'str'
    cert_path: 'str' = ''
    key_path: 'str' = ''

# ################################################################################################################################

class Definitions:
    """ Everything one suite imports, section by section.
    """

    def __init__(self) -> 'None':
        self.security:'anylist' = []
        self.outgoing_rest:'anylist' = []
        self.outgoing_mllp:'anylist' = []
        self.channel_mllp:'anylist' = []

# ################################################################################################################################
# ################################################################################################################################

def basic_auth(name:'str', username:'str', password:'str', realm:'str') -> 'stranydict':
    """ A Basic Auth definition an outgoing REST connection calls a foreign system with.
    """
    out = {
        'name': name,
        'type': 'basic_auth',
        'username': username,
        'password': password,
        'realm': realm,
    }

    return out

# ################################################################################################################################

def outgoing_rest(name:'str', host:'str', url_path:'str', security:'str') -> 'stranydict':
    """ An outgoing REST connection posting JSON to one path of a foreign system.
    """
    out = {
        'name': name,
        'host': host,
        'url_path': url_path,
        'data_format': 'json',
        'security': security,
    }

    return out

# ################################################################################################################################

def outgoing(
    name:'str',
    address:'str',
    *,
    tls:'TLSClient | None'=None,
    receive_timeout_ms:'int'=Default_Receive_Timeout_MS,
    ) -> 'stranydict':
    """ An outgoing MLLP connection to one address, `host:port`, over TLS when the authority to verify the
    far side against is given.
    """
    out = {
        'name': name,
        'address': address,
        'recv_timeout': receive_timeout_ms,
        'pool_size': 1,
        'should_log_messages': True,
    }

    if tls:
        out['tls_ca_path'] = tls.ca_path
        out['tls_cert_path'] = tls.cert_path
        out['tls_key_path'] = tls.key_path

    return out

# ################################################################################################################################

def mllp_destination(name:'str', connection:'str') -> 'stranydict':
    """ A channel destination delivering through an outgoing MLLP connection.
    """
    out = {
        'name': name,
        'type': DestinationType.MLLP,
        'connection': connection,
    }

    return out

# ################################################################################################################################

def rest_destination(name:'str', connection:'str') -> 'stranydict':
    """ A channel destination posting through an outgoing REST connection.
    """
    out = {
        'name': name,
        'type': DestinationType.REST,
        'connection': connection,
        'options': {'method': 'POST'},
    }

    return out

# ################################################################################################################################

def channel(
    name:'str',
    *,
    service:'str'='',
    destinations:'anylist | None'=None,
    respond_from:'str'=Respond_From_Service,
    delivery_mode:'str'=Default_Delivery_Mode,
    is_default:'bool'=False,
    idle_timeout:'int'=Default_Idle_Timeout,
    msh3_sending_app:'str'='',
    msh5_receiving_app:'str'='',
    msh9_message_type:'str'='',
    ) -> 'stranydict':
    """ An MLLP channel matched on MSH-3, MSH-5 and the message type of MSH-9, or taking everything no other
    channel claims when it is the default one. Messages reach the channel as they arrived, every message is
    logged and a sender is told why a message was refused.
    """
    if destinations is None:
        destinations = []

    out = {
        'name': name,
        'service': service,
        'msh3_sending_app': msh3_sending_app,
        'msh5_receiving_app': msh5_receiving_app,
        'msh9_message_type': msh9_message_type,
        'is_default': is_default,
        'idle_timeout': idle_timeout,
        'should_parse_on_input': False,
        'should_log_messages': True,
        'should_return_errors': True,
        'destinations': destinations,
        'respond_from': respond_from,
        'delivery_mode': delivery_mode,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def render(definitions:'Definitions') -> 'str':
    """ The YAML file enmasse imports, holding only the sections with something in them.
    """
    document:'stranydict' = {}

    if definitions.security:
        document['security'] = definitions.security

    if definitions.outgoing_rest:
        document['outgoing_rest'] = definitions.outgoing_rest

    if definitions.outgoing_mllp:
        document['outgoing_mllp'] = definitions.outgoing_mllp

    if definitions.channel_mllp:
        document['channel_mllp'] = definitions.channel_mllp

    out = yaml.safe_dump(document, sort_keys=False)
    return out

# ################################################################################################################################

def import_definitions(environment:'ZatoEnvironment', definitions:'Definitions') -> 'None':
    """ Creates everything the definitions describe.
    """
    _ = environment.import_yaml(Definitions_File_Name, render(definitions))

# ################################################################################################################################

@contextmanager
def extended(environment:'ZatoEnvironment', definitions:'Definitions', restored:'anylist') -> 'Iterator[None]':
    """ Imports more definitions for the length of the block - connections and channels added to an environment
    already imported - then imports the channels given back as they were. Connections stay, unused.
    """
    _ = environment.import_yaml(Switch_File_Name, render(definitions))

    try:
        yield
    finally:
        original = Definitions()
        original.channel_mllp.extend(restored)

        _ = environment.import_yaml(Switch_File_Name, render(original))

# ################################################################################################################################

def _import_channel(environment:'ZatoEnvironment', channel_definition:'stranydict') -> 'None':
    """ Imports one channel again - enmasse finds it by name and updates it.
    """
    definitions = Definitions()
    definitions.channel_mllp.append(channel_definition)

    _ = environment.import_yaml(Switch_File_Name, render(definitions))

# ################################################################################################################################

@contextmanager
def switch(
    environment:'ZatoEnvironment',
    channel_definition:'stranydict',
    service:'str',
    *,
    respond_from:'str'='',
    ) -> 'Iterator[None]':
    """ Re-imports one channel with another service for the length of the block, then puts its own back -
    and with another reply source too when given, for a channel that otherwise lets a destination answer.
    """
    switched = dict(channel_definition)
    switched['service'] = service

    if respond_from:
        switched['respond_from'] = respond_from

    _import_channel(environment, switched)

    try:
        yield
    finally:
        _import_channel(environment, channel_definition)

# ################################################################################################################################
# ################################################################################################################################
