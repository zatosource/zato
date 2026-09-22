# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# pytest
import pytest

# Test support
from queue_delivery.backends import get_backend_names
from queue_delivery.session import generate_session_certificates, make_certificate_directory, reset_after_test, \
    reset_before_test, Session
from _type import rest_type

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from certificates import CertificatePaths
    from zato.common.typing_ import any_

    certificatesgen = Iterator[CertificatePaths]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def certificate_paths() -> 'certificatesgen':
    """ Generates the throwaway CA along with server and client certificates once per session.
    """
    directory = make_certificate_directory()

    out = generate_session_certificates(directory)
    yield out

    shutil.rmtree(directory, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', params=get_backend_names(), autouse=True)
def zato_server(request:'any_', certificate_paths:'CertificatePaths') -> 'any_':
    """ One quickstart server per pub/sub backend.
    """
    session = Session(rest_type, request.param)
    session.start(certificate_paths)

    yield

    session.stop()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def clear_receivers() -> 'any_':
    """ Every test starts with endpoints that have received nothing and are accepting everything.
    """
    reset_before_test()

    yield

    reset_after_test()

# ################################################################################################################################
# ################################################################################################################################
