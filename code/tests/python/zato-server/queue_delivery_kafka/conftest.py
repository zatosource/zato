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
from live_environment.parts import missing_requirements, skip_or_fail
from live_kafka.bridge import local_requirements, start_bridge_parts
from live_kafka.containers import create_topic, start_kafka, stop_container
from live_kafka.suite import ModuleCtx as KafkaCtx
from queue_delivery.backends import get_backend_names
from queue_delivery.session import generate_session_certificates, make_certificate_directory, reset_after_test, \
    reset_before_test, Session
from _receiver import KafkaRecordingReceiver
from _type import kafka_type, Topics

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from certificates import CertificatePaths
    from live_kafka.containers import KafkaServer
    from zato.common.typing_ import any_

    certificatesgen = Iterator[CertificatePaths]
    kafkagen = Iterator[KafkaServer]

# ################################################################################################################################
# ################################################################################################################################

def _requirements() -> 'list[str]':
    out = missing_requirements(wants_docker=True, wants_haproxy=False)
    out.extend(local_requirements())

    return out

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

@pytest.fixture(scope='session')
def kafka_instance() -> 'kafkagen':
    """ One Kafka instance for the whole session, with the topic of every connection of the template - every
    endpoint stands in front of it.
    """
    skip_or_fail(_requirements(), KafkaCtx.Required_Variable)

    kafka = start_kafka()

    try:
        _, port = kafka.address.rsplit(':', 1)
        KafkaRecordingReceiver.instance_port = int(port)

        for topic in Topics.values():
            create_topic(kafka.container_name, topic)

        yield kafka

    finally:
        stop_container(kafka.container_name)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', params=get_backend_names(), autouse=True)
def zato_server(request:'any_', certificate_paths:'CertificatePaths', kafka_instance:'KafkaServer') -> 'any_':
    """ One quickstart server per pub/sub backend, each with a Redis and a queue bridge of its own.
    """
    bridge = start_bridge_parts()

    try:
        kafka_type.server_environment = bridge.server_environment

        session = Session(kafka_type, request.param)
        session.start(certificate_paths)

        try:
            yield
        finally:
            session.stop()

    finally:
        bridge.bridge.stop()
        bridge.redis.stop()

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
