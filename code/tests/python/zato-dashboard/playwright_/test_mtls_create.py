# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.typing_ import any_, cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/security/mtls/'

_Test_Name_Prefix = 'test.mtls.' + CryptoManager.generate_hex_string(32) + '.'

# The fields that an outgoing connection reads and those that a channel reads
_Outgoing_Field_Ids = ('#id_cert_path', '#id_key_path', '#id_ca_certs_path')
_Channel_Field_Ids  = ('#id_client_cert_fingerprint', '#id_client_cert_subject_dn')

# The label of the use that the create form selects on its own
_Default_Use_Label = 'Both channels and outgoing connections'

# ################################################################################################################################
# ################################################################################################################################

def _fill_definition_fields(page:'Page', name:'str') -> 'dict':
    """ Fills in the create dialog fields for a definition of the given name and returns the values used.
    """

    cert_path = f'/opt/hot-deploy/ssl/{name}-cert.pem'
    key_path = f'/opt/hot-deploy/ssl/{name}-key.pem'
    ca_certs_path = f'/opt/hot-deploy/ssl/{name}-ca.pem'
    fingerprint = CryptoManager.generate_hex_string(32)
    subject_dn = f'CN={name},O=Test,C=US'

    page.fill('#id_name', name)
    page.fill('#id_cert_path', cert_path)
    page.fill('#id_key_path', key_path)
    page.fill('#id_ca_certs_path', ca_certs_path)
    page.fill('#id_client_cert_fingerprint', fingerprint)
    page.fill('#id_client_cert_subject_dn', subject_dn)

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

def _open_create_dialog(page:'Page', base_url:'str') -> 'None':
    """ Navigates to the mTLS page and opens the create dialog.
    """
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
    _ = page.wait_for_selector('#data-table', state='visible')

    page.click('#markup .page_prompt a')
    _ = page.wait_for_selector('#create-div', state='visible')

# ################################################################################################################################

def _assert_fields_state(page:'Page', field_ids:'any_', is_enabled:'bool', use_for:'str') -> 'None':
    """ Asserts that each of the given fields is enabled or disabled.
    """
    for field_id in field_ids:
        field_is_enabled = page.is_enabled(field_id)
        assert field_is_enabled == is_enabled, \
            f'Expected {field_id} enabled={is_enabled} for use_for "{use_for}", got: {field_is_enabled}'

# ################################################################################################################################
# ################################################################################################################################

class TestMTLSCreate:
    """ Tests for the mTLS create flow.
    """

    def test_01_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates to the mTLS page and verifies its structure:
        - h2 heading contains "mTLS"
        - data table is visible
        - "Create an mTLS definition" link is present
        - table headers include Name, Certificate path, Fingerprint, Subject DN
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the mTLS page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#data-table', state='visible')

        # .. verify the page heading ..
        heading = cast_('any_', page.query_selector('h2.zato'))
        heading_text = heading.inner_text()
        assert 'mTLS' in heading_text, f'Expected "mTLS" in heading, got: {heading_text}'

        # .. verify the create link is present ..
        create_link = cast_('any_', page.query_selector('#markup .page_prompt a'))
        create_link_text = create_link.inner_text()
        assert 'Create an mTLS definition' in create_link_text, \
            f'Expected create link text, got: {create_link_text}'

        # .. verify table headers (CSS text-transform may uppercase them).
        headers = page.query_selector_all('#data-table thead th a')

        header_texts = [] # type: list

        for header in headers:
            raw_text = header.inner_text()
            text = raw_text.strip().lower()
            header_texts.append(text)

        assert 'name' in header_texts, f'Expected "name" in headers, got: {header_texts}'
        assert 'certificate path' in header_texts, f'Expected "certificate path" in headers, got: {header_texts}'
        assert 'fingerprint' in header_texts, f'Expected "fingerprint" in headers, got: {header_texts}'
        assert 'subject dn' in header_texts, f'Expected "subject dn" in headers, got: {header_texts}'

