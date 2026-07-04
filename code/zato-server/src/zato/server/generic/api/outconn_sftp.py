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

# One megabyte is eight thousand kilobits
_mb_to_kbit = 8000

# ################################################################################################################################

ip_type_map = {
    SFTP.IP_TYPE.IPV4.id: '-4',
    SFTP.IP_TYPE.IPV6.id: '-6',
}

log_level_map = {
    0: '',
    1: '-v',
    2: '-vv',
    3: '-vvv',
    4: '-vvvv',
}

# ################################################################################################################################

# Default values applied when a configuration key is missing or None
outconn_sftp_config_defaults:'dict[str, object]' = {
    'host': '',
    'port': SFTP.DEFAULT.PORT,
    'username': '',
    'identity_file': '',
    'ssh_config_file': '',
    'log_level': 0,
    'sftp_command': SFTP.DEFAULT.COMMAND_SFTP,
    'ping_command': SFTP.DEFAULT.COMMAND_PING,
    'buffer_size': SFTP.DEFAULT.BUFFER_SIZE,
    'bandwidth_limit': SFTP.DEFAULT.BANDWIDTH_LIMIT,
    'force_ip_type': '',
    'should_flush': False,
    'should_preserve_meta': True,
    'is_compression_enabled': False,
    'ssh_options': '',
    'default_directory': '',
}

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_sftp_int_config_keys = ('port', 'log_level', 'buffer_size')

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_sftp_bool_config_keys = ('should_flush', 'should_preserve_meta', 'is_compression_enabled')

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

        # Reject unknown IP types
        if self.config.force_ip_type:
            if not SFTP.IP_TYPE().is_valid(self.config.force_ip_type):
                raise Exception('Unknown IP type `{!r}`'.format(self.config.force_ip_type))

        # Reject unknown logging levels
        if self.config.log_level:
            if self.config.log_level not in log_level_map:
                raise Exception('Unknown log level `{!r}`'.format(self.config.log_level))

        self.id = self.config.id           # type: int
        self.name = self.config.name       # type: str
        self.is_active = self.config.is_active # type: bool

        self.host = self.config.host         # type: str
        self.port = self.config.port         # type: int
        self.username = self.config.username # type: str

        # The connection's password - it is optional because key-based authentication may be in use instead
        password = self.config.secret
        if password is None:
            password = ''
        self.password = password # type: str

        self.sftp_command = self.config.sftp_command # type: str
        self.ping_command = self.config.ping_command # type: str

        self.identity_file = self.config.identity_file     # type: str
        self.ssh_config_file = self.config.ssh_config_file # type: str

        self.log_level = self.config.log_level     # type: int
        self.should_flush = self.config.should_flush # type: bool
        self.buffer_size = self.config.buffer_size # type: int

        self.ssh_options = self.config.ssh_options     # type: str
        self.force_ip_type = self.config.force_ip_type # type: str

        self.should_preserve_meta = self.config.should_preserve_meta         # type: bool
        self.is_compression_enabled = self.config.is_compression_enabled     # type: bool

        # SFTP expects kilobits instead of megabytes
        self.bandwidth_limit = int(float(self.config.bandwidth_limit) * _mb_to_kbit) # type: int

        # Added for API completeness
        self.is_connected = True

        # The binary to invoke - it may be a name or a full path
        self.base_binary = shlex_split(self.sftp_command)

        # The reusable list of arguments that every invocation of the binary receives
        self.base_args = self._get_base_args()

        # The facade through which the sftp binary is invoked in a subprocess
        self.commands = CommandsFacade()
        self.commands.init(server)

# ################################################################################################################################

    def _get_base_args(self) -> 'strlist':
        """ Returns a reusable list of arguments that every invocation of the sftp binary receives.
        """

        # Arguments that follow the binary's name
        args = []

        # Buffer size is always available
        args.append('-B')
        args.append(str(self.buffer_size))

        # Bandwidth limit is always available
        args.append('-l')
        args.append(str(self.bandwidth_limit))

        # Preserving file and directory metadata is optional
        if self.should_preserve_meta:
            args.append('-p')

        # Immediate flushing is optional
        if self.should_flush:
            args.append('-f')

        # Compression is optional
        if self.is_compression_enabled:
            args.append('-C')

        # Forcing a particular IP version is optional
        if self.force_ip_type:
            args.append(ip_type_map[self.force_ip_type])

        # Port is optional
        if self.port:
            args.append('-P')
            args.append(str(self.port))

        # Identity file is optional - when it is given, only that identity is offered to the server
        if self.identity_file:
            args.append('-i')
            args.append(self.identity_file)
            args.append('-o')
            args.append('IdentitiesOnly=yes')

        # SSH config file is optional
        if self.ssh_config_file:
            args.append('-F')
            args.append(self.ssh_config_file)

        # Additional SSH options are optional, given as one option per line
        for option in self.ssh_options.splitlines():
            option = option.strip()
            if option:
                args.append('-o')
                args.append(option)

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

        out = self.execute(cid, self.ping_command)

        return out

# ################################################################################################################################
# ################################################################################################################################

class OutconnSFTPWrapper(Wrapper):
    """ Wraps a queue of connections to SFTP.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        config.parent = self
        config.auth_url = '{}:{}'.format(config.host, config.port)
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
