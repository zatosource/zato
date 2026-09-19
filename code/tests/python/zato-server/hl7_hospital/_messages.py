# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Live HL7
from live_hl7 import messages
from live_hl7.messages import Envelope, Order, Patient

# ################################################################################################################################
# ################################################################################################################################

# The registration system, as it names itself in MSH-3 and MSH-4 - the sender every feed message comes from
HIS_Application = 'HIS'
Hospital_Facility = 'HOSPITAL'

# The same system as it names itself when its way to the PACS is over TLS
HIS_TLS_Application = 'HIS_TLS'

# The integration engine, as the registration system addresses it in MSH-5 and MSH-6
Engine_Application = 'ZATO'

# The PACS, as it names itself in MSH-3 and MSH-4 of everything it sends
PACS_Application = 'DCM4CHEE'

# The identifier type the hospital's medical record numbers are issued under
MRN_Type = 'MR'

# What every control id of the feed starts with
Control_ID_Prefix = 'HOSP'

# What the rest of the suite reads out of the toolkit through this module
Order_Control_New = messages.Order_Control_New
Recorded = messages.Recorded
control_id_of = messages.control_id
deliveries_with_control_id = messages.deliveries_with_control_id
field = messages.field
message_type_of = messages.message_type
read_recorded = messages.read_recorded
recorded_with_control_id = messages.recorded_with_control_id
wait_for = messages.wait_for

# ################################################################################################################################
# ################################################################################################################################

# The registration system writing to the engine, under either of its names
Feed_Envelope = Envelope(HIS_Application, Hospital_Facility, Engine_Application, Hospital_Facility)
TLS_Feed_Envelope = Envelope(HIS_TLS_Application, Hospital_Facility, Engine_Application, Hospital_Facility)

# MSH-15 as a sender asking for an accept acknowledgment sets it
Accept_Ack_Always = 'AL'

# ################################################################################################################################
# ################################################################################################################################

def new_control_id() -> 'str':
    out = messages.new_control_id(Control_ID_Prefix)
    return out

# ################################################################################################################################

def new_mrn() -> 'str':
    out = messages.new_identifier('MRN')
    return out

# ################################################################################################################################

def new_patient(family_name:'str', given_name:'str', birth_date:'str', sex:'str') -> 'Patient':
    out = Patient(new_mrn(), MRN_Type, family_name, given_name, birth_date, sex)
    return out

# ################################################################################################################################

def new_order(modality:'str', procedure_code:'str', procedure_name:'str') -> 'Order':
    """ One imaging order with fresh placer, accession and admission numbers, scheduled for the timestamp
    every message here carries.
    """
    out = Order(
        placer_number=messages.new_identifier('PL'),
        accession_number=messages.new_identifier('ACC'),
        procedure_code=procedure_code,
        procedure_name=procedure_name,
        admission_id=messages.new_identifier('ADM'),
        start_date_time=messages.Timestamp,
        modality=modality,
    )

    return out

# ################################################################################################################################

def build_adt_a04(control_id:'str', patient:'Patient', admission_id:'str', *, envelope:'Envelope'=Feed_Envelope) -> 'str':
    out = messages.build_adt_a04(envelope, control_id, patient, admission_id)
    return out

# ################################################################################################################################

def with_accept_ack(message:'str') -> 'str':
    """ The message with MSH-15 set to AL - the sender asking to be told the message was received,
    on top of whatever the application says about it.
    """
    segments = messages.split(message)
    msh_fields = segments[0].split('|')

    # MSH-15 is the 14th element after the field separator, which the split does not produce
    msh_index = 14

    while len(msh_fields) <= msh_index:
        msh_fields.append('')

    msh_fields[msh_index] = Accept_Ack_Always
    segments[0] = '|'.join(msh_fields)

    out = messages.join(segments)
    return out

# ################################################################################################################################

def build_adt_a08(control_id:'str', patient:'Patient') -> 'str':
    out = messages.build_adt_a08(Feed_Envelope, control_id, patient)
    return out

# ################################################################################################################################

def build_adt_a40(control_id:'str', surviving:'Patient', prior:'Patient') -> 'str':
    out = messages.build_adt_a40(Feed_Envelope, control_id, surviving, prior)
    return out

# ################################################################################################################################

def build_orm_o01(control_id:'str', patient:'Patient', order:'Order') -> 'str':
    out = messages.build_orm_o01(Feed_Envelope, control_id, patient, order)
    return out

# ################################################################################################################################
# ################################################################################################################################
