# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The executive reporting services of the MCP healthcare demo. The importer deploys this file
# through the hot-deployment directory, and the demo MCP gateway exposes each service as one tool.

# stdlib
from datetime import date, timedelta

# Zato
from zato.server.demo_mcp.common import Service_Care_Flow, Service_Daily_Care_Flow, Service_Finance, \
    Service_List_Cities, Service_List_Facilities, Service_List_Measures, Service_List_Regions, Service_Quality, \
    Service_Scorecard, Service_Workforce, SQL_Finance, SQL_Warehouse, SQL_Workforce
from zato.server.demo_mcp.measures import add_daily_statuses, assess, Correlated_Measure, \
    get_daily_correlations, get_daily_statistics, get_report, list_measures
from zato.server.demo_mcp.queries import get_care_flow, get_daily_care_flow, get_facilities, get_finance, \
    get_quality, get_workforce
from zato.server.service import Int, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anytuple, stranydict

# ################################################################################################################################
# ################################################################################################################################

# How many days each reporting period covers unless a request says otherwise
_default_days = 7
_max_days     = 28

# ################################################################################################################################
# ################################################################################################################################

def _resolve_days(days:'int') -> 'int':
    """ Returns a valid reporting-period length.
    """
    if days < 1:
        raise Exception('The reporting period must contain at least one day')

    if days > _max_days:
        raise Exception(f'The reporting period cannot exceed {_max_days} days')

    out = days
    return out

# ################################################################################################################################

def _get_period(days:'int') -> 'anydict':
    """ Returns the current reporting period and the preceding period of the same length.
    """
    current_until  = date.today()
    current_since  = current_until - timedelta(days=days - 1)
    previous_until = current_since - timedelta(days=1)
    previous_since = previous_until - timedelta(days=days - 1)

    out = {
        'days': days,
        'current_since': current_since.isoformat(),
        'current_until': current_until.isoformat(),
        'previous_since': previous_since.isoformat(),
        'previous_until': previous_until.isoformat(),
    }
    return out

# ################################################################################################################################

def _get_percentage(numerator:'float', denominator:'float') -> 'float':
    """ Returns one number as a percentage of another.
    """
    if denominator == 0:
        out = 100.0
    else:
        out = round(numerator * 100 / denominator, 1)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _add_facility_details(rows:'anylist', facilities:'stranydict') -> 'anylist':
    """ Adds facility names and regions to reporting rows.
    """
    for row in rows:
        facility = facilities[row['facility_code']]
        row['facility_name'] = facility['name']
        row['region'] = facility['region']

    out = rows
    return out

# ################################################################################################################################

def _add_care_flow_measures(rows:'anylist') -> 'anylist':
    """ Adds care-flow percentages to facility rows.
    """
    for row in rows:
        row['referral_conversion_percent'] = _get_percentage(row['first_appointments'], row['referrals'])

    out = rows
    return out

# ################################################################################################################################

def _add_quality_measures(rows:'anylist') -> 'anylist':
    """ Adds quality percentages to facility rows.
    """
    for row in rows:
        row['positive_outcome_percent'] = _get_percentage(row['positive_outcomes'], row['outcome_assessments'])

    out = rows
    return out

# ################################################################################################################################

def _add_workforce_measures(rows:'anylist') -> 'anylist':
    """ Adds workforce percentages to facility rows.
    """
    for row in rows:
        row['staffing_percent'] = _get_percentage(row['worked_hours'], row['planned_hours'])
        row['absence_percent'] = _get_percentage(row['absence_hours'], row['planned_hours'])
        row['agency_percent'] = _get_percentage(row['agency_hours'], row['worked_hours'])

    out = rows
    return out

# ################################################################################################################################

