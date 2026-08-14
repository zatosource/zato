# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import shutil
import sys
import time
from http.client import NOT_FOUND, OK

# pytest
import pytest

# requests
import requests

# Zato
from zato.common.test import rand_string
from zato.common.test.mcp_ import make_jsonrpc_initialize
from zato.common.test.playwright_pubsub import create_basic_auth

# Zato - test helpers - the wizard driver lives next to the tests
_this_directory = os.path.dirname(__file__)

if _this_directory not in sys.path:
    sys.path.insert(0, _this_directory)

import _mcp_wizard as wizard_page

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, anytuple, dictlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.mcp.wizard.' + rand_string() + '.'

# The service every gateway in this suite exposes
_Echo_Service = 'demo.echo'

# The token cap the full-create test configures - it must stay above the minimum
# usable byte budget for graceful trimming, i.e. 1000 tokens at 4 characters each.
_Max_Response_Tokens = '2048'

# How many echo rows make a response that is comfortably over the cap above
_Oversized_Row_Count = 500

# How long to wait for a UI change to propagate to live MCP enforcement, in seconds
_Propagation_Timeout = 20

# How long to wait between the polling attempts above, in seconds
_Propagation_Poll_Interval = 0.5

# How long to wait after a refused save before concluding no confirmation shows, in milliseconds
_Refusal_Wait = 2000

# How long to wait for a UI element to show, in milliseconds
_UI_Timeout = 5000

# Log patterns produced by the server while the group membership is still propagating
_Group_Log_Patterns = (
    'Invalid bearer token (groups)',
    'Received neither Basic Auth, bearer token nor API key (groups)',
)

# ################################################################################################################################
# ################################################################################################################################

def _seed_skill(server_dir:'str', skill_name:'str') -> 'str':
    """ Seeds one user-authored skill on disk, under the server's config/repo directory,
    which is where the wizard's skills picker reads them from. Returns the skill's directory.
    """
    out = os.path.join(server_dir, 'config', 'repo', 'skills', skill_name)
    os.makedirs(out, exist_ok=True)

    skill_document = f'''---
name: {skill_name}
description: A test skill the MCP wizard suite assigns to a gateway
---

Use this skill when exercising the MCP wizard test suite.
'''

    skill_path = os.path.join(out, 'SKILL.md')

    with open(skill_path, 'w') as skill_file:
        _ = skill_file.write(skill_document)

    return out

# ################################################################################################################################

def _call_echo(server_port:'int', url_path:'str', auth:'anytuple', arguments:'anydict') -> 'anydict':
    """ Runs one initialize plus tools/call round trip against the live gateway
    and returns the result object of the JSON-RPC response.
    """

    url = f'http://127.0.0.1:{server_port}{url_path}'
    headers = {'Content-Type': 'application/json'}

    body = make_jsonrpc_initialize()
    initialize_response = requests.post(url, data=body, headers=headers, auth=auth, timeout=10)
    assert initialize_response.status_code == OK, f'initialize failed: {initialize_response.status_code}'

    session_id = initialize_response.headers['Mcp-Session-Id']
    headers['Mcp-Session-Id'] = session_id

    body = json.dumps({
        'jsonrpc': '2.0',
        'method': 'tools/call',
        'id': 2,
        'params': {'name': _Echo_Service, 'arguments': arguments},
    })

    response = requests.post(url, data=body, headers=headers, auth=auth, timeout=10)
    assert response.status_code == OK, f'tools/call failed: {response.status_code}: {response.text}'

    data = response.json()

    out = data['result']
    return out

# ################################################################################################################################

def _get_text(result:'anydict') -> 'str':
    """ Extracts the text of the first content element of a tools/call result.
    """

    content = result['content']
    first_content = content[0]

    out = first_content['text']
    return out

# ################################################################################################################################

