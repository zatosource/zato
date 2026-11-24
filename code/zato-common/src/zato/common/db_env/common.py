# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Environment-configured SQLAlchemy engines. This package builds and caches the engine of the Zato database,
# which the Zato_Database_* variables select.

# stdlib
import os
from datetime import timezone
from logging import getLogger

# SQLAlchemy
from sqlalchemy import DateTime, LargeBinary, String
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.functions import FunctionElement
from sqlalchemy.types import TypeDecorator

# Zato
from zato.common.util.eval_ import as_bool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy import MetaData
    from sqlalchemy.engine import Dialect
    from sqlalchemy.sql.compiler import SQLCompiler
    from sqlalchemy.types import TypeEngine
    from zato.common.typing_ import any_, anytuple, stranydict, strlist, strset, strtuple

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anytuple = anytuple
    strlist = strlist
    strset = strset
    strtuple = strtuple
    datetime = datetime
    Dialect = Dialect
    MetaData = MetaData
    SQLCompiler = SQLCompiler
    TypeEngine = TypeEngine

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The SQLAlchemy dialect name of the Zato database
Type_PostgreSQL = 'postgresql'

# SSL is off unless requested explicitly
Default_SSL = False

# When SSL is on, the server certificate is verified unless turned off explicitly
Default_SSL_Verify = True

# Pool sizing for network databases of stores that asked for a pool - every durable
# commit waits for the database's log flush and the flush is shared across all commits
# in flight, so throughput scales with how many connections may commit at once
# and SQLAlchemy's default cap of 5+10 is too low for stores like pub/sub.
# The total of 80 stays below the default connection limit of PostgreSQL (100),
# leaving room for other clients of the same database. A managed database whose connection limit
# is shared by several server processes and their cleanup process is given a smaller pool per process.
Default_Pool_Size = 80

# Binary content, raw bytes on every database.
Binary_Type = LargeBinary()

# The hour a timestamp falls in, in the form YYYY-MM-DDTHH, as Python and PostgreSQL format it.
Hour_Period_Format = '%Y-%m-%dT%H'
_postgresql_hour_format = 'YYYY-MM-DD"T"HH24'

# ################################################################################################################################
# ################################################################################################################################

class UTC_DateTime(TypeDecorator):
    """ A point in time in UTC. It accepts timezone-aware datetimes, stores them as a timestamp with a time zone
    and returns them timezone-aware in UTC.
    """
    impl = DateTime
    cache_ok = True

    def load_dialect_impl(self, dialect:'Dialect') -> 'TypeEngine':
        datetime_type = DateTime(timezone=True)

        out = dialect.type_descriptor(datetime_type)
        return out

# ################################################################################################################################

    def process_bind_param(self, value:'datetime | None', dialect:'Dialect') -> 'datetime | None':

        # A column that is not set stays NULL ..
        if value is None:
            return None

        # .. and every value is stored in UTC.
        out = value.astimezone(timezone.utc)
        return out

# ################################################################################################################################

    def process_result_value(self, value:'datetime | None', dialect:'Dialect') -> 'datetime | None':

        # A column that is not set is returned as None ..
        if value is None:
            return None

        # .. and PostgreSQL returns the time in the time zone of the session, which is converted to UTC.
        out = value.astimezone(timezone.utc)
        return out

# ################################################################################################################################
# ################################################################################################################################

class _HourPeriod(FunctionElement):
    """ The hour a timestamp column falls in, as the text YYYY-MM-DDTHH, compiled to the date function of PostgreSQL.
    """
    type = String()
    name = 'hour_period'
    inherit_cache = True

# ################################################################################################################################

def hour_period(column:'any_') -> '_HourPeriod':
    """ The SQL expression of the hour the given timestamp column falls in, in the form of Hour_Period_Format.
    """
    out = _HourPeriod(column)
    return out

# ################################################################################################################################

def to_hour_period(value:'datetime') -> 'str':
    """ The hour the given moment falls in, in UTC and in the form the hour_period expression returns.
    """
    value_utc = value.astimezone(timezone.utc)

    out = value_utc.strftime(Hour_Period_Format)
    return out

# ################################################################################################################################

@compiles(_HourPeriod, Type_PostgreSQL)
def compile_hour_period_postgresql(element:'_HourPeriod', compiler:'SQLCompiler', **kwargs:'any_') -> 'str':
    column = compiler.process(element.clauses, **kwargs)
    out = f"to_char({column} AT TIME ZONE 'UTC', '{_postgresql_hour_format}')"
    return out

# ################################################################################################################################
# ################################################################################################################################

# The aliases that this process has already reported in its log, either as used or as ignored
_reported_alias_names:'strset' = set()

# ################################################################################################################################

