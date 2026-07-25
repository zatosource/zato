# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.document import Comparator_Arity, Arity, NodeKind
from zato.common.rule_engine.models import rule_from_document
from zato.common.rule_engine.scenarios import validate_test_set
from zato.common.rule_engine.sql.constants import Definition_Type_Decision_Table, Definition_Type_Ruleset, \
    Definition_Type_Sentence_Rule, Definition_Type_Test_Set, Definition_Type_Vocabulary, Documents_Key
from zato.common.rule_engine.table import validate_table
from zato.common.rule_engine.tokens import identifier_pattern, rule_name_pattern
from zato.common.rule_engine.vocabulary import ErrorCode, new_error, validate_vocabulary

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

# Every key a canonical rule document has to carry - the engine reads all of them.
Required_Keys = ('name', 'ruleset_name', 'full_name', 'docs', 'defaults', 'conditions', 'joiners', 'then', 'else')

# The keys that are plain text.
Text_Keys = ('name', 'ruleset_name', 'full_name', 'docs')

# The keys that hold a list of actions.
Action_Keys = ('then', 'else')

# The joiners a document may put between its conditions.
Joiners = ('and', 'or')

# The key under which a document carries the negated guards a declared table override compiles into.
Guards_Key = 'unless'

# How many values each arity expects, where the count is fixed.
Value_Counts = {
    Arity.None_: 0,
    Arity.One:   1,
    Arity.Two:   2,
}

# ################################################################################################################################
# ################################################################################################################################

def _bad(rule:'str', block:'str', field:'str', message:'str') -> 'anydict':
    """ One structural finding about a stored document, shaped like every other validation error.
    """
    out = new_error(rule, block, field, ErrorCode.Bad_Document, message)
    return out

# ################################################################################################################################

def _check_value_node(node:'any_', rule:'str', block:'str', field:'str', errors:'dictlist') -> 'None':
    """ Checks one tagged value node, following lists into their items.
    """
    if not isinstance(node, dict):
        errors.append(_bad(rule, block, field, f'A value has to be a tagged node, not {type(node).__name__}'))
        return

    kind = node.get('kind')

    if kind == NodeKind.Literal:

        # A literal carries its value, and None is not a value any rule may compare against.
        if node.get('value') is None:
            errors.append(_bad(rule, block, field, 'A literal value node needs a value'))

    elif kind == NodeKind.List:
        items = node.get('items')

        if not isinstance(items, list):
            errors.append(_bad(rule, block, field, 'A list value node needs its items'))
            return

        for item in items:
            _check_value_node(item, rule, block, field, errors)

    elif kind == NodeKind.Object:
        if not isinstance(node.get('value'), dict):
            errors.append(_bad(rule, block, field, 'An object value node needs a mapping'))

    elif kind == NodeKind.Reference:
        term = node.get('term')

        if not isinstance(term, str) or not term:
            errors.append(_bad(rule, block, field, 'A reference value node needs the term it points to'))

    else:
        errors.append(_bad(rule, block, field, f'Not a value node kind -> {kind!r}'))

# ################################################################################################################################

def _check_condition(condition:'any_', rule:'str', block:'str', errors:'dictlist') -> 'None':
    """ Checks one condition - its subject, its comparator and as many values as that comparator takes.
    """
    if not isinstance(condition, dict):
        errors.append(_bad(rule, block, '', f'A condition has to be a mapping, not {type(condition).__name__}'))
        return

    subject = condition.get('subject')

    if not isinstance(subject, str) or not identifier_pattern.match(subject):
        errors.append(_bad(rule, block, '', f'Not a condition subject -> {subject!r}'))
        return

    comparator = condition.get('comparator')

    if isinstance(comparator, str):
        arity = Comparator_Arity.get(comparator)
    else:
        arity = None

    if arity is None:
        errors.append(_bad(rule, block, subject, f'Not a comparator -> {comparator!r}'))
        return

    values = condition.get('values')

    if not isinstance(values, list):
        errors.append(_bad(rule, block, subject, 'A condition needs its values, even if it takes none'))
        return

    value_count = len(values)
    expected_count = Value_Counts.get(arity)

    # Most comparators take a fixed number of values, a membership one takes any number but at least one.
    if expected_count is None:
        if value_count < 1:
            errors.append(_bad(rule, block, subject, f'{comparator!r} needs at least one value'))
    elif value_count != expected_count:
        errors.append(_bad(rule, block, subject, f'{comparator!r} takes {expected_count} values, not {value_count}'))

    for node in values:
        _check_value_node(node, rule, block, subject, errors)

