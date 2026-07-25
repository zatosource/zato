# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re

# Zato
from zato.common.rule_engine.document import Comparator
from zato.common.rule_engine.table import parse_cell, parse_cell_value
from zato.common.rule_engine.tokens import literal_node

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone, anylist, dictlist, strdict

# ################################################################################################################################
# ################################################################################################################################

def _slug(name:'str') -> 'str':
    """ Turns a table name into an identifier usable as a ruleset name.
    """
    out = re.sub(r'\W+', '_', name)
    out = out.strip('_')
    return out

# ################################################################################################################################

def _column_number(column:'anydict') -> 'int':
    out = column['number']
    return out

# ################################################################################################################################

def _always_true_condition() -> 'anydict':
    """ The condition a column without cells fires on - column 0 always fires.

    It compiles to `true == true`, an expression the engine matches against any input
    without touching the input at all, so no field ever has to exist for it.
    """
    out = {'subject': 'true', 'comparator': Comparator.Is, 'values': [literal_node(True)]}
    return out

# ################################################################################################################################

def _cell_conditions(table:'anydict', column:'anydict') -> 'dictlist':
    """ Builds the conditions one column's own cells contribute, in row order.
    """
    out = []

    for row in table['conditions']:
        letter = row['letter']
        cell_text = column['cells'].get(letter)

        if not cell_text:
            continue

        result = parse_cell(cell_text)
        if result.condition:
            condition = {'subject': row['subject']}
            condition.update(result.condition)
            out.append(condition)

    return out

# ################################################################################################################################

def _column_conditions(cell_conditions:'dictlist', filter_condition:'anydictnone') -> 'dictlist':
    """ Builds the condition list of one column, in row order, with the filter first.
    """
    out = []

    # The filter gates every column of the table ..
    if filter_condition:
        out.append(dict(filter_condition))

    # .. and then come the column's own cells.
    out.extend(cell_conditions)

    return out

# ################################################################################################################################

def _override_guards(table:'anydict', number:'int', cell_conditions_by_number:'anydict') -> 'anylist':
    """ Builds the negated guards that keep one column from firing while a column overriding it does.

    A column declares which other columns it overrides, so the guards of column N are the own
    conditions of every column that names N. They are the overriding column's cells only, without
    the table filter, because the filter already gates the guarded column itself.
    """
    out = []

    for other in table['columns']:
        other_number = other['number']

        # A column cannot override itself, so a self-reference guards nothing ..
        if other_number == number:
            continue

        # .. and a column that does not name this one leaves it alone.
        overrides = other.get('overrides')
        if not overrides:
            continue

        if number in overrides:
            guard = cell_conditions_by_number[other_number]

            # A column with no cells of its own always fires, and that is exactly what its
            # guard has to say, so it negates the same always-true condition such a column runs on.
            if not guard:
                guard = [_always_true_condition()]

            out.append(guard)

    return out

# ################################################################################################################################

def compile_table(table:'anydict') -> 'strdict':
    """ Compiles a decision table into the rule documents the engine already runs.

    Each rule column becomes one document named after its number, so one column reads
    as one rule. Conditions within a column join with and, the filter is prepended
    to every column, and column 0 compiles to a rule that always fires and fires first.
    A column another one declares itself to override compiles with that column's conditions
    as a negated guard, so a declared override decides what fires and not merely what the
    conflict report says. Statements travel with their documents. The table is expected to
    have passed validate_table before it is compiled.
    """

    # Our response to produce
    out = {}

    ruleset_name = _slug(table['name'])

    # The filter, when present, becomes the first condition of every column ..
    filter_condition = None
    filter_ = table.get('filter')
    if filter_:
        result = parse_cell(filter_['cell'])
        condition = result.condition

        # A table that passed validation always has a parseable, non-empty filter cell.
        if condition is None:
            raise Exception(f'Not a recognized filter cell -> `{filter_["cell"]}`')

        filter_condition = {'subject': filter_['subject']}
        filter_condition.update(condition)

    # .. every column's own cells are parsed once, because an overridden column needs
    # the conditions of the columns that override it, not only its own ..
    cell_conditions_by_number = {}

    for column in table['columns']:
        cell_conditions_by_number[column['number']] = _cell_conditions(table, column)

    # .. and each column compiles into one document, column 0 first so it fires first.
    for column in sorted(table['columns'], key=_column_number):

        number = column['number']
        name = f'column_{number}'
        full_name = f'{ruleset_name}_{name}'

        conditions = _column_conditions(cell_conditions_by_number[number], filter_condition)

        # A column without any conditions is column 0 without a filter - it always fires.
        if not conditions:
            conditions.append(_always_true_condition())

        joiners = ['and'] * (len(conditions) - 1)

        # Actions follow the action row order, skipping targets this column leaves alone.
        then = []
        for row in table['actions']:
            target = row['target']
            value_text = column['actions'].get(target)

            if not value_text:
                continue

            node = parse_cell_value(value_text)
            then.append({'target': target, 'value': node})

        document = {
            'name': name,
            'docs': '',
            'defaults': {},
            'conditions': conditions,
            'joiners': joiners,
            'then': then,
            'else': [],
            'ruleset_name': ruleset_name,
            'full_name': full_name,
        }

        # A column another one overrides carries one guard per overriding column, so it cannot
        # fire while any of them matches.
        guards = _override_guards(table, number, cell_conditions_by_number)
        if guards:
            document['unless'] = guards

        # The statement travels with the document so executions can return it.
        statement = column.get('statement')
        if statement:
            document['statement'] = dict(statement)

        out[full_name] = document

    return out

# ################################################################################################################################
# ################################################################################################################################
