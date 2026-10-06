# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import subprocess
import time

# Zato
from zato.common.audit_log.api import AuditEvent

# Zato - test helpers
from conftest import wait_for_port_open
from test_internal_services import _invoke_report
from test_mllp_audit import _send_and_receive, _wait_for_events

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The launcher the environment under test was built with, which is what runs enmasse against it
_zato_binary = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')

# How long enmasse waits for an object a definition refers to but has not seen yet
_missing_wait_time = '15'

# How long the import is given before the run is called off
_import_timeout = 120

# The channel this module creates and the MSH-3 value that routes messages to it
_channel_name        = 'test-mllp-reprocess-shape'
_sender_application  = 'TOLERANCE_SYSTEM'

# The echo service records the message it receives, a parsed one as the ER7 text it serializes to
_channel_service_name = 'test.hl7.mllp.echo'

# An OBX segment with an empty OBX-2 and a value in OBX-5 - the one normalize_obx2_value_type fills in
_control_id  = 'REPROCESS-SHAPE-001'
_obx_segment = 'OBX|1||GLUCOSE||5.4'

# How long to wait for routes to settle after the import
_settle_seconds = 1

# The channel as a user creates it - parsing on input with one tolerance toggle changed from its default
_definitions = f"""
channel_mllp:
  - name: {_channel_name}
    service: {_channel_service_name}
    msh3_sending_app: {_sender_application}
    is_audit_log_active: true
    should_parse_on_input: true
    normalize_obx2_value_type: false
"""

# ################################################################################################################################
# ################################################################################################################################

def _build_oru_r01(control_id:'str') -> 'bytes':
    message = (
        f'MSH|^~\\&|{_sender_application}|LAB|INTEGRATION_ENGINE|CENTRAL_HOSPITAL|'
        f'20260507120000||ORU^R01|{control_id}|P|2.5\r'
        f'PID|||445566^^^GENERAL_HOSPITAL^MR||SMITH^JOHN||19800101|M\r'
        f'{_obx_segment}\r'
    )
    out = message.encode('utf-8')
    return out

# ################################################################################################################################

def _import_channel(directory:'str', server_directory:'str') -> 'None':
    input_path = os.path.join(directory, 'mllp-reprocess-shape.yaml')

    with open(input_path, 'w') as input_file:
        _ = input_file.write(_definitions)

    command = [
        _zato_binary, 'enmasse', server_directory,
        '--verbose',
        '--import',
        '--input', input_path,
        '--missing-wait-time', _missing_wait_time,
    ]

    result = subprocess.run(command, capture_output=True, text=True, timeout=_import_timeout)

    if result.returncode != 0:
        raise Exception(f'enmasse import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

# ################################################################################################################################

def _recorded_messages(zato_client:'any_') -> 'anylist':
    response = zato_client.invoke('test.hl7.mllp.inspect')
    if isinstance(response, str):
        data = json.loads(response)
    else:
        data = response
    out = data['messages']
    return out

# ################################################################################################################################

def _messages_with_control_id(messages:'anylist') -> 'anylist':
    out = []
    for message in messages:
        if _control_id in message:
            out.append(message)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAReprocessDeliversTheShapeTheChannelDeliversLive:
    """ A channel that parses on input with one tolerance toggle changed from its default gives its
    service the same structured message on a reprocess as it gave it when the message arrived.
    """

# ################################################################################################################################

    def test_01_create_channel(self, zato_server:'dict', mllp_port:'int', tmp_path:'any_') -> 'None':

        _import_channel(str(tmp_path), zato_server['server_directory'])

        wait_for_port_open(mllp_port)
        time.sleep(_settle_seconds)

# ################################################################################################################################

    def test_02_the_reprocess_delivers_the_live_shape(
        self,
        zato_client:'any_',
        zato_server:'dict',
        mllp_port:'int',
        ) -> 'None':
        audit_db_path = zato_server['audit_db_path']

        # The message arrives live and the service records what it received - with the toggle off,
        # OBX-2 is empty, as it was sent ..
        ack_bytes = _send_and_receive('127.0.0.1', mllp_port, _build_oru_r01(_control_id))
        assert f'MSA|AA|{_control_id}'.encode('utf-8') in ack_bytes

        received_events = _wait_for_events(audit_db_path, _channel_name, 1, AuditEvent.Message_Received)
        original = received_events[-1]

        live_messages = _messages_with_control_id(_recorded_messages(zato_client))
        assert len(live_messages) == 1, live_messages
        assert _obx_segment in live_messages[0], live_messages[0]

        # .. and the reprocess gives the service the same structured message, parsed under the
        # channel's own toggles rather than the parser's defaults.
        report = _invoke_report(zato_client, 'zato.audit-log.hl7.reprocess', {'event_id': original['id']})
        assert report['is_ok'], report

        _ = _wait_for_events(audit_db_path, _channel_name, 2, AuditEvent.Message_Received)

        reprocessed_messages = _messages_with_control_id(_recorded_messages(zato_client))
        assert len(reprocessed_messages) == 2, reprocessed_messages
        assert reprocessed_messages[1] == live_messages[0], (reprocessed_messages[1], live_messages[0])

# ################################################################################################################################
# ################################################################################################################################
