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

class FabricTestCreateWorkspace(Service):
    """ Creates a new workspace.
    """
    name = 'test.fabric.create-workspace'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_name = self.request.raw_request['workspace_name']

        conn = self.microsoft.fabric[conn_name]
        result = conn.create_workspace(workspace_name)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class FabricTestDeleteWorkspace(Service):
    """ Deletes a workspace.
    """
    name = 'test.fabric.delete-workspace'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']

        conn = self.microsoft.fabric[conn_name]
        conn.delete_workspace(workspace_id)

        self.response.payload = json.dumps({'ok': True})

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
        result = conn.run_job(workspace_id, item_id, job_type)

        self.response.payload = json.dumps(result)

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
    """ Writes a file to a workspace's OneLake filesystem.
    """
    name = 'test.fabric.onelake-write'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        workspace_id = self.request.raw_request['workspace_id']
        file_path = self.request.raw_request['file_path']
        data = self.request.raw_request['data']

        conn = self.microsoft.fabric[conn_name]
        conn.onelake_write(workspace_id, file_path, data.encode('utf-8'))

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

        conn = self.microsoft.fabric[conn_name]
        conn.onelake_delete(workspace_id, file_path)

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
