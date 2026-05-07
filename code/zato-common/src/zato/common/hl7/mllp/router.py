# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from logging import getLogger
from threading import Lock

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# MSH field positions (0-based indexing within pipe-delimited MSH fields).
# MSH-1 is the field separator itself (|), MSH-2 is the encoding characters,
# so MSH-3 starts at index 2 in the split result.
_MSH3_Index  = 2
_MSH4_Index  = 3
_MSH5_Index  = 4
_MSH6_Index  = 5
_MSH9_Index  = 8
_MSH11_Index = 10
_MSH12_Index = 11

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ChannelRoute:
    """ A single routing rule mapping MSH field criteria to a service callback.
    """

    channel_name:'str'
    service_name:'str'
    callback:'callable_'

    # Match criteria - empty string means "match any"
    msh3_sending_application:'str'
    msh4_sending_facility:'str'
    msh5_receiving_application:'str'
    msh6_receiving_facility:'str'
    msh9_message_type:'str'
    msh9_trigger_event:'str'
    msh11_processing_id:'str'
    msh12_version_id:'str'

    # When True, this route is evaluated last and handles all unmatched messages
    is_default:'bool'

# ################################################################################################################################
# ################################################################################################################################

channel_route_list = list[ChannelRoute]

# ################################################################################################################################
# ################################################################################################################################

def _extract_msh_field(msh_fields:'list[str]', field_index:'int') -> 'str':
    """ Extracts a single MSH field value by index, returning an empty string if the field is not present.
    """

    if field_index < len(msh_fields):
        out = msh_fields[field_index]
        return out

    return ''

# ################################################################################################################################

