# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rules.outcome_diff import outcome_diff
from zato.common.rules.testing import evaluate_input, load_documents
from zato.common.rules.vocabulary import ErrorCode, new_error

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

class KpiKind:
    """ The aggregations a KPI definition can ask for.
    """
    Count     = 'count'      # How many outcomes assign the field a given value
    Rate      = 'rate'       # The count as a share of every evaluated scenario
    Sum       = 'sum'        # The total of a numeric field across outcomes
    Average   = 'average'    # The mean of a numeric field across outcomes
    Breakdown = 'breakdown'  # How many outcomes fall on each value of a field

# All the kinds a KPI definition may carry.
Kpi_Kinds = {KpiKind.Count, KpiKind.Rate, KpiKind.Sum, KpiKind.Average, KpiKind.Breakdown}

# The kinds that compare a field against a declared value.
_value_kinds = {KpiKind.Count, KpiKind.Rate}

# ################################################################################################################################
# ################################################################################################################################

def validate_kpis(kpis:'dictlist') -> 'dictlist':
    """ Validates KPI definitions structurally, returning parser-shaped findings.
    """

    # Our response to produce
    errors = []

    for kpi in kpis:
        name = kpi['name']

        if not name:
            errors.append(new_error('', 'kpi', 'name', ErrorCode.Bad_Kpi, 'A KPI needs a name'))
            continue

        if kpi['kind'] not in Kpi_Kinds:
            errors.append(new_error(name, 'kpi', 'kind', ErrorCode.Bad_Kpi, f'Not a recognized KPI kind -> `{kpi["kind"]}`'))
            continue

        if not kpi['field']:
            errors.append(new_error(name, 'kpi', 'field', ErrorCode.Bad_Kpi, 'A KPI needs a field to aggregate'))
            continue

        # Counts and rates compare against a value, so they have to declare one.
        if kpi['kind'] in _value_kinds:
            if 'value' not in kpi:
                errors.append(new_error(name, 'kpi', 'value', ErrorCode.Bad_Kpi, f'A {kpi["kind"]} KPI needs a value to count'))

    return errors

# ################################################################################################################################
# ################################################################################################################################

def _update_count(kpi:'anydict', state:'anydict', outcome:'anydict') -> 'None':
    """ Counts the outcomes that assign the field the declared value.
    """
    field = kpi['field']

    if field in outcome:
        if outcome[field] == kpi['value']:
            state['count'] += 1

# ################################################################################################################################

def _update_sum(kpi:'anydict', state:'anydict', outcome:'anydict') -> 'None':
    """ Totals a numeric field across the outcomes that assign it.
    """
    field = kpi['field']

    if field in outcome:
        state['total'] += outcome[field]
        state['count'] += 1

# ################################################################################################################################

def _update_breakdown(kpi:'anydict', state:'anydict', outcome:'anydict') -> 'None':
    """ Buckets the outcomes by the value they assign the field.
    """
    field = kpi['field']

    if field in outcome:
        value = outcome[field]
        buckets = state['buckets']

        if value not in buckets:
            buckets[value] = 0
        buckets[value] += 1

# ################################################################################################################################

# How each KPI kind folds one outcome into its running state.
_kpi_updates = {
    KpiKind.Count: _update_count,
    KpiKind.Rate: _update_count,
    KpiKind.Sum: _update_sum,
    KpiKind.Average: _update_sum,
    KpiKind.Breakdown: _update_breakdown,
}

# ################################################################################################################################

def _finalize_kpi(kpi:'anydict', state:'anydict', evaluated:'int') -> 'any_':
    """ Turns a KPI's running state into its final value once every scenario has run.
    """
    kind = kpi['kind']

    if kind == KpiKind.Count:
        out = state['count']

    elif kind == KpiKind.Rate:

        # A run where nothing evaluated has no meaningful share.
        if evaluated == 0:
            out = 0.0
        else:
            out = state['count'] / evaluated

    elif kind == KpiKind.Sum:
        out = state['total']

    elif kind == KpiKind.Average:

        # An average over no assignments has no meaningful value.
        if state['count'] == 0:
            out = 0.0
        else:
            out = state['total'] / state['count']

    else:
        out = state['buckets']

    return out

# ################################################################################################################################
# ################################################################################################################################

def simulate(documents:'anydict', scenarios:'dictlist', kpis:'dictlist') -> 'anydict':
    """ Runs one rule version over many scenarios, folding each outcome into the KPIs as it comes.

    This is the batch loop over imported or captured inputs - every scenario is
    evaluated once, the KPI states update incrementally instead of holding every
    outcome in memory, and a scenario the rules cannot evaluate is reported and
    skipped, it never stops the batch.
    """
    loaded = load_documents(documents)

    # One running state per KPI, updated as the outcomes come.
    states = []
    for kpi in kpis:
        states.append({'count': 0, 'total': 0.0, 'buckets': {}})

    results = []
    evaluated_count = 0
    error_count = 0

    for scenario in scenarios:
        evaluated = evaluate_input(loaded, scenario['input'])

        outcome = evaluated['actual']
        error = evaluated['error']

        fired = []
        for entry in evaluated['fired']:
            fired.append(entry['rule'])

        results.append({'scenario': scenario['name'], 'outcome': outcome, 'fired': fired, 'error': error})

        # A scenario that did not evaluate contributes to no KPI.
        if error:
            error_count += 1
            continue

        evaluated_count += 1

        # Fold this outcome into every KPI's running state.
        for index, kpi in enumerate(kpis):
            update = _kpi_updates[kpi['kind']]
            update(kpi, states[index], outcome)

    # With the batch done, every KPI state turns into its final value.
    kpi_results = []
    for index, kpi in enumerate(kpis):
        value = _finalize_kpi(kpi, states[index], evaluated_count)
        kpi_results.append({'name': kpi['name'], 'kind': kpi['kind'], 'value': value})

    # Our response to produce
    out = {
        'total': len(results),
        'evaluated': evaluated_count,
        'errors': error_count,
        'kpis': kpi_results,
        'scenarios': results,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

def champion_challenger(champion_documents:'anydict', challenger_documents:'anydict', scenarios:'dictlist', kpis:'dictlist') -> 'anydict':
    """ Runs two rule versions against the same scenarios, results and KPIs side by side.

    The champion is what runs today, the challenger is what might replace it. Both
    simulate over the same inputs with the same KPIs, and the outcome diff explains
    which decisions the challenger would change and through which rules.
    """

    # Our response to produce
    out = {
        'champion': simulate(champion_documents, scenarios, kpis),
        'challenger': simulate(challenger_documents, scenarios, kpis),
        'diff': outcome_diff(champion_documents, challenger_documents, scenarios),
    }
    return out

# ################################################################################################################################
# ################################################################################################################################
