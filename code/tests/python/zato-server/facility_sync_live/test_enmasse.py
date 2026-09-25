# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os

# pytest
import pytest

# PyYAML
import yaml

# Zato
from zato.common.defaults import default_cluster_id

# Project
from model.facility import Source_Consult_Notes, Source_Treatments

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

# The file the session imported.
Enmasse_File = os.path.join(os.path.dirname(__file__), 'enmasse.yaml')

SQL_List_Service = 'zato.outgoing.sql.get-list'
Job_Service      = 'zato.scheduler.job.get-by-name'

# The connection type in the file and the engine the server stores.
Connection_Type   = 'oracle'
Connection_Engine = 'oracle'

# ################################################################################################################################
# ################################################################################################################################

def _read_definitions() -> 'anydict':
    with open(Enmasse_File) as enmasse_file:
        out = yaml.safe_load(enmasse_file)

    return out

# ################################################################################################################################

def _find_by_name(items:'dictlist', name:'str') -> 'anydict':

    for item in items:
        if item['name'] == name:
            out = item
            break
    else:
        raise Exception(f'No item named {name} in {items}')

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def definitions() -> 'anydict':
    out = _read_definitions()
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_both_connections_read_back_as_imported(client:'AdminClient', definitions:'anydict') -> 'None':

    connections, _ = client.get_list(SQL_List_Service, cluster_id=default_cluster_id)

    for expected in definitions['sql']:

        assert expected['type'] == Connection_Type

        actual = _find_by_name(connections, expected['name'])

        assert actual['engine'] == Connection_Engine
        assert actual['host'] == expected['host']
        assert actual['port'] == expected['port']
        assert actual['db_name'] == expected['db_name']
        assert actual['username'] == expected['username']
        assert actual['pool_size'] == expected['pool_size']
        assert actual['is_active'] is True

        # A password never comes back.
        assert 'password' not in actual

# ################################################################################################################################

def test_both_jobs_read_back_as_imported(client:'AdminClient', definitions:'anydict') -> 'None':

    for expected in definitions['scheduler']:

        request = {'cluster_id': default_cluster_id, 'name': expected['name']}
        actual = client.invoke(Job_Service, request)

        assert actual['name'] == expected['name']
        assert actual['service_name'] == expected['service']
        assert actual['job_type'] == expected['job_type']
        assert actual['seconds'] == expected['seconds']
        assert actual['is_active'] is expected['is_active']

        # The payload the job passes on is the one from the file.
        actual_extra = json.loads(actual['extra'])
        expected_extra = json.loads(expected['extra'])
        assert actual_extra == expected_extra

        # The two jobs point at the same service with different sources.
        assert actual_extra['source'] in (Source_Treatments, Source_Consult_Notes)

# ################################################################################################################################
# ################################################################################################################################
