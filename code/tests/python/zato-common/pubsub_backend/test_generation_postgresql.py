# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile

# pytest
import pytest

# Zato
from zato.common.audit_log.api import AuditEvent, AuditSource
from zato.common.db_env.database import dispose_database_engine, get_database_engine
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.pubsub.sql.cleanup import PubSubCleanup
from zato.common.db_env.fence import read_generation_file, write_generation_file
from zato.common.pubsub.outgoing import get_outgoing_sub_key
from zato.common.pubsub.sql.fenced_ack import PubSubAckConflict
from zato.common.pubsub.sql.replaced import PubSubReplaced
from zato.common.test.direct_sql.fault import restore_previous_generation
from zato.common.test.takeover import take_over_as_another_server
from zato.common.test.pubsub_database import connect, get_suite_modes, pubsub_db_env, PubSubDBMode, \
    start_pubsub_database, stop_pubsub_database
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, strstrdict

# ################################################################################################################################
# ################################################################################################################################

_topic_name = 'generation.guard'
_sub_key = 'zpsk.generation.guard'

# The topic and the subscription of the server whose generation another server reaches again
_reached_topic_name = 'generation.reached'
_reached_sub_key = 'zpsk.generation.reached'

# The topic of the servers of active-standby nodes and the subscription of each server
_ha_topic_name = 'generation.ha'
_ha_current_sub_key = 'zpsk.generation.ha.current'
_ha_lower_sub_key = 'zpsk.generation.ha.lower'
_ha_earlier_sub_key = 'zpsk.generation.ha.earlier'
_ha_later_sub_key = 'zpsk.generation.ha.later'

# How far above the stored generation the active-standby nodes of a test begin
_ha_generation_step = 10

# The topic and the subscription of the server whose engine is disposed of after another server replaced it
_disposed_topic_name = 'generation.disposed'
_disposed_sub_key = 'zpsk.generation.disposed'

# The object of the audit event that the server whose engine is disposed of attempts to write
_disposed_object_name = 'generation.disposed'

# The topic and the connection of the outgoing queue whose messages a replaced server attempts to acknowledge
_outgoing_topic_name = 'generation.outgoing'
_outgoing_conn_type = 'generation-test'
_outgoing_conn_id = 1

# The pool sizes that give each server of these tests an engine of its own, since engines are cached by their settings
# and the guard of a cleanup process remains on the engine that it confirms the generation through
_pool_size_replaced  = 2
_pool_size_reached   = 3
_pool_size_current   = 4
_pool_size_lower     = 5
_pool_size_earlier   = 6
_pool_size_later     = 7
_pool_size_replacing = 8
_pool_size_reaching  = 9
_pool_size_failover  = 10
_pool_size_disposed  = 11
_pool_size_disposing = 12
_pool_size_queue     = 13
_pool_size_queue_new = 14

# ################################################################################################################################
# ################################################################################################################################

_modes = get_suite_modes([PubSubDBMode.PostgreSQL])

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module', params=_modes)
def pubsub_database(request:'pytest.FixtureRequest') -> 'any_':
    database = start_pubsub_database('generation', request.param)

    try:
        yield database
    finally:
        stop_pubsub_database(database)

# ################################################################################################################################

def _new_server_env(database:'PubSubDatabase', pool_size:'int') -> 'strstrdict':
    """ The variables of a server with a generation file and an engine of its own.
    """
    work_dir = tempfile.mkdtemp(prefix='zato_pubsub_generation_', dir=os.environ['TMPDIR'])

    out = dict(database.env)
    out['Zato_Database_Generation_File'] = os.path.join(work_dir, 'generation')
    out['Zato_Database_Pool_Size'] = str(pool_size)

    return out

# ################################################################################################################################

def _start_server(env:'strstrdict') -> 'SQLPubSubBackend':
    """ Starts the backend of a server, which takes over the database.
    """
    # The backend resolves its engine on first access, which happens here while the variables select the engine
    # that its guard is installed on.
    with pubsub_db_env(env):
        out = SQLPubSubBackend(audit_log=new_test_audit_log())
        out.take_over()
        _ = out.engine

    return out

# ################################################################################################################################

