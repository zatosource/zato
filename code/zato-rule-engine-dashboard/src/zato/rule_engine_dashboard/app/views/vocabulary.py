# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.http import JsonResponse

# Zato
from zato.common.rule_engine import webapi
from zato.common.rule_engine.bootstrap import infer_from_document, vocabulary_from_payload
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.references import apply_rename, preview_rename
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document
from zato.common.util.logging_ import count_text
from zato.rule_engine_dashboard.app.storage import get_backend
from zato.rule_engine_dashboard.app.views.api import BadRequestError, json_api, note_answer, read_json, reference_row, \
    required, serialize_all

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

# A rename that does not say otherwise only previews its impact.
_default_dry_run = True

# How many rulesets one rename scans - large enough for any repository the list screen itself can hold.
_rename_scan_limit = 10_000

# ################################################################################################################################
# ################################################################################################################################

def _vocabulary_note(vocabulary:'anydict') -> 'str':
    """ How much one vocabulary document holds, the way the log says it.
    """
    entities = vocabulary['entities']
    term_count = 0

    for entity in entities:
        term_count += len(entity['attributes'])

    entities_text = count_text(len(entities), 'entity', 'entities')
    terms_text = count_text(term_count, 'term', 'terms')

    out = f'{entities_text}, {terms_text}'
    return out

# ################################################################################################################################

@json_api
def vocabulary_get(req:'any_', definition_id:'int') -> 'any_':
    """ The vocabulary screen's tree - one stored vocabulary document.
    """
    result, note = webapi.get_vocabulary(get_backend(), definition_id)
    note_answer(req, note)

    out = JsonResponse(result)
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

    places_text = count_text(len(items), 'place', 'places')
    note_answer(req, f'`{term}` is used in {places_text}')

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

    rulesets_text = count_text(len(affected), 'ruleset', 'rulesets')

    if is_dry_run:
        note_answer(req, f'`{old_term}` would become `{new_term}` in {rulesets_text}')
    else:
        note_answer(req, f'`{old_term}` renamed to `{new_term}` in {rulesets_text}')

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

    note_answer(req, _vocabulary_note(vocabulary))

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

    proposals_text = count_text(len(proposals), 'proposed term', 'proposed terms')
    findings_text = count_text(len(errors), 'finding', 'findings')
    note_answer(req, f'{proposals_text}, {findings_text}')

    out = JsonResponse({'proposals': proposals, 'errors': errors})
    return out

# ################################################################################################################################
# ################################################################################################################################
