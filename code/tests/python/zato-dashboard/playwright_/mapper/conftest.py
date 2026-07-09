# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict
    Page = Page

# ################################################################################################################################
# ################################################################################################################################

# Under the importlib import mode the tests directory is not added
# to sys.path automatically, yet the modules here import from common.
_tests_dir = os.path.dirname(os.path.abspath(__file__))
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)

# ################################################################################################################################
# ################################################################################################################################

_timeout_ms = 3000

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def base_url(zato_dashboard:'anydict') -> 'str':
    """ The address of the Dashboard started by the session-scoped environment fixture.
    """
    out = zato_dashboard['dashboard_url']
    return out

# ################################################################################################################################

@pytest.fixture()
def page(logged_in_page:'Page') -> 'Page':
    """ A logged-in Dashboard page with the mapper's own default timeout.
    """
    logged_in_page.set_default_timeout(_timeout_ms)
    return logged_in_page

# ################################################################################################################################
# ################################################################################################################################