def _add_finance_measures(rows:'anylist') -> 'anylist':
    """ Adds financial percentages to facility rows.
    """
    for row in rows:
        margin_value = row['delivered_value'] - row['operating_cost']

        row['plan_percent'] = _get_percentage(row['delivered_value'], row['contract_value'])
        row['registration_percent'] = _get_percentage(row['registered_value'], row['delivered_value'])
        row['billing_percent'] = _get_percentage(row['billed_value'], row['registered_value'])
        row['margin_percent'] = _get_percentage(margin_value, row['delivered_value'])

    out = rows
    return out

# ################################################################################################################################

def _require_rows(rows:'anylist', facility_code:'str') -> 'None':
    """ Requires the requested reporting scope to contain data.
    """
    if rows:
        return

    raise Exception(f'No reporting data found for facility code `{facility_code}`')

# ################################################################################################################################

def _sum(rows:'anylist', field_name:'str') -> 'float':
    """ Returns the sum of one numeric field.
    """
    out = 0.0

    for row in rows:
        out += row[field_name]

    return out

# ################################################################################################################################

def _average(rows:'anylist', field_name:'str') -> 'float':
    """ Returns the average of one numeric field.
    """
    total = _sum(rows, field_name)

    out = round(total / len(rows), 1)
    return out

# ################################################################################################################################

def _summarize_care_flow(rows:'anylist') -> 'anydict':
    """ Returns network-level care-flow measures from facility rows.
    """
    referrals          = _sum(rows, 'referrals')
    first_appointments = _sum(rows, 'first_appointments')

    out = {
        'referrals': referrals,
        'first_appointments': first_appointments,
        'referral_conversion_percent': _get_percentage(first_appointments, referrals),
        'discharges': _sum(rows, 'discharges'),
        'waiting_patients': _sum(rows, 'waiting_patients'),
        'median_wait_days': _average(rows, 'median_wait_days'),
        'capacity_used_percent': _average(rows, 'capacity_used_percent'),
    }
    return out

# ################################################################################################################################

def _summarize_quality(rows:'anylist') -> 'anydict':
    """ Returns network-level quality measures from facility rows.
    """
    assessments       = _sum(rows, 'outcome_assessments')
    positive_outcomes = _sum(rows, 'positive_outcomes')

    out = {
        'safety_events': _sum(rows, 'safety_events'),
        'complaints': _sum(rows, 'complaints'),
        'outcome_assessments': assessments,
        'positive_outcome_percent': _get_percentage(positive_outcomes, assessments),
        'overdue_actions': _sum(rows, 'overdue_actions'),
    }
    return out

# ################################################################################################################################

def _summarize_workforce(rows:'anylist') -> 'anydict':
    """ Returns network-level workforce measures from facility rows.
    """
    planned_hours = _sum(rows, 'planned_hours')
    worked_hours  = _sum(rows, 'worked_hours')
    absence_hours = _sum(rows, 'absence_hours')
    agency_hours  = _sum(rows, 'agency_hours')

    out = {
        'planned_hours': planned_hours,
        'worked_hours': worked_hours,
        'staffing_percent': _get_percentage(worked_hours, planned_hours),
        'absence_percent': _get_percentage(absence_hours, planned_hours),
        'agency_percent': _get_percentage(agency_hours, worked_hours),
        'vacancies': _sum(rows, 'vacancies'),
    }
    return out

# ################################################################################################################################

def _summarize_finance(rows:'anylist') -> 'anydict':
    """ Returns network-level financial measures from facility rows.
    """
    contract_value   = _sum(rows, 'contract_value')
    delivered_value  = _sum(rows, 'delivered_value')
    registered_value = _sum(rows, 'registered_value')
    billed_value     = _sum(rows, 'billed_value')
    operating_cost   = _sum(rows, 'operating_cost')
    margin_value     = delivered_value - operating_cost

    out = {
        'contract_value': contract_value,
        'delivered_value': delivered_value,
        'registered_value': registered_value,
        'billed_value': billed_value,
        'operating_cost': operating_cost,
        'plan_percent': _get_percentage(delivered_value, contract_value),
        'registration_percent': _get_percentage(registered_value, delivered_value),
        'billing_percent': _get_percentage(billed_value, registered_value),
        'margin_percent': _get_percentage(margin_value, delivered_value),
    }
    return out

