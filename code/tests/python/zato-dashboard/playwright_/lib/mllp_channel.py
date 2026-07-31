# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import socket
import time

# Zato
from hl7_client import python_client
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anylist, strstrdict
    any_ = any_
    anylist = anylist
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The pages these helpers drive
Channel_Page_Url = '/zato/channel/hl7/mllp/?cluster=1&type_=channel-hl7-mllp'
Outgoing_Page_Url = '/zato/outgoing/hl7/mllp/?cluster=1&type_=outconn-hl7-mllp'

# Where the channels listen
Host = '127.0.0.1'

# How long a channel is given to start answering from its own route after the wizard created it
_Routed_Timeout = 30

# How long the listener port is given to start accepting connections
_Port_Timeout = 30

# How often the wire polls retry
_Poll_Interval = 0.5

# ################################################################################################################################
# ################################################################################################################################
#
# Page navigation and row lookup
#
# ################################################################################################################################
# ################################################################################################################################

def navigate_to_channels(page:'Page', base_url:'str') -> 'None':
    """ Opens the HL7 MLLP channels page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{Channel_Page_Url}')
    _ = page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def navigate_to_outgoing(page:'Page', base_url:'str') -> 'None':
    """ Opens the outgoing HL7 MLLP connections page and waits for the data table.
    """
    _ = page.goto(f'{base_url}{Outgoing_Page_Url}')
    _ = page.wait_for_selector('#data-table', state='visible')

# ################################################################################################################################

def get_item_id(page:'Page', name:'str') -> 'str':
    """ Extracts the server-side ID of a row by its name.
    """
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    row = page.query_selector(row_selector)
    assert row is not None, f'No row for "{name}" on the list page'

    id_cell = row.query_selector('td[class*="item_id_"]')
    assert id_cell is not None, f'No id cell in the row of "{name}"'

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################
# ################################################################################################################################
#
# Outgoing MLLP connections
#
# ################################################################################################################################
# ################################################################################################################################

def create_outgoing_connection(page:'Page', base_url:'str', name:'str', address:'str', recv_timeout_ms:'int'=0) -> 'None':
    """ Creates an outgoing MLLP connection through its own page, the way a person does.
    A receive timeout in milliseconds replaces the form's default when the receiver
    the connection points at is a slow one.
    """
    navigate_to_outgoing(page, base_url)

    page.click('#markup .page_prompt a:has-text("Create a new connection")')
    _ = page.wait_for_selector('#create-div', state='visible')

    page.fill('#id_name', name)
    page.fill('#id_address', address)

    if recv_timeout_ms:
        page.fill('#id_recv_timeout', str(recv_timeout_ms))

    page.click('#create-div input[type="submit"]')
    _ = page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    _ = page.wait_for_selector(f'#data-table tbody tr:has(td:text-is("{name}"))', state='visible', timeout=5000)

# ################################################################################################################################

def delete_outgoing_connection(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Deletes an outgoing MLLP connection through its own page.
    """
    navigate_to_outgoing(page, base_url)

    item_id = get_item_id(page, name)

    page.evaluate(f'$.fn.zato.outgoing.hl7.mllp.delete_("{item_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    time.sleep(0.5)

# ################################################################################################################################
# ################################################################################################################################
#
# Channels, created and deleted through the wizard and the list page
#
# ################################################################################################################################
# ################################################################################################################################

def create_channel(
    page:'Page',
    base_url:'str',
    name:'str',
    *,
    service:'str' = '',
    criteria:'strstrdict | None' = None,
    is_default:'bool' = False,
    is_audit_log_active:'bool' = False,
    destinations:'anylist | None' = None,
    respond_from:'str' = '',
    delivery_mode:'str' = '',
    ) -> 'None':
    """ Walks the wizard to create a channel - the name and the routing criteria on step 1,
    the service, the destinations, the delivery mode and the reply producer on step 2, and
    the review and finish on step 3. Destinations are a list of dicts with the connection,
    type, is_active flag and options of each, in the shape the wizard itself serializes.
    """
    navigate_to_channels(page, base_url)

    # Open the wizard from the list page ..
    page.click('#markup .page_prompt a:has-text("Create a new channel")')
    _ = page.wait_for_selector('#mllp-wizard', state='visible')

    # .. step 1 - the name, the default flag and the routing criteria, whose fields the
    # routing popover edits and the form posts ..
    page.fill('#id_name', name)

    if is_default:
        page.check('#id_is_default')

    if criteria:
        for field_name, value in criteria.items():
            page.evaluate(f'$("#id_{field_name}").val("{value}")')

    # .. auditing is one of the wizard's logging options, its field posted with the form ..
    if is_audit_log_active:
        page.evaluate('$("#id_is_audit_log_active").prop("checked", true)')

    page.click('#mllp-wizard-next')
    time.sleep(0.2)

    # .. step 2 - the target service, picked through the underlying chosen select ..
    if service:
        page.evaluate(f'$("#id_service").val("{service}").trigger("chosen:updated")')

    # .. the wizard serializes its destinations on finish, so their data has to have loaded ..
    _ = page.wait_for_function('$.fn.zato.channel.hl7.mllp.wizard.destinations._connectionData !== null')

    # .. the destinations, the reply producer and the delivery mode go into the wizard's own
    # state, which is what its panels edit and what its finish serializes into the form ..
    if destinations:

        state_updates = {
            'destinationList': destinations,
            'respondFrom': respond_from,
            'delivery': delivery_mode,
        }

        state_json = json.dumps(state_updates)

        page.evaluate(f'''
            var wizard = $.fn.zato.channel.hl7.mllp.wizard;
            var updates = {state_json};

            var destinationList = [];

            for(var itemIdx = 0; itemIdx < updates.destinationList.length; itemIdx++) {{
                var item = updates.destinationList[itemIdx];
                destinationList.push({{
                    connection: item.connection,
                    type: item.type,
                    isActive: item.is_active,
                    options: item.options
                }});
            }}

            wizard.state.destinationList = destinationList;

            if(updates.respondFrom) {{
                wizard.state.respondFrom = updates.respondFrom;
            }}

            if(updates.delivery) {{
                wizard.state.delivery = updates.delivery;
            }}

            wizard.destinations.settle();
            wizard.destinations.render();
        ''')

    page.click('#mllp-wizard-next')
    time.sleep(0.2)

    # .. step 3 - finish, which posts the form and returns to the list ..
    page.click('#mllp-wizard-next')
    _ = page.wait_for_url('**/zato/channel/hl7/mllp/**', timeout=10000)
    _ = page.wait_for_selector('#data-table', state='visible')

    # .. and the new channel is on the list.
    row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
    assert row is not None, f'Channel "{name}" should be on the list after the wizard'

# ################################################################################################################################

def delete_channel(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Deletes a channel through the list page, the way a person does.
    """
    navigate_to_channels(page, base_url)

    item_id = get_item_id(page, name)

    page.evaluate(f'$.fn.zato.channel.hl7.mllp.delete_("{item_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    time.sleep(0.5)

    row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{name}"))')
    assert row is None, f'Channel "{name}" should be gone after delete'

# ################################################################################################################################
# ################################################################################################################################
#
# The wire side - sends and readiness polls
#
# ################################################################################################################################
# ################################################################################################################################

def wait_for_port(port:'int') -> 'None':
    """ Waits until the MLLP listener accepts connections, which it starts doing
    when the first channel is created.
    """
    deadline = time.monotonic() + _Port_Timeout

    while time.monotonic() < deadline:
        try:
            with socket.create_connection((Host, port), timeout=1):
                return
        except OSError:
            time.sleep(_Poll_Interval)

    raise Exception(f'Port {port} did not accept connections within {_Port_Timeout}s')

# ################################################################################################################################

def send_python(
    port:'int',
    control_id:'str',
    sending_app:'str',
    sending_facility:'str' = '',
    message_type:'str' = 'ADT',
    trigger_event:'str' = 'A01',
    ) -> 'python_client.SendResult':
    """ One send through the python-hl7 client.
    """
    message = python_client.build_message(control_id, sending_app, sending_facility, message_type, trigger_event)

    out = python_client.send_message(Host, port, message)
    return out

# ################################################################################################################################

def wait_until_routed(
    port:'int',
    expected_channel:'str',
    sending_app:'str',
    sending_facility:'str' = '',
    message_type:'str' = 'ADT',
    trigger_event:'str' = 'A01',
    ) -> 'None':
    """ Sends probes until the named channel answers for itself, which is when its route
    has been registered with the running listener. The channel's service has to be one
    that names the channel in MSA-3 for this to be observable.
    """
    deadline = time.monotonic() + _Routed_Timeout
    last_result = None

    while time.monotonic() < deadline:

        control_id = 'probe.' + CryptoManager.generate_hex_string()

        try:
            last_result = send_python(port, control_id, sending_app, sending_facility, message_type, trigger_event)
        except OSError:
            time.sleep(_Poll_Interval)
            continue

        if last_result.msa_3 == expected_channel:
            return

        time.sleep(_Poll_Interval)

    raise Exception(f'Channel `{expected_channel}` did not answer within {_Routed_Timeout}s, last: {last_result}')

# ################################################################################################################################

def wait_until_accepted(
    port:'int',
    sending_app:'str',
    sending_facility:'str' = '',
    ) -> 'python_client.SendResult':
    """ Sends probes until the listener accepts one with an AA, which is when the route the
    probes match has been registered - for channels whose reply carries no channel name.
    """
    deadline = time.monotonic() + _Routed_Timeout
    last_result = None

    while time.monotonic() < deadline:

        control_id = 'probe.' + CryptoManager.generate_hex_string()

        try:
            last_result = send_python(port, control_id, sending_app, sending_facility)
        except OSError:
            time.sleep(_Poll_Interval)
            continue

        if last_result.msa_1 == 'AA':

            out = last_result
            return out

        time.sleep(_Poll_Interval)

    raise Exception(f'No AA answer within {_Routed_Timeout}s, last: {last_result}')

# ################################################################################################################################

def wait_for_item(item_list:'anylist', predicate:'any_', what:'str') -> 'any_':
    """ Waits until the given list, which a receiver appends to as deliveries arrive, holds
    an item the predicate accepts, and returns that item.
    """
    deadline = time.monotonic() + _Routed_Timeout

    while time.monotonic() < deadline:

        for item in item_list:
            if predicate(item):
                return item

        time.sleep(_Poll_Interval)

    raise Exception(f'No {what} arrived within {_Routed_Timeout}s, list: {item_list}')

# ################################################################################################################################

def wait_until_rejected(port:'int', sending_app:'str', sending_facility:'str') -> 'python_client.SendResult':
    """ Sends probes until the listener answers with a rejection, which is when the route
    that used to catch them has been removed.
    """
    deadline = time.monotonic() + _Routed_Timeout
    last_result = None

    while time.monotonic() < deadline:

        control_id = 'probe.' + CryptoManager.generate_hex_string()
        last_result = send_python(port, control_id, sending_app, sending_facility)

        if last_result.msa_1 == 'AR':

            out = last_result
            return out

        time.sleep(_Poll_Interval)

    raise Exception(f'The listener still accepts unmatched messages after {_Routed_Timeout}s, last: {last_result}')

# ################################################################################################################################
# ################################################################################################################################
