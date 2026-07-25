# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.document import Comparator, NodeKind
from zato.common.rule_engine.table import Cell_Symbols, parse_cell

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class CellReading:
    """ How one cell reads back, which is what the grid speaks its sentences and its hints from.
    """
    # A cell that takes no part in its column.
    Any = 'any'

    # A lower..upper range.
    Range = 'range'

    # Set membership, plain or negated.
    Set = 'set'

    # One comparison against one value, which is also what a plain value means.
    Comparison = 'comparison'

    # Text the cell grammar does not read at all.
    Unreadable = 'unreadable'

# ################################################################################################################################

# Which symbol each comparator is written as in cell syntax - the reverse of what the parser uses.
_symbols_by_comparator = {}

for _symbol, _comparator in Cell_Symbols:
    _symbols_by_comparator[_comparator] = _symbol

# ################################################################################################################################
# ################################################################################################################################

def _value_of(node:'anydict') -> 'any_':
    """ The value one cell node carries, as the screens receive it.

    A literal keeps its own type, so a number stays a number and reads back with its
    thousands separators, and a reference reads back as the term it points to.
    """
    if node['kind'] == NodeKind.Reference:
        out = node['term']
    else:
        out = node['value']

    return out

# ################################################################################################################################

def cell_reading(text:'str') -> 'anydict':
    """ How one cell of a decision table reads back, out of the same parse the engine compiles from.

    This is the only reading of cell syntax there is - the screens no longer have one of
    their own, so a grammar change here cannot leave a sentence bar behind speaking the
    grammar of last year.
    """
    result = parse_cell(text)

    # A cell either parses, or opts out of its column, or holds text the grammar does not read ..
    if result.condition is None:
        if result.error:
            out = {'kind': CellReading.Unreadable, 'text': text.strip()}
        else:
            out = {'kind': CellReading.Any}
        return out

    comparator = result.condition['comparator']
    values = result.condition['values']

    # .. a range carries both of its ends ..
    if comparator == Comparator.Is_Between:
        out = {'kind': CellReading.Range, 'low': _value_of(values[0]), 'high': _value_of(values[1])}
        return out

    # .. set membership carries every member and whether the cell excludes them ..
    if comparator in (Comparator.Is_One_Of, Comparator.Is_Not_One_Of):
        items = []
        for node in values:
            items.append(_value_of(node))

        negated = comparator == Comparator.Is_Not_One_Of
        out = {'kind': CellReading.Set, 'items': items, 'negated': negated}
        return out

    # .. and everything else compares against one value, under the symbol that comparison
    # is written with, which is == for a cell that names the value on its own.
    symbol = _symbols_by_comparator[comparator]
    out = {'kind': CellReading.Comparison, 'symbol': symbol, 'value': _value_of(values[0])}
    return out

# ################################################################################################################################

def table_readings(table:'anydict') -> 'anydict':
    """ How every condition cell of one table reads back, by column number and condition letter.

    Columns are keyed by their number rather than by the label a screen shows, so the
    numbering is the only thing both sides have to agree on.
    """
    out = {}

    for column in table['columns']:
        readings = {}

        for letter, cell_text in column['cells'].items():
            readings[letter] = cell_reading(cell_text)

        out[str(column['number'])] = readings

    return out

# ################################################################################################################################
# ################################################################################################################################
