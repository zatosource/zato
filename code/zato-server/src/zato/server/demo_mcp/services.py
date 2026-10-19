# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The services of the MCP healthcare demo. The importer deploys this file as it is through
# the hot-deployment directory, and the demo MCP gateway exposes each service as one tool.

# stdlib
from datetime import date, timedelta

# Zato
from zato.server.demo_mcp.common import Service_Interface_Feeds, Service_List_Facilities, Service_Network_Overview, \
    Service_Staffing, Service_Supply_Alerts, Service_Visit_Volume, SQL_Scheduling, SQL_Supplies, SQL_Warehouse
from zato.server.generic.api.channel_hl7_mllp import get_current_state
from zato.server.service import Int, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

# How many days back the figures go unless a request says otherwise
_default_days = 7

# ################################################################################################################################
# ################################################################################################################################

def _get_since(days:'int') -> 'str':
    """ Returns the first day of a period of the given number of days that ends today, as an ISO date.
    """
    first_day = date.today() - timedelta(days=days - 1)

    out = first_day.isoformat()
    return out

# ################################################################################################################################

def _get_clinic_filter(clinic_code:'str', column:'str') -> 'str':
    """ Returns the condition that narrows a query to one clinic, or nothing if no clinic is given.
    """
    if clinic_code:
        out = f' and {column} = :clinic_code'
    else:
        out = ''

    return out

# ################################################################################################################################

def _get_fill_rate(planned:'int', filled:'int') -> 'float':
    """ Returns the percentage of planned shifts that are filled.
    """
    if planned == 0:
        return 100.0

    out = round(filled * 100 / planned, 1)
    return out

# ################################################################################################################################
# ################################################################################################################################

def get_clinics(warehouse:'any_', region:'str') -> 'anylist':
    """ Returns the clinics of the network, optionally only those of one region.
    """
    query = 'select code, name, city, region, opened_year, exam_rooms from clinic'

    if region:
        query += ' where region = :region'

    query += ' order by code'

    out = warehouse.execute(query, {'region': region})
    return out

# ################################################################################################################################

def get_visit_volume(warehouse:'any_', clinic_code:'str', days:'int') -> 'anylist':
    """ Returns, per clinic, the visits of each type in the period, the missed appointments and the average wait.
    """
    clinic_filter = _get_clinic_filter(clinic_code, 'clinic_code')

    query = 'select clinic_code, visit_type, sum(visits) as visits, ' + \
        'sum(missed_appointments) as missed_appointments, ' + \
        'round(sum(average_wait_minutes * visits) / max(sum(visits), 1), 1) as average_wait_minutes ' + \
        'from daily_visits where visit_date >= :since' + clinic_filter + ' ' + \
        'group by clinic_code, visit_type order by clinic_code, visit_type'

    rows = warehouse.execute(query, {'since': _get_since(days), 'clinic_code': clinic_code})

    # The rows come per visit type, each clinic gets them all in one entry ..
    by_clinic:'anydict' = {}

    for row in rows:

        if row['clinic_code'] not in by_clinic:
            by_clinic[row['clinic_code']] = {
                'clinic_code': row['clinic_code'],
                'total_visits': 0,
                'missed_appointments': 0,
                'by_visit_type': {},
            }

        entry = by_clinic[row['clinic_code']]
        entry['total_visits'] += row['visits']
        entry['missed_appointments'] += row['missed_appointments']
        entry['by_visit_type'][row['visit_type']] = {
            'visits': row['visits'],
            'average_wait_minutes': row['average_wait_minutes'],
        }

    # .. in the order of their codes.
    out = list(by_clinic.values())
    return out

# ################################################################################################################################

def get_low_stock(supplies:'any_', clinic_code:'str') -> 'anylist':
    """ Returns the supply items that are at or below their reorder level, per clinic.
    """
    clinic_filter = _get_clinic_filter(clinic_code, 'stock.clinic_code')

    query = 'select stock.clinic_code, stock.sku, item.description, item.unit, stock.on_hand, ' + \
        'stock.reorder_level, stock.last_delivery_date ' + \
        'from stock_level stock join supply_item item on item.sku = stock.sku ' + \
        'where stock.on_hand <= stock.reorder_level' + clinic_filter + ' ' + \
        'order by stock.clinic_code, stock.sku'

    out = supplies.execute(query, {'clinic_code': clinic_code})
    return out

# ################################################################################################################################

