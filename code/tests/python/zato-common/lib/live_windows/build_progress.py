# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
import subprocess

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The status message that the container publishes for its web viewer
    Message_Path = '/dev/shm/msg.html'

    # The disk that Windows is installed to, in the container storage
    Data_Disk = 'data.img'

    # The size of one block that the file system reports a file's allocation in
    Block_Size = 512

    # The share of the whole build that each phase takes, in percent
    Download_Share = 40
    Prepare_Share  = 5
    Install_Share  = 50

    # The allocated size of the data disk after the installation and the provisioning, against which their progress is estimated
    Installed_Disk_Bytes = int(6.5 * 1024 ** 3)

    # A data disk with less than this allocated is not yet being installed to
    Install_Start_Bytes = 100 * 1024 ** 2

    # The highest estimate of the installation, which only the provisioning marker completes
    Install_Ceiling = 0.99

    Bytes_Per_GB = 1024 ** 3

    # The status message of a download in progress
    Download_Marker = 'Downloading'

    Tag_Pattern = re.compile(r'<[^>]+>')
    Percent_Pattern = re.compile(r'(\d+(?:\.\d+)?)%')

# ################################################################################################################################
# ################################################################################################################################

def _read_message(name:'str') -> 'str':
    """ Returns the status message of a container as plain text, or an empty string if it has none.
    """
    result = subprocess.run(
        ['docker', 'exec', name, 'cat', ModuleCtx.Message_Path], capture_output=True, text=True, check=False)

    text = ModuleCtx.Tag_Pattern.sub('', result.stdout)

    out = text.strip()
    return out

# ################################################################################################################################

def _message_ratio(message:'str') -> 'float':
    """ Returns the last percentage in a status message as a ratio, or zero if there is none.
    """
    matches = ModuleCtx.Percent_Pattern.findall(message)

    if not matches:
        return 0.0

    last = matches[-1]

    out = float(last) / 100
    return out

# ################################################################################################################################

def _disk_bytes(storage:'Path') -> 'int':
    """ Returns how many bytes of the data disk are allocated, which grows as Windows is installed.
    """
    path = storage / ModuleCtx.Data_Disk

    if not path.exists():
        return 0

    blocks = path.stat().st_blocks

    out = blocks * ModuleCtx.Block_Size
    return out

# ################################################################################################################################

def describe(name:'str', storage:'Path') -> 'str':
    """ Returns the overall progress of one build in percent, with the phase it is in.
    """
    message = _read_message(name)
    disk_bytes = _disk_bytes(storage)
    disk_gb = disk_bytes / ModuleCtx.Bytes_Per_GB

    # The media are being downloaded ..
    if message.startswith(ModuleCtx.Download_Marker):
        ratio = _message_ratio(message)
        done = ModuleCtx.Download_Share * ratio
        phase = message

    # .. Windows is being installed and provisioned, which only the growth of its disk shows ..
    elif disk_bytes >= ModuleCtx.Install_Start_Bytes:
        installed = disk_bytes / ModuleCtx.Installed_Disk_Bytes
        installed = min(installed, ModuleCtx.Install_Ceiling)
        done = ModuleCtx.Download_Share + ModuleCtx.Prepare_Share + ModuleCtx.Install_Share * installed
        phase = f'Installing and provisioning Windows, data disk at {disk_gb:.1f} GB'

    # .. or the media are being prepared for an unattended installation.
    else:
        ratio = _message_ratio(message)
        done = ModuleCtx.Download_Share + ModuleCtx.Prepare_Share * ratio
        phase = message

    out = f'{int(done)}% - {phase}'
    return out

# ################################################################################################################################
# ################################################################################################################################
