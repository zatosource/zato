# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
import subprocess
import sys

# SQLAlchemy
from sqlalchemy import text

# Zato
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.test.pubsub_database import connect, get_container_settings, ModuleCtx
from zato.common.test.pubsub_profile import Managed_Profiles

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import ManagedDatabase
    from zato.common.typing_ import any_, strlist, strset

# ################################################################################################################################
# ################################################################################################################################

# What the pub/sub role is and may do.
_role_query = text("""
    select rolsuper, rolcreaterole, rolcreatedb, rolreplication, rolbypassrls,
        pg_has_role(current_user, :admin_role, 'member')
    from pg_roles where rolname = current_user
""")

# The tables of pub/sub that another role owns.
_foreign_tables_query = text("""
    select count(*) from pg_tables where schemaname = 'public' and tableowner <> current_user
""")

# Whether the connection of the query runs over TLS.
_ssl_query = text('select ssl from pg_stat_ssl where pid = pg_backend_pid()')

# Where the value of a setting comes from.
_source_query = 'select source from pg_settings where name = %s'

# The context of a setting, which tells who may change it and when.
_context_query = 'select context from pg_settings where name = %s'

# The statements that the pub/sub role ran, as pg_stat_statements records them.
_statements_query = """
    select query from pg_stat_statements
    where userid = (select oid from pg_roles where rolname = %s)
"""

# The statements that set a parameter of a session, and the statements that pub/sub never runs.
_set_pattern = re.compile(r'^\s*set\s+(?:session\s+|local\s+)?([a-z_.]+)', re.IGNORECASE)
_forbidden_pattern = re.compile(r'^\s*(?:alter\s+system|create\s+extension|copy\s+\S+\s+from\s+\'|load\s)', re.IGNORECASE)

# The parameters that a statement of another form sets - SET SESSION CHARACTERISTICS AS TRANSACTION
# sets the isolation level of the session.
_set_parameters = {
    'characteristics': 'default_transaction_isolation',
}

# The source of the settings that the container configuration, standing for the parameter group, gives.
_configured_source = 'configuration file'
_command_line_source = 'command line'

# The context of the parameters that any role may set in its own session.
_user_context = 'user'

# ################################################################################################################################
# ################################################################################################################################

def _get_name(setting:'str') -> 'str':
    name, _, _ = setting.partition('=')
    out = name.strip()
    return out

# ################################################################################################################################

def _fetch_value(cursor:'any_', query:'str', name:'str') -> 'str':
    """ Returns the first column of the one row that a query about one setting returns.
    """
    cursor.execute(query, (name,))
    row:'any_' = cursor.fetchone()

    out = row[0]
    return out

# ################################################################################################################################

def _run_workload() -> 'None':
    """ Takes over the database, publishes, pulls and acknowledges, and runs one sweep of the cleanup process,
    so that every kind of statement of pub/sub is recorded.
    """
    backend = SQLPubSubBackend()
    backend.take_over()

    sub_key = 'zpsk.managed.privileges'
    topic_name = 'managed.privileges'

    backend.subscribe(sub_key, topic_name)
    _ = backend.publish(topic_name, 'privileges')

    messages = backend.pull_messages(sub_key, max_messages=10)

    msg_ids:'strlist' = []
    for message in messages:
        msg_ids.append(message['msg_id'])

    _ = backend.ack_pulled(sub_key, msg_ids)

    command = [sys.executable, '-m', 'zato.common.pubsub.sql.cleanup', '--once']
    _ = subprocess.run(command, check=True, capture_output=True)

# ################################################################################################################################
# ################################################################################################################################

def test_role(managed_database:'ManagedDatabase') -> 'None':
    """ Pub/sub runs under a role that is a member of the administrators
    of the service and is not a superuser, owns the tables of its schema and connects over TLS only.
    """
    profile = Managed_Profiles[managed_database.database.profile_name]

    with get_pubsub_engine().connect() as connection:
        role = connection.execute(_role_query, {'admin_role': profile.admin_role}).one()
        foreign_tables = connection.execute(_foreign_tables_query).scalar_one()
        is_ssl = connection.execute(_ssl_query).scalar_one()

    is_superuser, can_create_role, can_create_db, can_replicate, bypasses_rls, is_admin_member = role

    assert not is_superuser
    assert not can_create_role
    assert not can_create_db
    assert not can_replicate
    assert not bypasses_rls
    assert is_admin_member

    assert foreign_tables == 0, foreign_tables
    assert is_ssl

# ################################################################################################################################

def test_settings(managed_database:'ManagedDatabase') -> 'None':
    """ Each setting comes from the configuration that stands for the parameter group
    or the server parameters, and each setting that the service does not allow to change keeps its default.
    """
    database = managed_database.database
    profile = Managed_Profiles[database.profile_name]

    settings = get_container_settings(database, None)

    connection = connect(database, is_admin=True)

    # The names of the settings that the service gives values of its own to ..
    service_names:'strset' = set()

    for setting in profile.service_settings:
        name = _get_name(setting)
        service_names.add(name)

    try:
        cursor = connection.cursor()

        # .. each setting of the profile comes from the configuration ..
        for setting in settings:
            name = _get_name(setting)
            source = _fetch_value(cursor, _source_query, name)
            assert source == _command_line_source, f'{name} -> {source}'

        # .. and each setting that the service does not allow to change keeps its default, unless the service gives it.
        for name in profile.excluded_settings:
            if name not in service_names:
                source = _fetch_value(cursor, _source_query, name)
                assert source != _command_line_source, f'{name} -> {source}'
                assert source != _configured_source, f'{name} -> {source}'

    finally:
        connection.close()

# ################################################################################################################################

def test_session_statements(managed_database:'ManagedDatabase') -> 'None':
    """ Pub/sub sets only the parameters that any role may set in its own session,
    and it runs no statement that requires a superuser or an extension outside the list of the service.
    """
    database = managed_database.database

    connection = connect(database, is_admin=True)
    connection.autocommit = True

    try:
        cursor = connection.cursor()
        cursor.execute('create extension if not exists pg_stat_statements')
        cursor.execute('select pg_stat_statements_reset()')

        _run_workload()

        cursor.execute(_statements_query, (ModuleCtx.Username,))
        rows = cursor.fetchall()

        assert rows, 'No statement of pub/sub was recorded'

        for row in rows:
            query = row[0]

            assert not _forbidden_pattern.match(query), query

            if match := _set_pattern.match(query):
                name = match.group(1).lower()

                if name in _set_parameters:
                    name = _set_parameters[name]

                context = _fetch_value(cursor, _context_query, name)
                assert context == _user_context, f'{name} -> {context} in {query}'

    finally:
        connection.close()

# ################################################################################################################################
# ################################################################################################################################
