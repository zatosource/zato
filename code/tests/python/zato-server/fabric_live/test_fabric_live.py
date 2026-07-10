# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# PyPI
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.fabric_live')

# The main connection with valid credentials
_conn_name = 'test.fabric.main'

# The connection whose client secret the token endpoint rejects
_bad_credentials_conn_name = 'test.fabric.bad-credentials'

# The workspace the simulated tenant starts with
_workspace_id = 'workspace-sales-analytics'

# ################################################################################################################################
# ################################################################################################################################

class _AdminClient:
    """ Minimal admin client for invoking Zato services.
    """

    def __init__(self, base_url:'str', password:'str') -> 'None':
        self.base_url = base_url
        self.password = password

    def invoke(self, service_name:'str', payload:'anydict') -> 'anydict':
        from base64 import b64encode
        from urllib.error import HTTPError
        from urllib.request import Request, urlopen

        url = f'{self.base_url}/zato/api/invoke/{service_name}'
        body = json.dumps(payload).encode()

        credentials = f'admin.invoke:{self.password}'
        auth = b64encode(credentials.encode()).decode()

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {auth}')
        request.add_header('Content-Type', 'application/json')

        try:
            with urlopen(request) as response:
                raw = response.read()
        except HTTPError as error:
            raw = error.read()
            error_text = raw.decode('utf-8', errors='replace')
            raise Exception(f'{service_name} returned HTTP {error.code}: {error_text}')

        if not raw:
            return {}

        out = json.loads(raw)
        return out

# ################################################################################################################################
# ################################################################################################################################

class TestFabricWorkspaces:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_list_workspaces(self, zato_server:'anydict') -> 'None':
        """ All the workspaces in the tenant are returned.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.fabric.list-workspaces', {
            'conn_name': _conn_name,
        })

        workspaces = result['value']
        workspace_ids = {workspace['id'] for workspace in workspaces}

        assert _workspace_id in workspace_ids
        assert 'workspace-finance' in workspace_ids

        # Check that a workspace carries its full details ..
        for workspace in workspaces:
            if workspace['id'] == _workspace_id:
                assert workspace['displayName'] == 'Sales analytics'
                assert workspace['capacityId'] == 'capacity-main'

# ################################################################################################################################

    def test_get_workspace(self, zato_server:'anydict') -> 'None':
        """ A single workspace is returned with its details.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.fabric.get-workspace', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
        })

        assert result['id'] == _workspace_id
        assert result['displayName'] == 'Sales analytics'

# ################################################################################################################################

    def test_get_workspace_not_found(self, zato_server:'anydict') -> 'None':
        """ Asking for a workspace that does not exist raises an error.
        """
        client = self._get_client(zato_server)

        with pytest.raises(Exception) as exception_info:
            _ = client.invoke('test.fabric.get-workspace', {
                'conn_name': _conn_name,
                'workspace_id': 'workspace-does-not-exist',
            })

        assert 'HTTP' in str(exception_info.value)

# ################################################################################################################################

    def test_create_and_delete_workspace(self, zato_server:'anydict') -> 'None':
        """ A new workspace can be created and deleted again.
        """
        client = self._get_client(zato_server)

        # Create a new workspace ..
        result = client.invoke('test.fabric.create-workspace', {
            'conn_name': _conn_name,
            'workspace_name': 'Marketing analytics',
        })

        workspace_id = result['id']
        assert result['displayName'] == 'Marketing analytics'

        # .. confirm it can be read back ..
        result = client.invoke('test.fabric.get-workspace', {
            'conn_name': _conn_name,
            'workspace_id': workspace_id,
        })
        assert result['displayName'] == 'Marketing analytics'

        # .. delete it ..
        result = client.invoke('test.fabric.delete-workspace', {
            'conn_name': _conn_name,
            'workspace_id': workspace_id,
        })
        assert result['ok'] is True

        # .. and confirm it is gone now.
        with pytest.raises(Exception):
            _ = client.invoke('test.fabric.get-workspace', {
                'conn_name': _conn_name,
                'workspace_id': workspace_id,
            })

# ################################################################################################################################
# ################################################################################################################################

class TestFabricItems:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_list_items(self, zato_server:'anydict') -> 'None':
        """ All the items in a workspace are returned.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.fabric.list-items', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_type': '',
        })

        items = result['value']
        item_ids = {item['id'] for item in items}

        assert 'item-sales-lakehouse' in item_ids
        assert 'item-daily-load-notebook' in item_ids
        assert 'item-sales-pipeline' in item_ids

# ################################################################################################################################

    def test_list_items_filtered_by_type(self, zato_server:'anydict') -> 'None':
        """ Items can be filtered by their type.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.fabric.list-items', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_type': 'Notebook',
        })

        items = result['value']

        assert len(items) == 1
        assert items[0]['id'] == 'item-daily-load-notebook'

