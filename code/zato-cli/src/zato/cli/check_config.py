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

    def ping_sql(self, engine_params, ping_query):

        # Zato
        from zato.common.odb import ping_database

        ping_database(engine_params, ping_query)

        if self.show_output:
            self.logger.info('SQL ODB connection OK')

# ################################################################################################################################

    def check_sql_odb_server_scheduler(self, cm, conf, fs_sql_config, needs_decrypt_password=True):

        # Zato
        from zato.common.odb.ping import get_ping_query

        engine_params = dict((conf['odb']))
        engine_params['extra'] = {}
        engine_params['pool_size'] = 1

        # This will be needed by scheduler but not server
        if needs_decrypt_password:
            password = engine_params['password']
            if password:
                engine_params['password'] = cm.decrypt(password)

        self.ping_sql(engine_params, get_ping_query(fs_sql_config, engine_params))

# ################################################################################################################################

    def check_sql_odb_web_admin(self, cm, conf):

        # Zato
        from zato.common.api import ping_queries

        pairs = (
            ('engine', 'db_type'),
            ('username', 'DATABASE_USER'),
            ('password', 'DATABASE_PASSWORD'),
            ('host', 'DATABASE_HOST'),
            ('port', 'DATABASE_PORT'),
            ('db_name', 'DATABASE_NAME'),
        )
        engine_params = {'extra':{}, 'pool_size':1}
        for sqlalch_name, django_name in pairs:
            engine_params[sqlalch_name] = conf[django_name]
        password = engine_params['password']
        if password:
            engine_params['password'] = cm.decrypt(password)

        self.ping_sql(engine_params, ping_queries[engine_params['engine']])

# ################################################################################################################################

    def on_server_check_kvdb(self, cm, conf, conf_key='kvdb'):

        # Bunch
        from bunch import Bunch

        # Zato
        from zato.common.kvdb.api import KVDB

        # Redis is not configured = we can return
        kvdb_config = conf.get(conf_key) or {}
        if not kvdb_config:
            return

        # Redis is not enabled = we can return
        if not KVDB.is_config_enabled(kvdb_config):
            return

        kvdb_config = Bunch(kvdb_config)

        kvdb = KVDB(kvdb_config, cm.decrypt)
        kvdb.init()
        kvdb.conn.info()
        kvdb.close()

        if self.show_output:
            self.logger.info('Redis connection OK')

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
                    get_info(self.component_dir, INFO_FORMAT.DICT)
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

                    # .. but, if the component is load-balancer, we also need to delete its agent's pidfile.
                    # The assumption is that if the load-balancer is not running then so isn't its agent.
                    if log_file_marker == 'lb-agent':
                        lb_agent_pidfile = abspath(join(self.component_dir, 'zato-lb-agent.pid'))
                        try:
                            os.remove(lb_agent_pidfile)
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

                    # .. again, if the component is load-balancer, we also need to delete its agent's pidfile.
                    # The assumption is that if the load-balancer is not running then so isn't its agent.
                    if log_file_marker == 'lb-agent':
                        lb_agent_pidfile = abspath(join(self.component_dir, 'zato-lb-agent.pid'))
                        try:
                            os.remove(lb_agent_pidfile)
                        except Exception:
                            pass

        if self.show_output:
            self.logger.info('No such pidfile `%s`, OK', pidfile)

# ################################################################################################################################

    def on_server_check_port_available(self, server_conf):

        address = server_conf['main']['gunicorn_bind']
        _, port = address.split(':')
        self.ensure_port_free('Server', int(port), address)

# ################################################################################################################################

    def get_crypto_manager(self, secret_key=None, stdin_data=None, class_=None):

        # stdlib
        from os.path import join

        return class_.from_repo_dir(secret_key, join(self.config_dir, 'repo'), stdin_data)

