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
from zato.common.hl7.mllp.haproxy import find_haproxy_config, reload_haproxy, resolve_internal_port, \
    update_mllp_backend_port
from zato.common.hl7.mllp.router import HL7MessageRouter
from zato.common.hl7.mllp.server import HL7MLLPServer
from zato.common.util.api import hex_sequence_to_bytes, spawn_greenlet
from zato.server.connection.wrapper import Wrapper

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Default_Start_Sequence = '0b'
_Default_End_Sequence   = '1c0d'

_Max_Msg_Size_Multipliers = {
    'kb': 1024,
    'mb': 1048576,
}

# ################################################################################################################################
# ################################################################################################################################

class _SharedMLLPState:
    """ Holds the single shared HL7MLLPServer and HL7MessageRouter instance
    across all MLLP channel wrappers within a worker process.
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
        unit = self.config.max_msg_size_unit
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
            should_log_messages=self.config.should_log_messages,
            should_return_errors=self.config.should_return_errors,
            default_character_encoding=self.config.default_character_encoding,
            should_normalize_line_endings=self.config.normalize_line_endings,
            should_repair_truncated_msh=self.config.repair_truncated_msh,
            should_split_concatenated_messages=self.config.split_concatenated_messages,
            should_force_standard_delimiters=self.config.force_standard_delimiters,
            should_use_msh18_encoding=self.config.use_msh18_encoding,
            dedup_ttl_value=dedup_ttl_value,
            dedup_ttl_unit=dedup_ttl_unit,
        )

        spawn_greenlet(_shared_state.server.start)

        # .. update the mllp_backend port in haproxy.cfg so HAProxy routes to the right place ..
        server_base_directory = self.server.base_dir # pyright: ignore[reportOptionalMemberAccess]
        haproxy_config_path = find_haproxy_config(server_base_directory)
        _shared_state.haproxy_config_path = haproxy_config_path

        if os.path.exists(haproxy_config_path):
            update_mllp_backend_port(haproxy_config_path, internal_port)
            reload_haproxy()
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
            rest_only = getattr(self.config, 'rest_only', False)

            if not rest_only:

                # Start the shared server if needed ..
                self._ensure_shared_server_started()

            # .. register this channel's routing rule only if the channel is active ..
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
                    is_default=self.config.is_default,
                )

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
            rest_channel_id = getattr(self.config, 'rest_channel_id', 0)
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
