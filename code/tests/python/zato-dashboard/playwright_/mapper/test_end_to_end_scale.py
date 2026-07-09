# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Playwright
from playwright.sync_api import expect, Page

# Zato
from common import open_empty_page, paste_example, tree_item, tree_row

# ################################################################################################################################
# ################################################################################################################################

def test_scale_end_to_end(page:'Page', base_url:'str') -> 'None':
    """ A full session over the Group 4 features: paste two schemas, auto-map
    them with a review, inspect usage, search and filter the trees, rename a
    field with its expression propagating, and re-import a changed schema -
    with the output correct throughout.
    """
    open_empty_page(page, base_url)

    paste_example(page, 'source', """
    {
        "customer": "ACME",
        "order_id": "O-1",
        "internal_code": "X",
        "lines": [
            {"sku": "AA-11", "quantity": 2}
        ]
    }
    """)
    paste_example(page, 'target', """
    {
        "customer": "?",
        "OrderID": "?",
        "reference": "?",
        "lines": [
            {"sku": "?", "quantity": 0}
        ]
    }
    """)

    # Auto-map suggests the matching names, exactly and normalized,
    # and the lines pair up into an iteration scope with children ..
    page.locator('#mapper-automap').click()

    review = page.locator('.mapper-review-dialog')
    expect(review).to_contain_text('customer \u2190 customer')
    expect(review).to_contain_text('OrderID \u2190 order_id')
    expect(review).to_contain_text('lines \u2190 each lines')

    # .. everything accepted lands in one undoable step ..
    review.locator('.mapper-button-confirm').click()
    expect(page.locator('.mapper-row')).to_have_count(4)
    expect(page.locator('.mapper-scope-group')).to_have_count(1)
    expect(page.locator('#mapper-preview-output')).to_contain_text('AA-11')

    # .. the source usage badges count the new references ..
    expect(tree_row(page, 'source', 'customer').locator('.mapper-tree-usage-badge')).to_have_text('1')

    # .. search finds fields and expressions across the page ..
    page.locator('#mapper-search-input').fill('order')
    expect(page.locator('#mapper-search-count')).to_have_text('1 of 3')
    page.locator('#mapper-search-next').click()
    expect(page.locator('#mapper-search-count')).to_have_text('2 of 3')
    page.locator('#mapper-search-input').fill('')

    # .. the unmapped filter narrows the trees to the gaps ..
    page.locator('.mapper-filter-button[data-filter="unmapped"]').click()
    expect(tree_row(page, 'source', 'internal_code')).to_be_visible()
    expect(tree_row(page, 'source', 'customer')).to_be_hidden()
    expect(tree_row(page, 'target', 'reference')).to_be_visible()
    page.locator('.mapper-filter-button[data-filter="all"]').click()

    # .. renaming a mapped source field propagates into its expression ..
    tree_row(page, 'source', 'customer').click(button='right')
    page.locator('.mapper-context-menu-item', has_text='Rename field').click()
    page.locator('.mapper-dialog-input').fill('client')
    page.locator('.mapper-dialog .mapper-button-confirm').click()

    rename_review = page.locator('.mapper-review-dialog')
    expect(rename_review.locator('.mapper-review-item')).to_have_count(1)
    rename_review.locator('.mapper-button-confirm').click()

    expect(tree_item(page, 'source', 'client')).to_have_count(1)
    expect(page.locator('.mapper-row-expression').first).to_have_text('client')

    # .. a re-imported example with one field gone goes through review ..
    page.locator('#mapper-schema-actions-source .mapper-action-reimport').click()
    page.locator('.mapper-dialog-textarea').fill("""
    {
        "client": "ACME",
        "order_id": "O-1",
        "lines": [
            {"sku": "AA-11", "quantity": 2}
        ]
    }
    """)
    page.locator('.mapper-dialog .mapper-button-confirm').click()

    reimport_review = page.locator('.mapper-review-dialog')
    expect(reimport_review).to_contain_text('Removed: internal_code')
    reimport_review.locator('.mapper-button-confirm').click()
    expect(tree_item(page, 'source', 'internal_code')).to_have_count(0)

    # .. and the whole session survives a reload from autosave.
    _ = page.reload()
    expect(page.locator('.mapper-row')).to_have_count(4)
    expect(page.locator('#mapper-preview-output')).to_contain_text('AA-11')

# ################################################################################################################################
# ################################################################################################################################
