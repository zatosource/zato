# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.settings.base import SettingsBaseView
from zato.admin.web.views.settings.config import updates_page_config
from zato.admin.web.views.settings.handlers import ScheduleHandler, AuditLogHandler
from zato.admin.web.views.settings.utils import json_response
from zato.common.util.updates import Updater, UpdaterConfig

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

current_dir = os.path.dirname(os.path.abspath(__file__))

updater_config = UpdaterConfig(current_dir=current_dir)
updater = Updater(updater_config)

# ################################################################################################################################
# ################################################################################################################################

class UpdatesView(SettingsBaseView):

    def __init__(self):
        super().__init__(updates_page_config, updater, 'zato/updates/index.html')
        self.schedule_handler = ScheduleHandler(updater)
        self.audit_log_handler = AuditLogHandler(updater)

    def get_index_context(self):
        context = super().get_index_context()
        context['current_version'] = updater.get_zato_version()
        context['audit_log'] = updater.get_audit_log_entries(3)
        return context

    @method_allowed('POST')
    def save_schedule(self, req):
        return self.schedule_handler.save(req)

    @method_allowed('GET')
    def load_schedule(self, req):
        return self.schedule_handler.load(req)

    @method_allowed('POST')
    def delete_schedule(self, req):
        return self.schedule_handler.delete(req)

    @method_allowed('GET')
    def get_latest_audit_entry(self, req):
        return self.audit_log_handler.get_latest_entry(req)

    @method_allowed('GET')
    def get_audit_log_refresh(self, req):
        return self.audit_log_handler.get_refresh(req)

updates_view = UpdatesView()

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def check_availability(req):
    try:
        result = updater.check_latest_version()

        if not result['success']:
            return json_response({'updates_available': False})

        current_version = updater.get_zato_version()
        latest_version = result.get('version', '')

        updates_available = current_version != latest_version

        return json_response({
            'updates_available': updates_available,
            'current_version': current_version,
            'latest_version': latest_version
        })
    except Exception as e:
        logger.error('check_availability: exception: {}'.format(e))
        return json_response({'updates_available': False})

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def download_and_install(req):
    logger.info('download_and_install: called from client: {}'.format(req.META.get('REMOTE_ADDR')))
    result = updater.download_and_install(exclude_from_restart=['dashboard'])

    if result['success']:
        import redis
        try:
            r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            version_from = result.get('version_from', '')
            version_to = result.get('version_to', '')
            _ = r.set('zato:update:version_from', version_from)
            _ = r.set('zato:update:version_to', version_to)
            _ = r.set('zato:update:schedule', 'manual')
        except Exception:
            pass

    return json_response(result, success=result['success'])

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def check_latest_version(req):
    result = updater.check_latest_version()
    return json_response(result, success=result['success'])

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def download_logs(req):
    import os
    from django.http import FileResponse, HttpResponse

    base_dir = os.path.expanduser('~/env/qs-1')
    update_log_path = os.path.join(base_dir, 'server1', 'logs', 'update.log')

    if not os.path.exists(update_log_path):
        return HttpResponse('Update log file not found', status=404)

    try:
        response = FileResponse(open(update_log_path, 'rb'), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="update.log"'
        return response
    except Exception as e:
        logger.error('download_logs: failed to read update.log: {}'.format(e))
        return HttpResponse('Error reading update log: {}'.format(e), status=500)

# ################################################################################################################################
# ################################################################################################################################
