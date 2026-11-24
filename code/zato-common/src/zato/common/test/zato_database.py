# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Zato databases of individual tests. A test process starts one PostgreSQL server on first use, in the mode
# of the session, and each test receives a database of its own on that server, which is dropped after the test.

# stdlib
import atexit
from contextlib import contextmanager

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.db_env.database import dispose_database_engine, get_database_engine
from zato.common.test.pubsub_database import connect, get_db_mode, ModuleCtx as DatabaseModuleCtx, pubsub_db_env, \
    PubSubDatabase, start_pubsub_database, stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Iterator
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import strstrdict

    Engine = Engine
    Iterator = Iterator

    enginegen = Iterator[Engine]
    strstrdictgen = Iterator[strstrdict]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The label of the PostgreSQL server of the tests of one process
    Server_Label = 'test-databases'

    # The prefix of the name of the database of each test
    Database_Name_Prefix = 'zato_test_'

    # The environment variable with the name of the Zato database
    Env_Name = 'Zato_Database_Name'

# ################################################################################################################################
# ################################################################################################################################

class _ServerState:
    database: 'PubSubDatabase | None' = None

_server_state = _ServerState()

# ################################################################################################################################
# ################################################################################################################################

def get_test_server() -> 'PubSubDatabase':
    """ Returns the PostgreSQL server of the tests of this process, starting it on first use.
    The server is removed when the process exits.
    """
    if database := _server_state.database:
        return database

    mode = get_db_mode()

    out = start_pubsub_database(ModuleCtx.Server_Label, mode)
    _ = atexit.register(stop_pubsub_database, out)

    _server_state.database = out
    return out

# ################################################################################################################################

def _run_admin_statement(database:'PubSubDatabase', statement:'str') -> 'None':
    """ Runs a statement outside of a transaction, as the superuser of the server.
    """
    connection = connect(database, is_admin=True)
    connection.autocommit = True

    try:
        cursor = connection.cursor()
        _ = cursor.execute(statement)
    finally:
        connection.close()

# ################################################################################################################################

def create_test_database() -> 'strstrdict':
    """ Creates an empty database on the PostgreSQL server of this process, owned by the role of the tests,
    and returns the Zato_Database_* variables that select it.
    """
    database = get_test_server()

    suffix = CryptoManager.generate_hex_string()
    db_name = f'{ModuleCtx.Database_Name_Prefix}{suffix}'

    _run_admin_statement(database, f'create database {db_name} owner {DatabaseModuleCtx.Username}')

    out = dict(database.env)
    out[ModuleCtx.Env_Name] = db_name

    return out

# ################################################################################################################################

def drop_test_database(env:'strstrdict') -> 'None':
    """ Drops a database that create_test_database created, together with everything in it.
    """
    database = get_test_server()
    db_name = env[ModuleCtx.Env_Name]

    _run_admin_statement(database, f'drop database {db_name} with (force)')

# ################################################################################################################################

@contextmanager
def isolated_database_env() -> 'strstrdictgen':
    """ Points the Zato_Database_* variables at a new database for the duration of a block and yields them,
    then drops the database.
    """
    env = create_test_database()

    try:
        with pubsub_db_env(env):
            yield env
    finally:
        drop_test_database(env)

# ################################################################################################################################

@contextmanager
def zato_database_engine() -> 'enginegen':
    """ Points the Zato database at a new database and yields its engine from the engine factory,
    with the settings, the schemas and the hooks that every server process uses, then disposes of the engine
    and drops the database.
    """
    with isolated_database_env():
        try:
            yield get_database_engine()
        finally:
            dispose_database_engine()

# ################################################################################################################################
# ################################################################################################################################
