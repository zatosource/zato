# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

What one alerting sweep produces - a finding per thing that needs attention - and what a partner's
own configuration says about the windows it is held to and whether it wants to be alerted about.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.api import AS2

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone, dictlist
    anydict = anydict
    anydictnone = anydictnone
    dictlist = dictlist

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
finding_list = list['Finding']

# ################################################################################################################################
# ################################################################################################################################

# The kinds of findings one alerting sweep can raise.
Kind_MDN_Overdue         = 'mdn-overdue'
Kind_Ack_Overdue         = 'ack-overdue'
Kind_Cert_Expiry         = 'cert-expiry'
Kind_Ship_Notice_Missing = 'ship-notice-missing'

# The server name alerting events are recorded under when none is given.
Default_Server_Name = 'b2b-alerting'

# The object name a finding about our own keystore certificate is filed under.
Own_Keystore_Name = 'as2-keystore'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Finding:
    """ One thing the alerting sweep found - a digest line and an alert-raised event in the making.
    """
    # Which of the finding kinds this is.
    kind: str = ''

    # The audit source the finding belongs to - as2 or x12.
    source: str = ''

    # The identity pair or object the finding is about, which is also
    # the object name its alert-raised event is filed under.
    partner: str = ''

    # The human-readable digest line.
    message: str = ''

    # The Dashboard path the digest line links to.
    link: str = ''

# ################################################################################################################################

def new_finding(kind:'str', source:'str', partner:'str', message:'str', link:'str') -> 'Finding':

    # Our response to produce
    out = Finding()

    out.kind = kind
    out.source = source
    out.partner = partner
    out.message = message
    out.link = link

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_overdue_seconds(config:'anydictnone') -> 'int':
    """ Returns the overdue window of one partner - its own ack_overdue_after
    or the alerting default when the partner does not set one.
    """
    if config:
        if window := config['ack_overdue_after']:
            out = window
            return out

    out = AS2.Alerting.Default_Ack_Overdue_Seconds
    return out

# ################################################################################################################################

def is_opted_out(config:'anydictnone') -> 'bool':
    """ Tells whether a partner opted out of alerting - no configuration means no opt-out.
    """
    # No matching partner means nothing to opt out of.
    if config is None:
        return False

    # Connections saved before the opt-out existed do not carry the field at all.
    if opt_out := config.get('alerting_opt_out'):
        out = opt_out
    else:
        out = False

    return out

# ################################################################################################################################

def get_ship_notice_window_hours(config:'anydict') -> 'int':
    """ Returns the partner's ship notice window in hours - zero means the guard is off,
    and connections saved before the field existed do not carry it at all.
    """
    if window_hours := config.get('ship_notice_window_hours'):
        out = window_hours
    else:
        out = 0

    return out

# ################################################################################################################################
# ################################################################################################################################

def index_configs_by_as2_pair(configs:'dictlist') -> 'anydict':
    """ Indexes the connections by the AS2 identity pair they exchange messages under.
    Built once per sweep, because the alternative is walking every partner
    for every open message the sweep looks at.
    """
    out:'anydict' = {}

    for config in configs:
        as2_from = config['as2_from']
        as2_to = config['as2_to']
        pair = f'{as2_from}:{as2_to}'

        out[pair] = config

    return out

# ################################################################################################################################

def index_configs_by_isa_id(configs:'dictlist') -> 'anydict':
    """ Indexes the connections by their partner's EDI identifier, which is how X12
    reconciliation pairs map back to partners. Built once per sweep, for the same
    reason the AS2 pair index is.
    """
    out:'anydict' = {}

    for config in configs:
        isa_id = config['isa_id']
        out[isa_id] = config

    return out

# ################################################################################################################################
# ################################################################################################################################
