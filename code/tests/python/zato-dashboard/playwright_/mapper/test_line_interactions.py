# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re

# Playwright
from playwright.sync_api import expect, Page

# Zato
from common import commit_detail, drag_tree_row, open_clean_page, set_condition, set_expression

# ################################################################################################################################
# ################################################################################################################################

def line_midpoint(page:'Page', line_id:'str') -> 'dict':
    """ Returns the page coordinates of the midpoint of one connection line.
    """
    out = page.evaluate("""(lineId) => {
        const svg = document.getElementById('mapper-canvas-lines');
        const svgRect = svg.getBoundingClientRect();
        const line = svg.querySelector('path[data-line="' + lineId + '"]');
        const point = line.getPointAtLength(line.getTotalLength() / 2);
        return {x: svgRect.left + point.x, y: svgRect.top + point.y};
    }""", line_id)

    return out

# ################################################################################################################################

def empty_gutter_point(page:'Page') -> 'dict':
    """ Returns page coordinates inside the gutter but far away from any line.
    """
    out = page.evaluate("""() => {
        const sourceRect = document.getElementById('mapper-schema-column-source').getBoundingClientRect();
        const targetRect = document.getElementById('mapper-schema-column-target').getBoundingClientRect();
        return {x: (sourceRect.right + targetRect.left) / 2, y: sourceRect.top + 4};
    }""")

    return out

# ################################################################################################################################

def target_tree_row(page:'Page', path:'str'):
    """ Returns the locator of one target tree row.
    """
    out = page.locator('#mapper-schema-body-target .mapper-tree-item[data-path="' + path + '"] > .mapper-tree-row')
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_clicking_a_line_selects_its_row(page:'Page', base_url:'str') -> 'None':
    """ A click on a connection line selects the mapping row it belongs to.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')
    drag_tree_row(page, 'quantity', 'amount')

    # The second drop selected the second row ..
    expect(page.locator('.mapper-row-selected')).to_have_attribute('data-row-index', '1')

    # .. and clicking the first row's line moves the selection there.
    midpoint = line_midpoint(page, '0-0')
    page.mouse.click(midpoint['x'], midpoint['y'])

    expect(page.locator('.mapper-row-selected')).to_have_count(1)
    expect(page.locator('.mapper-row-selected')).to_have_attribute('data-row-index', '0')
    expect(page.locator('#mapper-detail')).to_be_visible()
    expect(page.locator('#mapper-detail-target')).to_have_value('buyer')

# ################################################################################################################################

def test_clicking_empty_gutter_space_deselects(page:'Page', base_url:'str') -> 'None':
    """ A click into the gutter away from every line clears the selection.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')

    expect(page.locator('.mapper-row-selected')).to_have_count(1)

    point = empty_gutter_point(page)
    page.mouse.click(point['x'], point['y'])

    expect(page.locator('.mapper-row-selected')).to_have_count(0)
    expect(page.locator('#mapper-detail')).to_be_hidden()

# ################################################################################################################################

def test_escape_deselects(page:'Page', base_url:'str') -> 'None':
    """ Escape clears the selection like a click into empty gutter space.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')

    expect(page.locator('.mapper-row-selected')).to_have_count(1)

    commit_detail(page)
    page.keyboard.press('Escape')

    expect(page.locator('.mapper-row-selected')).to_have_count(0)
    expect(page.locator('#mapper-detail')).to_be_hidden()

# ################################################################################################################################

def test_the_selected_line_never_dims(page:'Page', base_url:'str') -> 'None':
    """ While the gutter hover dims the other lines, the selected one
    stays at full strength next to the hovered one.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')
    drag_tree_row(page, 'quantity', 'amount')
    drag_tree_row(page, 'unit_price', 'invoice_number')

    # The last drop selected the third row, so its line is the selected one.
    expect(page.locator('#mapper-canvas-lines path.mapper-canvas-line-selected')).to_have_count(1)

    # Hovering the first row's line dims the second one ..
    midpoint = line_midpoint(page, '0-0')
    page.mouse.move(midpoint['x'], midpoint['y'])

    expect(page.locator('#mapper-canvas-lines')).to_have_class(re.compile('mapper-canvas-dimmed'))

    def opacity_of(line_id:'str') -> 'str':
        out = page.evaluate(
            "(lineId) => getComputedStyle(document.querySelector('path[data-line=\"' + lineId + '\"]')).opacity",
            line_id)
        return out

    assert opacity_of('1-0') == '0.2'

    # .. but never the hovered one or the selected one.
    assert opacity_of('0-0') == '1'
    assert opacity_of('2-0') == '1'

# ################################################################################################################################

def test_right_clicking_a_line_opens_its_menu(page:'Page', base_url:'str') -> 'None':
    """ A right-click on a line opens a menu with exactly its four entries,
    and Escape closes the menu without touching anything.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')

    midpoint = line_midpoint(page, '0-0')
    page.mouse.click(midpoint['x'], midpoint['y'], button='right')

    entries = page.locator('.mapper-context-menu-item')
    expect(entries).to_have_count(4)
    expect(entries.nth(0)).to_have_text('Edit')
    expect(entries.nth(1)).to_have_text('Add condition')
    expect(entries.nth(2)).to_have_text('Set default')
    expect(entries.nth(3)).to_have_text('Delete')

    page.keyboard.press('Escape')
    expect(page.locator('.mapper-context-menu')).to_have_count(0)
    expect(page.locator('.mapper-row')).to_have_count(1)

# ################################################################################################################################

def test_line_menu_entries_focus_their_detail_fields(page:'Page', base_url:'str') -> 'None':
    """ Edit, Add condition and Set default each select the row and put the
    caret into their own detail field.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')

    focused_by_entry = [
        ('Edit', '#mapper-detail-expression textarea'),
        ('Add condition', '#mapper-detail-condition textarea'),
        ('Set default', '#mapper-detail-default'),
    ]

    for entry_label, focused_selector in focused_by_entry:
        midpoint = line_midpoint(page, '0-0')
        page.mouse.click(midpoint['x'], midpoint['y'], button='right')
        page.locator('.mapper-context-menu-item', has_text=entry_label).click()

        expect(page.locator('.mapper-row-selected')).to_have_count(1)
        expect(page.locator(focused_selector)).to_be_focused()

        # The menu is gone after the entry ran.
        expect(page.locator('.mapper-context-menu')).to_have_count(0)

