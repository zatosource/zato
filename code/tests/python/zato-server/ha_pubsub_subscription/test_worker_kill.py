# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Local
from _support import assert_rows_equal_list, wait_for_no_unconfirmed, wait_for_unconfirmed, wait_for_worker, \
    yaml_subscription

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_worker_kill(environment:'any_', pickup:'any_', runtime:'any_', names:'any_', write_fault:'any_') -> 'None':
    """ After SIGKILL of the worker while a pair is pending, the new worker rebuilds the subscription list
    and the reconciler writes the row.
    """
    sub_key = runtime.sub_key(names.security_pull)
    added_pair = (sub_key, names.topic_second.lower())

    # The pair is pending because the writes fail ..
    write_fault.apply()

    pickup.apply('add-second-before-kill', yaml_subscription(names.security_pull, [names.topic_pull, names.topic_second]))
    wait_for_unconfirmed(runtime)

    # .. the worker is killed while answering the request that asks for it ..
    with pytest.raises(Exception):
        runtime.kill_worker()

    # .. the writes succeed again and the new worker answers ..
    write_fault.remove()
    wait_for_worker(runtime)

    # .. and it writes the row of the pair that it read from the configuration.
    wait_for_no_unconfirmed(runtime)

    assert added_pair in runtime.governed_pairs()
    assert_rows_equal_list(runtime)

# ################################################################################################################################
# ################################################################################################################################
