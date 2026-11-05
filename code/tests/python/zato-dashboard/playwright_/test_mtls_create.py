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

# The fields that a channel reads and those that an outgoing connection reads, by the tab that each set is on
_Channel_Field_Names  = ('client_cert_fingerprint', 'client_cert_subject_dn')
_Outgoing_Field_Names = ('cert_path', 'key_path', 'ca_certs_path')

# The tabs of the form, in the order they are displayed, with their labels
_Tab_Names  = ['channels', 'outgoing']
_Tab_Labels = ['For channels', 'For outgoing connections']

# The Name field on each tab, the outgoing one being a copy of the channels one
_Channels_Name_Id = '#id_name'
_Outgoing_Name_Id = '#id_outgoing_name'

# The panels that hold the fields of each tab
_Channels_Panel_Id = '#mtls-create-tab-panel-channels'
_Outgoing_Panel_Id = '#mtls-create-tab-panel-outgoing'

# ################################################################################################################################
# ################################################################################################################################

def _select_tab(page:'Page', tab_name:'str') -> 'None':
    page.click(f'#create-div .dashboard-tab[data-tab="{tab_name}"]')

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

    _select_tab(page, 'channels')
    page.fill('#id_client_cert_fingerprint', fingerprint)
    page.fill('#id_client_cert_subject_dn', subject_dn)

    _select_tab(page, 'outgoing')
    page.fill('#id_cert_path', cert_path)
    page.fill('#id_key_path', key_path)
    page.fill('#id_ca_certs_path', ca_certs_path)

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