def _wait_until_authenticated(server_port:'int', url_path:'str', auth:'anytuple') -> 'None':
    """ Polls the gateway with an initialize request until the group membership added via the UI
    reaches live enforcement and the credentials are accepted.
    """

    url = f'http://127.0.0.1:{server_port}{url_path}'
    headers = {'Content-Type': 'application/json'}
    body = make_jsonrpc_initialize()

    deadline = time.monotonic() + _Propagation_Timeout

    while True:
        response = requests.post(url, data=body, headers=headers, auth=auth, timeout=10)

        # Stop as soon as the credentials go through ..
        if response.status_code == OK:
            return

        # .. or fail loudly when the deadline passes.
        if time.monotonic() >= deadline:
            raise Exception(f'Credentials were not accepted within {_Propagation_Timeout}s, ' + \
                f'last status: {response.status_code}, body: {response.text}')

        time.sleep(_Propagation_Poll_Interval)

# ################################################################################################################################

def _wait_until_rejected_as_too_large(server_port:'int', url_path:'str', auth:'anytuple', arguments:'anydict') -> 'anydict':
    """ Polls the gateway with an oversized call until block mode, configured via the UI a moment earlier,
    starts refusing it. Returns the refusing result.
    """

    deadline = time.monotonic() + _Propagation_Timeout

    while True:
        out = _call_echo(server_port, url_path, auth, arguments)

        # Stop as soon as the response is refused ..
        if 'isError' in out:
            return out

        # .. or fail loudly when the deadline passes.
        if time.monotonic() >= deadline:
            raise Exception(f'Block mode did not take effect within {_Propagation_Timeout}s, last result: {out}')

        time.sleep(_Propagation_Poll_Interval)

# ################################################################################################################################

def _wait_until_gone(server_port:'int', url_path:'str', auth:'anytuple') -> 'None':
    """ Polls the gateway with an initialize request until the deletion made via the UI
    reaches the live server and the URL path stops being routable.
    """

    url = f'http://127.0.0.1:{server_port}{url_path}'
    headers = {'Content-Type': 'application/json'}
    body = make_jsonrpc_initialize()

    deadline = time.monotonic() + _Propagation_Timeout

    while True:
        response = requests.post(url, data=body, headers=headers, auth=auth, timeout=10)

        # Stop as soon as the path stops answering ..
        if response.status_code == NOT_FOUND:
            return

        # .. or fail loudly when the deadline passes.
        if time.monotonic() >= deadline:
            raise Exception(f'The gateway still answers {_Propagation_Timeout}s after its deletion, ' + \
                f'last status: {response.status_code}')

        time.sleep(_Propagation_Poll_Interval)

# ################################################################################################################################

def _make_rows(count:'int') -> 'dictlist':
    """ Builds this many invoice-like rows for oversized echo requests.
    """
    out:'dictlist' = []

    for index in range(count):
        row = {'id': f'inv-{index:05}', 'customer': 'Customer name here'}
        out.append(row)

    return out

# ################################################################################################################################

def _review_group_selector(group_label:'str') -> 'str':
    """ Where one group of the review step is - each group is headed by its label.
    """
    out = f'#mcp-wizard-review .wizard-review-group:has(.wizard-review-group-label:text-is("{group_label}"))'
    return out

# ################################################################################################################################

def _get_review_group_text(page:'Page', group_label:'str') -> 'str':
    """ Everything one review group currently says, keys and values alike.
    """
    out = page.inner_text(_review_group_selector(group_label))
    return out

# ################################################################################################################################

def _get_review_value(page:'Page', group_label:'str', row_key:'str') -> 'str':
    """ What one review row answers - the value beside the given key in the given group.
    """
    group = _review_group_selector(group_label)
    row = f'{group} .wizard-review-row:has(.wizard-review-key:text-is("{row_key}"))'

    out = page.inner_text(f'{row} .wizard-review-value')
    return out

# ################################################################################################################################

def _click_review_edit(page:'Page', group_label:'str') -> 'None':
    """ Clicks the Edit link of one review group, which goes back to the step
    the group's answers came from and opens whatever holds them.
    """
    page.click(f'{_review_group_selector(group_label)} .wizard-review-edit')

# ################################################################################################################################

