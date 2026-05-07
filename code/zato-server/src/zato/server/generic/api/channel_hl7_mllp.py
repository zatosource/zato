# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
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

        # .. use default MLLP framing sequences ..
        start_sequence = hex_sequence_to_bytes(_Default_Start_Sequence)
        end_sequence   = hex_sequence_to_bytes(_Default_End_Sequence)

        # .. create and start the shared server ..
        _shared_state.server = HL7MLLPServer(
            address,
            _shared_state.router,
            start_sequence,
            end_sequence,
        )

        spawn_greenlet(_shared_state.server.start)

        # .. update the mllp_backend port in haproxy.cfg so HAProxy routes to the right place ..
        server_base_directory = self.server.base_dir # pyright: ignore[reportOptionalMemberAccess]
        haproxy_config_path = find_haproxy_config(server_base_directory)
        _shared_state.haproxy_config_path = haproxy_config_path

        update_mllp_backend_port(haproxy_config_path, internal_port)
        reload_haproxy()

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

            # Start the shared server if needed ..
            self._ensure_shared_server_started()

            # .. register this channel's routing rule ..
            _shared_state.router.add_route(
                channel_name=self.config.name,
                service_name=self.config.service,
                callback=self._invoke_service,
                msh3_sending_application=self.config.get('msh3_sending_app', ''),      # pyright: ignore[reportAttributeAccessIssue]
                msh4_sending_facility=self.config.get('msh4_sending_facility', ''),     # pyright: ignore[reportAttributeAccessIssue]
                msh5_receiving_application=self.config.get('msh5_receiving_app', ''),    # pyright: ignore[reportAttributeAccessIssue]
                msh6_receiving_facility=self.config.get('msh6_receiving_facility', ''),  # pyright: ignore[reportAttributeAccessIssue]
                msh9_message_type=self.config.get('msh9_message_type', ''),             # pyright: ignore[reportAttributeAccessIssue]
                msh9_trigger_event=self.config.get('msh9_trigger_event', ''),           # pyright: ignore[reportAttributeAccessIssue]
                msh11_processing_id=self.config.get('msh11_processing_id', ''),         # pyright: ignore[reportAttributeAccessIssue]
                msh12_version_id=self.config.get('msh12_version_id', ''),               # pyright: ignore[reportAttributeAccessIssue]
                is_default=self.config.get('is_default', False),                        # pyright: ignore[reportAttributeAccessIssue]
            )

            _shared_state.channel_count += 1
            self.is_connected = True

# ################################################################################################################################

    def _delete(self) -> 'None':

        with _shared_state.lock:

            # Remove this channel's routing rule ..
            _shared_state.router.remove_route(self.config.name)
            _shared_state.channel_count -= 1

            # .. stop the shared server if no channels remain.
            if _shared_state.channel_count <= 0:
                self._stop_shared_server()
                _shared_state.channel_count = 0

# ################################################################################################################################

    def _ping(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################
