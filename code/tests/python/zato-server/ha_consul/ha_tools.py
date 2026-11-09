# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The fault tools of the active-standby suites. The libraries of the pub/sub fault suite are mounted into each node
# container and preloaded into every process of it - one delays and fails the file system calls under the data
# directory, the other offsets the wall clock and changes its rate - and each is controlled through a file
# that a test rewrites while the node runs. The cgroup of a node container limits its disk, CPU and memory,
# and netem degrades the packets of one link of a node only.

# stdlib
import logging
import os

# Zato
from container import Container, get_disk_device
from nodes import NodeHook
from tools import build_faketime, build_fsfault, get_tools_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from nodes import Node
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul.tools')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The files through which a test controls the libraries of a node, in the directory of the node
    FSFault_Control_File = 'fsfault.ctl'
    Faketime_File = 'faketime.rc'

    # The errors that the file system library returns
    Errno_EIO = 'EIO'
    Errno_ENOSPC = 'ENOSPC'

    # The interface of each container on the network of the run
    Interface = 'eth0'

    # The CPU period of cpu.max, in microseconds
    CPU_Period_US = 100000

    # The value of a cgroup limit that is not set
    No_Limit = 'max'

    # The severities of each fault, as fractions of its full extent, and the parameters of netem at total loss
    Severities = [0.1, 0.2, 0.5, 0.9]
    Total_Loss = 'loss 100%'

    # The full extent of each kind of packet fault - the delay, the share of packets lost, reordered, duplicated
    # or corrupted, and the share of the bandwidth taken away
    Max_Delay_Ms = 1000
    Jitter_Share = 0.2
    Reorder_Delay_Ms = 10
    Baseline_Rate_Mbit = 100

    # The kinds of packet faults
    Packet_Delay     = 'delay'
    Packet_Loss      = 'loss'
    Packet_Reorder   = 'reorder'
    Packet_Duplicate = 'duplicate'
    Packet_Corrupt   = 'corrupt'
    Packet_Rate      = 'rate'

    Packet_Faults = [Packet_Delay, Packet_Loss, Packet_Reorder, Packet_Duplicate, Packet_Corrupt, Packet_Rate]

# ################################################################################################################################
# ################################################################################################################################

class PreloadHook(NodeHook):
    """ Preloads the file system library and libfaketime into every process of each node, with no fault applied
    until a test writes its control files.
    """

    def __init__(self) -> 'None':
        self.fsfault_path = build_fsfault()
        self.faketime_path = build_faketime()
        self.tools_dir = get_tools_dir()

# ################################################################################################################################

    def _control_path(self, node:'Node') -> 'str':
        out = os.path.join(node.directory, ModuleCtx.FSFault_Control_File)
        return out

    def _faketime_path(self, node:'Node') -> 'str':
        out = os.path.join(node.directory, ModuleCtx.Faketime_File)
        return out

# ################################################################################################################################

    def before_start(self, node:'Node') -> 'None':

        # Neither library changes anything until a test writes its file ..
        self.set_disk_fault(node, 0, 0, ModuleCtx.Errno_EIO)
        self.set_clock(node, 0, 1.0)

        # .. and the wall clock alone is offset, as the timers of the node use the monotonic clock.
        node.fault_mounts.append(self.tools_dir)
        node.fault_env.update({
            'LD_PRELOAD': f'{self.fsfault_path}:{self.faketime_path}',
            'ZATO_FSFAULT_CONTROL': self._control_path(node),
            'FAKETIME_TIMESTAMP_FILE': self._faketime_path(node),
            'FAKETIME_NO_CACHE': '1',
            'DONT_FAKE_MONOTONIC': '1',
        })

# ################################################################################################################################

    def after_remove(self, node:'Node') -> 'None':
        """ The control files are in the directory of the node, which the next test replaces.
        """

# ################################################################################################################################

    def set_disk_fault(self, node:'Node', delay_us:'int', error_percent:'int', errno_name:'str') -> 'None':
        """ Delays each sync and positioned write under the data directory of a node and makes a percentage
        of them fail with the given error.
        """
        lines = [
            f'prefix={node.data_dir}',
            f'delay_us={delay_us}',
            f'error_percent={error_percent}',
            f'errno={errno_name}',
            '',
        ]

        with open(self._control_path(node), 'w') as control_file:
            _ = control_file.write('\n'.join(lines))

        logger.info('Disk of %s -> delay %dus, %d%% %s', node.node_name, delay_us, error_percent, errno_name)

# ################################################################################################################################

    def clear_disk_fault(self, node:'Node') -> 'None':
        self.set_disk_fault(node, 0, 0, ModuleCtx.Errno_EIO)

# ################################################################################################################################

    def set_clock(self, node:'Node', offset_seconds:'int', rate:'float') -> 'None':
        """ Offsets the wall clock of a node by the given number of seconds and runs it at the given rate.
        """
        with open(self._faketime_path(node), 'w') as faketime_file:
            _ = faketime_file.write(f'{offset_seconds:+d} x{rate}\n')

        logger.info('Clock of %s -> %+ds at x%s', node.node_name, offset_seconds, rate)

