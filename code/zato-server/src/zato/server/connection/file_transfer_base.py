# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from hashlib import sha256
from tempfile import mkstemp
from time import monotonic
from traceback import format_exc

# gevent
from gevent.fileobject import FileObjectThread

# humanize
from humanize import naturalsize

# Zato
from zato.common.audit_log.api import AuditOutcome
from zato.common.audit_log.file_transfer import record_file_transfer, Operation_Delete, Operation_Move, Operation_Read, \
    Operation_Store

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# How many seconds to wait for a client from the connection's pool
_pool_block_timeout = 60

# How many milliseconds are in one second
_ms_in_second = 1000

# The keys of the envelope a queued file transfer travels under - the bytes stay on the local disk
# and only the spool path and the remote destination go through the queue, so a file of any size
# travels without ever touching a pub/sub row.
Key_Spool_Path = 'spool_path'
Key_Remote_Path = 'remote_path'

# What a spool file's name ends with, so a stray one can be told apart in the temporary directory.
_spool_suffix = '-zato-file-delivery-spool.dat'

# ################################################################################################################################
# ################################################################################################################################

# A list of the info objects a directory listing turns into
file_info_list = list['FileInfo']

# ################################################################################################################################
# ################################################################################################################################

def _elapsed_ms(start:'float') -> 'int':
    """ Returns how many milliseconds passed since the given monotonic start time.
    """
    elapsed = monotonic() - start
    out = int(elapsed * _ms_in_second)
    return out

# ################################################################################################################################
# ################################################################################################################################

def spool_file_payload(data:'bytes') -> 'str':
    """ Writes the bytes of one queued file transfer to a local spool file, returning its path -
    what the publication puts in its envelope in place of the bytes themselves. The write runs
    in its own thread so as not to block the event loop.
    """
    spool_fd, spool_path = mkstemp(suffix=_spool_suffix)
    os.close(spool_fd)

    thread_file = FileObjectThread(spool_path, 'wb')
    _ = thread_file.write(data)
    thread_file.close()

    return spool_path

# ################################################################################################################################
# ################################################################################################################################

class EntryType:
    file = 'file'
    directory = 'directory'
    symlink = 'symlink'

# ################################################################################################################################
# ################################################################################################################################

class FileInfo:
    __slots__ = 'type', 'name', 'size', 'last_modified'

    def __init__(self) -> 'None':
        self.type = '' # type: str
        self.name = '' # type: str

        self.size = 0 # type: int

        self.last_modified = None # type: any_

# ################################################################################################################################

    def to_dict(self, skip_last_modified:'bool' = True) -> 'stranydict':

        out = {
            'type': self.type,
            'name': self.name,
            'size': self.size,
            'size_human': self.size_human,
            'is_file': self.is_file,
            'is_directory': self.is_directory,
            'is_symlink': self.is_symlink,

            'last_modified_iso': self.last_modified_iso,
        }

        # We do not return it by default so as not to make JSON serializers wonder what to do with a Python object.
        if not skip_last_modified:
            out['last_modified'] = self.last_modified

        return out

# ################################################################################################################################

    @property
    def is_file(self) -> 'bool':
        return self.type == EntryType.file

# ################################################################################################################################

    @property
    def is_directory(self) -> 'bool':
        return self.type == EntryType.directory

# ################################################################################################################################

    @property
    def is_symlink(self) -> 'bool':
        return self.type == EntryType.symlink

# ################################################################################################################################

    @property
    def last_modified_iso(self) -> 'str':
        out = self.last_modified.isoformat()
        return out

# ################################################################################################################################

    @property
    def size_human(self) -> 'str':
        out = naturalsize(self.size)
        return out

# ################################################################################################################################
# ################################################################################################################################

class FileTransferConnection:
    """ The shared public API of a single outgoing file transfer connection - the protocol-specific
    subclasses build listing entries from what their client returns and everything else lives here.
    """
    def __init__(self, cid:'str', wrapper:'any_') -> 'None':
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
        ) -> 'None':
        """ Records one file operation of this connection in the audit log.
        """
        _ = record_file_transfer(self.wrapper.audit_log, self.wrapper.config.name, operation, remote_path,
            cid=self.cid, outcome=outcome, size=size, duration_ms=duration_ms, error=error,
            to_path=to_path, checksum=checksum, content=content)

