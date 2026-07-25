# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The certificates an exchange rests on - each partner's own and ours - watched for the day they
expire, because a certificate that runs out stops every message with that partner at once.
"""

# stdlib
from datetime import datetime

# Zato
from zato.common.api import AS2
from zato.common.as2.alerting.common import is_opted_out, Kind_Cert_Expiry, new_finding, Own_Keystore_Name
from zato.common.audit_log.api import AuditSource
from zato.common.defaults import default_cluster_id
from zato.common.util.xml_.keystore import load_certificates_pem

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.alerting.common import finding_list
    from zato.common.typing_ import dictlist, intnone
    dictlist = dictlist
    finding_list = finding_list
    intnone = intnone

# ################################################################################################################################
# ################################################################################################################################

# How a day is spelled in a digest line, depending on how many of them are left.
_one_day = 'day'
_many_days = 'days'

# ################################################################################################################################
# ################################################################################################################################

def get_cert_days_left(cert_chain:'str', now:'datetime') -> 'intnone':
    """ Returns how many days are left until the first certificate of a pasted PEM chain
    expires, or None for an empty or unparseable chain.
    """
    if not cert_chain:
        return None

    cert_chain_bytes = cert_chain.encode('utf8')

    try:
        certificates = load_certificates_pem(cert_chain_bytes)
    except ValueError:
        return None

    first_certificate = certificates[0]
    not_after = first_certificate.not_valid_after_utc

    delta = not_after - now

    out = delta.days
    return out

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

def collect_expiring_certificates(configs:'dictlist', now:'datetime', own_cert_chain:'str') -> 'finding_list':
    """ Turns every partner certificate and our own signing certificate inside
    the warning window into a finding.
    """

    # Our response to produce
    out:'finding_list' = []

    # Each partner's pasted certificate is checked against the warning window ..
    for config in configs:

        # The partner said not to alert about it.
        if is_opted_out(config):
            continue

        days_left = get_cert_days_left(config['as2_partner_cert'], now)

        if days_left is None:
            continue

        if days_left >= AS2.Alerting.Cert_Warning_Days:
            continue

        as2_from = config['as2_from']
        as2_to = config['as2_to']
        pair = f'{as2_from}:{as2_to}'

        name = config['name']
        day_suffix = _day_suffix(days_left)
        message = f'Certificate of partner `{name}` ({pair}) expires in {days_left} {day_suffix}'
        link = f'/zato/outgoing/as2/?cluster={default_cluster_id}&type_=outconn-as2'

        finding = new_finding(Kind_Cert_Expiry, AuditSource.AS2, pair, message, link)
        out.append(finding)

    # .. and so is our own signing certificate.
    days_left = get_cert_days_left(own_cert_chain, now)

    if days_left is not None:
        if days_left < AS2.Alerting.Cert_Warning_Days:

            day_suffix = _day_suffix(days_left)
            message = f'Our own AS2 signing certificate expires in {days_left} {day_suffix}'
            link = f'/zato/as2-keystore/?cluster={default_cluster_id}'

            finding = new_finding(Kind_Cert_Expiry, AuditSource.AS2, Own_Keystore_Name, message, link)
            out.append(finding)

    return out

# ################################################################################################################################
# ################################################################################################################################
