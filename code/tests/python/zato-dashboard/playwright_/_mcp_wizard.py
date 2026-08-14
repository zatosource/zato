# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# Zato
from zato.common.test.playwright_pubsub import navigate_to_page
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anylistnone, boolnone, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

# Where the gateway list lives - the wizard is reached through its links
MCP_List_URL = '/zato/gateway/mcp/?cluster=1'

# What the tooltip beside the button says once a wizard save went through
Saved_Label = 'OK, saved'

# The action each step 1 picker card registers its badge picker under - the zone element ids derive from it
Picker_Actions = {
    'services': 'wizard',
    'skills': 'skills-wizard',
    'security': 'sec-wizard',
}

# The step a create ends on - the review, where Next says Save
Review_Step = 2

# How long to wait for the wizard page and its pickers, in milliseconds
_Wizard_Timeout = 10000

# How long to wait for a save to be confirmed, in milliseconds
_Save_Timeout = 15000

# How long to wait after an option click for Chosen to settle, in milliseconds -
# focusing the search field makes Chosen reopen the dropdown 50 ms later.
_Chosen_Settle_Time = 60

# ################################################################################################################################
# ################################################################################################################################
#
# Selectors
#
# ################################################################################################################################
# ################################################################################################################################

def field_selector(name:'str', is_edit:'bool'=False) -> 'str':
    """ Where one field of the wizard's Django form is - the edit page renders its form under the edit- prefix.
    """
    if is_edit:
        out = '#id_edit-' + name
    else:
        out = '#id_' + name

    return out

# ################################################################################################################################

def row_selector(gateway_name:'str') -> 'str':
    """ Where the gateway's row on the list page is - the name cell holds the name as an inline-edit link.
    """
    out = f'#data-table tbody tr:has(td a:text-is("{gateway_name}"))'
    return out

# ################################################################################################################################

def available_badge_selector(card_name:'str', badge_name:'str') -> 'str':
    """ Where one badge sits while it is still available - the picker lowercases each badge's data-name.
    """
    action = Picker_Actions[card_name]
    badge_name = badge_name.lower()

    out = f'#badge-zone-available-{action} .badge-zone-body .security-badge[data-name="{badge_name}"]'
    return out

# ################################################################################################################################

def assigned_badge_selector(card_name:'str', badge_name:'str') -> 'str':
    """ Where one badge sits once it is assigned.
    """
    action = Picker_Actions[card_name]
    badge_name = badge_name.lower()

    out = f'#badge-zone-assigned-{action} .badge-zone-body .security-badge[data-name="{badge_name}"]'
    return out

# ################################################################################################################################
# ################################################################################################################################
#
# Opening the wizard
#
# ################################################################################################################################
# ################################################################################################################################

def wait_until_pickers_loaded(page:'Page') -> 'None':
    """ Waits until all three badge pickers have replaced their Loading state with real badges.
    A save serializes whatever the assigned zones hold, so nothing may be saved before this.
    """
    _ = page.wait_for_function(
        '''() => {
            let ids = [
                'badge-zone-available-wizard',
                'badge-zone-available-skills-wizard',
                'badge-zone-available-sec-wizard',
            ];
            for (let id of ids) {
                let zone = document.getElementById(id);
                if (zone.querySelector('.badge-zone-empty')) return false;
            }
            return true;
        }''',
        timeout=_Wizard_Timeout)

# ################################################################################################################################

def _wait_until_wizard_ready(page:'Page', name_selector:'str') -> 'None':
    """ Waits until the wizard page is on screen with its form fields and pickers ready.
    """
    _ = page.wait_for_selector('#mcp-wizard', state='visible', timeout=_Wizard_Timeout)
    _ = page.wait_for_selector(name_selector, state='visible', timeout=_Wizard_Timeout)

    wait_until_pickers_loaded(page)

# ################################################################################################################################

def open_wizard_create(page:'Page', base_url:'str') -> 'None':
    """ Opens the create wizard through the gateway list's create link and waits until it is ready.
    """

    # Go to the gateway list ..
    navigate_to_page(page, base_url, MCP_List_URL)

    # .. follow the create link to the wizard page ..
    page.click('#markup .page_prompt a')

    # .. and wait for the form and the pickers.
    name_selector = field_selector('name')
    _wait_until_wizard_ready(page, name_selector)

# ################################################################################################################################

