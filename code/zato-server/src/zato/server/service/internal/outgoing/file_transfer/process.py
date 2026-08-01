# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone
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

def _get_file_name(entry:'any_') -> 'str':
    """ Returns the base file name of a listing entry - SFTP listings return full paths
    while SMB ones return base names, and everything downstream needs the base name.
    """
    out = entry.name.rsplit('/', 1)[-1]
    return out

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
        names.append(_get_file_name(entry))

    for entry in entries:

        file_name = _get_file_name(entry)

        # Only files are picked up, never directories or symlinks ..
        if not entry.is_file:
            continue

        # .. files claimed by any consumer are someone else's business ..
        if file_name.endswith(_scheduler.Claim_Suffix):
            continue

        if is_marker_mode:

            # .. the markers themselves are never picked up ..
            if file_name.endswith(marker_suffix):
                continue

            # .. and an upload without its marker is not complete yet ..
            marker_name = file_name + marker_suffix
            if marker_name not in names:
                continue

        # .. everything else must still match the schedule's pattern.
        if not fnmatch(file_name, pattern):
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

        full_path = f'{directory}/{_get_file_name(entry)}'

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

def _get_move_destination(conn:'any_', move_directory:'str', file_name:'str') -> 'str':
    """ Returns the path a file is moved to once its target service is done with it - its own name
    unless the destination already holds something of that name, in which case the moment the file
    arrived is what tells this one from the one already there.
    """
    out = f'{move_directory}/{file_name}'

    # Nothing of that name is in the way so the file keeps its own ..
    if not conn.exists(out):
        return out

    # .. otherwise it is given a name that says when it turned up, so that a feed sending
    # .. one name every day leaves every day's file behind rather than only the last one.
    stamp = datetime.now(timezone.utc).strftime(_scheduler.Collision_Suffix_Format)

    out = f'{move_directory}/{file_name}.{stamp}'
    return out

# ################################################################################################################################

def _ack_one_file(
    conn,         # type: any_
    schedule,     # type: stranydict
    directory,    # type: str
    file_name,    # type: str
    full_path,    # type: str
    current_path, # type: str
    ) -> 'None':
    """ Puts a file that its target service accepted out of the way - it is either moved to the schedule's
    destination or deleted, either of which makes sure the next run never picks it up again.
    """
    if schedule['on_success'] == _scheduler.OnSuccess.Move:

        move_directory = f'{directory}/{schedule["move_directory"]}'

        # The destination directory is created on first use
        if not conn.exists(move_directory):
            _ = conn.create_directory(move_directory)

        destination = _get_move_destination(conn, move_directory, file_name)
        _ = conn.move(current_path, destination)

    else:
        _ = conn.delete_file(current_path)

    # In marker mode, the marker goes away together with its data file
    if schedule['ready_how'] == _scheduler.ReadyHow.Marker:
        marker_path = full_path + schedule['marker_suffix']
        _ = conn.delete_file(marker_path)

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

    file_name = _get_file_name(entry)
    full_path = f'{directory}/{file_name}'

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
        item = FileTransferItem(conn_type, conn_name, schedule['name'], directory, file_name, full_path,
            entry.size, entry.last_modified_iso, data)

        _ = service.invoke(schedule['service'], item)

    except Exception:

        # The file is rejected by leaving it in place - it will be picked up anew
        # on the next run, which means that files are never lost.
        service.logger.warning('Could not invoke `%s` with file `%s` from `%s` -> `%s`',
            schedule['service'], full_path, conn_name, format_exc())

        # A claimed file is renamed back so the next run, here or elsewhere, can take it again.
        # The file may be gone by now, e.g. another consumer took it, which is not our concern here.
        if current_path != full_path:
            try:
                _ = conn.move(current_path, full_path)
            except Exception:
                service.logger.info('Could not release the claim on `%s`', current_path)

        return

    # Everything succeeded so the file is acked. An ack that cannot go through - because the destination
    # will not take the file or because another run moved it away a moment earlier - concerns this one
    # file alone, so it is logged and the run carries on with the files behind it.
    try:
        _ack_one_file(conn, schedule, directory, file_name, full_path, current_path)
    except Exception:
        service.logger.warning('Could not put file `%s` out of the way after `%s` took it -> `%s`',
            full_path, schedule['service'], format_exc())

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

    # A directory that is not there yet, e.g. the partner has not created it, or one that went away
    # during maintenance, means there is nothing to do - exactly what an empty one means.
    if not conn.exists(directory):
        service.logger.info('Directory `%s` does not exist in `%s`, nothing to do', directory, conn_name)
        return

    # Look into the directory ..
    entries = conn.list(directory)

    # .. an empty one means there is nothing to do ..
    if not entries:
        return

    # .. keep only what the schedule may pick up ..
    candidates = _get_candidates(schedule, entries)

    # .. in stability mode, a file is ready only once it stops changing ..
    if schedule['ready_how'] == _scheduler.ReadyHow.Stability:
        candidates = _keep_stable_entries(conn, directory, candidates, schedule['stability_delay'])

    # .. and now each ready file can be handled on its own. One file that cannot be handled never ends
    # the run for the files behind it - the run is over only once every file has had its turn.
    for entry in candidates:
        try:
            _process_one_file(service, conn, context, schedule, directory, entry)
        except Exception:
            service.logger.warning('Could not handle file `%s` from `%s` -> `%s`',
                _get_file_name(entry), conn_name, format_exc())

# ################################################################################################################################
# ################################################################################################################################
