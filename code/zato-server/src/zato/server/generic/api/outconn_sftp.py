# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger
from shlex import join as shlex_join, quote as shlex_quote, split as shlex_split
from tempfile import mkstemp
from traceback import format_exc

# Zato
from zato.common.api import SFTP
from zato.common.sftp import SFTPOutput
from zato.common.util.api import new_cid
from zato.server.commands import CommandsFacade
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import strlist
    from zato.server.base.parallel import ParallelServer
    from zato.server.commands import CommandResult
    Bunch = Bunch

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

log_level_map = {
    0: '',
    1: '-v',
    2: '-vv',
    3: '-vvv',
    4: '-vvvv',
}

# What to tell the binary about host keys - a server process has no TTY to answer prompts,
# which is why the two modes are either full strictness or accepting keys of new hosts.
_host_key_checking_strict = 'StrictHostKeyChecking=yes'
_host_key_checking_accept_new = 'StrictHostKeyChecking=accept-new'

# ################################################################################################################################

# Default values applied when a configuration key is missing or None
outconn_sftp_config_defaults:'dict[str, object]' = {
    'address': '',
    'username': '',
    'private_key': '',
    'strict_host_key_checking': True,
}

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_sftp_int_config_keys = ()

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_sftp_bool_config_keys = ('strict_host_key_checking',)

# ################################################################################################################################
# ################################################################################################################################

