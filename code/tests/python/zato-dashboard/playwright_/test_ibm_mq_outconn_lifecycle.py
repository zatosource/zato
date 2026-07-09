# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import close_dialog_via_jquery, open_create_dialog
from ibm_mq_outconn import create_ibm_mq_outconn, delete_ibm_mq_outconn, edit_ibm_mq_outconn, find_ibm_mq_outconn_row, \
    open_edit_dialog, open_ibm_mq_outconn_page, wait_for_ibm_mq_outconn_row

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.ibm-mq.out.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

class TestIBMMQOutconnLifecycle:
    """ Outgoing IBM MQ connection lifecycle across both tabs - Basic and Security -
    plus the how-it-works hints. Everything runs through the browser and every value
    is verified by reloading the page, so the table is rebuilt from the server,
    and reading the edit dialog.
    """

# ################################################################################################################################

    def test_full_lifecycle_across_all_tabs(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'tabs'

        # Create a connection touching both tabs of the dialog ..
        outconn_id = create_ibm_mq_outconn(page, base_url, name, {

            # Basic
            'address': 'localhost:21414',
            'queue_manager': 'QM1',
            'mq_channel_name': 'DEV.APP.SVRCONN',
            'queue': 'DEV.QUEUE.1',

            # Security
            'username': 'app',
            'ssl': True,
            'cipher_spec': 'ANY_TLS12_OR_HIGHER',
            'ssl_ca_file': '/opt/certs/ca.pem',
            'ssl_cert_file': '/opt/certs/client-cert.pem',
            'ssl_key_file': '/opt/certs/client-key.pem',
        })

        # .. reload the page so the table is rebuilt from what the server persisted ..
        open_ibm_mq_outconn_page(page, base_url, query=name)
        _ = wait_for_ibm_mq_outconn_row(page, name)

        # .. open the edit dialog and verify every value came back ..
        open_edit_dialog(page, outconn_id)

        assert page.input_value('#id_edit-name') == name
        assert page.input_value('#id_edit-address') == 'localhost:21414'
        assert page.input_value('#id_edit-queue_manager') == 'QM1'
        assert page.input_value('#id_edit-mq_channel_name') == 'DEV.APP.SVRCONN'
        assert page.input_value('#id_edit-queue') == 'DEV.QUEUE.1'

        assert page.input_value('#id_edit-username') == 'app'
        assert page.is_checked('#id_edit-ssl')
        assert page.input_value('#id_edit-cipher_spec') == 'ANY_TLS12_OR_HIGHER'
        assert page.input_value('#id_edit-ssl_ca_file') == '/opt/certs/ca.pem'
        assert page.input_value('#id_edit-ssl_cert_file') == '/opt/certs/client-cert.pem'
        assert page.input_value('#id_edit-ssl_key_file') == '/opt/certs/client-key.pem'

        # .. close the dialog before editing through the helper, which reopens it ..
        close_dialog_via_jquery(page, 'edit-div')

        # .. now edit fields from both tabs at once ..
        edited_name = name + '-edited'
        edit_ibm_mq_outconn(page, outconn_id, {
            'name': edited_name,
            'queue': 'DEV.QUEUE.2',
            'ssl': False,
            'ssl_key_file': '',
        })
        _ = wait_for_ibm_mq_outconn_row(page, edited_name)

        # .. reload again and verify the changes round-tripped through the server ..
        open_ibm_mq_outconn_page(page, base_url, query=edited_name)
        _ = wait_for_ibm_mq_outconn_row(page, edited_name)
        open_edit_dialog(page, outconn_id)

        assert page.input_value('#id_edit-name') == edited_name
        assert page.input_value('#id_edit-queue') == 'DEV.QUEUE.2'
        assert not page.is_checked('#id_edit-ssl')
        assert page.input_value('#id_edit-ssl_ca_file') == '/opt/certs/ca.pem'
        assert page.input_value('#id_edit-ssl_key_file') == ''

        # .. close the dialog ..
        close_dialog_via_jquery(page, 'edit-div')

        # .. delete and verify the row is gone ..
        delete_ibm_mq_outconn(page, outconn_id)
        assert find_ibm_mq_outconn_row(page, edited_name) is None

        # .. and one more reload to confirm the server no longer knows the connection.
        open_ibm_mq_outconn_page(page, base_url, query=edited_name)
        assert find_ibm_mq_outconn_row(page, edited_name) is None

# ################################################################################################################################

    def test_how_it_works_hints_render(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The create dialog shows the how-it-works badge and clicking it turns the help mode on,
        attaching hints to the form fields.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Open the create dialog ..
        open_ibm_mq_outconn_page(page, base_url)
        open_create_dialog(page)

        # .. the badge is there ..
        badge = page.wait_for_selector('#create-how-it-works', state='visible', timeout=5000)
        assert badge.text_content().strip() == 'How does it work?'

        # .. clicking it enters the help mode ..
        badge.click()
        _ = page.wait_for_selector('#create-how-it-works.how-it-works-active', state='attached', timeout=5000)

        # .. which shows the hint for the first field right away.
        tooltip = page.wait_for_selector('.tippy-box', state='visible', timeout=5000)
        assert 'A unique name' in tooltip.text_content()

        # Leave the help mode and close the dialog.
        page.click('#create-how-it-works')
        _ = page.wait_for_selector('#create-how-it-works:not(.how-it-works-active)', state='attached', timeout=5000)
        close_dialog_via_jquery(page, 'create-div')

# ################################################################################################################################
# ################################################################################################################################
