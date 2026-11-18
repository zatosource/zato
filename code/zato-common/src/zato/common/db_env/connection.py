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
from sqlalchemy.engine import URL

# Zato
from zato.common.db_env.common import Type_PostgreSQL, Type_SQLite

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
    Type_PostgreSQL: 'postgresql+pg8000',
}

# Default ports for each database type
_default_ports = {
    Type_PostgreSQL: 5432,
}

# How long an SQLite write waits for another writer to finish before giving up,
# in milliseconds - without this, two processes sharing one file, e.g. a server
# and the cron-driven cleanup process, fail immediately with a locked-database
# error instead of taking turns. Writes are bounded batches, so the wait is short.
SQLite_Busy_Timeout_Ms = 5000

# How much of an SQLite database file is read through memory mapping rather than copied in with a read call per page,
# in bytes. SQLite lowers it to the maximum its build allows.
SQLite_MMAP_Size = 1024 ** 4

# How long a PostgreSQL connection stays idle before it sends its first keepalive probe, in seconds - below
# the idle limits of cloud load balancers and NAT gateways, which drop idle flows silently after 240 to 350 seconds.
_keepalive_idle_seconds = 30

# How often the keepalive probes are repeated and how many unanswered ones make the connection fail.
_keepalive_interval_seconds = 10
_keepalive_count = 3

# How long sent data may remain unacknowledged before the connection fails, in milliseconds.
_user_timeout_ms = 60_000

# How long a PostgreSQL session may hold a transaction open without activity, in milliseconds.
_idle_in_transaction_timeout_ms = 60_000

# The commit levels of PostgreSQL under which a commit may return before its record is flushed to disk.
Relaxed_Commit_Levels = ('off', 'local', 'remote_write')

# How PostgreSQL shows a setting that is turned on.
Setting_On = 'on'

# The journal mode and the level of synchronization that every SQLite connection of Zato runs with.
SQLite_Journal_Mode = 'wal'
SQLite_Synchronous = 'full'

# The standbys that stream the write-ahead log of the server, without the logical replication connections,
# which receive changes that are already durable.
Standby_Count_Query = """
select count(*) from pg_stat_replication as replication
where not exists (
    select 1 from pg_replication_slots as slot
    where slot.active_pid = replication.pid
    and slot.slot_type = 'logical'
)
""".strip()

# The roles that Amazon RDS, Aurora and Azure Database for PostgreSQL create on each of their servers. On these services
# the provider performs every automatic failover, and only to a standby that it replicates synchronously, at the storage
# layer or through synchronous_standby_names that it manages, while the read replicas that stream asynchronously
# are never a target of an automatic failover.
Provider_Failover_Roles = ('rds_superuser', 'azure_pg_admin')

_provider_failover_query = """
select exists (select 1 from pg_roles where rolname in ({}))
""".strip().format(', '.join(f"'{role}'" for role in Provider_Failover_Roles))

# ################################################################################################################################
# ################################################################################################################################

class DatabaseDurabilityError(Exception):
    """ Raised when a database is configured in a way under which a commit could be acknowledged before it is durable.
    """

# ################################################################################################################################
# ################################################################################################################################

def set_sqlite_pragmas(dbapi_connection:'any_', connection_record:'any_') -> 'None':
    """ WAL mode lets multiple processes share the file safely, synchronous=FULL
    flushes the write-ahead log at each commit so that a committed transaction survives a power loss
    or a forced detachment of the volume, and the busy timeout makes concurrent writers from separate processes take turns.
    Secure deletion in its fast form zeroes deleted content on the pages a delete writes anyway and leaves freed
    overflow pages as they are, because SQLite builds that enable full secure deletion by default otherwise write
    each freed page of a large payload again, which doubles the cost of every commit that removes message bodies.
    Foreign keys are enforced, as on PostgreSQL. The file is read through memory mapping, which shares the pages
    of the operating system's cache among all the connections and processes instead of copying each page
    into the cache of each connection.
    """
    cursor = dbapi_connection.cursor()
    _ = cursor.execute('pragma journal_mode=wal')
    _ = cursor.execute('pragma synchronous=full')
    _ = cursor.execute('pragma secure_delete=fast')
    _ = cursor.execute('pragma foreign_keys=on')
    _ = cursor.execute(f'pragma busy_timeout={SQLite_Busy_Timeout_Ms}')
    _ = cursor.execute(f'pragma mmap_size={SQLite_MMAP_Size}')
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

