# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Playwright
from playwright.sync_api import expect, Page

# Zato
from common import drag_tree_row, open_clean_page

# ################################################################################################################################
# ################################################################################################################################

def test_canvas_end_to_end(page:'Page', base_url:'str') -> 'None':
    """ A full drag-and-drop session: map fields, watch every connection stay
    drawn with the selection highlighted, get an iteration scope from nested
    leaves, and see the flat list and the output stay in sync throughout.
    """
    open_clean_page(page, base_url)

    # Two plain field-to-field drags ..
    drag_tree_row(page, 'customer', 'buyer')
    drag_tree_row(page, 'quantity', 'amount')

    rows = page.locator('.mapper-row')
    expect(rows).to_have_count(2)

    # .. both connections stay drawn, the selected one highlighted ..
    expect(page.locator('#mapper-canvas-lines path')).to_have_count(2)
    expect(page.locator('#mapper-canvas-lines path.mapper-canvas-line-selected')).to_have_count(1)

    # .. clicking the other row moves the highlight with the selection ..
    rows.first.click()
    expect(page.locator('#mapper-detail-target')).to_have_value('buyer')
    expect(page.locator('#mapper-canvas-lines path.mapper-canvas-line-selected')).to_have_count(1)

    # .. nested leaves dropped onto each other create the scope automatically ..
    drag_tree_row(page, 'lines.sku', 'items.code')
    expect(page.locator('.mapper-scope-title')).to_contain_text('items')

    # .. another child maps into the same scope, no duplicate scope appears,
    # and the new row is the one selected in the detail panel ..
    drag_tree_row(page, 'lines.quantity', 'items.count')
    expect(page.locator('.mapper-scope-group')).to_have_count(1)
    expect(page.locator('.mapper-scope-rows .mapper-row')).to_have_count(2)
    expect(page.locator('#mapper-detail-target')).to_have_value('count')

    # .. the output carries the whole mapping ..
    output = page.locator('#mapper-preview-output')
    expect(output).to_contain_text('ACME')
    expect(output).to_contain_text('AA-11')
    expect(output).to_contain_text('BB-22')

    # .. and everything survives a reload from autosave.
    _ = page.reload()
    expect(page.locator('.mapper-row')).to_have_count(4)
    expect(page.locator('.mapper-scope-group')).to_have_count(1)
    expect(page.locator('#mapper-preview-output')).to_contain_text('AA-11')

# ################################################################################################################################
# ################################################################################################################################