# ################################################################################################################################

    def test_get_item(self, zato_server:'anydict') -> 'None':
        """ A single item is returned with its details.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.fabric.get-item', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_id': 'item-sales-lakehouse',
        })

        assert result['displayName'] == 'Sales lakehouse'
        assert result['type'] == 'Lakehouse'

# ################################################################################################################################

    def test_create_update_delete_item(self, zato_server:'anydict') -> 'None':
        """ An item can be created, updated and deleted.
        """
        client = self._get_client(zato_server)

        # Create a new notebook ..
        result = client.invoke('test.fabric.create-item', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_name': 'Weekly summary notebook',
            'item_type': 'Notebook',
        })

        item_id = result['id']
        assert result['displayName'] == 'Weekly summary notebook'
        assert result['type'] == 'Notebook'

        # .. update its display name ..
        result = client.invoke('test.fabric.update-item', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_id': item_id,
            'data': {'displayName': 'Weekly summary notebook v2'},
        })
        assert result['displayName'] == 'Weekly summary notebook v2'

        # .. confirm the update is visible on read ..
        result = client.invoke('test.fabric.get-item', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_id': item_id,
        })
        assert result['displayName'] == 'Weekly summary notebook v2'

        # .. delete it ..
        result = client.invoke('test.fabric.delete-item', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_id': item_id,
        })
        assert result['ok'] is True

        # .. and confirm it is gone now.
        with pytest.raises(Exception):
            _ = client.invoke('test.fabric.get-item', {
                'conn_name': _conn_name,
                'workspace_id': _workspace_id,
                'item_id': item_id,
            })

# ################################################################################################################################
# ################################################################################################################################

class TestFabricJobs:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_run_and_get_job(self, zato_server:'anydict') -> 'None':
        """ Running a notebook job starts a new job instance that can be read back.
        """
        client = self._get_client(zato_server)

        # Start a new job ..
        result = client.invoke('test.fabric.run-job', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_id': 'item-daily-load-notebook',
            'job_type': 'RunNotebook',
        })

        job_id = result['id']
        assert result['status'] == 'InProgress'
        assert result['jobType'] == 'RunNotebook'

        # .. and read it back.
        result = client.invoke('test.fabric.get-job', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_id': 'item-daily-load-notebook',
            'job_id': job_id,
        })

        assert result['id'] == job_id
        assert result['status'] == 'InProgress'

# ################################################################################################################################

    def test_get_existing_job(self, zato_server:'anydict') -> 'None':
        """ The job history the tenant starts with is visible.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.fabric.get-job', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_id': 'item-daily-load-notebook',
            'job_id': 'job-notebook-001',
        })

        assert result['status'] == 'Completed'
        assert result['jobType'] == 'RunNotebook'

# ################################################################################################################################

    def test_cancel_job(self, zato_server:'anydict') -> 'None':
        """ Cancelling a job changes its status to Cancelled.
        """
        client = self._get_client(zato_server)

        # Start a job that will be cancelled ..
        result = client.invoke('test.fabric.run-job', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_id': 'item-sales-pipeline',
            'job_type': 'Pipeline',
        })
        job_id = result['id']

        # .. cancel it ..
        result = client.invoke('test.fabric.cancel-job', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_id': 'item-sales-pipeline',
            'job_id': job_id,
        })
        assert result['ok'] is True

        # .. and confirm the status changed.
        result = client.invoke('test.fabric.get-job', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_id': 'item-sales-pipeline',
            'job_id': job_id,
        })
        assert result['status'] == 'Cancelled'

# ################################################################################################################################
# ################################################################################################################################

class TestFabricShortcuts:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_list_shortcuts(self, zato_server:'anydict') -> 'None':
        """ The shortcuts the tenant starts with are returned.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.fabric.list-shortcuts', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_id': 'item-sales-lakehouse',
        })

        shortcuts = result['value']
        shortcut_names = {shortcut['name'] for shortcut in shortcuts}

        assert 'external-orders' in shortcut_names

# ################################################################################################################################

    def test_create_and_delete_shortcut(self, zato_server:'anydict') -> 'None':
        """ A shortcut can be created and deleted again.
        """
        client = self._get_client(zato_server)

        shortcut = {
            'name': 'external-invoices',
            'path': 'Files',
            'target': {
                'adlsGen2': {
                    'url': 'https://example.dfs.core.windows.net',
                    'subpath': '/invoices',
                },
            },
        }

        # Create a new shortcut ..
        result = client.invoke('test.fabric.create-shortcut', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_id': 'item-sales-lakehouse',
            'data': shortcut,
        })
        assert result['name'] == 'external-invoices'

        # .. confirm it shows up in the list ..
        result = client.invoke('test.fabric.list-shortcuts', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_id': 'item-sales-lakehouse',
        })
        shortcut_names = {item['name'] for item in result['value']}
        assert 'external-invoices' in shortcut_names

        # .. delete it ..
        result = client.invoke('test.fabric.delete-shortcut', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_id': 'item-sales-lakehouse',
            'shortcut_path': 'Files',
            'shortcut_name': 'external-invoices',
        })
        assert result['ok'] is True

        # .. and confirm it is gone now.
        result = client.invoke('test.fabric.list-shortcuts', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'item_id': 'item-sales-lakehouse',
        })
        shortcut_names = {item['name'] for item in result['value']}
        assert 'external-invoices' not in shortcut_names

# ################################################################################################################################
# ################################################################################################################################

class TestFabricCapacities:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_list_capacities(self, zato_server:'anydict') -> 'None':
        """ All the capacities in the tenant are returned.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.fabric.list-capacities', {
            'conn_name': _conn_name,
        })

        capacities = result['value']
        capacity_ids = {capacity['id'] for capacity in capacities}

        assert 'capacity-main' in capacity_ids