def _assert_fields_visible(page:'Page', field_names:'any_', is_visible:'bool', tab_name:'str') -> 'None':
    """ Asserts that each of the given fields of the create form is visible or hidden.
    """
    for field_name in field_names:
        field_is_visible = page.is_visible(f'#id_{field_name}')
        assert field_is_visible == is_visible, \
            f'Expected #id_{field_name} visible={is_visible} on tab "{tab_name}", got: {field_is_visible}'

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

    def test_06_tabs_open_the_dialog(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Verifies that the create dialog opens with two tabs, "For channels" and "For outgoing connections",
        in this order, above every field, with the first one active.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _open_create_dialog(page, base_url)

        # The tabs come first in the form ..
        first_element_class = page.eval_on_selector('#create-form', 'node => node.firstElementChild.className')
        assert first_element_class == 'dashboard-tabs', f'Expected the tabs first in the form, got: "{first_element_class}"'

        # .. they are the two expected ones, in this order ..
        tab_names = page.eval_on_selector_all(
            '#create-div .dashboard-tab',
            'nodes => nodes.map(node => node.getAttribute("data-tab"))',
        )
        assert tab_names == _Tab_Names, f'Expected tabs {_Tab_Names}, got: {tab_names}'

        tab_labels = page.eval_on_selector_all(
            '#create-div .dashboard-tab',
            'nodes => nodes.map(node => node.textContent.trim())',
        )
        assert tab_labels == _Tab_Labels, f'Expected tab labels {_Tab_Labels}, got: {tab_labels}'

        # .. and the channels tab is the active one.
        active_tab = page.get_attribute('#create-div .dashboard-tab-active', 'data-tab')
        assert active_tab == 'channels', f'Expected "channels" to be active, got: "{active_tab}"'

# ################################################################################################################################

    def test_07_each_field_is_on_one_tab(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Verifies that each tab starts with Name, followed by the fields of its own side only,
        and that no field is submitted twice.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _open_create_dialog(page, base_url)

        # The channels tab holds Name and the match criteria ..
        channel_fields = page.eval_on_selector_all(
            f'{_Channels_Panel_Id} input',
            'nodes => nodes.map(node => "#" + node.id)',
        )
        expected_channel_fields = [_Channels_Name_Id] + [f'#id_{field_name}' for field_name in _Channel_Field_Names]
        assert channel_fields == expected_channel_fields, \
            f'Expected {expected_channel_fields} on the channels tab, got: {channel_fields}'

        # .. the outgoing tab holds its own Name and the paths ..
        outgoing_fields = page.eval_on_selector_all(
            f'{_Outgoing_Panel_Id} input',
            'nodes => nodes.map(node => "#" + node.id)',
        )
        expected_outgoing_fields = [_Outgoing_Name_Id] + [f'#id_{field_name}' for field_name in _Outgoing_Field_Names]
        assert outgoing_fields == expected_outgoing_fields, \
            f'Expected {expected_outgoing_fields} on the outgoing tab, got: {outgoing_fields}'

        # .. and no field is submitted twice.
        for field_name in ('name',) + _Channel_Field_Names + _Outgoing_Field_Names:
            count = page.locator(f'#create-form [name="{field_name}"]').count()
            assert count == 1, f'Expected one "{field_name}" field in the form, found: {count}'

# ################################################################################################################################

    def test_08_name_is_the_same_on_both_tabs(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Types the name on one tab, then on the other, and verifies that each time both tabs show it.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        channels_name = _Test_Name_Prefix + 'typed-on-channels'
        outgoing_name = _Test_Name_Prefix + 'typed-on-outgoing'

        _open_create_dialog(page, base_url)

        # A name typed on the channels tab ..
        page.fill(_Channels_Name_Id, channels_name)

        # .. is on the outgoing tab too ..
        _select_tab(page, 'outgoing')
        mirrored_name = page.input_value(_Outgoing_Name_Id)
        assert mirrored_name == channels_name, f'Expected "{channels_name}" on the outgoing tab, got: "{mirrored_name}"'

        # .. and a name typed on the outgoing tab ..
        page.fill(_Outgoing_Name_Id, outgoing_name)

        # .. is on the channels tab too.
        _select_tab(page, 'channels')
        mirrored_name = page.input_value(_Channels_Name_Id)
        assert mirrored_name == outgoing_name, f'Expected "{outgoing_name}" on the channels tab, got: "{mirrored_name}"'

# ################################################################################################################################

    def test_09_each_tab_shows_its_fields(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Switches between the tabs and verifies that each one shows its own fields and hides those of the other.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _open_create_dialog(page, base_url)

        # The dialog opens with the name and the match criteria in view ..
        assert page.is_visible(_Channels_Name_Id), 'Expected the name on the channels tab to be visible'
        assert not page.is_visible(_Outgoing_Name_Id), 'Expected the name on the outgoing tab to be hidden'
        _assert_fields_visible(page, _Channel_Field_Names, True, 'channels')
        _assert_fields_visible(page, _Outgoing_Field_Names, False, 'channels')

        # .. the outgoing tab shows its own name and the paths instead ..
        _select_tab(page, 'outgoing')
        assert page.is_visible(_Outgoing_Name_Id), 'Expected the name on the outgoing tab to be visible'
        assert not page.is_visible(_Channels_Name_Id), 'Expected the name on the channels tab to be hidden'
        _assert_fields_visible(page, _Channel_Field_Names, False, 'outgoing')
        _assert_fields_visible(page, _Outgoing_Field_Names, True, 'outgoing')

        # .. and the channels tab shows the match criteria again.
        _select_tab(page, 'channels')
        _assert_fields_visible(page, _Channel_Field_Names, True, 'channels')
        _assert_fields_visible(page, _Outgoing_Field_Names, False, 'channels')

# ################################################################################################################################

    def test_10_reopened_dialog_starts_on_channels_tab(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Switches to the outgoing tab, closes the dialog and verifies that it opens on the channels tab again.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _open_create_dialog(page, base_url)
        _select_tab(page, 'outgoing')

        # Close the dialog ..
        page.click('#create-div button:has-text("Cancel")')
        _ = page.wait_for_selector('#create-div', state='hidden', timeout=10000)

        # .. open it again ..
        page.click('#markup .page_prompt a')
        _ = page.wait_for_selector('#create-div', state='visible')

        # .. and it is back on the channels tab.
        active_tab = page.get_attribute('#create-div .dashboard-tab-active', 'data-tab')
        assert active_tab == 'channels', f'Expected "channels" to be active, got: "{active_tab}"'
        _assert_fields_visible(page, _Channel_Field_Names, True, 'channels')

# ################################################################################################################################

    def test_11_channels_only_definition(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Fills in the channels tab only, saves the definition and verifies that it reopens
        with its match criteria and with empty paths.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        definition_name = _Test_Name_Prefix + 'channels-only'
        fingerprint = CryptoManager.generate_hex_string(32)
        subject_dn = f'CN={definition_name},O=Test,C=US'

        _open_create_dialog(page, base_url)

        # Only the name and the match criteria are filled in ..
        page.fill('#id_name', definition_name)
        page.fill('#id_client_cert_fingerprint', fingerprint)
        page.fill('#id_client_cert_subject_dn', subject_dn)

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

        # .. the match criteria are what was typed in ..
        stored_fingerprint = page.input_value('#id_edit-client_cert_fingerprint')
        assert stored_fingerprint == fingerprint, f'Expected fingerprint "{fingerprint}", got: "{stored_fingerprint}"'

        stored_subject_dn = page.input_value('#id_edit-client_cert_subject_dn')
        assert stored_subject_dn == subject_dn, f'Expected subject DN "{subject_dn}", got: "{stored_subject_dn}"'

        # .. and the paths are empty.
        for field_name in _Outgoing_Field_Names:
            field_value = page.input_value(f'#id_edit-{field_name}')
            assert field_value == '', f'Expected empty {field_name}, got: "{field_value}"'

# ################################################################################################################################
# ################################################################################################################################
