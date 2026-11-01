# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from faults import get_label, Packet_Kinds, PacketFault, Severity_Levels
from run import FaultRun

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import FaultDatabase

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('level', Severity_Levels)
@pytest.mark.parametrize('kind', Packet_Kinds)
def test_packets(fault_database:'FaultDatabase', kind:'str', level:'int') -> 'None':
    """ Item 15.5 - the packets between pub/sub and PostgreSQL are lost, delayed with jitter, reordered,
    duplicated or corrupted, in both directions. In the TLS modes, a corrupted record ends its connection.
    """
    fault = PacketFault(fault_database.container, kind)

    label = get_label(fault.name, level)

    run = FaultRun(label)
    run.run(fault, level)
    run.check()

# ################################################################################################################################
# ################################################################################################################################
