# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from logging import getLogger

# Zato
from zato.common.hl7.audit import audit_ack_sent, audit_batch_received, get_wire_attrs
from zato.common.hl7.mllp.dedup import extract_control_id
from zato.common.hl7.mllp.reply import Accepted_Ack_Code, Rejection_Ack_Code, invoke_callback, resolve_reply
from zato.common.util.api import new_cid_server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.hl7.mllp.connection import ConnectionContext
    from zato.common.hl7.mllp.preprocess import BatchPayload
    from zato.common.hl7.mllp.router import ChannelRoute
    from zato.common.hl7.mllp.settings import RouteSettings
    from zato.common.typing_ import any_

    BatchPayload = BatchPayload
    ChannelRoute = ChannelRoute
    ConnectionContext = ConnectionContext
    RouteSettings = RouteSettings
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# What the sender is told when a batch matched no channel
_No_Channel_Error_Text = 'No matching channel for this batch'

# ################################################################################################################################
# ################################################################################################################################

def extract_first_msh_line(data:'str') -> 'str':
    """ Finds the first MSH segment line inside a batch/file payload.
    Used for routing and ACK building when the frame is a batch.
    """

    # .. scan through CR-delimited segments looking for the first MSH ..
    for line in data.split('\r'):
        if line.startswith('MSH|'):
            return line

    return ''

# ################################################################################################################################

def handle_batch_payload(
    server:'any_',
    active_socket:'socket.socket',
    batch_payload:'BatchPayload',
    connection_context:'ConnectionContext',
    matched_route:'ChannelRoute | None',
    settings:'RouteSettings',
    ) -> 'None':
    """ Processes a batch/file payload (BHS|... or FHS|...) as a single unit.
    The whole batch belongs to the channel its frame matched, and the entire raw batch string
    is passed to that channel's callback.
    """

    raw = batch_payload.raw

    # .. the ACK is built from the first MSH inside the batch, the routing decision
    # .. having already been made on the frame's own first line ..
    msh_line = extract_first_msh_line(raw)

    # .. if the batch contains no MSH at all, there is nothing to ACK ..
    if not msh_line:
        server.state.on_error()
        logger.warning('Batch payload from %s contains no MSH segment', connection_context.endpoint)
        return

    raw_length = len(raw)

    if settings.should_log_messages:
        logger.info('Processing batch payload (%d bytes) from %s', raw_length, connection_context.endpoint)

    # .. a matched batch counts on its channel's own state too ..
    if matched_route:
        channel_state = server.get_channel_state(matched_route.channel_name)
        channel_state.on_message_received()
    else:
        channel_state = None

    # .. a batch is audited when its channel says so - with no route there is no channel to ask,
    # .. and the channel it is filed under is what says afterwards whether it was audited ..
    audit_log = server.audit_log
    audit_channel_name = ''

    # .. all the batch's audit events share one correlation id ..
    if audit_log and matched_route and matched_route.is_audit_log_active:

        audit_cid = new_cid_server()
        audit_channel_name = matched_route.channel_name

        # .. the parent row for the batch plus a child row per contained message ..
        _ = audit_batch_received(
            audit_log, audit_channel_name, raw,
            cid=audit_cid, endpoint=connection_context.endpoint)
    else:
        audit_cid = ''

    # .. no route found - reject the entire batch ..
    if matched_route is None:
        logger.warning('No matching MLLP channel for batch from %s (MSH: %s)',
            connection_context.endpoint, msh_line)
        callback_response = None
        ack_code          = Rejection_Ack_Code
        error_text        = _No_Channel_Error_Text
        error_condition   = None

    # .. route found - pass the entire raw batch to the service callback,
    # .. the service is responsible for calling parse_batch_or_file on it ..
    else:

        if settings.should_log_messages:
            target = matched_route.get_target()
            logger.info('Routing batch to channel `%s` (%s)', matched_route.channel_name, target)

        # .. invoke the callback with the raw batch string, under the correlation id the
        # .. batch's own rows were written with, so everything it leads to shares them ..
        outcome = invoke_callback(matched_route, raw, audit_cid, connection_context.endpoint, 'batch')

        callback_response = outcome.callback_response
        ack_code          = outcome.ack_code
        error_text        = outcome.error_text
        error_condition   = outcome.error_condition

    # .. suppress error details if the channel is configured to hide them ..
    if not settings.should_return_errors:
        error_text = ''

    # .. the batch's acknowledgment outcome feeds the live state, the channel's own included ..
    if ack_code == Accepted_Ack_Code:
        server.state.on_ack_sent()
        if channel_state:
            channel_state.on_ack_sent()
    else:
        server.state.on_nack_sent()
        if channel_state:
            channel_state.on_nack_sent()

    # .. build the ACK using the first MSH from the batch, unless the channel already
    # .. answered with a message of its own ..
    ack_string = resolve_reply(callback_response, msh_line, ack_code, error_text, error_condition)

    # .. one acknowledgment covers the entire batch, on the same cid as its rows ..
    if audit_log and audit_channel_name:
        control_id = extract_control_id(msh_line)
        wire_attrs = get_wire_attrs(msh_line)

        _ = audit_ack_sent(
            audit_log, audit_channel_name, ack_code, ack_string,
            cid=audit_cid, msg_id=control_id, facility=wire_attrs['facility'])

    server.send_framed(active_socket, ack_string, settings, connection_context)

# ################################################################################################################################
# ################################################################################################################################
