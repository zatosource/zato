# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import subprocess
import time

# pg8000
import pg8000.dbapi

# pytest
import pytest

# Zato
from zato.common.test.exactly_once.config import TestConfig
from zato.common.test.pubsub_database import connect, get_db_mode, is_postgresql_mode
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase

# ################################################################################################################################
# ################################################################################################################################

# Whether the suite runs against PostgreSQL
_is_postgresql = is_postgresql_mode(get_db_mode())

# The markers of the tests that run against one database only
postgresql_only = pytest.mark.skipif(not _is_postgresql, reason='PostgreSQL only')
sqlite_only     = pytest.mark.skipif(_is_postgresql, reason='SQLite only')

# How long the trigger delays the insert of a message, in seconds
Insert_Delay_Seconds = 30

# How long the tests wait for a delayed insert and for the database to start again, and how often they look, in seconds
_session_timeout = 60.0
_ready_timeout   = 120.0
_poll_seconds    = 0.2

# How long a docker command may run, in seconds
_docker_timeout = 120

# The function and the trigger that delay the insert of the message with a given correlation ID
_delay_function_template = """
create or replace function zato_test_delay_insert() returns trigger language plpgsql as $body$
begin
    if new.correl_id = '{correl_id}' then
        perform pg_sleep({seconds});
    end if;
    return new;
end
$body$
"""

_delay_trigger = 'create trigger zato_test_delay_insert before insert on pubsub_message ' + \
    'for each row execute function zato_test_delay_insert()'

# The same function without the delay, which replaces it without a lock on the table that the delayed inserts hold
_no_delay_function = """
create or replace function zato_test_delay_insert() returns trigger language plpgsql as $body$
begin
    return new;
end
$body$
"""

_drop_trigger  = 'drop trigger if exists zato_test_delay_insert on pubsub_message'
_drop_function = 'drop function if exists zato_test_delay_insert()'

# The session of the server that waits in the delay of the trigger
_sleeping_session_query = "select pid from pg_stat_activity where wait_event = 'PgSleep' and pid <> pg_backend_pid()"

_terminate_query = 'select pg_terminate_backend(%s)'

# ################################################################################################################################
# ################################################################################################################################

def _get_database() -> 'PubSubDatabase':
    """ Returns the PostgreSQL container of the session.
    """
    out = cast_('PubSubDatabase', TestConfig.session_state.pubsub_database)
    return out

# ################################################################################################################################

def _execute(*statements:'str') -> 'None':
    """ Runs the statements in one transaction as the superuser of the container.
    """
    database = _get_database()
    connection = connect(database, is_admin=True)

    try:
        cursor = connection.cursor()

        for statement in statements:
            cursor.execute(statement)

        connection.commit()

    finally:
        connection.close()

# ################################################################################################################################

def add_insert_delay(correl_id:'str') -> 'None':
    """ Makes the insert of the message with the correlation ID wait inside its transaction.
    """
    delay_function = _delay_function_template.format(correl_id=correl_id, seconds=Insert_Delay_Seconds)
    _execute(_drop_trigger, delay_function, _delay_trigger)

# ################################################################################################################################

def _find_delayed_session() -> 'int':
    """ Returns the process ID of a session that waits in the delay of an insert, or 0 if none does.
    """
    database = _get_database()
    connection = connect(database, is_admin=True)

    try:
        cursor = connection.cursor()
        cursor.execute(_sleeping_session_query)
        row = cursor.fetchone()
    finally:
        connection.close()

    if row:
        out = row[0]
    else:
        out = 0

    return out

# ################################################################################################################################

def remove_insert_delay() -> 'None':
    """ Ends the delay of the inserts, waits until no insert waits in it, and removes the trigger, whose removal
    needs a lock on the table that a delayed insert holds until its delay ends.
    """
    _execute(_no_delay_function)

    deadline = time.monotonic() + _session_timeout

    while _find_delayed_session():
        if time.monotonic() > deadline:
            raise Exception(f'A session still waits in the delay of an insert after {_session_timeout}s')
        time.sleep(_poll_seconds)

    _execute(_drop_trigger, _drop_function)

# ################################################################################################################################

def wait_for_delayed_session() -> 'int':
    """ Waits until a session of the server waits in the delay of an insert and returns its process ID.
    """
    deadline = time.monotonic() + _session_timeout

    out = 0

    while not out:

        # The session is there ..
        out = _find_delayed_session()

        # .. or it is looked for again after a while, until the deadline.
        if not out:
            if time.monotonic() > deadline:
                raise Exception(f'No session waits in the delay of an insert within {_session_timeout}s')

            time.sleep(_poll_seconds)

    return out

# ################################################################################################################################

def terminate_session(pid:'int') -> 'None':
    """ Terminates one session of the database.
    """
    database = _get_database()
    connection = connect(database, is_admin=True)

    try:
        cursor = connection.cursor()
        cursor.execute(_terminate_query, (pid,))
        connection.commit()
    finally:
        connection.close()

# ################################################################################################################################

def _docker(*args:'str') -> 'None':
    """ Runs one docker command against the container of the session.
    """
    command = ['docker']
    command.extend(args)

    _ = subprocess.run(command, capture_output=True, text=True, check=True, timeout=_docker_timeout)

# ################################################################################################################################

def restart_database() -> 'None':
    """ Kills the PostgreSQL container with SIGKILL, starts it again and waits until it accepts connections.
    """
    database = _get_database()

    _docker('kill', '--signal', 'KILL', database.container_name)
    _docker('start', database.container_name)

    deadline = time.monotonic() + _ready_timeout

    while True:
        try:
            connection = connect(database)
        except pg8000.dbapi.Error:
            if time.monotonic() > deadline:
                raise
            time.sleep(_poll_seconds)
        else:
            connection.close()
            break

# ################################################################################################################################
# ################################################################################################################################
