# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from threading import Lock
from traceback import format_exc

# Zato
from zato.common.api import CHANNEL
from zato.common.audit_log.api import AuditLog
from zato.common.hl7.mllp.fields import Channel_Defaults, Channel_Int_Names, resolve_max_msg_size, Tolerance_Names
from zato.common.hl7.mllp.haproxy import resolve_internal_port
from zato.common.hl7.mllp.preprocess import build_tolerance_config
from zato.common.hl7.mllp.router import HL7MessageRouter
from zato.common.hl7.mllp.server import HL7MLLPServer
from zato.common.hl7.mllp.settings import extract_common_name, ListenerConfig, RouteSettings
from zato.common.hl7.mllp.state import ChannelState
from zato.common.typing_ import cast_
from zato.common.util.api import asbool, hex_sequence_to_bytes, spawn_greenlet
from zato.server.connection.wrapper import Wrapper
from zato.server.destination.channel import new_channel_item, run_for_channel

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, callable_, stranydict
    from zato.server.base.parallel import ParallelServer
    any_ = any_
    anylist = anylist
    callable_ = callable_
    stranydict = stranydict
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Defaults applied by the config manager when the create path does not supply a field,
# e.g. when a channel is created directly through zato.generic.connection.create.
channel_config_defaults = Channel_Defaults

# Config keys that must be integers but may arrive as strings from opaque storage
channel_int_config_keys = Channel_Int_Names

# What a channel is left accepting when the security definition it names cannot be resolved.
# No certificate carries this, so the channel refuses everything rather than everything through.
_Unresolvable_Common_Name = '\x00unresolvable'

# ################################################################################################################################

def _get_message_text(data:'any_') -> 'str':
    """ Returns the ER7 text of what the listener handed a channel - a channel that parses on
    input is given a parsed message and one that does not is given the text itself.
    """
    if isinstance(data, str):
        return data

    out = data.to_er7()
    return out

# What serialises the workers that all hold the same channel when its REST bridge is deleted
_Rest_Channel_Lock_Prefix = 'zato.channel.hl7.mllp.rest-channel.'
_Rest_Channel_Lock_Ttl    = 30
_Rest_Channel_Lock_Block  = 30

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
        self.internal_port = 0
        self.listener_config = ListenerConfig()

        # How many channels actually use the listener, which is what decides when it can stop.
        # A channel that only has a REST bridge never starts one and so never counts.
        self.listener_channel_count = 0

# ################################################################################################################################
# ################################################################################################################################

_shared_state = _SharedMLLPState()

# ################################################################################################################################
# ################################################################################################################################

def _iter_channel_states() -> 'anylist':
    """ Returns the live state object of every HL7 MLLP channel in this process, which is what
    both the state contract and the endpoint metrics are two projections of.
    """

    with _shared_state.lock:
        server = _shared_state.server
        channel_names = _shared_state.router.get_channel_names()

    out:'anylist' = []

    for channel_name in channel_names:

        # A running listener holds the live counters, without one there is nothing
        # to count and a zeroed state says exactly that.
        if server:
            channel_state = server.get_channel_state(channel_name)
        else:
            channel_state = ChannelState(channel_name)

        out.append(channel_state)

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_current_state() -> 'anylist':
    """ Returns the state contract of every HL7 MLLP channel in this process -
    what zato.channel.hl7.get-current-state serves. A channel that has not seen
    any traffic yet reports zero counters, and with no listener running at all
    every channel reports itself as not listening.
    """

    out:'anylist' = [channel_state.get_state() for channel_state in _iter_channel_states()]
    return out

# ################################################################################################################################
# ################################################################################################################################

def get_internal_port() -> 'int':
    """ Returns the internal port the shared MLLP listener is bound to in this process -
    zero when no listener is running, i.e. when no MLLP channel exists.
    """
    with _shared_state.lock:
        out = _shared_state.internal_port

    return out

# ################################################################################################################################
# ################################################################################################################################

