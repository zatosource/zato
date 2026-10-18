# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# requests
import requests

# Zato - test helpers
from _mcp_wizard import accept_popover, open_hooks_card, popover_input_selector

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# How long to wait for a section, the popover or a panel to show, in milliseconds
_wait_timeout = 10000

# How long an admin API call may take, in seconds
_request_timeout = 10

# The key of the custom fields' card in the popover
Custom_Key = 'custom'

# The hook kinds, each with a decision line of its own
Hook_Request  = 'request'
Hook_Response = 'response'

# Where the popover's parts are
_popup_selector  = '#mcp-wizard-popup'
_layout_selector = _popup_selector + ' .mcp-masking-layout'
_pane_selector   = _popup_selector + ' .mcp-masking-pane'

# ################################################################################################################################
# ################################################################################################################################
#
# The PII and data masking section
#
# ################################################################################################################################
# ################################################################################################################################

def open_pii_section(page:'Page') -> 'None':
    """ Unfolds the PII and data masking section of step 2, unless it is already open.
    """
    is_hidden = page.evaluate('document.getElementById("mcp-wizard-pii-body").hidden')

    if is_hidden:
        page.click('#mcp-wizard-pii-line')
        _ = page.wait_for_selector('#mcp-wizard-pii-body', state='visible', timeout=_wait_timeout)

# ################################################################################################################################

def get_masking_summary(page:'Page') -> 'str':
    """ What the data masking line of the section says.
    """
    out = page.inner_text('#mcp-wizard-summary-data-masking')
    return out

# ################################################################################################################################
# ################################################################################################################################
#
# The data masking popover
#
# ################################################################################################################################
# ################################################################################################################################

def _card_selector(key:'str') -> 'str':
    out = f'{_popup_selector} .mcp-masking-card[data-key="{key}"]'
    return out

# ################################################################################################################################

def _field_row_selector(field_name:'str') -> 'str':
    out = f'{_pane_selector} .mcp-masking-pane-field[data-field="{field_name}"]'
    return out

# ################################################################################################################################

def open_masking_popover(page:'Page') -> 'None':
    """ Opens the data masking popover from the line of the PII and data masking section.
    """
    open_pii_section(page)

    page.click('#mcp-wizard-edit-data-masking')
    _ = page.wait_for_selector(_layout_selector, state='visible', timeout=_wait_timeout)

# ################################################################################################################################

def accept_masking_popover(page:'Page') -> 'None':
    """ Accepts the popover, which writes its answers back to the wizard.
    """
    accept_popover(page)

# ################################################################################################################################

def get_popover_sets(page:'Page') -> 'list':
    """ The industry sets the popover shows, in order, each as a (name, label) pair.
    """
    out = page.evaluate(f'''Array.from(document.querySelectorAll('{_popup_selector} .mcp-masking-card'))
        .filter(card => card.getAttribute('data-key') !== '{Custom_Key}')
        .map(card => [card.getAttribute('data-key'), card.querySelector('.mcp-masking-card-title').textContent])''')

    return out

# ################################################################################################################################

def is_card_on(page:'Page', key:'str') -> 'bool':
    """ Whether a card's switch is on - a set picked, or the custom fields masked.
    """
    out = page.evaluate(
        f'''document.querySelector('{_card_selector(key)} .mcp-masking-switch').classList.contains('mcp-masking-switch-on')''')
    return out

# ################################################################################################################################

def toggle_card(page:'Page', key:'str') -> 'None':
    """ Flips the switch of a card - the whole of a set, or whether the custom fields are masked.
    """
    page.click(f'{_card_selector(key)} .mcp-masking-switch')

# ################################################################################################################################

def focus_card(page:'Page', key:'str') -> 'None':
    """ Shows a card in the pane - a set's fields, or the editor of the custom fields.
    """
    page.click(f'{_card_selector(key)} .mcp-masking-card-title')
    _ = page.wait_for_selector(f'{_card_selector(key)}.mcp-masking-card-focused', timeout=_wait_timeout)

# ################################################################################################################################

def search_fields(page:'Page', text:'str') -> 'None':
    """ Types into the search heading the cards.
    """
    page.fill(f'{_popup_selector} .mcp-search-box-input', text)

# ################################################################################################################################

def clear_search(page:'Page') -> 'None':
    """ Empties the search with its clear button.
    """
    page.click(f'{_popup_selector} .mcp-search-box-clear')

# ################################################################################################################################

def get_shown_cards(page:'Page') -> 'strlist':
    """ The keys of the cards the search leaves in, in order.
    """
    out = page.evaluate(f'''Array.from(document.querySelectorAll(
        '{_popup_selector} .mcp-masking-card:not(.mcp-masking-card-unmatched)'))
        .map(card => card.getAttribute('data-key'))''')

    return out

# ################################################################################################################################

