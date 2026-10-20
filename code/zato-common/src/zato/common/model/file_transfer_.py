# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.file_transfer.api import Default_Encoding, Encoding_Next_Line
from zato.common.file_transfer.spool import Chunk_Size, spool_bytes
from zato.common.typing_ import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.documents.model import doclist
    from zato.common.typing_ import binaryio_, generator_, stranydict, textio_
    doclist = doclist

    bytesgen = generator_[bytes, None, None]
    strgen   = generator_[str, None, None]

# ################################################################################################################################
# ################################################################################################################################

# A byte order mark is not part of the text it opens.
_byte_order_mark = '\ufeff'

# What a line or a record of a file's text ends with once the text is read - every kind of line break
# is read as this one.
_line_break = '\n'

# The line break of the EBCDIC encodings, read as a line feed.
_next_line = '\x85'

# How many characters at a time a file's text is read in when it is split into lines or records.
_text_chunk_size = 1024 * 1024

# How many bytes the head of a file has unless the caller asks for another number.
Default_Head_Size = 4096

# How a decoding error is handled - an error is raised, or an undecodable byte becomes the replacement character.
_errors_strict  = 'strict'
_errors_replace = 'replace'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class FileTransferSchedule:
    """ One recurring file pickup task of an SFTP or SMB connection - stored in the connection's
    opaque attributes and mirrored by one interval-based scheduler job.
    """

    # Identity - the id is a slug derived from the name when the schedule is created
    id: str = ''
    name: str = ''
    is_active: bool = True

    # What to pick up
    directory: str = ''
    pattern: str = ''

    # When is a file ready - stability or marker, with the per-mode details
    ready_how: str = ''
    stability_delay: int = 0
    marker_suffix: str = ''

    # Competing consumers - rename-to-claim before anything reads the file
    should_claim: bool = False

    # The encoding the text of each file is read in, as a Python codec name
    encoding: str = ''

    # What happens next
    service: str = ''
    on_success: str = ''
    move_directory: str = ''

    # How often to look
    run_every: int = 0
    run_unit: str = ''
    start_date: str = ''

    # How many seconds may pass without a file arriving before the arrival alert
    # considers the schedule overdue - zero means no such expectation.
    arrival_window: int = 0

    # The retry settings, zero attempts means no limit.
    max_attempts:         int = 0
    retry_backoff:        int = 0
    quarantine_directory: str = ''

    # The daily expectation, zero files means no expectation.
    expected_files: int = 0
    expected_by:    str = ''
    expected_days:  str = ''

    # The database ID of the linked scheduler job
    job_id: int = 0

# ################################################################################################################################

    def to_dict(self) -> 'stranydict':

        out = {
            'id': self.id,
            'name': self.name,
            'is_active': self.is_active,
            'directory': self.directory,
            'pattern': self.pattern,
            'ready_how': self.ready_how,
            'stability_delay': self.stability_delay,
            'marker_suffix': self.marker_suffix,
            'should_claim': self.should_claim,
            'encoding': self.encoding,
            'service': self.service,
            'on_success': self.on_success,
            'move_directory': self.move_directory,
            'run_every': self.run_every,
            'run_unit': self.run_unit,
            'start_date': self.start_date,
            'arrival_window': self.arrival_window,
            'max_attempts': self.max_attempts,
            'retry_backoff': self.retry_backoff,
            'quarantine_directory': self.quarantine_directory,
            'expected_files': self.expected_files,
            'expected_by': self.expected_by,
            'expected_days': self.expected_days,
            'job_id': self.job_id,
        }

        return out

# ################################################################################################################################

    @staticmethod
    def from_dict(data:'stranydict') -> 'FileTransferSchedule':

        out = FileTransferSchedule()

        for name, value in data.items():
            setattr(out, name, value)

        return out

# ################################################################################################################################
# ################################################################################################################################

class FileTransferItem:
    """ A single file received by a file transfer schedule, handed over to the service the schedule invokes -
    one instance per file. The file's bytes stay in a local spool file and are read only when the service asks for them,
    so a file of any size is handed over without being held in memory.
    """

    def __init__(
        self,
        conn_type:'str',
        conn_name:'str',
        schedule_name:'str',
        directory:'str',
        file_name:'str',
        full_path:'str',
        size:'int',
        last_modified:'str',
        path:'str',
        encoding:'str',
        ) -> 'None':

        # Where the file came from
        self.conn_type = conn_type
        self.conn_name = conn_name
        self.schedule_name = schedule_name

        # The file itself - last_modified is an ISO-8601 timestamp
        self.directory = directory
        self.file_name = file_name
        self.full_path = full_path
        self.size = size
        self.last_modified = last_modified

        # The local spool file the bytes are read from and the encoding its text is read in
        self.path = path
        self.encoding = encoding

    def __repr__(self) -> 'str':
        class_name = self.__class__.__name__
        self_id = hex(id(self))
        return '<{} at {}, full_path:`{}`, size:`{}`, encoding:`{}`, conn_name:`{}`, schedule_name:`{}`>'.format(
            class_name, self_id, self.full_path, self.size, self.encoding, self.conn_name, self.schedule_name)

    def __iter__(self) -> 'strgen':
        """ The lines of the file's text, read one at a time, each without its line break.
        """
        pending = ''

        for chunk in self._text_chunks(_errors_strict):

            # Every line before the last line break read so far is complete ..
            pending += chunk
            lines = pending.split(_line_break)

            # .. while what follows that line break waits for the next chunk to complete it.
            pending = lines.pop()

            for line in lines:
                yield line

        # Whatever follows the last line break of the file is its last line.
        if pending:
            yield pending

