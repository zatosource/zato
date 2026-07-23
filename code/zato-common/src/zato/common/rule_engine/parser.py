# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
from logging import getLogger

# Zato
from zato.common.rule_engine.document import Arity, Comparator, Comparator_Aliases, Comparator_Arity, NodeKind
from zato.common.rule_engine.errors import Severity
from zato.common.rule_engine.tokens import find_top_level, has_top_level_parenthesis, identifier_pattern, parse_scalar, \
    parse_value, rule_name_pattern, split_top_level, strip_comment
from zato.common.util.open_ import open_r
from zato.common.util.sorted_dict import SortedDict

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import anydict, anylist, anytuple, dictlist, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

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

# The block keywords a rule is made of, each on its own line in the text form.
_block_names = {'rule', 'docs', 'defaults', 'when', 'then', 'else'}

# Blocks every rule must have.
_required_blocks = ('rule', 'when', 'then')

# The joiner keywords accepted between conditions.
_joiner_names = ('and', 'or')

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

def _new_error(rule:'str', block:'str', line:'int', field:'str', code:'str', message:'str') -> 'anydict':
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

def _parse_condition(text:'str', line:'int', rule_name:'str', errors:'dictlist') -> 'anydict | None':
    """ Parses a single condition line into a subject, canonical comparator and tagged value nodes.
    """

    # Parenthesized grouping is not part of the grammar - deeper logic becomes two rules ..
    if has_top_level_parenthesis(text):
        message = 'Parentheses are not allowed - split the logic into two rules instead'
        errors.append(_new_error(rule_name, 'when', line, '', ErrorCode.Parenthesis, message))
        return None

    # .. the line has to start with a subject ..
    match = _subject_pattern.match(text)
    if not match:
        message = f'Expected a condition in the form of subject comparator value -> {text}'
        errors.append(_new_error(rule_name, 'when', line, '', ErrorCode.Bad_Condition, message))
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
        errors.append(_new_error(rule_name, 'when', line, subject, ErrorCode.Unknown_Comparator, message))
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
            errors.append(_new_error(rule_name, 'when', line, subject, ErrorCode.Wrong_Arity, message))
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
        errors.append(_new_error(rule_name, 'when', line, subject, ErrorCode.Wrong_Arity, message))
        return None

    node = parse_scalar(values_text)
    if node is None:
        message = f'Not a recognized value -> {values_text}'
        errors.append(_new_error(rule_name, 'when', line, subject, ErrorCode.Bad_Value, message))
        return None

    # A regex pattern has to be a quoted string, nothing else can be matched against.
    if comparator == Comparator.Matches:
        if node['kind'] != NodeKind.Literal or not isinstance(node['value'], str):
            message = f'The matches comparator needs a quoted pattern -> {values_text}'
            errors.append(_new_error(rule_name, 'when', line, subject, ErrorCode.Bad_Value, message))
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
        errors.append(_new_error(rule_name, 'when', line, subject, ErrorCode.Wrong_Arity, message))
        return None

    # .. and each boundary has to be a scalar.
    out = []
    for part in parts:
        node = parse_scalar(part)
        if node is None:
            message = f'Not a recognized value -> {part}'
            errors.append(_new_error(rule_name, 'when', line, subject, ErrorCode.Bad_Value, message))
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
        errors.append(_new_error(rule_name, 'when', line, subject, ErrorCode.Wrong_Arity, message))
        return None

    # .. and each comma-separated part has to be a scalar.
    out = []
    for part in split_top_level(values_text, ','):
        node = parse_scalar(part)
        if node is None:
            message = f'Not a recognized value -> {part}'
            errors.append(_new_error(rule_name, 'when', line, subject, ErrorCode.Bad_Value, message))
            return None
        out.append(node)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _parse_when(lines:'anylist', rule_name:'str', errors:'dictlist') -> 'anytuple':
    """ Parses the when block into a list of conditions and the joiners between them.
    """
    conditions = []
    joiners = []
    last_index = len(lines) - 1

    for index, (line, text) in enumerate(lines):

        # Each line except the last carries a trailing joiner ..
        joiner = ''
        for candidate in _joiner_names:
            if text.endswith(' ' + candidate):
                joiner = candidate
                text = text[:-len(candidate)-1].strip()
                break

        # .. a missing or excess joiner is reported but parsing continues ..
        if index < last_index:
            if not joiner:
                message = 'Expected the line to end with and or or'
                errors.append(_new_error(rule_name, 'when', line, '', ErrorCode.Missing_Joiner, message))
        else:
            if joiner:
                message = f'The last condition must not end with a joiner -> {joiner}'
                errors.append(_new_error(rule_name, 'when', line, '', ErrorCode.Joiner_After_Last, message))
                joiner = ''

        # .. and the line itself is a single condition.
        condition = _parse_condition(text, line, rule_name, errors)
        if condition:
            conditions.append(condition)
            if joiner:
                joiners.append(joiner)

    out = (conditions, joiners)
    return out

