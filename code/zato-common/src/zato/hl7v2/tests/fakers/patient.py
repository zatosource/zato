# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7v2.tests.fakers.base import fake

# ################################################################################################################################
# ################################################################################################################################

def fake_pid() -> 'str':
    """ Returns a fake PID (patient identification) segment.
    """

    # Random demographics for the patient ..
    mrn           = fake.numerify('######')
    last_name     = fake.last_name().upper()
    first_name    = fake.first_name().upper()
    date_of_birth = fake.date_of_birth(minimum_age=1, maximum_age=90).strftime('%Y%m%d')
    sex           = fake.random_element(['M', 'F'])

    # .. a random address ..
    address = fake.street_address().upper()
    city    = fake.city().upper()
    state   = fake.state_abbr()
    zipcode = fake.zipcode()
    phone   = fake.numerify('##########')

    # .. and now we can build the whole segment.
    out = (
        f'PID|1||{mrn}^^^FAC^MR||'
        f'{last_name}^{first_name}||'
        f'{date_of_birth}|{sex}|||'
        f'{address}^^{city}^{state}^{zipcode}||'
        f'{phone}\r'
    )

    return out

# ################################################################################################################################

def fake_nk1() -> 'str':
    """ Returns a fake NK1 (next of kin) segment.
    """

    # Random details of the next of kin ..
    last_name    = fake.last_name().upper()
    first_name   = fake.first_name().upper()
    relationship = fake.random_element(['SPO', 'PAR', 'CHD', 'SIB'])
    phone        = fake.numerify('##########')

    # .. and now we can build the whole segment.
    out = (
        f'NK1|1|{last_name}^{first_name}|'
        f'{relationship}||{phone}\r'
    )

    return out

# ################################################################################################################################

def fake_mrg() -> 'str':
    """ Returns a fake MRG (merge patient information) segment.
    """
    mrn = fake.numerify('######')

    out = f'MRG|{mrn}^^^FAC^MR\r'
    return out

# ################################################################################################################################

def fake_rel() -> 'str':
    """ Returns a fake REL (clinical relationship) segment.
    """
    first_mrn  = fake.numerify('######')
    second_mrn = fake.numerify('######')

    out = f'REL|1|FAM|{first_mrn}^^^FAC^MR|{second_mrn}^^^FAC^MR\r'
    return out

# ################################################################################################################################
# ################################################################################################################################
