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
def test_config_process_kill() -> 'None':
    """ A save during which the config process is killed shows an error and the page recovers after the reload.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################
