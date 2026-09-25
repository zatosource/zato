# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# pytest
import pytest

# Project
from model.facility import Operation_Insert, Section_Treatments, Source_Treatments

# Zato
from _schema import ModuleCtx as SchemaCtx
from _support import add_references, Condition_ID, Field_Treatment_ID, ModuleCtx, Patient_ID, run_sync, run_sync_failing, \
    Staff_ID, Treatment_ID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from _support import FacilityDatabase, FaultPlan, RecordsDatabase, SyncDatabase

# ################################################################################################################################
# ################################################################################################################################

# Every step a run can fail at, in the order a run reaches them.
Steps = (
    ModuleCtx.Step_Section_Create,
    ModuleCtx.Step_Field_Save,
    ModuleCtx.Step_Map_Insert,
    ModuleCtx.Step_Checkpoint_Update,
)

# With the committing package a fault at one of these steps leaves a second section behind.
Steps_Duplicating_With_Commit = (
    ModuleCtx.Step_Field_Save,
    ModuleCtx.Step_Map_Insert,
)

# What the one treatment of these tests writes - the ID, the patient, the staff member, the code and the title.
Field_Count = 5

# ################################################################################################################################
# ################################################################################################################################

def _expected_sections(step:'str', variant:'str') -> 'int':
    out = 1

    if variant == SchemaCtx.Variant_Commit:
        if step in Steps_Duplicating_With_Commit:
            out = 2

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('step', Steps)
def test_rerun_after_a_fault_converges(
    step:'str',
    records_api:'str',
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    faults:'FaultPlan',
    ) -> 'None':

    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    changed_at = checkpoint + timedelta(minutes=1)
    sync.seed_checkpoint(Source_Treatments, checkpoint)

    facility.log_treatment(changed_at, Operation_Insert, Treatment_ID,
        patient_id=Patient_ID, staff_id=Staff_ID, condition_id=Condition_ID)
    facility.commit()

    # The first run fails at the planned step ..
    faults.raise_at(step)
    error = run_sync_failing(client, Source_Treatments)
    assert step in error

    # .. and however far it got, the checkpoint did not move ..
    assert sync.checkpoint(Source_Treatments) == checkpoint

    # .. the rerun without the fault brings the target to where it should be.
    faults.clear()
    _ = run_sync(client, Source_Treatments)

    assert sync.checkpoint(Source_Treatments) == changed_at

    map_rows = sync.map_rows()
    map_row_count = len(map_rows)
    assert map_row_count == 1

    map_row = map_rows[0]
    mapped = records.fields(map_row.section_id)
    mapped_count = len(mapped)

    assert mapped_count == Field_Count
    assert mapped[Field_Treatment_ID] == str(Treatment_ID)

    # Only the mapped section has fields.
    assert records.count_fields() == Field_Count

    # The committing variant leaves a duplicate section behind at these steps.
    sections = records.sections(Section_Treatments)
    section_count = len(sections)
    expected_count = _expected_sections(step, records_api)

    assert section_count == expected_count

# ################################################################################################################################
# ################################################################################################################################
