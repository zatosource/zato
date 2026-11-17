# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import pathlib

# pytest
import pytest

# Zato
from zato.common.common_db.store import SharedObjectStore
from zato.common.crypto.api import CryptoManager
from zato.common.db_env.database import database_config, dispose_database_engine, get_database_engine
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.replaced import PubSubReplaced
from zato.common.test.pubsub_database import connect, get_suite_modes, PubSubDBMode, \
    start_pubsub_database, stop_pubsub_database
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

_object_type = 'test.shared.object'

_env_prefix = database_config.env_prefix

_modes = get_suite_modes([PubSubDBMode.PostgreSQL, PubSubDBMode.PostgreSQL_TLS])

# ################################################################################################################################
# ################################################################################################################################

def _new_name() -> 'str':
    out = 'test.object.' + CryptoManager.generate_hex_string()
    return out

# ################################################################################################################################

def _clear_database_variables(monkeypatch:'pytest.MonkeyPatch') -> 'None':
    """ Removes every variable that selects the Zato database, for the duration of one test.
    """
    for name in list(os.environ):
        if name.startswith(_env_prefix):
            monkeypatch.delenv(name)

# ################################################################################################################################

def _set_variables(monkeypatch:'pytest.MonkeyPatch', env:'strstrdict') -> 'None':
    for name, value in env.items():
        monkeypatch.setenv(name, value)

# ################################################################################################################################

def _new_sqlite_path(work_dir:'pathlib.Path', file_name:'str') -> 'str':
    out = os.path.join(work_dir, file_name)
    return out

# ################################################################################################################################

def _check_compare_and_set(store:'SharedObjectStore') -> 'None':
    """ Runs one object through its creation, updates, a stale update, listing and deletion.
    """
    name = _new_name()

    # The object does not exist yet ..
    assert store.get(_object_type, name) is None

    # .. it is created once, and a second creation does not take place ..
    assert store.compare_and_set(_object_type, name, {'count': 1}, None)
    assert not store.compare_and_set(_object_type, name, {'count': 100}, None)

    item = cast_('any_', store.get(_object_type, name))
    assert item.data == {'count': 1}
    assert item.version == 1

    # .. an update against the current version takes place and raises the version ..
    assert store.compare_and_set(_object_type, name, {'count': 2}, item.version)

    updated = cast_('any_', store.get(_object_type, name))
    assert updated.data == {'count': 2}
    assert updated.version == 2

    # .. an update against the version read before does not ..
    assert not store.compare_and_set(_object_type, name, {'count': 3}, item.version)

    # .. the object is listed under its type ..
    names:'strlist' = []

    for listed in store.list(_object_type):
        names.append(listed.name)

    assert name in names

    # .. and it is deleted once.
    assert store.delete(_object_type, name)
    assert not store.delete(_object_type, name)
    assert store.get(_object_type, name) is None

# ################################################################################################################################
# ################################################################################################################################

def test_sqlite_file(monkeypatch:'pytest.MonkeyPatch', tmp_path:'pathlib.Path') -> 'None':
    """ The shared objects are in the SQLite file of the Zato database, on the engine of the Zato database.
    """
    _clear_database_variables(monkeypatch)

    db_path = _new_sqlite_path(tmp_path, 'zato.db')
    monkeypatch.setenv('Zato_Database_Path', db_path)

    store = SharedObjectStore()

    try:
        _check_compare_and_set(store)

        assert store.engine is get_database_engine()
        assert str(store.engine.url) == f'sqlite:///{db_path}'

    finally:
        dispose_database_engine()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module', params=_modes)
def pubsub_database(request:'pytest.FixtureRequest') -> 'any_':
    database = start_pubsub_database('common-db', request.param)

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
        cursor.execute('update zato_active set generation = generation + 1 where id = 1 returning generation')
        row = cast_('any_', cursor.fetchone())
        connection.commit()
    finally:
        connection.close()

    out = row[0]
    return out

# ################################################################################################################################

def test_postgresql(monkeypatch:'pytest.MonkeyPatch', tmp_path:'pathlib.Path', pubsub_database:'PubSubDatabase') -> 'None':
    """ On PostgreSQL, the shared objects are in the Zato database, two stores contend for one object
    with one of them succeeding, and the writes of a replaced server are rejected.
    """
    _clear_database_variables(monkeypatch)
    _set_variables(monkeypatch, pubsub_database.env)

    monkeypatch.setenv('Zato_Database_Generation_File', os.path.join(tmp_path, 'generation'))

    # Two stores on the engine of the Zato database ..
    first_store = SharedObjectStore()
    second_store = SharedObjectStore()

    _check_compare_and_set(first_store)

    assert first_store.engine is get_database_engine()
    assert second_store.engine is first_store.engine

    # .. both of them read the same version of an object ..
    name = _new_name()
    assert first_store.compare_and_set(_object_type, name, {'slot': 'first'}, None)

    first_item = cast_('any_', first_store.get(_object_type, name))
    second_item = cast_('any_', second_store.get(_object_type, name))

    assert first_item.version == second_item.version

    # .. and of their two writes against it, only the first one takes place ..
    assert second_store.compare_and_set(_object_type, name, {'slot': 'second'}, second_item.version)
    assert not first_store.compare_and_set(_object_type, name, {'slot': 'third'}, first_item.version)

    stored = cast_('any_', first_store.get(_object_type, name))
    assert stored.data == {'slot': 'second'}

    # .. this server takes over the database, and the store, on the same engine, confirms its generation ..
    backend = SQLPubSubBackend()
    backend.take_over()

    guard = cast_('any_', backend.generation_guard)
    assert backend.engine is first_store.engine

    try:
        assert first_store.compare_and_set(_object_type, name, {'slot': 'fourth'}, stored.version)

        # .. until another server raises the generation, after which the store writes nothing.
        _ = _raise_generation(pubsub_database)

        with pytest.raises(PubSubReplaced):
            _ = first_store.compare_and_set(_object_type, name, {'slot': 'fifth'}, stored.version + 1)

    finally:
        guard.uninstall(backend.engine)
        dispose_database_engine()

# ################################################################################################################################
# ################################################################################################################################
