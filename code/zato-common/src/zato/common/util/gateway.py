# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

mcp_gateway_name = 'zato.gateway.mcp'
mcp_gateway_url_path = '/mcp/demo'
mcp_service_name = 'zato.server.service.internal.gateway.mcp.MCPEndpoint'

# ################################################################################################################################
# ################################################################################################################################

def ensure_mcp_gateway_exists(session, cluster_id):
    """ Creates both the HTTP channel and the generic connection for MCP if they do not exist.
    The HTTP channel routes POST /mcp to the MCPEndpoint service.
    The generic connection registers the gateway-mcp type in the config manager.
    Both must share the same name so MCPEndpoint can look up its handler.
    Returns True if created, False if already existed.
    """
    from zato.common.api import CONNECTION, DATA_FORMAT, GENERIC, URL_TYPE
    from zato.common.odb.model import Cluster, GenericConn, HTTPSOAP, Service

    existing_http = session.query(HTTPSOAP).filter(
        HTTPSOAP.name == mcp_gateway_name,
        HTTPSOAP.cluster_id == cluster_id,
        HTTPSOAP.connection == CONNECTION.CHANNEL,
    ).first()

    existing_generic = session.query(GenericConn).filter(
        GenericConn.name == mcp_gateway_name,
        GenericConn.type_ == GENERIC.CONNECTION.TYPE.GATEWAY_MCP,
        GenericConn.cluster_id == cluster_id,
    ).first()

    if existing_http and existing_generic:
        return False

    cluster = session.query(Cluster).filter(Cluster.id == cluster_id).one()

    # Create the HTTP channel if missing ..
    if not existing_http:

        service = session.query(Service).filter(
            Service.name == mcp_service_name,
            Service.cluster_id == cluster_id,
        ).first()

        if not service:
            service = Service(None, mcp_service_name, True, mcp_service_name, True, cluster)
            session.add(service)
            session.flush()

        channel = HTTPSOAP(
            None, mcp_gateway_name, True, True, CONNECTION.CHANNEL,
            URL_TYPE.PLAIN_HTTP, None, mcp_gateway_url_path, None, '', None, DATA_FORMAT.JSON,
            service=service, cluster=cluster)
        session.add(channel)

    # .. create the generic connection if missing.
    if not existing_generic:

        generic_conn = GenericConn()
        generic_conn.name = mcp_gateway_name
        generic_conn.type_ = GENERIC.CONNECTION.TYPE.GATEWAY_MCP
        generic_conn.is_active = True
        generic_conn.is_internal = True
        generic_conn.is_channel = True
        generic_conn.is_outconn = False
        generic_conn.cluster_id = cluster_id
        generic_conn.opaque1 = '{"services": ["demo.echo", "test.raise"], "url_path": "/mcp/demo"}'

        session.add(generic_conn)

    return True

# ################################################################################################################################
# ################################################################################################################################

def ensure_mcp_rest_channel(session, channel_name, url_path, cluster_id, is_active=True,
                            security_groups=None, old_name=None):
    """ Creates or updates the REST channel that makes an MCP gateway reachable over HTTP.
    Called from both the server-side hook (on_mcp_gateway_create_edit) and the enmasse importer.
    Does NOT commit - the caller is responsible for committing the session.
    """
    from zato.common.api import CONNECTION, DATA_FORMAT, URL_TYPE
    from zato.common.odb.model import Cluster, HTTPSOAP, Service
    from zato.common.util.sql import set_instance_opaque_attrs

    security_groups = security_groups or []

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
        existing_http.url_path = url_path
        existing_http.is_active = is_active
        set_instance_opaque_attrs(existing_http, {'security_groups': security_groups})

    # .. otherwise, create a new one.
    else:
        cluster = session.query(Cluster).filter(Cluster.id == cluster_id).one()

        mcp_service = session.query(Service).filter(
            Service.name == mcp_service_name,
            Service.cluster_id == cluster_id,
        ).first()

        if not mcp_service:
            mcp_service = Service(None, mcp_service_name, True, mcp_service_name, True, cluster)
            session.add(mcp_service)
            session.flush()

        http_channel = HTTPSOAP(
            None, channel_name, is_active, True, CONNECTION.CHANNEL,
            URL_TYPE.PLAIN_HTTP, None, url_path, None, '', None, DATA_FORMAT.JSON,
            service=mcp_service, cluster=cluster, security=None)
        set_instance_opaque_attrs(http_channel, {'security_groups': security_groups})
        session.add(http_channel)

