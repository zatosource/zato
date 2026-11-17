# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import subprocess
from dataclasses import dataclass
from threading import Thread
from time import monotonic, sleep

# Zato
from live_containers.ready import ContainerExited
from live_windows.agent_client import AgentClient
from live_windows.build import build_missing
from live_windows.docker_ import container_is_running, follow_logs, published_port, remove_container
from live_windows.layout import layout_command
from live_windows.settings import Accounts, container_name, Guest, Image, Media, Paths, storage_dir
from live_windows.share_client import ShareClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The host the published ports of the guests listen on
    Host = '127.0.0.1'

    # How long a guest may take to boot until its SMB server accepts a logon, in seconds
    Boot_Timeout = 300

    # How long the agent may take to start and to apply the layout, in seconds
    Agent_Timeout = 60

    # How often a boot is checked, and how often its progress is reported, in seconds
    Poll_Interval = 1
    Report_Every  = 5

    # The run name of the commands sent while a guest starts
    Setup_Run = 'setup'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class GuestInfo:
    version: str
    name:    str
    port:    int

    @property
    def prefix(self) -> 'str':
        out = f'[WIN{self.version.upper()}]'
        return out

    def harness_client(self) -> 'ShareClient':
        out = ShareClient(ModuleCtx.Host, self.port, Accounts.Harness_Username, Accounts.Harness_Password)
        return out

    def exchange_client(self) -> 'ShareClient':
        out = ShareClient(ModuleCtx.Host, self.port, Accounts.Exchange_Username, Accounts.Exchange_Password)
        return out

    def agent_client(self) -> 'AgentClient':
        client = self.harness_client()

        out = AgentClient(client, self.prefix)
        return out

    def to_dict(self) -> 'anydict':
        out = {
            'version': self.version,
            'name': self.name,
            'port': self.port,
        }
        return out

    @staticmethod
    def from_dict(data:'anydict') -> 'GuestInfo':
        out = GuestInfo()
        out.version = data['version']
        out.name = data['name']
        out.port = data['port']
        return out

# ################################################################################################################################
# ################################################################################################################################

guestlist = list[GuestInfo]
threadlist = list[Thread]

# ################################################################################################################################
# ################################################################################################################################

def _run_container(version:'str') -> 'None':
    """ Boots a guest from its prepared disk. QEMU keeps every write in a temporary overlay,
    so the prepared disk is the same after the container stops as it was before it started.
    """
    name = container_name(version)
    storage = storage_dir(version)
    release, language = Media[version]

    command:'strlist' = [
        'docker', 'run', '-d', '--rm',
        '--name', name,
        '--device', '/dev/kvm',
        '--device', '/dev/net/tun',
        '--cap-add', 'NET_ADMIN',
        '--stop-timeout', '10',
        '-e', f'VERSION={release}',
        '-e', f'LANGUAGE={language}',
        '-e', f'DISK_SIZE={Guest.Disk_Size}',
        '-e', f'RAM_SIZE={Guest.RAM_Size}',
        '-e', f'CPU_CORES={Guest.CPU_Cores}',
        '-e', 'SAMBA=N',
        '-e', 'ARGUMENTS=-snapshot',
        '-v', f'{storage}:/storage',
        '-p', f'{ModuleCtx.Host}::{Guest.SMB_Port}',
        Image.Name,
    ]

    _ = subprocess.run(command, check=True, capture_output=True)

# ################################################################################################################################

def _wait_for_logon(guest:'GuestInfo') -> 'None':
    """ Waits until the SMB server of a guest accepts a logon of the harness account.
    """
    client = guest.harness_client()

    start = monotonic()
    last_report = start
    last_error = ''

    while True:

        elapsed = monotonic() - start

        # A container that stopped will not boot ..
        if not container_is_running(guest.name):
            raise ContainerExited(f'{guest.prefix} Container {guest.name} stopped during the boot')

        # .. the boot has a limit ..
        if elapsed > ModuleCtx.Boot_Timeout:
            raise Exception(f'{guest.prefix} No SMB logon within {ModuleCtx.Boot_Timeout}s, last error: {last_error}')

        # .. a logon that succeeds means that Windows is up ..
        try:
            client.connect()
            client.close()
            print(f'{guest.prefix} SMB logon succeeded after {elapsed:.1f}s', flush=True)
            return

        except Exception as e:
            last_error = f'{e.__class__.__name__}: {e}'
            client.close()

        # .. and the wait reports its progress.
        now = monotonic()

        if now - last_report >= ModuleCtx.Report_Every:
            last_report = now
            print(f'{guest.prefix} Booting, {elapsed:.0f}s, last error: {last_error}', flush=True)

        sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

