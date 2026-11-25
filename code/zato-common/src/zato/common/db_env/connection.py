# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How connections to the Zato database are built - SSL contexts, driver-specific connection arguments
# and SQLAlchemy URLs.

# stdlib
import socket
import ssl

# SQLAlchemy
from sqlalchemy.engine import URL

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ssl import SSLContext
    from zato.common.typing_ import any_, stranydict

    # Dummy assignments to satisfy type checkers
    SSLContext = SSLContext

# ################################################################################################################################
# ################################################################################################################################

# The SQLAlchemy dialect and driver of the Zato database
Dialect_Name = 'postgresql+pg8000'

# The port of the Zato database when none is given
Default_Port = 5432

# How long a PostgreSQL connection stays idle before it sends its first keepalive probe, in seconds - below
# the idle limits of cloud load balancers and NAT gateways, which drop idle flows silently after 240 to 350 seconds.
_keepalive_idle_seconds = 30

# How often the keepalive probes are repeated and how many unanswered ones make the connection fail.
_keepalive_interval_seconds = 10
_keepalive_count = 3

# How long sent data may remain unacknowledged before the connection fails, in milliseconds.
_user_timeout_ms = 60_000

# How long establishing a PostgreSQL connection may take, in seconds. Without a limit, a connection attempt to an address
# that drops packets, e.g. the address of a database pod that was replaced, waits for the kernel's limit
# of SYN retransmissions of over two minutes.
PostgreSQL_Connect_Timeout_Seconds = 10

# How long PostgreSQL runs one statement of a session of Zato before it cancels it, in milliseconds,
# including the time the statement waits for locks.
PostgreSQL_Statement_Timeout_Ms = 60_000

# How long a connection waits for the next part of a reply before it fails, in seconds - the statement timeout
# and the time that the cancellation error of PostgreSQL needs to arrive. A TCP proxy between Zato and PostgreSQL
# acknowledges the data and answers the keepalive probes itself, so only this timeout detects a database
# that stopped answering behind it.
PostgreSQL_Read_Timeout_Seconds = 70

# How long a PostgreSQL session may hold a transaction open without activity, in milliseconds.
_idle_in_transaction_timeout_ms = 60_000

# The commit levels of PostgreSQL under which a commit may return before its record is flushed to disk.
Relaxed_Commit_Levels = ('off', 'local', 'remote_write')

# How PostgreSQL shows a setting that is turned on.
Setting_On = 'on'

# The custom setting of a PostgreSQL server that declares the level of durability that Zato requires of it.
Durability_Level_Setting = 'zato.durability_level'

# The level of durability of a server whose data is not retained, which Zato uses with the durability settings
# that the server configures.
Durability_Level_Relaxed = 'relaxed'

_durability_level_query = """
select current_setting('{}', true)
""".strip().format(Durability_Level_Setting)

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

def set_postgresql_no_delay(dbapi_connection:'any_', connection_record:'any_') -> 'None':
    """ Turns off the delay of small TCP segments on the socket of a pg8000 connection. The driver writes a statement
    through a buffered file, so a parameter larger than its buffer leaves a final partial segment that the kernel
    holds until the server acknowledges the previous one, and the server delays that acknowledgment by up to 40 ms,
    which adds that much to each row of a multi-row insert of message bodies.
    """
    dbapi_connection._usock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

# ################################################################################################################################

def set_postgresql_keepalive(dbapi_connection:'any_', connection_record:'any_') -> 'None':
    """ Makes a pg8000 connection detect a peer that is no longer reachable on a direct connection. An idle connection
    sends keepalive probes well before the idle limits of cloud load balancers and NAT gateways, and a connection whose
    sent data remains unacknowledged fails after a bounded time instead of waiting for the kernel's retransmission limit
    of many minutes. Behind a TCP proxy, the read timeout of the socket detects a peer that is no longer reachable.
    """
    sock = dbapi_connection._usock
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, _keepalive_idle_seconds)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, _keepalive_interval_seconds)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, _keepalive_count)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_USER_TIMEOUT, _user_timeout_ms)