# ################################################################################################################################

def test_line_menu_delete_removes_the_row(page:'Page', base_url:'str') -> 'None':
    """ The Delete entry of the line menu removes the mapping row.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')
    drag_tree_row(page, 'quantity', 'amount')

    midpoint = line_midpoint(page, '0-0')
    page.mouse.click(midpoint['x'], midpoint['y'], button='right')
    page.locator('.mapper-context-menu-item', has_text='Delete').click()

    expect(page.locator('.mapper-row')).to_have_count(1)
    expect(page.locator('.mapper-row-target')).to_have_text('amount')

# ################################################################################################################################

def test_delete_key_removes_the_selected_row(page:'Page', base_url:'str') -> 'None':
    """ With a row selected, the Delete key removes it.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')

    expect(page.locator('.mapper-row-selected')).to_have_count(1)

    commit_detail(page)
    page.keyboard.press('Delete')

    expect(page.locator('.mapper-row')).to_have_count(0)
    expect(page.locator('#mapper-detail')).to_be_hidden()

# ################################################################################################################################

def test_delete_all_clears_every_row_and_scope(page:'Page', base_url:'str') -> 'None':
    """ The Delete all action clears every top-level row and every scope
    after one confirmation.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')
    drag_tree_row(page, 'lines.sku', 'items.code')

    expect(page.locator('.mapper-row')).to_have_count(2)
    expect(page.locator('.mapper-scope-group')).to_have_count(1)

    page.locator('#mapper-delete-all-mappings').click()

    # Nothing happens before the confirmation ..
    expect(page.locator('.mapper-dialog')).to_be_visible()
    expect(page.locator('.mapper-row')).to_have_count(2)

    # .. and everything clears after it.
    page.locator('.mapper-button-confirm').click()

    expect(page.locator('.mapper-row')).to_have_count(0)
    expect(page.locator('.mapper-scope-group')).to_have_count(0)
    expect(page.locator('#mapper-mapping-list .mapper-empty-state')).to_be_visible()

# ################################################################################################################################

def test_a_conditioned_mapping_colors_its_line_and_badge(page:'Page', base_url:'str') -> 'None':
    """ A mapping with a condition draws its line in the condition color
    and its target badge picks up the same color.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')

    expect(page.locator('#mapper-canvas-lines path.mapper-canvas-line-conditioned')).to_have_count(0)

    set_condition(page, 'quantity > 1')

    expect(page.locator('#mapper-canvas-lines path.mapper-canvas-line-conditioned')).to_have_count(1)

    target_row = target_tree_row(page, 'buyer')
    expect(target_row.locator('.mapper-tree-mapped-badge-conditioned')).to_have_count(1)

# ################################################################################################################################

def test_a_computed_mapping_draws_a_dashed_line(page:'Page', base_url:'str') -> 'None':
    """ An expression beyond a plain copy marks its line as computed,
    which draws dashed even without a selection.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')

    # A plain copy is not computed ..
    expect(page.locator('#mapper-canvas-lines path.mapper-canvas-line-computed')).to_have_count(0)

    # .. a function call is.
    set_expression(page, '$uppercase(customer)')

    expect(page.locator('#mapper-canvas-lines path.mapper-canvas-line-computed')).to_have_count(1)

# ################################################################################################################################

def test_wrap_in_function_rewrites_the_expression(page:'Page', base_url:'str') -> 'None':
    """ Wrap in function on a mapped target field wraps the row's current
    expression in the chosen function.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')

    target_tree_row(page, 'buyer').click(button='right')
    page.locator('.mapper-context-menu-item', has_text='Wrap in function').click()

    # The function list is grouped under category headers.
    expect(page.locator('.mapper-context-menu-header').first).to_have_text('String')

    page.locator('.mapper-context-menu-item', has_text='$lowercase').click()

    expect(page.locator('.mapper-row-expression')).to_have_text('$lowercase(customer)')
    expect(page.locator('.mapper-row-value')).to_have_text('"acme"')

# ################################################################################################################################

def test_set_value_creates_a_constant_mapping(page:'Page', base_url:'str') -> 'None':
    """ Set value on an unmapped target field creates a mapping row whose
    expression is the entered literal, shown with the formula badge.
    """
    open_clean_page(page, base_url)

    target_tree_row(page, 'invoice_number').click(button='right')
    page.locator('.mapper-context-menu-item', has_text='Set value').click()

    page.locator('.mapper-dialog-input').fill('INV-9')
    page.locator('.mapper-button-confirm').click()

    expect(page.locator('.mapper-row-target')).to_have_text('invoice_number')
    expect(page.locator('.mapper-row-expression')).to_have_text('"INV-9"')
    expect(page.locator('#mapper-preview-output')).to_contain_text('INV-9')

    # There is no source line to draw, so the badge tells the story.
    target_row = target_tree_row(page, 'invoice_number')
    expect(target_row.locator('.mapper-tree-mapped-badge-formula')).to_have_count(1)

# ################################################################################################################################
# ################################################################################################################################
