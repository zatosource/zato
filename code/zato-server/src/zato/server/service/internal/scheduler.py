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
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

_service_name_prefix = 'zato.scheduler.job.'
_entity_type = 'scheduler'
_ib_params = ('weeks', 'days', 'hours', 'minutes', 'seconds')

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
        for s in self.server.config_store.get_list('service'):
            if s.get('name') == service_name:
                return s
        return None

    def _enrich_job(self, item):
        out = dict(item)
        svc = self._service_by_name(item.get('service'))
        if svc:
            out['service_id'] = svc.get('id')
            out['service_name'] = svc.get('name')
        else:
            out['service_id'] = None
            out['service_name'] = item.get('service')
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
    store = self.server.config_store

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
        msg = 'ODBService `{}` does not exist in this cluster'.format(service_name)
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
        if action == 'edit' and old_name and old_name != name:
            store.delete(_entity_type, old_name)
        store.set(_entity_type, name, data)
        saved = store.get(_entity_type, name) or data
        self.response.payload.id = saved.get('id')
        self.response.payload.name = input.name
    except Exception:
        logger.error('Could not complete the request, e:`%s`', format_exc())
        raise

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(_SchedulerAdmin):
    """ A base class for both creating and editing scheduler jobs.
    """
    class SimpleIO(AdminSIO):
        input_required = 'cluster_id', 'name', 'is_active', 'job_type', 'service', 'start_date'
        input_optional = 'id', 'extra', 'weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats', \
            'cron_definition', 'should_ignore_existing'
        output_optional = 'id', 'name', 'cron_definition'
        default_value = ''

    def handle(self):
        _create_edit(self, self.__class__.__name__.lower())

# ################################################################################################################################
# ################################################################################################################################

class _Get(_SchedulerAdmin):
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id',)
        output_required = 'id', 'name', 'is_active', 'job_type', 'start_date', 'service_id', 'service_name'
        output_optional = 'extra', 'weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats', 'cron_definition'
        output_repeated = True
        default_value = ''
        date_time_format = scheduler_date_time_format

# ################################################################################################################################
# ################################################################################################################################

class GetList(_Get):
    """ Returns a list of all jobs defined in the scheduler.
    """
    name = _service_name_prefix + 'get-list'

    class SimpleIO(_Get.SimpleIO):
        input_optional = GetListAdminSIO.input_optional + ('service_name',)

    def handle(self):
        input = self.request.input
        input.cluster_id = input.get('cluster_id') or self.server.cluster_id
        items = [self._enrich_job(dict(x)) for x in self.server.config_store.get_list(_entity_type)]
        if input.get('service_name'):
            items = [x for x in items if x.get('service_name') == input.service_name or x.get('service') == input.service_name]
        self.response.payload[:] = items

# ################################################################################################################################
# ################################################################################################################################

class GetByID(_Get):
    """ Returns a job by its ID.
    """
    name = _service_name_prefix + 'get-by-id'

    class SimpleIO(_Get.SimpleIO):
        request_elem = 'zato_scheduler_job_get_by_id_request'
        response_elem = None
        input_required = _Get.SimpleIO.input_required + ('id',)
        output_repeated = False

    def handle(self):
        item = _item_by_id(self.server.config_store.get_list(_entity_type), self.request.input.id)
        if not item:
            raise ZatoException(self.cid, 'Job not found')
        self.response.payload = self._enrich_job(item)

# ################################################################################################################################
# ################################################################################################################################

class GetByName(_Get):
    """ Returns a job by its name.
    """
    name = _service_name_prefix + 'get-by-name'

    class SimpleIO(_Get.SimpleIO):
        request_elem = 'zato_scheduler_job_get_by_name_request'
        response_elem = None
        input_required = _Get.SimpleIO.input_required + ('name',)
        output_repeated = False

    def handle(self):
        item = self.server.config_store.get(_entity_type, self.request.input.name)
        if not item:
            raise ZatoException(self.cid, 'Job not found')
        self.response.payload = self._enrich_job(item)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    """ Creates a new scheduler's job.
    """
    name = _service_name_prefix + 'create'

    class SimpleIO(_CreateEdit.SimpleIO):
        request_elem = 'zato_scheduler_job_create_request'
        response_elem = 'zato_scheduler_job_create_response'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    """ Updates a scheduler's job.
    """
    name = _service_name_prefix + 'edit'

    class SimpleIO(_CreateEdit.SimpleIO):
        request_elem = 'zato_scheduler_job_edit_request'
        response_elem = 'zato_scheduler_job_edit_response'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_SchedulerAdmin):
    """ Deletes a scheduler's job.
    """
    name = _service_name_prefix + 'delete'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_scheduler_job_delete_request'
        response_elem = 'zato_scheduler_job_delete_response'
        input_required = ('id',)

    def handle(self):
        store = self.server.config_store
        try:
            item = _item_by_id(store.get_list(_entity_type), self.request.input.id)
            if not item:
                raise ZatoException(self.cid, 'Job not found')
            store.delete(_entity_type, item['name'])
        except Exception:
            self.logger.error('Could not delete the job, e:`%s`', format_exc())
            raise

# ################################################################################################################################
# ################################################################################################################################

class Execute(_SchedulerAdmin):
    """ Executes a scheduler's job.
    """
    name = _service_name_prefix + 'execute'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_scheduler_job_execute_request'
        response_elem = 'zato_scheduler_job_execute_response'
        input_required = ('id',)

    def handle(self):
        try:
            item = _item_by_id(self.server.config_store.get_list(_entity_type), self.request.input.id)
            if not item:
                raise ZatoException(self.cid, 'Job not found')
            msg = {'action': SCHEDULER_MSG.EXECUTE.value, 'name': item['name']}
            self.broker_client.publish(msg, routing_key='scheduler')
        except Exception:
            self.logger.error('Could not execute the job, e:`%s`', format_exc())
            raise

# ################################################################################################################################
