# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from logging import getLogger
from time import monotonic

# Zato
from zato.common.hl7.audit import audit_ack_sent, audit_message_received, get_audit_attrs, get_control_id, \
    get_wire_attrs
from zato.common.hl7.mllp.ack import build_ack, Condition_Data_Type_Error, Condition_Unsupported_Message
from zato.common.hl7.mllp.batch import handle_batch_payload
from zato.common.hl7.mllp.dedup import extract_control_id
from zato.common.hl7.mllp.preprocess import BatchPayload, preprocess_message
from zato.common.hl7.mllp.reply import Accepted_Ack_Code, MSH9_Field_Index, Rejection_Ack_Code, \
    Unmatched_Object_Name, invoke_callback, resolve_reply
from zato.common.hl7.mllp.trace import Ms_Per_Second, trace
from zato.common.util.api import new_cid_server

from zato.hl7v2 import HL7ValidationError, parse_hl7

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.hl7.mllp.connection import ConnectionContext
    from zato.common.hl7.mllp.router import ChannelRoute
    from zato.common.hl7.mllp.settings import RouteSettings
    from zato.common.typing_ import any_

    ChannelRoute = ChannelRoute
    ConnectionContext = ConnectionContext
    RouteSettings = RouteSettings
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# What the sender is told when its message matched no channel
_No_Channel_Error_Text = 'No matching channel for this message'

# What the sender is told when MSH-9 names no message type
_No_Message_Type_Error_Text = 'No message type in MSH-9'

# The acknowledgment code and text a message that cannot be parsed or validated is answered with
_Parse_Error_Ack_Code = 'AE'
_Parse_Error_Text     = 'Message parsing or validation failed'

# ################################################################################################################################
# ################################################################################################################################

def handle_duplicate(
    server:'any_',
    active_socket:'socket.socket',
    msh_line:'str',
    control_id:'str',
    settings:'RouteSettings',
    connection_context:'ConnectionContext',
    channel_name:'str',
    ) -> 'None':
    """ Answers a message the matched channel has already seen within its own TTL window.
    A duplicate is acknowledged positively and its callback is not invoked.
    """
    if settings.should_log_messages:
        logger.info('Duplicate message (MSH-10: %s) from %s, skipping', control_id, connection_context.endpoint)

    # A duplicate's acknowledgment feeds the live state, the channel's own included
    server.state.on_ack_sent()

    channel_state = server.get_channel_state(channel_name)
    channel_state.on_ack_sent()

    ack_string = build_ack(msh_line, Accepted_Ack_Code)
    server.send_framed(active_socket, ack_string, settings, connection_context)

# ################################################################################################################################

