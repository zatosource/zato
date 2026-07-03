# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7v2.tests.fakers.base import fake

# ################################################################################################################################
# ################################################################################################################################

def fake_stf() -> 'str':
    """ Returns a fake STF (staff identification) segment.
    """

    # Random details of the staff member ..
    staff_id   = fake.numerify('######')
    last_name  = fake.last_name().upper()
    first_name = fake.first_name().upper()
    degree     = fake.random_element(['MD', 'DO', 'NP', 'PA'])
    staff_type = fake.random_element(['MD', 'DO', 'NP', 'PA', 'RN'])

    # .. and now we can build the whole segment.
    out = (
        f'STF|{staff_id}||'
        f'{last_name}^{first_name}^{degree}|||'
        f'{staff_type}\r'
    )

    return out

# ################################################################################################################################

def fake_prd() -> 'str':
    """ Returns a fake PRD (provider data) segment.
    """

    # Random details of the provider ..
    role       = fake.random_element(['RP', 'RT', 'PP'])
    last_name  = fake.last_name().upper()
    first_name = fake.first_name().upper()

    # .. and now we can build the whole segment.
    out = f'PRD|{role}|{last_name}^{first_name}^MD\r'

    return out

# ################################################################################################################################
# ################################################################################################################################
