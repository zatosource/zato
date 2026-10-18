# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys

# Zato
from zato.common.test import rand_string
from zato.common.util.safeguards.masking import get_masking_config

# Zato - test helpers - the wizard drivers live next to the tests
_this_directory = os.path.dirname(__file__)

if _this_directory not in sys.path:
    sys.path.insert(0, _this_directory)

import _mcp_wizard as wizard_page
import _mcp_wizard_masking as masking_page

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_test_name_prefix = 'test.mcp.masking.' + rand_string() + '.'

# The service every gateway in this suite exposes
_echo_service = 'demo.echo'

# The sets the round trip picks, in the order it picks them, and the field it leaves out of the first one
_picked_sets = ['banking', 'healthcare']
_excluded_field = 'iban'

# A field listed by the Common set and one other set only, the set every card search starts from,
# a field Common and Banking both list and one Banking lists and Common does not
_common_set = 'common'
_shared_field = 'last_ip'
_shared_field_banking = 'email'
_banking_only_field = 'bic'

# The custom fields the round trip masks, one in a case of its own
_custom_fields = ['customer.loyalty_id', 'Loyalty_Tier']

# What the review and the line of the section say about the masked fields
_review_group = 'PII and data masking'
_review_row = 'Data masking'
_no_fields = 'No fields'
_custom_label = 'Custom'

# How many masked fields the review names before it counts the rest
_review_name_limit = 12

# ################################################################################################################################
# ################################################################################################################################

def _holds(field_list:'strlist', name:'str') -> 'bool':
    name_lower = name.lower()

    for field_name in field_list:
        if field_name.lower() == name_lower:
            return True

    return False

# ################################################################################################################################

def _expected_masked_fields(sets:'strlist', excluded:'strlist', custom_fields:'strlist') -> 'strlist':
    """ Every field the wizard reports as masked, in its order - the fields of the sets less the excluded ones,
    then the custom fields, each field once without regard to case.
    """
    fields_by_set = {item['name']: item['fields'] for item in get_masking_config()}

    out:'strlist' = []

    for set_name in sets:
        for field_name in fields_by_set[set_name]:
            if not _holds(out, field_name) and not _holds(excluded, field_name):
                out.append(field_name)

    for field_name in custom_fields:
        if not _holds(out, field_name):
            out.append(field_name)

    return out

# ################################################################################################################################

def _expected_summary(sets:'strlist', excluded:'strlist', custom_fields:'strlist') -> 'str':
    """ What the data masking line says - each set by label with how many of its fields are masked,
    then Custom with the number of the custom fields.
    """
    sets_by_name = {item['name']: item for item in get_masking_config()}
    parts:'strlist' = []

    for set_name in sets:
        item = sets_by_name[set_name]
        masked_count = 0

        for field_name in item['fields']:
            if not _holds(excluded, field_name):
                masked_count += 1

        parts.append(f'{item["label"]} ({masked_count})')

    parts.append(f'{_custom_label} ({len(custom_fields)})')

    out = ', '.join(parts)
    return out

# ################################################################################################################################

def _expected_review_value(masked_fields:'strlist') -> 'str':
    """ What the review row says - the first names of the masked fields and how many follow them.
    """
    shown = masked_fields[:_review_name_limit]
    rest_count = len(masked_fields) - len(shown)

    out = ', '.join(shown)

    if rest_count:
        out += f' and {rest_count} more'

    return out

# ################################################################################################################################

def _assert_stored(
    zato_dashboard:'anydict',
    gateway_name:'str',
    sets:'strlist',
    excluded:'strlist',
    custom_fields:'strlist',
    is_custom_enabled:'bool',
    ) -> 'None':
    """ Reads the gateway back through the admin API and checks the four data masking keys it stores.
    """
    stored = masking_page.get_stored_gateway(zato_dashboard, gateway_name)

    assert stored['safeguards_masking_sets'] == sets, stored
    assert stored['safeguards_masking_excluded'] == excluded, stored
    assert stored['safeguards_masking_custom_fields'] == custom_fields, stored
    assert stored['safeguards_masking_custom_enabled'] is is_custom_enabled, stored

# ################################################################################################################################
# ################################################################################################################################

