# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
from http.client import OK
from typing import NamedTuple

# Zato
from pubsub_exactly_once.rest import publish
from zato.common.crypto.api import CryptoManager
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.test.conftest_base_pubsub import render_template
from zato.common.test.exactly_once.config import TestConfig
from zato.common.test.exactly_once.control import hold, Input_Topic, release, wait_until_held
from zato.common.test.exactly_once.verify import assert_exactly_once, wait_for_outputs
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.test.exactly_once.verify import OutputCheck
    from zato.common.typing_ import strlist

    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

# How long the tests wait for a held key, an imported definition and the outputs, in seconds
Hold_Timeout    = 30.0
Enmasse_Timeout = 120
Settle_Timeout  = 120.0

# ################################################################################################################################
# ################################################################################################################################

class NewKeys(NamedTuple):
    """ A prefix unique to one test and the keys under it, in the order of their publication.
    """
    prefix: 'str'
    keys: 'strlist'

# ################################################################################################################################
# ################################################################################################################################

def new_keys(count:'int') -> 'NewKeys':
    """ Returns a prefix unique to one test and that many keys under it, in the order of their publication.
    """
    suffix = CryptoManager.generate_hex_string(8)
    prefix = f'exactly-once.{suffix}.'

    keys:'strlist' = []

    for index in range(count):
        key = f'{prefix}{index:06d}'
        keys.append(key)

    out = NewKeys(prefix, keys)
    return out

# ################################################################################################################################

def publish_input(key:'str') -> 'None':
    """ Publishes one input message of the relay over REST.
    """
    payload = {'data': {'key': key}}
    result = publish(TestConfig.publisher_username, TestConfig.publisher_password, Input_Topic, payload)

    assert result.status_code == OK, result

# ################################################################################################################################

def publish_inputs(keys:'strlist') -> 'None':
    """ Publishes the input messages of the relay in the order of the keys.
    """
    for key in keys:
        publish_input(key)

# ################################################################################################################################

def get_engine() -> 'Engine':
    """ Returns the engine of the pub/sub database of the server.
    """
    out = get_pubsub_engine()
    return out

# ################################################################################################################################

def verify(prefix:'str', keys:'strlist') -> 'OutputCheck':
    """ Waits until the delivery of the keys settles and asserts that each of them was relayed exactly once and in order.
    """
    engine = get_engine()
    out = wait_for_outputs(engine, keys, prefix, Settle_Timeout)

    assert_exactly_once(out, keys)
    return out

# ################################################################################################################################

def stage_batch(keys:'strlist') -> 'None':
    """ Makes all the keys but the first one go out in one batch whose last key is held, with all the others processed.
    The first key is held until the others are published, so that the next batch reads all of them at once.
    """
    gate_key = keys[0]
    last_key = keys[-1]
    remaining_keys = keys[1:]

    # Hold the first key and the last one ..
    hold(gate_key)
    hold(last_key)

    # .. keep the delivery busy with the first key ..
    publish_input(gate_key)
    wait_until_held(gate_key, Hold_Timeout)

    # .. publish all the others meanwhile ..
    publish_inputs(remaining_keys)
    release(gate_key)

    # .. and wait until the batch of all the others reaches its last key.
    wait_until_held(last_key, Hold_Timeout)

# ################################################################################################################################

def import_enmasse(is_relay_active:'bool') -> 'None':
    """ Imports the definitions of the suite into the running server, with the delivery of the relay active or paused.
    """
    placeholders = dict(TestConfig.placeholders)

    if is_relay_active:
        placeholders['relay_delivery_active'] = 'true'
    else:
        placeholders['relay_delivery_active'] = 'false'

    # Render the template ..
    rendered = render_template(TestConfig.template_path, placeholders)

    control_dir = cast_('str', TestConfig.session_state.test_data_directory)
    rendered_path = os.path.join(control_dir, 'enmasse.yaml')

    with open(rendered_path, 'w') as rendered_file:
        _ = rendered_file.write(rendered)

    # .. and import it the way a user does.
    environment = os.environ.copy()
    _ = environment.pop('COVERAGE_PROCESS_START', None)

    command = [TestConfig.zato_bin, 'enmasse', TestConfig.server_directory, '--verbose',
        '--import', '--input', rendered_path, '--missing-wait-time', '15']

    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=Enmasse_Timeout, env=environment)

    assert result.returncode == 0, f'enmasse import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}'

# ################################################################################################################################
# ################################################################################################################################
