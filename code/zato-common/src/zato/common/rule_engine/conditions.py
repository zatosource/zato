# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re

# Zato
from zato.common.rule_engine.document import Arity, Comparator, Comparator_Aliases, Comparator_Arity, NodeKind
from zato.common.rule_engine.errors import Severity
from zato.common.rule_engine.tokens import find_top_level, has_top_level_parenthesis, parse_scalar, split_top_level

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anytuple, dictlist

# ################################################################################################################################
# ################################################################################################################################

class ErrorCode:
    """ Codes carried by structured parse errors, stable identifiers for editors and LLM self-correction.
    """
    Invoke_Block          = 'invoke_block'
    Content_Outside_Block = 'content_outside_block'
    Rule_Name_Invalid     = 'rule_name_invalid'
    Missing_Block         = 'missing_block'
    Parenthesis           = 'parenthesis'
    Bad_Condition         = 'bad_condition'
    Unknown_Comparator    = 'unknown_comparator'
    Wrong_Arity           = 'wrong_arity'
    Bad_Value             = 'bad_value'
    Missing_Joiner        = 'missing_joiner'
    Joiner_After_Last     = 'joiner_after_last'
    Bad_Assignment        = 'bad_assignment'

# ################################################################################################################################
# ################################################################################################################################

# Canonical comparators plus their symbol aliases, longest first so that longest-match wins.
def _build_comparator_candidates() -> 'anytuple':
    candidates = []

    # Collect the canonical names ..
    for name in Comparator_Arity:
        candidates.append((name, name))

    # .. add the symbol aliases ..
    for alias, name in Comparator_Aliases.items():
        candidates.append((alias, name))

    # .. and sort them longest first so is not one of matches before is not before is.
    def _by_length(candidate:'anytuple') -> 'int':
        return len(candidate[0])

    out = tuple(sorted(candidates, key=_by_length, reverse=True))
    return out

_comparator_candidates = _build_comparator_candidates()

# A condition line starts with its subject followed by whitespace.
_subject_pattern = re.compile(r'^([A-Za-z_][\w.]*)\s+(.*)$')

# ################################################################################################################################
# ################################################################################################################################

