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
def test_subscription_removal_pending() -> 'None':
    """ A topic removed while the lock is held shows as pending removal and withholds new messages.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################
