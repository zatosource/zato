# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from json import loads

# Zato
from zato.common.api import FileTransfer, GENERIC, SCHEDULER
from zato.common.defaults import default_cluster_id
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.test.file_transfer_harness.adapter import FileTransferAdapter
    from zato.common.typing_ import any_, anydict, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# The admin services the harness talks to
Service_Conn = 'zato.generic.connection'
Service_Job = 'zato.scheduler.job'
Service_Schedule = 'zato.outgoing.file-transfer.schedule'

# A start date far enough in the future that a schedule created for a test that does not want
# fire events will never produce one, no matter how long the suite runs.
Start_Date_Never = '2099-01-01T00:00:00'

# A generic connection type that carries no file transfer schedules, used by the tests that check
# what happens when a schedule names a connection of the wrong kind.
Foreign_Conn_Type = GENERIC.CONNECTION.TYPE.OUTCONN_LDAP

# How long to keep retrying the dispatch service while a newly created connection propagates
# to the server's connection store, in seconds
Dispatch_Wait_Seconds = 30

# How long to sleep between two attempts at the dispatch service, in seconds
Dispatch_Sleep_Time = 1

# What a schedule created by a test looks like unless the test says otherwise. The stability delay
# is one second rather than the product default so that the suite does not spend its life waiting.
Schedule_Defaults = {
    'is_active': True,
    'ready_how': _scheduler.ReadyHow.Stability,
    'stability_delay': 1,
    'on_success': _scheduler.OnSuccess.Move,
    'move_directory': _scheduler.Default_Move_Directory,
    'run_every': 5,
    'run_unit': _scheduler.Unit.Minutes,
    'start_date': Start_Date_Never,
}

# ################################################################################################################################
# ################################################################################################################################

def unwrap(response:'any_') -> 'any_':
    """ Some services wrap their response in a single zato_* root element.
    """
    out = response

    if isinstance(out, dict):
        key_count = len(out)
        if key_count == 1:
            key = next(iter(out))
            if key.startswith('zato_'):
                out = out[key]

    return out

# ################################################################################################################################
# ################################################################################################################################

class ScheduleClient:
    """ Everything the shared tests do to a Zato server, in terms of connections, schedules and jobs
    rather than of service names and request payloads.
    """

    def __init__(self, client:'AdminClient', adapter:'FileTransferAdapter', target_service:'str') -> 'None':
        self.client = client
        self.adapter = adapter

        # The service that a schedule invokes unless a test asks for another one
        self.target_service = target_service

# ################################################################################################################################

    def create_conn(self, name:'str', **extra:'any_') -> 'int':
        """ Creates a connection of the adapter's protocol pointing at its test server, returning the connection's ID.
        Anything given on top of the adapter's own fields replaces them, which is how a test asks
        for a connection that is not quite the one the adapter would build.
        """
        request:'anydict' = {
            'cluster_id': default_cluster_id,
            'name': name,
            'type_': self.adapter.conn_type,
            'is_active': True,
            'is_internal': False,
            'is_channel': False,
            'is_outgoing': True,
            'is_outconn': True,
            'pool_size': 1,
        }

        protocol_fields = self.adapter.create_conn_payload(name)
        request.update(protocol_fields)
        request.update(extra)

        response = unwrap(self.client.invoke(f'{Service_Conn}.create', request))

        out = response['id']
        return out

# ################################################################################################################################

    def edit_conn(self, conn_id:'int', name:'str', **extra:'any_') -> 'None':
        """ Edits a connection, which is how tests rename one or change what it points at.
        """
        request:'anydict' = {
            'cluster_id': default_cluster_id,
            'id': conn_id,
            'name': name,
            'type_': self.adapter.conn_type,
            'is_active': True,
            'is_internal': False,
            'is_channel': False,
            'is_outgoing': True,
            'is_outconn': True,
            'pool_size': 1,
        }

        protocol_fields = self.adapter.edit_conn_payload(name)
        request.update(protocol_fields)
        request.update(extra)

        _ = self.client.invoke(f'{Service_Conn}.edit', request)

# ################################################################################################################################

    def create_foreign_conn(self, name:'str') -> 'int':
        """ Creates a generic connection that is not a file transfer one, returning its ID.
        """
        request:'anydict' = {
            'cluster_id': default_cluster_id,
            'name': name,
            'type_': Foreign_Conn_Type,
            'is_active': True,
            'is_internal': False,
            'is_channel': False,
            'is_outgoing': True,
            'is_outconn': True,
            'pool_size': 1,
            'server_list': 'ldap://127.0.0.1:389',
            'username': 'zato.test.user',
            'secret': 'zato.test.secret',
        }

        response = unwrap(self.client.invoke(f'{Service_Conn}.create', request))

        out = response['id']
        return out

