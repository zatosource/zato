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
from snowflake_test_server import SnowflakeTestServer

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def snowflake_server():
    """ A live HTTPS Snowflake server with a CA-signed certificate. The connector's trust store
    is pointed at the test CA for the duration of the session.
    """
    server = SnowflakeTestServer()
    server.start()
    server.configure(password='password.' + CryptoManager.generate_hex_string())

    # The Snowflake connector goes through requests, which honours this variable.
    previous_bundle = os.environ.get('REQUESTS_CA_BUNDLE')
    os.environ['REQUESTS_CA_BUNDLE'] = server.tls_material.ca_path

    yield server

    if previous_bundle is None:
        del os.environ['REQUESTS_CA_BUNDLE']
    else:
        os.environ['REQUESTS_CA_BUNDLE'] = previous_bundle

    server.stop()

# ################################################################################################################################

@pytest.fixture(scope='session')
def snowflake_http_server():
    """ A live plain-HTTP Snowflake server for pure protocol tests.
    """
    server = SnowflakeTestServer(tls=False)
    server.start()
    server.configure(password='password.' + CryptoManager.generate_hex_string())

    yield server

    server.stop()

# ################################################################################################################################

@pytest.fixture(scope='session')
def snowflake_untrusted_server():
    """ A live HTTPS Snowflake server whose certificate no configured trust store knows about.
    """
    server = SnowflakeTestServer()
    server.start()
    server.configure(password='password.' + CryptoManager.generate_hex_string())

    yield server

    server.stop()

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
    os.environ['SSL_CERT_FILE'] = server.tls_material.ca_path

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
