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
# ################################################################################################################################
