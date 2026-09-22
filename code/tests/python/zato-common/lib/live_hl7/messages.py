# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The HL7 v2 messages a live suite sends and what it reads back - each builder takes the parties in an
# Envelope and the clinical content as arguments. Segments are joined with CR, as the wire expects them.

# stdlib
import json
import os
import time
from typing import NamedTuple

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, callable_, strlist

# ################################################################################################################################
# ################################################################################################################################

# The version every message here is written in
Version = '2.5'

# The timestamp every message here carries in MSH-7 and EVN-2
Timestamp = '20260919100000'

# How long a test waits for something asynchronous to show up, and how often it looks
Wait_Timeout = 60
Wait_Interval = 0.5

# What separates segments on the wire
Segment_Separator = '\r'

# How much randomness an identifier carries - 48 bits is 12 hex characters, short enough for MSH-10
# and the identifier fields, long enough that no two of one run collide
Identifier_Bits = 48

# The coding scheme a site's own procedure codes are issued under
Local_Coding_Scheme = 'L'

# TXA-2, TXA-3 and TXA-17 of a document sent as an encapsulated PDF, and OBX-3 naming what the OBX carries
Document_Type_Discharge_Summary = 'DS'
Document_Content_PDF = 'AP'
Document_Status_Authenticated = 'AU'
Document_Observation_ID = 'PDF^Encapsulated document'

# ORC-1 and ORC-5 of a new order - an imaging archive maps the pair to the status of the step it schedules,
# and a pair it has no mapping for is an order it refuses
Order_Control_New = 'NW'
Order_Status_Scheduled = 'SC'

# ORC-1 of results - the order they answer is complete
Order_Control_Results = 'RE'

# MSA-1 of an acknowledgment - the message was taken, or the application could not process it
Ack_Accepted = 'AA'
Ack_Application_Error = 'AE'

# MSH-15 as a sender asking for an accept acknowledgment sets it
Accept_Ack_Always = 'AL'

# MSH-15 is the 14th element after the field separator, which a split of the segment does not produce
MSH_15_Index = 14

# ################################################################################################################################
# ################################################################################################################################

class Envelope(NamedTuple):
    """ Who sends to whom - MSH-3 through MSH-6.
    """
    sending_application: 'str'
    sending_facility: 'str'
    receiving_application: 'str'
    receiving_facility: 'str'

# ################################################################################################################################

class Patient(NamedTuple):
    """ One person, as PID carries them - the identifier and what it is issued under, then demographics.
    """
    patient_id: 'str'
    id_type: 'str'
    family_name: 'str'
    given_name: 'str'
    birth_date: 'str'
    sex: 'str'

# ################################################################################################################################

class Order(NamedTuple):
    """ One imaging or laboratory order - what ORC, OBR and, for an imaging archive, IPC carry.
    """
    placer_number: 'str'
    accession_number: 'str'
    procedure_code: 'str'
    procedure_name: 'str'
    admission_id: 'str'
    start_date_time: 'str'
    modality: 'str'

# ################################################################################################################################

class Recorded(NamedTuple):
    """ One line a recording service wrote.
    """
    channel: 'str'
    message: 'str'

# ################################################################################################################################

recorded_list = list[Recorded]

# ################################################################################################################################
# ################################################################################################################################

def new_control_id(prefix:'str') -> 'str':
    """ A message control id no other message of this run has.
    """
    out = prefix + CryptoManager.generate_hex_string(Identifier_Bits).upper()
    return out

# ################################################################################################################################

def new_identifier(prefix:'str') -> 'str':
    """ A patient or order identifier no other of this run has.
    """
    out = prefix + CryptoManager.generate_hex_string(Identifier_Bits).upper()
    return out

# ################################################################################################################################

def new_patient(id_type:'str', family_name:'str', given_name:'str', birth_date:'str', sex:'str') -> 'Patient':
    out = Patient(new_identifier('P'), id_type, family_name, given_name, birth_date, sex)
    return out

# ################################################################################################################################
# ################################################################################################################################

def msh(envelope:'Envelope', message_type:'str', control_id:'str') -> 'str':
    out = (
        f'MSH|^~\\&|{envelope.sending_application}|{envelope.sending_facility}'
        f'|{envelope.receiving_application}|{envelope.receiving_facility}'
        f'|{Timestamp}||{message_type}|{control_id}|P|{Version}'
    )

    return out

# ################################################################################################################################

def pid(patient:'Patient') -> 'str':
    out = (
        f'PID|1||{patient.patient_id}^^^{patient.id_type}||{patient.family_name}^{patient.given_name}'
        f'||{patient.birth_date}|{patient.sex}'
    )

    return out

# ################################################################################################################################

def join(segments:'strlist') -> 'str':
    out = Segment_Separator.join(segments)
    return out

# ################################################################################################################################

