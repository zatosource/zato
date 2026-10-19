# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The SQLite databases of the MCP healthcare demo - the shared data warehouse with the clinics
# and their visit volumes, the supply chain database and the staff scheduling database. Every import
# builds them anew, with the history ending on the day of the import.

# stdlib
import os
import sqlite3
from contextlib import closing
from datetime import date, timedelta
from random import Random

# Zato
from zato.server.demo_mcp.common import Database_Files, History_Days, SQL_Scheduling, SQL_Supplies, SQL_Warehouse

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, anytuple, strdict

# ################################################################################################################################
# ################################################################################################################################

# The seed every database is generated from, so each import produces the same figures
_seed = 20261019

# The clinics of the network - code, name, city, region, opening year and number of exam rooms
_clinics:'anytuple' = (
    ('CL-01', 'Harbor Point Clinic',     'Riverside', 'South',   2009, 6),
    ('CL-02', 'Maple Street Clinic',     'Riverside', 'South',   2014, 4),
    ('CL-03', 'Eastgate Family Clinic',  'Eastgate',  'East',    2011, 8),
    ('CL-04', 'Hillcrest Clinic',        'Hillcrest', 'North',   2017, 5),
    ('CL-05', 'Lakeside Walk-in Center', 'Lakeside',  'West',    2019, 3),
    ('CL-06', 'Old Town Clinic',         'Old Town',  'Central', 2006, 7),
    ('CL-07', 'Westfield Clinic',        'Westfield', 'West',    2021, 4),
    ('CL-08', 'Northside Clinic',        'Northside', 'North',   2015, 6),
)

# How many visits of each type one exam room sees on a weekday
_visits_per_room = {
    'scheduled':  9,
    'walk-in':    4,
    'telehealth': 3,
}

# The share of each visit type's weekday volume seen on Saturdays and Sundays
_weekend_share = {
    'scheduled':  (0.4, 0.0),
    'walk-in':    (0.8, 0.5),
    'telehealth': (0.5, 0.3),
}

# The supply items each clinic keeps in stock - SKU, description, unit and reorder level
_supply_items:'anytuple' = (
    ('SUP-100', 'Nitrile gloves, medium',      'box of 100',  40),
    ('SUP-101', 'Nitrile gloves, large',       'box of 100',  30),
    ('SUP-200', 'Syringes, 5 ml',              'box of 100',  20),
    ('SUP-300', 'Gauze pads, 4 x 4 in',        'pack of 200', 25),
    ('SUP-400', 'Face masks',                  'box of 50',   60),
    ('SUP-500', 'Exam table paper',            'roll',        24),
    ('SUP-600', 'Hand sanitizer, 500 ml',      'bottle',      36),
    ('SUP-700', 'Thermometer probe covers',    'box of 200',  15),
    ('SUP-800', 'Adhesive bandages, assorted', 'box of 100',  30),
)

# The states a shipment to a clinic goes through
_shipment_statuses = ('scheduled', 'in transit', 'delivered')

# The roles each clinic schedules shifts for, with how many shifts per exam room a weekday needs
_shift_roles = {
    'physician':  0.5,
    'nurse':      1.0,
    'reception':  0.5,
    'technician': 0.3,
}

# The share of weekday shifts each clinic schedules on Saturdays and Sundays
_weekend_shift_share = (0.5, 0.2)

# ################################################################################################################################
# ################################################################################################################################

_warehouse_schema = (
    'create table clinic (code text primary key, name text, city text, region text, opened_year integer, ' + \
        'exam_rooms integer)',
    'create table daily_visits (visit_date text, clinic_code text, visit_type text, visits integer, ' + \
        'missed_appointments integer, average_wait_minutes real)',
    'create table satisfaction (month text, clinic_code text, responses integer, average_score real)',
)

_supplies_schema = (
    'create table supply_item (sku text primary key, description text, unit text)',
    'create table stock_level (clinic_code text, sku text, on_hand integer, reorder_level integer, ' + \
        'last_delivery_date text)',
    'create table shipment (shipment_id text primary key, clinic_code text, sku text, quantity integer, ' + \
        'ship_date text, status text)',
)