def _restore_previous_generation(database:'PubSubDatabase') -> 'None':
    """ Lowers the generation by one, as a failover to a replica that did not receive the last raise does.
    """
    env = dict(database.env)
    env['Zato_Database_Pool_Size'] = str(_pool_size_failover)

    with pubsub_db_env(env):
        engine = get_database_engine()
        restore_previous_generation(engine)

# ################################################################################################################################

def _read_active(database:'PubSubDatabase') -> 'tuple[int, str]':
    """ Returns the generation and the owner of the active server as the database holds them.
    """
    connection = connect(database)

    try:
        cursor = connection.cursor()
        cursor.execute('select generation, owner from zato_active where id = 1')
        row = cast_('any_', cursor.fetchone())
    finally:
        connection.close()

    out = (row[0], row[1])
    return out

# ################################################################################################################################

def _take_over_as_node(database:'PubSubDatabase', ha_generation:'int', pool_size:'int') -> 'SQLPubSubBackend':
    """ Starts the backend of a server whose active-standby node passed it the given generation,
    with an engine of its own.
    """
    env = _new_server_env(database, pool_size)
    env['Zato_HA_Generation'] = str(ha_generation)

    out = _start_server(env)
    return out

# ################################################################################################################################

def _count_messages(database:'PubSubDatabase') -> 'int':
    """ Counts the messages through a connection of its own, which no generation guard confirms.
    """
    connection = connect(database)

    try:
        cursor = connection.cursor()
        cursor.execute('select count(*) from pubsub_message')
        row = cast_('any_', cursor.fetchone())
    finally:
        connection.close()

    out = row[0]
    return out

# ################################################################################################################################

