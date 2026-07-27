# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Where a channel with a service fans out. It has to happen inside the service pipeline because
# this is the only place the overrides a service set through self.destination exist, and the only
# place the caller's reply can still be replaced by the answer of the destination the channel
# replies from. A channel with no service has no pipeline to be inside of and calls the
# coordinator on the message as it arrived, everything below being shared by the two.

# gevent
from gevent import sleep as gevent_sleep, spawn as gevent_spawn

# Zato
from zato.common.audit_log.api import AuditLog
from zato.common.destination.constants import Default_Delivery_Mode, Respond_From_Service
from zato.common.destination.coordinator import deliver, new_context, new_transports
from zato.common.destination.model import dump_entries, has_active_entries, parse_config, select_entries, \
    DestinationException
from zato.server.destination.dispatch import send as dispatch_send

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.destination.coordinator import DeliveryResult, DeliveryTransports
    from zato.common.destination.model import ChannelDestinationConfig, DestinationEntry
    from zato.common.destination.payload import PayloadOverrides
    from zato.common.typing_ import any_, stranydict, strlist
    from zato.server.destination.dispatch import DestinationConnections
    from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class ConnectionDispatcher:
    """ Delivers to a destination through the very connections a service reaches by itself.
    """
    connections: 'DestinationConnections'

    def __init__(self, connections:'DestinationConnections') -> 'None':
        self.connections = connections

# ################################################################################################################################

    def send(self, entry:'DestinationEntry', payload:'any_') -> 'any_':
        out = dispatch_send(self.connections, entry, payload)
        return out

# ################################################################################################################################
# ################################################################################################################################

def build_transports(connections:'DestinationConnections') -> 'DeliveryTransports':
    """ Builds the transports one channel's deliveries go out through - the connections given,
    and greenlets for everything the caller does not wait for.
    """
    dispatcher = ConnectionDispatcher(connections)

    out = new_transports(dispatcher.send, gevent_sleep, gevent_spawn)
    return out

# ################################################################################################################################

def get_config(channel_item:'stranydict') -> 'ChannelDestinationConfig | None':
    """ Returns what a channel says about its destinations, or nothing when it declares none
    or when every one it declares is paused.
    """

    # A channel that has never had a destination has nothing stored at all
    if not channel_item.get('destinations'):
        return None

    out = parse_config(
        channel_item['name'],
        channel_item['destinations'],
        channel_item.get('respond_from', Respond_From_Service),
        channel_item.get('delivery_mode', Default_Delivery_Mode),
    )

    if not has_active_entries(out):
        return None

    return out

# ################################################################################################################################

def narrow_to(channel_item:'stranydict', names:'strlist') -> 'stranydict':
    """ Returns the channel as it looks to one message that is to reach only the destinations named,
    which is what sending an already-received message to some of them rather than to all of them
    runs on. The channel itself is left exactly as it stands - this is about one message and not
    about what the channel does with the next one.
    """
    config = get_config(channel_item)

    if not config:
        raise DestinationException(f'Channel `{channel_item["name"]}` has no destination a message reaches')

    selected = select_entries(config, names)

    # Naming destinations the channel does not have is a mistake worth hearing about rather than
    # a message quietly going nowhere
    if not selected.entries:
        raise DestinationException(f'Channel `{channel_item["name"]}` has no destination among `{names}`')

    out = dict(channel_item)

    out['destinations'] = dump_entries(selected.entries)
    out['respond_from'] = selected.respond_from

    return out

# ################################################################################################################################

def run_destinations(
    config:'ChannelDestinationConfig',
    overrides:'PayloadOverrides',
    request_payload:'any_',
    transports:'DeliveryTransports',
    *,
    cid:'str',
    server_name:'str',
    ) -> 'DeliveryResult':
    """ Delivers one message to every destination of one channel.
    """
    audit_log = AuditLog(server_name)

    context = new_context(config.channel_name, cid, transports, audit_log)

    out = deliver(context, config, overrides, request_payload)
    return out

# ################################################################################################################################

def run_for_service(service:'Service', channel_item:'stranydict') -> 'DeliveryResult | None':
    """ Delivers what a service handled to the destinations its channel declares, taking into
    account everything the service said through self.destination. Returns nothing when the
    channel has no destinations, which is every channel that does not use the feature.
    """
    config = get_config(channel_item)

    if not config:
        return None

    overrides = service.destination.get_overrides()
    transports = build_transports(service)

    out = run_destinations(
        config, overrides, service.request.raw, transports,
        cid=service.cid, server_name=service.server.name)

    return out

# ################################################################################################################################
# ################################################################################################################################
