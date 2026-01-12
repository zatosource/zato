# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from shutil import copy as shutil_copy
from zipfile import ZipFile

# Zato
from zato.cli import ManageCommand
from zato.common.util.file_system import get_tmp_path
from zato.common.util.open_ import open_r

# ################################################################################################################################
# ################################################################################################################################

if 0:

    from zato.common.typing_ import any_, anydict, callnone, dictnone, strdict

    # During development, it is convenient to configure it here to catch information that should be logged
    # even prior to setting up main loggers in each of components.

    # stdlib
    import logging

    log_level = logging.INFO
    log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=log_level, format=log_format)

# ################################################################################################################################
# ################################################################################################################################

stderr_sleep_fg = 0.9
stderr_sleep_bg = 1.2

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Deploy_Dirs = {'code', 'config-server', 'config-user', 'enmasse', 'env', 'lib', 'pip'}

# ################################################################################################################################
# ################################################################################################################################

class Start(ManageCommand):
    """Starts a Zato component installed in the 'path'. The same command is used for starting servers, load-balancer and web admin instances. 'path' must point to a directory into which the given component has been installed. # noqa: E501

Examples:
  - Assuming a Zato server has been installed in /opt/zato/server1, the command to start the server is 'zato start /opt/zato/server1'.
  - If a load-balancer has been installed in /home/zato/lb1, the command to start it is 'zato start /home/zato/lb1'."""

    opts = [
        {'name':'--fg', 'help':'If given, the component will run in foreground', 'action':'store_true'},
        {'name':'--deploy', 'help':'Resources to deploy', 'action':'store'},
        {'name':'--sync-internal', 'help':"Whether to synchronize component's internal state with ODB", 'action':'store_true'},
        {'name':'--secret-key', 'help':"Component's secret key", 'action':'store'},
        {'name':'--env-file', 'help':'Path to a file with environment variables to use', 'action':'store'},
        {'name':'--stop-after', 'help':'After how many seconds to stop all the Zato components in the system', 'action':'store'},
        {'name':'--stderr-path', 'help':'Where to redirect stderr', 'action':'store'}
    ]

# ################################################################################################################################

    def run_check_config(self) -> 'None':

        # Bunch
        from bunch import Bunch

        # Zato
        from zato.cli.check_config import CheckConfig

        cc = CheckConfig(self.args)
        cc.show_output = False

        cc.execute(Bunch({
            'path': '.',
            'ensure_no_pidfile': True,
            'check_server_port_available': True,
            'stdin_data': self.stdin_data,
            'secret_key': self.args.secret_key,
        }))

# ################################################################################################################################

    def delete_pidfile(self) -> 'None':

        # stdlib
        import os

        # Zato
        from zato.common.api import MISC

        # Local aliases
        path = None

        try:
            path = os.path.join(self.component_dir, MISC.PIDFILE)
            os.remove(path)
        except Exception as e:
            self.logger.debug('Pidfile `%s` could not be deleted `%s`', path, e)

# ################################################################################################################################

    def check_pidfile(self, pidfile:'str'='') -> 'int':

        # stdlib
        import os

        # Zato
        from zato.common.api import MISC

        pidfile = pidfile or os.path.join(self.config_dir, MISC.PIDFILE)

        # If we have a pidfile of that name then we already have a running
        # server, in which case we refrain from starting new processes now.
        if os.path.exists(pidfile):
            msg = 'Error - found pidfile `{}`'.format(pidfile)
            self.logger.info(msg)
            return self.SYS_ERROR.COMPONENT_ALREADY_RUNNING

        # Returning None would have sufficed but let's be explicit.
        return 0