# ################################################################################################################################

    def _build_info(self, name:'str', stat_result:'any_') -> 'FileInfo':
        """ Turns what the client's stat method returned into our common info object.
        """
        raise Exception('Subclasses of FileTransferConnection must implement _build_info')

# ################################################################################################################################

    def _build_info_from_dir_entry(self, entry:'any_') -> 'FileInfo':
        """ Turns one entry of the client's directory listing into our common info object.
        """
        raise Exception('Subclasses of FileTransferConnection must implement _build_info_from_dir_entry')

# ################################################################################################################################

    def get_info(self, remote_path:'str') -> 'FileInfo':

        # Ask the remote server about the path ..
        with self.wrapper.client(should_block=True, block_timeout=_pool_block_timeout) as client:
            stat_result = client.stat(remote_path)

        # .. the entry's name is the last part of the input path ..
        stripped = remote_path.rstrip('/')
        parts = stripped.split('/')
        name = parts[-1]

        # .. and now we can build the full response.
        out = self._build_info(name, stat_result)

        return out

# ################################################################################################################################

    def exists(self, remote_path:'str') -> 'bool':

        with self.wrapper.client(should_block=True, block_timeout=_pool_block_timeout) as client:
            out = client.exists(remote_path)

        return out

# ################################################################################################################################

    def is_file(self, remote_path:'str') -> 'bool':

        info = self.get_info(remote_path)

        out = info.is_file
        return out

# ################################################################################################################################

    def is_directory(self, remote_path:'str') -> 'bool':

        info = self.get_info(remote_path)

        out = info.is_directory
        return out

# ################################################################################################################################

    def list(self, remote_path:'str') -> 'file_info_list':

        # Our response to produce
        out:'file_info_list' = []

        # List the remote directory ..
        with self.wrapper.client(should_block=True, block_timeout=_pool_block_timeout) as client:
            entries = client.scandir(remote_path)

        # .. and turn each entry into our common info object.
        for entry in entries:
            info = self._build_info_from_dir_entry(entry)
            out.append(info)

        return out

# ################################################################################################################################

    def delete_file(self, remote_path:'str') -> 'None':

        start = monotonic()

        # A failed deletion is recorded too, before the caller learns about it.
        try:
            with self.wrapper.client(should_block=True, block_timeout=_pool_block_timeout) as client:
                client.remove(remote_path)
        except Exception:
            duration_ms = _elapsed_ms(start)
            error = format_exc()
            self._record_transfer(Operation_Delete, remote_path,
                outcome=AuditOutcome.Error, duration_ms=duration_ms, error=error)
            raise

        duration_ms = _elapsed_ms(start)
        self._record_transfer(Operation_Delete, remote_path, outcome=AuditOutcome.OK, duration_ms=duration_ms)

# ################################################################################################################################

    def delete_directory(self, remote_path:'str') -> 'None':

        start = monotonic()

        # A failed deletion is recorded too, before the caller learns about it.
        try:
            with self.wrapper.client(should_block=True, block_timeout=_pool_block_timeout) as client:
                client.rmdir(remote_path)
        except Exception:
            duration_ms = _elapsed_ms(start)
            error = format_exc()
            self._record_transfer(Operation_Delete, remote_path,
                outcome=AuditOutcome.Error, duration_ms=duration_ms, error=error)
            raise

        duration_ms = _elapsed_ms(start)
        self._record_transfer(Operation_Delete, remote_path, outcome=AuditOutcome.OK, duration_ms=duration_ms)

# ################################################################################################################################

    def create_directory(self, remote_path:'str', exist_ok:'bool' = False) -> 'None':

        with self.wrapper.client(should_block=True, block_timeout=_pool_block_timeout) as client:
            client.makedirs(remote_path, exist_ok)

