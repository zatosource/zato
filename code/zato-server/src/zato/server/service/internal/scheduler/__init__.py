# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from datetime import datetime, timedelta, timezone
from json import loads
from traceback import format_exc

# requests
from requests.exceptions import ConnectionError as RequestsConnectionError

# ciso8601
try:
    from zato.common.util.api import parse_datetime
except ImportError:
    from dateutil.parser import parse as parse_datetime

# Zato
from zato.common.api import EMAIL, SCHEDULER, SchedulerLink, ZATO_NONE
from zato.common.defaults import default_cluster_id
from zato.common.exception import ServiceMissingException, ZatoException
from zato.common.odb.model import Cluster, IntervalBasedJob, Job, Service as ServiceModel
from zato.common.util.imap_scheduler import clear_imap_scheduler_fields, unit_from_interval, update_imap_scheduler_fields
from zato.common.util.rest_invocation import clear_linked_job_fields, update_linked_job_fields
from zato.common.typing_ import any_, anylist, anytuple
from zato.common.util.sql import elems_with_opaque, parse_instance_opaque_attr, set_instance_opaque_attrs
from zato.server.service import Int, Bool, List
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_service_name_prefix = 'zato.scheduler.job.'
_entity_type = 'scheduler'
_ib_params = ('weeks', 'days', 'hours', 'minutes', 'seconds')
_new_params = ('jitter_ms', 'timezone', 'max_execution_time_ms',
    'on_success_service', 'on_success_job', 'on_error_service', 'on_error_job')

# This one is stored in the job's opaque attributes only - it points back to the IMAP connection
# that the job was auto-created for and it must never be sent to the scheduler process itself.
_imap_conn_id_param = 'imap_conn_id'

# These are stored in the job's opaque attributes only - they point back to the connection of any type
# that the job was auto-created for, no matter if it runs scheduled invocations or health checks.
_link_params = list(SchedulerLink.FieldList)

# The key in a job's extra data under which an IMAP-linked job carries the service
# that is to be invoked once per each message received.
_imap_extra_service = EMAIL.IMAP.Scheduler.Extra_Service

# The key in a job's extra data under which an IMAP-linked job carries the invoke-with mode,
# i.e. whether the service receives whole messages or their individual attachments.
_imap_extra_invoke_with = EMAIL.IMAP.Scheduler.Extra_Invoke_With

_opaque_stale_keys = frozenset(_ib_params + (
    'repeats', 'service', 'name', 'is_active', 'job_type', 'start_date', 'extra', 'id', 'cluster_id',
))

default_page = 1
default_page_size = 50

# ################################################################################################################################
# ################################################################################################################################

def _item_by_id(items, id_):
    for item in items:
        if item['id'] == id_:
            return item
    return None

# ################################################################################################################################
# ################################################################################################################################

def _get_job_summaries(server:'any_') -> 'anylist':
    """ Returns runtime job summaries from the scheduler daemon. Environments that run without a scheduler,
    e.g. quickstart ones created with --no-scheduler, get an empty list so that job listings can still
    be served from the ODB, only without any last-run details.
    """
    try:
        out = server._scheduler.get_job_summaries()
    except RequestsConnectionError:
        logger.info('Scheduler unreachable, returning no job summaries')
        out = []

    return out

# ################################################################################################################################
# ################################################################################################################################

def _map_job_summaries(summaries:'anylist') -> 'anytuple':
    """ Maps runtime job summaries by ID, with a lookup by name for jobs whose IDs changed, e.g. after a redeployment.
    """
    summary_by_id = {}
    summary_by_name = {}

    for summary in summaries:
        name = summary['name']
        summary_by_id[summary['id']] = summary

        # Two summaries may share a name if runtime IDs diverged from ODB ones -
        # keep the one with the newest last run time so a stale leftover cannot shadow the live entry.
        existing = summary_by_name.get(name)

        if existing is None:
            summary_by_name[name] = summary
            continue

        last_run_utc = summary['last_run_utc']

        if last_run_utc:
            existing_last_run = existing['last_run_utc']
            if existing_last_run is None:
                summary_by_name[name] = summary
            elif last_run_utc > existing_last_run:
                summary_by_name[name] = summary

    out = summary_by_id, summary_by_name
    return out

