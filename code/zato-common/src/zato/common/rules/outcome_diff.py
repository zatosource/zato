# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rules.testing import evaluate_input, load_documents

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

class OutcomeStatus:
    """ How one scenario compares between two rule versions.
    """
    Changed   = 'changed'
    Unchanged = 'unchanged'
    Error     = 'error'

# ################################################################################################################################

class ChangeStatus:
    """ How one outcome field compares between two rule versions.
    """
    Different = 'different'  # Both versions assign the field, with different values
    Added     = 'added'      # Only the new version assigns the field
    Removed   = 'removed'    # Only the old version assigns the field

# ################################################################################################################################
# ################################################################################################################################

def _field_changes(old_outcome:'anydict', new_outcome:'anydict') -> 'dictlist':
    """ Compares two outcomes field by field, reporting only what changed.
    """

    # Our response to produce
    out = []

    fields = set(old_outcome) | set(new_outcome)

    for field in sorted(fields):

        # A field only the old version assigned was removed ..
        if field not in new_outcome:
            entry = {'field': field, 'old': old_outcome[field], 'new': None, 'status': ChangeStatus.Removed}
            out.append(entry)

        # .. one only the new version assigned was added ..
        elif field not in old_outcome:
            entry = {'field': field, 'old': None, 'new': new_outcome[field], 'status': ChangeStatus.Added}
            out.append(entry)

        # .. and one both assigned changed only if the values differ.
        elif old_outcome[field] != new_outcome[field]:
            entry = {'field': field, 'old': old_outcome[field], 'new': new_outcome[field], 'status': ChangeStatus.Different}
            out.append(entry)

    return out

# ################################################################################################################################

def _fired_names(evaluated:'anydict') -> 'strlist':
    """ The full names of the rules one evaluation fired.
    """
    out = []
    for entry in evaluated['fired']:
        out.append(entry['rule'])

    return out

# ################################################################################################################################

def outcome_diff(old_documents:'anydict', new_documents:'anydict', scenarios:'dictlist') -> 'anydict':
    """ Replays every scenario against two rule versions and reports which decisions change.

    Each scenario comes back with its field-level changes and the per-rule attribution -
    the rules that fired in one version only are what explains every change. A scenario
    neither version can evaluate is an error entry, it never stops the whole replay.
    """
    old_loaded = load_documents(old_documents)
    new_loaded = load_documents(new_documents)

    results = []
    counts = {
        OutcomeStatus.Changed: 0,
        OutcomeStatus.Unchanged: 0,
        OutcomeStatus.Error: 0,
    }

    for scenario in scenarios:

        old_evaluated = evaluate_input(old_loaded, scenario['input'])
        new_evaluated = evaluate_input(new_loaded, scenario['input'])

        # An error on either side makes the comparison meaningless for this scenario ..
        error = old_evaluated['error']
        if not error:
            error = new_evaluated['error']

        if error:
            status = OutcomeStatus.Error
            changes = []
            fired_only_old = []
            fired_only_new = []

        # .. otherwise the decision changed exactly when some field changed.
        else:
            changes = _field_changes(old_evaluated['actual'], new_evaluated['actual'])
            status = OutcomeStatus.Changed if changes else OutcomeStatus.Unchanged

            # The rules firing in one version only are the why behind the changes.
            old_fired = _fired_names(old_evaluated)
            new_fired = _fired_names(new_evaluated)

            fired_only_old = sorted(set(old_fired) - set(new_fired))
            fired_only_new = sorted(set(new_fired) - set(old_fired))

        entry = {
            'scenario': scenario['name'],
            'status': status,
            'changes': changes,
            'fired_only_old': fired_only_old,
            'fired_only_new': fired_only_new,
            'error': error,
        }
        results.append(entry)
        counts[status] += 1

    # Our response to produce
    out = {
        'total': len(results),
        'changed': counts[OutcomeStatus.Changed],
        'unchanged': counts[OutcomeStatus.Unchanged],
        'errors': counts[OutcomeStatus.Error],
        'scenarios': results,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################