def split(message:'str') -> 'strlist':
    """ The segments of a message, whichever of CR and LF it came with.
    """
    normalized = message.replace('\r\n', '\r').replace('\n', '\r')

    out:'strlist' = []

    for segment in normalized.split('\r'):
        if segment:
            out.append(segment)

    return out

# ################################################################################################################################

def field(message:'str', segment_name:'str', index:'int') -> 'str':
    """ One field of the first segment of the given name - MSH counts its fields from the separator, as
    the standard has it, so MSH-10 is index 10 here as it is everywhere else.
    """
    for segment in split(message):

        fields = segment.split('|')

        if fields[0] != segment_name:
            continue

        if segment_name == 'MSH':
            fields.insert(1, '|')

        if index < len(fields):
            return fields[index]

        return ''

    return ''

# ################################################################################################################################

def message_type(message:'str') -> 'str':
    out = field(message, 'MSH', 9)
    return out

# ################################################################################################################################

def control_id(message:'str') -> 'str':
    out = field(message, 'MSH', 10)
    return out

# ################################################################################################################################

def with_accept_ack(message:'str') -> 'str':
    """ The message with MSH-15 set to AL - the sender asking to be told the message was received,
    on top of whatever the application says about it.
    """
    segments = split(message)
    msh_fields = segments[0].split('|')

    while len(msh_fields) <= MSH_15_Index:
        msh_fields.append('')

    msh_fields[MSH_15_Index] = Accept_Ack_Always
    segments[0] = '|'.join(msh_fields)

    out = join(segments)
    return out

# ################################################################################################################################
# ################################################################################################################################

def build_adt_a01(envelope:'Envelope', message_control_id:'str', patient:'Patient', admission_id:'str') -> 'str':
    """ A patient is admitted.
    """
    segments = [
        msh(envelope, 'ADT^A01^ADT_A01', message_control_id),
        f'EVN|A01|{Timestamp}',
        pid(patient),
        f'PV1|1|I|||||||||||||||||{admission_id}',
    ]

    out = join(segments)
    return out

# ################################################################################################################################

def build_adt_a02(
    envelope:'Envelope',
    message_control_id:'str',
    patient:'Patient',
    admission_id:'str',
    ward:'str',
    ) -> 'str':
    """ A patient is transferred to another ward.
    """
    segments = [
        msh(envelope, 'ADT^A02^ADT_A02', message_control_id),
        f'EVN|A02|{Timestamp}',
        pid(patient),
        f'PV1|1|I|{ward}||||||||||||||||{admission_id}',
    ]

    out = join(segments)
    return out

# ################################################################################################################################

def build_adt_a03(envelope:'Envelope', message_control_id:'str', patient:'Patient', admission_id:'str') -> 'str':
    """ A patient is discharged.
    """
    segments = [
        msh(envelope, 'ADT^A03^ADT_A03', message_control_id),
        f'EVN|A03|{Timestamp}',
        pid(patient),
        f'PV1|1|I|||||||||||||||||{admission_id}||||||||||||||||||||||||||{Timestamp}',
    ]

    out = join(segments)
    return out

# ################################################################################################################################

def build_adt_a04(envelope:'Envelope', message_control_id:'str', patient:'Patient', admission_id:'str') -> 'str':
    """ A patient is registered as an outpatient.
    """
    segments = [
        msh(envelope, 'ADT^A04^ADT_A01', message_control_id),
        f'EVN|A04|{Timestamp}',
        pid(patient),
        f'PV1|1|O|||||||||||||||||{admission_id}',
    ]

    out = join(segments)
    return out

# ################################################################################################################################

def build_adt_a08(envelope:'Envelope', message_control_id:'str', patient:'Patient') -> 'str':
    """ A patient's demographics change.
    """
    segments = [
        msh(envelope, 'ADT^A08^ADT_A01', message_control_id),
        f'EVN|A08|{Timestamp}',
        pid(patient),
        'PV1|1|O',
    ]

    out = join(segments)
    return out

# ################################################################################################################################

def build_adt_a28(envelope:'Envelope', message_control_id:'str', patient:'Patient') -> 'str':
    """ A person is added to a record - the shared record of an exchange, the registry of a site.
    """
    segments = [
        msh(envelope, 'ADT^A28^ADT_A05', message_control_id),
        f'EVN|A28|{Timestamp}',
        pid(patient),
        'PV1|1|O',
    ]

    out = join(segments)
    return out

# ################################################################################################################################

def build_adt_a40(envelope:'Envelope', message_control_id:'str', surviving:'Patient', prior:'Patient') -> 'str':
    """ Two records of one person are merged - the one in PID survives, the one in MRG goes.
    """
    segments = [
        msh(envelope, 'ADT^A40^ADT_A39', message_control_id),
        f'EVN|A40|{Timestamp}',
        pid(surviving),
        f'MRG|{prior.patient_id}^^^{prior.id_type}',
    ]

    out = join(segments)
    return out

