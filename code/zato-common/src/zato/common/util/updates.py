# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from logging import getLogger, Formatter, DEBUG
from logging.handlers import RotatingFileHandler
from traceback import format_exc
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# humanize
import humanize

# Redis
import redis

# Zato
from zato.common.json_internal import dumps, loads
from zato.common.util.tcp import wait_until_port_free

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def setup_update_file_logger(base_dir:'str'=None, component_name:'str'='unknown') -> 'None':
    """ Sets up file handler for update.log at DEBUG level with rotation.
    Can be called from both Updater and CLI commands.
    """
    try:
        if not base_dir:
            base_dir = os.path.expanduser('~/env/qs-1')

        update_log_path = os.path.join(base_dir, 'server1', 'logs', 'update.log')
        os.makedirs(os.path.dirname(update_log_path), exist_ok=True)

        file_handler = RotatingFileHandler(
            update_log_path,
            maxBytes=10 * 1024 * 1024,
            backupCount=100
        )
        file_handler.setLevel(DEBUG)

        formatter = Formatter('%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s')
        formatter.converter = time.localtime
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.setLevel(DEBUG)

        logger.debug('setup_update_file_logger: update.log configured for component [{}] at {}'.format(component_name, update_log_path))
    except Exception:
        logger.error('setup_update_file_logger: failed to setup update logger for component [{}]: {}'.format(component_name, format_exc()))

# ################################################################################################################################
# ################################################################################################################################

class UpdaterConfig:
    """ Configuration for the Updater class.
    """
    def __init__(
        self,
        *,
        redis_host:'str' = 'localhost',
        redis_port:'int' = 6379,
        redis_db:'int' = 0,
        current_dir:'strnone' = None,
        base_dir:'strnone' = None,
        zato_path:'str' = os.path.sep.join(['code', 'bin', 'zato']),
        github_repo:'str' = 'zatosource/zato',
        github_branch:'str' = 'support/4.1',
        default_version:'str' = '4.1.0',
        audit_log_key:'str' = 'zato:autoupdate:audit_log',
        schedule_key:'str' = 'zato:autoupdate:schedule',
        lock_key:'str' = 'zato:autoupdate:lock',
        lock_timeout:'int' = 3600,
        audit_log_max_entries:'int' = 100
    ) -> 'None':
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.current_dir = current_dir or os.path.dirname(os.path.abspath(__file__))
        self.base_dir = base_dir or os.path.expanduser('~/env/qs-1')
        self.zato_path = zato_path
        self.github_repo = github_repo
        self.github_branch = github_branch
        self.default_version = default_version
        self.audit_log_key = audit_log_key
        self.schedule_key = schedule_key
        self.lock_key = lock_key
        self.lock_timeout = lock_timeout
        self.audit_log_max_entries = audit_log_max_entries

# ################################################################################################################################
# ################################################################################################################################

class Updater:
    """ Handles Zato version updates and related operations.
    """
    def __init__(self, config:'UpdaterConfig') -> 'None':
        self.config = config
        self._setup_update_logger()

# ################################################################################################################################

    def _setup_update_logger(self) -> 'None':
        """ Sets up file handler for update.log at DEBUG level.
        """
        setup_update_file_logger(self.config.base_dir, 'updater')

# ################################################################################################################################

    def get_component_path(self, component_name:'str') -> 'str':
        """ Returns the path for a component.
        """
        component_map = {
            'scheduler': 'scheduler',
            'server': 'server1',
            'proxy': 'load-balancer',
            'dashboard': 'web-admin'
        }

        component_dir = component_map.get(component_name, component_name)
        return os.path.join(self.config.base_dir, component_dir)

# ################################################################################################################################

    def restart_auxiliary_processes(self) -> 'dict':
        """ Restarts auxiliary Python processes.
        """
        results = {}
        failed = []

        aux_processes = [
            ('util_rabbitmqctl', 'pubsub/util_rabbitmqctl.py', []),
            ('pubsub_publisher', 'pubsub/cli.py', ['start', '--publish']),
            ('pubsub_pull_consumer', 'pubsub/cli.py', ['start', '--pull']),
            ('file_transfer_listener', 'file_transfer/listener.py', [])
        ]

        for process_name, script_path, args in aux_processes:
            logger.info('restart_auxiliary_processes: restarting {}'.format(process_name))
            result = self.restart_auxiliary_process(process_name, script_path, args)
            results[process_name] = result

            if not result['success']:
                failed.append(process_name)
                logger.error('restart_auxiliary_processes: failed to restart {}'.format(process_name))

        if failed:
            return {
                'success': False,
                'error': 'Failed to restart: {}'.format(', '.join(failed)),
                'results': results
            }

        return {'success': True, 'results': results}

# ################################################################################################################################

    def restart_auxiliary_process(self, process_name:'str', script_path:'str', args:'list'=None) -> 'dict':
        """ Restarts an auxiliary Python process by killing it and restarting.
        """
        try:
            args = args or []
            logger.info('restart_auxiliary_process: restarting {}'.format(process_name))

            full_script_path = os.path.join(self.config.base_dir, 'code', 'zato-common', 'src', 'zato', 'common', script_path)

            if not os.path.exists(full_script_path):
                logger.warning('restart_auxiliary_process: {} script not found at {}'.format(process_name, full_script_path))
                return {'success': True, 'message': 'Script not found, skipped'}

            subprocess.run(['pkill', '-f', script_path], capture_output=True)

            time.sleep(1)

            py_path = os.path.join(self.config.base_dir, 'code', 'bin', 'py')
            log_dir = os.path.join(self.config.base_dir, 'server1', 'logs')
            log_file = os.path.join(log_dir, '{}.log'.format(process_name))

            cmd = [py_path, full_script_path] + args

            with open(log_file, 'a') as log_f:
                subprocess.Popen(
                    cmd,
                    stdout=log_f,
                    stderr=log_f,
                    start_new_session=True
                )

            logger.info('restart_auxiliary_process: {} restarted successfully'.format(process_name))
            return {'success': True, 'message': 'Restarted'}

        except Exception:
            logger.error('restart_auxiliary_process: exception restarting {}: {}'.format(process_name, format_exc()))
            return {'success': False, 'error': format_exc()}

# ################################################################################################################################

    def get_component_port(self, component_name:'str') -> 'int':
        """ Returns the port for a component.
        """
        port_map = {
            'scheduler': 0,
            'server': 17010,
            'proxy': 11223,
            'dashboard': 8183
        }

        return port_map.get(component_name, 0)

