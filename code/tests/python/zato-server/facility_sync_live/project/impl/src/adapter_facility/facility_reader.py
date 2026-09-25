# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Project
from adapter_facility.facility_sql import Read_Consult_Note_Changes, Read_Treatment_Changes, Resolve_Conditions, \
    Resolve_Patients, Resolve_Staff, Resolve_Treatments
from model.facility import ConditionCode, ConsultNoteChange, FacilityReferences, TreatmentChange

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from common_sync.sync_database import DatabaseSession
    from model.facility import conditiondict, consult_list, intintdict, ReferenceIDs, treatment_list
    from zato.common.typing_ import anydict, dictlist, intlist, intset, strlist

# ################################################################################################################################
# ################################################################################################################################

intlistlist = list['intlist']

# ################################################################################################################################
# ################################################################################################################################

# Oracle rejects an IN list longer than this.
_in_list_limit = 1000

# ################################################################################################################################
# ################################################################################################################################

def _in_list(count:'int') -> 'str':
    """ Positional placeholders for an IN list of the given length.
    """
    names:'strlist' = []

    for index in range(count):
        names.append(f':id{index}')

    out = ', '.join(names)
    return out

# ################################################################################################################################

def _chunks(ids:'intset') -> 'intlistlist':
    """ The IDs split into lists Oracle accepts in one IN clause.
    """
    out:'intlistlist' = []
    ordered = sorted(ids)
    count = len(ordered)

    for start in range(0, count, _in_list_limit):
        end = start + _in_list_limit
        chunk = ordered[start:end]
        out.append(chunk)

    return out

# ################################################################################################################################
# ################################################################################################################################

class FacilityReader:
    """ Reads the source database - the change logs and the current tables the logs point at.
    """

    def __init__(self, database:'DatabaseSession') -> 'None':
        self.database = database

# ################################################################################################################################

    def _read_log(self, statement:'str', since:'datetime') -> 'dictlist':
        """ The log rows newer than the given moment, oldest first.
        """
        since_timestamp = self.database.timestamp(since)

        out = self.database.fetch_all(statement, {'since': since_timestamp})
        return out

# ################################################################################################################################

    def read_treatments(self, since:'datetime') -> 'treatment_list':
        """ The treatment changes logged after the given moment.
        """
        out:'treatment_list' = []

        for row in self._read_log(Read_Treatment_Changes, since):

            change = TreatmentChange()
            change.changed_at = row['timestamp']
            change.operation = row['operation']
            change.source_id = row['id']
            change.patient_id = row['patient_id']
            change.staff_id = row['staff_id']
            change.condition_id = row['condition_id']
            change.start_date = row['start_date']
            change.end_date = row['end_date']
            change.clarification = row['clarification']
            change.attention_value_id = row['attention_value_id']

            out.append(change)

        return out

# ################################################################################################################################

    def read_consult_notes(self, since:'datetime') -> 'consult_list':
        """ The consult note changes logged after the given moment.
        """
        out:'consult_list' = []

        for row in self._read_log(Read_Consult_Note_Changes, since):

            change = ConsultNoteChange()
            change.changed_at = row['timestamp']
            change.operation = row['operation']
            change.source_id = row['id']
            change.staff_id = row['staff_id']
            change.treatment_id = row['treatment_id']
            change.complaint_code_id = row['complaint_code_id']
            change.assessment_code_id = row['assessment_code_id']
            change.created_date = row['created_date']
            change.modified_date = row['modified_date']
            change.complaint_note = row['complaint_note']
            change.findings_note = row['findings_note']
            change.assessment_note = row['assessment_note']
            change.plan_note = row['plan_note']
            change.progress_note = row['progress_note']

            out.append(change)

        return out

# ################################################################################################################################

    def _lookup(self, statement:'str', ids:'intset') -> 'dictlist':
        """ The current rows for the given IDs.
        """
        out:'dictlist' = []

        for chunk in _chunks(ids):

            count = len(chunk)
            in_list = _in_list(count)
            parameters:'anydict' = {}

            for index, value in enumerate(chunk):
                parameters[f'id{index}'] = value

            lookup = statement.format(in_list=in_list)
            rows = self.database.fetch_all(lookup, parameters)
            out.extend(rows)

        return out

# ################################################################################################################################

    def _resolve_reference_ids(self, statement:'str', ids:'intset') -> 'intintdict':
        """ Each ID to the second column of its current row - a reference or a parent's ID.
        """
        out:'intintdict' = {}

        for row in self._lookup(statement, ids):
            out[row['id']] = row['value']

        return out

# ################################################################################################################################

    def _resolve_conditions(self, ids:'intset') -> 'conditiondict':
        out:'conditiondict' = {}

        for row in self._lookup(Resolve_Conditions, ids):
            code = row['condition_code']
            title = row['condition_title']
            out[row['id']] = ConditionCode(code, title)

        return out

# ################################################################################################################################

    def resolve(self, ids:'ReferenceIDs') -> 'FacilityReferences':
        """ Everything the current tables say about the given IDs. An ID that is not there is not in the result either.
        """
        out = FacilityReferences()
        out.staff = self._resolve_reference_ids(Resolve_Staff, ids.staff_ids)
        out.conditions = self._resolve_conditions(ids.condition_ids)
        out.treatments = self._resolve_reference_ids(Resolve_Treatments, ids.treatment_ids)

        # The patients the resolved treatments belong to are looked up too.
        patient_ids = set(ids.patient_ids)
        treatment_patient_ids = out.treatments.values()
        patient_ids.update(treatment_patient_ids)

        out.patients = self._resolve_reference_ids(Resolve_Patients, patient_ids)

        return out

# ################################################################################################################################
# ################################################################################################################################
