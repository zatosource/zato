# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import shutil
import tempfile
import unittest
from time import monotonic, sleep
from uuid import uuid4

# Zato
from zato.common.hl7.mllp.client import HL7MLLPClient
from zato.common.hl7.mllp.settings import Default_End_Sequence, Default_Start_Sequence
from zato.common.test.config_multi_cpu_hl7 import HL7Config
from zato.common.test.conftest_base_multi_cpu import enmasse_import, invoke_on_slot, ModuleCtx as MultiCPUCtx, \
     MultiCPUTestConfig, wait_for_every_slot
from zato.common.test.conftest_base_pubsub import find_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strset

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Host = '127.0.0.1'

    # How many times one message is retransmitted, each time over a new connection, which the listeners of the workers share
    Retransmission_Count = 16

    # How long the workers have to start the channel and the connection that an import created, in seconds
    Deadline = 60.0

    Receive_Timeout = 30.0

    # How long a duplicate count stays unchanged before it is taken as final, in seconds
    Settle_Time = 2.0

    # How many messages the counter test sends, each with a control ID of its own
    Counted_Message_Count = 24

    State_Service = 'zato.channel.hl7.get-current-state'

    Dedup_TTL_Value = 1
    Dedup_TTL_Unit = 'hours'

    # A single failure opens the breaker, which stays open for the rest of the test
    Breaker_Threshold_Percent = 50
    Breaker_Window_Seconds = 60
    Breaker_Reset_Seconds = 3600

    Outgoing_Sending_App = 'MULTICPU'

    Message_Template = 'MSH|^~\\&|{}|FACILITY|RECEIVER|FACILITY|20260101120000||ADT^A01|{}|P|2.5\rPID|1||{}'

# ################################################################################################################################
# ################################################################################################################################

def _build_message(sending_app:'str', control_id:'str') -> 'str':
    out = ModuleCtx.Message_Template.format(sending_app, control_id, uuid4().hex)
    return out

# ################################################################################################################################

def _send(message:'str', control_id:'str') -> 'bool':
    """ Sends a message over a new connection to the MLLP listener of the server and returns whether it was accepted.
    """
    client = HL7MLLPClient(
        ModuleCtx.Host,
        MultiCPUTestConfig.mllp_port,
        Default_Start_Sequence,
        Default_End_Sequence,
        receive_timeout=ModuleCtx.Receive_Timeout,
    )

    out = client.send(message.encode('utf8'), control_id).is_accepted
    return out

# ################################################################################################################################

def _get_record_directory(control_id:'str') -> 'str':
    out = os.path.join(tempfile.gettempdir(), HL7Config.Record_Directory, control_id)
    return out

# ################################################################################################################################

def _get_recorded_slots(control_id:'str') -> 'list[str]':
    """ Returns the slot of each invocation of the channel service for a control ID.
    """
    directory = _get_record_directory(control_id)

    if not os.path.isdir(directory):
        return []

    out = [name.split('-')[0] for name in os.listdir(directory)]
    return out

# ################################################################################################################################

def _send_mllp_through(slot:'int', conn_name:'str') -> 'str':
    payload = {
        'conn_name': conn_name,
        'message': _build_message(ModuleCtx.Outgoing_Sending_App, uuid4().hex),
    }

    status, body = invoke_on_slot(slot, HL7Config.Send_Service, payload)

    if status != MultiCPUCtx.Status_OK:
        raise Exception(f'{HL7Config.Send_Service} returned {status} through slot {slot} -> {body}')

    out = json.loads(body)['outcome']
    return out

# ################################################################################################################################

def _import_channel(channel_name:'str', sending_app:'str') -> 'None':
    enmasse_import({
        'channel_mllp': [{
            'name': channel_name,
            'service': HL7Config.Record_Service,
            'msh3_sending_app': sending_app,
            'is_default': False,
            'should_parse_on_input': False,
            'dedup_ttl_value': ModuleCtx.Dedup_TTL_Value,
            'dedup_ttl_unit': ModuleCtx.Dedup_TTL_Unit,
        }],
    })

# ################################################################################################################################

