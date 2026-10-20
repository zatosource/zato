# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from hashlib import sha256
from logging import getLogger
from os.path import getsize, isfile
from posixpath import basename, dirname
from tempfile import NamedTemporaryFile
from time import monotonic
from traceback import format_exc

# gevent
from gevent.fileobject import FileObjectThread

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome
from zato.common.audit_log.file_transfer import record_file_transfer, Operation_Delete, Operation_Move, Operation_Read, \
    Operation_Store
from zato.common.util.logging_ import file_transfer_logger_name
from zato.server.connection.file_transfer_base import ExchangeNotes, Key_Remote_Path, Key_Spool_Path, spool_file_payload, \
    to_file_bytes
from zato.server.connection.sftp_listing import EntryType, parse_stdout, quote_path
from zato.server.connection.sftp_verify import record_sftp_store

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.sftp import SFTPOutput
    from zato.common.typing_ import any_, stranydict
    from zato.server.connection.sftp_listing import SFTPInfo, sftp_info_list
    from zato.server.generic.api.outconn_sftp import OutconnSFTPWrapper

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(file_transfer_logger_name)

# The relative path of the directory a session starts in
_current_directory = '.'

# The root directory, which has no parent and is found as the entry of that name in its own listing
_root_directory = '/'
_root_entry_name = '.'

# How many seconds to wait for a client from the connection's pool. Waiting rather than giving up at once
# means that two runs over one connection take turns instead of one of them failing, and it also covers
# the window while the pool is still being filled in after the server starts.
_pool_block_timeout = 60

# How many bytes at a time a local file is read in when its digest is computed
_hash_chunk_size = 65536

# ################################################################################################################################
# ################################################################################################################################

class SFTPConnectionError(Exception):
    """ The sftp session itself failed and no command was answered.
    """

# ################################################################################################################################

def _reply_summary(sftp_output:'SFTPOutput') -> 'str':
    """ The server's reply on one line.
    """
    reply = _reply_text(sftp_output)
    lines = []

    for line in reply.splitlines():
        stripped = line.strip()
        if stripped:
            lines.append(line)

    out = ', '.join(lines)

    return out

# ################################################################################################################################

def _request_text(data:'str', out:'SFTPOutput') -> 'str':
    """ What was sent to the server as one piece of text - the sftp binary's own invocation
    first, the commands fed to its prompt under it.
    """
    commands = data.rstrip('\n')

    # The invocation is None when the binary's command line could not be built.
    if out.command:
        return '{}\n{}'.format(out.command, commands)

    return commands

# ################################################################################################################################

def _reply_text(out:'SFTPOutput') -> 'str':
    """ What the server said back to one command, as one piece of text - its regular output
    first, then anything it wrote to stderr, which is where the sftp binary explains a failure.
    """
    parts = []

    # Either stream is None when the binary could not be run.
    if out.stdout:
        parts.append(out.stdout)

    if out.stderr:
        parts.append(out.stderr)

    reply = '\n'.join(parts)

    return reply

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

class SFTPConnection(ExchangeNotes):
    """ The public API of a single outgoing SFTP connection, obtained via self.sftp['My Connection'] in services.
    """
    def __init__(self, cid:'str', wrapper:'OutconnSFTPWrapper') -> 'None':
        super().__init__()
        self.cid = cid
        self.wrapper = wrapper

# ################################################################################################################################

    def ping(self) -> 'None':
        self.wrapper.ping()

# ################################################################################################################################

    def _record_transfer(
        self,
        operation:'str',
        remote_path:'str',
        *,
        outcome:'str',
        size:'int' = 0,
        duration_ms:'int' = 0,
        error:'str' = '',
        to_path:'str' = '',
        checksum:'str' = '',
        content:'any_' = None,
        status:'str' = '',
        event_type:'str' = AuditEvent.Request_Sent,
        extra:'stranydict | None' = None,
        ) -> 'None':
        """ Records one file operation of this connection in the audit log.
        """
        _ = record_file_transfer(self.wrapper.audit_log, self.wrapper.config.name, operation, remote_path,
            cid=self.cid, outcome=outcome, size=size, duration_ms=duration_ms, error=error,
            to_path=to_path, checksum=checksum, content=content, status=status, event_type=event_type, extra=extra)