def get_open_shipments(supplies:'any_', clinic_code:'str') -> 'anylist':
    """ Returns the shipments that are scheduled or on their way to the clinics.
    """
    clinic_filter = _get_clinic_filter(clinic_code, 'shipment.clinic_code')

    query = 'select shipment.shipment_id, shipment.clinic_code, shipment.sku, item.description, ' + \
        'shipment.quantity, shipment.ship_date, shipment.status ' + \
        'from shipment join supply_item item on item.sku = shipment.sku ' + \
        "where shipment.status != 'delivered'" + clinic_filter + ' ' + \
        'order by shipment.ship_date'

    out = supplies.execute(query, {'clinic_code': clinic_code})
    return out

# ################################################################################################################################

def get_staffing(scheduling:'any_', clinic_code:'str', days:'int') -> 'anylist':
    """ Returns, per clinic and role, the shifts planned and filled in the period and the fill rate.
    """
    clinic_filter = _get_clinic_filter(clinic_code, 'clinic_code')

    query = 'select clinic_code, role, sum(shifts_planned) as shifts_planned, sum(shifts_filled) as shifts_filled ' + \
        'from shift where shift_date >= :since' + clinic_filter + ' ' + \
        'group by clinic_code, role order by clinic_code, role'

    rows = scheduling.execute(query, {'since': _get_since(days), 'clinic_code': clinic_code})

    # Each clinic gets its roles and its overall fill rate in one entry ..
    by_clinic:'anydict' = {}

    for row in rows:

        if row['clinic_code'] not in by_clinic:
            by_clinic[row['clinic_code']] = {
                'clinic_code': row['clinic_code'],
                'shifts_planned': 0,
                'shifts_filled': 0,
                'by_role': {},
            }

        entry = by_clinic[row['clinic_code']]
        entry['shifts_planned'] += row['shifts_planned']
        entry['shifts_filled'] += row['shifts_filled']
        entry['by_role'][row['role']] = {
            'shifts_planned': row['shifts_planned'],
            'shifts_filled': row['shifts_filled'],
            'fill_rate_percent': _get_fill_rate(row['shifts_planned'], row['shifts_filled']),
        }

    # .. with the overall rate computed once all of its roles are in.
    out = list(by_clinic.values())

    for entry in out:
        entry['fill_rate_percent'] = _get_fill_rate(entry['shifts_planned'], entry['shifts_filled'])

    return out

# ################################################################################################################################

def get_interface_feeds() -> 'anylist':
    """ Returns the live state of each HL7 MLLP feed of this server.
    """
    out:'anylist' = []

    for channel in get_current_state():
        out.append({
            'name': channel['name'],
            'is_listening': channel['is_listening'],
            'received': channel['received'],
            'acknowledged': channel['acked'],
            'rejected': channel['nacked'],
            'errored': channel['errored'],
            'last_message_time': channel['last_message_time_iso'],
            'silence_seconds': channel['silence_seconds'],
        })

    return out

# ################################################################################################################################
# ################################################################################################################################

class ListFacilities(Service):
    """ Lists the clinics of the network - each clinic's code, name, city, region, opening year
    and number of exam rooms. The codes it returns are what the other healthcare tools accept as clinic_code.
    Pass region to list only the clinics of one region - North, South, East, West or Central.
    """
    name = Service_List_Facilities

    input = '-region'

    def handle(self) -> 'None':

        warehouse = self.out.sql[SQL_Warehouse]
        clinics = get_clinics(warehouse, self.request.input.region)

        self.response.payload = {'clinics': clinics}

# ################################################################################################################################

class GetVisitVolume(Service):
    """ Returns the visit volumes of the clinics over the last given number of days, 7 by default -
    for each clinic, the visits by type (scheduled, walk-in and telehealth), the missed appointments
    and the average wait in minutes. Pass clinic_code to narrow it to one clinic.
    """
    name = Service_Visit_Volume

    input = '-clinic_code', Int('-days')

    def handle(self) -> 'None':

        days = self.request.input.days or _default_days

        warehouse = self.out.sql[SQL_Warehouse]
        clinics = get_visit_volume(warehouse, self.request.input.clinic_code, days)

        self.response.payload = {'days': days, 'clinics': clinics}

# ################################################################################################################################

class GetSupplyAlerts(Service):
    """ Returns the supply items that are at or below their reorder level in the clinics, with what is
    on hand, the reorder level and the last delivery date, along with the shipments that are scheduled
    or on their way. Pass clinic_code to narrow it to one clinic.
    """
    name = Service_Supply_Alerts

    input = '-clinic_code'

    def handle(self) -> 'None':

        clinic_code = self.request.input.clinic_code
        supplies = self.out.sql[SQL_Supplies]

        self.response.payload = {
            'low_stock': get_low_stock(supplies, clinic_code),
            'open_shipments': get_open_shipments(supplies, clinic_code),
        }