def is_channel_routed(channel_name:'str') -> 'bool':
    """ Returns whether the named channel is routed by a running listener, which is what a sender
    needs before its messages reach that channel - one that arrives while the listener is up but
    the route is not yet registered matches nothing and is turned away.
    """
    with _shared_state.lock:

        # Without a listener there is nothing routing anything anywhere
        if not _shared_state.server:
            return False

        channel_names = _shared_state.router.get_channel_names()

    out = channel_name in channel_names
    return out

# ################################################################################################################################
# ################################################################################################################################

def get_current_metrics() -> 'stranydict':
    """ Returns the live endpoint metrics of every HL7 MLLP channel in this process,
    keyed by channel name - what the alerting sweep's feed-silent collector runs over.
    """

    out:'stranydict' = {}

    for channel_state in _iter_channel_states():
        out[channel_state.name] = channel_state.get_metrics()

    return out

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

    @property
    def parallel_server(self) -> 'ParallelServer':
        """ The server this channel runs on. The base class allows for one built without a server,
        which a channel never is, so this is where that is said once rather than at each use.
        """
        return cast_('ParallelServer', self.server)

# ################################################################################################################################

    def _build_channel_item(self) -> 'stranydict':
        """ What this channel says about itself to everything that runs on its behalf, in the one
        shape a message sent again from the audit log is fanned out by as well.
        """
        out = new_channel_item(self.config)
        return out

# ################################################################################################################################

    def _invoke_service(self, data:'str', cid:'str') -> 'any_':
        """ Invokes the service configured for this channel, passing the HL7 message as the request
        payload, and returns what the service's pipeline produced - which is the answer of the
        destination this channel replies from, when it replies from one of them. The invocation
        runs under the correlation id the message arrived under, so the service's own trail and
        the fan-out that follows it read as one message rather than as several.
        """
        out = self.parallel_server.invoke(
            self.config.service,
            data,
            cid=cid,
            channel=CHANNEL.HL7_MLLP,
            zato_ctx={'zato.channel_item': self._build_channel_item()},
        )

        return out

# ################################################################################################################################

    def _deliver_to_destinations(self, data:'any_', cid:'str') -> 'any_':
        """ Delivers one message to this channel's destinations with nothing between the two, which
        is what a channel that names no service does with everything it accepts. Nothing here looks
        at what the message says - a channel with no service passes bytes through and no more.
        """
        # A channel that parses on input is handed a parsed message, and what a destination
        # receives is the message rather than an object, so the text of it is what goes out
        message_text = _get_message_text(data)

        result = run_for_channel(self.parallel_server, self._build_channel_item(), message_text, cid=cid)

        # Our response to produce - a channel that replies from one of its destinations answers
        # with what that destination said, and one that does not has nothing of its own to say
        out = None

        if result:
            if result.has_response:
                out = result.response

        return out

# ################################################################################################################################

    def _get_callback(self) -> 'callable_':
        """ Returns what each message matching this channel is handed to - the channel's service
        when it names one, and its destinations directly when it does not.
        """
        if self.config.service:
            out = self._invoke_service
        else:
            out = self._deliver_to_destinations

        return out

# ################################################################################################################################

    def _resolve_max_msg_size(self) -> 'int':
        """ Converts max_msg_size and max_msg_size_unit from config into bytes.
        """
        out = resolve_max_msg_size(self.config.max_msg_size, self.config.max_msg_size_unit)
        return out

# ################################################################################################################################

    def _get_security_common_name(self) -> 'str':
        """ Resolves this channel's security definition to the client certificate common name it
        accepts. A channel without one accepts a connection whatever certificate it was made with.

        The common name is the only part of the certificate that reaches the listener, so it is
        taken from the definition's subject distinguished name, of which it is a component.
        """
        security_id = self.config.security_id

        if not security_id:
            return ''

        url_data = self.parallel_server.worker_store.request_dispatcher.url_data
        security_definition = url_data.mtls_get_by_id(security_id)

        # A definition that has been deleted since the channel referenced it leaves the channel
        # accepting nothing, which is the safe end of the two
        if not security_definition:
            logger.warning('No mTLS definition with id %s for MLLP channel `%s`', security_id, self.config.name)
            return _Unresolvable_Common_Name

        # Looking a definition up by its id gives the configuration itself, whereas looking one up
        # by name gives an object that has the configuration under an attribute of its own
        subject_dn = security_definition['client_cert_subject_dn']
        common_name = extract_common_name(subject_dn)

        # A definition that only names a fingerprint cannot be matched here, because a fingerprint
        # is not among what the listener is told about the certificate
        if not common_name:
            logger.warning('The mTLS definition for MLLP channel `%s` has no subject DN to take a common name from',
                self.config.name)
            return _Unresolvable_Common_Name

        return common_name