# ################################################################################################################################

def _reject_references(node:'anydict', text:'str', line:'int', rule_name:'str', errors:'dictlist') -> 'bool':
    """ Returns True if the node holds no references, reporting an error otherwise - defaults must be concrete.
    """
    if node['kind'] == NodeKind.Reference:
        message = f'Defaults must be concrete values, not references -> {text}'
        errors.append(_new_error(rule_name, 'defaults', line, '', ErrorCode.Bad_Value, message))
        return False

    if node['kind'] == NodeKind.List:
        for item in node['items']:
            if not _reject_references(item, text, line, rule_name, errors):
                return False

    return True

# ################################################################################################################################

def _parse_assignments(lines:'anylist', block:'str', rule_name:'str', errors:'dictlist') -> 'dictlist':
    """ Parses target = value lines into a list of target and node pairs.
    """
    out = []

    for line, text in lines:

        # Each line is a single assignment ..
        equals_index = find_top_level(text, '=')
        if equals_index == -1:
            message = f'Expected an assignment in the form of target = value -> {text}'
            errors.append(_new_error(rule_name, block, line, '', ErrorCode.Bad_Assignment, message))
            continue

        # .. whose target is an identifier ..
        target = text[:equals_index].strip()
        if not identifier_pattern.match(target):
            message = f'Not a valid assignment target -> {target}'
            errors.append(_new_error(rule_name, block, line, target, ErrorCode.Bad_Assignment, message))
            continue

        # .. and whose value is a tagged node.
        value_text = text[equals_index+1:].strip()
        node = parse_value(value_text)
        if node is None:
            message = f'Not a recognized value -> {value_text}'
            errors.append(_new_error(rule_name, block, line, target, ErrorCode.Bad_Value, message))
            continue

        # Defaults have to be self-contained, they cannot point to other terms.
        if block == 'defaults':
            if not _reject_references(node, value_text, line, rule_name, errors):
                continue

        out.append({'target': target, 'value': node})

    return out

# ################################################################################################################################
# ################################################################################################################################

