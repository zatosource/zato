# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from http.client import ACCEPTED
from logging import getLogger
from queue import Empty, LifoQueue
from threading import BoundedSemaphore
from time import monotonic
from traceback import format_exc

# gevent
from gevent import get_hub

# mssql-python
import mssql_python

# typing-extensions
from typing_extensions import TypeAlias

# Zato
from zato.common.api import MicrosoftFabric
from zato.common.mssql_direct import _marker_pattern, _validate_params
from zato.common.typing_ import any_, anylist, cast_, tuple_
from zato.server.connection.cloud.microsoft_fabric.base import MicrosoftFabricBase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from mssql_python import Connection
    from zato.common.typing_ import anydict, callable_, dictlist, stranydict, strdictnone, strlist, strlistnone
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_default = MicrosoftFabric.Default
_sync_status = MicrosoftFabric.Sync_Status

# The query and the values of its markers, in the order the markers appear in it
_qmark_query = tuple_[str, anylist]

# What a call in a thread came back with - its result or the exception it raised
_thread_result = tuple_[any_, 'Exception | None']

connection_queue:TypeAlias = 'LifoQueue[Connection]'
login_attributes:TypeAlias = 'dict[int, int | str | bytes]'

# ################################################################################################################################
# ################################################################################################################################

def _to_qmark_query(query:'str', params:'strdictnone') -> '_qmark_query':
    """ Rewrites :name markers into the ? placeholders the SQL endpoint driver binds,
    returning the values in the order the markers appear. String literals are left as they are.
    """
    _validate_params(query, params)
    bound = cast_('stranydict', params)

    values:'anylist' = []

    def replace(match:'any_') -> 'str':
        name = match.group(1)
        if name:
            values.append(bound[name])
            out = '?'
        else:
            out = match.group(0)

        return out

    query = _marker_pattern.sub(replace, query)

    out = (query, values)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _run_in_thread(func:'callable_', *args:'any_') -> 'any_':
    """ Runs a call of the driver in a real thread - the driver is compiled code, so other greenlets
    would not run for the duration of the call otherwise. An exception the call raises is raised here,
    in the calling greenlet, and nowhere else.
    """
    threadpool = get_hub().threadpool

    def call() -> '_thread_result':
        try:
            out = (func(*args), None)
        except Exception as e:
            out = (None, e)

        return out

    result, error = threadpool.apply(call)

    if error:
        raise error

    out = result
    return out

# ################################################################################################################################

def _fetch_rows(conn:'Connection', sql:'str', values:'anylist') -> 'dictlist':
    """ Runs one statement on a connection and returns its rows as dicts.
    """
    out:'dictlist' = []

    cursor = conn.cursor()

    try:
        _ = cursor.execute(sql, values)

        # A statement without rows, e.g. a view definition, has no description.
        if cursor.description:

            column_names:'strlist' = []
            for column in cursor.description:
                column_names.append(column[0])

            for row in cursor.fetchall():
                pairs = zip(column_names, row)
                item = dict(pairs)
                out.append(item)

    finally:
        cursor.close()

    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SQLEndpoint:
    """ The address and database name of a lakehouse's SQL analytics endpoint.
    """
    endpoint_id: 'str'
    host:        'str'
    database:    'str'

# ################################################################################################################################
# ################################################################################################################################

class SQLPool:
    """ A small pool of connections to one SQL analytics endpoint. Each query checks a connection out
    and back in, a connection that failed is closed instead of returned.
    """
    def __init__(self, host:'str', connection_string:'str', size:'int', login_timeout:'int') -> 'None':
        self.host = host
        self.connection_string = connection_string
        self.login_timeout = login_timeout

        # Connections nobody is using right now
        self._idle:'connection_queue' = LifoQueue()

        # How many connections may exist at once, idle or in use
        self._slots = BoundedSemaphore(size)

