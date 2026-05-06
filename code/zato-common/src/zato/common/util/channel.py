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

django_channel_name = 'zato.django'
django_channel_url_path = '/django'
django_service_name = 'zato.server.service.internal.helpers.DjangoServiceGateway'

mcp_channel_name = 'zato.channel.mcp'
mcp_channel_url_path = '/mcp'
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

def ensure_django_channel_exists(session, cluster_id):
    """ Checks if Django channel exists, creates it if not.
    Returns True if created, False if already existed.
    """
    from zato.common.api import CONNECTION, DATA_FORMAT, URL_TYPE
    from zato.common.odb.model import Cluster, HTTPSOAP, Service

    existing = session.query(HTTPSOAP).filter(
        HTTPSOAP.name == django_channel_name,
        HTTPSOAP.cluster_id == cluster_id,
        HTTPSOAP.connection == CONNECTION.CHANNEL,
    ).first()

    if existing:
        return False

    cluster = session.query(Cluster).filter(Cluster.id == cluster_id).one()

    service = session.query(Service).filter(
        Service.name == django_service_name,
        Service.cluster_id == cluster_id,
    ).first()

    if not service:
        service = Service(None, django_service_name, True, django_service_name, True, cluster)
        session.add(service)
        session.flush()

    channel = HTTPSOAP(
        None, django_channel_name, True, True, CONNECTION.CHANNEL,
        URL_TYPE.PLAIN_HTTP, None, django_channel_url_path, None, '', None, DATA_FORMAT.JSON,
        service=service, cluster=cluster)
    session.add(channel)

    return True

# ################################################################################################################################
# ################################################################################################################################

def ensure_mcp_channel_exists(session, cluster_id):
    """ Creates both the HTTP channel and the generic connection for MCP if they do not exist.
    The HTTP channel routes POST /mcp to the MCPEndpoint service.
    The generic connection registers the channel-mcp type in the worker store.
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
            URL_TYPE.PLAIN_HTTP, None, mcp_channel_url_path, 'POST', '', None, DATA_FORMAT.JSON,
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
        generic_conn.opaque1 = {'services': ['helpers.echo']}

        session.add(generic_conn)

    return True

# ################################################################################################################################
# ################################################################################################################################
