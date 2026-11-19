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
from time import monotonic, sleep, time_ns

# Zato
from live_containers.ready import ContainerExited
from live_windows.agent_client import AgentClient
from live_windows.build import build_missing
from live_windows.docker_ import container_is_running, follow_logs, published_port, remove_container
from live_windows.layout import layout_command
from live_windows.ready_state import confirm_boot, discard, instance_mounts, is_ready, remove_instance_storage, restore_arguments, \
    save_arguments, save_state, write_stamp, ModuleCtx as ReadyCtx
from live_windows.settings import Accounts, container_name, current_instance, Guest, guest_name, Image, Media, state_path, \
    storage_dir, Versions
from live_windows.share_client import ShareClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, callable_, strlist

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

    # How often a guest that resumes from its ready state is checked, in seconds
    Resume_Poll_Interval = 0.2

    # The run name of the commands sent while a guest starts
    Setup_Run = 'setup'

    # The number of nanoseconds in a millisecond
    Nanoseconds_Per_Ms = 1_000_000

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

def _run_container(name:'str', version:'str', mounts:'strlist', arguments:'str') -> 'None':
    """ Starts the container of a guest with the given storage and the given additional QEMU arguments.
    """
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
        '-e', f'CPU_FLAGS={Guest.CPU_Flags}',
        '-e', f'HV={Guest.Hyper_V}',
        '-e', 'SAMBA=N',
        '-e', f'ARGUMENTS={arguments}',
        *mounts,
        '-p', f'{ModuleCtx.Host}::{Guest.SMB_Port}',
        Image.Name,
    ]

    _ = subprocess.run(command, check=True, capture_output=True)

# ################################################################################################################################

def _new_guest(version:'str', name:'str') -> 'GuestInfo':
    """ Returns the guest of a container that was just started, and prints its log from now on.
    """
    out = GuestInfo()
    out.version = version
    out.name = name
    out.port = published_port(name, Guest.SMB_Port)

    _ = follow_logs(name, out.prefix)

    return out

# ################################################################################################################################

def _wait_for_logon(guest:'GuestInfo', poll_interval:'float') -> 'None':
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

        sleep(poll_interval)

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

def _set_clock(guest:'GuestInfo') -> 'None':
    """ Has the agent of a guest resumed from its ready state, whose clock runs from the moment the state was saved,
    set the clock to the time of the host.
    """
    agent = guest.agent_client()
    agent.skip_existing()

    fields = {
        'unix_ms': time_ns() // ModuleCtx.Nanoseconds_Per_Ms,
    }

    _ = agent.run_command('set-clock', ModuleCtx.Setup_Run, fields, ModuleCtx.Agent_Timeout)
    agent.client.close()

# ################################################################################################################################

def _run_in_parallel(versions:'strlist', function:'callable_', what:'str', on_error:'callable_') -> 'None':
    """ Runs a function for each version in a thread of its own, and raises once all of them ended if any of them failed.
    Each failure calls the error handler, which ends the waits of the other threads, and the handler is called once more
    after all of them ended, for what a thread started after the first failure.
    """
    errors:'anydict' = {}
    threads:'threadlist' = []

    def _run(version:'str') -> 'None':
        try:
            function(version)
        except Exception as e:
            errors[version] = e
            print(f'[WIN{version.upper()}] Failed -> {e}', flush=True)
            on_error(versions)

    for version in versions:
        thread = Thread(target=_run, args=(version,), daemon=True, name=f'{what}-win{version}')
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    if errors:
        on_error(versions)
        raise Exception(f'Could not {what} -> {errors}')

# ################################################################################################################################

def build_ready_state(version:'str') -> 'None':
    """ Boots the prepared disk of a version, starts the agent, applies the layout and saves the state of the guest,
    from which every test session resumes its guests.
    """
    start = monotonic()

    name = container_name(version)
    storage = storage_dir(version)

    remove_container(name)
    discard(version)

    mounts = ['-v', f'{storage}:{ReadyCtx.Container_Storage}']
    _run_container(name, version, mounts, save_arguments())

    try:
        guest = _new_guest(version, name)
        print(f'{guest.prefix} Booting {name} from the prepared disk to save its ready state', flush=True)

        _wait_for_logon(guest, ModuleCtx.Poll_Interval)
        _start_agent(guest)

        output = save_state(name)
        print(f'{guest.prefix} {output}', flush=True)

    finally:
        remove_container(name)

    write_stamp(version)

    elapsed = monotonic() - start
    print(f'{guest.prefix} Ready state saved after {elapsed:.1f}s', flush=True)

