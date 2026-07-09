# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Playwright
from playwright.sync_api import expect, Page

# Zato
from common import add_mapping, drag_tree_row, open_clean_page, set_expression, set_target, tree_row

# ################################################################################################################################
# ################################################################################################################################

def test_a_source_badge_counts_its_references(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    # One mapping references customer ..
    drag_tree_row(page, 'customer', 'buyer')

    badge = tree_row(page, 'source', 'customer').locator('.mapper-tree-usage-badge')
    expect(badge).to_have_text('1')

    # .. a second mapping referencing it in an expression raises the count.
    add_mapping(page)
    set_target(page, 'invoice_number')
    set_expression(page, '$uppercase(customer)')

    expect(badge).to_have_text('2')

# ################################################################################################################################

def test_clicking_a_badge_lists_the_referencing_mappings(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    drag_tree_row(page, 'customer', 'buyer')

    add_mapping(page)
    set_target(page, 'invoice_number')
    set_expression(page, '$uppercase(customer)')

    tree_row(page, 'source', 'customer').locator('.mapper-tree-usage-badge').click()

    # The menu lists both mappings under a header ..
    menu = page.locator('.mapper-context-menu')
    expect(menu.locator('.mapper-context-menu-header')).to_have_text('Used by')
    expect(menu.locator('.mapper-context-menu-item')).to_have_count(2)
    expect(menu.locator('.mapper-context-menu-item').first).to_contain_text('buyer')
    expect(menu.locator('.mapper-context-menu-item').last).to_contain_text('$uppercase(customer)')

    # .. and choosing an entry opens that mapping's row.
    menu.locator('.mapper-context-menu-item').first.click()
    expect(page.locator('#mapper-detail-target')).to_have_value('buyer')

# ################################################################################################################################

def test_a_scope_reference_lists_as_an_iteration(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    # A drop of nested leaves creates the scope, so lines is referenced
    # by the scope itself and lines.sku by the child row.
    drag_tree_row(page, 'lines.sku', 'items.code')

    tree_row(page, 'source', 'lines').locator('.mapper-tree-usage-badge').click()

    # A scope has no row to open, so it lists as a header describing
    # the iteration it drives.
    menu = page.locator('.mapper-context-menu')
    expect(menu.locator('.mapper-context-menu-header').last).to_contain_text('items \u2190 each lines')

# ################################################################################################################################
# ################################################################################################################################
