# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Zato
from live_windows.docker_ import remove_directory
from live_windows.layout import layout_command
from live_windows.settings import Guest, Image, instance_dir, Paths, storage_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The file in the storage directory of a version that holds the memory and device state of its guest,
    # saved once the agent runs and the layout is applied
    State_Name = 'ready.state'

    # The file next to the storage directory that describes what the ready state was saved from
    Stamp_Name = 'ready.json'

    # The prepared disk in the storage directory, which every running guest of a version reads and none writes to
    Disk_Name = 'data.img'

    # Where the storage directory is inside a container
    Container_Storage = '/storage'

    # The QMP socket of QEMU inside a container
    QMP_Socket = '/run/zato-qmp.sock'

    # How long saving the ready state may take, in seconds
    Save_Timeout = 300

    # The script that saves the state, run by the Python of the image
    Save_Script = Path(__file__).parent / 'qmp_save.py'

# ################################################################################################################################
# ################################################################################################################################

def _source_hash() -> 'str':
    """ Returns a hash of everything that goes into a ready state - the image, the resources of the guest, the agent,
    the script that saves the state and the layout.
    """
    layout = layout_command()
    layout_document = json.dumps(layout, sort_keys=True)

    digest = hashlib.sha256()
    digest.update(Image.Name.encode('utf8'))
    digest.update(Guest.RAM_Size.encode('utf8'))
    digest.update(Guest.CPU_Cores.encode('utf8'))
    digest.update(Guest.CPU_Flags.encode('utf8'))
    digest.update(Guest.Hyper_V.encode('utf8'))
    digest.update(Paths.Agent_Path.read_bytes())
    digest.update(ModuleCtx.Save_Script.read_bytes())
    digest.update(layout_document.encode('utf8'))

    out = digest.hexdigest()
    return out

# ################################################################################################################################

def _stamp_path(version:'str') -> 'Path':
    out = storage_dir(version).parent / ModuleCtx.Stamp_Name
    return out

# ################################################################################################################################

def _state_path(version:'str') -> 'Path':
    out = storage_dir(version) / ModuleCtx.State_Name
    return out

# ################################################################################################################################

def is_ready(version:'str') -> 'bool':
    """ True if the ready state of a version exists and was saved from the current agent, layout and resources.
    """
    stamp_path = _stamp_path(version)

    if not stamp_path.exists():
        return False

    if not _state_path(version).exists():
        return False

    stamp = json.loads(stamp_path.read_text())

    out = stamp['source_hash'] == _source_hash()
    return out

# ################################################################################################################################

def discard(version:'str') -> 'None':
    """ Removes the ready state of a version and its stamp.
    """
    _stamp_path(version).unlink(missing_ok=True)
    _state_path(version).unlink(missing_ok=True)

# ################################################################################################################################

def write_stamp(version:'str') -> 'None':
    saved_at = datetime.now(timezone.utc)

    stamp = {
        'image': Image.Name,
        'source_hash': _source_hash(),
        'saved_at': saved_at.isoformat(),
    }

    stamp_document = json.dumps(stamp, indent=2)

    stamp_path = _stamp_path(version)
    _ = stamp_path.write_text(stamp_document)

# ################################################################################################################################

def save_arguments() -> 'str':
    """ Returns the QEMU arguments of a guest whose state is saved - its writes go to the prepared disk,
    and the harness reaches QEMU through a QMP socket.
    """
    out = f'-qmp unix:{ModuleCtx.QMP_Socket},server=on,wait=off'
    return out

# ################################################################################################################################

def restore_arguments() -> 'str':
    """ Returns the QEMU arguments of a guest resumed from the ready state - QEMU keeps every write in a temporary overlay,
    so the prepared disk stays as it was when the state was saved.
    """
    out = f'-snapshot -incoming file:{ModuleCtx.Container_Storage}/{ModuleCtx.State_Name}'
    return out

# ################################################################################################################################

def save_state(name:'str') -> 'str':
    """ Stops the guest of a container and saves its memory and device state into its storage directory.
    Returns what the script that saved it printed.
    """
    uri = f'file:{ModuleCtx.Container_Storage}/{ModuleCtx.State_Name}'
    script = ModuleCtx.Save_Script.read_text()
    save_timeout = str(ModuleCtx.Save_Timeout)

    command = ['docker', 'exec', '-i', name, 'python3', '-', ModuleCtx.QMP_Socket, uri, save_timeout]
    result = subprocess.run(command, input=script, text=True, capture_output=True, check=False)

    if result.returncode != 0:
        raise Exception(f'Could not save the state of {name} -> {result.stdout} {result.stderr}')

    out = result.stdout.strip()
    return out

# ################################################################################################################################

def instance_mounts(version:'str', instance:'str') -> 'strlist':
    """ Creates the storage directory of one guest of an instance and returns the Docker arguments that mount it.
    The guest receives copies of the small files that dockur and QEMU write to, and reads the prepared disk
    and the ready state of its version without a copy.
    """
    source_dir = storage_dir(version)
    target_dir = instance_dir(version, instance)

    if target_dir.exists():
        remove_directory(target_dir, Image.Name)

    target_dir.mkdir(parents=True)

    shared_names = ModuleCtx.Disk_Name, ModuleCtx.State_Name

    out:'strlist' = ['-v', f'{target_dir}:{ModuleCtx.Container_Storage}']

    for path in sorted(source_dir.iterdir()):

        if not path.is_file():
            continue

        # The shared files are mounted read-only over empty files of the same names, which Docker would otherwise
        # create as root ..
        if path.name in shared_names:
            mount_point = target_dir / path.name
            mount_point.touch()
            out.extend(['-v', f'{path}:{ModuleCtx.Container_Storage}/{path.name}:ro'])

        # .. and each of the other ones is copied.
        else:
            _ = shutil.copy2(path, target_dir)

    return out

# ################################################################################################################################

def remove_instance_storage(version:'str', instance:'str') -> 'None':
    """ Removes the storage directory of one guest of an instance, together with the files that its container created as root.
    """
    target_dir = instance_dir(version, instance)

    if target_dir.exists():
        remove_directory(target_dir, Image.Name)

# ################################################################################################################################
# ################################################################################################################################
