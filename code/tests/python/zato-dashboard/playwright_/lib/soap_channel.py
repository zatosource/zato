# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
from urllib.parse import urlparse

# Zato
from zato.common.api import ZATO_NONE
from zato.common.test.playwright_pubsub import navigate_to_page, open_create_dialog, select_option_by_label, \
    set_select_value, submit_create_form, submit_edit_form
from rest_channel import get_channel_id, open_edit_dialog, wait_for_channel_row
from soap_outconn import invoke_service_in_ide

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

SOAP_Channel_Page_Url = '/zato/http-soap/?cluster=1&connection=channel&transport=soap'

# Plain text fields in the create and edit forms, keyed by option name
_Text_Fields = ('name', 'url_path', 'soap_action')

# Select fields set by raw value via JS since Chosen.js hides the underlying elements
_Select_Fields = ('soap_version',)

# Checkbox fields toggled by boolean options, set via JS so the state is set directly regardless of the slider styling
_Toggle_Fields = ('use_mtom',)

# The readiness probe of the channel-side fixture services, deployed from fixtures/services during server boot
Channel_Fixtures_Probe_Service_Name = 'test.soap.channel.ping'

# How long to wait for the fixture services to respond to their first invocation
_Service_Deploy_Timeout = 60

# How long to wait between the polling attempts above
_Service_Poll_Interval = 1.0

# ################################################################################################################################
# ################################################################################################################################
#
# Page navigation
#
# ################################################################################################################################
# ################################################################################################################################

def open_soap_channel_page(page:'Page', base_url:'str', query:'str'='') -> 'None':
    """ Navigates to the SOAP channels page, optionally filtering by a query.
    """

    url_path = SOAP_Channel_Page_Url
    if query:
        url_path += f'&query={query}'

    navigate_to_page(page, base_url, url_path)

# ################################################################################################################################
# ################################################################################################################################
#
# Form filling
#
# ################################################################################################################################
# ################################################################################################################################

def fill_soap_channel_form(page:'Page', options:'anydict', prefix:'str'='') -> 'None':
    """ Fills the SOAP channel create or edit form. An empty prefix means the create form,
    the 'edit-' prefix means the edit form. Only the fields present in options are touched.
    """

    # Plain text inputs ..
    for field_name in _Text_Fields:
        if field_name in options:
            page.fill(f'#id_{prefix}{field_name}', options[field_name])

    # .. the service select ..
    if 'service' in options:
        set_select_value(page, f'#id_{prefix}service', options['service'])

    # .. the security select, selected by its visible label, e.g. "WS-Security/My def" ..
    if 'security' in options:
        select_option_by_label(page, f'#id_{prefix}security', options['security'])

    # .. the security select, selected by its raw value, e.g. ZATO_NONE ..
    if 'security_value' in options:
        set_select_value(page, f'#id_{prefix}security', options['security_value'])

    # .. selects set by raw value ..
    for field_name in _Select_Fields:
        if field_name in options:
            set_select_value(page, f'#id_{prefix}{field_name}', options[field_name])

    # .. the active checkbox, a plain visible one ..
    if 'is_active' in options:
        page.set_checked(f'#id_{prefix}is_active', options['is_active'])

    # .. the audit log checkbox, a plain visible one too ..
    if 'is_audit_log_active' in options:
        page.set_checked(f'#id_{prefix}is_audit_log_active', options['is_audit_log_active'])

    # .. and toggles hidden behind the switch styling.
    for field_name in _Toggle_Fields:
        if field_name in options:
            checked = 'true' if options[field_name] else 'false'
            page.evaluate(f'$("#id_{prefix}{field_name}").prop("checked", {checked})')

# ################################################################################################################################
# ################################################################################################################################
#
# Channel CRUD
#
# ################################################################################################################################
# ################################################################################################################################

def create_soap_channel(
    page:'Page',
    base_url:'str',
    name:'str',
    service:'str',
    url_path:'str',
    options:'anydict | None'=None,
    ) -> 'str':
    """ Creates a SOAP channel via the UI and returns its server-side ID.
    """

    # Navigate to the SOAP channels page ..
    open_soap_channel_page(page, base_url)

    # .. open the create dialog ..
    open_create_dialog(page)

    # .. combine the base fields with any extra options ..
    form_data = {
        'name': name,
        'url_path': url_path,
        'service': service,
    } # type: anydict

    if options:
        form_data.update(options)

    # .. default to no security definition unless the caller chose one ..
    if 'security' not in form_data:
        if 'security_value' not in form_data:
            form_data['security_value'] = ZATO_NONE

    # .. fill the form ..
    fill_soap_channel_form(page, form_data)

    # .. submit and wait for the dialog to close ..
    submit_create_form(page)

    # .. wait for the row and return the channel's ID.
    _ = wait_for_channel_row(page, name)

    out = get_channel_id(page, name)
    return out

# ################################################################################################################################

def edit_soap_channel(page:'Page', channel_id:'str', options:'anydict') -> 'None':
    """ Opens the edit dialog for a SOAP channel, applies the given changes and submits the form.
    """

    # Open the dialog ..
    open_edit_dialog(page, channel_id)

    # .. apply the changes ..
    fill_soap_channel_form(page, options, 'edit-')

    # .. and submit.
    submit_edit_form(page)

# ################################################################################################################################

def delete_soap_channel(page:'Page', channel_id:'str') -> 'None':
    """ Deletes a SOAP channel via the UI confirmation dialog.
    """

    # The page may be somewhere else, e.g. in the IDE after an invocation,
    # so go back to the channels page first.
    if '/zato/http-soap/' not in page.url:
        parsed_url = urlparse(page.url)
        open_soap_channel_page(page, f'{parsed_url.scheme}://{parsed_url.netloc}')

    # Trigger the delete confirmation ..
    page.evaluate(f'$.fn.zato.http_soap.delete_("{channel_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)

    # .. confirm ..
    page.click('#popup_ok')

    # .. and wait for the row removal animation.
    _ = page.wait_for_selector(f'#tr_{channel_id}', state='detached', timeout=5000)

# ################################################################################################################################
# ################################################################################################################################
#
# The pre-deployed fixture services
#
# ################################################################################################################################
# ################################################################################################################################

def wait_for_channel_fixture_services(page:'Page', base_url:'str') -> 'None':
    """ Opens the channel fixtures' readiness probe in the IDE and keeps clicking Invoke
    until it responds, confirming the fixture services deployed during server boot -
    which also means they are selectable in the channel form's service list.
    """

    _ = page.goto(f'{base_url}/zato/service/ide/service/{Channel_Fixtures_Probe_Service_Name}/?cluster=1')
    _ = page.wait_for_selector('#invoke-service:not([disabled])', state='visible', timeout=15000)

    deadline = time.monotonic() + _Service_Deploy_Timeout

    while time.monotonic() < deadline:

        # The invocation errors out until the service is deployed, at which point
        # the probe comes back with its readiness flag.
        try:
            response = invoke_service_in_ide(page, {'mode': 'ping'})
        except Exception as probe_error:
            logger.info('[wait_for_channel_fixture_services] not ready yet: %s', probe_error)
        else:
            if response.get('is_ready'):
                logger.info('[wait_for_channel_fixture_services] ready: %s', response)
                return
            logger.info('[wait_for_channel_fixture_services] unexpected probe response: %s', response)

        time.sleep(_Service_Poll_Interval)

    raise Exception(f'Service `{Channel_Fixtures_Probe_Service_Name}` did not deploy within {_Service_Deploy_Timeout}s')

# ################################################################################################################################
# ################################################################################################################################