def _attempt_refused_save(page:'Page') -> 'None':
    """ Clicks Save on the review of a create that cannot go through and asserts
    that no confirmation shows and the wizard stays on its page.
    """

    wizard_page.go_to_step(page, wizard_page.Review_Step)
    page.click('#mcp-wizard-next')

    page.wait_for_timeout(_Refusal_Wait)

    saved_visible = page.is_visible(f'text="{wizard_page.Saved_Label}"')
    assert not saved_visible, 'Expected no save confirmation for a refused save'

    wizard_visible = page.is_visible('#mcp-wizard')
    assert wizard_visible, 'Expected the wizard to remain open after a refused save'

# ################################################################################################################################
# ################################################################################################################################

class TestMCPWizard:
    """ End-to-end tests for the MCP gateway wizard itself - realistic gateways built through
    every control the wizard offers, asserted both on the review step and against the live gateway.
    """

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Group_Log_Patterns)
    def test_full_create_edit_delete(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The whole of the wizard in one realistic gateway - services, a skill seeded on disk
        and security assigned through their cards, size caps, compaction and gateway options set
        through their popovers, PII enabled with lands, detectors and an exclusion, content safety
        on with allowed hosts as chips. The review names it all, the save works, the live gateway
        strips nulls and trims to the cap, the edit reopens everything prefilled, block mode set
        through the edit starts refusing oversized responses, and the delete takes it all down.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']
        server_dir = zato_dashboard['server_dir']

        gateway_name = _Test_Name_Prefix + 'full'
        url_path = '/mcp/wizard-full/' + rand_string()
        skill_name = 'test-mcp-wizard-skill-' + rand_string()

        # Create the credentials the MCP client will use ..
        security_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'full')
        security_name = security_info['name']
        auth = (security_info['username'], security_info['password'])

        # .. seed a skill on disk - the picker reads them from the server's config/repo ..
        skill_directory = _seed_skill(server_dir, skill_name)

        try:

            # Step 1 - the name, the path and the three picker cards ..
            wizard_page.open_wizard_create(page, base_url)

            page.fill('#id_name', gateway_name)
            page.fill('#id_url_path', url_path)

            wizard_page.assign_badge(page, 'services', _Echo_Service)
            wizard_page.assign_badge(page, 'skills', skill_name)
            wizard_page.assign_badge(page, 'security', security_name)

            # Step 2 - the size caps popover ..
            wizard_page.go_to_step(page, 1)
            wizard_page.set_size_caps(page, max_response_size=_Max_Response_Tokens)

            # .. the gateway options and compaction popovers behind More options ..
            wizard_page.set_gateway_options(page, is_audit_log_active=True)
            wizard_page.set_compaction(page, strip_nulls=True)

            # .. PII removal - the master toggle enables the selects under it ..
            wizard_page.open_pii_card(page)
            page.check('#id_safeguards_pii_enabled')

            wizard_page.pick_from_chosen(page, 'safeguards_pii_lands', 'Poland')
            wizard_page.pick_from_chosen(page, 'safeguards_pii_lands', 'Germany')

            wizard_page.pick_from_chosen(page, 'safeguards_pii_detectors', 'Email address')
            wizard_page.pick_from_chosen(page, 'safeguards_pii_detectors', 'Mobile equipment identity (IMEI)')

            wizard_page.pick_from_chosen(page, 'safeguards_pii_exclude', 'IPv4 address')

            # .. content safety - each group opens on its own, each master toggle
            # enables the fields under it ..
            wizard_page.open_safety_group(page, 'Unicode')
            page.check('#id_safeguards_normalize_unicode')

            wizard_page.open_safety_group(page, 'Markup')
            page.check('#id_safeguards_sanitize_markup')

            wizard_page.open_safety_group(page, 'URL policy')
            page.check('#id_safeguards_url_policy_enabled')

            wizard_page.add_host_chip(page, 'example.com')
            wizard_page.add_host_chip(page, 'zato.io')

            # The review names every group with the values chosen ..
            wizard_page.go_to_step(page, wizard_page.Review_Step)

            basics_text = _get_review_group_text(page, 'Basics')
            assert gateway_name in basics_text, f'Expected the name on the review, got: {basics_text}'
            assert url_path in basics_text, f'Expected the URL path on the review, got: {basics_text}'

            services_text = _get_review_group_text(page, 'Services')
            assert _Echo_Service in services_text, f'Expected {_Echo_Service} on the review, got: {services_text}'

            skills_text = _get_review_group_text(page, 'Skills')
            assert skill_name in skills_text, f'Expected {skill_name} on the review, got: {skills_text}'

            security_text = _get_review_group_text(page, 'Security')
            assert security_name in security_text, f'Expected {security_name} on the review, got: {security_text}'

            shaping_text = _get_review_group_text(page, 'Response shaping')
            assert f'{_Max_Response_Tokens} tokens max' in shaping_text, \
                f'Expected the cap on the review, got: {shaping_text}'

            audit_log_value = _get_review_value(page, 'Gateway options', 'Audit log')
            assert audit_log_value == 'On', f'Expected the audit log on the review, got: {audit_log_value}'

            strip_nulls_value = _get_review_value(page, 'Compaction', 'Strip null fields')
            assert strip_nulls_value == 'On', f'Expected null stripping on the review, got: {strip_nulls_value}'

            pii_enabled_value = _get_review_value(page, 'PII removal', 'Enabled')
            assert pii_enabled_value == 'Yes', f'Expected PII enabled on the review, got: {pii_enabled_value}'

            pii_text = _get_review_group_text(page, 'PII removal')
            assert 'Poland' in pii_text, f'Expected Poland on the review, got: {pii_text}'
            assert 'Germany' in pii_text, f'Expected Germany on the review, got: {pii_text}'
            assert 'Email address' in pii_text, f'Expected the email detector on the review, got: {pii_text}'
            assert 'Mobile equipment identity (IMEI)' in pii_text, \
                f'Expected the IMEI detector on the review, got: {pii_text}'
            assert 'IPv4 address' in pii_text, f'Expected the exclusion on the review, got: {pii_text}'

            unicode_value = _get_review_value(page, 'Content safety', 'Unicode')
            assert unicode_value != 'Off', f'Expected the Unicode check on, got: {unicode_value}'

            markup_value = _get_review_value(page, 'Content safety', 'Markup')
            assert markup_value != 'Off', f'Expected the Markup check on, got: {markup_value}'

            url_policy_value = _get_review_value(page, 'Content safety', 'URL policy')
            assert '2 hosts allowed' in url_policy_value, \
                f'Expected the two hosts on the review, got: {url_policy_value}'

            # .. the save works ..
            wizard_page.save_create(page)

            # .. and the row is on the list.
            _ = wizard_page.go_to_list(page, base_url, gateway_name)
            item_id = wizard_page.get_gateway_id(page, gateway_name)

            # The live gateway authenticates the assigned definition ..
            _wait_until_authenticated(server_port, url_path, auth)

            # .. null stripping runs live - null keys disappear while real values survive ..
            result = _call_echo(server_port, url_path, auth,
                {'customer': 'Customer name here', 'middle_name': None, 'fax': None})
            echoed = json.loads(_get_text(result))

            assert 'isError' not in result, f'Expected no error, got: {result}'
            assert echoed == {'customer': 'Customer name here'}, f'Expected nulls to be stripped, got: {echoed}'

            # .. and so does the token cap - an oversized response is gracefully trimmed to fit.
            result = _call_echo(server_port, url_path, auth, {'status': 'ok', 'rows': _make_rows(_Oversized_Row_Count)})
            echoed = json.loads(_get_text(result))

            assert 'isError' not in result, f'Expected no error, got: {result}'
            assert echoed['status'] == 'ok', f'Expected the scalar field to survive, got: {echoed}'
            assert len(echoed['rows']) < _Oversized_Row_Count, f'Expected fewer than {_Oversized_Row_Count} rows'

            # The edit reopens everything prefilled under the edit- prefix ..
            wizard_page.open_wizard_edit(page, base_url, gateway_name)

            name_value = page.input_value('#id_edit-name')
            assert name_value == gateway_name, f'Expected the name prefilled, got: {name_value}'

            url_path_value = page.input_value('#id_edit-url_path')
            assert url_path_value == url_path, f'Expected the URL path prefilled, got: {url_path_value}'

            assigned_services = wizard_page.get_assigned_badge_names(page, 'services')
            assert _Echo_Service in assigned_services, f'Expected {_Echo_Service} assigned, got: {assigned_services}'

            assigned_skills = wizard_page.get_assigned_badge_names(page, 'skills')
            assert skill_name in assigned_skills, f'Expected {skill_name} assigned, got: {assigned_skills}'

            assigned_security = wizard_page.get_assigned_badge_names(page, 'security')
            assert security_name in assigned_security, f'Expected {security_name} assigned, got: {assigned_security}'

            max_response_size = page.input_value('#id_edit-max_response_size')
            assert max_response_size == _Max_Response_Tokens, \
                f'Expected the cap prefilled, got: {max_response_size}'

            assert page.is_checked('#id_edit-safeguards_strip_nulls'), 'Expected null stripping prefilled'
            assert page.is_checked('#id_edit-is_audit_log_active'), 'Expected the audit log prefilled'
            assert page.is_checked('#id_edit-safeguards_pii_enabled'), 'Expected PII prefilled'

            lands = wizard_page.get_multi_select_values(page, 'safeguards_pii_lands', is_edit=True)
            assert sorted(lands) == ['de', 'pl'], f'Expected the lands prefilled, got: {lands}'

            detectors = wizard_page.get_multi_select_values(page, 'safeguards_pii_detectors', is_edit=True)
            assert sorted(detectors) == ['intl_email', 'intl_imei'], f'Expected the detectors prefilled, got: {detectors}'

            exclude = wizard_page.get_multi_select_values(page, 'safeguards_pii_exclude', is_edit=True)
            assert exclude == ['intl_ipv4'], f'Expected the exclusion prefilled, got: {exclude}'

            assert page.is_checked('#id_edit-safeguards_normalize_unicode'), 'Expected the Unicode check prefilled'
            assert page.is_checked('#id_edit-safeguards_sanitize_markup'), 'Expected the Markup check prefilled'
            assert page.is_checked('#id_edit-safeguards_url_policy_enabled'), 'Expected the URL policy prefilled'

            # .. the stored comma-separated hosts come back as chips ..
            wizard_page.go_to_step(page, 1)
            wizard_page.open_safety_group(page, 'URL policy')

            chips = wizard_page.get_host_chip_texts(page)
            assert chips == ['example.com', 'zato.io'], f'Expected the hosts back as chips, got: {chips}'

            # .. switching the cap to block mode through the edit ..
            wizard_page.set_size_caps(page, size_cap_mode='block')
            wizard_page.save_edit(page)

            # .. makes the gateway refuse an oversized response outright, naming the size and the cap.
            result = _wait_until_rejected_as_too_large(
                server_port, url_path, auth, {'status': 'ok', 'rows': _make_rows(_Oversized_Row_Count)})

            text = _get_text(result)
            assert 'Response too large:' in text, f'Expected a size refusal, got: {text}'
            assert f'cap is {_Max_Response_Tokens}' in text, f'Expected the cap to be named, got: {text}'

            # The delete goes through the list page row ..
            _ = wizard_page.go_to_list(page, base_url, gateway_name)

            page.evaluate(f'$.fn.zato.gateway.mcp.delete_("{item_id}")')
            _ = page.wait_for_selector('#popup_container', state='visible', timeout=_UI_Timeout)
            page.click('#popup_ok')
            _ = page.wait_for_selector(wizard_page.row_selector(gateway_name), state='hidden', timeout=_UI_Timeout)

            # .. and the gateway stops answering.
            _wait_until_gone(server_port, url_path, auth)

        finally:
            shutil.rmtree(skill_directory, ignore_errors=True)

