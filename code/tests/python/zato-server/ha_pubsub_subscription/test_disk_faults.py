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
def test_disk_faults() -> 'None':
    """ Disk faults of the pub/sub database during a reload and a reconciliation are recovered from.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################
