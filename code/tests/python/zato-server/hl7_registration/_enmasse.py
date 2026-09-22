# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Live HL7
from live_hl7 import enmasse
from live_hl7.enmasse import TLSClient

# Zato - the suite's own parts
from _messages import PACS_Application, Registration_Application, Registration_TLS_Application
from _services import PACS_Record_Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

# The engine's outgoing connections - the PACS on its plain and its TLS listener, and the second department
PACS_Connection = 'pacs'
PACS_TLS_Connection = 'pacs_tls'
Department_Connection = 'department'

# The feed's entry points, one for admissions and one for orders, the one whose way to the PACS is
# over TLS, and where the PACS publishes to
ADT_Channel = 'registration.adt'
ADT_TLS_Channel = 'registration.adt.tls'
Orders_Channel = 'registration.orders'
Documents_Channel = 'registration.documents'
PACS_Channel = 'pacs.adt'

# What the channels call their destinations
PACS_Destination = 'pacs'
Department_Destination = 'department'

# Message types, as MSH-9 carries them
ADT_Type = 'ADT'
ORM_Type = 'ORM'
MDM_Type = 'MDM'

# ################################################################################################################################
# ################################################################################################################################

class RegistrationAddresses(NamedTuple):
    """ Where the engine's connections go and what the TLS one presents.
    """
    pacs: 'str'
    pacs_tls: 'str'
    department: 'str'
    tls: 'TLSClient'

# ################################################################################################################################
# ################################################################################################################################

def adt_channel() -> 'stranydict':
    """ The feed's entry point - every admission fans out to the PACS and the department at the same time,
    and the registration system hears back what the PACS said.
    """
    out = enmasse.channel(
        ADT_Channel,
        destinations=[
            enmasse.mllp_destination(PACS_Destination, PACS_Connection),
            enmasse.mllp_destination(Department_Destination, Department_Connection),
        ],
        respond_from=PACS_Destination,
        msh3_sending_app=Registration_Application,
        msh9_message_type=ADT_Type,
    )

    return out

# ################################################################################################################################

def adt_tls_channel() -> 'stranydict':
    """ The same feed as it reaches the PACS over its TLS listener - what a registration system naming
    itself differently in MSH-3 goes through.
    """
    out = enmasse.channel(
        ADT_TLS_Channel,
        destinations=[enmasse.mllp_destination(PACS_Destination, PACS_TLS_Connection)],
        respond_from=PACS_Destination,
        msh3_sending_app=Registration_TLS_Application,
        msh9_message_type=ADT_Type,
    )

    return out

# ################################################################################################################################

def orders_channel() -> 'stranydict':
    """ Orders go to the PACS alone, which answers for them.
    """
    out = enmasse.channel(
        Orders_Channel,
        destinations=[enmasse.mllp_destination(PACS_Destination, PACS_Connection)],
        respond_from=PACS_Destination,
        msh3_sending_app=Registration_Application,
        msh9_message_type=ORM_Type,
    )

    return out

# ################################################################################################################################

def documents_channel() -> 'stranydict':
    """ Documents from the registration system - the PACS takes images, not documents, so only the second
    department has these.
    """
    out = enmasse.channel(
        Documents_Channel,
        destinations=[enmasse.mllp_destination(Department_Destination, Department_Connection)],
        respond_from=Department_Destination,
        msh3_sending_app=Registration_Application,
        msh9_message_type=MDM_Type,
    )

    return out

# ################################################################################################################################

def pacs_channel() -> 'stranydict':
    """ Where the PACS publishes identity changes - recorded, answered by the service and carried on to
    the department.
    """
    out = enmasse.channel(
        PACS_Channel,
        service=PACS_Record_Service,
        destinations=[enmasse.mllp_destination(Department_Destination, Department_Connection)],
        msh3_sending_app=PACS_Application,
    )

    return out

# ################################################################################################################################

def build_definitions(addresses:'RegistrationAddresses') -> 'enmasse.Definitions':
    """ Everything the engine is made of.
    """
    out = enmasse.Definitions()

    out.outgoing_mllp.append(enmasse.outgoing(PACS_Connection, addresses.pacs))
    out.outgoing_mllp.append(enmasse.outgoing(PACS_TLS_Connection, addresses.pacs_tls, tls=addresses.tls))
    out.outgoing_mllp.append(enmasse.outgoing(Department_Connection, addresses.department))

    out.channel_mllp.append(adt_channel())
    out.channel_mllp.append(adt_tls_channel())
    out.channel_mllp.append(orders_channel())
    out.channel_mllp.append(documents_channel())
    out.channel_mllp.append(pacs_channel())

    return out

# ################################################################################################################################
# ################################################################################################################################
