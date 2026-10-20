# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A live SSH server, an SFTP connection created on the dashboard and pointing at it, and a schedule created
# from that connection's own schedules page, polling the server every five seconds. Each invoice put on
# the server is picked up, its amounts are added up by the target service and the file is moved away.

# stdlib
import os
import shutil
import time
from typing import NamedTuple

# Zato
from zato.common.api import FileTransfer
from zato.common.crypto.api import CryptoManager
from zato.common.test.sftp_ import SFTPTestServer

# Tests
from file_transfer_schedule import fill_run_every, fill_service, Invoice_Totals_Service, open_create_wizard, \
     open_schedules, read_invoice_totals, wizard_next, wizard_save
from outgoing_sftp import create_sftp_connection, delete_sftp_connection, get_sftp_conn_id, open_sftp_page

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, callable_

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.sftp.schedule.' + CryptoManager.generate_hex_string(32) + '.'

# The schedule every test here creates
_Schedule_Name = 'invoices'

# How often the schedule polls its directory
_Run_Every = '5'
_Run_Unit  = FileTransfer.Scheduler.Unit.Seconds

# A start time in the past, so the first run is not an hour away, which is what the wizard proposes by default.
# The default user profile displays dates as day-first.
_Past_Start_Date = '01-01-2020 00:00:00'

# The directory on the SSH server the invoices are put in, and the one the schedule moves them to once processed
_Invoices_Directory  = 'invoices'
_Processed_Directory = FileTransfer.Scheduler.Default_Move_Directory

# Where the connection's private key is copied to, under the environment's own directory
_Key_File_Name = 'sftp-schedule-key'

# The permissions ssh requires of a private key
_Key_File_Mode = 0o600

# How long an invoice may take to be picked up, processed and moved away, in seconds
_Processing_Timeout = 60

# How long to sleep between two looks at the results, in seconds
_Poll_Interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

class _Invoice(NamedTuple):
    """ One invoice put on the server, along with what the target service is expected to compute from it.
    """
    data: str
    row_count: int
    total: str

# ################################################################################################################################

_First_Invoice = _Invoice(
    data='invoice_id,customer,amount\nINV-2001,John Smith,120.50\nINV-2002,Maria Johnson,79.50\n',
    row_count=2,
    total='200.00',
)

_Second_Invoice = _Invoice(
    data='invoice_id,customer,amount\nINV-2003,Anna Miller,15.25\n',
    row_count=1,
    total='15.25',
)

# ################################################################################################################################
# ################################################################################################################################

def _wait_until(is_done:'callable_', description:'str') -> 'None':
    """ Polls the condition until it holds, raising if it does not within the processing timeout.
    """
    deadline = time.monotonic() + _Processing_Timeout

    while time.monotonic() < deadline:
        if is_done():
            break
        time.sleep(_Poll_Interval)
    else:
        raise Exception(f'Timed out after {_Processing_Timeout}s waiting for {description}')

# ################################################################################################################################

def _put_invoice(invoices_directory:'str', invoice:'_Invoice') -> 'str':
    """ Writes an invoice into the directory the SSH server serves and returns the name of its file.
    """
    hex_string = CryptoManager.generate_hex_string()
    file_name = f'invoice-{hex_string}.csv'

    path = os.path.join(invoices_directory, file_name)

    with open(path, 'w') as invoice_file:
        _ = invoice_file.write(invoice.data)

    return file_name

# ################################################################################################################################

