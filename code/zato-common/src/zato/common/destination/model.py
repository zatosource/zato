# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A channel's destination list - where each message it accepts is delivered to once the
# channel is done with it. One destination is one outgoing connection plus the options that
# connection needs, a channel says which of them produces the caller's reply and in what
# order the rest receive their message, and everything here is parsed out of the three
# configuration values a channel stores.

from __future__ import annotations

# stdlib
from dataclasses import dataclass
from json import dumps, loads

# Zato
from zato.common.destination.constants import Active_Delivery_Modes, Default_Delivery_Mode, Default_Is_Active, \
    Known_Destination_Types, Respond_From_Service
from zato.common.typing_ import dict_field, list_field

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strlist
    anylist = anylist
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
destination_entry_list = list['DestinationEntry']

# ################################################################################################################################
# ################################################################################################################################

class DestinationException(Exception):
    """ Raised when a channel's destination configuration cannot be used as it stands.
    """

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DestinationEntry:
    """ One destination of one channel - the connection a message is delivered through
    and everything that delivery needs beyond the message itself.
    """

    # How the destination is addressed - what a service naming one destination names.
    name: str = ''

    # The kind of connection the delivery goes through - one of DestinationType.
    type: str = ''

    # The outgoing connection resolved at the moment of each send.
    connection: str = ''

    # A destination that is not active stays declared and receives nothing.
    is_active: bool = Default_Is_Active

    # What the destination's own type needs - a method, a path, a recipient, a subject line.
    options: 'stranydict' = dict_field()

# ################################################################################################################################

@dataclass(init=False)
class ChannelDestinationConfig:
    """ Everything one channel declares about its destinations.
    """

    # The channel the destinations belong to.
    channel_name: str = ''

    # The destinations, in the order they were declared in.
    entries: 'destination_entry_list' = list_field()

    # Which of them produces the caller's reply - either Respond_From_Service
    # or the name of one destination.
    respond_from: str = Respond_From_Service

    # How the destinations that do not produce the reply receive their message.
    delivery_mode: str = Default_Delivery_Mode

# ################################################################################################################################
# ################################################################################################################################

def new_entry(
    name:'str',
    destination_type:'str',
    connection:'str',
    *,
    is_active:'bool' = Default_Is_Active,
    options:'stranydict | None' = None,
    ) -> 'DestinationEntry':
    """ Builds one destination.
    """
    if options is None:
        options = {}

    # Our response to produce
    out = DestinationEntry()

    out.name = name
    out.type = destination_type
    out.connection = connection
    out.is_active = is_active
    out.options = options

    return out

# ################################################################################################################################

def parse_entry(entry_data:'stranydict') -> 'DestinationEntry':
    """ Builds one destination out of its stored form - the object the channel's
    destination list holds one of per destination.
    """
    if 'connection' not in entry_data:
        raise DestinationException('Destination has no connection to deliver through')

    connection = entry_data['connection']

    if 'type' not in entry_data:
        raise DestinationException(f'Destination `{connection}` has no type')

    destination_type = entry_data['type']

    if destination_type not in Known_Destination_Types:
        raise DestinationException(f'Destination `{connection}` is of unknown type `{destination_type}`')

    # A destination is addressed by a name of its own, defaulting to the connection it delivers through.
    name = entry_data.get('name', connection)

    out = new_entry(
        name,
        destination_type,
        connection,
        is_active=entry_data.get('is_active', Default_Is_Active),
        options=entry_data.get('options', {}),
    )

    return out

# ################################################################################################################################

def parse_entries(destinations:'any_') -> 'destination_entry_list':
    """ Builds the destination list out of what a channel stores it as - the JSON text the
    Dashboard writes, or the list enmasse hands over already parsed. Either way, a channel
    with no destinations produces an empty list.
    """

    # A channel with no destinations stores the empty string ..
    if not destinations:
        return []

    # .. the Dashboard stores its list as JSON text ..
    if isinstance(destinations, str):
        try:
            destinations = loads(destinations)
        except ValueError:
            raise DestinationException('Destination list is not valid JSON')

    # .. and whatever the source, what arrives here has to be a list of destinations.
    if not isinstance(destinations, list):
        raise DestinationException('Destination list is not a list')

    out:'destination_entry_list' = []

    for entry_data in destinations:
        entry = parse_entry(entry_data)
        out.append(entry)

    return out

# ################################################################################################################################

