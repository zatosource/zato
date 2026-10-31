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
from zato.common.pubsub.sql.generation import PubSubReplaced, read_generation_file, write_generation_file
from zato.common.test.pubsub_database import connect, pubsub_db_env, PubSubDBMode, start_pubsub_database, \
    stop_pubsub_database
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

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def pubsub_database() -> 'any_':
    database = start_pubsub_database('generation', PubSubDBMode.PostgreSQL)

    try:
        yield database
    finally:
        stop_pubsub_database(database)

# ################################################################################################################################

def _raise_generation(database:'PubSubDatabase') -> 'int':
    """ Raises the generation the way the startup of another server does and returns the new value.
    """
    connection = connect(database)

    try:
        cursor = connection.cursor()
        cursor.execute('update pubsub_active set generation = generation + 1 where id = 1 returning generation')
        row = cast_('any_', cursor.fetchone())
        connection.commit()
    finally:
        connection.close()

    out = row[0]
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

    with pubsub_db_env(env):

        # The backend takes over the database and records its generation ..
        backend = SQLPubSubBackend()
        backend.take_over()

        guard = backend.generation_guard
        assert guard is not None
        assert read_generation_file() == guard.generation

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
        write_generation_file(new_generation)
        counts = cleanup.run_guarded_sweep()

        assert counts['expired'] == 1, counts
        assert _count_messages(pubsub_database) == 0

# ################################################################################################################################
# ################################################################################################################################