# ################################################################################################################################
# ################################################################################################################################

class _SchedulerAdmin(AdminService):
    """ Base class for scheduler administration services.
    """

    def _service_by_name(self, service_name):
        """ Returns True if the service is deployed on this server.
        """
        return service_name in self.server.service_store.name_to_impl_name

    def _enrich_job(self, item):
        """ Adds resolved service_name and service_id to a job dict.
        """
        out = dict(item)
        service_name = item['service']
        out['service_name'] = service_name
        if self._service_by_name(service_name):
            out['service_id'] = self.server.service_store.get_service_id_by_name(service_name)
        else:
            out['service_id'] = None
        return out

# ################################################################################################################################
# ################################################################################################################################

def _create_edit(self, action):
    """Creating and updating a job using ODB."""

    # stdlib
    from contextlib import closing

    input = self.request.input
    input.cluster_id = default_cluster_id

    self.logger.info('_create_edit: action=%s input=%s', action, input)

    job_type = input.job_type
    name = input.name
    service_name = input.service
    logger = self.logger
    cid = self.cid

    # Note whether the caller is the IMAP connection layer - if it is not, and the job carries a link
    # to an IMAP connection, the connection's own scheduler fields will be updated after the job is saved.
    input_had_imap_conn_id = bool(input.get(_imap_conn_id_param))

    # The same applies to the generic connection link, e.g. an outgoing REST or SOAP connection
    # whose scheduled invocations or health checks this job runs.
    input_had_link = bool(input.get(SchedulerLink.Conn_ID))

    if job_type not in (SCHEDULER.JOB_TYPE.ONE_TIME, SCHEDULER.JOB_TYPE.INTERVAL_BASED):
        msg = f'Unrecognized job type [{job_type}]'
        logger.error(msg)
        raise ZatoException(cid, msg)

    with closing(self.odb.session()) as session:
        job_rows = session.query(Job.id, Job.name).filter_by(cluster_id=default_cluster_id).all()
        jobs = [{'id': row.id, 'name': row.name} for row in job_rows]

    def _other_same_name(jid):
        for job in jobs:
            if job['name'] == name and job['id'] != jid:
                return job
        return None

    if action == 'create':
        existing_one = _other_same_name(None)
    else:
        existing_one = _other_same_name(input.id)

    if existing_one:
        if input.get('should_ignore_existing'):
            return
        raise ZatoException(cid, f'Job `{name}` already exists')

    if not self._service_by_name(service_name):
        msg = f'Service `{service_name}` does not exist'
        logger.info(msg)
        raise ServiceMissingException(cid, msg)

    extra = input.extra
    if extra is None:
        extra = ''
    is_active = input.is_active
    start_date = parse_datetime(input.start_date)
    start_iso = start_date.isoformat()

    if action == 'edit':
        old = _item_by_id(jobs, input.id)
        if not old:
            raise ZatoException(cid, f'Job `{input.id}` not found')
        data = dict(old)
    else:
        data = {}

    data.update({
        'name': name,
        'is_active': is_active,
        'job_type': job_type,
        'start_date': start_iso,
        'service': service_name,
        'extra': extra if extra else None,
    })

    for k in _ib_params + ('repeats',):
        val = input.get(k)
        if val == ZATO_NONE:
            val = None
        data[k] = val

    for k in _new_params:
        val = input.get(k)
        if val == ZATO_NONE:
            val = None
        if val is not None and val != '':
            data[k] = val

    if job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED:
        if not any(input.get(key) for key in _ib_params):
            msg = "At least one of ['weeks', 'days', 'hours', 'minutes', 'seconds'] must be given"
            logger.error(msg)
            raise ZatoException(cid, msg)
        for param in _ib_params + ('repeats',):
            value = input.get(param)
            if value == ZATO_NONE or value is None or value == '':
                data[param] = 0
            else:
                data[param] = int(value)
    else:
        for param in _ib_params + ('repeats',):
            data[param] = None

    try:
        with closing(self.odb.session()) as session:
            service_row = session.query(ServiceModel).filter_by(name=service_name, cluster_id=input.cluster_id).first()
            if not service_row:
                raise ZatoException(cid, f'Service `{service_name}` not found in ODB')

            if action == 'edit':
                job_row = session.query(Job).filter_by(id=input.id).first()
                if not job_row:
                    raise ZatoException(cid, f'Job `{input.id}` not found')
                job_row.name = name
                job_row.is_active = is_active
                job_row.job_type = job_type
                job_row.start_date = start_date
                job_row.service = service_row
                job_row.extra = extra if extra else None
            else:
                cluster_row = session.query(Cluster).filter_by(id=input.cluster_id).first()
                job_row = Job()
                job_row.name = name
                job_row.is_active = is_active
                job_row.job_type = job_type
                job_row.start_date = start_date
                job_row.service = service_row
                job_row.cluster = cluster_row
                job_row.extra = extra if extra else None
                session.add(job_row)
                session.flush()

            if job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED:
                ib = session.query(IntervalBasedJob).filter_by(job_id=job_row.id).first()
                if not ib:
                    ib = IntervalBasedJob()
                    ib.job = job_row
                    session.add(ib)

                ib.weeks = data['weeks']
                ib.days = data['days']
                ib.hours = data['hours']
                ib.minutes = data['minutes']
                ib.seconds = data['seconds']
                ib.repeats = data['repeats']

            # An empty value must not overwrite a link stored previously, e.g. when the edit comes
            # from the scheduler's own UI which does not carry this parameter in its forms.
            if not input_had_imap_conn_id:
                existing_opaque = parse_instance_opaque_attr(job_row)
                if existing_link := existing_opaque.get(_imap_conn_id_param):
                    input.imap_conn_id = existing_link

            # The same protection applies to the generic connection link
            if not input_had_link:
                existing_opaque = parse_instance_opaque_attr(job_row)
                for link_param in _link_params:
                    if existing_value := existing_opaque.get(link_param):
                        input[link_param] = existing_value

            set_instance_opaque_attrs(job_row, input, only=list(_new_params) + [_imap_conn_id_param] + _link_params)

            if job_row.opaque1:
                from json import loads as json_loads, dumps as json_dumps
                opaque = json_loads(job_row.opaque1)
                for stale_key in _opaque_stale_keys:
                    opaque.pop(stale_key, None)
                job_row.opaque1 = json_dumps(opaque)

            session.add(job_row)
            session.commit()

            data['id'] = job_row.id
            job_id = job_row.id

            # Read the link back after the commit - it may come from a previous save rather than from this input
            job_opaque = parse_instance_opaque_attr(job_row)

        logger.info('_create_edit action=%s job_id=%s data=%s', action, job_id, data)

        if action == 'create':
            self.server._scheduler.create_job(job_id, data)
            logger.info('_create_edit: create_job returned for job_id=%s', job_id)
        else:
            self.server._scheduler.edit_job(job_id, data)
            logger.info('_create_edit: edit_job returned for job_id=%s', job_id)

        # An edit made directly in the scheduler is written back to the IMAP connection that this job is linked to,
        # so the connection never shows a stale description of its job. Edits that come from the IMAP layer itself
        # are skipped because that layer updates the connection on its own.
        if action == 'edit':
            if not input_had_imap_conn_id:
                if job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED:
                    if imap_conn_id := job_opaque.get(_imap_conn_id_param):
                        run = unit_from_interval(data['weeks'], data['days'], data['hours'], data['minutes'], data['seconds'])

                        # The job's own service is the internal dispatch service so the one to write back
                        # is the per-message target service carried in the job's extra data, along with
                        # the invoke-with mode. If the extra data does not describe them, only the interval
                        # and start date are written back.
                        target_service = None
                        invoke_with = None
                        if extra:
                            try:
                                extra_data = loads(extra)
                            except ValueError:
                                extra_data = None
                            if extra_data:
                                target_service = extra_data.get(_imap_extra_service)
                                invoke_with = extra_data.get(_imap_extra_invoke_with)

                        with closing(self.odb.session()) as session:
                            update_imap_scheduler_fields(
                                session, imap_conn_id, run.run_every, run.run_unit, start_iso, target_service,
                                invoke_with, job_id)

        # Likewise, an edit made directly in the scheduler is written back to the connection of any type
        # that this job is linked to, no matter if the job runs scheduled invocations or health checks.
        if action == 'edit':
            if not input_had_link:
                if job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED:
                    if link_conn_id := job_opaque.get(SchedulerLink.Conn_ID):
                        link_kind = job_opaque[SchedulerLink.Kind]
                        run = unit_from_interval(data['weeks'], data['days'], data['hours'], data['minutes'], data['seconds'])

                        with closing(self.odb.session()) as session:
                            update_linked_job_fields(session, link_conn_id, link_kind, run.run_every, run.run_unit,
                                start_iso, job_id)

        self.response.payload.id = job_row.id
        self.response.payload.name = input.name
    except Exception:
        logger.error('Could not complete the request, e:`%s`', format_exc())
        raise

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(_SchedulerAdmin):
    """ A base class for both creating and editing scheduler jobs.
    """
    input = 'cluster_id', 'name', 'is_active', 'job_type', 'service', 'start_date', \
        Int('-id'), '-extra', '-weeks', '-days', '-hours', '-minutes', '-seconds', '-repeats', \
        '-cron_definition', '-should_ignore_existing', \
        '-jitter_ms', '-timezone', '-max_execution_time_ms', \
        '-on_success_service', '-on_success_job', '-on_error_service', '-on_error_job', \
        '-imap_conn_id', '-link_conn_type', '-link_conn_id', '-link_kind'
    output = '-id', '-name', '-cron_definition'

    def handle(self):
        _create_edit(self, self.__class__.__name__.lower())

