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

class AgreementEvent(NamedTuple):
    days_ago: int
    state: str
    user: str
    note: str

agreement_event_list = list[AgreementEvent]

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
    events: 'agreement_event_list'

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
# ################################################################################################################################

_order_services = ['SubmitOrderv2', 'ChangeOrderv2', 'CancelOrderv2', 'QueryOrderDetailsv2', 'NotifyOfOrderStatusv2']

_complaint_services = ['FileComplaintv2', 'EscalateComplaintv2', 'NotifyOfComplaintStatusv2']

Agreements = [
    Agreement('harborlight', 'Orders', 3, 'Active', -210, 155, _order_services, 3, 5, 'TLS 1.3',
        EbXMLSettings(7, 'mshSignalsOnly', True), [
        AgreementEvent(216, 'Proposed', 'Thomas Whitaker',   'Renewal of CPA version 2'),
        AgreementEvent(211, 'Agreed',   'Jennifer Caldwell', 'CPA agreed by both parties'),
        AgreementEvent(210, 'Active',   'Thomas Whitaker',   'CPA version 3 in effect'),
    ]),
    Agreement('harborlight', 'Complaints', 2, 'Active', -120, 245, _complaint_services, 3, 5, 'TLS 1.3',
        EbXMLSettings(7, 'mshSignalsOnly', True), [
        AgreementEvent(126, 'Proposed', 'Thomas Whitaker',   'Renewal of CPA version 1'),
        AgreementEvent(121, 'Agreed',   'Jennifer Caldwell', 'CPA agreed by both parties'),
        AgreementEvent(120, 'Active',   'Thomas Whitaker',   'CPA version 2 in effect'),
    ]),
    Agreement('redwood', 'Orders', 4, 'Active', -64, 301, ['SubmitOrderv2', 'CancelOrderv2', 'NotifyOfOrderStatusv2'],
        3, 5, 'TLS 1.2', AS4Settings(AS4Profile.EDelivery1, AS4_Default_MPC, AS4TokenType.X509v3, True, 24), [
        AgreementEvent(72, 'Proposed', 'Thomas Whitaker', 'Renewal of agreement version 3 without order changes'),
        AgreementEvent(66, 'Agreed',   'Marcus Delgado',  'P-Mode signed by both parties'),
        AgreementEvent(64, 'Active',   'Thomas Whitaker', 'Agreement version 4 in effect'),
    ]),
    Agreement('lakeshore', 'Orders', 1, 'Expiring', -347, 18, ['SubmitOrderv2', 'ScheduleInstallationv2',
        'NotifyOfOrderStatusv2'], 3, 5, 'TLS 1.2', AS2Settings('SHA-256', 'AES-128-CBC', True, AS2MDNMode.Sync, True, 30), [
        AgreementEvent(355, 'Proposed', 'Rachel Simmons',  'Partnership version 1 issued'),
        AgreementEvent(349, 'Agreed',   'Patricia Hollis', 'Partnership certificates exchanged'),
        AgreementEvent(347, 'Active',   'Rachel Simmons',  'Partnership version 1 in effect'),
        AgreementEvent(12,  'Expiring', 'Rachel Simmons',  'Renewal of partnership version 1 requested'),
    ]),
    Agreement('prairie', 'Orders', 2, 'Suspended', -190, 175, ['SubmitOrderv2', 'NotifyOfOrderStatusv2'], 3, 5, 'TLS 1.2',
        AS2Settings('SHA-256', 'AES-256-CBC', False, AS2MDNMode.Async, True, 60), [
        AgreementEvent(196, 'Proposed',  'Rachel Simmons', 'Partnership version 2 issued'),
        AgreementEvent(191, 'Agreed',    'Kevin Brennan',  'Partnership certificates exchanged'),
        AgreementEvent(190, 'Active',    'Rachel Simmons', 'Partnership version 2 in effect'),
        AgreementEvent(12,  'Suspended', 'Rachel Simmons', 'Signature verification failures over 24 hours'),
    ]),
    Agreement('bluemesa', 'Orders', 1, 'Proposed', 14, 379, ['SubmitOrderv2', 'QueryOrderDetailsv2',
        'NotifyOfOrderStatusv2'], 3, 15, 'TLS 1.3',
        AS4Settings(AS4Profile.EDelivery2, AS4_Default_MPC, AS4TokenType.PKIPath, True, 24), [
        AgreementEvent(2, 'Proposed', 'Rachel Simmons', 'P-Mode issued for signature'),
    ]),
    Agreement('coppercreek', 'Complaints', 1, 'Agreed', 5, 370, _complaint_services, 4, 10, 'TLS 1.3',
        EbXMLSettings(14, 'mshSignalsOnly', True), [
        AgreementEvent(11, 'Proposed', 'Rachel Simmons', 'CPA issued for signature'),
        AgreementEvent(4,  'Agreed',   'Daniel Foster',  'CPA agreed by both parties'),
    ]),
]

Agreement_By_ID = {}

for _agreement in Agreements:
    Agreement_By_ID[_agreement.agreement_id] = _agreement

# ################################################################################################################################
# ################################################################################################################################
