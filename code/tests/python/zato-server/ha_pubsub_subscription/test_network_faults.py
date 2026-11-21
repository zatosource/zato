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
def test_network_faults() -> 'None':
    """ Network faults on PostgreSQL during a reload end with rows equal to the subscription list.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################
