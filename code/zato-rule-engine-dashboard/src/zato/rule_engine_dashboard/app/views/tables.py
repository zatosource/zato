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
from zato.common.rule_engine.table import validate_table
from zato.common.rule_engine.table_compile import compile_table
from zato.common.rule_engine.table_checks import check_conflicts, check_subsumption, check_unreachable
from zato.common.rule_engine.table_completeness import check_completeness
from zato.common.rule_engine.table_reading import table_readings
from zato.common.rule_engine.table_shape import compress_table, expand_table
from zato.common.util.logging_ import count_text
from zato.rule_engine_dashboard.app.views.api import json_api, note_answer, read_json, required

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
        findings_text = count_text(len(errors), 'finding', 'findings')
        note_answer(req, f'the table does not hold together, {findings_text}')
        out = JsonResponse({'errors': errors}, status=BAD_REQUEST)
    else:
        out = table

    return out

# ################################################################################################################################

@json_api
def table_validate(req:'any_') -> 'any_':
    """ Structural validation of one decision-table document, with how every cell of it reads back.

    The readings travel with the errors because the screen speaks its sentences and its unfold
    hints from them - the cell grammar lives here alone, so there is nothing to keep in step.
    """
    body = read_json(req)
    table = required(body, 'table')

    errors = validate_table(table)
    readings = table_readings(table)

    findings_text = count_text(len(errors), 'finding', 'findings')
    columns_text = count_text(len(readings), 'column', 'columns')
    note_answer(req, f'{findings_text}, {columns_text} read back')

    out = JsonResponse({'errors': errors, 'readings': readings})
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

    columns_text = count_text(len(table['columns']), 'column', 'columns')
    rules_text = count_text(len(documents), 'rule', 'rules')
    note_answer(req, f'{columns_text} compiled into {rules_text}')

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

    completeness = check_completeness(table)
    conflicts = check_conflicts(table)
    subsumption = check_subsumption(table)
    unreachable = check_unreachable(table)

    gaps_text = count_text(len(completeness['missing']), 'gap', 'gaps')
    conflicts_text = count_text(len(conflicts['conflicts']), 'conflict', 'conflicts')
    subsumption_text = count_text(len(subsumption), 'subsumed column', 'subsumed columns')
    unreachable_text = count_text(len(unreachable), 'unreachable column', 'unreachable columns')
    note_answer(req, f'{gaps_text}, {conflicts_text}, {subsumption_text}, {unreachable_text}')

    out = JsonResponse({
        'completeness': completeness,
        'conflicts': conflicts,
        'subsumption': subsumption,
        'unreachable': unreachable,
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

    columns_text = count_text(len(table['columns']), 'column', 'columns')
    sub_rules_text = count_text(len(documents), 'sub-rule', 'sub-rules')
    note_answer(req, f'{columns_text} expanded into {sub_rules_text}')

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

    before_text = count_text(len(table['columns']), 'column', 'columns')
    after_text = count_text(len(compressed['columns']), 'column', 'columns')
    note_answer(req, f'{before_text} merged into {after_text}')

    out = JsonResponse({'table': compressed})
    return out

# ################################################################################################################################
# ################################################################################################################################
