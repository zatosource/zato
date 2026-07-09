# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Playwright
from playwright.sync_api import expect, Page

# Zato
from common import drag_tree_row, open_empty_page, paste_example, tree_row

# ################################################################################################################################
# ################################################################################################################################

# A source whose names match the target exactly and normalized
_automap_source = """
{
    "customer": "ACME",
    "order_id": "O-1",
    "lines": [
        {"sku": "AA-11", "quantity": 2}
    ]
}
"""

# The matching target - customer matches exactly, OrderID normalized,
# and the lines pair up into an iteration scope suggestion
_automap_target = """
{
    "customer": "?",
    "OrderID": "?",
    "lines": [
        {"sku": "?", "quantity": 0}
    ]
}
"""

# ################################################################################################################################
# ################################################################################################################################

def _paste_both_sides(page:'Page') -> 'None':
    paste_example(page, 'source', _automap_source)
    paste_example(page, 'target', _automap_target)

# ################################################################################################################################

def test_global_automap_suggests_and_applies(page:'Page', base_url:'str') -> 'None':
    open_empty_page(page, base_url)
    _paste_both_sides(page)

    page.locator('#mapper-automap').click()

    # The review lists the two field matches and the scope with its
    # two children, exact and normalized matches told apart.
    review = page.locator('.mapper-review-dialog')
    expect(review.locator('.mapper-review-item')).to_have_count(5)
    expect(review).to_contain_text('customer \u2190 customer')
    expect(review).to_contain_text('OrderID \u2190 order_id')
    expect(review).to_contain_text('lines \u2190 each lines')
    expect(review.locator('.mapper-review-item-note').first).to_have_text('exact name')
    expect(review).to_contain_text('normalized name')

    # Accepting everything creates two rows and the scope with its children.
    review.locator('.mapper-button-confirm').click()

    expect(page.locator('.mapper-row')).to_have_count(4)
    expect(page.locator('.mapper-scope-group')).to_have_count(1)
    expect(page.locator('#mapper-preview-output')).to_contain_text('AA-11')

# ################################################################################################################################

def test_an_unaccepted_suggestion_does_not_apply(page:'Page', base_url:'str') -> 'None':
    open_empty_page(page, base_url)
    _paste_both_sides(page)

    page.locator('#mapper-automap').click()

    review = page.locator('.mapper-review-dialog')

    # Unchecking the scope leaves only the two field suggestions ..
    scope_item = review.locator('.mapper-review-item').filter(has_text='each lines').first
    scope_item.locator('.mapper-review-checkbox').first.uncheck()

    review.locator('.mapper-button-confirm').click()

    # .. so no scope group appears, only the top-level rows.
    expect(page.locator('.mapper-row')).to_have_count(2)
    expect(page.locator('.mapper-scope-group')).to_have_count(0)

# ################################################################################################################################

def test_automap_never_suggests_what_is_already_mapped(page:'Page', base_url:'str') -> 'None':
    open_empty_page(page, base_url)
    _paste_both_sides(page)

    # The customer pair is mapped by hand first ..
    drag_tree_row(page, 'customer', 'customer')

    page.locator('#mapper-automap').click()

    # .. so the review offers everything except that pair.
    review = page.locator('.mapper-review-dialog')
    expect(review.locator('.mapper-review-item')).to_have_count(4)
    expect(review).not_to_contain_text('customer \u2190 customer')

# ################################################################################################################################

def test_a_structure_drop_opens_the_scoped_review(page:'Page', base_url:'str') -> 'None':
    open_empty_page(page, base_url)

    # Both sides carry one nested structure with matching children.
    paste_example(page, 'source', '{"header": {"name": "a", "city": "b"}, "other": 1}')
    paste_example(page, 'target', '{"header": {"name": "x", "city": "y"}, "misc": 2}')

    # Dropping one structure onto the other scopes the suggestions to the pair.
    drag_tree_row(page, 'header', 'header')

    review = page.locator('.mapper-review-dialog')
    expect(review).to_contain_text('header from header')
    expect(review.locator('.mapper-review-item')).to_have_count(2)
    expect(review).to_contain_text('header.name \u2190 header.name')
    expect(review).to_contain_text('header.city \u2190 header.city')

    review.locator('.mapper-button-confirm').click()

    # The accepted suggestions land as plain rows with absolute paths ..
    expect(page.locator('.mapper-row')).to_have_count(2)
    expect(page.locator('.mapper-row-target').first).to_have_text('header.name')

    # .. and the source badges reflect the new references.
    expect(tree_row(page, 'source', 'header.name').locator('.mapper-tree-usage-badge')).to_have_text('1')

# ################################################################################################################################

def test_automap_with_nothing_to_suggest_shows_the_empty_state(page:'Page', base_url:'str') -> 'None':
    open_empty_page(page, base_url)

    # No names match between the two sides.
    paste_example(page, 'source', '{"alpha": 1}')
    paste_example(page, 'target', '{"omega": 2}')

    page.locator('#mapper-automap').click()

    review = page.locator('.mapper-review-dialog')
    expect(review.locator('.mapper-review-empty')).to_contain_text('Nothing to suggest')

    # The empty review only closes, it never applies anything.
    review.locator('.mapper-button-confirm').click()
    expect(page.locator('.mapper-row')).to_have_count(0)

# ################################################################################################################################
# ################################################################################################################################
