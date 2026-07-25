# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# typing-extensions
from typing_extensions import TypeAlias

# Zato
from zato.common.rule_engine.constraint_ops import constraint_covers, constraints_overlap
from zato.common.rule_engine.constraints import any_constraint, condition_constraint
from zato.common.rule_engine.table import parse_cell

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist, intlist, strdict

# ################################################################################################################################
# ################################################################################################################################

prepared_column_list:TypeAlias = list['PreparedColumn']

# ################################################################################################################################
# ################################################################################################################################

def cell_constraint(cell_text:'str') -> 'anydict':
    """ The value-space constraint one cell describes - a blank cell allows everything.
    """
    result = parse_cell(cell_text)

    if result.condition is None:
        out = any_constraint()
    else:
        out = condition_constraint(result.condition)

    return out

# ################################################################################################################################

def column_cells(column:'anydict', letters:'dictlist') -> 'strdict':
    """ The cell text per row letter of one column, blank for rows the column opts out of.
    """
    out = {}

    for row in letters:
        letter = row['letter']
        cell_text = column['cells'].get(letter)

        if cell_text is None:
            cell_text = ''

        cell_text = cell_text.strip()

        # A lone dash means the same thing as a blank cell.
        if cell_text == '-':
            cell_text = ''

        out[letter] = cell_text

    return out

# ################################################################################################################################

def rule_columns(table:'anydict') -> 'dictlist':
    """ The lettered rule columns in number order - column 0 is action-only so it stays out.
    """
    out = []

    for column in table['columns']:
        if column['number'] != 0:
            out.append(column)

    def _by_number(column:'anydict') -> 'int':
        number = column['number']
        return number

    out.sort(key=_by_number)
    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PreparedColumn:
    """ One rule column with its per-row cell text and value-space constraint already parsed.

    The conflict and subsumption checks below compare every column with every other one, so a cell
    parsed inside those loops would be parsed again for each of the column's partners. Parsing every
    cell once here keeps the work linear in the number of cells the table actually has.
    """

    number:      'int'
    actions:     'strdict'
    overrides:   'intlist'
    cells:       'strdict'
    constraints: 'anydict'

    def __init__(self, column:'anydict', letters:'dictlist') -> 'None':
        self.number = column['number']
        self.actions = column['actions']
        self.cells = column_cells(column, letters)
        self.constraints = {}

        # A column that overrides nothing leaves the key out of the document altogether.
        declared = column.get('overrides')
        if declared is None:
            declared = []
        self.overrides = declared

        for letter, cell_text in self.cells.items():
            self.constraints[letter] = cell_constraint(cell_text)

# ################################################################################################################################

def prepare_columns(table:'anydict') -> 'prepared_column_list':
    """ Every lettered rule column of a table, in number order, with its cells parsed once.
    """

    # Our response to produce
    out = []

    letters = table['conditions']

    for column in rule_columns(table):
        prepared = PreparedColumn(column, letters)
        out.append(prepared)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _columns_overlap(first:'PreparedColumn', second:'PreparedColumn', letters:'dictlist') -> 'bool':
    """ Whether some single input satisfies both columns' cells in every row.
    """
    for row in letters:
        letter = row['letter']

        if not constraints_overlap(first.constraints[letter], second.constraints[letter]):
            return False

    return True

# ################################################################################################################################

def _differing_targets(first:'PreparedColumn', second:'PreparedColumn') -> 'dictlist':
    """ The targets both columns assign, with different values.
    """
    out = []

    for target, first_value in first.actions.items():
        second_value = second.actions.get(target)

        if second_value is None:
            continue

        if first_value.strip() != second_value.strip():
            out.append(target)

    return out

# ################################################################################################################################

