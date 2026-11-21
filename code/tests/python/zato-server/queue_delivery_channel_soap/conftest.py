# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# pytest
import pytest

# Test support
from queue_delivery.channel.client import reset_after_test, reset_before_test
from queue_delivery.channel.session import ChannelSession
from _type import soap_channel_type

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def zato_server() -> 'any_':
    """ One quickstart server, with the SOAP channels of the template on it.
    """
    session = ChannelSession(soap_channel_type)
    session.start()

    yield

    session.stop()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def clear_target() -> 'any_':
    """ Every test starts with a target that has recorded nothing and accepts everything.
    """
    reset_before_test()

    yield

    reset_after_test()

# ################################################################################################################################
# ################################################################################################################################