# ################################################################################################################################

    def delete_conn(self, conn_id:'int') -> 'None':
        _ = self.client.delete(f'{Service_Conn}.delete', id=conn_id)

# ################################################################################################################################

    def get_conn_names(self) -> 'strlist':
        data, _meta = self.client.get_list(f'{Service_Conn}.get-list',
            cluster_id=default_cluster_id, type_=self.adapter.conn_type, paginate=True, cur_page=1)

        out:'strlist' = []

        for item in data:
            out.append(item['name'])

        return out

# ################################################################################################################################

    def job_name(self, conn_name:'str', schedule_name:'str') -> 'str':
        """ The name the auto-created job of one schedule carries.
        """
        prefix = _scheduler.Job_Prefix[self.adapter.conn_type]

        out = f'{prefix}{conn_name}.{schedule_name}'
        return out

# ################################################################################################################################

    def get_job_names(self) -> 'strlist':
        data, _meta = self.client.get_list(f'{Service_Job}.get-list', cluster_id=default_cluster_id)

        out:'strlist' = []

        for item in data:
            out.append(item['name'])

        return out

# ################################################################################################################################

    def get_job(self, name:'str') -> 'anydict':
        request = {'cluster_id': default_cluster_id, 'name': name}

        out = unwrap(self.client.invoke(f'{Service_Job}.get-by-name', request))
        return out

# ################################################################################################################################

    def edit_job(self, job_id:'int', name:'str', **extra:'any_') -> 'None':
        """ Edits a job the way the scheduler's own UI does, without going through the schedule.
        """
        request:'anydict' = {
            'cluster_id': default_cluster_id,
            'id': job_id,
            'name': name,
            'is_active': True,
            'job_type': SCHEDULER.JOB_TYPE.INTERVAL_BASED,
            'service': _scheduler.Dispatch_Service[self.adapter.conn_type],
            'start_date': Start_Date_Never,
        }
        request.update(extra)

        _ = self.client.invoke(f'{Service_Job}.edit', request)

# ################################################################################################################################

    def create_job(self, name:'str', **extra:'any_') -> 'anydict':
        """ Creates a scheduler job directly, which is how a test puts one in the way of a schedule.
        """
        request:'anydict' = {
            'cluster_id': default_cluster_id,
            'name': name,
            'is_active': True,
            'job_type': SCHEDULER.JOB_TYPE.INTERVAL_BASED,
            'service': _scheduler.Dispatch_Service[self.adapter.conn_type],
            'start_date': Start_Date_Never,
            'minutes': 5,
        }
        request.update(extra)

        out = unwrap(self.client.invoke(f'{Service_Job}.create', request))
        return out

# ################################################################################################################################

    def delete_job(self, job_id:'int') -> 'None':
        _ = self.client.delete(f'{Service_Job}.delete', id=job_id)

# ################################################################################################################################

    def schedule_request(self, conn_id:'int', name:'str', directory:'str', **extra:'any_') -> 'anydict':
        """ A create or edit payload for one schedule, with everything the test did not mention left at its default.
        """
        out:'anydict' = {
            'conn_id': conn_id,
            'name': name,
            'directory': directory,
            'service': self.target_service,
        }
        out.update(Schedule_Defaults)
        out.update(extra)

        return out

# ################################################################################################################################

    def create_schedule(self, conn_id:'int', name:'str', directory:'str', **extra:'any_') -> 'anydict':
        """ Creates one schedule and returns the response carrying its id and job_id.
        """
        request = self.schedule_request(conn_id, name, directory, **extra)

        out = unwrap(self.client.invoke(f'{Service_Schedule}.create', request))
        return out

# ################################################################################################################################

    def edit_schedule(self, conn_id:'int', schedule_id:'str', name:'str', directory:'str', **extra:'any_') -> 'anydict':
        request = self.schedule_request(conn_id, name, directory, **extra)
        request['id'] = schedule_id

        out = unwrap(self.client.invoke(f'{Service_Schedule}.edit', request))
        return out

# ################################################################################################################################

    def delete_schedule(self, conn_id:'int', schedule_id:'str') -> 'None':
        _ = self.client.invoke(f'{Service_Schedule}.delete', {'conn_id': conn_id, 'id': schedule_id})

