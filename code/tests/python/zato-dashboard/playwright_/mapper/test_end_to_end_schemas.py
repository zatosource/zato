# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Playwright
from playwright.sync_api import expect, Page

# Mapper tests
from common import open_empty_page, paste_example, source_example, target_example

# ################################################################################################################################
# ################################################################################################################################

def test_full_schema_session(page:'Page', base_url:'str') -> 'None':
    """ A whole session as a user would run it: open the page, switch tabs, paste an example
    on each side, see both trees render with type and cardinality badges, reload and find
    everything restored from autosave, then undo and redo.
    """
    open_empty_page(page, base_url)

    # Switch through the tabs and back to Design ..
    page.locator('.mapper-tab[data-tab="code"]').click()
    expect(page.locator('#mapper-panel-code')).to_be_visible()

    page.locator('.mapper-tab[data-tab="design"]').click()
    expect(page.locator('#mapper-panel-design')).to_be_visible()

    # .. paste a JSON example on each side ..
    paste_example(page, 'source', source_example)
    paste_example(page, 'target', target_example)

    # .. both trees render with types and cardinality ..
    source_lines = page.locator('#mapper-schema-body-source .mapper-tree-item[data-path="lines"] > .mapper-tree-row')
    expect(source_lines.locator('.mapper-tree-cardinality-badge')).to_have_text('list')

    target_items = page.locator('#mapper-schema-body-target .mapper-tree-item[data-path="items"] > .mapper-tree-row')
    expect(target_items.locator('.mapper-tree-cardinality-badge')).to_have_text('list')

    target_amount = page.locator('#mapper-schema-body-target .mapper-tree-item[data-path="amount"] > .mapper-tree-row')
    expect(target_amount.locator('.mapper-tree-type-badge')).to_have_text('number')

    # .. rename the mapping ..
    name_input = page.locator('#mapper-name')
    name_input.fill('Order to invoice')
    name_input.blur()

    # .. reload and find everything restored from autosave ..
    _ = page.reload()
    expect(page.locator('#mapper-name')).to_have_value('Order to invoice')
    expect(page.locator('#mapper-sample-count-source')).to_have_text('1')
    expect(page.locator('#mapper-sample-count-target')).to_have_text('1')

    restored_lines = page.locator('#mapper-schema-body-source .mapper-tree-item[data-path="lines"] > .mapper-tree-row')
    expect(restored_lines.locator('.mapper-tree-cardinality-badge')).to_have_text('list')

    # .. undo steps back through the session ..
    # (a reload starts a fresh store, so only changes made now are undoable)
    name_input = page.locator('#mapper-name')
    name_input.fill('Order to shipment')
    name_input.blur()
    expect(page.locator('#mapper-undo')).to_be_enabled()

    page.locator('#mapper-undo').click()
    expect(page.locator('#mapper-name')).to_have_value('Order to invoice')

    # .. and redo brings the change back.
    page.locator('#mapper-redo').click()
    expect(page.locator('#mapper-name')).to_have_value('Order to shipment')

# ################################################################################################################################
# ################################################################################################################################
