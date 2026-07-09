# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Playwright
from playwright.sync_api import expect, Page

# Mapper tests
from common import open_clean_page

# ################################################################################################################################
# ################################################################################################################################

def test_toolbar_renders(page:'Page', base_url:'str') -> 'None':
    """ The toolbar shows the mapping name input and all action buttons.
    """
    open_clean_page(page, base_url)

    expect(page.locator('#mapper-name')).to_have_value('New mapping')
    expect(page.locator('#mapper-undo')).to_be_visible()
    expect(page.locator('#mapper-redo')).to_be_visible()
    expect(page.locator('#mapper-export')).to_be_visible()
    expect(page.locator('#mapper-import')).to_be_visible()

    # Nothing happened yet, so there is nothing to undo or redo.
    expect(page.locator('#mapper-undo')).to_be_disabled()
    expect(page.locator('#mapper-redo')).to_be_disabled()

# ################################################################################################################################

def test_tabs_render_and_switch(page:'Page', base_url:'str') -> 'None':
    """ All four tabs render, clicking one shows its panel and hides the others.
    """
    open_clean_page(page, base_url)

    tabs = page.locator('.mapper-tab')
    expect(tabs).to_have_count(4)
    expect(tabs.nth(0)).to_have_text('Design')
    expect(tabs.nth(1)).to_have_text('Code')
    expect(tabs.nth(2)).to_have_text('Tests')
    expect(tabs.nth(3)).to_have_text('Import')

    # Design is the default tab ..
    expect(page.locator('#mapper-panel-design')).to_be_visible()
    expect(page.locator('#mapper-panel-code')).to_be_hidden()

    # .. clicking Code switches the panels ..
    page.locator('.mapper-tab[data-tab="code"]').click()
    expect(page.locator('#mapper-panel-code')).to_be_visible()
    expect(page.locator('#mapper-panel-design')).to_be_hidden()

    # .. and the selection survives a reload.
    _ = page.reload()
    expect(page.locator('#mapper-panel-code')).to_be_visible()
    expect(page.locator('.mapper-tab[data-tab="code"]')).to_have_class('mapper-tab dashboard-tab mapper-tab-active dashboard-tab-active')

# ################################################################################################################################

def test_vendored_libraries_load(page:'Page', base_url:'str') -> 'None':
    """ Every vendored dependency is present on the page.
    """
    open_clean_page(page, base_url)

    assert page.evaluate('typeof jQuery') == 'function'
    assert page.evaluate('typeof window.store') == 'function'
    assert page.evaluate('typeof hotkeys') == 'function'
    assert page.evaluate('typeof Sortable') == 'function'
    assert page.evaluate('typeof jsonata') == 'function'

# ################################################################################################################################

def test_empty_states_are_designed(page:'Page', base_url:'str') -> 'None':
    """ The panels of upcoming features show designed empty states, never blank panes.
    """
    open_clean_page(page, base_url)

    page.locator('.mapper-tab[data-tab="code"]').click()
    expect(page.locator('#mapper-panel-code .mapper-empty-state-title')).to_have_text('Code view')

    page.locator('.mapper-tab[data-tab="tests"]').click()
    expect(page.locator('#mapper-panel-tests .mapper-empty-state-title')).to_have_text('Tests')

    page.locator('.mapper-tab[data-tab="import"]').click()
    expect(page.locator('#mapper-panel-import .mapper-empty-state-title')).to_have_text('Import')

# ################################################################################################################################

def drag_resize_edge(page:'Page', handle_id:'str', delta_x:'int') -> 'None':
    """ Drags one of the panel edge handles horizontally by the given distance.
    """
    handle_bounds = page.locator(handle_id).bounding_box()
    assert handle_bounds is not None

    handle_center_x = handle_bounds['x'] + handle_bounds['width'] / 2
    handle_center_y = handle_bounds['y'] + handle_bounds['height'] / 2

    page.mouse.move(handle_center_x, handle_center_y)
    page.mouse.down()
    page.mouse.move(handle_center_x + delta_x, handle_center_y, steps=5)
    page.mouse.up()

# ################################################################################################################################

def test_panels_resize_by_their_borders(page:'Page', base_url:'str') -> 'None':
    """ The facing borders of both panels act as resize handles and the split survives a reload.
    """
    open_clean_page(page, base_url)

    source_column = page.locator('.mapper-design-columns .mapper-schema-column').first

    source_bounds = source_column.bounding_box()
    assert source_bounds is not None

    # Dragging the source panel's right border 150 pixels grows it ..
    drag_resize_edge(page, '#mapper-resize-edge-source', 150)

    resized_bounds = source_column.bounding_box()
    assert resized_bounds is not None
    assert resized_bounds['width'] > source_bounds['width'] + 100

    # .. dragging the target panel's left border back shrinks it again ..
    drag_resize_edge(page, '#mapper-resize-edge-target', -100)

    shrunk_bounds = source_column.bounding_box()
    assert shrunk_bounds is not None
    assert shrunk_bounds['width'] < resized_bounds['width'] - 50

    # .. and the split survives a reload.
    _ = page.reload()
    restored_bounds = source_column.bounding_box()
    assert restored_bounds is not None
    assert abs(restored_bounds['width'] - shrunk_bounds['width']) < 5

# ################################################################################################################################

def test_panels_resize_with_the_keyboard(page:'Page', base_url:'str') -> 'None':
    """ The edge handles are keyboard-operable with the arrow keys.
    """
    open_clean_page(page, base_url)

    source_column = page.locator('.mapper-design-columns .mapper-schema-column').first
    handle = page.locator('#mapper-resize-edge-target')

    source_bounds = source_column.bounding_box()
    assert source_bounds is not None

    handle.focus()
    page.keyboard.press('ArrowRight')
    page.keyboard.press('ArrowRight')

    resized_bounds = source_column.bounding_box()
    assert resized_bounds is not None
    assert resized_bounds['width'] > source_bounds['width']

# ################################################################################################################################

def test_default_examples_render_on_first_visit(page:'Page', base_url:'str') -> 'None':
    """ A first visit is never blank - both sides carry a default example until the user pastes their own.
    """
    open_clean_page(page, base_url)

    # Both trees render from the default examples ..
    source_row = page.locator('#mapper-schema-body-source .mapper-tree-item[data-path="customer"] > .mapper-tree-row')
    expect(source_row.locator('.mapper-tree-type-badge')).to_have_text('string')

    target_row = page.locator('#mapper-schema-body-target .mapper-tree-item[data-path="invoice_number"] > .mapper-tree-row')
    expect(target_row.locator('.mapper-tree-type-badge')).to_have_text('string')

    # .. each side has its example stored as a sample ..
    expect(page.locator('#mapper-sample-count-source')).to_have_text('1')
    expect(page.locator('#mapper-sample-count-target')).to_have_text('1')

    # .. and the defaults arrive with nothing to undo.
    expect(page.locator('#mapper-undo')).to_be_disabled()

# ################################################################################################################################

def test_mapping_name_edit_is_stored(page:'Page', base_url:'str') -> 'None':
    """ Renaming the mapping goes through the store and survives a reload.
    """
    open_clean_page(page, base_url)

    name_input = page.locator('#mapper-name')
    name_input.fill('Order to invoice')
    name_input.blur()

    # The change lands in browser storage, so a reload keeps it.
    _ = page.reload()
    expect(page.locator('#mapper-name')).to_have_value('Order to invoice')

# ################################################################################################################################
# ################################################################################################################################
