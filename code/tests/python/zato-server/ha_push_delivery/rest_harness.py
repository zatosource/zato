# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The environment of the tests of a REST push subscription that receives several messages per request, the staging
# of its batches, and the faults of the database that hold or end the commit of a push cycle of the server.

# stdlib
import time
from dataclasses import dataclass
from functools import partial

# Zato
from ha_push_delivery.harness import count_pending, import_template, new_key_prefix, publish_through_server, wait_until
from zato.common.test.pubsub_database import connect
from zato.common.test.zato_database import get_test_server, ModuleCtx as ZatoDatabaseCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_push_delivery.rest_receiver import ListReceiver
    from ha_push_delivery.server import PushDeliveryServer
    from zato.common.typing_ import anydict, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The topic of the REST push subscription
    Topic = 'ha-push-delivery.rest'

    # How many messages a batch has and how many of them go in one push request,
    # which makes a batch go out in two requests
    Message_Count = 6
    Push_Batch_Size = 3

    # The retry settings of a message that a test acts on between two attempts - a wait that the test acts within
    Retry_Wait_Seconds = 10
    Retry_Settings:'anydict' = {
        'max_retries': 5,
        'retry_sleep_time': Retry_Wait_Seconds,
        'retry_backoff_multiplier': 1,
    }

    # How long the tests wait for the session of the server that the lock holds and for an outcome, in seconds,
    # and how often they check it
    Lock_Wait_Timeout = 20.0
    Outcome_Timeout   = 20.0
    Poll_Interval     = 0.05

# The statement that locks the delivery rows of the topic, which the commit of a push cycle deletes
_lock_query = 'select d.id from pubsub_delivery d join pubsub_message m on m.id = d.message_id ' + \
    'where m.topic_name = %s for update of d'

# The session of the server whose statement waits for the lock of the test
_blocked_session_query = "select pid from pg_stat_activity where wait_event_type = 'Lock' " + \
    'and %s = any(pg_blocking_pids(pid))'

_backend_pid_query = 'select pg_backend_pid()'
_terminate_query   = 'select pg_terminate_backend(%s)'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RESTPushEnvironment:
    """ The server of the module, the receiver that its REST push subscription calls and the files that steer them.
    """
    server: 'PushDeliveryServer'
    receiver: 'ListReceiver'

    control_dir: 'str'
    template_path: 'str'
    placeholders: 'strstrdict'

# ################################################################################################################################
# ################################################################################################################################

def publish_message(env:'RESTPushEnvironment', key:'str', retry_settings:'anydict') -> 'str':
    """ Publishes one message with the key to the topic of the subscription and returns its message ID.
    """
    data = {'key': key}

    out = publish_through_server(env.server, ModuleCtx.Topic, data, retry_settings)
    return out

# ################################################################################################################################

def stage_batch(env:'RESTPushEnvironment', retry_settings:'anydict') -> 'strlist':
    """ Publishes the messages of one batch while the push delivery is paused and resumes it, so that all of them
    are claimed at once, and returns their message IDs in the order of publication.
    """
    prefix = new_key_prefix()

    out:'strlist' = []

    # The messages wait in the queue ..
    import_template(env.server, env.control_dir, env.template_path, env.placeholders, False)

    for idx in range(ModuleCtx.Message_Count):
        msg_id = publish_message(env, f'{prefix}{idx}', retry_settings)
        out.append(msg_id)

    # .. until the delivery resumes and claims all of them.
    import_template(env.server, env.control_dir, env.template_path, env.placeholders, True)

    return out

# ################################################################################################################################

def is_acknowledged(msg_ids:'strlist') -> 'bool':
    """ Returns True if no message of the list waits in the queue of the subscription.
    """
    for msg_id in msg_ids:
        if count_pending(msg_id):
            return False

    return True

# ################################################################################################################################

def wait_until_concluded(msg_ids:'strlist') -> 'None':
    """ Waits until no message of the list waits in the queue of the subscription.
    """
    acknowledged = partial(is_acknowledged, msg_ids)
    wait_until(acknowledged, f'conclusion of {msg_ids}', ModuleCtx.Outcome_Timeout)

# ################################################################################################################################
# ################################################################################################################################

class CommitHold:
    """ A transaction of the test that locks the delivery rows of the topic, which holds the commit of a push cycle
    of the server until the transaction ends.
    """
    def __init__(self, env:'RESTPushEnvironment') -> 'None':

        self.database = get_test_server()
        self.db_name = env.server.database_env[ZatoDatabaseCtx.Env_Name]

        self.connection = connect(self.database, db_name=self.db_name)
        self.pid = 0

    def lock(self) -> 'None':
        """ Locks the delivery rows of the topic in the open transaction of the test.
        """
        cursor = self.connection.cursor()

        _ = cursor.execute(_backend_pid_query)
        self.pid = cursor.fetchall()[0][0]

        _ = cursor.execute(_lock_query, (ModuleCtx.Topic,))

    def wait_for_blocked_session(self) -> 'int':
        """ Waits until a session of the server waits for the lock and returns its process ID.
        """
        deadline = time.monotonic() + ModuleCtx.Lock_Wait_Timeout

        connection = connect(self.database, is_admin=True)

        try:
            cursor = connection.cursor()

            while True:
                _ = cursor.execute(_blocked_session_query, (self.pid,))
                row = cursor.fetchone()
                connection.rollback()

                if row:
                    return row[0]

                if time.monotonic() > deadline:
                    raise Exception(f'No session waits for the lock of the test within {ModuleCtx.Lock_Wait_Timeout}s')

                time.sleep(ModuleCtx.Poll_Interval)

        finally:
            connection.close()

    def release(self) -> 'None':
        """ Ends the transaction of the test, which releases its lock.
        """
        self.connection.rollback()
        self.connection.close()

# ################################################################################################################################

def terminate_session(pid:'int') -> 'None':
    """ Terminates one session of the database, as a database that ends a connection does.
    """
    database = get_test_server()
    connection = connect(database, is_admin=True)

    try:
        cursor = connection.cursor()
        _ = cursor.execute(_terminate_query, (pid,))
        connection.commit()
    finally:
        connection.close()

# ################################################################################################################################
# ################################################################################################################################
