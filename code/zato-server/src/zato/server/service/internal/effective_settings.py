# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The settings in force in the process of a server - those of the Zato database as its connections see them,
# the file system of the database, the audit log, the group commits, the pull lease, the retention limits,
# the active-standby mode with the timers of its node and the files that its logs are written to.

# stdlib
import logging
import os

# Zato
from zato.common.audit_log.api import is_audit_log_enabled
from zato.common.audit_log.common import get_commit_max_events, get_retention_days
from zato.common.db_env.commit_queue import Default_Max_In_Flight
from zato.common.db_env.common import Type_SQLite
from zato.common.db_env.connection import Standby_Count_Query
from zato.common.db_env.database import get_database_engine, get_database_sqlite_path, get_database_type
from zato.common.db_env.filesystem import get_filesystem_type, is_memory_filesystem
from zato.common.ha.common import is_active_standby, ModuleCtx as HACtx
from zato.common.pubsub.sql.config import get_commit_max_messages, get_commits_in_flight, get_delivered_max_days, \
    get_delivered_max_messages, get_pull_lease_seconds, get_urgent_commits_in_flight
from zato.common.typing_ import cast_
from zato.common.version import get_version
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import stranydict, strlist

    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The names of the levels of synchronization that SQLite reports as numbers
    SQLite_Synchronous_Names = {
        0: 'off',
        1: 'normal',
        2: 'full',
        3: 'extra',
    }

    # The settings of a PostgreSQL server that decide when a commit is durable
    PostgreSQL_Settings_Query = """
select
    current_setting('synchronous_commit'),
    current_setting('fsync'),
    current_setting('full_page_writes'),
    current_setting('synchronous_standby_names')
""".strip()

    # The variables with the timers of the node of an active-standby pair
    HA_Timer_Variables = (
        HACtx.Env_Heartbeat_Time,
        HACtx.Env_Takeover_Time,
    )

# ################################################################################################################################
# ################################################################################################################################

def _get_sqlite_settings(engine:'Engine') -> 'stranydict':
    """ Returns the journal mode and the level of synchronization of a pooled connection of the Zato database
    and the file system of the directory of its file.
    """
    with engine.connect() as connection:
        journal_mode = connection.exec_driver_sql('pragma journal_mode').scalar()
        synchronous = connection.exec_driver_sql('pragma synchronous').scalar()

    db_path = cast_('str', get_database_sqlite_path())
    db_dir = os.path.dirname(db_path)

    out:'stranydict' = {
        'journal_mode': journal_mode,
        'synchronous': ModuleCtx.SQLite_Synchronous_Names[synchronous],
        'filesystem_type': get_filesystem_type(db_dir),
        'is_memory_filesystem': is_memory_filesystem(db_dir),
    }

    return out

# ################################################################################################################################

def _get_postgresql_settings(engine:'Engine') -> 'stranydict':
    """ Returns the settings of the PostgreSQL server of the Zato database that decide when a commit is durable,
    as a pooled connection sees them, and the number of standbys that stream its write-ahead log.
    """
    with engine.connect() as connection:
        row = connection.exec_driver_sql(ModuleCtx.PostgreSQL_Settings_Query).one()
        standby_count = connection.exec_driver_sql(Standby_Count_Query).scalar()

    synchronous_commit, fsync, full_page_writes, synchronous_standby_names = row

    out:'stranydict' = {
        'synchronous_commit': synchronous_commit,
        'fsync': fsync,
        'full_page_writes': full_page_writes,
        'synchronous_standby_names': synchronous_standby_names,
        'standby_count': standby_count,
    }

    return out

# ################################################################################################################################

def _get_log_files(native_log_files:'strlist') -> 'strlist':
    """ Returns the path of each file that a handler of a logger of this process writes to,
    together with the files of zato_server_core that the processes of the server append to.
    """
    loggers = [logging.getLogger()]

    # The manager holds placeholders, too, for the parents of loggers that were never created themselves
    for item in logging.Logger.manager.loggerDict.values():
        if isinstance(item, logging.Logger):
            loggers.append(item)

    paths = set(native_log_files)

    for logger in loggers:
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                paths.add(handler.baseFilename)

    out = sorted(paths)
    return out

# ################################################################################################################################

def get_effective_settings(native_log_files:'strlist') -> 'stranydict':
    """ Returns the settings in force in this process, whose server appends to the given files of zato_server_core.
    """
    database_type = get_database_type()
    engine = get_database_engine()

    if database_type == Type_SQLite:
        database_settings = _get_sqlite_settings(engine)
    else:
        database_settings = _get_postgresql_settings(engine)

    # A timer of the node that the node was not given is one of its defaults, which this process does not know
    ha_timers:'stranydict' = {}
    for name in ModuleCtx.HA_Timer_Variables:
        ha_timers[name] = os.environ.get(name)

    out:'stranydict' = {
        'pid': os.getpid(),
        'version': get_version(),
        'database_type': database_type,
        'database': database_settings,
        'is_audit_log_enabled': is_audit_log_enabled(),
        'audit_log_commit_max_events': get_commit_max_events(),
        'audit_log_commits_in_flight': Default_Max_In_Flight,
        'audit_log_retention_days': get_retention_days(),
        'pubsub_commit_max_messages': get_commit_max_messages(),
        'pubsub_commits_in_flight': get_commits_in_flight(),
        'pubsub_urgent_commits_in_flight': get_urgent_commits_in_flight(),
        'pubsub_pull_lease_seconds': get_pull_lease_seconds(),
        'pubsub_delivered_max_messages': get_delivered_max_messages(),
        'pubsub_delivered_max_days': get_delivered_max_days(),
        'is_active_standby': is_active_standby(),
        'ha_timers': ha_timers,
        'log_files': _get_log_files(native_log_files),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class GetEffectiveSettings(AdminService):
    """ Returns the settings in force in the process of this server.
    """
    name = 'zato.server.get-effective-settings'

    def handle(self) -> 'None':
        self.response.payload = get_effective_settings(self.server.native_log_files)

# ################################################################################################################################
# ################################################################################################################################
