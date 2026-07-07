# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
from datetime import datetime, timezone
from json import dumps, loads
from uuid import uuid4

# PyPI
import pytest

# Zato
from zato.common.api import EMAIL, SCHEDULER
from zato.common.defaults import default_cluster_id
from zato.common.test.client import AdminClient

# Local test helpers
from _config import TestConfig

# ################################################################################################################################
# ################################################################################################################################

_scheduler = EMAIL.IMAP.Scheduler
_unit = _scheduler.Unit

_service_imap = 'zato.email.imap'
_service_job = 'zato.scheduler.job'

_conn_name_prefix = 'test-imap-'
_job_name_prefix = _scheduler.Job_Prefix + _conn_name_prefix
_custom_job_name_prefix = 'custom-imap-job-'

_invoked_service = 'demo.ping'
_start_date = '2099-01-01T00:00:00'

_sender = 'sender@example.com'
_recipient = 'recipient@example.com'

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
def cleanup(client, imap_test_server):
    """ Deletes everything a test may have left behind so that each test starts from a clean slate.
    """
    yield

    # Deleting a connection also deletes its linked job
    data, _meta = client.get_list(f'{_service_imap}.get-list', cluster_id=default_cluster_id, paginate=True, cur_page=1)

    for item in data:
        if item['name'].startswith(_conn_name_prefix):
            _ = client.delete(f'{_service_imap}.delete', id=item['id'])

    # Jobs renamed away from the convention are not covered by the connection delete above
    data, _meta = client.get_list(f'{_service_job}.get-list', cluster_id=default_cluster_id)

    for item in data:
        if item['name'].startswith(_job_name_prefix) or item['name'].startswith(_custom_job_name_prefix):
            _ = client.delete(f'{_service_job}.delete', id=item['id'])

    # The mailbox and the log of received commands start empty for each test
    imap_test_server.clear()

# ################################################################################################################################
# ################################################################################################################################

def _unwrap(response):
    """ Some services wrap their response in a single zato_* root element.
    """
    if len(response) == 1:
        key = next(iter(response))
        if key.startswith('zato_'):
            response = response[key]
    return response

# ################################################################################################################################

def _new_conn_name():
    return _conn_name_prefix + uuid4().hex[:12]

# ################################################################################################################################

def _get_imap_item(client, name):
    """ Returns the get-list row of the IMAP connection of the given name.
    """
    data, _meta = client.get_list(f'{_service_imap}.get-list', cluster_id=default_cluster_id, paginate=True, cur_page=1)

    for item in data:
        if item['name'] == name:
            out = item
            break
    else:
        out = None

    return out

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

def _conn_payload(imap_test_server, name):
    """ A base create/edit payload for an IMAP connection pointing to the test IMAP server.
    """
    out = {
        'cluster_id': default_cluster_id,
        'name': name,
        'is_active': True,
        'server_type': EMAIL.IMAP.ServerType.Generic,
        'host': imap_test_server.host,
        'port': imap_test_server.port,
        'timeout': 5,
        'debug_level': 0,
        'username': 'test-user@example.com',
        'mode': EMAIL.IMAP.MODE.PLAIN,
        'get_criteria': 'UNSEEN',

        # These two are declared as AsIs elements which the meta layer treats as required on input
        'tenant_id': '',
        'client_id': '',
    }

    return out

# ################################################################################################################################

def _scheduler_fields(run_every, run_unit, service=_invoked_service, start_date=_start_date):
    out = {
        'scheduler_run_every': run_every,
        'scheduler_run_unit': run_unit,
        'scheduler_start_date': start_date,
        'scheduler_service': service,
    }

    return out

# ################################################################################################################################

def _create_conn(client, imap_test_server, name, **extra):
    """ Creates an IMAP connection and returns its ID.
    """
    payload = _conn_payload(imap_test_server, name)
    payload.update(extra)

    response = _unwrap(client.create(f'{_service_imap}.create', **payload))
    out = response['id']

    return out

# ################################################################################################################################

