# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

# Every alert the Kafka channel under test routed to the receiver since the last clear request
_received:'strlist' = []

# What a call that succeeded reports as its error
_no_error = ''

# Whether a OneLake delete removes a directory with everything in it
_default_recursive = False

# ################################################################################################################################
# ################################################################################################################################

def to_rows(reply:'anydict') -> 'dictlist':
    """ Turns the eventhouse's reply into a list of dicts keyed by column name.
    """
    tables = reply['Tables']
    result = tables[0]

    column_names:'strlist' = []
    for column in result['Columns']:
        column_names.append(column['ColumnName'])

    out:'dictlist' = []
    for values in result['Rows']:
        pairs = zip(column_names, values)
        row = dict(pairs)
        out.append(row)

    return out

# ################################################################################################################################
# ################################################################################################################################

class FabricTestEventsReceiver(Service):
    """ The service the Kafka channel under test routes to - records every alert handed over.
    """
    name = 'test.fabric.events.receiver'

    def handle(self) -> 'None':
        data = self.request.raw_request.decode('utf-8')
        _received.append(data)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestEventsInvoker(Service):
    """ Drives the events connections under test from inside the server.
    """
    name = 'test.fabric.events.invoke'
    input = 'mode', '-connection', '-event', '-database', '-query'

# ################################################################################################################################

    def _ping(self) -> 'anydict':
        out = {'is_ready': True}
        return out

# ################################################################################################################################

    def _send(self) -> 'anydict':
        connection = self.request.input.connection

        try:
            self.out.kafka[connection].send(self.request.input.event)
        except Exception as e:
            out = {'is_ok': False, 'error': repr(e)}
        else:
            out = {'is_ok': True, 'error': _no_error}

        return out

# ################################################################################################################################

    def _ping_connection(self) -> 'anydict':
        connection = self.request.input.connection

        try:
            self.out.kafka[connection].ping()
        except Exception as e:
            out = {'is_ok': False, 'error': repr(e)}
        else:
            out = {'is_ok': True, 'error': _no_error}

        return out

# ################################################################################################################################

    def _query(self) -> 'anydict':
        connection = self.request.input.connection

        request = {
            'db': self.request.input.database,
            'csl': self.request.input.query,
        }

        conn = self.rest[connection]
        response = conn.post(self.cid, request)
        rows = to_rows(response.data)

        out = {'rows': rows}
        return out

# ################################################################################################################################

    def _get_received(self) -> 'anydict':
        out = {'received': list(_received)}
        return out

# ################################################################################################################################

    def _clear_received(self) -> 'anydict':
        _received.clear()

        out = {'is_cleared': True}
        return out

# ################################################################################################################################

    def handle(self) -> 'None':

        mode = self.request.input.mode

        if handler := _mode_handlers.get(mode):
            out = handler(self)
        else:
            out = {'error': f'Unknown mode `{mode}`'}

        self.response.payload = json.dumps(out)
        self.response.content_type = 'application/json'

# ################################################################################################################################
# ################################################################################################################################

_mode_handlers = {
    'ping':            FabricTestEventsInvoker._ping,
    'send':            FabricTestEventsInvoker._send,
    'ping-connection': FabricTestEventsInvoker._ping_connection,
    'query':           FabricTestEventsInvoker._query,
    'get-received':    FabricTestEventsInvoker._get_received,
    'clear-received':  FabricTestEventsInvoker._clear_received,
}

# ################################################################################################################################
# ################################################################################################################################

class FabricTestListWorkspaces(Service):
    """ Lists all the workspaces through a named Fabric connection.
    """
    name = 'test.fabric.list-workspaces'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        conn = self.microsoft.fabric[conn_name]
        result = conn.list_workspaces()

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestGetWorkspace(Service):
    """ Returns details of a single workspace.
    """
    name = 'test.fabric.get-workspace'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']

        conn = self.microsoft.fabric[conn_name]
        result = conn.get_workspace(workspace_id)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestListItems(Service):
    """ Lists items in a workspace, optionally filtered by their type.
    """
    name = 'test.fabric.list-items'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        item_type = self.request.raw_request['item_type']

        conn = self.microsoft.fabric[conn_name]
        result = conn.list_items(workspace_id, item_type)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestGetItem(Service):
    """ Returns details of a single item.
    """
    name = 'test.fabric.get-item'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        item_id = self.request.raw_request['item_id']

        conn = self.microsoft.fabric[conn_name]
        result = conn.get_item(workspace_id, item_id)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestCreateItem(Service):
    """ Creates a new item in a workspace.
    """
    name = 'test.fabric.create-item'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        item_name = self.request.raw_request['item_name']
        item_type = self.request.raw_request['item_type']

        conn = self.microsoft.fabric[conn_name]
        result = conn.create_item(workspace_id, item_name, item_type)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestUpdateItem(Service):
    """ Updates an item in a workspace.
    """
    name = 'test.fabric.update-item'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        item_id = self.request.raw_request['item_id']
        data = self.request.raw_request['data']

        conn = self.microsoft.fabric[conn_name]
        result = conn.update_item(workspace_id, item_id, data)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestDeleteItem(Service):
    """ Deletes an item from a workspace.
    """
    name = 'test.fabric.delete-item'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        item_id = self.request.raw_request['item_id']

        conn = self.microsoft.fabric[conn_name]
        conn.delete_item(workspace_id, item_id)

        self.response.payload = json.dumps({'ok': True})

