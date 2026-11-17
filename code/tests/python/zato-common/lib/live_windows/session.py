# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from time import time

# Zato
from live_environment.parts import missing_requirements
from live_windows.build import is_current
from live_windows.containers import acquire_guests
from live_windows.layout import Hub, local_path, sequence_name, share_local_path
from live_windows.settings import Suite

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.containers import GuestInfo
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the agent may take to confirm that it ran a command, in seconds
    Command_Timeout = 10

    # The defaults of each producer - the pause between two files, in milliseconds, and the size of each file, in bytes
    Interval_Ms = 50
    File_Size   = 2048

    # The suffix a producer writes a file under before it renames it
    Temp_Suffix = '.part'

    # A temporary file that stays in place for longer than this, in milliseconds, is reported as an error
    Stale_Temp_Ms = 5000

    # The suffixes of the temporary files that Zato writes before it renames them
    Ignore_Suffixes = Hub.Lock_Suffix, '.tmp'

    # Sequence numbers start at a point that depends on the time, so that two sessions on the same guests
    # do not reuse the names of each other's files. Each session has this many numbers per application.
    Sequence_Block = 2000
    Sequence_Blocks = 500

    # The run under which a session stops the tasks that earlier sessions left running on a guest
    Takeover_Run = 'session-takeover'

# ################################################################################################################################
# ################################################################################################################################

class Mode:
    """ The ways in which a producer creates its files.
    """
    Direct           = 'direct'
    Temp_Then_Rename = 'temp-then-rename'
    Slow             = 'slow'
    Locked           = 'locked'

class Action:
    """ What a consumer does with each file once it read it.
    """
    Delete = 'delete'
    Keep   = 'keep'

# ################################################################################################################################
# ################################################################################################################################

class Sequences:
    """ Gives out the sequence numbers of the files that the applications write into their outboxes.
    """
    def __init__(self) -> 'None':
        block = int(time()) % ModuleCtx.Sequence_Blocks
        self.next_number = block * ModuleCtx.Sequence_Block

    def next_names(self, app:'str', count:'int') -> 'strlist':
        out:'strlist' = []

        for _ in range(count):
            self.next_number += 1
            name = sequence_name(self.next_number, app)
            out.append(name)

        return out

    def next_numbers(self, count:'int') -> 'list[int]':
        out:'list[int]' = []

        for _ in range(count):
            self.next_number += 1
            out.append(self.next_number)

        return out

# ################################################################################################################################
# ################################################################################################################################

class GuestHandle:
    """ Sends commands to the agent of one guest. The events of the agent are read by a separate client,
    so that a monitor in another thread reads them while the commands are being sent.
    """
    def __init__(self, info:'GuestInfo') -> 'None':
        self.info = info
        self.version = info.version
        self.prefix = info.prefix

        self.sender = info.agent_client()
        self.sender.skip_existing()

        self.reader = info.agent_client()
        self.reader.skip_existing()

        self.task_sequence = 0

# ################################################################################################################################

    def _next_task(self, kind:'str') -> 'str':
        self.task_sequence += 1

        out = f'{kind}-{self.task_sequence}'
        return out

# ################################################################################################################################

    def _run(self, kind:'str', run:'str', fields:'anydict') -> 'None':
        _ = self.sender.run_command(kind, run, fields, ModuleCtx.Command_Timeout)

# ################################################################################################################################

    def produce(
        self,
        run:'str',
        share:'str',
        folder:'str',
        names:'strlist',
        *,
        mode:'str'=Mode.Direct,
        interval_ms:'int'=ModuleCtx.Interval_Ms,
        size:'int'=ModuleCtx.File_Size,
        chunk_count:'int'=1,
        slow_ms:'int'=0,
        lock_ms:'int'=0,
        ) -> 'str':
        """ Has the agent create files of the given names in a folder of a share, one after another.
        """
        out = self._next_task('produce')
        directory = local_path(share, folder)

        fields = {
            'task': out,
            'directory': directory,
            'names': names,
            'interval_ms': interval_ms,
            'size': size,
            'mode': mode,
            'temp_suffix': ModuleCtx.Temp_Suffix,
            'chunk_count': chunk_count,
            'slow_ms': slow_ms,
            'lock_ms': lock_ms,
        }

        self._run('produce', run, fields)
        return out

