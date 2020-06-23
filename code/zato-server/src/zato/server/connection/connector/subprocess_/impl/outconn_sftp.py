# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from datetime import datetime
from tempfile import NamedTemporaryFile
from traceback import format_exc

# Bunch
from bunch import bunchify

# sh
from sh import Command, ErrorReturnCode

# Zato
from zato.common import SFTP
from zato.common.sftp import SFTPOutput
from zato.common.util.json_ import dumps
from zato.server.connection.connector.subprocess_.base import BaseConnectionContainer, Response

# ################################################################################################################################

if 0:
    from logging import Logger

    Logger = Logger

# ################################################################################################################################

# One megabyte = eight thousand kilobits
mb_to_kbit = 8000

# ################################################################################################################################

ip_type_map = {
    SFTP.IP_TYPE.IPV4.id: '-4',
    SFTP.IP_TYPE.IPV6.id: '-6',
}

log_level_map = {
    SFTP.LOG_LEVEL.LEVEL0.id: '',
    SFTP.LOG_LEVEL.LEVEL1.id: '-v',
    SFTP.LOG_LEVEL.LEVEL2.id: '-vv',
    SFTP.LOG_LEVEL.LEVEL3.id: '-vvv',
    SFTP.LOG_LEVEL.LEVEL4.id: '-vvvv',
}

# ################################################################################################################################
# ################################################################################################################################

class PasswordHandler(object):
    """ Listens to the contents of stdout and submits an SSH password when the remote server asks for it.
    Used with SFTP connections that prefer passwords over public keys.
    """
    __slots__ = 'logger', 'password', 'password_prompt', 'current_stdout'

    def __init__(self, logger, password='', password_prompt='password:'):
        # type: (Logger, str, str)
        self.logger = logger
        self.password = password
        self.password_prompt = password_prompt
        self.current_stdout = ''

    def __call__(self, char, stdin):
        # type: (str, object)
        sys.stdout.write(char)
        sys.stdout.flush()
        self.current_stdout += char.strip().lower()
        if self.current_stdout.endswith(self.password_prompt):
            stdin.put(self.password + '\n')

# ################################################################################################################################
# ################################################################################################################################

class SFTPConnection(object):
    """ Wraps access to SFTP commands via command line.
    """
    command_no = 0

    def __init__(self, logger, **config):
        self.logger = logger           # type: Logger
        self.config = bunchify(config) # type: Bunch

        # Reject unknown IP types
        if self.config.force_ip_type:
            if not SFTP.IP_TYPE().is_valid(self.config.force_ip_type):
                raise ValueError('Unknown IP type `{!r}`'.format(self.config.force_ip_type))

        # Reject unknown logging levels
        if self.config.log_level:
            if not SFTP.LOG_LEVEL().is_valid(self.config.log_level):
                raise ValueError('Unknown log level `{!r}`'.format(self.config.log_level))

        self.id = self.config.id                # type: int
        self.name = self.config.name            # type: str
        self.is_active = self.config.is_active  # type: str
        self.password = self.config.secret      # type: str

        self.host = self.config.host or ''      # type: str
        self.port = self.config.port or None    # type: int
        self.username = self.config.username    # type: str

        self.sftp_command = self.config.sftp_command # type: str
        self.ping_command = self.config.ping_command # type: str

        self.identity_file = self.config.identity_file or ''     # type: str
        self.ssh_config_file = self.config.ssh_config_file or '' # type: str

        self.log_level = self.config.log_level       # type: int
        self.should_flush = self.config.should_flush # type: bool
        self.buffer_size = self.config.buffer_size   # type: int

        self.ssh_options = self.config.ssh_options or []     # type: str
        self.force_ip_type = self.config.force_ip_type or '' # type: str

        self.should_preserve_meta = self.config.should_preserve_meta     # type: bool
        self.is_compression_enabled = self.config.is_compression_enabled # type: bool

        # SFTP expects kilobits instead of megabytes
        self.bandwidth_limit = int(float(self.config.bandwidth_limit) * mb_to_kbit) # type: int

        # Added for API completeness
        self.is_connected = True

        # Create the reusable command object
        self.command = self.get_command()

# ################################################################################################################################

    def get_command(self):
        """ Returns a reusable sh.Command object that can execute multiple different SFTP commands.
        """
        # A list of arguments that will be added to the base command
        args = []

        # Buffer size is always available
        args.append('-B')
        args.append(self.buffer_size)

        # Bandwidth limit is always available
        args.append('-l')
        args.append(self.bandwidth_limit)

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
            args.append(self.port)

        # SSH config file is optional
        if self.ssh_config_file:
            args.append('-F')
            args.append(self.ssh_config_file)

        # Additional options in case we have a password
        if self.password:

            args.append('-o')
            args.append('PreferredAuthentications=password')

            args.append('-o')
            args.append('PubkeyAuthentication=no')

            args.append('-o')
            args.append('BatchMode=no')

        else:

            # Identity file is optional and we will set it only if we do not have a password
            if self.identity_file:
                args.append('-i')
                args.append(self.identity_file)

        # Base command to build additional arguments into
        command = Command(self.sftp_command)
        command = command.bake(*args)

        return command

