# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# LazyFS over one directory, which keeps every write that was not synced in its own cache and discards that cache
# on request, as a host that lost its power does. LazyFS runs in a tool container of its own, and its FUSE mount
# reaches the host and other containers through a shared directory, which the tool container mounts with shared
# propagation.

# stdlib
import logging
import os
import shutil
import subprocess
import time

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.reliability.lazyfs')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The image of the tool container and how it is built
    Image = 'zato-test-lazyfs:1'
    Repository = 'https://github.com/dsrhaslab/lazyfs.git'
    Binary = '/lazyfs/lazyfs/build/lazyfs'

    Dockerfile = '\n'.join([
        'FROM ubuntu:24.04',
        'RUN apt-get update && apt-get install -y --no-install-recommends g++ cmake make git ca-certificates ' + \
            'pkg-config libfuse3-dev fuse3 && rm -rf /var/lib/apt/lists/*',
        f'RUN git clone --depth 1 {Repository} /lazyfs && cd /lazyfs/libs/libpcache && ./build.sh ' + \
            '&& cd /lazyfs/lazyfs && ./build.sh',
        'RUN echo user_allow_other >> /etc/fuse.conf',
        '',
    ])

    # The command that discards every write that was not synced
    Clear_Cache_Command = 'lazyfs::clear-cache\n'

    # How long the mount may take to appear, in seconds
    Mount_Timeout = 60

    # How often the mount is checked while it appears, in seconds
    Poll_Interval = 0.2

    # The mount table of the host, in which the second field of each line is a mount point
    Mounts_Path = '/proc/self/mounts'

    # How large the cache of unsynced writes may grow
    Cache_Size = '1GB'

    # The names of the files of one mount in its work directory
    Root_Dir_Name = 'lazyfs-root'
    Fifo_Name = 'lazyfs.fifo'
    Config_Name = 'lazyfs.toml'

# ################################################################################################################################
# ################################################################################################################################

def _is_mounted(path:'str') -> 'bool':
    """ Returns whether a directory is a mount point of the host, including a FUSE mount whose daemon has ended.
    """
    with open(ModuleCtx.Mounts_Path) as mounts_file:
        mounts = mounts_file.read()

    for line in mounts.splitlines():
        fields = line.split()
        if fields[1] == path:
            return True

    return False

# ################################################################################################################################

def _docker(*args:'str', check:'bool'=True) -> 'subprocess.CompletedProcess[str]':
    """ Runs one docker command and returns its result.
    """
    command = ['docker', *args]

    out = subprocess.run(command, capture_output=True, text=True, check=False)

    if check:
        if out.returncode != 0:
            raise Exception(f'Command {command} failed with {out.returncode}: {out.stderr.strip()}')

    return out

# ################################################################################################################################

def _ensure_image() -> 'None':
    """ Builds the image of the tool container unless it exists already.
    """
    result = _docker('image', 'inspect', ModuleCtx.Image, check=False)

    if result.returncode != 0:
        dockerfile = ModuleCtx.Dockerfile.encode('utf8')
        _ = subprocess.run(['docker', 'build', '-t', ModuleCtx.Image, '-'], input=dockerfile, capture_output=True, check=True)

# ################################################################################################################################
# ################################################################################################################################

class LazyFSMount:
    """ LazyFS over one directory. The content that the directory holds when it is mounted becomes the content
    of the file system, and it returns to the directory once the file system is unmounted.
    """

    def __init__(self, container_name:'str', shared_dir:'str', work_dir:'str', mount_dir:'str') -> 'None':

        # The tool container, the directory that it shares with its peers, the directory with the files of the mount
        # and the directory that the mount is over, the last two under the shared one
        self.container_name = container_name
        self.shared_dir = shared_dir
        self.work_dir = work_dir
        self.mount_dir = mount_dir

        self.root_dir = os.path.join(work_dir, ModuleCtx.Root_Dir_Name)
        self.fifo_path = os.path.join(work_dir, ModuleCtx.Fifo_Name)
        self.config_path = os.path.join(work_dir, ModuleCtx.Config_Name)

        _ensure_image()

# ################################################################################################################################

    def _write_config(self) -> 'None':
        lines = [
            '[faults]',
            f'fifo_path="{self.fifo_path}"',
            '',
            '[cache]',
            'apply_eviction=false',
            '',
            '[cache.simple]',
            f'custom_size="{ModuleCtx.Cache_Size}"',
            'blocks_per_page=1',
            '',
            '[filesystem]',
            'log_all_operations=false',
            'logfile=""',
            '',
        ]

        with open(self.config_path, 'w') as config_file:
            _ = config_file.write('\n'.join(lines))

# ################################################################################################################################

    def mount(self) -> 'None':
        """ Moves the content of the directory under the root of LazyFS and mounts LazyFS over the directory.
        """
        os.makedirs(self.work_dir, exist_ok=True)

        os.rename(self.mount_dir, self.root_dir)
        os.makedirs(self.mount_dir)

        self._write_config()
        os.mkfifo(self.fifo_path)

        _ = _docker('rm', '-f', self.container_name, check=False)

        _ = _docker(
            'run', '-d',
            '--name', self.container_name,
            '--device', '/dev/fuse',
            '--cap-add', 'SYS_ADMIN',
            '--security-opt', 'apparmor=unconfined',
            '--user', f'{os.getuid()}:{os.getgid()}',
            '-v', f'{self.shared_dir}:{self.shared_dir}:rshared',
            ModuleCtx.Image,
            ModuleCtx.Binary, self.mount_dir,
            '--config-path', self.config_path,
            '-o', 'allow_other',
            '-o', 'modules=subdir',
            '-o', f'subdir={self.root_dir}',
            '-f',
        )

        deadline = time.monotonic() + ModuleCtx.Mount_Timeout

        while not os.path.ismount(self.mount_dir):
            if time.monotonic() > deadline:
                logs = _docker('logs', self.container_name, check=False)
                raise Exception(f'LazyFS not mounted at {self.mount_dir}:\n{logs.stdout}{logs.stderr}')
            time.sleep(ModuleCtx.Poll_Interval)

        logger.info('LazyFS mounted at %s', self.mount_dir)

# ################################################################################################################################

    def discard_unsynced(self) -> 'None':
        """ Discards every write to the directory that was not synced.
        """
        with open(self.fifo_path, 'w') as fifo:
            _ = fifo.write(ModuleCtx.Clear_Cache_Command)

        logger.info('Discarded the unsynced writes under %s', self.mount_dir)

# ################################################################################################################################

    def unmount(self) -> 'None':
        """ Unmounts LazyFS and returns its content to the directory.
        """
        # LazyFS is the main process of its container and ends once it is unmounted, which can end the exec session
        # before it reports success, so the outcome is read from the mount table of the host.
        out = _docker('exec', self.container_name, 'fusermount3', '-u', self.mount_dir, check=False)

        if _is_mounted(self.mount_dir):
            raise Exception(f'LazyFS could not be unmounted from {self.mount_dir}: {out.returncode} {out.stderr.strip()}')

        _ = _docker('rm', '-f', self.container_name, check=False)

        os.rmdir(self.mount_dir)
        _ = shutil.move(self.root_dir, self.mount_dir)

        os.remove(self.fifo_path)
        os.remove(self.config_path)

        logger.info('LazyFS unmounted from %s', self.mount_dir)

# ################################################################################################################################
# ################################################################################################################################
