# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The executive measures of the MCP healthcare demo - what each one means, in which direction it is better
# and what its target is - and the assessments, statistics and correlations the services report them with.

# stdlib
from math import atanh, sqrt
from statistics import correlation, mean
from typing import NamedTuple

# Zato
from zato.common.typing_ import dict_, list_
from zato.server.demo_mcp.common import Service_Care_Flow, Service_Daily_Care_Flow, Service_Finance, Service_Quality, \
    Service_Workforce

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, callable_, floatnone, stranydict, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

floatlist          = list_[float]
strmeasuredict     = dict_[str, 'Measure']
strmeasuredictdict = dict_[str, strmeasuredict]

# ################################################################################################################################
# ################################################################################################################################

# The direction in which a measure is better
Better_Higher  = 'higher'
Better_Lower   = 'lower'
Better_Neither = 'neither'

# What kind of bound a target is - a measure that is better higher has a minimum, one that is better lower has a maximum
Target_Minimum = 'minimum'
Target_Maximum = 'maximum'

# Whether a value meets its target
Status_Meets  = 'meets_target'
Status_Misses = 'misses_target'

# How a measure changed from the previous period
Trend_Improved  = 'improved'
Trend_Worsened  = 'worsened'
Trend_Increased = 'increased'
Trend_Decreased = 'decreased'
Trend_Unchanged = 'unchanged'

# What a correlation is reported as when it cannot be computed or is not statistically significant
Relationship_Not_Computable = 'not_computable'
Relationship_None_Detected  = 'none_detected'

# ################################################################################################################################
# ################################################################################################################################

# The fewest days a correlation is computed for
_min_correlation_days = 4

# The two-sided 95 percent critical value of the standard normal distribution,
# compared with the Fisher transformation of a correlation coefficient
_significance_critical_value = 1.96

# The absolute coefficients from which a significant correlation is moderate or strong
_moderate_correlation = 0.3
_strong_correlation   = 0.5

# The names of the strengths and the directions of a significant correlation
_strength_weak       = 'weak'
_strength_moderate   = 'moderate'
_strength_strong     = 'strong'
_direction_positive  = 'positive'
_direction_negative  = 'negative'

# The decimal places every reported figure is rounded to
_figure_precision = 1
_coefficient_precision = 2

# ################################################################################################################################
# ################################################################################################################################

class Measure(NamedTuple):
    """ One executive measure - what it means, in which direction it is better and, if it has one, its target.
    """
    description: 'str'
    better: 'str'
    target: 'floatnone' = None

# ################################################################################################################################
# ################################################################################################################################

# The groups of measures, each reported by a service of its own
Group_Care_Flow = 'care_flow'
Group_Quality   = 'quality'
Group_Workforce = 'workforce'
Group_Finance   = 'finance'