# ################################################################################################################################

def _check_when(document:'anydict', rule:'str', errors:'dictlist') -> 'None':
    """ Checks the conditions and the joiners between them.
    """
    conditions = document['conditions']
    joiners = document['joiners']

    if not isinstance(conditions, list):
        errors.append(_bad(rule, 'when', '', f'Conditions have to be a list, not {type(conditions).__name__}'))
        return

    condition_count = len(conditions)

    # A rule with no condition would fire on every input, which is never what an empty when block means.
    if condition_count == 0:
        errors.append(_bad(rule, 'when', '', 'A rule needs at least one condition'))
        return

    for condition in conditions:
        _check_condition(condition, rule, 'when', errors)

    if not isinstance(joiners, list):
        errors.append(_bad(rule, 'when', '', f'Joiners have to be a list, not {type(joiners).__name__}'))
        return

    # There is exactly one joiner between each pair of neighbouring conditions.
    joiner_count = len(joiners)
    expected_count = condition_count - 1

    if joiner_count != expected_count:
        message = f'{condition_count} conditions take {expected_count} joiners, not {joiner_count}'
        errors.append(_bad(rule, 'when', '', message))

    for joiner in joiners:
        if joiner not in Joiners:
            errors.append(_bad(rule, 'when', '', f'Not a joiner -> {joiner!r}'))

# ################################################################################################################################

def _check_actions(document:'anydict', rule:'str', errors:'dictlist') -> 'None':
    """ Checks both action blocks - every action assigns one identifier one value.
    """
    for block in Action_Keys:
        actions = document[block]

        if not isinstance(actions, list):
            errors.append(_bad(rule, block, '', f'Actions have to be a list, not {type(actions).__name__}'))
            continue

        for action in actions:

            if not isinstance(action, dict):
                errors.append(_bad(rule, block, '', f'An action has to be a mapping, not {type(action).__name__}'))
                continue

            target = action.get('target')

            if not isinstance(target, str) or not identifier_pattern.match(target):
                errors.append(_bad(rule, block, '', f'Not an assignment target -> {target!r}'))
                continue

            _check_value_node(action.get('value'), rule, block, target, errors)

    # A rule that assigns nothing on a match decides nothing at all.
    then_actions = document['then']

    if isinstance(then_actions, list):
        if not then_actions:
            errors.append(_bad(rule, 'then', '', 'A rule needs at least one then action'))

# ################################################################################################################################

def _check_defaults(document:'anydict', rule:'str', errors:'dictlist') -> 'None':
    """ Checks the defaults - named concrete values the input may leave out.
    """
    defaults = document['defaults']

    if not isinstance(defaults, dict):
        errors.append(_bad(rule, 'defaults', '', f'Defaults have to be a mapping, not {type(defaults).__name__}'))
        return

    for name, node in defaults.items():

        if not isinstance(name, str) or not identifier_pattern.match(name):
            errors.append(_bad(rule, 'defaults', '', f'Not a default name -> {name!r}'))
            continue

        _check_value_node(node, rule, 'defaults', name, errors)

# ################################################################################################################################

