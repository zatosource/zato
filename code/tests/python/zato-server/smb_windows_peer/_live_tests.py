# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import importlib

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

def live_test(module_name:'str', test_name:'str') -> 'callable_':
    """ Returns a test function of the live suites, whose directory the conftest puts on the path,
    so that the same test runs against the peer.
    """
    module = importlib.import_module(module_name)

    out = getattr(module, test_name)
    return out

# ################################################################################################################################
# ################################################################################################################################
