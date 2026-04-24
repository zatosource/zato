# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from traceback import format_exc

# ciso8601
try:
    from zato.common.util.api import parse_datetime
except ImportError:
    from dateutil.parser import parse as parse_datetime

# Zato
from zato.common.api import scheduler_date_time_format, SCHEDULER, ZATO_NONE
from zato.common.defaults import default_cluster_id
from zato.common.broker_message import SCHEDULER as SCHEDULER_MSG
from zato.common.exception import ServiceMissingException, ZatoException
from zato.common.odb.model import Job
from zato.common.util.sql import elems_with_opaque, parse_instance_opaque_attr, set_instance_opaque_attrs
from zato.server.service import Int, Bool
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

_service_name_prefix = 'zato.scheduler.job.'
_entity_type = 'scheduler'
_ib_params = ('weeks', 'days', 'hours', 'minutes', 'seconds')
_new_params = ('jitter_ms', 'timezone', 'calendar', 'on_missed', 'max_execution_time_ms')
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

class _SchedulerAdmin(AdminService):

    def _service_by_name(self, service_name):
        return service_name in self.server.service_store.name_to_impl_name

    def _enrich_job(self, item):
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
    """Creating and updating a job using Rust config store."""
    input = self.request.input
    input.cluster_id = default_cluster_id

    job_type = input.job_type
    name = input.name
    service_name = input.service
    logger = self.logger
    cid = self.cid

    if job_type not in (SCHEDULER.JOB_TYPE.ONE_TIME, SCHEDULER.JOB_TYPE.INTERVAL_BASED):
        msg = f'Unrecognized job type [{job_type}]'
        logger.error(msg)
        raise ZatoException(cid, msg)

    jobs = store.get_list(_entity_type)

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
        old_name = old['name']
        data = dict(old)
    else:
        old_name = None
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
            if value == ZATO_NONE:
                value = None
            if value is None:
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

            set_instance_opaque_attrs(job_row, input, only=list(_new_params))
            session.add(job_row)
            session.commit()

            data['id'] = job_row.id
            job_id = job_row.id

        from zato_scheduler_core import scheduler_create_job, scheduler_edit_job
        if action == 'create':
            scheduler_create_job(job_id, data)
        else:
            scheduler_edit_job(job_id, data)

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
        '-id', '-extra', '-weeks', '-days', '-hours', '-minutes', '-seconds', '-repeats', \
        '-cron_definition', '-should_ignore_existing', \
        '-jitter_ms', '-timezone', '-calendar', '-on_missed', '-max_execution_time_ms'
    output = '-id', '-name', '-cron_definition'

    def handle(self):
        _create_edit(self, self.__class__.__name__.lower())

# ################################################################################################################################
# ################################################################################################################################

class _Get(_SchedulerAdmin):
    output = 'id', 'name', 'is_active', 'job_type', 'start_date', 'service_id', 'service_name', \
        '-extra', '-weeks', '-days', '-hours', '-minutes', '-seconds', '-repeats', '-cron_definition', \
        '-jitter_ms', '-timezone', '-calendar', '-on_missed', '-max_execution_time_ms'

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
        from zato_scheduler_core import scheduler_get_history_page

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
            raise ZatoException(self.cid, 'Job not found')

        #  Build recent_outcomes, last_outcome and last_duration_ms
        #  from the last 10 history records in Rust ..
        last_outcome = None
        last_duration_ms = None
        recent_outcomes = [] # type: list

        result = scheduler_get_history_page(job_id, 0, 10, SCHEDULER.OUTCOME.All)
        records = result['records']

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
                session.query(IntervalBasedJob).filter_by(job_id=job_row.id).delete()
                session.delete(job_row)
                session.commit()

            from zato_scheduler_core import scheduler_delete_job
            scheduler_delete_job(job_id)
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

            from zato_scheduler_core import scheduler_execute_job
            scheduler_execute_job(job_row.id)
        except Exception:
            self.logger.error('Could not execute the job, e:`%s`', format_exc())
            raise

# ################################################################################################################################
# ################################################################################################################################

