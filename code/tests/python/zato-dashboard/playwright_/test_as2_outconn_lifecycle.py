# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import close_dialog_via_jquery
from as2_outconn import create_as2_outconn, delete_as2_outconn, edit_as2_outconn, find_as2_outconn_row, \
    open_as2_outconn_page, open_edit_dialog, wait_for_as2_outconn_row
from as4_keys import new_test_parties

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.as2.out.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

class TestAS2OutconnLifecycle:
    """ Outgoing AS2 connection lifecycle across every tab - Main, EDI, Security,
    Partner, Keys, Delivery and More. Everything runs through the browser and every
    value is verified by reloading the page, so the table is rebuilt from the server,
    and reading the edit dialog.
    """

# ################################################################################################################################

    def test_full_lifecycle_across_all_tabs(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'tabs'
        sender, receiver = new_test_parties()

        # Create a connection touching every tab of the dialog ..
        outconn_id = create_as2_outconn(page, base_url, name, 'https://as2.example.com/exchange', {

            # Main
            'as2_from': 'ZatoRetail',
            'as2_to': 'PartnerCorp',
            'subject': 'Purchase orders',

            # EDI
            'isa_qualifier': 'ZZ',
            'isa_id': 'ZATORETAIL',
            'gs_id': 'ZATORETAIL',
            'unb_id': 'ZATORETAIL:14',
            'content_type': 'application/edifact',
            'inbound_topic': 'orders.inbound',
            'inbound_service': 'orders.process',

            # Security
            'sign_algorithm': 'sha-384',
            'encryption_algorithm': 'aes-128-cbc',
            'compress': True,
            'compress_before_signing': False,
            'mdn_mode': 'async',
            'async_mdn_url': 'https://zato.example.com/zato/as2/mdn',

            # Certificates
            'as2_partner_cert': receiver.certificate,
            'as2_partner_next_cert': receiver.certificate,
            'as2_partner_next_cert_from': '2099-01-01',
            'as2_signing_key': sender.key,
            'as2_signing_cert_chain': sender.certificate,
            'as2_decryption_key': sender.key,
            'as2_next_decryption_key': sender.key,
            'as2_next_decryption_cert': sender.certificate,
            'as2_peer_signing_cert': receiver.certificate,
            'as2_peer_encryption_cert': receiver.certificate,
            'as2_trust_anchors': receiver.certificate,

            # Delivery
            'verify_tls': False,
            'username': 'as2-basic-user',
            'http_timeout_seconds': '30',
            'http_transfer_mode': 'threshold',
            'chunked_threshold_bytes': '5242880',
            'preserve_filename': True,
            'ack_overdue_after': '7200',
            'resend_max_retries': '3',

            # More
            'as2_version': '1.1',
            'content_transfer_encoding': 'base64',
            'force_base64': True,
            'prevent_canonicalization': True,
            'warn_on_duplicate_filename': True,
            'pool_size': '2',
        })

        # .. reload the page so the table is rebuilt from what the server persisted ..
        open_as2_outconn_page(page, base_url, query=name)
        _ = wait_for_as2_outconn_row(page, name)

        # .. open the edit dialog and verify every value came back ..
        open_edit_dialog(page, outconn_id)

        assert page.input_value('#id_edit-name') == name
        assert page.input_value('#id_edit-endpoint_url') == 'https://as2.example.com/exchange'
        assert page.input_value('#id_edit-as2_from') == 'ZatoRetail'
        assert page.input_value('#id_edit-as2_to') == 'PartnerCorp'
        assert page.input_value('#id_edit-subject') == 'Purchase orders'

        assert page.input_value('#id_edit-isa_qualifier') == 'ZZ'
        assert page.input_value('#id_edit-isa_id') == 'ZATORETAIL'
        assert page.input_value('#id_edit-gs_id') == 'ZATORETAIL'
        assert page.input_value('#id_edit-unb_id') == 'ZATORETAIL:14'
        assert page.input_value('#id_edit-content_type') == 'application/edifact'
        assert page.input_value('#id_edit-inbound_topic') == 'orders.inbound'
        assert page.input_value('#id_edit-inbound_service') == 'orders.process'

        assert page.is_checked('#id_edit-sign')
        assert page.input_value('#id_edit-sign_algorithm') == 'sha-384'
        assert page.is_checked('#id_edit-encrypt')
        assert page.input_value('#id_edit-encryption_algorithm') == 'aes-128-cbc'
        assert page.is_checked('#id_edit-compress')
        assert not page.is_checked('#id_edit-compress_before_signing')
        assert page.input_value('#id_edit-mdn_mode') == 'async'
        assert page.is_checked('#id_edit-mdn_signed')
        assert page.input_value('#id_edit-async_mdn_url') == 'https://zato.example.com/zato/as2/mdn'

        # The private keys never come back to the page, so the dialog shows them empty -
        # leaving them empty on an edit keeps the stored keys ..
        assert page.input_value('#id_edit-as2_signing_key') == ''
        assert page.input_value('#id_edit-as2_decryption_key') == ''
        assert page.input_value('#id_edit-as2_next_decryption_key') == ''

        # .. while the certificates round-trip verbatim.
        assert page.input_value('#id_edit-as2_partner_cert').strip() == receiver.certificate.strip()
        assert page.input_value('#id_edit-as2_partner_next_cert').strip() == receiver.certificate.strip()
        assert page.input_value('#id_edit-as2_partner_next_cert_from') == '2099-01-01'
        assert page.input_value('#id_edit-as2_signing_cert_chain').strip() == sender.certificate.strip()
        assert page.input_value('#id_edit-as2_next_decryption_cert').strip() == sender.certificate.strip()
        assert page.input_value('#id_edit-as2_peer_signing_cert').strip() == receiver.certificate.strip()
        assert page.input_value('#id_edit-as2_peer_encryption_cert').strip() == receiver.certificate.strip()
        assert page.input_value('#id_edit-as2_trust_anchors').strip() == receiver.certificate.strip()

        assert not page.is_checked('#id_edit-verify_tls')
        assert page.input_value('#id_edit-username') == 'as2-basic-user'
        assert page.input_value('#id_edit-http_timeout_seconds') == '30'
        assert page.input_value('#id_edit-http_transfer_mode') == 'threshold'
        assert page.input_value('#id_edit-chunked_threshold_bytes') == '5242880'
        assert page.is_checked('#id_edit-preserve_filename')
        assert page.input_value('#id_edit-ack_overdue_after') == '7200'
        assert page.input_value('#id_edit-resend_max_retries') == '3'

        assert page.input_value('#id_edit-as2_version') == '1.1'
        assert page.input_value('#id_edit-content_transfer_encoding') == 'base64'
        assert page.is_checked('#id_edit-force_base64')
        assert page.is_checked('#id_edit-prevent_canonicalization')
        assert page.is_checked('#id_edit-warn_on_duplicate_filename')
        assert page.input_value('#id_edit-pool_size') == '2'

        # .. now edit fields from several tabs at once ..
        edited_name = name + '-edited'
        edit_as2_outconn(page, outconn_id, {
            'name': edited_name,
            'as2_to': 'PartnerCorpEU',
            'gs_id': 'ZATOEU',
            'sign_algorithm': 'sha-256',
            'mdn_mode': 'sync',
            'async_mdn_url': '',
            'compress': False,
            'verify_tls': True,
            'ack_overdue_after': '3600',
        })
        _ = wait_for_as2_outconn_row(page, edited_name)

        # .. reload again and verify the changes round-tripped through the server ..
        open_as2_outconn_page(page, base_url, query=edited_name)
        _ = wait_for_as2_outconn_row(page, edited_name)
        open_edit_dialog(page, outconn_id)

        assert page.input_value('#id_edit-name') == edited_name
        assert page.input_value('#id_edit-as2_to') == 'PartnerCorpEU'
        assert page.input_value('#id_edit-gs_id') == 'ZATOEU'
        assert page.input_value('#id_edit-sign_algorithm') == 'sha-256'
        assert page.input_value('#id_edit-mdn_mode') == 'sync'
        assert page.input_value('#id_edit-async_mdn_url') == ''
        assert not page.is_checked('#id_edit-compress')
        assert page.is_checked('#id_edit-verify_tls')
        assert page.input_value('#id_edit-ack_overdue_after') == '3600'

        # The fields the edit did not touch are still there ..
        assert page.input_value('#id_edit-as2_from') == 'ZatoRetail'
        assert page.input_value('#id_edit-isa_id') == 'ZATORETAIL'
        assert page.input_value('#id_edit-username') == 'as2-basic-user'
        assert page.input_value('#id_edit-as2_partner_cert').strip() == receiver.certificate.strip()

        # .. and the private keys are still never shown, while the edit
        # with the key fields left empty kept the stored ones.
        assert page.input_value('#id_edit-as2_signing_key') == ''

        # .. close the dialog ..
        close_dialog_via_jquery(page, 'edit-div')

        # .. delete and verify the row is gone ..
        delete_as2_outconn(page, outconn_id)
        assert find_as2_outconn_row(page, edited_name) is None

        # .. and one more reload to confirm the server no longer knows the connection.
        open_as2_outconn_page(page, base_url, query=edited_name)
        assert find_as2_outconn_row(page, edited_name) is None

# ################################################################################################################################

    def test_minimal_create_uses_the_form_defaults(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A connection created with just the identities and key material keeps
        the defaults of every other field.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'defaults'
        sender, receiver = new_test_parties()

        outconn_id = create_as2_outconn(page, base_url, name, 'https://as2.example.com/exchange', {
            'as2_from': 'ZatoRetail',
            'as2_to': 'PartnerCorp',
            'as2_partner_cert': receiver.certificate,
            'as2_signing_key': sender.key,
            'as2_signing_cert_chain': sender.certificate,
            'as2_decryption_key': sender.key,
        })

        # Reload so the table is rebuilt from what the server persisted.
        open_as2_outconn_page(page, base_url, query=name)
        _ = wait_for_as2_outconn_row(page, name)
        open_edit_dialog(page, outconn_id)

        # The security defaults are the standard retail mandate - signed,
        # encrypted, uncompressed, with a signed synchronous MDN ..
        assert page.is_checked('#id_edit-sign')
        assert page.input_value('#id_edit-sign_algorithm') == 'sha-256'
        assert page.is_checked('#id_edit-encrypt')
        assert page.input_value('#id_edit-encryption_algorithm') == 'aes-256-cbc'
        assert not page.is_checked('#id_edit-compress')
        assert page.input_value('#id_edit-mdn_mode') == 'sync'
        assert page.is_checked('#id_edit-mdn_signed')

        # .. TLS verification is on and the numeric fields keep their zero defaults ..
        assert page.is_checked('#id_edit-verify_tls')
        assert page.input_value('#id_edit-http_timeout_seconds') == '0'
        assert page.input_value('#id_edit-ack_overdue_after') == '0'

        # .. and the escape hatches are all off.
        assert not page.is_checked('#id_edit-force_base64')
        assert not page.is_checked('#id_edit-prevent_canonicalization')
        assert not page.is_checked('#id_edit-warn_on_duplicate_filename')

        close_dialog_via_jquery(page, 'edit-div')
        delete_as2_outconn(page, outconn_id)

# ################################################################################################################################
# ################################################################################################################################
