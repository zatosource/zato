# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import close_dialog_via_jquery
from rest_channel import delete_channel, find_channel_row, open_edit_dialog
from soap_channel import create_soap_channel, edit_soap_channel, open_soap_channel_page

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.soap.channel.' + CryptoManager.generate_hex_string(32) + '.'

# A service that is always deployed, so the lifecycle needs no hot deployment
_Echo_Service = 'demo.echo'

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPChannelLifecycle:
    """ SOAP channel lifecycle across every field of the dialog - the SOAP action,
    both SOAP versions and the MTOM toggle. Everything runs through the browser
    and every value is verified by reloading the page, so the table is rebuilt
    from the server, and reading the edit dialog.
    """

# ################################################################################################################################

    def test_full_lifecycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'fields'
        url_path = '/' + name

        # Create a channel touching every SOAP-only field of the dialog ..
        channel_id = create_soap_channel(page, base_url, name, _Echo_Service, url_path, {
            'soap_action': 'urn:example:submit',
            'soap_version': '1.2',
            'use_mtom': True,
        })

        # .. reload the page so the table is rebuilt from what the server persisted ..
        open_soap_channel_page(page, base_url, query=name)

        # .. open the edit dialog and verify every value came back ..
        open_edit_dialog(page, channel_id)

        assert page.input_value('#id_edit-name') == name
        assert page.input_value('#id_edit-url_path') == url_path
        assert page.input_value('#id_edit-service') == _Echo_Service
        assert page.input_value('#id_edit-soap_action') == 'urn:example:submit'
        assert page.input_value('#id_edit-soap_version') == '1.2'
        assert page.is_checked('#id_edit-use_mtom')

        # .. close the dialog before editing through the helper ..
        close_dialog_via_jquery(page, 'edit-div')

        # .. now edit the SOAP fields ..
        edited_name = name + '-edited'
        edit_soap_channel(page, channel_id, {
            'name': edited_name,
            'soap_action': 'urn:example:submit-edited',
            'soap_version': '1.1',
            'use_mtom': False,
        })

        # .. reload again and verify the changes round-tripped through the server ..
        open_soap_channel_page(page, base_url, query=edited_name)
        open_edit_dialog(page, channel_id)

        assert page.input_value('#id_edit-name') == edited_name
        assert page.input_value('#id_edit-url_path') == url_path
        assert page.input_value('#id_edit-soap_action') == 'urn:example:submit-edited'
        assert page.input_value('#id_edit-soap_version') == '1.1'
        assert not page.is_checked('#id_edit-use_mtom')

        # .. close the dialog ..
        close_dialog_via_jquery(page, 'edit-div')

        # .. delete and verify the row is gone ..
        delete_channel(page, channel_id)
        assert find_channel_row(page, edited_name) is None

        # .. and one more reload to confirm the server no longer knows the channel.
        open_soap_channel_page(page, base_url, query=edited_name)
        assert find_channel_row(page, edited_name) is None

# ################################################################################################################################

    def test_soap_version_12_is_available(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The SOAP version select of the channel dialog offers both 1.1 and 1.2.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Open the create dialog on the SOAP channels page ..
        open_soap_channel_page(page, base_url)
        page.evaluate('$.fn.zato.http_soap.create("SOAP channel")')
        _ = page.wait_for_selector('#create-div', state='visible', timeout=5000)

        # .. and read the version select's options.
        versions = page.eval_on_selector_all(
            '#id_soap_version option', 'elements => elements.map(element => element.value)')

        assert versions == ['1.1', '1.2'], f'Expected both SOAP versions, got: {versions}'

        close_dialog_via_jquery(page, 'create-div')

# ################################################################################################################################
# ################################################################################################################################
