# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The single function through which every performance figure is recorded. A figure is recorded only together with
# the settings in force in the measured server before and after its measurement, and only when those settings are
# the settings of a production installation, the database is on a file system that is not held in memory
# and the server is a process of its own.

# stdlib
import json
import os
import subprocess
from dataclasses import dataclass
from logging import getLogger

# Zato
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.audit_log.common import Default_Commit_Max_Events, Default_Retention_Days
from zato.common.db_env.commit_queue import Default_Max_In_Flight
from zato.common.db_env.common import Type_SQLite
from zato.common.db_env.connection import Relaxed_Commit_Levels, Setting_On, SQLite_Journal_Mode, SQLite_Synchronous
from zato.common.db_env.filesystem import is_memory_filesystem, ModuleCtx as FilesystemCtx
from zato.common.pubsub.sql.config import Default_Commit_Max_Messages, Default_Commits_In_Flight, \
    Default_Delivered_Max_Days, Default_Delivered_Max_Messages, Default_Pull_Lease_Seconds, Urgent_Commits_In_Flight

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import stranydict, strlist

    AdminClient = AdminClient
    PubSubDatabase = PubSubDatabase

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The service that returns the settings in force in a server
    Settings_Service = 'zato.server.get-effective-settings'

    # The environment variable with the file to which each recorded figure is appended as a line of JSON,
    # read only by the test driver
    Env_Results_File = 'Zato_Test_Perf_Results_File'

    # The command that returns the type of the file system of the data directory in a PostgreSQL container
    Data_Directory_Type_Command = 'stat -f -c %T "$PGDATA"'

    # How stat names an overlay file system
    Overlay_Stat_Type = 'overlayfs'

    # The command that returns the directory under which Docker keeps the layers of its containers
    Docker_Root_Command = ['docker', 'info', '--format', '{{.DockerRootDir}}']

# ################################################################################################################################
# ################################################################################################################################

class PerfSettingsError(Exception):
    """ Raised when a figure would be recorded under settings other than those of a production installation.
    """

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Measurement:
    """ A measurement in progress, with the settings in force in the measured server before it began.
    """

    # The client that invokes the services of the measured server
    client: 'AdminClient'

    # The PostgreSQL database of the measured server, or None for a server whose Zato database is a SQLite file
    database: 'PubSubDatabase | None'

    # The settings in force in the measured server before the measurement
    settings_before: 'stranydict'

# ################################################################################################################################
# ################################################################################################################################

def _check_value(findings:'strlist', name:'str', value:'object', expected:'object') -> 'None':
    """ Adds a finding if a value is not the one that a production installation runs with.
    """
    if value != expected:
        findings.append(f'{name} is `{value}`, a production installation runs with `{expected}`')

# ################################################################################################################################

def _check_sqlite(findings:'strlist', database:'stranydict') -> 'None':
    """ Adds the findings of a SQLite Zato database.
    """
    _check_value(findings, 'journal_mode', database['journal_mode'], SQLite_Journal_Mode)
    _check_value(findings, 'synchronous', database['synchronous'], SQLite_Synchronous)

    if database['is_memory_filesystem']:
        findings.append(f'the database is on a file system held in memory, `{database["filesystem_type"]}`')

# ################################################################################################################################

def _check_postgresql(findings:'strlist', database:'stranydict') -> 'None':
    """ Adds the findings of a PostgreSQL Zato database.
    """
    synchronous_commit = database['synchronous_commit']

    if synchronous_commit in Relaxed_Commit_Levels:
        findings.append(f'synchronous_commit is `{synchronous_commit}`, a commit returns before it is durable')

    _check_value(findings, 'fsync', database['fsync'], Setting_On)
    _check_value(findings, 'full_page_writes', database['full_page_writes'], Setting_On)

    if database['standby_count'] and not database['synchronous_standby_names']:
        findings.append(f'{database["standby_count"]} streaming standby(s) and no synchronous one')

# ################################################################################################################################

def _check_data_directory(findings:'strlist', database:'PubSubDatabase') -> 'None':
    """ Adds a finding if the data directory of a PostgreSQL container is on a file system held in memory.
    """
    command = ['docker', 'exec', database.container_name, 'sh', '-c', ModuleCtx.Data_Directory_Type_Command]
    result = subprocess.run(command, capture_output=True, text=True, check=True)

    filesystem_type = result.stdout.strip()

    if filesystem_type in FilesystemCtx.Memory_Types:
        findings.append(f'the data directory of PostgreSQL is on a file system held in memory, `{filesystem_type}`')

    # The layers of a container are on the file system of the directory under which Docker keeps them
    elif filesystem_type == ModuleCtx.Overlay_Stat_Type:
        result = subprocess.run(ModuleCtx.Docker_Root_Command, capture_output=True, text=True, check=True)
        docker_root = result.stdout.strip()

        if is_memory_filesystem(docker_root):
            findings.append(f'the data directory of PostgreSQL is in an overlay held in memory under `{docker_root}`')