def get_shown_fields(page:'Page') -> 'strlist':
    """ The fields the pane shows, in order - those of the focused set, or the results of the search across every set.
    """
    out = page.evaluate(f'''Array.from(document.querySelectorAll(
        '{_pane_selector} .mcp-masking-pane-field:not(.mcp-masking-filtered-out)'))
        .map(row => row.getAttribute('data-field'))''')

    return out

# ################################################################################################################################

def is_field_masked(page:'Page', field_name:'str') -> 'bool':
    """ Whether a field the pane shows has its switch on.
    """
    out = page.evaluate(f'''document.querySelector(
        '{_field_row_selector(field_name)} .mcp-masking-switch').classList.contains('mcp-masking-switch-on')''')
    return out

# ################################################################################################################################

def toggle_field(page:'Page', field_name:'str') -> 'None':
    """ Flips the switch of one field the pane shows.
    """
    page.click(_field_row_selector(field_name))

# ################################################################################################################################

def toggle_show_only_active(page:'Page') -> 'None':
    """ Flips the switch in the pane's header showing the masked fields alone.
    """
    page.click(f'{_pane_selector} .mcp-masking-pane-only')

# ################################################################################################################################

def set_custom_fields(page:'Page', field_names:'strlist') -> 'None':
    """ Writes the custom fields into their editor, one per line.
    """
    focus_card(page, Custom_Key)

    editor_selector = popover_input_selector('data_masking_custom_fields')
    page.fill(editor_selector, '\n'.join(field_names))

# ################################################################################################################################

def get_custom_fields_text(page:'Page') -> 'str':
    """ What the editor of the custom fields holds.
    """
    focus_card(page, Custom_Key)

    editor_selector = popover_input_selector('data_masking_custom_fields')

    out = page.input_value(editor_selector)
    return out

# ################################################################################################################################
# ################################################################################################################################
#
# The hook services card
#
# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################

def _chip_selector(kind:'str') -> 'str':
    out = f'#mcp-wizard-slot-{kind}-hook-chip'
    return out

# ################################################################################################################################

def get_hook_chip_text(page:'Page', kind:'str') -> 'str':
    """ What the chip of one hook says - the service it invokes, or that there is none.
    """
    out = page.inner_text(f'{_chip_selector(kind)} .decision-chip-value')
    return out

# ################################################################################################################################

def _open_hook_panel(page:'Page', kind:'str') -> 'None':
    open_hooks_card(page)

    page.click(_chip_selector(kind))
    _ = page.wait_for_selector('#decision-pick-panel', state='visible', timeout=_wait_timeout)

# ################################################################################################################################

def pick_hook(page:'Page', kind:'str', service_name:'str') -> 'None':
    """ Picks the service one hook invokes, filtering the panel's list down to it first.
    """
    _open_hook_panel(page, kind)

    page.fill('#decision-pick-panel-filter', service_name)
    page.click(f'#decision-pick-panel .decision-pick-row:has(.decision-pick-name:text-is("{service_name}"))')

    _ = page.wait_for_selector('#decision-pick-panel', state='detached', timeout=_wait_timeout)

# ################################################################################################################################

def remove_hook(page:'Page', kind:'str') -> 'None':
    """ Leaves one hook without a service - a click on the picked service is what removes it.
    """
    _open_hook_panel(page, kind)

    page.click('#decision-pick-panel .decision-pick-row:has(.decision-pick-dot-on)')
    _ = page.wait_for_selector('#decision-pick-panel', state='detached', timeout=_wait_timeout)

# ################################################################################################################################
# ################################################################################################################################
#
# The review step
#
# ################################################################################################################################
# ################################################################################################################################

def get_review_value(page:'Page', group_label:'str', row_key:'str') -> 'str':
    """ What one review row answers - the value beside the given key in the given group.
    """
    group = f'#mcp-wizard-review .wizard-review-group:has(.wizard-review-group-label:text-is("{group_label}"))'
    row = f'{group} .wizard-review-row:has(.wizard-review-key:text-is("{row_key}"))'

    out = page.inner_text(f'{row} .wizard-review-value')
    return out

# ################################################################################################################################
# ################################################################################################################################
#
# The stored gateway
#
# ################################################################################################################################
# ################################################################################################################################

def get_stored_gateway(zato_dashboard:'anydict', gateway_name:'str') -> 'anydict':
    """ Reads one gateway's stored definition through the admin API.
    """
    server_port = zato_dashboard['server_port']

    api_url = f'http://127.0.0.1:{server_port}/zato/api/invoke/zato.generic.connection.get-list'
    api_auth = ('admin.invoke', zato_dashboard['password'])
    api_headers = {'Content-Type': 'application/json'}
    api_payload = json.dumps({'type_': 'gateway-mcp'})

    response = requests.post(api_url, data=api_payload, headers=api_headers, auth=api_auth, timeout=_request_timeout)
    assert response.status_code == 200, f'API call failed: {response.status_code} {response.text}'

    for item in response.json():
        if item['name'] == gateway_name:
            return item

    raise Exception(f'Gateway `{gateway_name}` not found')

# ################################################################################################################################
# ################################################################################################################################
