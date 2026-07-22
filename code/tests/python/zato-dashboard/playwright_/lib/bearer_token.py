# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.test.playwright_pubsub import navigate_to_page, open_create_dialog, submit_create_form, submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anylist, strlist, strlistnone

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The list page with all the Bearer token definitions
Bearer_Page_Url = '/zato/security/oauth/outconn/client-credentials/?cluster=1'

# The list page with all the API client security groups
Groups_Page_Url = '/zato/groups/group/zato-api-creds/?cluster=1'

# Cell indexes in the Bearer token definitions table
Cell_Name       = 2
Cell_Token_Type = 3
Cell_Username   = 4
Cell_Auth_URL   = 5

# Hidden cells with the inbound verification fields
Cell_Issuer   = 21
Cell_JWKS_URL = 22
Cell_Audience = 23
Cell_Claims   = 24

# Text fields the create and edit dialogs share, in both the dynamic and the inbound sections
_Text_Fields = ('name', 'auth_server_url', 'username', 'secret', 'issuer', 'jwks_url', 'audience', 'claims')

# The inbound verification fields live in a collapsed section that needs to be expanded before they can be filled
_Verification_Fields = ('issuer', 'jwks_url', 'audience', 'claims')

# Text fields specific to the static tokens tab - the token itself appears only in the create form
_Static_Fields = ('static_header', 'static_prefix')

# ################################################################################################################################
# ################################################################################################################################
#
# Row lookup
#
# ################################################################################################################################
# ################################################################################################################################

def find_definition_row(page:'Page', name:'str') -> 'any_':
    """ Returns the table row of a Bearer token definition with the given name or None if there is no such row.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.query_selector(row_selector)
    return out

# ################################################################################################################################

def wait_for_definition_row(page:'Page', name:'str') -> 'any_':
    """ Waits for the row of a definition with the given name to appear and returns it.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.wait_for_selector(row_selector, state='visible', timeout=10000)
    return out

# ################################################################################################################################

def get_definition_id(page:'Page', name:'str') -> 'str':
    """ Returns the server-side ID of a definition row identified by name.
    """

    row = find_definition_row(page, name)
    id_cell = row.query_selector('td[class*="item_id_"]')

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################

def get_cell_texts(row:'any_') -> 'anylist':
    """ Returns the text of every cell in a row, including the hidden ones,
    which is why text_content is used rather than inner_text.
    """

    out:'anylist' = []

    cells = row.query_selector_all('td')
    for cell in cells:
        text = cell.text_content().strip()
        out.append(text)

    return out

# ################################################################################################################################
# ################################################################################################################################
#
# Definition CRUD
#
# ################################################################################################################################
# ################################################################################################################################

def _fill_definition_form(page:'Page', options:'anydict', prefix:'str'='') -> 'None':
    """ Fills the Bearer token create or edit form. An empty prefix means the create form,
    the 'edit-' prefix means the edit form. Only the fields present in options are touched.
    """

    # The dialog that is being filled - the create one is the one without a prefix.
    dialog_id = 'edit-div' if prefix else 'create-div'

    # Check if any of the collapsed inbound verification fields is to be filled ..
    needs_verification_fields = False
    for field_name in _Verification_Fields:
        if field_name in options:
            needs_verification_fields = True
            break

    # .. and if so, expand the channel verification section first, unless it is already expanded.
    if needs_verification_fields:
        block_selector = f'#{dialog_id} .channel-verification-block'
        if not page.is_visible(block_selector):
            page.click(f'#{dialog_id} a[href*="channel-verification-block"]')
            _ = page.wait_for_selector(block_selector, state='visible', timeout=5000)

    # Plain text fields of the dynamic tab and the inbound verification section ..
    for field_name in _Text_Fields:
        if field_name in options:
            page.fill(f'#id_{prefix}{field_name}', options[field_name])

    # .. and the fields of the static tokens tab.
    for field_name in _Static_Fields:
        if field_name in options:
            page.fill(f'#id_{prefix}{field_name}', options[field_name])

# ################################################################################################################################