# ################################################################################################################################

def _get_period_rows(
    connection:'any_',
    getter:'any_',
    facility_code:'str',
    period:'anydict',
    ) -> 'anytuple':
    """ Returns current and previous reporting rows through the given measure function.
    """
    current = getter(
        connection,
        facility_code,
        period['current_since'],
        period['current_until'],
    )
    previous = getter(
        connection,
        facility_code,
        period['previous_since'],
        period['previous_until'],
    )

    _require_rows(current, facility_code)
    _require_rows(previous, facility_code)

    out = current, previous
    return out

# ################################################################################################################################

def _group_facilities(facilities:'stranydict', key:'str', *extra_keys:'str') -> 'anylist':
    """ Returns the facilities grouped by one of their attributes, each group with the code and name of its facilities.
    """
    groups:'stranydict' = {}

    for facility in facilities.values():

        value = facility[key]

        # The first facility of a group creates the group and copies the attributes the group shares ..
        if value not in groups:

            group:'anydict' = {key: value}

            for extra_key in extra_keys:
                group[extra_key] = facility[extra_key]

            group['facilities'] = []
            groups[value] = group

        # .. and each facility is added to its group.
        group_facilities = groups[value]['facilities']
        group_facilities.append({'code': facility['code'], 'name': facility['name']})

    out = [groups[value] for value in sorted(groups)]
    return out

# ################################################################################################################################
# ################################################################################################################################

class GetScorecard(Service):
    """ Returns the executive healthcare scorecard - care flow, quality, workforce and finance - for the current period
    and the preceding period of the same length. Omit facility_code for the whole network or pass one of the codes
    HC-01 to HC-08. Pass days for a period from 1 to 28 days, 7 by default. The assessment gives each measure its
    definition, its current and previous value, the change, whether the change is an improvement and, for a measure
    with a target, whether the current value meets the target. healthcare.list-facilities returns the code
    of each facility with its name, city and region.
    """
    name = Service_Scorecard

    input = '-facility_code', Int('-days')

    def handle(self) -> 'None':

        days          = _resolve_days(self.request.input.days or _default_days)
        facility_code = self.request.input.facility_code
        period        = _get_period(days)

        warehouse = self.out.sql[SQL_Warehouse]
        finance   = self.out.sql[SQL_Finance]
        workforce = self.out.sql[SQL_Workforce]

        current_care, previous_care             = _get_period_rows(warehouse, get_care_flow, facility_code, period)
        current_quality, previous_quality       = _get_period_rows(warehouse, get_quality, facility_code, period)
        current_workforce, previous_workforce   = _get_period_rows(workforce, get_workforce, facility_code, period)
        current_finance, previous_finance       = _get_period_rows(finance, get_finance, facility_code, period)

        facilities = get_facilities(warehouse)

        self.response.payload = {
            'period': period,
            'facility_count': len(current_care),
            'facilities': facilities,
            'assessment': {
                'care_flow': assess(_summarize_care_flow, current_care, previous_care),
                'quality': assess(_summarize_quality, current_quality, previous_quality),
                'workforce': assess(_summarize_workforce, current_workforce, previous_workforce),
                'finance': assess(_summarize_finance, current_finance, previous_finance),
            },
        }

# ################################################################################################################################

class TrackCareFlow(Service):
    """ Reports referrals, first appointments, discharges, waiting patients, waiting time and capacity use
    for the current period and the preceding period of the same length. Omit facility_code for the whole network
    or pass one of the codes HC-01 to HC-08. Pass days for a period from 1 to 28 days, 7 by default.
    The assessment gives each measure its definition, its current and previous value, the change, whether the change
    is an improvement and, for a measure with a target, whether the current value meets the target.
    For the figures of each day, use healthcare.get-daily-care-flow. healthcare.list-facilities returns the code
    of each facility with its name, city and region.
    """
    name = Service_Care_Flow

    input = '-facility_code', Int('-days')

    def handle(self) -> 'None':

        days          = _resolve_days(self.request.input.days or _default_days)
        facility_code = self.request.input.facility_code
        period        = _get_period(days)

        warehouse = self.out.sql[SQL_Warehouse]
        facilities = get_facilities(warehouse)

        current, previous = _get_period_rows(warehouse, get_care_flow, facility_code, period)
        current           = _add_facility_details(current, facilities)
        previous          = _add_facility_details(previous, facilities)
        current           = _add_care_flow_measures(current)
        previous          = _add_care_flow_measures(previous)

        self.response.payload = get_report(period, facility_code, facilities, _summarize_care_flow, current, previous)

