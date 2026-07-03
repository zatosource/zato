# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7v2.tests.fakers.base import fake

# ################################################################################################################################
# ################################################################################################################################

def fake_orc() -> 'str':
    """ Returns a fake ORC (common order) segment.
    """

    # Random identifiers and a timestamp for the order ..
    order_id        = fake.numerify('ORD######')
    group_id        = fake.numerify('GRP####')
    order_timestamp = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')

    # .. random details of the ordering provider ..
    provider_id    = fake.numerify('##########')
    provider_last  = fake.last_name().upper()
    provider_first = fake.first_name().upper()

    # .. and now we can build the whole segment.
    out = (
        f'ORC|NW|{order_id}||{group_id}||||'
        f'{order_timestamp}|||'
        f'{provider_id}^{provider_last}^{provider_first}^MD\r'
    )

    return out

# ################################################################################################################################

def fake_obr() -> 'str':
    """ Returns a fake OBR (observation request) segment.
    """

    # Random details of the requested test ..
    order_id              = fake.numerify('ORD######')
    test_code             = fake.numerify('#####')
    test_name             = fake.random_element(['CBC', 'BMP', 'CMP', 'LIPID', 'TSH', 'HBA1C'])
    observation_timestamp = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')

    # .. random details of the ordering provider ..
    provider_id    = fake.numerify('##########')
    provider_last  = fake.last_name().upper()
    provider_first = fake.first_name().upper()

    # .. and now we can build the whole segment.
    out = (
        f'OBR|1|{order_id}||'
        f'{test_code}^{test_name}^L|||'
        f'{observation_timestamp}|||||||||'
        f'{provider_id}^{provider_last}^{provider_first}^MD\r'
    )

    return out

# ################################################################################################################################

def fake_obx(set_id:'int'=1) -> 'str':
    """ Returns a fake OBX (observation result) segment with the given set ID.
    """

    # A random numeric result ..
    value = fake.pyfloat(min_value=1, max_value=500, right_digits=2)

    # .. random details of what was observed ..
    observation_code = fake.numerify('#####')
    observation_name = fake.random_element(['WBC', 'RBC', 'HGB', 'HCT', 'PLT', 'GLUC', 'BUN', 'CREAT'])
    units            = fake.random_element(['mg/dL', 'g/dL', '10*3/uL', '10*6/uL', '%'])

    # .. a reference range derived from the result itself ..
    reference_low  = value * 0.8
    reference_low  = round(reference_low, 2)
    reference_high = value * 1.2
    reference_high = round(reference_high, 2)

    # .. a random abnormality flag ..
    abnormal_flag = fake.random_element(['N', 'H', 'L'])

    # .. and now we can build the whole segment.
    out = (
        f'OBX|{set_id}|NM|'
        f'{observation_code}^{observation_name}^L||'
        f'{value}|{units}|'
        f'{reference_low}-{reference_high}|'
        f'{abnormal_flag}|||F\r'
    )

    return out

# ################################################################################################################################
# ################################################################################################################################
