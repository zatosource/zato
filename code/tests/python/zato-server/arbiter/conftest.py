# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# pytest
import pytest

# The tests of the writer process under the arbiter build their messages with the helpers of the writer tests
_writer_tests_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'pubsub_writer_process')
sys.path.insert(0, os.path.abspath(_writer_tests_dir))

# Zato
from arbiter_common import terminate_started_arbiters # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import generator_

    nonegenerator = generator_[None, None, None]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def terminate_arbiters() -> 'nonegenerator':
    """ Terminates the arbiters of a test after it completes, so a failed test leaves no process behind.
    """
    yield
    terminate_started_arbiters()

# ################################################################################################################################
# ################################################################################################################################