# ################################################################################################################################

    def get_schedules(self, conn_id:'int') -> 'dictlist':
        response = self.client.invoke(f'{Service_Schedule}.get-list', {'conn_id': conn_id})

        # The service hands back its list as a JSON string rather than as a payload
        if isinstance(response, str):
            response = loads(response)

        out = cast_('dictlist', response)
        return out

# ################################################################################################################################

    def get_schedule(self, conn_id:'int', schedule_id:'str') -> 'anydict | None':
        """ Returns one schedule entry of a connection, or None when the connection does not carry it.
        """
        schedules = self.get_schedules(conn_id)

        for schedule in schedules:
            if schedule['id'] == schedule_id:
                out = schedule
                break
        else:
            out = None

        return out

# ################################################################################################################################

    def require_schedule(self, conn_id:'int', schedule_id:'str') -> 'anydict':
        """ Returns one schedule entry of a connection, failing the test when the connection does not carry it.
        """
        out = self.get_schedule(conn_id, schedule_id)

        if out is None:
            raise AssertionError(f'Connection `{conn_id}` does not carry a schedule with id `{schedule_id}`')

        return out

# ################################################################################################################################

    def create_and_get_schedule(self, conn_id:'int', name:'str', directory:'str', **extra:'any_') -> 'anydict':
        """ Creates one schedule and hands back the stored entry, which is what a fire event carries.
        """
        response = self.create_schedule(conn_id, name, directory, **extra)
        schedule_id = response['id']

        out = self.require_schedule(conn_id, schedule_id)
        return out

# ################################################################################################################################

    def invoke_dispatch(self, conn_id:'int', conn_name:'str', schedule:'anydict') -> 'None':
        """ Invokes the dispatch service the way a scheduler fire event does, retrying until a newly created
        connection has propagated to the server's connection store.
        """
        payload = {
            _scheduler.Extra_Conn_ID: conn_id,
            _scheduler.Extra_Conn_Name: conn_name,
            _scheduler.Extra_Conn_Type: self.adapter.conn_type,
            _scheduler.Extra_Schedule: schedule,
        }

        service = _scheduler.Dispatch_Service[self.adapter.conn_type]

        deadline = time.monotonic() + Dispatch_Wait_Seconds
        last_error = None

        while time.monotonic() < deadline:
            try:
                _ = self.client.invoke(service, payload)
            except Exception as e:
                last_error = e
                time.sleep(Dispatch_Sleep_Time)
                continue
            else:
                return

        raise AssertionError(f'Could not invoke the dispatch service, last error: {last_error}')

# ################################################################################################################################

    def invoke_dispatch_once(self, conn_id:'int', conn_name:'str', schedule:'anydict') -> 'None':
        """ Invokes the dispatch service exactly once and lets any error through, which is what a test
        wants when the run itself is expected to fail.
        """
        payload = {
            _scheduler.Extra_Conn_ID: conn_id,
            _scheduler.Extra_Conn_Name: conn_name,
            _scheduler.Extra_Conn_Type: self.adapter.conn_type,
            _scheduler.Extra_Schedule: schedule,
        }

        service = _scheduler.Dispatch_Service[self.adapter.conn_type]
        _ = self.client.invoke(service, payload)

# ################################################################################################################################

    def cleanup(self) -> 'None':
        """ Removes every connection and job this adapter's tests may have left behind,
        so each test starts from a clean slate.
        """
        conn_prefix = self.adapter.conn_name_prefix
        job_prefix = _scheduler.Job_Prefix[self.adapter.conn_type] + conn_prefix

        conn_types = [self.adapter.conn_type, Foreign_Conn_Type]

        # Deleting a connection also deletes the jobs of all its schedules ..
        for conn_type in conn_types:

            data, _meta = self.client.get_list(f'{Service_Conn}.get-list',
                cluster_id=default_cluster_id, type_=conn_type, paginate=True, cur_page=1)

            for item in data:
                if item['name'].startswith(conn_prefix):
                    _ = self.client.delete(f'{Service_Conn}.delete', id=item['id'])

        # .. and jobs whose connection is already gone are deleted directly.
        data, _meta = self.client.get_list(f'{Service_Job}.get-list', cluster_id=default_cluster_id)

        for item in data:
            if item['name'].startswith(job_prefix):
                _ = self.client.delete(f'{Service_Job}.delete', id=item['id'])

# ################################################################################################################################
# ################################################################################################################################