# Every measure of a reporting period, by its group and by the name the services report it under
Measures_By_Group:'strmeasuredictdict' = {

    Group_Care_Flow: {
        'referrals': Measure('Referrals received in the period', Better_Neither),
        'first_appointments': Measure('First appointments held in the period', Better_Neither),
        'referral_conversion_percent': Measure('First appointments as a percentage of referrals', Better_Higher),
        'discharges': Measure('Patients discharged in the period', Better_Neither),
        'waiting_patients': Measure(
            'Patients waiting on an average day, added up across the facilities covered', Better_Lower),
        'median_wait_days': Measure(
            'Daily median waiting time in days, averaged over the days and the facilities covered', Better_Lower, 14.0),
        'capacity_used_percent': Measure(
            'Percentage of service capacity in use on an average day', Better_Higher, 90.0),
    },

    Group_Quality: {
        'safety_events': Measure('Safety events recorded in the period', Better_Lower),
        'complaints': Measure('Complaints received in the period', Better_Lower),
        'outcome_assessments': Measure('Care outcome assessments completed in the period', Better_Neither),
        'positive_outcome_percent': Measure(
            'Positive outcomes as a percentage of outcome assessments', Better_Higher, 85.0),
        'overdue_actions': Measure(
            'Overdue improvement actions on an average day, added up across the facilities covered', Better_Lower, 0.0),
    },

    Group_Workforce: {
        'planned_hours': Measure('Staff hours planned in the period', Better_Neither),
        'worked_hours': Measure('Staff hours worked in the period', Better_Neither),
        'staffing_percent': Measure('Worked hours as a percentage of planned hours', Better_Higher, 95.0),
        'absence_percent': Measure('Absence hours as a percentage of planned hours', Better_Lower, 6.0),
        'agency_percent': Measure('Agency hours as a percentage of worked hours', Better_Lower, 10.0),
        'vacancies': Measure(
            'Open posts on an average day, added up across the facilities covered - a count of posts, not a percentage',
            Better_Lower),
    },

    Group_Finance: {
        'contract_value': Measure(
            'Contracted value of the period, a monetary amount with no currency recorded', Better_Neither),
        'delivered_value': Measure(
            'Value of the care delivered in the period, a monetary amount with no currency recorded', Better_Neither),
        'registered_value': Measure(
            'Value of the care registered in the period, a monetary amount with no currency recorded', Better_Neither),
        'billed_value': Measure(
            'Value billed in the period, a monetary amount with no currency recorded', Better_Neither),
        'operating_cost': Measure(
            'Operating cost of the period, a monetary amount with no currency recorded', Better_Neither),
        'plan_percent': Measure('Delivered value as a percentage of contracted value', Better_Higher, 100.0),
        'registration_percent': Measure('Registered value as a percentage of delivered value', Better_Higher, 98.0),
        'billing_percent': Measure('Billed value as a percentage of registered value', Better_Higher),
        'margin_percent': Measure(
            'Delivered value less operating cost, as a percentage of delivered value', Better_Higher, 8.0),
    },
}

# Every measure of a reporting period, by the name the services report it under
Measures:'strmeasuredict' = {}

for _group_measures in Measures_By_Group.values():
    Measures.update(_group_measures)

# What each care-flow measure means in a row of one facility and one day
Daily_Care_Flow_Descriptions:'strstrdict' = {
    'referrals': 'Referrals received on the day',
    'first_appointments': 'First appointments held on the day',
    'discharges': 'Patients discharged on the day',
    'waiting_patients': 'Patients waiting on the day',
    'median_wait_days': 'Median waiting time on the day, in days',
    'capacity_used_percent': 'Percentage of service capacity in use on the day',
}

# The daily measure every other daily measure is correlated with
Correlated_Measure = 'median_wait_days'

# The group the daily care-flow measures are listed under
Group_Daily_Care_Flow = 'daily_care_flow'

# The service that reports each group of measures
_group_services:'strstrdict' = {
    Group_Care_Flow: Service_Care_Flow,
    Group_Quality: Service_Quality,
    Group_Workforce: Service_Workforce,
    Group_Finance: Service_Finance,
}

# ################################################################################################################################
# ################################################################################################################################

def _round(value:'float', precision:'int') -> 'float':
    """ Rounds a figure for the report, with a negative value that rounds to zero reported as zero.
    """
    out = round(value, precision)

    if out == 0:
        out = 0.0

    return out

# ################################################################################################################################

def _get_target_kind(measure:'Measure') -> 'str':
    """ Returns whether the target of a measure is a minimum or a maximum.
    """
    if measure.better == Better_Higher:
        out = Target_Minimum
    else:
        out = Target_Maximum

    return out

# ################################################################################################################################

def get_status(measure:'Measure', target:'float', value:'float') -> 'str':
    """ Returns whether a value of a measure meets the measure's target.
    """
    target_kind = _get_target_kind(measure)

    if target_kind == Target_Minimum:
        meets_target = value >= target
    else:
        meets_target = value <= target

    if meets_target:
        out = Status_Meets
    else:
        out = Status_Misses

    return out

# ################################################################################################################################

def _get_trend(measure:'Measure', change:'float') -> 'str':
    """ Returns how a measure changed - improved or worsened when it has a better direction,
    increased or decreased when it does not.
    """
    if change == 0:
        out = Trend_Unchanged

    elif measure.better == Better_Neither:
        if change > 0:
            out = Trend_Increased
        else:
            out = Trend_Decreased

    else:
        is_increase = change > 0
        is_higher_better = measure.better == Better_Higher

        if is_increase == is_higher_better:
            out = Trend_Improved
        else:
            out = Trend_Worsened

    return out