# ################################################################################################################################

    def start_component(
        self,
        py_path:'str',
        name:'str',
        program_dir:'str',
        on_keyboard_interrupt:'callnone'=None,
        *,
        extra_options: 'dictnone' = None,
        env_vars: 'dictnone' = None,
    ) -> 'int':
        """ Starts a component in background or foreground, depending on the 'fg' flag.
        """

        # Type hints
        env_file:'str'

        # Zato
        from zato.common.util.proc import start_python_process

        # We need for it to be an absolute path because the component
        # may want to listen for changes to its contents.
        if env_file := self.args.env_file: # type: ignore
            if not os.path.abspath(env_file):
                env_file = os.path.join(self.original_dir, env_file)
                env_file = os.path.abspath(env_file)
            else:
                env_file = os.path.expanduser(env_file)

        options:'strdict' = {
            'sync_internal': self.args.sync_internal,
            'secret_key': self.args.secret_key or '',
            'stderr_path': self.args.stderr_path,
            'env_file': env_file,
            'stop_after': self.args.stop_after,
        }

        if extra_options:
            options.update(extra_options)

        exit_code = start_python_process(
            name, self.args.fg, py_path, program_dir, on_keyboard_interrupt, self.SYS_ERROR.FAILED_TO_START, options,
            stderr_path=self.args.stderr_path,
            stdin_data=self.stdin_data,
            env_vars=env_vars
        )

        if self.show_output:
            if not self.args.fg and self.verbose:
                self.logger.debug('Zato {} `{}` starting in background'.format(name, self.component_dir))
            else:
                # Print out the success message only if there is no specific exit code,
                # meaning that it is neither 0 nor None.
                if not exit_code:
                    self.logger.info('OK')

        return exit_code

# ################################################################################################################################

    def _handle_deploy_local_dir_impl(self, src_path:'str') -> 'anydict':
        return {'deploy_auto_from':src_path}

# ################################################################################################################################

    def _handle_deploy_local_dir(self, src_path:'str', *, delete_src_path:'bool'=False) -> 'dictnone':

        # Local aliases
        has_one_name    = False
        top_name_is_dir = False
        top_name_path   = 'zato-does-not-exist_handle_deploy_local_dir'
        should_recurse  = False
        top_name_is_not_internal = False

        # If there is only one directory inside the source path, we drill into it
        # because this is where we expect to find our assets to deploy.
        names = os.listdir(src_path)

        has_one_name   = len(names) == 1

        if has_one_name:
            top_name = names[0]
            top_name_path = os.path.join(src_path, top_name)
            top_name_is_dir = os.path.isdir(top_name_path)
            top_name_is_not_internal = not (top_name in ModuleCtx.Deploy_Dirs)

        should_recurse = top_name_is_dir and top_name_is_not_internal

        # .. if we have a single top-level directory, we can recurse into that ..
        if should_recurse:
            return self._handle_deploy_local_dir(top_name_path)

        else:
            # If we are here, we have a leaf location to actually deploy from ..
            return self._handle_deploy_local_dir_impl(src_path)

# ################################################################################################################################

    def _handle_deploy_local_zip(self, src_path:'str', *, delete_src_path:'bool'=False) -> 'dictnone':

        # Extract the file name for later use
        zip_name = os.path.basename(src_path)

        # This will be a new directory ..
        tmp_path = get_tmp_path(body='deploy')

        # .. do create it now ..
        os.mkdir(tmp_path)

        # .. move the archive to the new location ..
        _ = shutil_copy(src_path, tmp_path)

        # .. get the zip file new location's full path ..
        zip_file_path = os.path.join(tmp_path, zip_name)

        # .. do extract it now ..
        with ZipFile(zip_file_path) as zip_file:

            # .. first, run a CRC test ..
            result = zip_file.testzip()
            if result:
                raise ValueError(f'Zip contents CRC file error -> {result}')

            # .. we can proceed with the extraction ..
            zip_file.extractall(tmp_path)

        # .. always delete the temporary zip file ..
        os.remove(zip_file_path)

        # .. optionally, delete the original, source file ..
        if delete_src_path:
            os.remove(src_path)

        # .. we can now treat it as deployment from a local directory ..
        return self._handle_deploy_local_dir(tmp_path)

