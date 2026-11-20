# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import tempfile

# pytest
import pytest

# Zato
from ha_push_delivery.harness import ModuleCtx as HarnessCtx, PushEnvironment
from ha_push_delivery.server import PushDeliveryServer, start_receiver
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import render_template
from zato.common.test.exactly_once.control import create_control_dir, Env_Dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.receiver import WebhookReceiver
    from zato.common.typing_ import any_, strstrdict

# ################################################################################################################################
# ################################################################################################################################

_current_dir = os.path.dirname(__file__)

_template_path   = os.path.join(_current_dir, '_enmasse_template.yaml')
_services_source = os.path.join(_current_dir, '_services.py')

# The prefix of the control directory and the name of the directory of what the endpoint received
_control_dir_prefix = 'zato_ha_push_delivery_control_'
_receiver_dir_name  = 'receiver'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def push_environment() -> 'any_':
    """ A server whose push subscriber calls an outgoing REST connection and publishes to a topic,
    the endpoint that the connection calls, and the control files of the subscriber.
    """
    # The control files of the subscriber are shared by the server and the test process ..
    control_dir = tempfile.mkdtemp(prefix=_control_dir_prefix)
    create_control_dir(control_dir)
    os.environ[Env_Dir] = control_dir

    # .. the endpoint of the outgoing connection runs in the test process on a reserved port ..
    receiver_dir = os.path.join(control_dir, _receiver_dir_name)
    receiver_start = start_receiver(receiver_dir, HarnessCtx.Receiver_Path)
    receiver:'WebhookReceiver' = receiver_start.result

    placeholders:'strstrdict' = {
        'reader_password': 'test.reader.' + CryptoManager.generate_hex_string(),
        'port_rest': f'{receiver_start.reservation.port}',
        HarnessCtx.Delivery_Active_Key: 'false',
    }

    rendered = render_template(_template_path, placeholders)

    # .. and the server starts with the push delivery paused.
    server = PushDeliveryServer({Env_Dir: control_dir})

    try:
        server.create(rendered, _services_source)
        server.start()

        out = PushEnvironment()
        out.server = server
        out.receiver = receiver
        out.control_dir = control_dir
        out.template_path = _template_path
        out.placeholders = placeholders

        yield out

    finally:
        server.remove()
        receiver.stop()
        receiver_start.reservation.release()
        shutil.rmtree(control_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
