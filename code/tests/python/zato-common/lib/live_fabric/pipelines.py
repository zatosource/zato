# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from logging import getLogger

# Zato
from zato.common.crypto.api import CryptoManager

# Live Fabric
from live_fabric import items, notebook
from live_fabric.common import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist
    from zato.server.connection.cloud.microsoft_fabric.client import MicrosoftFabricClient

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# What the nightly notebook runs
_nightly_cell = """
# Tonight's occupancy per location, out of the admissions still open ..
sql = \"\"\"
select
    admissions.location,
    current_date() as as_of,
    count(*) as occupied_beds,
    max(locations.beds) - count(*) as available_beds
from admissions
join locations on locations.name = admissions.location
where admissions.status = 'admitted'
group by admissions.location
\"\"\"

snapshot = spark.sql(sql)

# .. added to the table the report reads.
snapshot.write.mode('append').saveAsTable('occupancy')
"""

# The columns of the occupancy table as the semantic model sees them
_occupancy_columns = (
    ('location',       'string',   'none'),
    ('as_of',          'dateTime', 'none'),
    ('occupied_beds',  'int64',    'sum'),
    ('available_beds', 'int64',    'sum'),
)

# The columns the report's table visual shows, as query references
_visual_columns = (
    'occupancy.location',
    'occupancy.as_of',
    'Sum(occupancy.occupied_beds)',
    'Sum(occupancy.available_beds)',
)

# Where a lineage tag's hex string is split into its groups
_tag_bits = 128
_tag_groups = ((0, 8), (8, 12), (12, 16), (16, 20), (20, 32))

# ################################################################################################################################
# ################################################################################################################################

def _tag() -> 'str':
    """ A lineage tag of one TMDL object.
    """
    hex_string = CryptoManager.generate_hex_string(_tag_bits)

    groups:'strlist' = []
    for start, end in _tag_groups:
        groups.append(hex_string[start:end])

    out = '-'.join(groups)
    return out

# ################################################################################################################################

def occupancy_table_tmdl() -> 'str':
    """ The occupancy table of the semantic model, read straight from the lakehouse.
    """
    lines:'strlist' = [
        'table occupancy',
        f'\tlineageTag: {_tag()}',
        '\tsourceLineageTag: [dbo].[occupancy]',
        '',
    ]

    for name, data_type, summarize_by in _occupancy_columns:
        lines.extend([
            f'\tcolumn {name}',
            f'\t\tdataType: {data_type}',
            f'\t\tlineageTag: {_tag()}',
            f'\t\tsourceLineageTag: {name}',
            f'\t\tsummarizeBy: {summarize_by}',
            f'\t\tsourceColumn: {name}',
            '',
            '\t\tannotation SummarizationSetBy = Automatic',
            '',
        ])

    lines.extend([
        '\tpartition occupancy = entity',
        '\t\tmode: directLake',
        '\t\tsource',
        '\t\t\tentityName: occupancy',
        '\t\t\tschemaName: dbo',
        '\t\t\texpressionSource: DatabaseQuery',
        '',
    ])

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def expressions_tmdl(state:'anydict') -> 'str':
    """ The expression that points the model at the lakehouse's SQL endpoint.
    """
    connection_string = state['sql_endpoint_connection_string']
    sql_endpoint_id = state['sql_endpoint_id']

    lines = [
        'expression DatabaseQuery =',
        '\t\tlet',
        f'\t\t\tdatabase = Sql.Database("{connection_string}", "{sql_endpoint_id}")',
        '\t\tin',
        '\t\t\tdatabase',
        f'\tlineageTag: {_tag()}',
        '',
        '\tannotation PBI_IncludeFutureArtifacts = False',
        '',
    ]

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def model_definition(state:'anydict') -> 'anydict':
    """ The semantic model in Direct Lake mode over the occupancy table.
    """
    database_tmdl = 'database\n\tcompatibilityLevel: 1604\n'

    model_tmdl = '\n'.join([
        'model Model',
        '\tculture: en-US',
        '\tdefaultPowerBIDataSourceVersion: powerBI_V3',
        '\tsourceQueryCulture: en-US',
        '',
        'ref table occupancy',
        '',
    ])

    parts = [
        items.json_part('definition.pbism', {'version': '4.0', 'settings': {}}),
        items.definition_part('definition/database.tmdl', database_tmdl),
        items.definition_part('definition/model.tmdl', model_tmdl),
        items.definition_part('definition/expressions.tmdl', expressions_tmdl(state)),
        items.definition_part('definition/tables/occupancy.tmdl', occupancy_table_tmdl()),
    ]

    out = items.new_definition(parts, 'TMDL')
    return out

