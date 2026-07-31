# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a message published to an outgoing connection is actually handed over to it. There is one
# handler per type of connection, each of them reaching the connection the way a service would,
# so an edit to a connection is picked up without anything here being told about it. A handler
# raises when the connection did not accept the message, which is what makes the pub/sub delivery
# loop keep the message queued and try again.

# stdlib
from json import loads
from logging import getLogger

# Zato
from zato.common.pubsub.outgoing import register_delivery_handler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# How many seconds to wait for a pooled FHIR client, which covers the window
# while the connection queue is still being built at startup.
_fhir_block_timeout = 30

# A FHIR resource is created by posting it to the path its own type names.
_fhir_method = 'POST'

# ################################################################################################################################
# ################################################################################################################################

class OutgoingType:
    """ The kinds of outgoing connection that can be published to.
    """
    REST = 'rest'
    FHIR = 'fhir'

# ################################################################################################################################
# ################################################################################################################################

def _deliver_to_rest(server:'ParallelServer', cid:'str', conn_name:'str', data:'str') -> 'None':
    """ Hands one message over to an outgoing REST connection.
    """
    item = server.config_manager.config_store.out_plain_http[conn_name]
    wrapper = item.conn

    # The method, address, headers, query string and credentials all come from the connection itself ..
    response = wrapper.rest_invoke(cid, data)

    # .. and a response that was not accepted comes back rather than being raised, so it becomes an exception here.
    _ = response.raise_for_status()

# ################################################################################################################################

def _deliver_to_fhir(server:'ParallelServer', cid:'str', conn_name:'str', data:'str') -> 'None':
    """ Hands one message over to an outgoing HL7 FHIR connection, as a resource of the type the document names.
    """
    item = server.config_manager.outconn_hl7_fhir[conn_name]
    wrapper = item.conn

    # A FHIR resource travels as a document, so what arrives here as text is that document in its JSON form ..
    resource = loads(data)

    # .. and a resource is created under the path its own type names ..
    path = resource['resourceType']

    # .. through a client taken from the connection's own pool, blocking to cover the window
    # .. while that pool is still being built.
    with wrapper.client(should_block=True, block_timeout=_fhir_block_timeout) as client:
        _ = client._do_request(_fhir_method, path, data=resource)

# ################################################################################################################################
# ################################################################################################################################

def register_delivery_handlers() -> 'None':
    """ Makes every type of outgoing connection that can be published to publishable.
    """
    register_delivery_handler(OutgoingType.REST, _deliver_to_rest)
    register_delivery_handler(OutgoingType.FHIR, _deliver_to_fhir)

# ################################################################################################################################
# ################################################################################################################################
