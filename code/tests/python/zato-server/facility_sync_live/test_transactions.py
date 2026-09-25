# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Project
from model.facility import Operation_Insert, Source_Consult_Notes, Source_Treatments

# Zato
from _support import add_references, Condition_ID, ModuleCtx, Patient_ID, run_sync_failing, Staff_ID, Treatment_ID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from _support import FacilityDatabase, FaultPlan, RecordsDatabase, SyncDatabase

# ################################################################################################################################
# ################################################################################################################################

def test_failed_run_leaves_no_rows_and_the_checkpoint_unchanged(
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    faults:'FaultPlan',
    ) -> 'None':
    """ With the package that never commits, a run is one transaction - the last step failing undoes all the earlier ones.
    """
    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Treatments, checkpoint)

    first_changed_at = checkpoint + timedelta(minutes=1)
    second_changed_at = checkpoint + timedelta(minutes=2)

    facility.log_treatment(first_changed_at, Operation_Insert, Treatment_ID,
        patient_id=Patient_ID, staff_id=Staff_ID, condition_id=Condition_ID)

    facility.log_treatment(second_changed_at, Operation_Insert, Treatment_ID + 1, patient_id=Patient_ID)
    facility.commit()

    # Both sections and all their fields were written before the checkpoint step.
    faults.raise_at(ModuleCtx.Step_Checkpoint_Update)
    _ = run_sync_failing(client, Source_Treatments)

    assert records.count_sections() == 0
    assert records.count_fields() == 0
    assert sync.map_rows() == []
    assert sync.checkpoint(Source_Treatments) == checkpoint

# ################################################################################################################################

def test_failure_in_one_source_does_not_touch_the_other(
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    faults:'FaultPlan',
    ) -> 'None':

    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Treatments, checkpoint)
    sync.seed_checkpoint(Source_Consult_Notes, checkpoint)

    changed_at = checkpoint + timedelta(minutes=1)

    facility.log_treatment(changed_at, Operation_Insert, Treatment_ID, patient_id=Patient_ID)
    facility.commit()

    faults.raise_at(ModuleCtx.Step_Section_Create)
    _ = run_sync_failing(client, Source_Treatments)

    assert sync.checkpoint(Source_Treatments) == checkpoint
    assert sync.checkpoint(Source_Consult_Notes) == checkpoint
    assert records.count_sections() == 0

# ################################################################################################################################
# ################################################################################################################################
