# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST

# Django
from django.http import JsonResponse

# Zato
from zato.common.rule_engine import webapi
from zato.common.rule_engine.webapi import DocumentInvalidError
from zato.common.util.logging_ import count_text
from zato.rule_engine_dashboard.app.storage import get_backend
from zato.rule_engine_dashboard.app.views.api import json_api, note_answer, read_json

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

@json_api
def editor_validate(req:'any_') -> 'any_':
    """ Parses typed rules and, against a named vocabulary, checks their semantics too.
    """
    body = read_json(req)
    result, note = webapi.validate_rules(get_backend(), body)
    note_answer(req, note)

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@json_api
def editor_render(req:'any_') -> 'any_':
    """ The readable text form of canonical rule documents.
    """
    body = read_json(req)
    result, note = webapi.render_rules(body)
    note_answer(req, note)

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@json_api
def editor_completion(req:'any_', definition_id:'int') -> 'any_':
    """ The completion payload - every offerable term with its type, phrase, values and legal comparators.
    """
    result, note = webapi.completion_terms(get_backend(), definition_id)
    note_answer(req, note)

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@json_api
def editor_save(req:'any_') -> 'any_':
    """ Saves one document - a new definition with its first version or a new optimistic version of an existing one.
    """
    body = read_json(req)

    # A document that fails its type's validation answers with the findings, nothing is stored.
    try:
        result, note = webapi.save_document(get_backend(), body, req.user.username)
    except DocumentInvalidError as e:
        findings_text = count_text(len(e.errors), 'finding', 'findings')
        note_answer(req, f'not stored, {findings_text}')

        out = JsonResponse({'errors': e.errors}, status=BAD_REQUEST)
        return out

    note_answer(req, note)

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@json_api
def editor_outcomes(req:'any_') -> 'any_':
    """ The live-outcomes feed - the edited documents run against a test set, per-scenario results and traces included.
    """
    body = read_json(req)
    result, note = webapi.run_outcomes(body)
    note_answer(req, note)

    out = JsonResponse(result)
    return out

# ################################################################################################################################
# ################################################################################################################################
