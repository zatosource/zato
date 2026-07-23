# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from itertools import product

# Zato
from zato.common.rule_engine.document import Comparator, NodeKind
from zato.common.rule_engine.render import render_value
from zato.common.rule_engine.table import parse_cell
from zato.common.rule_engine.table_checks import column_cells, rule_columns

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone, dictlist, dictnone

# ################################################################################################################################
# ################################################################################################################################

def _cell_value_nodes(cell_text:'str') -> 'dictnone':
    """ The literal value nodes of an equality or membership cell, or None for any other cell.

    Only cells over plain literal values take part in expand and compress - references
    would change meaning when rewritten through a set.
    """
    result = parse_cell(cell_text)
    condition = result.condition

    if condition is None:
        return None

    comparator = condition['comparator']
    if comparator not in (Comparator.Is, Comparator.Is_One_Of):
        return None

    for node in condition['values']:
        if node['kind'] != NodeKind.Literal:
            return None

    out = {'values': condition['values']}
    return out

# ################################################################################################################################

def expand_column(table:'anydict', column:'anydict') -> 'dictlist':
    """ Expands one column into its dotted sub-rules, one per value a multi-value cell holds.

    A column whose cells all hold single values comes back as itself. Sub-rules number
    as 2.1, 2.2 and so on, each showing one logical possibility the engine derives.
    Numbers come back as texts either way, since a dotted number is not an integer.
    """
    number = column['number']

    # Per row, the single-value variants this column's cell expands into.
    variant_rows = []

    for row in table['conditions']:
        letter = row['letter']
        cell_text = column['cells'].get(letter)

        if not cell_text:
            continue

        wrapper = _cell_value_nodes(cell_text)

        # Cells that do not expand keep their text as the only variant ..
        if wrapper is None:
            variant_rows.append([{'letter': letter, 'text': cell_text}])
            continue

        values = wrapper['values']
        if len(values) == 1:
            variant_rows.append([{'letter': letter, 'text': cell_text}])
            continue

        # .. and a multi-value cell contributes one variant per value.
        variants = []
        for node in values:
            text = render_value(node)
            variants.append({'letter': letter, 'text': text})

        variant_rows.append(variants)

    # A column with nothing to expand is its own only form.
    combinations = list(product(*variant_rows))
    if len(combinations) == 1:
        out = [dict(column, number=str(number))]
        return out

    out = []
    for index, combination in enumerate(combinations, 1):

        cells = {}
        for variant in combination:
            cells[variant['letter']] = variant['text']

        sub_column = dict(column)
        sub_column['number'] = f'{number}.{index}'
        sub_column['cells'] = cells
        out.append(sub_column)

    return out

# ################################################################################################################################

def expand_table(table:'anydict') -> 'dictlist':
    """ Expands every rule column of a table into its dotted sub-rules.
    """

    # Our response to produce
    out = []

    for column in rule_columns(table):
        expanded = expand_column(table, column)
        out.extend(expanded)

    return out

# ################################################################################################################################

def _merge_pair(first:'anydict', second:'anydict', letters:'dictlist') -> 'anydictnone':
    """ Merges two columns into one when they differ in exactly one row, or returns None.

    Mergeable columns assign the same actions and their differing cells both hold
    plain values, which union into one membership cell.
    """

    # Only columns with the same actions can be one rule ..
    if first['actions'] != second['actions']:
        return None

    first_cells = column_cells(first, letters)
    second_cells = column_cells(second, letters)

    # .. and they have to differ in exactly one row.
    differing = []
    for row in letters:
        letter = row['letter']
        if first_cells[letter] != second_cells[letter]:
            differing.append(letter)

    if len(differing) != 1:
        return None

    letter = differing[0]

    first_wrapper = _cell_value_nodes(first_cells[letter])
    second_wrapper = _cell_value_nodes(second_cells[letter])

    if first_wrapper is None or second_wrapper is None:
        return None

    # The merged cell unions both value lists, keeping their order and dropping repeats.
    members = []
    seen = set()

    for node in first_wrapper['values'] + second_wrapper['values']:
        text = render_value(node)
        if text in seen:
            continue
        seen.add(text)
        members.append(text)

    joined = ', '.join(members)

    out = dict(first)
    out['cells'] = dict(first['cells'])
    out['cells'][letter] = f'in {{{joined}}}'
    return out

# ################################################################################################################################

def compress_table(table:'anydict') -> 'anydict':
    """ The inverse of expand - merges columns differing in one row into membership cells.

    Merging repeats until nothing merges anymore, then the rule columns renumber
    from 1 in their surviving order, with column 0 untouched.
    """
    letters = table['conditions']
    columns = rule_columns(table)

    # Keep merging the first mergeable pair until a full pass finds none.
    merged_any = True
    while merged_any:
        merged_any = False

        for first_index, first in enumerate(columns):
            for second_index in range(first_index + 1, len(columns)):
                second = columns[second_index]

                merged = _merge_pair(first, second, letters)
                if merged is None:
                    continue

                columns[first_index] = merged
                del columns[second_index]
                merged_any = True
                break

            if merged_any:
                break

    # The survivors renumber from 1 in order, after column 0 when the table has one.
    out = dict(table)
    new_columns = []

    for column in table['columns']:
        if column['number'] == 0:
            new_columns.append(column)

    for index, column in enumerate(columns, 1):
        renumbered = dict(column)
        renumbered['number'] = index
        new_columns.append(renumbered)

    out['columns'] = new_columns
    return out

# ################################################################################################################################
# ################################################################################################################################
