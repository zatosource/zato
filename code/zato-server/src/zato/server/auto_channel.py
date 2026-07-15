# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from contextlib import closing

# Zato
from zato.common.api import CONNECTION, DATA_FORMAT, HTTP_SOAP, MISC, PARAMS_PRIORITY, URL_PARAMS_PRIORITY, URL_TYPE
from zato.common.broker_message import CHANNEL
from zato.common.json_internal import dumps
from zato.common.odb.model import HTTPSOAP, Service
from zato.common.typing_ import cast_
from zato.common.util.auto_channel import get_auto_channel_config, get_auto_channel_url_path, is_channel_active, \
    should_create_channel
from zato.server.openapi_console.cache import suppressed_rebuilds

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictlist, strlist
    from zato.common.util.auto_channel import AutoChannelConfig
    from zato.server.base.parallel import ParallelServer
    AutoChannelConfig = AutoChannelConfig
    ParallelServer = ParallelServer
    any_ = any_
    dictlist = dictlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def create_auto_channels(server:'ParallelServer', service_names:'strlist', session:'any_'=None) -> 'None':
    """ Creates REST channels for the given services per the Zato_Auto_REST_Channel_* environment variables.
    Everything is processed as one batch - one SELECT loads the existing channels, the missing ones
    are computed in memory as a set difference and one bulk INSERT creates them all, so the cost
    never grows into one SQL request per service or per channel.
    """
    config = get_auto_channel_config()

    # The feature is off or nothing is included - the common case, and it costs no SQL at all
    if not config.is_enabled:
        return

    if not config.include:
        return

    # A channel is named after its service, so a set keeps the candidates unique
    candidates = sorted(name for name in set(service_names) if should_create_channel(name, config))

    if not candidates:
        return

    # A session given by the caller belongs to a bigger transaction, such as a hot-deployment,
    # and its owner commits it - a session of our own, as in the startup pass, is committed here.
    if session is not None:
        created = _create_missing_channels(session, server.cluster_id, candidates, config)
    else:
        with closing(server.odb.session()) as own_session:
            created = _create_missing_channels(own_session, server.cluster_id, candidates, config)
            if created:
                own_session.commit()

    if not created:
        return

    # One event per channel keeps url_data and the rest of the runtime updated through the normal
    # handlers - only the per-event OpenAPI rebuilds are suppressed because the document is rebuilt
    # exactly once after the whole batch, by our caller.
    with suppressed_rebuilds():
        for item in created:
            _publish_create_event(server, item)

    created_count = len(created)
    suffix = 'channel' if created_count == 1 else 'channels'
    logger.info('Auto-created %d REST %s -> %s', created_count, suffix, sorted(item['name'] for item in created))

# ################################################################################################################################

def _create_missing_channels(
    session,    # type: any_
    cluster_id, # type: int
    candidates, # type: strlist
    config      # type: AutoChannelConfig
) -> 'dictlist':
    """ Creates the channels that do not exist yet and returns them, IDs included, for the caller
    to publish configuration events about. One SELECT, an in-memory set difference, one bulk INSERT.
    """
    # One SELECT loads the names of all the existing channels for the set difference
    rows = session.query(HTTPSOAP.name).\
        filter(HTTPSOAP.cluster_id==cluster_id).\
        filter(HTTPSOAP.connection==CONNECTION.CHANNEL).\
        all()

    existing_names = {row.name for row in rows}

    # The set difference - a channel named after its service already exists, whether auto-created
    # earlier or hand-made, and this is how a hand-made one takes precedence.
    missing = [name for name in candidates if name not in existing_names]

    if not missing:
        return []

    to_create = []

    for name in missing:
        url_path = get_auto_channel_url_path(name, config)
        to_create.append({'name':name, 'url_path':url_path})

    # One query resolves all the target services to their IDs
    service_name_column = cast_('any_', Service.name)

    service_rows = session.query(Service.id, Service.name).\
        filter(Service.cluster_id==cluster_id).\
        filter(service_name_column.in_([item['name'] for item in to_create])).\
        all()

    service_id_by_name = {row.name: row.id for row in service_rows}

    # The marker records that the channel is auto-created, and the Accept header matches
    # what the Dashboard stores for hand-made REST channels.
    opaque = dumps({
        'is_auto_created': True,
        'http_accept': HTTP_SOAP.ACCEPT.ANY,
        'match_slash': True,
        'data_encoding': 'utf-8',
    })

    # Column defaults such as merge_url_params_req, url_params_pri, params_pri, serialization_type
    # and timeout are never re-stated here - the INSERT omits them and the model's own defaults apply.
    mappings = []

    for item in to_create:
        name = item['name']
        mappings.append({
            'name': name,
            'is_active': is_channel_active(name, config),
            'is_internal': False,
            'connection': CONNECTION.CHANNEL,
            'transport': URL_TYPE.PLAIN_HTTP,
            'url_path': item['url_path'],
            'method': MISC.DEFAULT_HTTP_METHOD,
            'soap_action': '',
            'data_format': DATA_FORMAT.JSON,
            'service_id': service_id_by_name[name],
            'cluster_id': cluster_id,
            'opaque1': opaque,
        })

    # One bulk INSERT creates all the missing channels
    _ = session.execute(HTTPSOAP.__table__.insert(), mappings)

    # One SELECT gives the new rows their IDs for the configuration events
    created_names = [item['name'] for item in mappings]
    channel_name_column = cast_('any_', HTTPSOAP.name)

    id_rows = session.query(HTTPSOAP.id, HTTPSOAP.name, HTTPSOAP.url_path, HTTPSOAP.is_active, HTTPSOAP.service_id).\
        filter(HTTPSOAP.cluster_id==cluster_id).\
        filter(HTTPSOAP.connection==CONNECTION.CHANNEL).\
        filter(HTTPSOAP.transport==URL_TYPE.PLAIN_HTTP).\
        filter(channel_name_column.in_(created_names)).\
        all()

    out = []

    for row in id_rows:
        out.append({
            'id': row.id,
            'name': row.name,
            'url_path': row.url_path,
            'is_active': row.is_active,
            'service_id': row.service_id,
        })

    return out

# ################################################################################################################################

def _publish_create_event(server:'ParallelServer', item:'any_') -> 'None':
    """ Publishes one CHANNEL_HTTP_SOAP_CREATE_EDIT event of the same shape the create service
    publishes, so url_data and the other handlers pick the new channel up the normal way.
    """
    name = item['name']

    msg = {
        'action': CHANNEL.HTTP_SOAP_CREATE_EDIT.value,
        'id': item['id'],
        'name': name,
        'is_active': item['is_active'],
        'is_internal': False,
        'connection': CONNECTION.CHANNEL,
        'transport': URL_TYPE.PLAIN_HTTP,
        'url_path': item['url_path'],
        'method': MISC.DEFAULT_HTTP_METHOD,
        'http_accept': HTTP_SOAP.ACCEPT.ANY,
        'soap_action': '',
        'data_format': DATA_FORMAT.JSON,
        'data_encoding': 'utf-8',
        'match_slash': True,
        'merge_url_params_req': True,
        'url_params_pri': URL_PARAMS_PRIORITY.DEFAULT,
        'params_pri': PARAMS_PRIORITY.DEFAULT,
        'service_id': item['service_id'],
        'service_name': name,
        'impl_name': server.service_store.name_to_impl_name[name],
        'security_id': None,
        'should_include_in_openapi': True,
        'is_auto_created': True,
    }

    server.config_dispatcher.publish(msg)

# ################################################################################################################################
# ################################################################################################################################
