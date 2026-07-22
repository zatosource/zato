# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# Zato
from zato.common.api import FileTransfer, SCHEDULER, SchedulerLink
from zato.common.defaults import default_cluster_id
from zato.common.exception import BadRequest
from zato.common.json_internal import dumps
from zato.common.odb.model import GenericConn, Job
from zato.common.util.file_transfer_scheduler import build_job_extra, get_job_name, get_schedule_id, get_schedule_list, \
    set_schedule_list
from zato.common.util.imap_scheduler import interval_from_unit
from zato.common.util.sql import parse_instance_opaque_attr
from zato.server.service import Boolean, Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictlist, intnone, stranydict
    from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# The schedule fields that create and edit accept on input, next to the connection's own ID.
_schedule_input = ('name', Boolean('is_active'), 'directory', '-pattern', 'ready_how', Int('-stability_delay'),
    '-marker_suffix', Boolean('-should_claim'), 'service', 'on_success', '-move_directory', Int('run_every'),
    'run_unit', 'start_date')

# ################################################################################################################################
# ################################################################################################################################

def get_connection(service:'Service', conn_id:'int') -> 'any_':
    """ Returns the GenericConn row of a file transfer connection, raising an error if it does not exist
    or is not of a file transfer type.
    """
    with closing(service.odb.session()) as session:
        row = session.query(GenericConn).filter_by(id=conn_id).first()
        if row:
            session.expunge(row)

    if not row:
        raise BadRequest(service.cid, f'Connection `{conn_id}` does not exist')

    if row.type_ not in FileTransfer.ConnTypeList:
        raise BadRequest(service.cid, f'Connection `{row.name}` is not an SFTP or SMB connection')

    return row

# ################################################################################################################################

def _validate_schedule(service:'Service', input:'any_') -> 'None':
    """ Makes sure the schedule fields given on input describe a schedule that can run.
    """
    if input.run_every < 1:
        raise BadRequest(service.cid, f'Run-every must be a positive integer instead of `{input.run_every}`')

    if input.run_unit not in _scheduler.UnitList:
        raise BadRequest(service.cid, f'Run unit `{input.run_unit}` is not one of `{_scheduler.UnitList}`')

    if input.ready_how not in _scheduler.ReadyHowList:
        raise BadRequest(service.cid, f'Ready-how `{input.ready_how}` is not one of `{_scheduler.ReadyHowList}`')

    if input.on_success not in _scheduler.OnSuccessList:
        raise BadRequest(service.cid, f'On-success `{input.on_success}` is not one of `{_scheduler.OnSuccessList}`')

    if input.service not in service.server.service_store.name_to_impl_name:
        raise BadRequest(service.cid, f'Service `{input.service}` does not exist')

    # Marker mode makes no sense without knowing what the markers look like
    if input.ready_how == _scheduler.ReadyHow.Marker:
        if not input.marker_suffix:
            raise BadRequest(service.cid, 'Marker suffix is required when files are ready on marker files')

    # A move without a destination cannot be carried out
    if input.on_success == _scheduler.OnSuccess.Move:
        if not input.move_directory:
            raise BadRequest(service.cid, 'Move directory is required when files are moved on success')

# ################################################################################################################################

def _build_schedule_dict(input:'any_', schedule_id:'str', job_id:'int') -> 'stranydict':
    """ Turns the validated input fields into one schedule entry of the connection's list.
    """
    stability_delay = input.stability_delay or _scheduler.Default_Stability_Delay
    pattern = input.pattern or _scheduler.Default_Pattern

    out = {
        'id': schedule_id,
        'name': input.name,
        'is_active': input.is_active,
        'directory': input.directory,
        'pattern': pattern,
        'ready_how': input.ready_how,
        'stability_delay': stability_delay,
        'marker_suffix': input.marker_suffix,
        'should_claim': input.should_claim,
        'service': input.service,
        'on_success': input.on_success,
        'move_directory': input.move_directory,
        'run_every': input.run_every,
        'run_unit': input.run_unit,
        'start_date': input.start_date,
        'job_id': job_id,
    }

    return out

