# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from time import monotonic, sleep

# Zato
from zato.common.audit_log.api import get_audit_engine
from zato.common.audit_log.common import event_attr_table, event_count_table
from zato.common.audit_log.event_count import compact_event_counts
from zato.common.audit_log.resubmit import run_once, Action_Resend
from zato.common.audit_log.retention import run_retention
from zato.common.audit_log.search_index import get_postgresql_index_names
from zato.common.audit_log.search_index_merge import SearchIndexMerger
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

# What the process runs - the background work of one server, or one resubmission that never completes
Mode_Background = 'background'
Mode_Resubmit   = 'resubmit'

# How long a resubmission that is in progress waits before it would complete - longer than any test runs
_resubmit_seconds = 3600

# ################################################################################################################################
# ################################################################################################################################

def run_background(seconds:'float') -> 'None':
    """ Runs the retention, the count compaction and the search index merge of one server process
    one after another, without a pause, for the given number of seconds.
    """
    engine = get_audit_engine()
    index_names = get_postgresql_index_names(event_attr_table.name)
    merger = SearchIndexMerger(engine, index_names)

    compacted_up_to = 0
    deadline = monotonic() + seconds

    while monotonic() < deadline:
        run_retention(engine, utcnow())
        compacted_up_to = compact_event_counts(engine, event_count_table, compacted_up_to)
        merger.merge()

# ################################################################################################################################

def run_resubmit(event_id:'int', payload:'str', cid:'str', actor:'str', marker_path:'str') -> 'None':
    """ Starts one resubmission whose dispatch writes the marker file and then waits,
    so that the process is killed while the resubmission is in progress.
    """
    def resubmit_one() -> 'None':
        with open(marker_path, 'w') as marker_file:
            _ = marker_file.write(cid)
        sleep(_resubmit_seconds)

    _ = run_once(Action_Resend, event_id, payload, cid, actor, resubmit_one)

# ################################################################################################################################

def main() -> 'None':
    mode = sys.argv[1]

    if mode == Mode_Background:
        seconds = float(sys.argv[2])
        run_background(seconds)
    else:
        event_id = int(sys.argv[2])
        payload, cid, actor, marker_path = sys.argv[3:7]
        run_resubmit(event_id, payload, cid, actor, marker_path)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
