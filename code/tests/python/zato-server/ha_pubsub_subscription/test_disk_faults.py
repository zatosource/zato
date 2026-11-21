# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# Zato
from zato.common.pubsub.subscription_list import Lock_Timeout_Ms
from zato.common.test.pubsub_in_process_support import FilesystemFault

# Local
from _support import assert_rows_equal_list, is_postgresql, wait_for_no_unconfirmed, wait_for_unconfirmed, \
    yaml_subscription

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long each sync of the pub/sub database waits during the first fault, past the deadline of its writes
    Sync_Delay_Ms = Lock_Timeout_Ms + 1000

    # The error that each write of the pub/sub database fails with during the second fault
    Write_Error = 'ENOSPC'

# ################################################################################################################################
# ################################################################################################################################

pytestmark = pytest.mark.skipif(is_postgresql(), reason='The disk faults apply to the SQLite file of the pub/sub database')

# ################################################################################################################################
# ################################################################################################################################

def test_disk_faults(environment:'any_', pickup:'any_', runtime:'any_', names:'any_') -> 'None':
    """ A delay of the syncs of the pub/sub database during a reload and ENOSPC on its writes during a reconciliation
    are both recovered from once the fault is removed.
    """
    sub_key = runtime.sub_key(names.security_pull)
    added_pair = (sub_key, names.topic_second.lower())
    removed_pair = (sub_key, names.topic_pull.lower())

    # The path that fsfault.so compares is the one that the descriptors of the server resolve to
    fault = FilesystemFault(os.path.realpath(environment.audit_db_path))

    # The syncs are delayed while the server applies the addition ..
    fault.delay_syncs(ModuleCtx.Sync_Delay_Ms)

    try:
        pickup.apply('add-second-during-sync-delay',
            yaml_subscription(names.security_pull, [names.topic_pull, names.topic_second]))
        wait_for_unconfirmed(runtime)
    finally:
        fault.clear()

    wait_for_no_unconfirmed(runtime)

    assert added_pair in runtime.governed_pairs()
    assert_rows_equal_list(runtime)

    # .. and the writes fail while it applies the removal.
    fault.fail_writes(ModuleCtx.Write_Error)

    try:
        pickup.apply('remove-pull-during-enospc', yaml_subscription(names.security_pull, [names.topic_second]))
        wait_for_unconfirmed(runtime)

        assert removed_pair in runtime.governed_pairs()
    finally:
        fault.clear()

    wait_for_no_unconfirmed(runtime)

    assert removed_pair not in runtime.governed_pairs()
    assert_rows_equal_list(runtime)

# ################################################################################################################################
# ################################################################################################################################
