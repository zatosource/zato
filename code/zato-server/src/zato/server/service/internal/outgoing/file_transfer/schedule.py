# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from posixpath import normpath

# Zato
from zato.common.api import FileTransfer, SCHEDULER, SchedulerLink
from zato.common.defaults import default_cluster_id
from zato.common.exception import BadRequest
from zato.common.json_internal import dumps
from zato.common.odb.model import GenericConn, Job
from zato.common.util.file_transfer_scheduler import build_job_extra, get_job_name, get_schedule_list, \
    new_schedule_id, set_schedule_list
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
# The switch is optional because an edit that says nothing about it keeps whatever the schedule
# and its job already agree on, which is how a job switched off by hand stays off.
_schedule_input = ('name', Boolean('-is_active'), 'directory', '-pattern', 'ready_how', Int('-stability_delay'),
    '-marker_suffix', Boolean('-should_claim'), 'service', 'on_success', '-move_directory', Int('run_every'),
    'run_unit', 'start_date', Int('-arrival_window'))

# What a schedule nobody said anything about starts out as
_default_is_active = True

# All of a connection's schedules live in one JSON blob, so every change is a read of the whole list,
# an edit in Python and a write of the whole list back. This is the name of the lock that makes those
# three one step, keyed by connection so that changes to different connections never wait for each other.
_schedule_lock_prefix = 'zato.outgoing.file-transfer.schedule.'

# How long one change to a connection's schedules may hold the lock, in seconds - long enough
# to cover creating or editing the linked scheduler job as well.
_schedule_lock_ttl = 60

# How long a change waits for another one to finish before giving up, in seconds
_schedule_lock_block = 30

# ################################################################################################################################
# ################################################################################################################################

def get_connection(service:'Service', conn_id:'int') -> 'any_':
    """ Returns the GenericConn row of a file transfer connection, raising an error if it does not exist
    or is not of a file transfer type.
    """
    with closing(service.odb.session()) as session:
        query = session.query(GenericConn)
        filtered = query.filter_by(id=conn_id)
        if out := filtered.first():
            session.expunge(out)

    if not out:
        raise BadRequest(service.cid, f'Connection `{conn_id}` does not exist')

    if out.type_ not in FileTransfer.ConnTypeList:
        raise BadRequest(service.cid, f'Connection `{out.name}` is not an SFTP, SMB or FTP connection')

    return out

# ################################################################################################################################

def schedule_lock(service:'Service', conn_id:'int') -> 'any_':
    """ Returns the lock that serialises every change to one connection's list of schedules.
    """
    name = f'{_schedule_lock_prefix}{conn_id}'

    out = service.lock(name, ttl=_schedule_lock_ttl, block=_schedule_lock_block)
    return out

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

    # A move without a destination cannot be carried out, and neither can one whose destination
    # is not somewhere a file can actually be put out of the way.
    if input.on_success == _scheduler.OnSuccess.Move:
        if not input.move_directory:
            raise BadRequest(service.cid, 'Move directory is required when files are moved on success')

        _validate_move_directory(service, input.move_directory)

# ################################################################################################################################

def _validate_move_directory(service:'Service', move_directory:'str') -> 'None':
    """ Makes sure a move destination leads somewhere out of the way. It is always relative to the
    directory being polled and must lead further down rather than back into that directory, which
    would hand every file to the target service over and over, or above it, which would put the files
    outside the area the schedule was given.
    """
    # A destination is always relative to the polled directory, so one named in full names nowhere
    if move_directory.startswith('/'):
        raise BadRequest(service.cid,
            f'Move directory `{move_directory}` must be relative to the directory being polled')

    # Where a relative destination leads is what matters ..
    resolved = normpath(move_directory)

    # .. a destination that resolves to the polled directory itself would be no move at all ..
    if resolved == '.':
        raise BadRequest(service.cid,
            f'Move directory `{move_directory}` is the directory being polled, so files would never leave it')

    # .. and one that walks upwards leads out of the area the schedule was given.
    if resolved == '..' or resolved.startswith('../'):
        raise BadRequest(service.cid,
            f'Move directory `{move_directory}` leads above the directory being polled')

