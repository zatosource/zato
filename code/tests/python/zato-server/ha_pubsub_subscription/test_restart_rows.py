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
def test_restart_rows() -> 'None':
    """ Subscriptions removed while the server is stopped have no rows after the restart.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################
