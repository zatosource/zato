# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ManageCommand
from zato.common.util.open_ import open_r

# ################################################################################################################################

class CheckConfig(ManageCommand):
    """ Checks config of a Zato component.
    """

# ################################################################################################################################

    def get_json_conf(self, conf_name, repo_dir=None):

        # stdlib
        from os.path import join

        # Zato
        from zato.common.json_internal import loads

        repo_dir = repo_dir or join(self.config_dir, 'repo')
        return loads(open_r(join(repo_dir, conf_name)).read())

# ################################################################################################################################

    def ensure_port_free(self, prefix, port, address):

        # Zato
        from zato.common.util.tcp import is_port_taken

        if is_port_taken(port):
            raise Exception('{} check failed. Address `{}` already taken.'.format(prefix, address))

# ################################################################################################################################

    def ensure_json_config_port_free(self, prefix, conf_name=None, conf=None):
        conf = self.get_json_conf(conf_name) if conf_name else conf
        address = '{}:{}'.format(conf['host'], conf['port'])
        self.ensure_port_free(prefix, conf['port'], address)

# ################################################################################################################################

    def ping_sql_odb(self, engine, sqlite_path):
        """ Opens the ODB file and runs a query against it.
        """
        # SQLAlchemy
        from sqlalchemy import create_engine, text

        # Zato
        from zato.common.util.api import get_engine_url

        engine_url = get_engine_url({'engine': engine, 'sqlite_path': sqlite_path})
        sql_engine = create_engine(engine_url)

        with sql_engine.connect() as connection:
            _ = connection.execute(text('SELECT 1'))

        sql_engine.dispose()

        if self.show_output:
            self.logger.info('SQL ODB connection OK')

# ################################################################################################################################

    def check_sql_odb_server(self, conf):
        self.ping_sql_odb(conf['odb']['engine'], conf['odb']['db_name'])

# ################################################################################################################################

    def check_sql_odb_web_admin(self, conf):
        self.ping_sql_odb(conf['db_type'], conf['DATABASE_NAME'])

# ################################################################################################################################

    def ensure_no_pidfile(self, log_file_marker):

        # stdlib
        from os.path import abspath, exists, join

        pidfile = abspath(join(self.component_dir, 'pidfile'))

        # Pidfile exists ..
        if exists(pidfile):

            # stdlib
            import os

            # psutil
            from psutil import AccessDenied, Process, NoSuchProcess

            # Zato
            from zato.common.api import INFO_FORMAT
            from zato.common.component_info import get_info

            # .. but raise an error only if the PID it points to belongs
            # to an already running component. Otherwise, it must be a stale pidfile
            # that we can safely delete.
            pid = open_r(pidfile).read().strip()
            try:
                if pid:
                    pid = int(pid)
            except ValueError:
                raise Exception('Could not parse pid value `{}` as an integer ({})'.format(pid, pidfile))
            else:
                try:
                    _ = get_info(self.component_dir, INFO_FORMAT.DICT)
                except AccessDenied:
                    # This could be another process /or/ it can be our own component started by another user,
                    # so to be on the safe side, indicate an error instead of deleting the pidfile
                    raise Exception('Access denied to PID `{}` found in `{}`'.format(pid, pidfile))
                except NoSuchProcess:
                    # This is fine, there is no process of that PID,
                    # which means that this PID does not belong to our component
                    # (because it doesn't belong to any process), so we may just delete this pidfile safely ..
                    try:
                        os.remove(pidfile)
                    except Exception:
                        pass

                else:
                    #
                    # This PID exists, but it still still possible that it belongs to another process
                    # that took over a PID previously assigned to a Zato component,
                    # in which case we can still delete the pidfile.
                    #
                    # We decide that a process is actually an already running Zato component if it has
                    # opened log files that should belong that kind of component, as indicated by log_file_marker,
                    # otherwise we assume this PID belongs to a completely different process and we can delete pidfile.
                    #
                    has_log = False
                    has_lock = False

                    log_path = abspath(join(self.component_dir, 'logs', '{}.log'.format(log_file_marker)))
                    lock_path = abspath(join(self.component_dir, 'logs', '{}.lock'.format(log_file_marker)))

                    if pid:
                        for name in Process(pid).open_files():
                            if name.path == log_path:
                                has_log = True
                            elif name.path == lock_path:
                                has_lock = True

                    # Both files exist - this is our component and it's running so we cannot continue
                    if has_log and has_lock:
                        raise Exception('Cannot proceed, found pidfile `{}`'.format(pidfile))

                    # This must be an unrelated process, so we can delete pidfile ..
                    try:
                        os.remove(pidfile)
                    except Exception:
                        pass

        if self.show_output:
            self.logger.info('No such pidfile `%s`, OK', pidfile)

# ################################################################################################################################

    def on_server_check_port_available(self, server_conf):

        address = server_conf['main']['bind']
        _, port = address.split(':')
        self.ensure_port_free('Server', int(port), address)

# ################################################################################################################################

    def get_crypto_manager(self, secret_key=None, stdin_data=None, class_=None):

        # stdlib
        from os.path import join

        return class_.from_repo_dir(secret_key, join(self.config_dir, 'repo'), stdin_data)

# ################################################################################################################################

    def _on_server(self, args):

        # stdlib
        from os.path import join

        # Zato
        from zato.common.ext.configobj_ import ConfigObj

        # Zato
        from zato.common.crypto.api import ServerCryptoManager

        cm = self.get_crypto_manager(getattr(args, 'secret_key', None), getattr(args, 'stdin_data', None),
            class_=ServerCryptoManager)

        repo_dir = join(self.component_dir, 'config', 'repo')
        server_conf_path = join(repo_dir, 'server.conf')
        secrets_conf_path = ConfigObj(join(repo_dir, 'secrets.conf'), use_zato=False)
        server_conf = ConfigObj(server_conf_path, zato_secrets_conf=secrets_conf_path, zato_crypto_manager=cm, use_zato=True)

        self.check_sql_odb_server(server_conf)

        if getattr(args, 'ensure_no_pidfile', False):
            self.ensure_no_pidfile('server')

        if getattr(args, 'check_server_port_available', False):
            self.on_server_check_port_available(server_conf)

# ################################################################################################################################

    def _on_web_admin(self, args, *ignored_args, **ignored_kwargs):

        # stdlib
        from os.path import join

        repo_dir = join(self.component_dir, 'config', 'repo')

        self.check_sql_odb_web_admin(self.get_json_conf('web-admin.conf', repo_dir))

        self.ensure_no_pidfile('web-admin')
        self.ensure_json_config_port_free('Web admin', 'web-admin.conf')

# ################################################################################################################################

    def _on_scheduler(self, args, *ignored_args, **ignored_kwargs):
        self.ensure_no_pidfile('scheduler')

# ################################################################################################################################