def _count_deliveries(database:'PubSubDatabase', sub_key:'str') -> 'int':
    """ Counts the delivery rows of a subscriber through a connection of its own, which no generation guard confirms.
    """
    connection = connect(database)

    try:
        cursor = connection.cursor()
        cursor.execute('select count(*) from pubsub_delivery where sub_key = %s', (sub_key,))
        row = cast_('any_', cursor.fetchone())
    finally:
        connection.close()

    out = row[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_replaced_backend_and_cleanup(pubsub_database:'PubSubDatabase') -> 'None':
    """ Once another server raises the generation, the backend of the replaced server rejects every operation,
    its cleanup process deletes nothing, and the cleanup process of the new server deletes as before.
    """
    env = _new_server_env(pubsub_database, _pool_size_replaced)

    with pubsub_db_env(env):

        # The backend takes over the database and records its generation ..
        backend = SQLPubSubBackend(audit_log=new_test_audit_log())
        backend.take_over()

        guard = backend.generation_guard
        assert guard is not None
        assert read_generation_file().generation == guard.generation

        # .. it accepts a subscription and a message that has already expired ..
        backend.subscribe(_sub_key, _topic_name)
        _ = backend.publish(_topic_name, 'expired', expiration=0)

        assert _count_messages(pubsub_database) == 1

        # .. another server raises the generation ..
        other = take_over_as_another_server(pubsub_database.env, _pool_size_replacing)

        other_guard = other.generation_guard
        assert other_guard is not None
        assert other_guard.generation == guard.generation + 1

        # .. so the backend rejects a publication and knows it was replaced ..
        with pytest.raises(PubSubReplaced):
            _ = backend.publish(_topic_name, 'rejected')

        assert backend.is_replaced

        guard.uninstall(backend.engine)

        # .. the cleanup process of the replaced server deletes nothing ..
        cleanup = PubSubCleanup()
        counts = cleanup.run_guarded_sweep()

        assert counts['expired'] == 0, counts
        assert _count_messages(pubsub_database) == 1

        # .. and once the new server records its generation, the cleanup process deletes the expired message.
        write_generation_file(other_guard.generation, other_guard.owner)
        counts = cleanup.run_guarded_sweep()

        assert counts['expired'] == 1, counts
        assert _count_messages(pubsub_database) == 0

    other_guard.uninstall(other.engine)

# ################################################################################################################################

def test_generation_reached_again_by_another_server(pubsub_database:'PubSubDatabase') -> 'None':
    """ After a failover of the database to a replica that did not receive the last raise, another server
    raises the generation to the value of this server, and this server is replaced and writes no row.
    """
    env = _new_server_env(pubsub_database, _pool_size_reached)

    with pubsub_db_env(env):

        # The backend takes over the database and publishes a message ..
        backend = SQLPubSubBackend(audit_log=new_test_audit_log())
        backend.take_over()

        guard = backend.generation_guard
        assert guard is not None

        backend.subscribe(_reached_sub_key, _reached_topic_name)
        _ = backend.publish(_reached_topic_name, 'accepted')

        message_count = _count_messages(pubsub_database)

        # .. the database fails over to a replica that holds the generation before the raise of the backend ..
        _restore_previous_generation(pubsub_database)

        # .. another server raises the generation to the value of the backend ..
        other = take_over_as_another_server(pubsub_database.env, _pool_size_reaching)

        other_guard = other.generation_guard
        assert other_guard is not None
        assert other_guard.generation == guard.generation

        # .. so the backend rejects a publication and knows it was replaced ..
        with pytest.raises(PubSubReplaced):
            _ = backend.publish(_reached_topic_name, 'rejected')

        assert backend.is_replaced

        # .. and no row of the rejected publication is in the database.
        assert _count_messages(pubsub_database) == message_count

        guard.uninstall(backend.engine)

    other_guard.uninstall(other.engine)

# ################################################################################################################################

def test_lower_ha_generation_leaves_the_server_replaced(pubsub_database:'PubSubDatabase') -> 'None':
    """ A server whose node passed it a generation below the stored one is replaced from its start and writes no row,
    while the server of the higher generation keeps writing.
    """
    stored_generation, _ = _read_active(pubsub_database)
    higher_generation = stored_generation + _ha_generation_step

    # The server of the higher generation takes over ..
    current = _take_over_as_node(pubsub_database, higher_generation, _pool_size_current)

    current_guard = current.generation_guard
    assert current_guard is not None
    assert not current.is_replaced
    assert _read_active(pubsub_database) == (higher_generation, current_guard.owner)

    # .. the server of a lower generation starts after it and is replaced from its start ..
    earlier = _take_over_as_node(pubsub_database, higher_generation - 1, _pool_size_lower)

    earlier_guard = earlier.generation_guard
    assert earlier_guard is not None
    assert earlier.is_replaced
    assert _read_active(pubsub_database) == (higher_generation, current_guard.owner)

    with pytest.raises(PubSubReplaced):
        earlier.subscribe(_ha_lower_sub_key, _ha_topic_name)

    # .. and the server of the higher generation keeps writing.
    current.subscribe(_ha_current_sub_key, _ha_topic_name)

    earlier_guard.uninstall(earlier.engine)
    current_guard.uninstall(current.engine)

# ################################################################################################################################

def test_equal_ha_generation_replaces_the_earlier_server(pubsub_database:'PubSubDatabase') -> 'None':
    """ A server whose node passed it the stored generation replaces the earlier server of that generation,
    which writes no row from then on.
    """
    stored_generation, _ = _read_active(pubsub_database)
    generation = stored_generation + _ha_generation_step

    # The earlier server of the generation takes over ..
    earlier = _take_over_as_node(pubsub_database, generation, _pool_size_earlier)

    earlier_guard = earlier.generation_guard
    assert earlier_guard is not None
    assert not earlier.is_replaced

    # .. a later server of the same generation takes over with an owner of its own ..
    later = _take_over_as_node(pubsub_database, generation, _pool_size_later)

    later_guard = later.generation_guard
    assert later_guard is not None
    assert not later.is_replaced
    assert later_guard.owner != earlier_guard.owner
    assert _read_active(pubsub_database) == (generation, later_guard.owner)

    # .. so the earlier server writes no row ..
    with pytest.raises(PubSubReplaced):
        earlier.subscribe(_ha_earlier_sub_key, _ha_topic_name)

    assert earlier.is_replaced

    # .. and the later one does.
    later.subscribe(_ha_later_sub_key, _ha_topic_name)

    earlier_guard.uninstall(earlier.engine)
    later_guard.uninstall(later.engine)

# ################################################################################################################################

def test_replaced_server_after_engine_disposal(pubsub_database:'PubSubDatabase') -> 'None':
    """ Once another server raises the generation and the replaced server disposes of the engine of the Zato database,
    the engine that the replaced server builds next carries the fence of its generation, so an audit insert through it
    is rejected, as are a publication and an acknowledgment of its backend.
    """
    env = _new_server_env(pubsub_database, _pool_size_disposed)

    with pubsub_db_env(env):

        # The backend takes over the database, subscribes and publishes a message ..
        backend = SQLPubSubBackend(audit_log=new_test_audit_log())
        backend.take_over()

        guard = backend.generation_guard
        assert guard is not None

        backend.subscribe(_disposed_sub_key, _disposed_topic_name)
        result = backend.publish(_disposed_topic_name, 'accepted')

        disposed_engine = backend.engine
        message_count = _count_messages(pubsub_database)

        # .. another server raises the generation ..
        other = take_over_as_another_server(pubsub_database.env, _pool_size_disposing)

        other_guard = other.generation_guard
        assert other_guard is not None
        assert other_guard.generation == guard.generation + 1

        # .. the replaced server disposes of its engine, so the next one is built anew ..
        dispose_database_engine()

        new_engine = get_database_engine()
        assert new_engine is not disposed_engine

        # .. an audit insert through the new engine is rejected ..
        with pytest.raises(PubSubReplaced):
            _ = backend.audit_log.insert(AuditSource.PubSub, AuditEvent.Published, _disposed_object_name)

        # .. as are a publication and an acknowledgment of the backend ..
        with pytest.raises(PubSubReplaced):
            _ = backend.publish(_disposed_topic_name, 'rejected')

        with pytest.raises(PubSubReplaced):
            _ = backend.ack_messages(_disposed_sub_key, [result.msg_id])

        assert backend.is_replaced

        # .. and no row of the rejected publication is in the database.
        assert _count_messages(pubsub_database) == message_count

        guard.uninstall(disposed_engine)

    other_guard.uninstall(other.engine)

# ################################################################################################################################

def test_replaced_server_cannot_ack_outgoing_queue(pubsub_database:'PubSubDatabase') -> 'None':
    """ A message of an outgoing connection's queue is acknowledged only with the delivery attempt that the server
    recorded for it, so a message handed out again stays in the queue, and once another server raises
    the generation, the replaced server acknowledges nothing of the queue.
    """
    env = _new_server_env(pubsub_database, _pool_size_queue)
    sub_key = get_outgoing_sub_key(_outgoing_conn_type, _outgoing_conn_id)

    with pubsub_db_env(env):

        # The backend takes over the database and two messages enter the queue of the connection ..
        backend = SQLPubSubBackend(audit_log=new_test_audit_log())
        backend.take_over()

        guard = backend.generation_guard
        assert guard is not None

        backend.subscribe(sub_key, _outgoing_topic_name)
        _ = backend.publish(_outgoing_topic_name, 'first')
        _ = backend.publish(_outgoing_topic_name, 'second')

        # .. the server hands both of them out, recording an attempt of each ..
        messages = backend.fetch_messages(sub_key)
        assert len(messages) == 2, messages

        first, second = messages

        assert backend.record_attempt(first)
        assert backend.record_attempt(second)

        # .. the first one is handed out again, so the acknowledgment of the earlier attempt is rejected ..
        handed_out_again = dict(first)
        assert backend.record_attempt(handed_out_again)
        assert handed_out_again['delivery_attempt'] == first['delivery_attempt'] + 1

        with pytest.raises(PubSubAckConflict):
            _ = backend.ack_delivered(sub_key, first['msg_id'], first['delivery_attempt'])

        assert _count_deliveries(pubsub_database, sub_key) == 2

        # .. while the acknowledgment of the current attempt removes the message ..
        fully_delivered_count = backend.ack_delivered(
            sub_key, handed_out_again['msg_id'], handed_out_again['delivery_attempt'])

        assert fully_delivered_count == 1
        assert _count_deliveries(pubsub_database, sub_key) == 1

        # .. another server raises the generation ..
        other = take_over_as_another_server(pubsub_database.env, _pool_size_queue_new)

        other_guard = other.generation_guard
        assert other_guard is not None
        assert other_guard.generation == guard.generation + 1

        # .. so the replaced server cannot acknowledge the second message ..
        with pytest.raises(PubSubReplaced):
            _ = backend.ack_delivered(sub_key, second['msg_id'], second['delivery_attempt'])

        assert backend.is_replaced

        # .. which stays in the queue for the server that replaced it.
        assert _count_deliveries(pubsub_database, sub_key) == 1

        guard.uninstall(backend.engine)

    other_guard.uninstall(other.engine)

# ################################################################################################################################
# ################################################################################################################################