def open_wizard_edit(page:'Page', base_url:'str', gateway_name:'str') -> 'None':
    """ Opens the edit wizard through the gateway's row on the list and waits until it is ready.
    """

    # The query keeps the row on the first page of results, whatever other tests created ..
    list_url = f'{MCP_List_URL}&query={gateway_name}'
    navigate_to_page(page, base_url, list_url)

    # .. follow the row's Edit link to the wizard page ..
    row = row_selector(gateway_name)
    edit_link = f'{row} a:text-is("Edit")'

    _ = page.wait_for_selector(row, state='visible', timeout=_Wizard_Timeout)
    page.click(edit_link)

    # .. and wait for the form and the pickers - the assigned zones open
    # on what the gateway already exposes.
    name_selector = field_selector('name', is_edit=True)
    _wait_until_wizard_ready(page, name_selector)

# ################################################################################################################################
# ################################################################################################################################
#
# Steps and saving
#
# ################################################################################################################################
# ################################################################################################################################

def go_to_step(page:'Page', step_index:'int') -> 'None':
    """ Jumps to one of the wizard's steps through its tab on the step strip.
    """
    page.click(f'#mcp-wizard-steps .wizard-step[data-step="{step_index}"]')
    _ = page.wait_for_selector(f'#mcp-wizard-step-body-{step_index}', state='visible', timeout=_Wizard_Timeout)

# ################################################################################################################################

def wait_until_saved(page:'Page') -> 'None':
    """ Waits until the tooltip beside the save button confirms the save.
    """
    _ = page.wait_for_selector(f'text="{Saved_Label}"', state='visible', timeout=_Save_Timeout)

# ################################################################################################################################

def save_create(page:'Page') -> 'None':
    """ Finishes a create - walks to the review step, where Next says Save, and clicks it.
    The wizard stays on its page, the tooltip beside the button confirming the save.
    """
    go_to_step(page, Review_Step)
    page.click('#mcp-wizard-next')

    wait_until_saved(page)

# ################################################################################################################################

def save_edit(page:'Page') -> 'None':
    """ Saves an edit from whichever step is on screen - an edit has one Save button in its footer.
    """
    page.click('#mcp-wizard-save')

    wait_until_saved(page)

# ################################################################################################################################

def go_to_list(page:'Page', base_url:'str', gateway_name:'str') -> 'any_':
    """ Goes back to the gateway list and returns the row of the given gateway.
    """

    # The query keeps the row on the first page of results ..
    list_url = f'{MCP_List_URL}&query={gateway_name}'
    navigate_to_page(page, base_url, list_url)

    # .. and the row must be there.
    row = row_selector(gateway_name)

    out = page.wait_for_selector(row, state='visible', timeout=_Wizard_Timeout)
    return out

# ################################################################################################################################

def get_gateway_id(page:'Page', gateway_name:'str') -> 'str':
    """ Reads the gateway's server-side id out of its hidden cell on the list page.
    """
    row = row_selector(gateway_name)
    row_element = cast_('any_', page.query_selector(row))
    id_cell = row_element.query_selector('td[class*="item_id_"]')

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################
# ################################################################################################################################
#
# The badge picker cards of step 1
#
# ################################################################################################################################
# ################################################################################################################################

def open_picker_card(page:'Page', card_name:'str') -> 'None':
    """ Expands one of the step 1 picker cards, unless it is already open - the zones
    inside a collapsed card cannot be clicked.
    """
    is_open = page.evaluate(
        f'document.getElementById("mcp-wizard-{card_name}-body").classList.contains("wizard-option-body-open")')

    if not is_open:
        page.click(f'#mcp-wizard-{card_name}-header')
        _ = page.wait_for_selector(f'#mcp-wizard-{card_name}-body', state='visible', timeout=_Wizard_Timeout)

# ################################################################################################################################

def wait_for_available_badges(page:'Page', card_name:'str', minimum:'int') -> 'None':
    """ Waits until the card's available zone holds at least this many badges.
    """
    action = Picker_Actions[card_name]

    _ = page.wait_for_function(
        f'document.querySelectorAll("#badge-zone-available-{action} .badge-zone-body .security-badge").length >= {minimum}',
        timeout=_Wizard_Timeout)

# ################################################################################################################################

def assign_badge(page:'Page', card_name:'str', badge_name:'str') -> 'None':
    """ Assigns one badge by name - opens the card, clicks the badge in the available zone
    and waits until it lands in the assigned one.
    """
    open_picker_card(page, card_name)

    available_selector = available_badge_selector(card_name, badge_name)
    assigned_selector = assigned_badge_selector(card_name, badge_name)

    badge = cast_('any_', page.wait_for_selector(available_selector, state='visible', timeout=_Wizard_Timeout))
    badge.click()

    _ = page.wait_for_selector(assigned_selector, state='visible', timeout=_Wizard_Timeout)

