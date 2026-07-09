# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Playwright
from playwright.sync_api import expect, Page

# Zato
from common import add_mapping, add_scope, open_clean_page, open_empty_page, open_preview, set_expression, set_target

# ################################################################################################################################
# ################################################################################################################################

def test_preview_panes_start_with_designed_empty_states(page:'Page', base_url:'str') -> 'None':
    """ Without a source sample both panes explain what will appear in them.
    """
    open_empty_page(page, base_url)
    open_preview(page)

    expect(page.locator('#mapper-preview-input .mapper-preview-empty')).to_be_visible()
    expect(page.locator('#mapper-preview-output .mapper-preview-empty')).to_be_visible()

# ################################################################################################################################

def test_input_pane_shows_the_default_example(page:'Page', base_url:'str') -> 'None':
    """ A first visit starts with the default example in the input pane.
    """
    open_clean_page(page, base_url)
    open_preview(page)

    input_pane = page.locator('#mapper-preview-input')
    expect(input_pane).to_contain_text('"customer"')
    expect(input_pane).to_contain_text('ACME')

    # The sample selector lists the stored sample.
    expect(page.locator('#mapper-preview-sample-select option')).to_have_count(1)

# ################################################################################################################################

def test_output_updates_live_while_typing(page:'Page', base_url:'str') -> 'None':
    """ The output pane follows every keystroke, before the edit is even committed.
    """
    open_clean_page(page, base_url)

    add_mapping(page)
    set_target(page, 'buyer')

    # Typing updates the output without leaving the editor.
    editor = page.locator('#mapper-detail-expression textarea')
    editor.press_sequentially('customer')
    expect(page.locator('#mapper-preview-output')).to_contain_text('ACME')

# ################################################################################################################################

def test_every_row_shows_its_evaluated_value_inline(page:'Page', base_url:'str') -> 'None':
    """ Each mapping row carries the value it produced against the active sample.
    """
    open_clean_page(page, base_url)

    add_mapping(page)
    set_target(page, 'buyer')
    set_expression(page, 'customer')

    add_mapping(page)
    set_target(page, 'amount')
    set_expression(page, 'quantity * unit_price')

    values = page.locator('.mapper-row-value')
    expect(values).to_have_count(2)
    expect(values.nth(0)).to_have_text('"ACME"')
    expect(values.nth(1)).to_have_text('21')

# ################################################################################################################################

def test_a_failing_row_carries_its_own_error(page:'Page', base_url:'str') -> 'None':
    """ A row that fails at evaluation time shows its error inline, other rows still evaluate.
    """
    open_clean_page(page, base_url)

    add_mapping(page)
    set_target(page, 'amount')
    set_expression(page, '$number(customer)')

    add_mapping(page)
    set_target(page, 'buyer')
    set_expression(page, 'customer')

    expect(page.locator('.mapper-row-error')).to_have_count(1)
    expect(page.locator('.mapper-row-value')).to_have_text('"ACME"')

# ################################################################################################################################

def test_scope_rows_preview_one_element_at_a_time(page:'Page', base_url:'str') -> 'None':
    """ A scope's child rows show the values of the picked element.
    """
    open_clean_page(page, base_url)
    add_scope(page)

    # The scope group renders its child rows against the first element ..
    expect(page.locator('.mapper-scope-title')).to_contain_text('invoice.items')
    expect(page.locator('.mapper-scope-rows .mapper-row-value').first).to_have_text('"AA-11"')

    # .. the picker lists every element of the source list ..
    picker = page.locator('.mapper-scope-element-picker')
    expect(picker.locator('option')).to_have_count(2)

    # .. and picking another element switches the previewed values.
    picker.select_option('1')
    expect(page.locator('.mapper-scope-rows .mapper-row-value').first).to_have_text('"BB-22"')

# ################################################################################################################################

def test_scope_output_maps_every_element(page:'Page', base_url:'str') -> 'None':
    """ The output pane carries every element of the scope, not only the previewed one.
    """
    open_clean_page(page, base_url)
    add_scope(page)

    output = page.locator('#mapper-preview-output')
    expect(output).to_contain_text('AA-11')
    expect(output).to_contain_text('BB-22')

