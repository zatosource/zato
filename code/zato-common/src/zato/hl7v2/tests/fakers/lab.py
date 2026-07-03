# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7v2.tests.fakers.base import fake

# ################################################################################################################################
# ################################################################################################################################

def fake_spm() -> 'str':
    """ Returns a fake SPM (specimen) segment.
    """

    # Random details of the specimen ..
    specimen_type = fake.random_element(['BLD', 'UR', 'SER', 'PLA'])
    specimen_name = fake.random_element(['BLOOD', 'URINE', 'SERUM', 'PLASMA'])

    # .. and now we can build the whole segment.
    out = f'SPM|1||{specimen_type}^{specimen_name}\r'

    return out

# ################################################################################################################################

def fake_equ() -> 'str':
    """ Returns a fake EQU (equipment detail) segment.
    """

    # Random details of the equipment ..
    equipment_id    = fake.numerify('EQ######')
    event_timestamp = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')

    # .. and now we can build the whole segment.
    out = f'EQU|{equipment_id}|{event_timestamp}|OP\r'

    return out

# ################################################################################################################################

def fake_inv() -> 'str':
    """ Returns a fake INV (inventory detail) segment.
    """

    # Random details of the inventory item ..
    item_code = fake.numerify('#####')
    item_type = fake.random_element(['REAGENT', 'CONTROL', 'CALIBRATOR'])

    # .. and now we can build the whole segment.
    out = f'INV|{item_code}^{item_type}|OK\r'

    return out

# ################################################################################################################################
# ################################################################################################################################
