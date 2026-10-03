# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from base64 import b64encode
from dataclasses import asdict
from logging import getLogger
from subprocess import PIPE, Popen
from traceback import format_exc

# Zato
from zato.common.api import HL7
from zato.common.bearer_token import normalize_scopes
from zato.common.const import ServiceConst
from zato.common.hl7.fhir.bulk_export.pid import is_job_running, write_pid_file
from zato.common.hl7.fhir.bulk_export.spec import get_download_dir, JobSpec, JobState
from zato.common.typing_ import cast_
from zato.common.util.api import new_cid
from zato.common.util.config import get_url_protocol_from_config_item

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, binaryio_, stranydict, strdict, strlist
    from zato.server.base.parallel import ParallelServer

    ParallelServer = ParallelServer
    any_           = any_
    binaryio_      = binaryio_
    stranydict     = stranydict
    strdict        = strdict
    strlist        = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_bulk = HL7.BulkExport
_basic_auth = HL7.Const.FHIR_Auth_Type.Basic_Auth.id
_oauth = HL7.Const.FHIR_Auth_Type.OAuth.id

# Every environment variable the audit log reads starts with this
Audit_Env_Prefix = 'Zato_Audit_Log_'

# The module the detached process runs
Program_Module = 'zato.common.hl7.fhir.bulk_export.program'

# The lock the workers of one server take turns under when resuming jobs
Resume_Lock_Name = 'zato.fhir.bulk-export.resume'

# ################################################################################################################################
# ################################################################################################################################

def to_list(value:'any_') -> 'strlist':
    """ Turns a comma or newline separated string, or a list, into a list of stripped non-empty strings.
    """
    out = []

    if isinstance(value, str):
        value = value.replace(',', '\n')
        value = value.splitlines()

    for item in value:
        item = item.strip()
        if item:
            out.append(item)

    return out

# ################################################################################################################################

def get_audit_env() -> 'strdict':
    out = {}
    for key, value in os.environ.items():
        if key.startswith(Audit_Env_Prefix):
            out[key] = value

    return out

# ################################################################################################################################

def get_invoke_url(server:'ParallelServer') -> 'str':
    protocol = get_url_protocol_from_config_item(server.fs_server_config.crypto.use_tls)
    out = f'{protocol}://{server.preferred_address}:{server.port}'
    return out

# ################################################################################################################################

def get_basic_auth_header(username:'str', password:'str') -> 'str':
    data = f'{username}:{password}'.encode('ascii')
    out = 'Basic ' + b64encode(data).decode('ascii')
    return out

# ################################################################################################################################

def get_bearer_config(server:'ParallelServer', security_id:'int') -> 'tuple[stranydict, str, str]':
    """ Returns the bearer token definition of a connection with its secrets decrypted, along with
    its data format and scopes, so the program can obtain tokens with no access to the server.
    """
    sec_def = server.security_facade.get_bearer_token_by_id(security_id)
    config = server.bearer_token_manager._get_bearer_token_config(sec_def)

    config.password = server.decrypt(config.password)
    config.private_key = server.decrypt(config.private_key)

    scopes = sec_def.get('scopes')
    if scopes:
        scopes = normalize_scopes(scopes)
    else:
        scopes = ''

    out = asdict(config)
    return out, sec_def['data_format'], scopes

# ################################################################################################################################

def get_override(conn_config:'stranydict', overrides:'stranydict', name:'str') -> 'any_':
    """ An override given on input replaces the tab's value, an empty one leaves the tab's value in place.
    """
    out = overrides.get(name)
    if not out:
        out = conn_config[_bulk.Field_Prefix + name]

    return out

# ################################################################################################################################