# ################################################################################################################################
# ################################################################################################################################

def _resolve_security_group_names_to_ids(session, group_names, cluster_id):
    """ Converts a list of security group names to their database IDs.
    Needed because GenericConn stores group names but HTTPSOAP needs group IDs
    for the server's security_groups_ctx_builder to work.
    """
    from zato.common.api import Groups
    from zato.common.odb.model import GenericObject

    if not group_names:
        return []

    out = []

    for name in group_names:

        # .. skip entries that are already numeric IDs ..
        if isinstance(name, int):
            out.append(name)
            continue

        group = session.query(GenericObject).filter(
            GenericObject.name == name,
            GenericObject.type_ == Groups.Type.Group_Parent,
            GenericObject.cluster_id == cluster_id,
        ).first()

        if group:
            out.append(group.id)

    return out

# ################################################################################################################################
# ################################################################################################################################

def on_mcp_gateway_create_edit(service, data, model, old_name):
    """ Hook called by zato.generic.connection create/edit for the gateway-mcp type.
    Creates or updates the HTTPSOAP channel by invoking the standard http-soap services,
    which handle ODB persistence, uniqueness checks, and broker notification.
    """
    import logging
    from contextlib import closing

    from zato.common.api import CONNECTION, DATA_FORMAT, URL_TYPE
    from zato.common.odb.model import HTTPSOAP

    logger = logging.getLogger(__name__)

    gateway_name = data['name']
    url_path = data['url_path']
    is_active = data.get('is_active', True)
    cluster_id = model.cluster_id

    with closing(service.server.odb.session()) as session:

        security_groups = data.get('security_groups', [])
        security_groups = _resolve_security_group_names_to_ids(session, security_groups, cluster_id)

        # Check if the HTTPSOAP channel already exists (use old_name for renames) ..
        lookup_name = old_name if (old_name and old_name != gateway_name) else gateway_name
        existing = session.query(HTTPSOAP).filter(
            HTTPSOAP.name == lookup_name,
            HTTPSOAP.cluster_id == cluster_id,
            HTTPSOAP.connection == CONNECTION.CHANNEL,
        ).first()

    # Build the payload common to both create and edit ..
    payload = {
        'name': gateway_name,
        'url_path': url_path,
        'connection': CONNECTION.CHANNEL,
        'transport': URL_TYPE.PLAIN_HTTP,
        'is_active': is_active,
        'is_internal': True,
        'data_format': DATA_FORMAT.JSON,
        'service': mcp_service_name,
        'security_groups': security_groups,
        'cluster_id': cluster_id,
    }

    if existing:
        payload['id'] = existing.id
        service_name = 'zato.http-soap.edit'
        logger.info('on_mcp_gateway_create_edit: editing HTTPSOAP id=%s name=%s -> %s', existing.id, lookup_name, gateway_name)
    else:
        service_name = 'zato.http-soap.create'
        logger.info('on_mcp_gateway_create_edit: creating HTTPSOAP name=%s url_path=%s', gateway_name, url_path)

    service.invoke(service_name, payload)

# ################################################################################################################################
# ################################################################################################################################

def on_mcp_gateway_delete(service, session, gateway_name, cluster_id):
    """ Removes the HTTPSOAP channel associated with an MCP gateway.
    Also removes the auto-created security group named mcp.<gateway_name>.
    Called when an MCP generic connection is deleted.
    """
    from zato.common.api import CONNECTION, Groups
    from zato.common.odb.model import GenericObject

    # Remove the HTTPSOAP channel by invoking the standard delete service - this both deletes
    # the database row and publishes the config event that removes the URL path
    # from the live request dispatcher, so requests to the deleted channel get 404 ..
    payload = {
        'name': gateway_name,
        'connection': CONNECTION.CHANNEL,
        'should_raise_if_missing': False,
    }
    _ = service.invoke('zato.http-soap.delete', payload)

    # .. also remove the auto-created security group and its members ..
    group_name = 'mcp.' + gateway_name
    existing_group = session.query(GenericObject).filter(
        GenericObject.name == group_name,
        GenericObject.type_ == Groups.Type.Group_Parent,
        GenericObject.cluster_id == cluster_id,
    ).first()

    if existing_group:
        # .. delete all members first ..
        session.query(GenericObject).filter(
            GenericObject.parent_object_id == existing_group.id,
            GenericObject.type_ == Groups.Type.Group_Member,
        ).delete()

        # .. then delete the group itself.
        session.delete(existing_group)

# ################################################################################################################################
# ################################################################################################################################
