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
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from threading import Thread
from time import monotonic, sleep

# Zato
from live_windows.build_progress import describe
from live_windows.docker_ import container_is_running, follow_logs, published_port, remove_container, remove_directory
from live_windows.settings import Accounts, computer_name, Control, container_name, Guest, Image, iso_name, Media, \
    Paths, storage_dir
from live_windows.share_client import ShareClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

threadlist = list[Thread]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The file next to each prepared disk that describes how it was built
    Stamp_Name = 'stamp.json'

    # How long one build may take, in seconds, including the download of the installation media
    Build_Timeout = 3 * 60 * 60

    # How often a build checks whether the provisioning finished, in seconds
    Poll_Interval = 10

    # After how many seconds a build reports that it is still waiting
    Report_Every = 60

    # The license status of an activated installation
    License_Licensed = 1

    # How many connections download the installation media at once
    Download_Connections = 16

    # Where the container reads installation media that it does not download itself
    Custom_ISO_Path = '/boot.iso'

    # The directory in the container storage that holds a download in progress
    Download_Dir = 'tmp'

    # The suffix of the file that marks a download as incomplete
    Partial_Suffix = '.aria2'

# ################################################################################################################################
# ################################################################################################################################

class BuildFailed(Exception):
    """ Raised when a prepared disk could not be built.
    """

# ################################################################################################################################
# ################################################################################################################################

def _settings_document() -> 'str':
    """ Returns the settings that the provisioning script reads from C:\\OEM\\settings.json.
    """
    settings = {
        'harness_username': Accounts.Harness_Username,
        'harness_password': Accounts.Harness_Password,
    }

    out = json.dumps(settings, indent=2)
    return out

# ################################################################################################################################

def _source_hash() -> 'str':
    """ Returns a hash of everything that goes into a prepared disk - the image, the guest scripts and their settings.
    """
    digest = hashlib.sha256()
    digest.update(Image.Name.encode('utf8'))

    settings = _settings_document()
    digest.update(settings.encode('utf8'))

    for path in sorted(Paths.OEM_Dir.iterdir()):
        name = path.name.encode('utf8')
        data = path.read_bytes()
        digest.update(name)
        digest.update(data)

    out = digest.hexdigest()
    return out

# ################################################################################################################################

def _stamp_path(version:'str') -> 'Path':
    out = storage_dir(version).parent / ModuleCtx.Stamp_Name
    return out

# ################################################################################################################################

def is_current(version:'str') -> 'bool':
    """ True if the prepared disk of a version exists, was built from the current sources and is not too old.
    """
    stamp_path = _stamp_path(version)

    if not stamp_path.exists():
        return False

    stamp = json.loads(stamp_path.read_text())

    if stamp['source_hash'] != _source_hash():
        return False

    built_at = datetime.fromisoformat(stamp['built_at'])
    age = datetime.now(timezone.utc) - built_at

    out = age.days < Guest.Max_Disk_Age_Days
    return out

# ################################################################################################################################

def _stage_oem_dir() -> 'Path':
    """ Copies the guest scripts into a temporary directory and adds their settings to it.
    """
    staging_dir = Path(tempfile.mkdtemp(prefix='zato-test-windows-oem-'))

    for path in Paths.OEM_Dir.iterdir():
        _ = shutil.copy(path, staging_dir)

    settings = _settings_document()

    settings_path = staging_dir / 'settings.json'
    _ = settings_path.write_text(settings)

    return staging_dir

# ################################################################################################################################

def _run_container(version:'str', oem_dir:'Path') -> 'None':
    """ Starts the container that installs and provisions one Windows version.
    """
    name = container_name(version)
    host = computer_name(version)
    storage = storage_dir(version)
    iso_path = Paths.ISO_Dir / iso_name(version)
    release, language = Media[version]

    command:'strlist' = [
        'docker', 'run', '-d',
        '--name', name,
        '--device', '/dev/kvm',
        '--device', '/dev/net/tun',
        '--cap-add', 'NET_ADMIN',
        '--stop-timeout', str(Image.Stop_Timeout),
        '-e', f'VERSION={release}',
        '-e', f'LANGUAGE={language}',
        '-e', f'EDITION={Guest.Edition}',
        '-e', f'DISK_SIZE={Guest.Disk_Size}',
        '-e', f'RAM_SIZE={Guest.RAM_Size}',
        '-e', f'CPU_CORES={Guest.CPU_Cores}',
        '-e', f'USERNAME={Accounts.Admin_Username}',
        '-e', f'PASSWORD={Accounts.Admin_Password}',
        '-e', f'HOST={host}',
        '-e', 'SAMBA=N',
        '-e', 'LOG=Y',
        '-e', f'CONNECTIONS={ModuleCtx.Download_Connections}',
        '-v', f'{storage}:/storage',
        '-v', f'{oem_dir}:/oem',
        '-p', f'127.0.0.1::{Guest.SMB_Port}',
    ]

    # Media downloaded by an earlier build are installed from directly, without a download ..
    if iso_path.exists():
        command.extend(['-v', f'{iso_path}:{ModuleCtx.Custom_ISO_Path}:ro'])

    # .. and the image name closes the command.
    command.append(Image.Name)

    _ = subprocess.run(command, check=True, capture_output=True)

# ################################################################################################################################

def _keep_iso(version:'str') -> 'None':
    """ Moves the installation media that a container downloaded into the directory of ISO files,
    from which every later build installs.
    """
    name = iso_name(version)
    target = Paths.ISO_Dir / name

    if target.exists():
        return

    storage = storage_dir(version)
    download_dir = storage / ModuleCtx.Download_Dir

    for candidate in storage / name, download_dir / name:

        partial = candidate.with_name(name + ModuleCtx.Partial_Suffix)

        # Only a complete download is worth keeping ..
        if candidate.exists() and not partial.exists():

            # .. and it is moved rather than copied, so that no ISO file stays in the storage.
            Paths.ISO_Dir.mkdir(parents=True, exist_ok=True)
            _ = shutil.move(candidate, target)

            print(f'[WIN{version} BUILD] Installation media kept in {target}', flush=True)
            return

