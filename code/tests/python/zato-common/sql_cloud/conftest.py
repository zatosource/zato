# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The test server library uses flat imports, the way the SOAP suite's lib does.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################

from redshift_test_server import RedshiftTestServer
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def redshift_server():
    """ A live Redshift server with the TLS upgrade backed by a CA-signed certificate.
    The default trust paths are pointed at the test CA for the duration of the session.
    """
    server = RedshiftTestServer()
    server.start()
    server.configure(password='password.' + CryptoManager.generate_hex_string())

    # redshift_connector loads the default certificates, which honour this variable.
    previous_cert_file = os.environ.get('SSL_CERT_FILE')
    os.environ['SSL_CERT_FILE'] = cast_('any_', server.tls_material).ca_path

    yield server

    if previous_cert_file is None:
        del os.environ['SSL_CERT_FILE']
    else:
        os.environ['SSL_CERT_FILE'] = previous_cert_file

    server.stop()

# ################################################################################################################################

@pytest.fixture(scope='session')
def redshift_plain_server():
    """ A live Redshift server without TLS for pure protocol tests.
    """
    server = RedshiftTestServer(tls=False)
    server.start()
    server.configure(password='password.' + CryptoManager.generate_hex_string())

    yield server

    server.stop()

# ################################################################################################################################

@pytest.fixture(scope='session')
def redshift_untrusted_server():
    """ A live TLS Redshift server whose certificate no configured trust store knows about.
    """
    server = RedshiftTestServer()
    server.start()
    server.configure(password='password.' + CryptoManager.generate_hex_string())

    yield server

    server.stop()

# ################################################################################################################################
# ################################################################################################################################