# ################################################################################################################################

def build_orm_o01(envelope:'Envelope', message_control_id:'str', patient:'Patient', order:'Order') -> 'str':
    """ A new order, complete enough for an imaging archive to schedule it - the IPC segment is what the scheduled
    procedure step is built from.
    """
    procedure = f'{order.procedure_code}^{order.procedure_name}'
    protocol = f'{order.procedure_code}^{order.procedure_name}^{Local_Coding_Scheme}'

    obr = f'OBR|1|{order.placer_number}||{procedure}||||||||||||||{order.accession_number}|{order.placer_number}'
    ipc = f'IPC|{order.accession_number}|{order.placer_number}||{order.placer_number}|{order.modality}|{protocol}'

    segments = [
        msh(envelope, 'ORM^O01^ORM_O01', message_control_id),
        pid(patient),
        f'PV1|1|O|||||||||||||||||{order.admission_id}',
        f'ORC|{Order_Control_New}|{order.placer_number}|||{Order_Status_Scheduled}||^^^{order.start_date_time}',
        obr,
        ipc,
    ]

    out = join(segments)
    return out

# ################################################################################################################################

def build_oru_r01(
    envelope:'Envelope',
    message_control_id:'str',
    patient:'Patient',
    order:'Order',
    observations:'anylist',
    ) -> 'str':
    """ Results of one order - each observation a triple of identifier, value and units. The accession is the
    filler's number of the order, ORC-3 and OBR-3, which is where a laboratory looks for its own.
    """
    procedure = f'{order.procedure_code}^{order.procedure_name}'
    obr = f'OBR|1|{order.placer_number}|{order.accession_number}|{procedure}|||{Timestamp}'

    segments = [
        msh(envelope, 'ORU^R01^ORU_R01', message_control_id),
        pid(patient),
        f'ORC|{Order_Control_Results}|{order.placer_number}|{order.accession_number}',
        obr,
    ]

    for index, observation in enumerate(observations, 1):
        identifier, value, units = observation
        segments.append(f'OBX|{index}|NM|{identifier}||{value}|{units}|||||F')

    out = join(segments)
    return out

# ################################################################################################################################

def build_mdm_t02(
    envelope:'Envelope',
    message_control_id:'str',
    patient:'Patient',
    document_id:'str',
    document_base64:'str',
    ) -> 'str':
    """ One document about a patient - a PDF, base64 in OBX-5 the way an encapsulated document travels.
    """
    txa = f'TXA|1|{Document_Type_Discharge_Summary}|{Document_Content_PDF}|{Timestamp}||||||||{document_id}||||'
    segments = [
        msh(envelope, 'MDM^T02^MDM_T02', message_control_id),
        pid(patient),
        f'{txa}{Document_Status_Authenticated}',
        f'OBX|1|ED|{Document_Observation_ID}||^application^pdf^Base64^{document_base64}||||||F',
    ]

    out = join(segments)
    return out

# ################################################################################################################################
# ################################################################################################################################

def read_recorded(messages_file:'str') -> 'recorded_list':
    """ Everything the recording services wrote so far.
    """
    out:'recorded_list' = []

    if not os.path.exists(messages_file):
        return out

    with open(messages_file) as file_handle:
        for line in file_handle:
            if line.strip():
                entry = json.loads(line)
                out.append(Recorded(entry['channel'], entry['message']))

    return out

# ################################################################################################################################

def recorded_containing(messages_file:'str', text:'str') -> 'recorded_list':
    """ What was recorded of messages carrying the text - a control id, an accession, whatever names the message.
    """
    out:'recorded_list' = []

    for recorded in read_recorded(messages_file):
        if text in recorded.message:
            out.append(recorded)

    return out

# ################################################################################################################################

def recorded_with_control_id(messages_file:'str', message_control_id:'str') -> 'recorded_list':
    """ What was recorded of one message.
    """
    out = recorded_containing(messages_file, message_control_id)
    return out

# ################################################################################################################################

def wait_for(check:'callable_', what:'str') -> 'None':
    """ Polls until the check says yes, failing with what was waited for when it does not in time.
    """
    deadline = time.monotonic() + Wait_Timeout

    while time.monotonic() < deadline:
        if check():
            return
        time.sleep(Wait_Interval)

    raise Exception(f'Timed out waiting for {what}')

# ################################################################################################################################

def deliveries_with_control_id(deliveries:'anylist', message_control_id:'str') -> 'anylist':
    """ The deliveries a receiver took of one message.
    """
    out:'anylist' = []

    for delivery in deliveries:
        if message_control_id in delivery.text:
            out.append(delivery)

    return out

# ################################################################################################################################
# ################################################################################################################################
