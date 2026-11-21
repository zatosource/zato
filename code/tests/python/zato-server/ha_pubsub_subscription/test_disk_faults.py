# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile

# pytest
import pytest

# Zato
from zato.common.test.pubsub_database import get_db_mode, is_postgresql_mode
from zato.common.test.pubsub_in_process_support import FilesystemFault, ModuleCtx as SupportCtx

from _support import wait_for_no_unconfirmed, yaml_add_second_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def _ensure_fsfault_control() -> 'None':
    if SupportCtx.Env_FSFault_Control not in os.environ:
        control_file = tempfile.NamedTemporaryFile(prefix='fsfault-control-', delete=False)
        _ = control_file.write(b'prefix=\n')
        control_file.close()
        os.environ[SupportCtx.Env_FSFault_Control] = control_file.name

# ################################################################################################################################

def test_disk_faults(environment:'any_', pickup:'any_', runtime:'any_', names:'any_') -> 'None':
    """ Disk faults of the pub/sub database during a reload and a reconciliation are recovered from.
    """
    if is_postgresql_mode(get_db_mode()):
        pytest.skip('Disk faults of the suite apply to SQLite')

    _ensure_fsfault_control()

    db_path = environment.audit_db_path
    fault = FilesystemFault(db_path)

    fault.delay_syncs(6000)

    try:
        pickup.apply('add-during-sync-delay', yaml_add_second_topic(names))
    finally:
        fault.clear()

    wait_for_no_unconfirmed(runtime)

    fault.fail_writes('ENOSPC')

    try:
        pickup.apply('add-during-enospc', yaml_add_second_topic(names))
    finally:
        fault.clear()

    wait_for_no_unconfirmed(runtime)

    pairs = runtime.governed_pairs()
    found = False

    for _sub_key, topic_name in pairs:
        if topic_name == names.topic_second.lower():
            found = True
            break

    assert found

# ################################################################################################################################
# ################################################################################################################################
