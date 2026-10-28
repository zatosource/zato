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
    product: str

# ################################################################################################################################
# ################################################################################################################################

Partners = [
    Partner('harborlight', 'Harborlight Wireless', '987654321', 'Active', 'Tier 1', 'gateway.harborlight-wireless.example.com',
        'Jennifer Caldwell', 'jennifer.caldwell@harborlight-wireless.example.com', 214, 301),
    Partner('redwood', 'Redwood Fiber Networks', '412907766', 'Active', 'Tier 1', 'b2b.redwood-fiber.example.com',
        'Marcus Delgado', 'marcus.delgado@redwood-fiber.example.com', 9, 188),
    Partner('lakeshore', 'Lakeshore Communications', '603318254', 'Active', 'Tier 2', 'ebxml.lakeshore-communications.example.com',
        'Patricia Hollis', 'patricia.hollis@lakeshore-communications.example.com', 402, 77),
    Partner('prairie', 'Prairie Sky Broadband', '118820931', 'Suspended', 'Tier 2', 'msh.prairie-sky.example.com',
        'Kevin Brennan', 'kevin.brennan@prairie-sky.example.com', 133, 133),
    Partner('bluemesa', 'Blue Mesa Mobile', '774205583', 'Onboarding', 'Tier 3', 'test-gw.bluemesa-mobile.example.com',
        'Ashley Whitfield', 'ashley.whitfield@bluemesa-mobile.example.com', 362, 362),
    Partner('coppercreek', 'Copper Creek Telecom', '305561870', 'Active', 'Tier 3', 'exchange.coppercreek-telecom.example.com',
        'Daniel Foster', 'daniel.foster@coppercreek-telecom.example.com', 27, 27),
]

Partner_By_Key = {}

for _partner in Partners:
    Partner_By_Key[_partner.key] = _partner

# ################################################################################################################################

Orders_Product     = 'Orders'
Complaints_Product = 'Complaints'

Services = [
    Service('SubmitOrderv2',                'rqSubmitOrder',                'rsSubmitOrder',                'Order',
        0, 120, False, Orders_Product),
    Service('ChangeOrderv2',                'rqChangeOrder',                'rsChangeOrder',                'Order change',
        0, 120, False, Orders_Product),
    Service('CancelOrderv2',                'rqCancelOrder',                'rsCancelOrder',                'Order cancellation',
        0, 120, False, Orders_Product),
    Service('ScheduleInstallationv2',       'rqScheduleInstallation',       'rsScheduleInstallation',       'Installation appointment',
        120, 300, False, Orders_Product),
    Service('QueryOrderDetailsv2',          'rqQueryOrderDetails',          'rsQueryOrderDetails',          'Order details',
        0, 60, False, Orders_Product),
    Service('NotifyOfOrderStatusv2',        'NotifyOfOrderStatus',          '',                             'Order status',
        300, 0, True, Orders_Product),
    Service('FileComplaintv2',              'rqFileComplaint',              'rsFileComplaint',              'Complaint',
        120, 600, False, Complaints_Product),
    Service('EscalateComplaintv2',          'rqEscalateComplaint',          'rsEscalateComplaint',          'Complaint escalation',
        120, 300, False, Complaints_Product),
    Service('NotifyOfComplaintStatusv2',    'NotifyOfComplaintStatus',      '',                             'Complaint status',
        300, 0, True, Complaints_Product),
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
    out = f'Pinecrest_Telecom_{name}_B2BGateway_{product}_R1.5.0_cpa{version}'
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
