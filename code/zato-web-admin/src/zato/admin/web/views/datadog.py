# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import socket
import subprocess
import threading
import time
from logging import getLogger
from traceback import format_exc

# redis
import redis

# requests
import requests

# Django
from django.http import HttpResponse
from django.http.response import HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.settings.config import datadog_page_config
from zato.common.json_internal import dumps, loads
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
    response_json = dumps(data)
    response_class = HttpResponse if success else HttpResponseServerError
    return response_class(response_json, content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

def restart_component(req, component_name, component_path, port=0):
    logger.info('restart_{}: called from client: {}'.format(component_name, req.META.get('REMOTE_ADDR')))
    result = updater.restart_component(component_name, component_path, port, check_changes=False)
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

    logger.info('restart_dashboard: called from client: {}'.format(req.META.get('REMOTE_ADDR')))

    def restart_after_delay():
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

def _test_agent_connection(address, label, errors, use_udp=False):
    host, port = address.split(':')
    port = int(port)
    try:
        sock_type = socket.SOCK_DGRAM if use_udp else socket.SOCK_STREAM
        sock = socket.socket(socket.AF_INET, sock_type)
        sock.settimeout(2)
        if use_udp:
            _ = sock.sendto(b'', (host, port))
        else:
            sock.connect((host, port))
        sock.close()
        logger.info('test_connection: {} connection successful'.format(label))
    except Exception as e:
        errors.append('{} ({}): {}'.format(label, address, e))
        logger.error('test_connection: {} connection failed: {}'.format(label, format_exc()))

# ################################################################################################################################

@method_allowed('POST')
def test_connection(req):

    response_data = {}
    response_data['success'] = False

    try:
        body = req.body.decode('utf-8')
        config_data = loads(body)

        main_agent = config_data.get('main_agent', '')
        metrics_agent = config_data.get('metrics_agent', '')

        logger.info('test_connection: main_agent={}, metrics_agent={}'.format(main_agent, metrics_agent))

        missing = []
        if not main_agent:
            missing.append('Main agent')
        if not metrics_agent:
            missing.append('Metrics agent')

        if missing:
            if len(missing) == 1:
                response_data['error'] = 'Field missing: {}'.format(missing[0])
            else:
                response_data['error'] = 'Fields missing: {}'.format(', '.join(missing))
            return json_response(response_data, success=False)

        errors = []

        _test_agent_connection(main_agent, 'Main agent', errors)
        _test_agent_connection(metrics_agent, 'Metrics agent', errors, use_udp=True)

        if errors:
            response_data['errors'] = errors
            return json_response(response_data, success=False)

        response_data['success'] = True
        response_data['message'] = 'Connection test successful'
        return json_response(response_data)

    except Exception as e:
        logger.error('test_connection exception: {}'.format(format_exc()))
        error_message = str(e)
        response_data['error'] = error_message
        return json_response(response_data, success=False)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def toggle_enabled(req):

    response_data = {}
    response_data['success'] = True

    body = req.body.decode('utf-8')
    config_data = loads(body)
    is_enabled = config_data.get('is_enabled', False)

    response_data['message'] = 'Toggle state updated'
    response_data['needs_restart'] = not is_enabled

    return json_response(response_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def save_config(req):

    response_data = {}
    response_data['success'] = False

    try:
        body = req.body.decode('utf-8')
        config_data = loads(body)
        logger.info('save_config: config_data={}'.format(config_data))

        main_agent = config_data.get('main_agent', '')
        metrics_agent = config_data.get('metrics_agent', '')

        try:
            r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            _ = r.set('zato:datadog:main_agent', main_agent)
            _ = r.set('zato:datadog:metrics_agent', metrics_agent)
            _ = r.set('zato:datadog:is_enabled', 'true')
        except Exception:
            logger.error('save_config redis error: {}'.format(format_exc()))

        response_data['success'] = True
        response_data['message'] = 'Configuration saved'

        logger.info('save_config: Datadog configuration saved')

        return json_response(response_data)

    except Exception as e:
        logger.error('save_config exception: {}'.format(format_exc()))
        error_message = str(e)
        response_data['error'] = error_message
        return json_response(response_data, success=False)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req):

    datadog_page_config['step1_label'] = 'Configuring'
    datadog_page_config['restart_step_id'] = 'install'
    datadog_page_config['restart_step_label'] = 'Restarting'

    main_agent = ''
    metrics_agent = ''
    is_enabled = False

    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        logger.info('index: connecting to redis')

        main_agent = r.get('zato:datadog:main_agent') or ''
        logger.info('index: main_agent from redis: {}'.format(main_agent))

        metrics_agent = r.get('zato:datadog:metrics_agent') or ''
        logger.info('index: metrics_agent from redis: {}'.format(metrics_agent))

        is_enabled_value = r.get('zato:datadog:is_enabled') or 'false'
        logger.info('index: is_enabled_value from redis: {}'.format(is_enabled_value))

        is_enabled = is_enabled_value == 'true'
        logger.info('index: is_enabled boolean: {}'.format(is_enabled))
    except Exception:
        logger.error('index: redis error: {}'.format(format_exc()))

    logger.info('index: returning template with is_enabled={}, main_agent={}, metrics_agent={}'.format(
        is_enabled, main_agent, metrics_agent))

    return TemplateResponse(req, 'zato/monitoring/datadog/index.html', {
        'page_config': datadog_page_config,
        'is_enabled': is_enabled,
        'main_agent': main_agent,
        'metrics_agent': metrics_agent,
        'audit_log': []
    })

# ################################################################################################################################
# ################################################################################################################################
