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
from zato.common.common_db.config import check_common_db_config, common_db_config, CommonDBConfigError, \
    get_common_db_source, get_common_engine, ModuleCtx
from zato.common.common_db.store import SharedObjectStore
from zato.common.crypto.api import CryptoManager
from zato.common.db_env import dispose_env_engine
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.config import get_pubsub_engine, pubsub_db_config
from zato.common.pubsub.sql.generation import PubSubReplaced
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

_pubsub_prefix = 'Zato_PubSub_DB_'
_common_prefix = ModuleCtx.Env_Prefix

_modes = get_suite_modes([PubSubDBMode.PostgreSQL, PubSubDBMode.PostgreSQL_TLS])

# ################################################################################################################################
# ################################################################################################################################

def _new_name() -> 'str':
    out = 'test.object.' + CryptoManager.generate_hex_string()
    return out

# ################################################################################################################################

def _clear_database_variables(monkeypatch:'pytest.MonkeyPatch') -> 'None':
    """ Removes every variable that selects the pub/sub or the common database, for the duration of one test.
    """
    for name in list(os.environ):
        if name.startswith(_pubsub_prefix):
            monkeypatch.delenv(name)
        elif name.startswith(_common_prefix):
            monkeypatch.delenv(name)

# ################################################################################################################################

def _set_variables(monkeypatch:'pytest.MonkeyPatch', env:'strstrdict') -> 'None':
    for name, value in env.items():
        monkeypatch.setenv(name, value)

# ################################################################################################################################

def _as_common_env(env:'strstrdict') -> 'strstrdict':
    """ Returns the variables of a pub/sub database renamed to the variables of the common database.
    """
    out:'strstrdict' = {}

    for name, value in env.items():
        suffix = name.removeprefix(_pubsub_prefix)
        common_name = _common_prefix + suffix
        out[common_name] = value

    return out

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

def test_resolution_order(monkeypatch:'pytest.MonkeyPatch', tmp_path:'pathlib.Path') -> 'None':
    """ The variables of the common database come first, then those of pub/sub, then the default SQLite file.
    """
    _clear_database_variables(monkeypatch)
    assert get_common_db_source() == ModuleCtx.Source_Default

    monkeypatch.setenv('Zato_PubSub_DB_Path', _new_sqlite_path(tmp_path, 'pubsub.db'))
    assert get_common_db_source() == ModuleCtx.Source_PubSub

    monkeypatch.setenv('Zato_Common_DB_Path', _new_sqlite_path(tmp_path, 'common.db'))
    assert get_common_db_source() == ModuleCtx.Source_Common

    monkeypatch.delenv('Zato_Common_DB_Path')
    monkeypatch.setenv('Zato_Common_DB_Type', 'sqlite')
    assert get_common_db_source() == ModuleCtx.Source_Common

# ################################################################################################################################

def test_sqlite_file(monkeypatch:'pytest.MonkeyPatch', tmp_path:'pathlib.Path') -> 'None':
    """ A SQLite file of its own holds the shared objects.
    """
    _clear_database_variables(monkeypatch)

    db_path = _new_sqlite_path(tmp_path, 'common.db')
    monkeypatch.setenv('Zato_Common_DB_Path', db_path)

    store = SharedObjectStore()
    _check_compare_and_set(store)

    assert str(store.engine.url) == f'sqlite:///{db_path}'

# ################################################################################################################################

def test_sqlite_pubsub_file(monkeypatch:'pytest.MonkeyPatch', tmp_path:'pathlib.Path') -> 'None':
    """ With only the pub/sub variables set, the shared objects are in the pub/sub file, on the engine of pub/sub.
    """
    _clear_database_variables(monkeypatch)
    monkeypatch.setenv('Zato_PubSub_DB_Path', _new_sqlite_path(tmp_path, 'pubsub.db'))

    store = SharedObjectStore()
    _check_compare_and_set(store)

    assert store.engine is get_pubsub_engine()

# ################################################################################################################################

