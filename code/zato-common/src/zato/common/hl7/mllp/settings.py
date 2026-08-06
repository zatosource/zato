# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from ipaddress import ip_address, ip_network

# Zato
from zato.common.hl7.mllp.dedup import Default_Max_Entries, MessageDeduplicator

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist
    from zato.hl7v2_rs import ToleranceConfig
    strlist = strlist
    ToleranceConfig = ToleranceConfig

# ################################################################################################################################
# ################################################################################################################################

# What one socket can have one of, in the units the listener uses.
Default_Bind_Address               = '127.0.0.1:31312'
Default_Max_Concurrent_Connections = 1000
Default_Accept_Backlog             = 128
Default_Read_Buffer_Size           = 4096

# The bounds that apply to the stretch of a connection before a route is known. They are the
# listener's own, because there is no channel to ask until the first line has been read.
Default_Max_First_Line_Size    = 8192
Default_First_Line_Timeout     = 30.0
Default_Max_Message_Size       = 16 * 1024 * 1024

# How long a connection may produce nothing at all before it is closed, and what one route
# is allowed to spend reading one message.
Default_Idle_Timeout  = 300.0
Default_Recv_Timeout  = 30.0

# What a route's messages are read and interpreted as when nothing says otherwise.
Default_Start_Sequence = b'\x0b'
Default_End_Sequence   = b'\x1c\x0d'
Default_Encoding       = 'utf-8'

# How often the kernel probes an idle connection, and how many unanswered probes end it.
Default_Keepalive_Idle          = 60
Default_Keepalive_Interval      = 10
Default_Keepalive_Probe_Count   = 6

# How the common name is written in a subject distinguished name.
_Common_Name_Attribute = 'CN'

# How many control ids one route's deduplication cache holds before the oldest are dropped.
Dedup_Max_Entries = Default_Max_Entries

# How many seconds each deduplication TTL unit stands for.
TTL_Multipliers = {
    'minutes': 60,
    'hours':   3600,
    'days':    86400,
}

# The listener is one per server rather than one per channel, so what it is comes from the server's
# own environment rather than from any channel's form. Each name maps to the attribute it sets and
# the function that reads its text.
Listener_Env_Names = {
    'Zato_HL7_MLLP_Max_Connections':     ('max_concurrent_connections', int),
    'Zato_HL7_MLLP_Accept_Backlog':      ('accept_backlog', int),
    'Zato_HL7_MLLP_Read_Buffer_Size':    ('read_buffer_size', int),
    'Zato_HL7_MLLP_Max_First_Line_Size': ('max_first_line_size', int),
    'Zato_HL7_MLLP_First_Line_Timeout':  ('first_line_timeout', float),
    'Zato_HL7_MLLP_Max_Msg_Size':        ('max_message_size', int),
    'Zato_HL7_MLLP_Idle_Timeout':        ('idle_timeout', float),
}

# ################################################################################################################################
# ################################################################################################################################

class ListenerConfig:
    """ What the one shared TCP listener is, as opposed to what any route through it is.
    Everything here is something a socket can only have one of.
    """

    def __init__(
        self,
        address:'str' = Default_Bind_Address,
        *,
        max_concurrent_connections:'int' = Default_Max_Concurrent_Connections,
        accept_backlog:'int' = Default_Accept_Backlog,
        read_buffer_size:'int' = Default_Read_Buffer_Size,
        max_first_line_size:'int' = Default_Max_First_Line_Size,
        first_line_timeout:'float' = Default_First_Line_Timeout,
        max_message_size:'int' = Default_Max_Message_Size,
        idle_timeout:'float' = Default_Idle_Timeout,
        ) -> 'None':

        self.address = address
        self.max_concurrent_connections = max_concurrent_connections
        self.accept_backlog = accept_backlog
        self.read_buffer_size = read_buffer_size

        # How much may be buffered, and how long may be spent, looking for the first CR of a message.
        # Until that line is in hand there is no route whose bounds could apply instead.
        self.max_first_line_size = max_first_line_size
        self.first_line_timeout = first_line_timeout

        # The ceiling no route may exceed, whatever its own limit says
        self.max_message_size = max_message_size

        # The ceiling no route's own idle deadline may exceed
        self.idle_timeout = idle_timeout

# ################################################################################################################################

    @staticmethod
    def from_env(address:'str', environ:'dict | None'=None) -> 'ListenerConfig':
        """ Builds the listener's configuration from the server's own environment, which is where
        a setting that belongs to one socket rather than to any channel comes from.
        """
        if environ is None:
            environ = dict(os.environ)

        out = ListenerConfig(address)

        for name, (attribute, parse) in Listener_Env_Names.items():

            raw_value = environ.get(name)

            # Each of these is genuinely optional and the default stands when it is not given
            if raw_value:
                setattr(out, attribute, parse(raw_value))

        return out

# ################################################################################################################################
# ################################################################################################################################