def set_postgresql_keepalive(dbapi_connection:'any_', connection_record:'any_') -> 'None':
    """ Makes a pg8000 connection detect a peer that is no longer reachable. An idle connection sends keepalive probes
    well before the idle limits of cloud load balancers and NAT gateways, and a connection whose sent data remains
    unacknowledged fails after a bounded time instead of waiting for the kernel's retransmission limit of many minutes.
    """
    sock = dbapi_connection._usock
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, _keepalive_idle_seconds)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, _keepalive_interval_seconds)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, _keepalive_count)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_USER_TIMEOUT, _user_timeout_ms)

# ################################################################################################################################

def set_postgresql_session(dbapi_connection:'any_', connection_record:'any_') -> 'None':
    """ Ends a session that holds a transaction open without activity, so that a client which stopped
    responding in the middle of a transaction does not keep its row locks indefinitely. Each commit of the session
    returns only once its write-ahead log record is flushed to disk. A level that the server configures and that waits
    for more than the local flush, such as remote_apply, is kept as it is.
    """
    cursor = dbapi_connection.cursor()

    _ = cursor.execute('show synchronous_commit')
    row = cursor.fetchone()
    configured_level = row[0]

    if configured_level in Relaxed_Commit_Levels:
        _ = cursor.execute('set synchronous_commit = on')

    _ = cursor.execute(f"set idle_in_transaction_session_timeout = '{_idle_in_transaction_timeout_ms}ms'")
    cursor.close()
    dbapi_connection.commit()

# ################################################################################################################################

def _show(cursor:'any_', query:'str') -> 'any_':
    _ = cursor.execute(query)
    row = cursor.fetchone()

    out = row[0]
    return out

# ################################################################################################################################

def verify_postgresql_server(dbapi_connection:'any_', connection_record:'any_') -> 'None':
    """ Refuses a PostgreSQL server on which a commit could be acknowledged before it is durable - one that does not
    flush its write-ahead log, one that does not write full pages after a checkpoint, and a primary with streaming
    standbys none of which is synchronous, unless the provider of the server performs the failover. The check runs
    on each new connection, so the primary that a failover of the database promotes is checked as well.
    """
    cursor = dbapi_connection.cursor()

    fsync = _show(cursor, 'show fsync')
    full_page_writes = _show(cursor, 'show full_page_writes')
    synchronous_standby_names = _show(cursor, 'show synchronous_standby_names')
    standby_count = _show(cursor, Standby_Count_Query)
    has_provider_failover = _show(cursor, _provider_failover_query)

    cursor.close()
    dbapi_connection.commit()

    if fsync != Setting_On:
        raise DatabaseDurabilityError(f'PostgreSQL server has fsync `{fsync}`, it must be `{Setting_On}`')

    if full_page_writes != Setting_On:
        raise DatabaseDurabilityError(
            f'PostgreSQL server has full_page_writes `{full_page_writes}`, it must be `{Setting_On}`')

    if standby_count and not has_provider_failover:
        if not synchronous_standby_names:
            message = f'PostgreSQL primary has {standby_count} streaming standby(s) and an empty synchronous_standby_names'
            raise DatabaseDurabilityError(f'{message}, at least one standby must be synchronous')

# ################################################################################################################################

def set_django_connection(sender:'any_', connection:'any_', **kwargs:'any_') -> 'None':
    """ Gives each connection that Django opens to a database of Zato the same settings of durability
    as the connections of the engine factory.
    """
    if connection.vendor == Type_SQLite:
        set_sqlite_pragmas(connection.connection, None)

    elif connection.vendor == Type_PostgreSQL:
        set_postgresql_session(connection.connection, None)
        verify_postgresql_server(connection.connection, None)

    else:
        raise DatabaseDurabilityError(f'Unsupported database vendor `{connection.vendor}`')

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
        out['ssl_context'] = False
        return out

    # .. and pg8000 receives the SSL context under its own keyword.
    out['ssl_context'] = build_ssl_context_from_values(values)

    return out

# ################################################################################################################################

def build_engine_url_from_values(values:'stranydict', db_type:'str') -> 'str | URL':
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

    # .. the URL is built from its parts so that characters such as @, / or % in a password are passed as they are.
    out = URL.create(dialect, username=username, password=password, host=host, port=port, database=db_name)
    return out

# ################################################################################################################################
# ################################################################################################################################
