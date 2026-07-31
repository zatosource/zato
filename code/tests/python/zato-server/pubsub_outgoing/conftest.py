# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The modules next to this one are imported by name, which is what puts them within reach
sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.config_pubsub_outgoing import TestConfig
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture, find_free_port

# local
from _receiver import RecordingReceiver

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_template_path = os.path.join(os.path.dirname(__file__), '_enmasse_template.yaml')
_services_source = os.path.join(os.path.dirname(__file__), '_services.py')

# What a FHIR server answers a document it stored with - the resource as it now stands,
# in the content type a FHIR server speaks.
_fhir_status_code = 201
_fhir_content_type = 'application/fhir+json'
_fhir_stored_body = '{"resourceType": "Patient", "id": "stored-1"}'

# ################################################################################################################################
# ################################################################################################################################

def _new_fhir_receiver(port:'int') -> 'RecordingReceiver':
    """ A target that answers the way a FHIR server does - the resource it stored, in its own content type.
    """
    out = RecordingReceiver(port, _fhir_status_code, _fhir_content_type, _fhir_stored_body)
    out.start()

    return out

# ################################################################################################################################
# ################################################################################################################################

def _build_config(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_port:'int',
    invoke_password:'str',
) -> 'anydict':

    connection_password = 'test.outgoing.' + CryptoManager.generate_hex_string()

    # Each connection has a target of its own, so that what one of them receives
    # is never mistaken for what another one did ..
    orders_port = find_free_port()
    inventory_port = find_free_port()
    rename_port = find_free_port()
    delete_port = find_free_port()
    fhir_port = find_free_port()
    fhir_secured_port = find_free_port()
    shared_rest_port = find_free_port()
    shared_fhir_port = find_free_port()

    orders_receiver = RecordingReceiver(orders_port)
    orders_receiver.start()

    inventory_receiver = RecordingReceiver(inventory_port)
    inventory_receiver.start()

    rename_receiver = RecordingReceiver(rename_port)
    rename_receiver.start()

    delete_receiver = RecordingReceiver(delete_port)
    delete_receiver.start()

    # .. the FHIR targets answer the way a FHIR server does, because what the client makes
    # of that answer is what decides whether a document counts as delivered ..
    fhir_receiver = _new_fhir_receiver(fhir_port)
    fhir_secured_receiver = _new_fhir_receiver(fhir_secured_port)

    shared_rest_receiver = RecordingReceiver(shared_rest_port)
    shared_rest_receiver.start()

    shared_fhir_receiver = _new_fhir_receiver(shared_fhir_port)

    # .. and all of them are stopped when the session ends.
    state.receivers.append(orders_receiver)
    state.receivers.append(inventory_receiver)
    state.receivers.append(rename_receiver)
    state.receivers.append(delete_receiver)
    state.receivers.append(fhir_receiver)
    state.receivers.append(fhir_secured_receiver)
    state.receivers.append(shared_rest_receiver)
    state.receivers.append(shared_fhir_receiver)

    logger.info('Receivers started on ports %s', [
        orders_port, inventory_port, rename_port, delete_port,
        fhir_port, fhir_secured_port, shared_rest_port, shared_fhir_port,
    ])

    placeholders = {
        'port_orders': str(orders_port),
        'port_inventory': str(inventory_port),
        'port_rename': str(rename_port),
        'port_delete': str(delete_port),
        'port_fhir': str(fhir_port),
        'port_fhir_secured': str(fhir_secured_port),
        'port_shared_rest': str(shared_rest_port),
        'port_shared_fhir': str(shared_fhir_port),
        'connection_password': connection_password,
    }

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
    ) -> 'None':

        TestConfig.base_url = f'http://{host}:{server_port}'
        TestConfig.password = invoke_password

        TestConfig.server_directory = server_directory
        TestConfig.server_port = server_port
        TestConfig.zato_bin = zato_bin

        TestConfig.connection_username = 'test.outgoing.api'
        TestConfig.connection_password = connection_password

        TestConfig.orders_receiver = orders_receiver
        TestConfig.inventory_receiver = inventory_receiver
        TestConfig.rename_receiver = rename_receiver
        TestConfig.delete_receiver = delete_receiver
        TestConfig.fhir_receiver = fhir_receiver
        TestConfig.fhir_secured_receiver = fhir_secured_receiver
        TestConfig.shared_rest_receiver = shared_rest_receiver
        TestConfig.shared_fhir_receiver = shared_fhir_receiver

        TestConfig.state = state

    out:'anydict' = {
        'placeholders': placeholders,
        'populate_callback': _populate,
        'hot_deploy_sources': [_services_source],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server = create_zato_server_fixture(
    logger_name='zato.test.pubsub_outgoing.conftest',
    server_log_copy_name='server-logs-pubsub-outgoing.txt',
    template_path=_template_path,
    quickstart_prefix='zato_pubsub_outgoing_qs_',
    extra_server_env={},
    patch_server_conf_bind=False,
    build_config_callback=_build_config,
)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def clear_receivers() -> 'any_':
    """ Every test starts with targets that have received nothing and are accepting everything.
    """
    TestConfig.orders_receiver.clear()
    TestConfig.inventory_receiver.clear()
    TestConfig.rename_receiver.clear()
    TestConfig.delete_receiver.clear()
    TestConfig.fhir_receiver.clear()
    TestConfig.fhir_secured_receiver.clear()
    TestConfig.shared_rest_receiver.clear()
    TestConfig.shared_fhir_receiver.clear()

    yield

# ################################################################################################################################
# ################################################################################################################################
