# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rules.render import render_document

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

def _signature(document:'anydict') -> 'anydict':
    """ Returns the parts of a document that carry meaning - everything except its name.

    Two documents with equal signatures are the same rule, however it is called,
    which is what lets a renamed rule read as a move and never as a delete plus an add.
    """
    out = {
        'docs': document['docs'],
        'defaults': document['defaults'],
        'conditions': document['conditions'],
        'joiners': document['joiners'],
        'then': document['then'],
        'else': document['else'],
    }
    return out

# ################################################################################################################################

def _changed_blocks(old_document:'anydict', new_document:'anydict') -> 'strlist':
    """ Names the blocks that differ between two versions of the same rule.

    Conditions and their joiners are one thing to a reader - the when block -
    so a change to either is reported as when.
    """
    out = []

    if old_document['docs'] != new_document['docs']:
        out.append('docs')

    if old_document['defaults'] != new_document['defaults']:
        out.append('defaults')

    # A joiner change alone rewires the logic just like a condition change does.
    when_changed = old_document['conditions'] != new_document['conditions']
    if not when_changed:
        when_changed = old_document['joiners'] != new_document['joiners']

    if when_changed:
        out.append('when')

    if old_document['then'] != new_document['then']:
        out.append('then')

    if old_document['else'] != new_document['else']:
        out.append('else')

    return out

# ################################################################################################################################
# ################################################################################################################################

def diff_documents(old_documents:'anydict', new_documents:'anydict') -> 'anydict':
    """ Compares two versions of a ruleset structurally, never by text.

    Both inputs map rule names to canonical documents, the same shape the parser produces.
    The result groups every rule into added, deleted, updated and unchanged, names
    the changed blocks per updated rule, and reports a renamed-but-identical rule
    as a rename. Because the comparison runs over parsed documents, reformatting,
    comments and layout changes produce no findings at all.

    Every entry carries the rendered canonical text so a reader never needs to
    reconstruct what a rule looked like.
    """

    # Our response to produce
    out = {
        'added': [],
        'deleted': [],
        'renamed': [],
        'updated': [],
        'unchanged': [],
    }

    old_names = set(old_documents)
    new_names = set(new_documents)

    # Rules present in both versions are unchanged or updated ..
    for name in sorted(old_names & new_names):
        old_document = old_documents[name]
        new_document = new_documents[name]

        if old_document == new_document:
            out['unchanged'].append({'rule': name})
        else:
            changed = _changed_blocks(old_document, new_document)
            old_rendered = render_document(old_document)
            new_rendered = render_document(new_document)
            entry = {'rule': name, 'changed': changed, 'old_rendered': old_rendered, 'new_rendered': new_rendered}
            out['updated'].append(entry)

    # .. rules present on one side only are rename candidates first ..
    deleted_names = sorted(old_names - new_names)
    added_names = sorted(new_names - old_names)
    claimed_added = set()

    for old_name in deleted_names:
        old_document = old_documents[old_name]
        old_signature = _signature(old_document)

        # .. a deleted rule whose content lives on under another name is a rename ..
        for new_name in added_names:
            if new_name in claimed_added:
                continue

            new_document = new_documents[new_name]
            new_signature = _signature(new_document)

            if old_signature == new_signature:
                rendered = render_document(new_document)
                entry = {'old_rule': old_name, 'new_rule': new_name, 'rendered': rendered}
                out['renamed'].append(entry)
                claimed_added.add(new_name)
                break

        # .. and one whose content is gone for good is a real deletion.
        else:
            rendered = render_document(old_document)
            out['deleted'].append({'rule': old_name, 'rendered': rendered})

    # Whatever no rename claimed is a real addition.
    for new_name in added_names:
        if new_name not in claimed_added:
            new_document = new_documents[new_name]
            rendered = render_document(new_document)
            out['added'].append({'rule': new_name, 'rendered': rendered})

    return out

# ################################################################################################################################
# ################################################################################################################################