# ################################################################################################################################

    def _execute(self, data:'str', log_level:'int', raise_on_error:'bool'=True) -> 'SFTPOutput':

        if log_level > 0:
            logger.info('Executing cid:`%s` `%s`', self.cid, data)

        # Run the command(s) using a client from the wrapper's queue, waiting for one if they are all busy ..
        with self.wrapper.client(should_block=True, block_timeout=_pool_block_timeout) as client:
            out = client.execute(self.cid, data, log_level) # type: SFTPOutput

        if log_level > 0:
            logger.info('Response received, cid:`%s`, data:`%s`', self.cid, out.to_dict())

        # .. remove the echoed sftp> prompt lines from the output ..
        out.strip_stdout_prefix()

        # .. keep what was sent and what came back for the audit log ..
        request_text = _request_text(data, out)
        reply_text = _reply_text(out)
        self.note_exchange(request_text, reply_text)

        # .. a session that never ran the commands is raised even with raise_on_error off ..
        if out.is_connection_failure():
            reply_summary = _reply_summary(out)
            raise SFTPConnectionError(reply_summary)

        # .. perhaps we are to raise an exception on an error encountered ..
        if not out.is_ok:
            if raise_on_error:
                raise Exception(out.to_dict())

        # .. and return the business response.
        return out

# ################################################################################################################################

    def execute(self, data:'str', log_level:'int'=0, raise_on_error:'bool'=True) -> 'SFTPOutput':

        out = self._execute(data, log_level, raise_on_error)

        return out

# ################################################################################################################################

    def _list(self, options:'str', remote_path:'str', log_level:'int', raise_on_error:'bool') -> 'sftp_info_list | None':
        """ The entries `ls` lists under the path, or None if the path could not be listed.
        The -n option makes the binary format every line itself, numeric owners and groups included,
        so the format and the time zone are the same no matter which server is on the other side.
        """
        result = self.execute(f'ls {options} {quote_path(remote_path)}', log_level, raise_on_error)

        if not result.is_ok:
            return None

        out = parse_stdout(result)
        return out

# ################################################################################################################################

    def _get_directory_info(self, remote_path:'str', log_level:'int', raise_on_error:'bool') -> 'SFTPInfo | None':
        """ Information about a directory, which is the entry of its name in the listing of its parent.
        """

        # Our response to produce
        out = None

        stripped = remote_path.rstrip('/')
        name = basename(stripped)
        parent = dirname(stripped)

        # The root directory has no parent and is found in its own listing ..
        if not name:
            name = _root_entry_name
            parent = _root_directory

        # .. while a relative name without any directories is in the current one.
        elif not parent:
            parent = _current_directory

        # The parent's entries include the hidden ones, because the name may begin with a dot ..
        entries = self._list('-lna', parent, log_level, raise_on_error)

        if entries is None:
            return out

        # .. and the entry is reported under the path it was asked about.
        for entry in entries:
            entry_name = basename(entry.name)
            if entry_name == name:
                entry.name = remote_path
                out = entry
                break

        return out

# ################################################################################################################################

    def get_info(self, remote_path:'str', log_level:'int'=0, raise_on_error:'bool'=True) -> 'SFTPInfo | None':
        """ Information about one entry, or None if it does not exist. A path that does not exist
        raises an exception instead, unless raise_on_error is False.
        """

        # Our response to produce
        out = None

        # Anything other than a directory lists as one line under the very path it was given ..
        entries = self._list('-ln', remote_path, log_level, raise_on_error)

        if entries is None:
            return out

        for entry in entries:
            if entry.name == remote_path:
                out = entry
                break

        # .. whereas a directory lists its contents, so it is looked up in its parent instead.
        else:
            out = self._get_directory_info(remote_path, log_level, raise_on_error)

        return out

# ################################################################################################################################

    def get_existing_info(self, remote_path:'str', log_level:'int'=0) -> 'SFTPInfo':
        """ Information about one entry, which must exist.
        """
        out = self.get_info(remote_path, log_level)

        if not out:
            raise Exception(f'Path `{remote_path}` does not exist')

        return out

# ################################################################################################################################

    def exists(self, remote_path:'str', log_level:'int'=0) -> 'bool':

        # The is_ok flag will be True only if the remote path points to an existing file or directory
        result = self.execute('ls {}'.format(quote_path(remote_path)), log_level, raise_on_error=False)

        out = result.is_ok is True
        return out

# ################################################################################################################################

    def is_file(self, remote_path:'str', log_level:'int'=0) -> 'bool':

        info = self.get_existing_info(remote_path, log_level)

        out = info.is_file
        return out

# ################################################################################################################################

    def is_directory(self, remote_path:'str', log_level:'int'=0) -> 'bool':

        info = self.get_existing_info(remote_path, log_level)

        out = info.is_directory
        return out

