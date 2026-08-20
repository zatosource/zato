# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from hl7_client.mllp_receiver import MLLPReceiver
from mllp_channel import wait_for_item, Host
from mllp_outconn import close_popover, delete_outgoing_connection, finish_wizard, go_to_step, \
    navigate_to_outgoing, open_create_wizard, open_edit_wizard, open_popover, set_in_popover, Popover_Input_Prefix, \
    Saved_Tippy_Selector, Wizard_Id
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict
    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.mllp.outconn.wizard.' + CryptoManager.generate_hex_string(32) + '.'

# What the two answers the test changes are set to - both differ from the form's own
# defaults, which is what makes them observable in the review and after a reopen
_Changed_Recv_Timeout = '3000'
_Changed_Max_Retries = '7'
_Changed_Pool_Size = '4'

# The message the Invoke page sends through the connection once it has been created. Its
# type is one the receiver answers rather than files away as unexpected.
_Wire_Message = (
    'MSH|^~\\&|ZATO_WIZARD|ZATO|RECEIVER|RECEIVER|20240315120000||ADT^A01^ADT_A01|{control_id}|P|2.5\r'
    'EVN|A01|20240315120000\r'
    'PID|1||12345^^^FAC^MR||SMITH^JOHN^A||19800115|M\r'
    'PV1|1|I'
)

# What every form on the dashboard says in a field it is waiting for an answer to
_Required_Message = 'This is a required field'

# The two marks a refused save leaves on the first step - the field itself, marked by the
# shared validator, and the label of the row asking for it, marked by the wizard
_Name_Attention_Selector = '#id_edit-name.zato-validator-attention'
_Name_Label_Missing_Selector = f'#{Wizard_Id}-step-body-0 .wizard-name-field label.wizard-missing'

# The same mark on the row opening the popover a required answer is given in
_Timing_Label_Missing_Selector = f'#{Wizard_Id}-row-timing label.wizard-missing'

# How long a refused save is given to mark what it is waiting for - the marking is the
# page's own work, with nothing to wait for on the wire
_Mark_Timeout = 2000

# How long a save is given to reach the server and say how it went - one POST answered
# by the same host the page came from, so anything beyond this is a fault, not a wait
_Save_Timeout = 2000

# How long a refused save is given to say nothing before the absence of the tooltip is
# read as an answer - a save that did go through would have shown it by then
_Refusal_Settle_Seconds = 0.5

# How long the live check is given to reach the receiver and come back
_Probe_Timeout = 20000

# How long the connection is given to reach the server after the wizard created it, so that
# the Invoke page has something to send through
_Deploy_Timeout = 60

# How often the Invoke page is asked again while the connection is still on its way
_Deploy_Poll_Interval = 2

# How long one Invoke attempt is given to come back with either an answer or an error
_Invoke_Timeout = 15000

# ################################################################################################################################
# ################################################################################################################################

def _text_has(control_id:'str') -> 'any_':
    """ A predicate matching a receiver delivery whose text carries this control id.
    """
    def _predicate(item:'any_') -> 'bool':
        out = control_id in item.text
        return out

    return _predicate

# ################################################################################################################################

def _assert_not_saved(page:'Page') -> 'None':
    """ Confirms a refused save said nothing about having gone through - the tooltip a
    save shows beside the button it was asked for through is given its time and does
    not turn up.
    """
    time.sleep(_Refusal_Settle_Seconds)

    saved = page.query_selector(Saved_Tippy_Selector)
    assert saved is None, 'A refused save should not have said that it went through'

# ################################################################################################################################

def _run_probe(page:'Page', button_id:'str') -> 'str':
    """ Presses one of the wizard's live checks and returns the verdict it painted.
    """
    result_selector = f'#{button_id} + .wizard-probe-result'

    page.click(f'#{button_id}')

    # The verdict stays empty until the check comes back, however it comes back
    _ = page.wait_for_function(
        f'document.querySelector("{result_selector}").textContent !== ""',
        timeout=_Probe_Timeout,
    )

    out = page.inner_text(result_selector)
    return out

# ################################################################################################################################

def _read_in_popover(page:'Page', link_name:'str', field_name:'str') -> 'str':
    """ Opens one popover, reads what one of its inputs came back with and closes it again.
    """
    open_popover(page, link_name)
    out = page.input_value(f'#{Popover_Input_Prefix}{field_name}')
    close_popover(page)

    return out

# ################################################################################################################################

