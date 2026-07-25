# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

What the B2B alerting sweep reports about AS4 - the messages whose receipt never arrived, and the
certificates every exchange rests on, watched for the day they expire.

Both are things an operator has to act on rather than things the runtime can resolve on its own: a
receipt that never came means the partner may not hold a document it was sent, and a certificate
that runs out stops every exchange with that partner at once.

The findings are the same kind the other B2B sources produce, so they travel in the same digest and
land in the same alerting history.
"""

from __future__ import annotations

# Zato
from zato.common.api import AS4
from zato.common.as2.alerting.common import Kind_Cert_Expiry, Kind_Receipt_Missing, new_finding
from zato.common.as2.alerting.certificates import get_cert_days_left
from zato.common.as4.audit import party_pair
from zato.common.as4.config import get_text_field
from zato.common.as4.resend import collect_missing_receipts
from zato.common.audit_log.api import AuditSource
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.as2.alerting.common import finding_list
    from zato.common.typing_ import dictlist, stranydict
    datetime = datetime
    dictlist = dictlist
    finding_list = finding_list
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The server name the sweep reads the store under when none is given.
Default_Server_Name = 'as4-alerting'

# How a day is spelled in a digest line, depending on how many of them are left.
_one_day = 'day'
_many_days = 'days'

# ################################################################################################################################

# The Dashboard pages a finding links to, one per side of an exchange.
_outgoing_link = f'/zato/outgoing/as4/?cluster={default_cluster_id}&type_=outconn-as4'
_channel_link = f'/zato/channel/as4/?cluster={default_cluster_id}&type_=channel-as4'

# ################################################################################################################################

# What each watched certificate field holds, as the digest line names it.
_certificate_titles = {
    'as4_signing_cert_chain':    'Own signing certificate',
    'as4_peer_signing_cert':     'Partner signing certificate',
    'as4_peer_encryption_cert':  'Partner encryption certificate',
}

# ################################################################################################################################
# ################################################################################################################################

def _day_suffix(days_left:'int') -> 'str':
    """ Returns how a day is spelled for the given number of days.
    """
    if days_left == 1:
        out = _one_day
    else:
        out = _many_days

    return out

# ################################################################################################################################

def _get_pair(config:'stranydict') -> 'str':
    """ Returns the party pair one AS4 channel or outgoing connection exchanges messages under,
    which is what its findings are filed under too.
    """
    from_party = get_text_field(config, 'as4_from_party')
    to_party = get_text_field(config, 'as4_to_party')

    out = party_pair(from_party, to_party)
    return out

# ################################################################################################################################

def _collect_item_certificates(config:'stranydict', now:'datetime', link:'str') -> 'finding_list':
    """ Turns every certificate of one channel or outgoing connection that is inside the warning
    window into a finding.
    """

    # Our response to produce
    out:'finding_list' = []

    pair = _get_pair(config)
    name = config['name']

    for field_name, title in _certificate_titles.items():

        # A certificate nobody pasted is not a certificate that expires.
        cert_chain = get_text_field(config, field_name)

        if not cert_chain:
            continue

        days_left = get_cert_days_left(cert_chain, now)

        # An unparseable chain is what the Dashboard shows as such - the sweep says nothing about it.
        if days_left is None:
            continue

        if days_left >= AS4.Alerting.Cert_Warning_Days:
            continue

        day_suffix = _day_suffix(days_left)
        message = f'{title} of AS4 `{name}` ({pair}) expires in {days_left} {day_suffix}'

        finding = new_finding(Kind_Cert_Expiry, AuditSource.AS4, pair, message, link)
        out.append(finding)

    return out

# ################################################################################################################################

def collect_expiring_certificates(
    outgoing_configs:'dictlist',
    channel_configs:'dictlist',
    now:'datetime',
    ) -> 'finding_list':
    """ Turns every AS4 certificate inside the warning window into a finding, on both sides of the
    exchange - the sending side's and the receiving one's, because either running out stops it.
    """

    # Our response to produce
    out:'finding_list' = []

    for config in outgoing_configs:
        findings = _collect_item_certificates(config, now, _outgoing_link)
        out.extend(findings)

    for config in channel_configs:
        findings = _collect_item_certificates(config, now, _channel_link)
        out.extend(findings)

    return out

# ################################################################################################################################
# ################################################################################################################################

def collect_missing_receipt_findings(
    outgoing_configs:'dictlist',
    now:'datetime',
    server_name:'str' = Default_Server_Name,
    ) -> 'finding_list':
    """ Turns every message whose receipt never arrived within the window it was given into a
    finding - a delivery that is no longer waiting to be repeated but waiting to be looked at.
    """

    # Our response to produce
    out:'finding_list' = []

    for pending in collect_missing_receipts(outgoing_configs, now, server_name):

        pair = party_pair(pending.from_party, pending.to_party)
        message = f'AS4 receipt is missing for message `{pending.message_id}` sent at {pending.sent_time_iso} ({pair})'

        finding = new_finding(Kind_Receipt_Missing, AuditSource.AS4, pair, message, _outgoing_link)
        out.append(finding)

    return out

# ################################################################################################################################
# ################################################################################################################################

def collect_findings(
    outgoing_configs:'dictlist',
    channel_configs:'dictlist',
    now:'datetime',
    server_name:'str' = Default_Server_Name,
    ) -> 'finding_list':
    """ Runs the AS4 half of one alerting sweep - the messages nobody acknowledged and the
    certificates that are about to expire, in that order.
    """

    # Our response to produce
    out:'finding_list' = []

    missing_receipts = collect_missing_receipt_findings(outgoing_configs, now, server_name)
    expiring_certificates = collect_expiring_certificates(outgoing_configs, channel_configs, now)

    out.extend(missing_receipts)
    out.extend(expiring_certificates)

    return out

# ################################################################################################################################
# ################################################################################################################################