# ################################################################################################################################
# ################################################################################################################################

def column_select(alias:'str', name:'str') -> 'anydict':
    """ One plain column of the visual's query.
    """
    out = {
        'Column': {'Expression': {'SourceRef': {'Source': alias}}, 'Property': name},
        'Name': f'occupancy.{name}',
    }
    return out

# ################################################################################################################################

def sum_select(alias:'str', name:'str') -> 'anydict':
    """ One summed column of the visual's query.
    """
    out = {
        'Aggregation': {
            'Expression': {'Column': {'Expression': {'SourceRef': {'Source': alias}}, 'Property': name}},
            'Function': 0,
        },
        'Name': f'Sum(occupancy.{name})',
    }
    return out

# ################################################################################################################################

def table_visual() -> 'str':
    """ One table visual over the occupancy table, as a JSON string.
    """
    alias = 'o'
    projections:'anylist' = []

    for reference in _visual_columns:
        projections.append({'queryRef': reference})

    selects = [
        column_select(alias, 'location'),
        column_select(alias, 'as_of'),
        sum_select(alias, 'occupied_beds'),
        sum_select(alias, 'available_beds'),
    ]

    visual = {
        'name': 'occupancyTable',
        'layouts': [{'id': 0, 'position': {'x': 20, 'y': 20, 'z': 0, 'width': 800, 'height': 500}}],
        'singleVisual': {
            'visualType': 'tableEx',
            'projections': {'Values': projections},
            'prototypeQuery': {
                'Version': 2,
                'From': [{'Name': alias, 'Entity': 'occupancy', 'Type': 0}],
                'Select': selects,
            },
            'drillFilterOtherVisuals': True,
        },
    }

    out = json.dumps(visual)
    return out

# ################################################################################################################################

def report_definition(model_id:'str') -> 'anydict':
    """ A report with one page and one table visual, bound to the semantic model.
    """
    pbir = {
        'version': '4.0',
        'datasetReference': {
            'byConnection': {
                'connectionString': None,
                'pbiServiceModelId': None,
                'pbiModelVirtualServerName': 'sobe_wowvirtualserver',
                'pbiModelDatabaseName': model_id,
                'name': 'EntityDataSource',
                'connectionType': 'pbiServiceXmlaStyleLive',
            },
        },
    }

    container = {
        'x': 20,
        'y': 20,
        'z': 0,
        'width': 800,
        'height': 500,
        'config': table_visual(),
    }

    section = {
        'name': 'occupancy',
        'displayName': ModuleCtx.Occupancy_Report_Name,
        'width': 1280,
        'height': 720,
        'displayOption': 1,
        'config': '{}',
        'visualContainers': [container],
        'filters': '[]',
    }

    report = {
        'config': json.dumps({'version': '5.43', 'activeSectionIndex': 0}),
        'layoutOptimization': 0,
        'sections': [section],
        'filters': '[]',
        'resourcePackages': [],
    }

    parts = [
        items.json_part('definition.pbir', pbir),
        items.json_part('report.json', report),
    ]

    out = items.new_definition(parts, 'PBIR-Legacy')
    return out

# ################################################################################################################################
# ################################################################################################################################

def build(client:'MicrosoftFabricClient', state:'anydict') -> 'None':
    """ The nightly notebook and pipeline, the semantic model and the report.
    """
    workspace_id = state['workspace_id']

    definition = notebook.notebook_definition(state, [_nightly_cell])
    nightly = items.find_or_create_item(client, workspace_id, ModuleCtx.Nightly_Notebook_Name, 'Notebook', definition)
    nightly_id = nightly['id']
    state['nightly_notebook_id'] = nightly_id

    activities = [notebook.notebook_activity('Run nightly occupancy', state, nightly_id)]
    definition = notebook.pipeline_definition(activities)
    pipeline = items.find_or_create_item(
        client, workspace_id, ModuleCtx.Nightly_Pipeline_Name, 'DataPipeline', definition)
    state['nightly_pipeline_id'] = pipeline['id']

    definition = model_definition(state)
    model = items.find_or_create_item(
        client, workspace_id, ModuleCtx.Occupancy_Model_Name, 'SemanticModel', definition)
    model_id = model['id']
    state['occupancy_dataset_id'] = model_id

    definition = report_definition(model_id)
    report = items.find_or_create_item(client, workspace_id, ModuleCtx.Occupancy_Report_Name, 'Report', definition)
    state['occupancy_report_id'] = report['id']

# ################################################################################################################################
# ################################################################################################################################
