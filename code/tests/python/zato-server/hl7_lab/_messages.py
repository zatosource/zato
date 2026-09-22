# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Live HL7
from live_hl7 import messages
from live_hl7.messages import Envelope, Order, Patient
from live_hl7.openelis.system import Haemoglobin_LOINC, Order_Message_Type, Order_Sending_Application, \
    Patient_ID_Type, Zato_Sending_Application

# ################################################################################################################################
# ################################################################################################################################

# The analyzer, as it names itself in MSH-3 of its results - the name the LIS registered it under
Analyzer_Application = Zato_Sending_Application

# The laboratory, MSH-4 of everything sent inside it
Lab_Facility = 'LAB'

# The LIS, as its bridge names itself in MSH-3 of its orders and as the analyzer addresses it in MSH-5
LIS_Application = Order_Sending_Application

# An analyzer the LIS never registered
Stranger_Application = 'STRANGER'

# The test every order here is for and the result every analyzer reports - haemoglobin, in grams per decilitre,
# under the code the LIS mapped for the analyzer
Haemoglobin_Name = 'HGB'
Haemoglobin_Units = 'g/dl'
Haemoglobin_Value = '13.7'

# What every control id of the analyzer starts with
Control_ID_Prefix = 'LAB'

# What the rest of the suite reads out of the toolkit through this module
Ack_Accepted = messages.Ack_Accepted
Ack_Application_Error = messages.Ack_Application_Error
Haemoglobin_LOINC = Haemoglobin_LOINC
Order_Message_Type = Order_Message_Type
Recorded = messages.Recorded
field = messages.field
message_type_of = messages.message_type
recorded_containing = messages.recorded_containing
wait_for = messages.wait_for
with_accept_ack = messages.with_accept_ack

# ################################################################################################################################
# ################################################################################################################################

# The analyzer reporting to the LIS
Results_Envelope = Envelope(Analyzer_Application, Lab_Facility, LIS_Application, Lab_Facility)

# An analyzer nobody registered, reporting to the LIS
Stranger_Envelope = Results_Envelope._replace(sending_application=Stranger_Application)

# ################################################################################################################################
# ################################################################################################################################

def new_control_id() -> 'str':
    out = messages.new_control_id(Control_ID_Prefix)
    return out

# ################################################################################################################################

def new_patient(family_name:'str', given_name:'str', birth_date:'str', sex:'str') -> 'Patient':
    out = Patient(messages.new_identifier(Patient_ID_Type), Patient_ID_Type, family_name, given_name, birth_date, sex)
    return out

# ################################################################################################################################

def order_for(accession:'str') -> 'Order':
    """ The haemoglobin order the LIS gave one accession, as the analyzer refers to it in its results.
    """
    out = Order(
        placer_number=messages.new_identifier('PL'),
        accession_number=accession,
        procedure_code=Haemoglobin_LOINC,
        procedure_name=Haemoglobin_Name,
        admission_id='',
        start_date_time=messages.Timestamp,
        modality='',
    )

    return out

# ################################################################################################################################

def build_oru_r01(
    control_id:'str',
    patient:'Patient',
    accession:'str',
    *,
    envelope:'Envelope'=Results_Envelope,
    value:'str'=Haemoglobin_Value,
    ) -> 'str':
    """ One haemoglobin result for one accession.
    """
    observations = [(Haemoglobin_LOINC, value, Haemoglobin_Units)]

    out = messages.build_oru_r01(envelope, control_id, patient, order_for(accession), observations)
    return out

# ################################################################################################################################
# ################################################################################################################################