# ################################################################################################################################

def test_preview_panes_collapse_and_expand(page:'Page', base_url:'str') -> 'None':
    """ Each pane's toggle hides and shows its body.
    """
    open_clean_page(page, base_url)
    open_preview(page)

    page.locator('#mapper-preview-input-toggle').click()
    expect(page.locator('#mapper-preview-input')).to_be_hidden()

    page.locator('#mapper-preview-input-toggle').click()
    expect(page.locator('#mapper-preview-input')).to_be_visible()

# ################################################################################################################################

def test_editing_the_input_updates_the_output_live(page:'Page', base_url:'str') -> 'None':
    """ Typing new JSON into the input pane re-evaluates the output against it.
    """
    open_clean_page(page, base_url)

    add_mapping(page)
    set_target(page, 'invoice_number')
    set_expression(page, 'customer')

    open_preview(page)
    expect(page.locator('#mapper-preview-output')).to_contain_text('ACME')

    # Replacing the input re-runs the mappings against the new payload ..
    page.locator('#mapper-preview-input').fill('{"customer": "Initech"}')
    expect(page.locator('#mapper-preview-output')).to_contain_text('Initech')

    # .. and the row values follow the edited input too.
    page.locator('.mapper-subtab[data-tab="mappings"]').click()
    expect(page.locator('.mapper-row-value')).to_have_text('"Initech"')

# ################################################################################################################################

def test_invalid_input_is_marked_and_keeps_the_output(page:'Page', base_url:'str') -> 'None':
    """ Text that is not valid JSON marks the input pane and the last good output stays.
    """
    open_clean_page(page, base_url)

    add_mapping(page)
    set_target(page, 'invoice_number')
    set_expression(page, 'customer')

    open_preview(page)
    expect(page.locator('#mapper-preview-output')).to_contain_text('ACME')

    # Broken JSON marks the pane and never clears the output ..
    page.locator('#mapper-preview-input').fill('{"customer": ')
    expect(page.locator('.mapper-preview-input-invalid')).to_be_visible()
    expect(page.locator('#mapper-preview-output')).to_contain_text('ACME')

    # .. and fixing the text lifts the mark and re-evaluates.
    page.locator('#mapper-preview-input').fill('{"customer": "Initech"}')
    expect(page.locator('.mapper-preview-input-invalid')).to_have_count(0)
    expect(page.locator('#mapper-preview-output')).to_contain_text('Initech')

# ################################################################################################################################

def test_preview_panes_resize_by_their_divider(page:'Page', base_url:'str') -> 'None':
    """ The divider between the input and output panes drags vertically and works with the arrow keys.
    """
    open_clean_page(page, base_url)
    open_preview(page)

    input_pane = page.locator('.mapper-preview .mapper-preview-pane').first
    handle = page.locator('#mapper-preview-split')

    initial_bounds = input_pane.bounding_box()
    assert initial_bounds is not None

    # Dragging the divider 100 pixels down grows the input pane ..
    handle_bounds = handle.bounding_box()
    assert handle_bounds is not None

    handle_center_x = handle_bounds['x'] + handle_bounds['width'] / 2
    handle_center_y = handle_bounds['y'] + handle_bounds['height'] / 2

    page.mouse.move(handle_center_x, handle_center_y)
    page.mouse.down()
    page.mouse.move(handle_center_x, handle_center_y + 100, steps=5)
    page.mouse.up()

    grown_bounds = input_pane.bounding_box()
    assert grown_bounds is not None
    assert grown_bounds['height'] > initial_bounds['height'] + 50

    # .. and the arrow keys move the split back up.
    handle.focus()
    page.keyboard.press('ArrowUp')
    page.keyboard.press('ArrowUp')

    shrunk_bounds = input_pane.bounding_box()
    assert shrunk_bounds is not None
    assert shrunk_bounds['height'] < grown_bounds['height']

# ################################################################################################################################
# ################################################################################################################################