# ################################################################################################################################

    def get_redis_connection(self) -> 'redis.Redis':
        """ Returns a Redis connection.
        """
        return redis.Redis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            decode_responses=True
        )

# ################################################################################################################################

    def add_audit_log_entry(
        self,
        update_type:'str',
        version_from:'str',
        version_to:'str',
        start_time:'datetime',
        end_time:'datetime'
    ) -> 'None':
        """ Adds an entry to the audit log.
        """
        try:
            r = self.get_redis_connection()

            entry = {
                'type': update_type,
                'version_from': version_from,
                'version_to': version_to,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }

            _ = r.lpush(self.config.audit_log_key, dumps(entry))
            _ = r.ltrim(self.config.audit_log_key, 0, self.config.audit_log_max_entries - 1)

            logger.info(f'add_audit_log_entry: added {update_type} update from {version_from} to {version_to}')
        except Exception:
            logger.error(f'add_audit_log_entry: exception: {format_exc()}')

# ################################################################################################################################

    def get_audit_log_entries(self, count:'int' = 10) -> 'list':
        """ Returns audit log entries.
        """
        try:
            r = self.get_redis_connection()
            entries = r.lrange(self.config.audit_log_key, 0, count - 1)

            out = []
            for idx, entry_json in enumerate(entries, 1): # type: ignore
                entry = loads(entry_json)
                end_time = datetime.fromisoformat(entry['end_time'])

                time_ago = humanize.naturaltime(end_time)
                time_ago = time_ago[0].upper() + time_ago[1:] if time_ago else ''
                if time_ago == 'A second ago':
                    time_ago = 'A moment ago'

                out.append({
                    'number': idx,
                    'type': entry['type'],
                    'version_from': entry['version_from'],
                    'version_to': entry['version_to'],
                    'time_ago': time_ago,
                    'timestamp': entry['end_time']
                })

            return out
        except Exception:
            logger.error(f'get_audit_log_entries: exception: {format_exc()}')
            return []

# ################################################################################################################################

    def find_file_in_parents(self, target_path:'str') -> 'strnone':
        """ Finds a file by searching parent directories.
        """
        search_dir = self.config.current_dir

        while True:
            candidate = os.path.join(search_dir, target_path)

            if os.path.isfile(candidate):
                return candidate

            parent_dir = os.path.dirname(search_dir)

            if parent_dir == search_dir:
                return None

            search_dir = parent_dir

# ################################################################################################################################

    def get_zato_version(self) -> 'str':
        """ Returns the current Zato version.
        """
        zato_binary = self.find_file_in_parents(self.config.zato_path)

        if not zato_binary:
            return self.config.default_version

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

        return self.config.default_version

# ################################################################################################################################

    def run_command(
        self,
        command:'list',
        cwd:'strnone' = None,
        timeout:'int' = 999_999,
        log_prefix:'str' = 'command'
    ) -> 'dict':
        """ Runs a shell command and returns the result.
        """
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

                error_msg = error_output.strip() if error_output.strip() else 'Command failed with exit code {}'.format(result.returncode)

                return {
                    'success': False,
                    'error': error_msg,
                    'exit_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }

            logger.info('{}: command succeeded'.format(log_prefix))
            command_output = 'stdout: {}\nstderr: {}'.format(result.stdout, result.stderr)
            if result.stdout or result.stderr:
                logger.info('{}: output: {}'.format(log_prefix, command_output))

            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr
            }

        except subprocess.TimeoutExpired:
            logger.error('{}: command timed out after {} seconds'.format(log_prefix, timeout))
            return {
                'success': False,
                'error': 'Command timed out after {} seconds'.format(timeout)
            }

        except Exception:
            logger.error('{}: exception: {}'.format(log_prefix, format_exc()))
            return {
                'success': False,
                'error': 'Internal error occurred'
            }

# ################################################################################################################################

    def get_changed_files(self) -> 'list':
        """ Gets list of changed files from git diff.
        """
        try:
            git_root_result = self.run_command(
                command=['git', 'rev-parse', '--show-toplevel'],
                cwd=self.config.current_dir,
                log_prefix='get_changed_files'
            )

            if not git_root_result['success']:
                logger.warning('get_changed_files: not in a git repository, assuming all components need restart')
                return []

            git_root = git_root_result['stdout'].strip()

            result = self.run_command(
                command=['git', 'diff', '--name-only', 'HEAD@{1}', 'HEAD'],
                cwd=git_root,
                log_prefix='get_changed_files'
            )
            if result['success']:
                files = [f.strip() for f in result['stdout'].split('\n') if f.strip()]
                logger.info('get_changed_files: {} files changed'.format(len(files)))
                return files
            else:
                logger.warning('get_changed_files: git diff failed, assuming all components need restart')
                return []
        except Exception:
            logger.error('get_changed_files: exception: {}'.format(format_exc()))
            return []

# ################################################################################################################################

    def has_directory_changes(self, changed_files:'list', directory:'str') -> 'bool':
        """ Checks if any changed files are in the specified directory.
        """
        for file in changed_files:
            if file.startswith(directory):
                logger.info('has_directory_changes: {} has changes'.format(directory))
                return True
        return False

