# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from fnmatch import fnmatch
from traceback import format_exc

# gevent
from gevent import sleep

# Zato
from zato.common.api import FileTransfer
from zato.common.model.file_transfer_ import FileTransferItem

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strlist
    from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# ################################################################################################################################
# ################################################################################################################################

def _get_candidates(schedule:'stranydict', entries:'anylist') -> 'anylist':
    """ Returns the listing entries that a schedule may pick up - files matching the pattern,
    leaving out claim files, marker files and, in marker mode, uploads whose marker has not arrived yet.
    """

    # Our response to produce
    out:'anylist' = []

    # Local aliases
    pattern = schedule['pattern']
    is_marker_mode = schedule['ready_how'] == _scheduler.ReadyHow.Marker
    marker_suffix = schedule['marker_suffix']

    # Everything the directory holds, for the marker lookups below
    names:'strlist' = []

    for entry in entries:
        names.append(entry.name)

    for entry in entries:

        # Only files are picked up, never directories or symlinks ..
        if not entry.is_file:
            continue

        # .. files claimed by any consumer are someone else's business ..
        if entry.name.endswith(_scheduler.Claim_Suffix):
            continue

        if is_marker_mode:

            # .. the markers themselves are never picked up ..
            if entry.name.endswith(marker_suffix):
                continue

            # .. and an upload without its marker is not complete yet ..
            marker_name = entry.name + marker_suffix
            if marker_name not in names:
                continue

        # .. everything else must still match the schedule's pattern.
        if not fnmatch(entry.name, pattern):
            continue

        out.append(entry)

    return out

# ################################################################################################################################

def _keep_stable_entries(conn:'any_', directory:'str', candidates:'anylist', stability_delay:'int') -> 'anylist':
    """ Returns the candidates that did not change between the directory listing and a second look
    taken after the configured delay - an unchanged size and modification time means the upload is complete.
    """

    # Our response to produce
    out:'anylist' = []

    # One wait covers all the candidates - each one is then compared with its listing baseline
    sleep(stability_delay)

    for entry in candidates:

        full_path = f'{directory}/{entry.name}'

        # The file may be gone by now, e.g. another consumer took it
        try:
            info = conn.get_info(full_path)
        except Exception:
            continue

        if not info:
            continue

        # A change in size means the upload is still in progress ..
        if info.size != entry.size:
            continue

        # .. and so does a change in the modification time.
        if info.last_modified_iso != entry.last_modified_iso:
            continue

        out.append(entry)

    return out

# ################################################################################################################################

def _process_one_file(
    service,   # type: Service
    conn,      # type: any_
    context,   # type: stranydict
    schedule,  # type: stranydict
    directory, # type: str
    entry,     # type: any_
    ) -> 'None':
    """ Handles a single ready file - claims it if configured to, downloads it, invokes the target service
    and moves or deletes the file on success. A failure leaves the file in place for the next run.
    """

    # Local aliases
    conn_name = context[_scheduler.Extra_Conn_Name]
    conn_type = context[_scheduler.Extra_Conn_Type]

    full_path = f'{directory}/{entry.name}'

    # The path the file is read from - it changes if the file is claimed first
    current_path = full_path

    # With claiming on, the file is renamed before anything reads it, so another environment
    # watching the same directory never takes the same file. A failed rename means another
    # consumer claimed it first, which is not an error.
    if schedule['should_claim']:
        claim_path = full_path + _scheduler.Claim_Suffix
        try:
            _ = conn.move(full_path, claim_path)
        except Exception:
            service.logger.info('File `%s` already claimed by another consumer, skipping', full_path)
            return
        current_path = claim_path

    try:
        # Download the file ..
        data = conn.read(current_path)

        # .. and hand it over to the target service, once per file.
        item = FileTransferItem(conn_type, conn_name, schedule['name'], directory, entry.name, full_path,
            entry.size, entry.last_modified_iso, data)

        _ = service.invoke(schedule['service'], item)

    except Exception:

        # The file is rejected by leaving it in place - it will be picked up anew
        # on the next run, which means that files are never lost.
        service.logger.warning('Could not invoke `%s` with file `%s` from `%s` -> `%s`',
            schedule['service'], full_path, conn_name, format_exc())

        # A claimed file is renamed back so the next run, here or elsewhere, can take it again
        if current_path != full_path:
            _ = conn.move(current_path, full_path)

        return

    # Everything succeeded so the file is acked - it is either moved away or deleted,
    # ensuring it is never picked up twice.
    if schedule['on_success'] == _scheduler.OnSuccess.Move:

        move_directory = f'{directory}/{schedule["move_directory"]}'

        # The destination directory is created on first use
        if not conn.exists(move_directory):
            _ = conn.create_directory(move_directory)

        _ = conn.move(current_path, f'{move_directory}/{entry.name}')

    else:
        _ = conn.delete_file(current_path)

    # In marker mode, the marker goes away together with its data file
    if schedule['ready_how'] == _scheduler.ReadyHow.Marker:
        marker_path = full_path + schedule['marker_suffix']
        _ = conn.delete_file(marker_path)

# ################################################################################################################################

def process_files(service:'Service', context:'stranydict') -> 'None':
    """ One run of a file transfer schedule - looks into the schedule's directory and processes
    each file that is ready, invoking the target service once per file. The context is the extra data
    of the schedule's linked job, no matter if the invocation came from the scheduler or over HTTP.
    """

    # Local aliases
    conn_name = context[_scheduler.Extra_Conn_Name]
    conn_type = context[_scheduler.Extra_Conn_Type]
    schedule = context[_scheduler.Extra_Schedule]

    # The trailing slash, if any, would only get in the way of the path arithmetic below
    directory = schedule['directory'].rstrip('/')

    # Each connection type has its own facade on the service
    if conn_type == FileTransfer.ConnType.SFTP:
        conn = service.sftp[conn_name]
    else:
        conn = service.smb[conn_name]

    # Look into the directory ..
    entries = conn.list(directory)

    # .. an empty or missing directory means there is nothing to do ..
    if not entries:
        return

    # .. keep only what the schedule may pick up ..
    candidates = _get_candidates(schedule, entries)

    # .. in stability mode, a file is ready only once it stops changing ..
    if schedule['ready_how'] == _scheduler.ReadyHow.Stability:
        candidates = _keep_stable_entries(conn, directory, candidates, schedule['stability_delay'])

    # .. and now each ready file can be handled on its own.
    for entry in candidates:
        _process_one_file(service, conn, context, schedule, directory, entry)

# ################################################################################################################################
# ################################################################################################################################
