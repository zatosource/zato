# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import csv
from datetime import date
from io import StringIO
from logging import getLogger

# Live Fabric
from live_fabric import tables
from live_fabric.common import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist, strlist
    from zato.server.connection.cloud.microsoft_fabric.client import MicrosoftFabricClient

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def last_month() -> 'str':
    """ The month before the current one, as YYYY-MM.
    """
    today = date.today()
    first_of_month = today.replace(day=1)
    year = first_of_month.year
    month = first_of_month.month - 1

    if month == 0:
        month = 12
        year = year - 1

    out = f'{year}-{month:02d}'
    return out

# ################################################################################################################################

def incoming_file_path() -> 'str':
    """ Where the invoices file the files page loads is.
    """
    month = last_month()

    out = f'{ModuleCtx.Incoming_Folder}/invoices-{month}.csv'
    return out

# ################################################################################################################################

def to_csv(rows:'dictlist') -> 'bytes':
    """ Rows as a CSV file with a header.
    """
    first_row = rows[0]
    columns:'strlist' = list(first_row)

    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)

    out = buffer.getvalue().encode('utf-8')
    return out

# ################################################################################################################################

def existing_paths(client:'MicrosoftFabricClient', workspace_id:'str', directory:'str') -> 'strlist':
    """ The paths directly under a directory of the workspace's OneLake filesystem.
    """
    out:'strlist' = []

    listing = client.onelake_list(workspace_id, directory)
    for path in listing['paths']:
        out.append(path['name'])

    return out

# ################################################################################################################################

def ensure_directory(client:'MicrosoftFabricClient', workspace_id:'str', lakehouse_id:'str', folder:'str') -> 'None':
    """ A folder in the lakehouse's Files section.
    """
    parent, _, _ = folder.rpartition('/')
    parent_path = f'{lakehouse_id}/{parent}'
    full_path = f'{lakehouse_id}/{folder}'

    existing = existing_paths(client, workspace_id, parent_path)

    if full_path in existing:
        logger.info(f'Folder {folder} exists')
        return

    logger.info(f'Creating folder {folder} ..')
    _ = client._invoke_onelake('PUT', f'/{workspace_id}/{full_path}', params={'resource': 'directory'})

# ################################################################################################################################
# ################################################################################################################################

def build(client:'MicrosoftFabricClient', state:'anydict') -> 'None':
    """ The Files folders and the invoices file.
    """
    workspace_id = state['workspace_id']
    lakehouse_id = state['lakehouse_id']

    ensure_directory(client, workspace_id, lakehouse_id, ModuleCtx.Incoming_Folder)
    ensure_directory(client, workspace_id, lakehouse_id, ModuleCtx.Exports_Folder)

    file_path = incoming_file_path()
    full_path = f'{lakehouse_id}/{file_path}'
    incoming_path = f'{lakehouse_id}/{ModuleCtx.Incoming_Folder}'
    existing = existing_paths(client, workspace_id, incoming_path)

    if full_path in existing:
        logger.info(f'File {file_path} exists')
    else:
        logger.info(f'Writing file {file_path} ..')
        rows = tables.invoices()
        data = to_csv(rows)
        client.onelake_write(workspace_id, full_path, data)

    state['incoming_file'] = file_path
    state['exports_folder'] = ModuleCtx.Exports_Folder

# ################################################################################################################################
# ################################################################################################################################