# ################################################################################################################################
# ################################################################################################################################

class _Get(_SchedulerAdmin):
    """ Base class for services that return scheduler job data.
    """
    output = 'id', 'name', 'is_active', 'job_type', 'start_date', 'service_id', 'service_name', \
        '-extra', '-weeks', '-days', '-hours', '-minutes', '-seconds', '-repeats', '-cron_definition', \
        '-jitter_ms', '-timezone', '-max_execution_time_ms', \
        '-on_success_service', '-on_success_job', '-on_error_service', '-on_error_job', \
        '-imap_conn_id', '-link_conn_type', '-link_conn_id', '-link_kind', '-last_run_utc', Int('-last_duration_ms')

# ################################################################################################################################
# ################################################################################################################################

class GetList(_Get):
    """ Returns a list of all jobs defined in the scheduler.
    """
    name = _service_name_prefix + 'get-list'
    _filter_by = Job.name,

    input = '-cluster_id', Int('-cur_page'), Bool('-paginate'), '-query', '-service_name'

    def handle(self):
        from contextlib import closing
        from zato.common.odb.query import job_list

        input = self.request.input
        input.cluster_id = default_cluster_id

        with closing(self.odb.session()) as session:

            search_result = self._search(job_list, session, input.cluster_id, input.get('service_name'), False)

            data = elems_with_opaque(search_result)

            items = []
            for row in data:
                row['service'] = row.pop('service_name')
                row['start_date'] = row['start_date'].isoformat()
                items.append(self._enrich_job(row))

        # Map runtime summaries by ID, with a lookup by name for jobs whose IDs changed, e.g. after a redeployment ..
        summary_by_id, summary_by_name = _map_job_summaries(_get_job_summaries(self.server))

        # .. and attach the last run details to each job - the time is an empty string
        # .. and the duration is None for jobs that never ran.
        for item in items:
            summary = summary_by_id.get(item['id'])
            if summary is None:
                summary = summary_by_name.get(item['name'])

            if summary is None:
                item['last_run_utc'] = ''
                item['last_duration_ms'] = None
            else:
                last_run_utc = summary['last_run_utc']
                if last_run_utc is None:
                    last_run_utc = ''
                item['last_run_utc'] = last_run_utc
                item['last_duration_ms'] = summary['last_duration_ms']

        self.response.payload = items