def _check_guards(document:'anydict', rule:'str', errors:'dictlist') -> 'None':
    """ Checks the negated guards, which only a compiled decision table carries.
    """
    guards = document.get(Guards_Key)

    if guards is None:
        return

    if not isinstance(guards, list):
        errors.append(_bad(rule, Guards_Key, '', f'Guards have to be a list, not {type(guards).__name__}'))
        return

    for guard in guards:

        if not isinstance(guard, list) or not guard:
            errors.append(_bad(rule, Guards_Key, '', 'Each guard is a non-empty list of conditions'))
            continue

        for condition in guard:
            _check_condition(condition, rule, Guards_Key, errors)

# ################################################################################################################################
# ################################################################################################################################

def validate_document_shape(document:'any_') -> 'dictlist':
    """ Validates one canonical rule document structurally, returning parser-shaped findings.

    This is what the store needs to be true of a document before it can run it - the keys the
    engine reads, the shapes it reads them in, and a when expression that compiles. Nothing here
    looks at a vocabulary, which is what validate_document does on top of this.
    """
    errors:'dictlist' = []

    if not isinstance(document, dict):
        errors.append(_bad('', 'rule', '', f'A rule document has to be a mapping, not {type(document).__name__}'))
        return errors

    # A document missing a key the engine reads cannot be checked any further ..
    missing = []
    for key in Required_Keys:
        if key not in document:
            missing.append(key)

    if missing:
        joined = ', '.join(missing)
        errors.append(_bad('', 'rule', '', f'The document has no {joined}'))
        return errors

    # .. its identity fields are all text ..
    for key in Text_Keys:
        value = document[key]
        if not isinstance(value, str):
            errors.append(_bad('', 'rule', key, f'{key} has to be text, not {type(value).__name__}'))

    if errors:
        return errors

    rule = document['name']

    if not rule_name_pattern.match(rule):
        errors.append(_bad(rule, 'rule', 'name', f'Not a rule name -> {rule!r}'))

    ruleset_name = document['ruleset_name']
    full_name = document['full_name']
    expected_full_name = ruleset_name + '_' + rule

    # .. the full name is how every store, cache and log refers to the rule, so it has to be the one
    # the ruleset and the rule name make together, never a name of its own ..
    if full_name != expected_full_name:
        errors.append(_bad(rule, 'rule', 'full_name', f'The full name of {rule} in {ruleset_name} is {expected_full_name}'))

    # .. and then come the blocks themselves.
    _check_defaults(document, rule, errors)
    _check_when(document, rule, errors)
    _check_actions(document, rule, errors)
    _check_guards(document, rule, errors)

    # A document whose shape is wrong cannot be compiled, and one whose shape is right still may
    # not compile, e.g. a comparison the engine's own grammar rejects, so that is checked last.
    if not errors:
        try:
            compiled = rule_from_document(document)
        except Exception as e:
            errors.append(_bad(rule, 'when', '', f'The rule cannot be compiled -> {e}'))
        else:
            if compiled is None:
                errors.append(_bad(rule, 'when', '', 'The when expression does not compile'))

    return errors

# ################################################################################################################################

def validate_documents(documents:'any_') -> 'dictlist':
    """ Validates the rule documents of one stored ruleset, returning parser-shaped findings.

    All of them belong to one ruleset and each is keyed by its own full name, which is what
    loading a stored version relies on.
    """
    errors:'dictlist' = []

    if not isinstance(documents, dict):
        errors.append(_bad('', 'rule', '', f'Rule documents have to be a mapping, not {type(documents).__name__}'))
        return errors

    # A ruleset with no rules decides nothing, which is an authoring error rather than a silent no-op.
    if not documents:
        errors.append(_bad('', 'rule', '', 'A ruleset needs at least one rule'))
        return errors

    ruleset_name = ''

    for key, document in documents.items():
        document_errors = validate_document_shape(document)

        if document_errors:
            errors.extend(document_errors)
            continue

        rule = document['name']

        # The key a document is stored under is the name everything else refers to it by ..
        if key != document['full_name']:
            errors.append(_bad(rule, 'rule', 'full_name', f'The document stored as {key!r} calls itself {document["full_name"]!r}'))

        # .. and one stored ruleset holds the rules of one ruleset only, because that is
        # the name the whole snapshot is loaded under.
        if not ruleset_name:
            ruleset_name = document['ruleset_name']
        elif document['ruleset_name'] != ruleset_name:
            message = f'{rule} belongs to {document["ruleset_name"]}, the other rules to {ruleset_name}'
            errors.append(_bad(rule, 'rule', 'ruleset_name', message))

    return errors

