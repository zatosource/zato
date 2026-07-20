# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the broker connections must be cooperative,
# so the patching runs before anything else is imported.
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import atexit
import logging
import os
import sys
from shutil import rmtree
from tempfile import gettempdir, mkdtemp

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

# pytest
import pytest

# Zato
from certificates import generate_certificates
from perf import silence_logging_teardown
from zato.common.test.rabbitmq_ import RabbitMQProcess

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from certificates import CertificatePaths

    brokergen = Iterator[RabbitMQProcess]
    certificatesgen = Iterator[CertificatePaths]
    logginggen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# Where the connectors' and consumers' log records go - the console stays clean.
Log_File_Path = os.path.join(gettempdir(), 'zato-pubsub-backend-amqp.log')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def quiet_logging() -> 'logginggen':
    """ Sends all log records to the log file for the whole session - consumer reconnects
    and intentional delivery failures would otherwise flood the console.
    """
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s')

    file_handler = logging.FileHandler(Log_File_Path)
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers[:] = [file_handler]
    root.setLevel(logging.INFO)

    _ = atexit.register(silence_logging_teardown)

    print(f'Logs go to {Log_File_Path}', flush=True)
    yield

# ################################################################################################################################

@pytest.fixture(scope='session')
def certificate_paths() -> 'certificatesgen':
    """ Generates the throwaway CA along with server and client certificates once per session.
    """
    directory = mkdtemp(prefix='zato-pubsub-backend-amqp-certificates-')

    out = generate_certificates(directory)
    yield out

    rmtree(directory, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture(scope='session')
def rabbitmq_broker() -> 'brokergen':
    """ A plain private RabbitMQ node started on demand.
    """
    broker = RabbitMQProcess()
    broker.start()
    yield broker

    broker.stop()

# ################################################################################################################################

@pytest.fixture(scope='session')
def rabbitmq_ssl_broker(certificate_paths:'CertificatePaths') -> 'brokergen':
    """ A private RabbitMQ node that accepts TLS connections only. The throwaway CA
    goes to SSL_CERT_FILE so every client in this process trusts the node's certificate.
    """
    previous_ca_file = os.environ.get('SSL_CERT_FILE')
    os.environ['SSL_CERT_FILE'] = certificate_paths.ca_cert

    broker = RabbitMQProcess(needs_ssl=True, certificates=certificate_paths)
    broker.start()
    yield broker

    broker.stop()

    # Restore whatever the environment held before this fixture ran.
    if previous_ca_file is None:
        _ = os.environ.pop('SSL_CERT_FILE', None)
    else:
        os.environ['SSL_CERT_FILE'] = previous_ca_file

# ################################################################################################################################
# ################################################################################################################################
