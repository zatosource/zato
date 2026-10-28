# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How connections to environment-configured databases are built - SQLite pragmas,
# SSL contexts, driver-specific connection arguments and SQLAlchemy URLs.

# stdlib
import socket
import ssl

# SQLAlchemy
from sqlalchemy import text

# Zato
from zato.common.db_env.common import Type_MySQL, Type_PostgreSQL, Type_SQLite

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ssl import SSLContext
    from sqlalchemy.engine import Connection
    from zato.common.typing_ import any_, stranydict

    # Dummy assignments to satisfy type checkers
    Connection = Connection
    SSLContext = SSLContext

# ################################################################################################################################
# ################################################################################################################################

# SQLAlchemy dialects for each database type
_dialects = {
    Type_MySQL:      'mysql+pymysql',
    Type_PostgreSQL: 'postgresql+pg8000',
}

# Default ports for each database type
_default_ports = {
    Type_MySQL:      3306,
    Type_PostgreSQL: 5432,
}

# How long an SQLite write waits for another writer to finish before giving up,
# in milliseconds - without this, two processes sharing one file, e.g. a server
# and the cron-driven cleanup process, fail immediately with a locked-database
# error instead of taking turns. Writes are bounded batches, so the wait is short.
_sqlite_busy_timeout_ms = 5000

# ################################################################################################################################
# ################################################################################################################################

def set_sqlite_pragmas(dbapi_connection:'any_', connection_record:'any_') -> 'None':
    """ WAL mode lets multiple processes share the file safely, synchronous=NORMAL
    keeps each insert fast while remaining durable enough for aggregate and audit data,
    and the busy timeout makes concurrent writers from separate processes take turns.
    """
    cursor = dbapi_connection.cursor()
    _ = cursor.execute('pragma journal_mode=wal')
    _ = cursor.execute('pragma synchronous=normal')
    _ = cursor.execute(f'pragma busy_timeout={_sqlite_busy_timeout_ms}')
    cursor.close()

# ################################################################################################################################

def set_postgresql_no_delay(dbapi_connection:'any_', connection_record:'any_') -> 'None':
    """ Turns off the delay of small TCP segments on the socket of a pg8000 connection. The driver writes a statement
    through a buffered file, so a parameter larger than its buffer leaves a final partial segment that the kernel
    holds until the server acknowledges the previous one, and the server delays that acknowledgment by up to 40 ms,
    which adds that much to each row of a multi-row insert of message bodies.
    """
    dbapi_connection._usock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

# ################################################################################################################################

def set_sqlite_busy_timeout(connection:'Connection', timeout_ms:'int') -> 'None':
    """ Sets how long writes on this connection wait for another writer before giving up, in milliseconds.
    The setting stays with the connection for as long as it lives in its pool.
    """
    _ = connection.execute(text(f'pragma busy_timeout={timeout_ms}'))

# ################################################################################################################################

def build_ssl_context_from_values(values:'stranydict') -> 'SSLContext':
    """ Builds an SSL context out of a dict of connection values.
    """
    ca_file      = values['ssl_ca_file']
    cert_file    = values['ssl_cert_file']
    key_file     = values['ssl_key_file']
    needs_verify = values['ssl_verify']

    # Verify against the given CA or, if none was given, against the system store ..
    if ca_file:
        out = ssl.create_default_context(cafile=ca_file)
    else:
        out = ssl.create_default_context()

    # .. a client certificate is only needed for mutual TLS ..
    if cert_file:
        out.load_cert_chain(cert_file, key_file)

    # .. and verification can be turned off explicitly.
    if not needs_verify:
        out.check_hostname = False
        out.verify_mode = ssl.CERT_NONE

    return out

# ################################################################################################################################

def build_connect_args_from_values(values:'stranydict', db_type:'str') -> 'stranydict':
    """ Returns driver-specific connection arguments, including SSL ones if SSL is enabled
    and an explicit opt-out of TLS for PostgreSQL if it is not, all built out of a dict of connection values.
    """

    # Our response to produce
    out:'stranydict' = {}

    # SSL never applies to SQLite files ..
    if db_type == Type_SQLite:
        return out

    # .. it is off unless requested explicitly, which pg8000 needs to be told about,
    # .. because without a context it attempts an unverified TLS connection first ..
    if not values['ssl']:
        if db_type == Type_PostgreSQL:
            out['ssl_context'] = False
        return out

    # .. each driver receives the same SSL context under its own keyword ..
    ssl_context = build_ssl_context_from_values(values)

    # .. PyMySQL accepts an SSL context directly ..
    if db_type == Type_MySQL:
        out['ssl'] = ssl_context

    # .. and pg8000 under its own keyword.
    else:
        out['ssl_context'] = ssl_context

    return out

# ################################################################################################################################

def build_engine_url_from_values(values:'stranydict', db_type:'str') -> 'str':
    """ Builds the SQLAlchemy URL for a database out of a dict of connection values.
    """

    # SQLite needs a file path only ..
    if db_type == Type_SQLite:
        db_path = values['name']
        out = f'sqlite:///{db_path}'
        return out

    # .. everything else is a network database with full credentials.
    dialect  = _dialects[db_type]
    host     = values['host']
    username = values['username']
    password = values['password']
    db_name  = values['name']

    if port := values['port']:
        port = int(port)
    else:
        port = _default_ports[db_type]

    out = f'{dialect}://{username}:{password}@{host}:{port}/{db_name}'
    return out

# ################################################################################################################################
# ################################################################################################################################
