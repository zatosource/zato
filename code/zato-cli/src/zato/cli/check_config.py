# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
from distutils.version import LooseVersion
from json import loads
from os.path import abspath, exists, join

# Bunch
from bunch import Bunch

# ConfigObj
from configobj import ConfigObj

# psutil
from psutil import AccessDenied, Process, NoSuchProcess

# Zato
from zato.cli import ManageCommand
from zato.common import INFO_FORMAT
from zato.common.component_info import get_info
from zato.common.crypto import CryptoManager
from zato.common.kvdb import KVDB
from zato.common.haproxy import validate_haproxy_config
from zato.common.odb import create_pool, ping_queries
from zato.common.util import is_port_taken

class CheckConfig(ManageCommand):
    """ Checks config of a Zato component.
    """
    def get_json_conf(self, conf_name, repo_dir=None):
        repo_dir = repo_dir or join(self.config_dir, 'repo')
        return loads(open(join(repo_dir, conf_name)).read())

    def ensure_port_free(self, prefix, port, address):
        if is_port_taken(port):
            raise Exception('{} check failed. Address `{}` already taken.'.format(prefix, address))

    def ensure_json_config_port_free(self, prefix, conf_name=None, conf=None):
        conf = self.get_json_conf(conf_name) if conf_name else conf
        address = '{}:{}'.format(conf['host'], conf['port'])
        self.ensure_port_free(prefix, conf['port'], address)

    def ping_sql(self, cm, engine_params):

        query = ping_queries[engine_params['engine']]

        session = create_pool(cm, engine_params)
        session.execute(query)
        session.close()

        if self.show_output:
            self.logger.info('SQL ODB connection OK')

    def check_sql_odb_server_scheduler(self, cm, conf):
        engine_params = dict(conf['odb'].items())
        engine_params['extra'] = {}
        engine_params['pool_size'] = 1
        self.ping_sql(cm, engine_params)

    def check_sql_odb_web_admin(self, cm, conf):
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

        self.ping_sql(cm, engine_params)

    def on_server_check_kvdb(self, cm, conf, conf_key='kvdb'):

        kvdb_config = Bunch(dict(conf[conf_key].items()))
        kvdb = KVDB(None, kvdb_config, cm.decrypt)
        kvdb.init()

        minimum = '2.8.4'

        info = kvdb.conn.info()
        redis_version = info.get('redis_version')

        if not redis_version:
            raise Exception('Could not obtain `redis_version` from {}'.format(info))

        if not LooseVersion(redis_version) >= LooseVersion(minimum):
            raise Exception('Redis version required: `{}` or later, found:`{}`'.format(minimum, redis_version))

        kvdb.close()

        if self.show_output:
            self.logger.info('Redis connection OK')

    def ensure_no_pidfile(self, log_file_marker):
        pidfile = abspath(join(self.component_dir, 'pidfile'))

        # Pidfile exists ..
        if exists(pidfile):

            # .. but raise an error only if the PID it points to belongs
            # to an already running component. Otherwise, it must be a stale pidfile
            # that we can safely delete.
            pid = open(pidfile).read().strip()
            try:
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
                    os.remove(pidfile)

                    # .. but, if the component is load-balancer, we also need to delete its agent's pidfile.
                    # The assumption is that if the load-balancer is not running then so isn't its agent.
                    if log_file_marker == 'lb-agent':
                        lb_agent_pidfile = abspath(join(self.component_dir, 'zato-lb-agent.pid'))
                        os.remove(lb_agent_pidfile)

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

                    for name in Process(pid).open_files():
                        if name.path == log_path:
                            has_log = True
                        elif name.path == lock_path:
                            has_lock = True

                    # Both files exist - this is our component and it's running so we cannot continue
                    if has_log and has_lock:
                        raise Exception('Cannot proceed, found pidfile `{}`'.format(pidfile))

                    # This must be an unrelated process, so we can delete pidfile ..
                    os.remove(pidfile)

                    # .. again, if the component is load-balancer, we also need to delete its agent's pidfile.
                    # The assumption is that if the load-balancer is not running then so isn't its agent.
                    if log_file_marker == 'lb-agent':
                        lb_agent_pidfile = abspath(join(self.component_dir, 'zato-lb-agent.pid'))
                        os.remove(lb_agent_pidfile)

        if self.show_output:
            self.logger.info('No such pidfile `%s`, OK', pidfile)

    def on_server_check_port_available(self, server_conf):
        address = server_conf['main']['gunicorn_bind']
        _, port = address.split(':')
        self.ensure_port_free('Server', int(port), address)

    def get_crypto_manager_conf(self, conf_file=None, priv_key_location=None, repo_dir=None):
        repo_dir = repo_dir or join(self.config_dir, 'repo')
        conf = None

        if not priv_key_location:
            conf = ConfigObj(join(repo_dir, conf_file))
            priv_key_location = priv_key_location or abspath(join(repo_dir, conf['crypto']['priv_key_location']))

        cm = CryptoManager(priv_key_location=priv_key_location)
        cm.load_keys()

        return cm, conf

    def _on_server(self, args):
        cm, conf = self.get_crypto_manager_conf('server.conf')

        self.check_sql_odb_server_scheduler(cm, conf)
        self.on_server_check_kvdb(cm, conf)

        if getattr(args, 'ensure_no_pidfile', False):
            self.ensure_no_pidfile('server')

        if getattr(args, 'check_server_port_available', False):
            self.on_server_check_port_available(conf)

    def _on_lb(self, *ignored_args, **ignored_kwargs):
        self.ensure_no_pidfile('lb-agent')
        repo_dir = join(self.config_dir, 'repo')

        lba_conf = self.get_json_conf('lb-agent.conf')
        lb_conf_string = open(join(repo_dir, 'zato.config')).read()

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

    def _on_web_admin(self, *ignored_args, **ignored_kwargs):
        repo_dir = join(self.component_dir, 'config', 'repo')

        self.check_sql_odb_web_admin(
            self.get_crypto_manager_conf(priv_key_location=join(repo_dir, 'web-admin-priv-key.pem'), repo_dir=repo_dir)[0],
            self.get_json_conf('web-admin.conf', repo_dir))

        self.ensure_no_pidfile('web-admin')
        self.ensure_json_config_port_free('Web admin', 'web-admin.conf')

    def _on_scheduler(self, *ignored_args, **ignored_kwargs):
        cm, conf = self.get_crypto_manager_conf('scheduler.conf')

        self.check_sql_odb_server_scheduler(cm, conf)
        self.on_server_check_kvdb(cm, conf, 'broker')

        self.ensure_no_pidfile('scheduler')
