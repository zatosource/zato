# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Config DB - services behind the dashboard screens that configure the environment-driven
# databases, i.e. the SQL ones (audit log and analytics) and the default Redis connection.
# All the configuration lives in environment variables, the same ones the stores themselves
# read, so saving here has the same semantics as the environment variables screen.

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
from zato.common.db_env import build_connect_args_from_values, build_engine_url_from_values, get_env_values, EnvDBConfig
from zato.common.redis_env import get_redis_conn_from_values, get_redis_values
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

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
        env_prefix='Zato_Audit_Log_DB_',
        sqlite_file_name=audit_db_file_name,
        metadata=audit_metadata,
    ),
    'analytics': EnvDBConfig(
        env_prefix='Zato_Analytics_DB_',
        sqlite_file_name=analytics_db_file_name,
        metadata=analytics_metadata,
    ),
}

# Maps the SQL form fields to the suffixes of the corresponding environment variables
_sql_suffixes = {
    'display_name':  'Display_Name',
    'description':   'Description',
    'type':          'Type',
    'host':          'Host',
    'port':          'Port',
    'username':      'Username',
    'password':      'Password',
    'name':          'Name',
    'ssl':           'SSL',
    'ssl_ca_file':   'SSL_CA_File',
    'ssl_cert_file': 'SSL_Cert_File',
    'ssl_key_file':  'SSL_Key_File',
    'ssl_verify':    'SSL_Verify',
}

# The prefix of the environment variables configuring the default Redis connection
_redis_env_prefix = 'Zato_Redis_'

# Maps the Redis form fields to the suffixes of the corresponding environment variables
_redis_suffixes = {
    'display_name':  'Display_Name',
    'description':   'Description',
    'host':          'Host',
    'port':          'Port',
    'db':            'DB',
    'username':      'Username',
    'password':      'Password',
    'ssl':           'SSL',
    'ssl_ca_file':   'SSL_CA_File',
    'ssl_cert_file': 'SSL_Cert_File',
    'ssl_key_file':  'SSL_Key_File',
    'ssl_verify':    'SSL_Verify',
}

# ################################################################################################################################
# ################################################################################################################################

def _save_env_values(env_prefix:'str', suffixes:'stranydict', values:'stranydict') -> 'int':
    """ Writes a dict of form values into the environment variables under a given prefix.
    Empty values delete their variables so the built-in defaults apply again,
    booleans are always written out explicitly.
    """

    # How many variables were set
    set_count = 0

    for key, suffix in suffixes.items():

        env_name = env_prefix + suffix
        value = values[key]

        # Booleans are always written out so an unchecked box overrides a non-empty default ..
        if isinstance(value, bool):
            os.environ[env_name] = str(value)
            set_count += 1

        # .. non-empty strings are set as they are ..
        elif value:
            os.environ[env_name] = value
            set_count += 1

        # .. and empty ones remove their variables so the defaults apply again.
        else:
            _ = os.environ.pop(env_name, None)

    return set_count

# ################################################################################################################################
# ################################################################################################################################

class SQLGet(AdminService):
    """ Returns the current configuration of one environment-driven SQL database.
    """
    name = _sql_service_prefix + 'get'

    def handle(self):

        # Which of the databases we are to read ..
        database = self.request.raw_request['database']
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

        values = self.request.raw_request['values']
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
    """ Writes the submitted SQL form values into this database's environment variables.
    """
    name = _sql_service_prefix + 'save'

    def handle(self):

        # Which of the databases we are to configure ..
        database = self.request.raw_request['database']
        values = self.request.raw_request['values']

        config = _sql_databases[database]

        # .. write everything out into the environment.
        set_count = _save_env_values(config.env_prefix, _sql_suffixes, values)

        logger.info('Config DB SQL save: `%s`, set %d variables', database, set_count)

        self.response.payload = {
            'success': True,
            'message': f'Saved, {set_count} variables set',
        }

# ################################################################################################################################
# ################################################################################################################################

class RedisGet(AdminService):
    """ Returns the current configuration of the default Redis connection.
    """
    name = _redis_service_prefix + 'get'

    def handle(self):

        # The connection values come out of the environment with defaults filled in ..
        values = get_redis_values()

        # .. and so do the display name and description.
        values['display_name'] = os.environ.get(_redis_env_prefix + 'Display_Name', '')
        values['description']  = os.environ.get(_redis_env_prefix + 'Description', '')

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

        values = self.request.raw_request['values']

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
    """ Writes the submitted Redis form values into the connection's environment variables.
    """
    name = _redis_service_prefix + 'save'

    def handle(self):

        values = self.request.raw_request['values']

        # Write everything out into the environment.
        set_count = _save_env_values(_redis_env_prefix, _redis_suffixes, values)

        logger.info('Config DB Redis save: set %d variables', set_count)

        self.response.payload = {
            'success': True,
            'message': f'Saved, {set_count} variables set',
        }

# ################################################################################################################################
# ################################################################################################################################
