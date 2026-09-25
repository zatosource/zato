# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Project
from model.facility import Operation_Delete, Operation_Insert, Source_Consult_Notes, Source_Treatments

# Zato
from _support import add_references, Consult_Note_ID, ModuleCtx, Patient_ID, run_sync, run_sync_failing, Treatment_ID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from _support import FacilityDatabase, RecordsDatabase, SyncDatabase

# ################################################################################################################################
# ################################################################################################################################

# A patient that is added and then removed before the sync runs.
Removed_Patient_ID        = 102
Removed_Patient_Reference = 90102

# A treatment nothing in the current tables knows.
Unknown_Treatment_ID = 5999

# ################################################################################################################################
# ################################################################################################################################

def test_change_pointing_at_a_deleted_patient_fails_the_run(
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

    facility.add_patient(Removed_Patient_ID, Removed_Patient_Reference, 'Mary Jones')

    # A change for a known patient and one for the patient that is about to disappear.
    facility.log_treatment(first_changed_at, Operation_Insert, Treatment_ID, patient_id=Patient_ID)
    facility.log_treatment(second_changed_at, Operation_Insert, Treatment_ID + 1, patient_id=Removed_Patient_ID)

    facility.delete_patient(Removed_Patient_ID)
    facility.commit()

    error = run_sync_failing(client, Source_Treatments)
    assert str(Removed_Patient_ID) in error

    # Nothing of the batch was written, the good change included, and the checkpoint stayed where it was.
    assert records.count_sections() == 0
    assert sync.map_rows() == []
    assert sync.checkpoint(Source_Treatments) == checkpoint

    # Once the patient is back, the same batch goes through.
    facility.add_patient(Removed_Patient_ID, Removed_Patient_Reference, 'Mary Jones')
    facility.commit()

    _ = run_sync(client, Source_Treatments)

    assert records.count_sections() == 2
    assert sync.checkpoint(Source_Treatments) == second_changed_at

# ################################################################################################################################

def test_consult_note_pointing_at_an_unknown_treatment_fails_the_run(
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    ) -> 'None':

    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Consult_Notes, checkpoint)

    changed_at = checkpoint + timedelta(minutes=1)

    facility.log_consult_note(changed_at, Operation_Insert, Consult_Note_ID, treatment_id=Unknown_Treatment_ID)
    facility.commit()

    error = run_sync_failing(client, Source_Consult_Notes)
    assert str(Unknown_Treatment_ID) in error

    assert records.count_sections() == 0
    assert sync.checkpoint(Source_Consult_Notes) == checkpoint

# ################################################################################################################################

def test_delete_of_a_row_whose_patient_is_gone_still_applies(
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    ) -> 'None':
    """ A deletion needs no references - the section goes away even if the patient did too.
    """
    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Treatments, checkpoint)

    insert_changed_at = checkpoint + timedelta(minutes=1)
    delete_changed_at = checkpoint + timedelta(minutes=2)

    facility.add_patient(Removed_Patient_ID, Removed_Patient_Reference, 'Mary Jones')
    facility.log_treatment(insert_changed_at, Operation_Insert, Treatment_ID, patient_id=Removed_Patient_ID)
    facility.commit()

    _ = run_sync(client, Source_Treatments)
    assert records.count_sections() == 1

    facility.log_treatment(delete_changed_at, Operation_Delete, Treatment_ID, patient_id=Removed_Patient_ID)
    facility.delete_patient(Removed_Patient_ID)
    facility.commit()

    _ = run_sync(client, Source_Treatments)

    assert records.count_sections() == 0
    assert sync.map_rows() == []

# ################################################################################################################################
# ################################################################################################################################
