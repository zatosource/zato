# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone
from time import monotonic
from traceback import format_exc

# Zato
from zato.common.api import FileTransfer
from zato.common.audit_log.common import AuditEvent, AuditOutcome
from zato.common.audit_log.file_transfer import record_schedule_event

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import any_, stranydict
    from zato.server.service import Service
    from zato.server.service.internal.outgoing.file_transfer.run import RunContext

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# The delivered files whose ack failed, keyed by connection and schedule, each one mapping the path the file is under
# to its original path, its name and its cid. The next run of the schedule acks each such file before it lists the directory.
_failed_acks:'stranydict' = {}

# Milliseconds per second.
_ms_per_second = 1000

# ################################################################################################################################
# ################################################################################################################################

def elapsed_ms(start:'float') -> 'int':
    elapsed = monotonic() - start
    out = int(elapsed * _ms_per_second)
    return out

# ################################################################################################################################

def _get_move_destination(conn:'any_', move_directory:'str', file_name:'str') -> 'str':
    """ The destination path of a moved file, with a timestamp suffix if the name is already taken.
    """
    out = f'{move_directory}/{file_name}'

    # The name is free ..
    if not conn.exists(out):
        return out

    # .. or it is taken and the file is given a timestamp suffix.
    now = datetime.now(timezone.utc)
    stamp = now.strftime(_scheduler.Collision_Suffix_Format)

    out = f'{move_directory}/{file_name}.{stamp}'
    return out

# ################################################################################################################################

def resolve_subdirectory(directory:'str', subdirectory:'str') -> 'str':
    """ The subdirectory as an absolute path, relative ones are under the directory.
    """
    if subdirectory.startswith('/'):
        out = subdirectory
    else:
        out = f'{directory}/{subdirectory}'

    return out

# ################################################################################################################################

def move_out_of_the_way(
    conn:'any_',
    run:'RunContext',
    destination_directory:'str',
    file_name:'str',
    current_path:'str',
    ) -> 'str':
    """ Moves a file into the directory, creating the directory if needed, and returns the new path.
    """

    # The directory is created once per run, and creating one that exists already is not an error
    if destination_directory not in run.ensured_directories:
        _ = conn.create_directory(destination_directory, exist_ok=True)
        run.ensured_directories.add(destination_directory)

    out = _get_move_destination(conn, destination_directory, file_name)
    _ = conn.move(current_path, out)

    return out

# ################################################################################################################################

def ack_one_file(
    conn:'any_',
    run:'RunContext',
    schedule:'stranydict',
    directory:'str',
    file_name:'str',
    full_path:'str',
    current_path:'str',
    ) -> 'str':
    """ Moves or deletes a delivered file and returns the path it was moved to, empty if deleted.
    """

    # Our response to produce
    out = ''

    if schedule['on_success'] == _scheduler.OnSuccess.Move:
        move_directory = resolve_subdirectory(directory, schedule['move_directory'])
        out = move_out_of_the_way(conn, run, move_directory, file_name, current_path)
    else:
        _ = conn.delete_file(current_path)

    # In marker mode, the marker is deleted with its file.
    if schedule['ready_how'] == _scheduler.ReadyHow.Marker:
        marker_path = full_path + schedule['marker_suffix']
        _ = conn.delete_file(marker_path)

    return out

# ################################################################################################################################

def record_acked(
    audit_log:'AuditLog',
    conn_name:'str',
    schedule:'stranydict',
    full_path:'str',
    file_name:'str',
    file_cid:'str',
    run:'RunContext',
    destination:'str',
    ack_ms:'int',
    ) -> 'None':
    """ Records in the audit log what the ack of a delivered file did with it.
    """
    if destination:
        acked:'stranydict' = {'moved_to': destination}
    else:
        acked = {'deleted': True}

    acked['ack_ms'] = ack_ms
    attrs_extra = {'current_run': run.data['current_run']}

    _ = record_schedule_event(audit_log, conn_name, AuditEvent.File_Acked, full_path,
        cid=file_cid, correl_id=run.run_cid, schedule=schedule['name'], outcome=AuditOutcome.OK,
        file_name=file_name, service=schedule['service'], duration_ms=ack_ms, extra=acked, attrs_extra=attrs_extra)

# ################################################################################################################################

def note_failed_ack(conn_name:'str', schedule_name:'str', full_path:'str', file_name:'str', file_cid:'str',
    current_path:'str') -> 'None':
    """ Remembers a delivered file whose ack failed, so that the next run of the schedule acks it.
    """
    failed_key = f'{conn_name}.{schedule_name}'
    failed_acks = _failed_acks.setdefault(failed_key, {})

    failed_acks[current_path] = {
        'full_path': full_path,
        'file_name': file_name,
        'file_cid': file_cid,
    }

# ################################################################################################################################

def retry_failed_acks(
    service:'Service',
    conn:'any_',
    conn_name:'str',
    schedule:'stranydict',
    directory:'str',
    run:'RunContext',
    ) -> 'None':
    """ Acks each file that an earlier run of the schedule delivered without acking it, so that the file is neither
    left under its claim name nor delivered again.
    """
    failed_key = f'{conn_name}.{schedule["name"]}'

    if failed_key not in _failed_acks:
        return

    failed_acks = _failed_acks[failed_key]
    audit_log:'AuditLog' = conn.wrapper.audit_log

    for current_path, failed in list(failed_acks.items()):

        full_path = failed['full_path']
        file_name = failed['file_name']
        ack_start = monotonic()

        # A file that is no longer under that path was acked by the earlier attempt after all ..
        try:
            if conn.exists(current_path):
                destination = ack_one_file(conn, run, schedule, directory, file_name, full_path, current_path)
                ack_ms = elapsed_ms(ack_start)
                record_acked(audit_log, conn_name, schedule, full_path, file_name, failed['file_cid'], run,
                    destination, ack_ms)

        # .. and a remote end that is still unreachable leaves the ack to the next run.
        except Exception:
            service.logger.info('Could not ack `%s` again -> `%s`', current_path, format_exc())
            continue

        del failed_acks[current_path]

# ################################################################################################################################
# ################################################################################################################################
