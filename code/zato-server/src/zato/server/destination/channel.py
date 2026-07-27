# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Where a channel with no service of its own fans out. There is no service pipeline to be inside
# of here, so the channel delivers the message as it arrived and nothing interprets its content -
# the destinations are reached through the same connections and recorded on the same rows as they
# are for a channel that does have a service, the overrides a service would have set being the
# only thing missing.

# Zato
from zato.common.destination.payload import new_overrides
from zato.common.util.api import new_cid_server
from zato.server.connection.email import EMailAPI
from zato.server.connection.facade import FHIRFacade, MLLPFacade, RESTFacade
from zato.server.destination.hook import build_transports, get_config, run_destinations

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.destination.coordinator import DeliveryResult
    from zato.common.typing_ import any_, stranydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class ChannelConnections:
    """ The outgoing connections a channel delivers through when it has no service to reach them
    for it. Each facade holds the live configuration the config manager keeps up to date, so a
    connection is resolved at the moment of each send rather than held on to here.
    """

    rest:  'RESTFacade'
    mllp:  'MLLPFacade'
    fhir:  'FHIRFacade'
    email: 'EMailAPI | None'

# ################################################################################################################################

    def init(self, server:'ParallelServer', cid:'str') -> 'None':

        config_manager = server.config_manager

        self.rest = RESTFacade()
        self.rest.init(cid, config_manager.config_store.out_plain_http)

        self.mllp = MLLPFacade()
        self.mllp.init(config_manager)

        self.fhir = FHIRFacade()
        self.fhir.init(config_manager)

        # E-mail is a component a server may run without, and a destination that needs one
        # is told so rather than the whole fan-out failing to be built
        if server.fs_server_config.component_enabled.email:
            self.email = EMailAPI(config_manager.email_smtp_api, config_manager.email_imap_api)
        else:
            self.email = None

# ################################################################################################################################
# ################################################################################################################################

def new_channel_item(config:'any_') -> 'stranydict':
    """ What one channel says about itself to everything that runs on its behalf - its own identity
    plus everything it declares about its destinations, which is what the fan-out at the end of a
    service's pipeline reads and what a channel with no service delivers by. A message arriving live
    and one sent again from the audit log both fan out by this, so the two go to the same places.
    """
    out = {
        'id': config.id,
        'name': config.name,
        'is_internal': config.is_internal,
        'data_format': config.data_format,
        'destinations': config.destinations,
        'respond_from': config.respond_from,
        'delivery_mode': config.delivery_mode,
    }

    return out

# ################################################################################################################################

def run_for_channel(
    server:'ParallelServer',
    channel_item:'stranydict',
    request_payload:'any_',
    *,
    cid:'str' = '',
    ) -> 'DeliveryResult | None':
    """ Delivers one message a channel accepted to the destinations that channel declares, with
    no service between the two. Returns nothing when the channel has no destination a message
    actually reaches.
    """
    config = get_config(channel_item)

    if not config:
        return None

    # Every delivery is recorded under the correlation id the message arrived under, so the trail
    # of that one message shows everything it fanned out to. A channel that is not audited has no
    # receipt to share an id with, so the deliveries are recorded under one of their own.
    if not cid:
        cid = new_cid_server()

    connections = ChannelConnections()
    connections.init(server, cid)

    # Nothing said anything about what any one destination is to receive, so all of them
    # receive the message as it arrived
    overrides = new_overrides()

    transports = build_transports(connections)

    out = run_destinations(
        config, overrides, request_payload, transports,
        cid=cid, server_name=server.name)

    return out

# ################################################################################################################################
# ################################################################################################################################
