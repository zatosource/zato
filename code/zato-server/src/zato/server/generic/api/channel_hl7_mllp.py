# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger
from threading import Lock

# Zato
from zato.common.api import HL7
from zato.common.hl7.mllp.haproxy import find_haproxy_config, reload_haproxy, resolve_internal_port, \
    update_mllp_backend_port
from zato.common.hl7.mllp.router import HL7MessageRouter
from zato.common.hl7.mllp.server import HL7MLLPServer
from zato.common.util.api import asbool, hex_sequence_to_bytes, spawn_greenlet
from zato.server.connection.wrapper import Wrapper

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Max_Msg_Size_Multipliers = {
    'kb': 1024,
    'mb': 1048576,
}

# Default channel config value for max_msg_size, interpreted together with max_msg_size_unit
_Default_Max_Msg_Size      = 2
_Default_Max_Msg_Size_Unit = 'mb'

# ################################################################################################################################
# ################################################################################################################################

# Defaults applied by the config manager when the create path does not supply a field,
# e.g. when a channel is created directly through zato.generic.connection.create.
channel_config_defaults:'dict[str, object]' = {

    # Framing and protocol
    'start_seq': HL7.Default.start_seq,
    'end_seq': HL7.Default.end_seq,
    'recv_timeout': HL7.Default.recv_timeout,
    'max_msg_size': _Default_Max_Msg_Size,
    'max_msg_size_unit': _Default_Max_Msg_Size_Unit,
    'read_buffer_size': HL7.Default.read_buffer_size,
    'default_character_encoding': HL7.Default.data_encoding,

    # Logging
    'should_log_messages': False,
    'should_return_errors': False,

    # Parsing
    'should_parse_on_input': True,
    'should_validate': False,

    # Tolerance toggles
    'normalize_line_endings': True,
    'repair_truncated_msh': True,
    'split_concatenated_messages': True,
    'force_standard_delimiters': True,
    'use_msh18_encoding': True,
    'normalize_obx2_value_type': True,
    'replace_invalid_obx2_value_type': True,
    'normalize_invalid_escape_sequences': True,
    'normalize_obx8_abnormal_flags': True,
    'normalize_quadruple_quoted_empty': True,
    'allow_short_encoding_characters': True,
    'fix_off_by_one_field_index': False,

    # Deduplication - disabled unless explicitly configured
    'dedup_ttl_value': 0,
    'dedup_ttl_unit': '',

    # Routing
    'msh3_sending_app': '',
    'msh4_sending_facility': '',
    'msh5_receiving_app': '',
    'msh6_receiving_facility': '',
    'msh9_message_type': '',
    'msh9_trigger_event': '',
    'msh11_processing_id': '',
    'msh12_version_id': '',
    'is_default': False,

    # REST bridge
    'use_rest': False,
    'rest_only': False,
    'rest_channel_id': 0,
}

# Config keys that must be integers but may arrive as strings from opaque storage
channel_int_config_keys = ('recv_timeout', 'max_msg_size', 'read_buffer_size', 'dedup_ttl_value', 'rest_channel_id')

# ################################################################################################################################
# ################################################################################################################################

class _SharedMLLPState:
    """ Holds the single shared HL7MLLPServer and HL7MessageRouter instance
    across all MLLP channel wrappers within a server process.
    """

    def __init__(self) -> 'None':
        self.server:'HL7MLLPServer | None' = None
        self.router:'HL7MessageRouter' = HL7MessageRouter()
        self.lock = Lock()
        self.channel_count = 0
        self.internal_port = 0
        self.haproxy_config_path = ''

# ################################################################################################################################
# ################################################################################################################################

_shared_state = _SharedMLLPState()

# ################################################################################################################################
# ################################################################################################################################

class ChannelHL7MLLPWrapper(Wrapper):
    """ Represents an HL7 MLLP channel.
    Each channel is a routing rule registered with the shared MLLP server.
    """
    needs_self_client = False
    wrapper_type = 'HL7 MLLP channel'
    build_if_not_active = True

    def __init__(self, *args:'object', **kwargs:'object') -> 'None':
        super().__init__(*args, **kwargs)

# ################################################################################################################################

    def _invoke_service(self, data:'str') -> 'object':
        """ Invokes the service configured for this channel, passing the HL7 message as the request payload.
        """
        out = self.server.invoke(self.config.service, data) # pyright: ignore[reportOptionalMemberAccess]
        return out

# ################################################################################################################################

    def _resolve_max_msg_size(self) -> 'int':
        """ Converts max_msg_size and max_msg_size_unit from config into bytes.
        """
        raw_value = self.config.max_msg_size

        # The dashboard and enmasse send the unit as MB or kB, the multiplier map is keyed lower-case
        unit = self.config.max_msg_size_unit.lower()
        multiplier = _Max_Msg_Size_Multipliers[unit]

        out = raw_value * multiplier
        return out

