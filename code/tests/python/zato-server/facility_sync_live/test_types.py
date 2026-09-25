# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta

# Project
from model.facility import Operation_Insert, Section_Consult_Notes, Section_Treatments, Source_Consult_Notes, \
    Source_Treatments

# Zato
from _support import add_references, Condition_Code, Condition_ID, Condition_Title, Consult_Note_ID, Field_Consult_Note_ID, \
    Field_Treatment_ID, Field_Treatment_Patient, ModuleCtx, Patient_ID, Patient_Reference, run_sync, Staff_ID, \
    Staff_Reference, Treatment_ID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import strlist
    from _support import FacilityDatabase, RecordsDatabase, SyncDatabase

# ################################################################################################################################
# ################################################################################################################################

Resolve_Service = 'facility.reference.resolve'

# The fields these tests look at.
Field_Start_Date      = 'TREATMENT_START_DATE'
Field_End_Date        = 'TREATMENT_END_DATE'
Field_Staff           = 'TREATMENT_STAFF'
Field_Condition_Code  = 'TREATMENT_CONDITION_CODE'
Field_Condition_Title = 'TREATMENT_CONDITION_TITLE'
Field_Attention_Value = 'TREATMENT_ATTENTION_VALUE'
Field_Clarification   = 'TREATMENT_CLARIFICATION'
Field_Created_Date    = 'CONSULT_NOTE_CREATED_DATE'
Field_Progress_Note   = 'CONSULT_NOTE_PROGRESS_NOTE'

# The longest text the target's columns take.
Note_Length = 4000

# The characters the longest note is built from - the printable ASCII range, from this code point onwards.
First_Character = 33
Character_Count = 90

# ################################################################################################################################
# ################################################################################################################################

def test_number_ids_arrive_as_integers(client:'AdminClient', facility:'FacilityDatabase') -> 'None':

    add_references(facility)

    request = {
        'patient_ids': [Patient_ID],
        'staff_ids': [Staff_ID],
        'condition_ids': [Condition_ID],
        'treatment_ids': [Treatment_ID],
    }

    response = client.invoke(Resolve_Service, request)

    # JSON keys are always strings, the values are what the adapter produced.
    patient_reference = response['patients'][str(Patient_ID)]
    staff_reference = response['staff'][str(Staff_ID)]
    treatment_patient = response['treatments'][str(Treatment_ID)]

    assert patient_reference == Patient_Reference
    assert isinstance(patient_reference, int)

    assert staff_reference == Staff_Reference
    assert isinstance(staff_reference, int)

    assert treatment_patient == Patient_ID
    assert isinstance(treatment_patient, int)

    condition = response['conditions'][str(Condition_ID)]
    assert condition == {'code': Condition_Code, 'title': Condition_Title}

# ################################################################################################################################

def test_dates_and_timestamps_keep_their_precision(
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    ) -> 'None':

    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Treatments, checkpoint)
    sync.seed_checkpoint(Source_Consult_Notes, checkpoint)

    # A DATE keeps its time of day, a TIMESTAMP keeps its microseconds.
    start_date = datetime(2026, 3, 1, 14, 30, 15)
    created_date = datetime(2026, 3, 2, 8, 15, 30, 123456)

    # The log's own TIMESTAMP is what a field's answered_at is set from.
    treatment_changed_at = checkpoint + timedelta(minutes=1, microseconds=654321)
    note_changed_at = checkpoint + timedelta(minutes=2, microseconds=1)

    facility.log_treatment(treatment_changed_at, Operation_Insert, Treatment_ID,
        patient_id=Patient_ID, start_date=start_date, attention_value_id=1)

    facility.log_consult_note(note_changed_at, Operation_Insert, Consult_Note_ID,
        treatment_id=Treatment_ID, created_date=created_date)

    facility.commit()

    _ = run_sync(client, Source_Treatments)
    _ = run_sync(client, Source_Consult_Notes)

    treatment_sections = records.sections(Section_Treatments)
    treatment_section = treatment_sections[0]
    treatment_fields = records.fields(treatment_section.section_id)

    assert treatment_fields[Field_Start_Date] == '2026-03-01T14:30:15'
    assert treatment_fields[Field_Attention_Value] == 'Low'

    for row in records.field_rows(treatment_section.section_id):
        assert row.answered_at == treatment_changed_at

    note_sections = records.sections(Section_Consult_Notes)
    note_section = note_sections[0]
    note_fields = records.fields(note_section.section_id)

    assert note_fields[Field_Created_Date] == '2026-03-02T08:15:30.123456'
    assert note_fields[Field_Consult_Note_ID] == str(Consult_Note_ID)

    for row in records.field_rows(note_section.section_id):
        assert row.answered_at == note_changed_at

    assert sync.checkpoint(Source_Treatments) == treatment_changed_at
    assert sync.checkpoint(Source_Consult_Notes) == note_changed_at