def parse_msh_fields(msh_line:'str') -> 'dict[str, str]':
    """ Parses an MSH line into a dictionary of field values keyed by their standard names.
    MSH-9 is split on the ^ component separator into message type (9.1) and trigger event (9.2).
    """

    # Split the MSH line by the field separator (first character after "MSH") ..
    if len(msh_line) < 4:
        out:'dict[str, str]' = {}
        return out

    field_separator = msh_line[3]
    msh_fields = msh_line.split(field_separator)

    # MSH-9 contains components separated by ^ (e.g. "ADT^A01^ADT_A01") ..
    msh9_raw = _extract_msh_field(msh_fields, _MSH9_Index)
    msh9_components = msh9_raw.split('^')

    msh9_message_type = msh9_components[0] if len(msh9_components) > 0 else ''
    msh9_trigger_event = msh9_components[1] if len(msh9_components) > 1 else ''

    out = {
        'msh3':             _extract_msh_field(msh_fields, _MSH3_Index),
        'msh4':             _extract_msh_field(msh_fields, _MSH4_Index),
        'msh5':             _extract_msh_field(msh_fields, _MSH5_Index),
        'msh6':             _extract_msh_field(msh_fields, _MSH6_Index),
        'msh9_type':        msh9_message_type,
        'msh9_trigger':     msh9_trigger_event,
        'msh11':            _extract_msh_field(msh_fields, _MSH11_Index),
        'msh12':            _extract_msh_field(msh_fields, _MSH12_Index),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class HL7MessageRouter:
    """ Routes incoming HL7 messages to the appropriate service callback based on MSH field matching.
    Thread-safe - routes can be added and removed while messages are being processed.
    """

    def __init__(self) -> 'None':
        self._routes:'channel_route_list' = []
        self._lock = Lock()

# ################################################################################################################################

    def add_route(
        self,
        channel_name:'str',
        service_name:'str',
        callback:'callable_',
        *,
        msh3_sending_application:'str' = '',
        msh4_sending_facility:'str' = '',
        msh5_receiving_application:'str' = '',
        msh6_receiving_facility:'str' = '',
        msh9_message_type:'str' = '',
        msh9_trigger_event:'str' = '',
        msh11_processing_id:'str' = '',
        msh12_version_id:'str' = '',
        is_default:'bool' = False,
        ) -> 'None':
        """ Registers a new routing rule. All match fields are optional - empty string means match any.
        Only one route can be the default at a time - setting a new default clears the previous one.
        """

        # If this route is marked as default, clear the flag from any existing default ..
        if is_default:
            with self._lock:
                for existing_route in self._routes:
                    if existing_route.is_default:
                        existing_route.is_default = False
                        logger.info('Cleared default flag from channel `%s`', existing_route.channel_name)

        route = ChannelRoute()
        route.channel_name = channel_name
        route.service_name = service_name
        route.callback     = callback

        route.msh3_sending_application  = msh3_sending_application
        route.msh4_sending_facility     = msh4_sending_facility
        route.msh5_receiving_application = msh5_receiving_application
        route.msh6_receiving_facility   = msh6_receiving_facility
        route.msh9_message_type         = msh9_message_type
        route.msh9_trigger_event        = msh9_trigger_event
        route.msh11_processing_id       = msh11_processing_id
        route.msh12_version_id          = msh12_version_id
        route.is_default                = is_default

        with self._lock:
            self._routes.append(route)

        logger.info('Added MLLP route for channel `%s` -> service `%s` (default: %s)', channel_name, service_name, is_default)

# ################################################################################################################################

    def remove_route(self, channel_name:'str') -> 'None':
        """ Removes the routing rule for the given channel name.
        """

        with self._lock:

            updated_routes:'channel_route_list' = []

            for route in self._routes:
                if route.channel_name != channel_name:
                    updated_routes.append(route)

            self._routes = updated_routes

        logger.info('Removed MLLP route for channel `%s`', channel_name)

# ################################################################################################################################

    def has_routes(self) -> 'bool':
        """ Returns True if there are any registered routing rules.
        """
        with self._lock:

            out = len(self._routes) > 0
            return out

# ################################################################################################################################

    def match(self, msh_line:'str') -> 'ChannelRoute | None':
        """ Finds the first routing rule that matches the given MSH line.
        Non-default routes are evaluated first (first match wins),
        then the default route is tried if no regular route matched.
        Returns None if no route matches at all.
        """

        # Parse the MSH fields from the line ..
        parsed_fields = parse_msh_fields(msh_line)

        if not parsed_fields:
            return None

        with self._lock:

            default_route:'ChannelRoute | None' = None

            # Walk non-default routes first ..
            for route in self._routes:

                if route.is_default:
                    default_route = route
                    continue

                if self._route_matches(route, parsed_fields):

                    out = route
                    return out

            # .. no regular route matched, try the default.
            if default_route:

                out = default_route
                return out

        return None

# ################################################################################################################################

    def _route_matches(self, route:'ChannelRoute', parsed_fields:'dict[str, str]') -> 'bool':
        """ Checks whether a single route matches the parsed MSH fields.
        A route matches when every non-empty criterion equals the corresponding field value.
        All comparisons are case-insensitive.
        """

        # Check each criterion - skip empty ones (they mean "match any") ..
        if route.msh3_sending_application:
            if route.msh3_sending_application.lower() != parsed_fields['msh3'].lower():
                return False

        if route.msh4_sending_facility:
            if route.msh4_sending_facility.lower() != parsed_fields['msh4'].lower():
                return False

        if route.msh5_receiving_application:
            if route.msh5_receiving_application.lower() != parsed_fields['msh5'].lower():
                return False

        if route.msh6_receiving_facility:
            if route.msh6_receiving_facility.lower() != parsed_fields['msh6'].lower():
                return False

        if route.msh9_message_type:
            if route.msh9_message_type.lower() != parsed_fields['msh9_type'].lower():
                return False

        if route.msh9_trigger_event:
            if route.msh9_trigger_event.lower() != parsed_fields['msh9_trigger'].lower():
                return False

        if route.msh11_processing_id:
            if route.msh11_processing_id.lower() != parsed_fields['msh11'].lower():
                return False

        if route.msh12_version_id:
            if route.msh12_version_id.lower() != parsed_fields['msh12'].lower():
                return False

        return True

# ################################################################################################################################
# ################################################################################################################################
