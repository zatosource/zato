# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from common import PerfDatabase
from runner import run_complete_perf

# ################################################################################################################################
# ################################################################################################################################

def test_rule_engine_perf_sqlite(sqlite_perf_database:'PerfDatabase') -> 'None':
    """ The complete rule-engine SQL layer performance scenario on file-backed SQLite.
    """
    run_complete_perf(sqlite_perf_database)

# ################################################################################################################################
# ################################################################################################################################