# ################################################################################################################################

def test_longest_note_round_trips_intact(
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    ) -> 'None':

    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Consult_Notes, checkpoint)

    # Every position holds a different character.
    characters:'strlist' = []

    for index in range(Note_Length):
        offset = index % Character_Count
        character = chr(First_Character + offset)
        characters.append(character)

    progress_note = ''.join(characters)
    note_length = len(progress_note)
    assert note_length == Note_Length

    changed_at = checkpoint + timedelta(minutes=1)

    facility.log_consult_note(changed_at, Operation_Insert, Consult_Note_ID,
        treatment_id=Treatment_ID, progress_note=progress_note)
    facility.commit()

    _ = run_sync(client, Source_Consult_Notes)

    sections = records.sections(Section_Consult_Notes)
    section = sections[0]
    fields = records.fields(section.section_id)

    assert fields[Field_Progress_Note] == progress_note

# ################################################################################################################################

def test_null_source_values_produce_no_field_rows(
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    ) -> 'None':

    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Treatments, checkpoint)

    changed_at = checkpoint + timedelta(minutes=1)

    # Only the patient is set - everything else in the log row is NULL.
    facility.log_treatment(changed_at, Operation_Insert, Treatment_ID, patient_id=Patient_ID)
    facility.commit()

    _ = run_sync(client, Source_Treatments)

    sections = records.sections(Section_Treatments)
    section = sections[0]
    fields = records.fields(section.section_id)

    # The ID and the patient are always there, nothing else is.
    assert fields == {
        Field_Treatment_ID: str(Treatment_ID),
        Field_Treatment_Patient: str(Patient_Reference),
    }

    assert records.count_fields() == 2

# ################################################################################################################################

def test_all_fields_of_a_full_treatment(
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    ) -> 'None':

    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Treatments, checkpoint)

    changed_at = checkpoint + timedelta(minutes=1)
    start_date = datetime(2026, 3, 1)
    end_date = datetime(2026, 3, 9)

    facility.log_treatment(changed_at, Operation_Insert, Treatment_ID,
        patient_id=Patient_ID,
        staff_id=Staff_ID,
        condition_id=Condition_ID,
        start_date=start_date,
        end_date=end_date,
        clarification='Follow-up in a week',
        attention_value_id=3,
    )
    facility.commit()

    _ = run_sync(client, Source_Treatments)

    sections = records.sections(Section_Treatments)
    section = sections[0]
    fields = records.fields(section.section_id)

    assert fields == {
        Field_Treatment_ID: str(Treatment_ID),
        Field_Treatment_Patient: str(Patient_Reference),
        Field_Staff: str(Staff_Reference),
        Field_Condition_Code: Condition_Code,
        Field_Condition_Title: Condition_Title,
        Field_Start_Date: '2026-03-01T00:00:00',
        Field_End_Date: '2026-03-09T00:00:00',
        Field_Clarification: 'Follow-up in a week',
        Field_Attention_Value: 'Inactive',
    }

# ################################################################################################################################
# ################################################################################################################################
