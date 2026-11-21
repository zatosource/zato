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
def test_subscriber_types_dashboard() -> 'None':
    """ Pull, push REST and push service subscribers created and edited in Dashboard while the lock is held.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################