# ################################################################################################################################

    def _build_tolerance_config(self) -> 'object':
        """ Builds the parser's tolerance configuration from this channel's own toggles, whose
        names come from the same list the form and enmasse are built from.
        """
        toggles = {}

        for name in Tolerance_Names:
            toggles[name] = asbool(self.config[name])

        out = build_tolerance_config(**toggles)
        return out

# ################################################################################################################################

    def _build_route_settings(self) -> 'RouteSettings':
        """ Builds how this channel's own messages are framed, read and interpreted, which is what
        the listener applies to each message that matches this channel and to no other.
        """

        out = RouteSettings(
            start_sequence=hex_sequence_to_bytes(self.config.start_seq),
            end_sequence=hex_sequence_to_bytes(self.config.end_seq),

            # The form asks for milliseconds, the socket layer works in seconds
            recv_timeout=self.config.recv_timeout / 1000.0,
            max_message_size=self._resolve_max_msg_size(),
            idle_timeout=self.config.idle_timeout,

            keepalive_idle=self.config.keepalive_idle,
            keepalive_interval=self.config.keepalive_interval,
            keepalive_probe_count=self.config.keepalive_probe_count,

            default_character_encoding=self.config.default_character_encoding,
            should_use_msh18_encoding=asbool(self.config.use_msh18_encoding),
            should_normalize_line_endings=asbool(self.config.normalize_line_endings),
            should_repair_truncated_msh=asbool(self.config.repair_truncated_msh),
            should_split_concatenated_messages=asbool(self.config.split_concatenated_messages),
            should_force_standard_delimiters=asbool(self.config.force_standard_delimiters),

            should_parse_on_input=asbool(self.config.should_parse_on_input),
            should_validate=asbool(self.config.should_validate),
            should_log_messages=asbool(self.config.should_log_messages),
            should_return_errors=asbool(self.config.should_return_errors),

            tolerance_config=self._build_tolerance_config(),

            dedup_ttl_value=self.config.dedup_ttl_value,
            dedup_ttl_unit=self.config.dedup_ttl_unit,

            security_common_name=self._get_security_common_name(),
            allowed_networks=self.config.allowed_networks,
        )

        # A channel tunes underneath the listener rather than around it, so anything wider
        # than what the listener allows is brought back to it
        out.apply_listener_bounds(_shared_state.listener_config)

        return out

# ################################################################################################################################

    def _ensure_shared_server_built(self) -> 'int':
        """ Builds the shared MLLP server if this is the first channel being created in this
        process, without letting it accept anything yet. Returns the port it is to bind, or
        zero when another channel had already built it and so nothing here has to start it.
        """

        if _shared_state.server:
            return 0

        # The internal port follows from the server's own port, so every worker process of one
        # server binds the same one and HAProxy has a line for it before any channel exists
        internal_port = resolve_internal_port(self.parallel_server.port)

        # What one socket can have one of comes from the server's environment rather than
        # from whichever channel happened to be created first
        listener_config = ListenerConfig.from_env(f'127.0.0.1:{internal_port}')
        _shared_state.listener_config = listener_config

        # The shared audit log all audited channels write through -
        # whether a given message is audited is each route's own flag
        audit_log = AuditLog(self.parallel_server.name)

        _shared_state.server = HL7MLLPServer(listener_config, _shared_state.router, audit_log=audit_log)

        return internal_port

# ################################################################################################################################

    def _start_shared_listener(self, internal_port:'int') -> 'None':
        """ Puts the shared listener on its port. This is the last thing the channel that built
        it does, so that the first message to arrive finds the channel the listener exists for
        already routed rather than nothing to be matched against.
        """
        server = cast_('HL7MLLPServer', _shared_state.server)

        _ = spawn_greenlet(server.start)

        # The port is only worth reporting once there is something behind it. The load balancer
        # already points at it, that being a fixed number its own configuration file carries.
        _shared_state.internal_port = internal_port

        logger.info('Started shared MLLP server on %s', _shared_state.listener_config.address)