# ################################################################################################################################

    def download_and_install(self, update_script_name:'str' = 'update.sh', update_type:'str' = 'manual', schedule:'strnone'=None, exclude_from_restart:'list'=None) -> 'dict':
        """ Downloads and installs an update.
        """
        time.sleep(0.05)
        return {
            'success': False,
            'error': 'Mock error for testing',
            'stdout': 'some stdout output',
            'stderr': 'some stderr output'
        }

        logger.info('')
        logger.info('#' * 80)
        logger.info('##' + ' ' * 76 + '##')
        logger.info('##' + ' ' * 22 + 'UPDATE STARTED' + ' ' * 40 + '##')
        logger.info('##' + ' ' * 76 + '##')
        logger.info('#' * 80)
        logger.info('')

        update_script = self.find_file_in_parents(update_script_name)

        if not update_script:
            logger.error(f'download_and_install: {update_script_name} not found in parent directories')
            return {
                'success': False,
                'error': f'{update_script_name} not found in parent directories'
            }

        version_from = self.get_zato_version()
        start_time = datetime.now(timezone.utc)

        script_dir = os.path.dirname(update_script)
        result = self.run_command(
            command=['bash', update_script],
            cwd=script_dir,
            log_prefix='download_and_install'
        )

        if result['success']:
            end_time = datetime.now(timezone.utc)
            version_to = self.get_zato_version()
            self.add_audit_log_entry(update_type, version_from, version_to, start_time, end_time)

            result['version_from'] = version_from
            result['version_to'] = version_to
            result['schedule'] = schedule

            changed_files = self.get_changed_files()

            logger.info('download_and_install: storing changed files for component restart checks')
            try:
                r = self.get_redis_connection()
                r.set('zato:autoupdate:changed_files', '\n'.join(changed_files), ex=3600)
            except Exception:
                logger.error('download_and_install: failed to store changed files: {}'.format(format_exc()))

            logger.info('')
            logger.info('#' * 80)
            logger.info('##' + ' ' * 76 + '##')
            logger.info('##' + ' ' * 20 + 'DOWNLOAD COMPLETED' + ' ' * 38 + '##')
            logger.info('##' + ' ' * 76 + '##')
            logger.info('#' * 80)
            logger.info('')
        else:
            logger.info('')
            logger.info('#' * 80)
            logger.info('##' + ' ' * 76 + '##')
            logger.info('##' + ' ' * 23 + 'UPDATE FAILED' + ' ' * 40 + '##')
            logger.info('##' + ' ' * 76 + '##')
            logger.info('#' * 80)
            logger.info('')

        return result

# ################################################################################################################################

    def check_latest_version(self) -> 'dict':
        """ Checks the latest version from GitHub.
        """
        commit_sha = None
        commit_date = None

        try:
            url = f'https://api.github.com/repos/{self.config.github_repo}/commits/{self.config.github_branch}'
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
                    ['git', 'clone', '--depth=1', f'--branch={self.config.github_branch}',
                     f'https://github.com/{self.config.github_repo}.git', temp_dir],
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
                return {
                    'success': False,
                    'error': 'Failed to check latest version'
                }

            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception:
            logger.error(f'check_latest_version: exception: {format_exc()}')
            return {
                'success': False,
                'error': 'Failed to check latest version'
            }

        try:
            dt = datetime.fromisoformat(commit_date.replace('Z', '+00:00'))
            year = str(dt.year).zfill(4)
            month = str(dt.month).zfill(2)
            day = str(dt.day).zfill(2)
            hour = str(dt.hour).zfill(2)
            minute = str(dt.minute).zfill(2)

            version = f'4.1.{year}{month}{day}.{hour}{minute}.{commit_sha}'
            return {
                'success': True,
                'version': version
            }

        except Exception:
            logger.error(f'check_latest_version: exception: {format_exc()}')
            return {
                'success': False,
                'error': 'Failed to check latest version'
            }

# ################################################################################################################################

    def save_schedule(self, schedule_data:'dict') -> 'dict':
        """ Saves the update schedule to Redis.
        """
        try:
            r = self.get_redis_connection()
            _ = r.set(self.config.schedule_key, dumps(schedule_data))
            logger.debug('save_schedule: schedule saved')

            return {'success': True}

        except Exception:
            logger.error('save_schedule: exception: {}'.format(format_exc()))
            return {
                'success': False,
                'error': 'Failed to save schedule'
            }

# ################################################################################################################################

    def load_schedule(self) -> 'dict':
        """ Loads the update schedule from Redis.
        """
        try:
            r = self.get_redis_connection()
            schedule_json = r.get(self.config.schedule_key)

            if schedule_json:
                logger.info('load_schedule: found schedule in Redis')
                schedule_data = loads(schedule_json) # type: ignore
                return {
                    'success': True,
                    'schedule': schedule_data
                }
            else:
                logger.info('load_schedule: no schedule found in Redis')
                return {
                    'success': True,
                    'schedule': None
                }

        except Exception:
            logger.error('load_schedule: exception: {}'.format(format_exc()))
            return {
                'success': False,
                'error': 'Failed to load schedule'
            }

# ################################################################################################################################

    def delete_schedule(self) -> 'dict':
        """ Deletes the update schedule from Redis.
        """
        try:
            r = self.get_redis_connection()
            _ = r.delete(self.config.schedule_key)
            logger.info('delete_schedule: schedule deleted from Redis')

            return {'success': True}

        except Exception:
            logger.error('delete_schedule: exception: {}'.format(format_exc()))
            return {
                'success': False,
                'error': 'Failed to delete schedule'
            }

# ################################################################################################################################

    def acquire_lock(self) -> 'bool':
        """ Acquires a lock for update operations.
        """
        try:
            r = self.get_redis_connection()
            result = r.set(self.config.lock_key, '1', nx=True, ex=self.config.lock_timeout)
            if result:
                logger.info('acquire_lock: lock acquired')
                return True
            else:
                logger.info('acquire_lock: lock already held by another process')
                return False
        except Exception:
            logger.error('acquire_lock: exception: {}'.format(format_exc()))
            return False

# ################################################################################################################################

    def release_lock(self) -> 'None':
        """ Releases the update lock.
        """
        try:
            r = self.get_redis_connection()
            _ = r.delete(self.config.lock_key)
            logger.info('release_lock: lock released')
        except Exception:
            logger.error('release_lock: exception: {}'.format(format_exc()))

# ################################################################################################################################

    def _get_last_update_time(self) -> 'datetime | None':
        """ Gets the last update run time from Redis.
        """
        try:
            r = self.get_redis_connection()
            last_run = r.get('zato:autoupdate:last_run')
            if last_run:
                return datetime.fromisoformat(last_run)
            return None
        except Exception:
            logger.error('_get_last_update_time: exception: {}'.format(format_exc()))
            return None

# ################################################################################################################################

    def _set_last_update_time(self) -> 'None':
        """ Sets the last update run time in Redis.
        """
        try:
            r = self.get_redis_connection()
            r.set('zato:autoupdate:last_run', datetime.now(timezone.utc).isoformat())
            logger.info('_set_last_update_time: recorded update time')
        except Exception:
            logger.error('_set_last_update_time: exception: {}'.format(format_exc()))

# ################################################################################################################################

    def _get_min_interval_minutes(self, frequency:'str') -> 'int':
        """ Returns minimum minutes between updates for a given frequency.
        """
        intervals = {
            'hourly': 50,
            'daily': 23 * 60,
            'weekly': 6 * 24 * 60,
            'monthly': 27 * 24 * 60
        }
        return intervals.get(frequency, 23 * 60)

