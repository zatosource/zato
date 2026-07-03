# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7v2.tests.fakers.base import fake

# ################################################################################################################################
# ################################################################################################################################

def fake_msa() -> 'str':
    """ Returns a fake MSA (message acknowledgment) segment.
    """
    msg_id = fake.numerify('MSG######')

    out = f'MSA|AA|{msg_id}\r'
    return out

# ################################################################################################################################

def fake_qak() -> 'str':
    """ Returns a fake QAK (query acknowledgment) segment.
    """
    query_tag = fake.numerify('Q######')

    out = f'QAK|{query_tag}|OK\r'
    return out

# ################################################################################################################################

def fake_qpd(query_name:'str'='IHE PDQ') -> 'str':
    """ Returns a fake QPD (query parameter definition) segment for the given query name.
    """
    query_tag = fake.numerify('Q######')
    mrn       = fake.numerify('######')

    out = f'QPD|{query_name}^QUERY|{query_tag}|{mrn}^^^FAC^MR\r'
    return out

# ################################################################################################################################

def fake_rcp() -> 'str':
    """ Returns a fake RCP (response control parameter) segment.
    """
    quantity = fake.random_int(10, 100)

    out = f'RCP|I|{quantity}^RD\r'
    return out

# ################################################################################################################################

def fake_qrd() -> 'str':
    """ Returns a fake QRD (query definition) segment.
    """

    # Random details of the query ..
    query_timestamp = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')
    query_id        = fake.numerify('Q######')
    quantity        = fake.random_int(10, 100)
    mrn             = fake.numerify('######')

    # .. and now we can build the whole segment.
    out = f'QRD|{query_timestamp}|R|I|{query_id}|||{quantity}^RD|{mrn}^^^FAC^MR|DEM\r'

    return out

# ################################################################################################################################

def fake_dsc() -> 'str':
    """ Returns a fake DSC (continuation pointer) segment.
    """
    continuation_pointer = fake.numerify('CONT######')

    out = f'DSC|{continuation_pointer}|I\r'
    return out

# ################################################################################################################################
# ################################################################################################################################
