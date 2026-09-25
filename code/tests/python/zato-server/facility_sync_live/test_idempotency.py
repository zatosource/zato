# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta
from typing import NamedTuple

# Project
from model.facility import Operation_Insert, Operation_Update, Section_Consult_Notes, Section_Treatments, \
    Source_Consult_Notes, Source_Treatments

# Zato
from _support import add_references, Condition_ID, Consult_Note_ID, ModuleCtx, Patient_ID, run_sync, Staff_ID, \
    Treatment_ID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from _support import FacilityDatabase, field_list, map_list, RecordsDatabase, section_list, SyncDatabase

# ################################################################################################################################
# ################################################################################################################################

class TargetState(NamedTuple):
    """ Everything a run can leave in the target, read back in a fixed order.
    """
    sections: 'section_list'
    fields:   'field_list'
    map_rows: 'map_list'

# ################################################################################################################################
# ################################################################################################################################

def _read_state(records:'RecordsDatabase', sync:'SyncDatabase', section_name:'str') -> 'TargetState':

    sections = records.sections(section_name)
    fields:'field_list' = []

    for section in sections:
        rows = records.field_rows(section.section_id)
        fields.extend(rows)

    map_rows = sync.map_rows()

    out = TargetState(sections, fields, map_rows)
    return out

# ################################################################################################################################

def _log_batch(facility:'FacilityDatabase') -> 'None':
    """ Two treatments, one of them updated, and one consult note.
    """
    checkpoint = ModuleCtx.Base_Time

    first_changed_at = checkpoint + timedelta(minutes=1)
    second_changed_at = checkpoint + timedelta(minutes=2)
    third_changed_at = checkpoint + timedelta(minutes=3)
    fourth_changed_at = checkpoint + timedelta(minutes=4)

    facility.log_treatment(first_changed_at, Operation_Insert, Treatment_ID,
        patient_id=Patient_ID, staff_id=Staff_ID, condition_id=Condition_ID, clarification='first')

    facility.log_treatment(second_changed_at, Operation_Insert, Treatment_ID + 1,
        patient_id=Patient_ID, attention_value_id=2)

    facility.log_treatment(third_changed_at, Operation_Update, Treatment_ID,
        patient_id=Patient_ID, staff_id=Staff_ID, condition_id=Condition_ID, clarification='second')

    facility.log_consult_note(fourth_changed_at, Operation_Insert, Consult_Note_ID,
        staff_id=Staff_ID, treatment_id=Treatment_ID, complaint_code_id=Condition_ID, complaint_note='Persistent cough')

    facility.commit()

# ################################################################################################################################
# ################################################################################################################################

def test_applying_the_same_batch_twice_changes_nothing(
    records_api:'str',
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    ) -> 'None':

    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Treatments, checkpoint)
    sync.seed_checkpoint(Source_Consult_Notes, checkpoint)

    _log_batch(facility)

    _ = run_sync(client, Source_Treatments)
    _ = run_sync(client, Source_Consult_Notes)

    treatments_before = _read_state(records, sync, Section_Treatments)
    consult_notes_before = _read_state(records, sync, Section_Consult_Notes)

    treatment_section_count = len(treatments_before.sections)
    consult_note_section_count = len(consult_notes_before.sections)
    map_row_count = len(treatments_before.map_rows)

    assert treatment_section_count == 2
    assert consult_note_section_count == 1
    assert map_row_count == 3

    # The second run reads the same rows again through the overlap and applies them once more.
    _ = run_sync(client, Source_Treatments)
    _ = run_sync(client, Source_Consult_Notes)

    treatments_after = _read_state(records, sync, Section_Treatments)
    consult_notes_after = _read_state(records, sync, Section_Consult_Notes)

    assert treatments_after == treatments_before
    assert consult_notes_after == consult_notes_before

    treatment_field_count = len(treatments_after.fields)
    consult_note_field_count = len(consult_notes_after.fields)
    field_count = treatment_field_count + consult_note_field_count

    assert records.count_sections() == 3
    assert records.count_fields() == field_count

# ################################################################################################################################
# ################################################################################################################################
