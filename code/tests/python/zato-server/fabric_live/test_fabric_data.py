# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# pytest
import pytest

# Zato
from zato.common.api import MicrosoftFabric
from zato.common.crypto.api import CryptoManager

# Live Fabric
from live_fabric.common import ModuleCtx as FabricCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import FabricLiveEnvironment
    from zato.common.typing_ import anydict, anydictnone, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

_sync_status = MicrosoftFabric.Sync_Status

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The connection with valid credentials
    Connection_Name = 'test.fabric.main'

    # The open admissions at Riverside in the sample data, in admission ID order
    Riverside_Admissions = ['ADM-0058', 'ADM-0061']

    # Occupied beds per location on the last day of the sample data
    Occupancy_Date = '2026-08-31'
    Occupied_Beds  = {'Maple Grove': 37, 'Oak Hill': 60, 'Riverside': 96}

    # A query on a pooled connection must complete within this many seconds.
    Pooled_Query_Seconds = 2.0

    # Tables the tests write are named with this prefix.
    Test_Table_Prefix = 'zato_test_'

    # Open admissions at one location, with markers for the location and the status
    Admissions_SQL = '''
    select admission_id, location, admitted_at
    from admissions
    where location = :location
    and status = :status
    order by admission_id
    '''

    # The same query with the two values written in
    Admissions_Literal_SQL = '''
    select admission_id, location, admitted_at
    from admissions
    where location = 'Riverside'
    and status = 'admitted'
    order by admission_id
    '''

# ################################################################################################################################
# ################################################################################################################################

def _invoke(fabric_live:'FabricLiveEnvironment', service:'str', **fields:'object') -> 'anydict':
    """ One call to a service deployed to the test server, against the lakehouse the setup built.
    """
    request = {
        'conn_name': ModuleCtx.Connection_Name,
        'workspace_id': fabric_live.fabric.workspace_id,
        'lakehouse_id': fabric_live.fabric.lakehouse_id,
        **fields,
    }

    client = fabric_live.zato.client()
    out = client.invoke(service, request)

    return out

# ################################################################################################################################

def _table_names(fabric_live:'FabricLiveEnvironment') -> 'strlist':
    """ The names of the lakehouse's tables.
    """
    result = _invoke(fabric_live, 'test.fabric.list-tables')

    out:'strlist' = []
    for table in result['tables']:
        out.append(table['name'])

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestFabricTables:

    def test_list_tables(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ The sample tables the setup wrote are all listed.
        """
        names = _table_names(fabric_live)

        for table_name in FabricCtx.Tables:
            assert table_name in names

# ################################################################################################################################
# ################################################################################################################################

def _query(fabric_live:'FabricLiveEnvironment', sql:'str', params:'anydictnone'=None) -> 'dictlist':
    """ Runs a query through the connection and returns its rows.
    """
    result = _invoke(fabric_live, 'test.fabric.query', sql=sql, params=params)

    out = result['rows']
    return out

# ################################################################################################################################

def _admission_ids(rows:'dictlist') -> 'strlist':
    """ The admission IDs of a query's rows, in the order returned.
    """
    out:'strlist' = []
    for row in rows:
        out.append(row['admission_id'])

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestFabricQuery:

    def test_query_open_admissions(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ The query with its values written in returns exactly the two open admissions at Riverside, in admission ID order.
        """
        rows = _query(fabric_live, ModuleCtx.Admissions_Literal_SQL)

        assert _admission_ids(rows) == ModuleCtx.Riverside_Admissions

        for row in rows:
            assert row['location'] == 'Riverside'
            assert row['admitted_at'].startswith('2026-08-')

# ################################################################################################################################

    def test_query_with_params(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ The same query with named markers and a params dict returns the same rows.
        """
        params = {'location': 'Riverside', 'status': 'admitted'}
        rows = _query(fabric_live, ModuleCtx.Admissions_SQL, params)

        assert _admission_ids(rows) == ModuleCtx.Riverside_Admissions

# ################################################################################################################################

    def test_query_occupancy(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ Occupied beds per location on the last day of the sample data match the sample.
        """
        sql = 'select location, occupied_beds from occupancy where as_of = :as_of order by location'
        rows = _query(fabric_live, sql, {'as_of': ModuleCtx.Occupancy_Date})

        occupied:'anydict' = {}
        for row in rows:
            occupied[row['location']] = row['occupied_beds']

        assert occupied == ModuleCtx.Occupied_Beds

# ################################################################################################################################

    def test_query_missing_table(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ A query over a table that does not exist raises an error carrying the T-SQL message.
        """
        with pytest.raises(Exception) as exception_info:
            _ = _query(fabric_live, 'select 1 from zato_no_such_table')

        assert "Invalid object name 'zato_no_such_table'" in str(exception_info.value)

# ################################################################################################################################

    def test_query_reuses_connection(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ Once a connection to the endpoint is open, a query does not log in again.
        """
        sql = 'select count(*) as admission_count from admissions'

        # The first query may have to open the connection ..
        _ = _query(fabric_live, sql)

        # .. the second one runs on the connection already open.
        start = monotonic()
        rows = _query(fabric_live, sql)
        elapsed = monotonic() - start

        first_row = rows[0]

        assert first_row['admission_count'] > 0
        assert elapsed < ModuleCtx.Pooled_Query_Seconds

# ################################################################################################################################

    def test_query_after_pools_disposed(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ When the connections a pool holds are closed, the next query opens a new one and succeeds.
        """
        sql = 'select count(*) as admission_count from admissions'

        _ = _query(fabric_live, sql)
        _ = _invoke(fabric_live, 'test.fabric.dispose-sql-pools')
        rows = _query(fabric_live, sql)

        first_row = rows[0]

        assert first_row['admission_count'] > 0

# ################################################################################################################################
# ################################################################################################################################

class TestFabricWriteThenQuery:

    def test_written_rows_are_queryable(self, fabric_live:'FabricLiveEnvironment') -> 'None':
        """ Rows written with write_table are visible to a query right after the call returns.
        """
        table_name = ModuleCtx.Test_Table_Prefix + CryptoManager.generate_hex_string(32)

        rows = [
            {'item_id': 'ITEM-001', 'quantity': 3},
            {'item_id': 'ITEM-002', 'quantity': 5},
        ]

        try:
            _ = _invoke(fabric_live, 'test.fabric.write-table', table_name=table_name, rows=rows)

            sql = f'select item_id, quantity from {table_name} order by item_id'
            result = _query(fabric_live, sql)

            assert result == rows

            # The endpoint's view of one table can be refreshed on its own ..
            refresh = _invoke(fabric_live, 'test.fabric.refresh-sql-endpoint', table_names=[table_name])
            statuses = refresh['value']
            status_count = len(statuses)
            first_status = statuses[0]

            assert status_count == 1
            assert first_status['tableName'] == table_name
            assert first_status['status'] != _sync_status.Failure

        finally:
            # .. and the table with the files it was loaded from are removed.
            lakehouse_id = fabric_live.fabric.lakehouse_id
            table_path = f'{lakehouse_id}/Tables/{table_name}'
            files_path = f'{lakehouse_id}/Files/zato/{table_name}'

            for file_path in [table_path, files_path]:
                _ = _invoke(fabric_live, 'test.fabric.onelake-delete', file_path=file_path, recursive=True)

        # The lakehouse's table listing is updated later than OneLake.
        result = _invoke(fabric_live, 'test.fabric.onelake-list', directory=f'{lakehouse_id}/Tables')

        for path in result['paths']:
            assert not path['name'].endswith(f'/{table_name}')

# ################################################################################################################################
# ################################################################################################################################
