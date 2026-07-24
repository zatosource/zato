# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.http import JsonResponse

# Zato
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.render import render_documents
from zato.common.rule_engine.semantics import validate_document
from zato.common.rule_engine.sql.constants import Documents_Key
from zato.common.rule_engine.testing import run_test_set
from zato.common.rule_engine.vocabulary import Comparators_By_Type, iter_attributes, Status_Deprecated
from zato.rule_engine_dashboard.app.storage import get_backend
from zato.rule_engine_dashboard.app.views.api import json_api, read_json, required

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictlist

# ################################################################################################################################
# ################################################################################################################################

@json_api
def editor_validate(req:'any_') -> 'any_':
    """ Parses typed rules and, against a named vocabulary, checks their semantics too.
    """
    body = read_json(req)
    text = required(body, 'text')
    ruleset_name = required(body, 'ruleset_name')

    documents, errors = parse_data_details(text, ruleset_name)

    # Semantic checks join in when the request names a vocabulary to validate against.
    if vocabulary_id := body.get('vocabulary_id'):
        backend = get_backend()
        vocabulary = backend.definitions.get_document(vocabulary_id)

        for document in documents.values():
            semantic_errors = validate_document(document, vocabulary)
            errors.extend(semantic_errors)

    out = JsonResponse({'documents': documents, 'errors': errors})
    return out

# ################################################################################################################################

@json_api
def editor_render(req:'any_') -> 'any_':
    """ The readable text form of canonical rule documents.
    """
    body = read_json(req)
    documents = required(body, 'documents')

    text = render_documents(documents)

    out = JsonResponse({'text': text})
    return out

# ################################################################################################################################

@json_api
def editor_completion(req:'any_', definition_id:'int') -> 'any_':
    """ The completion payload - every offerable term with its type, phrase, values and legal comparators.
    """
    backend = get_backend()
    vocabulary = backend.definitions.get_document(definition_id)

    terms:'dictlist' = []

    for path, attribute in iter_attributes(vocabulary):

        # Deprecated terms keep old rules running but are never offered again.
        if attribute['status'] == Status_Deprecated:
            continue

        comparators = sorted(Comparators_By_Type[attribute['type']])

        term = {
            'path':        path,
            'type':        attribute['type'],
            'phrase':      attribute['phrase'],
            'comparators': comparators,
        }

        # Choices carry their closed pick list ..
        if 'values' in attribute:
            term['values'] = attribute['values']

        # .. and ranges carry their domain.
        if 'domain' in attribute:
            term['domain'] = attribute['domain']

        terms.append(term)

    out = JsonResponse({'terms': terms})
    return out

# ################################################################################################################################

@json_api
def editor_save(req:'any_') -> 'any_':
    """ Saves one document - a new definition with its first version or a new optimistic version of an existing one.
    """
    body = read_json(req)
    document = required(body, 'document')
    comment = required(body, 'comment')

    backend = get_backend()
    actor = req.user.username

    # An existing definition gains a new optimistic version ..
    if definition_id := body.get('definition_id'):
        expected_current_version = required(body, 'expected_current_version')
        record = backend.versions.create(
            definition_id=definition_id,
            expected_current_version=expected_current_version,
            document=document,
            author=actor,
            comment=comment,
        )
        result = {'definition_id': definition_id, 'version': record.version}

    # .. while a new one comes into being together with its first version.
    else:
        name = required(body, 'name')
        object_type = required(body, 'object_type')
        created = backend.definitions.create(
            name=name,
            object_type=object_type,
            document=document,
            author=actor,
            comment=comment,
        )
        definition_id = created.id
        result = {'definition_id': created.id, 'version': created.current_version}

    # The where-used index follows every save whose document carries rule documents.
    if Documents_Key in document:
        _ = backend.references.rebuild(definition_id=definition_id, documents=document[Documents_Key])

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@json_api
def editor_outcomes(req:'any_') -> 'any_':
    """ The live-outcomes feed - the edited documents run against a test set, per-scenario results and traces included.
    """
    body = read_json(req)
    documents = required(body, 'documents')
    test_set = required(body, 'test_set')

    result = run_test_set(test_set, documents)

    out = JsonResponse(result)
    return out

# ################################################################################################################################
# ################################################################################################################################
