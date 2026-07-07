# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from json import dumps
from time import time
from traceback import format_exc

# Python 2/3 compatibility
from six import add_metaclass

# Zato
from zato.common.api import EMAIL as EMail_Common, SCHEDULER, Zato_None
from zato.common.broker_message import EMAIL
from zato.common.defaults import default_cluster_id
from zato.common.exception import BadRequest
from zato.common.odb.model import IMAP, Job
from zato.common.odb.query import email_imap_list
from zato.common.util.imap_scheduler import interval_from_unit, update_imap_scheduler_fields
from zato.common.util.sql import parse_instance_opaque_attr
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, ChangePasswordBase
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, intnone
    from zato.server.service import Service

# ################################################################################################################################

_scheduler_common = EMail_Common.IMAP.Scheduler

elem = 'email_imap'
model = IMAP
label = 'an IMAP connection'
get_list_docs = 'IMAP connections'
broker_message = EMAIL
broker_message_prefix = 'IMAP_'
list_func = email_imap_list
create_edit_input_optional_extra = ['server_type', AsIs('tenant_id'), AsIs('client_id'), 'filter_criteria',
    'scheduler_run_every', 'scheduler_run_unit', 'scheduler_start_date', 'scheduler_service', 'scheduler_job_id']
output_optional_extra = ['server_type', 'server_type_human', AsIs('tenant_id'), AsIs('client_id'), 'filter_criteria',
    'scheduler_run_every', 'scheduler_run_unit', 'scheduler_start_date', 'scheduler_service', 'scheduler_job_id']

# ################################################################################################################################

def instance_hook(service:'Service', input:'Bunch', instance:'any_', attrs:'any_'):
    if attrs.is_create_edit:
        instance.username = input.username or '' # So it's not stored as None/NULL
        instance.host = input.host or Zato_None

# ################################################################################################################################

def _has_scheduler_config(service:'Service', input:'Bunch') -> 'bool':
    """ Returns True if the scheduler-related fields were given on input, raising an error if only some of them were.
    """
    run_every = input.scheduler_run_every
    start_date = input.scheduler_start_date
    job_service = input.scheduler_service

    # Collect the core fields that were actually filled in
    given = []

    for value in (run_every, start_date, job_service):
        if value:
            given.append(value)

    given_count = len(given)

    # Nothing was given, which means that no job is expected to exist
    if not given_count:
        return False

    # Only some of the fields were given, which we cannot accept
    if given_count != 3:
        raise BadRequest(service.cid, 'Scheduler options require run-every, start date and service to be given together')

    return True

# ################################################################################################################################

def _validate_scheduler_config(service:'Service', input:'Bunch') -> 'None':
    """ Makes sure the scheduler-related fields describe a job that can be created.
    """
    run_every = int(input.scheduler_run_every)
    run_unit = input.scheduler_run_unit

    if run_every < 1:
        raise BadRequest(service.cid, f'Scheduler run-every must be a positive integer instead of `{run_every}`')

    if run_unit not in _scheduler_common.UnitList:
        raise BadRequest(service.cid, f'Scheduler unit `{run_unit}` is not one of `{_scheduler_common.UnitList}`')

    if input.scheduler_service not in service.server.service_store.name_to_impl_name:
        raise BadRequest(service.cid, f'Scheduler service `{input.scheduler_service}` does not exist')

    # Store the parsed value back so it is saved as an integer
    input.scheduler_run_every = run_every

# ################################################################################################################################

def pre_opaque_attrs_hook(service:'Service', input:'Bunch', instance:'any_', attrs:'any_') -> 'None':

    # An empty job ID on input must not overwrite the one stored previously - the authoritative value
    # is written back after the linked job is synchronized, once this request is committed.
    if attrs.is_edit:
        if not input.scheduler_job_id:
            previous_job_id = _get_previous_job_id(service, input.id)
            if previous_job_id:
                input.scheduler_job_id = previous_job_id

    # Validate the scheduler-related input before anything is committed to the database
    if _has_scheduler_config(service, input):
        _validate_scheduler_config(service, input)

# ################################################################################################################################

def _get_previous_job_id(service:'Service', conn_id:'int') -> 'intnone':
    """ Reads the linked job ID from the committed opaque attributes of an IMAP connection.
    """
    with closing(service.odb.session()) as session:
        row = session.query(IMAP).filter_by(id=conn_id).first()
        if not row:
            return None
        opaque = parse_instance_opaque_attr(row)

    out = opaque.get('scheduler_job_id')
    return out

# ################################################################################################################################

def _get_linked_job(service:'Service', job_id:'int') -> 'any_':
    """ Returns the Job row of the given ID or None if it no longer exists.
    """
    with closing(service.odb.session()) as session:
        out = session.query(Job).filter_by(id=job_id).first()
        if out:
            session.expunge(out)

    return out

# ################################################################################################################################