# ################################################################################################################################
# ################################################################################################################################

class GetByID(_Get):
    """ Returns a job by its ID.
    """
    name = _service_name_prefix + 'get-by-id'

    input = Int('cluster_id'), Int('id')

    def handle(self) -> 'None':
        from contextlib import closing
        from zato.common.odb.model import Job, IntervalBasedJob

        item = None
        job_id = self.request.input.id

        with closing(self.odb.session()) as session:
            job = session.query(Job).filter_by(id=job_id).first()
            if job:
                item = {'id': job.id, 'name': job.name, 'is_active': job.is_active, 'job_type': job.job_type,
                        'start_date': job.start_date.isoformat(), 'service': job.service.name,
                        'extra': job.extra}
                item.update(parse_instance_opaque_attr(job))
                ib = session.query(IntervalBasedJob).filter_by(job_id=job.id).first()
                if ib:
                    item['weeks'] = ib.weeks
                    item['days'] = ib.days
                    item['hours'] = ib.hours
                    item['minutes'] = ib.minutes
                    item['seconds'] = ib.seconds
                    item['repeats'] = ib.repeats

        if not item:
            self.logger.info('Job %s not found in ODB, returning empty response', job_id)
            self.response.payload = {}
            return

        result = self.server._scheduler.get_history_page(job_id, 0, 10, SCHEDULER.OUTCOME.All)
        records = result['records']

        last_outcome = None
        last_duration_ms = None
        recent_outcomes = [] # type: list

        if records:
            last_record = records[-1]
            last_outcome = last_record['outcome']

            for idx in range(len(records) - 1, -1, -1):
                rec_duration = records[idx]['duration_ms']
                if rec_duration is not None:
                    last_duration_ms = rec_duration
                    break

            for rec in records:
                recent_outcomes.append(rec['outcome'])

        item['last_outcome'] = last_outcome
        item['last_duration_ms'] = last_duration_ms
        item['recent_outcomes'] = recent_outcomes

        self.response.payload = self._enrich_job(item)