def new_error(rule:'str', block:'str', line:'int', field:'str', code:'str', message:'str') -> 'anydict':
    """ Builds a structured parse error - parse errors always block, so their severity is always error.
    """
    out = {
        'rule': rule,
        'block': block,
        'line': line,
        'field': field,
        'code': code,
        'message': message,
        'severity': Severity.Error,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

def parse_condition(text:'str', line:'int', rule_name:'str', errors:'dictlist') -> 'anydict | None':
    """ Parses a single condition line into a subject, canonical comparator and tagged value nodes.
    """

    # Parenthesized grouping is not part of the grammar - deeper logic becomes two rules ..
    if has_top_level_parenthesis(text):
        message = 'Parentheses are not allowed - split the logic into two rules instead'
        errors.append(new_error(rule_name, 'when', line, '', ErrorCode.Parenthesis, message))
        return None

    # .. the line has to start with a subject ..
    match = _subject_pattern.match(text)
    if not match:
        message = f'Expected a condition in the form of subject comparator value -> {text}'
        errors.append(new_error(rule_name, 'when', line, '', ErrorCode.Bad_Condition, message))
        return None

    subject = match.group(1)
    rest = match.group(2)

    # .. followed by a comparator, matched longest first ..
    for candidate, canonical in _comparator_candidates:
        if rest == candidate:
            comparator = canonical
            values_text = ''
            break
        if rest.startswith(candidate + ' '):
            comparator = canonical
            values_text = rest[len(candidate)+1:].strip()
            break
    else:
        message = f'Unknown comparator -> {rest}'
        errors.append(new_error(rule_name, 'when', line, subject, ErrorCode.Unknown_Comparator, message))
        return None

    # .. and by however many values that comparator expects.
    values = _parse_condition_values(comparator, values_text, line, rule_name, subject, errors)
    if values is None:
        return None

    out = {'subject': subject, 'comparator': comparator, 'values': values}
    return out

# ################################################################################################################################

def _parse_condition_values(
    comparator:'str',
    values_text:'str',
    line:'int',
    rule_name:'str',
    subject:'str',
    errors:'dictlist',
    ) -> 'dictlist | None':
    """ Parses the value part of a condition according to the comparator's arity.
    """
    arity = Comparator_Arity[comparator]

    # Comparators like is true take no values at all ..
    if arity == Arity.None_:
        if values_text:
            message = f'Comparator {comparator} takes no value -> {values_text}'
            errors.append(new_error(rule_name, 'when', line, subject, ErrorCode.Wrong_Arity, message))
            return None
        return []

    # .. is between takes exactly two, separated by the word and ..
    if arity == Arity.Two:
        out = _parse_between_values(comparator, values_text, line, rule_name, subject, errors)
        return out

    # .. membership comparators take one or more, comma-separated, optionally bracketed ..
    if arity == Arity.Many:
        out = _parse_membership_values(comparator, values_text, line, rule_name, subject, errors)
        return out

    # .. and everything else takes exactly one value.
    comma_index = find_top_level(values_text, ',')
    if comma_index != -1:
        message = f'Comparator {comparator} takes a single value -> {values_text}'
        errors.append(new_error(rule_name, 'when', line, subject, ErrorCode.Wrong_Arity, message))
        return None

    node = parse_scalar(values_text)
    if node is None:
        message = f'Not a recognized value -> {values_text}'
        errors.append(new_error(rule_name, 'when', line, subject, ErrorCode.Bad_Value, message))
        return None

    # A regex pattern has to be a quoted string, nothing else can be matched against.
    if comparator == Comparator.Matches:
        if node['kind'] != NodeKind.Literal or not isinstance(node['value'], str):
            message = f'The matches comparator needs a quoted pattern -> {values_text}'
            errors.append(new_error(rule_name, 'when', line, subject, ErrorCode.Bad_Value, message))
            return None

    return [node]

# ################################################################################################################################

def _parse_between_values(
    comparator:'str',
    values_text:'str',
    line:'int',
    rule_name:'str',
    subject:'str',
    errors:'dictlist',
    ) -> 'dictlist | None':
    """ Parses the two boundary values of an is between condition.
    """

    # The two boundaries are separated by the word and ..
    parts = re.split(r'\s+and\s+', values_text)
    part_count = len(parts)

    if part_count != 2:
        message = f'Comparator {comparator} takes two values separated by and -> {values_text}'
        errors.append(new_error(rule_name, 'when', line, subject, ErrorCode.Wrong_Arity, message))
        return None

    # .. and each boundary has to be a scalar.
    out = []
    for part in parts:
        node = parse_scalar(part)
        if node is None:
            message = f'Not a recognized value -> {part}'
            errors.append(new_error(rule_name, 'when', line, subject, ErrorCode.Bad_Value, message))
            return None
        out.append(node)

    return out

# ################################################################################################################################

def _parse_membership_values(
    comparator:'str',
    values_text:'str',
    line:'int',
    rule_name:'str',
    subject:'str',
    errors:'dictlist',
    ) -> 'dictlist | None':
    """ Parses the values of a membership condition - one or more scalars, comma-separated, optionally bracketed.
    """

    # Outer brackets are optional and carry no meaning of their own ..
    if values_text.startswith('[') and values_text.endswith(']'):
        values_text = values_text[1:-1].strip()

    if not values_text:
        message = f'Comparator {comparator} needs at least one value'
        errors.append(new_error(rule_name, 'when', line, subject, ErrorCode.Wrong_Arity, message))
        return None

    # .. and each comma-separated part has to be a scalar.
    out = []
    for part in split_top_level(values_text, ','):
        node = parse_scalar(part)
        if node is None:
            message = f'Not a recognized value -> {part}'
            errors.append(new_error(rule_name, 'when', line, subject, ErrorCode.Bad_Value, message))
            return None
        out.append(node)

    return out

# ################################################################################################################################
# ################################################################################################################################