def _sync_scheduler_job(service:'Service', input:'Bunch', instance:'any_', attrs:'any_') -> 'None':
    """ Creates, updates or deletes the scheduler job linked to an IMAP connection, based on the input just committed.
    """
    has_config = _has_scheduler_config(service, input)

    # On edit, the connection may already point to a job ..
    if attrs.is_edit:
        previous_job_id = _get_previous_job_id(service, input.id)
    else:
        previous_job_id = None

    # .. and that job may or may not still exist, e.g. it could have been deleted from the scheduler's own UI.
    job = None
    if previous_job_id:
        job = _get_linked_job(service, previous_job_id)

    # We are to keep a job in sync with what was given on input ..
    if has_config:

        # The job invokes the internal dispatch service and its extra data carries the connection's identity
        # along with the user's service, which the dispatch service invokes once per each message received.
        extra = dumps({
            _scheduler_common.Extra_Conn_ID: instance.id,
            _scheduler_common.Extra_Conn_Name: input.name,
            _scheduler_common.Extra_Service: input.scheduler_service,
        })

        request = {
            'cluster_id': default_cluster_id,
            'is_active': input.is_active,
            'job_type': SCHEDULER.JOB_TYPE.INTERVAL_BASED,
            'service': _scheduler_common.Dispatch_Service,
            'start_date': input.scheduler_start_date,
            'extra': extra,
            'imap_conn_id': instance.id,
        }

        interval = interval_from_unit(input.scheduler_run_every, input.scheduler_run_unit)
        request.update(interval)

        # .. the job exists so it is updated in place, keeping its current name to honor renames done in the scheduler ..
        if job:
            request['id'] = job.id
            request['name'] = job.name
            _ = service.invoke('zato.scheduler.job.edit', request)
            job_id = job.id

        # .. otherwise, a new job is created for this connection ..
        else:
            request['name'] = _scheduler_common.Job_Prefix + input.name
            response = service.invoke('zato.scheduler.job.create', request)
            if 'id' not in response:
                response = response['zato_scheduler_job_create_response']
            job_id = response['id']

        # .. either way, the connection's opaque attributes now reflect the job's current state.
        with closing(service.odb.session()) as session:
            update_imap_scheduler_fields(session, instance.id, input.scheduler_run_every, input.scheduler_run_unit,
                input.scheduler_start_date, input.scheduler_service, job_id)

    # There is no scheduler configuration on input ..
    else:

        # .. so a job that still exists is deleted, which also clears the connection's opaque scheduler fields.
        if job:
            _ = service.invoke('zato.scheduler.job.delete', {'id': job.id})

# ################################################################################################################################

def delete_hook(service:'Service', input:'Bunch', instance:'any_', attrs:'any_') -> 'None':

    # The connection is gone now so its linked job, if any, goes away too
    opaque = parse_instance_opaque_attr(instance)

    if job_id := opaque.get('scheduler_job_id'):
        _ = service.invoke('zato.scheduler.job.delete', {'id': job_id})

# ################################################################################################################################

def response_hook(service:'Service', input:'Bunch', instance:'any_', attrs:'any_', hook_type:'str'):

    if hook_type == 'get_list':

        for item in service.response.payload:

            # This may be None ..
            server_type = item.get('server_type')

            # .. in which case we can assume a default one ..
            if not server_type:
                item.server_type = EMail_Common.IMAP.ServerType.Generic

            # .. and now we can obtain a human-friendly name.
            item.server_type_human = EMail_Common.IMAP.ServerTypeHuman[item.server_type]

            # This should be cleared out in case there is no user-set value
            if item.host == Zato_None:
                item.host = ''

            # Connections created before the scheduler fields existed have none of them
            for name in _scheduler_common.FieldList:
                if not item.get(name):
                    item[name] = ''

    elif hook_type == 'create_edit':

        # The connection is committed by now so its linked job can be created, updated or deleted
        _sync_scheduler_job(service, input, instance, attrs)

# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = IMAP.name,

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Create(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Edit(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(DeleteMeta)
class Delete(AdminService):
    pass

# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an IMAP connection.
    """
    password_required = False

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        return self._handle(IMAP, _auth, EMAIL.IMAP_CHANGE_PASSWORD.value)

# ################################################################################################################################

class Ping(AdminService):
    """ Pings an IMAP connection to check its configuration.
    """
    input = 'id'
    output = '-info'

    def handle(self):

        with closing(self.odb.session()) as session:
            item = session.query(IMAP).filter_by(id=self.request.input.id).one()

        start_time = time()

        if not self.email:
            self.response.payload.info = 'Could not ping connection; is component_enabled.email set to True in server.conf?'
        else:
            self.email.imap.get(item.name, True).conn.ping()
            response_time = time() - start_time

            self.response.payload.info = 'Ping NOOP submitted, took:`{0:03.4f} s`, check server logs for details.'.format(
                response_time)

# ################################################################################################################################

class ProcessMessages(AdminService):
    """ Invoked by the scheduler on behalf of an IMAP connection - reads messages matching the connection's
    get-criteria and invokes the configured service once per each message received.
    """

    def handle(self) -> 'None':

        # The scheduler job carries the connection's identity and the target service in its extra data,
        # which arrives here as a dict no matter if the invocation came from the scheduler or over HTTP.
        context = self.request.payload

        conn_name = context[_scheduler_common.Extra_Conn_Name]
        target_service = context[_scheduler_common.Extra_Service]

        # The email component may be disabled in server.conf
        if not self.email:
            self.logger.warning('Could not process IMAP messages for `%s`; ' \
                'is component_enabled.email set to True in server.conf?', conn_name)
            return

        # Get a client for the mailbox that this connection points to ..
        conn = self.email.imap.get(conn_name, True).conn

        # .. and hand each message over to the target service. The service receives the message object itself
        # .. and it is up to the service to mark the message as seen or to delete it. The invocation is synchronous
        # .. so the underlying connection is still open while the service runs.
        for _, message in conn.get():
            try:
                _ = self.invoke(target_service, message)
            except Exception:
                self.logger.warning('Could not invoke `%s` with an IMAP message from `%s` -> `%s`',
                    target_service, conn_name, format_exc())

# ################################################################################################################################
