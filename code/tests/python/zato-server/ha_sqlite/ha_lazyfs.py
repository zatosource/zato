# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# LazyFS under the data directory of each node. Its FUSE mount reaches the node container through the run directory,
# which the tool container mounts with shared propagation and the node container with slave propagation.

# stdlib
import os

# Zato
from nodes import NodeHook
from zato.common.ha.common import ModuleCtx as HACtx
from zato.common.test.reliability.lazyfs import LazyFSMount

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from nodes import Node

# ################################################################################################################################
# ################################################################################################################################

class LazyFSHook(NodeHook):
    """ Places the data directory of each node on LazyFS before the node starts and unmounts it once the node
    container is removed.
    """

    def __init__(self) -> 'None':
        self._mounts:'dict[str, LazyFSMount]' = {}

# ################################################################################################################################

    def _get_mount(self, node:'Node') -> 'LazyFSMount':
        out = self._mounts[node.short_name]
        return out

# ################################################################################################################################

    def before_start(self, node:'Node') -> 'None':
        """ Moves the data of the node under the root of LazyFS and mounts LazyFS over its data directory.
        """
        container_name = f'zato-ha-test-lazyfs-{node.short_name}'

        mount = LazyFSMount(container_name, node.run_dir, node.directory, node.data_dir)
        mount.mount()

        self._mounts[node.short_name] = mount

        node.run_dir_options = ':rslave'

        # LazyFS does not support Unix sockets, so the barrier socket is placed outside of its mount.
        node.env[HACtx.Env_Barrier_Socket] = os.path.join(node.directory, HACtx.Default_Barrier_Socket_Name)

# ################################################################################################################################

    def discard_unsynced(self, node:'Node') -> 'None':
        """ Discards every write to the data directory of a node that was not synced.
        """
        mount = self._get_mount(node)
        mount.discard_unsynced()

# ################################################################################################################################

    def after_remove(self, node:'Node') -> 'None':
        """ Unmounts LazyFS and returns the data of the node to its data directory.
        """
        mount = self._mounts.pop(node.short_name)
        mount.unmount()

# ################################################################################################################################
# ################################################################################################################################