_scheduling_schema = (
    'create table shift (shift_date text, clinic_code text, role text, shifts_planned integer, shifts_filled integer)',
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

def _build_visit_rows(random:'Random') -> 'anylist':
    """ Returns one row per day, clinic and visit type, with the visits, the missed appointments
    and the average wait in minutes.
    """
    out:'anylist' = []

    for day in _get_history_dates():

        weekend_index = _get_weekend_index(day)

        for code, _name, _city, _region, _opened_year, exam_rooms in _clinics:
            for visit_type, visits_per_room in _visits_per_room.items():

                # The weekday volume of this clinic, with some variation from one day to the next ..
                expected = exam_rooms * visits_per_room * random.uniform(0.8, 1.2)

                # .. scaled down on weekends ..
                if weekend_index >= 0:
                    expected = expected * _weekend_share[visit_type][weekend_index]

                visits = round(expected)

                # .. only scheduled visits can be missed ..
                if visit_type == 'scheduled':
                    missed_appointments = round(visits * random.uniform(0.03, 0.12))
                else:
                    missed_appointments = 0

                # .. and walk-ins wait the longest.
                if visit_type == 'walk-in':
                    average_wait_minutes = round(random.uniform(18, 55), 1)
                elif visit_type == 'scheduled':
                    average_wait_minutes = round(random.uniform(6, 22), 1)
                else:
                    average_wait_minutes = round(random.uniform(2, 9), 1)

                if visits == 0:
                    average_wait_minutes = 0.0

                row = (day.isoformat(), code, visit_type, visits, missed_appointments, average_wait_minutes)
                out.append(row)

    return out

# ################################################################################################################################

def _build_satisfaction_rows(random:'Random') -> 'anylist':
    """ Returns one row per clinic for each of the last three months, with the survey responses
    received and their average score on a scale from 1 to 5.
    """
    out:'anylist' = []

    first_of_this_month = date.today().replace(day=1)
    month_starts = [first_of_this_month]

    for _ in range(2):
        previous = month_starts[-1] - timedelta(days=1)
        month_starts.append(previous.replace(day=1))

    for month_start in reversed(month_starts):

        month = month_start.strftime('%Y-%m')

        for code, _name, _city, _region, _opened_year, exam_rooms in _clinics:
            responses = round(exam_rooms * random.uniform(15, 30))
            average_score = round(random.uniform(3.6, 4.8), 2)
            out.append((month, code, responses, average_score))

    return out

# ################################################################################################################################

def _build_stock_rows(random:'Random') -> 'anylist':
    """ Returns one row per clinic and supply item, a few of them at or below their reorder level.
    """
    out:'anylist' = []
    today = date.today()

    for code, _name, _city, _region, _opened_year, _exam_rooms in _clinics:
        for sku, _description, _unit, reorder_level in _supply_items:

            # Most items are well stocked, roughly one in six is at or below its reorder level
            if random.random() < 0.17:
                on_hand = round(reorder_level * random.uniform(0.2, 1.0))
            else:
                on_hand = round(reorder_level * random.uniform(1.2, 3.5))

            last_delivery_date = today - timedelta(days=random.randint(2, 40))

            row = (code, sku, on_hand, reorder_level, last_delivery_date.isoformat())
            out.append(row)

    return out

# ################################################################################################################################

def _build_shipment_rows(random:'Random') -> 'anylist':
    """ Returns the shipments of the last two weeks and the coming one, two or three per clinic.
    """
    out:'anylist' = []
    today = date.today()
    shipment_number = 5000

    for code, _name, _city, _region, _opened_year, _exam_rooms in _clinics:
        for _ in range(random.randint(2, 3)):

            shipment_number += 1

            sku, _description, _unit, reorder_level = random.choice(_supply_items)
            quantity = reorder_level * random.randint(2, 4)
            days_offset = random.randint(-14, 7)
            ship_date = today + timedelta(days=days_offset)

            # What already left the warehouse a while ago is delivered, a recent one is on its way
            # and anything dated after today is still scheduled.
            if days_offset > 0:
                status = _shipment_statuses[0]
            elif days_offset > -3:
                status = _shipment_statuses[1]
            else:
                status = _shipment_statuses[2]

            row = (f'SHP-{shipment_number}', code, sku, quantity, ship_date.isoformat(), status)
            out.append(row)

    return out

# ################################################################################################################################

def _build_shift_rows(random:'Random') -> 'anylist':
    """ Returns one row per day, clinic and role, with the shifts planned and the shifts filled.
    """
    out:'anylist' = []

    for day in _get_history_dates():

        weekend_index = _get_weekend_index(day)

        for code, _name, _city, _region, _opened_year, exam_rooms in _clinics:
            for role, shifts_per_room in _shift_roles.items():

                planned = exam_rooms * shifts_per_room

                if weekend_index >= 0:
                    planned = planned * _weekend_shift_share[weekend_index]

                shifts_planned = max(round(planned), 1)

                # Most shifts are filled, a few stay open
                shifts_open = 0

                for _ in range(shifts_planned):
                    if random.random() < 0.08:
                        shifts_open += 1

                shifts_filled = shifts_planned - shifts_open

                row = (day.isoformat(), code, role, shifts_planned, shifts_filled)
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
    """ Builds the three databases of the healthcare network in the given directory
    and returns the path of each, by the name of the SQL connection it is for.
    """
    os.makedirs(directory, exist_ok=True)

    random = Random(_seed)

    clinic_rows = list(_clinics)

    supply_item_rows = []

    for sku, description, unit, _reorder_level in _supply_items:
        supply_item_rows.append((sku, description, unit))

    out:'strdict' = {}

    for connection_name, file_name in Database_Files.items():
        out[connection_name] = os.path.join(directory, file_name)

    # The data warehouse shared by the whole network ..
    _create_database(out[SQL_Warehouse], _warehouse_schema, (
        ('insert into clinic values (?, ?, ?, ?, ?, ?)', clinic_rows),
        ('insert into daily_visits values (?, ?, ?, ?, ?, ?)', _build_visit_rows(random)),
        ('insert into satisfaction values (?, ?, ?, ?)', _build_satisfaction_rows(random)),
    ))

    # .. the supply chain database ..
    _create_database(out[SQL_Supplies], _supplies_schema, (
        ('insert into supply_item values (?, ?, ?)', supply_item_rows),
        ('insert into stock_level values (?, ?, ?, ?, ?)', _build_stock_rows(random)),
        ('insert into shipment values (?, ?, ?, ?, ?, ?)', _build_shipment_rows(random)),
    ))

    # .. and the staff scheduling database.
    _create_database(out[SQL_Scheduling], _scheduling_schema, (
        ('insert into shift values (?, ?, ?, ?, ?)', _build_shift_rows(random)),
    ))

    return out

# ################################################################################################################################
# ################################################################################################################################
