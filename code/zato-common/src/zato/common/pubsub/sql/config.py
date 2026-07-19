# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.db_env import Default_SSL, Default_SSL_Verify, Default_Type, EnvDBConfig, get_env_engine, \
    get_env_values, Type_MySQL, Type_Oracle, Type_PostgreSQL, Type_SQLite
from zato.common.pubsub.sql.schema import metadata, pubsub_db_file_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import stranydict

    # Dummy assignments to satisfy type checkers
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Environment variables selecting and configuring the pub/sub database
    Env_Type     = 'Zato_PubSub_DB_Type'
    Env_Host     = 'Zato_PubSub_DB_Host'
    Env_Port     = 'Zato_PubSub_DB_Port'
    Env_Username = 'Zato_PubSub_DB_Username'
    Env_Password = 'Zato_PubSub_DB_Password'
    Env_Name     = 'Zato_PubSub_DB_Name'

    # Environment variables configuring SSL/TLS for the pub/sub database
    Env_SSL           = 'Zato_PubSub_DB_SSL'
    Env_SSL_CA_File   = 'Zato_PubSub_DB_SSL_CA_File'
    Env_SSL_Cert_File = 'Zato_PubSub_DB_SSL_Cert_File'
    Env_SSL_Key_File  = 'Zato_PubSub_DB_SSL_Key_File'
    Env_SSL_Verify    = 'Zato_PubSub_DB_SSL_Verify'

    # The environment variables overriding how long fully delivered messages are kept
    Env_Delivered_Max_Messages = 'Zato_PubSub_Delivered_Max_Messages'
    Env_Delivered_Max_Days     = 'Zato_PubSub_Delivered_Max_Days'

    # The environment variable overriding how many rows one bulk statement may touch
    Env_Batch_Size = 'Zato_PubSub_DB_Batch_Size'

    # Recognized database types
    Type_SQLite     = Type_SQLite
    Type_MySQL      = Type_MySQL
    Type_PostgreSQL = Type_PostgreSQL
    Type_Oracle     = Type_Oracle

    # What is used when Zato_PubSub_DB_Type is not set
    Default_Type = Default_Type

    # SSL is off unless requested explicitly
    Default_SSL = Default_SSL

    # When SSL is on, the server certificate is verified unless turned off explicitly
    Default_SSL_Verify = Default_SSL_Verify

# ################################################################################################################################
# ################################################################################################################################

# How many fully delivered messages one topic may retain for browsing and statistics
_default_delivered_max_messages = 1_000_000

# How many days a fully delivered message is retained for browsing and statistics
_default_delivered_max_days = 7

# How many rows one bulk delete or update statement may touch - bulk operations run
# in bounded batches so a single statement never stalls the process for long,
# which matters most under SQLite whose queries do not yield to other greenlets
_default_batch_size = 5_000

# ################################################################################################################################
# ################################################################################################################################

# How the pub/sub database is selected and configured through the environment -
# the pool matters because pub/sub runs many small transactions and an unpooled
# SQLite connection pays a WAL checkpoint on every single close
_env_config = EnvDBConfig(
    env_prefix='Zato_PubSub_DB_',
    sqlite_file_name=pubsub_db_file_name,
    metadata=metadata,
    needs_pool=True,
)

# ################################################################################################################################

def get_pubsub_db_path() -> 'str':
    """ Returns the full path to the default SQLite pub/sub database file.
    """
    out = _env_config.get_sqlite_path()
    return out

# ################################################################################################################################

def get_pubsub_engine() -> 'Engine':
    """ Returns an SQLAlchemy engine for the pub/sub database, creating the schema if needed.
    Which database is used comes from the Zato_PubSub_DB_* environment variables,
    defaulting to a shared SQLite file.
    """
    out = get_env_engine(_env_config)
    return out

# ################################################################################################################################

def get_pubsub_env_values() -> 'stranydict':
    """ Returns the pub/sub database connection values as read from the environment -
    for callers that talk to the database through its native driver, e.g. bulk loaders.
    """
    out = get_env_values(_env_config)
    return out

# ################################################################################################################################

def get_delivered_max_messages() -> 'int':
    """ Returns how many fully delivered messages one topic may retain.
    """
    if value := os.environ.get(ModuleCtx.Env_Delivered_Max_Messages, ''):
        out = int(value)
    else:
        out = _default_delivered_max_messages

    return out

# ################################################################################################################################

def get_delivered_max_days() -> 'int':
    """ Returns how many days a fully delivered message is retained.
    """
    if value := os.environ.get(ModuleCtx.Env_Delivered_Max_Days, ''):
        out = int(value)
    else:
        out = _default_delivered_max_days

    return out

# ################################################################################################################################

def get_batch_size() -> 'int':
    """ Returns how many rows one bulk delete or update statement may touch.
    """
    if value := os.environ.get(ModuleCtx.Env_Batch_Size, ''):
        out = int(value)
    else:
        out = _default_batch_size

    return out

# ################################################################################################################################
# ################################################################################################################################
