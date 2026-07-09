# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.const import SECRETS
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import close_dialog_via_jquery
from as4_outconn import create_as4_outconn, delete_as4_outconn, edit_as4_outconn, find_as4_outconn_row, \
    open_as4_outconn_page, open_edit_dialog, wait_for_as4_outconn_row
from as4_keys import new_test_parties

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.as4.out.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

class TestAS4OutconnLifecycle:
    """ Outgoing AS4 connection lifecycle across every tab - Main, Delivery, Security
    and More. Everything runs through the browser and every value is verified
    by reloading the page, so the table is rebuilt from the server, and reading
    the edit dialog.
    """

# ################################################################################################################################

    def test_full_lifecycle_across_all_tabs(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'tabs'
        sender, receiver = new_test_parties()

        # Create a connection touching every tab of the dialog ..
        outconn_id = create_as4_outconn(page, base_url, name, 'https://ap.example.com:8443', {

            # Main
            'as4_profile': 'peppol',
            'as4_from_party': 'my-access-point',
            'as4_to_party': 'peer-access-point',
            'as4_service': 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0',
            'as4_action': 'busdox-docid-qns::invoice',
            'as4_agreement': 'urn:fdc:peppol.eu:2017:agreements:tia:ap_provider',

            # Delivery
            'url_path': '/as4',
            'as4_use_discovery': True,
            'as4_sml_domain': 'acc.edelivery.tech.ec.europa.eu',
            'as4_mpc': 'urn:test:mpc',
            'timeout': '20',
            'validate_tls': 'False',

            # Security
            'as4_signing_key': sender.key,
            'as4_signing_cert_chain': sender.certificate,
            'as4_decryption_key': sender.key,
            'as4_peer_signing_cert': receiver.certificate,
            'as4_peer_encryption_cert': receiver.certificate,
            'as4_trust_anchors': receiver.certificate,

            # More
            'as4_original_sender': '0192:991825827',
            'as4_final_recipient': '0192:810418052',
            'as4_extra_pmodes': 'urn:extra:service|ExtraAction',
        })

        # .. reload the page so the table is rebuilt from what the server persisted ..
        open_as4_outconn_page(page, base_url, query=name)
        _ = wait_for_as4_outconn_row(page, name)

        # .. open the edit dialog and verify every value came back ..
        open_edit_dialog(page, outconn_id)

        assert page.input_value('#id_edit-name') == name
        assert page.input_value('#id_edit-as4_profile') == 'peppol'
        assert page.input_value('#id_edit-as4_from_party') == 'my-access-point'
        assert page.input_value('#id_edit-as4_to_party') == 'peer-access-point'
        assert page.input_value('#id_edit-as4_service') == 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0'
        assert page.input_value('#id_edit-as4_action') == 'busdox-docid-qns::invoice'
        assert page.input_value('#id_edit-as4_agreement') == 'urn:fdc:peppol.eu:2017:agreements:tia:ap_provider'

        assert page.input_value('#id_edit-host') == 'https://ap.example.com:8443'
        assert page.input_value('#id_edit-url_path') == '/as4'
        assert page.is_checked('#id_edit-as4_use_discovery')
        assert page.input_value('#id_edit-as4_sml_domain') == 'acc.edelivery.tech.ec.europa.eu'
        assert page.input_value('#id_edit-as4_mpc') == 'urn:test:mpc'
        assert page.input_value('#id_edit-timeout') == '20'
        assert page.input_value('#id_edit-validate_tls') == 'False'

        # The private keys are stored encrypted, so the dialog shows the encrypted
        # form rather than the pasted plain text ..
        assert page.input_value('#id_edit-as4_signing_key').startswith(SECRETS.PREFIX)
        assert page.input_value('#id_edit-as4_decryption_key').startswith(SECRETS.PREFIX)

        # .. while the public certificates round-trip verbatim.
        assert page.input_value('#id_edit-as4_signing_cert_chain').strip() == sender.certificate.strip()
        assert page.input_value('#id_edit-as4_peer_signing_cert').strip() == receiver.certificate.strip()
        assert page.input_value('#id_edit-as4_peer_encryption_cert').strip() == receiver.certificate.strip()
        assert page.input_value('#id_edit-as4_trust_anchors').strip() == receiver.certificate.strip()

        assert page.input_value('#id_edit-as4_original_sender') == '0192:991825827'
        assert page.input_value('#id_edit-as4_final_recipient') == '0192:810418052'
        assert page.input_value('#id_edit-as4_extra_pmodes') == 'urn:extra:service|ExtraAction'

        # .. now edit fields from several tabs at once ..
        edited_name = name + '-edited'
        edit_as4_outconn(page, outconn_id, {
            'name': edited_name,
            'as4_profile': 'ics2',
            'as4_to_party': 'sti-taxud',
            'as4_use_discovery': False,
            'as4_sml_domain': '',
            'as4_final_recipient': '',
        })
        _ = wait_for_as4_outconn_row(page, edited_name)

        # .. reload again and verify the changes round-tripped through the server ..
        open_as4_outconn_page(page, base_url, query=edited_name)
        _ = wait_for_as4_outconn_row(page, edited_name)
        open_edit_dialog(page, outconn_id)

        assert page.input_value('#id_edit-name') == edited_name
        assert page.input_value('#id_edit-as4_profile') == 'ics2'
        assert page.input_value('#id_edit-as4_to_party') == 'sti-taxud'
        assert not page.is_checked('#id_edit-as4_use_discovery')
        assert page.input_value('#id_edit-as4_sml_domain') == ''
        assert page.input_value('#id_edit-as4_final_recipient') == ''

        # The fields the edit did not touch are still there ..
        assert page.input_value('#id_edit-as4_from_party') == 'my-access-point'
        assert page.input_value('#id_edit-as4_mpc') == 'urn:test:mpc'
        assert page.input_value('#id_edit-as4_signing_cert_chain').strip() == sender.certificate.strip()

        # .. and the encrypted keys survived the edit unchanged in kind.
        assert page.input_value('#id_edit-as4_signing_key').startswith(SECRETS.PREFIX)

        # .. close the dialog ..
        close_dialog_via_jquery(page, 'edit-div')

        # .. delete and verify the row is gone ..
        delete_as4_outconn(page, outconn_id)
        assert find_as4_outconn_row(page, edited_name) is None

        # .. and one more reload to confirm the server no longer knows the connection.
        open_as4_outconn_page(page, base_url, query=edited_name)
        assert find_as4_outconn_row(page, edited_name) is None

# ################################################################################################################################

    def test_certificate_expiry_is_shown_after_save(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The connections table shows the expiry date parsed out of the pasted
        signing certificate chain.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'expiry'
        sender, _ = new_test_parties()

        outconn_id = create_as4_outconn(page, base_url, name, 'https://ap.example.com', {
            'as4_profile': 'edelivery1',
            'as4_signing_key': sender.key,
            'as4_signing_cert_chain': sender.certificate,
        })

        # Reload so the table is rebuilt from the server, which computes the expiry.
        open_as4_outconn_page(page, base_url, query=name)
        row = wait_for_as4_outconn_row(page, name)

        # The throwaway certificate is valid for a year, so its expiry year appears in the row.
        row_text = row.text_content()
        assert '20' in row_text, f'Expected an expiry date in the row, got: {row_text}'

        cells = row.query_selector_all('td')
        cell_texts = [cell.text_content().strip() for cell in cells]
        assert any(text.count('-') == 2 for text in cell_texts), \
            f'Expected an ISO expiry date in one of the cells, got: {cell_texts}'

        delete_as4_outconn(page, outconn_id)

# ################################################################################################################################
# ################################################################################################################################