# ################################################################################################################################

def _get_job(service:'Service', job_id:'intnone') -> 'any_':
    """ Returns the Job row of the given ID or None if it does not exist, e.g. it was deleted
    directly in the scheduler's own UI.
    """
    if not job_id:
        return None

    with closing(service.odb.session()) as session:
        out = session.query(Job).filter_by(id=job_id).first()
        if out:
            session.expunge(out)

    return out

# ################################################################################################################################

def sync_schedule_job(service:'Service', conn:'any_', schedule:'stranydict') -> 'int':
    """ Creates or updates the scheduler job linked to one schedule, returning the job's ID.
    The job invokes the per-type dispatch service and its extra data carries the full schedule
    so a fire event is self-contained.
    """
    extra = build_job_extra(conn.id, conn.name, conn.type_, schedule)
    job_name = get_job_name(conn.type_, conn.name, schedule['name'])

    request = {
        'cluster_id': default_cluster_id,
        'is_active': schedule['is_active'],
        'job_type': SCHEDULER.JOB_TYPE.INTERVAL_BASED,
        'service': _scheduler.Dispatch_Service[conn.type_],
        'start_date': schedule['start_date'],
        'extra': extra,
        'name': job_name,

        # The link lets the scheduler write edits made in its own UI back to the right schedule entry
        SchedulerLink.Conn_Type: conn.type_,
        SchedulerLink.Conn_ID: conn.id,
        SchedulerLink.Kind: schedule['id'],
    }

    interval = interval_from_unit(schedule['run_every'], schedule['run_unit'])
    request.update(interval)

    # The schedule may already point to a job and that job may or may not still exist
    job = _get_job(service, schedule['job_id'])

    # The job exists so it is updated in place ..
    if job:
        request['id'] = job.id
        _ = service.invoke('zato.scheduler.job.edit', request)
        out = job.id

    # .. otherwise, a new one is created for this schedule.
    else:
        response = service.invoke('zato.scheduler.job.create', request)
        if 'id' not in response:
            response = response['zato_scheduler_job_create_response']
        out = response['id']

    return out

def resync_connection_jobs(service:'Service', conn:'any_') -> 'None':
    """ Rebuilds the linked job of each schedule of a connection, e.g. after the connection was renamed -
    the jobs' names and extra data follow the connection's name.
    """
    with closing(service.odb.session()) as session:
        schedules = get_schedule_list(session, conn.id)

    # Nothing to rebuild if the connection has no schedules
    if not schedules:
        return

    # Bring each linked job up to date ..
    for schedule in schedules:
        job_id = sync_schedule_job(service, conn, schedule)
        schedule['job_id'] = job_id

    # .. and store the list back in case any job had to be re-created.
    with closing(service.odb.session()) as session:
        set_schedule_list(session, conn.id, schedules)

# ################################################################################################################################

