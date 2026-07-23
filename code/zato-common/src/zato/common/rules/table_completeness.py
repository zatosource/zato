# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
from itertools import product

# Zato
from zato.common.rules.constraint_ops import constraint_covers, constraints_cover_domain
from zato.common.rules.constraints import ConstraintKind, Mode_Include
from zato.common.rules.table_checks import cell_constraint, column_cells, rule_columns

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist, strdict

# ################################################################################################################################
# ################################################################################################################################

# A set member renders as a bare word when it looks like one, else it is quoted.
_bare_word_pattern = re.compile(r'^[A-Za-z_]\w*$')

# ################################################################################################################################
# ################################################################################################################################

def _member_text(value:'str') -> 'str':
    """ How one text value reads inside a set cell - bare when it can be, quoted otherwise.
    """
    if _bare_word_pattern.match(value):
        out = value
    else:
        escaped = value.replace('\\', '\\\\')
        escaped = escaped.replace("'", "\\'")
        out = f"'{escaped}'"

    return out

# ################################################################################################################################

def _complement_text(alternatives:'dictlist') -> 'str':
    """ The cell text of everything the used alternatives leave out.

    Texts complement into a parseable not in cell and a single missing boolean into
    its bare word. Numeric leftovers have no single-cell form, so they read as a
    not (...) placeholder for the author to refine - the proposed column is a draft
    with empty actions anyway.
    """
    texts = []
    constraints = []

    for alternative in alternatives:
        texts.append(alternative['text'])
        constraints.append(alternative['constraint'])

    kinds = set()
    for constraint in constraints:
        kinds.add(constraint['kind'])

    # A missing boolean value has its own bare word ..
    if kinds == {ConstraintKind.Boolean}:
        used = set()
        for constraint in constraints:
            used |= constraint['values']

        missing = {True, False} - used
        if len(missing) == 1:
            out = 'true' if True in missing else 'false'
            return out

    # .. plain allowed-text sets complement into a not in cell ..
    if kinds == {ConstraintKind.Text}:
        all_include = True
        used = set()

        for constraint in constraints:
            if constraint['mode'] != Mode_Include:
                all_include = False
            else:
                used |= constraint['values']

        if all_include:
            members = []
            for value in sorted(used):
                members.append(_member_text(value))

            joined = ', '.join(members)
            out = f'not in {{{joined}}}'
            return out

    # .. and anything else is a placeholder the author has to refine.
    joined = ', '.join(texts)
    out = f'not ({joined})'
    return out

# ################################################################################################################################

def _row_alternatives(table:'anydict') -> 'anydict':
    """ Per row letter, the distinct cell texts used across the rule columns, each with its constraint.

    A row also gets a complement alternative for everything the used cells leave out,
    unless they provably cover the whole value space already.
    """

    # Our response to produce
    out = {}

    columns = rule_columns(table)

    for row in table['conditions']:
        letter = row['letter']

        alternatives = []
        seen = set()

        for column in columns:
            cells = column_cells(column, [row])
            cell_text = cells[letter]

            if not cell_text:
                continue

            if cell_text in seen:
                continue

            seen.add(cell_text)
            constraint = cell_constraint(cell_text)
            alternatives.append({'text': cell_text, 'constraint': constraint, 'is_other': False})

        # A row no column constrains adds nothing to the cross product.
        if not alternatives:
            continue

        # The complement is only needed when the used cells leave something out.
        constraints = []
        for alternative in alternatives:
            constraints.append(alternative['constraint'])

        is_covered = constraints_cover_domain(constraints)
        if is_covered is not True:
            text = _complement_text(alternatives)
            alternatives.append({'text': text, 'constraint': None, 'is_other': True})

        out[letter] = alternatives

    return out

# ################################################################################################################################

def _column_covers(cells:'strdict', combination:'dictlist') -> 'bool':
    """ Whether one column fires for every value in the given combination of alternatives.
    """
    for entry in combination:
        letter = entry['letter']
        alternative = entry['alternative']
        cell_text = cells[letter]

        # A blank cell covers whatever the row holds ..
        if not cell_text:
            continue

        # .. only a blank cell can cover the complement of everything used ..
        if alternative['is_other']:
            return False

        # .. a cell trivially covers its own alternative ..
        if cell_text == alternative['text']:
            continue

        # .. and otherwise coverage has to be provable from the constraints.
        constraint = cell_constraint(cell_text)
        if not constraint_covers(constraint, alternative['constraint']):
            return False

    return True

# ################################################################################################################################

def check_completeness(table:'anydict') -> 'anydict':
    """ Finds the combinations of condition values no rule column handles.

    The cross product runs over the distinct cell values used per row, plus the
    complement of what they leave out. Each missing combination comes back both as
    the plain cells mapping and as a proposed new column with those cells and
    deliberately empty actions - choosing the actions is the author's job.
    """

    # Our response to produce
    out = {'missing': [], 'proposed': []}

    alternatives_by_letter = _row_alternatives(table)
    if not alternatives_by_letter:
        return out

    columns = rule_columns(table)

    # Precompute every column's full cell row once.
    all_column_cells = []
    for column in columns:
        cells = column_cells(column, table['conditions'])
        all_column_cells.append(cells)

    # Proposed columns number up from just past the highest existing column.
    next_number = 0
    for column in table['columns']:
        if column['number'] > next_number:
            next_number = column['number']
    next_number += 1

    letters = list(alternatives_by_letter)
    per_letter_lists = []
    for letter in letters:
        per_letter_lists.append(alternatives_by_letter[letter])

    for chosen in product(*per_letter_lists):

        # Pair each chosen alternative with its row letter ..
        combination = []
        for index, alternative in enumerate(chosen):
            combination.append({'letter': letters[index], 'alternative': alternative})

        # .. a combination some column covers is handled ..
        for cells in all_column_cells:
            if _column_covers(cells, combination):
                break

        # .. and one no column covers is missing, so it becomes a proposal.
        else:
            missing_cells = {}
            for entry in combination:
                missing_cells[entry['letter']] = entry['alternative']['text']

            out['missing'].append({'cells': dict(missing_cells)})
            out['proposed'].append({'number': next_number, 'cells': dict(missing_cells), 'actions': {}})
            next_number += 1

    return out

# ################################################################################################################################
# ################################################################################################################################