def _build_document(blocks:'anydict', ruleset_name:'str', errors:'dictlist') -> 'anydict | None':
    """ Builds a rule document out of the blocks collected for one rule.
    """

    # The rule's name is the single line of its rule block ..
    name_lines = blocks['rule']
    if len(name_lines) != 1:
        message = 'The rule block must contain exactly one line, the rule name'
        errors.append(_new_error('', 'rule', blocks['rule_line'], '', ErrorCode.Rule_Name_Invalid, message))
        return None

    name = name_lines[0][1]
    if not rule_name_pattern.match(name):
        message = f'Not a valid rule name -> {name}'
        errors.append(_new_error(name, 'rule', name_lines[0][0], '', ErrorCode.Rule_Name_Invalid, message))
        return None

    # .. every required block has to be present and non-empty ..
    for block in _required_blocks:
        if not blocks.get(block):
            message = f'The {block} block is required'
            errors.append(_new_error(name, block, blocks['rule_line'], '', ErrorCode.Missing_Block, message))
            return None

    # .. docs are free text, the stored place for rationale ..
    docs_lines = []
    for _, text in blocks.get('docs', []):
        docs_lines.append(text)
    docs = '\n'.join(docs_lines)

    # .. defaults are named concrete values ..
    error_count = len(errors)
    defaults = {}
    for action in _parse_assignments(blocks.get('defaults', []), 'defaults', name, errors):
        defaults[action['target']] = action['value']

    # .. conditions and joiners come from the when block ..
    conditions, joiners = _parse_when(blocks['when'], name, errors)

    # .. and the two action blocks close the document.
    then_actions = _parse_assignments(blocks['then'], 'then', name, errors)
    else_actions = _parse_assignments(blocks.get('else', []), 'else', name, errors)

    # A rule with any errors is not returned - the errors describe how to fix it.
    if len(errors) > error_count:
        return None

    full_name = ruleset_name + '_' + name

    out = {
        'name': name,
        'docs': docs,
        'defaults': defaults,
        'conditions': conditions,
        'joiners': joiners,
        'then': then_actions,
        'else': else_actions,
        'ruleset_name': ruleset_name,
        'full_name': full_name,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

def parse_data_details(data:'str', ruleset_name:'str') -> 'anytuple':
    """ Parses rules text into documents keyed by full name, plus a list of structured errors.
    """
    errors = []
    collected = []

    # Split the text into blocks, line by line ..
    current_blocks:'anydict | None' = None
    current_block = ''

    for line, raw in enumerate(data.splitlines(), 1):

        # .. comments are legal anywhere and simply skipped ..
        text = strip_comment(raw).strip()
        if not text:
            continue

        # .. a block keyword on its own line switches the current block ..
        if text in _block_names:

            # .. the rule keyword additionally starts a new rule ..
            if text == 'rule':
                current_blocks = {'rule_line': line}
                collected.append(current_blocks)

            if current_blocks is None:
                message = f'The {text} block appears before any rule'
                errors.append(_new_error('', text, line, '', ErrorCode.Content_Outside_Block, message))
                current_block = ''
                continue

            current_blocks[text] = []
            current_block = text
            continue

        # .. invoke blocks are rejected - enrichment happens in the calling service ..
        if text == 'invoke':
            message = 'The invoke block is not supported - enrichment happens in the calling service, before the rule runs'
            errors.append(_new_error('', 'invoke', line, '', ErrorCode.Invoke_Block, message))
            current_block = 'invoke'
            continue

        # .. lines inside a rejected invoke block are swallowed, the error was already reported ..
        if current_block == 'invoke':
            continue

        # .. and any other line is content that belongs to the current block.
        if current_blocks is None or not current_block:
            message = f'Content outside of any block -> {text}'
            errors.append(_new_error('', '', line, '', ErrorCode.Content_Outside_Block, message))
            continue

        current_blocks[current_block].append((line, text))

    # Now, build a document out of each collected rule ..
    documents = SortedDict()

    for blocks in collected:
        document = _build_document(blocks, ruleset_name, errors)
        if document:
            documents[document['full_name']] = document

    # .. and hand back both the documents and whatever errors were found.
    out = (documents, errors)
    return out

# ################################################################################################################################

def parse_data(data:'str', ruleset_name:'str') -> 'strdict':
    """ Parses rules text into documents keyed by full name, logging any errors found.
    """
    documents, errors = parse_data_details(data, ruleset_name)

    for error in errors:
        logger.warning(f'Rule parse error -> {error}')

    return documents

# ################################################################################################################################

def parse_file(path:'str | Path', ruleset_name:'str') -> 'strdict':
    """ Parses a rules file into documents keyed by full name.
    """
    path = str(path)

    with open_r(path) as file_object:
        data = file_object.read()

    out = parse_data(data, ruleset_name)
    return out

# ################################################################################################################################
# ################################################################################################################################