# ################################################################################################################################

    def test_picker_cards(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The step 1 picker cards - collapsed on open, their summaries walking from None assigned
        to 2 assigned as badges move, and the review's Edit links opening the right card.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wizard_page.open_wizard_create(page, base_url)

        # Every picker card is collapsed on open ..
        for card_name in ('services', 'skills', 'security'):
            is_open = page.evaluate(
                f'document.getElementById("mcp-wizard-{card_name}-body").classList.contains("wizard-option-body-open")')
            assert not is_open, f'Expected the {card_name} card collapsed on open'

        # .. and each summary says nothing is assigned yet.
        summary = wizard_page.get_picker_summary(page, 'services')
        assert summary == 'None assigned', f'Expected "None assigned", got: {summary}'

        # Assigning walks the summary to the count ..
        wizard_page.open_picker_card(page, 'services')
        wizard_page.wait_for_available_badges(page, 'services', 2)

        available_names = wizard_page.get_available_badge_names(page, 'services')
        service_name_1 = available_names[0]
        service_name_2 = available_names[1]

        wizard_page.assign_badge(page, 'services', service_name_1)

        summary = wizard_page.get_picker_summary(page, 'services')
        assert summary == '1 assigned', f'Expected "1 assigned", got: {summary}'

        wizard_page.assign_badge(page, 'services', service_name_2)

        summary = wizard_page.get_picker_summary(page, 'services')
        assert summary == '2 assigned', f'Expected "2 assigned", got: {summary}'

        # .. and removing walks it back.
        wizard_page.remove_assigned_badge(page, 'services', service_name_1)

        summary = wizard_page.get_picker_summary(page, 'services')
        assert summary == '1 assigned', f'Expected "1 assigned" after removal, got: {summary}'

        # The review's Edit link on the Services group goes back to step 1 with the card open ..
        wizard_page.go_to_step(page, wizard_page.Review_Step)
        _click_review_edit(page, 'Services')

        _ = page.wait_for_selector('#mcp-wizard-step-body-0', state='visible', timeout=_UI_Timeout)

        is_open = page.evaluate(
            'document.getElementById("mcp-wizard-services-body").classList.contains("wizard-option-body-open")')
        assert is_open, 'Expected the services card open after the review edit link'

        # .. and the PII group's link goes to step 2 with the options unfolded and the PII card open.
        wizard_page.go_to_step(page, wizard_page.Review_Step)
        _click_review_edit(page, 'PII removal')

        _ = page.wait_for_selector('#mcp-wizard-step-body-1', state='visible', timeout=_UI_Timeout)

        options_hidden = page.evaluate('document.getElementById("mcp-wizard-options-body").hidden')
        assert not options_hidden, 'Expected the options unfolded after the review edit link'

        is_open = page.evaluate(
            'document.getElementById("mcp-wizard-pii-body").classList.contains("wizard-option-body-open")')
        assert is_open, 'Expected the PII card open after the review edit link'

# ################################################################################################################################

    def test_allowed_hosts_chips(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The allowed hosts chips - Enter and comma add, a pasted comma list splits, duplicates
        are ignored, the close mark and Backspace remove, blur commits, and the stored value
        round-trips into chips on edit.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        gateway_name = _Test_Name_Prefix + 'chips'
        url_path = '/mcp/wizard-chips/' + rand_string()

        wizard_page.open_wizard_create(page, base_url)

        page.fill('#id_name', gateway_name)
        page.fill('#id_url_path', url_path)

        # The chips live in the URL policy group and stay disabled until the policy is on ..
        wizard_page.go_to_step(page, 1)
        wizard_page.open_safety_group(page, 'URL policy')
        page.check('#id_safeguards_url_policy_enabled')

        text_field = f'{wizard_page.Host_List_Selector} .search-field input'

        # .. Enter adds what was typed ..
        wizard_page.add_host_chip(page, 'example.com')

        # .. and so does a comma ..
        wizard_page.type_into_host_field(page, 'zato.io')
        page.press(text_field, ',')

        chips = wizard_page.get_host_chip_texts(page)
        assert chips == ['example.com', 'zato.io'], f'Expected two chips, got: {chips}'

        # .. a pasted comma list splits into one chip per host ..
        wizard_page.type_into_host_field(page, 'a.example.com, b.example.com')
        page.press(text_field, 'Enter')

        chips = wizard_page.get_host_chip_texts(page)
        assert chips == ['example.com', 'zato.io', 'a.example.com', 'b.example.com'], \
            f'Expected the pasted list split, got: {chips}'

        # .. a duplicate is ignored ..
        wizard_page.type_into_host_field(page, 'example.com')
        page.press(text_field, 'Enter')

        chips = wizard_page.get_host_chip_texts(page)
        assert chips == ['example.com', 'zato.io', 'a.example.com', 'b.example.com'], \
            f'Expected the duplicate ignored, got: {chips}'

        # .. the close mark removes its chip ..
        wizard_page.remove_host_chip(page, 'b.example.com')

        chips = wizard_page.get_host_chip_texts(page)
        assert chips == ['example.com', 'zato.io', 'a.example.com'], f'Expected the chip removed, got: {chips}'

        # .. Backspace in the empty field takes the last chip back ..
        page.click(text_field)
        page.press(text_field, 'Backspace')

        chips = wizard_page.get_host_chip_texts(page)
        assert chips == ['example.com', 'zato.io'], f'Expected the last chip removed, got: {chips}'

        # .. and leaving the field commits what was typed there.
        wizard_page.type_into_host_field(page, 'blur.example.com')
        page.click('#mcp-wizard-safety-header')

        chip = f'{wizard_page.Host_List_Selector} li.search-choice:has-text("blur.example.com")'
        _ = page.wait_for_selector(chip, state='visible', timeout=_UI_Timeout)

        # The underlying input carries the whole list as one comma-separated line ..
        stored_value = page.input_value('#id_safeguards_url_allow_list')
        assert stored_value == 'example.com, zato.io, blur.example.com', \
            f'Expected the comma-separated line, got: {stored_value}'

        # .. the save goes through ..
        wizard_page.save_create(page)

        # .. and the stored value round-trips into chips on edit.
        wizard_page.open_wizard_edit(page, base_url, gateway_name)

        wizard_page.go_to_step(page, 1)
        wizard_page.open_safety_group(page, 'URL policy')

        chips = wizard_page.get_host_chip_texts(page)
        assert chips == ['example.com', 'zato.io', 'blur.example.com'], \
            f'Expected the hosts back as chips on edit, got: {chips}'

# ################################################################################################################################

    def test_validation(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A save with no name or no URL path is refused with the review naming the missing field,
        and a duplicate name is refused by the uniqueness check.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        gateway_name = _Test_Name_Prefix + 'validation'
        url_path = '/mcp/wizard-validation/' + rand_string()

        # With no name, the review's Basics group says the name is missing ..
        wizard_page.open_wizard_create(page, base_url)
        page.fill('#id_url_path', url_path)

        wizard_page.go_to_step(page, wizard_page.Review_Step)

        basics_selector = _review_group_selector('Basics')
        missing = page.query_selector(f'{basics_selector} .wizard-review-missing')
        assert missing is not None, 'Expected the Basics group to say the name is missing'

        name_value = _get_review_value(page, 'Basics', 'Name')
        assert name_value == 'Missing', f'Expected the name named as missing, got: {name_value}'

        # .. and the save is refused, leaving the wizard on the review step.
        _attempt_refused_save(page)

        # With a name but no URL path, the review says so too - the fields
        # live on step 1, so the wizard walks back there first ..
        wizard_page.go_to_step(page, 0)

        page.fill('#id_name', gateway_name)
        page.fill('#id_url_path', '')

        wizard_page.go_to_step(page, wizard_page.Review_Step)

        url_path_value = _get_review_value(page, 'Basics', 'URL path')
        assert url_path_value == 'Missing', f'Expected the URL path named as missing, got: {url_path_value}'

        # .. and the save is refused again.
        _attempt_refused_save(page)

        # With both answered, the save goes through ..
        wizard_page.go_to_step(page, 0)
        page.fill('#id_url_path', url_path)

        wizard_page.save_create(page)

        # .. and a second gateway with the same name is refused by the uniqueness check.
        wizard_page.open_wizard_create(page, base_url)

        page.fill('#id_name', gateway_name)
        page.fill('#id_url_path', '/mcp/wizard-validation-dup/' + rand_string())

        _ = page.wait_for_selector('.zato-unique-taken', state='visible', timeout=_UI_Timeout)

        _attempt_refused_save(page)

# ################################################################################################################################
# ################################################################################################################################