def build_job_spec(server:'ParallelServer', conn_config:'stranydict', overrides:'stranydict') -> 'JobSpec':
    """ Builds the spec of a new job from a connection's configuration, with any overrides applied.
    """
    spec = JobSpec()

    spec.job_id = new_cid()
    spec.conn_id = conn_config['id']
    spec.conn_name = conn_config['name']
    spec.server_name = server.name

    spec.address = conn_config['address']
    spec.auth_type = conn_config['auth_type']

    # The program authenticates on its own so it receives what it needs ready to use ..
    if spec.auth_type == _basic_auth:
        spec.basic_auth_header = get_basic_auth_header(conn_config['username'], conn_config['secret'])

    elif spec.auth_type == _oauth:
        spec.bearer, spec.bearer_data_format, spec.scopes = get_bearer_config(server, conn_config['security_id'])

    # .. what to export comes from the tab unless overridden ..
    spec.level = get_override(conn_config, overrides, 'level')
    spec.group_id = get_override(conn_config, overrides, 'group_id')
    spec.patient_ids = to_list(get_override(conn_config, overrides, 'patient_ids'))
    spec.types = to_list(get_override(conn_config, overrides, 'types'))
    spec.since = get_override(conn_config, overrides, 'since')
    spec.type_filter = to_list(get_override(conn_config, overrides, 'type_filter'))

    # .. destinations given for this job alone travel with it, otherwise the connection's are used at delivery time ..
    destinations = overrides.get('destinations')
    if destinations:
        spec.destinations = destinations

    # .. where the files go ..
    spec.download_dir = get_download_dir(server.work_dir)
    spec.delete_files = conn_config[_bulk.Field_Delete_Files]
    spec.delete_on_server = conn_config[_bulk.Field_Delete_On_Server]

    # .. how the program hands files back to this server ..
    admin = server.config_manager.basic_auth_get(ServiceConst.API_Admin_Invoke_Username).config
    spec.invoke_url = get_invoke_url(server)
    spec.invoke_username = admin['username']
    spec.invoke_password = server.decrypt(admin['password'])

    # .. and which audit log it writes to.
    spec.audit_env = get_audit_env()

    return spec

# ################################################################################################################################

def start_job(server:'ParallelServer', spec:'JobSpec') -> 'str':
    """ Starts the export program as a process of its own that outlives this server's workers,
    handing it the spec on stdin, and returns the job's id.
    """
    log_path = os.path.join(server.logs_dir, _bulk.Log_File_Name)

    # The interpreter itself, not a shell wrapper around it, because the pid recorded below
    # must be the program's own or the program would find the job claimed by someone else and exit.
    command = [sys.executable, '-m', Program_Module]

    with open(log_path, 'a') as log_file:
        process = Popen(command, stdin=PIPE, stdout=log_file, stderr=log_file, start_new_session=True)

    # The spec goes in and stdin is closed so the program knows it has all of it
    stdin = cast_('binaryio_', process.stdin)
    _ = stdin.write(spec.to_json().encode('utf8'))
    stdin.close()

    # The job is claimed for the process right away so another worker resuming jobs sees it is taken
    write_pid_file(spec.job_dir, process.pid)

    logger.info('Started FHIR bulk export %s for `%s` (pid: %s)', spec.job_id, spec.conn_name, process.pid)

    out = spec.job_id
    return out

# ################################################################################################################################

def find_unfinished_jobs(download_dir:'str') -> 'list[JobState]':
    """ Returns the state of every job in the download directory that did not finish.
    """
    out = []

    if not os.path.isdir(download_dir):
        return out

    for name in sorted(os.listdir(download_dir)):
        job_dir = os.path.join(download_dir, name)
        state_path = os.path.join(job_dir, _bulk.State_File_Name)

        if not os.path.exists(state_path):
            continue

        state = JobState.load(job_dir)
        if not state.is_finished:
            out.append(state)

    return out

# ################################################################################################################################

def resume_unfinished_jobs(server:'ParallelServer') -> 'None':
    """ Starts the program again for every job a previous server process left unfinished,
    each from its connection's current configuration.
    """
    download_dir = get_download_dir(server.work_dir)

    # The workers of this server take turns so each job is started once
    with server.zato_lock_manager(Resume_Lock_Name):
        for state in find_unfinished_jobs(download_dir):
            _resume_one_job(server, download_dir, state)

# ################################################################################################################################

def _resume_one_job(server:'ParallelServer', download_dir:'str', state:'JobState') -> 'None':

    try:
        # A job another worker already started is left alone ..
        job_dir = os.path.join(download_dir, state.job_id)
        if is_job_running(job_dir):
            return

        # .. a connection that no longer exists has nothing to resume ..
        item = server.config_manager.outconn_hl7_fhir.get(state.conn_name)
        if not item:
            logger.info('Not resuming FHIR bulk export %s, connection `%s` no longer exists', state.job_id, state.conn_name)
            return

        spec = build_job_spec(server, item, {})

        # .. the job keeps its id so its state and files are found again.
        spec.job_id = state.job_id

        _ = start_job(server, spec)
        logger.info('Resumed FHIR bulk export %s for `%s`', state.job_id, state.conn_name)

    except Exception:
        logger.warning('Could not resume FHIR bulk export %s -> %s', state.job_id, format_exc())

# ################################################################################################################################
# ################################################################################################################################
