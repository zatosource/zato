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
from zato.admin.web.views.settings_config import grafana_cloud_page_config
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
        import redis
        import requests
        from logging import getLogger
        time.sleep(1)

        try:
            r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            version_from = r.get('zato:update:version_from') or ''
            version_to = r.get('zato:update:version_to') or ''
            schedule = r.get('zato:update:schedule') or 'manual'
            if version_from and version_to:
                url = f'https://zato.io/support/updates/info-4.1.json?from={version_from}&to={version_to}&mode=manual&schedule={schedule}'
                _ = requests.get(url, timeout=2)
        except Exception:
            pass

        update_logger = getLogger('zato.common.util.updates')

        update_logger.info('')
        update_logger.info('#' * 80)
        update_logger.info('##' + ' ' * 76 + '##')
        update_logger.info('##' + ' ' * 21 + 'UPDATE COMPLETED' + ' ' * 39 + '##')
        update_logger.info('##' + ' ' * 76 + '##')
        update_logger.info('#' * 80)
        update_logger.info('')

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
def test_connection(req):
    from traceback import format_exc
    from zato.common.json_internal import loads
    from zato.common.monitoring.grafana_cloud.auto_setup import AutoSetup

    response_data = {}
    response_data['success'] = False

    try:
        body = req.body.decode('utf-8')
        config_data = loads(body)

        instance_id = config_data.get('instance_id', '')
        api_token = config_data.get('api_token', '')

        if not instance_id or not api_token:
            response_data['error'] = 'Instance ID and API Token are required'
            return json_response(response_data, success=False)

        setup = AutoSetup(main_token=api_token, instance_id=instance_id)
        result = setup.test_connection()

        if result['success']:
            response_data['success'] = True
            response_data['message'] = result['message']
            return json_response(response_data)
        else:
            error_msg = result['error']
            response_data['error'] = error_msg
            return json_response(response_data, success=False)

    except Exception as e:
        logger.error('test_connection exception: {}'.format(format_exc()))
        error_message = str(e)
        response_data['error'] = error_message
        return json_response(response_data, success=False)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def save_config(req):
    from zato.common.json_internal import loads
    body = req.body.decode('utf-8')
    config_data = loads(body)
    logger.info('save_config: config_data={}'.format(config_data))
    response_data = {}
    response_data['success'] = True
    response_data['message'] = 'Configuration saved'
    return json_response(response_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req):
    grafana_cloud_page_config['step1_label'] = 'Configuring'
    grafana_cloud_page_config['restart_step_id'] = 'install'
    grafana_cloud_page_config['restart_step_label'] = 'Restarting'
    return TemplateResponse(req, 'zato/observability/grafana-cloud/index.html', {
        'page_config': grafana_cloud_page_config,
        'is_enabled': False,
        'instance_id': '',
        'api_token': '',
        'audit_log': []
    })

# ################################################################################################################################
# ################################################################################################################################