class GetHistory(_SchedulerAdmin):
    """ Returns paginated execution history for a scheduler job.
    """
    name = _service_name_prefix + 'get-history'

    input = Int('id'), Int('-page'), Int('-page_size'), '-since_ts', '-outcomes', '-running_runs'

    def handle(self) -> 'None':
        try:
            from zato_scheduler_core import scheduler_get_history_page, scheduler_get_history_since

            job_id = self.request.input.id
            since_ts = self.request.input.get('since_ts')
            outcomes_raw = self.request.input.get('outcomes')
            if outcomes_raw is None:
                outcomes = SCHEDULER.OUTCOME.All
            else:
                outcomes = json.loads(outcomes_raw)

            from contextlib import closing
            with closing(self.odb.session()) as session:
                job_row = session.query(Job).filter_by(id=job_id).one()
            job_name = job_row.name

            if since_ts:
                running_runs_raw = self.request.input.get('running_runs')
                running_runs = json.loads(running_runs_raw) if running_runs_raw else []
                records = scheduler_get_history_since(job_id, since_ts, outcomes, running_runs)
                rows = []
                for rec in records:
                    rec['job_id'] = job_id
                    rec['job_name'] = job_name
                    rows.append(rec)
                count_result = scheduler_get_history_page(job_id, 0, 0, outcomes)
                self.response.payload = {'rows': rows, 'total': count_result['total']}
            else:
                page = self.request.input.get('page')
                if page is None:
                    page = default_page

                page_size = self.request.input.get('page_size')
                if page_size is None:
                    page_size = default_page_size
                offset = (page - 1) * page_size

                result = scheduler_get_history_page(job_id, offset, page_size, outcomes)
                rows = []
                for rec in result['records']:
                    rec['job_id'] = job_id
                    rec['job_name'] = job_name
                    rows.append(rec)

                self.response.payload = {
                    'rows': rows,
                    'total': result['total'],
                    'page': page,
                    'page_size': page_size,
                }

        except Exception:
            self.logger.error('Could not get job history, e:`%s`', format_exc())
            raise

# ################################################################################################################################
# ################################################################################################################################

class GetAllHistory(_SchedulerAdmin):
    """ Returns execution history for all scheduler jobs.
    """
    name = _service_name_prefix + 'get-all-history'

    def handle(self):
        try:
            from zato_scheduler_core import scheduler_get_all_history
            self.response.payload = scheduler_get_all_history()
        except Exception:
            self.logger.error('Could not get all job history, e:`%s`', format_exc())
            raise

# ################################################################################################################################
# ################################################################################################################################

_cal_entity_type = 'holiday_calendar'
_cal_service_prefix = 'zato.scheduler.holiday-calendar.'

class _HolidayCalendarAdmin(AdminService):
    pass

# ################################################################################################################################

class HolidayCalendarGetList(_HolidayCalendarAdmin):
    """ Returns a list of all holiday calendars.
    """
    name = _cal_service_prefix + 'get-list'

    input = Int('-cur_page'), Bool('-paginate'), '-query'
    output = 'id', 'name', '-description'

    def handle(self):
        items = []
        self.response.payload = items

# ################################################################################################################################

class HolidayCalendarGetByID(_HolidayCalendarAdmin):
    """ Returns a holiday calendar by its ID.
    """
    name = _cal_service_prefix + 'get-by-id'

    input = 'id',
    output = 'id', 'name', '-description', '-dates', '-weekdays'

    def handle(self):
        raise ZatoException(self.cid, 'Holiday calendars are not yet supported in ODB')

# ################################################################################################################################

class HolidayCalendarCreate(_HolidayCalendarAdmin):
    """ Creates a new holiday calendar.
    """
    name = _cal_service_prefix + 'create'

    input = 'name', '-description', '-dates', '-weekdays'
    output = 'id', 'name'

    def handle(self):
        raise ZatoException(self.cid, 'Holiday calendars are not yet supported in ODB')

# ################################################################################################################################

class HolidayCalendarEdit(_HolidayCalendarAdmin):
    """ Updates a holiday calendar.
    """
    name = _cal_service_prefix + 'edit'

    input = 'id', 'name', '-description', '-dates', '-weekdays'
    output = 'id', 'name'

    def handle(self):
        raise ZatoException(self.cid, 'Holiday calendars are not yet supported in ODB')

# ################################################################################################################################

class HolidayCalendarDelete(_HolidayCalendarAdmin):
    """ Deletes a holiday calendar.
    """
    name = _cal_service_prefix + 'delete'

    input = 'id',

    def handle(self):
        raise ZatoException(self.cid, 'Holiday calendars are not yet supported in ODB')

# ################################################################################################################################
# ################################################################################################################################

