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
def test_publication_ordering() -> 'None':
    """ A publication held behind the lock while the operator removes the topic shows in the queue only when it committed first.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################
