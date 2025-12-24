# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
from datetime import datetime
from logging import getLogger
from traceback import format_exc
from urllib.request import urlopen, Request

# Django
from django.http import HttpResponse
from django.http.response import HttpResponseServerError
from django.template.response import TemplateResponse

# Redis
import redis

# Zato
from zato.admin.web.views import method_allowed
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

current_dir = os.path.dirname(os.path.abspath(__file__))
zato_path = os.path.sep.join(['code', 'bin', 'zato'])

# ################################################################################################################################
# ################################################################################################################################

def get_redis_connection():
    return redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# ################################################################################################################################
# ################################################################################################################################

def find_file_in_parents(target_path):
    search_dir = current_dir

    while True:
        candidate = os.path.join(search_dir, target_path)

        if os.path.isfile(candidate):
            return candidate

        parent_dir = os.path.dirname(search_dir)

        if parent_dir == search_dir:
            return None

        search_dir = parent_dir

# ################################################################################################################################
# ################################################################################################################################

def get_zato_version():
    zato_binary = find_file_in_parents(zato_path)

    if not zato_binary:
        return '4.1.0'

    try:
        result = subprocess.run(
            [zato_binary, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return '4.1.0'

# ################################################################################################################################
# ################################################################################################################################

def run_command(req, command, cwd=None, timeout=999_999, log_prefix='command'):

    logger.info('{}: called from client: {}'.format(log_prefix, req.META.get('REMOTE_ADDR')))
    logger.info('{}: command: {}'.format(log_prefix, command))
    logger.info('{}: cwd: {}'.format(log_prefix, cwd))

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0:
            logger.error('{}: command failed with exit code {}'.format(log_prefix, result.returncode))
            error_output = result.stdout + result.stderr
            logger.error('{}: error output: {}'.format(log_prefix, error_output))

            response_data = {
                'success': False,
                'error': error_output,
                'exit_code': result.returncode
            }

            response_json = dumps(response_data)
            response = HttpResponseServerError(response_json, content_type='application/json')
            return response

        logger.info('{}: command succeeded'.format(log_prefix))
        command_output = 'stdout: {}\nstderr: {}'.format(result.stdout, result.stderr)
        if result.stdout or result.stderr:
            logger.info('{}: output: {}'.format(log_prefix, command_output))

        success_data = {'success': True}
        success_json = dumps(success_data)
        response = HttpResponse(success_json, content_type='application/json')
        return response

    except subprocess.TimeoutExpired:
        logger.error('{}: command timed out after {} seconds'.format(log_prefix, timeout))

        timeout_msg = 'Command timed out after {} seconds'.format(timeout)
        response_data = {
            'success': False,
            'error': timeout_msg
        }

        response_json = dumps(response_data)
        response = HttpResponseServerError(response_json, content_type='application/json')
        return response

    except Exception:
        logger.error('{}: exception: {}'.format(log_prefix, format_exc()))

        response_data = {
            'success': False,
            'error': 'Internal error occurred'
        }

        response_json = dumps(response_data)
        response = HttpResponseServerError(response_json, content_type='application/json')
        return response

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def download_and_install(req):

    file_name = 'update.sh'
    update_script = find_file_in_parents(file_name)

    if not update_script:
        error_msg = '{} not found in parent directories'.format(file_name)
        logger.error('download_and_install: {}'.format(error_msg))
        response_data = {
            'success': False,
            'error': error_msg
        }
        response_json = dumps(response_data)
        return HttpResponseServerError(response_json, content_type='application/json')

    script_dir = os.path.dirname(update_script)
    return run_command(
        req,
        command=['bash', update_script],
        cwd=script_dir,
        log_prefix='download_and_install'
    )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def restart_scheduler(req):

    zato_binary = find_file_in_parents(zato_path)

    if not zato_binary:
        error_msg = '{} not found in parent directories'.format(zato_path)
        logger.error('restart_scheduler: {}'.format(error_msg))
        response_data = {
            'success': False,
            'error': error_msg
        }
        response_json = dumps(response_data)
        return HttpResponseServerError(response_json, content_type='application/json')

    return run_command(
        req,
        command=[zato_binary, '--version'],
        cwd=current_dir,
        log_prefix='restart_scheduler'
    )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def restart_server(req):

    zato_binary = find_file_in_parents(zato_path)

    if not zato_binary:
        error_msg = '{} not found in parent directories'.format(zato_path)
        logger.error('restart_server: {}'.format(error_msg))
        response_data = {
            'success': False,
            'error': error_msg
        }
        response_json = dumps(response_data)
        return HttpResponseServerError(response_json, content_type='application/json')

    return run_command(
        req,
        command=[zato_binary, '--version'],
        cwd=current_dir,
        log_prefix='restart_server'
    )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def restart_proxy(req):

    zato_binary = find_file_in_parents(zato_path)

    if not zato_binary:
        error_msg = '{} not found in parent directories'.format(zato_path)
        logger.error('restart_proxy: {}'.format(error_msg))
        response_data = {
            'success': False,
            'error': error_msg
        }
        response_json = dumps(response_data)
        return HttpResponseServerError(response_json, content_type='application/json')

    return run_command(
        req,
        command=[zato_binary, '--version'],
        cwd=current_dir,
        log_prefix='restart_proxy'
    )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def restart_dashboard(req):

    zato_binary = find_file_in_parents(zato_path)

    if not zato_binary:
        error_msg = '{} not found in parent directories'.format(zato_path)
        logger.error('restart_dashboard: {}'.format(error_msg))
        response_data = {
            'success': False,
            'error': error_msg
        }
        response_json = dumps(response_data)
        return HttpResponseServerError(response_json, content_type='application/json')

    return run_command(
        req,
        command=[zato_binary, '--version'],
        cwd=current_dir,
        log_prefix='restart_dashboard'
    )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def save_schedule(req):

    try:
        body = req.body.decode('utf-8')
        schedule_data = loads(body)

        logger.info('save_schedule: received data: {}'.format(schedule_data))

        r = get_redis_connection()
        _ = r.set('zato:autoupdate:schedule', dumps(schedule_data))

        logger.info('save_schedule: schedule saved to Redis')

        response_data = {'success': True}
        response_json = dumps(response_data)
        return HttpResponse(response_json, content_type='application/json')

    except Exception:
        logger.error('save_schedule: exception: {}'.format(format_exc()))

        response_data = {
            'success': False,
            'error': 'Failed to save schedule'
        }
        response_json = dumps(response_data)
        return HttpResponseServerError(response_json, content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def load_schedule(req):

    try:
        r = get_redis_connection()
        _ = schedule_json = r.get('zato:autoupdate:schedule')

        if schedule_json:
            logger.info('load_schedule: found schedule in Redis')
            schedule_data = loads(schedule_json) # type: ignore
            response_data = {
                'success': True,
                'schedule': schedule_data
            }
        else:
            logger.info('load_schedule: no schedule found in Redis')
            response_data = {
                'success': True,
                'schedule': None
            }

        response_json = dumps(response_data)
        return HttpResponse(response_json, content_type='application/json')

    except Exception:
        logger.error('load_schedule: exception: {}'.format(format_exc()))

        response_data = {
            'success': False,
            'error': 'Failed to load schedule'
        }
        response_json = dumps(response_data)
        return HttpResponseServerError(response_json, content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def delete_schedule(req):

    try:
        r = get_redis_connection()
        _ = r.delete('zato:autoupdate:schedule')

        logger.info('delete_schedule: schedule deleted from Redis')

        response_data = {'success': True}
        response_json = dumps(response_data)
        return HttpResponse(response_json, content_type='application/json')

    except Exception:
        logger.error('delete_schedule: exception: {}'.format(format_exc()))

        response_data = {
            'success': False,
            'error': 'Failed to delete schedule'
        }
        response_json = dumps(response_data)
        return HttpResponseServerError(response_json, content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req):
    return TemplateResponse(req, 'zato/in-app-updates/index.html', {
        'current_version': get_zato_version()
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def check_latest_version(req):
    try:
        url = 'https://api.github.com/repos/zatosource/zato/commits/support/4.1'
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0')

        with urlopen(request, timeout=10) as response:
            data = loads(response.read().decode('utf-8'))

        commit_sha = data['sha'][:9]
        commit_date = data['commit']['committer']['date']

        dt = datetime.fromisoformat(commit_date.replace('Z', '+00:00'))
        year = dt.year
        month = str(dt.month).zfill(2)
        day = str(dt.day).zfill(2)

        version = 'Zato 4.1.{}.{}.{}.{}'.format(year, month, day, commit_sha)

        import time
        time.sleep(1)

        response_data = {
            'success': True,
            'version': version
        }
        response_json = dumps(response_data)
        return HttpResponse(response_json, content_type='application/json')

    except Exception:
        logger.error('check_latest_version: exception: {}'.format(format_exc()))
        response_data = {
            'success': False,
            'error': 'Failed to check latest version'
        }
        response_json = dumps(response_data)
        return HttpResponseServerError(response_json, content_type='application/json')

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
