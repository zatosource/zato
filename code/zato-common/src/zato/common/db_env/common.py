# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Environment-configured SQLAlchemy engines for the audit log. This package builds
# and caches an engine selected through the Zato_Audit_Log_DB_* variables.

# stdlib
import os
from datetime import timezone

# SQLAlchemy
from sqlalchemy import DateTime, LargeBinary, String
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.functions import FunctionElement
from sqlalchemy.types import TypeDecorator

# Zato
from zato.common.defaults import default_env_base_dir
from zato.common.util.api import as_bool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy import MetaData
    from sqlalchemy.engine import Dialect
    from sqlalchemy.sql.compiler import SQLCompiler
    from sqlalchemy.types import TypeEngine
    from zato.common.typing_ import any_, stranydict

    # Dummy assignments to satisfy type checkers
    any_ = any_
    datetime = datetime
    Dialect = Dialect
    MetaData = MetaData
    SQLCompiler = SQLCompiler
    TypeEngine = TypeEngine

# ################################################################################################################################
# ################################################################################################################################

# Recognized database types
Type_SQLite     = 'sqlite'
Type_PostgreSQL = 'postgresql'

# What is used when the type variable is not set
Default_Type = Type_SQLite

# SSL is off unless requested explicitly
Default_SSL = False

# When SSL is on, the server certificate is verified unless turned off explicitly
Default_SSL_Verify = True

# Binary content, raw bytes on every database.
Binary_Type = LargeBinary()

# The hour a timestamp falls in, in the form YYYY-MM-DDTHH, as Python and each database format it.
Hour_Period_Format = '%Y-%m-%dT%H'
_sqlite_hour_format = '%Y-%m-%dT%H'
_postgresql_hour_format = 'YYYY-MM-DD"T"HH24'

# ################################################################################################################################
# ################################################################################################################################

class UTC_DateTime(TypeDecorator):
    """ A point in time in UTC. It accepts timezone-aware datetimes, keeps them in UTC and returns them timezone-aware
    in UTC on every database. PostgreSQL stores a timestamp with a time zone and SQLite stores the text form
    SQLAlchemy defines for its DATETIME type.
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

        # .. every value is stored in UTC ..
        out = value.astimezone(timezone.utc)

        # .. and SQLite, whose type has no time zone, receives it without one.
        if dialect.name != Type_PostgreSQL:
            out = out.replace(tzinfo=None)

        return out

# ################################################################################################################################

    def process_result_value(self, value:'datetime | None', dialect:'Dialect') -> 'datetime | None':

        # A column that is not set is returned as None ..
        if value is None:
            return None

        # .. PostgreSQL returns the time in the time zone of the session ..
        if dialect.name == Type_PostgreSQL:
            out = value.astimezone(timezone.utc)

        # .. while SQLite returns it in UTC without a time zone.
        else:
            out = value.replace(tzinfo=timezone.utc)

        return out

# ################################################################################################################################
# ################################################################################################################################

class _HourPeriod(FunctionElement):
    """ The hour a timestamp column falls in, as the text YYYY-MM-DDTHH, compiled to the date function of each database.
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

@compiles(_HourPeriod, Type_SQLite)
def compile_hour_period_sqlite(element:'_HourPeriod', compiler:'SQLCompiler', **kwargs:'any_') -> 'str':
    column = compiler.process(element.clauses, **kwargs)
    out = f"strftime('{_sqlite_hour_format}', {column})"
    return out

# ################################################################################################################################

@compiles(_HourPeriod, Type_PostgreSQL)
def compile_hour_period_postgresql(element:'_HourPeriod', compiler:'SQLCompiler', **kwargs:'any_') -> 'str':
    column = compiler.process(element.clauses, **kwargs)
    out = f"to_char({column} AT TIME ZONE 'UTC', '{_postgresql_hour_format}')"
    return out

# ################################################################################################################################
# ################################################################################################################################

