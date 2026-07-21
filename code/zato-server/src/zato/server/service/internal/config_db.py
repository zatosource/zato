# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Config DB - services behind the dashboard screens that configure the databases the server
# itself uses. The SQL screen drives the audit log and analytics databases through the
# Zato_Audit_Log_DB_* and Zato_Analytics_DB_* environment variables, applied live and
# persisted into an env file. The Redis screen drives the [redis] section of server.conf,
# persisted on disk and applied live to the cache's Redis client.

# stdlib
import os
from logging import getLogger
from time import time

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import text as sa_text

# Zato
from zato.common.analytics.api import analytics_db_file_name, metadata as analytics_metadata
from zato.common.audit_log.common import audit_db_file_name, metadata as audit_metadata
from zato.common.config_db import apply_env_variables, build_env_variables, get_default_env_file_path, \
    persist_env_variables, sql_env_prefix_by_database, sql_field_suffixes
from zato.common.db_env import build_connect_args_from_values, build_engine_url_from_values, get_env_values, EnvDBConfig
from zato.common.pubsub.sql.schema import metadata as pubsub_metadata, pubsub_db_file_name
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

_sql_service_prefix   = 'zato.config-db.sql.'
_redis_service_prefix = 'zato.config-db.redis.'

# ################################################################################################################################
# ################################################################################################################################

# The environment-configured SQL databases the SQL screen knows about
_sql_databases = {
    'audit-log': EnvDBConfig(
        env_prefix=sql_env_prefix_by_database['audit-log'],
        sqlite_file_name=audit_db_file_name,
        metadata=audit_metadata,
    ),
    'analytics': EnvDBConfig(
        env_prefix=sql_env_prefix_by_database['analytics'],
        sqlite_file_name=analytics_db_file_name,
        metadata=analytics_metadata,
    ),
    'pubsub': EnvDBConfig(
        env_prefix=sql_env_prefix_by_database['pubsub'],
        sqlite_file_name=pubsub_db_file_name,
        metadata=pubsub_metadata,
    ),
}

# The keys of the [redis] section of server.conf the Redis screen saves, mapped from the form fields
_redis_conf_keys = {
    'display_name':  'name',
    'description':   'description',
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

class SQLGet(AdminService):
    """ Returns the current configuration of one environment-driven SQL database.
    """
    name = _sql_service_prefix + 'get'

    def handle(self):

        # Which of the databases we are to read ..
        database = self.request.raw['database']
        config = _sql_databases[database]

        # .. the connection values come out of the environment with defaults filled in ..
        values = get_env_values(config)

        # .. and so do the display name and description.
        values['display_name'] = os.environ.get(config.env_prefix + 'Display_Name', '')
        values['description']  = os.environ.get(config.env_prefix + 'Description', '')

        self.response.payload = {
            'success': True,
            'values': values,
        }

# ################################################################################################################################
# ################################################################################################################################

class SQLTest(AdminService):
    """ Connects to an SQL database described by the submitted form values and runs a test query.
    """
    name = _sql_service_prefix + 'test'

    def handle(self):

        values = self.request.raw['values']
        db_type = values['type']

        try:
            # Build a throwaway engine out of the submitted values ..
            engine_url   = build_engine_url_from_values(values, db_type)
            connect_args = build_connect_args_from_values(values, db_type)
            engine       = create_engine(engine_url, connect_args=connect_args)

            # .. run the simplest possible query and time it ..
            start = time()

            with engine.connect() as connection:
                _ = connection.execute(sa_text('select 1'))

            response_time = round(time() - start, 3)

            # .. the engine is not needed anymore.
            engine.dispose()

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

class SQLSave(AdminService):
    """ Applies the submitted SQL form values to this database's environment variables,
    live in this process and persisted into an env file so they survive restarts.
    The audit log resolves its engine per write and the analytics rollup and queries
    resolve theirs per call, so new operations use the new database immediately.
    """
    name = _sql_service_prefix + 'save'

    def handle(self):

        # Which of the databases we are to configure ..
        database = self.request.raw['database']
        values = self.request.raw['values']

        env_prefix = sql_env_prefix_by_database[database]

        # .. turn the form values into their environment variables ..
        env_variables = build_env_variables(env_prefix, sql_field_suffixes, values)

        # .. apply them to the running server ..
        set_count = apply_env_variables(env_variables)

        # .. persist them so a restart re-applies them - into the file the server
        # .. was started with or, without one, into a well-known file under the config
        # .. repo that startup loads on its own ..
        if env_path := self.server.env_file:
            pass
        else:
            env_path = get_default_env_file_path(self.server.repo_location)

        message = f'Saved, {set_count} variables set'

        try:
            persist_env_variables(env_path, env_variables)
        except OSError as e:
            # .. the values are live in RAM even when the file cannot be written, e.g. on a read-only mount.
            message = f'Saved in RAM only, could not persist to `{env_path}` - {e}'

        logger.info('Config DB SQL save: `%s`, set %d variables, env file `%s`', database, set_count, env_path)

        self.response.payload = {
            'success': True,
            'message': message,
            'env_variables': env_variables,
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

        # .. and finally, rebuild the live Redis client behind self.cache.
        self.server.config_manager.reconfigure_redis_cache()

        logger.info('Config DB Redis save: `%s:%s` db `%s`', values['host'], values['port'], values['db'])

        self.response.payload = {
            'success': True,
            'message': 'Saved, the cache connection now uses the new configuration',
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
