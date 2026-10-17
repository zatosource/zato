# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.playwright_pubsub import navigate_to_page, submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

# How long to wait for a row or a dialog to render, in milliseconds
_Render_Timeout_MS = 5000

# How long to wait for the badge picker of a group to load its members, in milliseconds
_Badge_Load_Timeout_MS = 10_000

# ################################################################################################################################
# ################################################################################################################################

def _open_edit_dialog(page:'Page', base_url:'str', page_url:'str', name:'str', namespace:'str') -> 'None':
    """ Opens the edit dialog of the row of the given name on a list page.
    """

    # Go to the list page, where the row is to be read ..
    navigate_to_page(page, base_url, page_url)

    # .. read the server-side ID off the row ..
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    row:'any_' = page.wait_for_selector(row_selector, state='visible', timeout=_Render_Timeout_MS)
    id_cell = row.query_selector('td[class*="item_id_"]')
    item_id = id_cell.text_content().strip()

    # .. and open the edit dialog.
    page.evaluate(f'$.fn.zato.{namespace}.edit("{item_id}")')
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=_Render_Timeout_MS)

# ################################################################################################################################

def rename_apikey_definition(page:'Page', base_url:'str', name:'str', new_name:'str') -> 'None':
    """ Renames an API key security definition through its edit dialog, leaving its header and its key as they are.
    """

    # The list is filtered by the name so the row is on the first page ..
    _open_edit_dialog(page, base_url, f'/zato/security/apikey/?query={name}', name, 'security.apikey')

    # .. give the definition its new name ..
    page.fill('#id_edit-name', '')
    page.fill('#id_edit-name', new_name)

    # .. and submit, waiting for the row under the new name.
    submit_edit_form(page)

    new_row_selector = f'#data-table tbody tr:has(td:text-is("{new_name}"))'
    _ = page.wait_for_selector(new_row_selector, state='visible', timeout=_Render_Timeout_MS)

# ################################################################################################################################

def remove_security_group_members(page:'Page', base_url:'str', group_name:'str', member_names:'strlist') -> 'None':
    """ Removes the given members from an API clients security group in one edit, via the badge picker
    of its edit dialog, leaving all the other members assigned.
    """

    _open_edit_dialog(page, base_url, '/zato/groups/group/zato-api-creds/', group_name, 'groups')

    for member_name in member_names:

        # Wait for the member to be among the assigned ones, the badges carry their names in lowercase ..
        badge_selector = f'#badge-zone-assigned-edit .badge-zone-body .security-badge[data-name="{member_name.lower()}"]'
        badge:'any_' = page.wait_for_selector(badge_selector, state='visible', timeout=_Badge_Load_Timeout_MS)

        # .. and move it out of the assigned zone.
        badge.click()

    # Submit the group with the remaining members.
    submit_edit_form(page)

# ################################################################################################################################
# ################################################################################################################################