# ################################################################################################################################

def set_postgresql_read_timeout(dbapi_connection:'any_', connection_record:'any_') -> 'None':
    """ Replaces the timeout that bounds the establishment of a pg8000 connection with the read timeout of its socket,
    which is longer than the statement timeout of the session, so a statement that PostgreSQL runs within its limit
    completes, and a reply that does not arrive fails the connection, which the pool then replaces.
    """
    dbapi_connection._usock.settimeout(PostgreSQL_Read_Timeout_Seconds)

# ################################################################################################################################

def set_postgresql_session(dbapi_connection:'any_', connection_record:'any_') -> 'None':
    """ Ends a session that holds a transaction open without activity, so that a client which stopped
    responding in the middle of a transaction does not keep its row locks indefinitely. Each commit of the session
    returns only once its write-ahead log record is flushed to disk. A level that the server configures and that waits
    for more than the local flush, such as remote_apply, is kept as it is. A server with the relaxed level of durability
    keeps the commit level that it configures.
    """
    cursor = dbapi_connection.cursor()

    # A server with the relaxed level of durability keeps its own commit level ..
    durability_level = _show(cursor, _durability_level_query)

    # .. while on any other server each commit is flushed to disk before it returns ..
    if durability_level != Durability_Level_Relaxed:
        configured_level = _show(cursor, 'show synchronous_commit')

        if configured_level in Relaxed_Commit_Levels:
            _ = cursor.execute('set synchronous_commit = on')

    # .. and every session ends idle transactions and long statements.
    _ = cursor.execute(f"set idle_in_transaction_session_timeout = '{_idle_in_transaction_timeout_ms}ms'")
    _ = cursor.execute(f"set statement_timeout = '{PostgreSQL_Statement_Timeout_Ms}ms'")
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
    on each new connection, so the primary that a failover of the database promotes is checked as well. A server
    with the relaxed level of durability is accepted with the settings that it configures.
    """
    cursor = dbapi_connection.cursor()

    durability_level = _show(cursor, _durability_level_query)
    fsync = _show(cursor, 'show fsync')
    full_page_writes = _show(cursor, 'show full_page_writes')
    synchronous_standby_names = _show(cursor, 'show synchronous_standby_names')
    standby_count = _show(cursor, Standby_Count_Query)
    has_provider_failover = _show(cursor, _provider_failover_query)

    cursor.close()
    dbapi_connection.commit()

    # A server with the relaxed level of durability is accepted as it is ..
    if durability_level == Durability_Level_Relaxed:
        return

    # .. while any other server needs each of the durability settings.
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

def build_connect_args_from_values(values:'stranydict') -> 'stranydict':
    """ Returns driver-specific connection arguments, including SSL ones if SSL is enabled
    and an explicit opt-out of TLS if it is not, all built out of a dict of connection values.
    """

    # Our response to produce
    out:'stranydict' = {}

    # SSL is off unless requested explicitly, which pg8000 needs to be told about,
    # because without a context it attempts an unverified TLS connection first ..
    if not values['ssl']:
        out['ssl_context'] = False
        return out

    # .. and pg8000 receives the SSL context under its own keyword.
    out['ssl_context'] = build_ssl_context_from_values(values)

    return out

# ################################################################################################################################

def get_port_from_values(values:'stranydict') -> 'int':
    """ Returns the port of the Zato database out of a dict of connection values.
    """
    if port := values['port']:
        out = int(port)
    else:
        out = Default_Port

    return out

# ################################################################################################################################

def build_engine_url_from_values(values:'stranydict') -> 'URL':
    """ Builds the SQLAlchemy URL of the Zato database out of a dict of connection values.
    """
    host     = values['host']
    username = values['username']
    password = values['password']
    db_name  = values['name']
    port     = get_port_from_values(values)

    # The URL is built from its parts so that characters such as @, / or % in a password are passed as they are.
    out = URL.create(Dialect_Name, username=username, password=password, host=host, port=port, database=db_name)
    return out

# ################################################################################################################################
# ################################################################################################################################
