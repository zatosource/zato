# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.rule_engine.conditions import ErrorCode, new_error, parse_condition
from zato.common.rule_engine.document import NodeKind
from zato.common.rule_engine.tokens import find_top_level, identifier_pattern, parse_value, rule_name_pattern, strip_comment
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

# The block keywords a rule is made of, each on its own line in the text form.
_block_names = {'rule', 'docs', 'defaults', 'when', 'then', 'else'}

# Blocks every rule must have.
_required_blocks = ('rule', 'when', 'then')

# The joiner keywords accepted between conditions.
_joiner_names = ('and', 'or')

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
                errors.append(new_error(rule_name, 'when', line, '', ErrorCode.Missing_Joiner, message))
        else:
            if joiner:
                message = f'The last condition must not end with a joiner -> {joiner}'
                errors.append(new_error(rule_name, 'when', line, '', ErrorCode.Joiner_After_Last, message))
                joiner = ''

        # .. and the line itself is a single condition.
        condition = parse_condition(text, line, rule_name, errors)
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
        errors.append(new_error(rule_name, 'defaults', line, '', ErrorCode.Bad_Value, message))
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
            errors.append(new_error(rule_name, block, line, '', ErrorCode.Bad_Assignment, message))
            continue

        # .. whose target is an identifier ..
        target = text[:equals_index].strip()
        if not identifier_pattern.match(target):
            message = f'Not a valid assignment target -> {target}'
            errors.append(new_error(rule_name, block, line, target, ErrorCode.Bad_Assignment, message))
            continue

        # .. and whose value is a tagged node.
        value_text = text[equals_index+1:].strip()
        node = parse_value(value_text)
        if node is None:
            message = f'Not a recognized value -> {value_text}'
            errors.append(new_error(rule_name, block, line, target, ErrorCode.Bad_Value, message))
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
        errors.append(new_error('', 'rule', blocks['rule_line'], '', ErrorCode.Rule_Name_Invalid, message))
        return None

    name = name_lines[0][1]
    if not rule_name_pattern.match(name):
        message = f'Not a valid rule name -> {name}'
        errors.append(new_error(name, 'rule', name_lines[0][0], '', ErrorCode.Rule_Name_Invalid, message))
        return None

    # .. every required block has to be present and non-empty ..
    for block in _required_blocks:
        if not blocks.get(block):
            message = f'The {block} block is required'
            errors.append(new_error(name, block, blocks['rule_line'], '', ErrorCode.Missing_Block, message))
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
                errors.append(new_error('', text, line, '', ErrorCode.Content_Outside_Block, message))
                current_block = ''
                continue

            current_blocks[text] = []
            current_block = text
            continue

        # .. invoke blocks are rejected - enrichment happens in the calling service ..
        if text == 'invoke':
            message = 'The invoke block is not supported - enrichment happens in the calling service, before the rule runs'
            errors.append(new_error('', 'invoke', line, '', ErrorCode.Invoke_Block, message))
            current_block = 'invoke'
            continue

        # .. lines inside a rejected invoke block are swallowed, the error was already reported ..
        if current_block == 'invoke':
            continue

        # .. and any other line is content that belongs to the current block.
        if current_blocks is None or not current_block:
            message = f'Content outside of any block -> {text}'
            errors.append(new_error('', '', line, '', ErrorCode.Content_Outside_Block, message))
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