# ################################################################################################################################

def _get_findings(settings:'stranydict', database:'PubSubDatabase | None') -> 'strlist':
    """ Returns each way in which the settings of a measured server differ from those of a production installation.
    """
    out:'strlist' = []

    # The server is a process of its own ..
    if settings['pid'] == os.getpid():
        out.append('the server runs in the process of the test')

    # .. its database is durable and on a file system that is not held in memory ..
    if settings['database_type'] == Type_SQLite:
        _check_sqlite(out, settings['database'])
    else:
        _check_postgresql(out, settings['database'])

        if database is None:
            out.append('the PostgreSQL database of the measured server is not known to the test')
        else:
            _check_data_directory(out, database)

    # .. its audit log, group commits and pull lease are those of a production installation ..
    _check_value(out, 'is_audit_log_enabled', settings['is_audit_log_enabled'], AuditLogCtx.Default_Enabled)
    _check_value(out, 'audit_log_commit_max_events', settings['audit_log_commit_max_events'], Default_Commit_Max_Events)
    _check_value(out, 'audit_log_commits_in_flight', settings['audit_log_commits_in_flight'], Default_Max_In_Flight)
    _check_value(out, 'pubsub_commit_max_messages', settings['pubsub_commit_max_messages'], Default_Commit_Max_Messages)
    _check_value(out, 'pubsub_pull_lease_seconds', settings['pubsub_pull_lease_seconds'], Default_Pull_Lease_Seconds)

    # .. SQLite has a single writer whatever the environment says, while PostgreSQL takes the number of commits
    # .. in flight from it ..
    if settings['database_type'] != Type_SQLite:
        _check_value(out, 'pubsub_commits_in_flight', settings['pubsub_commits_in_flight'], Default_Commits_In_Flight)
        _check_value(out, 'pubsub_urgent_commits_in_flight', settings['pubsub_urgent_commits_in_flight'],
            Urgent_Commits_In_Flight)

    # .. so are its retention limits ..
    _check_value(out, 'audit_log_retention_days', settings['audit_log_retention_days'], Default_Retention_Days)
    _check_value(out, 'pubsub_delivered_max_messages', settings['pubsub_delivered_max_messages'],
        Default_Delivered_Max_Messages)
    _check_value(out, 'pubsub_delivered_max_days', settings['pubsub_delivered_max_days'], Default_Delivered_Max_Days)

    # .. and the node of an active-standby pair runs with its own timers.
    for name, value in settings['ha_timers'].items():
        if value is not None:
            out.append(f'{name} is `{value}`, a production node runs with its default')

    return out

# ################################################################################################################################

def _get_checked_settings(client:'AdminClient', database:'PubSubDatabase | None', moment:'str') -> 'stranydict':
    """ Returns the settings in force in the measured server, raising PerfSettingsError if they are not
    the settings of a production installation.
    """
    out = client.invoke(ModuleCtx.Settings_Service)

    if findings := _get_findings(out, database):
        findings_text = '; '.join(findings)
        raise PerfSettingsError(f'No figure is recorded, the settings {moment} the measurement -> {findings_text}')

    return out

# ################################################################################################################################
# ################################################################################################################################

def start_measurement(client:'AdminClient', database:'PubSubDatabase | None') -> 'Measurement':
    """ Begins a measurement of the server that the client invokes, whose PostgreSQL database is given,
    or None for a SQLite one, and returns the record of the settings with which report_result records its figures.
    """
    out = Measurement()
    out.client = client
    out.database = database
    out.settings_before = _get_checked_settings(client, database, 'before')

    return out

# ################################################################################################################################

def report_result(measurement:'Measurement', name:'str', figures:'stranydict') -> 'stranydict':
    """ Records the figures of a measurement with the settings in force in the measured server before and after it,
    once both are confirmed to be those of a production installation, and returns the record.
    """
    settings_after = _get_checked_settings(measurement.client, measurement.database, 'after')

    out:'stranydict' = {
        'name': name,
        'figures': figures,
        'settings_before': measurement.settings_before,
        'settings_after': settings_after,
    }

    line = json.dumps(out, sort_keys=True)
    logger.info('Performance result -> %s', line)

    if results_path := os.environ.get(ModuleCtx.Env_Results_File, ''):
        with open(results_path, 'a') as results_file:
            _ = results_file.write(line + '\n')

    return out

# ################################################################################################################################
# ################################################################################################################################