class SFTPClient:
    """ Wraps access to SFTP commands via the command-line sftp binary run in a subprocess.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':

        self.config = config
        self.server = server

        # How many times .execute has been called
        self.command_no = 0

        self.id = self.config.id           # type: int
        self.name = self.config.name       # type: str
        self.is_active = self.config.is_active # type: bool

        self.username = self.config.username # type: str

        # The address is a single field that may include a port, e.g. example.com or example.com:22022
        self.host, self.port = self._parse_address(self.config.address)

        # The connection's password - it is optional because key-based authentication may be in use instead
        password = self.config.secret
        if password is None:
            password = ''
        self.password = password # type: str

        # An optional path to a private key file - when it is empty, system-level keys are used
        self.private_key = self.config.private_key # type: str

        # Whether the remote host key must already be known or whether keys of new hosts are accepted
        self.strict_host_key_checking = self.config.strict_host_key_checking # type: bool

        # Added for API completeness
        self.is_connected = True

        # The binary to invoke - it may be a name or a full path
        self.base_binary = shlex_split(SFTP.DEFAULT.COMMAND_SFTP)

        # The reusable list of arguments that every invocation of the binary receives
        self.base_args = self._get_base_args()

        # The facade through which the sftp binary is invoked in a subprocess
        self.commands = CommandsFacade()
        self.commands.init(server)

# ################################################################################################################################

    def _parse_address(self, address:'str') -> 'tuple[str, int]':
        """ Splits an address of the form host or host:port into its parts, with a default port of 22.
        """

        # The port, if given at all, follows the last colon ..
        if ':' in address:
            host, _, port = address.rpartition(':')
            port = int(port)

        # .. otherwise, the whole address is the host and the port is the default one.
        else:
            host = address
            port = SFTP.DEFAULT.PORT

        return host, port

# ################################################################################################################################

    def _get_base_args(self) -> 'strlist':
        """ Returns a reusable list of arguments that every invocation of the sftp binary receives.
        """

        # Arguments that follow the binary's name
        args = []

        # Buffer size is always available
        args.append('-B')
        args.append(str(SFTP.DEFAULT.BUFFER_SIZE))

        # File and directory metadata is always preserved
        args.append('-p')

        # Port is always available - it either came with the address or it is the default one
        args.append('-P')
        args.append(str(self.port))

        # With strict checking on, the remote host key must already be in known_hosts,
        # otherwise keys of previously unknown hosts are accepted and recorded on first connection.
        args.append('-o')
        if self.strict_host_key_checking:
            args.append(_host_key_checking_strict)
        else:
            args.append(_host_key_checking_accept_new)

        # A private key is optional - when it is given, only that identity is offered to the server
        if self.private_key:
            args.append('-i')
            args.append(self.private_key)
            args.append('-o')
            args.append('IdentitiesOnly=yes')

        return args

# ################################################################################################################################

    def _get_askpass_prefix(self, password_path:'str', helper_path:'str') -> 'str':
        """ Returns the environment prefix that makes the sftp binary obtain the password from our helper script
        instead of prompting for it on a TTY. The prefix contains only paths, never the password itself.
        """

        # Write the password out to its own file ..
        with open(password_path, 'w', encoding='utf8') as password_file:
            _ = password_file.write(self.password)
            _ = password_file.write('\n')

        # .. build a one-shot helper script that prints the password ..
        helper_data = '#!/bin/sh\nexec cat {}\n'.format(shlex_quote(password_path))

        # .. write the helper out ..
        with open(helper_path, 'w', encoding='utf8') as helper_file:
            _ = helper_file.write(helper_data)

        # .. the helper must be executable for the binary to run it ..
        os.chmod(helper_path, 0o700)

        # .. and return the prefix with environment variables pointing to the helper.
        out = 'SSH_ASKPASS_REQUIRE=force SSH_ASKPASS={} DISPLAY=:0 '.format(shlex_quote(helper_path))

        return out

# ################################################################################################################################

    def _build_command(self, log_level:'int') -> 'str':
        """ Builds the full command line for a single invocation of the sftp binary.
        """

        # The binary's name goes first
        args = list(self.base_binary)

        # With a password in use, BatchMode must be explicitly disabled before -b is given below,
        # otherwise the binary would never ask our askpass helper for the password.
        # The first BatchMode value obtained wins, which is why this one must come first.
        if self.password:
            args.append('-o')
            args.append('BatchMode=no')

        # Now, the base arguments shared by all the invocations
        args.extend(self.base_args)

        # Logging is always available but may map to an empty string
        log_level_mapped = log_level_map[log_level]
        if log_level_mapped:
            args.append(log_level_mapped)

        # Commands are always read from stdin, which is what '-' means here
        args.append('-b')
        args.append('-')

        # Both username and host are optional but if they are provided, they must be the last arguments in the command
        if self.host:
            if self.username:
                args.append('{}@{}'.format(self.username, self.host))
            else:
                args.append(self.host)

        out = shlex_join(args)

        return out

# ################################################################################################################################

    def execute(self, cid:'str', data:'str', log_level:'int'=0) -> 'SFTPOutput':
        """ Executes a single or multiple SFTP commands from the input 'data' string.
        """
        # Increment the command counter each time .execute is called
        self.command_no += 1

        logger.info('Executing cid:`%s` (%s; %s; %s), data:`%s`', cid, self.id, self.name, self.command_no, data)

        # Build the full command line for this invocation
        command = self._build_command(log_level)

        # Each command must be on its own line and the last one must end with a newline for the binary to run it
        if not data.endswith('\n'):
            data += '\n'

        # Our response to produce
        out = SFTPOutput(cid, self.command_no)
        out.command = command

        # Paths to askpass-related files, if any are needed
        password_path = ''
        helper_path = ''

        try:
            # With a password in use, the binary needs an askpass helper to read it from ..
            if self.password:

                password_fd, password_path = mkstemp(suffix='-zato-sftp-password.txt')
                os.close(password_fd)

                helper_fd, helper_path = mkstemp(suffix='-zato-sftp-askpass.sh')
                os.close(helper_fd)

                prefix = self._get_askpass_prefix(password_path, helper_path)
                command = prefix + command

            # .. now, invoke the binary in a subprocess, feeding it commands via stdin ..
            result:'CommandResult' = self.commands.invoke(command, cid=cid, stdin=data)

            # .. and populate our output based on what the invocation returned.
            out.is_ok = result.is_ok
            out.stdout = result.stdout
            out.stderr = result.stderr
            out.response_time = result.total_time

            if not result.is_ok:
                out.details = result.stderr

        except Exception:
            out.is_ok = False
            out.details = format_exc()

        finally:
            # No matter the outcome, the askpass files must not outlive this call
            if password_path:
                os.remove(password_path)
            if helper_path:
                os.remove(helper_path)

        return out

# ################################################################################################################################

    def connect(self) -> 'None':
        # We do not maintain long-running connections but we may still want to ping the remote end
        # to make sure we are actually able to connect to it.
        out = self.ping()
        logger.info('SFTP ping; name:`%s`, command:`%s`, stdout:`%s`, stderr:`%s`',
            self.name, out.command, out.stdout, out.stderr)

# ################################################################################################################################

    def close(self) -> 'None':
        # Added for API completeness
        pass

# ################################################################################################################################

    def zato_delete_impl(self) -> 'None':
        # Added for API completeness - there is no long-running connection to close
        pass

# ################################################################################################################################

    def ping(self) -> 'SFTPOutput':
        cid = 'ping-{}'.format(new_cid())

        out = self.execute(cid, SFTP.DEFAULT.COMMAND_PING)

        return out

# ################################################################################################################################
# ################################################################################################################################

class OutconnSFTPWrapper(Wrapper):
    """ Wraps a queue of connections to SFTP.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        config.parent = self
        config.auth_url = config.address
        super(OutconnSFTPWrapper, self).__init__(config, 'outgoing SFTP', server)

# ################################################################################################################################

    def ping(self) -> 'None':
        with self.client() as client:
            out = client.ping() # type: ignore
            if not out.is_ok:
                raise Exception(out.details or out.stderr)

# ################################################################################################################################

    def add_client(self) -> 'None':
        try:
            conn = SFTPClient(self.config, self.server)
        except Exception:
            logger.warning('SFTP client could not be built `%s`', format_exc())
        else:
            _ = self.client.put_client(conn)

# ################################################################################################################################
# ################################################################################################################################
