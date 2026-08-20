# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import INTERNAL_SERVER_ERROR, OK

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.ftp_ import FTPTestServer

# Tests
from outgoing_ftp import create_ftp_connection, delete_ftp_connection, get_ftp_conn_id, open_ftp_page, row_selector

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.ftp.shell.' + CryptoManager.generate_hex_string(32) + '.'

# What the page shows in an output pane that a command left empty
_Empty_Output = '(None)'

# The class the page puts on its status line once a command has succeeded
_Status_Ok_Class = 'file-shell-status-ok'

# The class the page puts on its status line once a command has failed
_Status_Error_Class = 'file-shell-status-error'

# How long to wait for the command shell page to render, in milliseconds
_Page_Timeout = 15000

# How long to wait for a command to run against the live server, in milliseconds
_Command_Timeout = 60000

# The FTP reply code for a file that is unavailable
_FTP_Reply_File_Unavailable = '550'

# Console messages that every dashboard page produces and that say nothing about this page
_Console_Noise_Patterns = [
    'favicon.ico',
    'ERR_CONNECTION_REFUSED',
    'live-form-updates',
    'Content-Security-Policy',
]

# ################################################################################################################################
# ################################################################################################################################

def _write_remote_file(ftp_server:'any_', name:'str', content:'str') -> 'str':
    """ Writes a file into the directory the test FTP server serves and returns its name.
    """
    path = os.path.join(ftp_server.files_dir, name)

    with open(path, 'w', encoding='utf8') as file_handle:
        _ = file_handle.write(content)

    out = name
    return out

# ################################################################################################################################

