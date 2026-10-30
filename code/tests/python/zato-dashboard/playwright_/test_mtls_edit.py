# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/security/mtls/'

_Test_Name_Prefix = 'test.mtls.edit.' + CryptoManager.generate_hex_string(32) + '.'

# The fields that a channel reads and those that an outgoing connection reads, by the tab that each set is on
_Channel_Field_Names  = ('client_cert_fingerprint', 'client_cert_subject_dn')
_Outgoing_Field_Names = ('cert_path', 'key_path', 'ca_certs_path')

# ################################################################################################################################
# ################################################################################################################################

def _select_tab(page:'Page', div_id:'str', tab_name:'str') -> 'None':
    page.click(f'{div_id} .dashboard-tab[data-tab="{tab_name}"]')

# ################################################################################################################################

def _create_definition(page:'Page', suffix:'str') -> 'dict':
    """ Creates an mTLS definition via the UI and returns its details.
    """

    name = _Test_Name_Prefix + suffix
    cert_path = f'/opt/hot-deploy/ssl/{name}-cert.pem'
    key_path = f'/opt/hot-deploy/ssl/{name}-key.pem'
    ca_certs_path = f'/opt/hot-deploy/ssl/{name}-ca.pem'
    fingerprint = CryptoManager.generate_hex_string(32)
    subject_dn = f'CN={name},O=Test,C=US'

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    _ = page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields on both tabs ..
    page.fill('#id_name', name)

    _select_tab(page, '#create-div', 'channels')
    page.fill('#id_client_cert_fingerprint', fingerprint)
    page.fill('#id_client_cert_subject_dn', subject_dn)

    _select_tab(page, '#create-div', 'outgoing')
    page.fill('#id_cert_path', cert_path)
    page.fill('#id_key_path', key_path)
    page.fill('#id_ca_certs_path', ca_certs_path)

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    _ = page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    _ = page.wait_for_selector(row_selector, state='visible', timeout=5000)

    out = {
        'name': name,
        'cert_path': cert_path,
        'key_path': key_path,
        'ca_certs_path': ca_certs_path,
        'client_cert_fingerprint': fingerprint,
        'client_cert_subject_dn': subject_dn,
    }

    return out

# ################################################################################################################################

def _click_edit_for_row(page:'Page', name:'str') -> 'None':
    """ Finds the row with the given name and opens its edit dialog.
    """

    # Extract the row's item ID from the hidden td ..
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    row = cast_('any_', page.query_selector(row_selector))
    id_cell = row.query_selector('td[class*="item_id_"]')
    item_id = id_cell.inner_text().strip()

    # .. call the edit function directly via JS ..
    page.evaluate(f'$.fn.zato.security.mtls.edit("{item_id}")')
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################

class TestMTLSEdit:
    """ Tests for the mTLS edit flow.
    """

    def test_06_edit_form_is_prepopulated(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition, opens its edit dialog and verifies
        that all form fields hold the values the definition was created with.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, 'prepopulated')

        # .. open the edit dialog ..
        _click_edit_for_row(page, defn['name'])

        # .. verify each field holds the created value.
        field_map = {
            '#id_edit-name': defn['name'],
            '#id_edit-cert_path': defn['cert_path'],
            '#id_edit-key_path': defn['key_path'],
            '#id_edit-ca_certs_path': defn['ca_certs_path'],
            '#id_edit-client_cert_fingerprint': defn['client_cert_fingerprint'],
            '#id_edit-client_cert_subject_dn': defn['client_cert_subject_dn'],
        }

        for field_id, expected in field_map.items():
            field_value = page.input_value(field_id)
            assert field_value == expected, f'Expected "{expected}" in {field_id}, got: "{field_value}"'

# ################################################################################################################################

    def test_07_edit_changes_are_saved(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition, edits its name and certificate details,
        and verifies the row reflects the new values.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, 'save-changes')

        # .. open the edit dialog ..
        _click_edit_for_row(page, defn['name'])

        # .. change the name and certificate path ..
        edited_name = defn['name'] + '-edited'
        edited_cert_path = defn['cert_path'] + '.edited'

        page.fill('#id_edit-name', '')
        page.fill('#id_edit-name', edited_name)

        _select_tab(page, '#edit-div', 'outgoing')
        page.fill('#id_edit-cert_path', '')
        page.fill('#id_edit-cert_path', edited_cert_path)

        # .. submit and wait for the dialog to close ..
        page.click('#edit-div input[type="submit"]')
        _ = page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
        time.sleep(0.3)

        # .. the old name is gone ..
        old_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))')
        assert old_row is None, f'Old name "{defn["name"]}" should be gone after edit'

        # .. and the new row holds the new values.
        new_row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{edited_name}"))')
        assert new_row is not None, f'Edited name "{edited_name}" should be present'

        cells = new_row.query_selector_all('td')
        cert_path_cell_text = cells[3].inner_text().strip()

        assert cert_path_cell_text == edited_cert_path, \
            f'Expected certificate path "{edited_cert_path}", got: "{cert_path_cell_text}"'

