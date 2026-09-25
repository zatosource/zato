# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections.abc import Generator
from datetime import datetime, timedelta
from typing import NamedTuple

# pytest
import pytest

# Zato
from zato.common.api import SCHEDULER
from zato.common.defaults import default_cluster_id

# Live environment
from live_containers.ready import wait_until

# Project
from model.facility import Operation_Insert, Section_Consult_Notes, Section_Treatments, Source_Consult_Notes, \
    Source_Treatments

# Zato - the suite's own parts
from _support import add_references, Consult_Note_ID, ModuleCtx, Patient_ID, Treatment_ID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_environment.scheduler import SchedulerProcess
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import dictlist
    from _support import FacilityDatabase, FaultPlan, RecordsDatabase, SyncDatabase

# ################################################################################################################################
# ################################################################################################################################

run_list      = list['Run']
scheduler_gen = Generator['SchedulerProcess', None, None]

# ################################################################################################################################
# ################################################################################################################################

# The jobs enmasse.yaml defines, one per source.
Job_Treatments    = 'facility.sync.treatments'
Job_Consult_Notes = 'facility.sync.consult-notes'

# The interval both jobs fire at, as enmasse.yaml has it.
Job_Interval = timedelta(seconds=5)

Job_Service     = 'zato.scheduler.job.get-by-name'
History_Service = 'zato.scheduler.job.get-history'
History_Page    = 50

# A run of one treatment saves two fields at the least, its ID and its patient, and each save sleeps this long.
Sleep_Seconds  = 4
Fields_Per_Run = 2

Run_Duration = timedelta(seconds=Sleep_Seconds * Fields_Per_Run)

# How many runs the in-flight test waits for before it looks at how they were spaced.
Runs_To_Observe = 3

# ################################################################################################################################
# ################################################################################################################################

class Run(NamedTuple):
    """ One completed run of a job - when the server took it up and how long it kept it.
    """
    started_at: 'datetime'
    duration:   'timedelta'
    outcome:    'str'

# ################################################################################################################################
# ################################################################################################################################

def _job_id(client:'AdminClient', job_name:'str') -> 'int':
    response = client.invoke(Job_Service, {'cluster_id': default_cluster_id, 'name': job_name})

    out = response['id']
    return out

# ################################################################################################################################

def _history(client:'AdminClient', job_name:'str') -> 'dictlist':
    """ The newest runs of a job, the ones still going included.
    """
    job_id = _job_id(client, job_name)
    request = {'id': job_id, 'page': 1, 'page_size': History_Page}
    response = client.invoke(History_Service, request)

    out = response['rows']
    return out

# ################################################################################################################################

def _completed_runs(client:'AdminClient', job_name:'str') -> 'run_list':
    """ The runs of a job that finished, oldest first.
    """
    out:'run_list' = []

    for row in _history(client, job_name):

        if row['outcome'] == SCHEDULER.OUTCOME.RUNNING:
            continue

        fire_time = row['actual_fire_time_iso']
        started_at = datetime.fromisoformat(fire_time)

        duration_ms = row['duration_ms']
        duration = timedelta(milliseconds=duration_ms)

        outcome = row['outcome']

        run = Run(started_at, duration, outcome)
        out.append(run)

    out.sort()
    return out

# ################################################################################################################################

def _new_runs(client:'AdminClient', job_name:'str', known:'run_list') -> 'run_list':
    """ The completed runs of a job other than the ones a test saw before it started the scheduler.
    """
    out:'run_list' = []

    for run in _completed_runs(client, job_name):
        if run not in known:
            out.append(run)

    return out

# ################################################################################################################################

def _has_good_run(client:'AdminClient', job_name:'str', known:'run_list') -> 'bool':

    for run in _new_runs(client, job_name, known):
        if run.outcome == SCHEDULER.OUTCOME.OK:
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################

def _has_run_in_flight(client:'AdminClient') -> 'bool':

    rows:'dictlist' = []

    for job_name in (Job_Treatments, Job_Consult_Notes):
        job_rows = _history(client, job_name)
        rows.extend(job_rows)

    for row in rows:
        if row['outcome'] == SCHEDULER.OUTCOME.RUNNING:
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def running_scheduler(client:'AdminClient', scheduler:'SchedulerProcess') -> 'scheduler_gen':
    """ The scheduler for one test - the test starts it once its data is in place, and it is gone,
    with no run of its left in the server, before the next test resets the tables.
    """
    yield scheduler

    scheduler.stop()

    def _nothing_runs() -> 'bool':
        out = not _has_run_in_flight(client)
        return out

    wait_until(_nothing_runs, 'the last scheduled run to finish')