# ################################################################################################################################

def _remove_build_containers(versions:'strlist') -> 'None':
    for version in versions:
        name = container_name(version)
        remove_container(name)

# ################################################################################################################################

def build_ready_states(versions:'strlist') -> 'None':
    """ Saves, in parallel, the ready states of the versions that have none, or whose ready states are out of date.
    """
    to_build:'strlist' = []

    for version in versions:
        if is_ready(version):
            print(f'[WIN{version.upper()}] The ready state is current', flush=True)
        else:
            to_build.append(version)

    if to_build:
        _run_in_parallel(to_build, build_ready_state, 'save the ready states', _remove_build_containers)

# ################################################################################################################################

def prepare_guests(versions:'strlist') -> 'None':
    """ Builds the prepared disks and saves the ready states that are missing or out of date.
    """
    build_missing(versions)
    build_ready_states(versions)

# ################################################################################################################################

def start_guest(version:'str') -> 'GuestInfo':
    """ Resumes one guest of this process from the ready state of its version, with the agent running and the layout applied.
    """
    start = monotonic()

    instance = current_instance()
    name = guest_name(version, instance)
    remove_container(name)

    mounts = instance_mounts(version, instance)
    arguments = restore_arguments()
    _run_container(name, version, mounts, arguments)

    out = _new_guest(version, name)
    print(f'{out.prefix} Resuming {name} from its ready state, SMB on port {out.port}', flush=True)

    confirm_boot(name)

    _wait_for_logon(out, ModuleCtx.Resume_Poll_Interval)
    _set_clock(out)

    elapsed = monotonic() - start
    print(f'{out.prefix} Ready after {elapsed:.1f}s', flush=True)

    return out

# ################################################################################################################################

def write_state(guests:'guestlist') -> 'None':
    """ Records the guests that run, so that the next test session of the same instance reuses them.
    """
    state:'anydict' = {}

    for guest in guests:
        state[guest.version] = guest.to_dict()

    document = json.dumps(state, indent=2)

    path = state_path(current_instance())
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(document)

# ################################################################################################################################

def start_guests(versions:'strlist') -> 'guestlist':
    """ Builds what is missing, then resumes every guest in parallel.
    """
    prepare_guests(versions)

    out:'guestlist' = []

    def _start(version:'str') -> 'None':
        guest = start_guest(version)
        out.append(guest)

    _run_in_parallel(versions, _start, 'start the guests', stop_guests)

    return out

# ################################################################################################################################

def running_guests() -> 'guestlist':
    """ Returns the guests recorded in the state file of this instance whose containers still run.
    """
    out:'guestlist' = []
    path = state_path(current_instance())

    if not path.exists():
        return out

    document = path.read_text()
    state = json.loads(document)

    for data in state.values():
        guest = GuestInfo.from_dict(data)
        if container_is_running(guest.name):
            out.append(guest)

    return out

# ################################################################################################################################

def acquire_guests(versions:'strlist') -> 'tuple[guestlist, strlist]':
    """ Returns the guests of the given versions, reusing those that already run and starting the others,
    together with the versions that it started.
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
    """ Removes the containers of the guests of this process, which discards everything written to them,
    together with their storage directories and their entries in the state file.
    """
    instance = current_instance()

    for version in versions:
        name = guest_name(version, instance)
        remove_container(name)
        remove_instance_storage(version, instance)

    remaining = running_guests()

    if remaining:
        write_state(remaining)
    else:
        state_path(instance).unlink(missing_ok=True)

# ################################################################################################################################

def discard_instance(instance:'str') -> 'None':
    """ Removes every guest of an instance, whatever state the process that started them left them in.
    """
    for version in Versions.All:
        name = guest_name(version, instance)
        remove_container(name)
        remove_instance_storage(version, instance)

    state_path(instance).unlink(missing_ok=True)

# ################################################################################################################################
# ################################################################################################################################
