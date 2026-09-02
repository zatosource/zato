# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# The action each step 1 picker card registers its badge picker under - the zone element ids derive from it
Picker_Actions = {
    'tools': 'wizard',
    'skills': 'skills-wizard',
    'security': 'sec-wizard',
}

# The sources the Tools card serves - each one is a leaf of the card's tree
# and all of them share the one badge picker registered under the tools action.
Tool_Source_Keys = {
    'services',
    'rest',
    'soap',
    'sql',
    'odoo',
    'sap',
    'confluence',
    'microsoft_365',
    'microsoft_fabric',
    'microsoft_power_automate',
    'microsoft_teams',
    'es',
}

# The card a tool source's badges live in
Tools_Card = 'tools'

# How long to wait for the Tools card and its tree, in milliseconds
_Wizard_Timeout = 10000

# ################################################################################################################################
# ################################################################################################################################

def _picker_action(card_name:'str') -> 'str':
    """ The picker action of a card - every tool source shares the Tools card's picker.
    """
    if card_name in Tool_Source_Keys:
        card_name = Tools_Card

    out = Picker_Actions[card_name]
    return out

# ################################################################################################################################

def tool_source_selector(source_key:'str') -> 'str':
    """ Where one source's row of the Tools card's tree is.
    """
    out = f'#mcp-wizard-tool-source-list .mcp-tool-source[data-key="{source_key}"]'
    return out

# ################################################################################################################################

def available_badge_selector(card_name:'str', badge_name:'str') -> 'str':
    """ Where one badge sits while it is still available - the picker lowercases each badge's data-name.
    """
    action = _picker_action(card_name)
    badge_name = badge_name.lower()

    out = f'#badge-zone-available-{action} .badge-zone-body .security-badge[data-name="{badge_name}"]'
    return out

# ################################################################################################################################

def assigned_badge_selector(card_name:'str', badge_name:'str') -> 'str':
    """ Where one badge sits once it is assigned.
    """
    action = _picker_action(card_name)
    badge_name = badge_name.lower()

    out = f'#badge-zone-assigned-{action} .badge-zone-body .security-badge[data-name="{badge_name}"]'
    return out

# ################################################################################################################################

def select_tool_source(page:'Page', source_key:'str') -> 'None':
    """ Puts one source's items on the Tools card's picker - opening the card,
    clicking the source's row in the tree and waiting until the row is the active one.
    """

    # The card itself must be open first - a collapsed card's tree cannot be clicked ..
    is_open = page.evaluate(
        f'document.getElementById("mcp-wizard-{Tools_Card}-body").classList.contains("wizard-option-body-open")')

    if not is_open:
        page.click(f'#mcp-wizard-{Tools_Card}-header')
        _ = page.wait_for_selector(f'#mcp-wizard-{Tools_Card}-body', state='visible', timeout=_Wizard_Timeout)

    # .. an already selected source needs no click ..
    row = tool_source_selector(source_key)
    active_row = f'{row}.mcp-tool-source-active'

    if page.query_selector(active_row):
        return

    # .. and the click puts the source's items on the picker synchronously.
    page.click(row)
    _ = page.wait_for_selector(active_row, state='attached', timeout=_Wizard_Timeout)

# ################################################################################################################################

def get_tool_source_keys(page:'Page') -> 'strlist':
    """ The keys of every source the Tools card's tree offers, in tree order -
    sources with nothing to offer are pruned and never appear.
    """
    rows = page.query_selector_all('#mcp-wizard-tool-source-list .mcp-tool-source')

    out:'strlist' = []

    for row in rows:
        key = row.get_attribute('data-key')
        key = cast_('str', key)
        out.append(key)

    return out

# ################################################################################################################################

def get_tool_source_count(page:'Page', source_key:'str') -> 'str':
    """ What one source's row of the tree says about its assigned count -
    an empty string while the source holds no picks.
    """
    row = tool_source_selector(source_key)

    out = page.inner_text(f'{row} .mcp-tool-source-count')
    out = out.strip()
    return out

# ################################################################################################################################
# ################################################################################################################################
