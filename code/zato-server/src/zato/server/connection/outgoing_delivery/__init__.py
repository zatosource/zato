# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a queued message is handed over to an outgoing connection - a locator and a handler per connection type.

# stdlib
from logging import getLogger

# Zato
from zato.common.api import GENERIC
from zato.common.pubsub.outgoing import OutgoingType, register_outgoing_conn_type
from zato.server.connection.outgoing_delivery.files import deliver_to_ftp, deliver_to_sftp, deliver_to_smb, locate_ftp, \
    locate_sftp, locate_smb
from zato.server.connection.outgoing_delivery.http import deliver_to_fhir, deliver_to_rest, deliver_to_soap, fhir_page, \
    get_http_dlq_settings, get_http_retry_policy, locate_fhir, locate_rest, locate_soap, rest_page, soap_page

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

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

def register_delivery_handlers() -> 'None':
    """ Registers every type of outgoing connection that can be published to.
    """
    register_outgoing_conn_type(OutgoingType.REST, locate_rest, deliver_to_rest,
        retry_policy=get_http_retry_policy, dlq_settings=get_http_dlq_settings, page=rest_page)
    register_outgoing_conn_type(OutgoingType.SOAP, locate_soap, deliver_to_soap,
        retry_policy=get_http_retry_policy, dlq_settings=get_http_dlq_settings, page=soap_page)
    register_outgoing_conn_type(OutgoingType.FHIR, locate_fhir, deliver_to_fhir,
        retry_policy=get_http_retry_policy, dlq_settings=get_http_dlq_settings, page=fhir_page)

    # File deliveries are recorded as file-outgoing audit events already
    register_outgoing_conn_type(OutgoingType.SFTP, locate_sftp, deliver_to_sftp, is_audit_log_active=False)
    register_outgoing_conn_type(OutgoingType.SMB, locate_smb, deliver_to_smb, is_audit_log_active=False)
    register_outgoing_conn_type(OutgoingType.FTP, locate_ftp, deliver_to_ftp, is_audit_log_active=False)

# ################################################################################################################################
# ################################################################################################################################

