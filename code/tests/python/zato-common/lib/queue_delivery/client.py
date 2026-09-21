# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a test does with the server the session fixture started - it talks to the test services every type's suite
# provides under the same names, so the scenarios need not know which type they run through.

# stdlib
import time
from json import loads
from logging import getLogger

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_table, get_audit_engine
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.test.client import AdminClient
from zato.common.test.conftest_base_pubsub import find_free_port, start_server_process

# Test support
from queue_delivery.type_under_test import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, anydict, anylist, strdict, strlist, strnone
    from queue_delivery.receiver import RecordingReceiver

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_default_wait_timeout_seconds = 30.0
_poll_interval_seconds = 0.1

# ################################################################################################################################
# ################################################################################################################################

# The services a type's suite provides ..
_send_service = 'test.queue-delivery.send'
_send_many_service = 'test.queue-delivery.send-many'
_read_service = 'test.queue-delivery.read'
_get_connection_service = 'test.queue-delivery.get-connection'
_edit_connection_service = 'test.queue-delivery.edit-connection'
_create_connection_service = 'test.queue-delivery.create-connection'
_delete_connection_service = 'test.queue-delivery.delete-connection'

# .. and the shared ones
_get_pubsub_backend_service = 'test.queue-delivery.get-pubsub-backend'
_get_queue_service = 'test.queue-delivery.get-queue'
_get_topic_subscribers_service = 'test.queue-delivery.get-topic-subscribers'

# ################################################################################################################################
# ################################################################################################################################

def conn_name(key:'str') -> 'str':
    """ The name of the connection the type's template declares under that key.
    """
    out = TestConfig.type_under_test.connections[key]
    return out

# ################################################################################################################################

def get_client() -> 'AdminClient':
    """ A client for the server the session fixture started.
    """
    out = AdminClient(TestConfig.base_url, TestConfig.password)
    return out

# ################################################################################################################################

def is_broker_backend() -> 'bool':
    """ Whether the queues of the current server live in a broker rather than in its pub/sub database.
    """
    out = TestConfig.backend.is_broker
    return out

# ################################################################################################################################

def get_receiver(key:'str') -> 'RecordingReceiver':
    """ The endpoint of the connection known by that key.
    """
    out = TestConfig.receivers[key]
    return out

# ################################################################################################################################

def get_pubsub_db_engine() -> 'Engine':
    """ An engine over the pub/sub database the current server uses.
    """
    out = get_pubsub_engine()
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

def send(client:'AdminClient', conn_name:'str', data:'any_', headers:'strdict | None'=None) -> 'anydict':
    """ Sends one message through a connection and returns what the send came back with.
    """
    if headers is None:
        headers = {}

    request = {
        'conn_name': conn_name,
        'data': data,
        'headers': headers,
    }

    response = client.invoke(_send_service, request)

    out = as_dict(response)
    return out

# ################################################################################################################################

def send_many(client:'AdminClient', conn_name:'str', data_list:'anylist') -> 'anylist':
    """ Sends messages through a connection one after another and returns what each came back with, in order.
    """
    request = {
        'conn_name': conn_name,
        'data_list': data_list,
    }

    response = client.invoke(_send_many_service, request)
    response = as_dict(response)

    out = response['results']
    return out

# ################################################################################################################################

def read(client:'AdminClient', conn_name:'str') -> 'anydict':
    """ Reads through a connection and returns what the read came back with.
    """
    request = {
        'conn_name': conn_name,
    }

    response = client.invoke(_read_service, request)

    out = as_dict(response)
    return out

# ################################################################################################################################

def get_pubsub_backend(client:'AdminClient') -> 'anydict':
    """ The type and name of the database the server's own pub/sub backend runs on.
    """
    response = client.invoke(_get_pubsub_backend_service, {})

    out = as_dict(response)
    return out

# ################################################################################################################################

def get_connection(client:'AdminClient', conn_name:'str') -> 'anydict':
    """ The configuration a connection has right now.
    """
    request = {
        'conn_name': conn_name,
    }

    response = client.invoke(_get_connection_service, request)

    out = as_dict(response)
    return out

# ################################################################################################################################

