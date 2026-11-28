# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The settings of a PostgreSQL server under which a test runs are built at runtime out of the data
# of zato.common.test.sql_conformance.forbidden, so that no source of the repository spells out a relaxed setting.

# stdlib
import time
from typing import NamedTuple

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

# Zato
from zato.common.db_env.connection import DatabaseDurabilityError, DatabaseVersionError, Durability_Level_Relaxed, \
    Durability_Level_Setting, Minimum_Server_Version_Name, PostgreSQL_Connect_Timeout_Seconds, \
    PostgreSQL_Read_Timeout_Seconds, PostgreSQL_Statement_Timeout_Ms, Provider_Failover_Roles
from zato.common.db_env.database import dispose_database_engine, get_database_engine, new_odb_engine
from zato.common.test.pubsub_database import connect, get_database_address, pubsub_db_env, PubSubDBMode, \
    start_pubsub_database, stop_pubsub_database
from zato.common.test.pubsub_replication import start_replicated_database, stop_replicated_database
from zato.common.test.sql_conformance.forbidden import get_server_refusal_arguments, ModuleCtx as ForbiddenModuleCtx

# Toxiproxy
from toxiproxy import Database_Proxy, Stream_Downstream, Toxiproxy, Toxiproxy_Host

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy.engine import Engine
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import strlist, strstrdict

    Engine = Engine
    Iterator = Iterator
    PubSubDatabase = PubSubDatabase
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The image of a PostgreSQL server older than the version that Zato requires
    Older_Server_Image = 'postgres:18'

    # The setting of the commit level of a session
    Commit_Setting = 'synchronous_commit'

    # The commit level that a session runs with unless the server configures a stronger one
    Level_On = 'on'

    # A commit level stronger than the local flush, which a session keeps
    Level_Remote_Apply = 'remote_apply'

    # The environment variable with the host of the Zato database
    Env_Host = 'Zato_Database_Host'

    # An address of the documentation range, which no host answers and to which packets are dropped
    Unanswering_Host = '192.0.2.1'

    # How much longer than the connect timeout a connection attempt or a statement is allowed to take, in seconds
    Connect_Margin_Seconds = 5

    # The environment variable with the port of the Zato database
    Env_Port = 'Zato_Database_Port'

    # The setting of the statement timeout of a session, which pg_settings shows in milliseconds
    Statement_Timeout_Setting = 'statement_timeout'

    # The label of the container of Toxiproxy in front of the database of this module
    Toxiproxy_Label = 'durability-engines'

    # The toxic that drops every reply of PostgreSQL and keeps the connection open, which a timeout of 0 means
    Toxic_Hold_Replies = 'timeout'
    Toxic_Hold_Replies_Attributes = {'timeout': 0}

# ################################################################################################################################
# ################################################################################################################################

class DatabaseProxy(NamedTuple):
    """ The container of Toxiproxy in front of the database of the module and the environment that points at its proxy.
    """
    toxiproxy: 'Toxiproxy'
    env: 'strstrdict'

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
    """ Returns an engine of the tables of the configuration database, as the ODB pool of a server builds it.
    """
    out = new_odb_engine()
    return out

# ################################################################################################################################

def _get_session_level(engine:'Engine') -> 'str':
    with engine.connect() as connection:
        out = connection.execute(text(f'show {ModuleCtx.Commit_Setting}')).scalar()
    return out

# ################################################################################################################################

def _get_statement_timeout_ms(engine:'Engine') -> 'int':
    """ Returns the statement timeout of a new session of an engine, in milliseconds.
    """
    query = text('select setting from pg_settings where name = :name')

    with engine.connect() as connection:
        setting = connection.execute(query, {'name': ModuleCtx.Statement_Timeout_Setting}).scalar_one()

    out = int(setting)
    return out

# ################################################################################################################################

def _select_one(engine:'Engine') -> 'int':
    with engine.connect() as connection:
        out = connection.execute(text('select 1')).scalar_one()
    return out

# ################################################################################################################################

def _assert_unanswered_statement_bounded(engine:'Engine', toxiproxy:'Toxiproxy') -> 'None':
    """ A statement whose reply the proxy drops fails within the read timeout, plus the connect timeout of the new
    connection that the pre-ping of an engine opens in place of the one that failed, and the engine runs its next
    statement once the replies pass again.
    """

    # A statement through the proxy succeeds ..
    assert _select_one(engine) == 1

    # .. the proxy then drops every reply of PostgreSQL and keeps the connection open ..
    toxiproxy.add_toxic(Database_Proxy, ModuleCtx.Toxic_Hold_Replies, ModuleCtx.Toxic_Hold_Replies_Attributes,
        Stream_Downstream)

    try:
        started = time.monotonic()

        with pytest.raises(DBAPIError):
            _ = _select_one(engine)

        elapsed = time.monotonic() - started

    finally:
        toxiproxy.remove_toxics(Database_Proxy)

    limit = PostgreSQL_Read_Timeout_Seconds + PostgreSQL_Connect_Timeout_Seconds + ModuleCtx.Connect_Margin_Seconds
    assert elapsed < limit, elapsed

    # .. and once the replies pass again, the next statement runs on a connection that replaced the failed one.
    assert _select_one(engine) == 1

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