def _edit_conn(client, imap_test_server, name, conn_id, **extra):
    payload = _conn_payload(imap_test_server, name)
    payload['id'] = conn_id
    payload.update(extra)

    _ = client.edit(f'{_service_imap}.edit', **payload)

# ################################################################################################################################

def _job_extra(conn_id, conn_name, service):
    """ The extra data that an IMAP-linked job carries for the dispatch service.
    """
    out = {
        _scheduler.Extra_Conn_ID: conn_id,
        _scheduler.Extra_Conn_Name: conn_name,
        _scheduler.Extra_Service: service,
    }

    return out

# ################################################################################################################################

def _read_evidence(subject):
    """ Returns the entries of the evidence file whose subject matches the given one.
    """
    out = []

    # The file comes into existence only once the first message was recorded
    if not os.path.exists(TestConfig.evidence_file):
        return out

    with open(TestConfig.evidence_file) as evidence:
        for line in evidence:
            line = line.strip()
            if line:
                entry = loads(line)
                if entry['subject'] == subject:
                    out.append(entry)

    return out

# ################################################################################################################################

def _invoke_dispatch(client, conn_id, conn_name, service):
    """ Invokes the dispatch service directly, the way a scheduler fire event does it, retrying until the newly
    created connection has propagated to the server's connection store.
    """
    payload = _job_extra(conn_id, conn_name, service)

    deadline = time.monotonic() + _ping_wait_seconds
    last_error = None

    while time.monotonic() < deadline:
        try:
            _ = client.invoke(_scheduler.Dispatch_Service, payload)
        except Exception as e:
            last_error = e
            time.sleep(1)
            continue
        else:
            return

    raise AssertionError(f'Could not invoke the dispatch service, last error: {last_error}')

# ################################################################################################################################

def _prepare_dispatch_conn(client, imap_test_server, service):
    """ Creates a connection whose linked job points to the given per-message service, sets its password
    and returns the connection's name and ID.
    """
    conn_name = _new_conn_name()
    conn_id = _create_conn(client, imap_test_server, conn_name, **_scheduler_fields(2, _unit.Minutes, service=service))

    # The connection needs a password before it can log in anywhere
    _ = client.invoke(f'{_service_imap}.change-password', {'id': conn_id, 'password': 'test-password'})

    return conn_name, conn_id

# ################################################################################################################################
# ################################################################################################################################

def test_create_conn_with_scheduler_fields_creates_job(client, imap_test_server):

    conn_name = _new_conn_name()
    job_name = _scheduler.Job_Prefix + conn_name

    conn_id = _create_conn(client, imap_test_server, conn_name, **_scheduler_fields(2, _unit.Minutes))

    # The job exists, is interval-based and points back to its connection
    job = _get_job(client, job_name)

    assert job['job_type'] == SCHEDULER.JOB_TYPE.INTERVAL_BASED
    assert job['service_name'] == _scheduler.Dispatch_Service
    assert int(job['minutes']) == 2
    assert int(job['imap_conn_id']) == int(conn_id)

    # The job's extra data carries the connection's identity and the per-message service
    extra = loads(job['extra'])

    assert int(extra[_scheduler.Extra_Conn_ID]) == int(conn_id)
    assert extra[_scheduler.Extra_Conn_Name] == conn_name
    assert extra[_scheduler.Extra_Service] == _invoked_service

    # The connection's own row points to the job and mirrors its definition
    item = _get_imap_item(client, conn_name)

    assert str(item['scheduler_run_every']) == '2'
    assert item['scheduler_run_unit'] == _unit.Minutes
    assert item['scheduler_start_date'] == _start_date
    assert item['scheduler_service'] == _invoked_service
    assert int(item['scheduler_job_id']) == int(job['id'])

# ################################################################################################################################

