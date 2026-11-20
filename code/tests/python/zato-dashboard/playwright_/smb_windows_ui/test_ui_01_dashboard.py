# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# pytest
import pytest

# Zato
from live_windows.enmasse import exchange_connection_name, partner_connection_name
from live_windows.layout import app_folder, Hub, Shares

# Playwright helpers
from audit_log_ui import wait_for_table
from file_transfer_schedule import open_schedules
from smb_connection import navigate_to_list, row_selector

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page, Response
    from live_windows.progress import Monitor
    from zato.common.typing_ import anydict
    from _smb_windows_ui_suite import UISuite

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The path that a ping of a connection is sent to
    Ping_Path = '/zato/outgoing/smb/ping/'

    # How long a ping and the audit log may take, in milliseconds
    Ping_Timeout  = 30000
    Audit_Timeout = 30000

    # Schedules that each exchange connection has, among others
    Expected_Schedules = (
        'hub.plant',
        'hub.catalog',
        'hub.branch08',
        'documents',
        'shipping',
        'labels.site-a.failed',
        'people.hr-outbound',
    )

    # The pattern of the files the hub writes into each inbox
    Hub_Pattern = f'*{Hub.Out_Suffix}'

    # A password that the guests do not accept
    Wrong_Password = 'Zato.Wrong.Password.1'

    # What a logon with a wrong password makes Windows report - the failed logon in the Security log
    # and the failed authentication that the SMB server logs
    Logon_Failure_Events = 'Security', 'SMBServer'

    # What a ping with a wrong password makes the server and the Dashboard log
    Logon_Failure_Log = 'partner.win', 'Could not ping', 'STATUS_LOGON_FAILURE'

# ################################################################################################################################
# ################################################################################################################################

def _ping(page:'Page', name:'str') -> 'anydict':
    """ Clicks the Ping link of a connection and returns what the Dashboard answered with.
    """
    selector = row_selector(name)

    def _is_ping(response:'Response') -> 'bool':
        out = ModuleCtx.Ping_Path in response.url
        return out

    with page.expect_response(_is_ping, timeout=ModuleCtx.Ping_Timeout) as response_info:
        page.click(f'{selector} a:has-text("Ping")')

    response = response_info.value
    body = response.text()

    assert response.status == 200, f'Ping of {name} returned {response.status} -> {body}'

    out = json.loads(body)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_ping(
    logged_in_page:'Page',
    zato_dashboard:'anydict',
    smb_suite:'UISuite',
    version:'str',
    monitor:'Monitor',
    ) -> 'None':
    """ Both connections to the guest are listed and a ping of each succeeds.
    """
    page = logged_in_page
    info = smb_suite.guest(version).info

    exchange_name = exchange_connection_name(info)
    partner_name = partner_connection_name(info)

    navigate_to_list(page, zato_dashboard['dashboard_url'])

    for name in exchange_name, partner_name:
        response = _ping(page, name)
        assert response['is_success'], f'Ping of {name} failed -> {response}'
        monitor.raise_if_failed()

# ################################################################################################################################

def test_schedules_listed(
    logged_in_page:'Page',
    zato_dashboard:'anydict',
    smb_suite:'UISuite',
    version:'str',
    monitor:'Monitor',
    ) -> 'None':
    """ The schedules page of the exchange connection lists the schedules that the Dashboard created.
    """
    page = logged_in_page
    info = smb_suite.guest(version).info
    exchange_name = exchange_connection_name(info)

    navigate_to_list(page, zato_dashboard['dashboard_url'])
    open_schedules(page, exchange_name)

    for schedule_name in ModuleCtx.Expected_Schedules:
        selector = row_selector(schedule_name)
        row = page.query_selector(selector)
        assert row is not None, f'Schedule {schedule_name} of {exchange_name} is not listed'

    monitor.raise_if_failed()

# ################################################################################################################################

def test_audit_log_records_pickup(
    logged_in_page:'Page',
    zato_dashboard:'anydict',
    smb_suite:'UISuite',
    version:'str',
    run:'str',
    monitor:'Monitor',
    ) -> 'None':
    """ A file that the hub routes is recorded in the audit log of the exchange connection.
    """
    page = logged_in_page
    handle = smb_suite.guest(version)
    exchange_name = exchange_connection_name(handle.info)

    # The logistics application reads its inbox, and the plant writes one file ..
    inbox = app_folder(Hub.Logistics, Hub.Inbox)
    outbox = app_folder(Hub.Plant, Hub.Outbox)

    _ = handle.consume(run, Shares.Exchange, inbox, ModuleCtx.Hub_Pattern)

    names = smb_suite.sequences.next_names(Hub.Plant, 1)
    _ = handle.produce(run, Shares.Exchange, outbox, names)

    sequence, app = names[0].split('.')
    routed_name = f'{app}.{sequence}{Hub.Out_Suffix}'

    def _is_routed() -> 'bool':
        consumed = monitor.names(version, 'consumed', run)

        out = routed_name in consumed
        return out

    monitor.wait_until(_is_routed, f'win{version} received {routed_name}')

    # .. and the audit log of the connection shows what the hub did.
    selector = row_selector(exchange_name)

    navigate_to_list(page, zato_dashboard['dashboard_url'])
    page.click(f'{selector} a:has-text("Audit log")')
    wait_for_table(page)

    _ = page.wait_for_function(
        '''() => document.querySelectorAll('#audit-log-table-body tr.audit-log-row').length > 0''',
        timeout=ModuleCtx.Audit_Timeout)

    monitor.raise_if_failed()

# ################################################################################################################################

@pytest.mark.expect_log_errors(*ModuleCtx.Logon_Failure_Log)
def test_ping_fails_with_wrong_password(
    logged_in_page:'Page',
    zato_dashboard:'anydict',
    smb_suite:'UISuite',
    version:'str',
    monitor:'Monitor',
    ) -> 'None':
    """ A connection with a password that the guest does not accept fails its ping, and the guest reports the failed logon.
    """
    page = logged_in_page
    info = smb_suite.guest(version).info
    partner_name = partner_connection_name(info)

    monitor.expect_windows_events(*ModuleCtx.Logon_Failure_Events)
    monitor.expect_server_errors(*ModuleCtx.Logon_Failure_Log)

    # The password of the partner connection is changed through the Dashboard ..
    definitions = smb_suite.definitions(version)

    for connection in definitions['smb']:
        if connection['name'] == partner_name:
            connection['password'] = ModuleCtx.Wrong_Password

    smb_suite.apply_definitions(version, definitions)

    # .. which makes its ping fail ..
    try:
        navigate_to_list(page, zato_dashboard['dashboard_url'])

        response = _ping(page, partner_name)
        assert not response['is_success'], f'Ping of {partner_name} with a wrong password succeeded -> {response}'

        monitor.raise_if_failed()

    # .. until the password is changed back.
    finally:
        smb_suite.import_guest(version)

# ################################################################################################################################
# ################################################################################################################################