# ################################################################################################################################

class GetStaffing(Service):
    """ Returns how well the clinics' shifts are staffed over the last given number of days, 7 by default -
    for each clinic and role (physician, nurse, reception and technician), the shifts planned, the shifts
    filled and the fill rate in percent. Pass clinic_code to narrow it to one clinic.
    """
    name = Service_Staffing

    input = '-clinic_code', Int('-days')

    def handle(self) -> 'None':

        days = self.request.input.days or _default_days

        scheduling = self.out.sql[SQL_Scheduling]
        clinics = get_staffing(scheduling, self.request.input.clinic_code, days)

        self.response.payload = {'days': days, 'clinics': clinics}

# ################################################################################################################################

class GetInterfaceFeeds(Service):
    """ Returns the live state of the HL7 MLLP feeds the hospital, the laboratory and the clinics
    send their messages through - for each feed, whether it is listening, how many messages it received,
    acknowledged, rejected or failed to process, and when the last message arrived.
    """
    name = Service_Interface_Feeds

    def handle(self) -> 'None':
        self.response.payload = {'feeds': get_interface_feeds()}

# ################################################################################################################################

class GetNetworkOverview(Service):
    """ Returns one view of the whole healthcare network over the last 7 days, combining the data warehouse,
    the supply chain database, the staff scheduling database and the HL7 MLLP feeds - for each clinic,
    its visits, missed appointments, low-stock supply items and shift fill rate, followed by the totals
    for the network and the state of the feeds. Use the other healthcare tools to look into any of the figures.
    """
    name = Service_Network_Overview

    def handle(self) -> 'None':

        warehouse = self.out.sql[SQL_Warehouse]
        supplies = self.out.sql[SQL_Supplies]
        scheduling = self.out.sql[SQL_Scheduling]

        # Each data source is read once for the whole network ..
        clinics = get_clinics(warehouse, '')
        visits = get_visit_volume(warehouse, '', _default_days)
        low_stock = get_low_stock(supplies, '')
        staffing = get_staffing(scheduling, '', _default_days)
        feeds = get_interface_feeds()

        visits_by_clinic:'stranydict' = {}
        for entry in visits:
            visits_by_clinic[entry['clinic_code']] = entry

        staffing_by_clinic:'stranydict' = {}
        for entry in staffing:
            staffing_by_clinic[entry['clinic_code']] = entry

        low_stock_by_clinic:'stranydict' = {}
        for row in low_stock:
            if row['clinic_code'] not in low_stock_by_clinic:
                low_stock_by_clinic[row['clinic_code']] = []
            low_stock_by_clinic[row['clinic_code']].append(row['description'])

        # .. each clinic gets one row combining all of them ..
        clinic_rows:'anylist' = []

        for clinic in clinics:

            code = clinic['code']
            clinic_visits = visits_by_clinic[code]
            clinic_staffing = staffing_by_clinic[code]

            if code in low_stock_by_clinic:
                clinic_low_stock = low_stock_by_clinic[code]
            else:
                clinic_low_stock = []

            clinic_rows.append({
                'clinic_code': code,
                'name': clinic['name'],
                'region': clinic['region'],
                'visits': clinic_visits['total_visits'],
                'missed_appointments': clinic_visits['missed_appointments'],
                'walk_in_average_wait_minutes': clinic_visits['by_visit_type']['walk-in']['average_wait_minutes'],
                'low_stock_items': clinic_low_stock,
                'shift_fill_rate_percent': clinic_staffing['fill_rate_percent'],
            })

        # .. and the network as a whole is summed up from the same figures.
        total_visits = 0
        total_missed = 0
        total_planned = 0
        total_filled = 0

        for entry in visits:
            total_visits += entry['total_visits']
            total_missed += entry['missed_appointments']

        for entry in staffing:
            total_planned += entry['shifts_planned']
            total_filled += entry['shifts_filled']

        messages_received = 0
        feeds_listening = 0

        for feed in feeds:
            messages_received += feed['received']
            if feed['is_listening']:
                feeds_listening += 1

        self.response.payload = {
            'days': _default_days,
            'clinics': clinic_rows,
            'network': {
                'clinics': len(clinics),
                'visits': total_visits,
                'missed_appointments': total_missed,
                'low_stock_items': len(low_stock),
                'shift_fill_rate_percent': _get_fill_rate(total_planned, total_filled),
            },
            'interface_feeds': {
                'feeds': len(feeds),
                'listening': feeds_listening,
                'messages_received': messages_received,
            },
        }

# ################################################################################################################################
# ################################################################################################################################
