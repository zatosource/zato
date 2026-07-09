# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Playwright
from playwright.sync_api import expect, Page

# Zato
from common import drag_tree_row, open_clean_page, tree_item, tree_row

# ################################################################################################################################
# ################################################################################################################################

def _rename_field(page:'Page', side:'str', path:'str', new_name:'str') -> 'None':
    """ Renames a field through its tree row's context menu.
    """
    tree_row(page, side, path).click(button='right')
    page.locator('.mapper-context-menu-item', has_text='Rename field').click()

    page.locator('.mapper-dialog-input').fill(new_name)
    page.locator('.mapper-dialog .mapper-button-confirm').click()

# ################################################################################################################################

def test_renaming_an_unreferenced_field_updates_the_tree_only(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    _rename_field(page, 'source', 'notes', 'remarks')

    # No review appears - nothing references the field - and the tree
    # carries the new name right away.
    expect(page.locator('.mapper-review-dialog')).to_have_count(0)
    expect(tree_item(page, 'source', 'remarks')).to_have_count(1)
    expect(tree_item(page, 'source', 'notes')).to_have_count(0)

# ################################################################################################################################

def test_renaming_a_referenced_source_field_rewrites_the_expression(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')

    _rename_field(page, 'source', 'customer', 'client')

    # The review lists the expression update with its before and after ..
    review = page.locator('.mapper-review-dialog')
    expect(review.locator('.mapper-review-item')).to_have_count(1)
    expect(review.locator('.mapper-review-item-before')).to_have_text('customer')
    expect(review.locator('.mapper-review-item-after')).to_have_text('client')

    # .. accepting applies the rename and the rewrite together.
    review.locator('.mapper-button-confirm').click()

    expect(tree_item(page, 'source', 'client')).to_have_count(1)
    expect(page.locator('.mapper-row-expression')).to_have_text('client')

    # The connection line still finds both rows after the rename.
    expect(page.locator('#mapper-canvas-lines path')).to_have_count(1)

# ################################################################################################################################

def test_an_unaccepted_rewrite_keeps_its_old_text(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')

    _rename_field(page, 'source', 'customer', 'client')

    # The rewrite is unchecked, so only the schema rename applies ..
    review = page.locator('.mapper-review-dialog')
    review.locator('.mapper-review-checkbox').uncheck()
    review.locator('.mapper-button-confirm').click()

    expect(tree_item(page, 'source', 'client')).to_have_count(1)

    # .. the expression still says customer, which no longer resolves -
    # a loud state, never a silent breakage.
    expect(page.locator('.mapper-row-expression')).to_have_text('customer')
    expect(page.locator('#mapper-canvas-lines path')).to_have_count(0)

# ################################################################################################################################

def test_renaming_a_target_field_updates_the_row_target(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')

    _rename_field(page, 'target', 'buyer', 'purchaser')

    review = page.locator('.mapper-review-dialog')
    expect(review.locator('.mapper-review-item')).to_have_count(1)
    expect(review).to_contain_text('target path')

    review.locator('.mapper-button-confirm').click()

    expect(tree_item(page, 'target', 'purchaser')).to_have_count(1)
    expect(page.locator('.mapper-row-target')).to_have_text('purchaser')

# ################################################################################################################################

def test_a_rename_propagates_into_scope_children(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    # A scope over the lines, with sku mapped relatively.
    drag_tree_row(page, 'lines.sku', 'items.code')

    _rename_field(page, 'source', 'lines.sku', 'product_code')

    # The child expression is relative to the scope, and the review
    # shows exactly that rewrite.
    review = page.locator('.mapper-review-dialog')
    expect(review.locator('.mapper-review-item-before')).to_have_text('sku')
    expect(review.locator('.mapper-review-item-after')).to_have_text('product_code')

    review.locator('.mapper-button-confirm').click()

    expect(tree_item(page, 'source', 'lines.product_code')).to_have_count(1)
    expect(page.locator('.mapper-scope-rows .mapper-row-expression')).to_have_text('product_code')

# ################################################################################################################################

def test_a_name_clash_is_an_error(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    # The source already has a field named quantity at the top level.
    tree_row(page, 'source', 'notes').click(button='right')
    page.locator('.mapper-context-menu-item', has_text='Rename field').click()

    page.locator('.mapper-dialog-input').fill('quantity')
    page.locator('.mapper-dialog .mapper-button-confirm').click()

    # The dialog stays open with the error and nothing changes.
    expect(page.locator('.mapper-dialog-error')).to_contain_text('quantity')
    expect(tree_item(page, 'source', 'notes')).to_have_count(1)

# ################################################################################################################################
# ################################################################################################################################
