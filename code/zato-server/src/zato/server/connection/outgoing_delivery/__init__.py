# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a queued message is handed over to an outgoing connection - a locator and a handler per connection type.

# stdlib
from json import loads
from logging import getLogger

# Zato
from zato.common.api import GENERIC
from zato.common.pubsub.outgoing import Key_Data, OutgoingType, register_outgoing_conn_type
from zato.server.connection.outgoing_delivery.files import deliver_to_ftp, deliver_to_sftp, deliver_to_smb, locate_ftp, \
    locate_sftp, locate_smb
from zato.server.connection.outgoing_delivery.http import deliver_to_rest, get_rest_dlq_settings, get_rest_retry_policy, \
    locate_rest, rest_page

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple, stranydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# How many seconds to wait for a pooled FHIR client
_fhir_block_timeout = 30

_fhir_method = 'POST'

# ################################################################################################################################
# ################################################################################################################################

# Which generic connection type is which kind of outgoing connection
publishable_generic_types = {
    GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR: OutgoingType.FHIR,
    GENERIC.CONNECTION.TYPE.OUTCONN_SFTP: OutgoingType.SFTP,
    GENERIC.CONNECTION.TYPE.OUTCONN_SMB: OutgoingType.SMB,
    GENERIC.CONNECTION.TYPE.OUTCONN_FTP: OutgoingType.FTP,
}

# ################################################################################################################################
# ################################################################################################################################

def _locate_fhir(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ An outgoing HL7 FHIR connection by its id, as its name and its wrapper.
    """
    for item in server.config_manager.outconn_hl7_fhir.values():
        if item['id'] == conn_id:
            out = (item['name'], item.conn)
            return out

    return ()

# ################################################################################################################################

def _deliver_to_fhir(server:'ParallelServer', cid:'str', wrapper:'any_', request:'stranydict') -> 'None':
    """ Hands one message over to an outgoing HL7 FHIR connection as a resource of the type the document names.
    """
    resource = loads(request[Key_Data])
    path = resource['resourceType']

    with wrapper.client(should_block=True, block_timeout=_fhir_block_timeout) as client:
        _ = client._do_request(_fhir_method, path, data=resource)


# ################################################################################################################################
# ################################################################################################################################

def register_delivery_handlers() -> 'None':
    """ Registers every type of outgoing connection that can be published to.
    """
    register_outgoing_conn_type(OutgoingType.REST, locate_rest, deliver_to_rest,
        retry_policy=get_rest_retry_policy, dlq_settings=get_rest_dlq_settings, page=rest_page)
    register_outgoing_conn_type(OutgoingType.FHIR, _locate_fhir, _deliver_to_fhir)

    # File deliveries are recorded as file-outgoing audit events already
    register_outgoing_conn_type(OutgoingType.SFTP, locate_sftp, deliver_to_sftp, is_audit_log_active=False)
    register_outgoing_conn_type(OutgoingType.SMB, locate_smb, deliver_to_smb, is_audit_log_active=False)
    register_outgoing_conn_type(OutgoingType.FTP, locate_ftp, deliver_to_ftp, is_audit_log_active=False)

# ################################################################################################################################
# ################################################################################################################################

