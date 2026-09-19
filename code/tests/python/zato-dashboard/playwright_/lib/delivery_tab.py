# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Delivery tab of a create or edit dialog, as a Playwright test drives it.

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# In milliseconds
_Popover_Timeout = 5000

# From delivery-tab.js and micro-forms/core.js
_Popover_Input_Prefix = 'delivery-tab-tippy-'
_Popover_Selector = '#delivery-tab-popup'

# The OK is told apart from the Cancel by its text
_Popover_Ok_Selector = _Popover_Selector + ' .micro-form-buttons button:has-text("OK")'

_Tab_Button_Selector = '{div_id} .dashboard-tab[data-tab="{tab_name}"]'

Tab_Delivery = 'delivery'

Line_Retries = 'retries'
Line_Action = 'dlq_action'

Field_Max_Retries = 'max_retries'
Field_Sleep_Time = 'retry_sleep_time'
Field_Backoff_Threshold = 'retry_backoff_threshold'
Field_Backoff_Multiplier = 'retry_backoff_multiplier'
Field_Use_Queue = 'use_queue'
Field_Use_DLQ = 'use_dlq'
Field_Action = 'dlq_action'
Field_Retries = 'dlq_retries'
Field_Retry_Interval = 'dlq_retry_interval'
Field_Forward_To = 'dlq_forward_to'
Field_Keep_Header = 'dlq_keep_header'

Unit_Suffix = '_unit'

# The panel while the queue is off, a line while its switch is off
Panel_Off_Class = 'alerts-tab-off'
Line_Off_Class = 'alerts-tab-line-off'

# ################################################################################################################################
# ################################################################################################################################

def _div_id(form_type:'str') -> 'str':
    """ The dialog wrapper of a create or edit form.
    """
    out = f'#{form_type}-div'
    return out

# ################################################################################################################################

def _field_prefix(form_type:'str') -> 'str':
    """ The prefix Django gives the fields of a form.
    """
    if form_type == 'edit':
        out = 'edit-'
    else:
        out = ''

    return out

# ################################################################################################################################

def panel_id(page_prefix:'str', form_type:'str') -> 'str':
    """ The id of the Delivery tab panel of a dialog.
    """
    out = f'{page_prefix}-{form_type}-tab-panel-{Tab_Delivery}'
    return out

# ################################################################################################################################

def field_id(form_type:'str', field_name:'str') -> 'str':
    """ The id of one field of the tab on the Django form.
    """
    out = f'id_{_field_prefix(form_type)}{field_name}'
    return out

# ################################################################################################################################

def switch_to_tab(page:'Page', page_prefix:'str', form_type:'str') -> 'None':
    """ Clicks the Delivery tab of a dialog and waits for its panel to show.
    """
    selector = _Tab_Button_Selector.format(div_id=_div_id(form_type), tab_name=Tab_Delivery)
    page.click(selector)

    _ = page.wait_for_selector(f'#{panel_id(page_prefix, form_type)}', state='visible', timeout=_Popover_Timeout)

# ################################################################################################################################

def get_field_value(page:'Page', form_type:'str', field_name:'str') -> 'str':
    """ The value one hidden field of the tab currently holds.
    """
    out = page.input_value(f'#{field_id(form_type, field_name)}')
    return out

# ################################################################################################################################

def is_checked(page:'Page', form_type:'str', field_name:'str') -> 'bool':
    """ Whether one switch of the tab is on.
    """
    out = page.is_checked(f'#{field_id(form_type, field_name)}')
    return out

# ################################################################################################################################

def click_switch(page:'Page', form_type:'str', field_name:'str') -> 'None':
    """ Flips one of the two switches of the tab.
    """
    page.click(f'#{field_id(form_type, field_name)}')

# ################################################################################################################################

def panel_is_off(page:'Page', page_prefix:'str', form_type:'str') -> 'bool':
    """ Whether the whole tab but its retries is dimmed.
    """
    class_names = page.get_attribute(f'#{panel_id(page_prefix, form_type)}', 'class')
    out = Panel_Off_Class in class_names.split()
    return out

# ################################################################################################################################

def line_is_off(page:'Page', page_prefix:'str', form_type:'str', line_name:'str') -> 'bool':
    """ Whether one line of the tab is dimmed.
    """
    class_names = page.get_attribute(f'#{panel_id(page_prefix, form_type)}-line-{line_name}', 'class')
    out = Line_Off_Class in class_names.split()
    return out

# ################################################################################################################################

def open_popover(page:'Page', page_prefix:'str', form_type:'str', line_name:'str') -> 'None':
    """ Opens the popover of a line through the line's summary link.
    """
    page.click(f'#{panel_id(page_prefix, form_type)}-edit-{line_name}')
    _ = page.wait_for_selector(_Popover_Selector, state='visible', timeout=_Popover_Timeout)

# ################################################################################################################################

def accept_popover(page:'Page') -> 'None':
    """ Accepts the open popover.
    """
    page.click(_Popover_Ok_Selector)
    _ = page.wait_for_selector(_Popover_Selector, state='hidden', timeout=_Popover_Timeout)

# ################################################################################################################################

def fill_popover(page:'Page', values:'anydict') -> 'None':
    """ Sets the inputs of the open popover, by field name and in the order given.
    """
    for field_name, value in values.items():
        selector = f'#{_Popover_Input_Prefix}{field_name}'

        if isinstance(value, bool):
            page.set_checked(selector, value)
            continue

        tag_name = page.eval_on_selector(selector, 'item => item.tagName')
        if tag_name == 'SELECT':
            _ = page.select_option(selector, value)
        else:
            page.fill(selector, value)

# ################################################################################################################################

def popover_row_is_visible(page:'Page', field_name:'str') -> 'bool':
    """ Whether the input of one field is on show in the open popover.
    """
    out = page.is_visible(f'#{_Popover_Input_Prefix}{field_name}')
    return out

# ################################################################################################################################

def set_popover_values(page:'Page', page_prefix:'str', form_type:'str', line_name:'str', values:'anydict') -> 'None':
    """ Opens the popover of a line, fills its inputs and accepts it.
    """
    open_popover(page, page_prefix, form_type, line_name)
    fill_popover(page, values)
    accept_popover(page)

# ################################################################################################################################

def summary_text(page:'Page', page_prefix:'str', form_type:'str', line_name:'str') -> 'str':
    """ What a popover line's summary link currently reads.
    """
    out = page.inner_text(f'#{panel_id(page_prefix, form_type)}-summary-{line_name}')
    return out

# ################################################################################################################################
# ################################################################################################################################
