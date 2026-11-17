# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from faults import get_label, Packet_Kinds, Packet_Loss, PacketFault, Total_Loss
from run import FaultRun

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_rest.server import PubSubServer
    from conftest import FaultDatabase

# ################################################################################################################################
# ################################################################################################################################

# The level at which each kind of packet fault runs.
_partial_level = 50

# Each kind at its partial level, and one total loss, whose netem parameters are the same for every kind.
_cases:'list[tuple[str, int]]' = []

for _kind in Packet_Kinds:
    _cases.append((_kind, _partial_level))

_cases.append((Packet_Loss, Total_Loss))

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('kind, level', _cases)
def test_packets(fault_database:'FaultDatabase', server:'PubSubServer', kind:'str', level:'int') -> 'None':
    """ Item 15.5 - the packets between pub/sub and PostgreSQL are lost, delayed with jitter, reordered,
    duplicated or corrupted, in both directions. In the TLS modes, a corrupted record ends its connection.
    """
    fault = PacketFault(fault_database.container, kind)

    label = get_label(fault.name, level)

    run = FaultRun(server, label)
    run.run(fault, level)
    run.check()

# ################################################################################################################################
# ################################################################################################################################
