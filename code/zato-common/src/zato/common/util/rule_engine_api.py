# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from contextlib import closing

# Zato
from zato.common.api import CONNECTION, DATA_FORMAT, URL_TYPE
from zato.common.util.gateway import _resolve_security_group_names_to_ids

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anylist, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The one service every Rule engine API object routes to.
rule_engine_api_service_name = 'zato.rule-engine.api.invoke'

# The implementation path of that service, needed when its database row has to be created
# before the server deployed it, e.g. during an enmasse import against a fresh database.
rule_engine_api_service_impl_name = 'zato.server.service.internal.rule_engine.api.RuleEngineAPIInvoke'

# What the object's base path is extended with - the one path parameter that names the ruleset to invoke,
# with slashes allowed inside so `/versions/{number}` can pin a version.
rule_engine_api_channel_suffix = '/{ruleset}'

# The base path used when an object does not configure one.
default_rule_engine_api_url_path = '/api/rules'

# ################################################################################################################################
# ################################################################################################################################

def get_rule_engine_api_channel_url_path(url_path:'str') -> 'str':
    """ Returns the full channel URL path for one Rule engine API object's base path.
    """
    out = url_path.rstrip('/') + rule_engine_api_channel_suffix
    return out

# ################################################################################################################################

def ensure_rule_engine_api_channel(
    session:'SASession',
    channel_name:'str',
    url_path:'str',
    cluster_id:'int',
    is_active:'bool' = True,
    security_groups:'anylist | None' = None,
    old_name:'strnone' = None,
    ) -> 'None':
    """ Creates or updates the REST channel that makes a Rule engine API object reachable over HTTP.
    Called from the enmasse importer, which works on the database directly.
    Does NOT commit - the caller is responsible for committing the session.
    """
    from zato.common.odb.model import Cluster, HTTPSOAP, Service
    from zato.common.util.sql import set_instance_opaque_attrs

    if security_groups is None:
        security_groups = []

    channel_url_path = get_rule_engine_api_channel_url_path(url_path)

    # The channel is never part of the generated API documentation - the per-ruleset paths
    # documented for this object come from the rule engine itself, not from this channel's I/O.
    opaque_attrs = {
        'security_groups': security_groups,
        'should_include_in_openapi': False,
        'match_slash': True,
    }

    # If this is a rename, delete the old REST channel first ..
    if old_name and old_name != channel_name:
        old_http = session.query(HTTPSOAP).filter(
            HTTPSOAP.name == old_name,
            HTTPSOAP.cluster_id == cluster_id,
            HTTPSOAP.connection == CONNECTION.CHANNEL,
        ).first()
        if old_http:
            session.delete(old_http)

    # .. check if the REST channel already exists ..
    existing_http = session.query(HTTPSOAP).filter(
        HTTPSOAP.name == channel_name,
        HTTPSOAP.cluster_id == cluster_id,
        HTTPSOAP.connection == CONNECTION.CHANNEL,
    ).first()

    # .. if it exists, update it ..
    if existing_http:
        existing_http.url_path = channel_url_path
        existing_http.is_active = is_active
        set_instance_opaque_attrs(existing_http, opaque_attrs)

    # .. otherwise, create a new one.
    else:
        cluster = session.query(Cluster).filter(Cluster.id == cluster_id).one()

        target_service = session.query(Service).filter(
            Service.name == rule_engine_api_service_name,
            Service.cluster_id == cluster_id,
        ).first()

        # The service row matches what the server itself creates when it deploys the service,
        # so an import against a fresh database and a later server startup converge on one row.
        if not target_service:
            target_service = Service(
                None, rule_engine_api_service_name, True, rule_engine_api_service_impl_name, True, cluster)
            session.add(target_service)
            session.flush()

        http_channel = HTTPSOAP(
            None, channel_name, is_active, True, CONNECTION.CHANNEL,
            URL_TYPE.PLAIN_HTTP, None, channel_url_path, None, '', None, DATA_FORMAT.JSON,
            service=target_service, cluster=cluster, security=None)
        set_instance_opaque_attrs(http_channel, opaque_attrs)
        session.add(http_channel)

# ################################################################################################################################

def on_rule_engine_api_create_edit(service:'any_', data:'stranydict', model:'any_', old_name:'strnone') -> 'None':
    """ Hook called by zato.generic.connection create/edit for the gateway-rule-engine type.
    Creates or updates the HTTPSOAP channel by invoking the standard http-soap services,
    which handle ODB persistence, uniqueness checks, and broker notification.
    """
    from zato.common.odb.model import HTTPSOAP

    object_name = data['name']
    url_path = data.get('url_path') or default_rule_engine_api_url_path
    is_active = data.get('is_active', True)
    cluster_id = model.cluster_id

    channel_url_path = get_rule_engine_api_channel_url_path(url_path)

    with closing(service.server.odb.session()) as session:

        security_groups = data.get('security_groups', [])
        security_groups = _resolve_security_group_names_to_ids(session, security_groups, cluster_id)

        # Check if the HTTPSOAP channel already exists (use old_name for renames) ..
        lookup_name = old_name if (old_name and old_name != object_name) else object_name
        existing = session.query(HTTPSOAP).filter(
            HTTPSOAP.name == lookup_name,
            HTTPSOAP.cluster_id == cluster_id,
            HTTPSOAP.connection == CONNECTION.CHANNEL,
        ).first()

    # Build the payload common to both create and edit - the channel never shows up
    # in generated API documentation because the object's own per-ruleset paths do ..
    payload = {
        'name': object_name,
        'url_path': channel_url_path,
        'connection': CONNECTION.CHANNEL,
        'transport': URL_TYPE.PLAIN_HTTP,
        'is_active': is_active,
        'is_internal': True,
        'data_format': DATA_FORMAT.JSON,
        'match_slash': True,
        'should_include_in_openapi': False,
        'service': rule_engine_api_service_name,
        'security_groups': security_groups,
        'cluster_id': cluster_id,
    }

    if existing:
        payload['id'] = existing.id
        service_name = 'zato.http-soap.edit'
        logger.info(
            'on_rule_engine_api_create_edit: editing HTTPSOAP id=%s name=%s -> %s', existing.id, lookup_name, object_name)
    else:
        service_name = 'zato.http-soap.create'
        logger.info(
            'on_rule_engine_api_create_edit: creating HTTPSOAP name=%s url_path=%s', object_name, channel_url_path)

    _ = service.invoke(service_name, payload)

# ################################################################################################################################

def on_rule_engine_api_delete(service:'any_', object_name:'str') -> 'None':
    """ Removes the HTTPSOAP channel associated with a Rule engine API object.
    Called when its generic connection is deleted.
    """
    # Remove the HTTPSOAP channel by invoking the standard delete service - this both deletes
    # the database row and publishes the config event that removes the URL path
    # from the live request dispatcher, so requests to the deleted channel get 404.
    payload = {
        'name': object_name,
        'connection': CONNECTION.CHANNEL,
        'should_raise_if_missing': False,
    }
    _ = service.invoke('zato.http-soap.delete', payload)

# ################################################################################################################################
# ################################################################################################################################