# ################################################################################################################################

    def execute(self, cid, data, log_level=SFTP.LOG_LEVEL.LEVEL4.id):
        """ Executes a single or multiple SFTP commands from the input 'data' string.
        """
        # Increment the command counter each time .execute is called
        self.command_no += 1

        self.logger.info('Executing cid:`%s` (%s; %s; %s), data:`%s`', cid, self.id, self.name, self.command_no, data)

        # Additional command arguments
        args = []

        with NamedTemporaryFile(mode='w+', suffix='-zato-sftp.txt') as f:

            # Write command to the temporary file
            f.write(data)
            f.flush()

            # Append the file names to the list of arguments SFTP receives
            args.append('-b')
            args.append(f.name)

            # Logging is always available but may map to an empty string
            log_level_mapped = log_level_map[log_level]
            if log_level_mapped:
                args.append(log_level_mapped)

            # Both username and host are optional but if they are provided, they must be the last arguments in the command
            if self.host:
                if self.username:
                    args.append('{}@{}'.format(self.username, self.host))
                else:
                    args.append(self.host)

            # If we have a password, additional keyword arguments are needed
            kwargs = {}

            if self.password:
                kwargs['_out'] = PasswordHandler(self.logger, self.password)
                kwargs['_out_bufsize'] = 0
                kwargs['_tty_in'] = True
                kwargs['_unify_ttys'] = True

            out = SFTPOutput(cid, self.command_no)
            result = None

            try:
                # Finally, execute all the commands
                result = self.command(*args, **kwargs)
            except Exception:
                out.is_ok = False
                out.details = format_exc()
                if result:
                    out.command = result.cmd
                    out.stdout = result.stdout
                    out.stderr = result.stderr
            else:
                out.is_ok = True
                out.command = result.cmd
                out.stdout = result.stdout
                out.stderr = result.stderr
            finally:
                return out

# ################################################################################################################################

    def connect(self):
        # We do not maintain long-running connections but we may still want to ping the remote end
        # to make sure we are actually able to connect to it.
        out = self.ping()
        self.logger.info('SFTP ping; name:`%s`, command:`%s`, stdout:`%s`, stderr:`%s`',
            self.name, out.command, out.stdout, out.stderr)

# ################################################################################################################################

    def close(self):
        # Added for API completeness
        pass

# ################################################################################################################################

    def ping(self, _utcnow=datetime.utcnow):
        now = _utcnow().isoformat()
        out = self.execute('ping-{}'.format(now), self.ping_command)
        msg = 'Ping response ({}), is_ok:`{}`, details:`{}`, command:`{}`, stdout:`{}`, stderr:`{}`'.format(
            now, out.is_ok, out.details, out.command, out.stdout, out.stderr)

        if out.is_ok:
            self.logger.info(msg)
            return out
        else:
            raise Exception(msg)

# ################################################################################################################################
# ################################################################################################################################

class SFTPConnectionContainer(BaseConnectionContainer):

    connection_class = SFTPConnection
    ipc_name = conn_type = logging_file_name = 'sftp'

    remove_id_from_def_msg = False
    remove_name_from_def_msg = False

# ################################################################################################################################

    def _on_OUTGOING_SFTP_PING(self, msg):
        return super(SFTPConnectionContainer, self).on_definition_ping(msg)

# ################################################################################################################################

    def _on_OUTGOING_SFTP_DELETE(self, msg):
        return super(SFTPConnectionContainer, self).on_definition_delete(msg)

    _on_GENERIC_CONNECTION_DELETE = _on_OUTGOING_SFTP_DELETE

# ################################################################################################################################

    def _on_OUTGOING_SFTP_CREATE(self, msg):
        return super(SFTPConnectionContainer, self).on_definition_create(msg)

    _on_GENERIC_CONNECTION_CREATE = _on_OUTGOING_SFTP_CREATE

# ################################################################################################################################

    def _on_OUTGOING_SFTP_EDIT(self, msg):
        return super(SFTPConnectionContainer, self).on_definition_edit(msg)

    _on_GENERIC_CONNECTION_EDIT = _on_OUTGOING_SFTP_EDIT

# ################################################################################################################################

    def _on_OUTGOING_SFTP_CHANGE_PASSWORD(self, msg):
        return super(SFTPConnectionContainer, self).on_definition_change_password(msg)

    _on_GENERIC_CONNECTION_CHANGE_PASSWORD = _on_OUTGOING_SFTP_CHANGE_PASSWORD

# ################################################################################################################################

    def _on_OUTGOING_SFTP_EXECUTE(self, msg, is_reconnect=False, _utcnow=datetime.utcnow):
        out = {}
        connection = self.connections[msg.id] # type: SFTPConnection
        start_time = _utcnow()

        try:
            result = connection.execute(msg.cid, msg.data, msg.log_level) # type: Output
        except ErrorReturnCode as e:
            out['stdout'] = e.stdout
            out['stderr'] = e.stderr
        except Exception as e:
            out['stderr'] = format_exc()
            out['is_ok'] = False
        else:
            out.update(result.to_dict())
        finally:
            out['cid'] = msg.cid
            out['command_no'] = connection.command_no
            out['response_time'] = str(_utcnow() - start_time)

        return Response(data=dumps(out))

# ################################################################################################################################

if __name__ == '__main__':

    container = SFTPConnectionContainer()
    container.run()

# ################################################################################################################################