def parse_config(
    channel_name:'str',
    destinations:'any_',
    respond_from:'str' = Respond_From_Service,
    delivery_mode:'str' = Default_Delivery_Mode,
    ) -> 'ChannelDestinationConfig':
    """ Builds one channel's destination configuration out of the three values it stores,
    refusing a configuration that names a reply nobody produces or a delivery mode
    that does not exist.
    """
    entries = parse_entries(destinations)

    # An unset respond-from means the service answers the caller ..
    if not respond_from:
        respond_from = Respond_From_Service

    # .. and so does an unset delivery mode mean the default one.
    if not delivery_mode:
        delivery_mode = Default_Delivery_Mode

    if delivery_mode not in Active_Delivery_Modes:
        raise DestinationException(
            f'Channel `{channel_name}` cannot deliver in mode `{delivery_mode}`')

    # Our response to produce
    out = ChannelDestinationConfig()

    out.channel_name = channel_name
    out.entries = entries
    out.respond_from = respond_from
    out.delivery_mode = delivery_mode

    if respond_from != Respond_From_Service:
        if not get_entry(out, respond_from):
            raise DestinationException(
                f'Channel `{channel_name}` replies from `{respond_from}` which is not one of its destinations')

    return out

# ################################################################################################################################

def to_stored_data(entry:'DestinationEntry') -> 'stranydict':
    """ Returns one destination the way it is stored - the object the Dashboard writes and reads
    back, its options always there even when the destination has none of them.
    """
    out = {
        'name': entry.name,
        'type': entry.type,
        'connection': entry.connection,
        'is_active': entry.is_active,
        'options': entry.options,
    }

    return out

# ################################################################################################################################

def dump_entries(entries:'destination_entry_list') -> 'str':
    """ Returns a destination list in the form a channel stores it - the JSON text the Dashboard
    writes, which is what everything reading a channel's destinations back expects to find.
    """
    stored = []

    for entry in entries:
        stored.append(to_stored_data(entry))

    out = dumps(stored)
    return out

# ################################################################################################################################

def describe_entries(entries:'destination_entry_list') -> 'anylist':
    """ Returns a destination list in the plainest form it can be written by hand in, which is
    how enmasse holds it - a destination with no options of its own carries no options key,
    there being nothing for a hand-written file to say about them.
    """
    out:'anylist' = []

    for entry in entries:
        described = to_stored_data(entry)

        if not entry.options:
            del described['options']

        out.append(described)

    return out

# ################################################################################################################################

def count_entries(destinations:'any_') -> 'int':
    """ Returns how many destinations a channel declares, the way a list page counts them -
    a channel whose stored list cannot be read counts as declaring none rather than
    taking the page it is listed on down with it.
    """
    try:
        entries = parse_entries(destinations)
    except DestinationException:
        out = 0
    else:
        out = len(entries)

    return out

# ################################################################################################################################

def select_entries(config:'ChannelDestinationConfig', names:'strlist') -> 'ChannelDestinationConfig':
    """ Returns the same configuration narrowed to the destinations named, which is what
    delivering one message to some of a channel's destinations rather than to all of them
    runs on. A reply that was to come from a destination left out comes from the service
    instead, that destination not receiving this message at all.
    """

    # Our response to produce
    out = ChannelDestinationConfig()

    out.channel_name = config.channel_name
    out.entries = []
    out.delivery_mode = config.delivery_mode

    for entry in config.entries:
        if entry.name in names:
            out.entries.append(entry)

    if get_entry(out, config.respond_from):
        out.respond_from = config.respond_from
    else:
        out.respond_from = Respond_From_Service

    return out

# ################################################################################################################################

def get_entry(config:'ChannelDestinationConfig', name:'str') -> 'DestinationEntry | None':
    """ Returns the destination of that name, or nothing when the channel has no such destination.
    """
    for entry in config.entries:
        if entry.name == name:
            out = entry
            break
    else:
        out = None

    return out

# ################################################################################################################################

def get_option(entry:'DestinationEntry', name:'str', default:'any_') -> 'any_':
    """ Returns one of a destination's options, or the default in force for that
    option when the destination does not carry it.
    """
    out = entry.options.get(name, default)
    return out

# ################################################################################################################################

def has_active_entries(config:'ChannelDestinationConfig') -> 'bool':
    """ Tells whether the channel has any destination that a message actually reaches.
    """
    for entry in config.entries:
        if entry.is_active:
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################
# ################################################################################################################################