class TestMCPWizardMasking:
    """ The data masking popover of the MCP gateway wizard - the industry sets it offers, the answers
    it stores on create and on edit, and the state it restores when the gateway is opened again.
    """

    def test_the_popover_offers_every_set(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The popover shows one card per industry set, in the order and with the labels of the set files.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wizard_page.open_wizard_create(page, base_url)
        wizard_page.go_to_step(page, 1)

        masking_page.open_masking_popover(page)

        shown = masking_page.get_popover_sets(page)
        expected = [[item['name'], item['label']] for item in get_masking_config()]

        assert shown == expected, shown

        # A new gateway masks nothing, its custom fields switched on for when it is given some
        for set_name, _ in expected:
            assert not masking_page.is_card_on(page, set_name), set_name

        assert masking_page.is_card_on(page, masking_page.Custom_Key)

# ################################################################################################################################

    def test_the_search_shows_the_matching_fields_of_every_set(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The pane shows the fields of every set that match the search, each once, a card clicked shows its own matching fields,
        and the clear button returns the pane to that card with all of its fields.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        set_name = _picked_sets[0]
        all_sets = get_masking_config()
        set_fields = [item['fields'] for item in all_sets if item['name'] == set_name][0]

        expected:'strlist' = []

        for item in all_sets:
            for field_name in item['fields']:
                if _shared_field_banking in field_name.lower() and field_name.lower() not in [name.lower() for name in expected]:
                    expected.append(field_name)

        wizard_page.open_wizard_create(page, base_url)
        wizard_page.go_to_step(page, 1)

        masking_page.open_masking_popover(page)

        masking_page.search_fields(page, _shared_field_banking.upper())
        shown = masking_page.get_shown_fields(page)

        assert shown == expected, shown

        masking_page.focus_card(page, set_name)
        shown = masking_page.get_shown_fields(page)

        assert shown == [field_name for field_name in set_fields if _shared_field_banking in field_name.lower()], shown

        masking_page.clear_search(page)
        shown = masking_page.get_shown_fields(page)

        assert shown == set_fields, shown

# ################################################################################################################################

    def test_the_search_narrows_the_cards(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The search leaves in only the cards of the sets listing a matching field, and its clear button brings back all of them.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        all_sets = get_masking_config()
        listing = [item['name'] for item in all_sets if _shared_field in item['fields']]

        wizard_page.open_wizard_create(page, base_url)
        wizard_page.go_to_step(page, 1)

        masking_page.open_masking_popover(page)

        masking_page.search_fields(page, _shared_field)
        shown = masking_page.get_shown_cards(page)

        assert shown == listing, shown

        masking_page.clear_search(page)
        shown = masking_page.get_shown_cards(page)

        assert shown == [masking_page.Custom_Key] + [item['name'] for item in all_sets], shown

# ################################################################################################################################

    def test_show_only_active_shows_the_fields_masked_when_it_is_switched_on(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Show only active leaves in the fields masked at the moment it is switched on, keeps a field switched off after that
        in sight, and lets it go once it is switched on again.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        set_name = _picked_sets[0]
        set_fields = [item['fields'] for item in get_masking_config() if item['name'] == set_name][0]

        wizard_page.open_wizard_create(page, base_url)
        wizard_page.go_to_step(page, 1)

        masking_page.open_masking_popover(page)
        masking_page.toggle_card(page, set_name)
        masking_page.focus_card(page, set_name)
        masking_page.toggle_field(page, _excluded_field)

        masking_page.toggle_show_only_active(page)
        shown = masking_page.get_shown_fields(page)

        assert shown == [field_name for field_name in set_fields if field_name != _excluded_field], shown

        masking_page.toggle_field(page, _banking_only_field)
        shown = masking_page.get_shown_fields(page)

        assert _banking_only_field in shown, shown

        masking_page.toggle_show_only_active(page)
        masking_page.toggle_show_only_active(page)
        shown = masking_page.get_shown_fields(page)

        assert _banking_only_field not in shown, shown

        masking_page.toggle_show_only_active(page)
        shown = masking_page.get_shown_fields(page)

        assert shown == set_fields, shown

# ################################################################################################################################

    def test_a_field_of_another_set_keeps_the_shared_fields_masked(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A field is masked or not whichever set's pane shows it - with one set picked, its fields are masked in the pane
        of a set not picked, and switching on a single field there picks that set without unmasking the fields both list.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wizard_page.open_wizard_create(page, base_url)
        wizard_page.go_to_step(page, 1)

        masking_page.open_masking_popover(page)
        masking_page.toggle_card(page, _common_set)

        masking_page.focus_card(page, _picked_sets[0])

        assert masking_page.is_field_masked(page, _shared_field_banking)
        assert not masking_page.is_field_masked(page, _excluded_field)

        masking_page.toggle_field(page, _excluded_field)

        assert masking_page.is_card_on(page, _picked_sets[0])
        assert masking_page.is_field_masked(page, _excluded_field)
        assert masking_page.is_field_masked(page, _shared_field_banking)
        assert not masking_page.is_field_masked(page, _banking_only_field)

        masking_page.focus_card(page, _common_set)
        assert masking_page.is_field_masked(page, _shared_field_banking)

# ################################################################################################################################

    def test_create_and_edit(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Sets, an excluded field and custom fields picked on create are stored, summarized, shown on the review
        and restored on edit, the custom fields can be switched off, and clearing every pick stores nothing.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        gateway_name = _test_name_prefix + 'round-trip'
        url_path = '/mcp/' + gateway_name

        masked_fields = _expected_masked_fields(_picked_sets, [_excluded_field], _custom_fields)
        expected_summary = _expected_summary(_picked_sets, [_excluded_field], _custom_fields)

        # Step 1 - the gateway's name, path and one service ..
        wizard_page.open_wizard_create(page, base_url)

        page.fill(wizard_page.field_selector('name'), gateway_name)
        page.fill(wizard_page.field_selector('url_path'), url_path)

        wizard_page.assign_badge(page, 'services', _echo_service)

        # .. step 2 - two sets, one field of the first left out, and the custom fields ..
        wizard_page.go_to_step(page, 1)
        masking_page.open_masking_popover(page)

        for set_name in _picked_sets:
            masking_page.toggle_card(page, set_name)

        masking_page.focus_card(page, _picked_sets[0])
        masking_page.toggle_field(page, _excluded_field)

        assert not masking_page.is_field_masked(page, _excluded_field)

        masking_page.set_custom_fields(page, _custom_fields)
        masking_page.accept_masking_popover(page)

        summary = masking_page.get_masking_summary(page)
        assert summary == expected_summary, summary

        # .. the review names the masked fields ..
        wizard_page.go_to_step(page, wizard_page.Review_Step)

        review_value = masking_page.get_review_value(page, _review_group, _review_row)
        assert review_value == _expected_review_value(masked_fields), review_value

        # .. and the save stores every answer.
        wizard_page.save_create(page)
        _assert_stored(zato_dashboard, gateway_name, _picked_sets, [_excluded_field], _custom_fields, True)

        # The edit wizard opens on the same answers ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        wizard_page.go_to_step(page, 1)
        masking_page.open_pii_section(page)

        summary = masking_page.get_masking_summary(page)
        assert summary == expected_summary, summary

        masking_page.open_masking_popover(page)

        for set_name in _picked_sets:
            assert masking_page.is_card_on(page, set_name), set_name

        masking_page.focus_card(page, _picked_sets[0])
        assert not masking_page.is_field_masked(page, _excluded_field)

        custom_text = masking_page.get_custom_fields_text(page)
        assert custom_text == '\n'.join(_custom_fields), custom_text

        # .. the custom fields switched off are kept, though no longer masked ..
        masking_page.toggle_card(page, masking_page.Custom_Key)
        masking_page.accept_masking_popover(page)

        wizard_page.save_edit(page)
        _assert_stored(zato_dashboard, gateway_name, _picked_sets, [_excluded_field], _custom_fields, False)

        # .. and clearing every pick stores none of them.
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        wizard_page.go_to_step(page, 1)
        masking_page.open_masking_popover(page)

        for set_name in _picked_sets:
            masking_page.toggle_card(page, set_name)

        masking_page.set_custom_fields(page, [])
        masking_page.toggle_card(page, masking_page.Custom_Key)
        masking_page.accept_masking_popover(page)

        summary = masking_page.get_masking_summary(page)
        assert summary == _no_fields, summary

        wizard_page.save_edit(page)
        _assert_stored(zato_dashboard, gateway_name, [], [], [], True)

# ################################################################################################################################
# ################################################################################################################################
