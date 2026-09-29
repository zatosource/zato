# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import subprocess
import time

# Zato
from zato_deploy.common import Path, Stage_ID, StageFailed, strnone
from zato_deploy.docker_api import is_docker_answering
from zato_deploy.process import run_logged
from zato_deploy.state import Progress

# ################################################################################################################################
# ################################################################################################################################

_Apt_Env = {'DEBIAN_FRONTEND': 'noninteractive'}

# apt waits this many seconds for the lock that the first boot's own package jobs may still hold.
_Apt_Lock_Timeout = 'DPkg::Lock::Timeout=600'

_Docker_Start_Timeout = 120

# What lsblk calls the local NVMe disk of VM sizes that have one.
_NVMe_Model = 'direct disk'

# The directories that move onto the local NVMe disk.
_Docker_Data_Dirs = ['docker', 'containerd']

# ################################################################################################################################
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
    """ Installs Docker from the Ubuntu archive and waits until it answers.
    """
    progress.advance_to(Stage_ID.Docker)

    run_logged(progress, ['apt-get', '-q', '-o', _Apt_Lock_Timeout, 'update'], _Apt_Env)
    run_logged(progress, ['apt-get', '-q', '-o', _Apt_Lock_Timeout, 'install', '-y', 'docker.io'], _Apt_Env)

    _wait_for_docker(progress)

# ################################################################################################################################
# ################################################################################################################################

def _find_nvme_device() -> 'strnone':
    """ Returns the local NVMe disk of this VM size, or None if it has none.
    """
    if os.path.exists(Path.NVMe_Device):
        return Path.NVMe_Device

    result = subprocess.run(['lsblk', '-dpno', 'NAME,MODEL'], capture_output=True, text=True)
    lines = result.stdout.splitlines()

    for line in lines:
        name, _, model = line.partition(' ')
        model = model.lower()
        if _NVMe_Model in model:
            out = name
            break
    else:
        out = None

    return out

# ################################################################################################################################

def prepare_storage(progress:'Progress') -> 'None':
    """ Moves Docker and containerd onto the local NVMe disk if the VM size has one,
    because the OS disk is throttled to a fraction of the throughput that extracting the image needs.
    """
    progress.advance_to(Stage_ID.Storage)

    device = _find_nvme_device()

    if not device:
        progress.log('No local NVMe disk, Docker stays on the OS disk')
        return

    # The image may have mounted the disk somewhere already ..
    result = subprocess.run(['findmnt', '--source', device], capture_output=True)
    if result.returncode == 0:
        run_logged(progress, ['umount', device])

    # .. it gets a new file system of its own ..
    run_logged(progress, ['mkfs.ext4', '-F', device])
    os.makedirs(Path.NVMe_Mount, exist_ok=True)
    run_logged(progress, ['mount', device, Path.NVMe_Mount])

    # .. Docker stops while its data moves ..
    run_logged(progress, ['systemctl', 'stop', 'docker', 'docker.socket', 'containerd'])

    for name in _Docker_Data_Dirs:
        source = os.path.join('/var/lib', name)
        target = os.path.join(Path.NVMe_Mount, name)
        _ = shutil.move(source, target)
        os.symlink(target, source)

    progress.log(f'Docker data moved to {Path.NVMe_Mount}')

    # .. and it starts again from the new place.
    run_logged(progress, ['systemctl', 'start', 'containerd', 'docker'])
    _wait_for_docker(progress)

# ################################################################################################################################
# ################################################################################################################################