# ################################################################################################################################

def _add_target(record:'stranydict', measure:'Measure', value:'float') -> 'None':
    """ Adds the target of a measure to a record, together with the status of the value, if the measure has a target.
    """
    if measure.target is None:
        return

    record['target'] = measure.target
    record['target_kind'] = _get_target_kind(measure)
    record['status'] = get_status(measure, measure.target, value)

# ################################################################################################################################

def get_assessment(current:'anydict', previous:'anydict') -> 'stranydict':
    """ Returns the assessment of every measure of a summary - its definition, both values, the change,
    the trend and, for a measure with a target, the target and whether the current value meets it.
    """
    out:'stranydict' = {}

    for name, value in current.items():

        measure = Measures[name]
        previous_value = previous[name]

        # The change is rounded before the trend is derived from it, so a change reported as 0.0 is unchanged ..
        difference = value - previous_value
        change = _round(difference, _figure_precision)

        # .. and a measure with a target additionally states whether the current value meets it.
        record:'stranydict' = {
            'description': measure.description,
            'current': value,
            'previous': previous_value,
            'change': change,
            'trend': _get_trend(measure, change),
        }

        _add_target(record, measure, value)

        out[name] = record

    return out

# ################################################################################################################################

def _get_measure_record(
    name:'str',
    group:'str',
    service_name:'str',
    description:'str',
    measure:'Measure',
    ) -> 'stranydict':
    """ Returns how one measure is listed - its name, group, the service that reports it, its definition,
    the direction in which it is better and, for a measure with a target, the target and its kind.
    """
    out:'stranydict' = {
        'name': name,
        'group': group,
        'reported_by': service_name,
        'description': description,
        'better': measure.better,
    }

    if measure.target is not None:
        out['target'] = measure.target
        out['target_kind'] = _get_target_kind(measure)

    return out

# ################################################################################################################################

def list_measures() -> 'anylist':
    """ Returns every measure the services report, the measures of a period first, the daily ones after them.
    """
    out:'anylist' = []

    # The measures of a period are listed group by group ..
    for group, group_measures in Measures_By_Group.items():

        service_name = _group_services[group]

        for name, measure in group_measures.items():
            record = _get_measure_record(name, group, service_name, measure.description, measure)
            out.append(record)

    # .. and the daily ones keep the direction and the target of the period measure of the same name.
    for name, description in Daily_Care_Flow_Descriptions.items():

        measure = Measures[name]

        record = _get_measure_record(name, Group_Daily_Care_Flow, Service_Daily_Care_Flow, description, measure)
        out.append(record)

    return out

# ################################################################################################################################

def assess(summarize:'callable_', current:'anylist', previous:'anylist') -> 'stranydict':
    """ Returns the assessment of one group of measures from the facility rows of both periods.
    """
    current_summary  = summarize(current)
    previous_summary = summarize(previous)

    out = get_assessment(current_summary, previous_summary)
    return out

# ################################################################################################################################

def get_report(
    period:'anydict',
    facility_code:'str',
    facilities:'stranydict',
    summarize:'callable_',
    current:'anylist',
    previous:'anylist',
    ) -> 'stranydict':
    """ Returns the report of one group of measures - the assessment of the facilities covered,
    together with the details of the one facility requested or the figures of every facility.
    """
    out:'stranydict' = {
        'period': period,
        'assessment': assess(summarize, current, previous),
    }

    # A report on one facility names it, its figures are those of the assessment ..
    if facility_code:
        out['facility'] = facilities[facility_code]

    # .. while a report on the whole network lists the figures of each facility.
    else:
        out['facilities'] = {
            'current': current,
            'previous': previous,
        }

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_dates_of(rows:'anylist', name:'str', value:'float') -> 'strlist':
    """ Returns the report dates of the rows in which a measure has the given value.
    """
    out:'strlist' = []

    for row in rows:
        if row[name] == value:
            out.append(row['report_date'])

    return out

# ################################################################################################################################

def _get_values(rows:'anylist', name:'str') -> 'floatlist':
    """ Returns the values of one measure from daily rows, in the order of the rows.
    """
    out:'floatlist' = []

    for row in rows:
        out.append(row[name])

    return out

# ################################################################################################################################

