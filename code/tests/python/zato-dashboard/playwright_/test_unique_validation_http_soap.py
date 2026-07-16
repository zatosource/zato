# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.api import ZATO_NONE
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import open_create_dialog, submit_create_form

from rest_channel import create_channel, delete_channel, fill_channel_form, get_channel_id, open_channel_page, \
    open_edit_dialog, submit_create_form_expect_blocked, wait_for_channel_row
from rest_outconn import create_outconn, delete_outconn, open_outconn_page
from soap_channel import create_soap_channel, delete_soap_channel, open_soap_channel_page
from soap_outconn import create_soap_outconn, delete_soap_outconn, open_soap_outconn_page

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.unique.validation.' + CryptoManager.generate_hex_string(32) + '.'

_Echo_Service = 'demo.echo'

# The indicator selectors rendered by $.fn.zato.render_unique_indicator
_Taken_In_Create = '#create-form .zato-unique-taken'
_Ok_In_Create = '#create-form .zato-unique-ok'
_Taken_In_Edit = '#edit-form .zato-unique-taken'

# How long to wait for the async uniqueness check (300ms debounce timer + network)
_Indicator_Timeout = 10000

# ################################################################################################################################
# ################################################################################################################################

def _random_url_path(label:'str') -> 'str':
    out = f'/test/unique/{label}/' + CryptoManager.generate_hex_string(16)
    return out

# ################################################################################################################################

def _type_into_field(page:'Page', selector:'str', value:'str') -> 'None':
    """ Types a value character by character so the input event handler triggers the uniqueness check.
    The field is cleared first since some fields, e.g. url_path, come prefilled.
    """
    field = page.locator(selector)
    field.click()
    field.clear()
    field.press_sequentially(value, delay=10)

# ################################################################################################################################

def _close_create_dialog(page:'Page') -> 'None':
    page.evaluate('$("#create-div").dialog("close")')
    page.wait_for_function('!document.querySelector("#create-div").offsetParent')

# ################################################################################################################################

def _close_edit_dialog(page:'Page') -> 'None':
    page.evaluate('$("#edit-div").dialog("close")')
    page.wait_for_function('!document.querySelector("#edit-div").offsetParent')

# ################################################################################################################################
# ################################################################################################################################

class TestUniqueValidationHTTPSOAP:
    """ Tests for the uniqueness validator on the http-soap pages - REST channels, SOAP channels
    and the outgoing REST and SOAP connections, covering both the taken and the ok indicators.
    """