# ################################################################################################################################

    def is_symlink(self, remote_path:'str', log_level:'int'=0) -> 'bool':

        info = self.get_existing_info(remote_path, log_level)

        out = info.is_symlink
        return out

# ################################################################################################################################

    def delete(self, remote_path:'str', log_level:'int'=0) -> 'SFTPOutput':

        info = self.get_existing_info(remote_path, log_level)

        if info.is_directory:
            out = self.delete_directory(remote_path, log_level, False)

        elif info.is_file:
            out = self.delete_file(remote_path, log_level, False)

        elif info.is_symlink:
            out = self.delete_symlink(remote_path, log_level, False)

        # .. anything else is not an entry type that we can delete.
        else:
            raise Exception('Unexpected entry type (delete) `{}`'.format(info.to_dict()))

        return out

# ################################################################################################################################

    def delete_by_type(self, remote_path:'str', type:'str', log_level:'int'=0) -> 'SFTPOutput':

        delete_func_map = {
            EntryType.file: self.delete_file,
            EntryType.directory: self.delete_directory,
            EntryType.symlink: self.delete_symlink,
        }

        func = delete_func_map[type]

        out = func(remote_path, log_level, False)
        return out

# ################################################################################################################################

    def _remove(self, is_dir:'bool', remote_path:'str', log_level:'int') -> 'SFTPOutput':

        if is_dir:
            command = 'rmdir'
        else:
            command = 'rm'

        start = monotonic()

        # A failed deletion is recorded too, before the caller learns about it
        try:
            out = self.execute('{} {}'.format(command, quote_path(remote_path)), log_level)
        except Exception:
            duration_ms = int((monotonic() - start) * 1000)
            self._record_transfer(Operation_Delete, remote_path,
                outcome=AuditOutcome.Error, duration_ms=duration_ms, error=format_exc())
            raise

        duration_ms = int((monotonic() - start) * 1000)
        self._record_transfer(Operation_Delete, remote_path, outcome=AuditOutcome.OK, duration_ms=duration_ms)

        return out

# ################################################################################################################################

    def _ensure_entry_type(self, remote_path:'str', expected:'str', log_level:'int') -> 'None':

        info = self.get_existing_info(remote_path, log_level)

        if not info.type == expected:
            raise Exception('Expected for `{}` to be `{}` instead of `{}` ({})'.format(
                remote_path, expected, info.type, info.to_dict()))

# ################################################################################################################################

    def delete_file(self, remote_path:'str', log_level:'int'=0, needs_check:'bool'=True) -> 'SFTPOutput':

        if needs_check:
            self._ensure_entry_type(remote_path, EntryType.file, log_level)

        out = self._remove(False, remote_path, log_level)
        return out

# ################################################################################################################################

    def delete_directory(self, remote_path:'str', log_level:'int'=0, needs_check:'bool'=True) -> 'SFTPOutput':

        if needs_check:
            self._ensure_entry_type(remote_path, EntryType.directory, log_level)

        out = self._remove(True, remote_path, log_level)
        return out

# ################################################################################################################################

    def delete_symlink(self, remote_path:'str', log_level:'int'=0, needs_check:'bool'=True) -> 'SFTPOutput':

        if needs_check:
            self._ensure_entry_type(remote_path, EntryType.symlink, log_level)

        out = self._remove(False, remote_path, log_level)
        return out

# ################################################################################################################################

    def chmod(self, mode:'str', remote_path:'str', log_level:'int'=0) -> 'SFTPOutput':

        out = self.execute('chmod {} {}'.format(mode, quote_path(remote_path)), log_level)
        return out

# ################################################################################################################################

    def chown(self, owner:'str', remote_path:'str', log_level:'int'=0) -> 'SFTPOutput':

        out = self.execute('chown {} {}'.format(owner, quote_path(remote_path)), log_level)
        return out

# ################################################################################################################################

    def chgrp(self, group:'str', remote_path:'str', log_level:'int'=0) -> 'SFTPOutput':

        out = self.execute('chgrp {} {}'.format(group, quote_path(remote_path)), log_level)
        return out

# ################################################################################################################################

    def create_symlink(self, from_path:'str', to_path:'str', log_level:'int'=0) -> 'SFTPOutput':

        out = self.execute('ln -s {} {}'.format(quote_path(from_path), quote_path(to_path)), log_level)
        return out

# ################################################################################################################################

    def create_hardlink(self, from_path:'str', to_path:'str', log_level:'int'=0) -> 'SFTPOutput':

        out = self.execute('ln {} {}'.format(quote_path(from_path), quote_path(to_path)), log_level)
        return out

