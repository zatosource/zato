# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.db_env import get_sqlite_file_engine
from zato.common.defaults import default_env_base_dir
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

    # The environment variable with the full path to the pub/sub SQLite file.
    Env_Path = 'Zato_PubSub_DB_Path'

    # The environment variables overriding how long fully delivered messages are kept.
    Env_Delivered_Max_Messages = 'Zato_PubSub_Delivered_Max_Messages'
    Env_Delivered_Max_Days     = 'Zato_PubSub_Delivered_Max_Days'

    # The environment variable overriding how many rows one bulk statement may touch.
    Env_Batch_Size = 'Zato_PubSub_DB_Batch_Size'

# ################################################################################################################################

# How many fully delivered messages one topic may retain for browsing and statistics.
_default_delivered_max_messages = 1_000_000

# How many days a fully delivered message is retained for browsing and statistics.
_default_delivered_max_days = 7

# How many rows one bulk delete or update statement may touch.
_default_batch_size = 5_000

# ################################################################################################################################
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
    """ Returns an SQLAlchemy engine for the pub/sub SQLite file, creating the schema if needed.
    """
    db_path = get_pubsub_db_path()
    out = get_sqlite_file_engine(db_path, metadata, needs_pool=True)

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