def test_ping_reaches_imap_test_server(client, imap_test_server):

    conn_name = _new_conn_name()
    conn_id = _create_conn(client, imap_test_server, conn_name)

    # The connection needs a password before it can log in anywhere
    _ = client.invoke(f'{_service_imap}.change-password', {'id': conn_id, 'password': 'test-password'})

    # The connection definition needs a moment to propagate to the connection store,
    # hence the ping is retried until the test IMAP server confirms it saw a session.
    deadline = time.monotonic() + _ping_wait_seconds
    last_error = None

    while time.monotonic() < deadline:
        try:
            _ = client.invoke(f'{_service_imap}.ping', {'id': conn_id})
        except Exception as e:
            last_error = e
            time.sleep(1)
            continue

        if imap_test_server.has_received('NOOP'):
            break

        time.sleep(1)
    else:
        raise AssertionError(f'IMAP test server did not receive a ping, last error: {last_error}')

    assert imap_test_server.has_received('LOGIN')
    assert imap_test_server.has_received('NOOP')

# ################################################################################################################################

def test_imap_edit_updates_job(client, imap_test_server):

    conn_name = _new_conn_name()
    job_name = _scheduler.Job_Prefix + conn_name

    conn_id = _create_conn(client, imap_test_server, conn_name, **_scheduler_fields(2, _unit.Minutes))
    job_id = _get_job(client, job_name)['id']

    # Change the interval through the connection's edit
    _edit_conn(client, imap_test_server, conn_name, conn_id, **_scheduler_fields(3, _unit.Hours))

    # It is still the same job, just with a new interval
    job = _get_job(client, job_name)

    assert int(job['id']) == int(job_id)
    assert int(job['hours']) == 3
    assert int(job['minutes']) == 0

# ################################################################################################################################

def test_job_edit_syncs_back_to_conn(client, imap_test_server):

    conn_name = _new_conn_name()
    job_name = _scheduler.Job_Prefix + conn_name
    custom_job_name = _custom_job_name_prefix + uuid4().hex[:12]

    conn_id = _create_conn(client, imap_test_server, conn_name, **_scheduler_fields(2, _unit.Minutes))
    job_id = _get_job(client, job_name)['id']

    # Edit the job directly, the way the scheduler UI does it - renaming it, changing its interval
    # and pointing its extra data to another per-message service.
    _ = client.edit(f'{_service_job}.edit',
        cluster_id=default_cluster_id,
        id=job_id,
        name=custom_job_name,
        is_active=True,
        job_type=SCHEDULER.JOB_TYPE.INTERVAL_BASED,
        service=_scheduler.Dispatch_Service,
        start_date=_start_date,
        minutes=7,
        extra=dumps(_job_extra(conn_id, conn_name, TestConfig.service_store_message)),
    )

    # The connection now shows the job's new definition, including the service read out of the extra data
    item = _get_imap_item(client, conn_name)

    assert str(item['scheduler_run_every']) == '7'
    assert item['scheduler_run_unit'] == _unit.Minutes
    assert item['scheduler_service'] == TestConfig.service_store_message
    assert int(item['scheduler_job_id']) == int(job_id)

    # A subsequent IMAP edit updates the same job without clobbering its custom name
    _edit_conn(client, imap_test_server, conn_name, conn_id, **_scheduler_fields(4, _unit.Minutes))

    job = _get_job(client, custom_job_name)

    assert int(job['id']) == int(job_id)
    assert int(job['minutes']) == 4

# ################################################################################################################################

def test_job_delete_clears_conn(client, imap_test_server):

    conn_name = _new_conn_name()
    job_name = _scheduler.Job_Prefix + conn_name

    _ = _create_conn(client, imap_test_server, conn_name, **_scheduler_fields(2, _unit.Minutes))
    job_id = _get_job(client, job_name)['id']

    # Delete the job directly, the way the scheduler UI does it
    _ = client.delete(f'{_service_job}.delete', id=job_id)

    # The connection must not point to the deleted job any longer
    item = _get_imap_item(client, conn_name)

    assert not item['scheduler_job_id']
    assert not item['scheduler_run_every']
    assert not item['scheduler_service']

# ################################################################################################################################

