# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# typing-extensions
from typing_extensions import TypeAlias

# Zato
from zato.common.b2b.portal.sample.parties import agreement_id, Partner_By_Key

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# The message partition every AS4 agreement of the sample data exchanges its messages on
AS4_Default_MPC = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/defaultMPC'

class AS2MDNMode:
    Sync  = 'Synchronous'
    Async = 'Asynchronous'
    Not_Requested = 'None'

class AS4Profile:
    EDelivery1 = 'eDelivery AS4 1.x'
    EDelivery2 = 'eDelivery AS4 2.0'
    Peppol     = 'Peppol'
    ICS2       = 'ICS2'

class AS4TokenType:
    X509v3  = 'X.509 certificate'
    PKIPath = 'X.509 certificate chain'
    SAML20  = 'SAML 2.0 assertion'

# ################################################################################################################################
# ################################################################################################################################

class EbXMLSettings(NamedTuple):
    persist_days: int
    sync_reply: str
    is_signed_ack: bool

# ################################################################################################################################

class AS2Settings(NamedTuple):
    sign_algorithm: str
    encryption_algorithm: str
    is_compressed: bool
    mdn_mode: str
    is_mdn_signed: bool
    mdn_overdue_minutes: int

# ################################################################################################################################

class AS4Settings(NamedTuple):
    profile: str
    mpc: str
    token_type: str
    is_receipt_signed: bool
    missing_receipt_hours: int

# ################################################################################################################################

AgreementSettings:TypeAlias = 'EbXMLSettings | AS2Settings | AS4Settings'

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
    tls_version: str
    settings: 'AgreementSettings'

    @property
    def protocol(self) -> 'str':
        partner = Partner_By_Key[self.partner_key]
        out = partner.protocol
        return out

    @property
    def agreement_id(self) -> 'str':
        partner = Partner_By_Key[self.partner_key]
        out = agreement_id(partner, self.product, self.version)
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

_order_services = ['SubmitOrderv2', 'ChangeOrderv2', 'CancelOrderv2', 'QueryOrderDetailsv2', 'NotifyOfOrderStatusv2']

_complaint_services = ['FileComplaintv2', 'EscalateComplaintv2', 'NotifyOfComplaintStatusv2']

Agreements = [
    Agreement('harborlight', 'Orders', 3, 'Active', -210, 155, _order_services, 3, 5, 'TLS 1.3',
        EbXMLSettings(7, 'mshSignalsOnly', True)),
    Agreement('harborlight', 'Complaints', 2, 'Active', -120, 245, _complaint_services, 3, 5, 'TLS 1.3',
        EbXMLSettings(7, 'mshSignalsOnly', True)),
    Agreement('redwood', 'Orders', 4, 'Active', -64, 301, ['SubmitOrderv2', 'CancelOrderv2', 'NotifyOfOrderStatusv2'],
        3, 5, 'TLS 1.2', AS4Settings(AS4Profile.EDelivery1, AS4_Default_MPC, AS4TokenType.X509v3, True, 24)),
    Agreement('lakeshore', 'Orders', 1, 'Expiring', -347, 18, ['SubmitOrderv2', 'ScheduleInstallationv2',
        'NotifyOfOrderStatusv2'], 3, 5, 'TLS 1.2', AS2Settings('SHA-256', 'AES-128-CBC', True, AS2MDNMode.Sync, True, 30)),
    Agreement('prairie', 'Orders', 2, 'Suspended', -190, 175, ['SubmitOrderv2', 'NotifyOfOrderStatusv2'], 3, 5, 'TLS 1.2',
        AS2Settings('SHA-256', 'AES-256-CBC', False, AS2MDNMode.Async, True, 60)),
    Agreement('bluemesa', 'Orders', 1, 'Proposed', 14, 379, ['SubmitOrderv2', 'QueryOrderDetailsv2',
        'NotifyOfOrderStatusv2'], 3, 15, 'TLS 1.3',
        AS4Settings(AS4Profile.EDelivery2, AS4_Default_MPC, AS4TokenType.PKIPath, True, 24)),
    Agreement('coppercreek', 'Complaints', 1, 'Agreed', 5, 370, _complaint_services, 4, 10, 'TLS 1.3',
        EbXMLSettings(14, 'mshSignalsOnly', True)),
]