def edit_connection(client:'AdminClient', conn_name:'str', changes:'strdict') -> 'int':
    """ Changes some fields of a connection through the server's own edit service and returns the connection's id.
    """
    request = {
        'conn_name': conn_name,
        'changes': changes,
    }

    response = client.invoke(_edit_connection_service, request)
    response = as_dict(response)

    out = response['id']
    return out

# ################################################################################################################################

def create_connection(client:'AdminClient', conn_name:'str', like_conn_name:'str') -> 'int':
    """ Creates a connection configured like an existing one, under a new name, and returns its id.
    """
    request = {
        'conn_name': conn_name,
        'like_conn_name': like_conn_name,
    }

    response = client.invoke(_create_connection_service, request)
    response = as_dict(response)

    out = response['id']
    return out

# ################################################################################################################################

def delete_connection(client:'AdminClient', conn_name:'str') -> 'int':
    """ Deletes a connection through the server's own delete service and returns the id it had.
    """
    request = {
        'conn_name': conn_name,
    }

    response = client.invoke(_delete_connection_service, request)
    response = as_dict(response)

    out = response['id']
    return out

# ################################################################################################################################

def get_topic_subscribers(client:'AdminClient', topic_name:'str') -> 'anylist':
    """ The sub keys the pub/sub database has under a topic - none once the topic is gone.
    """
    request = {
        'topic_name': topic_name,
    }

    response = client.invoke(_get_topic_subscribers_service, request)
    response = as_dict(response)

    out = response['sub_key_list']
    return out

# ################################################################################################################################

def msg_ids_of(items:'anylist') -> 'strlist':
    """ The ids of a run of rows or messages, in order.
    """
    out = [item['msg_id'] for item in items]
    return out

# ################################################################################################################################

def get_queue(client:'AdminClient', conn_name:'str') -> 'anydict':
    """ What the server knows about a connection's queue.
    """
    request = {
        'conn_name': conn_name,
    }

    response = client.invoke(_get_queue_service, request)

    out = as_dict(response)
    return out

# ################################################################################################################################

def wait_for_queue_depth(
    client:'AdminClient',
    conn_name:'str',
    expected_depth:'int',
    timeout:'float'=_default_wait_timeout_seconds,
    ) -> 'anydict':
    """ Blocks until the server counts that many messages in a connection's queue, then returns what it knows about it.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        out = get_queue(client, conn_name)

        if out['depth'] == expected_depth:
            return out

        time.sleep(_poll_interval_seconds)

    out = get_queue(client, conn_name)
    return out

# ################################################################################################################################

def wait_for_queue_empty(
    client:'AdminClient',
    conn_name:'str',
    timeout:'float'=_default_wait_timeout_seconds,
    ) -> 'anydict':
    """ Blocks until a connection's queue is empty.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        out = get_queue(client, conn_name)

        if out['depth'] == 0 and not out['messages']:
            return out

        time.sleep(_poll_interval_seconds)

    out = get_queue(client, conn_name)
    return out

# ################################################################################################################################

def get_audit_events(cid:'str', event_type:'strnone'=None) -> 'anylist':
    """ The events the audit log holds under one correlation id, oldest first.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.where(event_table.c.cid == cid)

    if event_type:
        query = query.where(event_table.c.event_type == event_type)

    query = query.order_by(event_table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            event = dict(row._mapping)
            out.append(event)

    return out

# ################################################################################################################################

def wait_for_audit_events(
    cid:'str',
    event_type:'str',
    expected_count:'int',
    timeout:'float'=_default_wait_timeout_seconds,
    ) -> 'anylist':
    """ Blocks until that many events of one type are in the audit log under a correlation id, then returns them.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        out = get_audit_events(cid, event_type)

        if len(out) >= expected_count:
            return out

        time.sleep(_poll_interval_seconds)

    out = get_audit_events(cid, event_type)
    return out

# ################################################################################################################################

def restart_server() -> 'None':
    """ Stops the server and starts it again on the same port.
    """
    state = TestConfig.state
    state.kill_server()

    broker_port = find_free_port()

    _ = start_server_process(
        state=state,
        logger=logger,
        zato_bin=TestConfig.zato_bin,
        server_directory=TestConfig.server_directory,
        server_port=TestConfig.server_port,
        broker_port=broker_port,
        extra_server_env={},
        patch_server_conf_bind=False,
    )

# ################################################################################################################################
# ################################################################################################################################