def create_dynamic_definition(page:'Page', base_url:'str', name:'str', options:'anydict') -> 'str':
    """ Creates a dynamic Bearer token definition via the UI and returns its server-side ID.
    """

    # Navigate to the Bearer tokens page ..
    navigate_to_page(page, base_url, Bearer_Page_Url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. fill the name and everything else the caller provided ..
    page.fill('#id_name', name)
    _fill_definition_form(page, options)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row and return the definition's ID.
    _ = wait_for_definition_row(page, name)

    out = get_definition_id(page, name)
    return out

# ################################################################################################################################

def create_static_definition(page:'Page', base_url:'str', name:'str', token:'str', options:'anydict | None'=None) -> 'str':
    """ Creates a static Bearer token definition via the UI and returns its server-side ID.
    """

    # Navigate to the Bearer tokens page ..
    navigate_to_page(page, base_url, Bearer_Page_Url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. switch to the static tokens tab ..
    page.click('#create-div .dashboard-tab[data-tab="static"]')
    page.wait_for_selector('#bearer-create-tab-panel-static', state='visible', timeout=5000)

    # .. the name field on this tab mirrors its value into the main name field ..
    page.fill('#id_create_static_name', name)

    # .. fill in the token itself ..
    page.fill('#id_static_token', token)

    # .. along with any other fields the caller provided ..
    if options:
        _fill_definition_form(page, options)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row and return the definition's ID.
    _ = wait_for_definition_row(page, name)

    out = get_definition_id(page, name)
    return out

# ################################################################################################################################

def open_edit_dialog(page:'Page', definition_id:'str') -> 'None':
    """ Opens the edit dialog for a definition of the given ID.
    """

    # Call the page's JS edit function ..
    page.evaluate(f'$.fn.zato.security.oauth.edit("{definition_id}")')

    # .. and wait for the dialog to appear.
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def edit_definition(page:'Page', base_url:'str', definition_id:'str', options:'anydict') -> 'None':
    """ Opens the edit dialog for a definition, applies the given changes and submits the form.
    """

    # Navigate to the Bearer tokens page first, since the caller may be on a different one ..
    navigate_to_page(page, base_url, Bearer_Page_Url)

    # .. open the dialog ..
    open_edit_dialog(page, definition_id)

    # .. apply the changes ..
    _fill_definition_form(page, options, 'edit-')

    # .. and submit.
    submit_edit_form(page)

# ################################################################################################################################

def delete_definition(page:'Page', definition_id:'str') -> 'None':
    """ Deletes a definition via the UI confirmation dialog.
    """

    # Trigger the delete confirmation ..
    page.evaluate(f'$.fn.zato.security.oauth.delete_("{definition_id}")')
    page.wait_for_selector('#popup_container', state='visible', timeout=5000)

    # .. confirm ..
    page.click('#popup_ok')

    # .. and wait for the row removal animation.
    page.wait_for_selector(f'#tr_{definition_id}', state='detached', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################
#
# Security group membership
#
# ################################################################################################################################
# ################################################################################################################################

def get_group_id(page:'Page', base_url:'str', group_name:'str') -> 'str':
    """ Returns the server-side ID of a security group identified by name.
    """

    # Navigate to the groups page ..
    navigate_to_page(page, base_url, Groups_Page_Url)

    # .. find the group's row ..
    row_selector = f'#data-table tbody tr:has(td:text-is("{group_name}"))'
    row = page.wait_for_selector(row_selector, state='visible', timeout=10000)

    # .. and read the ID out of its hidden cell.
    id_cell = row.query_selector('td[class*="item_id_"]')

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################

def edit_group_members(
    page:'Page',
    base_url:'str',
    group_name:'str',
    add_names:'strlistnone'=None,
    remove_names:'strlistnone'=None,
    ) -> 'None':
    """ Edits a security group via the UI, adding and removing members through the badge picker.
    """

    # Find the group and open its edit dialog ..
    group_id = get_group_id(page, base_url, group_name)

    page.evaluate(f'$.fn.zato.groups.edit("{group_id}")')
    page.wait_for_selector('#edit-div', state='visible', timeout=5000)

    # .. wait for the badges to load ..
    page.wait_for_function(
        'document.querySelectorAll("#badge-picker-edit .badge-zone-body .security-badge").length >= 1',
        timeout=10000
    )

    # .. move each member to add from the available zone to the assigned one ..
    if add_names:
        _click_badges(page, 'badge-zone-available-edit', add_names)

    # .. and each member to remove the other way around ..
    if remove_names:
        _click_badges(page, 'badge-zone-assigned-edit', remove_names)

    # .. submit and wait for the dialog to close.
    submit_edit_form(page)

# ################################################################################################################################

def _click_badges(page:'Page', zone_id:'str', member_names:'strlist') -> 'None':
    """ Clicks each named badge in a badge picker zone, which moves it to the other zone.
    """

    for member_name in member_names:
        badge_selector = f'#{zone_id} .badge-zone-body .security-badge[data-name="{member_name}"]'
        badge = page.wait_for_selector(badge_selector, state='visible', timeout=10000)
        badge.click()

# ################################################################################################################################
# ################################################################################################################################
