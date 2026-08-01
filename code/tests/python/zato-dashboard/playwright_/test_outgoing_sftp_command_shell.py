# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
from tempfile import mkdtemp

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.sftp_ import SFTPTestServer

# Tests
from outgoing_sftp import create_sftp_connection, delete_sftp_connection, forget_host_key, get_sftp_conn_id, \
     open_sftp_page, row_selector

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.sftp.shell.' + CryptoManager.generate_hex_string(32) + '.'

# What the page shows in an output pane that a command left empty
_Empty_Output = '(None)'

# The class the page puts on its status line once a command has succeeded
_Status_Ok_Class = 'sftp-shell-status-ok'

# The class the page puts on its status line once a command has failed
_Status_Error_Class = 'sftp-shell-status-error'

# How long to wait for the command shell page to render, in milliseconds
_Page_Timeout = 15000

# How long to wait for a command to run against the live server, in milliseconds
_Command_Timeout = 60000

# Console messages that every dashboard page produces and that say nothing about this page
_Console_Noise_Patterns = [
    'favicon.ico',
    'ERR_CONNECTION_REFUSED',
    'live-form-updates',
    'Content-Security-Policy',
]

# ################################################################################################################################
# ################################################################################################################################

def _write_remote_file(sftp_server:'any_', name:'str', content:'str') -> 'str':
    """ Writes a file into the directory the test SSH server serves and returns its absolute path.
    """
    path = os.path.join(sftp_server.files_dir, name)

    with open(path, 'w', encoding='utf8') as file_handle:
        _ = file_handle.write(content)

    return path

# ################################################################################################################################

def _read_file(path:'str') -> 'str':

    with open(path, encoding='utf8') as file_handle:
        out = file_handle.read()

    return out

# ################################################################################################################################

