# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from logging import getLogger
from traceback import format_exc
from urllib.error import HTTPError
from urllib.request import urlopen, Request

# humanize
import humanize

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

def json_response(data, success=True):
    response_json = dumps(data)
    response_class = HttpResponse if success else HttpResponseServerError
    return response_class(response_json, content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

def error_response(error_msg, log_prefix=None):
    if log_prefix:
        logger.error(f'{log_prefix}: {error_msg}')
    return json_response({'success': False, 'error': error_msg}, success=False)

# ################################################################################################################################
# ################################################################################################################################

def add_audit_log_entry(update_type, version_from, version_to, start_time, end_time):
    try:
        r = get_redis_connection()

        entry = {
            'type': update_type,
            'version_from': version_from,
            'version_to': version_to,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }

        _ = r.lpush('zato:autoupdate:audit_log', dumps(entry))
        _ = r.ltrim('zato:autoupdate:audit_log', 0, 99)

        logger.info(f'add_audit_log_entry: added {update_type} update from {version_from} to {version_to}')
    except Exception:
        logger.error(f'add_audit_log_entry: exception: {format_exc()}')

# ################################################################################################################################
# ################################################################################################################################

def get_audit_log_entries(count=10):
    try:
        r = get_redis_connection()
        entries = r.lrange('zato:autoupdate:audit_log', 0, count - 1)

        result = []
        for idx, entry_json in enumerate(entries, 1): # type: ignore
            entry = loads(entry_json)
            end_time = datetime.fromisoformat(entry['end_time'])

            time_ago = humanize.naturaltime(end_time)
            time_ago = time_ago[0].upper() + time_ago[1:] if time_ago else ''
            if time_ago == 'A second ago':
                time_ago = 'A moment ago'

            result.append({
                'number': idx,
                'type': entry['type'],
                'version_from': entry['version_from'],
                'version_to': entry['version_to'],
                'time_ago': time_ago,
                'timestamp': entry['end_time']
            })

        return result
    except Exception:
        logger.error(f'get_audit_log_entries: exception: {format_exc()}')
        return []

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
            version = result.stdout.strip()
            if version.startswith('Zato '):
                version = version[5:]
            return version
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

            return json_response({
                'success': False,
                'error': error_output,
                'exit_code': result.returncode
            }, success=False)

        logger.info('{}: command succeeded'.format(log_prefix))
        command_output = 'stdout: {}\nstderr: {}'.format(result.stdout, result.stderr)
        if result.stdout or result.stderr:
            logger.info('{}: output: {}'.format(log_prefix, command_output))

        return json_response({'success': True})

    except subprocess.TimeoutExpired:
        logger.error('{}: command timed out after {} seconds'.format(log_prefix, timeout))
        return error_response('Command timed out after {} seconds'.format(timeout))

    except Exception:
        logger.error('{}: exception: {}'.format(log_prefix, format_exc()))
        return error_response('Internal error occurred')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def download_and_install(req):

    file_name = 'update.sh'
    update_script = find_file_in_parents(file_name)

    if not update_script:
        return error_response(f'{file_name} not found in parent directories', 'download_and_install')

    version_from = get_zato_version()
    start_time = datetime.now(timezone.utc)

    script_dir = os.path.dirname(update_script)
    result = run_command(
        req,
        command=['bash', update_script],
        cwd=script_dir,
        log_prefix='download_and_install'
    )

    if result.status_code == 200:
        end_time = datetime.now(timezone.utc)
        version_to = get_zato_version()
        add_audit_log_entry('manual', version_from, version_to, start_time, end_time)

    return result

# ################################################################################################################################
# ################################################################################################################################

def restart_component(req, component_name):
    zato_binary = find_file_in_parents(zato_path)

    if not zato_binary:
        return error_response(f'{zato_path} not found in parent directories', f'restart_{component_name}')

    return run_command(
        req,
        command=[zato_binary, '--version'],
        cwd=current_dir,
        log_prefix=f'restart_{component_name}'
    )

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
    try:
        body = req.body.decode('utf-8')
        schedule_data = loads(body)
        logger.info('save_schedule: received data: {}'.format(schedule_data))

        r = get_redis_connection()
        _ = r.set('zato:autoupdate:schedule', dumps(schedule_data))
        logger.info('save_schedule: schedule saved to Redis')

        return json_response({'success': True})

    except Exception:
        logger.error('save_schedule: exception: {}'.format(format_exc()))
        return error_response('Failed to save schedule')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def load_schedule(req):
    try:
        r = get_redis_connection()
        schedule_json = r.get('zato:autoupdate:schedule')

        if schedule_json:
            logger.info('load_schedule: found schedule in Redis')
            _ = schedule_data = loads(schedule_json) # type: ignore
            return json_response({'success': True, 'schedule': schedule_data})
        else:
            logger.info('load_schedule: no schedule found in Redis')
            return json_response({'success': True, 'schedule': None})

    except Exception:
        logger.error('load_schedule: exception: {}'.format(format_exc()))
        return error_response('Failed to load schedule')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def delete_schedule(req):
    try:
        r = get_redis_connection()
        _ = r.delete('zato:autoupdate:schedule')
        logger.info('delete_schedule: schedule deleted from Redis')

        return json_response({'success': True})

    except Exception:
        logger.error('delete_schedule: exception: {}'.format(format_exc()))
        return error_response('Failed to delete schedule')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req):
    return TemplateResponse(req, 'zato/in-app-updates/index.html', {
        'current_version': get_zato_version(),
        'audit_log': get_audit_log_entries(5)
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_latest_audit_entry(req):
    try:
        entries = get_audit_log_entries(1)
        if entries:
            return json_response({'success': True, 'entry': entries[0]})
        else:
            return json_response({'success': True, 'entry': None})
    except Exception:
        logger.error(f'get_latest_audit_entry: exception: {format_exc()}')
        return error_response('Failed to get latest audit entry')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_audit_log_refresh(req):
    try:
        entries = get_audit_log_entries(5)
        return json_response({'success': True, 'entries': entries})
    except Exception:
        logger.error(f'get_audit_log_refresh: exception: {format_exc()}')
        return error_response('Failed to refresh audit log')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def check_latest_version(req):
    commit_sha = None
    commit_date = None

    try:
        url = 'https://api.github.com/repos/zatosource/zato/commits/support/4.1'
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0')

        with urlopen(request, timeout=10) as response:
            data = loads(response.read().decode('utf-8'))

        commit_sha = data['sha'][:9]
        commit_date = data['commit']['committer']['date']

    except HTTPError as e:
        logger.warning(f'check_latest_version: GitHub API error: {e}, using git clone')

        temp_dir = tempfile.mkdtemp()
        try:
            result = subprocess.run(
                ['git', 'clone', '--depth=1', '--branch=support/4.1', 'https://github.com/zatosource/zato.git', temp_dir],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise Exception(f'Git clone failed: {result.stderr}')

            logger.info(f'check_latest_version: git clone succeeded')

            if result.stdout:
                logger.info(f'check_latest_version: git clone stdout: {result.stdout}')
            if result.stderr:

                logger.info(f'check_latest_version: git clone stderr: {result.stderr}')

            result = subprocess.run(
                ['git', 'log', '-1', '--format=%H|%cI'],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                raise Exception(f'Git log failed: {result.stderr}')

            commit_sha, commit_date = result.stdout.strip().split('|')
            commit_sha = commit_sha[:9]
            logger.info(f'check_latest_version: obtained commit {commit_sha} from git')
            logger.info(f'check_latest_version: git log stdout: {result.stdout.strip()}')

        except Exception:
            logger.error(f'check_latest_version: git method failed: {format_exc()}')
            shutil.rmtree(temp_dir, ignore_errors=True)
            return error_response('Failed to check latest version')

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception:
        logger.error(f'check_latest_version: exception: {format_exc()}')
        return error_response('Failed to check latest version')

    try:
        dt = datetime.fromisoformat(commit_date.replace('Z', '+00:00'))
        year = str(dt.year % 100).zfill(2)
        month = str(dt.month).zfill(2)
        day = str(dt.day).zfill(2)
        hour = str(dt.hour).zfill(2)
        minute = str(dt.minute).zfill(2)

        version = f'4.1.{year}.{month}.{day}.{hour}.{minute}.{commit_sha}'
        return json_response({'success': True, 'version': version})

    except Exception:
        logger.error(f'check_latest_version: exception: {format_exc()}')
        return error_response('Failed to check latest version')

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
