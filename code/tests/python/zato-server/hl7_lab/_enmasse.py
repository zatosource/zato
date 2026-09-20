# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Live HL7
from live_hl7 import enmasse

# Zato - the suite's own parts
from _messages import LIS_Application, Order_Message_Type
from _services import Orders_Channel, Orders_Record_Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

# The middleware's one outgoing connection - the LIS, on the MLLP port its bridge listens on
LIS_Connection = 'lis'

# Where analyzers report results to - the orders channel is named next to its service
Results_Channel = 'lab.results'

# What the results channel calls its destination
LIS_Destination = 'lis'

# Message types, as MSH-9 carries them
ORU_Type = 'ORU'

# ################################################################################################################################
# ################################################################################################################################

def orders_channel() -> 'stranydict':
    """ The analyzer's side of the middleware - the LIS dispatches an order here, the service records it and
    acknowledges it, as an analyzer taking the order would.
    """
    out = enmasse.channel(
        Orders_Channel,
        service=Orders_Record_Service,
        msh3_sending_app=LIS_Application,
        msh9_message_type=Order_Message_Type,
    )

    return out

# ################################################################################################################################

def results_channel() -> 'stranydict':
    """ The LIS's side of the middleware - an analyzer reports here, the result goes on to the LIS and the
    analyzer hears what the LIS said of it.
    """
    out = enmasse.channel(
        Results_Channel,
        destinations=[enmasse.mllp_destination(LIS_Destination, LIS_Connection)],
        respond_from=LIS_Destination,
        msh9_message_type=ORU_Type,
    )

    return out

# ################################################################################################################################

def build_definitions(lis_address:'str') -> 'enmasse.Definitions':
    """ Everything the middleware is made of.
    """
    out = enmasse.Definitions()

    out.outgoing_mllp.append(enmasse.outgoing(LIS_Connection, lis_address))

    out.channel_mllp.append(orders_channel())
    out.channel_mllp.append(results_channel())

    return out

# ################################################################################################################################
# ################################################################################################################################
