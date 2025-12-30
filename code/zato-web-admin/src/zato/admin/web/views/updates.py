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
from zato.common.json_internal import dumps
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

def json_response(data, success=True):
    from django.http.response import HttpResponseServerError
    response_json = dumps(data)
    response_class = HttpResponse if success else HttpResponseServerError
    return response_class(response_json, content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def download_and_install(req):
    logger.info('download_and_install: called from client: {}'.format(req.META.get('REMOTE_ADDR')))
    result = updater.download_and_install()
    return json_response(result, success=result['success'])

# ################################################################################################################################
# ################################################################################################################################

def restart_component(req, component_name):
    logger.info('restart_{}: called from client: {}'.format(component_name, req.META.get('REMOTE_ADDR')))
    zato_binary = updater.find_file_in_parents(updater_config.zato_path)

    if not zato_binary:
        result = {
            'success': False,
            'error': f'{updater_config.zato_path} not found in parent directories'
        }
        return json_response(result, success=False)

    result = updater.run_command(
        command=[zato_binary, '--version'],
        cwd=current_dir,
        log_prefix=f'restart_{component_name}'
    )
    return json_response(result, success=result['success'])

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def restart_scheduler(req):
    return restart_component(req, 'scheduler')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def restart_server(req):
    return restart_component(req, 'server')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def restart_proxy(req):
    return restart_component(req, 'proxy')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def restart_dashboard(req):
    return restart_component(req, 'dashboard')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def save_schedule(req):
    from zato.common.json_internal import loads
    body = req.body.decode('utf-8')
    schedule_data = loads(body)
    result = updater.save_schedule(schedule_data)
    return json_response(result, success=result['success'])

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def load_schedule(req):
    result = updater.load_schedule()
    return json_response(result, success=result['success'])

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def delete_schedule(req):
    result = updater.delete_schedule()
    return json_response(result, success=result['success'])

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req):
    return TemplateResponse(req, 'zato/in-app-updates/index.html', {
        'current_version': updater.get_zato_version(),
        'audit_log': updater.get_audit_log_entries(5)
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_latest_audit_entry(req):
    entries = updater.get_audit_log_entries(1)
    if entries:
        return json_response({'success': True, 'entry': entries[0]})
    else:
        return json_response({'success': True, 'entry': None})

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_audit_log_refresh(req):
    entries = updater.get_audit_log_entries(5)
    return json_response({'success': True, 'entries': entries})

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
    lorem_ipsum = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""

    response = HttpResponse(lorem_ipsum, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="update.log"'
    return response

# ################################################################################################################################
# ################################################################################################################################
