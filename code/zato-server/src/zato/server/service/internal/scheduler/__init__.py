# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc

# ciso8601
try:
    from zato.common.util.api import parse_datetime
except ImportError:
    from dateutil.parser import parse as parse_datetime

# Zato
from zato.common.api import scheduler_date_time_format, SCHEDULER, ZATO_NONE
from zato.common.broker_message import SCHEDULER as SCHEDULER_MSG
from zato.common.exception import ServiceMissingException, ZatoException
from zato.server.service import Int, Bool
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

_service_name_prefix = 'zato.scheduler.job.'
_entity_type = 'scheduler'
_ib_params = ('weeks', 'days', 'hours', 'minutes', 'seconds')
_new_params = ('jitter_ms', 'timezone', 'calendar', 'on_missed', 'max_execution_time_ms')

# ################################################################################################################################
# ################################################################################################################################

def _item_by_id(items, id_):
    sid = str(id_)
    for item in items:
        if str(item.get('id')) == sid:
            return item
    return None

# ################################################################################################################################
# ################################################################################################################################

class _SchedulerAdmin(AdminService):

    def _service_by_name(self, service_name):
        return service_name in self.server.service_store.name_to_impl_name

    def _enrich_job(self, item):
        out = dict(item)
        service_name = item.get('service')
        if self._service_by_name(service_name):
            out['service_id'] = self.server.service_store.get_service_id_by_name(service_name)
            out['service_name'] = service_name

        else:
            out['service_id'] = None
            out['service_name'] = service_name
        return out

# ################################################################################################################################
# ################################################################################################################################

def _create_edit(self, action):
    """Creating and updating a job using Rust config store."""
    input = self.request.input
    input.cluster_id = input.get('cluster_id') or self.server.cluster_id

    job_type = input.job_type
    name = input.name
    service_name = input.service
    logger = self.logger
    cid = self.cid

    if job_type not in (SCHEDULER.JOB_TYPE.ONE_TIME, SCHEDULER.JOB_TYPE.INTERVAL_BASED):
        msg = 'Unrecognized job type [{}]'.format(job_type)
        logger.error(msg)
        raise ZatoException(cid, msg)

    jobs = store.get_list(_entity_type)

    def _other_same_name(jid):
        for j in jobs:
            if j.get('name') == name and str(j.get('id')) != str(jid):
                return j
        return None

    if action == 'create':
        existing_one = _other_same_name(None)
    else:
        existing_one = _other_same_name(input.id)

    if existing_one:
        if input.get('should_ignore_existing'):
            return
        raise ZatoException(cid, 'Job `{}` already exists on this cluster'.format(name))

    if not self._service_by_name(service_name):
        msg = 'Service `{}` does not exist in this cluster'.format(service_name)
        logger.info(msg)
        raise ServiceMissingException(cid, msg)

    extra = (input.extra or u'').encode('utf-8')
    extra_str = extra.decode('utf8')
    is_active = input.is_active
    start_date = parse_datetime(input.start_date)
    start_iso = start_date.isoformat()

    if action == 'edit':
        old = _item_by_id(jobs, input.id)
        if not old:
            raise ZatoException(cid, 'Job `{}` not found'.format(input.id))
        old_name = old.get('name')
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
        'extra': extra_str or None,
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
            data[param] = int(value) if value else 0
    else:
        for param in _ib_params + ('repeats',):
            data[param] = None

    try:
        with closing(self.odb.session()) as session:
            service_row = session.query(ServiceModel).filter_by(name=service_name, cluster_id=input.cluster_id).first()
            if not service_row:
                raise ZatoException(cid, 'Service `{}` not found in ODB'.format(service_name))

            if action == 'edit':
                job_row = session.query(Job).filter_by(id=input.id).first()
                if not job_row:
                    raise ZatoException(cid, 'Job `{}` not found'.format(input.id))
                job_row.name = name
                job_row.is_active = is_active
                job_row.job_type = job_type
                job_row.start_date = start_date
                job_row.service = service_row
                job_row.extra = extra_str or None
            else:
                cluster_row = session.query(Cluster).filter_by(id=input.cluster_id).first()
                job_row = Job()
                job_row.name = name
                job_row.is_active = is_active
                job_row.job_type = job_type
                job_row.start_date = start_date
                job_row.service = service_row
                job_row.cluster = cluster_row
                job_row.extra = extra_str or None
                session.add(job_row)
                session.flush()

            if job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED:
                ib = session.query(IntervalBasedJob).filter_by(job_id=job_row.id).first()
                if not ib:
                    ib = IntervalBasedJob()
                    ib.job = job_row
                    session.add(ib)
                for param in _ib_params:
                    setattr(ib, param, data.get(param) or 0)
                ib.repeats = data.get('repeats')

            session.commit()

            data['id'] = job_row.id
            job_id = str(job_row.id)

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

    input = '-cluster_id', Int('-cur_page'), Bool('-paginate'), '-query', '-service_name'

    def handle(self):
        input = self.request.input
        input.cluster_id = input.get('cluster_id') or self.server.cluster_id
        from contextlib import closing
        from zato.common.odb.model import Job, IntervalBasedJob
        with closing(self.odb.session()) as session:
            job_rows = session.query(Job).filter_by(cluster_id=input.cluster_id).all()
            items = []
            for j in job_rows:
                d = {'id': j.id, 'name': j.name, 'is_active': j.is_active, 'job_type': j.job_type,
                     'start_date': j.start_date.isoformat() if j.start_date else '', 'service': j.service.name if j.service else '',
                     'extra': j.extra or ''}
                ib = session.query(IntervalBasedJob).filter_by(job_id=j.id).first()
                if ib:
                    for p in _ib_params:
                        d[p] = getattr(ib, p, 0) or 0
                    d['repeats'] = ib.repeats
                items.append(self._enrich_job(d))
        if input.get('service_name'):
            items = [x for x in items if x.get('service_name') == input.service_name or x.get('service') == input.service_name]
        self.response.payload = items

