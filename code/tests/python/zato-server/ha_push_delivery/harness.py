# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import subprocess
import time
from dataclasses import dataclass

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import AuditEvent, event_table
from zato.common.audit_log.common import event_data
from zato.common.crypto.api import CryptoManager
from zato.common.db_env.database import get_database_engine
from zato.common.pubsub.sql.schema import message_table
from zato.common.test.client import AdminClient
from zato.common.test.conftest_base_pubsub import render_template
from zato.common.test.exactly_once.control import hold
from zato.common.test.exactly_once.verify import count_deliveries, read_correl_ids

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_push_delivery.server import PushDeliveryServer
    from zato.common.test.receiver import WebhookReceiver
    from zato.common.typing_ import anydict, anylist, callable_, strlist, strnone, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The topics, the outgoing connection and the publishing service of the suite
    Input_Topic     = 'ha-push-delivery.input'
    Output_Topic    = 'ha-push-delivery.output'
    Outgoing_Name   = 'test.ha-push-delivery.out'
    Publish_Service = 'test.ha-push-delivery.publish'

    # The path that the outgoing connection calls
    Receiver_Path = '/ha-push-delivery'

    # The placeholder of the enmasse file that turns the push delivery on and off
    Delivery_Active_Key = 'delivery_active'

    # The retry settings of a message that fails - one retry after a wait that a test acts within
    Retry_Wait_Seconds = 10
    Failing_Retry_Settings:'anydict' = {
        'max_retries': 1,
        'retry_sleep_time': Retry_Wait_Seconds,
        'retry_backoff_multiplier': 1,
    }

    # The invocation of the subscriber that a hold of a key applies to, unless a message names another one
    Default_Held_Invocation = 1

    # How long an import of the enmasse file may take, in seconds
    Enmasse_Timeout = 120

    # How long the tests wait for an outcome, in seconds, and how often they check it
    Wait_Timeout  = 120.0
    Poll_Interval = 0.1

    # The name of the rendered enmasse file in the control directory
    Enmasse_File_Name = 'enmasse.yaml'

    # The log file of the server, under its server directory, and the beginning of the entry that it logs
    # once a publication is committed
    Server_Log_Path  = ('logs', 'server.log')
    Published_Prefix = 'Published message -> msg_id:'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PushEnvironment:
    """ The server of the module, the endpoint that its outgoing connection calls and the files that steer them.
    """
    server: 'PushDeliveryServer'
    receiver: 'WebhookReceiver'

    control_dir: 'str'
    template_path: 'str'
    placeholders: 'strstrdict'

# ################################################################################################################################

@dataclass(init=False)
class StagedBatch:
    """ The keys and the message IDs of the two messages of a batch, the first of which is concluded
    before the second one.
    """
    first_key: 'str'
    second_key: 'str'

    first_msg_id: 'str'
    second_msg_id: 'str'

# ################################################################################################################################
# ################################################################################################################################

def new_key_prefix() -> 'str':
    """ Returns a prefix of the keys that is unique to one test.
    """
    suffix = CryptoManager.generate_hex_string()

    out = f'push-delivery.{suffix}.'
    return out

# ################################################################################################################################

def import_enmasse(env:'PushEnvironment', is_delivery_active:'bool') -> 'None':
    """ Imports the definitions of the suite into the running server, with the push delivery active or paused.
    """
    placeholders = dict(env.placeholders)

    if is_delivery_active:
        placeholders[ModuleCtx.Delivery_Active_Key] = 'true'
    else:
        placeholders[ModuleCtx.Delivery_Active_Key] = 'false'

    # Render the template ..
    rendered = render_template(env.template_path, placeholders)
    rendered_path = os.path.join(env.control_dir, ModuleCtx.Enmasse_File_Name)

    with open(rendered_path, 'w') as rendered_file:
        _ = rendered_file.write(rendered)

    # .. and import it the way a user does.
    environment = os.environ.copy()
    _ = environment.pop('COVERAGE_PROCESS_START', None)

    command = [env.server.zato_bin, 'enmasse', env.server.server_directory, '--verbose',
        '--import', '--input', rendered_path, '--missing-wait-time', '15']

    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=ModuleCtx.Enmasse_Timeout,
        env=environment)

    assert result.returncode == 0, f'enmasse import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}'

# ################################################################################################################################

def _publish_to_topic(env:'PushEnvironment', topic_name:'str', data:'anydict', options:'anydict') -> 'str':
    """ Publishes one message to a topic through the publishing service of the suite, with the given options
    of the publication, and returns its message ID.
    """
    client = AdminClient(env.server.base_url, env.server.invoke_password)

    request = {
        'topic_name': topic_name,
        'data': data,
        'options': options,
    }

    response = client.invoke(ModuleCtx.Publish_Service, request)

    out = response['msg_id']
    return out

# ################################################################################################################################

def publish(
    env:'PushEnvironment',
    key:'str',
    should_fail:'bool',
    retry_settings:'anydict',
    held_invocation:'int' = ModuleCtx.Default_Held_Invocation,
    output_msg_id:'strnone' = None,
    ) -> 'str':
    """ Publishes one message to the input topic and returns its message ID. A hold of the key applies
    to the invocation of the subscriber with the given number only. The subscriber publishes to the output topic
    under the given message ID, or under one of its own if none is given.
    """
    data = {
        'key': key,
        'should_fail': should_fail,
        'held_invocation': held_invocation,
        'output_msg_id': output_msg_id,
    }

    out = _publish_to_topic(env, ModuleCtx.Input_Topic, data, retry_settings)
    return out

# ################################################################################################################################

