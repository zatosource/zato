# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Live HL7
from live_hl7 import messages
from live_hl7.messages import Envelope, Patient

# ################################################################################################################################
# ################################################################################################################################

# Who sends - the facilities the exchange knows, as they name themselves in MSH-4, which is also the
# name the shared record files a message's source under
Facility_A = 'FACILITY-A'
Facility_B = 'FACILITY-B'

# The facility's own system, in MSH-3
Facility_B_Application = 'FACILITY-B-EMR'

# Whom the exchange delivers to, in MSH-5 and MSH-6
Receiving_Application = 'SHR'
Receiving_Facility = 'NATIONAL'

# The identifier type the shared record files a patient's national number under
National_ID_Type = 'HIE National ID'

# What every control id of the exchange starts with
Control_ID_Prefix = 'HIE'

# What the rest of the suite reads out of the toolkit through this module
Recorded = messages.Recorded
read_recorded = messages.read_recorded
recorded_with_control_id = messages.recorded_with_control_id
deliveries_with_control_id = messages.deliveries_with_control_id
wait_for = messages.wait_for

# ################################################################################################################################
# ################################################################################################################################

def envelope(facility:'str') -> 'Envelope':
    out = Envelope(Facility_B_Application, facility, Receiving_Application, Receiving_Facility)
    return out

# ################################################################################################################################

def new_control_id() -> 'str':
    out = messages.new_control_id(Control_ID_Prefix)
    return out

# ################################################################################################################################

def new_national_id() -> 'str':
    out = messages.new_identifier('N')
    return out

# ################################################################################################################################

def new_patient(family_name:'str', given_name:'str', birth_date:'str', sex:'str') -> 'Patient':
    out = Patient(new_national_id(), National_ID_Type, family_name, given_name, birth_date, sex)
    return out

# ################################################################################################################################

def build_adt_a28(control_id:'str', patient:'Patient', *, facility:'str'=Facility_B) -> 'str':
    """ A facility adds a person to the shared record.
    """
    out = messages.build_adt_a28(envelope(facility), control_id, patient)
    return out

# ################################################################################################################################

def build_adt_a40(control_id:'str', surviving:'Patient', prior:'Patient', *, facility:'str'=Facility_B) -> 'str':
    """ A facility merges two records of one person - the one in PID survives, the one in MRG goes.
    """
    out = messages.build_adt_a40(envelope(facility), control_id, surviving, prior)
    return out

# ################################################################################################################################
# ################################################################################################################################
