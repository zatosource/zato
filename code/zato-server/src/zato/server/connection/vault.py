# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

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
from zato.common.api import UNITTEST
from zato.common.vault_ import VAULT

# ################################################################################################################################

basicConfig(level=INFO, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################

class VaultResponse:
    """ A convenience class to hold individual attributes of responses from Vault.
    """
    __slots__ = ('action', 'client_token', 'lease_duration', 'accessor', 'policies')

    def __init__(self, action=None, client_token=None, lease_duration=None, accessor=None, policies=None):
        self.action = action
        self.client_token = client_token
        self.lease_duration = lease_duration
        self.accessor = accessor
        self.policies = policies

    def __str__(self):
        attrs = []
        for elem in sorted(self.__slots__):
            value = getattr(self, elem)
            attrs.append('{}:{}'.format(elem, value))

        return '<{} at {}, {}>'.format(self.__class__.__name__, hex(id(self)), ', '.join(attrs))

    @staticmethod
    def from_vault(action, response, main_key='auth', token_key='client_token', has_lease_duration=True):
        """ Builds a VaultResponse out of a dictionary returned from Vault.
        """
        auth = response[main_key]

        vr = VaultResponse(action)
        vr.client_token = auth[token_key]
        vr.accessor = auth['accessor']
        vr.policies = auth['policies']

        if has_lease_duration:
            vr.lease_duration = auth['lease_duration']

        return vr

# ################################################################################################################################

class _Client(Client):
    """ A thin wrapper around hvac.Client providing connectivity to Vault.
    """
    def __init__(self, *args, **kwargs):
        super(_Client, self).__init__(*args, **kwargs)
        self._auth_func = {
            VAULT.AUTH_METHOD.TOKEN.id: self._auth_token,
            VAULT.AUTH_METHOD.USERNAME_PASSWORD.id: self._auth_username_password,
            VAULT.AUTH_METHOD.GITHUB.id: self._auth_github,
        }

    def ping(self):
        return self.is_sealed

    def _auth_token(self, client_token, _from_vault=VaultResponse.from_vault):
        if not client_token:
            raise ValueError('Client token missing on input')

        response = self.lookup_token(client_token)
        return _from_vault('auth_token', response, 'data', 'id', False)

    def _auth_username_password(self, username, password, mount_point='userpass', _from_vault=VaultResponse.from_vault):
        login_response = self.auth_userpass(username, password, mount_point, use_token=False)
        return _from_vault('auth_userpass', login_response)

    def _auth_github(self, gh_token, _from_vault=VaultResponse.from_vault):
        login_response = self.auth_github(gh_token, use_token=False)
        return _from_vault('auth_github', login_response)

    def renew(self, client_token, _from_vault=VaultResponse.from_vault):
        login_response = self.renew_token(client_token)
        return _from_vault('renew', login_response)

    def authenticate(self, auth_method, *credentials):
        return self._auth_func[auth_method](*credentials)

# ################################################################################################################################

class _VaultConn:
    def __init__(self, name, url, token, service_name, tls_verify, timeout, allow_redirects, client_class=_Client,
            requests_adapter=None):
        self.name = name
        self.url = url
        self.token = token
        self.service_name = service_name
        self.tls_verify = tls_verify
        self.timeout = timeout
        self.allow_redirects = allow_redirects
        self.client = client_class(self.url, self.token, verify=self.tls_verify, timeout=self.timeout,
                allow_redirects=self.allow_redirects, adapter=requests_adapter)

# ################################################################################################################################

class VaultConnAPI:
    """ An API through which connections to Vault are established and managed.
    """
    def __init__(self, config_list=None, requests_adapter=None):
        self.config = Bunch()
        self.lock = RLock()
        self.requests_adapter = requests_adapter

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
        except Exception:
            logger.warning('Could not ping Vault connection `%s`, e:`%s`', name, format_exc())
        else:
            logger.info('Ping OK, Vault connection `%s`', name)

    def ping(self, name):
        spawn(self._ping, name)

# ################################################################################################################################

    def _create(self, config):
        conn = _VaultConn(
            config.name, config.url, config.token, config.get('service_name'), config.tls_verify, config.timeout,
            config.allow_redirects, requests_adapter=self.requests_adapter)
        self.config[config.name] = conn

        if config.url != UNITTEST.VAULT_URL:
            self.ping(config.name)

# ################################################################################################################################

    def create(self, config):
        with self.lock:
            self._create(config)

# ################################################################################################################################

    def _delete(self, name):
        try:
            self.config[name].client.close()
        except Exception:
            logger.warning(format_exc())
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
    client_token = '5f763fa3-2872-71ab-4e5d-f1398aca6637'
    username = 'user1'
    password = 'secret1'
    gh_token = ''

    config = Bunch()
    config.name = name
    config.url = 'https://localhost:49517'
    config.token = client_token
    config.service_name = 'my.service'
    config.tls_verify = True
    config.timeout = 20
    config.allow_redirects = True

    api = VaultConnAPI([config])

    import time
    time.sleep(0.1)

    response1 = api[name].client.authenticate(VAULT.AUTH_METHOD.TOKEN.id, client_token)
    logger.info('Response1 %s', response1)

    response2 = api[name].client.authenticate(VAULT.AUTH_METHOD.USERNAME_PASSWORD.id, username, password)
    logger.info('Response2 %s', response2)
    api[name].client.authenticate(VAULT.AUTH_METHOD.TOKEN.id, response2.client_token)
    api[name].client.renew_token(response2.client_token)

    if gh_token:
        token3 = api[name].client.authenticate(VAULT.AUTH_METHOD.GITHUB.id, gh_token)
        api[name].client.authenticate(VAULT.AUTH_METHOD.TOKEN.id, token3)
        api[name].client.renew_token(token3)
        logger.info('Token3 %s', token3)

    response = api[name].client.renew(response2.client_token)
    logger.info('Renew 11 %s', bunchify(response))

# ################################################################################################################################
