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
from zato.admin.web.views.settings.config import grafana_cloud_page_config
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
    import subprocess as _subprocess
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
            result = _subprocess.run(
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

    from opentelemetry import metrics as _
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.resources import Resource
    from traceback import format_exc
    from zato.common.json_internal import loads

    response_data = {}
    response_data['success'] = False

    try:
        body = req.body.decode('utf-8')
        config_data = loads(body)
        logger.info('test_connection: config_data={}'.format(config_data))

        _instance_id = config_data.get('instance_id', '')
        _api_key = config_data.get('api_key', '')
        _endpoint = config_data.get('endpoint', '')

        logger.info('test_connection: instance_id={}, api_key={}, endpoint={}'.format(
            _instance_id, _api_key[:10] + '...' if _api_key else '', _endpoint))

        if not _instance_id or not _api_key or not _endpoint:
            response_data['error'] = 'Instance ID, API key and endpoint are required'
            logger.error('test_connection: missing required fields')
            return json_response(response_data, success=False)

        otlp_endpoint = 'http://localhost:4318/v1/metrics'
        logger.info('test_connection: creating resource')
        resource = Resource.create({'service.name': 'zato'})

        logger.info('test_connection: creating exporter with endpoint={}'.format(otlp_endpoint))
        exporter = OTLPMetricExporter(endpoint=otlp_endpoint)

        logger.info('test_connection: creating reader')
        reader = PeriodicExportingMetricReader(exporter, export_interval_millis=1000)

        logger.info('test_connection: creating provider')
        provider = MeterProvider(resource=resource, metric_readers=[reader])

        logger.info('test_connection: creating meter')
        meter = provider.get_meter('zato.test')

        logger.info('test_connection: creating gauge zato.test.conn')
        gauge = meter.create_gauge('zato.test.conn')

        logger.info('test_connection: setting gauge value to 1')
        gauge.set(1)

        logger.info('test_connection: calling force_flush')
        flush_result = provider.force_flush()
        logger.info('test_connection: force_flush returned {}'.format(flush_result))

        logger.info('test_connection: calling shutdown')
        provider.shutdown()
        logger.info('test_connection: shutdown complete')

        response_data['success'] = True
        response_data['message'] = 'Test metric sent'
        logger.info('test_connection: success')
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
    import redis
    from traceback import format_exc
    from zato.common.json_internal import loads

    response_data = {}
    response_data['success'] = False

    try:
        body = req.body.decode('utf-8')
        config_data = loads(body)

        is_enabled = config_data.get('is_enabled', False)

        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

        if is_enabled:
            _ = r.set('zato:grafana_cloud:is_enabled', 'true')
            response_data['message'] = 'Configuration updated'
        else:
            _ = r.delete('zato:grafana_cloud:is_enabled')
            _ = r.delete('zato:grafana_cloud:instance_id')
            _ = r.delete('zato:grafana_cloud:runtime_token')
            _ = r.delete('zato:grafana_cloud:endpoint')
            response_data['message'] = 'Configuration removed'
            response_data['needs_restart'] = True

        response_data['success'] = True
        logger.info('toggle_enabled: is_enabled set to {}'.format(is_enabled))

        return json_response(response_data)

    except Exception as e:
        logger.error('toggle_enabled exception: {}'.format(format_exc()))
        error_message = str(e)
        response_data['error'] = error_message
        return json_response(response_data, success=False)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def save_config(req):
    import base64
    import redis
    import subprocess
    import tempfile
    from traceback import format_exc
    from zato.admin.web.views.otelcol_config import template as otelcol_template
    from zato.common.json_internal import loads

    response_data = {}
    response_data['success'] = False

    username = req.user.username if req.user else ''
    if username != 'zato':
        response_data['success'] = True
        response_data['message'] = 'Configuration saved'
        return json_response(response_data)

    try:
        body = req.body.decode('utf-8')
        config_data = loads(body)
        logger.info('save_config: config_data={}'.format(config_data))

        instance_id = config_data.get('instance_id', '')
        api_key = config_data.get('api_key', '')
        endpoint = config_data.get('endpoint', '')

        if not instance_id or not api_key or not endpoint:
            response_data['error'] = 'Instance ID, API key and endpoint are required'
            return json_response(response_data, success=False)

        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        _ = r.set('zato:grafana_cloud:instance_id', instance_id)
        _ = r.set('zato:grafana_cloud:runtime_token', api_key)
        _ = r.set('zato:grafana_cloud:endpoint', endpoint)
        _ = r.set('zato:grafana_cloud:is_enabled', 'true')

        credentials_raw = '{}:{}'.format(instance_id, api_key)
        credentials_encoded = base64.b64encode(credentials_raw.encode('utf-8')).decode('utf-8')
        logger.info('save_config: credentials encoded')

        otelcol_config = otelcol_template.format(
            endpoint=endpoint,
            credentials=credentials_encoded
        )
        logger.info('save_config: otelcol config generated')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=True) as f:
            _ = f.write(otelcol_config)
            f.flush()
            temp_path = f.name
            logger.info('save_config: temp file written to {}'.format(temp_path))

            result = subprocess.run(
                ['sudo', 'cp', temp_path, '/etc/otelcol-contrib/config.yaml'],
                capture_output=True,
                text=True
            )
            logger.info('save_config: cp result: returncode={}, stdout={}, stderr={}'.format(
                result.returncode, result.stdout, result.stderr))

        result = subprocess.run(
            ['sudo', 'systemctl', 'restart', 'otelcol-contrib'],
            capture_output=True,
            text=True
        )
        logger.info('save_config: restart otelcol-contrib result: returncode={}, stdout={}, stderr={}'.format(
            result.returncode, result.stdout, result.stderr))

        response_data['success'] = True
        response_data['message'] = 'Configuration saved'

        logger.info('save_config: saved instance_id={}'.format(instance_id))

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

    import redis
    from traceback import format_exc

    grafana_cloud_page_config['step1_label'] = 'Configuring'
    grafana_cloud_page_config['restart_step_id'] = 'install'
    grafana_cloud_page_config['restart_step_label'] = 'Restarting'

    instance_id = ''
    api_key = ''
    endpoint = ''
    is_enabled = False

    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        logger.info('index: connecting to redis')

        instance_id = r.get('zato:grafana_cloud:instance_id') or ''
        logger.info('index: instance_id from redis: {}'.format(instance_id))

        api_key = r.get('zato:grafana_cloud:runtime_token') or ''
        logger.info('index: api_key from redis: {}'.format(api_key))

        endpoint = r.get('zato:grafana_cloud:endpoint') or ''
        logger.info('index: endpoint from redis: {}'.format(endpoint))

        is_enabled_value = r.get('zato:grafana_cloud:is_enabled') or 'false'
        logger.info('index: is_enabled_value from redis: {}'.format(is_enabled_value))

        is_enabled = is_enabled_value == 'true'
        logger.info('index: is_enabled boolean: {}'.format(is_enabled))
    except Exception:
        logger.error('index: redis error: {}'.format(format_exc()))

    logger.info('index: returning template with is_enabled={}, instance_id={}'.format(
        is_enabled, instance_id))

    return TemplateResponse(req, 'zato/monitoring/grafana-cloud/index.html', {
        'page_config': grafana_cloud_page_config,
        'is_enabled': is_enabled,
        'instance_id': instance_id,
        'api_key': api_key,
        'endpoint': endpoint,
        'audit_log': []
    })

# ################################################################################################################################
# ################################################################################################################################