# ################################################################################################################################

    def _maybe_set_up_deploy(self) -> 'dictnone':

        # Local aliases
        env_from1 = os.environ.get('Zato_Deploy_From') or ''
        env_from2 = os.environ.get('ZATO_DEPLOY_FROM') or ''

        # Zato_Deploy_Auto_Path_To_Delete
        # Zato_Deploy_Auto_Enmasse

        # First goes the command line, then both of the environment variables
        deploy:'str' = self.args.deploy or env_from1 or env_from2 or ''

        # We have a resource to deploy ..
        if deploy:

            is_ssh   = deploy.startswith('ssh://')
            is_http  = deploy.startswith('http://')
            is_https = deploy.startswith('https//')
            is_local = not (is_ssh or is_http or is_https)

            # .. handle a local path ..
            if is_local:

                # .. this can be done upfront if it is a local path ..
                deploy = os.path.expanduser(deploy)

                # .. deploy local .zip archives ..
                if deploy.endswith('.zip'):

                    # .. do handle the input now ..
                    return self._handle_deploy_local_zip(deploy)

# ################################################################################################################################

    def _on_server(self, *ignored:'any_') -> 'int': # show_output was an old param, *ignored is safer for dispatch

        # redis
        import redis

        from zato.common.util.updates import setup_update_file_logger
        setup_update_file_logger(component_name='server')

        # Potentially sets up the deployment of any assets given on input
        extra_options = self._maybe_set_up_deploy()

        # Check basic configuration
        self.run_check_config()

        # Read Datadog config from Redis and set env vars
        env_vars = {}
        try:
            redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            main_agent = redis_client.get('zato:datadog:main_agent') or ''
            metrics_agent = redis_client.get('zato:datadog:metrics_agent') or ''
            if main_agent:
                env_vars['Zato_Datadog_Main_Agent'] = main_agent
            if metrics_agent:
                env_vars['Zato_Datadog_Metrics_Agent'] = metrics_agent
        except Exception:
            pass

        # Read Grafana Cloud config from Redis and set env vars
        try:
            redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            grafana_cloud_enabled = redis_client.get('zato:grafana_cloud:is_enabled') or ''
            if grafana_cloud_enabled == 'true':
                env_vars['Zato_Grafana_Cloud_Enabled'] = 'true'
        except Exception:
            pass

        # Start the server now
        return self.start_component(
            'zato.server.main',
            'server',
            self.component_dir,
            self.delete_pidfile,
            extra_options=extra_options,
            env_vars=env_vars
        )

