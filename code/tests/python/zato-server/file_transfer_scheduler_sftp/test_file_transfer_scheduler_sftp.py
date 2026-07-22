# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
from datetime import datetime, timezone
from getpass import getuser
from json import loads
from uuid import uuid4

# PyPI
import pytest

# Zato
from zato.common.api import FileTransfer, SCHEDULER, SchedulerLink
from zato.common.defaults import default_cluster_id
from zato.common.test.client import AdminClient

# Local test helpers
from _config import TestConfig

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler
_conn_type = FileTransfer.ConnType.SFTP

_service_conn = 'zato.generic.connection'
_service_job = 'zato.scheduler.job'
_service_schedule = 'zato.outgoing.file-transfer.schedule'

_conn_name_prefix = 'test-file-transfer-sftp-'
_job_name_prefix = _scheduler.Job_Prefix[_conn_type] + _conn_name_prefix

_start_date = '2099-01-01T00:00:00'

_ping_wait_seconds = 30
_fire_wait_seconds = 45

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client():
    base_url = f'http://{TestConfig.host}:{TestConfig.server_port}'
    return AdminClient(base_url, TestConfig.invoke_password)

# ################################################################################################################################

@pytest.fixture(autouse=True)
def cleanup(client):
    """ Deletes everything a test may have left behind so that each test starts from a clean slate.
    """
    yield

    # Deleting a connection also deletes the jobs of all its schedules
    data, _meta = client.get_list(
        f'{_service_conn}.get-list', cluster_id=default_cluster_id, type_=_conn_type, paginate=True, cur_page=1)

    for item in data:
        if item['name'].startswith(_conn_name_prefix):
            _ = client.delete(f'{_service_conn}.delete', id=item['id'])

    # Jobs whose connection is already gone are deleted directly
    data, _meta = client.get_list(f'{_service_job}.get-list', cluster_id=default_cluster_id)

    for item in data:
        if item['name'].startswith(_job_name_prefix):
            _ = client.delete(f'{_service_job}.delete', id=item['id'])

# ################################################################################################################################

def _unwrap(response):
    """ Some services wrap their response in a single zato_* root element.
    """
    if isinstance(response, dict) and len(response) == 1:
        key = next(iter(response))
        if key.startswith('zato_'):
            response = response[key]
    return response

# ################################################################################################################################

def _new_conn_name():
    return _conn_name_prefix + uuid4().hex[:12]

# ################################################################################################################################

def _get_job_names(client):
    data, _meta = client.get_list(f'{_service_job}.get-list', cluster_id=default_cluster_id)

    out = []
    for item in data:
        out.append(item['name'])

    return out

# ################################################################################################################################

def _get_job(client, name):
    out = _unwrap(client.invoke(f'{_service_job}.get-by-name', {'cluster_id': default_cluster_id, 'name': name}))
    return out

# ################################################################################################################################

def _create_conn(client, sftp_test_server, name):
    """ Creates an SFTP connection pointing to the test SSH server and returns its ID.
    """
    response = _unwrap(client.create(f'{_service_conn}.create',
        cluster_id=default_cluster_id,
        name=name,
        type_=_conn_type,
        is_active=True,
        is_internal=False,
        is_channel=False,
        is_outgoing=True,
        is_outconn=True,
        pool_size=1,
        address=f'{sftp_test_server.host}:{sftp_test_server.port}',
        username=getuser(),
        private_key=TestConfig.key_env_name,
        strict_host_key_checking=False,
    ))

    out = response['id']
    return out

# ################################################################################################################################

def _schedule_request(conn_id, name, directory, **extra):
    """ A base create/edit payload for one schedule of a connection.
    """
    out = {
        'conn_id': conn_id,
        'name': name,
        'is_active': True,
        'directory': directory,
        'ready_how': _scheduler.ReadyHow.Stability,
        'stability_delay': 1,
        'service': TestConfig.service_store_file,
        'on_success': _scheduler.OnSuccess.Move,
        'move_directory': _scheduler.Default_Move_Directory,
        'run_every': 5,
        'run_unit': _scheduler.Unit.Minutes,
        'start_date': _start_date,
    }
    out.update(extra)

    return out

# ################################################################################################################################

def _create_schedule(client, conn_id, name, directory, **extra):
    """ Creates one schedule and returns its response with the id and job_id.
    """
    request = _schedule_request(conn_id, name, directory, **extra)
    out = _unwrap(client.invoke(f'{_service_schedule}.create', request))

    return out

# ################################################################################################################################

