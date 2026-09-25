# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Project
from model.facility import Operation_Insert, Read_Overlap, Section_Treatments, Source_Treatments

# Zato
from _support import add_references, ModuleCtx, Patient_ID, Patient_Reference, run_sync

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import intlist, strlist
    from _support import FacilityDatabase, RecordsDatabase, SyncDatabase

# ################################################################################################################################
# ################################################################################################################################

# The service that reads one source's log.
Read_Service = 'facility.change.read-log'

# ################################################################################################################################
# ################################################################################################################################

def test_changes_arrive_in_timestamp_order_and_only_after_since(
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    ) -> 'None':

    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    since = checkpoint - Read_Overlap

    before_window = since - timedelta(minutes=5)
    inside_window_before_checkpoint = checkpoint - timedelta(minutes=2)
    after_checkpoint_first = checkpoint + timedelta(minutes=1)
    after_checkpoint_second = checkpoint + timedelta(minutes=2)

    # Logged out of order.
    facility.log_treatment(after_checkpoint_second, Operation_Insert, 5003, patient_id=Patient_ID)
    facility.log_treatment(before_window, Operation_Insert, 5000, patient_id=Patient_ID)
    facility.log_treatment(inside_window_before_checkpoint, Operation_Insert, 5001, patient_id=Patient_ID)
    facility.log_treatment(since, Operation_Insert, 5004, patient_id=Patient_ID)
    facility.log_treatment(after_checkpoint_first, Operation_Insert, 5002, patient_id=Patient_ID)
    facility.commit()

    since_iso = since.isoformat()
    request = {'source': Source_Treatments, 'since': since_iso}

    response = client.invoke(Read_Service, request)
    changes = response['changes']

    source_ids:'intlist' = []
    changed_at_list:'strlist' = []

    for change in changes:
        source_ids.append(change['source_id'])
        changed_at_list.append(change['changed_at'])

    # The row before the window and the row exactly at its start are both left out.
    assert source_ids == [5001, 5002, 5003]
    assert changed_at_list == sorted(changed_at_list)

    # A run reads the same window and moves the checkpoint to the newest row it saw.
    sync.seed_checkpoint(Source_Treatments, checkpoint)
    _ = run_sync(client, Source_Treatments)

    sections = records.sections(Section_Treatments)
    sequence_numbers:'intlist' = []

    for section in sections:
        assert section.patient == Patient_Reference
        sequence_numbers.append(section.sequence_number)

    assert sorted(sequence_numbers) == [5001, 5002, 5003]
    assert sync.checkpoint(Source_Treatments) == after_checkpoint_second

# ################################################################################################################################

def test_run_without_changes_leaves_checkpoint_alone(client:'AdminClient', sync:'SyncDatabase') -> 'None':

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Treatments, checkpoint)

    response = run_sync(client, Source_Treatments)

    assert response['applied'] == 0
    assert sync.checkpoint(Source_Treatments) == checkpoint

# ################################################################################################################################
# ################################################################################################################################
