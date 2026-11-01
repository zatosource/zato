# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from conftest import Database_Proxy
from faults import get_label, Severity_Levels
from run import FaultRun
from stream_faults import Stream_Kinds, StreamFault

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from toxiproxy import Toxiproxy

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('level', Severity_Levels)
@pytest.mark.parametrize('kind', Stream_Kinds)
def test_database_link(stream_database:'Toxiproxy', kind:'str', level:'int') -> 'None':
    """ Item 15.6 - the connections from the server to PostgreSQL are delayed, limited, sliced, reset and cut,
    and held in a black hole at a total loss.
    """
    fault = StreamFault(stream_database, Database_Proxy, kind)

    label = get_label(fault.name, level)

    run = FaultRun(label)
    run.run(fault, level)
    run.check()

# ################################################################################################################################
# ################################################################################################################################
