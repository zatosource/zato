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
    from zato.common.typing_ import anydict, anydictnone, dictlist, strdict

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

def _column_conditions(table:'anydict', column:'anydict', filter_condition:'anydictnone') -> 'dictlist':
    """ Builds the condition list of one column, in row order, with the filter first.
    """
    out = []

    # The filter gates every column of the table ..
    if filter_condition:
        out.append(dict(filter_condition))

    # .. and each participating cell contributes one condition, in row order.
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

def compile_table(table:'anydict') -> 'strdict':
    """ Compiles a decision table into the rule documents the engine already runs.

    Each rule column becomes one document named after its number, so one column reads
    as one rule. Conditions within a column join with and, the filter is prepended
    to every column, and column 0 compiles to a rule that always fires and fires first.
    Statements travel with their documents. The table is expected to have passed
    validate_table before it is compiled.
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

    # .. and each column compiles into one document, column 0 first so it fires first.
    for column in sorted(table['columns'], key=_column_number):

        number = column['number']
        name = f'column_{number}'
        full_name = f'{ruleset_name}_{name}'

        conditions = _column_conditions(table, column, filter_condition)

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

        # The statement travels with the document so executions can return it.
        statement = column.get('statement')
        if statement:
            document['statement'] = dict(statement)

        out[full_name] = document

    return out

# ################################################################################################################################
# ################################################################################################################################
