# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7v2.tests.fakers.base import fake

# ################################################################################################################################
# ################################################################################################################################

def fake_sch() -> 'str':
    """ Returns a fake SCH (scheduling activity) segment.
    """

    # Random details of the appointment ..
    appointment_id = fake.numerify('APT######')
    duration       = fake.random_int(15, 120)
    priority       = fake.random_element(['ROUTINE', 'URGENT', 'STAT'])

    # .. random details of who booked it ..
    scheduler_id    = fake.numerify('##########')
    scheduler_last  = fake.last_name().upper()
    scheduler_first = fake.first_name().upper()

    # .. and now we can build the whole segment.
    out = (
        f'SCH|{appointment_id}||||||||'
        f'{duration}|MIN|^^{priority}|||||||'
        f'{scheduler_id}^{scheduler_last}^{scheduler_first}|||||BOOKED\r'
    )

    return out

# ################################################################################################################################

def fake_arq() -> 'str':
    """ Returns a fake ARQ (appointment request) segment.
    """

    # Random details of the requested appointment ..
    appointment_id = fake.numerify('APT######')
    duration       = fake.random_int(15, 120)
    priority       = fake.random_element(['ROUTINE', 'URGENT'])

    # .. and now we can build the whole segment.
    out = (
        f'ARQ|{appointment_id}||||||||'
        f'{duration}|MIN|^^{priority}\r'
    )

    return out

# ################################################################################################################################

def fake_rgs() -> 'str':
    """ Returns a fake RGS (resource group) segment.
    """
    resource_id = fake.numerify('RES######')

    out = f'RGS|1||{resource_id}\r'
    return out

# ################################################################################################################################
# ################################################################################################################################