# ################################################################################################################################

    def get_sql_ini(self, conf_file, repo_dir=None):

        # stdlib
        from os.path import join

        # Zato
        from zato.common.ext.configobj_ import ConfigObj

        repo_dir = repo_dir or join(self.config_dir, 'repo')
        return ConfigObj(join(repo_dir, conf_file))

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

        fs_sql_config = self.get_sql_ini('sql.conf')
        repo_dir = join(self.component_dir, 'config', 'repo')
        server_conf_path = join(repo_dir, 'server.conf')
        secrets_conf_path = ConfigObj(join(repo_dir, 'secrets.conf'), use_zato=False)
        server_conf = ConfigObj(server_conf_path, zato_secrets_conf=secrets_conf_path, zato_crypto_manager=cm, use_zato=True)

        self.check_sql_odb_server_scheduler(cm, server_conf, fs_sql_config, False)

        if getattr(args, 'ensure_no_pidfile', False):
            self.ensure_no_pidfile('server')

        if getattr(args, 'check_server_port_available', False):
            self.on_server_check_port_available(server_conf)

# ################################################################################################################################

    def _on_lb(self, args, *ignored_args, **ignored_kwargs):

        # stdlib
        from os.path import join

        # Zato
        from zato.common.haproxy import validate_haproxy_config

        self.ensure_no_pidfile('lb-agent')
        repo_dir = join(self.config_dir, 'repo')

        lba_conf = self.get_json_conf('lb-agent.conf')
        lb_conf_string = open_r(join(repo_dir, 'zato.config')).read()

        # Load-balancer's agent
        self.ensure_json_config_port_free('Load balancer\'s agent', None, lba_conf)

        # Load balancer itself
        lb_address = None
        marker = 'ZATO frontend front_http_plain:bind'
        lb_conf = lb_conf_string.splitlines()
        for line in lb_conf:
            if marker in line:
                lb_address = line.split(marker)[0].strip().split()[1]
                break

        if not lb_address:
            raise Exception('Load balancer check failed. Marker line not found `{}`.'.format(marker))

        _, port = lb_address.split(':')
        self.ensure_port_free('Load balancer', int(port), lb_address)

        validate_haproxy_config(lb_conf_string, lba_conf['haproxy_command'])

# ################################################################################################################################

    def _on_web_admin(self, args, *ignored_args, **ignored_kwargs):

        # stdlib
        from os.path import join

        # Zato
        from zato.common.crypto.api import WebAdminCryptoManager
        from zato.common.crypto.secret_key import resolve_secret_key

        repo_dir = join(self.component_dir, 'config', 'repo')

        secret_key = getattr(args, 'secret_key', None)
        secret_key = resolve_secret_key(secret_key)

        self.check_sql_odb_web_admin(
            self.get_crypto_manager(secret_key, getattr(args, 'stdin_data', None), WebAdminCryptoManager),
            self.get_json_conf('web-admin.conf', repo_dir))

        self.ensure_no_pidfile('web-admin')
        self.ensure_json_config_port_free('Web admin', 'web-admin.conf')

# ################################################################################################################################

    def _on_scheduler(self, args, *ignored_args, **ignored_kwargs):

        # stdlib
        from os.path import join

        # Zato
        from zato.common.crypto.api import SchedulerCryptoManager
        from zato.common.ext.configobj_ import ConfigObj

        repo_dir = join(self.component_dir, 'config', 'repo')
        server_conf_path = join(repo_dir, 'scheduler.conf')

        cm = self.get_crypto_manager(getattr(args, 'secret_key', None), getattr(args, 'stdin_data', None), SchedulerCryptoManager)

        secrets_conf_path = ConfigObj(join(repo_dir, 'secrets.conf'), use_zato=False)
        server_conf = ConfigObj(server_conf_path, zato_secrets_conf=secrets_conf_path, zato_crypto_manager=cm, use_zato=True)

        # ODB is optional for schedulers
        if 'odb' in server_conf:
            fs_sql_config = self.get_sql_ini('sql.conf')
            self.check_sql_odb_server_scheduler(cm, server_conf, fs_sql_config)
            self.ensure_no_pidfile('scheduler')

# ################################################################################################################################
