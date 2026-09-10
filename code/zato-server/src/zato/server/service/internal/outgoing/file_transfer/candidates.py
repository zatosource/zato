# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The selection of directory entries a run takes, with the reason for each entry it skips.

# stdlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from fnmatch import fnmatch

# gevent
from gevent import sleep

# Zato
from zato.common.api import FileTransfer
from zato.common.audit_log.file_transfer_run import Skip_Claim_File, Skip_Marker_File, Skip_Marker_Missing, \
    Skip_Mtime_Changed, Skip_Not_A_File, Skip_Pattern_Mismatch, Skip_Retry_Backoff, Skip_Size_Changed, Skip_Vanished
from zato.common.file_transfer.api import Retry_Backoff_Max

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Selection:
    """ The entries a selection step kept and the ones it skipped, each with its reason.
    """
    kept:    'anylist' = field(default_factory=list)
    skipped: 'anylist' = field(default_factory=list)

# ################################################################################################################################

    def skip(self, entry:'any_', reason:'str', next_attempt_iso:'str'='') -> 'None':
        self.skipped.append((entry, reason, next_attempt_iso))

# ################################################################################################################################
# ################################################################################################################################

def _new_selection() -> 'Selection':
    out = Selection()
    out.kept = []
    out.skipped = []

    return out

# ################################################################################################################################

def get_file_name(entry:'any_') -> 'str':
    """ Returns the base file name of a listing entry - SFTP listings return full paths
    while SMB and FTP ones return base names, and everything downstream needs the base name.
    """
    name = entry.name
    parts = name.rsplit('/', 1)
    out = parts[-1]
    return out

# ################################################################################################################################

def get_candidates(schedule:'stranydict', entries:'anylist') -> 'Selection':
    """ Splits the listing entries into the ones a schedule may pick up - files matching the pattern -
    and the ones it leaves alone: directories, claim files, marker files and, in marker mode,
    uploads whose marker has not arrived yet.
    """

    # Our response to produce
    out = _new_selection()

    # Local aliases
    pattern = schedule['pattern']
    is_marker_mode = schedule['ready_how'] == _scheduler.ReadyHow.Marker
    marker_suffix = schedule['marker_suffix']

    # Everything the directory holds, for the marker lookups below
    names:'strlist' = []

    for entry in entries:
        names.append(get_file_name(entry))

    for entry in entries:

        file_name = get_file_name(entry)

        # Only files are picked up, never directories or symlinks ..
        if not entry.is_file:
            out.skip(entry, Skip_Not_A_File)
            continue

        # .. files claimed by any consumer are someone else's business ..
        if file_name.endswith(_scheduler.Claim_Suffix):
            out.skip(entry, Skip_Claim_File)
            continue

        if is_marker_mode:

            # .. the markers themselves are never picked up ..
            if file_name.endswith(marker_suffix):
                out.skip(entry, Skip_Marker_File)
                continue

            # .. and an upload without its marker is not complete yet ..
            marker_name = file_name + marker_suffix
            if marker_name not in names:
                out.skip(entry, Skip_Marker_Missing)
                continue

        # .. everything else must still match the schedule's pattern.
        if not fnmatch(file_name, pattern):
            out.skip(entry, Skip_Pattern_Mismatch)
            continue

        out.kept.append(entry)

    return out

# ################################################################################################################################

def keep_stable_entries(conn:'any_', directory:'str', candidates:'anylist', stability_delay:'int') -> 'Selection':
    """ Keeps the candidates that did not change between the directory listing and a second look
    picked up after the configured delay - an unchanged size and modification time means the upload is complete.
    """

    # Our response to produce
    out = _new_selection()

    # One wait covers all the candidates - each one is then compared with its listing baseline.
    sleep(stability_delay)

    for entry in candidates:

        file_name = get_file_name(entry)
        full_path = f'{directory}/{file_name}'

        # The file may be gone by now, e.g. another consumer picked it up
        try:
            info = conn.get_info(full_path)
        except Exception:
            out.skip(entry, Skip_Vanished)
            continue

        # A change in size means the upload is still in progress ..
        if info.size != entry.size:
            out.skip(entry, Skip_Size_Changed)
            continue

        # .. and so does a change in the modification time.
        if info.last_modified_iso != entry.last_modified_iso:
            out.skip(entry, Skip_Mtime_Changed)
            continue

        out.kept.append(entry)

    return out

# ################################################################################################################################

def backoff_seconds(retry_backoff:'int', attempts:'int') -> 'int':
    """ The wait after the given number of failed attempts, doubling with each one up to Retry_Backoff_Max.
    """
    doubling = 2 ** (attempts - 1)
    wait = retry_backoff * doubling

    out = min(wait, Retry_Backoff_Max)
    return out

# ################################################################################################################################

def keep_entries_past_backoff(
    candidates:'anylist',
    memory:'anydict',
    retry_backoff:'int',
    now:'datetime',
    ) -> 'Selection':
    """ Keeps the candidates past their backoff wait, as (entry, attempt, first_failed_iso) triples.
    """

    # Our response to produce
    out = _new_selection()

    for entry in candidates:

        file_name = get_file_name(entry)

        # A file with no failures on record is on its first attempt ..
        if not (remembered := memory.get(file_name)):
            out.kept.append((entry, 1, ''))
            continue

        attempts = remembered['attempts']
        last_failed = datetime.fromisoformat(remembered['last_failed_iso'])

        wait = backoff_seconds(retry_backoff, attempts)
        next_attempt = last_failed + timedelta(seconds=wait)

        # .. one still inside its wait is left for a later run ..
        if now < next_attempt:
            next_attempt_iso = next_attempt.isoformat()
            out.skip(entry, Skip_Retry_Backoff, next_attempt_iso)
            continue

        # .. and one past it gets its next attempt.
        out.kept.append((entry, attempts + 1, remembered['first_failed_iso']))

    return out

# ################################################################################################################################
# ################################################################################################################################
