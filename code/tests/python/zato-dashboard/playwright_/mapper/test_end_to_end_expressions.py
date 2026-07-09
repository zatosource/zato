# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Playwright
from playwright.sync_api import expect, Page

# Zato
from common import add_mapping, open_clean_page, set_expression, set_target

# ################################################################################################################################
# ################################################################################################################################

def test_expressions_and_preview_end_to_end(page:'Page', base_url:'str') -> 'None':
    """ A full session: build an expression from pills, flip modes, watch the
    output follow live, break the expression and recover.
    """

    # A first visit starts with the default examples on both sides ..
    open_clean_page(page, base_url)

    # .. a first mapping is written by hand ..
    add_mapping(page)
    set_target(page, 'invoice_number')
    set_expression(page, 'customer')

    expect(page.locator('.mapper-row-value')).to_have_text('"ACME"')
    expect(page.locator('#mapper-preview-output')).to_contain_text('ACME')

    # .. a second one is built from pills without typing ..
    add_mapping(page)
    set_target(page, 'amount')

    page.locator('#mapper-detail-mode-builder').click()
    page.locator('.mapper-builder-field-select').select_option('quantity')
    page.locator('.mapper-builder-operator-chip', has_text='*').click()
    page.locator('.mapper-builder-field-select').select_option('unit_price')

    # .. flipping to raw shows the built text, flipping back keeps the pills ..
    page.locator('#mapper-detail-mode-raw').click()
    expect(page.locator('#mapper-detail-expression textarea')).to_have_value('quantity * unit_price')

    page.locator('#mapper-detail-mode-builder').click()
    expect(page.locator('.mapper-builder-pill')).to_have_count(2)

    # .. every row shows its value inline and the output pane has both fields ..
    values = page.locator('.mapper-row-value')
    expect(values).to_have_count(2)
    expect(values.nth(1)).to_have_text('21')
    expect(page.locator('#mapper-preview-output')).to_contain_text('21')

    # .. breaking the first expression surfaces at that row alone ..
    page.locator('.mapper-row').first.click()
    set_expression(page, 'customer +')

    expect(page.locator('.mapper-row-error')).to_have_count(1)
    expect(page.locator('.mapper-row-value')).to_have_text('21')

    # .. and fixing it brings the value back.
    page.locator('.mapper-row').first.click()
    set_expression(page, 'customer')

    expect(page.locator('.mapper-row-error')).to_have_count(0)
    expect(page.locator('.mapper-row-value')).to_have_count(2)

# ################################################################################################################################
# ################################################################################################################################
