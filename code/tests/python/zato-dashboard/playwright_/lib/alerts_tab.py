# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Alerts tab of a create or edit dialog, as a Playwright test drives it - the tab strip,
# the sliders, the popovers behind the summary links and the hidden Django fields the
# popovers write to. Every page that includes the tab names its panels after one prefix,
# e.g. `out-sftp`, which is what the helpers below take.

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page

# ################################################################################################################################
# ################################################################################################################################

# How long to wait for a popover or a panel to show up, in milliseconds
_Popover_Timeout = 5000

# The prefix every field of the tab carries on the form
_Field_Prefix = 'alert_'

# The prefix the popover inputs carry, from alerts-tab.js and micro-forms.js
_Popover_Input_Prefix = 'alerts-tab-tippy-'

# Where the one open popover lives
_Popover_Selector = '#alerts-tab-popup'

# The button that writes a popover's answers back into the form
_Popover_Ok_Selector = _Popover_Selector + ' button.action-button'

# The tab strip button that leads to a tab
_Tab_Button_Selector = '{div_id} .dashboard-tab[data-tab="{tab_name}"]'

# The names the tabs go by in the strip
Tab_Main = 'main'
Tab_Alerts = 'alerts'

# The lines of the tab and the fields behind them
Line_Failures_In_A_Row = 'failures_in_a_row'
Field_Consecutive_Failures = 'consecutive_failures'
Field_Is_Active = 'is_active'

# ################################################################################################################################
# ################################################################################################################################

def _div_id(form_type:'str') -> 'str':
    """ The dialog wrapper of a create or edit form.
    """
    out = f'#{form_type}-div'
    return out

# ################################################################################################################################

def _field_prefix(form_type:'str') -> 'str':
    """ The prefix Django gives the fields of a form - the edit form carries one, the create form none.
    """
    if form_type == 'edit':
        out = 'edit-'
    else:
        out = ''

    return out

# ################################################################################################################################

def panel_id(page_prefix:'str', form_type:'str') -> 'str':
    """ The id of the Alerts tab panel of a dialog.
    """
    out = f'{page_prefix}-{form_type}-tab-panel-{Tab_Alerts}'
    return out

# ################################################################################################################################

def field_id(form_type:'str', field_name:'str') -> 'str':
    """ The id of one hidden field of the tab on the Django form.
    """
    out = f'id_{_field_prefix(form_type)}{_Field_Prefix}{field_name}'
    return out

# ################################################################################################################################

def switch_to_tab(page:'Page', page_prefix:'str', form_type:'str', tab_name:'str') -> 'None':
    """ Clicks a tab of a dialog and waits for its panel to show.
    """
    selector = _Tab_Button_Selector.format(div_id=_div_id(form_type), tab_name=tab_name)
    page.click(selector)

    panel_selector = f'#{page_prefix}-{form_type}-tab-panel-{tab_name}'
    _ = page.wait_for_selector(panel_selector, state='visible', timeout=_Popover_Timeout)

# ################################################################################################################################

def get_field_value(page:'Page', form_type:'str', field_name:'str') -> 'str':
    """ The value one hidden field of the tab currently holds - the fields are hidden,
    so the value is read off the element rather than off the screen.
    """
    out = page.input_value(f'#{field_id(form_type, field_name)}')
    return out

# ################################################################################################################################

def is_checked(page:'Page', form_type:'str', field_name:'str') -> 'bool':
    """ Whether one slider of the tab is on.
    """
    out = page.is_checked(f'#{field_id(form_type, field_name)}')
    return out

# ################################################################################################################################

def click_active_slider(page:'Page', form_type:'str') -> 'None':
    """ Flips the Active slider - the tab has to be the visible one for the slider to take the click.
    """
    page.click(f'#{field_id(form_type, Field_Is_Active)}')

# ################################################################################################################################

def set_popover_value(page:'Page', page_prefix:'str', form_type:'str', line_name:'str', field_name:'str', value:'str') -> 'None':
    """ Opens the popover of a line, types a new value into one of its inputs and accepts it,
    which writes the value back into the hidden field of the same name.
    """

    # Open the popover through the line's summary link ..
    page.click(f'#{panel_id(page_prefix, form_type)}-edit-{line_name}')
    _ = page.wait_for_selector(_Popover_Selector, state='visible', timeout=_Popover_Timeout)

    # .. type the value ..
    page.fill(f'#{_Popover_Input_Prefix}{field_name}', value)

    # .. and accept, which closes the popover.
    page.click(_Popover_Ok_Selector)
    _ = page.wait_for_selector(_Popover_Selector, state='hidden', timeout=_Popover_Timeout)

# ################################################################################################################################

def summary_text(page:'Page', page_prefix:'str', form_type:'str', line_name:'str') -> 'str':
    """ What a popover line's summary link currently reads.
    """
    out = page.inner_text(f'#{panel_id(page_prefix, form_type)}-summary-{line_name}')
    return out

# ################################################################################################################################
# ################################################################################################################################