class EnvDBConfig:
    """ Describes one environment-configured database - the environment variables
    selecting it, its default SQLite file name and the schema it needs.
    """

    def __init__(
        self,
        *,
        env_prefix:'str',
        sqlite_file_name:'str',
        metadata:'MetaData',
        needs_pool:'bool' = False,
        needs_background_checkpoint:'bool' = False,
        ) -> 'None':

        self.env_prefix = env_prefix
        self.sqlite_file_name = sqlite_file_name
        self.metadata = metadata

        # Whether SQLite connections are pooled - SQLAlchemy's default for file-based SQLite
        # is no pooling at all, which makes every transaction open and close the database file,
        # and each close checkpoints the WAL, costing more than ten milliseconds. Stores with
        # many small transactions, such as pub/sub, need a real pool instead.
        self.needs_pool = needs_pool

        # Whether the WAL of a SQLite database is checkpointed in a thread of its own rather than by the commits
        self.needs_background_checkpoint = needs_background_checkpoint

        # The full names of the environment variables selecting and configuring the database
        self.env_type     = f'{env_prefix}Type'
        self.env_host     = f'{env_prefix}Host'
        self.env_port     = f'{env_prefix}Port'
        self.env_username = f'{env_prefix}Username'
        self.env_password = f'{env_prefix}Password'
        self.env_name     = f'{env_prefix}Name'

        # The full names of the environment variables configuring SSL/TLS
        self.env_ssl           = f'{env_prefix}SSL'
        self.env_ssl_ca_file   = f'{env_prefix}SSL_CA_File'
        self.env_ssl_cert_file = f'{env_prefix}SSL_Cert_File'
        self.env_ssl_key_file  = f'{env_prefix}SSL_Key_File'
        self.env_ssl_verify    = f'{env_prefix}SSL_Verify'

# ################################################################################################################################

    def get_sqlite_path(self) -> 'str':
        """ Returns the full path to the default SQLite file of this database.
        """
        out = os.path.join(default_env_base_dir, self.sqlite_file_name)
        return out

# ################################################################################################################################
# ################################################################################################################################

def get_env_values(config:'EnvDBConfig') -> 'stranydict':
    """ Reads this database's environment variables into a dict of connection values,
    filling in the defaults for anything that is not set.
    """

    # Our response to produce
    out:'stranydict' = {}

    # The type has a well-known default ..
    if db_type := os.environ.get(config.env_type, ''):
        out['type'] = db_type
    else:
        out['type'] = Default_Type

    # .. the SQLite file path defaults to this store's shared file ..
    if name := os.environ.get(config.env_name, ''):
        out['name'] = name
    elif out['type'] == Type_SQLite:
        out['name'] = config.get_sqlite_path()
    else:
        out['name'] = ''

    # .. the network location and credentials are empty unless given ..
    out['host']     = os.environ.get(config.env_host, '')
    out['port']     = os.environ.get(config.env_port, '')
    out['username'] = os.environ.get(config.env_username, '')
    out['password'] = os.environ.get(config.env_password, '')

    # .. SSL is off unless requested explicitly ..
    if ssl_enabled := os.environ.get(config.env_ssl, ''):
        out['ssl'] = as_bool(ssl_enabled)
    else:
        out['ssl'] = Default_SSL

    # .. the server certificate is verified by default when SSL is on ..
    if verify := os.environ.get(config.env_ssl_verify, ''):
        out['ssl_verify'] = as_bool(verify)
    else:
        out['ssl_verify'] = Default_SSL_Verify

    # .. and the certificate paths are empty unless given.
    out['ssl_ca_file']   = os.environ.get(config.env_ssl_ca_file, '')
    out['ssl_cert_file'] = os.environ.get(config.env_ssl_cert_file, '')
    out['ssl_key_file']  = os.environ.get(config.env_ssl_key_file, '')

    return out

# ################################################################################################################################
# ################################################################################################################################
