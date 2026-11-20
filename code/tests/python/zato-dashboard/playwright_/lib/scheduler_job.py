# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

if 0:
    from playwright.sync_api import Page

# ################################################################################################################################
# ################################################################################################################################

# The list of scheduler jobs, relative to the address of the Dashboard
Page_Url = '/zato/scheduler/'

# The prefixes of the identifiers of the fields of the create and of the edit form of an interval-based job
_Create_Prefix = '#id_create-interval_based-'
_Edit_Prefix   = '#id_edit-interval_based-'

# The fields of the interval of a job that is created with a number of seconds only
_Other_Interval_Fields = 'weeks', 'days', 'hours', 'minutes'

# How long to wait for a dialog to open or for a row to appear, in milliseconds
_Dialog_Timeout = 5000

# How long to wait for a form to be submitted, in milliseconds
_Submit_Timeout = 10000

# ################################################################################################################################
# ################################################################################################################################

def job_row_selector(name:'str') -> 'str':
    out = f'#data-table tbody tr:has(td a:text-is("{name}"))'
    return out

# ################################################################################################################################

def navigate_to_jobs(page:'Page', base_url:'str') -> 'None':
    _ = page.goto(f'{base_url}{Page_Url}')
    _ = page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def get_job_id(page:'Page', name:'str') -> 'str':
    """ Returns the server-side ID of a job on the open list of jobs.
    """
    selector = job_row_selector(name)
    id_cell = page.locator(f'{selector} td[class*="job_id_"]')

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################

def create_interval_job(
    page:'Page',
    name:'str',
    service:'str',
    seconds:'int',
    start_date:'str',
    extra:'str',
    is_active:'bool',
    ) -> 'None':
    """ Creates an interval-based job on the open list of jobs. The start date is in the format of the date fields
    of the Dashboard.
    """

    # Open the create dialog ..
    page.click('#markup .page_prompt a:has-text("Create a new job")')
    _ = page.wait_for_selector('#create-interval_based', state='visible', timeout=_Dialog_Timeout)

    # .. name the job and say whether it runs ..
    page.fill(f'{_Create_Prefix}name', name)
    page.set_checked(f'{_Create_Prefix}is_active', is_active)

    # .. its interval is a number of seconds only ..
    for field_name in _Other_Interval_Fields:
        page.fill(f'{_Create_Prefix}{field_name}', '')

    page.fill(f'{_Create_Prefix}seconds', str(seconds))

    # .. the start date and the service come from widgets that hide their inputs ..
    _ = page.evaluate(f'$("{_Create_Prefix}start_date").val("{start_date}")')
    _ = page.evaluate(f'$("{_Create_Prefix}service").val("{service}").trigger("chosen:updated").trigger("change")')

    # .. the extra data is among the options that the form keeps folded ..
    page.click('#create-interval_based a:has-text("Toggle options")')
    page.fill(f'{_Create_Prefix}extra', extra)

    # .. and the job is listed once the dialog closes.
    page.click('#create-interval_based input[type="submit"]')
    _ = page.wait_for_selector('#create-interval_based', state='hidden', timeout=_Submit_Timeout)

    selector = job_row_selector(name)
    _ = page.wait_for_selector(selector, state='visible', timeout=_Dialog_Timeout)

# ################################################################################################################################

def set_job_active(page:'Page', job_id:'str', is_active:'bool') -> 'None':
    """ Activates or deactivates an interval-based job on the open list of jobs, through its edit dialog.
    """
    _ = page.evaluate(f'$.fn.zato.scheduler.edit("interval_based", "{job_id}")')
    _ = page.wait_for_selector('#edit-interval_based', state='visible', timeout=_Dialog_Timeout)

    page.set_checked(f'{_Edit_Prefix}is_active', is_active)

    page.click('#edit-interval_based input[type="submit"]')
    _ = page.wait_for_selector('#edit-interval_based', state='hidden', timeout=_Submit_Timeout)

# ################################################################################################################################
# ################################################################################################################################