# ################################################################################################################################

class GetDailyCareFlow(Service):
    """ Returns one row per day of referrals, first appointments, discharges, waiting patients, median waiting time
    and capacity use for one facility, with the average, minimum and maximum of each measure, the number of days
    that meet and miss each target, and the correlation of the median waiting time with each other measure,
    which names a relationship only when the correlation is statistically significant. Pass facility_code,
    one of the codes HC-01 to HC-08, and days for a period from 1 to 28 days, 7 by default.
    healthcare.list-facilities returns the code of each facility with its name, city and region.
    """
    name = Service_Daily_Care_Flow

    input = 'facility_code', Int('-days')

    def handle(self) -> 'None':

        days          = _resolve_days(self.request.input.days or _default_days)
        facility_code = self.request.input.facility_code
        period        = _get_period(days)

        since = period['current_since']
        until = period['current_until']

        warehouse  = self.out.sql[SQL_Warehouse]
        facilities = get_facilities(warehouse)

        # The breakdown covers the current period only ..
        rows = get_daily_care_flow(warehouse, facility_code, since, until)
        _require_rows(rows, facility_code)

        # .. its figures are computed from the rows ..
        statistics   = get_daily_statistics(rows)
        correlations = get_daily_correlations(rows)

        # .. and each row states whether its own values meet their targets.
        rows = add_daily_statuses(rows)

        self.response.payload = {
            'period': {
                'days': days,
                'since': since,
                'until': until,
            },
            'facility': facilities[facility_code],
            'statistics': statistics,
            f'{Correlated_Measure}_correlations': correlations,
            'rows': rows,
        }

# ################################################################################################################################

class ReviewQuality(Service):
    """ Reports care outcomes, safety events, complaints and overdue actions for the current period
    and the preceding period of the same length. Omit facility_code for the whole network or pass one of the codes
    HC-01 to HC-08. Pass days for a period from 1 to 28 days, 7 by default. The assessment gives each measure
    its definition, its current and previous value, the change, whether the change is an improvement and,
    for a measure with a target, whether the current value meets the target. healthcare.list-facilities returns
    the code of each facility with its name, city and region.
    """
    name = Service_Quality

    input = '-facility_code', Int('-days')

    def handle(self) -> 'None':

        days          = _resolve_days(self.request.input.days or _default_days)
        facility_code = self.request.input.facility_code
        period        = _get_period(days)

        warehouse = self.out.sql[SQL_Warehouse]
        facilities = get_facilities(warehouse)

        current, previous = _get_period_rows(warehouse, get_quality, facility_code, period)
        current           = _add_facility_details(current, facilities)
        previous          = _add_facility_details(previous, facilities)
        current           = _add_quality_measures(current)
        previous          = _add_quality_measures(previous)

        self.response.payload = get_report(period, facility_code, facilities, _summarize_quality, current, previous)

# ################################################################################################################################

