# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The settings of a PostgreSQL server under which a test runs are built at runtime out of the data
# of zato.common.test.sql_conformance.forbidden, so that no source of the repository spells out a relaxed setting.

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import text

# Zato
from zato.common.db_env.common import Type_PostgreSQL
from zato.common.db_env.connection import build_connect_args_from_values, build_engine_url_from_values, \
    DatabaseDurabilityError, Provider_Failover_Roles
from zato.common.db_env.database import dispose_database_engine, get_database_engine, get_database_values
from zato.common.db_env.engine import new_zato_engine
from zato.common.test.pubsub_database import connect, pubsub_db_env, PubSubDBMode, start_pubsub_database, \
    stop_pubsub_database
from zato.common.test.pubsub_replication import start_replicated_database, stop_replicated_database
from zato.common.test.sql_conformance.forbidden import get_server_refusal_arguments, ModuleCtx as ForbiddenModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy.engine import Engine
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import strlist

    Engine = Engine
    Iterator = Iterator
    PubSubDatabase = PubSubDatabase

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The setting of the commit level of a session
    Commit_Setting = 'synchronous_commit'

    # The commit level that a session runs with unless the server configures a stronger one
    Level_On = 'on'

    # A commit level stronger than the local flush, which a session keeps
    Level_Remote_Apply = 'remote_apply'

# ################################################################################################################################
# ################################################################################################################################

def _get_relaxed_levels() -> 'strlist':
    """ Returns the commit levels under which a commit may return before its record is flushed.
    """
    for item in ForbiddenModuleCtx.PostgreSQL_Settings:
        if item.name == ModuleCtx.Commit_Setting:
            out = list(item.values)
            break
    else:
        raise Exception(f'No forbidden values of `{ModuleCtx.Commit_Setting}`')

    return out

# ################################################################################################################################

def _set_server_level(database:'PubSubDatabase', level:'str') -> 'None':
    """ Configures the commit level of the server, which each new session starts with.
    """
    connection = connect(database, is_admin=True)
    connection.autocommit = True

    cursor = connection.cursor()
    cursor.execute(f"alter system set {ModuleCtx.Commit_Setting} = '{level}'")
    cursor.execute('select pg_reload_conf()')

    connection.close()

# ################################################################################################################################

def _new_configuration_engine() -> 'Engine':
    """ Returns an engine of a database of Zato that the environment does not configure, on the same server.
    """
    values = get_database_values()

    engine_url = build_engine_url_from_values(values, Type_PostgreSQL)
    connect_args = build_connect_args_from_values(values, Type_PostgreSQL)

    out = new_zato_engine(engine_url, connect_args=connect_args)
    return out

# ################################################################################################################################

def _get_session_level(engine:'Engine') -> 'str':
    with engine.connect() as connection:
        out = connection.execute(text(f'show {ModuleCtx.Commit_Setting}')).scalar()
    return out

# ################################################################################################################################

def _get_levels() -> 'tuple[str, str]':
    """ Returns the commit level of a new session of the Zato database and of a new session of a database of Zato
    that the environment does not configure.
    """
    dispose_database_engine()
    zato_level = _get_session_level(get_database_engine())
    dispose_database_engine()

    configuration_engine = _new_configuration_engine()

    try:
        configuration_level = _get_session_level(configuration_engine)
    finally:
        configuration_engine.dispose()

    return zato_level, configuration_level

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def database() -> 'Iterator[PubSubDatabase]':
    out = start_pubsub_database('durability-session', PubSubDBMode.PostgreSQL)

    try:
        with pubsub_db_env(out.env):
            yield out
    finally:
        dispose_database_engine()
        stop_pubsub_database(out)

# ################################################################################################################################
# ################################################################################################################################

def test_session_level_on_by_default(database:'PubSubDatabase') -> 'None':
    _set_server_level(database, ModuleCtx.Level_On)
    assert _get_levels() == (ModuleCtx.Level_On, ModuleCtx.Level_On)