# ################################################################################################################################

def _build_schedule_dict(input:'any_', schedule_id:'str', job_id:'int', is_active:'bool') -> 'stranydict':
    """ Turns the validated input fields into one schedule entry of the connection's list. The switch
    comes from the caller because an edit that does not name it keeps what the schedule already had.
    """
    stability_delay = input.stability_delay or _scheduler.Default_Stability_Delay
    pattern = input.pattern or _scheduler.Default_Pattern

    # Optional inputs arrive as None when not given and the stored entry always uses concrete values
    marker_suffix = input.marker_suffix
    if marker_suffix is None:
        marker_suffix = ''

    should_claim = input.should_claim
    if should_claim is None:
        should_claim = False

    out = {
        'id': schedule_id,
        'name': input.name,
        'is_active': is_active,
        'directory': input.directory,
        'pattern': pattern,
        'ready_how': input.ready_how,
        'stability_delay': stability_delay,
        'marker_suffix': marker_suffix,
        'should_claim': should_claim,
        'service': input.service,
        'on_success': input.on_success,
        'move_directory': input.move_directory,
        'run_every': input.run_every,
        'run_unit': input.run_unit,
        'start_date': input.start_date,
        'arrival_window': input.arrival_window or _scheduler.Default_Arrival_Window,
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
    # The whole list is read, changed and written back, so nothing else may change it in the meantime
    with schedule_lock(service, conn.id):

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
    """ Returns the list of file transfer schedules of one file transfer connection.
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
    """ Creates a new file transfer schedule of one file transfer connection,
    along with the scheduler job that runs it.
    """
    input = (Int('conn_id'),) + _schedule_input
    output = 'id', 'name', Int('job_id')

    def handle(self) -> 'None':

        input = self.request.input

        # Make sure the connection exists and the schedule fields make sense ..
        conn = get_connection(self, input.conn_id)
        _validate_schedule(self, input)

        # .. the id belongs to the schedule alone and is never derived from anything the user may change ..
        schedule_id = new_schedule_id()

        # .. a new schedule is on unless the caller says otherwise ..
        is_active = input.is_active
        if is_active is None:
            is_active = _default_is_active

        # .. and from the read of the list to the write of it nothing else may change it, otherwise
        # .. two schedules created at the same time would lose each other.
        with schedule_lock(self, conn.id):

            # The name is a label, so the only rule about it is that no other schedule
            # of this connection carries it right now ..
            with closing(self.odb.session()) as session:
                schedules = get_schedule_list(session, conn.id)

            for schedule in schedules:
                if schedule['name'] == input.name:
                    raise BadRequest(self.cid, f'Schedule `{input.name}` already exists')

            # .. build the new entry and its linked job ..
            schedule = _build_schedule_dict(input, schedule_id, 0, is_active)
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
    """ Updates an existing file transfer schedule of one file transfer connection,
    keeping its scheduler job in sync.
    """
    input = (Int('conn_id'), 'id') + _schedule_input
    output = 'id', 'name', Int('job_id')

    def handle(self) -> 'None':

        input = self.request.input

        # Make sure the connection exists and the schedule fields make sense ..
        conn = get_connection(self, input.conn_id)
        _validate_schedule(self, input)

        # .. and from the read of the list to the write of it nothing else may change it.
        with schedule_lock(self, conn.id):

            # The entry being edited must exist ..
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

            # .. an edit that says nothing about the switch keeps what the entry already carries, which
            # .. the sync-back keeps in step with the job, so a job switched off by hand stays off ..
            is_active = input.is_active
            if is_active is None:
                is_active = existing['is_active']

            # .. rebuild the entry, keeping its id and job link ..
            updated = _build_schedule_dict(input, input.id, existing['job_id'], is_active)

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
    """ Deletes a file transfer schedule of one file transfer connection, along with its scheduler job.
    """
    input = Int('conn_id'), 'id'

    def handle(self) -> 'None':

        input = self.request.input

        # Make sure the connection exists ..
        conn = get_connection(self, input.conn_id)

        # .. and from the read of the list to the write of it nothing else may change it.
        with schedule_lock(self, conn.id):

            # Find the entry to delete ..
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