def _get_schedules(client, conn_id):
    out = client.invoke(f'{_service_schedule}.get-list', {'conn_id': conn_id})

    if isinstance(out, str):
        out = loads(out)

    return out

# ################################################################################################################################

def _get_schedule(client, conn_id, schedule_id):
    for schedule in _get_schedules(client, conn_id):
        if schedule['id'] == schedule_id:
            return schedule

    return None

# ################################################################################################################################

def _read_evidence(schedule_name):
    """ Returns the entries of the evidence file whose schedule name matches the given one.
    """
    out = []

    # The file comes into existence only once the first item was recorded
    if not os.path.exists(TestConfig.evidence_file):
        return out

    with open(TestConfig.evidence_file) as evidence:
        for line in evidence:
            line = line.strip()
            if line:
                entry = loads(line)
                if entry['schedule_name'] == schedule_name:
                    out.append(entry)

    return out

# ################################################################################################################################

def _invoke_dispatch(client, conn_id, conn_name, schedule):
    """ Invokes the dispatch service directly, the way a scheduler fire event does it, retrying until the newly
    created connection has propagated to the server's connection store.
    """
    payload = {
        _scheduler.Extra_Conn_ID: conn_id,
        _scheduler.Extra_Conn_Name: conn_name,
        _scheduler.Extra_Conn_Type: _conn_type,
        _scheduler.Extra_Schedule: schedule,
    }

    deadline = time.monotonic() + _ping_wait_seconds
    last_error = None

    while time.monotonic() < deadline:
        try:
            _ = client.invoke(_scheduler.Dispatch_Service[_conn_type], payload)
        except Exception as e:
            last_error = e
            time.sleep(1)
            continue
        else:
            return

    raise AssertionError(f'Could not invoke the dispatch service, last error: {last_error}')

# ################################################################################################################################

def _make_remote_directory(sftp_test_server):
    """ Creates a new directory for one test's remote files, returning its absolute path -
    the test SSH server serves local paths directly.
    """
    out = os.path.join(sftp_test_server.files_dir, uuid4().hex[:12])
    os.mkdir(out)

    return out

# ################################################################################################################################

def _write_remote_file(directory, file_name, data):
    full_path = os.path.join(directory, file_name)

    with open(full_path, 'w') as remote_file:
        _ = remote_file.write(data)

    return full_path

# ################################################################################################################################
# ################################################################################################################################

def test_create_schedule_creates_job(client, sftp_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, sftp_test_server, conn_name)

    response = _create_schedule(client, conn_id, 'invoices.hourly', '/incoming/invoices')

    schedule_id = response['id']
    job_id = response['job_id']

    assert schedule_id == 'invoices.hourly'

    # The job exists, is interval-based and points back to its connection
    job_name = _scheduler.Job_Prefix[_conn_type] + conn_name + '.invoices.hourly'
    job = _get_job(client, job_name)

    assert int(job['id']) == int(job_id)
    assert job['job_type'] == SCHEDULER.JOB_TYPE.INTERVAL_BASED
    assert job['service_name'] == _scheduler.Dispatch_Service[_conn_type]
    assert int(job['minutes']) == 5
    assert int(job[SchedulerLink.Conn_ID]) == int(conn_id)
    assert job[SchedulerLink.Conn_Type] == _conn_type
    assert job[SchedulerLink.Kind] == schedule_id

    # The job's extra data carries the connection's identity and the full schedule
    extra = loads(job['extra'])

    assert int(extra[_scheduler.Extra_Conn_ID]) == int(conn_id)
    assert extra[_scheduler.Extra_Conn_Name] == conn_name
    assert extra[_scheduler.Extra_Conn_Type] == _conn_type
    assert extra[_scheduler.Extra_Schedule]['directory'] == '/incoming/invoices'

    # The connection's own list mirrors the job
    schedule = _get_schedule(client, conn_id, schedule_id)

    assert schedule['name'] == 'invoices.hourly'
    assert schedule['directory'] == '/incoming/invoices'
    assert schedule['pattern'] == _scheduler.Default_Pattern
    assert schedule['run_every'] == 5
    assert schedule['run_unit'] == _scheduler.Unit.Minutes
    assert int(schedule['job_id']) == int(job_id)

# ################################################################################################################################

