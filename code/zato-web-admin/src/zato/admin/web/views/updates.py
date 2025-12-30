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
    result = updater.download_and_install(exclude_from_restart=['dashboard'])
    return json_response(result, success=result['success'])

# ################################################################################################################################
# ################################################################################################################################

def restart_component(req, component_name, component_path, port=0):
    logger.info('restart_{}: called from client: {}'.format(component_name, req.META.get('REMOTE_ADDR')))
    result = updater.restart_component(component_name, component_path, port)
    return json_response(result, success=result['success'])

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def restart_scheduler(req):
    return restart_component(req, 'scheduler', updater.get_component_path('scheduler'), updater.get_component_port('scheduler'))

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def restart_server(req):
    return restart_component(req, 'server', updater.get_component_path('server'), updater.get_component_port('server'))

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def restart_proxy(req):
    return restart_component(req, 'proxy', updater.get_component_path('proxy'), updater.get_component_port('proxy'))

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def restart_dashboard(req):
    import subprocess
    import threading
    import os
    
    logger.info('restart_dashboard: called from client: {}'.format(req.META.get('REMOTE_ADDR')))
    
    def restart_after_delay():
        import time
        time.sleep(1)
        
        logger.info('')
        logger.info('#' * 80)
        logger.info('##' + ' ' * 76 + '##')
        logger.info('##' + ' ' * 21 + 'UPDATE COMPLETED' + ' ' * 39 + '##')
        logger.info('##' + ' ' * 76 + '##')
        logger.info('#' * 80)
        logger.info('')
        
        logger.info('restart_dashboard: executing make restart-dashboard')
        try:
            makefile_dir = os.path.expanduser('~/projects/zatosource-zato/4.1')
            logger.info('restart_dashboard: makefile_dir={}'.format(makefile_dir))
            result = subprocess.run(
                ['make', 'restart-dashboard'],
                cwd=makefile_dir,
                capture_output=True,
                text=True
            )
            logger.info('restart_dashboard: returncode={}'.format(result.returncode))
            logger.info('restart_dashboard: stdout={}'.format(result.stdout))
            if result.stderr:
                logger.error('restart_dashboard: stderr={}'.format(result.stderr))
        except Exception as e:
            logger.error('restart_dashboard: failed to execute make: {}'.format(e))
    
    thread = threading.Thread(target=restart_after_delay, daemon=True)
    thread.start()
    
    result = {
        'success': True,
        'message': 'Dashboard restarting'
    }
    return json_response(result, success=True)

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
