# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from glob import glob
from json import loads
from os.path import abspath, join

# Bunch
from bunch import Bunch

# ConfigObj
from configobj import ConfigObj

# Zato
from zato.cli import ManageCommand
from zato.common.crypto import CryptoManager
from zato.common.kvdb import KVDB
from zato.common.odb import create_pool, ping_queries
from zato.common.util import is_port_taken

class CheckConfig(ManageCommand):
    """ Checks config of a Zato component (currently limited to servers only)
    """
    def ensure_port_free(self, prefix, port, address):
        if is_port_taken(port):
            raise Exception('{} check failed. Address `{}` already taken.'.format(prefix, address))

    def ensure_json_config_port_free(self, conf_name, prefix):
        repo_dir = join(self.config_dir, 'repo')
        conf = loads(open(join(repo_dir, conf_name)).read())
        address = '{}:{}'.format(conf['host'], conf['port'])
        self.ensure_port_free(prefix, conf['port'], address)

    def on_server_check_sql_odb(self, cm, server_conf, repo_dir):

        engine_params = dict(server_conf['odb'].items())
        engine_params['extra'] = {}
        engine_params['pool_size'] = 1
        
        query = ping_queries[engine_params['engine']]

        session = create_pool(cm, engine_params)
        session.execute(query)
        session.close()

        if self.show_output:
            self.logger.info('SQL ODB connection OK')

    def on_server_check_kvdb(self, cm, server_conf):

        kvdb_config = Bunch(dict(server_conf['kvdb'].items()))
        kvdb = KVDB(None, kvdb_config, cm.decrypt)
        kvdb.init()
        
        kvdb.conn.info()
        kvdb.close()

        if self.show_output:
            self.logger.info('Redis connection OK')

    def on_server_check_stale_unix_socket(self):
        zdaemon_dir = abspath(join(self.config_dir, 'zdaemon'))
        results = glob(join(zdaemon_dir, '*.sock'))
        if results:
            len_results = len(results)
            count, suffix = ('a', '') if len_results == 1 else (len_results, 's')
            sockets = results[0] if len_results == 1 else ', '.join(results)
            raise Exception('Found {} stale socket{} to manual deletion: {}'.format(count, suffix, sockets))

        if self.show_output:
            self.logger.info('No stale sockets found in {}, OK'.format(zdaemon_dir))

    def on_server_check_port_available(self, server_conf):
        address = server_conf['main']['gunicorn_bind']
        _, port = address.split(':')
        self.ensure_port_free('Server', int(port), address)

    def _on_server(self, args):
        repo_dir = join(self.config_dir, 'repo')
        server_conf = ConfigObj(join(repo_dir, 'server.conf'))

        cm = CryptoManager(priv_key_location=abspath(join(repo_dir, server_conf['crypto']['priv_key_location'])))
        cm.load_keys()

        self.on_server_check_sql_odb(cm, server_conf, repo_dir)
        self.on_server_check_kvdb(cm, server_conf)
        self.on_server_check_port_available(server_conf)

        # enmasse actually needs a sockets because it means a server is running
        # so we can't quit if one is available.
        if getattr(args, 'check_stale_server_sockets', True):
            self.on_server_check_stale_unix_socket()

    def _on_lb(self, *ignored_args, **ignored_kwargs):
        repo_dir = join(self.config_dir, 'repo')

        # Load-balancer's agent
        self.ensure_json_config_port_free('lb-agent.conf', 'Load balancer agent')

        # Load balancer itself
        lb_address = None
        marker = 'ZATO frontend front_http_plain:bind'
        lb_conf = open(join(repo_dir, 'zato.config')).read().splitlines()
        for line in lb_conf:
            if marker in line:
                lb_address = line.split(marker)[0].strip().split()[1]
                break

        if not lb_address:
            raise Exception('Load balancer check failed. Marker line not found `{}`.'.format(marker))

        _, port = lb_address.split(':')
        self.ensure_port_free('Load balancer', int(port), lb_address)

    def _on_web_admin(self, *ignored_args, **ignored_kwargs):
        self.ensure_json_config_port_free('web-admin.conf', 'Web admin')
