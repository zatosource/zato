# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from hl7_client import java_client
from mllp_channel import create_channel, delete_channel, send_python, wait_for_port, wait_until_rejected, \
    wait_until_routed, Host
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.mllp.clients.' + CryptoManager.generate_hex_string(32) + '.'

# The fixture service every channel here points at - it answers each message with an
# acknowledgment whose MSA-3 names the channel that handled it
_Test_Service = 'test.hl7.mllp.wire.ack-identity'

# The senders the routing criteria are about
_Registration_App = 'REGISTRATION'
_Lab_Facility     = 'LAB_FACILITY'
_Emergency_App    = 'EMERGENCY_DEPT'
_Lab_App          = 'LAB_SYSTEM'
_Unmatched_App    = 'EXTERNAL_CLINIC'
_Unmatched_Fac    = 'EXTERNAL_SITE'

# ################################################################################################################################
# ################################################################################################################################

class TestChannelHL7MLLPClients:
    """ Creates channels with different routing criteria through the wizard and proves,
    with the python-hl7 and Java HAPI clients real senders use, that each message reaches
    exactly the channel its MSH fields say - the acknowledgment's MSA-3 names the channel
    that answered, MSA-2 echoes the control id sent, and a message no route claims is
    rejected with AR.
    """

    @pytest.mark.expect_log_errors('No matching MLLP channel for message')
    def test_mllp_routing_with_external_clients(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        mllp_port = zato_dashboard['mllp_port']

        by_app_channel  = _Test_Name_Prefix + 'by-sending-app'
        by_fac_channel  = _Test_Name_Prefix + 'by-sending-facility'
        by_type_channel = _Test_Name_Prefix + 'by-message-type'
        default_channel = _Test_Name_Prefix + 'default-route'

        # Each channel is routed by different criteria, all of them filled in through the wizard
        create_channel(page, base_url, by_app_channel, service=_Test_Service,
            criteria={'msh3_sending_app': _Registration_App})

        create_channel(page, base_url, by_fac_channel, service=_Test_Service,
            criteria={'msh4_sending_facility': _Lab_Facility})

        create_channel(page, base_url, by_type_channel, service=_Test_Service,
            criteria={'msh9_message_type': 'ORU', 'msh9_trigger_event': 'R01'})

        create_channel(page, base_url, default_channel, service=_Test_Service, is_default=True)

        # The listener starts with the first channel and each route registers on its own,
        # so the wire tests begin once every channel answers for itself
        wait_for_port(mllp_port)

        wait_until_routed(mllp_port, by_app_channel,  _Registration_App)
        wait_until_routed(mllp_port, by_fac_channel,  _Emergency_App, _Lab_Facility)
        wait_until_routed(mllp_port, by_type_channel, _Lab_App, 'LAB_CENTER', 'ORU', 'R01')
        wait_until_routed(mllp_port, default_channel, _Unmatched_App, _Unmatched_Fac)

        # The same matrix runs through both clients, python-hl7 first ..
        self._run_matrix_python(mllp_port, by_app_channel, by_fac_channel, by_type_channel, default_channel)

        # .. and the Java HAPI client next, wherever there is a Java runtime to run it with.
        has_java = java_client.is_java_available()

        if has_java:
            self._run_matrix_java(mllp_port, by_app_channel, by_fac_channel, by_type_channel, default_channel)

        # With the default route gone, a message no route claims is rejected outright
        delete_channel(page, base_url, default_channel)

        rejection = wait_until_rejected(mllp_port, _Unmatched_App, _Unmatched_Fac)
        assert rejection.msa_1 == 'AR', f'Expected an AR rejection, got: {rejection}'

        if has_java:
            control_id = 'java.' + CryptoManager.generate_hex_string()
            result = java_client.send_message(Host, mllp_port, control_id, _Unmatched_App, _Unmatched_Fac)

            assert result.msa_1 == 'AR', f'Expected an AR rejection, got: {result}'
            assert result.msa_2 == control_id, f'Expected the control id echoed, got: {result}'

        # Delete the channels the test created
        delete_channel(page, base_url, by_app_channel)
        delete_channel(page, base_url, by_fac_channel)
        delete_channel(page, base_url, by_type_channel)

# ################################################################################################################################

    def _run_matrix_python(
        self,
        port:'int',
        by_app_channel:'str',
        by_fac_channel:'str',
        by_type_channel:'str',
        default_channel:'str',
        ) -> 'None':
        """ The routing matrix as the python-hl7 client sends it.
        """

        # A message with the matching sending application lands on the channel routed by MSH-3 ..
        control_id = 'py.' + CryptoManager.generate_hex_string()
        result = send_python(port, control_id, _Registration_App, 'GENERAL_HOSPITAL')

        assert result.msa_1 == 'AA', f'Expected AA, got: {result}'
        assert result.msa_2 == control_id, f'Expected the control id echoed, got: {result}'
        assert result.msa_3 == by_app_channel, f'Expected `{by_app_channel}`, got: {result}'

        # .. a different application from the matching facility lands on the one routed by MSH-4 ..
        control_id = 'py.' + CryptoManager.generate_hex_string()
        result = send_python(port, control_id, _Emergency_App, _Lab_Facility)

        assert result.msa_1 == 'AA', f'Expected AA, got: {result}'
        assert result.msa_2 == control_id, f'Expected the control id echoed, got: {result}'
        assert result.msa_3 == by_fac_channel, f'Expected `{by_fac_channel}`, got: {result}'

        # .. lab results from an unrelated sender land on the one routed by message type ..
        control_id = 'py.' + CryptoManager.generate_hex_string()
        result = send_python(port, control_id, _Lab_App, 'LAB_CENTER', 'ORU', 'R01')

        assert result.msa_1 == 'AA', f'Expected AA, got: {result}'
        assert result.msa_2 == control_id, f'Expected the control id echoed, got: {result}'
        assert result.msa_3 == by_type_channel, f'Expected `{by_type_channel}`, got: {result}'

        # .. and a message matching no criteria lands on the default channel.
        control_id = 'py.' + CryptoManager.generate_hex_string()
        result = send_python(port, control_id, _Unmatched_App, _Unmatched_Fac)

        assert result.msa_1 == 'AA', f'Expected AA, got: {result}'
        assert result.msa_2 == control_id, f'Expected the control id echoed, got: {result}'
        assert result.msa_3 == default_channel, f'Expected `{default_channel}`, got: {result}'

# ################################################################################################################################

    def _run_matrix_java(
        self,
        port:'int',
        by_app_channel:'str',
        by_fac_channel:'str',
        by_type_channel:'str',
        default_channel:'str',
        ) -> 'None':
        """ The same routing matrix as the Java HAPI client sends it.
        """

        # A message with the matching sending application lands on the channel routed by MSH-3 ..
        control_id = 'java.' + CryptoManager.generate_hex_string()
        result = java_client.send_message(Host, port, control_id, _Registration_App, 'GENERAL_HOSPITAL')

        assert result.msa_1 == 'AA', f'Expected AA, got: {result}'
        assert result.msa_2 == control_id, f'Expected the control id echoed, got: {result}'
        assert result.msa_3 == by_app_channel, f'Expected `{by_app_channel}`, got: {result}'

        # .. a different application from the matching facility lands on the one routed by MSH-4 ..
        control_id = 'java.' + CryptoManager.generate_hex_string()
        result = java_client.send_message(Host, port, control_id, _Emergency_App, _Lab_Facility)

        assert result.msa_1 == 'AA', f'Expected AA, got: {result}'
        assert result.msa_2 == control_id, f'Expected the control id echoed, got: {result}'
        assert result.msa_3 == by_fac_channel, f'Expected `{by_fac_channel}`, got: {result}'

        # .. lab results from an unrelated sender land on the one routed by message type ..
        control_id = 'java.' + CryptoManager.generate_hex_string()
        result = java_client.send_message(Host, port, control_id, _Lab_App, 'LAB_CENTER', 'ORU', 'R01')

        assert result.msa_1 == 'AA', f'Expected AA, got: {result}'
        assert result.msa_2 == control_id, f'Expected the control id echoed, got: {result}'
        assert result.msa_3 == by_type_channel, f'Expected `{by_type_channel}`, got: {result}'

        # .. and a message matching no criteria lands on the default channel.
        control_id = 'java.' + CryptoManager.generate_hex_string()
        result = java_client.send_message(Host, port, control_id, _Unmatched_App, _Unmatched_Fac)

        assert result.msa_1 == 'AA', f'Expected AA, got: {result}'
        assert result.msa_2 == control_id, f'Expected the control id echoed, got: {result}'
        assert result.msa_3 == default_channel, f'Expected `{default_channel}`, got: {result}'

# ################################################################################################################################
# ################################################################################################################################
