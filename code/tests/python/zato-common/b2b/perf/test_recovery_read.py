# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.test.b2b_perf import new_perf_settings, PerfRun
from zato.common.test.b2b_perf_common import Max_Recovery_Seconds
from zato.common.test.b2b_perf_seed import Seed_Exchanges, Seed_Transactions, seed_recovery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from perf_db import PerfDatabase
    from zato.common.typing_ import callable_
    callable_ = callable_
    Path = Path
    PerfDatabase = PerfDatabase

# ################################################################################################################################
# ################################################################################################################################

def test_recovery_read(database:'PerfDatabase', tmp_path:'Path', record_property:'callable_') -> 'None':
    """ A host started over an audit log with awaiting business transactions, open exchanges and a large number
    of completed events recovers the transactions and the exchanges within the time a recovery is allowed.
    """
    writer = GroupCommitWriter(database.engine)
    seed_recovery(database.engine, writer)
    writer.stop()

    work_dir = str(tmp_path)
    settings = new_perf_settings(work_dir, database.env, 0, 0)

    run = PerfRun(settings)
    result = run.run_recovery()

    recovery_seconds = round(result.duration_seconds, 2)
    rss_mb = round(result.rss_mb, 1)

    record_property('recovery_seconds', recovery_seconds)
    record_property('recovery_statements', result.statements)
    record_property('recovery_rss_mb', rss_mb)
    record_property('recovered_transactions', result.transactions)
    record_property('recovered_exchanges', result.exchanges)

    assert result.transactions == Seed_Transactions
    assert result.exchanges == Seed_Exchanges
    assert result.duration_seconds < Max_Recovery_Seconds

# ################################################################################################################################
# ################################################################################################################################