# ################################################################################################################################

    def _new_connection(self) -> 'Connection':
        """ Opens a new connection to the endpoint.
        """
        attrs_before:'login_attributes' = {mssql_python.SQL_ATTR_LOGIN_TIMEOUT: self.login_timeout}

        out = _run_in_thread(self._connect, attrs_before)
        return out

# ################################################################################################################################

    def _connect(self, attrs_before:'login_attributes') -> 'Connection':
        """ The driver's own connect call.
        """
        out = mssql_python.connect(self.connection_string, autocommit=True, attrs_before=attrs_before)
        return out

# ################################################################################################################################

    def checkout(self, timeout:'float') -> 'Connection':
        """ Returns an idle connection or opens a new one if there is room for it.
        """
        if not self._slots.acquire(timeout=timeout):
            raise Exception(f'No SQL endpoint connection became available in {timeout}s')

        try:
            out = self._idle.get_nowait()
        except Empty:
            try:
                out = self._new_connection()
            except Exception:
                self._slots.release()
                raise

        return out

# ################################################################################################################################

    def checkin(self, conn:'Connection') -> 'None':
        """ Returns a connection for the next query to use.
        """
        self._idle.put(conn)
        self._slots.release()

# ################################################################################################################################

    def discard(self, conn:'Connection') -> 'None':
        """ Closes a connection that failed, freeing its slot for a new one.
        """
        try:
            conn.close()
        except Exception:
            logger.warning('Could not close an SQL endpoint connection -> %s', format_exc())

        self._slots.release()

# ################################################################################################################################

    def dispose(self) -> 'None':
        """ Closes every idle connection - the ones in use close when they are discarded or checked in later.
        """
        while True:
            try:
                conn = self._idle.get_nowait()
            except Empty:
                break

            try:
                conn.close()
            except Exception:
                logger.warning('Could not close an SQL endpoint connection -> %s', format_exc())

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftFabricSQL(MicrosoftFabricBase):
    """ T-SQL queries against the SQL analytics endpoints of lakehouses.
    """

    def _get_sql_endpoint(self, workspace_id:'str', lakehouse_id:'str') -> 'SQLEndpoint':
        """ Returns the lakehouse's SQL analytics endpoint, reading it from the lakehouse the first time.
        """
        endpoint_key = f'{workspace_id}/{lakehouse_id}'

        if endpoint := self._sql_endpoints.get(endpoint_key):
            return endpoint

        lakehouse = self.get(f'/workspaces/{workspace_id}/lakehouses/{lakehouse_id}')
        lakehouse = cast_('anydict', lakehouse)
        properties = lakehouse['properties']

        # A lakehouse just created has no endpoint address yet ..
        if endpoint_properties := properties.get('sqlEndpointProperties'):
            if host := endpoint_properties.get('connectionString'):
                endpoint = SQLEndpoint()
                endpoint.endpoint_id = endpoint_properties['id']
                endpoint.host = host
                endpoint.database = lakehouse['displayName']

                self._sql_endpoints[endpoint_key] = endpoint

        # .. and there is nothing to connect to until it has one.
        if not endpoint:
            raise Exception(f'Lakehouse {lakehouse_id} has no SQL analytics endpoint yet ({self.name})')

        out = endpoint
        return out

# ################################################################################################################################

    def _get_sql_connection_string(self, endpoint:'SQLEndpoint') -> 'str':
        """ The connection string of an endpoint.
        """

        # A closing brace inside a braced value is written twice.
        secret = self.client_secret.replace('}', '}}')

        out = (
            f'Server={endpoint.host},{_default.SQL_Port};'
            f'Database={{{endpoint.database}}};'
            'Authentication=ActiveDirectoryServicePrincipal;'
            f'UID={self.client_id};'
            f'PWD={{{secret}}};'
            'Encrypt=yes;'
        )
        return out

