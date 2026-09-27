# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta
from logging import getLogger

# Live Fabric
from live_fabric import items
from live_fabric.common import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist
    from zato.server.connection.cloud.microsoft_fabric.client import MicrosoftFabricClient

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The reference point of the sample data
_now = datetime(2026, 9, 1, 8, 0, 0)

# ################################################################################################################################
# ################################################################################################################################

def _at(days_ago:'int', hour:'int'=9) -> 'str':
    """ A timestamp that many days before the sample data's reference point.
    """
    moment = _now - timedelta(days=days_ago)
    moment = moment.replace(hour=hour)

    out = moment.strftime('%Y-%m-%d %H:%M:%S')
    return out

# ################################################################################################################################

def _day(days_ago:'int') -> 'str':
    """ A date that many days before the sample data's reference point.
    """
    moment = _now - timedelta(days=days_ago)

    out = moment.strftime('%Y-%m-%d')
    return out

# ################################################################################################################################
# ################################################################################################################################

def locations() -> 'dictlist':
    return [
        {'location_id': 'LOC-1', 'name': 'Riverside',   'city': 'Portland', 'state': 'OR', 'beds': 120},
        {'location_id': 'LOC-2', 'name': 'Oak Hill',    'city': 'Salem',    'state': 'OR', 'beds': 80},
        {'location_id': 'LOC-3', 'name': 'Maple Grove', 'city': 'Eugene',   'state': 'OR', 'beds': 60},
    ]

# ################################################################################################################################

def insurers() -> 'dictlist':
    return [
        {'insurer_id': 'INS-1', 'name': 'Cascade Health Plan'},
        {'insurer_id': 'INS-2', 'name': 'Pacific Mutual'},
        {'insurer_id': 'INS-3', 'name': 'Evergreen Assurance'},
    ]

# ################################################################################################################################

def staff() -> 'dictlist':
    return [
        {'staff_id': 'STF-101', 'location': 'Riverside',   'role': 'Nurse',      'cost_center': 'CC-100', 'active': True},
        {'staff_id': 'STF-102', 'location': 'Riverside',   'role': 'Physician',  'cost_center': 'CC-100', 'active': True},
        {'staff_id': 'STF-103', 'location': 'Oak Hill',    'role': 'Nurse',      'cost_center': 'CC-200', 'active': True},
        {'staff_id': 'STF-104', 'location': 'Maple Grove', 'role': 'Technician', 'cost_center': 'CC-300', 'active': False},
        {'staff_id': 'STF-105', 'location': 'Oak Hill',    'role': 'Physician',  'cost_center': 'CC-200', 'active': True},
    ]

# ################################################################################################################################

def admissions() -> 'dictlist':
    out:'dictlist' = []
    counter = 1

    # Three weeks of admissions, a few per location per day, with the most recent ones still open.
    for days_ago in range(21, 0, -1):
        for location in ModuleCtx.Locations:

            is_open = days_ago <= 2

            if is_open:
                discharged_at = ''
                status = 'admitted'
            else:
                discharge_days_ago = days_ago - 2
                discharged_at = _at(discharge_days_ago, hour=14)
                status = 'discharged'

            out.append({
                'admission_id': f'ADM-{counter:04d}',
                'location': location,
                'admitted_at': _at(days_ago),
                'discharged_at': discharged_at,
                'status': status,
            })

            counter += 1

    return out

# ################################################################################################################################

def occupancy() -> 'dictlist':
    out:'dictlist' = []

    beds = {'Riverside': 120, 'Oak Hill': 80, 'Maple Grove': 60}
    occupied = {'Riverside': 97, 'Oak Hill': 61, 'Maple Grove': 38}

    # A fortnight of nightly snapshots per location.
    for days_ago in range(14, 0, -1):
        for location in ModuleCtx.Locations:

            occupied_beds = occupied[location] - days_ago % 5
            available_beds = beds[location] - occupied_beds

            out.append({
                'location': location,
                'as_of': _day(days_ago),
                'occupied_beds': occupied_beds,
                'available_beds': available_beds,
            })

    return out

