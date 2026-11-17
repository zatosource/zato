# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from faults import get_label, Total_Loss
from run import FaultRun
from stream_faults import Stream_Cut, Stream_Kinds, StreamFault
from toxiproxy import Database_Proxy

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_rest.server import PubSubServer
    from toxiproxy import Toxiproxy

# ################################################################################################################################
# ################################################################################################################################

# The level at which each kind of stream fault runs.
_partial_level = 50

# Each kind at its partial level, and one total loss, whose black hole is the same for every kind.
_cases:'list[tuple[str, int]]' = []

for _kind in Stream_Kinds:
    _cases.append((_kind, _partial_level))

_cases.append((Stream_Cut, Total_Loss))

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('kind, level', _cases)
def test_database_link(stream_database:'Toxiproxy', server:'PubSubServer', kind:'str', level:'int') -> 'None':
    """ Item 15.6 - the connections from the server to PostgreSQL are delayed, limited, sliced, reset and cut,
    and held in a black hole at a total loss.
    """
    fault = StreamFault(stream_database, Database_Proxy, kind)

    label = get_label(fault.name, level)

    run = FaultRun(server, label)
    run.run(fault, level)
    run.check()

# ################################################################################################################################
# ################################################################################################################################
