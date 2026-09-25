# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Project
from model.facility import Operation_Insert, Section_Treatments, Source_Treatments

# Zato
from _support import add_references, FacilityDatabase, ModuleCtx, Patient_ID, run_sync

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import intlist
    from _schema import Schema
    from _support import RecordsDatabase, SyncDatabase

# ################################################################################################################################
# ################################################################################################################################

def test_row_committed_late_is_applied_through_the_overlap(
    client:'AdminClient',
    schema:'Schema',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    ) -> 'None':

    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Treatments, checkpoint)

    late_changed_at = checkpoint + timedelta(minutes=1)
    newer_changed_at = checkpoint + timedelta(minutes=3)

    # A second session logs a change and holds it open.
    late_session = FacilityDatabase(schema)

    try:
        late_session.log_treatment(late_changed_at, Operation_Insert, 5001, patient_id=Patient_ID)

        # Meanwhile, a newer change is committed and synced.
        facility.log_treatment(newer_changed_at, Operation_Insert, 5002, patient_id=Patient_ID)
        facility.commit()

        _ = run_sync(client, Source_Treatments)

        sections = records.sections(Section_Treatments)
        section_count = len(sections)
        assert section_count == 1

        section = sections[0]
        assert section.sequence_number == 5002
        assert sync.checkpoint(Source_Treatments) == newer_changed_at

        # Only now does the late change become visible.
        late_session.commit()

    finally:
        late_session.close()

    # The next run reads from before its checkpoint and picks the late row up.
    _ = run_sync(client, Source_Treatments)

    sequence_numbers:'intlist' = []

    for section in records.sections(Section_Treatments):
        sequence_numbers.append(section.sequence_number)

    assert sorted(sequence_numbers) == [5001, 5002]

    # The newest row seen was still the one from the first run, so the checkpoint stays put.
    assert sync.checkpoint(Source_Treatments) == newer_changed_at

# ################################################################################################################################
# ################################################################################################################################
