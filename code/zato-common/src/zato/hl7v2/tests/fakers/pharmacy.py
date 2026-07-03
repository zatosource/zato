# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7v2.tests.fakers.base import fake

# ################################################################################################################################
# ################################################################################################################################

def fake_rxe() -> 'str':
    """ Returns a fake RXE (pharmacy encoded order) segment.
    """

    # Random details of the drug ..
    drug_code  = fake.numerify('#####')
    drug_name  = fake.random_element(['ASPIRIN', 'LISINOPRIL', 'METFORMIN', 'ATORVASTATIN'])
    dose       = fake.random_int(1, 500)
    dose_units = fake.random_element(['MG', 'MCG', 'ML'])

    # .. random details of how it is to be given ..
    form      = fake.random_element(['TAB', 'CAP', 'INJ', 'SOL'])
    route     = fake.random_element(['PO', 'IV', 'IM', 'SC'])
    frequency = fake.random_element(['QD', 'BID', 'TID', 'QID', 'PRN'])
    quantity  = fake.random_int(10, 90)

    # .. and now we can build the whole segment.
    out = (
        f'RXE|1|{drug_code}^{drug_name}^NDC|'
        f'{dose}|{dose_units}|'
        f'{form}|{route}|'
        f'{frequency}||||||{quantity}\r'
    )

    return out

# ################################################################################################################################

def fake_rxd() -> 'str':
    """ Returns a fake RXD (pharmacy dispense) segment.
    """

    # Random details of the dispensed drug ..
    drug_code          = fake.numerify('#####')
    drug_name          = fake.random_element(['ASPIRIN', 'LISINOPRIL', 'METFORMIN'])
    dispense_timestamp = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')
    dose               = fake.random_int(1, 500)
    dose_units         = fake.random_element(['MG', 'MCG', 'ML'])
    form               = fake.random_element(['TAB', 'CAP', 'INJ'])

    # .. and now we can build the whole segment.
    out = (
        f'RXD|1|{drug_code}^{drug_name}^NDC|'
        f'{dispense_timestamp}|'
        f'{dose}|{dose_units}|'
        f'{form}\r'
    )

    return out

# ################################################################################################################################

def fake_rxa() -> 'str':
    """ Returns a fake RXA (pharmacy administration) segment.
    """

    # Random timestamps of when the administration started and ended ..
    administration_timestamp = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')
    end_timestamp            = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')

    # .. random details of the vaccine given ..
    vaccine_code = fake.numerify('#####')
    vaccine_name = fake.random_element(['FLU', 'COVID', 'TDAP', 'MMR'])

    # .. a random amount between 0.1 and 1.0 ml, in tenths ..
    amount = fake.random_int(1, 10)
    amount = amount / 10

    # .. and now we can build the whole segment.
    out = (
        f'RXA|0|1|{administration_timestamp}|'
        f'{end_timestamp}|'
        f'{vaccine_code}^{vaccine_name}^CVX|'
        f'{amount}|ML\r'
    )

    return out

# ################################################################################################################################

def fake_rxg() -> 'str':
    """ Returns a fake RXG (pharmacy give) segment.
    """

    # Random details of the drug to be given ..
    drug_code  = fake.numerify('#####')
    drug_name  = fake.random_element(['ASPIRIN', 'LISINOPRIL'])
    dose       = fake.random_int(1, 500)
    dose_units = fake.random_element(['MG', 'MCG'])

    # .. and now we can build the whole segment.
    out = (
        f'RXG|1|1|{drug_code}^{drug_name}^NDC|'
        f'{dose}|{dose_units}\r'
    )

    return out

# ################################################################################################################################
# ################################################################################################################################
