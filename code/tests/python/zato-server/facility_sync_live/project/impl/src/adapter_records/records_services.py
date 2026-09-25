# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime

# Zato
from zato.server.service import Model, Service

# Project
from adapter_facility.facility_reader import FacilityReader
from adapter_records.records_apply import apply_change
from adapter_records.records_consult_notes import Consult_Note_Rules
from adapter_records.records_treatments import Treatment_Rules
from adapter_records.records_writer import RecordsWriter
from common_sync.sync_database import DatabaseSession
from model.facility import Connection_Facility, Connection_Records, ConsultNoteChange, Source_Consult_Notes, \
    Source_Treatments, TreatmentChange

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from adapter_records.records_apply import SourceRules
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

# Each source to the section of the target it lands in.
_section_names = {
    Source_Treatments: Treatment_Rules.section_name,
    Source_Consult_Notes: Consult_Note_Rules.section_name,
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CheckpointRequest(Model):
    source: 'str'

# ################################################################################################################################

@dataclass(init=False)
class SetCheckpointRequest(Model):
    source:         'str'
    last_timestamp: 'str'

# ################################################################################################################################

@dataclass(init=False)
class ApplyRequest(Model):
    change: 'anydict'

# ################################################################################################################################
# ################################################################################################################################

def apply_one_change(service:'Service', source:'str', change_class:'any_', rules:'SourceRules') -> 'int':
    """ Applies one change of one source in a transaction of its own - the checkpoint is not touched,
    that is for callers that apply whole batches. Returns the source ID of the change.
    """
    request:'ApplyRequest' = service.request.input
    change = change_class.from_dict(request.change)

    facility_database = DatabaseSession(service.out.sql[Connection_Facility])
    records_database = DatabaseSession(service.out.sql[Connection_Records])

    try:
        reader = FacilityReader(facility_database)

        changes = [change]
        ids = rules.collect_reference_ids(changes)
        references = reader.resolve(ids)

        writer = RecordsWriter(records_database, source, rules.section_name)
        apply_change(writer, rules, change, references)

        records_database.commit()

    except Exception:
        records_database.rollback()
        raise

    finally:
        records_database.close()
        facility_database.close()

    out = change.source_id
    return out

# ################################################################################################################################
# ################################################################################################################################

class GetCheckpoint(Service):
    """ Where the sync of one source got to.
    """
    name = 'records.checkpoint.get'
    input = CheckpointRequest

    def handle(self) -> 'None':

        request:'CheckpointRequest' = self.request.input
        section_name = _section_names[request.source]
        database = DatabaseSession(self.out.sql[Connection_Records])

        try:
            writer = RecordsWriter(database, request.source, section_name)
            checkpoint = writer.get_checkpoint()
        finally:
            database.close()

        self.response.payload = {
            'source': checkpoint.source,
            'last_timestamp': checkpoint.last_timestamp.isoformat(),
        }

# ################################################################################################################################
# ################################################################################################################################

class SetCheckpoint(Service):
    """ Moves the checkpoint of one source to a moment given in ISO format.
    """
    name = 'records.checkpoint.set'
    input = SetCheckpointRequest

    def handle(self) -> 'None':

        request:'SetCheckpointRequest' = self.request.input
        last_timestamp = datetime.fromisoformat(request.last_timestamp)
        section_name = _section_names[request.source]

        database = DatabaseSession(self.out.sql[Connection_Records])

        try:
            writer = RecordsWriter(database, request.source, section_name)
            writer.set_checkpoint(last_timestamp)
            database.commit()
        except Exception:
            database.rollback()
            raise
        finally:
            database.close()

        self.response.payload = {'source': request.source}

# ################################################################################################################################
# ################################################################################################################################

class ApplyTreatment(Service):
    """ Applies one change of a treatment.
    """
    name = 'records.treatment.apply'
    input = ApplyRequest

    def handle(self) -> 'None':
        source_id = apply_one_change(self, Source_Treatments, TreatmentChange, Treatment_Rules)
        self.response.payload = {'source_id': source_id}

# ################################################################################################################################
# ################################################################################################################################

class ApplyConsultNote(Service):
    """ Applies one change of a consult note.
    """
    name = 'records.consult-note.apply'
    input = ApplyRequest

    def handle(self) -> 'None':
        source_id = apply_one_change(self, Source_Consult_Notes, ConsultNoteChange, Consult_Note_Rules)
        self.response.payload = {'source_id': source_id}

# ################################################################################################################################
# ################################################################################################################################
