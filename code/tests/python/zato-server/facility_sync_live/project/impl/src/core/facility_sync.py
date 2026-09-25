# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from typing import Callable, NamedTuple

# Zato
from zato.server.service import Model, Service

# Project
from adapter_facility.facility_reader import FacilityReader
from adapter_records.records_apply import apply_change
from adapter_records.records_consult_notes import Consult_Note_Rules
from adapter_records.records_treatments import Treatment_Rules
from adapter_records.records_writer import RecordsWriter
from common_sync.sync_database import DatabaseSession
from model.facility import Connection_Facility, Connection_Records, Read_Overlap, Source_Consult_Notes, Source_Treatments

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from adapter_records.records_apply import SourceRules
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

read_func   = Callable[['FacilityReader', 'datetime'], 'anylist']
changesbyid = dict[int, 'any_']

# ################################################################################################################################
# ################################################################################################################################

class SourceSync(NamedTuple):
    """ How one source is read and how its changes are applied.
    """
    read:  'read_func'
    rules: 'SourceRules'

# ################################################################################################################################
# ################################################################################################################################

# Each source to its reader and rules.
_sources = {
    Source_Treatments: SourceSync(FacilityReader.read_treatments, Treatment_Rules),
    Source_Consult_Notes: SourceSync(FacilityReader.read_consult_notes, Consult_Note_Rules),
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SyncRequest(Model):
    source: 'str'

# ################################################################################################################################
# ################################################################################################################################

def collapse(changes:'anylist') -> 'anylist':
    """ One change per source row, the last one logged, in order of first appearance.
    """
    latest:'changesbyid' = {}

    for change in changes:
        latest[change.source_id] = change

    values = latest.values()

    out = list(values)
    return out

# ################################################################################################################################
# ################################################################################################################################

class RunSync(Service):
    """ Brings the target up to date with one source - everything a run writes, the checkpoint included,
    commits at once or not at all.
    """
    name = 'facility.sync.run'
    input = SyncRequest

    def handle(self) -> 'None':

        request:'SyncRequest' = self.request.input

        if request.source not in _sources:
            raise Exception(f'Unknown source -> {request.source}')

        source_sync = _sources[request.source]
        rules = source_sync.rules

        facility_database = DatabaseSession(self.out.sql[Connection_Facility])
        records_database = DatabaseSession(self.out.sql[Connection_Records])

        try:
            reader = FacilityReader(facility_database)
            writer = RecordsWriter(records_database, request.source, rules.section_name)

            checkpoint = writer.get_checkpoint()
            since = checkpoint.last_timestamp - Read_Overlap

            logged = source_sync.read(reader, since)
            changes = collapse(logged)

            # Everything the batch points at is looked up once, before anything is written.
            ids = rules.collect_reference_ids(changes)
            references = reader.resolve(ids)

            for change in changes:
                apply_change(writer, rules, change, references)

            # The checkpoint moves to the newest row read.
            if logged:
                newest = logged[-1]
                writer.set_checkpoint(newest.changed_at)

            records_database.commit()

        except Exception:
            records_database.rollback()
            raise

        finally:
            records_database.close()
            facility_database.close()

        applied = len(changes)

        self.response.payload = {
            'source': request.source,
            'applied': applied,
        }

# ################################################################################################################################
# ################################################################################################################################
