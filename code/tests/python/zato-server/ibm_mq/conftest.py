# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from shutil import rmtree
from tempfile import mkdtemp

sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# Zato
from certificates import generate_certificates
from containers import start_ibm_mq, stop_container

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from certificates import CertificatePaths
    from containers import MQServer

    certificatesgen = Iterator[CertificatePaths]
    servergen = Iterator[MQServer]

# ################################################################################################################################
# ################################################################################################################################

# The queue manager inside the container must be able to traverse into the certificate directory
_certificate_dir_mode = 0o755

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def certificate_paths() -> 'certificatesgen':
    """ Generates the throwaway CA along with the queue manager's keystore once per session.
    The directory lives directly under the system temporary directory because the keystore
    is mounted into a container whose user cannot traverse pytest's own 0700 directories.
    """
    directory = mkdtemp(prefix='zato-ibm-mq-certificates-')
    os.chmod(directory, _certificate_dir_mode)

    out = generate_certificates(directory)
    yield out

    rmtree(directory, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture(scope='session')
def ibm_mq_server() -> 'servergen':
    """ A plain IBM MQ queue manager started on demand in a container.
    """
    server = start_ibm_mq(needs_ssl=False)
    yield server

    stop_container(server.container_name)

# ################################################################################################################################

@pytest.fixture(scope='session')
def ibm_mq_ssl_server(certificate_paths:'CertificatePaths') -> 'servergen':
    """ An IBM MQ queue manager whose developer channels require TLS.
    """
    server = start_ibm_mq(needs_ssl=True, certificates=certificate_paths)
    yield server

    stop_container(server.container_name)

# ################################################################################################################################
# ################################################################################################################################
