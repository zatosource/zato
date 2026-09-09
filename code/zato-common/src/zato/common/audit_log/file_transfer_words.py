# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Labels and sentence templates for file transfer runs, shared by the server and the browser.

from __future__ import annotations

# Zato
from zato.common.audit_log.file_transfer_run import Decision_Failed, Decision_Quarantined, Decision_Skipped, Decision_Taken, \
    Phase_Acking, Phase_Checking_Directory, Phase_Claiming, Phase_Connecting, Phase_Delivering, Phase_Done, Phase_Listing, \
    Phase_Reading, Phase_Waiting, Run_Status_Clean, Run_Status_Empty, Run_Status_Failed, Run_Status_Interrupted, \
    Run_Status_List_Failed, Run_Status_No_Directory, Run_Status_Partial, Run_Status_Running, Run_Status_Unchanged, \
    Skip_Reason_Label

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, stranydict, strlist
    anydict = anydict
    stranydict = stranydict
    strlist = strlist

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
        'default_view_labels': Default_View_Labels,
    }

    return out

# ################################################################################################################################

def entries_text(entries:'int') -> 'str':
    """ The count of entries with its noun.
    """
    if entries == 1:
        out = Sentence_Template['entries_one']
    else:
        out = Sentence_Template['entries_many'].format(entries=entries)

    return out

# ################################################################################################################################

def _skip_count(item:'tuple') -> 'int':
    count = item[1]
    return count

# ################################################################################################################################

def skips_text(skip_reasons:'anydict') -> 'str':
    """ The skip reasons with their counts, most frequent first.
    """
    parts:'strlist' = []
    items = skip_reasons.items()
    ordered = sorted(items, key=_skip_count, reverse=True)

    for reason, count in ordered:
        if not (label := Skip_Reason_Label.get(reason)):
            label = reason

        part = Sentence_Template['skip_item'].format(count=count, reason=label)
        parts.append(part)

    out = ', '.join(parts)
    return out

# ################################################################################################################################

def _expected_suffix(data:'stranydict') -> 'str':
    """ The day's count against the schedule's expectation, empty without an expectation.
    """
    if not (expected_files := data.get('expected_files')):
        return ''

    if not data['expected_by']:
        return ''

    out = Sentence_Template['expected_suffix'].format(
        delivered_today=data['delivered_today'],
        expected_files=expected_files,
        expected_by=data['expected_by'],
    )

    return out

# ################################################################################################################################

def _running_sentence(data:'stranydict', status:'str', since_text:'str') -> 'str':
    """ The sentence of a run still going.
    """
    phase = data['phase']

    if not (phase_word := Phase_Label.get(phase)):
        phase_word = phase

    is_file_phase = phase in File_Phases

    if is_file_phase:
        if not (current_file := data.get('current_file')):
            current_file = ''

        if data['taken']:
            out = Sentence_Template['running_progress'].format(
                phase=phase_word, file=current_file, taken_so_far=data['taken_so_far'], taken=data['taken'])
        else:
            out = Sentence_Template['running_file'].format(phase=phase_word, file=current_file)

    else:
        out = Sentence_Template['running_plain'].format(phase=phase_word)

    return out

# ################################################################################################################################

def _list_failed_sentence(data:'stranydict', status:'str', since_text:'str') -> 'str':
    """ The sentence of a run that failed before listing its directory.
    """
    template = List_Failed_Phase_Template[data['phase']]
    out = template.format(directory=data['remote_path'], error=data['error'])

    return out

# ################################################################################################################################

def _no_directory_sentence(data:'stranydict', status:'str', since_text:'str') -> 'str':
    """ The sentence of a run whose directory does not exist.
    """
    out = Sentence_Template['no_directory'].format(directory=data['remote_path'])
    return out

# ################################################################################################################################

def _interrupted_sentence(data:'stranydict', status:'str', since_text:'str') -> 'str':
    """ The sentence of a run interrupted by a server stop.
    """
    if current_file := data.get('current_file'):
        phase = data['phase']

        if phase_word := Phase_Label.get(phase):
            phase_word = phase_word.lower()
        else:
            phase_word = phase

        out = Sentence_Template['interrupted_file'].format(phase=phase_word, file=current_file)
    else:
        out = Sentence_Template['interrupted_plain']

    return out

# ################################################################################################################################

def _unchanged_sentence(data:'stranydict', status:'str', since_text:'str') -> 'str':
    """ The sentence of a run that saw the same listing as the run before it.
    """
    out = Sentence_Template['unchanged'].format(directory=data['remote_path'], since=since_text)
    return out

# ################################################################################################################################

def _empty_sentence(data:'stranydict', status:'str', since_text:'str') -> 'str':
    """ The sentence of a run that took nothing.
    """
    directory = data['remote_path']
    entries = data['entries']

    if entries:
        skips = skips_text(data['skip_reasons'])
        entries_word = entries_text(entries)
        out = Sentence_Template['took_none'].format(entries=entries_word, directory=directory, skips=skips)
    else:
        out = Sentence_Template['empty_directory'].format(directory=directory)

    return out

# ################################################################################################################################

def _delivered_sentence(data:'stranydict', status:'str', since_text:'str') -> 'str':
    """ The sentence of a run that took files.
    """
    taken = data['taken']
    processed = data['processed']
    failed = data['failed']

    if not (failed_file := data.get('first_failed_file')):
        failed_file = ''

    if not (error := data.get('first_failed_error')):
        error = ''

    if status == Run_Status_Clean:
        if skipped := data['skipped']:
            out = Sentence_Template['clean_with_skips'].format(taken=taken, processed=processed, skipped=skipped)
        else:
            out = Sentence_Template['clean'].format(taken=taken, processed=processed)

    elif status == Run_Status_Partial:
        if error:
            out = Sentence_Template['partial_with_error'].format(
                taken=taken, processed=processed, failed=failed, failed_file=failed_file, error=error)
        else:
            out = Sentence_Template['partial'].format(
                taken=taken, processed=processed, failed=failed, failed_file=failed_file)

    else:
        if error:
            out = Sentence_Template['failed_with_error'].format(taken=taken, failed_file=failed_file, error=error)
        else:
            out = Sentence_Template['failed'].format(taken=taken, failed_file=failed_file)

    if quarantined := data.get('quarantined'):
        out += Sentence_Template['quarantined_suffix'].format(quarantined=quarantined)

    return out

# ################################################################################################################################

# The sentence function of each run status, the delivered statuses share one.
_sentence_by_status = {
    Run_Status_Running:      _running_sentence,
    Run_Status_List_Failed:  _list_failed_sentence,
    Run_Status_No_Directory: _no_directory_sentence,
    Run_Status_Interrupted:  _interrupted_sentence,
    Run_Status_Unchanged:    _unchanged_sentence,
    Run_Status_Empty:        _empty_sentence,
    Run_Status_Clean:        _delivered_sentence,
    Run_Status_Partial:      _delivered_sentence,
    Run_Status_Failed:       _delivered_sentence,
}

# ################################################################################################################################

def run_sentence(data:'stranydict', status:'str', since_text:'str'='') -> 'str':
    """ The sentence of a run, built from its data and status. The `since_text` is the already formatted
    time of the run an unchanged run repeats.
    """
    sentence = _sentence_by_status[status]
    out = sentence(data, status, since_text)
    out += _expected_suffix(data)

    return out

# ################################################################################################################################
# ################################################################################################################################