# ################################################################################################################################

    def _get_sql_pool(self, workspace_id:'str', lakehouse_id:'str') -> 'SQLPool':
        """ Returns the lakehouse's connection pool, building it the first time.
        """
        pool_key = f'{workspace_id}/{lakehouse_id}'

        if pool := self._sql_pools.get(pool_key):
            return pool

        with self._sql_lock:

            if pool := self._sql_pools.get(pool_key):
                return pool

            endpoint = self._get_sql_endpoint(workspace_id, lakehouse_id)
            connection_string = self._get_sql_connection_string(endpoint)

            pool = SQLPool(endpoint.host, connection_string, _default.SQL_Pool_Size, _default.SQL_Login_Timeout)
            self._sql_pools[pool_key] = pool

        out = pool
        return out

# ################################################################################################################################

    def _run_sql(self, pool:'SQLPool', sql:'str', values:'anylist') -> 'dictlist':
        """ Runs one statement on a pooled connection and returns its rows as dicts.
        """
        conn = pool.checkout(_default.SQL_Login_Timeout)

        try:
            out = _run_in_thread(_fetch_rows, conn, sql, values)
        except Exception:
            pool.discard(conn)
            raise

        pool.checkin(conn)

        return out

# ################################################################################################################################

    def query(self, workspace_id:'str', lakehouse_id:'str', sql:'str', params:'strdictnone'=None) -> 'dictlist':
        """ Runs a T-SQL query against a lakehouse's SQL analytics endpoint and returns its rows
        as a list of dicts. Markers in the form :name are bound from params.
        """
        pool = self._get_sql_pool(workspace_id, lakehouse_id)
        qmark_sql, values = _to_qmark_query(sql, params)

        url = f'tds://{pool.host}'
        start = monotonic()

        try:

            try:
                out = self._run_sql(pool, qmark_sql, values)

            # A connection-level error closes the idle connections and the query runs once more on a new one.
            except (mssql_python.OperationalError, mssql_python.InterfaceError) as e:
                logger.info('Retrying a Fabric SQL query after a connection error (%s) -> %s', self.name, e)
                pool.dispose()
                out = self._run_sql(pool, qmark_sql, values)

        except Exception as e:
            self._record_call(url, start, str(e))
            raise Exception(f'Fabric SQL error ({self.name}) -> {e}') from e

        self._record_call(url, start)

        return out

# ################################################################################################################################

    def refresh_sql_endpoint(
        self,
        workspace_id:'str',
        lakehouse_id:'str',
        table_names:'strlistnone'=None,
        ) -> 'anydict':
        """ Makes the SQL analytics endpoint pick up tables written to the lakehouse, all of them
        or only the named ones, and returns the sync status of each table.
        """
        endpoint = self._get_sql_endpoint(workspace_id, lakehouse_id)

        request_data:'anydict' = {}
        if table_names:
            request_data['tables'] = [{'schema': _default.SQL_Schema, 'tableNames': table_names}]

        path = f'/workspaces/{workspace_id}/sqlEndpoints/{endpoint.endpoint_id}/refreshMetadata'
        response = self.invoke_raw('POST', path, data=request_data)

        # A refresh that runs on is followed to its end and its result read from where it points ..
        if response.status_code == ACCEPTED:
            location = response.headers['Location']
            _ = self.wait_for_operation(location)
            result = self.get(f'{location}/result')

        # .. one that completed at once carries the result in the body.
        else:
            result = response.json()

        result = cast_('anydict', result)

        # A table the endpoint could not sync is an error for the caller.
        for table in result['value']:
            if table['status'] == _sync_status.Failure:
                raise Exception(f'SQL endpoint refresh failed ({self.name}) -> {table}')

        out = result
        return out

# ################################################################################################################################

    def dispose_sql_pools(self) -> 'None':
        """ Closes the connections of every pool.
        """
        for pool in self._sql_pools.values():
            pool.dispose()

        self._sql_pools.clear()
        self._sql_endpoints.clear()

# ################################################################################################################################
# ################################################################################################################################
