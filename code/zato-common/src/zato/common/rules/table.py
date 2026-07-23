# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
from typing import NamedTuple

# Zato
from zato.common.rules.document import Comparator, NodeKind
from zato.common.rules.tokens import identifier_pattern, literal_node, parse_scalar
from zato.common.rules.vocabulary import ErrorCode, new_error

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone, anyset, dictlist, strdict, strset

# ################################################################################################################################
# ################################################################################################################################

class StatementSeverity:
    """ How strongly a rule statement speaks when its column fires.
    """
    Info      = 'info'
    Warning   = 'warning'
    Violation = 'violation'

# All the severities a rule statement may carry.
Statement_Severities = {StatementSeverity.Info, StatementSeverity.Warning, StatementSeverity.Violation}

# Condition rows are lettered a, b, c and so on - one lowercase letter each.
_letter_pattern = re.compile(r'^[a-z]$')

# Cell text may open with a comparator symbol - two-character symbols must be tried before one-character ones.
_cell_symbols = (
    ('==', Comparator.Is),
    ('!=', Comparator.Is_Not),
    ('<=', Comparator.Is_At_Most),
    ('>=', Comparator.Is_At_Least),
    ('=~', Comparator.Matches),
    ('<', Comparator.Is_Less_Than),
    ('>', Comparator.Is_More_Than),
)

# A cell with this text, or with no text at all, takes no part in its column.
_empty_cell = '-'

# ################################################################################################################################
# ################################################################################################################################

class CellParseResult(NamedTuple):
    """ What parsing one cell produced - a condition body, nothing at all, or an error message.
    """
    condition: 'anydictnone'
    error: 'str'

# ################################################################################################################################
# ################################################################################################################################

def parse_cell_value(text:'str') -> 'anydictnone':
    """ Parses one scalar in cell syntax into a tagged value node.

    Cells follow the zrules scalar syntax with one twist - a bare word without a dot
    is an enumeration text like Gold or MA, not a reference, because table authors
    write set members without quotes. A dotted bare word stays a reference to a term.
    """
    node = parse_scalar(text)

    if node is None:
        return None

    if node['kind'] == NodeKind.Reference:
        term = node['term']
        if '.' not in term:
            node = literal_node(term)

    return node

# ################################################################################################################################

def _split_keyword(text:'str', keyword:'str') -> 'str | None':
    """ Returns what follows a leading keyword, or None if the text does not start with that keyword.

    The keyword has to be a whole word - a cell like inactive must not read as the in keyword.
    """
    if not text.startswith(keyword):
        return None

    rest = text[len(keyword):]

    # The keyword alone, with nothing after it, is incomplete but still that keyword.
    if not rest:
        return ''

    # A whole word ends before whitespace or before the opening brace of a set.
    first_char = rest[0]
    if first_char not in (' ', '{'):
        return None

    out = rest.strip()
    return out

# ################################################################################################################################

def _parse_set(text:'str', comparator:'str') -> 'CellParseResult':
    """ Parses the {A, B, C} part of a set membership cell.
    """

    # The members have to be wrapped in braces ..
    has_braces = text.startswith('{')
    if has_braces:
        has_braces = text.endswith('}')

    if not has_braces:
        return CellParseResult(None, f'Set members need braces -> `{text}`')

    inner = text[1:-1].strip()
    if not inner:
        return CellParseResult(None, 'A set needs at least one member')

    # .. and each member has to be a scalar we recognize.
    values = []
    for part in inner.split(','):
        node = parse_cell_value(part.strip())
        if node is None:
            return CellParseResult(None, f'Not a recognized set member -> `{part.strip()}`')
        values.append(node)

    condition = {'comparator': comparator, 'values': values}
    out = CellParseResult(condition, '')
    return out

# ################################################################################################################################

