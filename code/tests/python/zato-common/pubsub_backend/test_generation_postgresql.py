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
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.cleanup import PubSubCleanup
from zato.common.pubsub.sql.generation import read_generation_file, write_generation_file
from zato.common.pubsub.sql.replaced import PubSubReplaced
from zato.common.test.pubsub_database import connect, get_suite_modes, pubsub_db_env, PubSubDBMode, \
    start_pubsub_database, stop_pubsub_database
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_topic_name = 'generation.guard'
_sub_key = 'zpsk.generation.guard'

# The topic and the subscription of the server whose generation another server reaches again
_reached_topic_name = 'generation.reached'
_reached_sub_key = 'zpsk.generation.reached'

# The owner that another server writes when it raises the generation
_other_owner = 'other.server'

# The topic of the servers of active-standby nodes and the subscription of each server
_ha_topic_name = 'generation.ha'
_ha_current_sub_key = 'zpsk.generation.ha.current'
_ha_lower_sub_key = 'zpsk.generation.ha.lower'
_ha_earlier_sub_key = 'zpsk.generation.ha.earlier'
_ha_later_sub_key = 'zpsk.generation.ha.later'

# How far above the stored generation the active-standby nodes of a test begin
_ha_generation_step = 10

# The pool sizes that give each server of these tests an engine of its own, since engines are cached by their settings
# and the guard of a cleanup process remains on the engine that it confirms the generation through
_pool_size_replaced = 2
_pool_size_reached  = 3
_pool_size_current  = 4
_pool_size_lower    = 5
_pool_size_earlier  = 6
_pool_size_later    = 7

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

def _raise_generation(database:'PubSubDatabase') -> 'int':
    """ Raises the generation and writes the owner the way the startup of another server does
    and returns the new value.
    """
    connection = connect(database)

    try:
        cursor = connection.cursor()
        query = 'update pubsub_active set generation = generation + 1, owner = %s where id = 1 returning generation'
        cursor.execute(query, (_other_owner,))
        row = cast_('any_', cursor.fetchone())
        connection.commit()
    finally:
        connection.close()

    out = row[0]
    return out

# ################################################################################################################################

def _restore_previous_generation(database:'PubSubDatabase') -> 'None':
    """ Lowers the generation by one, as a failover to a replica that did not receive the last raise does.
    """
    connection = connect(database)

    try:
        cursor = connection.cursor()
        cursor.execute('update pubsub_active set generation = generation - 1 where id = 1')
        connection.commit()
    finally:
        connection.close()

# ################################################################################################################################

def _read_active(database:'PubSubDatabase') -> 'tuple[int, str]':
    """ Returns the generation and the owner of the active server as the database holds them.
    """
    connection = connect(database)

    try:
        cursor = connection.cursor()
        cursor.execute('select generation, owner from pubsub_active where id = 1')
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
    work_dir = tempfile.mkdtemp(prefix='zato_pubsub_generation_', dir=os.environ['TMPDIR'])

    env = dict(database.env)
    env['Zato_PubSub_Generation_File'] = os.path.join(work_dir, 'generation')
    env['Zato_HA_Generation'] = str(ha_generation)
    env['Zato_PubSub_DB_Pool_Size'] = str(pool_size)

    # The backend resolves its engine on first access, which happens here while the variables select the engine
    # that its guard is installed on.
    with pubsub_db_env(env):
        out = SQLPubSubBackend()
        out.take_over()
        _ = out.engine

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
# ################################################################################################################################

def test_replaced_backend_and_cleanup(pubsub_database:'PubSubDatabase') -> 'None':
    """ Once another server raises the generation, the backend of the replaced server rejects every operation,
    its cleanup process deletes nothing, and the cleanup process of the new server deletes as before.
    """
    work_dir = tempfile.mkdtemp(prefix='zato_pubsub_generation_', dir=os.environ['TMPDIR'])

    env = dict(pubsub_database.env)
    env['Zato_PubSub_Generation_File'] = os.path.join(work_dir, 'generation')
    env['Zato_PubSub_DB_Pool_Size'] = str(_pool_size_replaced)

    with pubsub_db_env(env):

        # The backend takes over the database and records its generation ..
        backend = SQLPubSubBackend()
        backend.take_over()

        guard = backend.generation_guard
        assert guard is not None
        assert read_generation_file().generation == guard.generation

        # .. it accepts a subscription and a message that has already expired ..
        backend.subscribe(_sub_key, _topic_name)
        _ = backend.publish(_topic_name, 'expired', expiration=0)

        assert _count_messages(pubsub_database) == 1

        # .. another server raises the generation ..
        new_generation = _raise_generation(pubsub_database)
        assert new_generation == guard.generation + 1

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
        write_generation_file(new_generation, _other_owner)
        counts = cleanup.run_guarded_sweep()

        assert counts['expired'] == 1, counts
        assert _count_messages(pubsub_database) == 0

# ################################################################################################################################

def test_generation_reached_again_by_another_server(pubsub_database:'PubSubDatabase') -> 'None':
    """ After a failover of the database to a replica that did not receive the last raise, another server
    raises the generation to the value of this server, and this server is replaced and writes no row.
    """
    work_dir = tempfile.mkdtemp(prefix='zato_pubsub_generation_', dir=os.environ['TMPDIR'])

    env = dict(pubsub_database.env)
    env['Zato_PubSub_Generation_File'] = os.path.join(work_dir, 'generation')
    env['Zato_PubSub_DB_Pool_Size'] = str(_pool_size_reached)

    with pubsub_db_env(env):

        # The backend takes over the database and publishes a message ..
        backend = SQLPubSubBackend()
        backend.take_over()

        guard = backend.generation_guard
        assert guard is not None

        backend.subscribe(_reached_sub_key, _reached_topic_name)
        _ = backend.publish(_reached_topic_name, 'accepted')

        message_count = _count_messages(pubsub_database)

        # .. the database fails over to a replica that holds the generation before the raise of the backend ..
        _restore_previous_generation(pubsub_database)

        # .. another server raises the generation to the value of the backend ..
        new_generation = _raise_generation(pubsub_database)
        assert new_generation == guard.generation

        # .. so the backend rejects a publication and knows it was replaced ..
        with pytest.raises(PubSubReplaced):
            _ = backend.publish(_reached_topic_name, 'rejected')

        assert backend.is_replaced

        # .. and no row of the rejected publication is in the database.
        assert _count_messages(pubsub_database) == message_count

        guard.uninstall(backend.engine)

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
# ################################################################################################################################
