# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.skip(reason='Requires a live server fixture of the suite')
def test_lock_timeout_postgresql() -> 'None':
    """ Publications to other topics keep committing while a row lock is held past the lock timeout.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################