# ################################################################################################################################
# ################################################################################################################################

def limit_disk(node:'Node', bytes_per_second:'int', operations_per_second:'int') -> 'None':
    """ Limits the reads and writes of a node container on the disk of its data directory.
    """
    device = get_disk_device(node.data_dir)
    value = f'{device} rbps={bytes_per_second} wbps={bytes_per_second} riops={operations_per_second} ' + \
        f'wiops={operations_per_second}'

    Container(node.container_name).write_cgroup('io.max', value)

# ################################################################################################################################

def clear_disk_limit(node:'Node') -> 'None':
    device = get_disk_device(node.data_dir)
    no_limit = ModuleCtx.No_Limit
    value = f'{device} rbps={no_limit} wbps={no_limit} riops={no_limit} wiops={no_limit}'

    Container(node.container_name).write_cgroup('io.max', value)

# ################################################################################################################################

def limit_cpu(node:'Node', share:'float') -> 'None':
    """ Limits a node container to the given share of one CPU.
    """
    quota = int(ModuleCtx.CPU_Period_US * share)
    Container(node.container_name).write_cgroup('cpu.max', f'{quota} {ModuleCtx.CPU_Period_US}')

# ################################################################################################################################

def clear_cpu_limit(node:'Node') -> 'None':
    Container(node.container_name).write_cgroup('cpu.max', f'{ModuleCtx.No_Limit} {ModuleCtx.CPU_Period_US}')

# ################################################################################################################################

def limit_memory(node:'Node', file_name:'str', limit_bytes:'int') -> 'None':
    """ Sets memory.high or memory.max of a node container.
    """
    Container(node.container_name).write_cgroup(file_name, str(limit_bytes))

# ################################################################################################################################

def clear_memory_limit(node:'Node', file_name:'str') -> 'None':
    Container(node.container_name).write_cgroup(file_name, ModuleCtx.No_Limit)

# ################################################################################################################################

def read_memory_current(node:'Node') -> 'int':
    out = Container(node.container_name).read_memory_current()
    return out

# ################################################################################################################################

def read_oom_kills(node:'Node') -> 'int':
    out = Container(node.container_name).read_oom_kills()
    return out

# ################################################################################################################################

def protect_node_from_oom_killer(node:'Node') -> 'None':
    """ Keeps the node process out of the choice of the OOM killer, which then ends a process of the Zato server.
    """
    Container(node.container_name).protect_from_oom_killer()

# ################################################################################################################################
# ################################################################################################################################

def degrade_link(node:'Node', addresses:'strlist', netem:'str') -> 'None':
    """ Applies netem with the given parameters to the packets that a node sends to the given addresses only.
    """
    interface = ModuleCtx.Interface

    commands = [
        f'tc qdisc add dev {interface} root handle 1: prio bands 3 priomap 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2',
        f'tc qdisc add dev {interface} parent 1:1 handle 10: netem {netem}',
    ]

    for address in addresses:
        commands.append(f'tc filter add dev {interface} parent 1:0 protocol ip prio 1 u32 match ip dst {address}/32 flowid 1:1')

    script = ' && '.join(commands)
    _ = Container(node.container_name).run_tc(script)

    logger.info('Link of %s to %s -> netem %s', node.node_name, addresses, netem)

# ################################################################################################################################

def get_netem(kind:'str', severity:'float') -> 'str':
    """ Returns the parameters of netem for one kind of packet fault at the given severity.
    """
    percent = round(severity * 100, 1)

    if kind == ModuleCtx.Packet_Delay:
        delay = int(ModuleCtx.Max_Delay_Ms * severity)
        jitter = int(delay * ModuleCtx.Jitter_Share)
        out = f'delay {delay}ms {jitter}ms distribution normal'

    elif kind == ModuleCtx.Packet_Loss:
        out = f'loss {percent}%'

    elif kind == ModuleCtx.Packet_Reorder:
        out = f'delay {ModuleCtx.Reorder_Delay_Ms}ms reorder {percent}% 50%'

    elif kind == ModuleCtx.Packet_Duplicate:
        out = f'duplicate {percent}%'

    elif kind == ModuleCtx.Packet_Corrupt:
        out = f'corrupt {percent}%'

    elif kind == ModuleCtx.Packet_Rate:
        rate = ModuleCtx.Baseline_Rate_Mbit * (1 - severity)
        out = f'rate {rate}mbit'

    else:
        raise Exception(f'Unknown packet fault `{kind}`')

    return out

# ################################################################################################################################

def restore_link(node:'Node') -> 'None':
    _ = Container(node.container_name).run_tc(f'tc qdisc del dev {ModuleCtx.Interface} root')

    logger.info('Link of %s restored', node.node_name)

# ################################################################################################################################
# ################################################################################################################################
