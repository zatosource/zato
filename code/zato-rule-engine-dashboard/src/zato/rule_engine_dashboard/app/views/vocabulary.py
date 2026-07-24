# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.http import JsonResponse

# Zato
from zato.common.rule_engine.bootstrap import infer_from_document, vocabulary_from_payload
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.references import apply_rename, preview_rename
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document
from zato.rule_engine_dashboard.app.storage import get_backend
from zato.rule_engine_dashboard.app.views.api import BadRequestError, json_api, read_json, reference_row, required, \
    serialize_all

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictlist

# ################################################################################################################################
# ################################################################################################################################

# A rename that does not say otherwise only previews its impact.
_default_dry_run = True

# How many rulesets one rename scans - large enough for any repository the list screen itself can hold.
_rename_scan_limit = 10_000

# ################################################################################################################################
# ################################################################################################################################

@json_api
def vocabulary_get(req:'any_', definition_id:'int') -> 'any_':
    """ The vocabulary screen's tree - one stored vocabulary document.
    """
    backend = get_backend()
    document = backend.definitions.get_document(definition_id)

    out = JsonResponse({'vocabulary': document})
    return out

# ################################################################################################################################

@json_api
def term_where_used(req:'any_') -> 'any_':
    """ Every indexed place one term is referenced from - delete stays blocked while any remain.
    """
    if term := req.GET.get('term'):
        pass
    else:
        raise BadRequestError('Missing required parameter -> term')

    backend = get_backend()
    records = backend.references.where_used(term)
    items = serialize_all(records, reference_row)
    is_used = len(items) > 0

    out = JsonResponse({'term': term, 'items': items, 'is_used': is_used, 'can_delete': not is_used})
    return out

# ################################################################################################################################

@json_api
def term_rename(req:'any_') -> 'any_':
    """ Renames one term across every referencing ruleset - a dry run reports the impact without changing anything.
    """
    body = read_json(req)
    old_term = required(body, 'old_term')
    new_term = required(body, 'new_term')

    # A rename is a preview unless the request explicitly asks to apply it.
    if 'dry_run' in body:
        is_dry_run = body['dry_run']
    else:
        is_dry_run = _default_dry_run

    backend = get_backend()
    actor = req.user.username
    definitions = backend.definitions.list(object_type=Definition_Type_Ruleset, limit=_rename_scan_limit)

    affected:'dictlist' = []

    for record in definitions:
        document = deserialize_document(record.document)

        # Only stored documents that carry rule documents can reference terms.
        if Documents_Key not in document:
            continue

        documents = document[Documents_Key]
        impact = preview_rename(old_term, new_term, documents)

        # A ruleset without a single reference stays untouched.
        if not impact:
            continue

        affected.append({'definition_id': record.id, 'definition_name': record.name, 'impact': impact})

        # The dry run stops at the impact report ..
        if is_dry_run:
            continue

        # .. while an applied rename rewrites the referencing documents ..
        renamed = apply_rename(old_term, new_term, documents)
        merged = dict(documents)
        merged.update(renamed)

        # .. stores the rewrite as a new optimistic version ..
        comment = f'Rename term {old_term} to {new_term}'
        _ = backend.versions.create(
            definition_id=record.id,
            expected_current_version=record.current_version,
            document={Documents_Key: merged},
            author=actor,
            comment=comment,
        )

        # .. and keeps the where-used index true to what is now stored.
        _ = backend.references.rebuild(definition_id=record.id, documents=merged)

    out = JsonResponse({'old_term': old_term, 'new_term': new_term, 'dry_run': is_dry_run, 'definitions': affected})
    return out

# ################################################################################################################################

@json_api
def vocabulary_bootstrap(req:'any_') -> 'any_':
    """ Paste-a-payload - one JSON example deterministically becomes a vocabulary fragment.
    """
    body = read_json(req)
    payload = required(body, 'payload')

    vocabulary = vocabulary_from_payload(payload)

    out = JsonResponse({'vocabulary': vocabulary})
    return out

# ################################################################################################################################

@json_api
def vocabulary_infer(req:'any_', definition_id:'int') -> 'any_':
    """ Infer-from-typing - unknown terms in typed rules become proposed terms with types inferred from usage.
    """
    body = read_json(req)
    text = required(body, 'text')
    ruleset_name = required(body, 'ruleset_name')

    backend = get_backend()
    vocabulary = backend.definitions.get_document(definition_id)

    documents, errors = parse_data_details(text, ruleset_name)

    proposals:'dictlist' = []

    for document in documents.values():
        found = infer_from_document(document, vocabulary)
        proposals.extend(found)

    out = JsonResponse({'proposals': proposals, 'errors': errors})
    return out

# ################################################################################################################################
# ################################################################################################################################