def _send_through_connection(page:'Page', base_url:'str', name:'str', control_id:'str') -> 'None':
    """ Sends one message through the saved connection from the per-row Invoke overlay,
    retrying while the connection is still on its way to the server.
    """
    navigate_to_outgoing(page, base_url)

    # The Invoke link opens the shared invoker overlay ..
    page.click(f'#data-table tbody tr:has(td:text-is("{name}")) a:text-is("Invoke")')
    _ = page.wait_for_selector('#invoker-modal-overlay:not(.hidden)', state='visible', timeout=_Mark_Timeout)

    # .. the segments are separated by carriage returns and an editor filled the way a person
    # fills one would not keep them, so the value is written as it stands ..
    message = _Wire_Message.format(control_id=control_id)
    page.evaluate('text => $.fn.zato.invoker._request_pane.setValue(text)', message)

    deadline = time.monotonic() + _Deploy_Timeout
    last_response = ''

    while time.monotonic() < deadline:

        # The status line is cleared first so each attempt waits for its own verdict
        page.evaluate('$("#invoker-modal-status").text("")')
        page.click('#invoker-modal-invoke-button')

        _ = page.wait_for_function(
            '''() => {
                let status = document.querySelector("#invoker-modal-status");
                let text = status.textContent;
                return text && text.indexOf("Invoking") === -1 && text.trim().length > 0;
            }''',
            timeout=_Invoke_Timeout,
        )

        last_response = page.evaluate('$("#invoker-modal-response-pane").data("raw-response")')

        # An acknowledgment carries the control id back, which is what says the message
        # went out rather than that the connection was not there yet
        if control_id in last_response:
            page.evaluate('$.fn.zato.invoker.close_overlay()')
            return

        time.sleep(_Deploy_Poll_Interval)

    raise Exception(f'`{name}` did not send within {_Deploy_Timeout}s, last response: {last_response}')

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingHL7MLLPWizard:
    """ Walks the MLLP outgoing connection wizard end to end - creating a connection through
    its three steps against a real hl7apy receiver, checking the endpoint live before anything
    is saved, sending through the connection once it exists and reopening it for an edit, which
    is the wizard reaching its fields under the edit- prefix. Along the way the walk is taken
    with the Enter key and a save is refused over an answer taken back out, which marks the
    field the way every form on the dashboard marks one it is waiting for.
    """

    def test_mllp_outconn_wizard_full_cycle(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The endpoint the connection points at - a real hl7apy MLLP server
        receiver = MLLPReceiver()
        receiver.start()

        # Collect console errors along the way ..
        console_errors = [] # type: list

        def _on_console(msg:'any_') -> 'None':
            if msg.type == 'error':
                console_errors.append(msg.text)

        page.on('console', _on_console)

        # .. and server errors too.
        server_errors = [] # type: list

        def _on_response(response:'any_') -> 'None':
            if response.status >= 500:
                server_errors.append(f'{response.status} {response.url}')

        page.on('response', _on_response)

        conn_name = _Test_Name_Prefix + 'conn'
        address = f'{Host}:{receiver.port}'

        # Step 1 - the two answers nothing can stand in for
        open_create_wizard(page, base_url)

        page.fill('#id_name', conn_name)
        page.fill('#id_address', address)

        # The header badge mirrors the name as it is typed
        badge_text = page.inner_text(f'#{Wizard_Id}-name-badge')
        assert conn_name in badge_text, f'Expected "{conn_name}" in the name badge, got: "{badge_text}"'

        # A step filled in from the keyboard is left from the keyboard - Enter does what
        # Next does, and the walk goes on from the step it lands on
        page.press('#id_address', 'Enter')
        _ = page.wait_for_selector(f'#{Wizard_Id}-step-body-1', state='visible', timeout=_Mark_Timeout)

        go_to_step(page, 0)

        # The live check reaches the receiver with nothing stored yet, which is the whole
        # point of it - a wrong address is found out here rather than after a save
        verdict = _run_probe(page, f'{Wizard_Id}-check')

        assert address in verdict, f'Expected the address in the verdict, got: "{verdict}"'
        assert 'AA' in verdict, f'Expected an accepted acknowledgment, got: "{verdict}"'

        # .. and the receiver has it on record, not only the dashboard
        assert receiver.deliveries, 'The receiver should have taken delivery of the check message'

        # The timing popover holds the receive timeout ..
        set_in_popover(page, 'timing', 'recv_timeout', _Changed_Recv_Timeout)

        summary_text = page.inner_text(f'#{Wizard_Id}-summary-timing')
        assert _Changed_Recv_Timeout in summary_text, \
            f'Expected the changed timeout in the summary, got: "{summary_text}"'

        # .. and the retries popover on step 2 how often a failed send is tried again
        go_to_step(page, 1)
        set_in_popover(page, 'retries', 'max_retries', _Changed_Max_Retries)

        # Step 3 - the review says everything the two steps were told
        go_to_step(page, 2)
        review_text = page.inner_text(f'#{Wizard_Id}-review')

        assert conn_name in review_text, f'Expected "{conn_name}" in the review, got: "{review_text}"'
        assert address in review_text, f'Expected "{address}" in the review, got: "{review_text}"'
        assert _Changed_Recv_Timeout in review_text, \
            f'Expected the changed timeout in the review, got: "{review_text}"'
        assert _Changed_Max_Retries in review_text, \
            f'Expected the changed retry count in the review, got: "{review_text}"'

        # The review's own check reaches the same receiver
        verdict = _run_probe(page, f'{Wizard_Id}-review-check')
        assert 'AA' in verdict, f'Expected an accepted acknowledgment on the review, got: "{verdict}"'

        # Create - back on the list, with the connection's own row on it
        finish_wizard(page, conn_name)

        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{conn_name}"))')
        assert row is not None, f'Connection "{conn_name}" should be on the list after the wizard'

        row_text = row.inner_text()
        assert address in row_text, f'Expected the address in the row, got: "{row_text}"'

        # The connection is live now - a message sent through it from the Invoke page
        # reaches the receiver on the other side
        control_id = 'wire.' + CryptoManager.generate_hex_string()
        _send_through_connection(page, base_url, conn_name, control_id)

        _ = wait_for_item(receiver.deliveries, _text_has(control_id), f'delivery of {control_id}')

        # Reopening for an edit is the wizard reaching every field under the edit- prefix,
        # so what comes back is what was stored rather than the form's defaults
        open_edit_wizard(page, base_url, conn_name)

        assert page.input_value('#id_edit-name') == conn_name, 'The stored name should come back on edit'
        assert page.input_value('#id_edit-address') == address, 'The stored address should come back on edit'

        stored_timeout = _read_in_popover(page, 'timing', 'recv_timeout')
        assert stored_timeout == _Changed_Recv_Timeout, \
            f'Expected the stored timeout on edit, got: "{stored_timeout}"'

        # A save asked for with the name taken out is refused, the field marked the way every
        # form on the dashboard marks one it is waiting for and the row's label saying so too
        page.fill('#id_edit-name', '')
        page.click(f'#{Wizard_Id}-save')

        _ = page.wait_for_selector(_Name_Attention_Selector, state='attached', timeout=_Mark_Timeout)
        _ = page.wait_for_selector(_Name_Label_Missing_Selector, state='attached', timeout=_Mark_Timeout)

        placeholder = page.get_attribute('#id_edit-name', 'placeholder')
        assert placeholder == _Required_Message, \
            f'Expected the required message on the name, got: "{placeholder}"'

        _assert_not_saved(page)

        # An answer given in a popover is asked for on the row that opens it, the input
        # holding it never being on screen - and the answered name is left alone
        page.fill('#id_edit-name', conn_name)
        set_in_popover(page, 'timing', 'recv_timeout', '')

        page.click(f'#{Wizard_Id}-save')

        _ = page.wait_for_selector(_Timing_Label_Missing_Selector, state='attached', timeout=_Mark_Timeout)
        _ = page.wait_for_selector(_Name_Attention_Selector, state='detached', timeout=_Mark_Timeout)

        _assert_not_saved(page)

        # With both answered the step is saved from the keyboard, an edit being saved
        # from wherever it stands
        set_in_popover(page, 'timing', 'recv_timeout', _Changed_Recv_Timeout)
        page.press('#id_edit-name', 'Enter')

        _ = page.wait_for_selector(Saved_Tippy_Selector, timeout=_Save_Timeout)

        go_to_step(page, 1)

        stored_retries = _read_in_popover(page, 'retries', 'max_retries')
        assert stored_retries == _Changed_Max_Retries, \
            f'Expected the stored retry count on edit, got: "{stored_retries}"'

        # One more change, saved through the same wizard
        set_in_popover(page, 'pool', 'pool_size', _Changed_Pool_Size)
        finish_wizard(page, conn_name)

        # .. and it stuck, which the next reopen says
        open_edit_wizard(page, base_url, conn_name)
        go_to_step(page, 1)

        stored_pool_size = _read_in_popover(page, 'pool', 'pool_size')
        assert stored_pool_size == _Changed_Pool_Size, \
            f'Expected the stored pool size on the second edit, got: "{stored_pool_size}"'

        # Delete the connection the test created
        delete_outgoing_connection(page, base_url, conn_name)

        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{conn_name}"))')
        assert row is None, f'Connection "{conn_name}" should be gone after delete'

        # The receiver has served its purpose
        receiver.stop()

        # No console or server errors along the way
        real_errors = [] # type: list

        for error_text in console_errors:
            if 'favicon.ico' in error_text or 'Content-Security-Policy' in error_text:
                continue
            real_errors.append(error_text)

        assert not real_errors, 'Console errors during the MLLP outconn wizard cycle:\n' + '\n'.join(real_errors)
        assert not server_errors, 'HTTP 500+ responses during the MLLP outconn wizard cycle:\n' + '\n'.join(server_errors)

# ################################################################################################################################
# ################################################################################################################################
