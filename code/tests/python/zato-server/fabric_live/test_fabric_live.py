# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager

# Live Fabric
from live_fabric.common import ModuleCtx as FabricCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import FabricLiveEnvironment
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The connection with valid credentials
    Connection_Name = 'test.fabric.main'

    # The connection whose client secret the token endpoint rejects
    Bad_Credentials_Connection_Name = 'test.fabric.bad-credentials'

    # A workspace ID no tenant has
    Missing_Workspace_ID = '00000000-0000-0000-0000-000000000000'

    # A file the tests write and remove under Files/exports/
    Export_File_Prefix = 'Files/exports/zato-test-'

# ################################################################################################################################
# ################################################################################################################################

def _invoke(fabric_live:'FabricLiveEnvironment', service:'str', **fields:'object') -> 'anydict':
    """ One call to a service deployed to the test server, through the main connection.
    """
    request = {'conn_name': ModuleCtx.Connection_Name, **fields}

    client = fabric_live.zato.client()
    out = client.invoke(service, request)

    return out

# ################################################################################################################################

def _values_of(items:'anylist', key:'str') -> 'strlist':
    """ The value of one key across a list of dicts.
    """
    out:'strlist' = []

    for item in items:
        out.append(item[key])

    return out

# ################################################################################################################################

def _find_item(fabric_live:'FabricLiveEnvironment', name:'str', item_type:'str') -> 'anydict':
    """ The item of that name and type in the workspace.
    """
    result = _invoke(fabric_live, 'test.fabric.list-items',
        workspace_id=fabric_live.fabric.workspace_id, item_type=item_type)

    for item in result['value']:
        if item['displayName'] == name:
            out = item
            break
    else:
        raise Exception(f'{item_type} {name} not found')

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module', autouse=True)
def deployed(deployed_client:'AdminClient') -> 'None':
    pass

# ################################################################################################################################
# ################################################################################################################################

