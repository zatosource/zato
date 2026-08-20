# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# pytest
import pytest

# Zato
from audit_log_ui import goto_audit_log, wait_for_msg_id_row
from audit_resubmit import is_report_ok, resubmit_until
from hl7_client.mllp_receiver import MLLPReceiver
from mllp_channel import create_channel, create_outgoing_connection, delete_channel, delete_outgoing_connection, \
    save_channel, send_python, send_with_both_clients, wait_for_item, wait_for_port, wait_until_accepted, Host
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict
    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.mllp.audit.' + CryptoManager.generate_hex_string(32) + '.'

# The sender the channel's routing criteria are about
_Audit_App = 'AUDIT_SENDER'

# The source the channel-side MLLP events are filed under
_Audit_Source = 'mllp-channel'

# The event an arrival is written down as - the channel also records the acknowledgment
# it answered with, under the same control id
_Event_Message_Received = 'message-received'

# How long a failed delivery's own retries take to run their course - each hop gets two more
# attempts a second apart, so by now what failed stays failed until an operator steps in
_Retry_Exhaustion_Wait = 6.0

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_received_row(page:'Page', control_id:'str') -> 'str':
    """ Waits until the audit list holds the arrival of the message with this control id
    and returns the selector of its row - an HL7 message is named by its control id, MSH-10.
    """
    out = wait_for_msg_id_row(page, control_id, event_type=_Event_Message_Received)
    return out

# ################################################################################################################################

def _text_has(control_id:'str') -> 'any_':
    """ A predicate matching a receiver delivery whose text carries this control id.
    """
    def _predicate(item:'any_') -> 'bool':
        out = control_id in item.text
        return out

    return _predicate

# ################################################################################################################################
# ################################################################################################################################

class TestChannelHL7MLLPAudit:
    """ Proves the compliance and recovery story of an audited channel from outside - what
    external clients send over the wire is what the dashboard's audit log lists, and a message
    whose receiver was down when it arrived reaches that receiver after an operator reprocesses
    it from that very audit log. The channel is saved through the wizard along the way, so a
    switch the edit posted back the other way round is caught by the log going quiet.
    """

    @pytest.mark.expect_log_errors(
        'No matching MLLP channel for message',
        'Connection refused',
        'ConnectionRefusedError',
    )
    def test_audit_log_and_reprocess(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        mllp_port = zato_dashboard['mllp_port']

        channel_name = _Test_Name_Prefix + 'audited'
        mllp_conn    = _Test_Name_Prefix + 'audited-mllp'

        receiver = MLLPReceiver()
        receiver.start()

        try:
            # An audited channel with one MLLP destination and no service - the wizard's
            # logging step is where auditing is turned on
            create_outgoing_connection(page, base_url, mllp_conn, f'{Host}:{receiver.port}')

            create_channel(page, base_url, channel_name,
                criteria={'msh3_sending_app': _Audit_App},
                is_audit_log_active=True,
                destinations=[_mllp_destination_of(mllp_conn)])

            wait_for_port(mllp_port)
            _ = wait_until_accepted(mllp_port, _Audit_App)

            # The compliance half - what the clients send is what the audit log lists ..
            control_ids = []

            for control_id, result in send_with_both_clients(mllp_port, _Audit_App):
                assert result.msa_1 == 'AA', f'Expected AA, got: {result}'
                control_ids.append(control_id)

            # .. each message reached the receiver ..
            for control_id in control_ids:
                _ = wait_for_item(receiver.deliveries, _text_has(control_id), f'delivery of {control_id}')

            # .. and each is on the channel's audit log page under the control id its
            # sender gave it.
            goto_audit_log(page, base_url, _Audit_Source, channel_name)

            for control_id in control_ids:
                _ = _wait_for_received_row(page, control_id)

            # Saving the channel through the wizard again, with nothing changed, leaves it
            # audited - a switch the wizard posted back the other way round would show up
            # here as an arrival its audit log knows nothing about ..
            save_channel(page, base_url, channel_name)
            _ = wait_until_accepted(mllp_port, _Audit_App)

            saved_control_id = 'py.' + CryptoManager.generate_hex_string()
            result = send_python(mllp_port, saved_control_id, _Audit_App)
            assert result.msa_1 == 'AA', f'Expected AA, got: {result}'

            _ = wait_for_item(receiver.deliveries, _text_has(saved_control_id), f'delivery of {saved_control_id}')

            goto_audit_log(page, base_url, _Audit_Source, channel_name)
            _ = _wait_for_received_row(page, saved_control_id)

            # .. the recovery half - the receiver goes down and a message arrives while it is gone ..
            receiver.stop()

            lost_control_id = 'py.' + CryptoManager.generate_hex_string()
            result = send_python(mllp_port, lost_control_id, _Audit_App)

            # .. the sender still gets its acknowledgment - the delivery failing behind
            # the scenes is the channel's problem, not the sender's ..
            assert result.msa_1 == 'AA', f'Expected AA, got: {result}'

            # .. the delivery's own retries run their course against the closed port, so what
            # arrives later can only have come from the reprocess ..
            time.sleep(_Retry_Exhaustion_Wait)

            for delivery in receiver.deliveries:
                assert lost_control_id not in delivery.text, f'The message arrived without a reprocess: {delivery.text}'

            # .. the receiver comes back on the same port, the way real systems do ..
            receiver.start()

            # .. an operator reprocesses the message from the audit log page ..
            goto_audit_log(page, base_url, _Audit_Source, channel_name)
            row_selector = _wait_for_received_row(page, lost_control_id)

            _ = resubmit_until(page, row_selector, is_report_ok)

            # .. and the delivery that had nowhere to go now arrives.
            _ = wait_for_item(receiver.deliveries, _text_has(lost_control_id), f'delivery of {lost_control_id}')

        finally:
            delete_channel(page, base_url, channel_name)
            delete_outgoing_connection(page, base_url, mllp_conn)

            receiver.stop()

# ################################################################################################################################
# ################################################################################################################################

def _mllp_destination_of(connection:'str') -> 'anydict':
    """ One MLLP destination entry in the shape the wizard's state holds them in.
    """
    out = {'connection': connection, 'type': 'hl7-mllp', 'is_active': True, 'options': {}}
    return out

# ################################################################################################################################
# ################################################################################################################################
