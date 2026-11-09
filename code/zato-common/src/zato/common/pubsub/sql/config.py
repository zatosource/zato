# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.db_env import get_sqlite_file_engine
from zato.common.db_env.common import Default_Type, EnvDBConfig
from zato.common.db_env.engine import get_env_engine
from zato.common.defaults import default_env_base_dir
from zato.common.ha.common import Database_PubSub
from zato.common.pubsub.sql.schema import metadata, pubsub_db_file_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine

    # Dummy assignments to satisfy type checkers
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The prefix of the environment variables selecting the pub/sub database
    Env_Prefix = 'Zato_PubSub_DB_'

    # The environment variable with the full path to the pub/sub SQLite file.
    Env_Path = 'Zato_PubSub_DB_Path'

    # The environment variables overriding how long fully delivered messages are kept.
    Env_Delivered_Max_Messages = 'Zato_PubSub_Delivered_Max_Messages'
    Env_Delivered_Max_Days     = 'Zato_PubSub_Delivered_Max_Days'

    # The environment variable overriding how many rows one bulk statement may touch.
    Env_Batch_Size = 'Zato_PubSub_DB_Batch_Size'

    # The environment variable overriding how many messages the publications and acknowledgements
    # of one group commit refer to at most.
    Env_Commit_Max_Messages = 'Zato_PubSub_Commit_Max_Messages'

    # The environment variable overriding how many group commits may be in progress at once on PostgreSQL.
    Env_Commits_In_Flight = 'Zato_PubSub_Commits_In_Flight'

    # The environment variable with how long the messages of a pull wait for their acknowledgement, in seconds,
    # before the next pull hands them out again.
    Env_Pull_Lease_Seconds = 'Zato_PubSub_Pull_Lease_Seconds'

    # The environment variable with the path to the file in which the active server records its generation.
    Env_Generation_File = 'Zato_PubSub_Generation_File'

# ################################################################################################################################

# How long the messages of a pull wait for their acknowledgement, in seconds.
_default_pull_lease_seconds = 30

# How many fully delivered messages one topic may retain for browsing and statistics.
_default_delivered_max_messages = 1_000_000

# How many days a fully delivered message is retained for browsing and statistics.
_default_delivered_max_days = 7

# How many rows one bulk delete or update statement may touch.
_default_batch_size = 5_000

# How many messages the publications and acknowledgements of one group commit refer to at most.
_default_commit_max_messages = 500

# How many group commits may be in progress at once on PostgreSQL. SQLite has a single writer.
_default_commits_in_flight = 2

# How many group commits of publications may be in progress on PostgreSQL in addition to the ones above.
_urgent_commits_in_flight = 1

# The name of the file in which the active server records its generation, under the environment directory.
_generation_file_name = 'pubsub-generation'

# The pub/sub database, as the Zato_PubSub_DB_* variables select it.
pubsub_db_config = EnvDBConfig(
    env_prefix=ModuleCtx.Env_Prefix,
    sqlite_file_name=pubsub_db_file_name,
    metadata=metadata,
    needs_pool=True,
    needs_background_checkpoint=True,
    replicated_database=Database_PubSub,
)

# ################################################################################################################################
# ################################################################################################################################

def get_pubsub_db_type() -> 'str':
    """ Returns the type of the pub/sub database, sqlite or postgresql.
    """
    if db_type := os.environ.get(pubsub_db_config.env_type, ''):
        out = db_type
    else:
        out = Default_Type

    return out

# ################################################################################################################################

def get_pubsub_db_path() -> 'str':
    """ Returns the full path to the pub/sub SQLite file.
    """
    out = os.environ.get(ModuleCtx.Env_Path)

    if out is None:
        out = os.path.join(default_env_base_dir, pubsub_db_file_name)

    return out

# ################################################################################################################################

def get_pubsub_engine() -> 'Engine':
    """ Returns an SQLAlchemy engine for the pub/sub database, creating the schema if needed.
    SQLite uses the file that Zato_PubSub_DB_Path names, and every other type is built from the Zato_PubSub_DB_* variables.
    """
    db_type = get_pubsub_db_type()

    if db_type == Default_Type:
        db_path = get_pubsub_db_path()
        out = get_sqlite_file_engine(db_path, metadata, needs_pool=True, needs_background_checkpoint=True,
            replicated_database=Database_PubSub)
    else:
        out = get_env_engine(pubsub_db_config)

    return out

# ################################################################################################################################

def get_generation_file_path() -> 'str':
    """ Returns the path to the file in which the active server records its generation.
    """
    if path := os.environ.get(ModuleCtx.Env_Generation_File, ''):
        out = path
    else:
        out = os.path.join(default_env_base_dir, _generation_file_name)

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

def get_commit_max_messages() -> 'int':
    """ Returns how many messages the publications and acknowledgements of one group commit refer to at most.
    """
    if value := os.environ.get(ModuleCtx.Env_Commit_Max_Messages, ''):
        out = int(value)
    else:
        out = _default_commit_max_messages

    return out

# ################################################################################################################################

def get_pull_lease_seconds() -> 'int':
    """ Returns how long the messages of a pull wait for their acknowledgement before they are handed out again.
    """
    if value := os.environ.get(ModuleCtx.Env_Pull_Lease_Seconds, ''):
        out = int(value)
    else:
        out = _default_pull_lease_seconds

    return out

# ################################################################################################################################

def get_commits_in_flight() -> 'int':
    """ Returns how many group commits may be in progress at once - one on SQLite, which has a single writer.
    """
    db_type = get_pubsub_db_type()

    if db_type == Default_Type:
        out = 1
    elif value := os.environ.get(ModuleCtx.Env_Commits_In_Flight, ''):
        out = int(value)
    else:
        out = _default_commits_in_flight

    return out

# ################################################################################################################################

def get_urgent_commits_in_flight() -> 'int':
    """ Returns how many group commits of publications may be in progress in addition to those that get_commits_in_flight
    allows, so that a publication does not wait for a commit of acknowledgements - none on SQLite, which has a single writer.
    """
    db_type = get_pubsub_db_type()

    if db_type == Default_Type:
        out = 0
    else:
        out = _urgent_commits_in_flight

    return out

# ################################################################################################################################
# ################################################################################################################################