def _parse_range(text:'str') -> 'CellParseResult':
    """ Parses a lower..upper range cell into an is-between condition body.
    """
    left, _, right = text.partition('..')

    lower = parse_cell_value(left.strip())
    upper = parse_cell_value(right.strip())

    if lower is None or upper is None:
        return CellParseResult(None, f'Not a recognized range -> `{text}`')

    condition = {'comparator': Comparator.Is_Between, 'values': [lower, upper]}
    out = CellParseResult(condition, '')
    return out

# ################################################################################################################################

def parse_cell(text:'str') -> 'CellParseResult':
    """ Parses the text of one condition cell into a condition body - a comparator with its values.

    The syntax is what table authors expect from a grid - 18..65 is a range,
    in {MA, NH, VT} is set membership, not in {..} is its negation, a leading
    symbol like >= applies that comparison, and a plain value means equality.
    An empty cell, or a lone dash, means the condition takes no part in that column.
    """
    text = text.strip()

    # A blank or dashed cell opts out of its column ..
    if not text:
        return CellParseResult(None, '')

    if text == _empty_cell:
        return CellParseResult(None, '')

    # .. negated set membership has to be tried before plain membership ..
    rest = _split_keyword(text, 'not in')
    if rest is not None:
        out = _parse_set(rest, Comparator.Is_Not_One_Of)
        return out

    rest = _split_keyword(text, 'in')
    if rest is not None:
        out = _parse_set(rest, Comparator.Is_One_Of)
        return out

    # .. a range never opens with a quote, so quoted text skips straight to the plain value case ..
    is_quoted = text.startswith(("'", '"', "d'"))
    if not is_quoted:
        if '..' in text:
            out = _parse_range(text)
            return out

    # .. a leading comparator symbol applies that comparison to what follows ..
    for symbol, comparator in _cell_symbols:
        if text.startswith(symbol):
            value_text = text[len(symbol):].strip()
            node = parse_cell_value(value_text)
            if node is None:
                return CellParseResult(None, f'Not a recognized value -> `{value_text}`')
            condition = {'comparator': comparator, 'values': [node]}
            return CellParseResult(condition, '')

    # .. and a plain value means equality.
    node = parse_cell_value(text)
    if node is None:
        return CellParseResult(None, f'Not a recognized cell -> `{text}`')

    condition = {'comparator': Comparator.Is, 'values': [node]}
    out = CellParseResult(condition, '')
    return out

# ################################################################################################################################
# ################################################################################################################################

def _check_condition_rows(table:'anydict', errors:'dictlist') -> 'strset':
    """ Checks the lettered condition rows and returns the set of valid letters.
    """
    letters = set()

    for row in table['conditions']:
        letter = row['letter']

        if not _letter_pattern.match(letter):
            errors.append(new_error('', 'table', letter, ErrorCode.Bad_Row, f'Row letters are single lowercase letters -> `{letter}`'))
            continue

        if letter in letters:
            errors.append(new_error('', 'table', letter, ErrorCode.Duplicate_Row, f'Row letter `{letter}` appears more than once'))
            continue

        letters.add(letter)

        subject = row['subject']
        if not identifier_pattern.match(subject):
            errors.append(new_error('', 'table', letter, ErrorCode.Bad_Row, f'Not a recognized subject -> `{subject}`'))

    return letters

# ################################################################################################################################

def _check_action_rows(table:'anydict', errors:'dictlist') -> 'strset':
    """ Checks the action rows and returns the set of valid targets.
    """
    targets = set()

    for row in table['actions']:
        target = row['target']

        if not identifier_pattern.match(target):
            errors.append(new_error('', 'table', target, ErrorCode.Bad_Row, f'Not a recognized target -> `{target}`'))
            continue

        if target in targets:
            errors.append(new_error('', 'table', target, ErrorCode.Duplicate_Row, f'Action target `{target}` appears more than once'))
            continue

        targets.add(target)

    return targets

# ################################################################################################################################

