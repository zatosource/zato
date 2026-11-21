# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.skip(reason='Requires the Dashboard fixture of the suite')
def test_lock_timeout_postgresql() -> 'None':
    """ A topic removed in Dashboard while a row lock is held is saved at once and clears after the lock is released.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################
