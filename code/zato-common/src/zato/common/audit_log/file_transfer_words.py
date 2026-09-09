# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Labels and sentence templates for file transfer runs, served to the browser, which builds the sentences.

from __future__ import annotations

# Zato
from zato.common.audit_log.file_transfer_run import Decision_Failed, Decision_Quarantined, Decision_Skipped, Decision_Taken, \
    Phase_Acking, Phase_Checking_Directory, Phase_Claiming, Phase_Connecting, Phase_Delivering, Phase_Done, Phase_Listing, \
    Phase_Reading, Phase_Waiting, Run_Status_Clean, Run_Status_Empty, Run_Status_Failed, Run_Status_Interrupted, \
    Run_Status_List_Failed, Run_Status_No_Directory, Run_Status_Partial, Run_Status_Running, Run_Status_Unchanged, \
    Skip_Reason_Label, Skip_Reason_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# The label of each run status.
Run_Status_Label = {
    Run_Status_Running:      'Running',
    Run_Status_Clean:        'Delivered',
    Run_Status_Partial:      'Partly delivered',
    Run_Status_Failed:       'Failed',
    Run_Status_Empty:        'Nothing to take',
    Run_Status_Unchanged:    'Nothing new',
    Run_Status_No_Directory: 'No directory',
    Run_Status_List_Failed:  'Unreachable',
    Run_Status_Interrupted:  'Interrupted',
}

# The tone of each run status.
Run_Status_Tone = {
    Run_Status_Running:      'running',
    Run_Status_Clean:        'good',
    Run_Status_Partial:      'bad',
    Run_Status_Failed:       'bad',
    Run_Status_Empty:        'neutral',
    Run_Status_Unchanged:    'muted',
    Run_Status_No_Directory: 'warn',
    Run_Status_List_Failed:  'bad',
    Run_Status_Interrupted:  'bad',
}

# The label of each phase, the file phases take the file's name after them.
Phase_Label = {
    Phase_Connecting:         'Connecting',
    Phase_Checking_Directory: 'Checking the directory',
    Phase_Listing:            'Listing the directory',
    Phase_Waiting:            'Waiting for files to settle',
    Phase_Claiming:           'Claiming',
    Phase_Reading:            'Reading',
    Phase_Delivering:         'Delivering',
    Phase_Acking:             'Putting away',
    Phase_Done:               'Done',
}

# The label of each ledger decision.
Decision_Label = {
    Decision_Taken:       'Taken',
    Decision_Skipped:     'Skipped',
    Decision_Failed:      'Failed',
    Decision_Quarantined: 'Quarantined',
}

# The tone of each ledger decision.
Decision_Tone = {
    Decision_Taken:       'good',
    Decision_Skipped:     'muted',
    Decision_Failed:      'bad',
    Decision_Quarantined: 'bad',
}

# The phases that are about one file.
File_Phases = [Phase_Claiming, Phase_Reading, Phase_Delivering, Phase_Acking]

# The template of each phase a run can fail in before listing its directory.
List_Failed_Phase_Template = {
    Phase_Connecting:         'Could not connect to reach {directory}: {error}',
    Phase_Checking_Directory: 'Could not check whether {directory} exists: {error}',
    Phase_Listing:            'Could not list {directory}: {error}',
}

# The sentence templates, filled from the run's data.
Sentence_Template = {
    'running_progress':      '{phase} {file}, {taken_so_far} of {taken}',
    'running_file':          '{phase} {file}',
    'running_plain':         '{phase}',
    'no_directory':          'Directory {directory} does not exist',
    'interrupted_file':      'Interrupted while {phase} {file}',
    'interrupted_plain':     'Interrupted before any file was read',
    'unchanged':             'Nothing new in {directory} since {since}',
    'empty_directory':       'Nothing in {directory}',
    'took_none':             'Saw {entries} in {directory}, took none - {skips}',
    'clean':                 'Took {taken}, delivered {processed}',
    'clean_with_skips':      'Took {taken}, delivered {processed}, {skipped} left behind',
    'partial':               'Took {taken}, delivered {processed}, {failed} failed - {failed_file}',
    'partial_with_error':    'Took {taken}, delivered {processed}, {failed} failed - {failed_file}, {error}',
    'failed':                'Took {taken}, none delivered - {failed_file}',
    'failed_with_error':     'Took {taken}, none delivered - {failed_file}, {error}',
    'quarantined_suffix':    ', {quarantined} quarantined',
    'expected_suffix':       ', {delivered_today} of {expected_files} expected by {expected_by}',
    'overdue_suffix_one':    ', 1 minute overdue',
    'overdue_suffix_many':   ', {overdue_minutes} minutes overdue',
    'skip_item':             '{count} {reason}',
    'entries_one':           '1 entry',
    'entries_many':          '{entries} entries',
    'store_verified':        'Stored {file}, {size}, verified in {verify_ms} ms',
    'store_unverified':      'Stored {file}, {size}, not verified - {error}',
    'store_verify_failed':   'Stored {file}, {size}, but the remote holds {remote_size}',
    'quarantined_file_one':  'Quarantined after 1 attempt - {error}',
    'quarantined_file_many': 'Quarantined after {attempts} attempts - {error}',
    'retried_file':          'Put back by {actor}',
    'attempt_of':            'attempt {attempt} of {max_attempts}',
    'attempt_plain':         'attempt {attempt}',
}

# The label of each data key shown on the default view.
Default_View_Labels = {
    'schedule':          'Schedule',
    'file_name':         'File',
    'remote_path':       'Directory',
    'endpoint':          'Remote path',
    'service':           'Service',
    'current_run':       'Run',
    'entries':           'Seen',
    'candidates':        'Matching',
    'taken':             'Taken',
    'processed':         'Delivered',
    'failed':            'Failed',
    'skipped':           'Skipped',
    'quarantined':       'Quarantined',
    'acked':             'Put away',
    'ack_failed':        'Not put away',
    'expected':          'Expected',
    'attempt':           'Attempt',
    'checksum':          'Checksum',
    'read_ms':           'Read',
    'service_ms':        'Service',
    'ack_ms':            'Put away in',
    'verify_ms':         'Verified in',
    'list_ms':           'Listing',
    'moved_to':          'Moved to',
    'deleted':           'Deleted',
    'seen_before':       'Same content',
    'handed_to':         'Handed to',
    'remote_size':       'Remote size',
    'verified':          'Verified',
    'quarantine_path':   'Quarantined at',
    'note':              'Note',
    'error':             'Error',
    'phase':             'Doing',
    'claim_released':    'Claim released',
    'delivered_today':   'Delivered today',
}

# ################################################################################################################################
# ################################################################################################################################

def file_transfer_words() -> 'anydict':
    """ The labels and templates as one dict for the browser.
    """
    out = {
        'run_status_label': Run_Status_Label,
        'run_status_tone': Run_Status_Tone,
        'phase_label': Phase_Label,
        'decision_label': Decision_Label,
        'decision_tone': Decision_Tone,
        'file_phases': File_Phases,
        'list_failed_phase_template': List_Failed_Phase_Template,
        'sentence_template': Sentence_Template,
        'skip_reason_label': Skip_Reason_Label,
        'skip_reason_name': Skip_Reason_Name,
        'default_view_labels': Default_View_Labels,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
