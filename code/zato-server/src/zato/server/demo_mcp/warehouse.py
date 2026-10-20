# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The SQLite databases of the MCP healthcare demo - the reporting warehouse, finance system
# and workforce system. Every import builds them anew, with the history ending on the day of the import.

# stdlib
import os
import sqlite3
from contextlib import closing
from datetime import date, timedelta
from random import Random

# Zato
from zato.server.demo_mcp.common import Database_Files, History_Days, SQL_Finance, SQL_Warehouse, SQL_Workforce

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, anytuple, strdict

# ################################################################################################################################
# ################################################################################################################################

# The seed every database is generated from, so each import produces the same figures
_seed = 20261019

# The healthcare facilities - code, name, city, region and service capacity
_facilities:'anytuple' = (
    ('HC-01', 'Harbor Health Center',   'Riverside', 'South',   120),
    ('HC-02', 'Maple Health Center',    'Riverside', 'South',    80),
    ('HC-03', 'Eastgate Care Center',   'Eastgate',  'East',    150),
    ('HC-04', 'Hillcrest Care Center',  'Hillcrest', 'North',   100),
    ('HC-05', 'Lakeside Health Center', 'Lakeside',  'West',     70),
    ('HC-06', 'Old Town Care Center',   'Old Town',  'Central', 130),
    ('HC-07', 'Westfield Care Center',  'Westfield', 'West',     90),
    ('HC-08', 'Northside Health Center','Northside', 'North',   110),
)

# The share of weekday activity recorded on Saturdays and Sundays
_weekend_activity_share = (0.55, 0.35)

# ################################################################################################################################
# ################################################################################################################################

_warehouse_schema = (
    'create table facility (code text primary key, name text, city text, region text, service_capacity integer)',
    'create table care_flow (report_date text, facility_code text, referrals integer, first_appointments integer, ' + \
        'discharges integer, waiting_patients integer, median_wait_days real, capacity_used_percent real)',
    'create table quality (report_date text, facility_code text, safety_events integer, complaints integer, ' + \
        'outcome_assessments integer, positive_outcomes integer, overdue_actions integer)',
)

_finance_schema = (
    'create table financial_performance (report_date text, facility_code text, contract_value integer, ' + \
        'delivered_value integer, registered_value integer, billed_value integer, operating_cost integer)',
)

_workforce_schema = (
    'create table workforce (report_date text, facility_code text, planned_hours integer, worked_hours integer, ' + \
        'absence_hours integer, agency_hours integer, vacancies integer)',
)

# ################################################################################################################################
# ################################################################################################################################

def _get_history_dates() -> 'anylist':
    """ Returns the days the history covers, oldest first, the day of the import being the last one.
    """
    today = date.today()

    out:'anylist' = []

    for days_back in range(History_Days - 1, -1, -1):
        day = today - timedelta(days=days_back)
        out.append(day)

    return out

# ################################################################################################################################

def _get_weekend_index(day:'date') -> 'int':
    """ Returns 0 for a Saturday, 1 for a Sunday and -1 for a weekday.
    """
    weekday = day.weekday()

    if weekday == 5:
        out = 0
    elif weekday == 6:
        out = 1
    else:
        out = -1

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_activity_share(day:'date') -> 'float':
    """ Returns the share of weekday activity expected on the given day.
    """
    weekend_index = _get_weekend_index(day)

    if weekend_index >= 0:
        out = _weekend_activity_share[weekend_index]
    else:
        out = 1.0

    return out

# ################################################################################################################################

def _build_care_flow_rows(random:'Random') -> 'anylist':
    """ Returns one executive care-flow row per day and facility.
    """
    out:'anylist' = []

    for day in _get_history_dates():

        activity_share = _get_activity_share(day)

        for code, _name, _city, _region, capacity in _facilities:

            referrals         = round(capacity * random.uniform(0.025, 0.045) * activity_share)
            first_appointments = round(capacity * random.uniform(0.020, 0.040) * activity_share)
            discharges        = round(capacity * random.uniform(0.015, 0.035) * activity_share)
            waiting_patients  = round(capacity * random.uniform(0.18, 0.42))
            median_wait_days  = round(random.uniform(7.0, 24.0), 1)
            capacity_used     = round(random.uniform(82.0, 98.5), 1)

            row = (
                day.isoformat(),
                code,
                referrals,
                first_appointments,
                discharges,
                waiting_patients,
                median_wait_days,
                capacity_used,
            )
            out.append(row)

    return out

# ################################################################################################################################