class TestFabricWorkspaces:

    def test_list_workspaces(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ The workspace the setup built is among the ones the principal sees.
        """
        result = _invoke(fabric_live, 'test.fabric.list-workspaces')

        workspaces = result['value']
        by_id:'anydict' = {}
        for workspace in workspaces:
            by_id[workspace['id']] = workspace

        workspace = by_id[fabric_live.fabric.workspace_id]

        assert workspace['displayName'] == FabricCtx.Workspace_Name
        assert workspace['capacityId'] == fabric_live.fabric.capacity_id

# ################################################################################################################################

    def test_get_workspace(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ A single workspace is returned with its details.
        """
        result = _invoke(fabric_live, 'test.fabric.get-workspace', workspace_id=fabric_live.fabric.workspace_id)

        assert result['id'] == fabric_live.fabric.workspace_id
        assert result['displayName'] == FabricCtx.Workspace_Name

# ################################################################################################################################

    def test_get_workspace_not_found(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ Asking for a workspace that does not exist raises an error.
        """
        with pytest.raises(Exception) as exception_info:
            _ = _invoke(fabric_live, 'test.fabric.get-workspace', workspace_id=ModuleCtx.Missing_Workspace_ID)

        assert 'HTTP' in str(exception_info.value)

# ################################################################################################################################
# ################################################################################################################################

class TestFabricItems:

    def test_list_items(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ The lakehouse the setup built is among the workspace's items.
        """
        item = _find_item(fabric_live, FabricCtx.Lakehouse_Name, 'Lakehouse')

        assert item['id'] == fabric_live.fabric.lakehouse_id
        assert item['type'] == 'Lakehouse'

# ################################################################################################################################

    def test_list_items_filtered_by_type(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ Items can be filtered by their type.
        """
        result = _invoke(fabric_live, 'test.fabric.list-items',
            workspace_id=fabric_live.fabric.workspace_id, item_type='Lakehouse')

        items = result['value']

        assert items
        for item in items:
            assert item['type'] == 'Lakehouse'

# ################################################################################################################################

    def test_get_item(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ A single item is returned with its details.
        """
        result = _invoke(fabric_live, 'test.fabric.get-item',
            workspace_id=fabric_live.fabric.workspace_id, item_id=fabric_live.fabric.lakehouse_id)

        assert result['displayName'] == FabricCtx.Lakehouse_Name
        assert result['type'] == 'Lakehouse'

# ################################################################################################################################

    def test_create_update_delete_item(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ A throwaway notebook can be created, renamed and deleted.
        """
        workspace_id = fabric_live.fabric.workspace_id
        suffix = CryptoManager.generate_hex_string()
        name = f'zato-test-{suffix}'
        new_name = f'{name}-v2'

        # Create a new notebook ..
        result = _invoke(fabric_live, 'test.fabric.create-item',
            workspace_id=workspace_id, item_name=name, item_type='Notebook')

        item_id = result['id']
        assert result['displayName'] == name
        assert result['type'] == 'Notebook'

        # .. rename it ..
        result = _invoke(fabric_live, 'test.fabric.update-item',
            workspace_id=workspace_id, item_id=item_id, data={'displayName': new_name})
        assert result['displayName'] == new_name

        # .. confirm the change is visible on read ..
        result = _invoke(fabric_live, 'test.fabric.get-item', workspace_id=workspace_id, item_id=item_id)
        assert result['displayName'] == new_name

        # .. delete it ..
        result = _invoke(fabric_live, 'test.fabric.delete-item', workspace_id=workspace_id, item_id=item_id)
        assert result['ok'] is True

        # .. and confirm it is gone now.
        with pytest.raises(Exception):
            _ = _invoke(fabric_live, 'test.fabric.get-item', workspace_id=workspace_id, item_id=item_id)

# ################################################################################################################################
# ################################################################################################################################

class TestFabricJobs:

    def test_run_get_and_cancel_job(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ Running the reminder candidates notebook starts a job that can be read back and cancelled.
        """
        workspace_id = fabric_live.fabric.workspace_id
        notebook_id = fabric_live.fabric.state['reminder_notebook_id']

        # Start a new job ..
        result = _invoke(fabric_live, 'test.fabric.run-job',
            workspace_id=workspace_id, item_id=notebook_id, job_type='RunNotebook')

        job_id = result['job_id']

        # .. read it back ..
        result = _invoke(fabric_live, 'test.fabric.get-job',
            workspace_id=workspace_id, item_id=notebook_id, job_id=job_id)

        assert result['id'] == job_id
        assert result['jobType'] == 'RunNotebook'

        # .. and cancel it so the capacity is not kept busy.
        result = _invoke(fabric_live, 'test.fabric.cancel-job',
            workspace_id=workspace_id, item_id=notebook_id, job_id=job_id)
        assert result['ok'] is True

# ################################################################################################################################
# ################################################################################################################################

class TestFabricShortcuts:

    def test_list_shortcuts(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ The lakehouse's shortcuts can be listed, even when there are none.
        """
        result = _invoke(fabric_live, 'test.fabric.list-shortcuts',
            workspace_id=fabric_live.fabric.workspace_id, item_id=fabric_live.fabric.lakehouse_id)

        assert 'value' in result

# ################################################################################################################################

    def test_create_and_delete_shortcut(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ A shortcut from Files to the lakehouse's own Tables can be created and deleted again.
        """
        workspace_id = fabric_live.fabric.workspace_id
        lakehouse_id = fabric_live.fabric.lakehouse_id
        suffix = CryptoManager.generate_hex_string()
        name = f'zato-test-{suffix}'

        shortcut = {
            'name': name,
            'path': 'Files',
            'target': {
                'oneLake': {
                    'workspaceId': workspace_id,
                    'itemId': lakehouse_id,
                    'path': 'Tables/locations',
                },
            },
        }

        # Create a new shortcut ..
        result = _invoke(fabric_live, 'test.fabric.create-shortcut',
            workspace_id=workspace_id, item_id=lakehouse_id, data=shortcut)
        assert result['name'] == name

        # .. confirm it shows up in the list ..
        result = _invoke(fabric_live, 'test.fabric.list-shortcuts', workspace_id=workspace_id, item_id=lakehouse_id)
        names = _values_of(result['value'], 'name')
        assert name in names

        # .. delete it ..
        result = _invoke(fabric_live, 'test.fabric.delete-shortcut',
            workspace_id=workspace_id, item_id=lakehouse_id, shortcut_path='Files', shortcut_name=name)
        assert result['ok'] is True

        # .. and confirm it is gone now.
        result = _invoke(fabric_live, 'test.fabric.list-shortcuts', workspace_id=workspace_id, item_id=lakehouse_id)
        names = _values_of(result['value'], 'name')
        assert name not in names

# ################################################################################################################################
# ################################################################################################################################

class TestFabricCapacities:

    def test_list_capacities(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ The capacity the workspace runs on is among the ones the principal sees.
        """
        result = _invoke(fabric_live, 'test.fabric.list-capacities')

        by_id:'anydict' = {}
        for capacity in result['value']:
            by_id[capacity['id']] = capacity

        capacity = by_id[fabric_live.fabric.capacity_id]
        assert capacity['displayName'] == FabricCtx.Capacity_Name

# ################################################################################################################################
# ################################################################################################################################

class TestFabricOneLake:

    def test_onelake_list(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ The incoming file the setup wrote is listed.
        """
        lakehouse_id = fabric_live.fabric.lakehouse_id
        incoming_file = fabric_live.fabric.state['incoming_file']

        result = _invoke(fabric_live, 'test.fabric.onelake-list',
            workspace_id=fabric_live.fabric.workspace_id, directory=f'{lakehouse_id}/{FabricCtx.Incoming_Folder}')

        names = _values_of(result['paths'], 'name')

        assert f'{lakehouse_id}/{incoming_file}' in names

# ################################################################################################################################

    def test_onelake_read(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ The incoming file the setup wrote can be read.
        """
        lakehouse_id = fabric_live.fabric.lakehouse_id
        incoming_file = fabric_live.fabric.state['incoming_file']

        result = _invoke(fabric_live, 'test.fabric.onelake-read',
            workspace_id=fabric_live.fabric.workspace_id, file_path=f'{lakehouse_id}/{incoming_file}')

        assert result['data'].startswith('invoice_id,insurer,location,amount,status,sent_at')

# ################################################################################################################################

    def test_onelake_write_read_delete(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ A file under Files/exports/ can be written, read back and deleted.
        """
        workspace_id = fabric_live.fabric.workspace_id
        lakehouse_id = fabric_live.fabric.lakehouse_id
        suffix = CryptoManager.generate_hex_string()

        file_path = f'{lakehouse_id}/{ModuleCtx.Export_File_Prefix}{suffix}.csv'
        file_data = 'date,total\n2026-07-10,18250.75\n'

        # Write a new file ..
        result = _invoke(fabric_live, 'test.fabric.onelake-write',
            workspace_id=workspace_id, file_path=file_path, data=file_data)
        assert result['ok'] is True

        # .. read it back and compare ..
        result = _invoke(fabric_live, 'test.fabric.onelake-read', workspace_id=workspace_id, file_path=file_path)
        assert result['data'] == file_data

        # .. list it under its directory ..
        result = _invoke(fabric_live, 'test.fabric.onelake-list',
            workspace_id=workspace_id, directory=f'{lakehouse_id}/{FabricCtx.Exports_Folder}')
        names = _values_of(result['paths'], 'name')
        assert file_path in names

        # .. delete it ..
        result = _invoke(fabric_live, 'test.fabric.onelake-delete', workspace_id=workspace_id, file_path=file_path)
        assert result['ok'] is True

        # .. and confirm it is gone now.
        with pytest.raises(Exception):
            _ = _invoke(fabric_live, 'test.fabric.onelake-read', workspace_id=workspace_id, file_path=file_path)

# ################################################################################################################################
# ################################################################################################################################

class TestFabricInvoke:

    def test_generic_invoke(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ Any endpoint can be invoked through the generic invoke method.
        """
        workspace_id = fabric_live.fabric.workspace_id

        result = _invoke(fabric_live, 'test.fabric.invoke', method='GET', path=f'/workspaces/{workspace_id}/items')

        ids = _values_of(result['value'], 'id')

        assert fabric_live.fabric.lakehouse_id in ids

# ################################################################################################################################
# ################################################################################################################################

class TestFabricPing:

    def test_ping(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ .ping() succeeds against the real tenant.
        """
        result = _invoke(fabric_live, 'test.fabric.ping')

        assert result['ok'] is True

# ################################################################################################################################
# ################################################################################################################################

class TestFabricSecurity:

    def test_bad_credentials_are_rejected(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ A connection with an invalid client secret cannot obtain a token.
        """
        client = fabric_live.zato.client()

        with pytest.raises(Exception) as exception_info:
            _ = client.invoke('test.fabric.list-workspaces', {'conn_name': ModuleCtx.Bad_Credentials_Connection_Name})

        assert 'HTTP' in str(exception_info.value)

# ################################################################################################################################

    def test_token_refresh_after_invalidation(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ When the token a connection holds is invalid, the next call obtains a new one and succeeds.
        """
        # First, make a call so the connection holds a token ..
        result = _invoke(fabric_live, 'test.fabric.list-workspaces')
        assert 'value' in result

        # .. replace it with one Fabric rejects ..
        result = _invoke(fabric_live, 'test.fabric.invalidate-token')
        assert result['ok'] is True

        # .. and confirm the next call still succeeds.
        result = _invoke(fabric_live, 'test.fabric.list-workspaces')

        ids = _values_of(result['value'], 'id')

        assert fabric_live.fabric.workspace_id in ids

# ################################################################################################################################
# ################################################################################################################################