class GetCurrentState(_SchedulerAdmin):
    """ Returns the current state of all scheduler jobs and their execution history.
    """
    name = _service_name_prefix + 'get-current-state'

    def handle(self):
        try:
            from zato_scheduler_core import scheduler_get_all_history, scheduler_get_job_summaries

            from contextlib import closing
            from zato.common.odb.model import Job, IntervalBasedJob
            with closing(self.odb.session()) as session:
                job_rows = session.query(Job).filter_by(cluster_id=default_cluster_id).all()
                store_jobs = []
                for job in job_rows:
                    d = {'id': job.id, 'name': job.name, 'is_active': job.is_active, 'job_type': job.job_type,
                         'service': job.service.name}
                    store_jobs.append(d)

            runtime_by_id = {}
            runtime_by_name = {}
            for s in scheduler_get_job_summaries():
                runtime_by_id[s['id']] = s
                runtime_by_name[s['name']] = s

            all_history = scheduler_get_all_history()

            history_by_name = {}
            for summary in runtime_by_name.values():
                summary_id = summary['id']
                if summary_id in all_history:
                    history_by_name[summary['name']] = all_history[summary_id]

            total_jobs = len(store_jobs)
            active_jobs = 0
            paused_jobs = 0

            jobs = []

            for item in store_jobs:
                job_id = item['id']
                is_active = item['is_active']
                job_type = item['job_type']
                service = item['service']
                name = item['name']

                if is_active:
                    active_jobs += 1
                else:
                    paused_jobs += 1

                runtime = runtime_by_id.get(job_id)
                if runtime is None:
                    runtime = runtime_by_name.get(name)

                history = all_history.get(job_id)
                if history is None:
                    history = history_by_name.get(name)

                if runtime is not None:
                    is_running = runtime['in_flight']
                    next_fire_utc = runtime['next_fire_utc']
                    current_run = runtime['current_run']
                    interval_ms = runtime['interval_ms']
                else:
                    is_running = False
                    next_fire_utc = None
                    current_run = 0
                    interval_ms = 0

                last_outcome = None
                last_duration_ms = None
                recent_outcomes = []

                if history:
                    last_record = history[-1]
                    last_outcome = last_record['outcome']

                    # .. walk backwards to find the most recent completed record's duration ..
                    for idx in range(len(history) - 1, -1, -1):
                        rec_duration = history[idx]['duration_ms']
                        if rec_duration is not None:
                            last_duration_ms = rec_duration
                            break

                    start_idx = max(0, len(history) - 10)
                    for rec in history[start_idx:]:
                        recent_outcomes.append(rec['outcome'])

                jobs.append({
                    'id': job_id,
                    'name': name,
                    'is_active': is_active,
                    'job_type': job_type,
                    'service': service,
                    'next_fire_utc': next_fire_utc,
                    'is_running': is_running,
                    'current_run': current_run,
                    'interval_ms': interval_ms,
                    'last_outcome': last_outcome,
                    'last_duration_ms': last_duration_ms,
                    'recent_outcomes': recent_outcomes,
                })

            outcome_counts = {
                'ok': 0,
                'error': 0,
                'timeout': 0,
                'running': 0,
                'skipped_already_in_flight': 0,
                'skipped_holiday': 0,
                'missed_catchup': 0,
            }
            history_timeline = []
            total_executions = 0

            execution_outcomes = {'ok', 'error', 'timeout'}

            for job_id, records in all_history.items():
                job_name = ''
                for item in store_jobs:
                    if item['id'] == job_id:
                        job_name = item['name']
                        break
                if not job_name:
                    summary = runtime_by_id.get(job_id)
                    if summary is not None:
                        job_name = summary['name']

                for rec in records:
                    outcome = rec['outcome']
                    outcome_counts[outcome] += 1
                    if outcome in execution_outcomes:
                        total_executions += 1
                    entry = dict(rec)
                    entry['job_id'] = job_id
                    entry['job_name'] = job_name
                    history_timeline.append(entry)

            history_timeline.sort(key=lambda x: x['actual_fire_time_iso'], reverse=True)

            self.response.payload = {
                'total_jobs': total_jobs,
                'active_jobs': active_jobs,
                'paused_jobs': paused_jobs,
                'total_executions': total_executions,
                'outcome_counts': outcome_counts,
                'jobs': jobs,
                'history_timeline': history_timeline,
            }

        except Exception:
            self.logger.error('Could not get current state, e:`%s`', format_exc())
            raise

# ################################################################################################################################
# ################################################################################################################################
