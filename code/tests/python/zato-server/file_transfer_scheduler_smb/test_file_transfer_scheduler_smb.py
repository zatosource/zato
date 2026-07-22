# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
from datetime import datetime, timezone
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
_conn_type = FileTransfer.ConnType.SMB

_service_conn = 'zato.generic.connection'
_service_job = 'zato.scheduler.job'
_service_schedule = 'zato.outgoing.file-transfer.schedule'

_conn_name_prefix = 'test-file-transfer-smb-'
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

def _create_conn(client, smb_test_server, name):
    """ Creates an SMB connection pointing to the test SMB server and returns its ID.
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
        host=smb_test_server.host,
        port=smb_test_server.port,
        username=smb_test_server.username,
        secret=smb_test_server.password,
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

def _make_remote_directory(smb_test_server):
    """ Creates a new directory for one test's remote files, returning both the remote path
    that includes the share name and the local path backing it on disk.
    """
    name = uuid4().hex[:12]

    local_directory = os.path.join(smb_test_server.files_dir, name)
    os.mkdir(local_directory)

    remote_directory = f'{smb_test_server.share_name}/{name}'

    return remote_directory, local_directory

# ################################################################################################################################

def _write_local_file(directory, file_name, data):
    full_path = os.path.join(directory, file_name)

    with open(full_path, 'w') as local_file:
        _ = local_file.write(data)

    return full_path

# ################################################################################################################################
# ################################################################################################################################

def test_create_schedule_creates_job(client, smb_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, smb_test_server, conn_name)

    response = _create_schedule(client, conn_id, 'invoices.hourly', f'{smb_test_server.share_name}/invoices')

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

    # The connection's own list mirrors the job
    schedule = _get_schedule(client, conn_id, schedule_id)

    assert schedule['name'] == 'invoices.hourly'
    assert int(schedule['job_id']) == int(job_id)

# ################################################################################################################################

def test_conn_delete_removes_jobs(client, smb_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, smb_test_server, conn_name)

    _ = _create_schedule(client, conn_id, 'first.one', f'{smb_test_server.share_name}/first')
    _ = _create_schedule(client, conn_id, 'second.one', f'{smb_test_server.share_name}/second')

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

def test_dispatch_moves_file_on_success(client, smb_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, smb_test_server, conn_name)

    remote_directory, local_directory = _make_remote_directory(smb_test_server)
    schedule_name = 'move.' + uuid4().hex[:8]

    _ = _write_local_file(local_directory, 'first.txt', 'First file payload')
    _ = _write_local_file(local_directory, 'second.txt', 'Second file payload')

    response = _create_schedule(client, conn_id, schedule_name, remote_directory)
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
    assert entry['directory'] == remote_directory
    assert entry['full_path'] == f'{remote_directory}/first.txt'
    assert entry['size'] == len('First file payload')
    assert entry['data'] == 'First file payload'

    entry = entry_by_name['second.txt']
    assert entry['data'] == 'Second file payload'

    # .. and both files were moved into the destination directory.
    move_directory = os.path.join(local_directory, _scheduler.Default_Move_Directory)

    assert sorted(os.listdir(move_directory)) == ['first.txt', 'second.txt']
    assert sorted(os.listdir(local_directory)) == [_scheduler.Default_Move_Directory]

# ################################################################################################################################

def test_dispatch_deletes_file_on_success(client, smb_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, smb_test_server, conn_name)

    remote_directory, local_directory = _make_remote_directory(smb_test_server)
    schedule_name = 'delete.' + uuid4().hex[:8]

    _ = _write_local_file(local_directory, 'ephemeral.txt', 'Payload to delete after processing')

    response = _create_schedule(client, conn_id, schedule_name, remote_directory,
        on_success=_scheduler.OnSuccess.Delete, move_directory='')
    schedule = _get_schedule(client, conn_id, response['id'])

    _invoke_dispatch(client, conn_id, conn_name, schedule)

    # The file was recorded and then deleted rather than moved
    entries = _read_evidence(schedule_name)

    assert len(entries) == 1
    assert entries[0]['data'] == 'Payload to delete after processing'

    assert os.listdir(local_directory) == []

# ################################################################################################################################

def test_dispatch_marker_mode(client, smb_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, smb_test_server, conn_name)

    remote_directory, local_directory = _make_remote_directory(smb_test_server)
    schedule_name = 'marker.' + uuid4().hex[:8]

    # One upload is complete - its marker is there - and the other one is still in progress
    _ = _write_local_file(local_directory, 'complete.txt', 'Complete upload payload')
    _ = _write_local_file(local_directory, 'complete.txt' + _scheduler.Default_Marker_Suffix, '')
    _ = _write_local_file(local_directory, 'incomplete.txt', 'Upload still in progress')

    response = _create_schedule(client, conn_id, schedule_name, remote_directory,
        ready_how=_scheduler.ReadyHow.Marker, marker_suffix=_scheduler.Default_Marker_Suffix)
    schedule = _get_schedule(client, conn_id, response['id'])

    _invoke_dispatch(client, conn_id, conn_name, schedule)

    # Only the upload with a marker was processed ..
    entries = _read_evidence(schedule_name)

    assert len(entries) == 1
    assert entries[0]['file_name'] == 'complete.txt'

    # .. its marker was deleted together with it ..
    remaining = sorted(os.listdir(local_directory))

    # .. while the incomplete upload stays in place for the next run.
    assert remaining == sorted([_scheduler.Default_Move_Directory, 'incomplete.txt'])
    assert os.listdir(os.path.join(local_directory, _scheduler.Default_Move_Directory)) == ['complete.txt']

# ################################################################################################################################

def test_dispatch_error_leaves_file_in_place(client, smb_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, smb_test_server, conn_name)

    remote_directory, local_directory = _make_remote_directory(smb_test_server)
    schedule_name = 'error.' + uuid4().hex[:8]

    _ = _write_local_file(local_directory, 'unlucky.txt', 'Payload that will not be processed')

    # The target service always raises and the file is claimed before it is read
    response = _create_schedule(client, conn_id, schedule_name, remote_directory,
        service=TestConfig.service_always_raise, should_claim=True)
    schedule = _get_schedule(client, conn_id, response['id'])

    _invoke_dispatch(client, conn_id, conn_name, schedule)

    # Nothing was recorded ..
    assert _read_evidence(schedule_name) == []

    # .. and the file was renamed back after the failure, so the next run can take it again.
    assert os.listdir(local_directory) == ['unlucky.txt']

# ################################################################################################################################

def test_dispatch_via_real_scheduler_fire(client, smb_test_server, scheduler_process):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, smb_test_server, conn_name)

    remote_directory, local_directory = _make_remote_directory(smb_test_server)
    schedule_name = 'fire.' + uuid4().hex[:8]

    full_path = _write_local_file(local_directory, 'delivered.txt', 'Payload delivered by the scheduler')

    # The schedule starts now and runs every second so that the test does not wait long for a fire
    start_date = datetime.now(timezone.utc).isoformat()

    _ = _create_schedule(client, conn_id, schedule_name, remote_directory,
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
    assert os.listdir(os.path.join(local_directory, _scheduler.Default_Move_Directory)) == ['delivered.txt']

# ################################################################################################################################
# ################################################################################################################################