# ################################################################################################################################

    def test_02_create_one(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a single mTLS definition via the UI dialog and verifies
        that the new row appears in the table with correct cell text for name, certificate path,
        fingerprint and subject DN.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'create-one'

        # Navigate to the mTLS page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#data-table', state='visible')

        # .. click the create link to open the dialog ..
        page.click('#markup .page_prompt a')
        _ = page.wait_for_selector('#create-div', state='visible')

        # .. fill in the form fields ..
        defn = _fill_definition_fields(page, definition_name)

        # .. submit the form ..
        page.click('#create-div input[type="submit"]')

        # .. wait for the dialog to close ..
        _ = page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. verify the new row appears in the table ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{definition_name}"))'
        row = cast_('any_', page.wait_for_selector(row_selector, state='visible', timeout=5000))

        # .. extract cell texts from the row ..
        cells = row.query_selector_all('td')

        name_cell_text = cells[2].inner_text().strip()
        cert_path_cell_text = cells[3].inner_text().strip()
        fingerprint_cell_text = cells[4].inner_text().strip()
        subject_dn_cell_text = cells[5].inner_text().strip()

        # .. verify each cell has the correct value.
        assert name_cell_text == defn['name'], \
            f'Expected name "{defn["name"]}", got: "{name_cell_text}"'

        assert cert_path_cell_text == defn['cert_path'], \
            f'Expected certificate path "{defn["cert_path"]}", got: "{cert_path_cell_text}"'

        assert fingerprint_cell_text == defn['client_cert_fingerprint'], \
            f'Expected fingerprint "{defn["client_cert_fingerprint"]}", got: "{fingerprint_cell_text}"'

        assert subject_dn_cell_text == defn['client_cert_subject_dn'], \
            f'Expected subject DN "{defn["client_cert_subject_dn"]}", got: "{subject_dn_cell_text}"'

# ################################################################################################################################

    def test_03_create_multiple(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates 3 mTLS definitions with distinct names and verifies
        that all 3 rows appear in the table with correct cell text.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the mTLS page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#data-table', state='visible')

        # .. create each definition ..
        definitions = [] # type: list

        for index in range(3):
            name = _Test_Name_Prefix + f'multi-{index}'

            # .. open the create dialog ..
            page.click('#markup .page_prompt a')
            _ = page.wait_for_selector('#create-div', state='visible')

            # .. fill in the form fields ..
            defn = _fill_definition_fields(page, name)
            definitions.append(defn)

            # .. submit and wait for the dialog to close ..
            page.click('#create-div input[type="submit"]')
            _ = page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. verify all 3 rows are present with correct values.
        for defn in definitions:

            row_selector = f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))'
            row = cast_('any_', page.wait_for_selector(row_selector, state='visible', timeout=5000))

            cells = row.query_selector_all('td')

            name_cell_text = cells[2].inner_text().strip()
            cert_path_cell_text = cells[3].inner_text().strip()

            assert name_cell_text == defn['name'], \
                f'Expected name "{defn["name"]}", got: "{name_cell_text}"'

            assert cert_path_cell_text == defn['cert_path'], \
                f'Expected certificate path "{defn["cert_path"]}", got: "{cert_path_cell_text}"'

