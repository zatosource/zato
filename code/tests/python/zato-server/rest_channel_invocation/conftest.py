# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The fixtures of the suite - one server with every object of the suite, shared by all the test modules.

# stdlib
import os
import sys

# pytest
import pytest

_suite_directory = os.path.dirname(os.path.abspath(__file__))
_lib_directory = os.path.abspath(os.path.join(_suite_directory, '..', '..', 'zato-common', 'lib'))

sys.path.insert(0, _suite_directory)
sys.path.insert(0, _lib_directory)

# Zato
from channel_client import ChannelClient
from channel_definitions import build_yaml
from channel_environment import ChannelEnvironment
from channel_suite import Suite
from channel_tokens import IdentityProvider

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_services_path = os.path.join(_suite_directory, 'channel_services.py')

# The name the services module is deployed under in pickup
_services_file_name = 'rest_channel_services.py'

_name_prefix = 'zato-rest-channel-'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def suite() -> 'any_':
    """ Starts the identity provider and the server, imports every object of the suite and stops both at the end.
    """
    provider = IdentityProvider()
    provider.start()

    environment = ChannelEnvironment({_services_file_name: _services_path}, name_prefix=_name_prefix)

    try:
        environment.start()
        environment.import_yaml(build_yaml(provider))

        out = Suite(environment, provider)
        yield out

    finally:
        environment.stop()
        provider.stop()

# ################################################################################################################################

@pytest.fixture(scope='session')
def client(suite:'Suite') -> 'ChannelClient':
    out = suite.client
    return out

# ################################################################################################################################
# ################################################################################################################################