# ################################################################################################################################
# ################################################################################################################################

def test_two_jobs_sync_two_sources_without_anyone_invoking_the_service(
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    running_scheduler:'SchedulerProcess',
    ) -> 'None':

    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Treatments, checkpoint)
    sync.seed_checkpoint(Source_Consult_Notes, checkpoint)

    treatment_changed_at = checkpoint + timedelta(minutes=1)
    note_changed_at = checkpoint + timedelta(minutes=2)

    facility.log_treatment(treatment_changed_at, Operation_Insert, Treatment_ID, patient_id=Patient_ID)
    facility.log_consult_note(note_changed_at, Operation_Insert, Consult_Note_ID, treatment_id=Treatment_ID)
    facility.commit()

    # The jobs start firing.
    treatment_runs_before = _completed_runs(client, Job_Treatments)
    consult_note_runs_before = _completed_runs(client, Job_Consult_Notes)

    running_scheduler.start()

    def _both_sources_synced() -> 'bool':
        treatments = records.sections(Section_Treatments)
        consult_notes = records.sections(Section_Consult_Notes)

        treatment_count = len(treatments)
        consult_note_count = len(consult_notes)

        out = False

        if treatment_count == 1:
            if consult_note_count == 1:
                out = True

        return out

    wait_until(_both_sources_synced, 'both sources to be synced by the scheduler')

    assert sync.checkpoint(Source_Treatments) == treatment_changed_at
    assert sync.checkpoint(Source_Consult_Notes) == note_changed_at

    # Each job has at least one run that went well.
    def _treatments_ran_well() -> 'bool':
        out = _has_good_run(client, Job_Treatments, treatment_runs_before)
        return out

    def _consult_notes_ran_well() -> 'bool':
        out = _has_good_run(client, Job_Consult_Notes, consult_note_runs_before)
        return out

    wait_until(_treatments_ran_well, f'a completed run of {Job_Treatments}')
    wait_until(_consult_notes_ran_well, f'a completed run of {Job_Consult_Notes}')

# ################################################################################################################################

def test_run_still_in_flight_is_not_started_again(
    client:'AdminClient',
    facility:'FacilityDatabase',
    records:'RecordsDatabase',
    sync:'SyncDatabase',
    faults:'FaultPlan',
    running_scheduler:'SchedulerProcess',
    ) -> 'None':
    """ A run that outlasts the interval is left alone - the fires that fall while it runs start nothing,
    and the next run only begins once it is over.
    """
    add_references(facility)

    checkpoint = ModuleCtx.Base_Time
    sync.seed_checkpoint(Source_Treatments, checkpoint)
    sync.seed_checkpoint(Source_Consult_Notes, checkpoint)

    changed_at = checkpoint + timedelta(minutes=1)

    facility.log_treatment(changed_at, Operation_Insert, Treatment_ID, patient_id=Patient_ID)
    facility.commit()

    # Every run of the treatments job now takes longer than the interval between fires.
    assert Run_Duration > Job_Interval
    faults.sleep_at(ModuleCtx.Step_Field_Save, Sleep_Seconds)

    runs_before = _completed_runs(client, Job_Treatments)
    running_scheduler.start()

    def _enough_runs_completed() -> 'bool':
        new_runs = _new_runs(client, Job_Treatments, runs_before)
        new_run_count = len(new_runs)

        out = new_run_count >= Runs_To_Observe
        return out

    wait_until(_enough_runs_completed, f'{Runs_To_Observe} completed runs of {Job_Treatments}')

    runs = _new_runs(client, Job_Treatments, runs_before)
    previous = runs[0]

    for current in runs[1:]:

        # Each run began only after the previous one had ended, however many fires fell in between.
        previous_ended_at = previous.started_at + previous.duration
        assert current.started_at >= previous_ended_at, (previous, current)
        previous = current

    for run in runs:
        assert run.outcome == SCHEDULER.OUTCOME.OK, run
        assert run.duration >= Run_Duration, run

    sections = records.sections(Section_Treatments)
    section_count = len(sections)
    assert section_count == 1

    map_rows = sync.map_rows()
    map_row_count = len(map_rows)
    assert map_row_count == 1

# ################################################################################################################################
# ################################################################################################################################