class RouteSettings:
    """ How one channel's messages are read and interpreted. Each is derived per message from the
    route the message's own MSH line matched, so two senders down one connection are read
    differently from one another.
    """

    def __init__(
        self,
        *,
        start_sequence:'bytes' = Default_Start_Sequence,
        end_sequence:'bytes' = Default_End_Sequence,
        recv_timeout:'float' = Default_Recv_Timeout,
        max_message_size:'int' = Default_Max_Message_Size,
        idle_timeout:'float' = Default_Idle_Timeout,
        keepalive_idle:'int' = Default_Keepalive_Idle,
        keepalive_interval:'int' = Default_Keepalive_Interval,
        keepalive_probe_count:'int' = Default_Keepalive_Probe_Count,
        default_character_encoding:'str' = Default_Encoding,
        should_use_msh18_encoding:'bool' = True,
        should_normalize_line_endings:'bool' = True,
        should_restore_truncated_msh:'bool' = True,
        should_split_concatenated_messages:'bool' = True,
        should_force_standard_delimiters:'bool' = True,
        should_parse_on_input:'bool' = True,
        should_validate:'bool' = False,
        should_log_messages:'bool' = False,
        should_return_errors:'bool' = False,
        tolerance_config:'ToleranceConfig | None' = None,
        dedup_ttl_value:'int' = 0,
        dedup_ttl_unit:'str' = '',
        security_common_name:'str' = '',
        allowed_networks:'str' = '',
        ) -> 'None':

        self.start_sequence = start_sequence
        self.end_sequence = end_sequence
        self.recv_timeout = recv_timeout
        self.max_message_size = max_message_size
        self.idle_timeout = idle_timeout

        self.keepalive_idle = keepalive_idle
        self.keepalive_interval = keepalive_interval
        self.keepalive_probe_count = keepalive_probe_count

        self.default_character_encoding = default_character_encoding
        self.should_use_msh18_encoding = should_use_msh18_encoding
        self.should_normalize_line_endings = should_normalize_line_endings
        self.should_restore_truncated_msh = should_restore_truncated_msh
        self.should_split_concatenated_messages = should_split_concatenated_messages
        self.should_force_standard_delimiters = should_force_standard_delimiters

        self.should_parse_on_input = should_parse_on_input
        self.should_validate = should_validate
        self.should_log_messages = should_log_messages
        self.should_return_errors = should_return_errors

        self.tolerance_config = tolerance_config

        # Each route counts duplicates on its own, so one channel's TTL never governs another's,
        # and each holds the same number of ids before the oldest of them are dropped
        if dedup_ttl_value and dedup_ttl_unit:
            ttl_seconds = dedup_ttl_value * TTL_Multipliers[dedup_ttl_unit]
            self.deduplicator:'MessageDeduplicator | None' = MessageDeduplicator(
                ttl_seconds, Dedup_Max_Entries)
        else:
            self.deduplicator = None

        # The common name a verified client certificate has to carry, empty when the channel
        # accepts a connection whatever certificate it was made with
        self.security_common_name = security_common_name

        # The networks a sender's address has to fall inside, empty when any address is allowed
        self.allowed_networks = parse_allowed_networks(allowed_networks)

# ################################################################################################################################

    def apply_listener_bounds(self, listener_config:'ListenerConfig') -> 'None':
        """ Narrows this route to the listener's own bounds. A route's values tune what the
        listener already allows, so one that would widen a bound is capped at that bound.
        """
        self.max_message_size = min(self.max_message_size, listener_config.max_message_size)
        self.idle_timeout = min(self.idle_timeout, listener_config.idle_timeout)

# ################################################################################################################################
# ################################################################################################################################

def describe_bounds_violations(
    max_message_size:'int',
    idle_timeout:'float',
    listener_config:'ListenerConfig | None'=None,
    ) -> 'strlist':
    """ Returns what a channel is asking for that the listener will not give it. A channel's
    values tune what the listener already allows, so saying where one exceeds a bound is better
    than storing a value that is silently capped later.
    """

    if listener_config is None:
        listener_config = ListenerConfig.from_env(Default_Bind_Address)

    out:'strlist' = []

    if max_message_size > listener_config.max_message_size:
        allowed = listener_config.max_message_size
        out.append(f'Maximum message size {max_message_size} is above the {allowed} bytes the listener allows')

    if idle_timeout > listener_config.idle_timeout:
        allowed = listener_config.idle_timeout
        out.append(f'Idle timeout {idle_timeout} is above the {allowed} seconds the listener allows')

    return out

# ################################################################################################################################
# ################################################################################################################################

def extract_common_name(subject_dn:'str') -> 'str':
    """ Takes the common name out of a subject distinguished name, which is where a certificate's
    identity is written as a whole. An empty string means the name carries no common name.
    """
    if not subject_dn:
        return ''

    # The components are comma-separated and may be given in either order and either case
    for component in subject_dn.split(','):

        name, separator, value = component.strip().partition('=')

        if separator and name.strip().upper() == _Common_Name_Attribute:
            out = value.strip()
            return out

    return ''

# ################################################################################################################################

def parse_allowed_networks(raw_value:'str') -> 'list':
    """ Turns a comma-separated list of addresses and CIDR blocks into networks to test against.
    """
    out = []

    for entry in raw_value.split(','):

        entry = entry.strip()

        if not entry:
            continue

        # A bare address is a network of one, which is what strict=False allows to be written
        out.append(ip_network(entry, strict=False))

    return out

# ################################################################################################################################

def is_address_allowed(client_ip:'str', allowed_networks:'list') -> 'bool':
    """ Returns whether an address falls inside any of the networks a channel accepts.
    An empty list means the channel does not restrict addresses at all.
    """
    if not allowed_networks:
        return True

    # An address that cannot be read is not one that can be matched against anything
    try:
        address = ip_address(client_ip)
    except ValueError:
        return False

    for network in allowed_networks:
        if address in network:
            return True

    return False

# ################################################################################################################################
# ################################################################################################################################