# ################################################################################################################################
# ################################################################################################################################

class GetByID(_Get):
    """ Returns a job by its ID.
    """
    name = _service_name_prefix + 'get-by-id'

    input = 'cluster_id', 'id'

    def handle(self):
        from contextlib import closing
        from zato.common.odb.model import Job, IntervalBasedJob
        item = None
        with closing(self.odb.session()) as session:
            j = session.query(Job).filter_by(id=self.request.input.id).first()
            if j:
                item = {'id': j.id, 'name': j.name, 'is_active': j.is_active, 'job_type': j.job_type,
                        'start_date': j.start_date.isoformat() if j.start_date else '', 'service': j.service.name if j.service else '',
                        'extra': j.extra or ''}
                ib = session.query(IntervalBasedJob).filter_by(job_id=j.id).first()
                if ib:
                    for p in _ib_params:
                        item[p] = getattr(ib, p, 0) or 0
                    item['repeats'] = ib.repeats
        if not item:
            raise ZatoException(self.cid, 'Job not found')
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
            j = session.query(Job).filter_by(name=self.request.input.name, cluster_id=self.server.cluster_id).first()
            if j:
                item = {'id': j.id, 'name': j.name, 'is_active': j.is_active, 'job_type': j.job_type,
                        'start_date': j.start_date.isoformat() if j.start_date else '', 'service': j.service.name if j.service else '',
                        'extra': j.extra or ''}
                ib = session.query(IntervalBasedJob).filter_by(job_id=j.id).first()
                if ib:
                    for p in _ib_params:
                        item[p] = getattr(ib, p, 0) or 0
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

                job_id = str(job_row.id)
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

    input = 'id',

    def handle(self):
        try:
            from contextlib import closing
            from zato.common.odb.model import Job
            with closing(self.odb.session()) as session:
                job_row = session.query(Job).filter_by(id=self.request.input.id).first()
            item = {'id': job_row.id, 'name': job_row.name} if job_row else None
            if not item:
                raise ZatoException(self.cid, 'Job not found')

            job_id = str(item['id'])

            from zato_scheduler_core import scheduler_execute_job
            scheduler_execute_job(job_id)
        except Exception:
            self.logger.error('Could not execute the job, e:`%s`', format_exc())
            raise

# ################################################################################################################################
# ################################################################################################################################

class GetHistory(_SchedulerAdmin):
    """ Returns execution history for a scheduler job.
    """
    name = _service_name_prefix + 'get-history'

    input = 'id',

    def handle(self):
        try:
            from zato_scheduler_core import scheduler_get_history
            job_id = str(self.request.input.id)
            self.response.payload = scheduler_get_history(job_id)
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
                job_rows = session.query(Job).filter_by(cluster_id=self.server.cluster_id).all()
                store_jobs = []
                for j in job_rows:
                    d = {'id': str(j.id), 'name': j.name, 'is_active': j.is_active, 'job_type': j.job_type,
                         'service': j.service.name if j.service else ''}
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
                job_id = str(item.get('id', ''))
                is_active = item.get('is_active', False)
                job_type = item.get('job_type', '')
                service = item.get('service') or item.get('service_name') or ''
                name = item.get('name', '')

                if is_active:
                    active_jobs += 1
                else:
                    paused_jobs += 1

                runtime = runtime_by_id.get(job_id) or runtime_by_name.get(name, {})
                is_running = runtime.get('in_flight', False)

                history = all_history.get(job_id, []) or history_by_name.get(name, [])

                last_outcome = None
                last_duration_ms = None
                recent_outcomes = []

                if history:
                    last_record = history[-1]
                    last_outcome = last_record.get('outcome')
                    last_duration_ms = last_record.get('duration_ms')

                    start_idx = max(0, len(history) - 10)
                    for rec in history[start_idx:]:
                        recent_outcomes.append(rec.get('outcome', ''))

                jobs.append({
                    'id': job_id,
                    'name': name,
                    'is_active': is_active,
                    'job_type': job_type,
                    'service': service,
                    'next_fire_utc': runtime.get('next_fire_utc'),
                    'is_running': is_running,
                    'current_run': runtime.get('current_run', 0),
                    'interval_ms': runtime.get('interval_ms', 0),
                    'last_outcome': last_outcome,
                    'last_duration_ms': last_duration_ms,
                    'recent_outcomes': recent_outcomes,
                })

            outcome_counts = {}
            history_timeline = []
            total_executions = 0

            # A history record represents an "execution" (as opposed to a
            # scheduler-internal skip) when its outcome is one of these.
            # Rust sets outcome = "ok" on dispatch and updates it to
            # "error"/"timeout" on completion if it failed.
            execution_outcomes = {'ok', 'error', 'timeout'}

            for job_id, records in all_history.items():
                job_name = ''
                for item in store_jobs:
                    if str(item.get('id', '')) == job_id:
                        job_name = item.get('name', '')
                        break
                if not job_name:
                    summary = runtime_by_id.get(job_id, {})
                    job_name = summary.get('name', '')

                for rec in records:
                    outcome = rec.get('outcome', '')
                    outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

                    if outcome in execution_outcomes:
                        total_executions += 1

                    entry = dict(rec)
                    entry['job_id'] = job_id
                    entry['job_name'] = job_name
                    history_timeline.append(entry)

            history_timeline.sort(key=lambda x: x.get('actual_fire_time_iso', ''), reverse=True)

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
