# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Playwright
from playwright.sync_api import expect, Page

# Mapper tests
from common import add_mapping, open_clean_page

# ################################################################################################################################
# ################################################################################################################################

def drag_split(page:'Page', delta_x:'int') -> 'None':
    """ Drags the maps-to-side split divider horizontally by the given distance.
    """
    handle_bounds = page.locator('#mapper-design-split').bounding_box()
    assert handle_bounds is not None

    handle_center_x = handle_bounds['x'] + handle_bounds['width'] / 2
    handle_center_y = handle_bounds['y'] + handle_bounds['height'] / 2

    page.mouse.move(handle_center_x, handle_center_y)
    page.mouse.down()
    page.mouse.move(handle_center_x + delta_x, handle_center_y, steps=5)
    page.mouse.up()

# ################################################################################################################################

def test_side_area_sits_to_the_right_of_the_maps(page:'Page', base_url:'str') -> 'None':
    """ The maps, the divider and the side area line up left to right.
    """
    open_clean_page(page, base_url)

    maps_bounds = page.locator('#mapper-design-maps').bounding_box()
    split_bounds = page.locator('#mapper-design-split').bounding_box()
    side_bounds = page.locator('#mapper-design-side').bounding_box()

    assert maps_bounds is not None
    assert split_bounds is not None
    assert side_bounds is not None

    # The divider starts where the maps end ..
    assert split_bounds['x'] >= maps_bounds['x'] + maps_bounds['width'] - 1

    # .. and the side area starts where the divider ends ..
    assert side_bounds['x'] >= split_bounds['x'] + split_bounds['width'] - 1

    # .. with both areas sharing the same top edge, so they are side by side.
    assert abs(side_bounds['y'] - maps_bounds['y']) < 5

# ################################################################################################################################

def test_dragging_the_divider_changes_the_split(page:'Page', base_url:'str') -> 'None':
    """ Dragging the divider grows and shrinks the maps area and the split survives a reload.
    """
    open_clean_page(page, base_url)

    maps_area = page.locator('#mapper-design-maps')

    initial_bounds = maps_area.bounding_box()
    assert initial_bounds is not None

    # Dragging the divider 150 pixels left shrinks the maps ..
    drag_split(page, -150)

    shrunk_bounds = maps_area.bounding_box()
    assert shrunk_bounds is not None
    assert shrunk_bounds['width'] < initial_bounds['width'] - 100

    # .. and the split survives a reload.
    _ = page.reload()
    restored_bounds = maps_area.bounding_box()
    assert restored_bounds is not None
    assert abs(restored_bounds['width'] - shrunk_bounds['width']) < 5

# ################################################################################################################################

def test_divider_moves_with_the_keyboard(page:'Page', base_url:'str') -> 'None':
    """ The divider is keyboard-operable with the arrow keys.
    """
    open_clean_page(page, base_url)

    maps_area = page.locator('#mapper-design-maps')
    handle = page.locator('#mapper-design-split')

    initial_bounds = maps_area.bounding_box()
    assert initial_bounds is not None

    handle.focus()
    page.keyboard.press('ArrowRight')
    page.keyboard.press('ArrowRight')

    grown_bounds = maps_area.bounding_box()
    assert grown_bounds is not None
    assert grown_bounds['width'] > initial_bounds['width']

    page.keyboard.press('ArrowLeft')

    shrunk_bounds = maps_area.bounding_box()
    assert shrunk_bounds is not None
    assert shrunk_bounds['width'] < grown_bounds['width']

# ################################################################################################################################

def test_subtabs_switch_panels_in_the_side_area(page:'Page', base_url:'str') -> 'None':
    """ The Mappings and Preview subtabs still switch their panels in the new position.
    """
    open_clean_page(page, base_url)

    # The mappings panel is the default ..
    expect(page.locator('#mapper-side-panel-mappings')).to_be_visible()
    expect(page.locator('#mapper-side-panel-preview')).to_be_hidden()

    # .. clicking Preview swaps the panels ..
    page.locator('.mapper-subtab[data-tab="preview"]').click()
    expect(page.locator('#mapper-side-panel-preview')).to_be_visible()
    expect(page.locator('#mapper-side-panel-mappings')).to_be_hidden()

    # .. and the selection survives a reload.
    _ = page.reload()
    expect(page.locator('#mapper-side-panel-preview')).to_be_visible()

# ################################################################################################################################

def test_side_panels_render_inside_the_side_area(page:'Page', base_url:'str') -> 'None':
    """ The mappings list and the detail panel both render within the side area's bounds.
    """
    open_clean_page(page, base_url)

    add_mapping(page)

    side_bounds = page.locator('#mapper-design-side').bounding_box()
    list_bounds = page.locator('#mapper-mapping-list').bounding_box()
    detail_bounds = page.locator('#mapper-detail').bounding_box()

    assert side_bounds is not None
    assert list_bounds is not None
    assert detail_bounds is not None

    # Both sections start at or right of the side area's left edge ..
    assert list_bounds['x'] >= side_bounds['x'] - 1
    assert detail_bounds['x'] >= side_bounds['x'] - 1

    # .. and the detail stacks under the mappings list.
    assert detail_bounds['y'] >= list_bounds['y'] + list_bounds['height'] - 1

# ################################################################################################################################
# ################################################################################################################################
