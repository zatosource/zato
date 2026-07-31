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
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

# The services that hot deployment put in the server, one per way of naming a connection
# and one per thing that can be done to one.
_publish_service = 'test.outgoing.publish'
_publish_through_facade_service = 'test.outgoing.publish-through-facade'
_rename_service = 'test.outgoing.rename-connection'
_delete_service = 'test.outgoing.delete-connection'
_get_queues_service = 'test.outgoing.get-queues'

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

def rename_connection(client:'AdminClient', conn_name:'str', new_name:'str') -> 'int':
    """ Renames an outgoing connection and returns the id it keeps through that rename.
    """
    request = {
        'conn_name': conn_name,
        'new_name': new_name,
    }

    response = client.invoke(_rename_service, request)
    response = as_dict(response)

    out = int(response['id'])
    return out

# ################################################################################################################################

def delete_connection(client:'AdminClient', conn_name:'str') -> 'int':
    """ Deletes an outgoing connection and returns the id it had, which is what its queue was named after.
    """
    request = {
        'conn_name': conn_name,
    }

    response = client.invoke(_delete_service, request)
    response = as_dict(response)

    out = int(response['id'])
    return out

# ################################################################################################################################

def get_queues(client:'AdminClient') -> 'anylist':
    """ Every queue that stands in front of an outgoing connection, each with the topics it holds.
    """
    response = client.invoke(_get_queues_service, {})
    response = as_dict(response)

    out = response['queues']
    return out

# ################################################################################################################################

def get_queue(client:'AdminClient', sub_key:'str') -> 'anydict':
    """ The one queue of one connection, or nothing at all if that connection has none.
    """
    for queue in get_queues(client):
        if queue['sub_key'] == sub_key:
            return queue

    return {}

# ################################################################################################################################
# ################################################################################################################################
