# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Playwright
from playwright.sync_api import Locator, Page

# ################################################################################################################################
# ################################################################################################################################

# A source-side example used across the schema tests
source_example = """
{
    "customer": "ACME",
    "total": 125.5,
    "is_priority": true,
    "created": "2026-05-01",
    "lines": [
        {"sku": "AA-11", "quantity": 2},
        {"sku": "BB-22", "quantity": 5, "discount": 0.1}
    ]
}
"""

# A target-side example used across the schema tests
target_example = """
{
    "invoice_number": "INV-100",
    "amount": 125.5,
    "items": [
        {"code": "AA-11", "count": 2}
    ]
}
"""

# ################################################################################################################################
# ################################################################################################################################

# The mapper is a regular Dashboard page under this path.
mapper_path = '/zato/mapping/'

# ################################################################################################################################
# ################################################################################################################################

def open_clean_page(page:'Page', base_url:'str') -> 'None':
    """ Opens the mapper page with empty browser storage - a first visit,
    which starts with the default examples on both sides.
    """

    # Storage is origin-scoped, so the page loads first ..
    _ = page.goto(base_url + mapper_path)

    # .. then storage is cleared and the page reloads clean.
    _ = page.evaluate('localStorage.clear()')
    _ = page.reload()

# ################################################################################################################################

def open_empty_page(page:'Page', base_url:'str') -> 'None':
    """ Opens the mapper page with an empty artifact and no default examples,
    for tests that exercise pasting and empty states from scratch.
    """

    # Storage is origin-scoped, so the page loads first ..
    _ = page.goto(base_url + mapper_path)
    _ = page.evaluate('localStorage.clear()')

    # .. an empty artifact stored ahead of the reload means the page
    # restores it instead of seeding the default examples.
    _ = page.evaluate(
        'window.store.set(zato.mapper.config.artifactStorageKey,'
        ' zato.mapper.store.serialize(zato.mapper.store.newArtifact()))'
    )
    _ = page.reload()

# ################################################################################################################################

def paste_example(page:'Page', side:'str', payload_text:'str') -> 'None':
    """ Pastes a JSON example into one side's schema panel through its dialog.
    """
    actions = page.locator('#mapper-schema-actions-' + side)
    actions.locator('.mapper-action-paste-example').click()

    page.locator('.mapper-dialog-textarea').fill(payload_text)
    page.locator('.mapper-button-confirm').click()

# ################################################################################################################################

def paste_json_schema(page:'Page', side:'str', document_text:'str') -> 'None':
    """ Pastes a JSON Schema document into one side's schema panel through its dialog.
    """
    actions = page.locator('#mapper-schema-actions-' + side)
    actions.locator('.mapper-action-paste-json-schema').click()

    page.locator('.mapper-dialog-textarea').fill(document_text)
    page.locator('.mapper-button-confirm').click()

# ################################################################################################################################

def open_preview(page:'Page') -> 'None':
    """ Switches the side Design-tab area to its Preview tab.
    """
    page.locator('.mapper-subtab[data-tab="preview"]').click()

# ################################################################################################################################

def add_mapping(page:'Page') -> 'None':
    """ Adds a new mapping row, which also selects it and opens the detail panel.
    """
    page.locator('#mapper-add-mapping').click()

# ################################################################################################################################

def commit_detail(page:'Page') -> 'None':
    """ Moves focus away from the detail panel, committing any pending edit.
    """

    # The source column's title is inert, so clicking it only blurs the detail editor.
    page.locator('#mapper-schema-column-source .mapper-schema-column-title').click()

# ################################################################################################################################

def set_target(page:'Page', path:'str') -> 'None':
    """ Sets the selected mapping's target path through the detail panel.
    """
    target_input = page.locator('#mapper-detail-target')
    target_input.fill(path)
    target_input.press('Tab')

# ################################################################################################################################

def set_expression(page:'Page', text:'str') -> 'None':
    """ Sets the selected mapping's expression through the raw editor.
    """
    editor = page.locator('#mapper-detail-expression textarea')
    editor.fill(text)
    commit_detail(page)

# ################################################################################################################################

def set_condition(page:'Page', text:'str') -> 'None':
    """ Sets the selected mapping's condition through its editor.
    """
    editor = page.locator('#mapper-detail-condition textarea')
    editor.fill(text)
    commit_detail(page)

# ################################################################################################################################

def drag_tree_row(page:'Page', source_path:'str', target_path:'str') -> 'None':
    """ Drags a source tree row onto a target tree row with the mouse.
    """
    source_row = page.locator('#mapper-schema-body-source .mapper-tree-item[data-path="' + source_path + '"] > .mapper-tree-row')
    target_row = page.locator('#mapper-schema-body-target .mapper-tree-item[data-path="' + target_path + '"] > .mapper-tree-row')

    source_bounds = source_row.bounding_box()
    target_bounds = target_row.bounding_box()
    assert source_bounds is not None
    assert target_bounds is not None

    page.mouse.move(source_bounds['x'] + source_bounds['width'] / 2, source_bounds['y'] + source_bounds['height'] / 2)
    page.mouse.down()
    page.mouse.move(target_bounds['x'] + target_bounds['width'] / 2, target_bounds['y'] + target_bounds['height'] / 2, steps=8)
    page.mouse.up()

# ################################################################################################################################

def tree_item(page:'Page', side:'str', path:'str') -> 'Locator':
    """ The tree item of one field on one side.
    """
    out = page.locator('#mapper-schema-body-' + side + ' .mapper-tree-item[data-path="' + path + '"]')
    return out

# ################################################################################################################################

def tree_row(page:'Page', side:'str', path:'str') -> 'Locator':
    """ The tree row of one field on one side.
    """
    out = tree_item(page, side, path).locator('> .mapper-tree-row')
    return out

# ################################################################################################################################

def add_scope(page:'Page') -> 'None':
    """ Adds an iteration scope over the example's lines, with two child rows.
    """
    _ = page.evaluate("""() => {
        const firstRow = zato.mapper.store.newMapping();
        firstRow.target = 'code';
        firstRow.expression = 'sku';

        const secondRow = zato.mapper.store.newMapping();
        secondRow.target = 'amount';
        secondRow.expression = 'quantity * 2';

        zato.mapper.pageStore.addScope({
            target: 'invoice.items',
            source: 'lines',
            mappings: [firstRow, secondRow]
        });
    }""")

# ################################################################################################################################
# ################################################################################################################################