# ################################################################################################################################

def test_session_level_on_under_relaxed_server(database:'PubSubDatabase') -> 'None':
    """ A server configured with a level under which a commit returns before its flush still has each session of Zato
    flush its commits.
    """
    try:
        for level in _get_relaxed_levels():
            _set_server_level(database, level)
            assert _get_levels() == (ModuleCtx.Level_On, ModuleCtx.Level_On), level
    finally:
        _set_server_level(database, ModuleCtx.Level_On)

# ################################################################################################################################

def test_session_keeps_stronger_level(database:'PubSubDatabase') -> 'None':
    """ A server configured with a level stronger than the local flush keeps it in each session of Zato.
    """
    _set_server_level(database, ModuleCtx.Level_Remote_Apply)

    try:
        assert _get_levels() == (ModuleCtx.Level_Remote_Apply, ModuleCtx.Level_Remote_Apply)
    finally:
        _set_server_level(database, ModuleCtx.Level_On)

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('setting', get_server_refusal_arguments())
def test_server_refused(setting:'str') -> 'None':
    """ A server that does not flush its log or does not write full pages after a checkpoint is refused at the first
    connection of an engine of Zato, with an error that names the setting.
    """
    name, _, _ = setting.partition('=')
    label = 'durability-refused-' + name.replace('_', '-')

    database = start_pubsub_database(label, PubSubDBMode.PostgreSQL, extra_settings=[setting])

    try:
        with pubsub_db_env(database.env):

            with pytest.raises(DatabaseDurabilityError, match=name):
                _ = get_database_engine()

            configuration_engine = _new_configuration_engine()

            try:
                with pytest.raises(DatabaseDurabilityError, match=name):
                    _ = _get_session_level(configuration_engine)
            finally:
                configuration_engine.dispose()
    finally:
        dispose_database_engine()
        stop_pubsub_database(database)

# ################################################################################################################################

def test_asynchronous_standby_refused() -> 'None':
    """ A primary with a streaming standby that is not synchronous is refused at the first connection of an engine
    of Zato, with an error that names synchronous_standby_names.
    """
    replicated = start_replicated_database('durability-async', PubSubDBMode.PostgreSQL, is_sync=False)

    try:
        with pubsub_db_env(replicated.env):
            with pytest.raises(DatabaseDurabilityError, match=ForbiddenModuleCtx.Synchronous_Standby_Names):
                _ = get_database_engine()
    finally:
        dispose_database_engine()
        stop_replicated_database(replicated)

# ################################################################################################################################

@pytest.mark.parametrize('role', Provider_Failover_Roles)
def test_asynchronous_standby_of_provider_failover_accepted(role:'str') -> 'None':
    """ A primary with a streaming standby that is not synchronous is accepted on a managed service whose provider
    performs the failover, which the role that the provider creates on each of its servers identifies.
    """
    replicated = start_replicated_database('durability-provider', PubSubDBMode.PostgreSQL, is_sync=False)

    try:
        connection = connect(replicated.primary, is_admin=True)
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(f'create role {role}')
        connection.close()

        with pubsub_db_env(replicated.env):
            engine = get_database_engine()
            assert _get_session_level(engine) == ModuleCtx.Level_On
    finally:
        dispose_database_engine()
        stop_replicated_database(replicated)

# ################################################################################################################################

def test_synchronous_standby_accepted() -> 'None':
    replicated = start_replicated_database('durability-sync', PubSubDBMode.PostgreSQL, is_sync=True)

    try:
        with pubsub_db_env(replicated.env):
            engine = get_database_engine()
            assert _get_session_level(engine) == ModuleCtx.Level_On
    finally:
        dispose_database_engine()
        stop_replicated_database(replicated)

# ################################################################################################################################

def test_primary_without_standbys_accepted(database:'PubSubDatabase') -> 'None':
    engine = get_database_engine()
    assert _get_session_level(engine) == ModuleCtx.Level_On

# ################################################################################################################################
# ################################################################################################################################