def handle_message(
    server:'any_',
    active_socket:'socket.socket',
    raw_message_bytes:'bytes',
    connection_context:'ConnectionContext',
    matched_route:'ChannelRoute | None',
    settings:'RouteSettings',
    ) -> 'None':
    """ Processes a single unframed HL7 message under the settings of the channel it matched:
    pre-process, deliver, send ACK.
    """

    connection_context.total_messages_received += 1
    server.state.on_message_received()

    # Trace point 1: the message arrived and processing begins
    message_start = monotonic()
    byte_count = len(raw_message_bytes)

    trace('message #%d in (%d bytes)', connection_context.total_messages_received, byte_count)

    if settings.should_log_messages:
        logger.info('Received message #%d (%d bytes) from %s',
            connection_context.total_messages_received, byte_count, connection_context.endpoint)

    # Run the pre-processing pipeline under the matched channel's own settings ..
    preprocessed = preprocess_message(
        raw_message_bytes,
        should_normalize_line_endings=settings.should_normalize_line_endings,
        should_restore_truncated_msh=settings.should_restore_truncated_msh,
        should_split_concatenated_messages=settings.should_split_concatenated_messages,
        should_force_standard_delimiters=settings.should_force_standard_delimiters,
        should_use_msh18_encoding=settings.should_use_msh18_encoding,
        default_character_encoding=settings.default_character_encoding,
    )

    # .. if the payload is a batch/file, handle it as a single unit ..
    if isinstance(preprocessed, BatchPayload):
        handle_batch_payload(server, active_socket, preprocessed, connection_context, matched_route, settings)
        return

    # .. process each message (usually just one, unless concatenated) ..
    for message_text in preprocessed:

        # .. extract the MSH line for ACK building ..
        first_cr = message_text.find('\r')

        if first_cr == -1:
            msh_line = message_text
        else:
            msh_line = message_text[:first_cr]

        # .. a channel with deduplication on answers a control id it has already seen
        # .. without invoking anything - only a matched route carries a deduplicator ..
        if matched_route:
            if settings.deduplicator:

                control_id = extract_control_id(msh_line)

                # .. only deduplicate if the message actually has a control ID ..
                if control_id:
                    if settings.deduplicator.is_duplicate(control_id):
                        handle_duplicate(server, active_socket, msh_line, control_id, settings,
                            connection_context, matched_route.channel_name)
                        continue

        # .. a matched message counts on its channel's own state too ..
        if matched_route:
            channel_state = server.get_channel_state(matched_route.channel_name)
            channel_state.on_message_received()
        else:
            channel_state = None

        # .. a matched message is audited when its channel says so, and one that matched
        # .. nothing is always audited, filed under a reserved name of its own, since there
        # .. is no channel whose audit setting could be consulted ..
        audit_log = server.audit_log
        audit_channel_name = ''

        if audit_log:
            if matched_route is None:
                audit_channel_name = Unmatched_Object_Name
            elif matched_route.is_audit_log_active:
                audit_channel_name = matched_route.channel_name

        # .. the received event and its acknowledgment share one correlation id,
        # .. with the wire-level attributes as the defaults the parsed ones replace ..
        if audit_channel_name:
            audit_cid = new_cid_server()
            audit_msg_id = extract_control_id(msh_line)
            audit_attrs = get_wire_attrs(msh_line)
            peer_endpoint = connection_context.endpoint
        else:
            audit_cid = ''
            audit_msg_id = ''
            audit_attrs = {}
            peer_endpoint = ''

        # .. how long the service callback ran, reported on the acknowledgment's row ..
        callback_duration_ms = 0

        # .. what the channel answered with itself, when it answered at all,
        # .. and what ERR-3 says when the acknowledgment is a negative one ..
        callback_response = None
        error_condition   = None

        if matched_route is None:
            logger.warning('No matching MLLP channel for message from %s (MSH: %s)',
                connection_context.endpoint, msh_line)
            ack_code   = Rejection_Ack_Code
            error_text = _No_Channel_Error_Text

            # .. a turned-away message still leaves its receipt behind, the acknowledgment
            # .. that answers it landing on the same correlation id further below ..
            if audit_log and audit_channel_name:
                _ = audit_message_received(
                    audit_log, audit_channel_name, message_text,
                    cid=audit_cid, msg_id=audit_msg_id, attrs=audit_attrs, endpoint=peer_endpoint)

        # .. invoke the matched route's callback ..
        else:

            if settings.should_log_messages:
                target = matched_route.get_target()
                logger.info('Routing message to channel `%s` (%s)', matched_route.channel_name, target)

            # .. when should_parse_on_input is enabled, parse the raw ER7 text
            # .. into a structured HL7Message object. If should_validate is also
            # .. enabled, the parser runs validation and raises on errors.
            # .. On success the callback receives the parsed object, otherwise
            # .. it receives the raw ER7 string.
            if settings.should_parse_on_input:

                # .. a header with no message type cannot be identified as any message at all,
                # .. so it is turned away here rather than handed to a parser that can only
                # .. refuse it - the sender is told exactly what was missing ..
                msh_fields = msh_line.split('|')
                field_count = len(msh_fields)

                if field_count > MSH9_Field_Index:
                    message_type = msh_fields[MSH9_Field_Index]
                else:
                    message_type = ''

                if not message_type:
                    logger.warning('No message type in MSH-9 from %s, rejecting (MSH: %s)',
                        connection_context.endpoint, msh_line)

                    ack_code   = Rejection_Ack_Code
                    error_text = _No_Message_Type_Error_Text

                    # .. suppress error details if the channel hides them ..
                    if not settings.should_return_errors:
                        error_text = ''

                    # .. a reject is a negative acknowledgment in the channel's live state,
                    # .. the matched channel's own included ..
                    server.state.on_nack_sent()
                    if channel_state:
                        channel_state.on_nack_sent()

                    ack_string = build_ack(msh_line, ack_code, error_text=error_text,
                        error_condition=Condition_Unsupported_Message)

                    # .. a rejected message still leaves its audit trail - the receipt
                    # .. and the negative acknowledgment that answered it ..
                    if audit_log and audit_channel_name:
                        _ = audit_message_received(
                            audit_log, audit_channel_name, message_text,
                            cid=audit_cid, msg_id=audit_msg_id, attrs=audit_attrs, endpoint=peer_endpoint)
                        _ = audit_ack_sent(
                            audit_log, audit_channel_name, ack_code, ack_string,
                            cid=audit_cid, msg_id=audit_msg_id, facility=audit_attrs['facility'])

                    server.send_framed(active_socket, ack_string, settings, connection_context)

                    # .. skip to the next message in the batch ..
                    continue

                # .. attempt to parse (and optionally validate) the message ..
                try:
                    # Trace point 2: how long the parse took
                    parse_start = monotonic()

                    callback_data = parse_hl7(
                        message_text, validate=settings.should_validate, tolerance=settings.tolerance_config)

                    parse_ms = (monotonic() - parse_start) * Ms_Per_Second
                    trace('parse done %.1fms (%s)', parse_ms, audit_msg_id)

                    # .. a parsed message contributes richer searchable attributes,
                    # .. including the patient's medical record number ..
                    if audit_channel_name:
                        audit_attrs = get_audit_attrs(callback_data)
                        audit_msg_id = get_control_id(callback_data)

                # .. parsing or validation failed - send an AE reject ACK
                # .. back to the sender and skip this message. A malformed message is the
                # .. sender's error rather than an internal one, so one line says what was
                # .. wrong without a traceback ..
                except (ValueError, HL7ValidationError) as e:
                    logger.warning('Parse/validation error for channel `%s` from %s; e:`%s`',
                        matched_route.channel_name, connection_context.endpoint, e)
                    ack_code   = _Parse_Error_Ack_Code
                    error_text = _Parse_Error_Text

                    # .. suppress error details if the channel hides them ..
                    if not settings.should_return_errors:
                        error_text = ''

                    # .. a reject is a negative acknowledgment in the channel's live state,
                    # .. the matched channel's own included ..
                    server.state.on_nack_sent()
                    if channel_state:
                        channel_state.on_nack_sent()

                    ack_string = build_ack(msh_line, ack_code, error_text=error_text,
                        error_condition=Condition_Data_Type_Error)

                    # .. a rejected message still leaves its audit trail - the receipt
                    # .. and the negative acknowledgment that answered it ..
                    if audit_log and audit_channel_name:
                        _ = audit_message_received(
                            audit_log, audit_channel_name, message_text,
                            cid=audit_cid, msg_id=audit_msg_id, attrs=audit_attrs, endpoint=peer_endpoint)
                        _ = audit_ack_sent(
                            audit_log, audit_channel_name, ack_code, ack_string,
                            cid=audit_cid, msg_id=audit_msg_id, facility=audit_attrs['facility'])

                    server.send_framed(active_socket, ack_string, settings, connection_context)

                    # .. skip to the next message in the batch ..
                    continue

            # .. parsing not enabled - pass the raw ER7 string to the callback ..
            else:
                callback_data = message_text

            # .. the receipt is recorded before the service runs, so a message
            # .. that crashes its service is still visibly received ..
            if audit_log and audit_channel_name:

                # Trace point 3: how long the received-event audit write took
                audit_received_start = monotonic()

                _ = audit_message_received(
                    audit_log, audit_channel_name, message_text,
                    cid=audit_cid, msg_id=audit_msg_id, attrs=audit_attrs, endpoint=peer_endpoint)

                audit_received_ms = (monotonic() - audit_received_start) * Ms_Per_Second
                trace('audit received done %.1fms (%s)', audit_received_ms, audit_msg_id)

            # .. invoke the matched route's service callback ..
            callback_start = monotonic()

            # The correlation id goes along with the message, so what the channel does with it
            # next - the service it runs and the destinations it fans out to - is recorded
            # under the very id the receipt was
            outcome = invoke_callback(
                matched_route, callback_data, audit_cid, connection_context.endpoint, 'message')

            callback_response = outcome.callback_response
            ack_code          = outcome.ack_code
            error_text        = outcome.error_text
            error_condition   = outcome.error_condition

            callback_duration_ms = int((monotonic() - callback_start) * Ms_Per_Second)

            # Trace point 4: how long the service callback ran
            trace('callback done %dms (%s)', callback_duration_ms, audit_msg_id)

        # .. suppress error details if configured to not return errors ..
        if not settings.should_return_errors:
            error_text = ''

        # .. the acknowledgment outcome feeds the live state, the channel's own included ..
        if ack_code == Accepted_Ack_Code:
            server.state.on_ack_sent()
            if channel_state:
                channel_state.on_ack_sent()
        else:
            server.state.on_nack_sent()
            if channel_state:
                channel_state.on_nack_sent()

        # .. a channel that answered with a message of its own is answered with,
        # .. and everything else is acknowledged by an acknowledgment built here ..
        ack_string = resolve_reply(callback_response, msh_line, ack_code, error_text, error_condition)

        # .. the acknowledgment lands on the same cid as the receipt it answers ..
        if audit_log and audit_channel_name:

            # Trace point 5: how long the acknowledgment audit write took
            audit_ack_start = monotonic()

            _ = audit_ack_sent(
                audit_log, audit_channel_name, ack_code, ack_string,
                cid=audit_cid, msg_id=audit_msg_id, facility=audit_attrs['facility'],
                duration_ms=callback_duration_ms)

            audit_ack_ms = (monotonic() - audit_ack_start) * Ms_Per_Second
            trace('audit ack done %.1fms (%s)', audit_ack_ms, audit_msg_id)

        server.send_framed(active_socket, ack_string, settings, connection_context)

        # Trace point 6: the ACK left and the message is fully processed
        total_ms = (monotonic() - message_start) * Ms_Per_Second
        trace('message done %.1fms total (%s %s)', total_ms, ack_code, audit_msg_id)

# ################################################################################################################################
# ################################################################################################################################
