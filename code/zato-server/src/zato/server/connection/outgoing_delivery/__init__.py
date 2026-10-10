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
from zato.common.pubsub.outgoing import Direction_In, InboundType, OutgoingType, register_outgoing_conn_type
from zato.server.connection.outgoing_delivery.files import deliver_to_ftp, deliver_to_sftp, deliver_to_smb, locate_ftp, \
    locate_sftp, locate_smb
from zato.server.connection.outgoing_delivery.hl7 import deliver_to_mllp, locate_mllp, mllp_page
from zato.server.connection.outgoing_delivery.http import deliver_to_fhir, deliver_to_http_channel, deliver_to_rest, \
    deliver_to_soap, fhir_page, get_channel_dlq_settings, get_channel_retry_policy, get_http_dlq_settings, \
    get_http_retry_policy, locate_fhir, locate_rest, locate_rest_channel, locate_soap, locate_soap_channel, rest_channel_page, \
    rest_page, soap_channel_page, soap_page
from zato.server.connection.outgoing_delivery.kafka import deliver_to_kafka, deliver_to_kafka_channel, kafka_channel_page, \
    kafka_page, locate_kafka, locate_kafka_channel

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Which generic connection type is which kind of outgoing connection
publishable_generic_types = {
    GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR: OutgoingType.FHIR,
    GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP: OutgoingType.MLLP,
    GENERIC.CONNECTION.TYPE.OUTCONN_SFTP: OutgoingType.SFTP,
    GENERIC.CONNECTION.TYPE.OUTCONN_SMB: OutgoingType.SMB,
    GENERIC.CONNECTION.TYPE.OUTCONN_FTP: OutgoingType.FTP,
    GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA: OutgoingType.KAFKA,
}

# The kind of channel each generic connection type is
inbound_generic_types = {
    GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA: InboundType.KAFKA,
}

# ################################################################################################################################
# ################################################################################################################################

def register_delivery_handlers() -> 'None':
    """ Registers every type of outgoing connection that can be published to and every type of channel that has a DLQ.
    """
    register_outgoing_conn_type(OutgoingType.REST, locate_rest, deliver_to_rest,
        retry_policy=get_http_retry_policy, dlq_settings=get_http_dlq_settings, page=rest_page)
    register_outgoing_conn_type(OutgoingType.SOAP, locate_soap, deliver_to_soap,
        retry_policy=get_http_retry_policy, dlq_settings=get_http_dlq_settings, page=soap_page)
    register_outgoing_conn_type(OutgoingType.FHIR, locate_fhir, deliver_to_fhir,
        retry_policy=get_http_retry_policy, dlq_settings=get_http_dlq_settings, page=fhir_page)

    # REST and SOAP channels have a queue of their own when their queue switch is on, the message in it
    # is the request as it arrived and the delivery is the service's run.
    register_outgoing_conn_type(InboundType.REST, locate_rest_channel, deliver_to_http_channel,
        retry_policy=get_channel_retry_policy, dlq_settings=get_channel_dlq_settings, page=rest_channel_page,
        direction=Direction_In)
    register_outgoing_conn_type(InboundType.SOAP, locate_soap_channel, deliver_to_http_channel,
        retry_policy=get_channel_retry_policy, dlq_settings=get_channel_dlq_settings, page=soap_channel_page,
        direction=Direction_In)

    # An MLLP connection carries the same retry and DLQ fields as the HTTP ones do
    register_outgoing_conn_type(OutgoingType.MLLP, locate_mllp, deliver_to_mllp,
        retry_policy=get_http_retry_policy, dlq_settings=get_http_dlq_settings, page=mllp_page)

    # .. and so do a Kafka connection and a Kafka channel, the channel without a queue.
    register_outgoing_conn_type(OutgoingType.KAFKA, locate_kafka, deliver_to_kafka,
        retry_policy=get_http_retry_policy, dlq_settings=get_http_dlq_settings, page=kafka_page)
    register_outgoing_conn_type(InboundType.KAFKA, locate_kafka_channel, deliver_to_kafka_channel,
        retry_policy=get_http_retry_policy, dlq_settings=get_http_dlq_settings, page=kafka_channel_page,
        direction=Direction_In, has_queue=False)

    # File deliveries are recorded as file-outgoing audit events already
    register_outgoing_conn_type(OutgoingType.SFTP, locate_sftp, deliver_to_sftp, is_audit_log_active=False)
    register_outgoing_conn_type(OutgoingType.SMB, locate_smb, deliver_to_smb, is_audit_log_active=False)
    register_outgoing_conn_type(OutgoingType.FTP, locate_ftp, deliver_to_ftp, is_audit_log_active=False)

# ################################################################################################################################
# ################################################################################################################################