@pytest.fixture(scope='module')
def database_proxy(database:'PubSubDatabase') -> 'Iterator[DatabaseProxy]':
    """ A container of Toxiproxy with a proxy in front of the database of the module.
    """
    toxiproxy = Toxiproxy(ModuleCtx.Toxiproxy_Label)
    toxiproxy.start()

    try:
        upstream_host = get_database_address(database)
        listen_port = toxiproxy.add_proxy(Database_Proxy, database.port, upstream_host)

        env = dict(database.env)
        env[ModuleCtx.Env_Host] = Toxiproxy_Host
        env[ModuleCtx.Env_Port] = f'{listen_port}'

        yield DatabaseProxy(toxiproxy, env)

    finally:
        toxiproxy.stop()

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

def test_relaxed_durability_level_accepted() -> 'None':
    """ A server with the relaxed level of durability is accepted at the first connection of an engine of Zato
    with each of its durability settings turned off, and each session of Zato keeps the commit level of the server.
    """
    relaxed_levels = _get_relaxed_levels()
    relaxed_level = relaxed_levels[0]

    # The server turns off each durability setting and declares the relaxed level of durability ..
    commit_setting = f'{ModuleCtx.Commit_Setting}={relaxed_level}'
    durability_setting = f'{Durability_Level_Setting}={Durability_Level_Relaxed}'

    extra_settings = get_server_refusal_arguments()
    extra_settings.append(commit_setting)
    extra_settings.append(durability_setting)

    database = start_pubsub_database('durability-relaxed', PubSubDBMode.PostgreSQL, extra_settings=extra_settings)

    # .. and both engines connect to it, with sessions that keep its commit level.
    try:
        with pubsub_db_env(database.env):
            assert _get_levels() == (relaxed_level, relaxed_level)
    finally:
        dispose_database_engine()
        stop_pubsub_database(database)

# ################################################################################################################################

def test_older_server_refused() -> 'None':
    """ A server older than the version of PostgreSQL that Zato requires is refused at the first connection
    of an engine of Zato, with an error that names the required version.
    """
    database = start_pubsub_database('version-refused', PubSubDBMode.PostgreSQL, image=ModuleCtx.Older_Server_Image)

    try:
        with pubsub_db_env(database.env):
            with pytest.raises(DatabaseVersionError, match=f'requires PostgreSQL {Minimum_Server_Version_Name}'):
                _ = get_database_engine()
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

def test_connection_to_unanswering_address_bounded(database:'PubSubDatabase') -> 'None':
    """ A connection attempt to an address that drops every packet fails once the connect timeout elapses.
    """
    env = dict(database.env)
    env[ModuleCtx.Env_Host] = ModuleCtx.Unanswering_Host

    dispose_database_engine()

    try:
        with pubsub_db_env(env):
            started = time.monotonic()

            with pytest.raises(Exception):
                _ = get_database_engine()

            elapsed = time.monotonic() - started
    finally:
        dispose_database_engine()

    assert elapsed < PostgreSQL_Connect_Timeout_Seconds + ModuleCtx.Connect_Margin_Seconds, elapsed

# ################################################################################################################################

def test_statement_longer_than_connect_timeout(database:'PubSubDatabase') -> 'None':
    """ A statement that runs longer than the connect timeout completes, because the timeout bounds the connection
    attempt only.
    """
    sleep_seconds = PostgreSQL_Connect_Timeout_Seconds + ModuleCtx.Connect_Margin_Seconds
    engine = get_database_engine()

    with engine.connect() as connection:
        _ = connection.execute(text('select pg_sleep(:seconds)'), {'seconds': sleep_seconds})

# ################################################################################################################################

def test_statement_timeout_of_both_engines(database:'PubSubDatabase') -> 'None':
    """ A new session of the Zato database and of a database of Zato that the environment does not configure
    runs with the statement timeout of Zato.
    """
    dispose_database_engine()

    try:
        assert _get_statement_timeout_ms(get_database_engine()) == PostgreSQL_Statement_Timeout_Ms
    finally:
        dispose_database_engine()

    configuration_engine = _new_configuration_engine()

    try:
        assert _get_statement_timeout_ms(configuration_engine) == PostgreSQL_Statement_Timeout_Ms
    finally:
        configuration_engine.dispose()

# ################################################################################################################################

def test_unanswered_statement_of_zato_database_bounded(database_proxy:'DatabaseProxy') -> 'None':
    """ A statement of the Zato database whose reply a proxy that keeps the connection open never forwards
    fails within a bounded time.
    """
    dispose_database_engine()

    try:
        with pubsub_db_env(database_proxy.env):
            _assert_unanswered_statement_bounded(get_database_engine(), database_proxy.toxiproxy)
    finally:
        dispose_database_engine()

# ################################################################################################################################

def test_unanswered_statement_of_configuration_engine_bounded(database_proxy:'DatabaseProxy') -> 'None':
    """ A statement of a database of Zato that the environment does not configure, whose reply a proxy that keeps
    the connection open never forwards, fails within a bounded time.
    """
    with pubsub_db_env(database_proxy.env):
        configuration_engine = _new_configuration_engine()

    try:
        _assert_unanswered_statement_bounded(configuration_engine, database_proxy.toxiproxy)
    finally:
        configuration_engine.dispose()

# ################################################################################################################################
# ################################################################################################################################