# ################################################################################################################################

    def should_run_scheduled_update(self) -> 'bool':
        """ Checks if a scheduled update should run now.
        """
        try:
            schedule_result = self.load_schedule()
            if not schedule_result['success']:
                logger.info('should_run_scheduled_update: failed to load schedule')
                return False

            schedule = schedule_result.get('schedule')
            if not schedule:
                logger.info('should_run_scheduled_update: no schedule configured')
                return False

            logger.info('should_run_scheduled_update: schedule data: {}'.format(schedule))

            if not schedule.get('enabled', False):
                logger.info('should_run_scheduled_update: schedule is disabled, enabled={}'.format(schedule.get('enabled')))
                return False

            frequency = schedule.get('frequency', 'daily')

            # Check if enough time has passed since last update
            last_run = self._get_last_update_time()
            if last_run:
                min_interval = self._get_min_interval_minutes(frequency)
                minutes_since_last = (datetime.now(timezone.utc) - last_run).total_seconds() / 60
                minutes_since_last_int = int(minutes_since_last)
                minutes_word = 'minute' if minutes_since_last_int == 1 else 'minutes'
                interval_word = 'minute' if min_interval == 1 else 'minutes'
                logger.info('should_run_scheduled_update: last run was {} {} ago, min interval is {} {}'.format(
                    minutes_since_last_int, minutes_word, min_interval, interval_word))
                if minutes_since_last < min_interval:
                    logger.info('should_run_scheduled_update: not enough time since last update, skipping')
                    return False

            if frequency == 'hourly':
                # For hourly, run at the specified minute each hour
                schedule_time = schedule.get('time', '')
                if schedule_time and ':' in schedule_time:
                    time_parts = schedule_time.split(':')
                    schedule_minute = int(time_parts[1])
                else:
                    schedule_minute = schedule.get('minute', 0)

                from zoneinfo import ZoneInfo

                schedule_timezone_str = schedule.get('timezone', 'UTC')
                try:
                    schedule_tz = ZoneInfo(schedule_timezone_str)
                except Exception:
                    logger.warning('should_run_scheduled_update: invalid timezone {}, using UTC'.format(schedule_timezone_str))
                    schedule_tz = ZoneInfo('UTC')

                now_server = datetime.now(timezone.utc)
                now_user_tz = now_server.astimezone(schedule_tz)
                current_minute = now_user_tz.minute

                minute_diff = current_minute - schedule_minute

                logger.info('should_run_scheduled_update: hourly schedule at minute {}, current minute {} (diff {} min)'.format(
                    schedule_minute, current_minute, minute_diff))

                if 0 <= minute_diff <= 10:
                    logger.info('should_run_scheduled_update: minute matches within 10-minute window after schedule, update will run')
                    return True
                else:
                    logger.info('should_run_scheduled_update: minute not within 0-10 minutes after scheduled minute')
                    return False

            from zoneinfo import ZoneInfo

            schedule_timezone_str = schedule.get('timezone', 'UTC')
            try:
                schedule_tz = ZoneInfo(schedule_timezone_str)
            except Exception:
                logger.warning('should_run_scheduled_update: invalid timezone {}, using UTC'.format(schedule_timezone_str))
                schedule_tz = ZoneInfo('UTC')

            now_server = datetime.now(timezone.utc)
            now_user_tz = now_server.astimezone(schedule_tz)

            current_hour = now_user_tz.hour
            current_minute = now_user_tz.minute
            current_day = now_user_tz.weekday()

            schedule_time = schedule.get('time', '')
            if schedule_time and ':' in schedule_time:
                time_parts = schedule_time.split(':')
                schedule_hour = int(time_parts[0])
                schedule_minute = int(time_parts[1])
            else:
                schedule_hour = schedule.get('hour')
                schedule_minute = schedule.get('minute')

            if schedule_hour is None or schedule_minute is None:
                logger.info('should_run_scheduled_update: invalid schedule configuration, hour={}, minute={}'.format(
                    schedule_hour, schedule_minute))
                return False

            day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            current_day_name = day_names[current_day]
            current_time_str = '{:02d}:{:02d}'.format(current_hour, current_minute)
            schedule_time_str = '{:02d}:{:02d}'.format(schedule_hour, schedule_minute)

            current_total_minutes = current_hour * 60 + current_minute
            schedule_total_minutes = schedule_hour * 60 + schedule_minute
            time_diff = current_total_minutes - schedule_total_minutes

            if frequency == 'daily':
                logger.info('should_run_scheduled_update: daily schedule at {}, current time {} (diff {} min)'.format(
                    schedule_time_str, current_time_str, time_diff))

                if 0 <= time_diff <= 10:
                    logger.info('should_run_scheduled_update: time matches within 10-minute window after schedule, update will run')
                    return True
                else:
                    logger.info('should_run_scheduled_update: time not within 0-10 minutes after scheduled time')
                    return False

            if frequency == 'weekly':
                schedule_day_name = schedule.get('day', '')
                day_map = {
                    'monday': 0,
                    'tuesday': 1,
                    'wednesday': 2,
                    'thursday': 3,
                    'friday': 4,
                    'saturday': 5,
                    'sunday': 6
                }

                if schedule_day_name and schedule_day_name.lower() in day_map:
                    schedule_days = [day_map[schedule_day_name.lower()]]
                else:
                    schedule_days = schedule.get('days', [])

                schedule_day_names = [day_names[d] for d in schedule_days] if schedule_days else []

                logger.info('should_run_scheduled_update: weekly schedule at {} on {}, current time {} (day {}, diff {} min)'.format(
                    schedule_time_str, schedule_day_names, current_time_str, current_day_name, time_diff))

                if schedule_days and current_day not in schedule_days:
                    logger.info('should_run_scheduled_update: current day {} not in scheduled days {}'.format(
                        current_day_name, schedule_day_names))
                    return False

                if 0 <= time_diff <= 10:
                    logger.info('should_run_scheduled_update: time and day match within 10-minute window after schedule, update will run')
                    return True
                else:
                    logger.info('should_run_scheduled_update: time not within 0-10 minutes after scheduled time')
                    return False

            if frequency == 'monthly':
                schedule_day_name = schedule.get('day', '')
                schedule_week = schedule.get('week', '')

                day_map = {
                    'monday': 0,
                    'tuesday': 1,
                    'wednesday': 2,
                    'thursday': 3,
                    'friday': 4,
                    'saturday': 5,
                    'sunday': 6
                }

                if not schedule_day_name or schedule_day_name.lower() not in day_map:
                    logger.info('should_run_scheduled_update: invalid day for monthly schedule')
                    return False

                schedule_weekday = day_map[schedule_day_name.lower()]

                current_month_day = now_user_tz.day
                import calendar
                month_days = calendar.monthrange(now_user_tz.year, now_user_tz.month)[1]

                week_of_month = (current_month_day - 1) // 7 + 1

                target_week = None
                if schedule_week == 'first':
                    target_week = 1
                elif schedule_week == 'second':
                    target_week = 2
                elif schedule_week == 'third':
                    target_week = 3
                elif schedule_week == 'last':
                    last_day = month_days
                    last_week = (last_day - 1) // 7 + 1
                    target_week = last_week
                else:
                    logger.info('should_run_scheduled_update: invalid week specification for monthly schedule: {}'.format(schedule_week))
                    return False

                logger.info('should_run_scheduled_update: monthly schedule at {} on {} of {} week, current time {} (day {}, week {}, diff {} min)'.format(
                    schedule_time_str, schedule_day_name, schedule_week, current_time_str, current_day_name, week_of_month, time_diff))

                if current_day != schedule_weekday:
                    logger.info('should_run_scheduled_update: current day {} does not match scheduled day {}'.format(
                        current_day_name, schedule_day_name))
                    return False

                if week_of_month != target_week:
                    logger.info('should_run_scheduled_update: current week {} does not match target week {}'.format(
                        week_of_month, target_week))
                    return False

                if 0 <= time_diff <= 10:
                    logger.info('should_run_scheduled_update: time, day, and week match within 10-minute window after schedule, update will run')
                    return True
                else:
                    logger.info('should_run_scheduled_update: time not within 0-10 minutes after scheduled time')
                    return False

            logger.info('should_run_scheduled_update: unknown frequency {}'.format(frequency))
            return False

        except Exception:
            logger.error('should_run_scheduled_update: exception: {}'.format(format_exc()))
            return False

