# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from gevent.monkey import patch_all
patch_all()

# stdlib
from logging import basicConfig, getLogger, INFO
from traceback import format_exc

# Bunch
from bunch import Bunch, bunchify

# gevent
from gevent import spawn
from gevent.lock import RLock

# Vault
from hvac import Client

# Zato
from zato.common import VAULT
from zato.server.config import ConfigDict

# ################################################################################################################################

basicConfig(level=INFO, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################

class _Client(Client):

    def __init__(self, *args, **kwargs):
        super(_Client, self).__init__(*args, **kwargs)
        self._auth_func = {
            VAULT.AUTH_METHOD.TOKEN: self._auth_token,
            VAULT.AUTH_METHOD.USERNAME_PASSWORD: self._auth_username_password,
            VAULT.AUTH_METHOD.GITHUB: self._auth_github,
        }

    def ping(self):
        return self.is_sealed()

    def _auth_token(self, vault_token):
        return self.lookup_token(vault_token)['data']['id']

    def _auth_username_password(self, username, password):
        return self.auth_userpass(username, password, use_token=False)['auth']['client_token']

    def _auth_github(self, gh_token):
        return self.auth_github(gh_token, use_token=False)

    def authenticate(self, auth_method, *credentials):
        return self._auth_func[auth_method](*credentials)

# ################################################################################################################################

class _VaultConn(object):
    def __init__(self, name, url, token, service_name, tls_verify, timeout, allow_redirects):
        self.name = name
        self.url = url
        self.token = token
        self.service_name = service_name
        self.tls_verify = tls_verify
        self.timeout = timeout
        self.allow_redirects = allow_redirects
        self.client = _Client(self.url, self.token, verify=self.tls_verify, timeout=self.timeout,
                allow_redirects=self.allow_redirects)

# ################################################################################################################################

class VaultConnAPI(object):
    """ An API through which connections to Vault are established and managed.
    """
    def __init__(self, config_list=None):
        self.config = Bunch()
        self.lock = RLock()

        for config in config_list or []:
            self.create(config)

# ################################################################################################################################

    def __getitem__(self, name):
        return self.config[name]

# ################################################################################################################################

    def get(self, name):
        return self.config.get(name)

# ################################################################################################################################

    def get_client(self, name):
        return self.config[name].client

# ################################################################################################################################

    def _ping(self, name):
        try:
            self.config[name].client.ping()
        except Exception, e:
            logger.warn('Could not ping Vault connection `%s`, e:`%s`', name, format_exc(e))
        else:
            logger.info('Ping OK, Vault connection `%s`', name)

    def ping(self, name):
        spawn(self._ping, name)

# ################################################################################################################################

    def _create(self, config):
        conn = _VaultConn(
            config.name, config.url, config.token, config.get('service_name'), config.tls_verify, config.timeout,
            config.allow_redirects)
        self.config[config.name] = conn
        self.ping(config.name)

# ################################################################################################################################

    def create(self, config):
        with self.lock:
            self._create(config)

# ################################################################################################################################

    def _delete(self, name):
        try:
            self.config[name].client.close()
        except Exception, e:
            logger.warn(format_exc(e))
        finally:
            del self.config[name]

# ################################################################################################################################

    def delete(self, name):
        with self.lock:
            self._delete(name)

# ################################################################################################################################

    def edit(self, new_config):
        with self.lock:
            self._delete(new_config.old_name)
            self._create(new_config)

# ################################################################################################################################

if __name__ == '__main__':

    name = 'abc'
    vault_token = '5f763fa3-2872-71ab-4e5d-f1398aca6637'
    username = 'user1'
    password = 'secret1'
    gh_token = ''

    config = Bunch()
    config.name = name
    config.url = 'http://localhost:49517'
    config.token = vault_token
    config.service_name = 'my.service'
    config.tls_verify = True
    config.timeout = 20
    config.allow_redirects = True

    api = VaultConnAPI([config])

    import time
    time.sleep(0.1)

    token1 = api[name].client.authenticate(VAULT.AUTH_METHOD.TOKEN, vault_token)
    logger.info('Token1 %s', token1)

    token2 = api[name].client.authenticate(VAULT.AUTH_METHOD.USERNAME_PASSWORD, username, password)
    api[name].client.authenticate(VAULT.AUTH_METHOD.TOKEN, token2)
    api[name].client.renew_token(token2)
    logger.info('Token2 %s', token2)

# ################################################################################################################################