# ################################################################################################################################

    def consume(
        self,
        run:'str',
        share:'str',
        folder:'str',
        pattern:'str',
        *,
        action:'str'=Action.Delete,
        fail_names:'strlist | None'=None,
        ) -> 'str':
        """ Has the agent read each file that appears in a folder of a share, as the application that the folder belongs to.
        """
        if fail_names is None:
            fail_names = []

        out = self._next_task('consume')
        directory = local_path(share, folder)
        ignore_suffixes = list(ModuleCtx.Ignore_Suffixes)

        fields = {
            'task': out,
            'directory': directory,
            'pattern': pattern,
            'action': action,
            'fail_names': fail_names,
            'ignore_suffixes': ignore_suffixes,
            'stale_temp_ms': ModuleCtx.Stale_Temp_Ms,
        }

        self._run('consume', run, fields)
        return out

# ################################################################################################################################

    def observe(self, run:'str', share:'str') -> 'str':
        """ Has the agent report each file that appears in or disappears from a share, in any of its directories.
        """
        out = self._next_task('observe')
        root = share_local_path(share)

        fields = {
            'task': out,
            'root': root,
        }

        self._run('observe', run, fields)
        return out

# ################################################################################################################################

    def restart_smb_service(self, run:'str') -> 'None':
        """ Has the agent restart the SMB server of the guest. The control share goes away with it,
        so the command is only sent and the events that follow are read by the monitor.
        """
        task = self._next_task('restart-smb-service')

        fields = {
            'task': task,
        }

        self.sender.send('restart-smb-service', run, fields)

# ################################################################################################################################

    def block_port(self, run:'str', duration_ms:'int') -> 'None':
        """ Has the agent block the SMB port of the guest for the given time. The block applies to the harness too,
        so the command is only sent and the events that follow are read by the monitor.
        """
        task = self._next_task('block-port')

        fields = {
            'task': task,
            'duration_ms': duration_ms,
        }

        self.sender.send('block-port', run, fields)

# ################################################################################################################################

    def set_password(self, run:'str', user:'str', password:'str') -> 'None':
        fields = {
            'user': user,
            'password': password,
        }
        self._run('set-password', run, fields)

# ################################################################################################################################

    def remove_share(self, run:'str', share:'str') -> 'None':
        fields = {
            'share': share,
        }
        self._run('remove-share', run, fields)

# ################################################################################################################################

    def restore_share(self, run:'str', share:'str') -> 'None':
        fields = {
            'share': share,
        }
        self._run('restore-share', run, fields)

# ################################################################################################################################

    def stop_run(self, run:'str') -> 'None':
        """ Stops every producer, consumer and observer of a run.
        """
        self._run('stop', run, {})

# ################################################################################################################################

    def stop_all(self, run:'str') -> 'None':
        """ Stops every producer, consumer and observer, whichever run started it.
        """
        self._run('stop-all', run, {})

# ################################################################################################################################

    def close(self) -> 'None':
        """ Drops the connections of both clients, which open new ones on their next call.
        """
        self.sender.client.close()
        self.reader.client.close()

# ################################################################################################################################
# ################################################################################################################################

handledict = dict[str, GuestHandle]

# ################################################################################################################################
# ################################################################################################################################

def missing_guest_requirements(versions:'strlist') -> 'strlist':
    """ What this machine lacks for the guests to run - empty when nothing is missing. The suites run only
    when they are asked for, because each guest takes gigabytes of memory.
    """
    variables = Suite.Required_Variable,
    out = missing_requirements(wants_docker=True, wants_haproxy=False, variables=variables)

    if not os.path.exists(Suite.KVM_Device):
        out.append(f'{Suite.KVM_Device} is not available, so no guest can run')

    for version in versions:
        if not is_current(version):
            out.append(f'The prepared disk of Windows Server {version} is missing or out of date - make test-smb-windows-build')

    return out

# ################################################################################################################################

def open_guests(versions:'strlist') -> 'tuple[handledict, strlist]':
    """ Returns a handle to each guest, reusing the guests that already run and booting the others,
    together with the versions that it booted.
    """
    out:'handledict' = {}

    guests, started_versions = acquire_guests(versions)

    for info in guests:
        handle = GuestHandle(info)

        # A reused guest may still run the tasks of a session that was interrupted before it stopped them
        handle.stop_all(ModuleCtx.Takeover_Run)

        out[info.version] = handle

    return out, started_versions

# ################################################################################################################################
# ################################################################################################################################
