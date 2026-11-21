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
def test_delivery_toggle_pending() -> 'None':
    """ Delivery switched on while a pair is pending shows the active flag and the pending status together.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################
