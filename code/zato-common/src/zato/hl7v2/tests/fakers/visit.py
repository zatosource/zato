# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7v2.tests.fakers.base import fake

# ################################################################################################################################
# ################################################################################################################################

def fake_pv1() -> 'str':
    """ Returns a fake PV1 (patient visit) segment.
    """

    # Random details of where the patient is ..
    patient_class = fake.random_element(['I', 'O', 'E'])
    location      = fake.random_element(['ICU', 'ER', 'MED', 'SURG'])
    room          = fake.numerify('###')
    bed           = fake.random_letter().upper()

    # .. random details of the attending doctor ..
    attending_id    = fake.numerify('##########')
    attending_last  = fake.last_name().upper()
    attending_first = fake.first_name().upper()

    # .. random details of the admission itself ..
    service    = fake.random_element(['MED', 'SURG', 'OBS', 'PED'])
    admit_type = fake.random_element(['R', 'E', 'U'])

    # .. random details of the admitting doctor ..
    admitting_id    = fake.numerify('##########')
    admitting_last  = fake.last_name().upper()
    admitting_first = fake.first_name().upper()

    # .. the patient type and admission time ..
    patient_type    = fake.random_element(['IP', 'OP', 'ER'])
    admit_timestamp = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')

    # .. and now we can build the whole segment.
    out = (
        f'PV1|1|{patient_class}|'
        f'{location}^{room}^{bed}|||'
        f'{attending_id}^{attending_last}^{attending_first}^MD|||'
        f'{service}|||||||'
        f'{admit_type}||'
        f'{admitting_id}^{admitting_last}^{admitting_first}^MD|'
        f'{patient_type}||||||||||||||||||'
        f'{admit_timestamp}\r'
    )

    return out

# ################################################################################################################################

def fake_evn(trigger:'str') -> 'str':
    """ Returns a fake EVN (event type) segment for the given trigger.
    """
    event_timestamp = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')

    out = f'EVN|{trigger}|{event_timestamp}\r'
    return out

# ################################################################################################################################

def fake_npu() -> 'str':
    """ Returns a fake NPU (bed status update) segment.
    """

    # Random details of the bed and its status ..
    location = fake.random_element(['ICU', 'ER', 'MED', 'SURG'])
    room     = fake.numerify('###')
    bed      = fake.random_letter().upper()
    status   = fake.random_element(['Y', 'N'])

    # .. and now we can build the whole segment.
    out = f'NPU|{location}^{room}^{bed}|{status}\r'

    return out

# ################################################################################################################################
# ################################################################################################################################
