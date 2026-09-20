# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from collections.abc import Generator

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib'))
sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# Zato - the suite's own parts
from _environment import LabEnvironment, Parts, bring_up, missing_requirements, skip_or_fail, tear_down

# ################################################################################################################################
# ################################################################################################################################

environment_gen = Generator[LabEnvironment, None, None]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def lab() -> 'environment_gen':
    """ The laboratory, up for the whole session and gone afterwards.
    """
    skip_or_fail(missing_requirements())

    parts = Parts()

    try:
        environment = bring_up(parts)
    # An interrupt is not an Exception and a setup cut short has to leave nothing behind either
    except BaseException:
        tear_down(parts)
        raise

    yield environment

    tear_down(parts)

# ################################################################################################################################
# ################################################################################################################################