def test_edit_schedule_updates_job(client, sftp_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, sftp_test_server, conn_name)

    response = _create_schedule(client, conn_id, 'reports.daily', '/incoming/reports')

    schedule_id = response['id']
    job_id = response['job_id']

    # Change the interval and the directory through the schedule's edit
    request = _schedule_request(conn_id, 'reports.daily', '/incoming/reports-v2', run_every=3, run_unit=_scheduler.Unit.Hours)
    request['id'] = schedule_id

    _ = client.invoke(f'{_service_schedule}.edit', request)

    # It is still the same job, just with a new interval and extra data
    job_name = _scheduler.Job_Prefix[_conn_type] + conn_name + '.reports.daily'
    job = _get_job(client, job_name)

    assert int(job['id']) == int(job_id)
    assert int(job['hours']) == 3
    assert int(job['minutes']) == 0

    extra = loads(job['extra'])
    assert extra[_scheduler.Extra_Schedule]['directory'] == '/incoming/reports-v2'

    # The connection's own list reflects the edit as well
    schedule = _get_schedule(client, conn_id, schedule_id)

    assert schedule['directory'] == '/incoming/reports-v2'
    assert schedule['run_every'] == 3
    assert schedule['run_unit'] == _scheduler.Unit.Hours

# ################################################################################################################################

def test_job_edit_syncs_back_to_schedule(client, sftp_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, sftp_test_server, conn_name)

    response = _create_schedule(client, conn_id, 'sync.back', '/incoming/sync')

    schedule_id = response['id']
    job_id = response['job_id']

    job_name = _scheduler.Job_Prefix[_conn_type] + conn_name + '.sync.back'
    job = _get_job(client, job_name)

    # Edit the job directly, the way the scheduler UI does it - changing its interval
    _ = client.edit(f'{_service_job}.edit',
        cluster_id=default_cluster_id,
        id=job_id,
        name=job_name,
        is_active=True,
        job_type=SCHEDULER.JOB_TYPE.INTERVAL_BASED,
        service=_scheduler.Dispatch_Service[_conn_type],
        start_date=_start_date,
        minutes=7,
        extra=job['extra'],
    )

    # The connection's schedule entry now shows the job's new interval
    schedule = _get_schedule(client, conn_id, schedule_id)

    assert schedule['run_every'] == 7
    assert schedule['run_unit'] == _scheduler.Unit.Minutes
    assert int(schedule['job_id']) == int(job_id)

# ################################################################################################################################

def test_job_delete_removes_schedule_entry(client, sftp_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, sftp_test_server, conn_name)

    response = _create_schedule(client, conn_id, 'to.be.deleted', '/incoming/deleted')

    schedule_id = response['id']
    job_id = response['job_id']

    # Delete the job directly, the way the scheduler UI does it
    _ = client.delete(f'{_service_job}.delete', id=job_id)

    # The schedule entry is gone from the connection as well
    assert _get_schedule(client, conn_id, schedule_id) is None

# ################################################################################################################################

def test_delete_schedule_deletes_job(client, sftp_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, sftp_test_server, conn_name)

    response = _create_schedule(client, conn_id, 'short.lived', '/incoming/short')
    schedule_id = response['id']

    job_name = _scheduler.Job_Prefix[_conn_type] + conn_name + '.short.lived'
    assert job_name in _get_job_names(client)

    _ = client.invoke(f'{_service_schedule}.delete', {'conn_id': conn_id, 'id': schedule_id})

    # Both the job and the entry are gone
    assert job_name not in _get_job_names(client)
    assert _get_schedule(client, conn_id, schedule_id) is None

# ################################################################################################################################

def test_conn_delete_removes_jobs(client, sftp_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, sftp_test_server, conn_name)

    _ = _create_schedule(client, conn_id, 'first.one', '/incoming/first')
    _ = _create_schedule(client, conn_id, 'second.one', '/incoming/second')

    job_name_first = _scheduler.Job_Prefix[_conn_type] + conn_name + '.first.one'
    job_name_second = _scheduler.Job_Prefix[_conn_type] + conn_name + '.second.one'

    job_names = _get_job_names(client)

    assert job_name_first in job_names
    assert job_name_second in job_names

    # Deleting the connection removes the jobs of all its schedules
    _ = client.delete(f'{_service_conn}.delete', id=conn_id)

    job_names = _get_job_names(client)

    assert job_name_first not in job_names
    assert job_name_second not in job_names

# ################################################################################################################################