def _build_quality_rows(random:'Random') -> 'anylist':
    """ Returns one quality and safety row per day and facility.
    """
    out:'anylist' = []

    for day in _get_history_dates():

        activity_share = _get_activity_share(day)

        for code, _name, _city, _region, capacity in _facilities:

            outcome_assessments = max(round(capacity * random.uniform(0.025, 0.055) * activity_share), 1)
            positive_outcomes   = round(outcome_assessments * random.uniform(0.72, 0.94))
            safety_events       = 1 if random.random() < 0.14 else 0
            complaints          = 1 if random.random() < 0.06 else 0
            overdue_actions     = random.randint(0, 3)

            row = (
                day.isoformat(),
                code,
                safety_events,
                complaints,
                outcome_assessments,
                positive_outcomes,
                overdue_actions,
            )
            out.append(row)

    return out

# ################################################################################################################################

def _build_finance_rows(random:'Random') -> 'anylist':
    """ Returns one financial performance row per day and facility.
    """
    out:'anylist' = []

    for day in _get_history_dates():

        activity_share = _get_activity_share(day)

        for code, _name, _city, _region, capacity in _facilities:

            contract_value   = round(capacity * 175 * activity_share)
            delivered_value  = round(contract_value * random.uniform(0.90, 1.06))
            registered_value = round(delivered_value * random.uniform(0.94, 0.995))
            billed_value     = round(registered_value * random.uniform(0.95, 0.995))
            operating_cost   = round(delivered_value * random.uniform(0.82, 0.98))

            row = (
                day.isoformat(),
                code,
                contract_value,
                delivered_value,
                registered_value,
                billed_value,
                operating_cost,
            )
            out.append(row)

    return out

# ################################################################################################################################

def _build_workforce_rows(random:'Random') -> 'anylist':
    """ Returns one workforce performance row per day and facility.
    """
    out:'anylist' = []

    for day in _get_history_dates():

        activity_share = _get_activity_share(day)

        for code, _name, _city, _region, capacity in _facilities:

            planned_hours = round(capacity * 3.5 * activity_share)
            worked_hours  = round(planned_hours * random.uniform(0.88, 0.99))
            absence_hours = round(planned_hours * random.uniform(0.04, 0.10))
            agency_hours  = round(worked_hours * random.uniform(0.03, 0.14))
            vacancies     = max(round(capacity * random.uniform(0.015, 0.055)), 1)

            row = (
                day.isoformat(),
                code,
                planned_hours,
                worked_hours,
                absence_hours,
                agency_hours,
                vacancies,
            )
            out.append(row)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _create_database(path:'str', schema:'anytuple', inserts:'anytuple') -> 'None':
    """ Creates one database file anew, with its tables and rows.
    """

    # An earlier import's file is replaced as a whole ..
    if os.path.exists(path):
        os.remove(path)

    with closing(sqlite3.connect(path)) as connection:

        # .. the tables are created ..
        for statement in schema:
            _ = connection.execute(statement)

        # .. filled in ..
        for statement, rows in inserts:
            _ = connection.executemany(statement, rows)

        # .. and everything is committed in one go.
        connection.commit()

# ################################################################################################################################

def build_databases(directory:'str') -> 'strdict':
    """ Builds the three executive reporting databases in the given directory
    and returns the path of each, by the name of the SQL connection it is for.
    """
    os.makedirs(directory, exist_ok=True)

    random = Random(_seed)
    facility_rows = list(_facilities)

    out:'strdict' = {}

    for connection_name, file_name in Database_Files.items():
        out[connection_name] = os.path.join(directory, file_name)

    # The reporting warehouse contains care flow, quality and facility reference data ..
    _create_database(out[SQL_Warehouse], _warehouse_schema, (
        ('insert into facility values (?, ?, ?, ?, ?)', facility_rows),
        ('insert into care_flow values (?, ?, ?, ?, ?, ?, ?, ?)', _build_care_flow_rows(random)),
        ('insert into quality values (?, ?, ?, ?, ?, ?, ?)', _build_quality_rows(random)),
    ))

    # .. the finance system provides contract and revenue measures ..
    _create_database(out[SQL_Finance], _finance_schema, (
        ('insert into financial_performance values (?, ?, ?, ?, ?, ?, ?)', _build_finance_rows(random)),
    ))

    # .. and the workforce system provides staffing measures.
    _create_database(out[SQL_Workforce], _workforce_schema, (
        ('insert into workforce values (?, ?, ?, ?, ?, ?, ?)', _build_workforce_rows(random)),
    ))

    return out

# ################################################################################################################################
# ################################################################################################################################
