# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a queued message is handed over to an outgoing HL7 MLLP connection, and what the delivery page shows of it.

# Zato
from zato.common.pubsub.outgoing import Body_Mode_HL7, OutgoingPage

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple, dictlist, stranydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

# What the Destination column opens with - the protocol, the address of the receiving system following
_destination_prefix = 'MLLP'

# ################################################################################################################################
# ################################################################################################################################

def locate_mllp(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ An outgoing HL7 MLLP connection by its id, as its name and its wrapper.
    """
    for item in server.config_manager.outconn_hl7_mllp.values():
        if item['id'] == conn_id:
            out = (item['name'], item.conn)
            return out

    return ()

# ################################################################################################################################

def deliver_to_mllp(server:'ParallelServer', cid:'str', wrapper:'any_', request:'stranydict') -> 'None':
    """ Makes one attempt to hand a message over to an outgoing HL7 MLLP connection - an acknowledgment that is not
    an AA or a CA raises, as a send that no acknowledgment came back from does.
    """
    _ = wrapper.send_from_queue(cid, request)

# ################################################################################################################################
# ################################################################################################################################

def get_mllp_destination(wrapper:'any_', request:'stranydict') -> 'str':
    """ Where a queued HL7 message goes - the receiving system's host and port.
    """
    out = f'{_destination_prefix} {wrapper.config.address}'
    return out

# ################################################################################################################################

def get_mllp_details_facts(request:'stranydict') -> 'dictlist':
    """ A queued HL7 message has no request facts beyond its body - the message itself says what it is.
    """
    return []

# ################################################################################################################################

def get_mllp_body_mode(request:'stranydict') -> 'str':
    """ A queued HL7 message's body is ER7 text.
    """
    return Body_Mode_HL7

# ################################################################################################################################

# What the delivery page shows of an outgoing HL7 MLLP connection's messages - its list page's invoke dialog
# takes a message of its own rather than a queued one, so the destination is not a link
mllp_page = OutgoingPage()
mllp_page.destination = get_mllp_destination
mllp_page.details_facts = get_mllp_details_facts
mllp_page.body_mode = get_mllp_body_mode

# ################################################################################################################################
# ################################################################################################################################
