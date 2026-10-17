# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# SQLAlchemy
from sqlalchemy import inspect, text

# Zato
from common import analytics_path_env
from zato.common.analytics.api import analytics_db_file_name, get_analytics_db_path, get_analytics_engine, \
    ModuleCtx as AnalyticsCtx
from zato.common.defaults import default_env_base_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pytest import MonkeyPatch

    # Dummy assignments to satisfy type checkers
    MonkeyPatch = MonkeyPatch

# ################################################################################################################################
# ################################################################################################################################

# The tables the analytics store consists of
_expected_tables = {'usage', 'watermark'}

# ################################################################################################################################
# ################################################################################################################################

def test_default_path(monkeypatch:'MonkeyPatch') -> 'None':
    """ Without the environment variable, the store is the default file under the environment directory.
    """
    monkeypatch.delenv(AnalyticsCtx.Env_Path, raising=False)

    db_path = get_analytics_db_path()
    expected_path = os.path.join(default_env_base_dir, analytics_db_file_name)

    assert db_path == expected_path, f'Expected `{expected_path}`, got `{db_path}`'

# ################################################################################################################################

def test_path_from_environment(tmp_path:'os.PathLike') -> 'None':
    """ The environment variable selects another file, created along with its directory and schema on first use.
    """
    db_path = os.path.join(str(tmp_path), 'store', 'analytics-custom.db')

    with analytics_path_env(db_path):

        # The variable points to the file under test ..
        resolved_path = get_analytics_db_path()
        assert resolved_path == db_path, f'Expected `{db_path}`, got `{resolved_path}`'

        engine = get_analytics_engine()

        # .. the engine is an SQLite one, built for that very file ..
        assert engine.dialect.name == 'sqlite', f'Expected sqlite, got `{engine.dialect.name}`'
        assert engine.url.database == db_path, f'Expected `{db_path}`, got `{engine.url.database}`'

        # .. its connections run in WAL mode ..
        with engine.connect() as connection:
            result = connection.execute(text('pragma journal_mode'))
            journal_mode = result.scalar()

        assert journal_mode == 'wal', f'Expected wal, got `{journal_mode}`'

        # .. and the schema is in place.
        inspector = inspect(engine)
        table_names = set(inspector.get_table_names())

        assert table_names == _expected_tables, f'Expected {_expected_tables}, got {table_names}'

    assert os.path.exists(db_path)

# ################################################################################################################################

def test_engine_follows_path_change(tmp_path:'os.PathLike') -> 'None':
    """ Each call resolves the path again, so a changed variable selects another file at once.
    """
    first_path = os.path.join(str(tmp_path), 'analytics-first.db')
    second_path = os.path.join(str(tmp_path), 'analytics-second.db')

    with analytics_path_env(first_path):
        first_engine = get_analytics_engine()

    with analytics_path_env(second_path):
        second_engine = get_analytics_engine()

    assert first_engine.url.database == first_path
    assert second_engine.url.database == second_path

    # The same file always maps to the same engine
    with analytics_path_env(first_path):
        first_engine_again = get_analytics_engine()

    assert first_engine_again is first_engine

# ################################################################################################################################
# ################################################################################################################################
