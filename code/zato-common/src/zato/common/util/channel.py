# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

openapi_channel_name = 'zato.channel.openapi.get'
openapi_channel_url_path = '/openapi/{name}'
openapi_service_name = 'zato.server.service.internal.helpers.OpenAPIHandler'

mcp_channel_name = 'zato.channel.mcp'
mcp_channel_url_path = '/mcp/demo'
mcp_service_name = 'zato.server.service.internal.channel.mcp.MCPEndpoint'

# ################################################################################################################################
# ################################################################################################################################

def create_openapi_channel(session, cluster, service):
    """ Creates the OpenAPI handler channel.
    """
    from zato.common.api import CONNECTION, DATA_FORMAT, URL_TYPE
    from zato.common.odb.model import HTTPSOAP

    channel = HTTPSOAP(
        None, openapi_channel_name, True, True, CONNECTION.CHANNEL,
        URL_TYPE.PLAIN_HTTP, None, openapi_channel_url_path, None, '', None, DATA_FORMAT.JSON,
        service=service, cluster=cluster)
    session.add(channel)

    return channel

# ################################################################################################################################
# ################################################################################################################################

def ensure_openapi_channel_exists(session, cluster_id):
    """ Checks if OpenAPI channel exists, creates it if not.
    Returns True if created, False if already existed.
    """
    from zato.common.api import CONNECTION, DATA_FORMAT, URL_TYPE
    from zato.common.odb.model import Cluster, HTTPSOAP, Service

    existing = session.query(HTTPSOAP).filter(
        HTTPSOAP.name == openapi_channel_name,
        HTTPSOAP.cluster_id == cluster_id,
        HTTPSOAP.connection == CONNECTION.CHANNEL,
    ).first()

    if existing:
        return False

    cluster = session.query(Cluster).filter(Cluster.id == cluster_id).one()

    service = session.query(Service).filter(
        Service.name == openapi_service_name,
        Service.cluster_id == cluster_id,
    ).first()

    if not service:
        service = Service(None, openapi_service_name, True, openapi_service_name, True, cluster)
        session.add(service)
        session.flush()

    channel = HTTPSOAP(
        None, openapi_channel_name, True, True, CONNECTION.CHANNEL,
        URL_TYPE.PLAIN_HTTP, None, openapi_channel_url_path, None, '', None, DATA_FORMAT.JSON,
        service=service, cluster=cluster)
    session.add(channel)

    return True

# ################################################################################################################################
# ################################################################################################################################

def ensure_mcp_channel_exists(session, cluster_id):
    """ Creates both the HTTP channel and the generic connection for MCP if they do not exist.
    The HTTP channel routes POST /mcp to the MCPEndpoint service.
    The generic connection registers the channel-mcp type in the config manager.
    Both must share the same name so MCPEndpoint can look up its handler.
    Returns True if created, False if already existed.
    """
    from zato.common.api import CONNECTION, DATA_FORMAT, GENERIC, URL_TYPE
    from zato.common.odb.model import Cluster, GenericConn, HTTPSOAP, Service

    existing_http = session.query(HTTPSOAP).filter(
        HTTPSOAP.name == mcp_channel_name,
        HTTPSOAP.cluster_id == cluster_id,
        HTTPSOAP.connection == CONNECTION.CHANNEL,
    ).first()

    existing_generic = session.query(GenericConn).filter(
        GenericConn.name == mcp_channel_name,
        GenericConn.type_ == GENERIC.CONNECTION.TYPE.CHANNEL_MCP,
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
            None, mcp_channel_name, True, True, CONNECTION.CHANNEL,
            URL_TYPE.PLAIN_HTTP, None, mcp_channel_url_path, None, '', None, DATA_FORMAT.JSON,
            service=service, cluster=cluster)
        session.add(channel)

    # .. create the generic connection if missing.
    if not existing_generic:

        generic_conn = GenericConn()
        generic_conn.name = mcp_channel_name
        generic_conn.type_ = GENERIC.CONNECTION.TYPE.CHANNEL_MCP
        generic_conn.is_active = True
        generic_conn.is_internal = True
        generic_conn.is_channel = True
        generic_conn.is_outconn = False
        generic_conn.cluster_id = cluster_id
        generic_conn.opaque1 = '{"services": ["demo.echo"], "url_path": "/mcp/demo"}'

        session.add(generic_conn)

    return True

# ################################################################################################################################
# ################################################################################################################################

def on_mcp_channel_create_edit(service, data, model, old_name):
    """ Hook called by zato.generic.connection create/edit for channel-mcp type.
    Ensures a matching HTTPSOAP channel exists and routes to the MCPEndpoint service.
    On rename, the old HTTPSOAP channel is removed and a new one is created.
    Also propagates security_groups from the MCP channel to the HTTPSOAP channel's opaque data.
    """
    from contextlib import closing

    from zato.common.api import CONNECTION, DATA_FORMAT, URL_TYPE
    from zato.common.odb.model import Cluster, HTTPSOAP, Service

    with closing(service.server.odb.session()) as session:

        channel_name = data['name']
        url_path = data['url_path']
        cluster_id = model.cluster_id
        security_groups = data.get('security_groups', [])

        # If this is a rename, delete the old HTTPSOAP channel first ..
        if old_name and old_name != channel_name:
            old_http = session.query(HTTPSOAP).filter(
                HTTPSOAP.name == old_name,
                HTTPSOAP.cluster_id == cluster_id,
                HTTPSOAP.connection == CONNECTION.CHANNEL,
            ).first()
            if old_http:
                session.delete(old_http)

        # .. check if the HTTPSOAP channel already exists ..
        existing_http = session.query(HTTPSOAP).filter(
            HTTPSOAP.name == channel_name,
            HTTPSOAP.cluster_id == cluster_id,
            HTTPSOAP.connection == CONNECTION.CHANNEL,
        ).first()

        # Build the opaque data with security groups ..
        opaque = {'security_groups': security_groups} if security_groups else {}

        # .. if it exists, update its URL path and security groups ..
        if existing_http:
            existing_http.url_path = url_path
            existing_http.is_active = data.get('is_active', True)

            # .. merge security_groups into existing opaque data ..
            current_opaque = existing_http.opaque1 or {}
            current_opaque['security_groups'] = security_groups
            existing_http.opaque1 = current_opaque

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
                None, channel_name, True, data.get('is_active', True), CONNECTION.CHANNEL,
                URL_TYPE.PLAIN_HTTP, None, url_path, None, '', None, DATA_FORMAT.JSON,
                service=mcp_service, cluster=cluster, opaque=opaque)
            session.add(http_channel)

        session.commit()

# ################################################################################################################################
# ################################################################################################################################

def on_mcp_channel_delete(session, channel_name, cluster_id):
    """ Removes the HTTPSOAP channel associated with an MCP channel.
    Also removes the auto-created security group named mcp.<channel_name>.
    Called when an MCP generic connection is deleted.
    """
    from zato.common.api import CONNECTION, Groups
    from zato.common.odb.model import GenericObject, HTTPSOAP

    # Remove the HTTPSOAP channel ..
    existing_http = session.query(HTTPSOAP).filter(
        HTTPSOAP.name == channel_name,
        HTTPSOAP.cluster_id == cluster_id,
        HTTPSOAP.connection == CONNECTION.CHANNEL,
    ).first()

    if existing_http:
        session.delete(existing_http)

    # .. also remove the auto-created security group and its members ..
    group_name = 'mcp.' + channel_name
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
