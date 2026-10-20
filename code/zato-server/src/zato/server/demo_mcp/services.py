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
from zato.server.demo_mcp.common import Service_Care_Flow, Service_Finance, Service_Quality, Service_Scorecard, \
    Service_Workforce, SQL_Finance, SQL_Warehouse, SQL_Workforce
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

# The targets shown with each executive measure
_target_wait_days                = 14.0
_target_capacity_used_percent    = 90.0
_target_positive_outcome_percent = 85.0
_target_overdue_actions          = 0
_target_staffing_percent         = 95.0
_target_absence_percent          = 6.0
_target_agency_percent           = 10.0
_target_plan_percent             = 100.0
_target_registration_percent     = 98.0
_target_margin_percent           = 8.0

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

def _get_facility_filter(facility_code:'str', column:'str') -> 'str':
    """ Returns the condition that narrows a query to one facility.
    """
    if facility_code:
        out = f' and {column} = :facility_code'
    else:
        out = ''

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

def get_facilities(warehouse:'any_') -> 'stranydict':
    """ Returns the healthcare facilities by code.
    """
    query = 'select code, name, city, region, service_capacity from facility order by code'
    rows = warehouse.execute(query)

    out:'stranydict' = {}

    for row in rows:
        out[row['code']] = row

    return out

# ################################################################################################################################

def get_care_flow(
    warehouse:'any_',
    facility_code:'str',
    since:'str',
    until:'str',
    ) -> 'anylist':
    """ Returns care-flow measures per facility for one reporting period.
    """
    facility_filter = _get_facility_filter(facility_code, 'facility_code')

    query = 'select facility_code, sum(referrals) as referrals, ' + \
        'sum(first_appointments) as first_appointments, sum(discharges) as discharges, ' + \
        'round(avg(waiting_patients), 1) as waiting_patients, ' + \
        'round(avg(median_wait_days), 1) as median_wait_days, ' + \
        'round(avg(capacity_used_percent), 1) as capacity_used_percent ' + \
        'from care_flow where report_date between :since and :until' + facility_filter + ' ' + \
        'group by facility_code order by facility_code'

    parameters = {
        'facility_code': facility_code,
        'since': since,
        'until': until,
    }

    out = warehouse.execute(query, parameters)
    return out

# ################################################################################################################################

def get_quality(
    warehouse:'any_',
    facility_code:'str',
    since:'str',
    until:'str',
    ) -> 'anylist':
    """ Returns quality and safety measures per facility for one reporting period.
    """
    facility_filter = _get_facility_filter(facility_code, 'facility_code')

    query = 'select facility_code, sum(safety_events) as safety_events, sum(complaints) as complaints, ' + \
        'sum(outcome_assessments) as outcome_assessments, sum(positive_outcomes) as positive_outcomes, ' + \
        'round(avg(overdue_actions), 1) as overdue_actions ' + \
        'from quality where report_date between :since and :until' + facility_filter + ' ' + \
        'group by facility_code order by facility_code'

    parameters = {
        'facility_code': facility_code,
        'since': since,
        'until': until,
    }

    out = warehouse.execute(query, parameters)
    return out

# ################################################################################################################################

def get_workforce(
    workforce:'any_',
    facility_code:'str',
    since:'str',
    until:'str',
    ) -> 'anylist':
    """ Returns workforce measures per facility for one reporting period.
    """
    facility_filter = _get_facility_filter(facility_code, 'facility_code')

    query = 'select facility_code, sum(planned_hours) as planned_hours, sum(worked_hours) as worked_hours, ' + \
        'sum(absence_hours) as absence_hours, sum(agency_hours) as agency_hours, ' + \
        'round(avg(vacancies), 1) as vacancies ' + \
        'from workforce where report_date between :since and :until' + facility_filter + ' ' + \
        'group by facility_code order by facility_code'

    parameters = {
        'facility_code': facility_code,
        'since': since,
        'until': until,
    }

    out = workforce.execute(query, parameters)
    return out

# ################################################################################################################################

