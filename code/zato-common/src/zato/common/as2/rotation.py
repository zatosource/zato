# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Zato
from zato.common.as2.common import Default
from zato.common.as2.config import _parse_activation_date

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import stranydict
    datetime = datetime
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

def needs_rotation_completion(config:'stranydict', now:'datetime') -> 'bool':
    """ Tells whether a connection's scheduled certificate rotation is ready to be completed -
    there is a next certificate with an activation date and the date plus the grace window has passed.
    """

    # A rotation needs a next certificate to promote ..
    if not config['as2_partner_next_cert']:
        return False

    # .. a next certificate without a date is an extra accepted certificate,
    # .. not a scheduled cutover, so it is never promoted automatically ..
    activation = config['as2_partner_next_cert_from']
    if not activation:
        return False

    # .. and the cutover is completed only once the grace window has also passed, which keeps
    # .. inbound messages signed with the old certificate verifiable shortly after the date.
    activation = _parse_activation_date(activation)
    completion_from = activation + timedelta(days=Default.Rotation_Grace_Days)

    out = now >= completion_from
    return out

# ################################################################################################################################

def complete_rotation(config:'stranydict') -> 'None':
    """ Completes a rotation in place - the next certificate becomes the current one, verbatim,
    and the two next-certificate fields are cleared.
    """
    config['as2_partner_cert'] = config['as2_partner_next_cert']
    config['as2_partner_next_cert'] = ''
    config['as2_partner_next_cert_from'] = ''

# ################################################################################################################################
# ################################################################################################################################
