# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This module is generated from the HL7 v2-to-FHIR ConceptMap files
# by tests/python/zato-common/hl7_fhir/generate_vocabulary.py - do not edit it by hand.

# ################################################################################################################################
# ################################################################################################################################


# Table HL70078 to V3 ObservationInterpretation Map
# Source: http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation
abnormal_flags = {
    '<': {'code': '<', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    '>': {'code': '>', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'A': {'code': 'A', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'AA': {'code': 'AA', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'B': {'code': 'B', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'CAR': {'code': 'CAR', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'D': {'code': 'D', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'DET': {'code': 'DET', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'E': {'code': 'E', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'EX': {'code': 'EX', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'EXP': {'code': 'EXP', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'H': {'code': 'H', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'HH': {'code': 'HH', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'HU': {'code': 'HU', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'I': {'code': 'I', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'IE': {'code': 'IE', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'IND': {'code': 'IND', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'L': {'code': 'L', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'LL': {'code': 'LL', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'LU': {'code': 'LU', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'MS': {'code': 'MS', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'N': {'code': 'N', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'NCL': {'code': 'NCL', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'ND': {'code': 'ND', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'NEG': {'code': 'NEG', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'NR': {'code': 'NR', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'NS': {'code': 'NS', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'POS': {'code': 'POS', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'R': {'code': 'R', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'RR': {'code': 'RR', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'S': {'code': 'S', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'SDD': {'code': 'SDD', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'SYN-R': {'code': 'SYN-R', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'SYN-S': {'code': 'SYN-S', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'U': {'code': 'U', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'VS': {'code': 'VS', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'UNE': {'code': 'UNE', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'W': {'code': 'W', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
    'WR': {'code': 'WR', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'},
}

# ################################################################################################################################

# Table HL70190 to Address Use Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0190
address_type = {
    'BA': {'code': 'old', 'system': 'http://hl7.org/fhir/address-use'},
    'BI': {'code': 'billing', 'system': 'http://hl7.org/fhir/address-use'},
    'C': {'code': 'temp', 'system': 'http://hl7.org/fhir/address-use'},
    'B': {'code': 'work', 'system': 'http://hl7.org/fhir/address-use'},
    'H': {'code': 'home', 'system': 'http://hl7.org/fhir/address-use'},
    'O': {'code': 'work', 'system': 'http://hl7.org/fhir/address-use'},
}

# ################################################################################################################################

# Table HL70001 to Administrative Gender Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0001
administrative_sex = {
    'F': {'code': 'female', 'system': 'http://hl7.org/fhir/administrative-gender'},
    'M': {'code': 'male', 'system': 'http://hl7.org/fhir/administrative-gender'},
    'O': {'code': 'other', 'system': 'http://hl7.org/fhir/administrative-gender'},
    'U': {'code': 'unknown', 'system': 'http://hl7.org/fhir/administrative-gender'},
    'A': {'code': 'other', 'system': 'http://hl7.org/fhir/administrative-gender'},
    'N': {'code': 'other', 'system': 'http://hl7.org/fhir/administrative-gender'},
}

# ################################################################################################################################

# Table HL70127 to Allergy Intolerance Category Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0127
allergy_category = {
    'DA': {'code': 'medication', 'system': 'http://hl7.org/fhir/allergy-intolerance-category'},
    'FA': {'code': 'food', 'system': 'http://hl7.org/fhir/allergy-intolerance-category'},
    'EA': {'code': 'environment', 'system': 'http://hl7.org/fhir/allergy-intolerance-category'},
    'AA': {'code': 'biologic', 'system': 'http://hl7.org/fhir/allergy-intolerance-category'},
    'PA': {'code': 'environment', 'system': 'http://hl7.org/fhir/allergy-intolerance-category'},
    'LA': {'code': 'environment', 'system': 'http://hl7.org/fhir/allergy-intolerance-category'},
}

# ################################################################################################################################

# Table HL70128 to Allergy Intolerance Criticality Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0128
allergy_criticality = {
    'SV': {'code': 'high', 'system': 'http://hl7.org/fhir/allergy-intolerance-criticality'},
    'MI': {'code': 'low', 'system': 'http://hl7.org/fhir/allergy-intolerance-criticality'},
}

# ################################################################################################################################

# Table HL70128 to Reaction Event Severity Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0128
allergy_severity = {
    'SV': {'code': 'severe', 'system': 'http://hl7.org/fhir/reaction-event-severity'},
    'MO': {'code': 'moderate', 'system': 'http://hl7.org/fhir/reaction-event-severity'},
    'MI': {'code': 'mild', 'system': 'http://hl7.org/fhir/reaction-event-severity'},
}

# ################################################################################################################################

# Table HL70127 to Allergy Intolerance Type Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0127
allergy_type = {
    'DA': {'code': 'allergy', 'system': 'http://hl7.org/fhir/allergy-intolerance-type'},
    'FA': {'code': 'allergy', 'system': 'http://hl7.org/fhir/allergy-intolerance-type'},
    'MA': {'code': 'allergy', 'system': 'http://hl7.org/fhir/allergy-intolerance-type'},
    'EA': {'code': 'allergy', 'system': 'http://hl7.org/fhir/allergy-intolerance-type'},
    'AA': {'code': 'allergy', 'system': 'http://hl7.org/fhir/allergy-intolerance-type'},
    'PA': {'code': 'allergy', 'system': 'http://hl7.org/fhir/allergy-intolerance-type'},
    'LA': {'code': 'allergy', 'system': 'http://hl7.org/fhir/allergy-intolerance-type'},
}

# ################################################################################################################################

# Table HL70322 to Event Status Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0322
completion_status = {
    'CP': {'code': 'completed', 'system': 'http://hl7.org/fhir/event-status'},
    'RE': {'code': 'not-done', 'system': 'http://hl7.org/fhir/event-status'},
    'NA': {'code': 'not-done', 'system': 'http://hl7.org/fhir/event-status'},
    'PA': {'code': 'completed', 'system': 'http://hl7.org/fhir/event-status'},
}

# ################################################################################################################################

# Table HL70052 to Diagnosis Role Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0052
diagnosis_type = {
    'A': {'code': 'AD', 'system': 'http://terminology.hl7.org/CodeSystem/diagnosis-role'},
}

# ################################################################################################################################

# Table HL70278 to Appointmentstatus Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0278
filler_status = {
    'Pending': {'code': 'pending', 'system': 'http://hl7.org/fhir/appointmentstatus'},
    'Waitlist': {'code': 'waitlist', 'system': 'http://hl7.org/fhir/appointmentstatus'},
    'Booked': {'code': 'booked', 'system': 'http://hl7.org/fhir/appointmentstatus'},
    'Started': {'code': 'checked-in', 'system': 'http://hl7.org/fhir/appointmentstatus'},
    'Complete': {'code': 'fulfilled', 'system': 'http://hl7.org/fhir/appointmentstatus'},
    'Cancelled': {'code': 'cancelled', 'system': 'http://hl7.org/fhir/appointmentstatus'},
    'Deleted': {'code': 'entered-in-error', 'system': 'http://hl7.org/fhir/appointmentstatus'},
    'Noshow': {'code': 'noshow', 'system': 'http://hl7.org/fhir/appointmentstatus'},
}

# ################################################################################################################################

# Table HL70002 to V3 MaritalStatus Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0002
marital_status = {
    'A': {'code': 'L', 'system': 'http://terminology.hl7.org/CodeSystem/v3-MaritalStatus'},
    'D': {'code': 'D', 'system': 'http://terminology.hl7.org/CodeSystem/v3-MaritalStatus'},
    'M': {'code': 'M', 'system': 'http://terminology.hl7.org/CodeSystem/v3-MaritalStatus'},
    'S': {'code': 'S', 'system': 'http://terminology.hl7.org/CodeSystem/v3-MaritalStatus'},
    'W': {'code': 'W', 'system': 'http://terminology.hl7.org/CodeSystem/v3-MaritalStatus'},
    'C': {'code': 'C', 'system': 'http://terminology.hl7.org/CodeSystem/v3-MaritalStatus'},
    'G': {'code': 'T', 'system': 'http://terminology.hl7.org/CodeSystem/v3-MaritalStatus'},
    'P': {'code': 'T', 'system': 'http://terminology.hl7.org/CodeSystem/v3-MaritalStatus'},
    'R': {'code': 'T', 'system': 'http://terminology.hl7.org/CodeSystem/v3-MaritalStatus'},
    'E': {'code': 'L', 'system': 'http://terminology.hl7.org/CodeSystem/v3-MaritalStatus'},
    'N': {'code': 'A', 'system': 'http://terminology.hl7.org/CodeSystem/v3-MaritalStatus'},
    'I': {'code': 'I', 'system': 'http://terminology.hl7.org/CodeSystem/v3-MaritalStatus'},
    'B': {'code': 'U', 'system': 'http://terminology.hl7.org/CodeSystem/v3-MaritalStatus'},
    'U': {'code': 'UNK', 'system': 'http://terminology.hl7.org/CodeSystem/v3-NullFlavor'},
    'O': {'code': 'OTH', 'system': 'http://terminology.hl7.org/CodeSystem/v3-NullFlavor'},
    'T': {'code': 'NAVU', 'system': 'http://terminology.hl7.org/CodeSystem/v3-NullFlavor'},
}

# ################################################################################################################################

# Table HL70200 to Name Use Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0200
name_type = {
    'BAD': {'code': 'old', 'system': 'http://hl7.org/fhir/name-use'},
    'D': {'code': 'usual', 'system': 'http://hl7.org/fhir/name-use'},
    'L': {'code': 'official', 'system': 'http://hl7.org/fhir/name-use'},
    'M': {'code': 'maiden', 'system': 'http://hl7.org/fhir/name-use'},
    'MSK': {'code': 'anonymous', 'system': 'http://hl7.org/fhir/name-use'},
    'N': {'code': 'nickname', 'system': 'http://hl7.org/fhir/name-use'},
    'NAV': {'code': 'temp', 'system': 'http://hl7.org/fhir/name-use'},
    'R': {'code': 'official', 'system': 'http://hl7.org/fhir/name-use'},
    'TEMP': {'code': 'temp', 'system': 'http://hl7.org/fhir/name-use'},
}

# ################################################################################################################################

# Table HL70085 to Observation Status Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0085
observation_result_status = {
    'A': {'code': 'amended', 'system': 'http://hl7.org/fhir/observation-status'},
    'C': {'code': 'corrected', 'system': 'http://hl7.org/fhir/observation-status'},
    'D': {'code': 'entered-in-error', 'system': 'http://hl7.org/fhir/observation-status'},
    'F': {'code': 'final', 'system': 'http://hl7.org/fhir/observation-status'},
    'P': {'code': 'preliminary', 'system': 'http://hl7.org/fhir/observation-status'},
    'X': {'code': 'cancelled', 'system': 'http://hl7.org/fhir/observation-status'},
    'W': {'code': 'entered-in-error', 'system': 'http://hl7.org/fhir/observation-status'},
}

# ################################################################################################################################

# Table HL70485 to Request Priority Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0485
order_priority = {
    'S': {'code': 'stat', 'system': 'http://hl7.org/fhir/request-priority'},
    'A': {'code': 'asap', 'system': 'http://hl7.org/fhir/request-priority'},
    'R': {'code': 'routine', 'system': 'http://hl7.org/fhir/request-priority'},
}

# ################################################################################################################################

# Table HL70119 to Request Status Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0119
order_status = {
    'AF': {'code': 'active', 'system': 'http://hl7.org/fhir/request-status'},
    'CA': {'code': 'active', 'system': 'http://hl7.org/fhir/request-status'},
    'CR': {'code': 'revoked', 'system': 'http://hl7.org/fhir/request-status'},
    'DC': {'code': 'revoked', 'system': 'http://hl7.org/fhir/request-status'},
    'DF': {'code': 'revoked', 'system': 'http://hl7.org/fhir/request-status'},
    'DR': {'code': 'revoked', 'system': 'http://hl7.org/fhir/request-status'},
    'FU': {'code': 'completed', 'system': 'http://hl7.org/fhir/request-status'},
    'HD': {'code': 'active', 'system': 'http://hl7.org/fhir/request-status'},
    'HR': {'code': 'on-hold', 'system': 'http://hl7.org/fhir/request-status'},
    'NW': {'code': 'active', 'system': 'http://hl7.org/fhir/request-status'},
    'OC': {'code': 'revoked', 'system': 'http://hl7.org/fhir/request-status'},
    'OD': {'code': 'revoked', 'system': 'http://hl7.org/fhir/request-status'},
    'OH': {'code': 'on-hold', 'system': 'http://hl7.org/fhir/request-status'},
    'OK': {'code': 'active', 'system': 'http://hl7.org/fhir/request-status'},
    'PR': {'code': 'active', 'system': 'http://hl7.org/fhir/request-status'},
    'PY': {'code': 'active', 'system': 'http://hl7.org/fhir/request-status'},
    'RL': {'code': 'active', 'system': 'http://hl7.org/fhir/request-status'},
    'RO': {'code': 'active', 'system': 'http://hl7.org/fhir/request-status'},
    'RQ': {'code': 'active', 'system': 'http://hl7.org/fhir/request-status'},
}

# ################################################################################################################################

# Table HL70004 to V3 ActCode Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0004
patient_class = {
    'E': {'code': 'EMER', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode'},
    'I': {'code': 'IMP', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode'},
    'O': {'code': 'AMB', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode'},
    'P': {'code': 'PRENC', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode'},
    'R': {'code': 'R', 'system': 'http://terminology.hl7.org/CodeSystem/v2-0004'},
    'B': {'code': 'B', 'system': 'http://terminology.hl7.org/CodeSystem/v2-0004'},
    'C': {'code': 'C', 'system': 'http://terminology.hl7.org/CodeSystem/v2-0004'},
    'N': {'code': 'N', 'system': 'http://terminology.hl7.org/CodeSystem/v2-0004'},
    'U': {'code': 'U', 'system': 'http://terminology.hl7.org/CodeSystem/v2-0004'},
}

# ################################################################################################################################

# Table HL70004 to Encounter Status Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0004
patient_class_status = {
    'E': {'code': 'in-progress', 'system': 'http://hl7.org/fhir/encounter-status'},
    'I': {'code': 'in-progress', 'system': 'http://hl7.org/fhir/encounter-status'},
    'O': {'code': 'in-progress', 'system': 'http://hl7.org/fhir/encounter-status'},
    'P': {'code': 'planned', 'system': 'http://hl7.org/fhir/encounter-status'},
    'R': {'code': 'in-progress', 'system': 'http://hl7.org/fhir/encounter-status'},
    'B': {'code': 'in-progress', 'system': 'http://hl7.org/fhir/encounter-status'},
    'C': {'code': 'in-progress', 'system': 'http://hl7.org/fhir/encounter-status'},
    'N': {'code': 'in-progress', 'system': 'http://hl7.org/fhir/encounter-status'},
    'U': {'code': 'unknown', 'system': 'http://hl7.org/fhir/encounter-status'},
}

# ################################################################################################################################

# Table HL70123 [Queries] to Diagnostic Report Status Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0123
result_status = {
    'O': {'code': 'registered', 'system': 'http://hl7.org/fhir/diagnostic-report-status'},
    'I': {'code': 'registered', 'system': 'http://hl7.org/fhir/diagnostic-report-status'},
    'S': {'code': 'registered', 'system': 'http://hl7.org/fhir/diagnostic-report-status'},
    'P': {'code': 'preliminary', 'system': 'http://hl7.org/fhir/diagnostic-report-status'},
    'C': {'code': 'corrected', 'system': 'http://hl7.org/fhir/diagnostic-report-status'},
    'R': {'code': 'partial', 'system': 'http://hl7.org/fhir/diagnostic-report-status'},
    'F': {'code': 'final', 'system': 'http://hl7.org/fhir/diagnostic-report-status'},
    'X': {'code': 'cancelled', 'system': 'http://hl7.org/fhir/diagnostic-report-status'},
}

# ################################################################################################################################

# Table HL70202 to Contact Point System Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0202
telecom_equipment_type = {
    'PH': {'code': 'phone', 'system': 'http://hl7.org/fhir/contact-point-system'},
    'FX': {'code': 'fax', 'system': 'http://hl7.org/fhir/contact-point-system'},
    'MD': {'code': 'other', 'system': 'http://hl7.org/fhir/contact-point-system'},
    'SAT': {'code': 'other', 'system': 'http://hl7.org/fhir/contact-point-system'},
    'BP': {'code': 'pager', 'system': 'http://hl7.org/fhir/contact-point-system'},
    'Internet': {'code': 'email', 'system': 'http://hl7.org/fhir/contact-point-system'},
    'X.400': {'code': 'email', 'system': 'http://hl7.org/fhir/contact-point-system'},
    'TDD': {'code': 'other', 'system': 'http://hl7.org/fhir/contact-point-system'},
    'TTY': {'code': 'other', 'system': 'http://hl7.org/fhir/contact-point-system'},
    'CP': {'code': 'mobile', 'system': 'http://hl7.org/fhir/contact-point-use'},
}

# ################################################################################################################################

# Table HL70201 to Contact Point Use Map
# Source: http://terminology.hl7.org/CodeSystem/v2-0201
telecom_use = {
    'PRN': {'code': 'home', 'system': 'http://hl7.org/fhir/contact-point-use'},
    'WPN': {'code': 'work', 'system': 'http://hl7.org/fhir/contact-point-use'},
    'PRS': {'code': 'mobile', 'system': 'http://hl7.org/fhir/contact-point-use'},
}

# ################################################################################################################################

# Which ConceptMap fixture each map above was generated from
table_sources = {
    'abnormal_flags': 'table-hl70078-to-v3-observationinterpretation',
    'address_type': 'table-hl70190-to-address-use',
    'administrative_sex': 'table-hl70001-to-administrative-gender',
    'allergy_category': 'table-hl70127-to-allergy-intolerance-category',
    'allergy_criticality': 'table-hl70128-to-allergy-intolerance-criticality',
    'allergy_severity': 'table-hl70128-to-reaction-event-severity',
    'allergy_type': 'table-hl70127-to-allergy-intolerance-type',
    'completion_status': 'table-hl70322-to-event-status',
    'diagnosis_type': 'table-hl70052-to-diagnosis-role',
    'filler_status': 'table-hl70278-to-appointmentstatus',
    'marital_status': 'table-hl70002-to-v3-maritalstatus',
    'name_type': 'table-hl70200-to-name-use',
    'observation_result_status': 'table-hl70085-to-observation-status',
    'order_priority': 'table-hl70485-to-request-priority',
    'order_status': 'table-hl70119-to-request-status',
    'patient_class': 'table-hl70004-to-v3-actcode',
    'patient_class_status': 'table-hl70004-to-encounter-status',
    'result_status': 'table-hl70123-queries-to-diagnostic-report-status',
    'telecom_equipment_type': 'table-hl70202-to-contact-point-system',
    'telecom_use': 'table-hl70201-to-contact-point-use',
}

# ################################################################################################################################
# ################################################################################################################################
