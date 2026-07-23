# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from typing import NamedTuple

# Zato
from zato.common.rules.document import Default_Prefix, NodeKind

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

class Role:
    """ How a term is used inside a rule document.
    """
    Subject = 'subject'
    Value   = 'value'
    Target  = 'target'

# ################################################################################################################################
# ################################################################################################################################

class RenameResult(NamedTuple):
    """ A document rewritten by a rename, along with how many places changed.
    """
    document: 'anydict'
    change_count: 'int'

# ################################################################################################################################
# ################################################################################################################################

def node_reference_terms(node:'anydict') -> 'strlist':
    """ Returns the vocabulary terms one value node references, recursing into lists.

    References to defaults are rule-local names, not vocabulary terms, so they are never included.
    """
    out = []
    kind = node['kind']

    # A reference names a term directly, unless it points to a rule-local default ..
    if kind == NodeKind.Reference:
        term = node['term']
        if not term.startswith(Default_Prefix):
            out.append(term)

    # .. and a list carries other value nodes inside.
    elif kind == NodeKind.List:
        for item in node['items']:
            child_terms = node_reference_terms(item)
            out.extend(child_terms)

    return out

# ################################################################################################################################

def _collect_node_terms(node:'anydict', block:'str', out:'dictlist') -> 'None':
    """ Collects reference terms from one value node as usage entries.
    """
    for term in node_reference_terms(node):
        out.append({'term': term, 'block': block, 'role': Role.Value})

# ################################################################################################################################

def extract_references(document:'anydict') -> 'dictlist':
    """ Returns every term usage in a rule document - subjects, value references and action targets.

    Defaults are skipped by design - the parser guarantees they hold concrete values only.
    """
    out = []

    # Conditions use terms as subjects and inside the values they compare against ..
    for condition in document['conditions']:
        out.append({'term': condition['subject'], 'block': 'when', 'role': Role.Subject})
        for node in condition['values']:
            _collect_node_terms(node, 'when', out)

    # .. and actions write to targets and read terms through their values.
    for block in ('then', 'else'):
        for action in document[block]:
            out.append({'term': action['target'], 'block': block, 'role': Role.Target})
            _collect_node_terms(action['value'], block, out)

    return out

# ################################################################################################################################

def referenced_terms(document:'anydict') -> 'strlist':
    """ Returns the sorted unique terms a rule document references anywhere.
    """
    terms = set()
    for usage in extract_references(document):
        terms.add(usage['term'])

    out = sorted(terms)
    return out

# ################################################################################################################################
# ################################################################################################################################

def where_used(term:'str', documents:'anydict') -> 'dictlist':
    """ Returns every usage of a term across the given documents, keyed by rule and place.
    """
    out = []

    for document in documents.values():
        for usage in extract_references(document):
            if usage['term'] == term:
                entry = {'rule': document['full_name'], 'block': usage['block'], 'role': usage['role']}
                out.append(entry)

    return out

# ################################################################################################################################

def can_delete(term:'str', documents:'anydict') -> 'bool':
    """ Returns True only when no document references the term - deletion is blocked while anything still uses it.
    """
    usages = where_used(term, documents)

    out = not usages
    return out

# ################################################################################################################################
# ################################################################################################################################

def _rename_in_node(node:'anydict', old_term:'str', new_term:'str') -> 'int':
    """ Renames references inside one value node, returning how many places changed.
    """
    kind = node['kind']
    out = 0

    # A matching reference is renamed in place ..
    if kind == NodeKind.Reference:
        if node['term'] == old_term:
            node['term'] = new_term
            out = 1

    # .. and a list renames item by item.
    elif kind == NodeKind.List:
        for item in node['items']:
            out += _rename_in_node(item, old_term, new_term)

    return out

# ################################################################################################################################

def rename_term(document:'anydict', old_term:'str', new_term:'str') -> 'RenameResult':
    """ Returns a copy of the document with every use of a term renamed, along with the change count.

    The input document is never modified - the rewrite happens on a deep copy.
    """
    rewritten = deepcopy(document)
    count = 0

    # Conditions rename their subjects and the references inside their values ..
    for condition in rewritten['conditions']:
        if condition['subject'] == old_term:
            condition['subject'] = new_term
            count += 1
        for node in condition['values']:
            count += _rename_in_node(node, old_term, new_term)

    # .. and actions rename their targets and the references inside their values.
    for block in ('then', 'else'):
        for action in rewritten[block]:
            if action['target'] == old_term:
                action['target'] = new_term
                count += 1
            count += _rename_in_node(action['value'], old_term, new_term)

    out = RenameResult(rewritten, count)
    return out

# ################################################################################################################################

def preview_rename(old_term:'str', new_term:'str', documents:'anydict') -> 'dictlist':
    """ Returns the impact a rename would have - per rule, how many places would change - without changing anything.
    """
    out = []

    for document in documents.values():
        result = rename_term(document, old_term, new_term)
        if result.change_count:
            entry = {'rule': document['full_name'], 'change_count': result.change_count}
            out.append(entry)

    return out

# ################################################################################################################################

def apply_rename(old_term:'str', new_term:'str', documents:'anydict') -> 'anydict':
    """ Rewrites every document that references a term, returning only the rewritten ones keyed by full name.
    """
    out = {}

    for full_name, document in documents.items():
        result = rename_term(document, old_term, new_term)
        if result.change_count:
            out[full_name] = result.document

    return out

# ################################################################################################################################
# ################################################################################################################################
