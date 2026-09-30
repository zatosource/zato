# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time

# Zato
from zato_deploy.common import Line_Kind, Local_Disk, Path, Stage_ID, StageFailed, strlist, strnone, Systemd_Unit
from zato_deploy.docker_api import is_docker_answering
from zato_deploy.process import run_command, run_logged
from zato_deploy.state import Progress

# ################################################################################################################################
# ################################################################################################################################

_Apt_Env = {'DEBIAN_FRONTEND': 'noninteractive'}

# apt waits this many seconds for the lock that the first boot's own package jobs may still hold.
_Apt_Lock_Timeout = 'DPkg::Lock::Timeout=600'

_Docker_Package       = 'docker.io'
_Docker_Start_Timeout = 120

# What dpkg-query prints for a package that is installed.
_Installed_Status = 'install ok installed'

_File_System = 'ext4'

# The directories that are kept on the local disk.
_Docker_Data_Dirs = ['docker', 'containerd']

_Local_Disk_Models:'strlist' = []

for _model in Local_Disk.Models:
    _Local_Disk_Models.append(_model.lower())

# ################################################################################################################################
# ################################################################################################################################

def is_docker_installed() -> 'bool':

    result = run_command(['dpkg-query', '-W', '-f=${Status}', _Docker_Package])

    out = result.stdout.strip() == _Installed_Status
    return out

# ################################################################################################################################

def _wait_for_docker(progress:'Progress') -> 'None':

    deadline = time.monotonic() + _Docker_Start_Timeout

    while not is_docker_answering():
        now = time.monotonic()
        if now > deadline:
            raise StageFailed(f'Docker did not start within {_Docker_Start_Timeout} seconds')
        time.sleep(1)

    progress.log('Docker is running', 'ok')

# ################################################################################################################################

def install_docker(progress:'Progress') -> 'None':
    """ Installs Docker from the Ubuntu archive and leaves its start to this program, after the storage is ready.
    """
    progress.advance_to(Stage_ID.Docker)

    run_logged(progress, ['apt-get', '-q', '-o', _Apt_Lock_Timeout, 'update'], _Apt_Env)
    run_logged(progress, ['apt-get', '-q', '-o', _Apt_Lock_Timeout, 'install', '-y', _Docker_Package], _Apt_Env)

    command = ['systemctl', 'disable']
    command.extend(Systemd_Unit.Docker)
    run_logged(progress, command)

# ################################################################################################################################

def start_docker(progress:'Progress') -> 'None':

    command = ['systemctl', 'start']
    command.extend(Systemd_Unit.Docker)
    run_logged(progress, command)

    _wait_for_docker(progress)

# ################################################################################################################################
# ################################################################################################################################

def _is_local_disk_model(model:'str') -> 'bool':

    model = model.lower()

    for known_model in _Local_Disk_Models:
        if known_model in model:
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################

def _find_local_disk() -> 'strnone':
    """ Returns the local NVMe disk of this VM size, or None if it has none.
    """
    result = run_command(['lsblk', '-dpno', 'NAME,MODEL'])
    lines = result.stdout.splitlines()

    for line in lines:
        name, _, model = line.partition(' ')
        if _is_local_disk_model(model):
            out = name
            break
    else:
        out = None

    return out

# ################################################################################################################################

def _get_mount_point(device:'str') -> 'strnone':
    """ Returns where a device is mounted, or None if it is not.
    """
    result = run_command(['findmnt', '-n', '-o', 'TARGET', '--source', device])

    if result.exit_code != 0:
        return None

    out = result.stdout.strip()
    return out

# ################################################################################################################################

def _is_mount_point(path:'str') -> 'bool':

    result = run_command(['findmnt', '-n', '--mountpoint', path])

    out = result.exit_code == 0
    return out

# ################################################################################################################################

def _has_file_system(device:'str') -> 'bool':

    result = run_command(['blkid', '-o', 'value', '-s', 'TYPE', device])

    out = result.stdout.strip() == _File_System
    return out

# ################################################################################################################################

def prepare_storage(progress:'Progress') -> 'None':
    """ Puts the data of Docker and containerd on the local disk if the VM size has one,
    because the OS disk is throttled to a fraction of the throughput that extracting the image needs.
    The disk keeps its file system across reboots and loses it when the VM is deallocated.
    """
    progress.advance_to(Stage_ID.Storage)

    device = _find_local_disk()

    if not device:
        progress.log('No local NVMe disk, Docker stays on the OS disk')
        return

    mount_point = _get_mount_point(device)

    # The disk is already where it belongs if this is a restart rather than a boot ..
    if mount_point == Path.Local_Disk_Mount:
        progress.log(f'{device} is mounted on {mount_point}')

    else:

        # .. otherwise the image may have mounted it somewhere else ..
        if mount_point:
            run_logged(progress, ['umount', device])

        # .. it gets a new file system unless it kept the one from an earlier boot ..
        if _has_file_system(device):
            progress.log(f'{device} has a file system from an earlier boot')
        else:
            run_logged(progress, ['mkfs.ext4', '-F', device])

        os.makedirs(Path.Local_Disk_Mount, exist_ok=True)
        run_logged(progress, ['mount', device, Path.Local_Disk_Mount])

    # .. and each data directory is a view of a directory on that disk.
    for name in _Docker_Data_Dirs:
        source = os.path.join('/var/lib', name)
        target = os.path.join(Path.Local_Disk_Mount, name)
        os.makedirs(source, exist_ok=True)
        os.makedirs(target, exist_ok=True)
        if _is_mount_point(source):
            continue
        run_logged(progress, ['mount', '--bind', target, source])

    progress.log(f'Docker data is on {device}', Line_Kind.OK)

# ################################################################################################################################
# ################################################################################################################################