# ################################################################################################################################
# ################################################################################################################################

class GetByName(_Get):
    """ Returns a job by its name.
    """
    name = _service_name_prefix + 'get-by-name'

    input = 'cluster_id', 'name'

    def handle(self):
        from contextlib import closing
        from zato.common.odb.model import Job, IntervalBasedJob
        item = None
        with closing(self.odb.session()) as session:
            job = session.query(Job).filter_by(name=self.request.input.name, cluster_id=default_cluster_id).first()
            if job:
                item = {'id': job.id, 'name': job.name, 'is_active': job.is_active, 'job_type': job.job_type,
                        'start_date': job.start_date.isoformat(), 'service': job.service.name,
                        'extra': job.extra}
                item.update(parse_instance_opaque_attr(job))
                ib = session.query(IntervalBasedJob).filter_by(job_id=job.id).first()
                if ib:
                    item['weeks'] = ib.weeks
                    item['days'] = ib.days
                    item['hours'] = ib.hours
                    item['minutes'] = ib.minutes
                    item['seconds'] = ib.seconds
                    item['repeats'] = ib.repeats
        if not item:
            raise ZatoException(self.cid, 'Job not found')
        self.response.payload = self._enrich_job(item)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    """ Creates a new scheduler's job.
    """
    name = _service_name_prefix + 'create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    """ Updates a scheduler's job.
    """
    name = _service_name_prefix + 'edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_SchedulerAdmin):
    """ Deletes a scheduler's job.
    """
    name = _service_name_prefix + 'delete'

    input = 'id',

    def handle(self):
        from contextlib import closing
        from zato.common.odb.model import Job, IntervalBasedJob
        try:
            with closing(self.odb.session()) as session:
                job_row = session.query(Job).filter_by(id=self.request.input.id).first()
                if not job_row:
                    raise ZatoException(self.cid, 'Job not found')

                job_id = job_row.id

                # Read the link to an IMAP connection, if any, before the row is deleted
                job_opaque = parse_instance_opaque_attr(job_row)

                session.query(IntervalBasedJob).filter_by(job_id=job_row.id).delete()
                session.delete(job_row)
                session.commit()

            self.server._scheduler.delete_job(job_id)

            # The job was auto-created for an IMAP connection so the connection's scheduler fields
            # are cleared now - otherwise it would still describe a job that no longer exists.
            if imap_conn_id := job_opaque.get(_imap_conn_id_param):
                with closing(self.odb.session()) as session:
                    clear_imap_scheduler_fields(session, imap_conn_id)

            # The same applies to jobs auto-created for connections of any other type,
            # no matter if the job ran scheduled invocations or health checks.
            if link_conn_id := job_opaque.get(SchedulerLink.Conn_ID):
                link_kind = job_opaque[SchedulerLink.Kind]
                with closing(self.odb.session()) as session:
                    clear_linked_job_fields(session, link_conn_id, link_kind)

        except Exception:
            self.logger.error('Could not delete the job, e:`%s`', format_exc())
            raise

# ################################################################################################################################
# ################################################################################################################################

class Execute(_SchedulerAdmin):
    """ Executes a scheduler's job.
    """
    name = _service_name_prefix + 'execute'

    input = 'job_id',

    def handle(self):
        try:
            from contextlib import closing
            from zato.common.odb.model import Job
            with closing(self.odb.session()) as session:
                job_row = session.query(Job).filter_by(id=self.request.input.job_id).first()
            if not job_row:
                raise ZatoException(self.cid, 'Job not found')

            self.server._scheduler.execute_job(job_row.id, job_row.name)
        except Exception:
            self.logger.error('Could not execute the job, e:`%s`', format_exc())
            raise

# ################################################################################################################################
# ################################################################################################################################

class GetHistory(_SchedulerAdmin):
    """ Returns paginated execution history for a scheduler job.
    """
    name = _service_name_prefix + 'get-history'

    input = Int('id'), Int('-page'), Int('-page_size'), '-since_timestamp', '-since_iso', List('-outcomes'), List('-running_runs')

    def handle(self) -> 'None':
        try:
            job_id = self.request.input.id
            since_timestamp = self.request.input.get('since_timestamp')
            since_iso = self.request.input.get('since_iso') or ''
            outcomes = self.request.input.get('outcomes')
            if not outcomes:
                outcomes = SCHEDULER.OUTCOME.All

            scheduler = self.server._scheduler

            if since_timestamp:
                running_runs = self.request.input.get('running_runs') or []
                result = scheduler.get_history_since(job_id, since_timestamp, outcomes, running_runs, since_iso)
                self.response.payload = {'rows': result['rows'], 'total': result['total']}
            else:
                page = self.request.input.get('page')
                if not page:
                    page = default_page

                page_size = self.request.input.get('page_size')
                if not page_size:
                    page_size = default_page_size

                offset = (page - 1) * page_size

                result = scheduler.get_history_page(job_id, offset, page_size, outcomes, since_iso)

                self.response.payload = {
                    'rows': result['records'],
                    'total': result['total'],
                    'page': page,
                    'page_size': page_size,
                }

        except Exception:
            self.logger.error('Could not get job history, e:`%s`', format_exc())
            raise

# ################################################################################################################################
# ################################################################################################################################

class GetRunDetail(_SchedulerAdmin):
    """ Returns a single execution record by run number with prev/next navigation metadata.
    """
    name = _service_name_prefix + 'get-run-detail'

    input = Int('job_id'), Int('current_run')

    def handle(self) -> 'None':
        result = self.server._scheduler.get_run_detail(
            self.request.input.job_id,
            self.request.input.current_run,
        )
        self.response.payload = result

# ################################################################################################################################
# ################################################################################################################################

class GetLastRunList(_SchedulerAdmin):
    """ Returns last run times for a list of jobs, based on the scheduler's runtime summaries.
    """
    name = _service_name_prefix + 'get-last-run-list'

    input = List('id_list')

    def handle(self) -> 'None':
        from contextlib import closing

        # The IDs arrive as strings from the network, hence the conversion ..
        id_list = set()
        for job_id in self.request.input.id_list:
            id_list.add(int(job_id))

        # .. map each requested ID to its name so that jobs can also be matched by name
        # .. if their IDs changed, e.g. after a redeployment ..
        name_by_id = {}
        with closing(self.odb.session()) as session:
            job_rows = session.query(Job).filter_by(cluster_id=default_cluster_id).all()
            for job in job_rows:
                if job.id in id_list:
                    name_by_id[job.id] = job.name

        # .. one call returns runtime summaries for all jobs ..
        summary_by_id, summary_by_name = _map_job_summaries(_get_job_summaries(self.server))

        # .. and each requested job is looked up by ID first and by name second - the last run time
        # .. is an empty string and the duration is None for jobs that never ran.
        items = []
        for job_id in id_list:
            summary = summary_by_id.get(job_id)
            if summary is None:
                name = name_by_id.get(job_id)
                summary = summary_by_name.get(name)

            if summary is None:
                last_run_utc = ''
                last_duration_ms = None
            else:
                last_run_utc = summary['last_run_utc']
                if last_run_utc is None:
                    last_run_utc = ''
                last_duration_ms = summary['last_duration_ms']

            items.append({'id': job_id, 'last_run_utc': last_run_utc, 'last_duration_ms': last_duration_ms})

        self.response.payload = {'items': items}

# ################################################################################################################################
# ################################################################################################################################

class GetLogEntries(_SchedulerAdmin):
    """ Returns log entries for a specific execution record, supporting incremental fetching.
    """
    name = _service_name_prefix + 'get-log-entries'

    input = Int('job_id'), Int('current_run'), Int('since_idx')

    def handle(self) -> 'None':
        try:
            job_id = self.request.input.job_id
            current_run = self.request.input.current_run
            since_idx = self.request.input.since_idx

            entries = self.server._scheduler.get_log_entries(job_id, current_run, since_idx)
            self.response.payload = {'entries': entries}
        except Exception:
            self.logger.error('Could not get log entries, e:`%s`', format_exc())
            raise

# ################################################################################################################################
# ################################################################################################################################

class GetCurrentState(_SchedulerAdmin):
    """ Returns the current state of all scheduler jobs and their execution history.
    """
    name = _service_name_prefix + 'get-current-state'

    input = '-chart_since_iso', '-chart_until_iso', '-recent_since_iso', Int('-recent_limit')

    def handle(self) -> 'None':
        try:
            from contextlib import closing

            scheduler = self.server._scheduler

            chart_since_iso = self.request.input.chart_since_iso or ''
            chart_until_iso = self.request.input.chart_until_iso or ''
            recent_since_iso = self.request.input.recent_since_iso or ''
            recent_limit = self.request.input.recent_limit or 100

            with closing(self.odb.session()) as session:
                job_rows = session.query(Job).filter_by(cluster_id=default_cluster_id).all()
                store_jobs = []
                for job in job_rows:
                    store_jobs.append({
                        'id': job.id,
                        'name': job.name,
                        'is_active': job.is_active,
                        'job_type': job.job_type,
                        'service': job.service.name,
                    })

            # .. get_job_summaries now includes last_outcome, last_duration_ms,
            # .. recent_outcomes, and per-job outcome_counts ..
            runtime_by_id = {}
            runtime_by_name = {}
            for summary in _get_job_summaries(self.server):
                runtime_by_id[summary['id']] = summary
                runtime_by_name[summary['name']] = summary

            total_jobs = len(store_jobs)
            active_jobs = 0
            paused_jobs = 0

            jobs = []

            for item in store_jobs:
                job_id = item['id']
                is_active = item['is_active']
                name = item['name']

                if is_active:
                    active_jobs += 1
                else:
                    paused_jobs += 1

                runtime = runtime_by_id.get(job_id)
                if runtime is None:
                    runtime = runtime_by_name.get(name)

                entry = {
                    'id': job_id,
                    'name': name,
                    'is_active': is_active,
                    'job_type': item['job_type'],
                    'service': item['service'],
                }

                if runtime is not None:
                    entry['next_fire_utc'] = runtime['next_fire_utc']
                    entry['is_running'] = runtime['in_flight']
                    entry['current_run'] = runtime['current_run']
                    entry['interval_ms'] = runtime['interval_ms']
                    entry['last_outcome'] = runtime['last_outcome']
                    entry['last_duration_ms'] = runtime['last_duration_ms']
                    entry['recent_outcomes'] = runtime['recent_outcomes']
                else:
                    entry['next_fire_utc'] = None
                    entry['is_running'] = False
                    entry['current_run'] = 0
                    entry['interval_ms'] = 0
                    entry['last_outcome'] = None
                    entry['last_duration_ms'] = None
                    entry['recent_outcomes'] = []

                jobs.append(entry)

            # .. outcome_counts and total_executions are summed from per-job summaries ..
            outcome_counts = {
                'ok': 0,
                'error': 0,
                'timeout': 0,
                'running': 0,
                'skipped_already_in_flight': 0,
            }
            execution_outcomes = {'ok', 'error', 'timeout'}
            total_executions = 0

            for summary in runtime_by_id.values():
                per_job = summary['outcome_counts']
                for key in outcome_counts:
                    outcome_counts[key] += per_job[key]
                for outcome_key in execution_outcomes:
                    total_executions += per_job[outcome_key]

            # .. get chart_buckets from Rust (pre-aggregated) ..
            chart_buckets = scheduler.get_chart_data(chart_since_iso, chart_until_iso)

            # .. get recent events for the table ..
            recent_events = scheduler.get_timeline_events_since(recent_since_iso, recent_limit)

            # .. compute header tile stats from a fixed 1-hour window,
            # .. independent of whatever chart range the user picked ..
            now = datetime.now(timezone.utc)
            hour_ago = now - timedelta(hours=1)
            hour_since_iso = hour_ago.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            hour_until_iso = now.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            hour_buckets = scheduler.get_chart_data(hour_since_iso, hour_until_iso)

            runs_last_hour = 0
            recent_last_hour = 0
            for bucket in hour_buckets['buckets']:
                runs_last_hour += bucket['ok'] + bucket['error'] + bucket['timeout']
                recent_last_hour += bucket['error'] + bucket['timeout']

            self.response.payload = {
                'total_jobs': total_jobs,
                'active_jobs': active_jobs,
                'paused_jobs': paused_jobs,
                'total_executions': total_executions,
                'outcome_counts': outcome_counts,
                'jobs': jobs,
                'chart_buckets': chart_buckets,
                'recent_events': recent_events,
                'runs_last_hour': runs_last_hour,
                'recent_last_hour': recent_last_hour,
            }

        except Exception:
            self.logger.error('Could not get current state, e:`%s`', format_exc())
            raise

# ################################################################################################################################
# ################################################################################################################################
