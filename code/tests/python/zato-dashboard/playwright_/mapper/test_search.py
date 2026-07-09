# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Playwright
from playwright.sync_api import expect, Page

# Zato
from common import drag_tree_row, open_clean_page, set_expression, tree_item, tree_row

# ################################################################################################################################
# ################################################################################################################################

def test_search_finds_tree_fields_and_counts_matches(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    # The name quantity appears twice on the source side - at the top
    # level and inside the repeating lines.
    page.locator('#mapper-search-input').fill('quantity')

    expect(page.locator('#mapper-search-count')).to_have_text('1 of 2')
    expect(page.locator('.mapper-search-match')).to_have_count(2)
    expect(page.locator('.mapper-search-current')).to_have_count(1)

# ################################################################################################################################

def test_search_navigates_between_matches(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    search_input = page.locator('#mapper-search-input')
    search_input.fill('quantity')
    expect(page.locator('#mapper-search-count')).to_have_text('1 of 2')

    # The next button steps forward ..
    page.locator('#mapper-search-next').click()
    expect(page.locator('#mapper-search-count')).to_have_text('2 of 2')

    # .. and wraps around past the last match ..
    page.locator('#mapper-search-next').click()
    expect(page.locator('#mapper-search-count')).to_have_text('1 of 2')

    # .. the previous button wraps backwards ..
    page.locator('#mapper-search-previous').click()
    expect(page.locator('#mapper-search-count')).to_have_text('2 of 2')

    # .. and Enter in the input steps forward too.
    search_input.press('Enter')
    expect(page.locator('#mapper-search-count')).to_have_text('1 of 2')

# ################################################################################################################################

def test_search_expands_a_collapsed_branch_on_its_way_to_a_match(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    # With everything collapsed, sku sits inside a hidden branch ..
    page.locator('#mapper-collapse-all').click()
    expect(tree_item(page, 'source', 'lines')).to_have_class('mapper-tree-item mapper-tree-item-collapsed')

    # .. searching for it expands its way there.
    page.locator('#mapper-search-input').fill('sku')
    expect(page.locator('#mapper-search-count')).to_have_text('1 of 1')
    expect(tree_item(page, 'source', 'lines')).to_have_class('mapper-tree-item')
    expect(tree_row(page, 'source', 'lines.sku')).to_be_visible()

# ################################################################################################################################

def test_search_covers_the_mapping_list(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')
    set_expression(page, '$uppercase(customer)')

    # The expression text matches even though no tree field is named so.
    page.locator('#mapper-search-input').fill('uppercase')

    expect(page.locator('#mapper-search-count')).to_have_text('1 of 1')
    expect(page.locator('.mapper-row.mapper-search-current')).to_have_count(1)

# ################################################################################################################################

def test_search_says_when_nothing_matches(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    page.locator('#mapper-search-input').fill('no-such-name-anywhere')

    expect(page.locator('#mapper-search-count')).to_have_text('No matches')
    expect(page.locator('.mapper-search-match')).to_have_count(0)

# ################################################################################################################################

def test_the_mapped_filter_narrows_both_trees(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')

    page.locator('.mapper-filter-button[data-filter="mapped"]').click()

    # The mapped fields stay ..
    expect(tree_row(page, 'source', 'customer')).to_be_visible()
    expect(tree_row(page, 'target', 'buyer')).to_be_visible()

    # .. the unmapped ones disappear on both sides.
    expect(tree_row(page, 'source', 'notes')).to_be_hidden()
    expect(tree_row(page, 'target', 'amount')).to_be_hidden()

# ################################################################################################################################

def test_the_unmapped_filter_is_the_complement(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')

    page.locator('.mapper-filter-button[data-filter="unmapped"]').click()

    expect(tree_row(page, 'source', 'customer')).to_be_hidden()
    expect(tree_row(page, 'target', 'buyer')).to_be_hidden()

    expect(tree_row(page, 'source', 'notes')).to_be_visible()
    expect(tree_row(page, 'target', 'amount')).to_be_visible()

# ################################################################################################################################

def test_the_invalid_filter_shows_broken_and_missing_targets(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    # A mapping whose expression does not parse ..
    drag_tree_row(page, 'customer', 'buyer')
    set_expression(page, 'customer +')

    page.locator('.mapper-filter-button[data-filter="invalid"]').click()

    # .. its target counts as invalid, and so does a required target
    # field nothing writes ..
    expect(tree_row(page, 'target', 'buyer')).to_be_visible()
    expect(tree_row(page, 'target', 'amount')).to_be_visible()

    # .. while the source side has no invalid fields of its own.
    expect(tree_row(page, 'source', 'customer')).to_be_hidden()

# ################################################################################################################################

def test_the_all_filter_shows_everything_again(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')

    page.locator('.mapper-filter-button[data-filter="mapped"]').click()
    expect(tree_row(page, 'source', 'notes')).to_be_hidden()

    page.locator('.mapper-filter-button[data-filter="all"]').click()
    expect(tree_row(page, 'source', 'notes')).to_be_visible()

# ################################################################################################################################

def test_collapse_all_folds_every_branch(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    page.locator('#mapper-collapse-all').click()

    expect(tree_item(page, 'source', 'lines')).to_have_class('mapper-tree-item mapper-tree-item-collapsed')
    expect(tree_item(page, 'target', 'items')).to_have_class('mapper-tree-item mapper-tree-item-collapsed')
    expect(tree_row(page, 'source', 'lines.sku')).to_be_hidden()

# ################################################################################################################################

def test_expand_mapped_opens_exactly_the_mapped_branches(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    # One mapping deep inside the repeating nodes on both sides.
    drag_tree_row(page, 'lines.sku', 'items.code')

    page.locator('#mapper-collapse-all').click()
    expect(tree_row(page, 'source', 'lines.sku')).to_be_hidden()

    page.locator('#mapper-expand-mapped').click()

    expect(tree_row(page, 'source', 'lines.sku')).to_be_visible()
    expect(tree_row(page, 'target', 'items.code')).to_be_visible()

# ################################################################################################################################
# ################################################################################################################################
