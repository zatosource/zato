# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from typing import NamedTuple

# Live HL7
from live_hl7.openhim.system import Host_Address, add_client, add_tcp_channel, login as openhim_login, tcp_route
from live_hl7.openmrs.system import ensure_hl7_source, ensure_identifier_type, login as openmrs_login, \
    make_identifier_types_optional

# Zato - the suite's own parts
from _messages import Facility_A, Facility_B, National_ID_Type

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_hl7.http import Session
    from live_hl7.system import Handle
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The exchange's channels - the national ADT feed, and the two whose routes model a system that is down
National_ADT_Channel = 'national-adt'
Registry_Down_Channel = 'national-adt-registry-down'
SHR_Down_Channel = 'national-adt-shr-down'

# Which published port of the exchange each channel listens on
Channel_Purposes = {
    National_ADT_Channel:  'channel_1',
    Registry_Down_Channel: 'channel_2',
    SHR_Down_Channel:      'channel_3',
}

# The routes of every channel - the shared record answers the facility, the client registry gets a copy
SHR_Route = 'shr'
Registry_Route = 'registry'

# What the exchange calls the facilities and the role its channels allow
Facility_A_Client = 'facility-a'
Facility_B_Client = 'facility-b'
Facility_Role = 'facility'

# ################################################################################################################################
# ################################################################################################################################

class ExchangeChannels(NamedTuple):
    """ The ids the exchange gave its channels, which is what its transactions are filtered by.
    """
    national_adt: 'str'
    registry_down: 'str'
    shr_down: 'str'

# ################################################################################################################################
# ################################################################################################################################

def find_closed_port() -> 'int':
    """ A port nothing listens on, which is what a system that is down looks like from the exchange.
    """
    temporary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temporary_socket.bind(('0.0.0.0', 0))

    _, port = temporary_socket.getsockname()
    temporary_socket.close()

    out = port
    return out

# ################################################################################################################################

def _channel_id(channel:'anydict') -> 'str':
    out = channel['_id']
    return out

# ################################################################################################################################

def configure_exchange(openhim:'Handle', shr_port:'int', registry_port:'int', facility_password:'str') -> 'ExchangeChannels':
    """ Two facilities and three channels - the national feed with both routes up, one with the registry down
    and one with the shared record down, every route pointing at this machine.
    """
    session = openhim_login(openhim)

    add_client(session, Facility_A_Client, facility_password, [Facility_Role])
    add_client(session, Facility_B_Client, facility_password, [Facility_Role])

    allow = [Facility_Role]
    closed_port = find_closed_port()

    national_adt = add_tcp_channel(session, National_ADT_Channel, Channel_Purposes[National_ADT_Channel], [
        tcp_route(SHR_Route, Host_Address, shr_port, is_primary=True),
        tcp_route(Registry_Route, Host_Address, registry_port, is_primary=False),
    ], allow)

    registry_down = add_tcp_channel(session, Registry_Down_Channel, Channel_Purposes[Registry_Down_Channel], [
        tcp_route(SHR_Route, Host_Address, shr_port, is_primary=True),
        tcp_route(Registry_Route, Host_Address, closed_port, is_primary=False),
    ], allow)

    shr_down = add_tcp_channel(session, SHR_Down_Channel, Channel_Purposes[SHR_Down_Channel], [
        tcp_route(SHR_Route, Host_Address, closed_port, is_primary=True),
        tcp_route(Registry_Route, Host_Address, registry_port, is_primary=False),
    ], allow)

    out = ExchangeChannels(
        national_adt=_channel_id(national_adt),
        registry_down=_channel_id(registry_down),
        shr_down=_channel_id(shr_down),
    )

    return out

# ################################################################################################################################

def configure_shared_record(openmrs:'Handle') -> 'Session':
    """ The shared record knows both facilities as sources and files patients under their national ids.
    """
    session = openmrs_login(openmrs)

    ensure_hl7_source(session, Facility_A)
    ensure_hl7_source(session, Facility_B)
    ensure_identifier_type(session, National_ID_Type)
    make_identifier_types_optional(session)

    out = session
    return out

# ################################################################################################################################
# ################################################################################################################################