def test_imap_edit_recreates_job_after_direct_job_delete(client, imap_test_server):

    conn_name = _new_conn_name()
    job_name = _scheduler.Job_Prefix + conn_name

    conn_id = _create_conn(client, imap_test_server, conn_name, **_scheduler_fields(2, _unit.Minutes))
    job_id = _get_job(client, job_name)['id']

    _ = client.delete(f'{_service_job}.delete', id=job_id)

    # An IMAP edit that fills the scheduler fields in again creates a fresh job under the conventional name
    _edit_conn(client, imap_test_server, conn_name, conn_id, **_scheduler_fields(5, _unit.Minutes))

    job = _get_job(client, job_name)

    assert int(job['minutes']) == 5
    assert int(job['imap_conn_id']) == int(conn_id)

# ################################################################################################################################

def test_imap_edit_clearing_fields_deletes_job(client, imap_test_server):

    conn_name = _new_conn_name()
    job_name = _scheduler.Job_Prefix + conn_name

    conn_id = _create_conn(client, imap_test_server, conn_name, **_scheduler_fields(2, _unit.Minutes))

    _edit_conn(client, imap_test_server, conn_name, conn_id,
        scheduler_run_every='',
        scheduler_run_unit='',
        scheduler_start_date='',
        scheduler_service='',
    )

    # The job is gone ..
    assert job_name not in _get_job_names(client)

    # .. and the connection no longer points to it.
    item = _get_imap_item(client, conn_name)
    assert not item['scheduler_job_id']

# ################################################################################################################################

def test_partial_scheduler_fields_are_rejected(client, imap_test_server):

    conn_name = _new_conn_name()
    job_name = _scheduler.Job_Prefix + conn_name

    payload = _conn_payload(imap_test_server, conn_name)
    payload.update({
        'scheduler_run_every': 5,
        'scheduler_run_unit': _unit.Minutes,
    })

    with pytest.raises(Exception, match='run-every, start date and service'):
        _ = client.create(f'{_service_imap}.create', **payload)

    # Neither the connection nor a job were created
    assert _get_imap_item(client, conn_name) is None
    assert job_name not in _get_job_names(client)

# ################################################################################################################################

def test_conn_delete_removes_job(client, imap_test_server):

    conn_name = _new_conn_name()
    job_name = _scheduler.Job_Prefix + conn_name

    conn_id = _create_conn(client, imap_test_server, conn_name, **_scheduler_fields(10, _unit.Seconds))

    assert job_name in _get_job_names(client)

    # Deleting the connection removes its job as well
    _ = client.delete(f'{_service_imap}.delete', id=conn_id)

    assert job_name not in _get_job_names(client)
    assert _get_imap_item(client, conn_name) is None

# ################################################################################################################################

def test_conn_without_scheduler_fields_creates_no_job(client, imap_test_server):

    conn_name = _new_conn_name()
    job_name = _scheduler.Job_Prefix + conn_name

    conn_id = _create_conn(client, imap_test_server, conn_name)

    # No job was auto-created for this connection ..
    assert job_name not in _get_job_names(client)

    # .. and its row carries no scheduler fields.
    item = _get_imap_item(client, conn_name)
    assert not item['scheduler_job_id']
    assert not item['scheduler_service']

    # Deleting a connection that never had a job works cleanly
    _ = client.delete(f'{_service_imap}.delete', id=conn_id)

    assert _get_imap_item(client, conn_name) is None

# ################################################################################################################################