def get_daily_statistics(rows:'anylist') -> 'stranydict':
    """ Returns the average, the minimum and the maximum of every daily care-flow measure, with the dates
    of each extreme, and, for a measure with a target, how many days meet and miss the target.
    """
    out:'stranydict' = {}

    for name, description in Daily_Care_Flow_Descriptions.items():

        # Each extreme lists every date it occurred on ..
        values = _get_values(rows, name)
        minimum = min(values)
        maximum = max(values)
        average = mean(values)

        record:'stranydict' = {
            'description': description,
            'average': _round(average, _figure_precision),
            'minimum': minimum,
            'minimum_dates': _get_dates_of(rows, name, minimum),
            'maximum': maximum,
            'maximum_dates': _get_dates_of(rows, name, maximum),
        }

        measure = Measures[name]

        # .. and a measure with a target counts the days that meet it.
        if measure.target is not None:

            days_meeting_target = 0

            for value in values:
                if get_status(measure, measure.target, value) == Status_Meets:
                    days_meeting_target += 1

            record['target'] = measure.target
            record['target_kind'] = _get_target_kind(measure)
            record['days_meeting_target'] = days_meeting_target
            record['days_missing_target'] = len(values) - days_meeting_target

        out[name] = record

    return out

# ################################################################################################################################

def add_daily_statuses(rows:'anylist') -> 'anylist':
    """ Adds to each daily row whether each of its measures with a target meets the target.
    """
    for row in rows:
        for name in Daily_Care_Flow_Descriptions:

            measure = Measures[name]

            if measure.target is not None:
                row[f'{name}_status'] = get_status(measure, measure.target, row[name])

    out = rows
    return out

# ################################################################################################################################

def _get_relationship(coefficient:'float', day_count:'int') -> 'str':
    """ Describes a correlation coefficient - none detected when it is not significant at the 95 percent level,
    otherwise its strength and its direction, e.g. strong_negative.
    """
    strength = abs(coefficient)

    # A perfect correlation is significant, its Fisher transformation is infinite ..
    if strength == 1:
        is_significant = True

    # .. any other one is tested through the Fisher transformation, whose standard error is 1 / sqrt(n - 3) ..
    else:
        fisher_value = atanh(coefficient)
        standard_score = abs(fisher_value) * sqrt(day_count - 3)
        is_significant = standard_score >= _significance_critical_value

    # .. a correlation that is not significant names no relationship ..
    if not is_significant:
        out = Relationship_None_Detected

    # .. while a significant one is named by its strength and direction.
    else:
        if strength >= _strong_correlation:
            strength_name = _strength_strong
        elif strength >= _moderate_correlation:
            strength_name = _strength_moderate
        else:
            strength_name = _strength_weak

        if coefficient > 0:
            direction_name = _direction_positive
        else:
            direction_name = _direction_negative

        out = f'{strength_name}_{direction_name}'

    return out

# ################################################################################################################################

def get_daily_correlations(rows:'anylist') -> 'stranydict':
    """ Returns the Pearson correlation of the correlated measure with every other daily care-flow measure,
    with a description of each that names a relationship only when the correlation is statistically significant.
    """
    out:'stranydict' = {}

    day_count = len(rows)
    correlated_values = _get_values(rows, Correlated_Measure)

    for name in Daily_Care_Flow_Descriptions:

        if name == Correlated_Measure:
            continue

        values = _get_values(rows, name)

        has_enough_days = day_count >= _min_correlation_days
        has_variation = len(set(values)) > 1
        has_correlated_variation = len(set(correlated_values)) > 1

        # A correlation is defined only for enough days with values that vary on both sides ..
        is_computable = False

        if has_enough_days:
            if has_variation:
                if has_correlated_variation:
                    is_computable = True

        # .. a defined one is tested before it is rounded for the report ..
        if is_computable:
            coefficient = correlation(correlated_values, values)
            relationship = _get_relationship(coefficient, day_count)
            coefficient = _round(coefficient, _coefficient_precision)

        # .. while an undefined one is reported as such.
        else:
            coefficient = None
            relationship = Relationship_Not_Computable

        out[name] = {
            'coefficient': coefficient,
            'relationship': relationship,
        }

    return out

# ################################################################################################################################
# ################################################################################################################################