def _start_agent(guest:'GuestInfo') -> 'None':
    """ Uploads and starts the agent of a guest, and has it create the accounts, directories and shares.
    """
    agent = guest.agent_client()

    agent.upload_agent()

    def _is_started(event:'anydict') -> 'bool':
        out = event['kind'] == 'agent-started'
        return out

    started = agent.wait_for_event(_is_started, 'the start of the agent', ModuleCtx.Agent_Timeout)
    print(f'{guest.prefix} Agent started on {started["caption"]} {started["version"]}', flush=True)

    fields = layout_command()
    _ = agent.run_command('apply-layout', ModuleCtx.Setup_Run, fields, ModuleCtx.Agent_Timeout)
    print(f'{guest.prefix} Layout applied', flush=True)

    agent.client.close()

# ################################################################################################################################

def start_guest(version:'str') -> 'GuestInfo':
    """ Boots one guest from its prepared disk, starts its agent and applies the layout.
    """
    start = monotonic()

    name = container_name(version)
    remove_container(name)

    _run_container(version)

    out = GuestInfo()
    out.version = version
    out.name = name
    out.port = published_port(name, Guest.SMB_Port)

    _ = follow_logs(name, out.prefix)

    print(f'{out.prefix} Booting {name}, SMB on port {out.port}', flush=True)

    _wait_for_logon(out)
    _start_agent(out)

    elapsed = monotonic() - start
    print(f'{out.prefix} Ready after {elapsed:.1f}s', flush=True)

    return out

# ################################################################################################################################

def write_state(guests:'guestlist') -> 'None':
    """ Records the guests that run, so that the next test session reuses them.
    """
    state:'anydict' = {}

    for guest in guests:
        state[guest.version] = guest.to_dict()

    document = json.dumps(state, indent=2)

    Paths.State_Path.parent.mkdir(parents=True, exist_ok=True)
    _ = Paths.State_Path.write_text(document)

# ################################################################################################################################

def start_guests(versions:'strlist') -> 'guestlist':
    """ Builds the prepared disks that are missing, then boots every guest in parallel.
    """
    build_missing(versions)

    out:'guestlist' = []
    errors:'anydict' = {}
    threads:'threadlist' = []

    def _start(version:'str') -> 'None':
        try:
            guest = start_guest(version)
            out.append(guest)
        except Exception as e:
            errors[version] = e

    for version in versions:
        thread = Thread(target=_start, args=(version,), daemon=True, name=f'start-win{version}')
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    if errors:
        stop_guests(versions)
        raise Exception(f'Guests failed to start -> {errors}')

    return out

# ################################################################################################################################

def running_guests() -> 'guestlist':
    """ Returns the guests recorded in the state file whose containers still run.
    """
    out:'guestlist' = []

    if not Paths.State_Path.exists():
        return out

    document = Paths.State_Path.read_text()
    state = json.loads(document)

    for data in state.values():
        guest = GuestInfo.from_dict(data)
        if container_is_running(guest.name):
            out.append(guest)

    return out

# ################################################################################################################################

def acquire_guests(versions:'strlist') -> 'tuple[guestlist, strlist]':
    """ Returns the guests of the given versions, reusing those that already run and booting the others,
    together with the versions that it booted.
    """
    out:'guestlist' = []
    started_versions:'strlist' = []
    running_versions:'strlist' = []

    for guest in running_guests():
        if guest.version in versions:
            out.append(guest)
            running_versions.append(guest.version)
            print(f'{guest.prefix} Reusing {guest.name}, SMB on port {guest.port}', flush=True)

    for version in versions:
        if version not in running_versions:
            started_versions.append(version)

    if started_versions:
        started = start_guests(started_versions)
        out.extend(started)

    write_state(out)

    return out, started_versions

# ################################################################################################################################

def stop_guests(versions:'strlist') -> 'None':
    """ Removes the containers of the guests, which discards everything written to them, and their entries in the state file.
    """
    for version in versions:
        name = container_name(version)
        remove_container(name)

    remaining = running_guests()

    if remaining:
        write_state(remaining)
    else:
        Paths.State_Path.unlink(missing_ok=True)

# ################################################################################################################################
# ################################################################################################################################
