# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# Zato
from zato.common.test.client import AdminClient
from zato.common.test.config_pubsub_outgoing import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

# The services that hot deployment put in the server, one per way of naming a connection.
_publish_service = 'test.outgoing.publish'
_publish_through_facade_service = 'test.outgoing.publish-through-facade'

# ################################################################################################################################
# ################################################################################################################################

def get_client() -> 'AdminClient':
    """ A client for the server the session fixture started.
    """
    out = AdminClient(TestConfig.base_url, TestConfig.password)
    return out

# ################################################################################################################################

def as_dict(response:'any_') -> 'anydict':
    """ What a service answered, whether it came back as text or already parsed.
    """
    if isinstance(response, str):
        response = loads(response)

    out = response
    return out

# ################################################################################################################################

def publish(client:'AdminClient', conn_name:'str', data:'any_') -> 'str':
    """ Publishes one message to an outgoing connection and returns the id it was given.
    """
    request = {
        'conn_name': conn_name,
        'data': data,
    }

    response = client.invoke(_publish_service, request)
    response = as_dict(response)

    out = response['msg_id']
    return out

# ################################################################################################################################

def publish_through_facade(client:'AdminClient', conn_name:'str', data:'any_') -> 'str':
    """ The same publication, with the connection named through the REST facade instead.
    """
    request = {
        'conn_name': conn_name,
        'data': data,
    }

    response = client.invoke(_publish_through_facade_service, request)
    response = as_dict(response)

    out = response['msg_id']
    return out

# ################################################################################################################################
# ################################################################################################################################
