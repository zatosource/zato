# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone
from stat import S_ISDIR, S_ISLNK

# Zato
from zato.server.connection.file_transfer_base import EntryType, FileInfo, FileTransferConnection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class SMBConnection(FileTransferConnection):
    """ The public API of a single outgoing SMB connection, obtained via self.smb['My Connection'] in services.

    Remote paths always include the share name and use forward slashes, e.g. MyShare/documents/invoice.pdf.
    """

# ################################################################################################################################

    def _build_info(self, name:'str', stat_result:'any_') -> 'FileInfo':

        # Our response to produce
        out = FileInfo()

        # Map the mode bits to one of our entry types ..
        if S_ISLNK(stat_result.st_mode):
            entry_type = EntryType.symlink
        elif S_ISDIR(stat_result.st_mode):
            entry_type = EntryType.directory
        else:
            entry_type = EntryType.file

        # .. and populate everything before returning.
        out.type = entry_type
        out.name = name
        out.size = stat_result.st_size

        # The timestamp is made UTC-aware so it compares equal to what directory listings return -
        # their modification times come from the SMB protocol layer as UTC-aware datetime objects.
        out.last_modified = datetime.fromtimestamp(stat_result.st_mtime, tz=timezone.utc)

        return out

# ################################################################################################################################

    def _build_info_from_dir_entry(self, entry:'any_') -> 'FileInfo':

        # Our response to produce
        out = FileInfo()

        # Map the entry's attributes to one of our entry types ..
        if entry.is_symlink():
            entry_type = EntryType.symlink
        elif entry.is_dir():
            entry_type = EntryType.directory
        else:
            entry_type = EntryType.file

        # .. the size and modification time are already in the listing itself ..
        smb_info = entry.smb_info

        # .. and populate everything before returning.
        out.type = entry_type
        out.name = entry.name
        out.size = smb_info.end_of_file
        out.last_modified = smb_info.last_write_time

        return out

# ################################################################################################################################
# ################################################################################################################################
