# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# cryptography
from cryptography.x509 import load_pem_x509_certificate

# Zato
from zato.common.crypto.api import CryptoManager
from as2_outconn import create_as2_outconn, delete_as2_outconn, find_as2_outconn_row, open_as2_outconn_page, \
    wait_for_as2_outconn_row
from as4_keys import new_party

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.as2.expiry.' + CryptoManager.generate_hex_string(32) + '.'

# A certificate this many days from expiry triggers the red warning in the list.
_Short_Validity_Days = 10

# A certificate this many days from expiry does not.
_Long_Validity_Days = 365

# ################################################################################################################################
# ################################################################################################################################

def _expiry_date_of(certificate_pem:'str') -> 'str':
    """ The not-after date of a PEM certificate, formatted the way the list page shows it.
    """
    certificate = load_pem_x509_certificate(certificate_pem.encode('utf8'))

    out = certificate.not_valid_after_utc.strftime('%Y-%m-%d')
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAS2CertExpiry:
    """ The certificate expiry column of the outgoing AS2 connections list -
    each partner certificate's not-after date is parsed server-side and shown
    in the table, red when the certificate is about to expire.
    """

# ################################################################################################################################

    def test_expiry_column(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        expiring_name = _Test_Name_Prefix + 'expiring'
        current_name = _Test_Name_Prefix + 'current'
        no_cert_name = _Test_Name_Prefix + 'no-cert'

        sender = new_party('as2-expiry-sender')
        expiring_party = new_party('as2-expiring-partner', _Short_Validity_Days)
        current_party = new_party('as2-current-partner', _Long_Validity_Days)

        # The dates the page is expected to show, read off the certificates themselves.
        expiring_date = _expiry_date_of(expiring_party.certificate)
        current_date = _expiry_date_of(current_party.certificate)

        # Our own key material, shared by all three connections.
        key_material = {
            'as2_signing_key': sender.key,
            'as2_signing_cert_chain': sender.certificate,
            'as2_decryption_key': sender.key,
        }

        # One connection with a certificate about to expire ..
        expiring_options = {
            'as2_from': 'ZatoRetail',
            'as2_to': 'PartnerCorp',
            'as2_partner_cert': expiring_party.certificate,
        }
        expiring_options.update(key_material)
        expiring_id = create_as2_outconn(page, base_url, expiring_name, 'https://as2.example.com/exchange',
            expiring_options)

        # .. one with a long-lived certificate ..
        current_options = {
            'as2_from': 'ZatoRetail',
            'as2_to': 'PartnerCorpEU',
            'as2_partner_cert': current_party.certificate,
        }
        current_options.update(key_material)
        current_id = create_as2_outconn(page, base_url, current_name, 'https://as2.example.com/exchange',
            current_options)

        # .. and one without any partner certificate at all.
        no_cert_options = {
            'as2_from': 'ZatoRetail',
            'as2_to': 'PartnerCorpUS',
        }
        no_cert_options.update(key_material)
        no_cert_id = create_as2_outconn(page, base_url, no_cert_name, 'https://as2.example.com/exchange',
            no_cert_options)

        try:

            # Reload so the table is rebuilt from what the server persisted,
            # with the expiry computed server-side per row.
            open_as2_outconn_page(page, base_url, query=_Test_Name_Prefix)
            _ = wait_for_as2_outconn_row(page, expiring_name)
            _ = wait_for_as2_outconn_row(page, current_name)
            _ = wait_for_as2_outconn_row(page, no_cert_name)

            # The expiring certificate shows its date with the red warning ..
            expiring_row = find_as2_outconn_row(page, expiring_name)
            expiring_cell = expiring_row.query_selector('span.cert-expiry')

            assert expiring_cell.text_content() == expiring_date
            assert 'cert-expiry-warning' in expiring_cell.get_attribute('class')

            # .. the long-lived one shows its date without the warning ..
            current_row = find_as2_outconn_row(page, current_name)
            current_cell = current_row.query_selector('span.cert-expiry')

            assert current_cell.text_content() == current_date
            assert 'cert-expiry-warning' not in current_cell.get_attribute('class')

            # .. and the one without a certificate shows a placeholder.
            no_cert_row = find_as2_outconn_row(page, no_cert_name)
            assert no_cert_row.query_selector('span.cert-expiry') is None

            no_cert_hint = no_cert_row.query_selector('span.form_hint')
            assert no_cert_hint.text_content() == '---'

        finally:
            delete_as2_outconn(page, expiring_id)
            delete_as2_outconn(page, current_id)
            delete_as2_outconn(page, no_cert_id)

# ################################################################################################################################
# ################################################################################################################################
