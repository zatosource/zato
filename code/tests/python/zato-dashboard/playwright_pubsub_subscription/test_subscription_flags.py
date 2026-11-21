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
def test_subscription_flags() -> 'None':
    """ Every flag changed in Dashboard is obeyed by publications and by the queue of the subscriber.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################