def test_dispatch_invokes_service_per_message(client, imap_test_server):

    subject_first = 'Test message one ' + uuid4().hex[:8]
    subject_second = 'Test message two ' + uuid4().hex[:8]

    uid_first = imap_test_server.add_message(_sender, _recipient, subject_first, 'First message body')
    uid_second = imap_test_server.add_message(_sender, _recipient, subject_second, 'Second message body')

    conn_name, conn_id = _prepare_dispatch_conn(client, imap_test_server, TestConfig.service_store_message)

    # Invoke the dispatch service directly, the way a scheduler fire event does it
    _invoke_dispatch(client, conn_id, conn_name, TestConfig.service_store_message)

    # The per-message service saw each of the two messages exactly once ..
    entries_first = _read_evidence(subject_first)
    entries_second = _read_evidence(subject_second)

    assert len(entries_first) == 1
    assert len(entries_second) == 1

    # .. with the full details of each of them ..
    entry = entries_first[0]

    assert entry['uid'] == uid_first
    assert entry['sent_from'] == _sender
    assert entry['body'].strip() == 'First message body'

    entry = entries_second[0]

    assert entry['uid'] == uid_second
    assert entry['sent_from'] == _sender
    assert entry['body'].strip() == 'Second message body'

    # .. and both messages were marked as seen because the service did it itself.
    assert imap_test_server.is_seen(uid_first)
    assert imap_test_server.is_seen(uid_second)

# ################################################################################################################################

def test_dispatch_skips_seen_messages(client, imap_test_server):

    subject = 'Test message already seen ' + uuid4().hex[:8]
    uid = imap_test_server.add_message(_sender, _recipient, subject, 'Message body to process once')

    conn_name, conn_id = _prepare_dispatch_conn(client, imap_test_server, TestConfig.service_store_message)

    # The first dispatch processes the message and marks it as seen
    _invoke_dispatch(client, conn_id, conn_name, TestConfig.service_store_message)

    assert len(_read_evidence(subject)) == 1
    assert imap_test_server.is_seen(uid)

    # The second dispatch finds nothing to do because the UNSEEN criteria no longer matches the message
    _ = client.invoke(_scheduler.Dispatch_Service, _job_extra(conn_id, conn_name, TestConfig.service_store_message))

    assert len(_read_evidence(subject)) == 1

# ################################################################################################################################

def test_dispatch_error_leaves_message_unseen(client, imap_test_server):

    subject = 'Test message that fails ' + uuid4().hex[:8]
    uid = imap_test_server.add_message(_sender, _recipient, subject, 'Message body that will not be processed')

    conn_name, conn_id = _prepare_dispatch_conn(client, imap_test_server, TestConfig.service_always_raise)

    # The dispatch itself succeeds even though the per-message service raises
    _invoke_dispatch(client, conn_id, conn_name, TestConfig.service_always_raise)

    # The message was fetched from the mailbox ..
    assert imap_test_server.has_received('FETCH')

    # .. yet it stays unseen because no service marked it, so it will be retried ..
    assert not imap_test_server.is_seen(uid)

    # .. and nothing was recorded about it either.
    assert len(_read_evidence(subject)) == 0

# ################################################################################################################################

def test_dispatch_via_real_scheduler_fire(client, imap_test_server, scheduler_process):

    conn_name = _new_conn_name()
    subject = 'Test message via scheduler ' + uuid4().hex[:8]

    uid = imap_test_server.add_message(_sender, _recipient, subject, 'Message body delivered by the scheduler')

    # The job starts now and runs every second so that the test does not wait long for a fire
    start_date = datetime.now(timezone.utc).isoformat()
    fields = _scheduler_fields(1, _unit.Seconds, service=TestConfig.service_store_message, start_date=start_date)

    conn_id = _create_conn(client, imap_test_server, conn_name, **fields)
    _ = client.invoke(f'{_service_imap}.change-password', {'id': conn_id, 'password': 'test-password'})

    # Wait until a fire event polled the mailbox and the per-message service recorded the message
    deadline = time.monotonic() + _fire_wait_seconds

    while time.monotonic() < deadline:
        if _read_evidence(subject):
            break
        time.sleep(1)
    else:
        raise AssertionError(f'The scheduler did not deliver the message `{subject}` in {_fire_wait_seconds} seconds')

    assert imap_test_server.is_seen(uid)

    # Further fires must not process the same message again
    time.sleep(3)

    assert len(_read_evidence(subject)) == 1

# ################################################################################################################################
# ################################################################################################################################