def _assert_processed(invoices_directory:'str', file_name:'str', conn_name:'str', invoice:'_Invoice') -> 'None':
    """ Waits until the schedule has handed the invoice to the target service and moved its file away,
    and checks what the service computed from it.
    """
    incoming_path = os.path.join(invoices_directory, file_name)
    processed_path = os.path.join(invoices_directory, _Processed_Directory, file_name)

    def _is_computed() -> 'bool':
        totals = read_invoice_totals()
        out = file_name in totals
        return out

    def _is_moved() -> 'bool':
        out = os.path.exists(processed_path)
        return out

    # The target service adds up the invoice ..
    _wait_until(_is_computed, f'the total of `{file_name}`')

    totals = read_invoice_totals()
    result = totals[file_name]

    assert result['conn_name'] == conn_name, f'Unexpected connection in {result}'
    assert result['schedule_name'] == _Schedule_Name, f'Unexpected schedule in {result}'
    assert result['row_count'] == invoice.row_count, f'Unexpected row count in {result}'
    assert result['total'] == invoice.total, f'Unexpected total in {result}'

    # .. and the schedule moves the file out of the directory it polls.
    _wait_until(_is_moved, f'`{file_name}` to be moved to `{_Processed_Directory}`')

    assert not os.path.exists(incoming_path), f'Expected `{incoming_path}` to be gone'

# ################################################################################################################################
# ################################################################################################################################

class TestSFTPSchedulePickup:
    """ An SFTP connection's schedule polls a live SSH server and has each invoice found there processed.
    """

    def test_invoices_are_processed_on_schedule(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # A live SSH server with an empty directory for the invoices ..
        sftp_server = SFTPTestServer()
        sftp_server.start()

        invoices_directory = os.path.join(sftp_server.files_dir, _Invoices_Directory)
        os.mkdir(invoices_directory)

        # .. and the encrypted key the connection authenticates with, its passphrase being the connection's password.
        key_path = os.path.join(zato_dashboard['temporary_dir'], _Key_File_Name)

        _ = shutil.copyfile(sftp_server.client_key_encrypted_path, key_path)
        os.chmod(key_path, _Key_File_Mode)

        conn_name = _Test_Name_Prefix + 'invoices'
        conn_id = ''

        try:

            # The connection is created on the dashboard, recording no host key, because the server's key is a new one ..
            open_sftp_page(page, base_url)

            address = f'{sftp_server.host}:{sftp_server.port}'

            create_sftp_connection(
                page,
                conn_name,
                address,
                sftp_server.username,
                sftp_server.password,
                private_key=key_path,
                ignore_host_key_changes=True,
            )

            conn_id = get_sftp_conn_id(page, conn_name)

            # .. its schedule is created from its own schedules page, with the directory to poll ..
            open_schedules(page, conn_name)
            open_create_wizard(page)

            page.fill('#id_name', _Schedule_Name)
            page.fill('#id_directory', invoices_directory)

            wizard_next(page)

            # .. the service each invoice goes to and an interval of five seconds, starting right away ..
            fill_service(page, Invoice_Totals_Service)
            fill_run_every(page, _Run_Every, _Run_Unit)

            _ = page.evaluate(f'$("#id_start_date").val("{_Past_Start_Date}")')

            run_every = page.input_value('#id_run_every')
            run_unit = page.input_value('#id_run_unit')

            assert run_every == _Run_Every, f'Expected the interval to be {_Run_Every}, got: `{run_every}`'
            assert run_unit == _Run_Unit, f'Expected the unit to be {_Run_Unit}, got: `{run_unit}`'

            # .. and it is saved from the review step ..
            wizard_next(page)
            wizard_save(page)

            # .. an invoice put on the server is picked up and processed ..
            first_file_name = _put_invoice(invoices_directory, _First_Invoice)
            _assert_processed(invoices_directory, first_file_name, conn_name, _First_Invoice)

            # .. and so is the next one, on a later run of the same schedule.
            second_file_name = _put_invoice(invoices_directory, _Second_Invoice)
            _assert_processed(invoices_directory, second_file_name, conn_name, _Second_Invoice)

        finally:

            # The connection goes away together with its schedule, before the server it points at does.
            if conn_id:
                open_sftp_page(page, base_url)
                delete_sftp_connection(page, conn_id)

            sftp_server.stop()

# ################################################################################################################################
# ################################################################################################################################
