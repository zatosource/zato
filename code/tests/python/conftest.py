# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import threading

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import generator_, strlist

    nonegen = generator_[None, None, None]
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def no_thread_outlives_its_test() -> 'nonegen':
    """ Fails a test that leaves a thread running in this process. Later tests fork workers from this process,
    and a forked worker inherits in their locked state the locks that such a thread holds at the time of the fork.
    """
    threads_before = set(threading.enumerate())

    yield

    remaining:'strlist' = []

    for thread in threading.enumerate():
        if thread not in threads_before:
            remaining.append(thread.name)

    assert remaining == []

# ################################################################################################################################
# ################################################################################################################################
