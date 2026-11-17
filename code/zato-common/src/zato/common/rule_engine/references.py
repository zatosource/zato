# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.document import Default_Prefix, NodeKind

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
