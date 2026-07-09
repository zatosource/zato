# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Playwright
from playwright.sync_api import expect, Page

# Mapper tests
from common import open_empty_page, paste_example, paste_json_schema, source_example

# ################################################################################################################################
# ################################################################################################################################

_json_schema_document = """
{
    "type": "object",
    "required": ["invoice_number"],
    "properties": {
        "invoice_number": {"type": "string", "pattern": "^INV-"},
        "amount": {"type": "number"},
        "status": {"type": "string", "enum": ["new", "paid"]}
    }
}
"""

# ################################################################################################################################
# ################################################################################################################################

def test_example_inference_renders_tree(page:'Page', base_url:'str') -> 'None':
    """ Pasting a JSON example infers a schema and renders its tree with type and cardinality badges.
    """
    open_empty_page(page, base_url)
    paste_example(page, 'source', source_example)

    body = page.locator('#mapper-schema-body-source')

    # Field names render in the pasted order ..
    names = body.locator('.mapper-tree-name')
    expect(names.first).to_have_text('customer')

    # .. types are detected ..
    customer_row = body.locator('.mapper-tree-item[data-path="customer"] > .mapper-tree-row')
    expect(customer_row.locator('.mapper-tree-type-badge')).to_have_text('string')

    total_row = body.locator('.mapper-tree-item[data-path="total"] > .mapper-tree-row')
    expect(total_row.locator('.mapper-tree-type-badge')).to_have_text('number')

    # .. a date-looking string carries its format hint ..
    created_row = body.locator('.mapper-tree-item[data-path="created"] > .mapper-tree-row')
    expect(created_row.locator('.mapper-tree-format-badge')).to_have_text('date')

    # .. the repeating node carries a cardinality badge ..
    lines_row = body.locator('.mapper-tree-item[data-path="lines"] > .mapper-tree-row')
    expect(lines_row.locator('.mapper-tree-cardinality-badge')).to_have_text('list')

    # .. its children render relative to it ..
    sku_row = body.locator('.mapper-tree-item[data-path="lines.sku"] > .mapper-tree-row')
    expect(sku_row.locator('.mapper-tree-type-badge')).to_have_text('string')

    # .. and a field absent from some elements is marked optional.
    discount_row = body.locator('.mapper-tree-item[data-path="lines.discount"] > .mapper-tree-row')
    expect(discount_row.locator('.mapper-tree-optional-badge')).to_have_text('optional')

# ################################################################################################################################

def test_example_becomes_a_sample(page:'Page', base_url:'str') -> 'None':
    """ The pasted example is stored as a sample, so the tree and the preview share one data source.
    """
    open_empty_page(page, base_url)
    expect(page.locator('#mapper-sample-count-source')).to_have_text('0')

    paste_example(page, 'source', source_example)
    expect(page.locator('#mapper-sample-count-source')).to_have_text('1')

# ################################################################################################################################

def test_invalid_json_keeps_the_dialog_open(page:'Page', base_url:'str') -> 'None':
    """ Pasting text that is not JSON shows an error in the dialog instead of closing it.
    """
    open_empty_page(page, base_url)

    page.locator('#mapper-schema-actions-source .mapper-action-paste-example').click()
    page.locator('.mapper-dialog-textarea').fill('this is not JSON')
    page.locator('.mapper-button-confirm').click()

    expect(page.locator('.mapper-dialog-error')).to_contain_text('Not valid JSON')
    expect(page.locator('.mapper-dialog')).to_be_visible()

# ################################################################################################################################

def test_json_schema_paste_and_unsupported_notice(page:'Page', base_url:'str') -> 'None':
    """ A pasted JSON Schema renders as a tree and keywords outside the subset are listed in a notice.
    """
    open_empty_page(page, base_url)
    paste_json_schema(page, 'target', _json_schema_document)

    body = page.locator('#mapper-schema-body-target')

    # The tree renders with the required flag respected ..
    invoice_row = body.locator('.mapper-tree-item[data-path="invoice_number"] > .mapper-tree-row')
    expect(invoice_row.locator('.mapper-tree-type-badge')).to_have_text('string')
    expect(invoice_row.locator('.mapper-tree-optional-badge')).to_have_count(0)

    amount_row = body.locator('.mapper-tree-item[data-path="amount"] > .mapper-tree-row')
    expect(amount_row.locator('.mapper-tree-optional-badge')).to_have_text('optional')

    # .. and the unsupported keyword is reported, never silently dropped.
    notice = page.locator('#mapper-schema-notice-target')
    expect(notice).to_be_visible()
    expect(notice).to_contain_text('pattern')

# ################################################################################################################################

def test_named_schemas_save_and_load(page:'Page', base_url:'str') -> 'None':
    """ A schema saved under a name on one side loads back on the other side.
    """
    open_empty_page(page, base_url)
    paste_example(page, 'source', source_example)

    # Save the source schema under a name ..
    page.locator('#mapper-schema-actions-source .mapper-action-save-named').click()
    page.locator('.mapper-dialog-input').fill('order')
    page.locator('.mapper-button-confirm').click()

    # .. and load it into the target side.
    page.locator('#mapper-schema-actions-target .mapper-action-load-named').click()
    page.locator('.mapper-dialog-input').fill('order')
    page.locator('.mapper-button-confirm').click()

    target_row = page.locator('#mapper-schema-body-target .mapper-tree-item[data-path="customer"] > .mapper-tree-row')
    expect(target_row.locator('.mapper-tree-type-badge')).to_have_text('string')

# ################################################################################################################################

def test_scaffold_adds_a_new_sample(page:'Page', base_url:'str') -> 'None':
    """ Scaffolding generates a new sample from the schema without touching existing ones.
    """
    open_empty_page(page, base_url)

    # Without a schema the scaffold action is disabled ..
    scaffold_button = page.locator('#mapper-schema-actions-source .mapper-action-scaffold')
    expect(scaffold_button).to_be_disabled()

    paste_example(page, 'source', source_example)
    expect(page.locator('#mapper-sample-count-source')).to_have_text('1')

    # .. with one it adds a new sample each time.
    scaffold_button.click()
    expect(page.locator('#mapper-sample-count-source')).to_have_text('2')

    scaffold_button.click()
    expect(page.locator('#mapper-sample-count-source')).to_have_text('3')

# ################################################################################################################################

def test_second_example_refines_the_schema(page:'Page', base_url:'str') -> 'None':
    """ Pasting another example merges into the schema - new fields arrive as optional.
    """
    open_empty_page(page, base_url)
    paste_example(page, 'source', '{"customer": "ACME"}')
    paste_example(page, 'source', '{"customer": "Initech", "po_number": "PO-1"}')

    body = page.locator('#mapper-schema-body-source')

    # The shared field stays required ..
    customer_row = body.locator('.mapper-tree-item[data-path="customer"] > .mapper-tree-row')
    expect(customer_row.locator('.mapper-tree-optional-badge')).to_have_count(0)

    # .. the field present in only one sample is optional.
    po_number_row = body.locator('.mapper-tree-item[data-path="po_number"] > .mapper-tree-row')
    expect(po_number_row.locator('.mapper-tree-optional-badge')).to_have_text('optional')

# ################################################################################################################################
# ################################################################################################################################
