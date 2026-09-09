# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

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
    one instance per file.
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
        data:'bytes',
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
        self.data = data

    def __repr__(self) -> 'str':
        class_name = self.__class__.__name__
        self_id = hex(id(self))
        return '<{} at {}, full_path:`{}`, size:`{}`, conn_name:`{}`, schedule_name:`{}`>'.format(
            class_name, self_id, self.full_path, self.size, self.conn_name, self.schedule_name)

    def to_dict(self) -> 'stranydict':
        """ The item as a JSON-friendly dict, which is what lets a service return the item it received
        as its response - the file's bytes become text, size is still the byte count.
        """
        out:'stranydict' = {
            'conn_type': self.conn_type,
            'conn_name': self.conn_name,
            'schedule_name': self.schedule_name,
            'directory': self.directory,
            'file_name': self.file_name,
            'full_path': self.full_path,
            'size': self.size,
            'last_modified': self.last_modified,
            'data': self.data.decode('utf8', 'replace'),
        }
        return out

# ################################################################################################################################
# ################################################################################################################################
