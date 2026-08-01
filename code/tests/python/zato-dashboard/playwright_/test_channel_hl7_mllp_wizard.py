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
from hl7_client.mllp_receiver import MLLPReceiver
from mllp_channel import delete_channel, get_item_id, navigate_to_channels, send_with_both_clients, wait_for_item, \
    wait_for_port, wait_until_routed, Host
from mllp_outconn import create_outgoing_connection, delete_outgoing_connection
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.mllp.wizard.' + CryptoManager.generate_hex_string(32) + '.'

# The service every channel in these tests invokes - the fixture that answers each message
# with an acknowledgment naming the channel that handled it, so the wire sends below can
# tell from the acknowledgment alone that the wizard-created channel is the one answering
_Test_Service = 'test.hl7.mllp.wire.ack-identity'

# The sender the channel's routing criteria are about
_Wizard_App = 'WIZARD_SENDER'

# The badge picker the wizard's destinations panel runs on
_Picker_Action = 'mllp-wizard-destinations'

# ################################################################################################################################
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

class TestChannelHL7MLLPWizard:
    """ Walks the MLLP channel wizard end to end - a regression check that the wizard,
    now a wizard-kit instance, still creates channels through all three steps - and then
    invokes the created channel over the wire with the python-hl7 and Java HAPI clients.
    The same wizard then opens on the channel it created and saves it with nothing changed,
    after which the wire sends run again - a channel the edit quietly changed is one that
    stops answering the way it did before.
    """

    @pytest.mark.expect_log_errors('No matching MLLP channel for message')
    def test_mllp_wizard_full_cycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        mllp_port = zato_dashboard['mllp_port']

        # The receiver the channel's destination delivers to - a real hl7apy MLLP server
        receiver = MLLPReceiver()
        receiver.start()

        # Collect console errors along the way ..
        console_errors = [] # type: list

        def _on_console(msg:'any_') -> 'None':
            if msg.type == 'error':
                console_errors.append(msg.text)

        page.on('console', _on_console)

        # .. and server errors too.
        server_errors = [] # type: list

        def _on_response(response:'any_') -> 'None':
            if response.status >= 500:
                server_errors.append(f'{response.status} {response.url}')

        page.on('response', _on_response)

        # The connection the channel's destination points at has to exist before the wizard
        # opens, so the destinations panel has it to offer
        outconn_name = _Test_Name_Prefix + 'outconn'
        create_outgoing_connection(page, base_url, outconn_name, f'{Host}:{receiver.port}')

        navigate_to_channels(page, base_url)

        # Open the wizard from the list page
        page.click('#markup .page_prompt a:has-text("Create a new channel")')
        _ = page.wait_for_selector('#mllp-wizard', state='visible')

        # Step 1 - the name and one routing criterion, everything else keeps its defaults
        channel_name = _Test_Name_Prefix + 'channel'

        page.fill('#id_name', channel_name)
        page.evaluate(f'$("#id_msh3_sending_app").val("{_Wizard_App}")')

        # The header badge mirrors the name as it is typed
        badge_text = page.inner_text('#mllp-wizard-name-badge')
        assert channel_name in badge_text, f'Expected "{channel_name}" in the name badge, got: "{badge_text}"'

        page.click('#mllp-wizard-next')
        time.sleep(0.2)

        # Step 2 - the target service, picked through the underlying chosen select
        page.evaluate(f'$("#id_service").val("{_Test_Service}").trigger("chosen:updated")')

        # The destinations panel offers only the connections it has already loaded
        _ = page.wait_for_function('$.fn.zato.channel.hl7.mllp.wizard.destinations._connectionData !== null')

        # Open the destinations panel and pick the connection the test created
        page.click('#mllp-wizard-slot-destinations-chip')
        _ = page.wait_for_selector('#wizard-panel', state='visible')

        available_badge = f'#badge-zone-available-{_Picker_Action} .security-badge[data-connection="{outconn_name}"]'
        assigned_badge = f'#badge-zone-assigned-{_Picker_Action} .security-badge[data-connection="{outconn_name}"]'

        page.click(f'{available_badge} .security-badge-name')
        _ = page.wait_for_selector(assigned_badge, state='visible', timeout=5000)

        # Closing the panel is what writes the picked destination into the wizard's state
        page.click('#mllp-wizard-slot-destinations-chip')
        _ = page.wait_for_selector('#wizard-panel', state='detached')

        chip_text = page.inner_text('#mllp-wizard-slot-destinations-chip')
        assert '1 destination' in chip_text, f'Expected "1 destination" on the chip, got: "{chip_text}"'

        page.click('#mllp-wizard-next')
        time.sleep(0.2)

        # Step 3 - the review shows what was filled in, the destination included
        review_text = page.inner_text('#mllp-wizard-review')

        assert channel_name in review_text, f'Expected "{channel_name}" in the review, got: "{review_text}"'
        assert _Test_Service in review_text, f'Expected "{_Test_Service}" in the review, got: "{review_text}"'
        assert outconn_name in review_text, f'Expected "{outconn_name}" in the review, got: "{review_text}"'

        # Finish - back on the list with the new channel
        page.click('#mllp-wizard-next')
        page.wait_for_url('**/zato/channel/hl7/mllp/**', timeout=10000)
        _ = page.wait_for_selector('#data-table', state='visible')

        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{channel_name}"))')
        assert row is not None, f'Channel "{channel_name}" should be on the list after the wizard'

        row_text = row.inner_text()
        assert _Test_Service in row_text, f'Expected the service in the row, got: "{row_text}"'

        # The channel is live now - the external clients invoke it over the wire and it
        # answers for itself, its message reaching the destination the wizard stored
        wait_for_port(mllp_port)
        self._check_over_the_wire(mllp_port, channel_name, receiver)

        # The same wizard opens on the channel it just created, and everything the channel
        # stores is what it opens with - the destination in its hidden JSON field ..
        item_id = get_item_id(page, channel_name)

        _ = page.goto(f'{base_url}/zato/channel/hl7/mllp/wizard/{item_id}/?cluster=1')
        _ = page.wait_for_selector('#mllp-wizard', state='visible')

        stored_destinations = page.input_value('#id_edit-destinations')

        assert outconn_name in stored_destinations, \
            f'Expected "{outconn_name}" among the stored destinations, got: "{stored_destinations}"'

        assert 'hl7-mllp' in stored_destinations, \
            f'Expected the destination type among the stored destinations, got: "{stored_destinations}"'

        # .. the name in the header badge ..
        badge_text = page.inner_text('#mllp-wizard-name-badge')
        assert channel_name in badge_text, f'Expected "{channel_name}" in the name badge, got: "{badge_text}"'

        # .. and the destination counted on the chip of step 2 ..
        page.click('#mllp-wizard-next')
        time.sleep(0.2)

        chip_text = page.inner_text('#mllp-wizard-slot-destinations-chip')
        assert '1 destination' in chip_text, f'Expected "1 destination" on the chip, got: "{chip_text}"'

        # .. and saving from the review, with nothing changed, lands back on the list.
        page.click('#mllp-wizard-next')
        time.sleep(0.2)

        page.click('#mllp-wizard-next')
        _ = page.wait_for_selector('#data-table', state='visible', timeout=10000)

        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{channel_name}"))')
        assert row is not None, f'Channel "{channel_name}" should still be on the list after the edit wizard'

        # .. and the saved channel is the same channel over the wire as before - what the
        # wizard read back is what it posted, so the route and the destination are intact.
        self._check_over_the_wire(mllp_port, channel_name, receiver)

        # Delete the channel the test created and the connection its destination pointed at
        delete_channel(page, base_url, channel_name)
        delete_outgoing_connection(page, base_url, outconn_name)

        # The receiver has served its purpose
        receiver.stop()

        # No console or server errors along the way
        real_errors = [] # type: list

        for error_text in console_errors:
            if 'favicon.ico' in error_text or 'Content-Security-Policy' in error_text:
                continue
            real_errors.append(error_text)

        assert not real_errors, 'Console errors during the MLLP wizard cycle:\n' + '\n'.join(real_errors)
        assert not server_errors, 'HTTP 500+ responses during the MLLP wizard cycle:\n' + '\n'.join(server_errors)

# ################################################################################################################################

    def _check_over_the_wire(self, mllp_port:'int', channel_name:'str', receiver:'MLLPReceiver') -> 'None':
        """ Both external clients get the channel's own acknowledgment, control id echoed and
        all, and each message reaches the destination the channel stores. Runs once on the
        channel the wizard created and once more on the same channel saved through the wizard,
        so a value the edit failed to carry over is a channel that stops behaving this way.
        """
        wait_until_routed(mllp_port, channel_name, _Wizard_App)

        for control_id, result in send_with_both_clients(mllp_port, _Wizard_App):

            assert result.msa_1 == 'AA', f'Expected AA, got: {result}'
            assert result.msa_2 == control_id, f'Expected the control id echoed, got: {result}'
            assert result.msa_3 == channel_name, f'Expected `{channel_name}` to answer, got: {result}'

            _ = wait_for_item(receiver.deliveries, _text_has(control_id), f'delivery of {control_id}')

# ################################################################################################################################
# ################################################################################################################################
