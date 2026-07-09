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
from common import drag_tree_row, open_clean_page

# ################################################################################################################################
# ################################################################################################################################

def test_dragging_a_field_onto_a_field_creates_a_mapping(page:'Page', base_url:'str') -> 'None':
    """ Dragging a source leaf onto a target leaf creates a row in the mapping list.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')

    # The row appears with the dragged paths ..
    expect(page.locator('.mapper-row-target')).to_have_text('buyer')
    expect(page.locator('.mapper-row-expression')).to_have_text('customer')

    # .. it is selected and the detail panel opens on it ..
    expect(page.locator('.mapper-row-selected')).to_have_count(1)
    expect(page.locator('#mapper-detail')).to_be_visible()
    expect(page.locator('#mapper-detail-target')).to_have_value('buyer')

    # .. and the output pane carries the mapped value.
    expect(page.locator('.mapper-row-value')).to_have_text('"ACME"')
    expect(page.locator('#mapper-preview-output')).to_contain_text('ACME')

# ################################################################################################################################

def test_mapped_fields_carry_badges_on_both_trees(page:'Page', base_url:'str') -> 'None':
    """ A mapped field carries a compact badge on its tree instead of a permanent line.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')

    source_row = page.locator('#mapper-schema-body-source .mapper-tree-item[data-path="customer"] > .mapper-tree-row')
    expect(source_row.locator('.mapper-tree-mapped-badge')).to_have_count(1)

    target_row = page.locator('#mapper-schema-body-target .mapper-tree-item[data-path="buyer"] > .mapper-tree-row')
    expect(target_row.locator('.mapper-tree-mapped-badge')).to_have_count(1)

# ################################################################################################################################

def test_every_connection_line_is_visible(page:'Page', base_url:'str') -> 'None':
    """ The line layer always draws every connection - plain rows, the scope
    between two lists and the rows inside it, all at the same time.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')
    drag_tree_row(page, 'quantity', 'amount')
    drag_tree_row(page, 'lines.sku', 'items.code')

    # Two plain rows, the lines-to-items scope and its child row
    # make four lines, each of them visible.
    lines = page.locator('#mapper-canvas-lines path')
    expect(lines).to_have_count(4)

    for line_idx in range(4):
        expect(lines.nth(line_idx)).to_be_visible()

    # The selected row's line stands out from the rest.
    expect(page.locator('#mapper-canvas-lines path.mapper-canvas-line-selected')).to_have_count(1)

    # Nothing is dimmed while the pointer stays away from the gutter.
    expect(page.locator('#mapper-canvas-lines')).not_to_have_class(re.compile('mapper-canvas-dimmed'))

# ################################################################################################################################

def test_gutter_hover_dims_all_lines_except_the_hovered_one(page:'Page', base_url:'str') -> 'None':
    """ Moving the pointer over the gutter dims every line except the one
    under the pointer, and leaving the gutter restores them all.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')
    drag_tree_row(page, 'quantity', 'amount')

    expect(page.locator('#mapper-canvas-lines path')).to_have_count(2)

    # The midpoint of the first line, in page coordinates.
    midpoint = page.evaluate("""() => {
        const svg = document.getElementById('mapper-canvas-lines');
        const svgRect = svg.getBoundingClientRect();
        const line = svg.querySelector('path');
        const point = line.getPointAtLength(line.getTotalLength() / 2);
        return {x: svgRect.left + point.x, y: svgRect.top + point.y};
    }""")

    page.mouse.move(midpoint['x'], midpoint['y'])

    # Everything dims except the line under the pointer.
    expect(page.locator('#mapper-canvas-lines')).to_have_class(re.compile('mapper-canvas-dimmed'))
    expect(page.locator('#mapper-canvas-lines path.mapper-canvas-line-hovered')).to_have_count(1)

    # Both lines are still in the layer - dimming hides nothing.
    expect(page.locator('#mapper-canvas-lines path')).to_have_count(2)

    # The rows the lit line connects light up with it.
    expect(page.locator('.mapper-tree-row-connected-source')).to_have_count(1)
    expect(page.locator('.mapper-tree-row-connected-target')).to_have_count(1)

    # Moving back over a tree lifts the dimming and the row highlights.
    page.locator('#mapper-schema-body-source .mapper-tree-item[data-path="customer"] > .mapper-tree-row').hover()
    expect(page.locator('#mapper-canvas-lines')).not_to_have_class(re.compile('mapper-canvas-dimmed'))
    expect(page.locator('#mapper-canvas-lines path.mapper-canvas-line-hovered')).to_have_count(0)
    expect(page.locator('.mapper-tree-row-connected-source')).to_have_count(0)
    expect(page.locator('.mapper-tree-row-connected-target')).to_have_count(0)

# ################################################################################################################################

def test_dragging_a_list_onto_a_list_creates_a_scope(page:'Page', base_url:'str') -> 'None':
    """ Two repeating nodes dropped onto each other become an iteration scope.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'lines', 'items')

    expect(page.locator('.mapper-scope-title')).to_contain_text('items')
    expect(page.locator('.mapper-scope-title')).to_contain_text('lines')

    # Children then map relatively within the scope.
    drag_tree_row(page, 'lines.sku', 'items.code')

    child_row = page.locator('.mapper-scope-rows .mapper-row')
    expect(child_row.locator('.mapper-row-target')).to_have_text('code')
    expect(child_row.locator('.mapper-row-expression')).to_have_text('sku')
    expect(child_row.locator('.mapper-row-value')).to_have_text('"AA-11"')

    # The output maps every element of the source list.
    output = page.locator('#mapper-preview-output')
    expect(output).to_contain_text('AA-11')
    expect(output).to_contain_text('BB-22')

# ################################################################################################################################

def test_dropping_nested_leaves_creates_the_scope_automatically(page:'Page', base_url:'str') -> 'None':
    """ A leaf under a list dropped onto a leaf under another list creates the scope on its own.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'lines.sku', 'items.code')

    # The scope arrived together with its first child row.
    expect(page.locator('.mapper-scope-title')).to_contain_text('items')
    expect(page.locator('.mapper-scope-rows .mapper-row-target')).to_have_text('code')
    expect(page.locator('#mapper-preview-output')).to_contain_text('BB-22')

# ################################################################################################################################

def test_a_repeating_target_refuses_a_single_source_value(page:'Page', base_url:'str') -> 'None':
    """ A field repeating per element cannot take one scalar - the drop is refused with a notice.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'unit_price', 'items.code')

    # No row is created and the notice explains why.
    expect(page.locator('.mapper-row')).to_have_count(0)

    notice = page.locator('#mapper-page-notice')
    expect(notice).to_be_visible()
    expect(notice).to_contain_text('repeats per element')

# ################################################################################################################################

def test_a_second_drop_never_overwrites_silently(page:'Page', base_url:'str') -> 'None':
    """ Dropping onto an already-mapped target selects the existing row instead of replacing it.
    """
    open_clean_page(page, base_url)
    drag_tree_row(page, 'customer', 'buyer')
    drag_tree_row(page, 'quantity', 'buyer')

    # Still one row, with the original expression, selected for editing.
    expect(page.locator('.mapper-row')).to_have_count(1)
    expect(page.locator('.mapper-row-expression')).to_have_text('customer')
    expect(page.locator('.mapper-row-selected')).to_have_count(1)

# ################################################################################################################################
# ################################################################################################################################