# ################################################################################################################################

    def move(self, from_path:'str', to_path:'str') -> 'None':

        start = monotonic()

        # A failed move is recorded too, before the caller learns about it.
        try:
            with self.wrapper.client(should_block=True, block_timeout=_pool_block_timeout) as client:
                client.rename(from_path, to_path)
        except Exception:
            duration_ms = _elapsed_ms(start)
            error = format_exc()
            self._record_transfer(Operation_Move, from_path,
                outcome=AuditOutcome.Error, duration_ms=duration_ms, error=error, to_path=to_path)
            raise

        duration_ms = _elapsed_ms(start)
        self._record_transfer(Operation_Move, from_path, outcome=AuditOutcome.OK, duration_ms=duration_ms, to_path=to_path)

    rename = move

# ################################################################################################################################

    def read(self, remote_path:'str') -> 'bytes':

        start = monotonic()

        # A failed read is recorded too, before the caller learns about it.
        try:
            with self.wrapper.client(should_block=True, block_timeout=_pool_block_timeout) as client:
                out = client.read(remote_path)
        except Exception:
            duration_ms = _elapsed_ms(start)
            error = format_exc()
            self._record_transfer(Operation_Read, remote_path,
                outcome=AuditOutcome.Error, duration_ms=duration_ms, error=error)
            raise

        # The bytes themselves are kept only when the connection asked for that.
        if self.wrapper.should_store_content:
            content = out
        else:
            content = None

        hasher = sha256(out)
        checksum = hasher.hexdigest()

        size = len(out)
        duration_ms = _elapsed_ms(start)
        self._record_transfer(Operation_Read, remote_path,
            outcome=AuditOutcome.OK, size=size, duration_ms=duration_ms, checksum=checksum, content=content)

        return out

# ################################################################################################################################

    def write(self, data:'any_', remote_path:'str', encoding:'str' = 'utf8') -> 'None':

        # Data to be written out must be always bytes.
        if not isinstance(data, bytes):
            data = data.encode(encoding)

        size = len(data)
        start = monotonic()

        # A failed store is recorded too, before the caller learns about it.
        try:
            with self.wrapper.client(should_block=True, block_timeout=_pool_block_timeout) as client:
                client.write(remote_path, data)
        except Exception:
            duration_ms = _elapsed_ms(start)
            error = format_exc()
            self._record_transfer(Operation_Store, remote_path,
                outcome=AuditOutcome.Error, size=size, duration_ms=duration_ms, error=error)
            raise

        # The bytes themselves are kept only when the connection asked for that.
        if self.wrapper.should_store_content:
            content = data
        else:
            content = None

        hasher = sha256(data)
        checksum = hasher.hexdigest()

        duration_ms = _elapsed_ms(start)
        self._record_transfer(Operation_Store, remote_path,
            outcome=AuditOutcome.OK, size=size, duration_ms=duration_ms, checksum=checksum, content=content)

# ################################################################################################################################

    def upload(self, local_path:'str', remote_path:'str') -> 'None':

        # Read the local file in using a separate thread so as not to block the event loop ..
        thread_file = FileObjectThread(local_path, 'rb')
        data = thread_file.read()
        thread_file.close()

        # .. and write it out to the remote location.
        self.write(data, remote_path)

# ################################################################################################################################

    def download_file(self, remote_path:'str', local_path:'str') -> 'None':

        # Read the remote file in first ..
        data = self.read(remote_path)

        # .. and write it out locally using a separate thread so as not to block the event loop.
        thread_file = FileObjectThread(local_path, 'wb')
        _ = thread_file.write(data)
        thread_file.close()

    download = download_file

# ################################################################################################################################

    def publish(self, data:'any_', remote_path:'str', encoding:'str' = 'utf8') -> 'any_':
        """ Queues one file for guaranteed delivery to the remote path, returning as soon as it is stored.
        The bytes go to a local spool file and only its path travels through the queue, so a file
        of any size is delivered with retries, backoff and an audit event per attempt.
        """

        # Data to be written out must be always bytes.
        if not isinstance(data, bytes):
            data = data.encode(encoding)

        spool_path = spool_file_payload(data)

        envelope = {
            Key_Spool_Path: spool_path,
            Key_Remote_Path: remote_path,
        }

        out = self.wrapper.publisher.publish(envelope)
        return out

# ################################################################################################################################
# ################################################################################################################################