def get_finance(
    finance:'any_',
    facility_code:'str',
    since:'str',
    until:'str',
    ) -> 'anylist':
    """ Returns financial and contract measures per facility for one reporting period.
    """
    facility_filter = _get_facility_filter(facility_code, 'facility_code')

    query = 'select facility_code, sum(contract_value) as contract_value, ' + \
        'sum(delivered_value) as delivered_value, sum(registered_value) as registered_value, ' + \
        'sum(billed_value) as billed_value, sum(operating_cost) as operating_cost ' + \
        'from financial_performance where report_date between :since and :until' + facility_filter + ' ' + \
        'group by facility_code order by facility_code'

    parameters = {
        'facility_code': facility_code,
        'since': since,
        'until': until,
    }

    out = finance.execute(query, parameters)
    return out

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
# ################################################################################################################################

class GetScorecard(Service):
    """ Returns the executive healthcare scorecard for the current period and the preceding period,
    covering care flow, quality, workforce and finance. Pass facility_code for one facility and days
    for a reporting period from 1 to 28 days.
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
            'current': {
                'care_flow': _summarize_care_flow(current_care),
                'quality': _summarize_quality(current_quality),
                'workforce': _summarize_workforce(current_workforce),
                'finance': _summarize_finance(current_finance),
            },
            'previous': {
                'care_flow': _summarize_care_flow(previous_care),
                'quality': _summarize_quality(previous_quality),
                'workforce': _summarize_workforce(previous_workforce),
                'finance': _summarize_finance(previous_finance),
            },
            'targets': {
                'median_wait_days': _target_wait_days,
                'capacity_used_percent': _target_capacity_used_percent,
                'positive_outcome_percent': _target_positive_outcome_percent,
                'overdue_actions': _target_overdue_actions,
                'staffing_percent': _target_staffing_percent,
                'absence_percent': _target_absence_percent,
                'agency_percent': _target_agency_percent,
                'plan_percent': _target_plan_percent,
                'registration_percent': _target_registration_percent,
                'margin_percent': _target_margin_percent,
            },
        }

# ################################################################################################################################

class TrackCareFlow(Service):
    """ Reports referrals, first appointments, discharges, waiting patients, waiting time and capacity use
    for the current period and the preceding period. Pass facility_code for one facility and days for a
    reporting period from 1 to 28 days.
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

        self.response.payload = {
            'period': period,
            'current': {
                'summary': _summarize_care_flow(current),
                'facilities': current,
            },
            'previous': {
                'summary': _summarize_care_flow(previous),
                'facilities': previous,
            },
            'targets': {
                'median_wait_days': _target_wait_days,
                'capacity_used_percent': _target_capacity_used_percent,
            },
        }

# ################################################################################################################################

class ReviewQuality(Service):
    """ Reports care outcomes, safety events, complaints and overdue actions for the current period and
    the preceding period. Pass facility_code for one facility and days for a reporting period from 1 to 28 days.
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

        self.response.payload = {
            'period': period,
            'current': {
                'summary': _summarize_quality(current),
                'facilities': current,
            },
            'previous': {
                'summary': _summarize_quality(previous),
                'facilities': previous,
            },
            'targets': {
                'positive_outcome_percent': _target_positive_outcome_percent,
                'overdue_actions': _target_overdue_actions,
            },
        }

# ################################################################################################################################

class AssessWorkforce(Service):
    """ Reports staffing coverage, absence, agency work and vacancies for the current period and the
    preceding period. Pass facility_code for one facility and days for a reporting period from 1 to 28 days.
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

        self.response.payload = {
            'period': period,
            'current': {
                'summary': _summarize_workforce(current),
                'facilities': current,
            },
            'previous': {
                'summary': _summarize_workforce(previous),
                'facilities': previous,
            },
            'targets': {
                'staffing_percent': _target_staffing_percent,
                'absence_percent': _target_absence_percent,
                'agency_percent': _target_agency_percent,
            },
        }

# ################################################################################################################################

class TrackFinance(Service):
    """ Reports contract delivery, care registration, billing and operating margin for the current period
    and the preceding period. Pass facility_code for one facility and days for a reporting period from 1 to 28 days.
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

        self.response.payload = {
            'period': period,
            'current': {
                'summary': _summarize_finance(current),
                'facilities': current,
            },
            'previous': {
                'summary': _summarize_finance(previous),
                'facilities': previous,
            },
            'targets': {
                'plan_percent': _target_plan_percent,
                'registration_percent': _target_registration_percent,
                'margin_percent': _target_margin_percent,
            },
        }

# ################################################################################################################################
# ################################################################################################################################
