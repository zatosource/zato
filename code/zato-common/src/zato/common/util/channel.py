# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strnone
    any_ = any_
    anylist = anylist
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

openapi_channel_name = 'zato.channel.openapi.get'
openapi_channel_url_path = '/openapi/{name}'
openapi_service_name = 'zato.server.service.internal.helpers.OpenAPIHandler'

as2_mdn_service_name = 'zato.server.service.internal.channel.as2.AS2MDNEndpoint'

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

def ensure_as2_channel_exists(session, cluster_id):
    """ Checks if the AS2 inbound channel exists, creates it if not.
    Returns True if created, False if already existed.
    """
    from zato.common.api import AS2, CONNECTION, URL_TYPE
    from zato.common.odb.model import Cluster, HTTPSOAP

    existing = session.query(HTTPSOAP).filter(
        HTTPSOAP.name == AS2.Default.Channel_Name,
        HTTPSOAP.cluster_id == cluster_id,
        HTTPSOAP.connection == CONNECTION.CHANNEL,
    ).first()

    if existing:
        return False

    cluster = session.query(Cluster).filter(Cluster.id == cluster_id).one()

    # The dispatcher handles AS2 channels itself, so there is no service to point to,
    # and the data format is None so the raw MIME body arrives untouched.
    channel = HTTPSOAP(
        None, AS2.Default.Channel_Name, True, True, CONNECTION.CHANNEL,
        URL_TYPE.AS2, None, AS2.Default.Channel_URL_Path, None, '', None, None,
        cluster=cluster)
    session.add(channel)

    return True

# ################################################################################################################################
# ################################################################################################################################

def find_channel_collision(
    url_path,      # type: str
    http_accept,   # type: strnone
    http_method,   # type: strnone
    soap_action,   # type: str
    existing_items # type: anylist
) -> 'strnone':
    """ The one collision rule for HTTP channels - a candidate collides with an existing channel
    when both sit at the same URL path with the same SOAP action and their HTTP method and Accept
    header are equal too. Each existing item carries name, url_path, method, soap_action and http_accept.
    Returns the name of the colliding channel or None. Callers differ only in how they load
    the existing items - zato.http-soap.create with its per-candidate query, the auto-channel
    batch with its one SELECT for everything.
    """
    for item in existing_items:

        # A different URL path can never collide ..
        if item['url_path'] != url_path:
            continue

        # .. neither can a different SOAP action ..
        if item['soap_action'] != soap_action:
            continue

        # .. it takes both the same method and the same Accept header to collide.
        if item['method'] == http_method:
            if item['http_accept'] == http_accept:
                return item['name']

    return None

# ################################################################################################################################
# ################################################################################################################################

def ensure_as2_mdn_channel_exists(session, cluster_id):
    """ Checks if the channel for incoming asynchronous AS2 MDNs exists, creates it if not.
    Returns True if created, False if already existed.
    """
    from zato.common.api import AS2, CONNECTION, URL_TYPE
    from zato.common.odb.model import Cluster, HTTPSOAP, Service

    existing = session.query(HTTPSOAP).filter(
        HTTPSOAP.name == AS2.Default.MDN_Channel_Name,
        HTTPSOAP.cluster_id == cluster_id,
        HTTPSOAP.connection == CONNECTION.CHANNEL,
    ).first()

    if existing:
        return False

    cluster = session.query(Cluster).filter(Cluster.id == cluster_id).one()

    service = session.query(Service).filter(
        Service.name == as2_mdn_service_name,
        Service.cluster_id == cluster_id,
    ).first()

    if not service:
        service = Service(None, as2_mdn_service_name, True, as2_mdn_service_name, True, cluster)
        session.add(service)
        session.flush()

    # The data format is None so the raw MDN body arrives untouched.
    channel = HTTPSOAP(
        None, AS2.Default.MDN_Channel_Name, True, True, CONNECTION.CHANNEL,
        URL_TYPE.PLAIN_HTTP, None, AS2.Default.MDN_Channel_URL_Path, None, '', None, None,
        service=service, cluster=cluster)
    session.add(channel)

    return True

# ################################################################################################################################
# ################################################################################################################################