# ################################################################################################################################

    def _ensure_shared_server_started(self) -> 'None':
        """ Starts the shared MLLP server if this is the first channel being created.
        Updates the mllp_backend port in haproxy.cfg and reloads HAProxy.
        """

        if _shared_state.server:
            return

        # Resolve a free internal port for the MLLP server ..
        internal_port = resolve_internal_port()
        _shared_state.internal_port = internal_port

        # .. build the bind address ..
        address = f'127.0.0.1:{internal_port}'

        # .. read framing sequences from config ..
        start_sequence = hex_sequence_to_bytes(self.config.start_seq)
        end_sequence   = hex_sequence_to_bytes(self.config.end_seq)

        # .. convert recv_timeout from milliseconds to seconds ..
        recv_timeout_seconds = self.config.recv_timeout / 1000.0

        # .. resolve max message size to bytes ..
        max_msg_size_bytes = self._resolve_max_msg_size()

        # .. resolve dedup config ..
        dedup_ttl_value = self.config.dedup_ttl_value
        dedup_ttl_unit = self.config.dedup_ttl_unit

        # .. create and start the shared server ..
        _shared_state.server = HL7MLLPServer(
            address,
            _shared_state.router,
            start_sequence,
            end_sequence,
            receive_timeout=recv_timeout_seconds,
            max_message_size=max_msg_size_bytes,
            should_log_messages=asbool(self.config.should_log_messages),
            should_return_errors=asbool(self.config.should_return_errors),
            should_parse_on_input=asbool(self.config.should_parse_on_input),
            should_validate=asbool(self.config.should_validate),
            default_character_encoding=self.config.default_character_encoding,
            should_normalize_line_endings=asbool(self.config.normalize_line_endings),
            should_repair_truncated_msh=asbool(self.config.repair_truncated_msh),
            should_split_concatenated_messages=asbool(self.config.split_concatenated_messages),
            should_force_standard_delimiters=asbool(self.config.force_standard_delimiters),
            should_use_msh18_encoding=asbool(self.config.use_msh18_encoding),
            dedup_ttl_value=dedup_ttl_value,
            dedup_ttl_unit=dedup_ttl_unit,
            normalize_obx2_value_type=asbool(self.config.normalize_obx2_value_type),
            replace_invalid_obx2_value_type=asbool(self.config.replace_invalid_obx2_value_type),
            normalize_invalid_escape_sequences=asbool(self.config.normalize_invalid_escape_sequences),
            normalize_obx8_abnormal_flags=asbool(self.config.normalize_obx8_abnormal_flags),
            normalize_quadruple_quoted_empty=asbool(self.config.normalize_quadruple_quoted_empty),
            allow_short_encoding_characters=asbool(self.config.allow_short_encoding_characters),
            fix_off_by_one_field_index=asbool(self.config.fix_off_by_one_field_index),
        )

        _ = spawn_greenlet(_shared_state.server.start)

        # .. update the mllp_backend port in haproxy.cfg so HAProxy routes to the right place ..
        server_base_directory = self.server.base_dir # pyright: ignore[reportOptionalMemberAccess]
        haproxy_config_path = find_haproxy_config(server_base_directory)
        _shared_state.haproxy_config_path = haproxy_config_path

        if os.path.exists(haproxy_config_path):
            update_mllp_backend_port(haproxy_config_path, internal_port)
            _ = reload_haproxy(haproxy_config_path)
        else:
            logger.info('HAProxy config not found at %s, skipping HAProxy integration', haproxy_config_path)

        logger.info('Started shared MLLP server on %s', address)

# ################################################################################################################################

    def _stop_shared_server(self) -> 'None':
        """ Stops the shared MLLP server when the last channel is removed.
        """

        if not _shared_state.server:
            return

        _shared_state.server.stop()
        _shared_state.server = None

        logger.info('Stopped shared MLLP server')

# ################################################################################################################################

    def _init_impl(self) -> 'None':

        with _shared_state.lock:

            # .. if rest_only is set, the MLLP listener is not started ..
            rest_only = asbool(self.config.rest_only)

            # .. register this channel's routing rule only if the channel is active.
            # The route is registered before the listener starts so the server
            # never accepts a message for which no route exists yet ..
            if self.config.is_active and not rest_only:
                _shared_state.router.add_route(
                    channel_name=self.config.name,
                    service_name=self.config.service,
                    callback=self._invoke_service,
                    msh3_sending_application=self.config.msh3_sending_app,
                    msh4_sending_facility=self.config.msh4_sending_facility,
                    msh5_receiving_application=self.config.msh5_receiving_app,
                    msh6_receiving_facility=self.config.msh6_receiving_facility,
                    msh9_message_type=self.config.msh9_message_type,
                    msh9_trigger_event=self.config.msh9_trigger_event,
                    msh11_processing_id=self.config.msh11_processing_id,
                    msh12_version_id=self.config.msh12_version_id,
                    is_default=asbool(self.config.is_default),
                )

            # .. start the shared server if needed, now that the route is in place ..
            if not rest_only:
                self._ensure_shared_server_started()

            _shared_state.channel_count += 1
            self.is_connected = True

# ################################################################################################################################

    def _delete(self) -> 'None':

        with _shared_state.lock:

            # Remove this channel's routing rule ..
            _shared_state.router.remove_route(self.config.name)
            _shared_state.channel_count -= 1

            # .. stop the shared server if no channels remain ..
            if _shared_state.channel_count <= 0:
                self._stop_shared_server()
                _shared_state.channel_count = 0

            # .. clean up the backing REST channel if one exists ..
            rest_channel_id = self.config.rest_channel_id
            if rest_channel_id:
                try:
                    self.server.invoke('zato.http-soap.delete', { # pyright: ignore[reportOptionalMemberAccess]
                        'id': rest_channel_id,
                        'cluster_id': 1,
                    })
                    logger.info('Deleted backing REST channel id=%s for MLLP channel `%s`', rest_channel_id, self.config.name)
                except Exception:
                    logger.warning('Could not delete backing REST channel id=%s', rest_channel_id)

# ################################################################################################################################

    def _ping(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################
