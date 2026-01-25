# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import subprocess
import threading
from logging import getLogger
from traceback import format_exc

# requests
import requests

# Django
from django.http import HttpResponse
from django.http.response import HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.settings.config import python_packages_page_config
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

hot_deploy_requirements_path = '/opt/hot-deploy/python-reqs/requirements.txt'
user_requirements_path = '/tmp/zato-user-packages.txt'

# ################################################################################################################################
# ################################################################################################################################

def json_response(data, success=True):
    response_json = dumps(data)
    response_class = HttpResponse if success else HttpResponseServerError
    return response_class(response_json, content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

def restart_component(req, component_name, component_path, port=0):
    logger.info('restart_%s: called from client: %s', component_name, req.META.get('REMOTE_ADDR'))
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

    logger.info('restart_dashboard: called from client: %s', req.META.get('REMOTE_ADDR'))

    def restart_after_delay():
        import time
        time.sleep(1)

        logger.info('restart_dashboard: executing make restart-dashboard')
        try:
            makefile_dir = os.path.expanduser('~/projects/zatosource-zato/4.1')
            logger.info('restart_dashboard: makefile_dir=%s', makefile_dir)
            result = subprocess.run(
                ['make', 'restart-dashboard'],
                cwd=makefile_dir,
                capture_output=True,
                text=True
            )
            logger.info('restart_dashboard: returncode=%s', result.returncode)
            logger.info('restart_dashboard: stdout=%s', result.stdout)
            if result.stderr:
                logger.error('restart_dashboard: stderr=%s', result.stderr)
        except Exception as e:
            logger.error('restart_dashboard: failed to execute make: %s', e)

    thread = threading.Thread(target=restart_after_delay, daemon=True)
    thread.start()

    result = {
        'success': True,
        'message': 'Dashboard restarting'
    }
    return json_response(result, success=True)

# ################################################################################################################################
# ################################################################################################################################

def _is_pypi_package(requirement_line):
    """ Returns True if this looks like a pypi package, False if it should be skipped. """
    line = requirement_line.strip()

    if not line:
        return False

    if line.startswith('#'):
        return False

    if line.startswith('-e'):
        return False

    if line.startswith('git+'):
        return False

    if line.startswith('http://') or line.startswith('https://'):
        return False

    if line.startswith('-i') or line.startswith('--index-url'):
        return False

    if line.startswith('--extra-index-url'):
        return False

    if line.startswith('-f') or line.startswith('--find-links'):
        return False

    if '@' in line and ('git' in line or 'http' in line):
        return False

    return True

# ################################################################################################################################

def _extract_package_name(requirement_line):
    """ Extracts the package name from a requirement line. """
    line = requirement_line.strip()

    match = re.match(r'^([a-zA-Z0-9_-]+)', line)
    if match:
        return match.group(1)

    return None

# ################################################################################################################################

@method_allowed('POST')
def test_packages(req):

    response_data = {}
    response_data['success'] = False

    try:
        body = req.body.decode('utf-8')
        config_data = loads(body)

        requirements_text = config_data.get('requirements', '')
        logger.info('test_packages: requirements_text length=%d', len(requirements_text))

        if not requirements_text.strip():
            response_data['error'] = 'No requirements provided'
            return json_response(response_data, success=False)

        lines = requirements_text.strip().split('\n')
        results = []
        has_errors = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if not _is_pypi_package(line):
                results.append({
                    'package': line,
                    'status': 'skipped',
                    'message': 'Not a pypi package'
                })
                continue

            package_name = _extract_package_name(line)
            if not package_name:
                results.append({
                    'package': line,
                    'status': 'skipped',
                    'message': 'Could not extract package name'
                })
                continue

            try:
                pypi_url = 'https://pypi.org/pypi/{}/json'.format(package_name)
                resp = requests.get(pypi_url, timeout=10)

                if resp.status_code == 200:
                    results.append({
                        'package': package_name,
                        'status': 'ok',
                        'message': 'Found on PyPI'
                    })
                else:
                    has_errors = True
                    results.append({
                        'package': package_name,
                        'status': 'error',
                        'message': 'Not found on PyPI'
                    })

            except requests.exceptions.Timeout:
                has_errors = True
                results.append({
                    'package': package_name,
                    'status': 'error',
                    'message': 'Timeout checking pypi'
                })
            except Exception as e:
                has_errors = True
                results.append({
                    'package': package_name,
                    'status': 'error',
                    'message': str(e)
                })

        response_data['results'] = results
        response_data['success'] = not has_errors

        if has_errors:
            error_packages = [r['package'] for r in results if r['status'] == 'error']
            response_data['error'] = 'Package(s) not found: {}'.format(', '.join(error_packages))

        return json_response(response_data, success=not has_errors)

    except Exception as e:
        logger.error('test_packages exception: %s', format_exc())
        response_data['error'] = str(e)
        return json_response(response_data, success=False)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def save_config(req):

    response_data = {}
    response_data['success'] = False

    try:
        body = req.body.decode('utf-8')
        config_data = loads(body)
        logger.info('save_config: config_data keys=%s', list(config_data.keys()))

        requirements_text = config_data.get('requirements', '')

        with open(user_requirements_path, 'w') as f:
            f.write(requirements_text)

        logger.info('save_config: saved requirements to %s', user_requirements_path)

        curdir = os.path.dirname(os.path.abspath(__file__))
        code_dir = os.path.abspath(os.path.join(curdir, '..', '..', '..', '..', '..', '..'))
        uv_bin = os.path.join(code_dir, 'support-linux', 'bin', 'uv')

        logger.info('save_config: code_dir=%s', code_dir)
        logger.info('save_config: uv_bin=%s', uv_bin)

        if not os.path.exists(uv_bin):
            response_data['error'] = 'uv binary not found at {}'.format(uv_bin)
            return json_response(response_data, success=False)

        result = subprocess.run(
            [uv_bin, 'pip', 'install', '-r', user_requirements_path],
            cwd=code_dir,
            capture_output=True,
            text=True
        )

        logger.info('save_config: uv returncode=%s', result.returncode)
        logger.info('save_config: uv stdout=%s', result.stdout)
        if result.stderr:
            logger.info('save_config: uv stderr=%s', result.stderr)

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or 'uv pip install failed'
            response_data['error'] = error_msg
            return json_response(response_data, success=False)

        response_data['success'] = True
        response_data['message'] = 'Packages installed'

        return json_response(response_data)

    except Exception as e:
        logger.error('save_config exception: %s', format_exc())
        response_data['error'] = str(e)
        return json_response(response_data, success=False)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req):

    python_packages_page_config['step1_label'] = 'Installing'
    python_packages_page_config['restart_step_id'] = 'install'
    python_packages_page_config['restart_step_label'] = 'Restarting'

    requirements = ''

    if os.path.exists(hot_deploy_requirements_path):
        try:
            with open(hot_deploy_requirements_path, 'r') as f:
                requirements = f.read()
            logger.info('index: requirements from hot-deploy length: %d', len(requirements))
        except Exception:
            logger.error('index: hot-deploy file read error: %s', format_exc())

    if not requirements and os.path.exists(user_requirements_path):
        try:
            with open(user_requirements_path, 'r') as f:
                requirements = f.read()
            logger.info('index: requirements from user file length: %d', len(requirements))
        except Exception:
            logger.error('index: user file read error: %s', format_exc())

    return TemplateResponse(req, 'zato/settings/python-packages/index.html', {
        'page_config': python_packages_page_config,
        'requirements': requirements,
    })

# ################################################################################################################################
# ################################################################################################################################
