# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

openapi_channel_name = 'zato.channel.openapi.get'
openapi_channel_url_path = '/openapi/{name}'
openapi_service_name = 'zato.server.service.internal.helpers.OpenAPIHandler'

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