# ################################################################################################################################

    def test_08_duplicate_name_in_edit_shows_taken(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates two definitions A and B. Opens edit for A and types B's name.
        Asserts the 'Already taken' indicator appears.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create two definitions ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#data-table', state='visible')

        defn_a = _create_definition(page, 'dup-edit-a')
        defn_b = _create_definition(page, 'dup-edit-b')

        # .. reload so the server knows about both for the uniqueness check ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#data-table', state='visible')

        # .. open edit for A ..
        _click_edit_for_row(page, defn_a['name'])

        # .. clear the name field and type B's name ..
        name_field = page.locator('#id_edit-name')
        name_field.fill('')
        name_field.click()
        name_field.press_sequentially(defn_b['name'], delay=10)

        # .. wait for the uniqueness indicator ..
        taken_indicator = page.wait_for_selector(
            '#edit-form .zato-unique-taken', state='visible', timeout=10000)

        taken_text = cast_('any_', taken_indicator).inner_text()
        assert 'Already taken' in taken_text, f'Expected "Already taken", got: "{taken_text}"'

# ################################################################################################################################

    def test_09_edit_opens_on_channels_tab(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Opens the edit dialog, switches to the outgoing tab, closes the dialog, and verifies
        that the next edit dialog opens on the channels tab.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, 'opens-on-channels')

        # .. open the edit dialog on the outgoing tab ..
        _click_edit_for_row(page, defn['name'])
        _select_tab(page, '#edit-div', 'outgoing')

        # .. the outgoing tab has the stored name too ..
        outgoing_name = page.input_value('#id_edit-outgoing_name')
        assert outgoing_name == defn['name'], f'Expected "{defn["name"]}" on the outgoing tab, got: "{outgoing_name}"'

        # .. close it ..
        page.click('#edit-div button:has-text("Cancel")')
        _ = page.wait_for_selector('#edit-div', state='hidden', timeout=10000)

        # .. open it again ..
        _click_edit_for_row(page, defn['name'])

        # .. and it is back on the channels tab, with the match criteria in view.
        active_tab = page.get_attribute('#edit-div .dashboard-tab-active', 'data-tab')
        assert active_tab == 'channels', f'Expected "channels" to be active, got: "{active_tab}"'

        for field_name in _Channel_Field_Names:
            field_id = f'#id_edit-{field_name}'
            assert page.is_visible(field_id), f'Expected {field_id} to be visible'

        for field_name in _Outgoing_Field_Names:
            field_id = f'#id_edit-{field_name}'
            assert not page.is_visible(field_id), f'Expected {field_id} to be hidden'

# ################################################################################################################################

    def test_10_fields_on_both_tabs_are_saved(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Changes a field on each tab in one edit and verifies that both changes are saved.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, 'both-tabs')

        edited_subject_dn = defn['client_cert_subject_dn'] + ',OU=Edited'
        edited_key_path = defn['key_path'] + '.edited'

        # .. open the edit dialog and change the subject DN on the channels tab ..
        _click_edit_for_row(page, defn['name'])

        _select_tab(page, '#edit-div', 'channels')
        page.fill('#id_edit-client_cert_subject_dn', edited_subject_dn)

        # .. and the key path on the outgoing tab ..
        _select_tab(page, '#edit-div', 'outgoing')
        page.fill('#id_edit-key_path', edited_key_path)

        # .. submit and wait for the dialog to close ..
        page.click('#edit-div input[type="submit"]')
        _ = page.wait_for_selector('#edit-div', state='hidden', timeout=10000)
        time.sleep(0.3)

        # .. reload so the form is populated from what the server stored ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#data-table', state='visible')

        _click_edit_for_row(page, defn['name'])

        # .. both changes are there and the other fields are as they were.
        expected = dict(defn)
        expected['client_cert_subject_dn'] = edited_subject_dn
        expected['key_path'] = edited_key_path

        for field_name in _Channel_Field_Names + _Outgoing_Field_Names:
            field_value = page.input_value(f'#id_edit-{field_name}')
            assert field_value == expected[field_name], \
                f'Expected "{expected[field_name]}" in {field_name}, got: "{field_value}"'

# ################################################################################################################################
# ################################################################################################################################