# ################################################################################################################################

def remove_assigned_badge(page:'Page', card_name:'str', badge_name:'str') -> 'None':
    """ Removes one badge from the card's assigned zone - clicking it sends it back to the available one.
    """
    open_picker_card(page, card_name)

    available_selector = available_badge_selector(card_name, badge_name)
    assigned_selector = assigned_badge_selector(card_name, badge_name)

    badge = cast_('any_', page.wait_for_selector(assigned_selector, state='visible', timeout=_Wizard_Timeout))
    badge.click()

    _ = page.wait_for_selector(available_selector, state='visible', timeout=_Wizard_Timeout)

# ################################################################################################################################

def _get_badge_names(page:'Page', zone_kind:'str', card_name:'str') -> 'strlist':
    """ The names of every badge one of the card's zones holds.
    """
    action = Picker_Actions[card_name]
    badges = page.query_selector_all(f'#badge-zone-{zone_kind}-{action} .badge-zone-body .security-badge')

    out:'strlist' = []

    for badge in badges:
        name = badge.get_attribute('data-name')
        name = cast_('str', name)
        out.append(name)

    return out

# ################################################################################################################################

def get_assigned_badge_names(page:'Page', card_name:'str') -> 'strlist':
    """ The names of every badge the card's assigned zone holds.
    """
    out = _get_badge_names(page, 'assigned', card_name)
    return out

# ################################################################################################################################

def get_available_badge_names(page:'Page', card_name:'str') -> 'strlist':
    """ The names of every badge the card's available zone holds.
    """
    out = _get_badge_names(page, 'available', card_name)
    return out

# ################################################################################################################################

def get_picker_summary(page:'Page', card_name:'str') -> 'str':
    """ What the card's header summary currently says, e.g. None assigned or 2 assigned.
    """
    out = page.inner_text(f'#mcp-wizard-summary-{card_name}')
    return out

# ################################################################################################################################
# ################################################################################################################################
#
# The popover micro-forms of step 2
#
# ################################################################################################################################
# ################################################################################################################################

def popover_input_selector(field_name:'str') -> 'str':
    """ Where a popover micro-form's input for the given field is.
    """
    out = '#mcp-wizard-tippy-' + field_name
    return out

# ################################################################################################################################

def accept_popover(page:'Page') -> 'None':
    """ Accepts the open popover micro-form - OK writes the answers back into the form and closes it.
    """
    page.click('#mcp-wizard-popup .wizard-tippy-buttons button.action-button')
    _ = page.wait_for_selector('#mcp-wizard-popup', state='detached', timeout=_Wizard_Timeout)

# ################################################################################################################################

def set_size_caps(
    page:'Page',
    *,
    max_response_size:'strnone'=None,
    min_size_threshold:'strnone'=None,
    size_cap_mode:'strnone'=None,
    characters_per_token:'strnone'=None,
    ) -> 'None':
    """ Sets the response size caps through the popover the size caps line of step 2 opens.
    Only the values given change, the rest keeps what the popover opened with.
    """
    max_size_input = popover_input_selector('max_response_size')

    page.click('#mcp-wizard-edit-size-caps')
    _ = page.wait_for_selector(max_size_input, state='visible', timeout=_Wizard_Timeout)

    if max_response_size is not None:
        page.fill(max_size_input, max_response_size)

    if min_size_threshold is not None:
        threshold_input = popover_input_selector('min_size_threshold')
        page.fill(threshold_input, min_size_threshold)

    if size_cap_mode is not None:
        mode_input = popover_input_selector('size_cap_mode')
        _ = page.select_option(mode_input, size_cap_mode)

    if characters_per_token is not None:
        characters_input = popover_input_selector('characters_per_token')
        page.fill(characters_input, characters_per_token)

    accept_popover(page)

# ################################################################################################################################

def open_more_options(page:'Page') -> 'None':
    """ Unfolds the More options block of step 2, unless it is already open.
    """
    is_hidden = page.evaluate('document.getElementById("mcp-wizard-options-body").hidden')

    if is_hidden:
        page.click('#mcp-wizard-edit-options')
        _ = page.wait_for_selector('#mcp-wizard-options-body', state='visible', timeout=_Wizard_Timeout)

# ################################################################################################################################

