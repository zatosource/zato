# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
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

class CheckConfig(ManageCommand):
    """ Checks config of a Zato component (currently limited to servers only)
    """
    # TODO: Make it handle more components
    def _on_server(self, args):
        
        repo_dir = join(self.config_dir, 'repo')
        server_conf = ConfigObj(join(repo_dir, 'server.conf'))

        cm = CryptoManager(priv_key_location=abspath(join(repo_dir, server_conf['crypto']['priv_key_location'])))
        cm.load_keys()
        
        engine_params = dict(server_conf['odb'].items())
        engine_params['extra'] = {}
        engine_params['pool_size'] = 1
        
        query = ping_queries[engine_params['engine']]
        
        session = create_pool(cm, engine_params)
        session.execute(query)
        session.close()
        
        if self.show_output:
            self.logger.info('SQL ODB connection OK')
        
        kvdb_config = Bunch(dict(server_conf['kvdb'].items()))
        kvdb = KVDB(None, kvdb_config, cm.decrypt)
        kvdb.init()
        
        kvdb.conn.info()
        kvdb.close()
        
        if self.show_output:
            self.logger.info('Redis connection OK')

    def _on_lb(self, *ignored_args, **ignored_kwargs):
        self.logger.info('This command works with servers only')
        
    _on_web_admin = _on_lb