# ################################################################################################################################

    def create_directory(self, remote_path:'str', log_level:'int'=0, exist_ok:'bool'=False) -> 'SFTPOutput':

        # A leading dash makes the batch go on when the command fails, which it does when the directory exists already
        if exist_ok:
            command = '-mkdir'
        else:
            command = 'mkdir'

        out = self.execute(f'{command} {quote_path(remote_path)}', log_level)
        return out

# ################################################################################################################################

    def list(self, remote_path:'str', log_level:'int'=0) -> 'sftp_info_list':

        result = self.execute(f'ls -ln {quote_path(remote_path)}', log_level)

        out = parse_stdout(result)
        return out

# ################################################################################################################################

    def move(self, from_path:'str', to_path:'str', log_level:'int'=0) -> 'SFTPOutput':

        start = monotonic()

        # A failed move is recorded too, before the caller learns about it
        try:
            # The -l option sends the plain rename of the protocol, which refuses to replace an existing target
            out = self.execute('rename -l {} {}'.format(quote_path(from_path), quote_path(to_path)), log_level)
        except Exception:
            duration_ms = int((monotonic() - start) * 1000)
            self._record_transfer(Operation_Move, from_path,
                outcome=AuditOutcome.Error, duration_ms=duration_ms, error=format_exc(), to_path=to_path)
            raise

        duration_ms = int((monotonic() - start) * 1000)
        self._record_transfer(Operation_Move, from_path, outcome=AuditOutcome.OK, duration_ms=duration_ms, to_path=to_path)

        return out

    rename = move

# ################################################################################################################################

    def download(
        self,
        remote_path:'str',
        local_path:'str',
        recursive:'bool'=True,
        require_file:'bool'=False,
        log_level:'int'=0,
        _needs_audit:'bool'=True
        ) -> 'SFTPOutput':

        # Make sure this is indeed a file
        if require_file:
            self._ensure_entry_type(remote_path, EntryType.file, log_level)

        if recursive:
            options = ' -r'
        else:
            options = ''

        start = monotonic()

        # A failed read is recorded too, before the caller learns about it
        try:
            out = self.execute('get{} {} {}'.format(options, quote_path(remote_path), quote_path(local_path)), log_level)
        except Exception:
            if _needs_audit:
                duration_ms = int((monotonic() - start) * 1000)
                self._record_transfer(Operation_Read, remote_path,
                    outcome=AuditOutcome.Error, duration_ms=duration_ms, error=format_exc())
            raise

        if _needs_audit:
            duration_ms = int((monotonic() - start) * 1000)
            self._record_transfer(Operation_Read, remote_path, outcome=AuditOutcome.OK, duration_ms=duration_ms)

        return out

# ################################################################################################################################

    def download_file(self, remote_path:'str', local_path:'str', log_level:'int'=0, _needs_audit:'bool'=True) -> 'SFTPOutput':

        out = self.download(remote_path, local_path, require_file=True, log_level=log_level, _needs_audit=_needs_audit)
        return out

# ################################################################################################################################

    def read(self, remote_path:'str', mode:'str'='r+b', log_level:'int'=0) -> 'any_':

        start = monotonic()

        # Download the file to a temporary location ..
        with NamedTemporaryFile(mode, suffix='zato-sftp-read.txt') as local_path:

            # .. a failed read is recorded too, before the caller learns about it -
            # .. the event is written here rather than by the download because only
            # .. this method has the file's bytes in hand once it succeeds ..
            # .. a get without -r refuses anything other than a regular file on its own ..
            try:
                _ = self.download(remote_path, local_path.name, recursive=False, log_level=log_level, _needs_audit=False)
            except Exception:
                duration_ms = int((monotonic() - start) * 1000)
                self._record_transfer(Operation_Read, remote_path,
                    outcome=AuditOutcome.Error, duration_ms=duration_ms, error=format_exc())
                raise

            # .. and read it in using a separate thread so as not to block the event loop.
            # .. The mode is passed explicitly, otherwise the file would be reopened in text mode,
            # .. and the descriptor stays open because the temporary file closes it on its own.
            file_descriptor = local_path.fileno()
            thread_file = FileObjectThread(file_descriptor, mode, closefd=False)
            data = thread_file.read()
            thread_file.close()

        # A text-mode read hands back a string while the digest and the archive need the bytes
        if isinstance(data, bytes):
            payload = data
        else:
            payload = data.encode('utf8')

        # The bytes themselves are kept only when the connection asked for that
        if self.wrapper.should_store_content:
            content = payload
        else:
            content = None

        checksum = sha256(payload).hexdigest()

        duration_ms = int((monotonic() - start) * 1000)
        self._record_transfer(Operation_Read, remote_path,
            outcome=AuditOutcome.OK, size=len(payload), duration_ms=duration_ms, checksum=checksum, content=content)

        return data

