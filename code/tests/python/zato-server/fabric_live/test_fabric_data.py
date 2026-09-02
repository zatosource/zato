# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# Zato - test helpers
import _fabric_lakehouse
from _admin_client import AdminClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The main connection with valid credentials
_conn_name = 'test.fabric.main'

# The workspace and the lakehouse the simulated tenant starts with
_workspace_id = 'workspace-sales-analytics'
_lakehouse_id = 'item-sales-lakehouse'

# ################################################################################################################################
# ################################################################################################################################

class TestFabricTables:

    def _get_client(self, zato_server:'anydict') -> 'AdminClient':
        out = AdminClient(zato_server['base_url'], zato_server['invoke_password'])
        return out

# ################################################################################################################################

    def test_list_tables(self, zato_server:'anydict') -> 'None':
        """ The tables the lakehouse starts with are returned.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.fabric.list-tables', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'lakehouse_id': _lakehouse_id,
        })

        tables = result['tables']
        table_names = {table['name'] for table in tables}

        assert 'regions' in table_names

# ################################################################################################################################

    def test_load_table(self, zato_server:'anydict') -> 'None':
        """ A OneLake file can be loaded into a table and the load runs to completion.
        """
        client = self._get_client(zato_server)

        # Write the file to load ..
        file_data = 'order_id,amount\nORD-001,250.00\nORD-002,99.90\n'

        result = client.invoke('test.fabric.onelake-write', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'file_path': f'{_lakehouse_id}/Files/incoming/orders.csv',
            'data': file_data,
        })
        assert result['ok'] is True

        # .. load it into a table, waiting until the load completes ..
        result = client.invoke('test.fabric.load-table', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'lakehouse_id': _lakehouse_id,
            'table_name': 'orders',
            'relative_path': 'Files/incoming/orders.csv',
        })
        assert result['status'] == 'Succeeded'

        # .. and confirm the new table is listed now.
        result = client.invoke('test.fabric.list-tables', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'lakehouse_id': _lakehouse_id,
        })
        table_names = {table['name'] for table in result['tables']}
        assert 'orders' in table_names

# ################################################################################################################################

    def test_write_table(self, zato_server:'anydict') -> 'None':
        """ A list of dicts becomes a table - the rows travel through OneLake and one load turns them into data.
        """
        client = self._get_client(zato_server)

        rows = [
            {'region': 'EMEA', 'total': 1250.5},
            {'region': 'APAC', 'total': 875.25},
        ]

        # Write the rows ..
        result = client.invoke('test.fabric.write-table', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'lakehouse_id': _lakehouse_id,
            'table_name': 'daily_totals',
            'rows': rows,
        })
        assert result['status'] == 'Succeeded'

        # .. and confirm the new table is listed now.
        result = client.invoke('test.fabric.list-tables', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'lakehouse_id': _lakehouse_id,
        })
        table_names = {table['name'] for table in result['tables']}
        assert 'daily_totals' in table_names

# ################################################################################################################################
# ################################################################################################################################

class TestFabricQuery:

    def _get_client(self, zato_server:'anydict') -> 'AdminClient':
        out = AdminClient(zato_server['base_url'], zato_server['invoke_password'])
        return out

# ################################################################################################################################

    def test_query(self, zato_server:'anydict') -> 'None':
        """ An SQL query returns its rows as a list of dicts keyed by column names.
        """
        client = self._get_client(zato_server)

        result = client.invoke('test.fabric.query', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'lakehouse_id': _lakehouse_id,
            'sql': 'select region, total from daily_totals',
        })

        rows = result['rows']

        assert rows == [
            {'region': 'EMEA', 'total': 1250.5},
            {'region': 'APAC', 'total': 875.25},
        ]

# ################################################################################################################################

    def test_query_reuses_the_session(self, zato_server:'anydict') -> 'None':
        """ Two queries against the same lakehouse share one Spark session.
        """
        client = self._get_client(zato_server)

        # Run the first query and note how many sessions exist afterwards ..
        result = client.invoke('test.fabric.query', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'lakehouse_id': _lakehouse_id,
            'sql': 'select region, total from daily_totals',
        })
        assert result['rows']

        session_count = _fabric_lakehouse.state.session_count

        # .. run the second one ..
        result = client.invoke('test.fabric.query', {
            'conn_name': _conn_name,
            'workspace_id': _workspace_id,
            'lakehouse_id': _lakehouse_id,
            'sql': 'select region, total from daily_totals where total > 1000',
        })
        assert result['rows']

        # .. and confirm no new session was opened for it.
        assert _fabric_lakehouse.state.session_count == session_count

# ################################################################################################################################
# ################################################################################################################################