# ################################################################################################################################

# ################################################################################################################################

    def kill_process_by_port(self, port:'int') -> 'bool':
        """ Finds and kills the process using a specific port.
        """
        try:
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid_str in pids:
                    if pid_str:
                        pid = int(pid_str)
                        logger.info(f'kill_process_by_port: killing process {pid} using port {port}')
                        kill_args = ['-9', str(pid)]
                        kill_result = subprocess.run(['sudo', 'kill'] + kill_args, capture_output=True)
                        if kill_result.returncode != 0:
                            logger.info(f'kill_process_by_port: sudo kill failed for pid {pid}, trying without sudo')
                            kill_result = subprocess.run(['kill'] + kill_args, capture_output=True)
                            logger.info(f'kill_process_by_port: non-sudo kill result for pid {pid}: returncode={kill_result.returncode}')
                return True
            else:
                logger.info(f'kill_process_by_port: no process found using port {port}')
                return False
        except Exception:
            logger.error(f'kill_process_by_port: exception: {format_exc()}')
            return False

# ################################################################################################################################

    def kill_orphaned_processes(self, component_name:'str') -> 'None':
        """ Kills all orphaned processes for a component.
        """
        try:
            ps_result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=5
            )

            process_name = 'zato.web-admin' if component_name == 'dashboard' else 'zato.{}'.format(component_name)

            current_pid = os.getpid()
            logger.info('kill_orphaned_processes: current process pid is {}'.format(current_pid))

            for line in ps_result.stdout.split('\n'):
                if process_name in line and 'grep' not in line and 'start-' not in line and 'Zato_' not in line:
                    parts = line.split()
                    if len(parts) > 1:
                        pid = int(parts[1])

                        if pid == current_pid:
                            logger.warning('kill_orphaned_processes: SKIPPING pid {} - this is our own process!'.format(pid))
                            continue

                        logger.info('kill_orphaned_processes: about to kill orphaned {} process {} ({})'.format(component_name, pid, process_name))
                        logger.info('kill_orphaned_processes: full ps line for pid {}: {}'.format(pid, line.strip()))
                        for handler in logger.handlers:
                            handler.flush()

                        kill_args = ['-9', str(pid)]
                        orphan_kill_result = subprocess.run(['sudo', 'kill'] + kill_args, capture_output=True)

                        if orphan_kill_result.returncode != 0:
                            logger.info('kill_orphaned_processes: sudo kill failed for pid {}, trying without sudo'.format(pid))
                            orphan_kill_result = subprocess.run(['kill'] + kill_args, capture_output=True)

                        logger.info('kill_orphaned_processes: kill result for pid {}: returncode={}, stdout={}, stderr={}'.format(
                            pid, orphan_kill_result.returncode, orphan_kill_result.stdout, orphan_kill_result.stderr))
                        for handler in logger.handlers:
                            handler.flush()
        except Exception:
            logger.error('kill_orphaned_processes: EXCEPTION: {}'.format(format_exc()))
            for handler in logger.handlers:
                handler.flush()