def check_conflicts(table:'anydict') -> 'anydict':
    """ Finds pairs of columns that can both fire for one input yet assign different values.

    A declared override resolves a conflict - the overriding column carries the numbers
    it overrides, an explicit declaration and never an execution ordering. Resolved
    pairs come back separately, as do override declarations naming unknown columns.
    """

    # Our response to produce
    out = {'conflicts': [], 'overridden': [], 'unknown_overrides': []}

    letters = table['conditions']
    columns = prepare_columns(table)

    # Gather the declared overrides first, checking they point at real columns.
    known_numbers = set()
    for column in table['columns']:
        known_numbers.add(column['number'])

    overrides = set()
    for column in columns:
        for number in column.overrides:
            if number in known_numbers:
                overrides.add((column.number, number))
            else:
                out['unknown_overrides'].append({'column': column.number, 'overrides': number})

    # Every pair of rule columns is checked once, lower number first.
    for first_index, first in enumerate(columns):
        for second in columns[first_index + 1:]:

            # Columns that cannot both fire never conflict ..
            if not _columns_overlap(first, second, letters):
                continue

            # .. nor do columns that agree on everything they both assign.
            targets = _differing_targets(first, second)
            if not targets:
                continue

            first_number = first.number
            second_number = second.number

            # A declared override resolves the pair, in either direction.
            if (first_number, second_number) in overrides:
                out['overridden'].append({'winner': first_number, 'loser': second_number})
            elif (second_number, first_number) in overrides:
                out['overridden'].append({'winner': second_number, 'loser': first_number})
            else:
                out['conflicts'].append({'first': first_number, 'second': second_number, 'targets': targets})

    return out

# ################################################################################################################################
# ################################################################################################################################

def column_covers_column(general:'PreparedColumn', specific:'PreparedColumn', letters:'dictlist') -> 'bool':
    """ Whether every input firing the specific column also fires the general one.
    """
    for row in letters:
        letter = row['letter']

        # Equal cells cover each other trivially ..
        if general.cells[letter] == specific.cells[letter]:
            continue

        # .. otherwise coverage has to be provable from the constraints.
        if not constraint_covers(general.constraints[letter], specific.constraints[letter]):
            return False

    return True

# ################################################################################################################################

def check_subsumption(table:'anydict') -> 'dictlist':
    """ Finds columns whose conditions another column already covers whole.

    Subsumption is always flagged, never tolerated - a narrower column under a more
    general one is a problem waiting to surface in a bigger table. Two equivalent
    columns come back once, with the lower number as the general one.
    """

    # Our response to produce
    out = []

    letters = table['conditions']
    columns = prepare_columns(table)

    for first_index, first in enumerate(columns):
        for second in columns[first_index + 1:]:

            first_covers = column_covers_column(first, second, letters)
            second_covers = column_covers_column(second, first, letters)

            if first_covers:
                out.append({'general': first.number, 'specific': second.number})
            elif second_covers:
                out.append({'general': second.number, 'specific': first.number})

    return out

# ################################################################################################################################
# ################################################################################################################################

def check_unreachable(table:'anydict') -> 'dictlist':
    """ Finds columns that can never fire because their own conditions contradict each other.

    Contradictions arise between the filter and a cell on the same subject, or between
    two condition rows sharing a subject - whenever their value spaces have nothing in common.
    """

    # Our response to produce
    out = []

    subjects_by_letter = {}
    for row in table['conditions']:
        subjects_by_letter[row['letter']] = row['subject']

    # The filter, when present, constrains its subject in every column.
    filter_ = table.get('filter')
    filter_constraint = None
    filter_subject = ''

    if filter_:
        filter_subject = filter_['subject']
        filter_constraint = cell_constraint(filter_['cell'])

    for column in prepare_columns(table):

        # Group this column's constraints by the subject they describe ..
        by_subject = {}

        if filter_constraint:
            by_subject[filter_subject] = [filter_constraint]

        for letter, cell_text in column.cells.items():

            if not cell_text:
                continue

            subject = subjects_by_letter[letter]
            constraint = column.constraints[letter]

            if subject not in by_subject:
                by_subject[subject] = []
            by_subject[subject].append(constraint)

        # .. and a subject whose constraints share no value makes the column unreachable.
        for subject, constraints in by_subject.items():

            is_reachable = True

            for first_index, first in enumerate(constraints):
                for second in constraints[first_index + 1:]:
                    if not constraints_overlap(first, second):
                        is_reachable = False

            if not is_reachable:
                out.append({'column': column.number, 'subject': subject})

    return out

# ################################################################################################################################
# ################################################################################################################################