# ################################################################################################################################
# ################################################################################################################################

class FabricTestRunJob(Service):
    """ Runs an item's job on demand, e.g. a notebook or a pipeline.
    """
    name = 'test.fabric.run-job'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        item_id = self.request.raw_request['item_id']
        job_type = self.request.raw_request['job_type']

        conn = self.microsoft.fabric[conn_name]
        job_id = conn.run_job(workspace_id, item_id, job_type)

        self.response.payload = json.dumps({'job_id': job_id})

# ################################################################################################################################
# ################################################################################################################################

class FabricTestGetJob(Service):
    """ Returns details of a single job instance.
    """
    name = 'test.fabric.get-job'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        item_id = self.request.raw_request['item_id']
        job_id = self.request.raw_request['job_id']

        conn = self.microsoft.fabric[conn_name]
        result = conn.get_job(workspace_id, item_id, job_id)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestCancelJob(Service):
    """ Cancels a job instance.
    """
    name = 'test.fabric.cancel-job'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        item_id = self.request.raw_request['item_id']
        job_id = self.request.raw_request['job_id']

        conn = self.microsoft.fabric[conn_name]
        conn.cancel_job(workspace_id, item_id, job_id)

        self.response.payload = json.dumps({'ok': True})

# ################################################################################################################################
# ################################################################################################################################

class FabricTestWaitForJob(Service):
    """ Waits until a job instance ends, returning its final state or the error it ended with.
    """
    name = 'test.fabric.wait-for-job'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        item_id = self.request.raw_request['item_id']
        job_id = self.request.raw_request['job_id']
        timeout = self.request.raw_request['timeout']

        conn = self.microsoft.fabric[conn_name]

        try:
            result = conn.wait_for_job(workspace_id, item_id, job_id, timeout=timeout)
        except Exception as e:
            self.response.payload = json.dumps({'error': str(e)})
        else:
            self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestListShortcuts(Service):
    """ Lists OneLake shortcuts of an item.
    """
    name = 'test.fabric.list-shortcuts'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        item_id = self.request.raw_request['item_id']

        conn = self.microsoft.fabric[conn_name]
        result = conn.list_shortcuts(workspace_id, item_id)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestCreateShortcut(Service):
    """ Creates a OneLake shortcut in an item.
    """
    name = 'test.fabric.create-shortcut'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        item_id = self.request.raw_request['item_id']
        data = self.request.raw_request['data']

        conn = self.microsoft.fabric[conn_name]
        result = conn.create_shortcut(workspace_id, item_id, data)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestDeleteShortcut(Service):
    """ Deletes a OneLake shortcut from an item.
    """
    name = 'test.fabric.delete-shortcut'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        item_id = self.request.raw_request['item_id']
        shortcut_path = self.request.raw_request['shortcut_path']
        shortcut_name = self.request.raw_request['shortcut_name']

        conn = self.microsoft.fabric[conn_name]
        conn.delete_shortcut(workspace_id, item_id, shortcut_path, shortcut_name)

        self.response.payload = json.dumps({'ok': True})

# ################################################################################################################################
# ################################################################################################################################

class FabricTestListCapacities(Service):
    """ Lists all the capacities.
    """
    name = 'test.fabric.list-capacities'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        conn = self.microsoft.fabric[conn_name]
        result = conn.list_capacities()

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestOneLakeList(Service):
    """ Lists paths in a workspace's OneLake filesystem.
    """
    name = 'test.fabric.onelake-list'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        directory = self.request.raw_request['directory']

        conn = self.microsoft.fabric[conn_name]
        result = conn.onelake_list(workspace_id, directory)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestOneLakeRead(Service):
    """ Reads a file from a workspace's OneLake filesystem.
    """
    name = 'test.fabric.onelake-read'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        file_path = self.request.raw_request['file_path']

        conn = self.microsoft.fabric[conn_name]
        result = conn.onelake_read(workspace_id, file_path)

        data = result.decode('utf-8')
        self.response.payload = json.dumps({'data': data})