# ################################################################################################################################

    def _on_web_admin(self, *ignored:'any_') -> 'None':
        # Zato
        from zato.common.json_internal import loads
        from zato.common.util import proc # For start_process
        from zato.common.util.updates import setup_update_file_logger

        # stdlib
        import os

        setup_update_file_logger(component_name='dashboard')

        self.run_check_config() # Keep this: checks basic config and ensures no existing pidfile (important)

        # --- Determine Zato code paths for PYTHONPATH ---
        # __file__ for start.py is e.g., /path/to/zato/code/zato-cli/src/zato/cli/start.py
        # We want to get to /path/to/zato/code/
        script_dir = os.path.dirname(__file__)  # .../zato-cli/src/zato/cli
        zato_cli_src_zato_dir = os.path.dirname(script_dir) # .../zato-cli/src/zato
        zato_cli_src_dir = os.path.dirname(zato_cli_src_zato_dir) # .../zato-cli/src
        zato_cli_code_dir = os.path.dirname(zato_cli_src_dir) # .../zato-cli
        zato_base_code_dir = os.path.dirname(zato_cli_code_dir) # .../code - This is the root for component src dirs

        zato_src_paths_to_add = [
            os.path.join(zato_base_code_dir, 'zato-common', 'src'),
            os.path.join(zato_base_code_dir, 'zato-web-admin', 'src'),
            # Add other Zato src directories if they become necessary for wsgi.py or its imports
            # e.g., os.path.join(zato_base_code_dir, 'zato-server', 'src'),
        ]

        current_pythonpath = os.environ.get('PYTHONPATH', '')
        # Prepend our paths to ensure they take precedence and handle existing paths
        new_pythonpath_parts = list(zato_src_paths_to_add) # Start with our new paths
        if current_pythonpath:
            new_pythonpath_parts.extend(current_pythonpath.split(os.pathsep))

        # Create a clean, unique list of paths
        unique_paths = []
        for p_item in new_pythonpath_parts:
            if p_item and p_item not in unique_paths:
                unique_paths.append(p_item)
        final_pythonpath = os.pathsep.join(unique_paths)

        # --- Configuration for Gunicorn ---
        component_path = self.component_dir # This is ZATO_DASHBOARD_BASE_DIR for the wsgi.py script
        web_admin_conf_path = os.path.join(component_path, 'config', 'repo', 'web-admin.conf')

        try:
            with open_r(web_admin_conf_path) as f:
                conf_content = f.read()
            web_admin_config = loads(conf_content)
            host = web_admin_config.get('host', '127.0.0.1')
            port = web_admin_config.get('port', 8183) # Default Zato web-admin port for Django dev server
        except Exception as e:
            self.logger.error(f'Error reading web-admin.conf for Gunicorn: {e}')
            # Consider exiting with self.SYS_ERROR.CONFIG_ERROR if critical
            return

        bind_address = f'{host}:{port}'
        workers = 8

        # Gunicorn PID file must match what `zato stop` expects: component_dir/pidfile
        pid_file = os.path.join(component_path, 'pidfile')

        # Log files for Gunicorn
        logs_dir = os.path.join(component_path, 'logs')
        os.makedirs(logs_dir, exist_ok=True) # Ensure logs directory exists
        access_log = os.path.join(logs_dir, 'gunicorn-access.log')

        if self.args.fg:
            error_log = '-'
        else:
            error_log = os.path.join(logs_dir, 'gunicorn-error.log')

        # Use the Zato Python interpreter to run Gunicorn
        zato_python = os.path.join(zato_base_code_dir, 'bin', 'python')
        gunicorn_executable = zato_python + ' -m gunicorn'
        wsgi_app_module = 'zato.admin.wsgi:application' # Path to the WSGI app object

        gunicorn_args = [
            wsgi_app_module,
            '--bind', bind_address,
            '--workers', str(workers),
            '--pid', pid_file,
            '--access-logfile', access_log,
            '--error-logfile', error_log,
            '--name', 'zato-dashboard', # Set desired process name
            '--timeout', '0',
        ]

        if not self.args.fg:
            gunicorn_args.append('--daemon')

        # Environment variables for Gunicorn process
        gunicorn_env_vars = os.environ.copy() # Start with a copy of current environment
        gunicorn_env_vars['Zato_Dashboard_Base_Dir'] = component_path
        gunicorn_env_vars['PYTHONPATH'] = final_pythonpath # Set the carefully constructed PYTHONPATH

        # For `proc.start_process`, `extra_cli_options` is a string.
        gunicorn_extra_cli_options = ' '.join(gunicorn_args)

        if 0:
            self.logger.debug(f'Gunicorn executable: {gunicorn_executable}')
            self.logger.debug(f'Gunicorn CLI options: {gunicorn_extra_cli_options}')
            self.logger.debug(f'Gunicorn working directory (implied by component_path for logs/pid): {component_path}')
            self.logger.debug(f'Gunicorn Zato_Dashboard_Base_Dir: {gunicorn_env_vars.get("Zato_Dashboard_Base_Dir")}')
            self.logger.debug(f'Gunicorn PYTHONPATH (inherited): {gunicorn_env_vars.get("PYTHONPATH", "Not explicitly set, inherited")}')

        self.logger.info(f'Dashboard started at {bind_address}')

        # `stderr_path` for `proc.start_process` captures Gunicorn's initial bootstrap errors.
        # Gunicorn's own `--error-logfile` handles its operational errors.
        if self.args.fg:
            gunicorn_bootstrap_stderr = self.args.stderr_path
        else:
            gunicorn_bootstrap_stderr = self.args.stderr_path or os.path.join(logs_dir, 'gunicorn-bootstrap-stderr.log')

        # `on_keyboard_interrupt` in `proc.start_process` gets called if the Zato wrapper (sarge) is interrupted.
        # Gunicorn, when run in foreground, handles SIGINT itself to gracefully shut down and remove its PID file.
        # If Gunicorn is daemonized, this Zato-level SIGINT handler isn't for Gunicorn directly.
        # `self.delete_pidfile` (passed from original start_component) is safe if Gunicorn failed before creating its PID,
        # or if Gunicorn cleans up its own PID on SIGINT anyway.
        on_interrupt_handler = self.delete_pidfile

        exit_code = proc.start_process(
            component_name='Dashboard', # Name for Zato's logging
            executable=gunicorn_executable,
            run_in_fg=self.args.fg, # Controls if `sarge.run` is blocking/async
            cli_options=None,       # Not a `python -m module` style invocation for Gunicorn
            extra_cli_options=gunicorn_extra_cli_options, # Gunicorn's own arguments
            on_keyboard_interrupt=on_interrupt_handler,
            failed_to_start_err=self.SYS_ERROR.FAILED_TO_START,
            env_vars=gunicorn_env_vars, # Pass environment to Gunicorn via the new parameter
            stderr_path=gunicorn_bootstrap_stderr,    # For initial Gunicorn errors
            stdin_data=self.stdin_data # Pass through stdin configuration
        )

        # This logging mimics what start_component would do via start_python_process's caller
        if self.show_output:
            if not self.args.fg:
                if exit_code == 0:
                    self.logger.debug('Zato Dashboard `{}` starting in background'.format(component_path))
                else:
                    self.logger.error(
                        'Zato Dashboard `{}` failed to start in background (sarge exit code: {}). Check logs.'.format(
                            component_path, exit_code
                        )
                    )
            # If in foreground, sarge blocks, and OK/error is determined by Gunicorn's actual exit code.
            # `proc.start_process` already handles logging errors from stderr if `wait_for_error` finds something.
            # If it's foreground and `proc.start_process` returns, Gunicorn has exited.
            # An explicit 'OK' might only be for successful daemonization or clean foreground exit.
            elif exit_code == 0: # Gunicorn exited cleanly in foreground
                self.logger.info('OK')
            else: # Gunicorn exited with an error in foreground
                log_msg_parts = [
                    f'Zato Dashboard `{component_path}` (Gunicorn) running in foreground exited with code {exit_code}.',
                    'To check logs, run:',
                    f'  Error log:         cat {error_log}',
                    f'  Access log:        cat {access_log}',
                    f'  Bootstrap log:     cat {gunicorn_bootstrap_stderr}',
                ]
                self.logger.error('\n'.join(log_msg_parts))

        # Original code was `_ = self.start_component(...)`, so no explicit return needed here.

# ################################################################################################################################

    def _on_scheduler(self, *ignored:'any_') -> 'None':
        from zato.common.util.updates import setup_update_file_logger
        setup_update_file_logger(component_name='scheduler')

        env_vars = {
            'Zato_Component_Dir': self.component_dir,
            'ZATO_SCHEDULER_BASE_DIR': self.component_dir
        }
        self.run_check_config()
        _ = self.check_pidfile()
        _ = self.start_component('zato.scheduler.main', 'scheduler', '', self.delete_pidfile, env_vars=env_vars)

# ################################################################################################################################
# ################################################################################################################################