# ################################################################################################################################

    def stop_component(self, component_name:'str', component_path:'str', port:'int'=0) -> 'dict':
        """ Stops a Zato component.
        """
        try:
            # Handle proxy component separately - it uses haproxy which runs without pidfile
            if component_name == 'proxy':
                return self._stop_proxy_component()

            pidfile = os.path.join(component_path, 'pidfile')

            if not os.path.exists(pidfile):
                logger.info('stop_component: no pidfile found for {} at {}, checking for orphaned processes'.format(component_name, pidfile))
                self.kill_orphaned_processes(component_name)
                if port:
                    logger.info('stop_component: killing process using port {}'.format(port))
                    self.kill_process_by_port(port)
                return {'success': True, 'message': 'Component not running, orphaned processes cleaned'}

            with open(pidfile, 'r') as f:
                pid_str = f.read().strip()

            if not pid_str:
                logger.error('stop_component: empty pidfile for {} at {}'.format(component_name, pidfile))
                os.remove(pidfile)
                self.kill_orphaned_processes(component_name)
                return {'success': True, 'message': 'Empty pidfile removed, orphaned processes cleaned'}

            pid = int(pid_str)
            logger.info('stop_component: sending SIGKILL to {} (pid {})'.format(component_name, pid))

            kill_args = ['-9', str(pid)]
            kill_result = subprocess.run(['sudo', 'kill'] + kill_args, capture_output=True)
            logger.info('stop_component: kill result for {} (pid {}): returncode={}, stdout={}, stderr={}'.format(
                component_name, pid, kill_result.returncode, kill_result.stdout, kill_result.stderr))

            if kill_result.returncode != 0:
                logger.info('stop_component: sudo kill failed, trying without sudo')
                kill_result = subprocess.run(['kill'] + kill_args, capture_output=True)
                logger.info('stop_component: non-sudo kill result for {} (pid {}): returncode={}, stdout={}, stderr={}'.format(
                    component_name, pid, kill_result.returncode, kill_result.stdout, kill_result.stderr))

            logger.info('stop_component: sleeping 1 second after kill for {}'.format(component_name))
            time.sleep(1)
            logger.info('stop_component: sleep completed for {}'.format(component_name))

            if os.path.exists(pidfile):
                os.remove(pidfile)
            logger.info('stop_component: calling kill_orphaned_processes for {}'.format(component_name))
            self.kill_orphaned_processes(component_name)
            logger.info('stop_component: kill_orphaned_processes completed for {}'.format(component_name))
            logger.info('stop_component: returning success for {}'.format(component_name))
            for handler in logger.handlers:
                handler.flush()
            return {'success': True, 'message': 'Component killed, orphaned processes cleaned'}

        except Exception:
            logger.error('stop_component: EXCEPTION stopping {}: {}'.format(component_name, format_exc()))
            for handler in logger.handlers:
                handler.flush()
            return {'success': False, 'error': format_exc()}

# ################################################################################################################################

    def _stop_proxy_component(self) -> 'dict':
        """ Stops HAProxy by finding and killing the process.
        """
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'haproxy.*haproxy.cfg'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0 or not result.stdout.strip():
                logger.info('_stop_proxy_component: haproxy not running')
                return {'success': True, 'message': 'HAProxy not running'}

            pids = result.stdout.strip().split('\n')
            for pid_str in pids:
                if pid_str:
                    pid = int(pid_str)
                    logger.info('_stop_proxy_component: killing haproxy process {}'.format(pid))
                    kill_args = ['-9', str(pid)]
                    kill_result = subprocess.run(['sudo', 'kill'] + kill_args, capture_output=True)
                    if kill_result.returncode != 0:
                        logger.info('_stop_proxy_component: sudo kill failed for pid {}, trying without sudo'.format(pid))
                        kill_result = subprocess.run(['kill'] + kill_args, capture_output=True)
                    logger.info('_stop_proxy_component: kill result for pid {}: returncode={}'.format(pid, kill_result.returncode))

            time.sleep(1)
            logger.info('_stop_proxy_component: haproxy stopped')
            return {'success': True, 'message': 'HAProxy stopped'}

        except Exception:
            logger.error('_stop_proxy_component: exception: {}'.format(format_exc()))
            return {'success': False, 'error': format_exc()}

# ################################################################################################################################

    def stop_pubsub_component(self, component_name:'str') -> 'dict':
        """ Stops a pubsub component by killing its process.
        """
        try:
            process_patterns = {
                'util-rabbitmqctl': 'util_rabbitmqctl.py',
                'pubsub-publisher': 'pubsub/cli.py.*--publish',
                'pubsub-pull-consumer': 'pubsub/cli.py.*--pull'
            }

            pattern = process_patterns.get(component_name)
            if not pattern:
                logger.error('stop_pubsub_component: unknown component {}'.format(component_name))
                return {'success': False, 'error': 'Unknown component'}

            result = subprocess.run(
                ['pgrep', '-f', pattern],
                capture_output=True,
                text=True
            )

            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid_str in pids:
                    if pid_str:
                        pid = int(pid_str)
                        logger.info('stop_pubsub_component: killing {} (pid {})'.format(component_name, pid))
                        kill_args = ['-9', str(pid)]
                        kill_result = subprocess.run(['sudo', 'kill'] + kill_args, capture_output=True)
                        if kill_result.returncode != 0:
                            logger.info('stop_pubsub_component: sudo kill failed for pid {}, trying without sudo'.format(pid))
                            kill_result = subprocess.run(['kill'] + kill_args, capture_output=True)
                            logger.info('stop_pubsub_component: non-sudo kill result for pid {}: returncode={}'.format(pid, kill_result.returncode))
                return {'success': True, 'message': 'Component stopped'}
            else:
                logger.info('stop_pubsub_component: {} not running'.format(component_name))
                return {'success': True, 'message': 'Component not running'}

        except Exception:
            logger.error('stop_pubsub_component: exception stopping {}: {}'.format(component_name, format_exc()))
            return {'success': False, 'error': format_exc()}

