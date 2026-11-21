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
def test_worker_kill() -> 'None':
    """ After SIGKILL of the worker the new worker rebuilds the subscription list and the reconciler commits.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################
