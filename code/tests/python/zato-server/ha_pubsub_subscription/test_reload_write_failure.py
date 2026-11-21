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
def test_reload_write_failure() -> 'None':
    """ An enmasse file applied while writes to the pub/sub database fail is obeyed by publications.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################
