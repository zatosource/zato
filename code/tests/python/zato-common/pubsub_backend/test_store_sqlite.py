# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# SQLAlchemy
from sqlalchemy import inspect, text
from sqlalchemy.pool import QueuePool

# Zato
from common import pubsub_path_env
from zato.common.defaults import default_env_base_dir
from zato.common.db_env.database import database_config, get_database_engine, get_database_sqlite_path
from zato.common.db_env.database_env import DatabaseEnv

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pytest import MonkeyPatch
    from zato.common.typing_ import strset

    # Dummy assignments to satisfy type checkers
    MonkeyPatch = MonkeyPatch
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

def _get_expected_tables() -> 'strset':
    """ Returns the names of the tables of every schema of the Zato database, all of which the engine creates in one file,
    next to the tables that SQLite itself creates for the full-text search of the audit log.
    """
    out:'strset' = set()

    for metadata in database_config.metadata_tuple:
        for table_name in metadata.tables:
            out.add(table_name)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_default_path(monkeypatch:'MonkeyPatch') -> 'None':
    """ Without the environment variable, the store is the default file under the environment directory.
    """
    monkeypatch.delenv(DatabaseEnv.Env_Path, raising=False)

    db_path = get_database_sqlite_path()
    expected_path = os.path.join(default_env_base_dir, DatabaseEnv.File_Name)

    assert db_path == expected_path, f'Expected `{expected_path}`, got `{db_path}`'

# ################################################################################################################################

def test_path_from_environment(tmp_path:'os.PathLike') -> 'None':
    """ The environment variable selects the SQLite file and its schema.
    """
    db_path = os.path.join(str(tmp_path), 'store', 'pubsub-custom.db')

    with pubsub_path_env(db_path):
        resolved_path = get_database_sqlite_path()
        assert resolved_path == db_path, f'Expected `{db_path}`, got `{resolved_path}`'

        engine = get_database_engine()

        assert engine.dialect.name == 'sqlite', f'Expected sqlite, got `{engine.dialect.name}`'
        assert engine.url.database == db_path, f'Expected `{db_path}`, got `{engine.url.database}`'
        assert isinstance(engine.pool, QueuePool), f'Expected QueuePool, got `{engine.pool.__class__.__name__}`'

        with engine.connect() as connection:
            result = connection.execute(text('pragma journal_mode'))
            journal_mode = result.scalar()

        assert journal_mode == 'wal', f'Expected wal, got `{journal_mode}`'

        inspector = inspect(engine)
        table_names = set(inspector.get_table_names())
        expected_tables = _get_expected_tables()
        missing_tables = expected_tables - table_names

        assert not missing_tables, f'Missing tables {missing_tables}, got {table_names}'

    assert os.path.exists(db_path)

# ################################################################################################################################

def test_engine_follows_path_change(tmp_path:'os.PathLike') -> 'None':
    """ A changed path selects another engine.
    """
    first_path  = os.path.join(str(tmp_path), 'pubsub-first.db')
    second_path = os.path.join(str(tmp_path), 'pubsub-second.db')

    with pubsub_path_env(first_path):
        first_engine = get_database_engine()

    with pubsub_path_env(second_path):
        second_engine = get_database_engine()

    assert first_engine.url.database == first_path
    assert second_engine.url.database == second_path
    assert second_engine is not first_engine

# ################################################################################################################################

def test_engine_is_cached_per_path(tmp_path:'os.PathLike') -> 'None':
    """ Repeated calls for one path return the same engine.
    """
    db_path = os.path.join(str(tmp_path), 'pubsub-cached.db')

    with pubsub_path_env(db_path):
        first_engine  = get_database_engine()
        second_engine = get_database_engine()

    assert second_engine is first_engine

# ################################################################################################################################
# ################################################################################################################################