def publish_output(env:'PushEnvironment', msg_id:'str', key:'str') -> 'None':
    """ Publishes one message with the key to the output topic under the given message ID,
    with the key as its correlation ID.
    """
    data = {'key': key}

    options = {
        'msg_id': msg_id,
        'correl_id': key,
    }

    _ = _publish_to_topic(env, ModuleCtx.Output_Topic, data, options)

# ################################################################################################################################

def get_message_correl_ids(msg_id:'str') -> 'strlist':
    """ Returns the correlation ID of each stored message with the message ID, of which there is at most one.
    """
    engine = get_database_engine()

    query = select(message_table.c.correl_id)
    query = query.where(message_table.c.msg_id == msg_id)

    with engine.connect() as connection:
        rows = connection.execute(query).fetchall()

    out:'strlist' = []

    for row in rows:
        out.append(row.correl_id)

    return out

# ################################################################################################################################

def count_published_log_entries(env:'PushEnvironment', msg_id:'str') -> 'int':
    """ Returns how many times the server logged that the publication of the message ID was committed.
    """
    path = os.path.join(env.server.server_directory, *ModuleCtx.Server_Log_Path)
    entry = f'{ModuleCtx.Published_Prefix}{msg_id},'

    out = 0

    with open(path) as log_file:
        for line in log_file:
            if entry in line:
                out += 1

    return out

# ################################################################################################################################

def stage_batch(env:'PushEnvironment', second_fails:'bool', is_second_held:'bool') -> 'StagedBatch':
    """ Publishes two messages while the push delivery is paused and resumes it, so that both of them
    go out in one batch. The first message succeeds, the second one fails if requested, under retry settings
    that make its round wait between its two attempts, and its first invocation is held if requested.
    """
    prefix = new_key_prefix()

    out = StagedBatch()
    out.first_key = prefix + 'first'
    out.second_key = prefix + 'second'

    # The messages wait in the queue ..
    import_enmasse(env, False)

    if second_fails:
        second_retry_settings = ModuleCtx.Failing_Retry_Settings
    else:
        second_retry_settings = {}

    out.first_msg_id = publish(env, out.first_key, False, {})
    out.second_msg_id = publish(env, out.second_key, second_fails, second_retry_settings)

    if is_second_held:
        hold(out.second_key)

    # .. until the delivery resumes and reads both of them at once.
    import_enmasse(env, True)

    return out

# ################################################################################################################################
# ################################################################################################################################

def wait_until(check:'callable_', description:'str', timeout:'float'=ModuleCtx.Wait_Timeout) -> 'None':
    """ Waits until the check returns True.
    """
    deadline = time.monotonic() + timeout

    while not check():
        if time.monotonic() > deadline:
            raise Exception(f'Not reached within {timeout}s -> {description}')
        time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

def get_audit_events(msg_id:'str', event_type:'str') -> 'anylist':
    """ Returns the events of one type that the audit log holds about one message.
    """
    engine = get_database_engine()

    query = select(event_table.c.id)
    query = query.where(event_table.c.msg_id == msg_id)
    query = query.where(event_table.c.event_type == event_type)

    with engine.connect() as connection:
        out = connection.execute(query).fetchall()

    return out

# ################################################################################################################################

def count_audit_events(msg_id:'str', event_type:'str') -> 'int':
    """ Returns how many events of one type the audit log holds about one message.
    """
    events = get_audit_events(msg_id, event_type)

    out = len(events)
    return out

# ################################################################################################################################

def count_outgoing_requests(key:'str') -> 'int':
    """ Returns how many requests of the outgoing connection with the key the audit log holds.
    """
    engine = get_database_engine()

    query = select(event_table.c.id, event_data)
    query = query.where(event_table.c.object_name == ModuleCtx.Outgoing_Name)
    query = query.where(event_table.c.event_type == AuditEvent.Request_Sent)

    with engine.connect() as connection:
        rows = connection.execute(query).fetchall()

    out = 0

    for row in rows:
        if key in row.data:
            out += 1

    return out

# ################################################################################################################################

def count_received(env:'PushEnvironment', key:'str') -> 'int':
    """ Returns how many requests with the key the endpoint of the outgoing connection received.
    """
    out = 0

    for item in env.receiver.get_delivered_messages():
        if item['key'] == key:
            out += 1

    return out

# ################################################################################################################################

def count_rejected(env:'PushEnvironment', key:'str') -> 'int':
    """ Returns how many requests with the key the endpoint of the outgoing connection rejected.
    """
    out = 0

    for body in env.receiver.behavior.rejected_bodies:
        item = json.loads(body)
        if item['key'] == key:
            out += 1

    return out

# ################################################################################################################################

def count_outputs(key:'str') -> 'int':
    """ Returns how many messages with the key the output topic holds.
    """
    engine = get_database_engine()
    correl_ids = read_correl_ids(engine, ModuleCtx.Output_Topic, key)

    out = 0

    for correl_id in correl_ids:
        if correl_id == key:
            out += 1

    return out

# ################################################################################################################################

def count_pending(msg_id:'str') -> 'int':
    """ Returns how many delivery rows the message still has.
    """
    engine = get_database_engine()

    out = count_deliveries(engine, msg_id)
    return out

# ################################################################################################################################

def is_concluded(msg_id:'str', event_type:'str') -> 'bool':
    """ Whether the message has an audit event of the type and no delivery row left.
    """
    event_count = count_audit_events(msg_id, event_type)

    if not event_count:
        return False

    pending_count = count_pending(msg_id)

    out = pending_count == 0
    return out

# ################################################################################################################################
# ################################################################################################################################