def set_gateway_options(page:'Page', *, validate_input:'boolnone'=None, is_audit_log_active:'boolnone'=None) -> 'None':
    """ Sets the gateway options through the popover their card opens.
    """
    open_more_options(page)

    validate_selector = popover_input_selector('validate_input')

    page.click('#mcp-wizard-card-gateway-options')
    _ = page.wait_for_selector(validate_selector, state='attached', timeout=_Wizard_Timeout)

    if validate_input is not None:
        page.set_checked(validate_selector, validate_input)

    if is_audit_log_active is not None:
        audit_log_selector = popover_input_selector('is_audit_log_active')
        page.set_checked(audit_log_selector, is_audit_log_active)

    accept_popover(page)

# ################################################################################################################################

def set_compaction(
    page:'Page',
    *,
    strip_nulls:'boolnone'=None,
    collapse_whitespace:'boolnone'=None,
    strip_base64:'boolnone'=None,
    ) -> 'None':
    """ Sets the compaction toggles through the popover their card opens.
    """
    open_more_options(page)

    strip_nulls_selector = popover_input_selector('safeguards_strip_nulls')

    page.click('#mcp-wizard-card-compaction')
    _ = page.wait_for_selector(strip_nulls_selector, state='attached', timeout=_Wizard_Timeout)

    if strip_nulls is not None:
        page.set_checked(strip_nulls_selector, strip_nulls)

    if collapse_whitespace is not None:
        whitespace_selector = popover_input_selector('safeguards_collapse_whitespace')
        page.set_checked(whitespace_selector, collapse_whitespace)

    if strip_base64 is not None:
        base64_selector = popover_input_selector('safeguards_strip_base64')
        page.set_checked(base64_selector, strip_base64)

    accept_popover(page)

# ################################################################################################################################
# ################################################################################################################################
#
# The PII and content safety cards of step 2
#
# ################################################################################################################################
# ################################################################################################################################

def _open_option_card(page:'Page', card_name:'str') -> 'None':
    """ Unfolds one of the collapsible option cards of step 2, unless it is already open.
    """
    open_more_options(page)

    is_open = page.evaluate(
        f'document.getElementById("mcp-wizard-{card_name}-body").classList.contains("wizard-option-body-open")')

    if not is_open:
        page.click(f'#mcp-wizard-{card_name}-header')
        _ = page.wait_for_selector(f'#mcp-wizard-{card_name}-body', state='visible', timeout=_Wizard_Timeout)

# ################################################################################################################################

def open_pii_card(page:'Page') -> 'None':
    """ Unfolds the PII removal card, unless it is already open.
    """
    _open_option_card(page, 'pii')

# ################################################################################################################################

def open_safety_card(page:'Page') -> 'None':
    """ Unfolds the content safety card, unless it is already open.
    """
    _open_option_card(page, 'safety')

# ################################################################################################################################

def open_safety_group(page:'Page', group_title:'str') -> 'None':
    """ Unfolds one of the collapse groups inside the content safety card - Unicode, Markup or URL policy.
    """
    open_safety_card(page)

    title_selector = f'#mcp-wizard-safety-body .wizard-collapse-group-title:has-text("{group_title}")'
    body_selector = f'{title_selector} + .wizard-collapse-group-body'

    body = cast_('any_', page.query_selector(body_selector))
    is_hidden = body.evaluate('element => element.hidden')

    if is_hidden:
        page.click(title_selector)
        _ = page.wait_for_selector(body_selector, state='visible', timeout=_Wizard_Timeout)

# ################################################################################################################################

def set_multi_select(page:'Page', field_name:'str', values:'anylistnone', is_edit:'bool'=False) -> 'None':
    """ Sets a Chosen multi-select's values - the underlying select is hidden by Chosen,
    so the value goes through the select itself with the update events Chosen listens for.
    """
    selector = field_selector(field_name, is_edit)
    values_json = dumps(values)

    _ = page.evaluate(f'$("{selector}").val({values_json}).trigger("chosen:updated").trigger("change")')

# ################################################################################################################################

def get_multi_select_values(page:'Page', field_name:'str', is_edit:'bool'=False) -> 'any_':
    """ What a Chosen multi-select currently holds.
    """
    selector = field_selector(field_name, is_edit)
    values = page.evaluate(f'$("{selector}").val()')

    if values is None:
        values = []

    out = values
    return out

# ################################################################################################################################