def _get_alias_value(name:'str', alias_names:'strtuple') -> 'str':
    """ Returns the value of the first alias of an environment variable that is set, or an empty string if none is set.
    Each alias that is used or ignored is reported once per process.
    """

    # Our response to produce
    out = ''

    # The alias that provides the value
    used_alias_name = ''

    for alias_name in alias_names:

        # Aliases that are not set are skipped ..
        if not (value := os.environ.get(alias_name, '')):
            continue

        # .. the first alias that is set provides the value ..
        if not used_alias_name:
            used_alias_name = alias_name
            out = value

            if alias_name not in _reported_alias_names:
                _reported_alias_names.add(alias_name)
                logger.info('Environment variable %s not set, using %s', name, alias_name)

        # .. and each later alias with a different value is ignored.
        elif value != out:
            if alias_name not in _reported_alias_names:
                _reported_alias_names.add(alias_name)
                logger.warning('Environment variable %s ignored, its value differs from %s, which %s is read from',
                    alias_name, used_alias_name, name)

    return out

# ################################################################################################################################

def get_env_value(name:'str', alias_names:'strtuple') -> 'str':
    """ Returns the value of an environment variable or, if it is not set, the value of the first of its aliases
    that is set, or an empty string if none of them is set.
    """

    # The variable set under its own name takes precedence over all of its aliases ..
    if value := os.environ.get(name, ''):
        out = value

    # .. otherwise, the aliases are read in their order.
    else:
        out = _get_alias_value(name, alias_names)

    return out

# ################################################################################################################################
# ################################################################################################################################

class EnvDBConfig:
    """ Describes one environment-configured database - the environment variables
    selecting it and the schemas it needs.
    """

    def __init__(
        self,
        *,
        env_prefix:'str',
        alias_env_prefixes:'strtuple',
        metadata_tuple:'anytuple',
        ) -> 'None':

        self.env_prefix = env_prefix

        # The prefixes under which each variable is read, in this order, when it is not set under env_prefix
        self.alias_env_prefixes = alias_env_prefixes
        self.metadata_tuple = metadata_tuple

        # The full names of the environment variables selecting and configuring the database
        self.env_host     = f'{env_prefix}Host'
        self.env_port     = f'{env_prefix}Port'
        self.env_username = f'{env_prefix}Username'
        self.env_password = f'{env_prefix}Password'
        self.env_name     = f'{env_prefix}Name'

        # The full name of the environment variable with the path to a file holding the password,
        # read again for each new connection so that a rotated password takes effect without a restart.
        self.env_password_file = f'{env_prefix}Password_File'

        # The full name of the environment variable with the number of pooled connections of a network database
        self.env_pool_size = f'{env_prefix}Pool_Size'

        # The full names of the environment variables configuring SSL/TLS
        self.env_ssl           = f'{env_prefix}SSL'
        self.env_ssl_ca_file   = f'{env_prefix}SSL_CA_File'
        self.env_ssl_cert_file = f'{env_prefix}SSL_Cert_File'
        self.env_ssl_key_file  = f'{env_prefix}SSL_Key_File'
        self.env_ssl_verify    = f'{env_prefix}SSL_Verify'

# ################################################################################################################################

    def get_value(self, name:'str') -> 'str':
        """ Returns the value of one of the environment variables of this database, given by its full name,
        or of the same variable under the first of the alias prefixes that is set.
        """
        suffix = name.removeprefix(self.env_prefix)
        alias_names:'strlist' = []

        for prefix in self.alias_env_prefixes:
            alias_name = f'{prefix}{suffix}'
            alias_names.append(alias_name)

        alias_names_tuple = tuple(alias_names)

        out = get_env_value(name, alias_names_tuple)
        return out

# ################################################################################################################################
# ################################################################################################################################

def get_env_values(config:'EnvDBConfig') -> 'stranydict':
    """ Reads this database's environment variables into a dict of connection values,
    filling in the defaults for anything that is not set.
    """

    # Our response to produce
    out:'stranydict' = {}

    # The database is given by its name ..
    out['name'] = config.get_value(config.env_name)

    # .. the network location and credentials are empty unless given ..
    out['host']     = config.get_value(config.env_host)
    out['port']     = config.get_value(config.env_port)
    out['username'] = config.get_value(config.env_username)
    out['password'] = config.get_value(config.env_password)
    out['password_file'] = config.get_value(config.env_password_file)

    # .. SSL is off unless requested explicitly ..
    if ssl_enabled := config.get_value(config.env_ssl):
        out['ssl'] = as_bool(ssl_enabled)
    else:
        out['ssl'] = Default_SSL

    # .. the server certificate is verified by default when SSL is on ..
    if verify := config.get_value(config.env_ssl_verify):
        out['ssl_verify'] = as_bool(verify)
    else:
        out['ssl_verify'] = Default_SSL_Verify

    # .. the pool of a network database has its default size unless given ..
    if pool_size := config.get_value(config.env_pool_size):
        out['pool_size'] = int(pool_size)
    else:
        out['pool_size'] = Default_Pool_Size

    # .. and the certificate paths are empty unless given.
    out['ssl_ca_file']   = config.get_value(config.env_ssl_ca_file)
    out['ssl_cert_file'] = config.get_value(config.env_ssl_cert_file)
    out['ssl_key_file']  = config.get_value(config.env_ssl_key_file)

    return out

# ################################################################################################################################
# ################################################################################################################################