def delete_connection_jobs(service:'Service', instance:'any_') -> 'None':
    """ Deletes the scheduler jobs linked to a connection's schedules - invoked when the connection itself
    is being deleted, so the jobs do not outlive it.
    """
    opaque = parse_instance_opaque_attr(instance)
    schedules = opaque.get(_scheduler.Schedules_Field) or []

    for schedule in schedules:
        job = _get_job(service, schedule['job_id'])
        if job:
            _ = service.invoke('zato.scheduler.job.delete', {'id': job.id})

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns the list of file transfer schedules of one SFTP or SMB connection.
    """
    input = Int('conn_id')

    def handle(self) -> 'None':

        # Make sure the connection exists and is of the right type ..
        conn = get_connection(self, self.request.input.conn_id)

        # .. and return the schedules stored with it.
        with closing(self.odb.session()) as session:
            schedules = get_schedule_list(session, conn.id)

        self.response.payload = dumps(schedules)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new file transfer schedule of one SFTP or SMB connection,
    along with the scheduler job that runs it.
    """
    input = (Int('conn_id'),) + _schedule_input
    output = 'id', 'name', Int('job_id')

    def handle(self) -> 'None':

        input = self.request.input

        # Make sure the connection exists and the schedule fields make sense ..
        conn = get_connection(self, input.conn_id)
        _validate_schedule(self, input)

        # .. the schedule's id is a slug derived from its name ..
        schedule_id = get_schedule_id(input.name)

        # .. names must be unique within the connection ..
        with closing(self.odb.session()) as session:
            schedules = get_schedule_list(session, conn.id)

        for schedule in schedules:
            if schedule['id'] == schedule_id:
                raise BadRequest(self.cid, f'Schedule `{input.name}` already exists')

        # .. build the new entry and its linked job ..
        schedule = _build_schedule_dict(input, schedule_id, 0)
        job_id = sync_schedule_job(self, conn, schedule)
        schedule['job_id'] = job_id

        # .. and store the updated list with the connection.
        schedules.append(schedule)

        with closing(self.odb.session()) as session:
            set_schedule_list(session, conn.id, schedules)

        self.response.payload.id = schedule_id
        self.response.payload.name = input.name
        self.response.payload.job_id = job_id

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an existing file transfer schedule of one SFTP or SMB connection,
    keeping its scheduler job in sync.
    """
    input = (Int('conn_id'), 'id') + _schedule_input
    output = 'id', 'name', Int('job_id')

    def handle(self) -> 'None':

        input = self.request.input

        # Make sure the connection exists and the schedule fields make sense ..
        conn = get_connection(self, input.conn_id)
        _validate_schedule(self, input)

        # .. the entry being edited must exist ..
        with closing(self.odb.session()) as session:
            schedules = get_schedule_list(session, conn.id)

        for schedule in schedules:
            if schedule['id'] == input.id:
                existing = schedule
                break
        else:
            raise BadRequest(self.cid, f'Schedule `{input.id}` does not exist')

        # .. a rename must not collide with any other entry ..
        for schedule in schedules:
            if schedule['name'] == input.name:
                if schedule['id'] != input.id:
                    raise BadRequest(self.cid, f'Schedule `{input.name}` already exists')

        # .. rebuild the entry, keeping its id and job link ..
        updated = _build_schedule_dict(input, input.id, existing['job_id'])

        # .. bring the linked job up to date ..
        job_id = sync_schedule_job(self, conn, updated)
        updated['job_id'] = job_id

        # .. and store the updated list with the connection.
        out:'dictlist' = []

        for schedule in schedules:
            if schedule['id'] == input.id:
                out.append(updated)
            else:
                out.append(schedule)

        with closing(self.odb.session()) as session:
            set_schedule_list(session, conn.id, out)

        self.response.payload.id = input.id
        self.response.payload.name = input.name
        self.response.payload.job_id = job_id

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a file transfer schedule of one SFTP or SMB connection, along with its scheduler job.
    """
    input = Int('conn_id'), 'id'

    def handle(self) -> 'None':

        input = self.request.input

        # Make sure the connection exists ..
        conn = get_connection(self, input.conn_id)

        # .. find the entry to delete ..
        with closing(self.odb.session()) as session:
            schedules = get_schedule_list(session, conn.id)

        for schedule in schedules:
            if schedule['id'] == input.id:
                existing = schedule
                break
        else:
            raise BadRequest(self.cid, f'Schedule `{input.id}` does not exist')

        # .. delete the linked job if it still exists - the scheduler's delete service
        # .. also removes the entry from the connection through the job's link ..
        job = _get_job(self, existing['job_id'])
        if job:
            _ = self.invoke('zato.scheduler.job.delete', {'id': job.id})

        # .. and make sure the entry is gone even if there was no job to cascade from.
        out:'dictlist' = []

        with closing(self.odb.session()) as session:
            schedules = get_schedule_list(session, conn.id)

            for schedule in schedules:
                if schedule['id'] != input.id:
                    out.append(schedule)

            set_schedule_list(session, conn.id, out)

# ################################################################################################################################
# ################################################################################################################################