def _open_command_shell(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Goes from the list of connections to the command shell page of the connection of the given name.
    """

    # Follow the Command shell link from the connection's row ..
    open_ftp_page(page, base_url)

    selector = row_selector(name)
    page.click(selector + ' a:has-text("Command shell")')

    # .. and wait for the card.
    _ = page.wait_for_selector('#file-shell-card', state='visible', timeout=_Page_Timeout)

# ################################################################################################################################

def _run_command(page:'Page', command:'str') -> 'anydict':
    """ Types a command into the shell, runs it and returns everything the page has to say about it.
    """

    page.fill('#id_data', command)

    def _is_action_response(response:'any_') -> 'bool':
        out = '/zato/outgoing/ftp/command-shell-action/' in response.url
        return out

    # Run and wait for the dashboard's own response ..
    with page.expect_response(_is_action_response, timeout=_Command_Timeout) as response_info:
        page.click('#file-shell-run')

    response = response_info.value

    # .. wait for the timing pill to come back ..
    _ = page.wait_for_selector('#file-shell-timing:not([hidden])', timeout=_Command_Timeout)

    # .. the outcome is read off the status line ..
    status_class = page.get_attribute('#file-shell-status', 'class')
    assert status_class is not None, 'The status line must always carry a class'

    out:'anydict' = {
        'status_code': response.status,
        'stdout': page.text_content('#file-shell-stdout'),
        'stderr': page.text_content('#file-shell-stderr'),
        'status': page.text_content('#file-shell-status'),
        'status_class': status_class,
        'is_ok': _Status_Ok_Class in status_class,
        'timing': page.text_content('#file-shell-timing'),
        'active_tab': page.get_attribute('.file-shell-card .dashboard-tab-active', 'data-tab'),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def ftp_shell(logged_in_page:'Page', zato_dashboard:'anydict') -> 'any_':
    """ A live FTP server, a connection pointing at it and the command shell page open.
    """

    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']

    # Everything the commands operate on lives under this server's own temporary directory.
    ftp_server = FTPTestServer()
    ftp_server.start()

    name = _Test_Name_Prefix + CryptoManager.generate_hex_string(8)
    conn_id = ''

    try:
        open_ftp_page(page, base_url)

        create_ftp_connection(page, name, ftp_server.host, ftp_server.port, ftp_server.username, ftp_server.password)

        conn_id = get_ftp_conn_id(page, name)

        yield {
            'page': page,
            'base_url': base_url,
            'name': name,
            'conn_id': conn_id,
            'server': ftp_server,
        }

    finally:

        # The connection has to go before the server it points at does.
        if conn_id:
            open_ftp_page(page, base_url)
            delete_ftp_connection(page, conn_id)

        ftp_server.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingFTPCommandShell:
    """ Drives the outgoing FTP command shell page against a live FTP server.
    """

    def test_ls_lists_prepared_files(self, ftp_shell:'anydict') -> 'None':
        """ Files placed in the served directory beforehand must show up in the stdout pane.
        """

        page = ftp_shell['page']
        base_url = ftp_shell['base_url']
        name = ftp_shell['name']
        server = ftp_shell['server']

        # Prepare three files before the page is even opened ..
        file_names:'strlist' = []

        for file_number in range(3):
            hex_string = CryptoManager.generate_hex_string(8)
            file_name = f'listed-{file_number}-{hex_string}.txt'
            _ = _write_remote_file(server, file_name, f'contents of file {file_number}')
            file_names.append(file_name)

        # .. list them through the shell ..
        _open_command_shell(page, base_url, name)
        result = _run_command(page, 'ls .')

        # .. and every one of them must be in what came back.
        assert result['status_code'] == OK, f'Expected HTTP 200, got {result["status_code"]}'
        assert result['is_ok'], f'Expected the command to succeed, stderr was: "{result["stderr"]}"'

        for file_name in file_names:
            assert file_name in result['stdout'], f'Expected "{file_name}" in stdout, got: "{result["stdout"]}"'

        assert result['active_tab'] == 'stdout', f'Expected the stdout tab to stay active, got: "{result["active_tab"]}"'

# ################################################################################################################################

    def test_cat_reads_file_back(self, ftp_shell:'anydict') -> 'None':
        """ A file written into the served directory must come back byte for byte through cat.
        """

        page = ftp_shell['page']
        base_url = ftp_shell['base_url']
        name = ftp_shell['name']
        server = ftp_shell['server']

        # Write a file whose contents nothing else could produce ..
        content = 'zato-ftp-shell-' + CryptoManager.generate_hex_string(32)
        remote_name = 'fetched-' + CryptoManager.generate_hex_string(8) + '.txt'
        _ = _write_remote_file(server, remote_name, content)

        # .. read it through the shell ..
        _open_command_shell(page, base_url, name)
        result = _run_command(page, f'cat {remote_name}')

        # .. the command must have succeeded and what came back must be exactly what was written.
        assert result['is_ok'], f'Expected the command to succeed, stderr was: "{result["stderr"]}"'
        assert content in result['stdout'], f'Expected the file contents in stdout, got: "{result["stdout"]}"'

# ################################################################################################################################

    def test_mkdir_mv_exists_cycle(self, ftp_shell:'anydict') -> 'None':
        """ A directory made through mkdir receives a file through mv, and exists tracks the move.
        """

        page = ftp_shell['page']
        base_url = ftp_shell['base_url']
        name = ftp_shell['name']
        server = ftp_shell['server']

        # A file to move and a directory to move it into.
        file_name = 'moved-' + CryptoManager.generate_hex_string(8) + '.txt'
        directory = 'made-' + CryptoManager.generate_hex_string(8)

        _ = _write_remote_file(server, file_name, 'file to be moved')

        _open_command_shell(page, base_url, name)

        # Make the directory and move the file into it ..
        result = _run_command(page, f'mkdir {directory}\nmv {file_name} {directory}/{file_name}')
        assert result['is_ok'], f'Expected the commands to succeed, stderr was: "{result["stderr"]}"'

        # .. the old path is empty now and the new one is taken ..
        old_exists = _run_command(page, f'exists {file_name}')
        assert old_exists['stdout'].strip() == 'False', f'Expected "False" after the move, got: "{old_exists["stdout"]}"'

        new_exists = _run_command(page, f'exists {directory}/{file_name}')
        assert new_exists['stdout'].strip() == 'True', f'Expected "True" after the move, got: "{new_exists["stdout"]}"'

        # .. and the file really did land there, with its contents intact.
        moved_path = os.path.join(server.files_dir, directory, file_name)
        assert os.path.exists(moved_path), f'Expected "{moved_path}" to exist after mv'

# ################################################################################################################################

    def test_multi_line_commands(self, ftp_shell:'anydict') -> 'None':
        """ Several commands given on their own lines all run, and each run gets its own command number.
        """

        page = ftp_shell['page']
        base_url = ftp_shell['base_url']
        name = ftp_shell['name']
        server = ftp_shell['server']

        file_name = 'multi-' + CryptoManager.generate_hex_string(8) + '.txt'
        _ = _write_remote_file(server, file_name, 'multi line command test')

        _open_command_shell(page, base_url, name)

        # A directory listing and an existence check, one per line ..
        first_result = _run_command(page, f'ls .\nexists {file_name}')

        assert first_result['is_ok'], f'Expected the commands to succeed, stderr was: "{first_result["stderr"]}"'
        assert file_name in first_result['stdout'], f'Expected "{file_name}" in stdout, got: "{first_result["stdout"]}"'

        # .. the exists output is in stdout too ..
        assert 'True' in first_result['stdout'], f'Expected the exists output in stdout, got: "{first_result["stdout"]}"'

        # .. and a second run must be numbered after the first one.
        second_result = _run_command(page, 'ls .')

        first_command_number = _command_number_of(first_result['timing'])
        second_command_number = _command_number_of(second_result['timing'])

        assert second_command_number > first_command_number, \
            f'Expected the command number to advance, got {first_command_number} then {second_command_number}'

# ################################################################################################################################

    def test_stderr_on_failure(self, ftp_shell:'anydict') -> 'None':
        """ A command that cannot succeed reports on stderr, and the page brings that pane forward.
        """

        page = ftp_shell['page']
        base_url = ftp_shell['base_url']
        name = ftp_shell['name']

        missing_path = 'zato-does-not-exist-' + CryptoManager.generate_hex_string(16) + '.txt'

        _open_command_shell(page, base_url, name)
        result = _run_command(page, f'cat {missing_path}')

        # The request succeeds while the command fails ..
        assert result['status_code'] == OK, f'Expected HTTP 200, got {result["status_code"]}'
        assert not result['is_ok'], f'Expected the command to fail, status was: "{result["status"]}"'

        # .. stderr says what went wrong ..
        assert result['stderr'] != _Empty_Output, 'Expected stderr to carry the failure'
        assert _FTP_Reply_File_Unavailable in result['stderr'], f'Expected the 550 reply in stderr, got: "{result["stderr"]}"'

        # .. and the page says so too, with the failing pane in front.
        assert result['status'], 'Expected a status message after a failed command'
        assert result['active_tab'] == 'stderr', f'Expected the stderr tab to come forward, got: "{result["active_tab"]}"'
        assert _Status_Error_Class in result['status_class'], f'Expected an error status, got: "{result["status_class"]}"'

# ################################################################################################################################

    def test_page_is_on_the_dashboard_kit(self, ftp_shell:'anydict') -> 'None':
        """ The page is built on the dashboard kit.
        """

        page = ftp_shell['page']
        base_url = ftp_shell['base_url']
        name = ftp_shell['name']

        _open_command_shell(page, base_url, name)

        # The kit's own building blocks ..
        for selector in [
            '.dashboard-page',
            '.dashboard-card',
            '.dashboard-card-header',
            '.dashboard-tabs',
            '.dashboard-tab[data-tab="stdout"]',
            '.dashboard-tab[data-tab="stderr"]',
            '.action-button',
            '.secondary-button',
            '#file-shell-timing',
        ]:
            assert page.query_selector(selector) is not None, f'Expected "{selector}" on the command shell page'

        # .. the card is revealed rather than left transparent ..
        opacity = page.evaluate('window.getComputedStyle(document.querySelector(".dashboard-page")).opacity')
        assert opacity == '1', f'Expected the page to be revealed, got opacity "{opacity}"'

        # .. the connection's name is what the card's select has selected ..
        conn_name = page.eval_on_selector('#file-shell-connection-select', 'select => select.selectedOptions[0].textContent')
        assert conn_name == name, f'Expected "{name}" on the card, got: "{conn_name}"'

        # .. and the data table selectors #data-table, .inline_header, #id_stdout and #id_stderr must be absent.
        for selector in ['#data-table', '.inline_header', '#id_stdout', '#id_stderr']:
            assert page.query_selector(selector) is None, f'Did not expect "{selector}" on the command shell page'

# ################################################################################################################################

    def test_no_console_errors_and_no_http_500(self, ftp_shell:'anydict') -> 'None':
        """ Running commands produces neither console errors nor server errors.
        """

        page = ftp_shell['page']
        base_url = ftp_shell['base_url']
        name = ftp_shell['name']

        console_errors:'strlist' = []
        server_errors:'strlist' = []

        def _on_console(msg:'any_') -> 'None':
            if msg.type == 'error':
                console_errors.append(msg.text)

        def _on_response(response:'any_') -> 'None':
            if response.status >= INTERNAL_SERVER_ERROR:
                server_errors.append(f'{response.status} {response.url}')

        page.on('console', _on_console)
        page.on('response', _on_response)

        # Open the page, run a command that works and one that does not, then clear the panes ..
        _open_command_shell(page, base_url, name)

        missing_path = 'zato-does-not-exist-' + CryptoManager.generate_hex_string(16) + '.txt'

        _ = _run_command(page, 'ls .')
        _ = _run_command(page, f'cat {missing_path}')

        page.click('#file-shell-clear')

        # .. filter the console noise every dashboard page makes ..
        real_errors:'strlist' = []

        for error_text in console_errors:
            is_noise = False
            for noise_pattern in _Console_Noise_Patterns:
                if noise_pattern in error_text:
                    is_noise = True
                    break

            if not is_noise:
                real_errors.append(error_text)

        # .. and neither list may have anything in it.
        assert not real_errors, 'Console errors on the command shell page:\n' + '\n'.join(real_errors)
        assert not server_errors, 'HTTP 500+ responses on the command shell page:\n' + '\n'.join(server_errors)

# ################################################################################################################################
# ################################################################################################################################

def _command_number_of(timing_text:'str') -> 'int':
    """ Extracts the command number out of what the timing pill shows, e.g. "0:00:00.12 (#3)" -> 3.
    """
    _, _, tail = timing_text.partition('(#')
    number, _, _ = tail.partition(')')

    out = int(number)
    return out

# ################################################################################################################################
# ################################################################################################################################