# ################################################################################################################################

    def test_01_rest_channel_url_path_taken_by_soap_channel(
        self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A url_path used by an existing SOAP channel must show the taken indicator
        in the REST channel create form because channel url paths are shared across transports.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        soap_name = _Test_Name_Prefix + 'soap-owner-01'
        url_path = _random_url_path('cross-transport-01')

        # Create a SOAP channel that owns the url_path ..
        soap_channel_id = create_soap_channel(page, base_url, soap_name, _Echo_Service, url_path)

        # .. open the REST channel create dialog ..
        open_channel_page(page, base_url)
        open_create_dialog(page)

        # .. type the SOAP channel's url_path ..
        _type_into_field(page, '#id_url_path', url_path)

        # .. and expect the taken indicator.
        taken_indicator = page.wait_for_selector(_Taken_In_Create, state='visible', timeout=_Indicator_Timeout)
        taken_text = taken_indicator.inner_text()
        assert 'Already taken' in taken_text, f'Expected "Already taken", got: "{taken_text}"'

        # Clean up.
        _close_create_dialog(page)
        open_soap_channel_page(page, base_url)
        delete_soap_channel(page, soap_channel_id)

# ################################################################################################################################

    # The cleanup deletes a documented REST endpoint, a breaking change the servers report on rebuild
    @pytest.mark.expect_log_errors('OpenAPI breaking change:')
    def test_02_soap_channel_url_path_taken_by_rest_channel(
        self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The reverse direction - a url_path used by an existing REST channel must show
        the taken indicator in the SOAP channel create form.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        rest_name = _Test_Name_Prefix + 'rest-owner-02'
        url_path = _random_url_path('cross-transport-02')

        # Create a REST channel that owns the url_path ..
        rest_channel_id = create_channel(page, base_url, rest_name, _Echo_Service, url_path)

        # .. open the SOAP channel create dialog ..
        open_soap_channel_page(page, base_url)
        open_create_dialog(page)

        # .. type the REST channel's url_path ..
        _type_into_field(page, '#id_url_path', url_path)

        # .. and expect the taken indicator.
        taken_indicator = page.wait_for_selector(_Taken_In_Create, state='visible', timeout=_Indicator_Timeout)
        taken_text = taken_indicator.inner_text()
        assert 'Already taken' in taken_text, f'Expected "Already taken", got: "{taken_text}"'

        # Clean up.
        _close_create_dialog(page)
        open_channel_page(page, base_url)
        delete_channel(page, rest_channel_id)

# ################################################################################################################################

    def test_03_submit_blocked_on_taken_url_path(
        self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Clicking OK with a url_path that an existing SOAP channel already uses must be blocked
        client-side - the dialog stays open and the taken indicator is shown, with no server error.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        soap_name = _Test_Name_Prefix + 'soap-owner-03'
        rest_name = _Test_Name_Prefix + 'rest-blocked-03'
        url_path = _random_url_path('submit-blocked-03')

        # Create a SOAP channel that owns the url_path ..
        soap_channel_id = create_soap_channel(page, base_url, soap_name, _Echo_Service, url_path)

        # .. open the REST channel create dialog and fill the whole form ..
        open_channel_page(page, base_url)
        open_create_dialog(page)

        fill_channel_form(page, {
            'name': rest_name,
            'url_path': url_path,
            'service': _Echo_Service,
        })

        # .. the submission must be blocked and the dialog must stay open ..
        submit_create_form_expect_blocked(page)

        # .. with the taken indicator rendered on the url_path field ..
        taken_indicator = page.wait_for_selector(_Taken_In_Create, state='visible', timeout=_Indicator_Timeout)
        taken_text = taken_indicator.inner_text()
        assert 'Already taken' in taken_text, f'Expected "Already taken", got: "{taken_text}"'

        # .. and no row for the blocked channel may exist.
        _close_create_dialog(page)
        open_channel_page(page, base_url)
        page_content = page.content()
        assert rest_name not in page_content, f'Blocked channel "{rest_name}" should not be in the page'

        # Clean up.
        open_soap_channel_page(page, base_url)
        delete_soap_channel(page, soap_channel_id)

# ################################################################################################################################

    # The cleanup deletes documented REST endpoints, a breaking change the servers report on rebuild
    @pytest.mark.expect_log_errors('OpenAPI breaking change:')
    def test_04_same_url_path_different_method_is_ok(
        self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The same url_path with a different HTTP method must show the ok indicator
        and the create must succeed, mirroring the server's uniqueness rule.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        get_name = _Test_Name_Prefix + 'method-get-04'
        post_name = _Test_Name_Prefix + 'method-post-04'
        url_path = _random_url_path('same-path-04')

        # Create a channel that owns the url_path with the GET method ..
        get_method_channel_id = create_channel(page, base_url, get_name, _Echo_Service, url_path, {
            'method': 'GET',
        })

        # .. open the create dialog again ..
        open_channel_page(page, base_url)
        open_create_dialog(page)

        # .. choose a different method first so the uniqueness check compares against it ..
        fill_channel_form(page, {
            'method': 'POST',
        })

        # .. type the same url_path ..
        _type_into_field(page, '#id_url_path', url_path)

        # .. expect the ok indicator since the methods differ ..
        ok_indicator = page.wait_for_selector(_Ok_In_Create, state='visible', timeout=_Indicator_Timeout)
        ok_text = ok_indicator.inner_text()
        assert '\u2713' in ok_text, f'Expected checkmark in indicator, got: "{ok_text}"'

        # .. fill in the remaining fields and submit ..
        fill_channel_form(page, {
            'name': post_name,
            'service': _Echo_Service,
            'security_value': ZATO_NONE,
        })
        submit_create_form(page)

        # .. the new channel must appear in the table.
        _ = wait_for_channel_row(page, post_name)

        # Clean up both channels.
        post_channel_id = get_channel_id(page, post_name)
        delete_channel(page, post_channel_id)
        delete_channel(page, get_method_channel_id)

# ################################################################################################################################

    # The cleanup deletes a documented REST endpoint, a breaking change the servers report on rebuild
    @pytest.mark.expect_log_errors('OpenAPI breaking change:')
    def test_05_rest_channel_duplicate_name_shows_taken(
        self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A REST channel name that already exists in the same transport must show the taken indicator.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        channel_name = _Test_Name_Prefix + 'dup-name-05'
        url_path = _random_url_path('dup-name-05')

        # Create the channel that owns the name ..
        channel_id = create_channel(page, base_url, channel_name, _Echo_Service, url_path)

        # .. reload so the create dialog starts clean ..
        open_channel_page(page, base_url)
        open_create_dialog(page)

        # .. type the same name ..
        _type_into_field(page, '#id_name', channel_name)

        # .. and expect the taken indicator.
        taken_indicator = page.wait_for_selector(_Taken_In_Create, state='visible', timeout=_Indicator_Timeout)
        taken_text = taken_indicator.inner_text()
        assert 'Already taken' in taken_text, f'Expected "Already taken", got: "{taken_text}"'

        # Clean up.
        _close_create_dialog(page)
        open_channel_page(page, base_url)
        delete_channel(page, channel_id)

# ################################################################################################################################

    # The cleanup deletes a documented REST endpoint, a breaking change the servers report on rebuild
    @pytest.mark.expect_log_errors('OpenAPI breaking change:')
    def test_06_rest_channel_name_matching_soap_channel_is_ok(
        self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A REST channel name equal to an existing SOAP channel's name must show the ok indicator
        and the create must succeed - names are unique per transport.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        shared_name = _Test_Name_Prefix + 'shared-name-06'
        soap_url_path = _random_url_path('soap-06')
        rest_url_path = _random_url_path('rest-06')

        # Create a SOAP channel that owns the name ..
        soap_channel_id = create_soap_channel(page, base_url, shared_name, _Echo_Service, soap_url_path)

        # .. open the REST channel create dialog ..
        open_channel_page(page, base_url)
        open_create_dialog(page)

        # .. type the SOAP channel's name ..
        _type_into_field(page, '#id_name', shared_name)

        # .. expect the ok indicator since names are per transport ..
        ok_indicator = page.wait_for_selector(_Ok_In_Create, state='visible', timeout=_Indicator_Timeout)
        ok_text = ok_indicator.inner_text()
        assert '\u2713' in ok_text, f'Expected checkmark in indicator, got: "{ok_text}"'

        # .. fill in the remaining fields and submit ..
        fill_channel_form(page, {
            'url_path': rest_url_path,
            'service': _Echo_Service,
            'security_value': ZATO_NONE,
        })
        submit_create_form(page)

        # .. the new channel must appear in the table.
        _ = wait_for_channel_row(page, shared_name)

        # Clean up both channels.
        rest_channel_id = get_channel_id(page, shared_name)
        delete_channel(page, rest_channel_id)
        open_soap_channel_page(page, base_url)
        delete_soap_channel(page, soap_channel_id)

# ################################################################################################################################

    def test_07_soap_outconn_duplicate_name_shows_taken(
        self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ An outgoing SOAP connection name that already exists must show the taken indicator.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'soap-outconn-07'

        # Create the connection that owns the name ..
        outconn_id = create_soap_outconn(page, base_url, outconn_name, 'https://example.com:8443')

        # .. reload so the create dialog starts clean ..
        open_soap_outconn_page(page, base_url)
        open_create_dialog(page)

        # .. type the same name ..
        _type_into_field(page, '#id_name', outconn_name)

        # .. and expect the taken indicator.
        taken_indicator = page.wait_for_selector(_Taken_In_Create, state='visible', timeout=_Indicator_Timeout)
        taken_text = taken_indicator.inner_text()
        assert 'Already taken' in taken_text, f'Expected "Already taken", got: "{taken_text}"'

        # Clean up.
        _close_create_dialog(page)
        open_soap_outconn_page(page, base_url)
        delete_soap_outconn(page, outconn_id)

# ################################################################################################################################

    def test_08_rest_outconn_duplicate_name_shows_taken_and_unique_ok(
        self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ An outgoing REST connection name that already exists must show the taken indicator
        while a unique name must show the ok indicator.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'rest-outconn-08'
        unique_name = _Test_Name_Prefix + 'rest-outconn-unique-08'

        # Create the connection that owns the name ..
        outconn_id = create_outconn(page, base_url, outconn_name, 'https://example.com:8443')

        # .. reload so the create dialog starts clean ..
        open_outconn_page(page, base_url)
        open_create_dialog(page)

        # .. type the same name and expect the taken indicator ..
        _type_into_field(page, '#id_name', outconn_name)

        taken_indicator = page.wait_for_selector(_Taken_In_Create, state='visible', timeout=_Indicator_Timeout)
        taken_text = taken_indicator.inner_text()
        assert 'Already taken' in taken_text, f'Expected "Already taken", got: "{taken_text}"'

        # .. clear the field and type a unique name instead ..
        _type_into_field(page, '#id_name', unique_name)

        # .. and expect the ok indicator.
        ok_indicator = page.wait_for_selector(_Ok_In_Create, state='visible', timeout=_Indicator_Timeout)
        ok_text = ok_indicator.inner_text()
        assert '\u2713' in ok_text, f'Expected checkmark in indicator, got: "{ok_text}"'

        # Clean up.
        _close_create_dialog(page)
        open_outconn_page(page, base_url)
        delete_outconn(page, outconn_id)

# ################################################################################################################################

    # The cleanup deletes documented REST endpoints, a breaking change the servers report on rebuild
    @pytest.mark.expect_log_errors('OpenAPI breaking change:')
    def test_09_edit_url_path_conflict(
        self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ In the edit form, an unchanged url_path must not be flagged while changing it
        to another channel's url_path must show the taken indicator and block the submission.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        owner_name = _Test_Name_Prefix + 'edit-owner-09'
        edited_name = _Test_Name_Prefix + 'edit-target-09'
        owner_url_path = _random_url_path('edit-owner-09')
        edited_url_path = _random_url_path('edit-target-09')

        # Create the channel that owns the conflicting url_path and the channel to edit ..
        owner_channel_id = create_channel(page, base_url, owner_name, _Echo_Service, owner_url_path)
        edited_channel_id = create_channel(page, base_url, edited_name, _Echo_Service, edited_url_path)

        # .. open the edit dialog for the second channel ..
        open_edit_dialog(page, edited_channel_id)

        # .. retype the channel's own url_path - an unchanged value must not be flagged ..
        _type_into_field(page, '#id_edit-url_path', edited_url_path)

        page.wait_for_timeout(1000)
        taken_after_own_value = page.query_selector(_Taken_In_Edit)
        assert taken_after_own_value is None, 'An unchanged url_path must not be flagged as taken'

        # .. now change it to the other channel's url_path ..
        _type_into_field(page, '#id_edit-url_path', owner_url_path)

        # .. expect the taken indicator ..
        taken_indicator = page.wait_for_selector(_Taken_In_Edit, state='visible', timeout=_Indicator_Timeout)
        taken_text = taken_indicator.inner_text()
        assert 'Already taken' in taken_text, f'Expected "Already taken", got: "{taken_text}"'

        # .. clicking OK must be blocked and the dialog must stay open ..
        page.click('#edit-div input[type="submit"]')
        page.wait_for_timeout(1000)

        edit_dialog = page.query_selector('#edit-div')
        assert edit_dialog.is_visible(), 'Expected the edit dialog to remain open after a blocked submission'

        # Clean up.
        _close_edit_dialog(page)
        open_channel_page(page, base_url)
        delete_channel(page, edited_channel_id)
        delete_channel(page, owner_channel_id)

# ################################################################################################################################
# ################################################################################################################################
