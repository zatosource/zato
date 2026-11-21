# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from threading import Thread
from time import monotonic

# pytest
import pytest

# Zato
from zato.common.pubsub.subscription_list import Lock_Timeout_Ms
from zato.common.test.pubsub_database import get_db_mode, is_postgresql_mode

from _support import wait_for_no_unconfirmed, yaml_add_second_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_lock_timeout_postgresql(environment:'any_', pickup:'any_', runtime:'any_', names:'any_') -> 'None':
    """ Publications to other topics keep committing while a row lock is held past the lock timeout.
    """
    if not is_postgresql_mode(get_db_mode()):
        pytest.skip('Lock timeout of the suite applies to PostgreSQL')

    holder = Thread(target=runtime.hold_locks, args=(names.topic_pull, Lock_Timeout_Ms / 1000.0 + 3.0), daemon=True)
    holder.start()

    started = monotonic()
    pickup.apply('add-while-pg-locked', yaml_add_second_topic(names))
    elapsed_ms = (monotonic() - started) * 1000

    holder.join(timeout=30)
    wait_for_no_unconfirmed(runtime)

    assert elapsed_ms < Lock_Timeout_Ms * 4

    pairs = runtime.governed_pairs()
    found = False

    for _sub_key, topic_name in pairs:
        if topic_name == names.topic_second.lower():
            found = True
            break

    assert found

# ################################################################################################################################
# ################################################################################################################################
