# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps
import select
import sys

# sh
import sh
from sh import CommandNotFound

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sh import RunningCommand
    from zato.cli import ServerAwareCommand
    from zato.common.typing_ import any_, anydict, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

class CommandName:

    # This is the default name if $PATH is populated
    Default = 'zato'

    # This is the default path based on .deb / .rpm installers,
    # in case $PATH is not populated.
    PackageFullPath = '/opt/zato/current/bin/zato'

# ################################################################################################################################
# ################################################################################################################################

def get_zato_sh_command(command_name:'str'=CommandName.Default) -> 'RunningCommand':

    try:
        command = getattr(sh, command_name) # type: ignore
        return command
    except CommandNotFound:

        # In case we were using the default name, let's try again with a fallback one ..
        if command_name == CommandName.Default:
            command = getattr(sh, CommandName.PackageFullPath)
            return command

        # .. otherwise, re-raise the exception as we are not sure what to do otherwise.
        else:
            raise

# ################################################################################################################################
# ################################################################################################################################

def read_stdin_data(strip=True):
    """ Reads data from sys.stdin without blocking the caller - in its current form (using select),
    it will work only on Linux and OS X.
    """
    if sys.platform.startswith('win32'):
        return ''
    # Note that we check only sys.stdin for read and that there is no timeout,
    # because we expect for sys.stdin to be available immediately when we run.
    to_read, _, _ = select.select([sys.stdin], [], [], 0)

    if to_read:
        data = to_read[0].readline()
        out = data.strip() if strip else data
    else:
        out = ''

    return out

# ################################################################################################################################
# ################################################################################################################################

class CommandLineInvoker:

    def __init__(
        self,
        expected_stdout=b'',  # type: bytes
        check_stdout=True,    # type: bool
        check_exit_code=True, # type: bool
        server_location=''    # type: str
        ) -> 'None':

        # Imported here to rule out circular references
        from zato.common.test.config import TestConfig

        self.check_stdout = check_stdout
        self.check_exit_code = check_exit_code

        self.expected_stdout = expected_stdout or TestConfig.default_stdout
        self.server_location = server_location or TestConfig.server_location

# ################################################################################################################################

    def _assert_command_line_result(self, out:'RunningCommand') -> 'None':

        if self.check_exit_code:
            if out.exit_code != 0:
                raise ValueError(f'Exit code should be 0 instead `{out.exit_code}`')

        if self.check_stdout:
            if out.stdout != self.expected_stdout:
                raise ValueError(f'Stdout should {self.expected_stdout} instead of {out.stdout}')

# ################################################################################################################################

    def invoke_cli(self, cli_params:'anylist', command_name:'str'=CommandName.Default) -> 'RunningCommand':

        command = get_zato_sh_command(command_name)
        out = command(*cli_params)
        return out

# ################################################################################################################################
# ################################################################################################################################

class CommandLineServiceInvoker(CommandLineInvoker):

    def invoke(self, service:'str', request:'anydict') -> 'any_':

        cli_params = []
        cli_params.append('service')
        cli_params.append('invoke')

        if request:
            request = dumps(request)
            cli_params.append('--payload')
            cli_params.append(request)

        cli_params.append(self.server_location)
        cli_params.append(service)

        return self.invoke_cli(cli_params)

# ################################################################################################################################

    def invoke_and_test(self, service:'str') -> 'any_':
        out = self.invoke(service, {})
        self._assert_command_line_result(out)
        return out

# ################################################################################################################################
# ################################################################################################################################

class _AuthManager:

    # A CLI command on whose behalf we run
    command: 'ServerAwareCommand'

    # API service to invoke to create a new definition
    create_service: 'str'

    # API service to invoke to change password of the newly created definition
    change_password_service: 'str'

    name: 'str'
    password: 'str'

    def __init__(self, command:'ServerAwareCommand', name:'str', password:'str') -> 'None':
        self.command = command
        self.name = name
        self.password = password

# ################################################################################################################################

    def _create(self, create_request:'stranydict', needs_stdout:'bool'=False) -> 'stranydict':

        # This will create a new definition and, in the next step, we will change its password.
        create_response = self.command._invoke_service(self.create_service, create_request)

        if needs_stdout:
            self.command._log_response(create_response, needs_stdout=needs_stdout)

        # API request to send to create a new definition
        change_password_request = {
            'name': self.name,
            'password1': self.password,
            'password2': self.password,
        }

        # Change the newly created definition's password
        self.command._invoke_service_and_log_response(self.change_password_service, change_password_request, needs_stdout=False)

        return create_response

# ################################################################################################################################
# ################################################################################################################################

class BasicAuthManager(_AuthManager):

    create_service = 'zato.security.basic-auth.create'
    change_password_service = 'zato.security.basic-auth.change-password'

    def __init__(
        self,
        command:'ServerAwareCommand',
        name:'str',
        is_active:'bool',
        username:'str',
        realm:'str',
        password:'str'
    ) -> 'None':

        super().__init__(command, name, password)

        self.is_active = is_active
        self.username = username
        self.realm = realm

# ################################################################################################################################

    def create(self, needs_stdout:'bool'=False) -> 'stranydict':

        # API request to send to create a new definition
        create_request = {
            'name': self.name,
            'realm': self.realm,
            'username': self.username,
            'password': self.password,
            'is_active': self.is_active,
        }

        return self._create(create_request, needs_stdout)

# ################################################################################################################################
# ################################################################################################################################