Agreement_By_ID = {}

for _agreement in Agreements:
    Agreement_By_ID[_agreement.agreement_id] = _agreement

# ################################################################################################################################

Registrations = [
    Registration('2026-0117', 'bluemesa', 'Orders', 'In review', ['SubmitOrderv2', 'QueryOrderDetailsv2',
        'NotifyOfOrderStatusv2'], 1, [
        RegistrationEvent(9, 'Draft',     'Ashley Whitfield', 'Registration started'),
        RegistrationEvent(6, 'Submitted', 'Ashley Whitfield', 'Submitted for review'),
        RegistrationEvent(2, 'In review', 'Rachel Simmons',   'Signing certificate under verification'),
    ]),
    Registration('2026-0112', 'coppercreek', 'Complaints', 'Approved', _complaint_services, 1, [
        RegistrationEvent(31, 'Draft',     'Daniel Foster',  'Registration started'),
        RegistrationEvent(24, 'Submitted', 'Daniel Foster',  'Submitted for review'),
        RegistrationEvent(17, 'In review', 'Rachel Simmons', 'Endpoint reachable over TLS 1.3'),
        RegistrationEvent(11, 'Approved',  'Rachel Simmons', 'CPA issued for signature'),
    ]),
    Registration('2026-0109', 'redwood', 'Orders', 'Active', ['SubmitOrderv2', 'CancelOrderv2',
        'NotifyOfOrderStatusv2'], 4, [
        RegistrationEvent(80, 'Submitted', 'Marcus Delgado',  'Renewal of agreement version 3'),
        RegistrationEvent(72, 'In review', 'Thomas Whitaker', 'Order change removed from the scope'),
        RegistrationEvent(66, 'Approved',  'Thomas Whitaker', 'P-Mode issued for signature'),
        RegistrationEvent(64, 'Active',    'Thomas Whitaker', 'Agreement signed by both parties'),
    ]),
    Registration('2026-0104', 'harborlight', 'Complaints', 'Active', _complaint_services, 2, [
        RegistrationEvent(140, 'Submitted', 'Jennifer Caldwell', 'Renewal of CPA version 1'),
        RegistrationEvent(126, 'Approved',  'Thomas Whitaker',   'CPA issued for signature'),
        RegistrationEvent(120, 'Active',    'Thomas Whitaker',   'CPA agreed by both parties'),
    ]),
    Registration('2026-0121', 'lakeshore', 'Orders', 'Submitted', ['SubmitOrderv2', 'ScheduleInstallationv2',
        'NotifyOfOrderStatusv2', 'CancelOrderv2'], 2, [
        RegistrationEvent(3, 'Draft',     'Patricia Hollis', 'Renewal of partnership version 1'),
        RegistrationEvent(1, 'Submitted', 'Patricia Hollis', 'Order cancellation added to the scope'),
    ]),
    Registration('2026-0098', 'prairie', 'Orders', 'Suspended', ['SubmitOrderv2', 'NotifyOfOrderStatusv2'],
        2, [
        RegistrationEvent(196, 'Submitted', 'Kevin Brennan',  'Registration started'),
        RegistrationEvent(190, 'Active',    'Rachel Simmons', 'Partnership certificates exchanged'),
        RegistrationEvent(12,  'Suspended', 'Rachel Simmons', 'Signature verification failures over 24 hours'),
    ]),
    Registration('2026-0122', 'bluemesa', 'Complaints', 'Draft', _complaint_services, 1, [
        RegistrationEvent(1, 'Draft', 'Ashley Whitfield', 'Registration started'),
    ]),
    Registration('2026-0087', 'lakeshore', 'Complaints', 'Rejected', ['FileComplaintv2'], 1, [
        RegistrationEvent(48, 'Submitted', 'Patricia Hollis', 'Registration started'),
        RegistrationEvent(41, 'Rejected',  'Rachel Simmons',  'Complaint status notifications are mandatory'),
    ]),
]

# ################################################################################################################################
# ################################################################################################################################
