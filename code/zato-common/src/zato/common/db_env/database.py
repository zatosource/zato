# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Zato database, which holds the tables of publish/subscribe, of the audit log, of the shared objects
# and of the rule engine. The Zato_Database_* variables select it, and without them it is the SQLite file zato.db
# in the environment directory.

# Zato
from zato.common.audit_log.common import metadata as audit_metadata
from zato.common.common_db.schema import metadata as common_metadata
from zato.common.db_env.common import EnvDBConfig, get_env_sqlite_path, get_env_values
from zato.common.db_env.engine import dispose_env_engine, get_env_engine, new_unshared_env_engine
from zato.common.pubsub.sql.schema import metadata as pubsub_metadata
from zato.common.rule_engine.sql.schema import metadata as rule_engine_metadata

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import stranydict, strnone

    # Dummy assignments to satisfy type checkers
    Engine = Engine
    stranydict = stranydict
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The prefix of the environment variables selecting the Zato database
    Env_Prefix = 'Zato_Database_'

    # The prefixes of the environment variables that selected the databases of publish/subscribe, of the audit log
    # and of the shared objects before the Zato database replaced them. Each Zato_Database_* variable that is not set
    # is read under these prefixes, in this order.
    Alias_Env_Prefixes = ('Zato_PubSub_DB_', 'Zato_Audit_Log_DB_', 'Zato_Common_DB_')

    # The SQLite file of the database in the environment directory
    File_Name = 'zato.db'

# ################################################################################################################################

# The Zato database, as the Zato_Database_* variables select it.
database_config = EnvDBConfig(
    env_prefix=ModuleCtx.Env_Prefix,
    alias_env_prefixes=ModuleCtx.Alias_Env_Prefixes,
    sqlite_file_name=ModuleCtx.File_Name,
    metadata_tuple=(pubsub_metadata, audit_metadata, common_metadata, rule_engine_metadata),
    needs_pool=True,
    needs_background_checkpoint=True,
)

# ################################################################################################################################
# ################################################################################################################################

def get_database_type() -> 'str':
    """ Returns the type of the Zato database, sqlite or postgresql.
    """
    values = get_env_values(database_config)

    out = values['type']
    return out

# ################################################################################################################################

def get_database_sqlite_path() -> 'strnone':
    """ Returns the path to the SQLite file of the Zato database, or None if the database is a PostgreSQL one.
    """
    out = get_env_sqlite_path(database_config)
    return out

# ################################################################################################################################

def get_database_values() -> 'stranydict':
    """ Returns the connection values of the Zato database, as get_env_values reads them out of the environment.
    """
    out = get_env_values(database_config)
    return out

# ################################################################################################################################

def get_database_engine() -> 'Engine':
    """ Returns the SQLAlchemy engine of the Zato database that all the callers of this process share,
    creating its schemas if needed.
    """
    out = get_env_engine(database_config)
    return out

# ################################################################################################################################

def new_unshared_database_engine() -> 'Engine':
    """ Returns an engine of the Zato database that no other caller receives, which its caller disposes,
    e.g. the arbiter before it forks the worker and the config process.
    """
    out = new_unshared_env_engine(database_config)
    return out

# ################################################################################################################################

def dispose_database_engine() -> 'None':
    """ Disposes the shared engine of the Zato database, stopping its background checkpointer, so that the next
    get_database_engine call builds a fresh engine and no checkpoint thread is left running.
    """
    dispose_env_engine(database_config)

# ################################################################################################################################
# ################################################################################################################################