# ################################################################################################################################

def _wait_for_provisioning(version:'str') -> 'anydict':
    """ Waits until the provisioning script reports through the control share that it finished,
    and returns what it reported.
    """
    name = container_name(version)
    storage = storage_dir(version)
    port = published_port(name, Guest.SMB_Port)

    client = ShareClient('127.0.0.1', port, Accounts.Harness_Username, Accounts.Harness_Password)

    start = monotonic()
    last_report = start
    last_error = ''

    while True:

        elapsed = monotonic() - start

        # A container that stopped will not provision anything ..
        if not container_is_running(name):
            raise BuildFailed(f'Container {name} stopped during the installation of Windows Server {version}')

        # .. the build has a ceiling of its own ..
        if elapsed > ModuleCtx.Build_Timeout:
            raise BuildFailed(f'Windows Server {version} was not provisioned within {ModuleCtx.Build_Timeout}s, ' +
                f'last error: {last_error}')

        # .. the control share exists only once the provisioning has started ..
        try:
            client.connect()

            if client.exists(Control.Share, Control.Provision_Error):
                details = client.read_text(Control.Share, Control.Provision_Error)
                raise BuildFailed(f'Provisioning of Windows Server {version} failed -> {details}')

            if client.exists(Control.Share, Control.Provisioned):
                marker = client.read_text(Control.Share, Control.Provisioned)
                client.close()
                out = json.loads(marker)
                return out

        except BuildFailed:
            raise

        except Exception as e:
            last_error = f'{e.__class__.__name__}: {e}'
            client.close()

        # .. and a long wait reports how far the build is.
        now = monotonic()

        if now - last_report >= ModuleCtx.Report_Every:
            last_report = now
            progress = describe(name, storage)
            print(f'[WIN{version} BUILD] {progress}, {int(elapsed)}s', flush=True)

        sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

def _write_stamp(version:'str', marker:'anydict') -> 'None':
    built_at = datetime.now(timezone.utc)

    stamp = {
        'image': Image.Name,
        'source_hash': _source_hash(),
        'built_at': built_at.isoformat(),
        'windows': marker,
    }

    stamp_path = _stamp_path(version)
    stamp_document = json.dumps(stamp, indent=2)

    _ = stamp_path.write_text(stamp_document)

# ################################################################################################################################

def build(version:'str') -> 'None':
    """ Installs one Windows version from its evaluation media, provisions it and shuts it down,
    which leaves the prepared disk that test sessions boot from.
    """
    name = container_name(version)
    storage = storage_dir(version)
    prefix = f'[WIN{version} BUILD]'

    # A previous build that did not finish leaves nothing that can be reused, apart from its downloaded media ..
    remove_container(name)
    _keep_iso(version)

    if storage.parent.exists():
        remove_directory(storage.parent, Image.Name)

    storage.mkdir(parents=True)

    oem_dir = _stage_oem_dir()

    try:

        # .. the container downloads the media, installs Windows and runs the provisioning script ..
        print(f'{prefix} Starting container {name}, storage in {storage}', flush=True)
        _run_container(version, oem_dir)
        _ = follow_logs(name, prefix)

        marker = _wait_for_provisioning(version)

        status = marker['license_status']
        if status != ModuleCtx.License_Licensed:
            raise BuildFailed(f'Windows Server {version} is not activated, license status {status} -> {marker}')

        print(f'{prefix} 95% - Provisioned -> {marker}', flush=True)

        # .. Windows is shut down cleanly, so that the disk is consistent ..
        print(f'{prefix} Shutting down', flush=True)
        stop_timeout = str(Image.Stop_Timeout)
        _ = subprocess.run(['docker', 'stop', '--time', stop_timeout, name], check=True, capture_output=True)

        # .. and the stamp says that the disk is ready for use.
        _write_stamp(version, marker)
        print(f'{prefix} 100% - Done', flush=True)

    finally:
        remove_container(name)
        _keep_iso(version)
        shutil.rmtree(oem_dir, ignore_errors=True)

# ################################################################################################################################

def pull_image() -> 'None':
    print(f'Pulling {Image.Name}', flush=True)
    _ = subprocess.run(['docker', 'pull', Image.Name], check=True)

# ################################################################################################################################

def build_missing(versions:'strlist', force:'bool'=False) -> 'None':
    """ Builds, in parallel, the prepared disks of the versions that have none, or whose disks are out of date.
    """
    to_build:'strlist' = []

    for version in versions:
        if force:
            to_build.append(version)
        elif not is_current(version):
            to_build.append(version)
        else:
            print(f'[WIN{version} BUILD] The prepared disk is current', flush=True)

    if not to_build:
        return

    pull_image()

    errors:'anydict' = {}
    threads:'threadlist' = []

    def _build(version:'str') -> 'None':
        try:
            build(version)
        except Exception as e:

            # The first failure is reported at once ..
            errors[version] = e
            print(f'[WIN{version} BUILD] Failed -> {e}', flush=True)

            # .. and it ends the other builds too, whose waits stop as soon as their containers are gone.
            for other_version in to_build:
                other_name = container_name(other_version)
                remove_container(other_name)

    for version in to_build:
        thread = Thread(target=_build, args=(version,), daemon=True, name=f'build-win{version}')
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    if errors:
        raise BuildFailed(f'Builds failed -> {errors}')

# ################################################################################################################################
# ################################################################################################################################
