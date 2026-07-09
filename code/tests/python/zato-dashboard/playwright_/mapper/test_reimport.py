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

# The default source example, with notes gone and a new priority flag
_changed_source = """
{
    "customer": "ACME",
    "quantity": 2,
    "unit_price": 10.5,
    "priority": true,
    "lines": [
        {"sku": "AA-11", "quantity": 2}
    ]
}
"""

# ################################################################################################################################
# ################################################################################################################################

def _reimport(page:'Page', side:'str', payload_text:'str') -> 'None':
    """ Pastes a changed example through one side's re-import dialog.
    """
    page.locator('#mapper-schema-actions-' + side + ' .mapper-action-reimport').click()

    page.locator('.mapper-dialog-textarea').fill(payload_text)
    page.locator('.mapper-dialog .mapper-button-confirm').click()

# ################################################################################################################################

def test_the_review_lists_added_and_removed_fields(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    _reimport(page, 'source', _changed_source)

    review = page.locator('.mapper-review-dialog')
    expect(review.locator('.mapper-review-item')).to_have_count(2)
    expect(review).to_contain_text('Removed: notes')
    expect(review).to_contain_text('Added: priority')

    # Accepting both reshapes the tree accordingly.
    review.locator('.mapper-button-confirm').click()

    expect(tree_item(page, 'source', 'priority')).to_have_count(1)
    expect(tree_item(page, 'source', 'notes')).to_have_count(0)

# ################################################################################################################################

def test_an_unaccepted_change_keeps_the_current_shape(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    _reimport(page, 'source', _changed_source)

    # The removal stays unaccepted, the addition applies ..
    review = page.locator('.mapper-review-dialog')
    removal = review.locator('.mapper-review-item').filter(has_text='Removed: notes')
    removal.locator('.mapper-review-checkbox').uncheck()

    review.locator('.mapper-button-confirm').click()

    # .. so both fields are in the tree afterwards.
    expect(tree_item(page, 'source', 'notes')).to_have_count(1)
    expect(tree_item(page, 'source', 'priority')).to_have_count(1)

# ################################################################################################################################

def test_a_type_change_shows_before_and_after(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    # The quantity arrives as a string this time.
    _reimport(page, 'source', """
    {
        "customer": "ACME",
        "quantity": "2",
        "unit_price": 10.5,
        "notes": "",
        "lines": [
            {"sku": "AA-11", "quantity": 2}
        ]
    }
    """)

    review = page.locator('.mapper-review-dialog')
    expect(review).to_contain_text('Type changed: quantity')
    expect(review.locator('.mapper-review-item-before')).to_have_text('number')
    expect(review.locator('.mapper-review-item-after')).to_have_text('string')

    review.locator('.mapper-button-confirm').click()

    expect(tree_row(page, 'source', 'quantity').locator('.mapper-tree-type-badge')).to_have_text('string')

# ################################################################################################################################

def test_a_rename_is_detected_and_propagates(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    # The customer field is referenced by a mapping ..
    drag_tree_row(page, 'customer', 'buyer')

    # .. and the re-imported example calls it client instead.
    _reimport(page, 'source', """
    {
        "client": "ACME",
        "quantity": 2,
        "unit_price": 10.5,
        "notes": "",
        "lines": [
            {"sku": "AA-11", "quantity": 2}
        ]
    }
    """)

    # The removed-and-added pair reads as one rename, with the mapping
    # it affects listed under it.
    review = page.locator('.mapper-review-dialog')
    expect(review.locator('.mapper-review-item')).to_have_count(1)
    expect(review).to_contain_text('Renamed: customer to client')
    expect(review.locator('.mapper-review-item-detail')).to_contain_text('Used by buyer')

    # Accepting the rename rewrites the expression with it.
    review.locator('.mapper-button-confirm').click()

    expect(tree_item(page, 'source', 'client')).to_have_count(1)
    expect(page.locator('.mapper-row-expression')).to_have_text('client')

# ################################################################################################################################

def test_an_identical_reimport_only_adds_the_sample(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)
    expect(page.locator('#mapper-sample-count-source')).to_have_text('1')

    # The pasted example matches the current schema exactly.
    _reimport(page, 'source', """
    {
        "customer": "ACME",
        "quantity": 2,
        "unit_price": 10.5,
        "notes": "",
        "lines": [
            {"sku": "AA-11", "quantity": 2}
        ]
    }
    """)

    review = page.locator('.mapper-review-dialog')
    expect(review.locator('.mapper-review-empty')).to_contain_text('matches the current schema')
    review.locator('.mapper-button-confirm').click()

    expect(page.locator('#mapper-sample-count-source')).to_have_text('2')

# ################################################################################################################################

def test_a_mapping_onto_a_removed_field_is_never_deleted(page:'Page', base_url:'str') -> 'None':
    open_clean_page(page, base_url)

    # The notes field is referenced before its removal.
    drag_tree_row(page, 'notes', 'buyer')

    _reimport(page, 'source', _changed_source)

    review = page.locator('.mapper-review-dialog')
    expect(review.locator('.mapper-review-item').filter(has_text='Removed: notes')).to_contain_text('Used by buyer')

    review.locator('.mapper-button-confirm').click()

    # The mapping stays even though its source field is gone - the
    # unresolvable reference is a validation matter, not a deletion.
    expect(page.locator('.mapper-row')).to_have_count(1)
    expect(page.locator('.mapper-row-expression')).to_have_text('notes')
    expect(tree_item(page, 'source', 'notes')).to_have_count(0)

# ################################################################################################################################
# ################################################################################################################################
