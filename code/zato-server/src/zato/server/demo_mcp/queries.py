# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queries the services of the MCP healthcare demo read the reporting databases with.

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict

# ################################################################################################################################
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

def get_daily_care_flow(
    warehouse:'any_',
    facility_code:'str',
    since:'str',
    until:'str',
    ) -> 'anylist':
    """ Returns the care-flow rows of one facility, one per day, oldest first.
    """
    query = 'select report_date, referrals, first_appointments, discharges, waiting_patients, median_wait_days, ' + \
        'capacity_used_percent from care_flow ' + \
        'where report_date between :since and :until and facility_code = :facility_code ' + \
        'order by report_date'

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
# ################################################################################################################################