# ################################################################################################################################

    @staticmethod
    def from_bytes(
        conn_type:'str',
        conn_name:'str',
        schedule_name:'str',
        directory:'str',
        file_name:'str',
        full_path:'str',
        last_modified:'str',
        data:'bytes',
        encoding:'str' = Default_Encoding,
        ) -> 'FileTransferItem':
        """ An item of a file whose bytes are already in memory - they are written to a spool file of their own.
        """
        spooled = spool_bytes(data)

        out = FileTransferItem(conn_type, conn_name, schedule_name, directory, file_name, full_path,
            spooled.size, last_modified, spooled.path, encoding)

        return out

# ################################################################################################################################

    @property
    def data(self) -> 'bytes':
        """ All the bytes of the file at once.
        """
        with self.open() as binary_file:
            out = binary_file.read()

        return out

# ################################################################################################################################

    @property
    def text(self) -> 'str':
        """ All the text of the file at once, read in the schedule's encoding.
        """
        out = ''.join(self._text_chunks(_errors_strict))
        return out

# ################################################################################################################################

    def open(self) -> 'binaryio_':
        """ The file's bytes as a binary file object, to be read in any way a file object is.
        """
        out = open(self.path, 'rb', buffering=Chunk_Size)
        return out

# ################################################################################################################################

    def _open_text(self, errors:'str') -> 'textio_':
        """ The file's text as a text file object, positioned after the byte order mark if the file opens with one.
        """
        out = open(self.path, 'r', encoding=self.encoding, errors=errors, buffering=Chunk_Size)

        # A text with no byte order mark is read from its first character again
        first_character = out.read(1)

        if first_character != _byte_order_mark:
            _ = out.seek(0)

        return out

# ################################################################################################################################

    def open_text(self) -> 'textio_':
        """ The file's text as a text file object in the schedule's encoding, e.g. for csv.reader.
        """
        out = self._open_text(_errors_strict)
        return out

# ################################################################################################################################

    def _text_chunks(self, errors:'str') -> 'strgen':
        """ The file's text, read a chunk at a time, with each line break of an EBCDIC encoding read as a line feed.
        """
        has_next_line = self.encoding in Encoding_Next_Line

        with self._open_text(errors) as text_file:
            while chunk := text_file.read(_text_chunk_size):
                if has_next_line:
                    chunk = chunk.replace(_next_line, _line_break)
                yield chunk

# ################################################################################################################################

    def chunks(self, size:'int' = Chunk_Size) -> 'bytesgen':
        """ The file's bytes, read the given number of bytes at a time.
        """
        with self.open() as binary_file:
            while chunk := binary_file.read(size):
                yield chunk

# ################################################################################################################################

    def records(self, terminator:'str') -> 'strgen':
        """ The file's text split on a terminator, e.g. the segments of an EDIFACT interchange split on an apostrophe,
        read one at a time. Line breaks around a record are not part of it and records that hold nothing else are skipped.
        """
        pending = ''

        for chunk in self._text_chunks(_errors_strict):

            # Everything up to the last terminator read so far is made of complete records ..
            pending += chunk
            parts = pending.split(terminator)

            # .. while what follows the last terminator waits for the next chunk to complete it.
            pending = parts.pop()

            for part in parts:
                record = part.strip(_line_break)
                if record:
                    yield record

        # Whatever follows the last terminator of the file is its last record.
        record = pending.strip(_line_break)

        if record:
            yield record

# ################################################################################################################################

    def head(self, size:'int' = Default_Head_Size) -> 'bytes':
        """ The first bytes of the file, e.g. to tell which format it is in.
        """
        with self.open() as binary_file:
            out = binary_file.read(size)

        return out

# ################################################################################################################################

    def close(self) -> 'None':
        """ Deletes the spool file once the service the file was handed to is done with it.
        """
        os.remove(self.path)

# ################################################################################################################################

    def to_dict(self) -> 'stranydict':
        """ The item as a JSON-friendly dict, which is what lets a service return the item it received
        as its response - the file's text is read in the schedule's encoding, size is still the byte count.
        """
        text = ''.join(self._text_chunks(_errors_replace))

        out:'stranydict' = {
            'conn_type': self.conn_type,
            'conn_name': self.conn_name,
            'schedule_name': self.schedule_name,
            'directory': self.directory,
            'file_name': self.file_name,
            'full_path': self.full_path,
            'size': self.size,
            'last_modified': self.last_modified,
            'encoding': self.encoding,
            'data': text,
        }
        return out

# ################################################################################################################################

    def documents(self) -> 'doclist':
        """ The documents this file carries - the file itself unless it is an archive, in which case each file inside,
        and each document the metadata names if the archive is an IHE XDM package.
        """
        from zato.common.documents.unpack import read_documents_from_path

        out = read_documents_from_path(self.path, file_name=self.file_name)
        return out

# ################################################################################################################################
# ################################################################################################################################
