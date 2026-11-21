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
def test_enmasse_pending() -> 'None':
    """ An enmasse file with deletions placed while the lock is held shows the affected pairs as pending.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################
