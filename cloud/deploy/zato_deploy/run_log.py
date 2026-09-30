# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import hashlib
import logging
import os
import sys
from logging import getLogger

# Zato
from zato_deploy.common import Config, Path, Restart_Reason, strlist
from zato_deploy.process import run_command
from zato_deploy.state import stage_list

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Log_Format = '%(asctime)s %(levelname)s %(name)s - %(message)s'

# The commands whose output describes the host at the end of a run and when a run fails.
_Snapshot_Commands = [
    ['uptime'],
    ['free', '-m'],
    ['df', '-h', '/', '/var/lib/docker'],
    ['findmnt', '-n', Path.Local_Disk_Mount],
    ['systemctl', 'is-active', 'docker.service', 'containerd.service'],
    ['docker', 'ps', '-a', '--no-trunc'],
    ['docker', 'images'],
    ['iptables', '-t', 'nat', '-S', 'PREROUTING'],
    ['ss', '-ltnp'],
]

# ################################################################################################################################
# ################################################################################################################################

def setup_logging(log_path:'str') -> 'None':
    """ Sends the log to the journal through stdout and to a file that survives the journal's rotation.
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    handlers:'list[logging.Handler]' = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_path),
    ]

    logging.basicConfig(level=logging.INFO, format=_Log_Format, handlers=handlers)

# ################################################################################################################################

def read_restart_reason() -> 'str':
    """ Returns why this run started, which the environment repository service leaves in a file before a restart.
    """
    if not os.path.exists(Path.Restart_Reason):
        return Restart_Reason.Boot

    with open(Path.Restart_Reason) as input_file:
        out = input_file.read().strip()

    os.remove(Path.Restart_Reason)

    if not out:
        out = Restart_Reason.Boot

    return out

# ################################################################################################################################

def _read_first_line(path:'str') -> 'str':

    with open(path) as input_file:
        out = input_file.readline().strip()

    return out

# ################################################################################################################################

def _get_program_files() -> 'strlist':

    out:'strlist' = []

    if not os.path.exists(Path.Files_List):
        return out

    with open(Path.Files_List) as input_file:
        lines = input_file.read().splitlines()

    for line in lines:
        line = line.strip()
        if line:
            out.append(line)

    return out

# ################################################################################################################################

def _get_sha256(path:'str') -> 'str':

    digest = hashlib.sha256()

    with open(path, 'rb') as input_file:
        while chunk := input_file.read(65536):
            digest.update(chunk)

    out = digest.hexdigest()
    return out

# ################################################################################################################################

def _log_file_hashes() -> 'None':
    """ Logs the hash of each program file, so a run can be matched to the exact version that ran it.
    """
    for name in _get_program_files():
        path = os.path.join(Path.Program_Dir, name)
        if os.path.isfile(path):
            logger.info('File %s sha256 %s', name, _get_sha256(path))
        else:
            logger.info('File %s missing', name)

# ################################################################################################################################

def _log_stages(stages:'stage_list') -> 'None':

    names:'strlist' = []

    for stage in stages:
        names.append(stage.id)

    logger.info('Stages to run: %s', ', '.join(names))

# ################################################################################################################################

def log_run_header(config:'Config', reason:'str', stages:'stage_list') -> 'None':

    logger.info('Run started, reason: %s', reason)
    logger.info('Boot ID %s, uptime %s', _read_first_line(Path.Boot_ID), _read_first_line(Path.Uptime))
    logger.info('Image %s, FQDN %s, Zato_Install_Updates %s', config.image, config.fqdn, config.is_install_updates)

    _log_file_hashes()
    _log_stages(stages)

# ################################################################################################################################

def log_host_snapshot(label:'str') -> 'None':

    logger.info('Host snapshot: %s', label)

    for command in _Snapshot_Commands:
        try:
            _ = run_command(command)
        except OSError as exception:
            logger.info('Snapshot command %s not run: %s', command[0], exception)

# ################################################################################################################################
# ################################################################################################################################
