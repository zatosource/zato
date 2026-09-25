# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Project
from model.facility import Operation_Delete, Operation_Insert, Operation_Update, Section_Treatments, Source_Treatments

# Zato
from _support import add_references, Field_Treatment_ID, ModuleCtx, Patient_ID, Patient_Reference, run_sync, \
    Staff_ID, Staff_Reference, Treatment_ID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from _support import FacilityDatabase, RecordsDatabase, SyncDatabase

# ################################################################################################################################
# ################################################################################################################################

Field_Clarification = 'TREATMENT_CLARIFICATION'
Field_Staff         = 'TREATMENT_STAFF'

# ################################################################################################################################
# ################################################################################################################################

def test_insert_update_update_gives_one_section_with_the_last_values(
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    ) -> 'None':

    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Treatments, checkpoint)

    first_changed_at = checkpoint + timedelta(minutes=1)
    second_changed_at = checkpoint + timedelta(minutes=2)
    third_changed_at = checkpoint + timedelta(minutes=3)

    facility.log_treatment(first_changed_at, Operation_Insert, Treatment_ID,
        patient_id=Patient_ID, staff_id=Staff_ID, clarification='first')

    facility.log_treatment(second_changed_at, Operation_Update, Treatment_ID,
        patient_id=Patient_ID, staff_id=Staff_ID, clarification='second')

    # The last change drops the staff member.
    facility.log_treatment(third_changed_at, Operation_Update, Treatment_ID,
        patient_id=Patient_ID, clarification='third')

    facility.commit()

    response = run_sync(client, Source_Treatments)
    assert response['applied'] == 1

    sections = records.sections(Section_Treatments)
    section_count = len(sections)
    assert section_count == 1

    section = sections[0]
    assert section.patient == Patient_Reference
    assert section.sequence_number == Treatment_ID

    fields = records.fields(section.section_id)
    assert fields[Field_Treatment_ID] == str(Treatment_ID)
    assert fields[Field_Clarification] == 'third'
    assert Field_Staff not in fields

    map_rows = sync.map_rows()
    map_row_count = len(map_rows)
    assert map_row_count == 1

    map_row = map_rows[0]
    assert map_row.source_id == Treatment_ID
    assert map_row.section_id == section.section_id

# ################################################################################################################################

def test_update_after_a_synced_insert_keeps_the_section_and_changes_its_fields(
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    ) -> 'None':

    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Treatments, checkpoint)

    first_changed_at = checkpoint + timedelta(minutes=1)
    second_changed_at = checkpoint + timedelta(minutes=2)
    third_changed_at = checkpoint + timedelta(minutes=3)

    facility.log_treatment(first_changed_at, Operation_Insert, Treatment_ID,
        patient_id=Patient_ID, clarification='first')
    facility.commit()

    _ = run_sync(client, Source_Treatments)

    sections = records.sections(Section_Treatments)
    section = sections[0]
    section_id_before = section.section_id

    facility.log_treatment(second_changed_at, Operation_Update, Treatment_ID,
        patient_id=Patient_ID, staff_id=Staff_ID, clarification='second')
    facility.commit()

    _ = run_sync(client, Source_Treatments)

    sections = records.sections(Section_Treatments)
    section_count = len(sections)
    assert section_count == 1

    section = sections[0]
    assert section.section_id == section_id_before

    fields = records.fields(section_id_before)
    assert fields[Field_Clarification] == 'second'
    assert fields[Field_Staff] == str(Staff_Reference)

    # A value that became NULL takes its field away from the section.
    facility.log_treatment(third_changed_at, Operation_Update, Treatment_ID,
        patient_id=Patient_ID, clarification='third')
    facility.commit()

    _ = run_sync(client, Source_Treatments)

    fields = records.fields(section_id_before)
    assert fields[Field_Clarification] == 'third'
    assert Field_Staff not in fields

# ################################################################################################################################

def test_insert_then_delete_in_one_batch_leaves_nothing(
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    ) -> 'None':

    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Treatments, checkpoint)

    insert_changed_at = checkpoint + timedelta(minutes=1)
    delete_changed_at = checkpoint + timedelta(minutes=2)

    facility.log_treatment(insert_changed_at, Operation_Insert, Treatment_ID, patient_id=Patient_ID)
    facility.log_treatment(delete_changed_at, Operation_Delete, Treatment_ID, patient_id=Patient_ID)
    facility.commit()

    _ = run_sync(client, Source_Treatments)

    assert records.count_sections() == 0
    assert records.count_fields() == 0
    assert sync.map_rows() == []
    assert sync.checkpoint(Source_Treatments) == delete_changed_at

# ################################################################################################################################

def test_delete_of_a_synced_row_removes_its_section(
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    ) -> 'None':

    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Treatments, checkpoint)

    insert_changed_at = checkpoint + timedelta(minutes=1)
    delete_changed_at = checkpoint + timedelta(minutes=2)

    facility.log_treatment(insert_changed_at, Operation_Insert, Treatment_ID, patient_id=Patient_ID)
    facility.commit()

    _ = run_sync(client, Source_Treatments)
    assert records.count_sections() == 1

    facility.log_treatment(delete_changed_at, Operation_Delete, Treatment_ID)
    facility.commit()

    _ = run_sync(client, Source_Treatments)

    assert records.count_sections() == 0
    assert records.count_fields() == 0
    assert sync.map_rows() == []

# ################################################################################################################################

def test_delete_of_an_unmapped_row_is_a_no_op(
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    ) -> 'None':

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Treatments, checkpoint)

    delete_changed_at = checkpoint + timedelta(minutes=1)

    facility.log_treatment(delete_changed_at, Operation_Delete, Treatment_ID)
    facility.commit()

    response = run_sync(client, Source_Treatments)

    assert response['applied'] == 1
    assert records.count_sections() == 0
    assert sync.map_rows() == []
    assert sync.checkpoint(Source_Treatments) == delete_changed_at

# ################################################################################################################################
# ################################################################################################################################