# ################################################################################################################################

    def _overwrite_if_needed(self, remote_path:'str', overwrite:'bool', log_level:'int') -> 'None':

        info = self.get_info(remote_path, log_level, raise_on_error=False)

        # The remote location exists so we either need to delete it (overwrite=True) or raise an error (overwrite=False)
        if info:
            if overwrite:
                _ = self.delete_by_type(remote_path, info.type, log_level)
            else:
                raise Exception('Cannot upload, location `{}` already exists ({})'.format(remote_path, info.to_dict()))

# ################################################################################################################################

    def upload(
        self,
        local_path:'str',
        remote_path:'str',
        recursive:'bool'=True,
        overwrite:'bool'=False,
        log_level:'int'=0,
        _needs_overwrite_check:'bool'=True
        ) -> 'SFTPOutput':

        # Will raise an exception or delete the remote location, depending on what is needed
        if _needs_overwrite_check:
            self._overwrite_if_needed(remote_path, overwrite, log_level)

        if recursive:
            options = ' -r'
        else:
            options = ''

        # How much is about to be moved - a directory uploaded recursively reports no size
        try:
            size = getsize(local_path)
        except OSError:
            size = 0

        # A single file has a digest and, when the connection asked for that,
        # its bytes travel to the audit log too - a directory has neither.
        checksum = ''
        content = None

        if isfile(local_path):

            # With the archive on, the bytes are read once and serve both purposes ..
            if self.wrapper.should_store_content:
                with open(local_path, 'rb') as local_file:
                    content = local_file.read()
                checksum = sha256(content).hexdigest()

            # .. and without it, the file is digested chunk by chunk.
            else:
                digest = sha256()
                with open(local_path, 'rb') as local_file:
                    while chunk := local_file.read(_hash_chunk_size):
                        digest.update(chunk)
                checksum = digest.hexdigest()

        start = monotonic()

        # A failed store is recorded too, before the caller learns about it
        try:
            out = self.execute('put{} {} {}'.format(options, quote_path(local_path), quote_path(remote_path)), log_level)
        except Exception:
            duration_ms = int((monotonic() - start) * 1000)
            self._record_transfer(Operation_Store, remote_path,
                outcome=AuditOutcome.Error, size=size, duration_ms=duration_ms, error=format_exc())
            raise

        # The store is verified and recorded.
        record_sftp_store(self, remote_path, size, checksum, content, start)

        return out

# ################################################################################################################################

    def write(
        self,
        data:'any_',
        remote_path:'str',
        mode:'str'='w+b',
        overwrite:'bool'=False,
        log_level:'int'=0,
        encoding:'str'='utf8'
        ) -> 'None':

        # Will raise an exception or delete the remote location, depending on what is needed
        self._overwrite_if_needed(remote_path, overwrite, log_level)

        # Data to be written out must be always bytes
        data = to_file_bytes(data, encoding)

        # A temporary file to write data to ..
        with NamedTemporaryFile(mode, suffix='zato-sftp-write.txt') as local_path:

            # .. wrap the file in separate thread so as not to block the event loop.
            # .. the descriptor stays open because the temporary file closes it on its own.
            file_descriptor = local_path.fileno()
            thread_file = FileObjectThread(file_descriptor, mode, closefd=False)
            thread_file.write(data)
            thread_file.flush()

            try:
                # Data written out, we can now upload it to the remote location
                _ = self.upload(local_path.name, remote_path, False, overwrite, log_level, False)

            finally:
                # Now we can close the file too
                thread_file.close()

# ################################################################################################################################

    def publish(self, data:'any_', remote_path:'str', encoding:'str'='utf8') -> 'any_':
        """ Queues one file for guaranteed delivery to the remote path, returning as soon as it is stored.
        The bytes go to a local spool file and only its path travels through the queue, so a file
        of any size is delivered with retries, backoff and an audit event per attempt.
        """

        # Data to be written out must be always bytes
        data = to_file_bytes(data, encoding)

        spool_path = spool_file_payload(data)

        envelope = {
            Key_Spool_Path: spool_path,
            Key_Remote_Path: remote_path,
        }

        out = self.wrapper.publisher.publish(envelope)
        return out

# ################################################################################################################################
# ################################################################################################################################
