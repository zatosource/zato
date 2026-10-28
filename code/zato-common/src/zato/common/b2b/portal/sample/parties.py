# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

DUNS_Type = 'urn:oasis:names:tc:ebXML-cppa:partyid-type:duns'

Partner_Role = 'CommunicationsProvider'

# ################################################################################################################################
# ################################################################################################################################

class Partner(NamedTuple):
    key: str
    name: str
    duns: str
    state: str
    category: str
    host: str
    contact: str
    email: str
    signing_days_left: int
    tls_days_left: int

# ################################################################################################################################

class Service(NamedTuple):
    name: str
    request: str
    response: str
    label: str
    receipt_seconds: int
    perform_seconds: int
    is_notification: bool

# ################################################################################################################################
# ################################################################################################################################

Partners = [
    Partner('dolor',  'Dolor Sit',     '987654321', 'Active',     'Tier 1', 'gateway.dolor-sit.example.com',
        'Quis Nostrud',    'quis.nostrud@dolor-sit.example.com',    214, 301),
    Partner('amet',  'Amet Consectetur',   '412907766', 'Active',     'Tier 1', 'b2b.amet-consectetur.example.com',
        'Ullamco Laboris', 'ullamco.laboris@amet-consectetur.example.com', 9, 188),
    Partner('adipiscing',     'Adipiscing Elit', '603318254', 'Active',     'Tier 2', 'ebxml.adipiscing-elit.example.com',
        'Nisi Aliquip',   'nisi.aliquip@adipiscing-elit.example.com',        402, 77),
    Partner('tempor',  'Tempor Incididunt',    '118820931', 'Suspended',  'Tier 2', 'msh.tempor-incididunt.example.com',
        'Duis Aute',  'duis.aute@tempor-incididunt.example.com', 133, 133),
    Partner('labore',    'Labore Magna',       '774205583', 'Onboarding', 'Tier 3', 'test-gw.labore-magna.example.com',
        'Irure Reprehenderit',      'irure.reprehenderit@labore-magna.example.com',        362, 362),
    Partner('aliqua', 'Aliqua Veniam',      '305561870', 'Active',     'Tier 3', 'exchange.aliqua-veniam.example.com',
        'Velit Esse',   'velit.esse@aliqua-veniam.example.com',    27, 27),
]

Partner_By_Key = {}

for _partner in Partners:
    Partner_By_Key[_partner.key] = _partner

# ################################################################################################################################

Services = [
    Service('bcRequestOrderv5',             'rqRequestOrder',             'rsRequestOrder',             'Order',
        0, 120, False),
    Service('bcRequestOrderAmendmentv5',    'rqRequestOrderAmendment',    'rsRequestOrderAmendment',    'Order amendment',
        0, 120, False),
    Service('bcRequestOrderCancellationv5', 'rqRequestOrderCancellation', 'rsRequestOrderCancellation', 'Order cancellation',
        0, 120, False),
    Service('bcRequestAppointmentv5',       'rqRequestAppointment',       'rsRequestAppointment',       'Appointment',
        120, 300, False),
    Service('bcRequestTroubleReportv4',     'rqRequestTroubleReport',     'rsRequestTroubleReport',     'Trouble report',
        120, 600, False),
    Service('bcQueryOrderDetailsv5',        'rqQueryOrderDetails',        'rsQueryOrderDetails',        'Order details',
        0, 60, False),
    Service('bcNotifyOfOrderStatusv5',      'NotifyOfOrderStatus',        '',                           'Order status',
        300, 0, True),
    Service('bcNotifyOfTroubleReportStatusv4', 'NotifyOfTroubleReportStatus', '',                     'Trouble report status',
        300, 0, True),
]

Service_By_Name = {}

for _service in Services:
    Service_By_Name[_service.name] = _service

# ################################################################################################################################
# ################################################################################################################################

def endpoint(partner:'Partner') -> 'str':
    out = f'https://{partner.host}/exchange/{partner.duns}'
    return out

# ################################################################################################################################

def cpa_id(partner:'Partner', product:'str', version:'int') -> 'str':
    name = partner.name.split(' ')[0]
    out = f'Lorem_Ipsum_{name}_B2BGateway_{product}_R1.5.0_cpa{version}'
    return out

# ################################################################################################################################

def duration(seconds:'int') -> 'str':
    """ A time limit of the CPA in the XML duration format the CPA itself uses.
    """
    if seconds % 60 == 0:
        minutes = seconds // 60
        out = f'PT{minutes}M'
    else:
        out = f'PT{seconds}S'

    return out

# ################################################################################################################################
# ################################################################################################################################
