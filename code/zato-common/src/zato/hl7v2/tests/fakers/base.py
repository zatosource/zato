# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Faker
from faker import Faker

# ################################################################################################################################
# ################################################################################################################################

fake = Faker()
Faker.seed(12345)

# ################################################################################################################################
# ################################################################################################################################

# The sending sides a message can come from - each one an application in MSH-3 and the facility
# it runs in in MSH-4, drawn as a pair because the two always belong together on a real interface
Sender_Pool = (
    ('HIS_ADT',      'GENERAL_HOSPITAL'),
    ('HIS_ADT',      'ST_MARYS_HOSPITAL'),
    ('EMR_ADT',      'RIVERSIDE_CLINIC'),
    ('REGISTRATION', 'LAKEVIEW_CLINIC'),
    ('SCHEDULING',   'EASTGATE_HOSPITAL'),
    ('ORDER_ENTRY',  'NORTHSIDE_CLINIC'),
    ('LIS_RESULTS',  'CENTRAL_LAB'),
    ('LIS_RESULTS',  'REGIONAL_LAB'),
    ('RIS_IMAGING',  'WESTGATE_IMAGING'),
    ('PHARMACY',     'HOSPITAL_PHARMACY'),
)

# The receiving sides a message can be addressed to - the integration engine
# and the systems behind it, in MSH-5 and MSH-6
Receiver_Pool = (
    ('ZATO',           'INTEGRATION_ENGINE'),
    ('EHR_GATEWAY',    'CENTRAL_HOSPITAL'),
    ('EMR_MAIN',       'CENTRAL_HOSPITAL'),
    ('DATA_WAREHOUSE', 'HEALTH_NETWORK'),
)

# ################################################################################################################################
# ################################################################################################################################

def fake_msh(message_type:'str', trigger:'str', structure_id:'str') -> 'str':
    """ Returns a fake MSH segment for the given message type, trigger and structure ID.
    """

    # The two sides of the exchange, each drawn as an application and its facility ..
    sending_application, sending_facility     = fake.random_element(Sender_Pool)
    receiving_application, receiving_facility = fake.random_element(Receiver_Pool)

    # .. a timestamp and control ID for the header ..
    message_timestamp = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')
    msg_id            = fake.numerify('MSG######')

    # .. and now we can build the whole segment.
    out = (
        f'MSH|^~\\&|{sending_application}|{sending_facility}|'
        f'{receiving_application}|{receiving_facility}|'
        f'{message_timestamp}||'
        f'{message_type}^{trigger}^{structure_id}|{msg_id}|P|2.9\r'
    )

    return out

# ################################################################################################################################

def fake_segment(segment_id:'str') -> 'str':
    """ Returns a minimal valid segment for any segment type.
    """
    out = f'{segment_id}|1\r'
    return out

# ################################################################################################################################
# ################################################################################################################################