def pick_from_chosen(page:'Page', field_name:'str', option_label:'str', is_edit:'bool'=False) -> 'None':
    """ Picks one option from a Chosen multi-select the way a person does - opening the dropdown
    and clicking the option by its visible label.
    """
    select_selector = field_selector(field_name, is_edit)

    # Chosen derives the container id from the select's id with dashes turned to underscores ..
    field_id = select_selector.lstrip('#')
    container_id = field_id.replace('-', '_') + '_chosen'

    results_selector = f'#{container_id} .chosen-results li.active-result'

    # Close the field first - a field left active by an earlier pick ignores the next open request ..
    _ = page.evaluate(f'$("{select_selector}").trigger("chosen:close")')

    # .. open the dropdown through Chosen's own event - a click on the choices area can land
    # on a chip instead - and wait for the with-drop class that marks the open state ..
    _ = page.evaluate(f'$("{select_selector}").trigger("chosen:open")')
    _ = page.wait_for_selector(f'#{container_id}.chosen-with-drop', state='attached', timeout=_Wizard_Timeout)

    # .. pick the option by its visible label ..
    page.click(f'{results_selector}:has-text("{option_label}")')

    # .. wait out Chosen's deferred reopen so the close below is not undone ..
    page.wait_for_timeout(_Chosen_Settle_Time)

    # .. and close the dropdown again.
    _ = page.evaluate(f'$("{select_selector}").trigger("chosen:close")')
    _ = page.wait_for_function(
        f'!document.getElementById("{container_id}").classList.contains("chosen-with-drop")',
        timeout=_Wizard_Timeout)

# ################################################################################################################################
# ################################################################################################################################
#
# The allowed hosts chips
#
# ################################################################################################################################
# ################################################################################################################################

# Where the chip widget standing in for the allowed hosts input lives
Host_List_Selector = '#mcp-wizard-safety-body .mcp-host-list'

# ################################################################################################################################

def add_host_chip(page:'Page', host:'str') -> 'None':
    """ Adds one host to the allowed hosts chips - typing it and pressing Enter.
    """
    text_field = f'{Host_List_Selector} .search-field input'
    chip = f'{Host_List_Selector} li.search-choice:has-text("{host}")'

    page.fill(text_field, host)
    page.press(text_field, 'Enter')

    _ = page.wait_for_selector(chip, state='visible', timeout=_Wizard_Timeout)

# ################################################################################################################################

def type_into_host_field(page:'Page', text:'str') -> 'None':
    """ Types into the chip widget's text field without committing anything.
    """
    text_field = f'{Host_List_Selector} .search-field input'
    page.fill(text_field, text)

# ################################################################################################################################

def get_host_chip_texts(page:'Page') -> 'strlist':
    """ What the allowed hosts chips currently say, in order.
    """
    chips = page.query_selector_all(f'{Host_List_Selector} li.search-choice span')

    out:'strlist' = []

    for chip in chips:
        text = chip.inner_text().strip()
        out.append(text)

    return out

# ################################################################################################################################

def remove_host_chip(page:'Page', host:'str') -> 'None':
    """ Removes one host chip through its close mark.
    """
    close_mark = f'{Host_List_Selector} a.search-choice-close[data-host="{host}"]'
    chip = f'{Host_List_Selector} li.search-choice:has-text("{host}")'

    page.click(close_mark)
    _ = page.wait_for_selector(chip, state='detached', timeout=_Wizard_Timeout)

# ################################################################################################################################
# ################################################################################################################################
#
# Whole flows
#
# ################################################################################################################################
# ################################################################################################################################

def create_gateway(
    page:'Page',
    base_url:'str',
    gateway_name:'str',
    url_path:'str',
    *,
    services:'anylistnone'=None,
    security:'anylistnone'=None,
    skills:'anylistnone'=None,
    ) -> 'str':
    """ Creates a gateway through the wizard - name and URL path on step 1, the given badges
    assigned through their cards, the save made from the review step - and returns the new
    gateway's id read off the list page.
    """

    # Open the wizard and answer step 1 ..
    open_wizard_create(page, base_url)

    name_selector = field_selector('name')
    url_path_selector = field_selector('url_path')

    page.fill(name_selector, gateway_name)
    page.fill(url_path_selector, url_path)

    # .. assign whatever the gateway exposes and authenticates with ..
    if services:
        for service_name in services:
            assign_badge(page, 'services', service_name)

    if skills:
        for skill_name in skills:
            assign_badge(page, 'skills', skill_name)

    if security:
        for definition_name in security:
            assign_badge(page, 'security', definition_name)

    # .. walk to the review and save ..
    save_create(page)

    # .. and read the new gateway's id off the list.
    _ = go_to_list(page, base_url, gateway_name)

    out = get_gateway_id(page, gateway_name)
    return out

# ################################################################################################################################
# ################################################################################################################################