# ################################################################################################################################
# ################################################################################################################################

class TestFabricOneLake:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_onelake_list(self, zato_server:'anydict') -> 'None':
        """ The files the tenant's OneLake starts with are listed.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.fabric.onelake-list', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'directory': '',
        })

        paths = result['paths']
        path_names = {path['name'] for path in paths}

        assert 'item-sales-lakehouse/Files/reference/regions.csv' in path_names

# ################################################################################################################################

    def test_onelake_read(self, zato_server:'anydict') -> 'None':
        """ A OneLake file can be read.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.fabric.onelake-read', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'file_path': 'item-sales-lakehouse/Files/reference/regions.csv',
        })

        assert 'EMEA,Europe' in result['data']

# ################################################################################################################################

    def test_onelake_write_read_delete(self, zato_server:'anydict') -> 'None':
        """ A OneLake file can be written, read back and deleted.
        """
        client = self._get_client(zato_server)

        file_path = 'item-sales-lakehouse/Files/exports/daily-summary.csv'
        file_data = 'date,total\n2026-07-10,18250.75\n'

        # Write a new file ..
        result = client.invoke('test.fabric.onelake-write', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'file_path': file_path,
            'data': file_data,
        })
        assert result['ok'] is True

        # .. read it back and compare ..
        result = client.invoke('test.fabric.onelake-read', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'file_path': file_path,
        })
        assert result['data'] == file_data

        # .. list it under its directory ..
        result = client.invoke('test.fabric.onelake-list', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'directory': 'item-sales-lakehouse/Files/exports',
        })
        path_names = {path['name'] for path in result['paths']}
        assert file_path in path_names

        # .. delete it ..
        result = client.invoke('test.fabric.onelake-delete', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'file_path': file_path,
        })
        assert result['ok'] is True

        # .. and confirm it is gone now.
        with pytest.raises(Exception):
            _ = client.invoke('test.fabric.onelake-read', {
                'conn_name': _conn_name,
                'workspace_id': _workspace_id,
                'file_path': file_path,
            })

# ################################################################################################################################
# ################################################################################################################################

class TestFabricInvoke:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_generic_invoke(self, zato_server:'anydict') -> 'None':
        """ Any endpoint can be invoked through the generic invoke method.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.fabric.invoke', {
            'conn_name': _conn_name,
            'method': 'GET',
            'path': f'/workspaces/{_workspace_id}/items',
        })

        items = result['value']
        item_ids = {item['id'] for item in items}

        assert 'item-sales-lakehouse' in item_ids

# ################################################################################################################################
# ################################################################################################################################

class TestFabricPing:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_ping(self, zato_server:'anydict') -> 'None':
        """ .ping() succeeds against the live tenant.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.fabric.ping', {
            'conn_name': _conn_name,
        })

        assert result['ok'] is True

# ################################################################################################################################
# ################################################################################################################################

class TestFabricSecurity:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_bad_credentials_are_rejected(self, zato_server:'anydict') -> 'None':
        """ A connection with an invalid client secret cannot obtain a token.
        """
        client = self._get_client(zato_server)

        with pytest.raises(Exception) as exception_info:
            _ = client.invoke('test.fabric.list-workspaces', {
                'conn_name': _bad_credentials_conn_name,
            })

        assert 'HTTP' in str(exception_info.value)

# ################################################################################################################################

    def test_token_refresh_after_invalidation(self, zato_server:'anydict') -> 'None':
        """ When the token a client holds is invalidated server-side, the client transparently obtains
        a new one and retries, so the caller never notices.
        """
        from _fabric_server import FabricTestHandler

        client = self._get_client(zato_server)

        # First, make a call so the connection holds a token ..
        result = client.invoke('test.fabric.list-workspaces', {
            'conn_name': _conn_name,
        })
        assert 'value' in result

        # .. now invalidate all the tokens the tenant has issued ..
        FabricTestHandler.invalidate_tokens()

        # .. and confirm the next call still succeeds - the connection re-authenticated on its own.
        result = client.invoke('test.fabric.list-workspaces', {
            'conn_name': _conn_name,
        })

        workspaces = result['value']
        workspace_ids = {workspace['id'] for workspace in workspaces}

        assert _workspace_id in workspace_ids

# ################################################################################################################################
# ################################################################################################################################
