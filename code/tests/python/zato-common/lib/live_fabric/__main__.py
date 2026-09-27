# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import sys
from logging import getLogger

# Live Fabric
from live_fabric import base, cleanup, events, files, local_systems, notebook, pipelines, render, state as state_, tables
from live_fabric.common import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The modules each chapter needs
_chapters = {
    'tutorial':              (),
    'loading-tables':        (tables,),
    'lookup-tables':         (tables,),
    'looking-up-data':       (tables,),
    'api-on-fabric-data':    (tables,),
    'scheduled-reports':     (tables,),
    'files':                 (tables, files),
    'sending-events':        (events,),
    'receiving-events':      (events,),
    'reading-events':        (events,),
    'notebook-results':      (tables, notebook),
    'pipelines-and-reports': (tables, pipelines),
    'local-systems':         (tables, local_systems),
}

# The state keys and their labels
_item_labels = (
    ('workspace_id',             f'Workspace {ModuleCtx.Workspace_Name}'),
    ('lakehouse_id',             f'Lakehouse {ModuleCtx.Lakehouse_Name}'),
    ('tables',                   'Tables ' + ', '.join(ModuleCtx.Tables)),
    ('incoming_file',            f'Folders {ModuleCtx.Incoming_Folder} and {ModuleCtx.Exports_Folder}'),
    ('eventhouse_id',            f'Eventhouse {ModuleCtx.Eventhouse_Name} with table {ModuleCtx.Events_Table}'),
    ('eventstream_id',           f'Eventstream {ModuleCtx.Eventstream_Name} with destination {ModuleCtx.Eventstream_Alerts}'),
    ('reminder_notebook_id',     f'Notebook {ModuleCtx.Reminder_Notebook_Name}'),
    ('reminders_pipeline_id',    f'Pipeline {ModuleCtx.Reminders_Pipeline_Name}'),
    ('nightly_notebook_id',      f'Notebook {ModuleCtx.Nightly_Notebook_Name}'),
    ('nightly_pipeline_id',      f'Pipeline {ModuleCtx.Nightly_Pipeline_Name}'),
    ('occupancy_dataset_id',     f'Semantic model {ModuleCtx.Occupancy_Model_Name}'),
    ('occupancy_report_id',      f'Report {ModuleCtx.Occupancy_Report_Name}'),
    ('appointments_pipeline_id', f'Pipeline {ModuleCtx.Appointments_Pipeline_Name}'),
    ('zato_connection_id',       f'Connection {ModuleCtx.Zato_Connection_Name}'),
)

# ################################################################################################################################
# ################################################################################################################################

def summary(state:'anydict') -> 'strlist':
    """ What exists now and where the files are.
    """
    out:'strlist' = ['', 'What exists now:']

    for state_key, label in _item_labels:
        if state_key in state:
            out.append(f'  {label}')

    out.extend([
        '',
        f'Import into your environment: {state_.path_of(ModuleCtx.Enmasse_File)}',
        f'Copy into its config/user-conf/: {state_.path_of(ModuleCtx.INI_File)}',
        '',
    ])

    return out

# ################################################################################################################################

def run_chapter(chapter:'str') -> 'None':
    """ Builds the shared part, then the chapter's modules.
    """
    modules = _chapters[chapter]
    state = state_.load()

    client = base.setup(state)
    render.write_all(state)

    for module in modules:
        module.build(client, state)
        render.write_all(state)

    for line in summary(state):
        logger.info(line)

# ################################################################################################################################

def main() -> 'None':
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    if len(sys.argv) != 2:
        names = ', '.join(_chapters)
        raise Exception(f'Expected one argument - a chapter ({names}) or cleanup')

    name = sys.argv[1]

    if name == 'cleanup':
        for line in cleanup.run():
            logger.info(line)
        return

    if name not in _chapters:
        names = ', '.join(_chapters)
        raise Exception(f'Unknown chapter {name}, expected one of {names} or cleanup')

    run_chapter(name)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