class AssessWorkforce(Service):
    """ Reports staffing coverage, absence, agency work and vacancies for the current period and the preceding period
    of the same length. Omit facility_code for the whole network or pass one of the codes HC-01 to HC-08.
    Pass days for a period from 1 to 28 days, 7 by default. The assessment gives each measure its definition,
    its current and previous value, the change, whether the change is an improvement and, for a measure
    with a target, whether the current value meets the target. healthcare.list-facilities returns the code
    of each facility with its name, city and region.
    """
    name = Service_Workforce

    input = '-facility_code', Int('-days')

    def handle(self) -> 'None':

        days          = _resolve_days(self.request.input.days or _default_days)
        facility_code = self.request.input.facility_code
        period        = _get_period(days)

        warehouse = self.out.sql[SQL_Warehouse]
        workforce = self.out.sql[SQL_Workforce]
        facilities = get_facilities(warehouse)

        current, previous = _get_period_rows(workforce, get_workforce, facility_code, period)
        current           = _add_facility_details(current, facilities)
        previous          = _add_facility_details(previous, facilities)
        current           = _add_workforce_measures(current)
        previous          = _add_workforce_measures(previous)

        self.response.payload = get_report(period, facility_code, facilities, _summarize_workforce, current, previous)

# ################################################################################################################################

class TrackFinance(Service):
    """ Reports contract delivery, care registration, billing and operating margin for the current period
    and the preceding period of the same length. Monetary amounts have no currency recorded. Omit facility_code
    for the whole network or pass one of the codes HC-01 to HC-08. Pass days for a period from 1 to 28 days,
    7 by default. The assessment gives each measure its definition, its current and previous value, the change,
    whether the change is an improvement and, for a measure with a target, whether the current value meets the target.
    healthcare.list-facilities returns the code of each facility with its name, city and region.
    """
    name = Service_Finance

    input = '-facility_code', Int('-days')

    def handle(self) -> 'None':

        days          = _resolve_days(self.request.input.days or _default_days)
        facility_code = self.request.input.facility_code
        period        = _get_period(days)

        warehouse = self.out.sql[SQL_Warehouse]
        finance   = self.out.sql[SQL_Finance]
        facilities = get_facilities(warehouse)

        current, previous = _get_period_rows(finance, get_finance, facility_code, period)
        current           = _add_facility_details(current, facilities)
        previous          = _add_facility_details(previous, facilities)
        current           = _add_finance_measures(current)
        previous          = _add_finance_measures(previous)

        self.response.payload = get_report(period, facility_code, facilities, _summarize_finance, current, previous)

# ################################################################################################################################

class ListFacilities(Service):
    """ Returns every healthcare facility with its code, name, city, region and service capacity. The code is
    the value the facility_code parameter of the other healthcare tools takes.
    """
    name = Service_List_Facilities

    def handle(self) -> 'None':

        warehouse  = self.out.sql[SQL_Warehouse]
        facilities = get_facilities(warehouse)

        self.response.payload = {
            'facilities': list(facilities.values()),
        }

# ################################################################################################################################

class ListRegions(Service):
    """ Returns every region with the code and name of each facility in it. The healthcare tools report
    by facility code, and a regional figure is obtained by calling them for the facilities of the region.
    """
    name = Service_List_Regions

    def handle(self) -> 'None':

        warehouse  = self.out.sql[SQL_Warehouse]
        facilities = get_facilities(warehouse)

        self.response.payload = {
            'regions': _group_facilities(facilities, 'region'),
        }

# ################################################################################################################################

class ListCities(Service):
    """ Returns every city with its region and the code and name of each facility in it. The healthcare tools
    report by facility code, and a city figure is obtained by calling them for the facilities of the city.
    """
    name = Service_List_Cities

    def handle(self) -> 'None':

        warehouse  = self.out.sql[SQL_Warehouse]
        facilities = get_facilities(warehouse)

        self.response.payload = {
            'cities': _group_facilities(facilities, 'city', 'region'),
        }

# ################################################################################################################################

class ListMeasures(Service):
    """ Returns every measure the healthcare tools report - its name, its group, the tool that reports it,
    its definition, whether a higher or a lower value is better and, for a measure with a target, the target
    and whether the target is a minimum or a maximum.
    """
    name = Service_List_Measures

    def handle(self) -> 'None':

        self.response.payload = {
            'measures': list_measures(),
        }

# ################################################################################################################################
# ################################################################################################################################
