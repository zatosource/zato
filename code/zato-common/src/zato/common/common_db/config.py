# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.common_db.schema import common_db_file_name, metadata
from zato.common.db_env.common import EnvDBConfig, get_env_values, Type_PostgreSQL, Type_SQLite
from zato.common.db_env.engine import create_schema, get_env_engine, get_sqlite_file_engine
from zato.common.defaults import default_env_base_dir
from zato.common.ha.common import Database_Common
from zato.common.pubsub.sql.config import get_pubsub_engine, ModuleCtx as PubSubModuleCtx, pubsub_db_config

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import stranydict

    # Dummy assignments to satisfy type checkers
    Engine = Engine
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The prefix of the environment variables selecting the common database
    Env_Prefix = 'Zato_Common_DB_'

    # The environment variable with the full path to the SQLite file of the common database
    Env_Path = 'Zato_Common_DB_Path'

    # Where the common database is - its own variables, the database of pub/sub or its own default SQLite file
    Source_Common  = 'common'
    Source_PubSub  = 'pubsub'
    Source_Default = 'default'

# ################################################################################################################################

# The connection values that identify a database, as get_env_values returns them.
_identity_keys = ('type', 'host', 'port', 'name')

# The common database, as the Zato_Common_DB_* variables select it.
common_db_config = EnvDBConfig(
    env_prefix=ModuleCtx.Env_Prefix,
    sqlite_file_name=common_db_file_name,
    metadata=metadata,
    needs_pool=True,
    replicated_database=Database_Common,
)

# ################################################################################################################################
# ################################################################################################################################

class CommonDBConfigError(Exception):
    """ Raised when the common database on PostgreSQL is not the pub/sub database.
    """

# ################################################################################################################################
# ################################################################################################################################

def _is_selected(type_variable:'str', path_variable:'str') -> 'bool':
    """ Whether the variables of one database select it, by its type or by the path to its SQLite file.
    """
    if os.environ.get(type_variable, ''):
        out = True
    elif os.environ.get(path_variable, ''):
        out = True
    else:
        out = False

    return out

# ################################################################################################################################

def get_common_db_source() -> 'str':
    """ Returns where the common database is. Its own variables come first, then the database of the pub/sub variables,
    and its own SQLite file in the environment directory is the default.
    """
    if _is_selected(common_db_config.env_type, ModuleCtx.Env_Path):
        out = ModuleCtx.Source_Common

    elif _is_selected(pubsub_db_config.env_type, PubSubModuleCtx.Env_Path):
        out = ModuleCtx.Source_PubSub

    else:
        out = ModuleCtx.Source_Default

    return out

# ################################################################################################################################

def _describe(values:'stranydict') -> 'str':
    """ Names a database by its type, location and name, without its credentials.
    """
    db_type = values['type']
    host = values['host']
    port = values['port']
    name = values['name']

    out = f'{db_type}://{host}:{port}/{name}'
    return out

# ################################################################################################################################

def check_common_db_config() -> 'None':
    """ Raises an exception if the common database is PostgreSQL and it is not the pub/sub database, because both
    confirm the generation of the active server in one row of the pub/sub database.
    """
    source = get_common_db_source()

    # Only a database that its own variables select can differ from the pub/sub one ..
    if source != ModuleCtx.Source_Common:
        return

    common_values = get_env_values(common_db_config)

    # .. and SQLite serves a single server.
    if common_values['type'] != Type_PostgreSQL:
        return

    pubsub_values = get_env_values(pubsub_db_config)

    for key in _identity_keys:
        if common_values[key] != pubsub_values[key]:
            common_name = _describe(common_values)
            pubsub_name = _describe(pubsub_values)
            message = f'The common database `{common_name}` must be the pub/sub database `{pubsub_name}` on PostgreSQL'
            raise CommonDBConfigError(message)

# ################################################################################################################################

def _get_sqlite_engine(db_path:'str') -> 'Engine':
    out = get_sqlite_file_engine(db_path, metadata, needs_pool=True, needs_background_checkpoint=False,
        replicated_database=Database_Common)
    return out

# ################################################################################################################################

def get_common_engine() -> 'Engine':
    """ Returns an SQLAlchemy engine for the common database, creating its schema if needed.
    When the common database is the pub/sub database, the engine is the one of pub/sub.
    """
    source = get_common_db_source()

    # The pub/sub engine receives the tables of the common database ..
    if source == ModuleCtx.Source_PubSub:
        out = get_pubsub_engine()
        create_schema(out, metadata)

    # .. the variables of the common database name either its SQLite file or a network database ..
    elif source == ModuleCtx.Source_Common:

        db_type = os.environ.get(common_db_config.env_type, '')

        if db_type:
            if db_type == Type_SQLite:
                db_path = os.environ.get(ModuleCtx.Env_Path, '')

                if not db_path:
                    db_path = common_db_config.get_sqlite_path()

                out = _get_sqlite_engine(db_path)

            else:
                out = get_env_engine(common_db_config)

        # .. a path alone names a SQLite file ..
        else:
            db_path = os.environ[ModuleCtx.Env_Path]
            out = _get_sqlite_engine(db_path)

    # .. and without any variables, the database is a SQLite file in the environment directory.
    else:
        db_path = os.path.join(default_env_base_dir, common_db_file_name)
        out = _get_sqlite_engine(db_path)

    return out

# ################################################################################################################################
# ################################################################################################################################
