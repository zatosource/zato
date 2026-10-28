# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Zato
from zato.common.b2b.portal.sample.parties import cpa_id, Partner_By_Key

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

class Agreement(NamedTuple):
    partner_key: str
    product: str
    version: int
    state: str
    start_days: int
    end_days: int
    services: 'strlist'
    retries: int
    retry_minutes: int
    persist_days: int
    sync_reply: str
    tls_version: str
    is_signed_ack: bool

    @property
    def cpa_id(self) -> 'str':
        partner = Partner_By_Key[self.partner_key]
        out = cpa_id(partner, self.product, self.version)
        return out

# ################################################################################################################################

class RegistrationEvent(NamedTuple):
    days_ago: int
    state: str
    user: str
    note: str

registration_event_list = list[RegistrationEvent]

# ################################################################################################################################

class Registration(NamedTuple):
    number: str
    partner_key: str
    product: str
    state: str
    services: 'strlist'
    agreement_version: int
    events: 'registration_event_list'

# ################################################################################################################################
# ################################################################################################################################

_order_services = ['bcRequestOrderv5', 'bcRequestOrderAmendmentv5', 'bcRequestOrderCancellationv5', 'bcQueryOrderDetailsv5',
    'bcNotifyOfOrderStatusv5']

_repair_services = ['bcRequestTroubleReportv4', 'bcRequestAppointmentv5', 'bcNotifyOfTroubleReportStatusv4']

Agreements = [
    Agreement('dolor',  'wBC', 3, 'Active',    -210,  155, _order_services,
        3, 5, 7, 'mshSignalsOnly', 'TLS 1.3', True),
    Agreement('dolor',  'T2R', 2, 'Active',    -120,  245, _repair_services,
        3, 5, 7, 'mshSignalsOnly', 'TLS 1.3', True),
    Agreement('amet',  'wBC', 4, 'Active',    -64,   301, ['bcRequestOrderv5', 'bcRequestOrderCancellationv5',
        'bcNotifyOfOrderStatusv5'], 3, 5, 7, 'mshSignalsOnly', 'TLS 1.2', True),
    Agreement('adipiscing',     'wBC', 1, 'Expiring',  -347,  18,  ['bcRequestOrderv5', 'bcRequestAppointmentv5',
        'bcNotifyOfOrderStatusv5'], 3, 5, 3, 'none', 'TLS 1.2', False),
    Agreement('tempor',  'wBC', 2, 'Suspended', -190,  175, ['bcRequestOrderv5', 'bcNotifyOfOrderStatusv5'],
        3, 5, 7, 'mshSignalsOnly', 'TLS 1.2', True),
    Agreement('labore',    'wBC', 1, 'Proposed',  14,    379, ['bcRequestOrderv5', 'bcQueryOrderDetailsv5',
        'bcNotifyOfOrderStatusv5'], 3, 5, 7, 'mshSignalsOnly', 'TLS 1.3', True),
    Agreement('aliqua', 'T2R', 1, 'Agreed',    5,     370, _repair_services,
        4, 10, 14, 'mshSignalsOnly', 'TLS 1.3', True),
]

Agreement_By_ID = {}

for _agreement in Agreements:
    Agreement_By_ID[_agreement.cpa_id] = _agreement

# ################################################################################################################################

Registrations = [
    Registration('2026-0117', 'labore', 'wBC', 'In review', ['bcRequestOrderv5', 'bcQueryOrderDetailsv5',
        'bcNotifyOfOrderStatusv5'], 1, [
        RegistrationEvent(9, 'Draft',     'Irure Reprehenderit',      'Registration started'),
        RegistrationEvent(6, 'Submitted', 'Irure Reprehenderit',      'Submitted for review'),
        RegistrationEvent(2, 'In review', 'Ullamco Laboris', 'Signing certificate under verification'),
    ]),
    Registration('2026-0112', 'aliqua', 'T2R', 'Approved', _repair_services, 1, [
        RegistrationEvent(31, 'Draft',     'Velit Esse',   'Registration started'),
        RegistrationEvent(24, 'Submitted', 'Velit Esse',   'Submitted for review'),
        RegistrationEvent(17, 'In review', 'Quis Nostrud',    'Endpoint reachable over TLS 1.3'),
        RegistrationEvent(11, 'Approved',  'Quis Nostrud',    'CPA issued for signature'),
    ]),
    Registration('2026-0109', 'amet', 'wBC', 'Active', ['bcRequestOrderv5', 'bcRequestOrderCancellationv5',
        'bcNotifyOfOrderStatusv5'], 4, [
        RegistrationEvent(80, 'Submitted', 'Ullamco Laboris', 'Renewal of CPA version 3'),
        RegistrationEvent(72, 'In review', 'Nisi Aliquip',   'Order amendment removed from the scope'),
        RegistrationEvent(66, 'Approved',  'Nisi Aliquip',   'CPA issued for signature'),
        RegistrationEvent(64, 'Active',    'Nisi Aliquip',   'CPA agreed by both parties'),
    ]),
    Registration('2026-0104', 'dolor', 'T2R', 'Active', _repair_services, 2, [
        RegistrationEvent(140, 'Submitted', 'Quis Nostrud',   'Renewal of CPA version 1'),
        RegistrationEvent(126, 'Approved',  'Nisi Aliquip',  'CPA issued for signature'),
        RegistrationEvent(120, 'Active',    'Nisi Aliquip',  'CPA agreed by both parties'),
    ]),
    Registration('2026-0121', 'adipiscing', 'wBC', 'Submitted', ['bcRequestOrderv5', 'bcRequestAppointmentv5',
        'bcNotifyOfOrderStatusv5', 'bcRequestOrderCancellationv5'], 2, [
        RegistrationEvent(3, 'Draft',     'Nisi Aliquip',   'Renewal of CPA version 1'),
        RegistrationEvent(1, 'Submitted', 'Nisi Aliquip',   'Order cancellation added to the scope'),
    ]),
    Registration('2026-0098', 'tempor', 'wBC', 'Suspended', ['bcRequestOrderv5', 'bcNotifyOfOrderStatusv5'],
        2, [
        RegistrationEvent(196, 'Submitted', 'Duis Aute', 'Registration started'),
        RegistrationEvent(190, 'Active',    'Quis Nostrud',   'CPA agreed by both parties'),
        RegistrationEvent(12,  'Suspended', 'Quis Nostrud',   'Signature verification failures over 24 hours'),
    ]),
    Registration('2026-0122', 'labore', 'T2R', 'Draft', _repair_services, 1, [
        RegistrationEvent(1, 'Draft', 'Irure Reprehenderit', 'Registration started'),
    ]),
    Registration('2026-0087', 'adipiscing', 'T2R', 'Rejected', ['bcRequestTroubleReportv4'], 1, [
        RegistrationEvent(48, 'Submitted', 'Nisi Aliquip',  'Registration started'),
        RegistrationEvent(41, 'Rejected',  'Ullamco Laboris', 'Trouble report status notifications are mandatory'),
    ]),
]

# ################################################################################################################################
# ################################################################################################################################
