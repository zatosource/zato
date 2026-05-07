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
_MSH3_Index = 2
_MSH4_Index = 3
_MSH5_Index = 4
_MSH6_Index = 5
_MSH9_Index = 8

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
    """

    # Split the MSH line by the field separator (first character after "MSH") ..
    if len(msh_line) < 4:
        out:'dict[str, str]' = {}
        return out

    field_separator = msh_line[3]
    msh_fields = msh_line.split(field_separator)

    out = {
        'msh3': _extract_msh_field(msh_fields, _MSH3_Index),
        'msh4': _extract_msh_field(msh_fields, _MSH4_Index),
        'msh5': _extract_msh_field(msh_fields, _MSH5_Index),
        'msh6': _extract_msh_field(msh_fields, _MSH6_Index),
        'msh9': _extract_msh_field(msh_fields, _MSH9_Index),
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
        ) -> 'None':
        """ Registers a new routing rule. All match fields are optional - empty string means match any.
        """

        route = ChannelRoute()
        route.channel_name = channel_name
        route.service_name = service_name
        route.callback     = callback

        route.msh3_sending_application  = msh3_sending_application
        route.msh4_sending_facility     = msh4_sending_facility
        route.msh5_receiving_application = msh5_receiving_application
        route.msh6_receiving_facility   = msh6_receiving_facility
        route.msh9_message_type         = msh9_message_type

        with self._lock:
            self._routes.append(route)

        logger.info('Added MLLP route for channel `%s` -> service `%s`', channel_name, service_name)

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
        Returns None if no route matches.
        """

        # Parse the MSH fields from the line ..
        parsed_fields = parse_msh_fields(msh_line)

        if not parsed_fields:
            return None

        # .. walk through routes under the lock and find the first match ..
        with self._lock:

            for route in self._routes:

                if self._route_matches(route, parsed_fields):

                    out = route
                    return out

        return None

# ################################################################################################################################

    def _route_matches(self, route:'ChannelRoute', parsed_fields:'dict[str, str]') -> 'bool':
        """ Checks whether a single route matches the parsed MSH fields.
        A route matches when every non-empty criterion equals the corresponding field value.
        """

        # Check each criterion - skip empty ones (they mean "match any") ..
        if route.msh3_sending_application:
            if route.msh3_sending_application != parsed_fields['msh3']:
                return False

        if route.msh4_sending_facility:
            if route.msh4_sending_facility != parsed_fields['msh4']:
                return False

        if route.msh5_receiving_application:
            if route.msh5_receiving_application != parsed_fields['msh5']:
                return False

        if route.msh6_receiving_facility:
            if route.msh6_receiving_facility != parsed_fields['msh6']:
                return False

        if route.msh9_message_type:
            if route.msh9_message_type != parsed_fields['msh9']:
                return False

        return True

# ################################################################################################################################
# ################################################################################################################################