# ################################################################################################################################

    def test_04_create_then_reopen_form_is_empty(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ After a successful create, reopens the create dialog and verifies
        that all input fields are empty and no uniqueness indicator spans remain.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'reopen-empty'

        # Navigate to the mTLS page ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#data-table', state='visible')

        # .. create a definition first ..
        page.click('#markup .page_prompt a')
        _ = page.wait_for_selector('#create-div', state='visible')

        _ = _fill_definition_fields(page, definition_name)

        page.click('#create-div input[type="submit"]')
        _ = page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. reopen the create dialog ..
        page.click('#markup .page_prompt a')
        _ = page.wait_for_selector('#create-div', state='visible')

        # .. verify all fields are empty ..
        for field_id in ('#id_name', '#id_cert_path', '#id_key_path', '#id_ca_certs_path',
            '#id_client_cert_fingerprint', '#id_client_cert_subject_dn'):
            field_value = page.input_value(field_id)
            assert field_value == '', f'Expected empty {field_id}, got: "{field_value}"'

        # .. verify no uniqueness indicators remain.
        indicators = page.query_selector_all('#create-form .zato-unique-indicator')
        indicator_count = len(indicators)
        assert indicator_count == 0, f'Expected 0 indicators, found: {indicator_count}'

# ################################################################################################################################

    def test_05_duplicate_name_shows_taken_indicator(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition, reopens the create dialog, types the same name,
        and verifies that the 'Already taken' indicator appears.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        existing_name = _Test_Name_Prefix + 'duplicate-check'

        # Navigate and create a definition to have a known name ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#data-table', state='visible')

        page.click('#markup .page_prompt a')
        _ = page.wait_for_selector('#create-div', state='visible')

        _ = _fill_definition_fields(page, existing_name)

        page.click('#create-div input[type="submit"]')
        _ = page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. reload the page so the server's check_attr_exists picks up the new definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#data-table', state='visible')

        # .. reopen the create dialog and type the same name character by character
        # .. so that the input event handler triggers the uniqueness check ..
        page.click('#markup .page_prompt a')
        _ = page.wait_for_selector('#create-div', state='visible')

        name_field = page.locator('#id_name')
        name_field.click()
        name_field.press_sequentially(existing_name, delay=10)

        # .. wait for the async uniqueness check (300ms timer + network) ..
        taken_indicator = page.wait_for_selector(
            '#create-form .zato-unique-taken', state='visible', timeout=10000)

        # .. verify the indicator text.
        taken_text = cast_('any_', taken_indicator).inner_text()
        assert 'Already taken' in taken_text, f'Expected "Already taken", got: "{taken_text}"'

# ################################################################################################################################

    def test_06_use_for_row_follows_name(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Verifies that the "For use with" row is the one directly below "Name" in the create dialog.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _open_create_dialog(page, base_url)

        # Read the labels of the form's rows in the order they are displayed ..
        labels = page.eval_on_selector_all(
            '#create-form table.form-data label',
            'nodes => nodes.map(node => node.textContent.trim())',
        )

        # .. and confirm the first two.
        assert labels[0] == 'Name', f'Expected "Name" in the first row, got: {labels}'
        assert labels[1] == 'For use with', f'Expected "For use with" in the second row, got: {labels}'

# ################################################################################################################################

    def test_07_default_use_enables_all_fields(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Verifies that the create dialog selects "Both channels and outgoing connections"
        and that all five fields are enabled then.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _open_create_dialog(page, base_url)

        selected_label = page.eval_on_selector('#id_use_for', 'node => node.options[node.selectedIndex].text')
        assert selected_label == _Default_Use_Label, f'Expected "{_Default_Use_Label}", got: "{selected_label}"'

        _assert_fields_state(page, _Outgoing_Field_Ids, True, 'both')
        _assert_fields_state(page, _Channel_Field_Ids, True, 'both')

# ################################################################################################################################

    def test_08_each_use_disables_its_fields(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Selects each use in turn and verifies which fields are disabled, ending with "Both",
        which enables all of them again.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _open_create_dialog(page, base_url)

        # A definition used with channels has no outgoing material ..
        _ = page.select_option('#id_use_for', 'channels')
        _assert_fields_state(page, _Outgoing_Field_Ids, False, 'channels')
        _assert_fields_state(page, _Channel_Field_Ids, True, 'channels')

        # .. one used with outgoing connections has no match criteria ..
        _ = page.select_option('#id_use_for', 'outgoing')
        _assert_fields_state(page, _Outgoing_Field_Ids, True, 'outgoing')
        _assert_fields_state(page, _Channel_Field_Ids, False, 'outgoing')

        # .. and one used with both has both.
        _ = page.select_option('#id_use_for', 'both')
        _assert_fields_state(page, _Outgoing_Field_Ids, True, 'both')
        _assert_fields_state(page, _Channel_Field_Ids, True, 'both')

# ################################################################################################################################

    def test_09_use_for_select_is_not_truncated(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Verifies that the "For use with" select is wide enough for its longest label.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _open_create_dialog(page, base_url)

        widths = page.eval_on_selector('#id_use_for', 'node => [node.scrollWidth, node.clientWidth]')
        scroll_width, client_width = widths

        assert scroll_width <= client_width, \
            f'Expected the select to fit its text, scrollWidth={scroll_width}, clientWidth={client_width}'

# ################################################################################################################################

    def test_10_channels_definition_has_no_outgoing_fields(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Fills in all five fields, switches the use to "Channels" and saves the definition,
        then verifies that it reopens with its outgoing fields empty.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'channels-only'

        _open_create_dialog(page, base_url)

        # The outgoing fields hold values until the use is switched to one that does not read them ..
        defn = _fill_definition_fields(page, definition_name)
        _ = page.select_option('#id_use_for', 'channels')

        # .. submit the form ..
        page.click('#create-div input[type="submit"]')
        _ = page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. read the server-side ID off the new row ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{definition_name}"))'
        row = cast_('any_', page.wait_for_selector(row_selector, state='visible', timeout=5000))

        cells = row.query_selector_all('td')
        cert_path_cell_text = cells[3].inner_text().strip()
        assert cert_path_cell_text == '', f'Expected no certificate path, got: "{cert_path_cell_text}"'

        id_cell = row.query_selector('td[class*="item_id_"]')
        item_id = id_cell.inner_text().strip()

        # .. reload the page so the form is populated from what the server stored ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}?query={definition_name}')
        _ = page.wait_for_selector(row_selector, state='visible', timeout=5000)

        # .. open the edit dialog ..
        page.evaluate(f'$.fn.zato.security.mtls.edit("{item_id}")')
        _ = page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        # .. the use is the one it was saved with ..
        use_for = page.input_value('#id_edit-use_for')
        assert use_for == 'channels', f'Expected "channels", got: "{use_for}"'

        # .. the outgoing fields are empty ..
        for field_name in ('cert_path', 'key_path', 'ca_certs_path'):
            field_value = page.input_value(f'#id_edit-{field_name}')
            assert field_value == '', f'Expected empty {field_name}, got: "{field_value}"'

        # .. and the match criteria are what was typed in.
        fingerprint = page.input_value('#id_edit-client_cert_fingerprint')
        assert fingerprint == defn['client_cert_fingerprint'], \
            f'Expected fingerprint "{defn["client_cert_fingerprint"]}", got: "{fingerprint}"'

# ################################################################################################################################
# ################################################################################################################################
