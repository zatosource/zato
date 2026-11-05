# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from combined import BacklogDrainFault, CombinedFault, FailoverFault
from container import Container
from faults import CPUFault, DiskFault, MemoryFault, Packet_Delay, Packet_Loss, PacketFault
from run import FaultRun
from runner import get_duration

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import FaultDatabase
    from zato.common.test.pubsub_replication import ReplicatedDatabase

# ################################################################################################################################
# ################################################################################################################################

# The level at which every fault of a combination runs unless a combination says otherwise.
_level = 50

# ################################################################################################################################
# ################################################################################################################################

def test_disk_and_packet_loss(fault_database:'FaultDatabase') -> 'None':
    """ A slow disk of PostgreSQL with 10 percent packet loss, during which the cleanup process runs its retention sweeps.
    """
    disk = DiskFault(fault_database.container, fault_database.device)
    loss = PacketFault(fault_database.container, Packet_Loss)

    fault = CombinedFault('disk-50-and-packet-loss-10', [(disk, _level), (loss, 10)])

    run = FaultRun(fault.name)
    run.run(fault, _level)
    run.check()

# ################################################################################################################################

def test_disk_delay_and_cpu(fault_database:'FaultDatabase') -> 'None':
    """ A slow disk, delayed packets and a shortage of CPU of PostgreSQL at the same time.
    """
    disk = DiskFault(fault_database.container, fault_database.device)
    delay = PacketFault(fault_database.container, Packet_Delay)
    cpu = CPUFault(fault_database.container)

    fault = CombinedFault('disk-50-packet-delay-20-and-cpu-50', [(disk, _level), (delay, 20), (cpu, _level)])

    run = FaultRun(fault.name)
    run.run(fault, _level)
    run.check()

# ################################################################################################################################

def test_memory_during_drain(fault_database:'FaultDatabase') -> 'None':
    """ The pull partners stop for half of the fault, and the backlog drains during the other half with PostgreSQL
    short of half of its memory.
    """
    run = FaultRun('')

    memory = MemoryFault(fault_database.container)
    backlog_seconds = get_duration('Zato_Test_Fault_Seconds', 120) / 2

    fault = BacklogDrainFault('memory-50-during-drain', run.traffic, memory, _level, backlog_seconds)

    run.label = fault.name
    run.run(fault, _level)
    run.check()

# ################################################################################################################################

def test_cpu_during_failover(failover_database:'ReplicatedDatabase') -> 'None':
    """ The standby is short of 90 percent of its CPU when the primary ends and the standby is promoted.
    """
    cpu = CPUFault(Container(failover_database.standby_container))

    fault = FailoverFault('cpu-90-during-failover', failover_database, cpu, 90)

    run = FaultRun(fault.name)
    run.run(fault, 90)
    run.check()

# ################################################################################################################################
# ################################################################################################################################
