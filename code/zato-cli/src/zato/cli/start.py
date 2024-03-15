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
            self.logger.info('Pidfile `%s` could not be deleted `%s`', path, e)

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
            stdin_data=self.stdin_data)

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
        shutil_copy(src_path, tmp_path)

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

    def _on_server(self, show_output:'bool'=True, *ignored:'any_') -> 'int':

        # Potentially sets up the deployment of any assets given on input
        extra_options = self._maybe_set_up_deploy()

        # Check basic configuration
        self.run_check_config()

        # Start the server now
        return self.start_component(
            'zato.server.main',
            'server',
            self.component_dir,
            self.delete_pidfile,
            extra_options=extra_options
        )

# ################################################################################################################################

    def _on_lb(self, *ignored:'any_') -> 'None':

        # stdlib
        import os
        import sys

        # Zato
        from zato.cli.stop import Stop
        from zato.common.util.api import get_haproxy_agent_pidfile

        self.run_check_config()

        def stop_haproxy():
            Stop(self.args).stop_haproxy(self.component_dir)

        found_pidfile = self.check_pidfile()
        if not found_pidfile:
            found_agent_pidfile = self.check_pidfile(get_haproxy_agent_pidfile(self.component_dir))
            if not found_agent_pidfile:
                _ = self.start_component(
                    'zato.agent.load_balancer.main', 'load-balancer', os.path.join(self.config_dir, 'repo'), stop_haproxy)
                return

        # Will be returned if either of pidfiles was found
        sys.exit(self.SYS_ERROR.FOUND_PIDFILE)

# ################################################################################################################################

    def _on_web_admin(self, *ignored:'any_') -> 'None':
        self.run_check_config()
        _ = self.start_component('zato.admin.main', 'web-admin', '', self.delete_pidfile)

# ################################################################################################################################

    def _on_scheduler(self, *ignored:'any_') -> 'None':
        self.run_check_config()
        _ = self.check_pidfile()
        _ = self.start_component('zato.scheduler.main', 'scheduler', '', self.delete_pidfile)

# ################################################################################################################################
# ################################################################################################################################