# ################################################################################################################################

    def _stop_shared_server(self) -> 'None':
        """ Stops the shared MLLP server when the last channel is removed.
        """

        if not _shared_state.server:
            return

        _shared_state.server.stop()
        _shared_state.server = None

        # With the listener gone there is no port to report - a sender that asks now is told
        # there is nothing to send to rather than handed a port that nothing is behind
        _shared_state.internal_port = 0

        logger.info('Stopped shared MLLP server')

# ################################################################################################################################

    def _init_impl(self) -> 'None':

        with _shared_state.lock:

            # .. a channel that only has a REST bridge never reaches the listener at all ..
            rest_only = asbool(self.config.rest_only)

            if rest_only:
                self.is_connected = True
                return

            # .. the listener has to exist before a route can be built against its bounds ..
            internal_port = self._ensure_shared_server_built()

            # .. register this channel's routing rule only if the channel is active ..
            if self.config.is_active:
                _shared_state.router.add_route(
                    channel_name=self.config.name,
                    callback=self._get_callback(),
                    service_name=self.config.service,
                    has_destinations=bool(self.config.destinations),
                    msh3_sending_application=self.config.msh3_sending_app,
                    msh4_sending_facility=self.config.msh4_sending_facility,
                    msh5_receiving_application=self.config.msh5_receiving_app,
                    msh6_receiving_facility=self.config.msh6_receiving_facility,
                    msh9_message_type=self.config.msh9_message_type,
                    msh9_trigger_event=self.config.msh9_trigger_event,
                    msh11_processing_id=self.config.msh11_processing_id,
                    msh12_version_id=self.config.msh12_version_id,
                    is_default=asbool(self.config.is_default),
                    is_audit_log_active=asbool(self.config.is_audit_log_active),
                    settings=self._build_route_settings(),
                )

            # .. a listener this channel built starts accepting only now, with its own route in place ..
            if internal_port:
                self._start_shared_listener(internal_port)

            _shared_state.listener_channel_count += 1
            self.is_connected = True

# ################################################################################################################################

    def _delete(self) -> 'None':

        with _shared_state.lock:

            rest_only = asbool(self.config.rest_only)

            # A channel that never used the listener has nothing to remove from it
            if not rest_only:

                _shared_state.router.remove_route(self.config.name)
                _shared_state.listener_channel_count -= 1

                # .. stop the shared server if no channels are left using it ..
                if _shared_state.listener_channel_count <= 0:
                    self._stop_shared_server()
                    _shared_state.listener_channel_count = 0

            self._delete_rest_channel()

# ################################################################################################################################

    def _delete_rest_channel(self) -> 'None':
        """ Removes the backing REST channel of a channel that had one. Every worker process holds
        the same channel and runs this, so the work is done under a cluster-wide lock and whoever
        gets there second finds it already gone and leaves it alone.
        """
        rest_channel_id = self.config.rest_channel_id

        if not rest_channel_id:
            return

        server = self.parallel_server
        lock_name = f'{_Rest_Channel_Lock_Prefix}{rest_channel_id}'

        with server.zato_lock_manager(lock_name, ttl=_Rest_Channel_Lock_Ttl, block=_Rest_Channel_Lock_Block):

            # Another worker holding the same channel may already have deleted it, and asking
            # is what tells that apart from a deletion that genuinely failed
            try:
                _ = server.invoke('zato.http-soap.get', {'id': rest_channel_id, 'cluster_id': 1})
            except Exception:
                logger.info('Backing REST channel id=%s is already gone', rest_channel_id)
                return

            try:
                _ = server.invoke('zato.http-soap.delete', {'id': rest_channel_id, 'cluster_id': 1})
                logger.info('Deleted backing REST channel id=%s for MLLP channel `%s`',
                    rest_channel_id, self.config.name)
            except Exception:
                logger.warning('Could not delete backing REST channel id=%s; e:`%s`', rest_channel_id, format_exc())

# ################################################################################################################################

    def _ping(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################
