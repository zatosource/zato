# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.const import SECRETS
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import close_dialog_via_jquery
from as4_channel import create_as4_channel, delete_as4_channel, edit_as4_channel, find_as4_channel_row, \
    open_as4_channel_page, open_edit_dialog, wait_for_as4_channel_row
from as4_keys import new_test_parties

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.as4.channel.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

class TestAS4ChannelLifecycle:
    """ AS4 channel lifecycle across every tab - Main, Security, Participants
    and Routing. Everything runs through the browser and every value is verified
    by reloading the page, so the table is rebuilt from the server, and reading
    the edit dialog.
    """

# ################################################################################################################################

    def test_full_lifecycle_across_all_tabs(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'tabs'
        url_path = '/' + name
        sender, receiver = new_test_parties()

        # Create a channel touching every tab of the dialog ..
        channel_id = create_as4_channel(page, base_url, name, url_path, {

            # Main
            'as4_profile': 'peppol',
            'as4_from_party': 'peer-access-point',
            'as4_to_party': 'my-access-point',
            'as4_service': 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0',
            'as4_action': 'busdox-docid-qns::invoice',
            'as4_agreement': 'urn:fdc:peppol.eu:2017:agreements:tia:ap_provider',
            'as4_mpc': 'urn:test:mpc',
            'as4_extra_pmodes': 'urn:extra:service|ExtraAction',

            # Security
            'as4_signing_key': receiver.key,
            'as4_signing_cert_chain': receiver.certificate,
            'as4_decryption_key': receiver.key,
            'as4_peer_signing_cert': sender.certificate,
            'as4_trust_anchors': sender.certificate,

            # Participants
            'as4_serviced_participants': '0192:991825827\n0088:7315458756324',
            'as4_original_sender': '0192:991825827',
            'as4_final_recipient': '0192:810418052',

            # Routing
            'as4_inbound_topic': 'test.as4.inbound.topic',
        })

        # .. reload the page so the table is rebuilt from what the server persisted ..
        open_as4_channel_page(page, base_url, query=name)
        _ = wait_for_as4_channel_row(page, name)

        # .. open the edit dialog and verify every value came back ..
        open_edit_dialog(page, channel_id)

        assert page.input_value('#id_edit-name') == name
        assert page.input_value('#id_edit-url_path') == url_path
        assert page.input_value('#id_edit-as4_profile') == 'peppol'
        assert page.input_value('#id_edit-as4_from_party') == 'peer-access-point'
        assert page.input_value('#id_edit-as4_to_party') == 'my-access-point'
        assert page.input_value('#id_edit-as4_service') == 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0'
        assert page.input_value('#id_edit-as4_action') == 'busdox-docid-qns::invoice'
        assert page.input_value('#id_edit-as4_agreement') == 'urn:fdc:peppol.eu:2017:agreements:tia:ap_provider'
        assert page.input_value('#id_edit-as4_mpc') == 'urn:test:mpc'
        assert page.input_value('#id_edit-as4_extra_pmodes') == 'urn:extra:service|ExtraAction'

        # The private keys are stored encrypted, so the dialog shows the encrypted
        # form rather than the pasted plain text ..
        assert page.input_value('#id_edit-as4_signing_key').startswith(SECRETS.PREFIX)
        assert page.input_value('#id_edit-as4_decryption_key').startswith(SECRETS.PREFIX)

        # .. while the public certificates round-trip verbatim.
        assert page.input_value('#id_edit-as4_signing_cert_chain').strip() == receiver.certificate.strip()
        assert page.input_value('#id_edit-as4_peer_signing_cert').strip() == sender.certificate.strip()
        assert page.input_value('#id_edit-as4_trust_anchors').strip() == sender.certificate.strip()

        assert page.input_value('#id_edit-as4_serviced_participants') == '0192:991825827\n0088:7315458756324'
        assert page.input_value('#id_edit-as4_original_sender') == '0192:991825827'
        assert page.input_value('#id_edit-as4_final_recipient') == '0192:810418052'

        assert page.input_value('#id_edit-as4_inbound_topic') == 'test.as4.inbound.topic'

        # .. now edit fields from several tabs at once ..
        edited_name = name + '-edited'
        edit_as4_channel(page, channel_id, {
            'name': edited_name,
            'as4_profile': 'edelivery1',
            'as4_serviced_participants': '0192:991825827',
            'as4_inbound_topic': '',
            'service': 'demo.ping',
        })
        _ = wait_for_as4_channel_row(page, edited_name)

        # .. reload again and verify the changes round-tripped through the server ..
        open_as4_channel_page(page, base_url, query=edited_name)
        _ = wait_for_as4_channel_row(page, edited_name)
        open_edit_dialog(page, channel_id)

        assert page.input_value('#id_edit-name') == edited_name
        assert page.input_value('#id_edit-as4_profile') == 'edelivery1'
        assert page.input_value('#id_edit-as4_serviced_participants') == '0192:991825827'
        assert page.input_value('#id_edit-as4_inbound_topic') == ''
        assert page.input_value('#id_edit-service') == 'demo.ping'

        # The fields the edit did not touch are still there ..
        assert page.input_value('#id_edit-url_path') == url_path
        assert page.input_value('#id_edit-as4_to_party') == 'my-access-point'
        assert page.input_value('#id_edit-as4_signing_cert_chain').strip() == receiver.certificate.strip()

        # .. and the encrypted keys survived the edit unchanged in kind.
        assert page.input_value('#id_edit-as4_signing_key').startswith(SECRETS.PREFIX)

        # .. close the dialog ..
        close_dialog_via_jquery(page, 'edit-div')

        # .. delete and verify the row is gone ..
        delete_as4_channel(page, channel_id)
        assert find_as4_channel_row(page, edited_name) is None

        # .. and one more reload to confirm the server no longer knows the channel.
        open_as4_channel_page(page, base_url, query=edited_name)
        assert find_as4_channel_row(page, edited_name) is None

# ################################################################################################################################

    def test_channel_without_service_or_topic(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A channel needs neither a service nor a topic - accepted messages then go
        to the default inbound topic, which the form leaves empty.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'serviceless'
        url_path = '/' + name
        _, receiver = new_test_parties()

        channel_id = create_as4_channel(page, base_url, name, url_path, {
            'as4_profile': 'edelivery1',
            'as4_signing_key': receiver.key,
            'as4_signing_cert_chain': receiver.certificate,
        })

        open_as4_channel_page(page, base_url, query=name)
        _ = wait_for_as4_channel_row(page, name)
        open_edit_dialog(page, channel_id)

        assert page.input_value('#id_edit-service') == ''
        assert page.input_value('#id_edit-as4_inbound_topic') == ''

        close_dialog_via_jquery(page, 'edit-div')
        delete_as4_channel(page, channel_id)

# ################################################################################################################################
# ################################################################################################################################