def _get_channel_state(slot:'int', channel_name:'str') -> 'anydict':
    status, body = invoke_on_slot(slot, ModuleCtx.State_Service, {'name': channel_name})

    if status != MultiCPUCtx.Status_OK:
        raise Exception(f'{ModuleCtx.State_Service} returned {status} through slot {slot} -> {body}')

    response = json.loads(body)
    out = json.loads(response['response_data'])['channels'][0]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMLLPAcrossWorkers(unittest.TestCase):
    """ The duplicate detection of an MLLP channel and the circuit breaker of an outgoing MLLP connection are one state
    for every worker of the server.
    """

    def test_retransmission_is_a_duplicate_in_every_worker(self) -> 'None':

        sending_app = f'MULTICPU{uuid4().hex[:8].upper()}'
        prefix = uuid4().hex[:12]

        _import_channel(f'test.multi-cpu.mllp.{prefix}', sending_app)

        control_ids:'list[str]' = []

        try:

            # Messages with control IDs of their own are sent until each worker has run the channel service,
            # which is when the channel is started in every worker and new connections reach each of them ..
            slots_seen:'strset' = set()
            all_slots = {str(slot) for slot in range(MultiCPUTestConfig.worker_count)}
            deadline = monotonic() + ModuleCtx.Deadline

            while slots_seen != all_slots:

                if monotonic() > deadline:
                    raise Exception(f'Channel service ran only in slots {sorted(slots_seen)}')

                control_id = f'{prefix}-ready-{len(control_ids)}'
                control_ids.append(control_id)

                if _send(_build_message(sending_app, control_id), control_id):
                    slots_seen.update(_get_recorded_slots(control_id))
                else:
                    sleep(MultiCPUCtx.Poll_Interval)

            # .. after which one message, retransmitted over new connections that the workers share among themselves,
            # is accepted each time ..
            control_id = f'{prefix}-retransmitted'
            control_ids.append(control_id)

            message = _build_message(sending_app, control_id)

            for _ in range(ModuleCtx.Retransmission_Count):
                self.assertTrue(_send(message, control_id))

            # .. and the service runs for it once only, whichever worker received each retransmission.
            sleep(ModuleCtx.Settle_Time)
            self.assertEqual(len(_get_recorded_slots(control_id)), 1)

        finally:
            for control_id in control_ids:
                shutil.rmtree(_get_record_directory(control_id), ignore_errors=True)

# ################################################################################################################################

    def test_channel_counters_are_identical_on_every_slot(self) -> 'None':

        sending_app = f'MULTICPU{uuid4().hex[:8].upper()}'
        prefix = uuid4().hex[:12]
        channel_name = f'test.multi-cpu.mllp.{prefix}'

        _import_channel(channel_name, sending_app)

        control_ids:'list[str]' = []
        accepted_count = 0
        deadline = monotonic() + ModuleCtx.Deadline

        try:

            # Each message travels over a new connection, which the listeners of the workers share among themselves ..
            while accepted_count < ModuleCtx.Counted_Message_Count:

                if monotonic() > deadline:
                    raise Exception(f'Accepted {accepted_count} of {ModuleCtx.Counted_Message_Count} messages')

                control_id = f'{prefix}-counted-{len(control_ids)}'
                control_ids.append(control_id)

                if _send(_build_message(sending_app, control_id), control_id):
                    accepted_count += 1
                else:
                    sleep(MultiCPUCtx.Poll_Interval)

            # .. and the counters of the channel, read through each slot, cover the messages of every worker.
            def _reports_every_message(slot:'int') -> 'bool':
                state = _get_channel_state(slot, channel_name)
                out = state['received'] == accepted_count and state['acked'] == accepted_count
                return out

            wait_for_every_slot(_reports_every_message, f'{accepted_count} messages', ModuleCtx.Deadline)

        finally:
            for control_id in control_ids:
                shutil.rmtree(_get_record_directory(control_id), ignore_errors=True)

# ################################################################################################################################

    def test_failure_in_one_worker_stops_sending_in_every_worker(self) -> 'None':

        conn_name = f'test.multi-cpu.mllp.outgoing.{uuid4().hex[:12]}'

        enmasse_import({
            'outgoing_mllp': [{
                'name': conn_name,
                'address': f'{ModuleCtx.Host}:{find_free_port()}',
                'max_retries': 0,
                'use_queue': False,
                'use_dlq': False,
                'circuit_breaker_threshold_percent': ModuleCtx.Breaker_Threshold_Percent,
                'circuit_breaker_window_seconds': ModuleCtx.Breaker_Window_Seconds,
                'circuit_breaker_reset_seconds': ModuleCtx.Breaker_Reset_Seconds,
            }],
        })

        # Every worker has the connection before any of them sends ..
        def _has_connection(slot:'int') -> 'bool':
            payload:'anydict' = {'conn_name': conn_name}
            status, _ = invoke_on_slot(slot, HL7Config.Exists_Service, payload)
            out = status == MultiCPUCtx.Status_OK
            return out

        wait_for_every_slot(_has_connection, f'connection {conn_name}', ModuleCtx.Deadline)

        # .. the endpoint refuses the one send of the worker of slot 0 ..
        self.assertEqual(_send_mllp_through(0, conn_name), HL7Config.Outcome_Failed)

        # .. and no worker sends anything more, including those that never sent.
        for slot in range(MultiCPUTestConfig.worker_count):
            self.assertEqual(_send_mllp_through(slot, conn_name), HL7Config.Outcome_Stopped, f'Slot {slot}')

# ################################################################################################################################
# ################################################################################################################################
