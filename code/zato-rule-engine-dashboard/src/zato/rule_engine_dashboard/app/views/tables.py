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
from zato.common.rule_engine.table import compile_table, validate_table
from zato.common.rule_engine.table_checks import check_conflicts, check_subsumption, check_unreachable
from zato.common.rule_engine.table_completeness import check_completeness
from zato.common.rule_engine.table_shape import compress_table, expand_table
from zato.rule_engine_dashboard.app.views.api import json_api, read_json, required

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

def _valid_table(req:'any_') -> 'anydict | JsonResponse':
    """ Returns the request's table document or, when it does not hold together, the error response to send back.
    """
    body = read_json(req)
    table = required(body, 'table')

    # Structural errors make every further check meaningless, so they end the request here.
    errors = validate_table(table)
    if errors:
        out = JsonResponse({'errors': errors}, status=BAD_REQUEST)
    else:
        out = table

    return out

# ################################################################################################################################

@json_api
def table_validate(req:'any_') -> 'any_':
    """ Structural validation of one decision-table document.
    """
    body = read_json(req)
    table = required(body, 'table')

    errors = validate_table(table)

    out = JsonResponse({'errors': errors})
    return out

# ################################################################################################################################

@json_api
def table_compile(req:'any_') -> 'any_':
    """ Compiles one decision table into the matchable rule documents the engine runs.
    """
    table = _valid_table(req)
    if isinstance(table, JsonResponse):
        return table

    documents = compile_table(table)

    out = JsonResponse({'documents': documents})
    return out

# ################################################################################################################################

@json_api
def table_checks(req:'any_') -> 'any_':
    """ The integrity checks in one answer - completeness gaps, conflicts, subsumption and unreachable columns.
    """
    table = _valid_table(req)
    if isinstance(table, JsonResponse):
        return table

    out = JsonResponse({
        'completeness': check_completeness(table),
        'conflicts': check_conflicts(table),
        'subsumption': check_subsumption(table),
        'unreachable': check_unreachable(table),
    })
    return out

# ################################################################################################################################

@json_api
def table_expand(req:'any_') -> 'any_':
    """ Expands one decision table into dotted sub-rule documents.
    """
    table = _valid_table(req)
    if isinstance(table, JsonResponse):
        return table

    documents = expand_table(table)

    out = JsonResponse({'documents': documents})
    return out

# ################################################################################################################################

@json_api
def table_compress(req:'any_') -> 'any_':
    """ Compresses one decision table by merging columns that only differ in one row.
    """
    table = _valid_table(req)
    if isinstance(table, JsonResponse):
        return table

    compressed = compress_table(table)

    out = JsonResponse({'table': compressed})
    return out

# ################################################################################################################################
# ################################################################################################################################