# ################################################################################################################################
# ################################################################################################################################

def _validate_ruleset(document:'anydict') -> 'dictlist':
    """ Validates a stored ruleset document - its rules are what makes it runnable.
    """
    if Documents_Key not in document:
        out = [_bad('', 'rule', Documents_Key, f'A ruleset document keeps its rules under `{Documents_Key}`')]
        return out

    out = validate_documents(document[Documents_Key])
    return out

# ################################################################################################################################

# Which structural validation each definition type runs before it is stored.
_validators = {
    Definition_Type_Ruleset:        _validate_ruleset,
    Definition_Type_Sentence_Rule:  _validate_ruleset,
    Definition_Type_Decision_Table: validate_table,
    Definition_Type_Vocabulary:     validate_vocabulary,
    Definition_Type_Test_Set:       validate_test_set,
}

# The top-level keys each type's document carries, with the kind of container each one holds.
# A validator reads these directly, so they are checked before it runs and their absence is
# reported by name rather than as a failure inside it.
_document_keys = {
    Definition_Type_Ruleset:        {Documents_Key: dict},
    Definition_Type_Sentence_Rule:  {Documents_Key: dict},
    Definition_Type_Decision_Table: {'name': str, 'conditions': list, 'actions': list, 'columns': list},
    Definition_Type_Vocabulary:     {'entities': list},
    Definition_Type_Test_Set:       {'name': str, 'scenarios': list},
}

# ################################################################################################################################

def _check_document_keys(object_type:'str', document:'anydict', errors:'dictlist') -> 'None':
    """ Checks the top-level keys one document type's own validation reads.
    """
    for key, expected_type in _document_keys[object_type].items():

        if key not in document:
            errors.append(_bad('', 'rule', key, f'A {object_type} document has no {key}'))
            continue

        value = document[key]

        if not isinstance(value, expected_type):
            message = f'{key} of a {object_type} document holds a {expected_type.__name__}, not a {type(value).__name__}'
            errors.append(_bad('', 'rule', key, message))

# ################################################################################################################################

def validate_definition_document(object_type:'any_', document:'any_') -> 'dictlist':
    """ Validates one stored document against the checks its own type declares.

    Every definition type has such checks, so no document type reaches the store on a browser's
    word alone. An unknown type is refused rather than waved through.
    """
    errors:'dictlist' = []

    if isinstance(object_type, str):
        validator = _validators.get(object_type)
    else:
        validator = None

    if validator is None:
        errors.append(_bad('', 'rule', 'object_type', f'Unknown rule definition type -> {object_type!r}'))
        return errors

    if not isinstance(document, dict):
        errors.append(_bad('', 'rule', '', f'A document has to be a mapping, not {type(document).__name__}'))
        return errors

    # The keys each validator reads are checked first, so a document missing one is told which ..
    _check_document_keys(object_type, document, errors)

    if errors:
        return errors

    # .. and below the top level these validators are written for documents the screens produce,
    # so one shaped differently all the way down is something they cannot read at all, and that
    # is itself the finding rather than a failure a caller sees as a broken endpoint.
    try:
        out = validator(document)
    except Exception as e:
        out = [_bad('', 'rule', '', f'The document cannot be read as a {object_type} -> {e}')]

    return out

# ################################################################################################################################
# ################################################################################################################################