def _check_column(column:'anydict', letters:'strset', targets:'strset', numbers:'anyset', errors:'dictlist') -> 'None':
    """ Checks one rule column - its number, its cells, its actions and its statement.
    """
    number = column['number']
    rule = f'column_{number}'

    # Column numbers count up from zero, the action-only column ..
    is_valid_number = isinstance(number, int)
    if is_valid_number:
        is_valid_number = number >= 0

    if not is_valid_number:
        errors.append(new_error(rule, 'table', 'number', ErrorCode.Bad_Column, f'Column numbers count up from 0 -> `{number}`'))
        return

    if number in numbers:
        errors.append(new_error(rule, 'table', 'number', ErrorCode.Duplicate_Column, f'Column {number} appears more than once'))
        return

    numbers.add(number)

    # .. each cell has to sit in a known row and has to parse ..
    condition_count = 0

    for letter, cell_text in column['cells'].items():

        if letter not in letters:
            errors.append(new_error(rule, 'table', letter, ErrorCode.Bad_Cell, f'No condition row is lettered `{letter}`'))
            continue

        result = parse_cell(cell_text)
        if result.error:
            errors.append(new_error(rule, 'table', letter, ErrorCode.Bad_Cell, result.error))
            continue

        if result.condition:
            condition_count += 1

    # .. column 0 always fires so it never has conditions, while every other column needs at least one ..
    if number == 0:
        if condition_count:
            errors.append(new_error(rule, 'table', 'cells', ErrorCode.Bad_Column, 'Column 0 is action-only - it always fires and takes no conditions'))
    else:
        if not condition_count:
            errors.append(new_error(rule, 'table', 'cells', ErrorCode.Bad_Column, f'Column {number} has no conditions - action-only rules belong in column 0'))

    # .. each action cell has to name a known target and has to hold a value we recognize ..
    for target, value_text in column['actions'].items():

        if target not in targets:
            errors.append(new_error(rule, 'table', target, ErrorCode.Bad_Cell, f'No action row targets `{target}`'))
            continue

        node = parse_cell_value(value_text)
        if node is None:
            errors.append(new_error(rule, 'table', target, ErrorCode.Bad_Cell, f'Not a recognized value -> `{value_text}`'))

    # .. a column that assigns nothing does nothing when it fires ..
    if not column['actions']:
        errors.append(new_error(rule, 'table', 'actions', ErrorCode.Bad_Column, f'Column {number} assigns nothing'))

    # .. and the statement, when present, has to carry a known severity.
    statement = column.get('statement')
    if statement:
        severity = statement['severity']
        if severity not in Statement_Severities:
            errors.append(new_error(rule, 'table', 'statement', ErrorCode.Bad_Statement, f'Not a recognized severity -> `{severity}`'))

# ################################################################################################################################

def validate_table(table:'anydict') -> 'dictlist':
    """ Validates a decision table structurally, returning a list of findings shaped like the parser's errors.

    A valid table has uniquely lettered condition rows with recognizable subjects,
    uniquely targeted action rows, uniquely numbered columns whose cells parse and
    sit in known rows, an action-only column 0, and statements with known severities.
    """

    # Our response to produce
    errors = []

    letters = _check_condition_rows(table, errors)
    targets = _check_action_rows(table, errors)

    # The filter, when present, scopes the whole table so it has to parse like any cell ..
    filter_ = table.get('filter')
    if filter_:
        subject = filter_['subject']
        if not identifier_pattern.match(subject):
            errors.append(new_error('', 'table', 'filter', ErrorCode.Bad_Row, f'Not a recognized subject -> `{subject}`'))

        result = parse_cell(filter_['cell'])
        if result.error:
            errors.append(new_error('', 'table', 'filter', ErrorCode.Bad_Cell, result.error))
        elif result.condition is None:
            errors.append(new_error('', 'table', 'filter', ErrorCode.Bad_Cell, 'A filter cell cannot be empty'))

    # .. and each column is checked on its own.
    numbers = set()
    for column in table['columns']:
        _check_column(column, letters, targets, numbers, errors)

    return errors

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