# ################################################################################################################################

    def start_pubsub_component(self, component_name:'str') -> 'dict':
        """ Starts a pubsub component using its startup script.
        """
        try:
            script_name_map = {
                'util-rabbitmqctl': 'start-util-rabbitmqctl.sh',
                'pubsub-publisher': 'start-pubsub-publisher.sh',
                'pubsub-pull-consumer': 'start-pubsub-pull-consumer.sh'
            }

            script_name = script_name_map.get(component_name)
            if not script_name:
                logger.error('start_pubsub_component: unknown component {}'.format(component_name))
                return {'success': False, 'error': 'Unknown component'}

            startup_script = os.path.join(self.config.base_dir, script_name)
            logger.info('start_pubsub_component: looking for script at {}'.format(startup_script))

            if not os.path.exists(startup_script):
                logger.error('start_pubsub_component: script not found {}'.format(startup_script))
                return {'success': False, 'error': 'Script not found'}

            subprocess.Popen(
                ['bash', startup_script],
                cwd=self.config.base_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            logger.info('start_pubsub_component: {} started'.format(component_name))
            time.sleep(2)
            return {'success': True, 'message': 'Component started'}

        except Exception:
            logger.error('start_pubsub_component: exception starting {}: {}'.format(component_name, format_exc()))
            return {'success': False, 'error': format_exc()}

# ################################################################################################################################

    def start_component(self, component_name:'str', component_path:'str') -> 'dict':
        """ Starts a Zato component using the startup scripts.
        """
        try:
            # Handle proxy component separately - it uses haproxy which runs in foreground without pidfile
            if component_name == 'proxy':
                return self._start_proxy_component()

            # Map component names to their startup script names
            script_name_map = {
                'scheduler': 'start-scheduler-fg.sh',
                'server': 'start-server1-fg.sh',
                'dashboard': 'start-web-admin-fg.sh',
            }

            script_name = script_name_map.get(component_name)
            if not script_name:
                error = 'Unknown component name: {}'.format(component_name)
                logger.error('start_component: {}'.format(error))
                return {'success': False, 'error': error}

            startup_script = os.path.join(self.config.base_dir, script_name)
            logger.info('start_component: looking for startup script at {}'.format(startup_script))

            if not os.path.exists(startup_script):
                error = 'Startup script not found: {}'.format(startup_script)
                logger.error('start_component: {}'.format(error))
                return {'success': False, 'error': error}

            pidfile = os.path.join(component_path, 'pidfile')
            logger.info('start_component: checking for pidfile at {}'.format(pidfile))

            if os.path.exists(pidfile):
                logger.error('start_component: pidfile exists for {}, component may already be running'.format(component_name))
                return {'success': False, 'error': 'Component already running'}

            logger.info('start_component: starting {} using script {}'.format(component_name, startup_script))
            logger.info('start_component: cwd: {}'.format(self.config.base_dir))
            logger.info('start_component: about to call subprocess.Popen for {}'.format(component_name))

            process = subprocess.Popen(
                ['bash', startup_script],
                cwd=self.config.base_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            logger.info('start_component: launched {} with pid {}'.format(component_name, process.pid))
            logger.info('start_component: waiting for pidfile to appear for {} (max_wait=40s)'.format(component_name))

            max_wait = 40
            for i in range(max_wait):
                time.sleep(1)
                if os.path.exists(pidfile):
                    logger.info('start_component: {} started successfully'.format(component_name))
                    return {'success': True, 'message': 'Component started'}

            logger.error('start_component: pidfile not created after {} seconds for {}'.format(max_wait, component_name))
            logger.error('start_component: expected pidfile at: {}'.format(pidfile))
            logger.error('start_component: component_path exists check: {}'.format(os.path.exists(component_path)))

            all_files = os.listdir(component_path) if os.path.exists(component_path) else []
            logger.error('start_component: all files in {}: {}'.format(component_path, all_files))

            return {
                'success': False,
                'error': 'Pidfile not created after {} seconds'.format(max_wait)
            }

        except Exception:
            logger.error('start_component: exception starting {}: {}'.format(component_name, format_exc()))
            return {'success': False, 'error': format_exc()}

# ################################################################################################################################

    def _start_proxy_component(self) -> 'dict':
        """ Starts HAProxy using the same method as entrypoint.sh - runs in foreground without pidfile.
        """
        try:
            startup_script = os.path.join(self.config.base_dir, 'start-haproxy.sh')
            logger.info('_start_proxy_component: looking for startup script at {}'.format(startup_script))

            if not os.path.exists(startup_script):
                error = 'Startup script not found: {}'.format(startup_script)
                logger.error('_start_proxy_component: {}'.format(error))
                return {'success': False, 'error': error}

            # Check if haproxy is already running
            check_result = subprocess.run(
                ['pgrep', '-f', 'haproxy.*haproxy.cfg'],
                capture_output=True,
                text=True
            )
            if check_result.returncode == 0 and check_result.stdout.strip():
                logger.info('_start_proxy_component: haproxy already running with pids: {}'.format(check_result.stdout.strip()))
                return {'success': False, 'error': 'HAProxy already running'}

            logger.info('_start_proxy_component: starting haproxy using script {}'.format(startup_script))
            logger.info('_start_proxy_component: cwd: {}'.format(self.config.base_dir))

            process = subprocess.Popen(
                ['bash', startup_script],
                cwd=self.config.base_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            logger.info('_start_proxy_component: launched haproxy with pid {}'.format(process.pid))

            # Wait and verify haproxy process is running
            time.sleep(2)

            verify_result = subprocess.run(
                ['pgrep', '-f', 'haproxy.*haproxy.cfg'],
                capture_output=True,
                text=True
            )

            if verify_result.returncode == 0 and verify_result.stdout.strip():
                logger.info('_start_proxy_component: haproxy started successfully, pids: {}'.format(verify_result.stdout.strip()))
                return {'success': True, 'message': 'HAProxy started'}

            logger.error('_start_proxy_component: haproxy process not found after startup')
            return {'success': False, 'error': 'HAProxy process not found after startup'}

        except Exception:
            logger.error('_start_proxy_component: exception: {}'.format(format_exc()))
            return {'success': False, 'error': format_exc()}

# ################################################################################################################################

    def get_stored_changed_files(self) -> 'list':
        """ Gets changed files stored in Redis from the last update.
        """
        try:
            r = self.get_redis_connection()
            files_str = r.get('zato:autoupdate:changed_files')
            if files_str:
                files = files_str.decode('utf-8').split('\n') if isinstance(files_str, bytes) else files_str.split('\n')
                return [f for f in files if f.strip()]
            return []
        except Exception:
            logger.error('get_stored_changed_files: exception: {}'.format(format_exc()))
            return []

# ################################################################################################################################

    def restart_component(self, component_name:'str', component_path:'str', port:'int'=0, check_changes:'bool'=True) -> 'dict':
        """ Restarts a Zato component with port checking.
        """
        time.sleep(0.05)
        return {
            'success': True,
            'message': '{} restarted'.format(component_name)
        }

        try:
            if component_name == 'proxy' and not os.path.exists(component_path):
                import getpass
                current_user = getpass.getuser()
                logger.info('restart_component: proxy component not found at {}, current user is {}, skipping'.format(
                    component_path, current_user))
                return {'success': True, 'message': 'Proxy component not installed, skipped'}

            if check_changes:
                changed_files = self.get_stored_changed_files()
                if changed_files:
                    component_dirs = {
                        'scheduler': 'code/zato-scheduler/',
                        'server': 'code/zato-server/',
                        'dashboard': 'code/zato-web-admin/'
                    }

                    has_common_changes = self.has_directory_changes(changed_files, 'code/zato-common/')
                    component_dir = component_dirs.get(component_name, '')
                    has_component_changes = self.has_directory_changes(changed_files, component_dir)

                    if not has_common_changes and not has_component_changes:
                        logger.info('restart_component: {} has no changes, skipping restart'.format(component_name))
                        return {'success': True, 'message': 'No changes detected, restart skipped'}

            logger.info('restart_component: restarting {} at {}'.format(component_name, component_path))

            stop_result = self.stop_component(component_name, component_path, port)
            logger.info('restart_component: stop_component returned for {}: {}'.format(component_name, stop_result))
            for handler in logger.handlers:
                handler.flush()

            if not stop_result['success']:
                logger.error('restart_component: failed to stop {}: {}'.format(component_name, stop_result.get('error')))

            logger.info('restart_component: proceeding to start phase for {}, port={}'.format(component_name, port))
            for handler in logger.handlers:
                handler.flush()

            if port:
                logger.info('restart_component: waiting for port {} to be released (timeout=30s)'.format(port))
                port_free = wait_until_port_free(port, timeout=30)
                logger.info('restart_component: wait_until_port_free returned {} for port {}'.format(port_free, port))
                if not port_free:
                    logger.error('restart_component: port {} still in use after stopping {}'.format(
                        port, component_name))

                    pidfile = os.path.join(component_path, 'pidfile')
                    if os.path.exists(pidfile):
                        logger.info('restart_component: removing stale pidfile for {}'.format(component_name))
                        os.remove(pidfile)

                    port_free_retry = wait_until_port_free(port, timeout=10)
                    logger.info('restart_component: wait_until_port_free retry returned {} for port {}'.format(port_free_retry, port))
                    if not port_free_retry:
                        logger.error('restart_component: port {} still in use after retries, cannot start {}'.format(port, component_name))
                        return {
                            'success': False,
                            'error': 'Port {} still in use, cannot start {}'.format(port, component_name)
                        }

            logger.info('restart_component: calling start_component for {}'.format(component_name))
            start_result = self.start_component(component_name, component_path)
            logger.info('restart_component: start_component returned for {}: {}'.format(component_name, start_result))

            if start_result['success']:
                logger.info('restart_component: {} restarted successfully'.format(component_name))
            else:
                logger.error('restart_component: failed to start {}: {}'.format(
                    component_name, start_result.get('error')))

            return start_result

        except Exception:
            logger.error('restart_component: EXCEPTION restarting {}: {}'.format(component_name, format_exc()))
            for handler in logger.handlers:
                handler.flush()
            return {'success': False, 'error': format_exc()}

# ################################################################################################################################

    def restart_all_components(self, exclude_components:'list'=None, changed_files:'list'=None) -> 'dict':
        """ Restarts all Zato components in order based on changed files.
        Stop order: proxy -> dashboard -> server -> scheduler -> pubsub-pull-consumer -> pubsub-publisher -> util-rabbitmqctl
        Start order: util-rabbitmqctl -> pubsub-publisher -> pubsub-pull-consumer -> scheduler -> server -> dashboard -> proxy
        """
        exclude_components = exclude_components or []
        changed_files = changed_files or []

        component_dirs = {
            'scheduler': 'code/zato-scheduler/',
            'server': 'code/zato-server/',
            'dashboard': 'code/zato-web-admin/'
        }

        has_common_changes = self.has_directory_changes(changed_files, 'code/zato-common/')

        if has_common_changes:
            logger.info('restart_all_components: zato-common has changes, restarting all components')

        main_components = ['scheduler', 'server', 'dashboard', 'proxy']
        pubsub_components = ['util-rabbitmqctl', 'pubsub-publisher', 'pubsub-pull-consumer']

        start_order = pubsub_components + main_components
        stop_order = ['proxy', 'dashboard', 'server', 'scheduler', 'pubsub-pull-consumer', 'pubsub-publisher', 'util-rabbitmqctl']

        results = {}
        failed = []
        skipped = []
        to_restart = []

        for component_name in main_components:
            if component_name in exclude_components:
                logger.info('restart_all_components: {} excluded from restart'.format(component_name))
                skipped.append(component_name)
                results[component_name] = {'success': True, 'message': 'Excluded'}
                continue

            component_dir = component_dirs.get(component_name)
            has_changes = has_common_changes or self.has_directory_changes(changed_files, component_dir)

            if not has_changes and changed_files:
                logger.info('restart_all_components: {} has no changes, skipping restart'.format(component_name))
                skipped.append(component_name)
                results[component_name] = {'success': True, 'message': 'No changes detected'}
                continue

            to_restart.append(component_name)

        if 'server' in to_restart or has_common_changes:
            for comp in pubsub_components:
                if comp not in to_restart:
                    to_restart.insert(0, comp)

        logger.info('restart_all_components: stopping components in order: {}'.format([c for c in stop_order if c in to_restart]))
        for component_name in stop_order:
            if component_name not in to_restart:
                continue
            logger.info('restart_all_components: stopping {}'.format(component_name))
            if component_name in pubsub_components:
                self.stop_pubsub_component(component_name)
            else:
                component_path = self.get_component_path(component_name)
                component_port = self.get_component_port(component_name)
                self.stop_component(component_name, component_path, component_port)

        logger.info('restart_all_components: starting components in order: {}'.format([c for c in start_order if c in to_restart]))
        for component_name in start_order:
            if component_name not in to_restart:
                continue
            logger.info('restart_all_components: starting {}'.format(component_name))
            if component_name in pubsub_components:
                result = self.start_pubsub_component(component_name)
            else:
                component_path = self.get_component_path(component_name)
                result = self.start_component(component_name, component_path)
            results[component_name] = result

            if not result['success']:
                failed.append(component_name)
                logger.error('restart_all_components: failed to start {}'.format(component_name))

        if failed:
            message = 'Failed to restart components: {}. '.format(', '.join(failed))
            if skipped:
                message += 'Skipped: {}'.format(', '.join(skipped))
            return {
                'success': False,
                'error': message,
                'results': results
            }

        message = 'All components restarted successfully'
        if skipped:
            message += '. Skipped: {}'.format(', '.join(skipped))

        logger.info('restart_all_components: {}'.format(message))

        logger.info('')
        logger.info('#' * 80)
        logger.info('##' + ' ' * 76 + '##')
        logger.info('##' + ' ' * 21 + 'UPDATE COMPLETED' + ' ' * 39 + '##')
        logger.info('##' + ' ' * 76 + '##')
        logger.info('#' * 80)
        logger.info('')

        return {
            'success': True,
            'message': message,
            'results': results
        }

# ################################################################################################################################
# ################################################################################################################################