# ################################################################################################################################
# ################################################################################################################################

class FabricTestOneLakeWrite(Service):
    """ Writes a file to a workspace's OneLake filesystem - the data is text or a list of dicts.
    """
    name = 'test.fabric.onelake-write'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        file_path = self.request.raw_request['file_path']
        data = self.request.raw_request['data']

        conn = self.microsoft.fabric[conn_name]
        conn.onelake_write(workspace_id, file_path, data)

        self.response.payload = json.dumps({'ok': True})

# ################################################################################################################################
# ################################################################################################################################

class FabricTestOneLakeDelete(Service):
    """ Deletes a file from a workspace's OneLake filesystem.
    """
    name = 'test.fabric.onelake-delete'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        file_path = self.request.raw_request['file_path']
        recursive = self.request.raw_request.get('recursive')

        if recursive is None:
            recursive = _default_recursive

        conn = self.microsoft.fabric[conn_name]
        conn.onelake_delete(workspace_id, file_path, recursive)

        self.response.payload = json.dumps({'ok': True})

# ################################################################################################################################
# ################################################################################################################################

class FabricTestInvoke(Service):
    """ Invokes any Fabric endpoint through the generic invoke method.
    """
    name = 'test.fabric.invoke'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        method = self.request.raw_request['method']
        path = self.request.raw_request['path']

        conn = self.microsoft.fabric[conn_name]
        result = conn.invoke(method, path)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestPing(Service):
    """ Pings a Fabric connection.
    """
    name = 'test.fabric.ping'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        conn = self.microsoft.fabric[conn_name]
        conn.ping()

        self.response.payload = json.dumps({'ok': True})

# ################################################################################################################################
# ################################################################################################################################

class FabricTestInvalidateToken(Service):
    """ Replaces the API token a connection holds with one Fabric rejects.
    """
    name = 'test.fabric.invalidate-token'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        conn = self.microsoft.fabric[conn_name]
        conn.token = 'invalid'

        self.response.payload = json.dumps({'ok': True})

# ################################################################################################################################
# ################################################################################################################################

class FabricTestListTables(Service):
    """ Lists the tables of a lakehouse.
    """
    name = 'test.fabric.list-tables'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        lakehouse_id = self.request.raw_request['lakehouse_id']

        conn = self.microsoft.fabric[conn_name]
        result = conn.list_tables(workspace_id, lakehouse_id)

        self.response.payload = json.dumps({'tables': result})

# ################################################################################################################################
# ################################################################################################################################

class FabricTestQuery(Service):
    """ Runs a T-SQL query against a lakehouse's SQL analytics endpoint.
    """
    name = 'test.fabric.query'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        lakehouse_id = self.request.raw_request['lakehouse_id']
        sql = self.request.raw_request['sql']
        params = self.request.raw_request.get('params')

        conn = self.microsoft.fabric[conn_name]
        rows = conn.query(workspace_id, lakehouse_id, sql, params)

        # Dates and decimals travel back as strings.
        self.response.payload = json.dumps({'rows': rows}, default=str)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestWriteTable(Service):
    """ Writes rows to a lakehouse table.
    """
    name = 'test.fabric.write-table'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        lakehouse_id = self.request.raw_request['lakehouse_id']
        table_name = self.request.raw_request['table_name']
        rows = self.request.raw_request['rows']

        conn = self.microsoft.fabric[conn_name]
        result = conn.write_table(workspace_id, lakehouse_id, table_name, rows)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestRefreshSQLEndpoint(Service):
    """ Refreshes the SQL analytics endpoint's view of a lakehouse's tables.
    """
    name = 'test.fabric.refresh-sql-endpoint'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        lakehouse_id = self.request.raw_request['lakehouse_id']
        table_names = self.request.raw_request.get('table_names')

        conn = self.microsoft.fabric[conn_name]
        result = conn.refresh_sql_endpoint(workspace_id, lakehouse_id, table_names)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestDisposeSQLPools(Service):
    """ Closes the connections a connection holds to SQL analytics endpoints.
    """
    name = 'test.fabric.dispose-sql-pools'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        conn = self.microsoft.fabric[conn_name]
        conn.dispose_sql_pools()

        self.response.payload = json.dumps({'ok': True})

# ################################################################################################################################
# ################################################################################################################################
