# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# LazyFS under the data directory of each node, which keeps every write that was not synced in its own cache
# and discards that cache on request, as a host that lost its power does. LazyFS runs in a tool container
# of its own, which the suite builds, and its FUSE mount reaches the node container through the run directory,
# which the tool container mounts with shared propagation and the node container with slave propagation.

# stdlib
import logging
import os
import shutil
import time

# Zato
from nodes import NodeHook
from topology import docker, ensure_image, remove_container

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from nodes import Node

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite.lazyfs')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The image of the tool container and how it is built
    Image = 'zato-ha-test-lazyfs:1'
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

    # How large the cache of unsynced writes may grow
    Cache_Size = '1GB'

# ################################################################################################################################
# ################################################################################################################################

class LazyFSHook(NodeHook):
    """ Places the data directory of each node on LazyFS before the node starts and unmounts it once the node
    container is removed.
    """

    def __init__(self) -> 'None':
        ensure_image(ModuleCtx.Image, ModuleCtx.Dockerfile)

# ################################################################################################################################

    def _container_name(self, node:'Node') -> 'str':
        out = f'zato-ha-test-lazyfs-{node.short_name}'
        return out

    def _root_dir(self, node:'Node') -> 'str':
        out = os.path.join(node.directory, 'lazyfs-root')
        return out

    def _fifo_path(self, node:'Node') -> 'str':
        out = os.path.join(node.directory, 'lazyfs.fifo')
        return out

# ################################################################################################################################

    def _write_config(self, node:'Node') -> 'str':
        lines = [
            '[faults]',
            f'fifo_path="{self._fifo_path(node)}"',
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

        out = os.path.join(node.directory, 'lazyfs.toml')

        with open(out, 'w') as config_file:
            _ = config_file.write('\n'.join(lines))

        return out

# ################################################################################################################################

    def before_start(self, node:'Node') -> 'None':
        """ Moves the data of the node under the root of LazyFS and mounts LazyFS over its data directory.
        """
        root_dir = self._root_dir(node)

        os.rename(node.data_dir, root_dir)
        os.makedirs(node.data_dir)

        config_path = self._write_config(node)
        os.mkfifo(self._fifo_path(node))

        container_name = self._container_name(node)
        remove_container(container_name)

        _ = docker(
            'run', '-d',
            '--name', container_name,
            '--device', '/dev/fuse',
            '--cap-add', 'SYS_ADMIN',
            '--security-opt', 'apparmor=unconfined',
            '--user', f'{os.getuid()}:{os.getgid()}',
            '-v', f'{node.run_dir}:{node.run_dir}:rshared',
            ModuleCtx.Image,
            ModuleCtx.Binary, node.data_dir,
            '--config-path', config_path,
            '-o', 'allow_other',
            '-o', 'modules=subdir',
            '-o', f'subdir={root_dir}',
            '-f',
        )

        deadline = time.monotonic() + ModuleCtx.Mount_Timeout

        while not os.path.ismount(node.data_dir):
            if time.monotonic() > deadline:
                logs = docker('logs', container_name, check=False)
                raise Exception(f'LazyFS not mounted at {node.data_dir}:\n{logs.stdout}{logs.stderr}')
            time.sleep(ModuleCtx.Poll_Interval)

        node.run_dir_options = ':rslave'

        logger.info('LazyFS mounted at %s', node.data_dir)

# ################################################################################################################################

    def discard_unsynced(self, node:'Node') -> 'None':
        """ Discards every write to the data directory of a node that was not synced.
        """
        with open(self._fifo_path(node), 'w') as fifo:
            _ = fifo.write(ModuleCtx.Clear_Cache_Command)

        logger.info('Discarded the unsynced writes of %s', node.node_name)

# ################################################################################################################################

    def after_remove(self, node:'Node') -> 'None':
        """ Unmounts LazyFS and returns the data of the node to its data directory.
        """
        container_name = self._container_name(node)

        _ = docker('exec', container_name, 'fusermount3', '-u', node.data_dir, check=False)
        remove_container(container_name)

        os.rmdir(node.data_dir)
        _ = shutil.move(self._root_dir(node), node.data_dir)

# ################################################################################################################################
# ################################################################################################################################