def test_conn_rename_renames_jobs(client, sftp_test_server):

    conn_name = _new_conn_name()
    new_conn_name = _new_conn_name()

    conn_id = _create_conn(client, sftp_test_server, conn_name)
    _ = _create_schedule(client, conn_id, 'renamed.along', '/incoming/renamed')

    # Rename the connection through its edit
    _ = client.edit(f'{_service_conn}.edit',
        cluster_id=default_cluster_id,
        id=conn_id,
        name=new_conn_name,
        type_=_conn_type,
        is_active=True,
        is_internal=False,
        is_channel=False,
        is_outgoing=True,
        is_outconn=True,
        pool_size=1,
        address=f'{sftp_test_server.host}:{sftp_test_server.port}',
        username=getuser(),
        private_key=TestConfig.key_env_name,
        strict_host_key_checking=False,
    )

    old_job_name = _scheduler.Job_Prefix[_conn_type] + conn_name + '.renamed.along'
    new_job_name = _scheduler.Job_Prefix[_conn_type] + new_conn_name + '.renamed.along'

    job_names = _get_job_names(client)

    # The job now follows the connection's new name ..
    assert new_job_name in job_names
    assert old_job_name not in job_names

    # .. and its extra data carries the new name as well.
    job = _get_job(client, new_job_name)
    extra = loads(job['extra'])

    assert extra[_scheduler.Extra_Conn_Name] == new_conn_name

# ################################################################################################################################

def test_duplicate_schedule_name_is_rejected(client, sftp_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, sftp_test_server, conn_name)

    _ = _create_schedule(client, conn_id, 'only.once', '/incoming/once')

    with pytest.raises(Exception, match='already exists'):
        _ = _create_schedule(client, conn_id, 'only.once', '/incoming/once-again')

    # There is still just the one schedule
    assert len(_get_schedules(client, conn_id)) == 1

# ################################################################################################################################

def test_marker_mode_without_suffix_is_rejected(client, sftp_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, sftp_test_server, conn_name)

    with pytest.raises(Exception, match='Marker suffix'):
        _ = _create_schedule(client, conn_id, 'no.marker.suffix', '/incoming/markers',
            ready_how=_scheduler.ReadyHow.Marker, marker_suffix='')

    # Neither a schedule nor a job were created
    assert _get_schedules(client, conn_id) == []
    assert _scheduler.Job_Prefix[_conn_type] + conn_name + '.no.marker.suffix' not in _get_job_names(client)

# ################################################################################################################################

def test_dispatch_moves_file_on_success(client, sftp_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, sftp_test_server, conn_name)

    directory = _make_remote_directory(sftp_test_server)
    schedule_name = 'move.' + uuid4().hex[:8]

    _ = _write_remote_file(directory, 'first.txt', 'First file payload')
    _ = _write_remote_file(directory, 'second.txt', 'Second file payload')

    response = _create_schedule(client, conn_id, schedule_name, directory)
    schedule = _get_schedule(client, conn_id, response['id'])

    # Invoke the dispatch service directly, the way a scheduler fire event does it
    _invoke_dispatch(client, conn_id, conn_name, schedule)

    # The target service saw each of the two files exactly once ..
    entries = _read_evidence(schedule_name)
    assert len(entries) == 2

    entry_by_name = {}
    for entry in entries:
        entry_by_name[entry['file_name']] = entry

    # .. with the full details of each of them ..
    entry = entry_by_name['first.txt']

    assert entry['conn_type'] == _conn_type
    assert entry['conn_name'] == conn_name
    assert entry['directory'] == directory
    assert entry['full_path'] == f'{directory}/first.txt'
    assert entry['size'] == len('First file payload')
    assert entry['data'] == 'First file payload'

    entry = entry_by_name['second.txt']
    assert entry['data'] == 'Second file payload'

    # .. and both files were moved into the destination directory.
    move_directory = os.path.join(directory, _scheduler.Default_Move_Directory)

    assert sorted(os.listdir(move_directory)) == ['first.txt', 'second.txt']
    assert sorted(os.listdir(directory)) == [_scheduler.Default_Move_Directory]

# ################################################################################################################################

def test_dispatch_deletes_file_on_success(client, sftp_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, sftp_test_server, conn_name)

    directory = _make_remote_directory(sftp_test_server)
    schedule_name = 'delete.' + uuid4().hex[:8]

    _ = _write_remote_file(directory, 'ephemeral.txt', 'Payload to delete after processing')

    response = _create_schedule(client, conn_id, schedule_name, directory,
        on_success=_scheduler.OnSuccess.Delete, move_directory='')
    schedule = _get_schedule(client, conn_id, response['id'])

    _invoke_dispatch(client, conn_id, conn_name, schedule)

    # The file was recorded and then deleted rather than moved
    entries = _read_evidence(schedule_name)

    assert len(entries) == 1
    assert entries[0]['data'] == 'Payload to delete after processing'

    assert os.listdir(directory) == []

# ################################################################################################################################

