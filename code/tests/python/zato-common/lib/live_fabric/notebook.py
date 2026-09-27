# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Live Fabric
from live_fabric import items
from live_fabric.common import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist
    from zato.server.connection.cloud.microsoft_fabric.client import MicrosoftFabricClient

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The REST channel the pipeline posts to when the notebook is done
_results_ready_path = '/api/fabric/results-ready'

# What the reminder candidates notebook runs
_reminder_cell = """
# The appointments that are scheduled and have no reminder yet ..
sql = \"\"\"
select appointment_id, location, starts_at
from appointments
where status = 'scheduled'
and not reminder_sent
\"\"\"

candidates = spark.sql(sql)

# .. written to the table the service reads.
candidates.write.mode('overwrite').saveAsTable('reminder_candidates')
"""

# ################################################################################################################################
# ################################################################################################################################

def notebook_definition(state:'anydict', cells:'strlist') -> 'anydict':
    """ A notebook attached to the lakehouse, one code cell per string.
    """
    cell_list:'anylist' = []

    for source in cells:
        source_text = source.strip() + '\n'
        cell_list.append({
            'cell_type': 'code',
            'source': source_text,
            'execution_count': None,
            'outputs': [],
            'metadata': {},
        })

    notebook = {
        'nbformat': 4,
        'nbformat_minor': 5,
        'metadata': {
            'language_info': {'name': 'python'},
            'kernelspec': {'name': 'synapse_pyspark', 'display_name': 'Synapse PySpark'},
            'dependencies': {
                'lakehouse': {
                    'default_lakehouse': state['lakehouse_id'],
                    'default_lakehouse_name': ModuleCtx.Lakehouse_Name,
                    'default_lakehouse_workspace_id': state['workspace_id'],
                },
            },
        },
        'cells': cell_list,
    }

    parts = [items.json_part('notebook-content.ipynb', notebook)]

    out = items.new_definition(parts, 'ipynb')
    return out

# ################################################################################################################################

def pipeline_definition(activities:'anylist') -> 'anydict':
    """ A pipeline out of its activities.
    """
    content = {'properties': {'activities': activities, 'parameters': {}}}

    parts = [items.json_part('pipeline-content.json', content)]

    out = items.new_definition(parts)
    return out

# ################################################################################################################################

def notebook_activity(name:'str', state:'anydict', notebook_id:'str') -> 'anydict':
    """ An activity running a notebook of the workspace.
    """
    out = {
        'name': name,
        'type': 'TridentNotebook',
        'dependsOn': [],
        'policy': {'timeout': '0.12:00:00', 'retry': 0, 'retryIntervalInSeconds': 30},
        'typeProperties': {
            'notebookId': notebook_id,
            'workspaceId': state['workspace_id'],
        },
    }

    return out

# ################################################################################################################################

def web_activity(name:'str', state:'anydict', after:'str', relative_url:'str') -> 'anydict':
    """ An activity posting to a Zato REST channel once another activity succeeded.
    """
    out = {
        'name': name,
        'type': 'WebActivity',
        'dependsOn': [{'activity': after, 'dependencyConditions': ['Succeeded']}],
        'policy': {'timeout': '0.00:10:00', 'retry': 0, 'retryIntervalInSeconds': 30},
        'typeProperties': {
            'method': 'POST',
            'relativeUrl': relative_url,
            'headers': {ModuleCtx.API_Key_Header: ModuleCtx.API_Key_Placeholder},
            'body': '{}',
        },
        'externalReferences': {'connection': state['zato_connection_id']},
    }

    return out

# ################################################################################################################################

def ensure_zato_connection(client:'MicrosoftFabricClient', state:'anydict') -> 'None':
    """ The Fabric connection the pipelines reach Zato through.
    """
    state['zato_connection_id'] = items.find_or_create_web_connection(
        client, ModuleCtx.Zato_Connection_Name, ModuleCtx.Zato_Connection_URL)

# ################################################################################################################################
# ################################################################################################################################

def build(client:'MicrosoftFabricClient', state:'anydict') -> 'None':
    """ The reminder candidates notebook and its pipeline.
    """
    workspace_id = state['workspace_id']

    definition = notebook_definition(state, [_reminder_cell])
    notebook = items.find_or_create_item(client, workspace_id, ModuleCtx.Reminder_Notebook_Name, 'Notebook', definition)
    notebook_id = notebook['id']
    state['reminder_notebook_id'] = notebook_id

    ensure_zato_connection(client, state)

    activities = [
        notebook_activity('Run reminder candidates', state, notebook_id),
        web_activity('Tell Zato', state, 'Run reminder candidates', _results_ready_path),
    ]

    definition = pipeline_definition(activities)
    pipeline = items.find_or_create_item(
        client, workspace_id, ModuleCtx.Reminders_Pipeline_Name, 'DataPipeline', definition)
    state['reminders_pipeline_id'] = pipeline['id']

# ################################################################################################################################
# ################################################################################################################################
