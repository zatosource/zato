# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Live HL7
from live_hl7 import enmasse

# Zato - the suite's own parts
from _services import Record_Service, SHR_Destination

# ################################################################################################################################
# ################################################################################################################################

# The shared record's REST API and the security definition Zato calls it with
SHR_Security_Name = 'hie.shr.api'
SHR_Queue_Connection = 'hie.shr.hl7-queue'

# The shared record's channel - what a facility addresses in MSH-5 to reach the record through the exchange
SHR_Channel = 'shr.inbound'
SHR_Receiving_Application = 'SHR'

# A facility's outgoing connections, one per channel of the exchange it sends to
Facility_B_Connection = 'facility.b'
Facility_B_Registry_Down_Connection = 'facility.b.registry-down'
Facility_B_SHR_Down_Connection = 'facility.b.shr-down'

# How long the record's channel keeps a connection open with nothing on it, in seconds - the exchange reads
# a route's response up to the close, so a short wait here is what makes it answer a facility promptly
SHR_Idle_Timeout = 1

# ################################################################################################################################
# ################################################################################################################################

class ExchangeAddresses(NamedTuple):
    """ Where a facility's connections go and where the shared record's queue is.
    """

    # The exchange's channel ports, on this machine
    national_adt: 'str'
    national_adt_registry_down: 'str'
    national_adt_shr_down: 'str'

    # The shared record's web address and the account its queue is posted to with
    shr_host: 'str'
    shr_queue_path: 'str'
    shr_username: 'str'
    shr_password: 'str'

# ################################################################################################################################
# ################################################################################################################################

def build_definitions(addresses:'ExchangeAddresses') -> 'enmasse.Definitions':
    """ Everything Zato needs to be facility B and the shared record's front door at once.
    """
    out = enmasse.Definitions()

    out.security.append(
        enmasse.basic_auth(SHR_Security_Name, addresses.shr_username, addresses.shr_password, 'openmrs'))

    out.outgoing_rest.append(
        enmasse.outgoing_rest(SHR_Queue_Connection, addresses.shr_host, addresses.shr_queue_path, SHR_Security_Name))

    out.outgoing_mllp.append(enmasse.outgoing(Facility_B_Connection, addresses.national_adt))
    out.outgoing_mllp.append(enmasse.outgoing(Facility_B_Registry_Down_Connection, addresses.national_adt_registry_down))
    out.outgoing_mllp.append(enmasse.outgoing(Facility_B_SHR_Down_Connection, addresses.national_adt_shr_down))

    out.channel_mllp.append(enmasse.channel(
        SHR_Channel,
        service=Record_Service,
        destinations=[enmasse.rest_destination(SHR_Destination, SHR_Queue_Connection)],
        msh5_receiving_app=SHR_Receiving_Application,
        idle_timeout=SHR_Idle_Timeout,
    ))

    return out

# ################################################################################################################################
# ################################################################################################################################
