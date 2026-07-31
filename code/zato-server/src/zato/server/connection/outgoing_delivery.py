# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a message published to an outgoing connection is actually handed over to it. There are two
# functions per type of connection - one that finds a connection by the id it was published to,
# and one that gives a message to what was found - each of them reaching the connection the way
# a service would, so an edit to a connection is picked up without anything here being told about
# it. A handler raises when the connection did not accept the message, which is what makes the
# pub/sub delivery loop keep the message queued and try again.

# stdlib
from json import loads
from logging import getLogger

# Zato
from zato.common.api import GENERIC
from zato.common.pubsub.outgoing import OutgoingType, register_outgoing_conn_type

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple
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

# Which generic connection type is published to as which kind of outgoing connection. A type that is
# not here has no queue, so a rename or a delete of one has nothing to move or to remove.
publishable_generic_types = {
    GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR: OutgoingType.FHIR,
}

# ################################################################################################################################
# ################################################################################################################################

def _locate_rest(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ Finds an outgoing REST connection by its id, which is what the connection keeps through a rename.
    """
    item = server.config_manager.config_store.out_plain_http.get_by_id(conn_id)

    # A connection that was deleted is no longer anywhere to be found
    if not item:
        return ()

    out = (item.config['name'], item.conn)
    return out

# ################################################################################################################################

def _deliver_to_rest(server:'ParallelServer', cid:'str', wrapper:'any_', data:'str') -> 'None':
    """ Hands one message over to an outgoing REST connection.
    """

    # The method, address, headers, query string and credentials all come from the connection itself ..
    response = wrapper.rest_invoke(cid, data)

    # .. and a response that was not accepted comes back rather than being raised, so it becomes an exception here.
    _ = response.raise_for_status()

# ################################################################################################################################

def _locate_fhir(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ Finds an outgoing HL7 FHIR connection by its id. These connections live in a dict keyed by name,
    so the id is what each of them is compared by.
    """
    for item in server.config_manager.outconn_hl7_fhir.values():
        if item['id'] == conn_id:
            out = (item['name'], item.conn)
            return out

    return ()

# ################################################################################################################################

def _deliver_to_fhir(server:'ParallelServer', cid:'str', wrapper:'any_', data:'str') -> 'None':
    """ Hands one message over to an outgoing HL7 FHIR connection, as a resource of the type the document names.
    """

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
    register_outgoing_conn_type(OutgoingType.REST, _locate_rest, _deliver_to_rest)
    register_outgoing_conn_type(OutgoingType.FHIR, _locate_fhir, _deliver_to_fhir)

# ################################################################################################################################
# ################################################################################################################################