def test_refused_configuration(monkeypatch:'pytest.MonkeyPatch') -> 'None':
    """ A common database on PostgreSQL other than the pub/sub database is refused, and the error names both.
    """
    _clear_database_variables(monkeypatch)

    pubsub_env = {
        'Zato_PubSub_DB_Type': 'postgresql',
        'Zato_PubSub_DB_Host': 'pubsub.example.com',
        'Zato_PubSub_DB_Port': '5432',
        'Zato_PubSub_DB_Name': 'zato_pubsub',
    }

    _set_variables(monkeypatch, pubsub_env)

    # Only the pub/sub variables select the database, which is therefore one and the same ..
    check_common_db_config()

    # .. as it is when the variables of the common database name the same database ..
    common_env = _as_common_env(pubsub_env)
    _set_variables(monkeypatch, common_env)
    check_common_db_config()

    # .. while another database is refused.
    monkeypatch.setenv('Zato_Common_DB_Name', 'zato_common')

    with pytest.raises(CommonDBConfigError) as error_info:
        check_common_db_config()

    message = str(error_info.value)
    assert 'pubsub.example.com:5432/zato_common' in message
    assert 'pubsub.example.com:5432/zato_pubsub' in message

    # A common database on PostgreSQL next to pub/sub on SQLite is refused as well.
    _clear_database_variables(monkeypatch)
    _set_variables(monkeypatch, common_env)

    with pytest.raises(CommonDBConfigError):
        check_common_db_config()

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
        cursor.execute('update pubsub_active set generation = generation + 1 where id = 1 returning generation')
        row = cast_('any_', cursor.fetchone())
        connection.commit()
    finally:
        connection.close()

    out = row[0]
    return out

# ################################################################################################################################

def test_postgresql(monkeypatch:'pytest.MonkeyPatch', tmp_path:'pathlib.Path', pubsub_database:'PubSubDatabase') -> 'None':
    """ On PostgreSQL, the shared objects are in the pub/sub database, two engines contend for one object
    with one of them succeeding, and the writes of a replaced server are rejected on both engines.
    """
    _clear_database_variables(monkeypatch)
    _set_variables(monkeypatch, pubsub_database.env)

    monkeypatch.setenv('Zato_PubSub_Generation_File', os.path.join(tmp_path, 'generation'))

    # The store on the engine of pub/sub ..
    pubsub_store = SharedObjectStore()
    _check_compare_and_set(pubsub_store)

    assert pubsub_store.engine is get_pubsub_engine()

    # .. and a store on an engine of its own, which the variables of the common database select ..
    common_env = _as_common_env(pubsub_database.env)
    _set_variables(monkeypatch, common_env)

    check_common_db_config()

    common_store = SharedObjectStore()
    assert common_store.engine is get_common_engine()
    assert common_store.engine is not pubsub_store.engine

    # .. both of them read the same version of an object ..
    name = _new_name()
    assert pubsub_store.compare_and_set(_object_type, name, {'slot': 'first'}, None)

    pubsub_item = cast_('any_', pubsub_store.get(_object_type, name))
    common_item = cast_('any_', common_store.get(_object_type, name))

    assert pubsub_item.version == common_item.version

    # .. and of their two writes against it, only the first one takes place ..
    assert common_store.compare_and_set(_object_type, name, {'slot': 'second'}, common_item.version)
    assert not pubsub_store.compare_and_set(_object_type, name, {'slot': 'third'}, pubsub_item.version)

    stored = cast_('any_', pubsub_store.get(_object_type, name))
    assert stored.data == {'slot': 'second'}

    # .. this server takes over the database and both stores confirm its generation ..
    backend = SQLPubSubBackend()
    backend.take_over()

    guard = cast_('any_', backend.generation_guard)

    pubsub_store.install_generation_guard(guard, backend.engine)
    common_store.install_generation_guard(guard, backend.engine)

    try:
        assert common_store.compare_and_set(_object_type, name, {'slot': 'fourth'}, stored.version)

        # .. until another server raises the generation, after which neither store writes anything.
        _ = _raise_generation(pubsub_database)

        with pytest.raises(PubSubReplaced):
            _ = common_store.compare_and_set(_object_type, name, {'slot': 'fifth'}, stored.version + 1)

        with pytest.raises(PubSubReplaced):
            _ = pubsub_store.compare_and_set(_object_type, name, {'slot': 'sixth'}, stored.version + 1)

    finally:
        guard.uninstall(backend.engine)
        guard.uninstall(common_store.engine)

        dispose_env_engine(common_db_config)
        dispose_env_engine(pubsub_db_config)

# ################################################################################################################################
# ################################################################################################################################
