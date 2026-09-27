# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Live Fabric
from live_fabric import items, notebook
from live_fabric.common import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    from zato.server.connection.cloud.microsoft_fabric.client import MicrosoftFabricClient

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The REST channel the pipeline reads appointments from
_appointments_path = '/api/appointments'

# ################################################################################################################################
# ################################################################################################################################

def copy_activity(name:'str', state:'anydict') -> 'anydict':
    """ An activity copying what a Zato REST channel returns into a lakehouse table.
    """
    source = {
        'type': 'RestSource',
        'httpRequestTimeout': '00:01:40',
        'requestInterval': '00.00:00:00.010',
        'requestMethod': 'GET',
        'additionalHeaders': {ModuleCtx.API_Key_Header: ModuleCtx.API_Key_Placeholder},
        'datasetSettings': {
            'type': 'RestResource',
            'typeProperties': {'relativeUrl': _appointments_path},
            'externalReferences': {'connection': state['zato_connection_id']},
        },
    }

    sink = {
        'type': 'LakehouseTableSink',
        'tableActionOption': 'Append',
        'datasetSettings': {
            'type': 'LakehouseTable',
            'typeProperties': {'table': 'appointments'},
            'linkedService': {
                'name': ModuleCtx.Lakehouse_Name,
                'properties': {
                    'type': 'Lakehouse',
                    'typeProperties': {
                        'workspaceId': state['workspace_id'],
                        'artifactId': state['lakehouse_id'],
                        'rootFolder': 'Tables',
                    },
                },
            },
        },
    }

    out = {
        'name': name,
        'type': 'Copy',
        'dependsOn': [],
        'policy': {'timeout': '0.12:00:00', 'retry': 0, 'retryIntervalInSeconds': 30},
        'typeProperties': {
            'source': source,
            'sink': sink,
            'enableStaging': False,
        },
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def build(client:'MicrosoftFabricClient', state:'anydict') -> 'None':
    """ The pipeline that copies appointments into the lakehouse.
    """
    workspace_id = state['workspace_id']

    notebook.ensure_zato_connection(client, state)

    activities = [copy_activity('Copy appointments', state)]
    definition = notebook.pipeline_definition(activities)

    pipeline = items.find_or_create_item(
        client, workspace_id, ModuleCtx.Appointments_Pipeline_Name, 'DataPipeline', definition)
    state['appointments_pipeline_id'] = pipeline['id']

# ################################################################################################################################
# ################################################################################################################################
