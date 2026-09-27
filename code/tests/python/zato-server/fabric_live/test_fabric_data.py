# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Live Fabric
from live_fabric.common import ModuleCtx as FabricCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import FabricLiveEnvironment
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The connection with valid credentials
    Connection_Name = 'test.fabric.main'

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
