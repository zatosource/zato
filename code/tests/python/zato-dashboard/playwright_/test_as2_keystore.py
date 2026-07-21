# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from as4_keys import new_party

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict
    from client import ZatoClient

# ################################################################################################################################
# ################################################################################################################################

_Keystore_Page_Url = '/zato/as2/keystore/?cluster=1'

# A certificate this many days from expiry triggers the red warning on the page.
_Short_Validity_Days = 10

# The services the page talks to
_Service_Get  = 'zato.channel.as2.keystore.get'
_Service_Edit = 'zato.channel.as2.keystore.edit'

# ################################################################################################################################
# ################################################################################################################################

def _open_keystore_page(page:'Page', base_url:'str') -> 'None':
    """ Navigates to the keystore page and waits for its form.
    """
    _ = page.goto(f'{base_url}{_Keystore_Page_Url}')
    page.wait_for_selector('#keystore-form', state='visible')

# ################################################################################################################################

def _save_keystore_form(page:'Page') -> 'None':
    """ Submits the keystore form and waits for the success message.
    """

    # An earlier save may have left the message showing - hide it so the wait below
    # only passes once this save's response has arrived.
    _ = page.evaluate("$('#user-message-div').hide()")

    page.click('#keystore-form input[type="submit"]')
    page.wait_for_selector('#user-message-div', state='visible')

    message = page.text_content('#user-message')
    assert 'Keystore saved' in message

# ################################################################################################################################
# ################################################################################################################################

class TestAS2Keystore:
    """ The Dashboard page holding our own AS2 keystore - the signing pair, the current
    decryption key and the next decryption pair staged for rotation - all stored
    on the inbound AS2 channel, with private keys encrypted at rest.
    """

# ################################################################################################################################

    def test_keystore_page_round_trip(
        self, logged_in_page:'Page', zato_dashboard:'anydict', api_client:'ZatoClient') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # A soon-to-expire signing certificate exercises the red expiry warning
        # while the next decryption pair uses a long-lived one.
        signing_party = new_party('as2-keystore-signing', _Short_Validity_Days)
        next_party = new_party('as2-keystore-next')

        # Fill in the whole form ..
        _open_keystore_page(page, base_url)

        page.fill('#id_as2_signing_key', signing_party.key)
        page.fill('#id_as2_signing_cert_chain', signing_party.certificate)
        page.fill('#id_as2_decryption_key', signing_party.key)
        page.fill('#id_as2_next_decryption_key', next_party.key)
        page.fill('#id_as2_next_decryption_cert', next_party.certificate)

        # .. and save it.
        _save_keystore_form(page)

        # Reload so the page is rebuilt from what the server now has stored ..
        _open_keystore_page(page, base_url)

        # .. the private keys never come back to the page - the textareas are empty
        # .. and the hints say a key is stored ..
        assert page.input_value('#id_as2_signing_key') == ''
        assert page.input_value('#id_as2_decryption_key') == ''
        assert page.input_value('#id_as2_next_decryption_key') == ''

        assert 'A key is stored' in page.text_content('#signing-key-hint')
        assert 'A key is stored' in page.text_content('#decryption-key-hint')
        assert 'A key is stored' in page.text_content('#next-key-hint')

        # .. the certificates are stored as pasted ..
        assert page.input_value('#id_as2_signing_cert_chain').strip() == signing_party.certificate.strip()
        assert page.input_value('#id_as2_next_decryption_cert').strip() == next_party.certificate.strip()

        # .. the soon-to-expire signing certificate is shown with the red warning ..
        signing_expiry_class = page.get_attribute('#signing-expiry', 'class')
        assert 'cert-expiry-warning' in signing_expiry_class

        signing_expiry_text = page.text_content('#signing-expiry')
        assert 'days left' in signing_expiry_text

        # .. while the long-lived next certificate is not.
        next_expiry_class = page.get_attribute('#next-cert-expiry', 'class')
        assert 'cert-expiry-warning' not in next_expiry_class

        # The backend view of the keystore matches what the page shows - the keys are
        # reported only as flags and the browser submits textareas with CRLF line endings,
        # so the stored certificate is compared with those normalized away.
        stored = api_client.invoke(_Service_Get)

        stored_cert_chain = stored['as2_signing_cert_chain'].replace('\r\n', '\n')

        assert stored['has_as2_signing_key'] is True
        assert stored['has_as2_decryption_key'] is True
        assert stored['has_as2_next_decryption_key'] is True
        assert stored_cert_chain.strip() == signing_party.certificate.strip()

        # A save with the key fields left empty keeps the stored keys in place ..
        page.fill('#id_as2_signing_cert_chain', signing_party.certificate)
        _save_keystore_form(page)

        stored = api_client.invoke(_Service_Get)
        assert stored['has_as2_signing_key'] is True
        assert stored['has_as2_decryption_key'] is True

        # .. and clearing the next decryption certificate removes the staged key with it,
        # which is how a completed rotation is wrapped up ..
        _open_keystore_page(page, base_url)
        page.fill('#id_as2_next_decryption_cert', '')

        _save_keystore_form(page)

        # .. after which the page no longer shows the pair at all.
        _open_keystore_page(page, base_url)

        assert page.input_value('#id_as2_next_decryption_key') == ''
        assert page.input_value('#id_as2_next_decryption_cert') == ''
        assert 'No key is stored yet' in page.text_content('#next-key-hint')
        assert page.text_content('#next-cert-expiry').strip() == '---'

# ################################################################################################################################
# ################################################################################################################################