def _open_command_shell(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Goes from the list of connections to the command shell page of the connection of the given name.
    """

    # The link carries the connection's ID and name slug, which is why it is followed
    # rather than reconstructed from the name here ..
    open_sftp_page(page, base_url)
    page.click(row_selector(name) + ' a:has-text("Command shell")')

    # .. and the card is only there once the page's own JS has revealed it.
    _ = page.wait_for_selector('#sftp-shell-card', state='visible', timeout=_Page_Timeout)

# ################################################################################################################################

def _run_command(page:'Page', command:'str') -> 'anydict':
    """ Types a command into the shell, runs it and returns everything the page has to say about it.
    """

    page.fill('#id_data', command)

    def _is_action_response(response:'any_') -> 'bool':
        found = '/zato/outgoing/sftp/command-shell-action/' in response.url
        return found

    # Run and wait for the dashboard's own response ..
    with page.expect_response(_is_action_response, timeout=_Command_Timeout) as response_info:
        page.click('#sftp-shell-run')

    response = response_info.value

    # .. the timing pill is hidden while a command runs, so it coming back means the panes are filled ..
    _ = page.wait_for_selector('#sftp-shell-timing:not([hidden])', timeout=_Command_Timeout)

    # .. the outcome is read off the status line rather than off stderr, because ssh writes
    # .. its "permanently added to the list of known hosts" notice there on a first, successful connection ..
    status_class = page.get_attribute('#sftp-shell-status', 'class')
    assert status_class is not None, 'The status line must always carry a class'

    # .. and text_content is what reads a pane whose tab is not the active one.
    out = {
        'status_code': response.status,
        'stdout': page.text_content('#sftp-shell-stdout'),
        'stderr': page.text_content('#sftp-shell-stderr'),
        'status': page.text_content('#sftp-shell-status'),
        'status_class': status_class,
        'is_ok': _Status_Ok_Class in status_class,
        'timing': page.text_content('#sftp-shell-timing'),
        'active_tab': page.get_attribute('.sftp-shell-card .dashboard-tab-active', 'data-tab'),
    } # type: anydict

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def sftp_shell(logged_in_page:'Page', zato_dashboard:'anydict') -> 'any_':
    """ A live SSH server with an SFTP subsystem, a connection pointing at it and the command shell page open.
    """

    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']

    # Everything the commands operate on lives under this server's own temporary directory
    sftp_server = SFTPTestServer()
    sftp_server.start()

    # An earlier run may have recorded a different key for this same host and port
    forget_host_key(sftp_server.host, sftp_server.port)

    # The zato server was started with an environment variable pointing to this path -
    # the key itself is copied there only now, with the permissions that ssh requires.
    sftp_key_env_name = zato_dashboard['sftp_key_env_name']
    sftp_key_path = zato_dashboard['sftp_key_path']

    shutil.copyfile(sftp_server.client_key_encrypted_path, sftp_key_path)
    os.chmod(sftp_key_path, 0o600)

    # A directory of this machine's own, which is where files fetched from the server land
    local_dir = mkdtemp(prefix='zato-test-sftp-shell-local-')

    name = _Test_Name_Prefix + CryptoManager.generate_hex_string(8)
    conn_id = ''

    try:
        # The connection authenticates with an encrypted key whose passphrase is its password,
        # and host key checking must be off because the server's host key was generated a moment ago.
        open_sftp_page(page, base_url)

        create_sftp_connection(
            page,
            name,
            f'{sftp_server.host}:{sftp_server.port}',
            sftp_server.username,
            sftp_server.password,
            private_key=sftp_key_env_name,
            strict_host_key_checking=False,
        )

        conn_id = get_sftp_conn_id(page, name)

        yield {
            'page': page,
            'base_url': base_url,
            'name': name,
            'conn_id': conn_id,
            'server': sftp_server,
            'remote_dir': sftp_server.files_dir,
            'local_dir': local_dir,
        }

    finally:

        # The connection has to go before the server it points at does ..
        if conn_id:
            open_sftp_page(page, base_url)
            delete_sftp_connection(page, conn_id)

        # .. and both temporary directories go with them.
        sftp_server.stop()
        shutil.rmtree(local_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingSFTPCommandShell:
    """ Drives the outgoing SFTP command shell page against a live SSH server.
    """

    def test_ls_lists_prepared_files(self, sftp_shell:'anydict') -> 'None':
        """ Files placed in the served directory beforehand must show up in the stdout pane.
        """

        page = sftp_shell['page']
        remote_dir = sftp_shell['remote_dir']

        # Prepare three files before the page is even opened ..
        file_names = [] # type: list

        for index in range(3):
            file_name = f'listed-{index}-{CryptoManager.generate_hex_string(8)}.txt'
            _ = _write_remote_file(sftp_shell['server'], file_name, f'contents of file {index}')
            file_names.append(file_name)

        # .. list them through the shell ..
        _open_command_shell(page, sftp_shell['base_url'], sftp_shell['name'])
        result = _run_command(page, f'ls {remote_dir}')

        # .. and every one of them must be in what came back.
        assert result['status_code'] == 200, f'Expected HTTP 200, got {result["status_code"]}'
        assert result['is_ok'], f'Expected the command to succeed, stderr was: "{result["stderr"]}"'

        for file_name in file_names:
            assert file_name in result['stdout'], f'Expected "{file_name}" in stdout, got: "{result["stdout"]}"'

        assert result['active_tab'] == 'stdout', f'Expected the stdout tab to stay active, got: "{result["active_tab"]}"'

# ################################################################################################################################

    def test_get_reads_file_back(self, sftp_shell:'anydict') -> 'None':
        """ A file written into the served directory must come back byte for byte through get.
        """

        page = sftp_shell['page']

        # Write a file whose contents nothing else could produce ..
        content = 'zato-sftp-shell-' + CryptoManager.generate_hex_string(32)
        remote_name = 'fetched-' + CryptoManager.generate_hex_string(8) + '.txt'
        remote_path = _write_remote_file(sftp_shell['server'], remote_name, content)

        local_path = os.path.join(sftp_shell['local_dir'], remote_name)

        # .. fetch it through the shell ..
        _open_command_shell(page, sftp_shell['base_url'], sftp_shell['name'])
        result = _run_command(page, f'get {remote_path} {local_path}')

        # .. the command must have succeeded ..
        assert result['is_ok'], f'Expected the command to succeed, stderr was: "{result["stderr"]}"'
        assert os.path.exists(local_path), f'Expected "{local_path}" to exist after get'

        # .. and what landed locally must be exactly what was written remotely.
        assert _read_file(local_path) == content, f'Fetched contents differ, got: "{_read_file(local_path)}"'

# ################################################################################################################################

    def test_put_then_read_back(self, sftp_shell:'anydict') -> 'None':
        """ A local file uploaded through put must appear in the served directory and be listed there.
        """

        page = sftp_shell['page']
        remote_dir = sftp_shell['remote_dir']

        # Write a local file ..
        content = 'zato-sftp-shell-upload-' + CryptoManager.generate_hex_string(32)
        file_name = 'uploaded-' + CryptoManager.generate_hex_string(8) + '.txt'
        local_path = os.path.join(sftp_shell['local_dir'], file_name)

        with open(local_path, 'w', encoding='utf8') as file_handle:
            _ = file_handle.write(content)

        remote_path = os.path.join(remote_dir, file_name)

        # .. upload it through the shell ..
        _open_command_shell(page, sftp_shell['base_url'], sftp_shell['name'])
        upload_result = _run_command(page, f'put {local_path} {remote_path}')

        assert upload_result['is_ok'], f'Expected the command to succeed, stderr was: "{upload_result["stderr"]}"'

        # .. it must be on the other side, with the contents it went out with ..
        assert os.path.exists(remote_path), f'Expected "{remote_path}" to exist after put'
        assert _read_file(remote_path) == content, f'Uploaded contents differ, got: "{_read_file(remote_path)}"'

        # .. and the shell must list it too.
        list_result = _run_command(page, f'ls {remote_dir}')
        assert file_name in list_result['stdout'], f'Expected "{file_name}" in stdout, got: "{list_result["stdout"]}"'

# ################################################################################################################################

    def test_multi_line_commands(self, sftp_shell:'anydict') -> 'None':
        """ Several commands given on their own lines all run, and each run gets its own command number.
        """

        page = sftp_shell['page']
        remote_dir = sftp_shell['remote_dir']

        file_name = 'multi-' + CryptoManager.generate_hex_string(8) + '.txt'
        _ = _write_remote_file(sftp_shell['server'], file_name, 'multi line command test')

        _open_command_shell(page, sftp_shell['base_url'], sftp_shell['name'])

        # A directory listing and a working directory query, one per line ..
        first_result = _run_command(page, f'ls {remote_dir}\npwd')

        assert first_result['is_ok'], f'Expected the commands to succeed, stderr was: "{first_result["stderr"]}"'
        assert file_name in first_result['stdout'], f'Expected "{file_name}" in stdout, got: "{first_result["stdout"]}"'

        # .. pwd answers with a path, which the listing above could not have produced on its own ..
        assert 'Remote working directory' in first_result['stdout'], \
            f'Expected pwd output in stdout, got: "{first_result["stdout"]}"'

        # .. and a second run must be numbered after the first one.
        second_result = _run_command(page, f'ls {remote_dir}')

        first_command_no = _command_no_of(first_result['timing'])
        second_command_no = _command_no_of(second_result['timing'])

        assert second_command_no > first_command_no, \
            f'Expected the command number to advance, got {first_command_no} then {second_command_no}'

# ################################################################################################################################

    def test_stderr_on_failure(self, sftp_shell:'anydict') -> 'None':
        """ A command that cannot succeed reports on stderr, and the page brings that pane forward.
        """

        page = sftp_shell['page']

        missing_dir = '/zato/does/not/exist/' + CryptoManager.generate_hex_string(16)

        _open_command_shell(page, sftp_shell['base_url'], sftp_shell['name'])
        result = _run_command(page, f'ls {missing_dir}')

        # The dashboard itself is fine, it is the command that failed ..
        assert result['status_code'] == 200, f'Expected HTTP 200, got {result["status_code"]}'
        assert not result['is_ok'], f'Expected the command to fail, status was: "{result["status"]}"'

        # .. stderr says what went wrong ..
        assert result['stderr'] != _Empty_Output, 'Expected stderr to carry the failure'
        assert missing_dir in result['stderr'], f'Expected "{missing_dir}" in stderr, got: "{result["stderr"]}"'

        # .. and the page says so too, with the failing pane in front.
        assert result['status'], 'Expected a status message after a failed command'
        assert result['active_tab'] == 'stderr', f'Expected the stderr tab to come forward, got: "{result["active_tab"]}"'
        assert _Status_Error_Class in result['status_class'], f'Expected an error status, got: "{result["status_class"]}"'

# ################################################################################################################################

    def test_page_is_on_the_dashboard_kit(self, sftp_shell:'anydict') -> 'None':
        """ The page wears the dashboard kit and nothing of the data table markup it used to have.
        """

        page = sftp_shell['page']

        _open_command_shell(page, sftp_shell['base_url'], sftp_shell['name'])

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
            '#sftp-shell-timing',
        ]:
            assert page.query_selector(selector) is not None, f'Expected "{selector}" on the command shell page'

        # .. the card is revealed rather than left transparent ..
        opacity = page.evaluate('window.getComputedStyle(document.querySelector(".dashboard-page")).opacity')
        assert opacity == '1', f'Expected the page to be revealed, got opacity "{opacity}"'

        # .. the connection's name is on the card ..
        conn_name = page.text_content('#sftp-shell-conn-name')
        assert conn_name == sftp_shell['name'], f'Expected "{sftp_shell["name"]}" on the card, got: "{conn_name}"'

        # .. and none of the markup the page used to be built from is left.
        for selector in ['#data-table', '.inline_header', '#id_stdout', '#id_stderr']:
            assert page.query_selector(selector) is None, f'Did not expect "{selector}" on the command shell page'

# ################################################################################################################################

    def test_no_console_errors_and_no_http_500(self, sftp_shell:'anydict') -> 'None':
        """ Running commands produces neither console errors nor server errors.
        """

        page = sftp_shell['page']
        remote_dir = sftp_shell['remote_dir']

        console_errors = [] # type: list
        server_errors = [] # type: list

        def _on_console(msg:'any_') -> 'None':
            if msg.type == 'error':
                console_errors.append(msg.text)

        def _on_response(response:'any_') -> 'None':
            if response.status >= 500:
                server_errors.append(f'{response.status} {response.url}')

        page.on('console', _on_console)
        page.on('response', _on_response)

        # Open the page, run a command that works and one that does not, then clear the panes ..
        _open_command_shell(page, sftp_shell['base_url'], sftp_shell['name'])

        _ = _run_command(page, f'ls {remote_dir}')
        _ = _run_command(page, 'ls /zato/does/not/exist/' + CryptoManager.generate_hex_string(16))

        page.click('#sftp-shell-clear')

        # .. filter the console noise every dashboard page makes ..
        real_errors = [] # type: list

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

def _command_no_of(timing_text:'str') -> 'int':
    """ Extracts the command number out of what the timing pill shows, e.g. "0:00:00.12 (#3)" -> 3.
    """
    _, _, tail = timing_text.partition('(#')
    number, _, _ = tail.partition(')')

    out = int(number)
    return out

# ################################################################################################################################
# ################################################################################################################################
