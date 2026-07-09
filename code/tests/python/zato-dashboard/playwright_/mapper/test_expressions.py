# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Playwright
from playwright.sync_api import expect, Page

# Zato
from common import add_mapping, commit_detail, open_clean_page, set_expression, set_target

# ################################################################################################################################
# ################################################################################################################################

def test_detail_panel_opens_for_a_new_mapping(page:'Page', base_url:'str') -> 'None':
    """ Adding a mapping selects it and opens the detail panel.
    """
    open_clean_page(page, base_url)

    # The panel is hidden until a row is selected ..
    expect(page.locator('#mapper-detail')).to_be_hidden()

    # .. adding a mapping selects the new row ..
    add_mapping(page)
    expect(page.locator('#mapper-detail')).to_be_visible()
    expect(page.locator('.mapper-row-selected')).to_have_count(1)

    # .. and the panel edits flow into the row.
    set_target(page, 'invoice_number')
    set_expression(page, 'customer')
    expect(page.locator('.mapper-row-target')).to_have_text('invoice_number')

# ################################################################################################################################

def test_expression_autocomplete_offers_source_fields(page:'Page', base_url:'str') -> 'None':
    """ Typing in the raw editor offers matching source schema paths, Enter accepts one.
    """
    open_clean_page(page, base_url)

    add_mapping(page)
    set_target(page, 'invoice_number')

    # Typing a prefix opens the dropdown with the matching path ..
    editor = page.locator('#mapper-detail-expression textarea')
    editor.press_sequentially('cust')
    expect(page.locator('#mapper-detail-expression .mapper-editor-completion-label').first).to_have_text('customer')

    # .. and Enter completes the token.
    editor.press('Enter')
    expect(editor).to_have_value('customer')

# ################################################################################################################################

def test_expression_autocomplete_offers_functions(page:'Page', base_url:'str') -> 'None':
    """ Function names are offered alongside schema paths, with their short docs.
    """
    open_clean_page(page, base_url)

    add_mapping(page)

    editor = page.locator('#mapper-detail-expression textarea')
    editor.press_sequentially('$upper')

    completion = page.locator('#mapper-detail-expression .mapper-editor-completion').first
    expect(completion.locator('.mapper-editor-completion-label')).to_have_text('$uppercase')
    expect(completion.locator('.mapper-editor-completion-doc')).to_contain_text('upper case')

# ################################################################################################################################

def test_a_broken_expression_is_marked_in_the_editor(page:'Page', base_url:'str') -> 'None':
    """ An expression that does not parse marks its line in the editor gutter.
    """
    open_clean_page(page, base_url)

    add_mapping(page)

    editor = page.locator('#mapper-detail-expression textarea')
    editor.fill('customer +')
    expect(page.locator('#mapper-detail-expression .mapper-editor-gutter-line-error')).to_have_count(1)

    # Fixing the expression clears the marker.
    editor.fill('customer')
    expect(page.locator('#mapper-detail-expression .mapper-editor-gutter-line-error')).to_have_count(0)

# ################################################################################################################################

def test_builder_composes_an_expression_from_pills(page:'Page', base_url:'str') -> 'None':
    """ Field pills and an operator chip build quantity * unit_price without typing.
    """
    open_clean_page(page, base_url)

    add_mapping(page)
    set_target(page, 'amount')

    # The builder opens for an empty expression ..
    page.locator('#mapper-detail-mode-builder').click()
    expect(page.locator('#mapper-detail-builder')).to_be_visible()

    # .. two field pills and an operator chip compose the expression ..
    page.locator('.mapper-builder-field-select').select_option('quantity')
    page.locator('.mapper-builder-operator-chip', has_text='*').click()
    page.locator('.mapper-builder-field-select').select_option('unit_price')

    expect(page.locator('.mapper-builder-pill')).to_have_count(2)
    expect(page.locator('.mapper-builder-chip-operator')).to_have_count(1)

    # .. flipping to the raw editor shows the same expression ..
    page.locator('#mapper-detail-mode-raw').click()
    expect(page.locator('#mapper-detail-expression textarea')).to_have_value('quantity * unit_price')

    # .. and flipping back loses nothing.
    page.locator('#mapper-detail-mode-builder').click()
    expect(page.locator('.mapper-builder-pill')).to_have_count(2)

# ################################################################################################################################

def test_builder_stays_unavailable_for_expressions_it_cannot_represent(page:'Page', base_url:'str') -> 'None':
    """ An expression outside the builder's shape keeps the builder disabled, the text intact.
    """
    open_clean_page(page, base_url)

    add_mapping(page)
    set_target(page, 'items')
    set_expression(page, '$map(lines, function($v) { $v.sku })')

    # Reselect the row so the panel renders from the committed state.
    page.locator('.mapper-row').first.click()

    expect(page.locator('#mapper-detail-mode-builder')).to_be_disabled()
    expect(page.locator('#mapper-detail-expression textarea')).to_have_value('$map(lines, function($v) { $v.sku })')

# ################################################################################################################################

def test_condition_skips_a_row(page:'Page', base_url:'str') -> 'None':
    """ A false condition skips the row and the list says so.
    """
    open_clean_page(page, base_url)

    add_mapping(page)
    set_target(page, 'priority_flag')
    set_expression(page, 'customer')

    condition = page.locator('#mapper-detail-condition textarea')
    condition.fill('quantity > 100')
    commit_detail(page)

    expect(page.locator('.mapper-row-note')).to_have_text('skipped')

# ################################################################################################################################

def test_default_value_fills_an_empty_result(page:'Page', base_url:'str') -> 'None':
    """ An empty result takes the row's default value.
    """
    open_clean_page(page, base_url)

    add_mapping(page)
    set_target(page, 'remarks')
    set_expression(page, 'notes')

    # The sample's notes field is empty, so the default kicks in.
    default_input = page.locator('#mapper-detail-default')
    default_input.fill('No notes')
    default_input.press('Tab')

    expect(page.locator('.mapper-row-value')).to_have_text('"No notes"')
    expect(page.locator('#mapper-preview-output')).to_contain_text('No notes')

# ################################################################################################################################

def test_omit_if_empty_drops_the_field(page:'Page', base_url:'str') -> 'None':
    """ The omit toggle drops an empty result from the output instead of writing it.
    """
    open_clean_page(page, base_url)

    add_mapping(page)
    set_target(page, 'remarks')
    set_expression(page, 'notes')

    # Without the toggle the empty string is written ..
    expect(page.locator('#mapper-preview-output')).to_contain_text('remarks')

    # .. with it the field disappears from the output.
    page.locator('#mapper-detail-omit').check()
    expect(page.locator('.mapper-row-note')).to_have_text('omitted')
    expect(page.locator('#mapper-preview-output')).not_to_contain_text('remarks')

# ################################################################################################################################

def test_removing_a_row_closes_the_detail_panel(page:'Page', base_url:'str') -> 'None':
    """ Removing the selected row deselects it and hides the panel.
    """
    open_clean_page(page, base_url)

    add_mapping(page)
    expect(page.locator('#mapper-detail')).to_be_visible()

    page.locator('.mapper-row-remove').click()
    expect(page.locator('#mapper-detail')).to_be_hidden()
    expect(page.locator('.mapper-row')).to_have_count(0)

# ################################################################################################################################
# ################################################################################################################################