def test_dispatch_pattern_leaves_other_files_alone(client, sftp_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, sftp_test_server, conn_name)

    directory = _make_remote_directory(sftp_test_server)
    schedule_name = 'pattern.' + uuid4().hex[:8]

    _ = _write_remote_file(directory, 'data.csv', 'name,value')
    _ = _write_remote_file(directory, 'notes.txt', 'Not a CSV file')

    response = _create_schedule(client, conn_id, schedule_name, directory, pattern='*.csv')
    schedule = _get_schedule(client, conn_id, response['id'])

    _invoke_dispatch(client, conn_id, conn_name, schedule)

    # Only the matching file was processed ..
    entries = _read_evidence(schedule_name)

    assert len(entries) == 1
    assert entries[0]['file_name'] == 'data.csv'

    # .. and the other one stays untouched in the directory.
    assert sorted(os.listdir(directory)) == sorted([_scheduler.Default_Move_Directory, 'notes.txt'])

# ################################################################################################################################

def test_dispatch_marker_mode(client, sftp_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, sftp_test_server, conn_name)

    directory = _make_remote_directory(sftp_test_server)
    schedule_name = 'marker.' + uuid4().hex[:8]

    # One upload is complete - its marker is there - and the other one is still in progress
    _ = _write_remote_file(directory, 'complete.txt', 'Complete upload payload')
    _ = _write_remote_file(directory, 'complete.txt' + _scheduler.Default_Marker_Suffix, '')
    _ = _write_remote_file(directory, 'incomplete.txt', 'Upload still in progress')

    response = _create_schedule(client, conn_id, schedule_name, directory,
        ready_how=_scheduler.ReadyHow.Marker, marker_suffix=_scheduler.Default_Marker_Suffix)
    schedule = _get_schedule(client, conn_id, response['id'])

    _invoke_dispatch(client, conn_id, conn_name, schedule)

    # Only the upload with a marker was processed ..
    entries = _read_evidence(schedule_name)

    assert len(entries) == 1
    assert entries[0]['file_name'] == 'complete.txt'

    # .. its marker was deleted together with it ..
    remaining = sorted(os.listdir(directory))

    # .. while the incomplete upload stays in place for the next run.
    assert remaining == sorted([_scheduler.Default_Move_Directory, 'incomplete.txt'])
    assert os.listdir(os.path.join(directory, _scheduler.Default_Move_Directory)) == ['complete.txt']

# ################################################################################################################################

def test_dispatch_error_leaves_file_in_place(client, sftp_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, sftp_test_server, conn_name)

    directory = _make_remote_directory(sftp_test_server)
    schedule_name = 'error.' + uuid4().hex[:8]

    _ = _write_remote_file(directory, 'unlucky.txt', 'Payload that will not be processed')

    # The target service always raises and the file is claimed before it is read
    response = _create_schedule(client, conn_id, schedule_name, directory,
        service=TestConfig.service_always_raise, should_claim=True)
    schedule = _get_schedule(client, conn_id, response['id'])

    _invoke_dispatch(client, conn_id, conn_name, schedule)

    # Nothing was recorded ..
    assert _read_evidence(schedule_name) == []

    # .. and the file was renamed back after the failure, so the next run can take it again.
    assert os.listdir(directory) == ['unlucky.txt']

# ################################################################################################################################

def test_dispatch_via_real_scheduler_fire(client, sftp_test_server, scheduler_process):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, sftp_test_server, conn_name)

    directory = _make_remote_directory(sftp_test_server)
    schedule_name = 'fire.' + uuid4().hex[:8]

    full_path = _write_remote_file(directory, 'delivered.txt', 'Payload delivered by the scheduler')

    # The schedule starts now and runs every second so that the test does not wait long for a fire
    start_date = datetime.now(timezone.utc).isoformat()

    _ = _create_schedule(client, conn_id, schedule_name, directory,
        run_every=1, run_unit=_scheduler.Unit.Seconds, start_date=start_date)

    # Wait until a fire event picked the file up and the target service recorded it
    deadline = time.monotonic() + _fire_wait_seconds

    while time.monotonic() < deadline:
        if _read_evidence(schedule_name):
            break
        time.sleep(1)
    else:
        raise AssertionError(f'The scheduler did not deliver the file `{full_path}` in {_fire_wait_seconds} seconds')

    entries = _read_evidence(schedule_name)

    assert entries[0]['file_name'] == 'delivered.txt'
    assert entries[0]['data'] == 'Payload delivered by the scheduler'

    # The file was moved away so further fires must not process it again
    time.sleep(3)

    assert len(_read_evidence(schedule_name)) == 1
    assert os.listdir(os.path.join(directory, _scheduler.Default_Move_Directory)) == ['delivered.txt']

# ################################################################################################################################
# ################################################################################################################################
