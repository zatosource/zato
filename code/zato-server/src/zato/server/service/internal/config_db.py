# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Config DB - services behind the Dashboard screen that configures the Redis connection of the server.
# The screen drives the [redis] section of server.conf, persisted on disk and applied live to the Redis client of the cache.

# stdlib
from logging import getLogger
from time import time

# Zato
from zato.common.broker_message import Server as BrokerMessageServer
from zato.common.redis_env import get_redis_conn_from_values, get_redis_values_from_section
from zato.common.util.config import get_config_object, update_config_file
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_redis_service_prefix = 'zato.config-db.redis.'

# ################################################################################################################################
# ################################################################################################################################

# The keys of the [redis] section of server.conf the Redis screen saves, mapped from the form fields
_redis_conf_keys = {
    'host':          'host',
    'port':          'port',
    'db':            'db',
    'username':      'username',
    'ssl':           'ssl',
    'ssl_ca_file':   'ssl_ca_file',
    'ssl_cert_file': 'ssl_cert_file',
    'ssl_key_file':  'ssl_key_file',
    'ssl_verify':    'ssl_verify',
}

# ################################################################################################################################
# ################################################################################################################################

class RedisGet(AdminService):
    """ Returns the current configuration of the server's Redis connection,
    read from the [redis] section of server.conf.
    """
    name = _redis_service_prefix + 'get'

    def handle(self):

        # The on-disk section is the source of truth for what was saved ..
        config = get_config_object(self.server.repo_location, 'server.conf')
        values = get_redis_values_from_section(config['redis'])

        # .. the on-disk password is an encrypted pointer, never shown in the form.
        values['password'] = ''

        self.response.payload = {
            'success': True,
            'values': values,
        }

# ################################################################################################################################
# ################################################################################################################################

class RedisTest(AdminService):
    """ Connects to a Redis server described by the submitted form values and pings it.
    """
    name = _redis_service_prefix + 'test'

    def handle(self):

        values = self.request.raw['values']

        # The port and the database number arrive as strings from the form
        values['port'] = int(values['port'])
        values['db']   = int(values['db'])

        try:
            # Build a throwaway client out of the submitted values ..
            conn = get_redis_conn_from_values(values)

            # .. ping the server and time it ..
            start = time()
            _ = conn.ping()
            response_time = round(time() - start, 3)

            # .. the client is not needed anymore.
            conn.close()

            self.response.payload = {
                'success': True,
                'message': f'Connection OK, response time: {response_time}s',
            }

        except Exception as e:
            self.response.payload = {
                'success': False,
                'error': str(e),
            }

# ################################################################################################################################
# ################################################################################################################################

class RedisSave(AdminService):
    """ Saves the submitted Redis form values into the [redis] section of server.conf,
    persisted on disk so restarts see them, applied to the in-RAM configuration,
    and followed by a rebuild of the cache's live Redis client. The pub/sub backend
    keeps its startup connection - repointing delivery greenlets is a restart-level
    operation.
    """
    changes_config = True
    name = _redis_service_prefix + 'save'

    def handle(self):

        values = self.request.raw['values']

        # The port and the database number arrive as strings from the form
        values['port'] = int(values['port'])
        values['db']   = int(values['db'])

        # First, update the persistent configuration on disk ..
        config = get_config_object(self.server.repo_location, 'server.conf')
        self._apply_values(config['redis'], values)

        update_config_file(config, self.server.repo_location, 'server.conf') # type: ignore

        # .. a newly given password goes encrypted into secrets.conf - the on-disk
        # .. server.conf keeps its zato+secret pointer to that entry ..
        password = values['password']

        if password:
            self._save_password(password)

        # .. then, apply the same values to the in-RAM server-wide configuration,
        # .. with the password in the clear, the way startup decryption leaves it ..
        ram_section = self.server.fs_server_config.redis
        self._apply_values(ram_section, values)

        if password:
            ram_section['password'] = password

        # .. rebuild the live Redis client behind self.redis ..
        self.server.config_manager.reconfigure_redis_cache()

        # .. and have every other process of the server read the same configuration, the password from secrets.conf.
        ram_values:'stranydict' = {}
        self._apply_values(ram_values, values)

        self.config_dispatcher.relay_only({
            'action': BrokerMessageServer.Redis_Reload.value,
            'section': ram_values,
            'has_password': bool(password),
        })

        logger.info('Redis save: `%s:%s` db `%s`', values['host'], values['port'], values['db'])

        self.response.payload = {
            'success': True,
            'message': 'Saved, the Redis connection now uses the new configuration',
        }

# ################################################################################################################################

    def _apply_values(self, section:'any_', values:'stranydict') -> 'None':
        """ Writes the form values into a [redis] section, be it the on-disk one or the in-RAM one.
        """
        for field, key in _redis_conf_keys.items():
            section[key] = values[field]

# ################################################################################################################################

    def _save_password(self, password:'str') -> 'None':
        """ Encrypts the password and stores it in secrets.conf, the same entry
        the zato+secret pointer in server.conf points to.
        """
        encrypted = self.crypto.encrypt(password.encode('utf8'), needs_str=True)

        config = get_config_object(self.server.repo_location, 'secrets.conf')
        config['zato']['server_conf.redis.password'] = encrypted # type: ignore

        update_config_file(config, self.server.repo_location, 'secrets.conf') # type: ignore

# ################################################################################################################################
# ################################################################################################################################