# ################################################################################################################################

def appointments() -> 'dictlist':
    out:'dictlist' = []
    counter = 1

    statuses = 'scheduled', 'scheduled', 'confirmed', 'cancelled'
    status_count = len(statuses)

    # Appointments over the coming days, most without a reminder yet.
    for days_ahead in range(1, 8):
        for location in ModuleCtx.Locations:
            for slot in range(3):

                status_index = (counter + slot) % status_count
                status = statuses[status_index]
                reminder_sent = slot == 0
                days_ago = -days_ahead
                hour = 9 + slot * 2

                out.append({
                    'appointment_id': f'APT-{counter:04d}',
                    'location': location,
                    'starts_at': _at(days_ago, hour=hour),
                    'status': status,
                    'reminder_sent': reminder_sent,
                    'updated_at': _at(1),
                })

                counter += 1

    return out

# ################################################################################################################################

def invoices() -> 'dictlist':
    out:'dictlist' = []
    counter = 1

    insurer_names = 'Cascade Health Plan', 'Pacific Mutual', 'Evergreen Assurance'
    statuses = 'sent', 'paid', 'overdue'
    insurer_count = len(insurer_names)
    location_count = len(ModuleCtx.Locations)
    status_count = len(statuses)

    # Two dozen invoices spread across insurers and locations.
    for days_ago in range(24, 0, -1):

        insurer_index = counter % insurer_count
        location_index = counter % location_count
        status_index = counter % status_count

        insurer = insurer_names[insurer_index]
        location = ModuleCtx.Locations[location_index]
        status = statuses[status_index]

        out.append({
            'invoice_id': f'INV-{counter:04d}',
            'insurer': insurer,
            'location': location,
            'amount': 1250.00 + counter * 37.5,
            'status': status,
            'sent_at': _at(days_ago, hour=16),
        })

        counter += 1

    return out

# ################################################################################################################################

def inventory() -> 'dictlist':
    out:'dictlist' = []

    supplies = 'Gloves', 'Saline', 'Syringes', 'Gauze', 'Masks'

    # One row per supply per location, a couple of them under their reorder level.
    for location_index, location in enumerate(ModuleCtx.Locations):
        for supply_index, supply in enumerate(supplies):

            reorder_level = 100 + supply_index * 20
            quantity = reorder_level + 40 - (location_index + supply_index) * 15
            location_number = location_index + 1
            supply_number = supply_index + 1

            out.append({
                'item_id': f'ITM-{location_number}{supply_number:02d}',
                'location': location,
                'name': supply,
                'quantity': quantity,
                'reorder_level': reorder_level,
            })

    return out

# ################################################################################################################################
# ################################################################################################################################

# What fills each table
_builders = {
    'locations':    locations,
    'insurers':     insurers,
    'staff':        staff,
    'admissions':   admissions,
    'occupancy':    occupancy,
    'appointments': appointments,
    'invoices':     invoices,
    'inventory':    inventory,
}

# ################################################################################################################################
# ################################################################################################################################

def build(client:'MicrosoftFabricClient', state:'anydict') -> 'None':
    """ Writes the sample tables.
    """
    workspace_id = state['workspace_id']
    lakehouse_id = state['lakehouse_id']

    existing = items.table_names(client, workspace_id, lakehouse_id)

    for table_name in ModuleCtx.Tables:

        if table_name in existing:
            logger.info(f'Table {table_name} exists')
            continue

        logger.info(f'Writing table {table_name} ..')

        builder = _builders[table_name]
        rows = builder()
        _ = client.write_table(workspace_id, lakehouse_id, table_name, rows)

    state['tables'] = list(ModuleCtx.Tables)

# ################################################################################################################################
# ################################################################################################################################
