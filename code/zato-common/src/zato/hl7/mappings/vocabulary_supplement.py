# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The generated vocabulary in vocabulary.py mirrors the HL7 v2-to-FHIR ConceptMaps exactly.
# This module supplements it with standard v2 table codes the ConceptMaps do not cover
# and with spelled-out variants of those codes that messages can carry.
# The two layers merge in codes.py, with this one applied on top of the generated maps.

# ################################################################################################################################
# ################################################################################################################################

# The systems the FHIR status and code values below belong to
_administrative_gender     = 'http://hl7.org/fhir/administrative-gender'
_name_use                  = 'http://hl7.org/fhir/name-use'
_contact_point_system      = 'http://hl7.org/fhir/contact-point-system'
_appointment_status        = 'http://hl7.org/fhir/appointmentstatus'
_composition_status        = 'http://hl7.org/fhir/composition-status'
_diagnosis_role            = 'http://terminology.hl7.org/CodeSystem/diagnosis-role'
_diagnostic_report_status  = 'http://hl7.org/fhir/diagnostic-report-status'
_document_reference_status = 'http://hl7.org/fhir/document-reference-status'
_issue_severity            = 'http://hl7.org/fhir/issue-severity'
_issue_type                = 'http://hl7.org/fhir/issue-type'
_chargeitem_status         = 'http://hl7.org/fhir/chargeitem-status'
_observation_status        = 'http://hl7.org/fhir/observation-status'
_request_priority          = 'http://hl7.org/fhir/request-priority'
_request_status            = 'http://hl7.org/fhir/request-status'
_response_code             = 'http://hl7.org/fhir/response-code'
_v3_act_code               = 'http://terminology.hl7.org/CodeSystem/v3-ActCode'
_allergy_criticality       = 'http://hl7.org/fhir/allergy-intolerance-criticality'
_reaction_event_severity   = 'http://hl7.org/fhir/reaction-event-severity'
_encounter_status          = 'http://hl7.org/fhir/encounter-status'
_personal_relationship     = 'http://terminology.hl7.org/CodeSystem/v2-0063'
_contact_role              = 'http://terminology.hl7.org/CodeSystem/v2-0131'
_subscriber_relationship   = 'http://terminology.hl7.org/CodeSystem/subscriber-relationship'
_ambulatory_status         = 'http://terminology.hl7.org/CodeSystem/v2-0009'
_special_arrangements      = 'http://terminology.hl7.org/CodeSystem/encounter-special-arrangements'
_special_courtesy          = 'http://terminology.hl7.org/CodeSystem/v3-EncounterSpecialCourtesy'
_readmission_indicator     = 'http://terminology.hl7.org/CodeSystem/v2-0092'
_bed_status                = 'http://terminology.hl7.org/CodeSystem/v2-0116'

# ################################################################################################################################
# ################################################################################################################################

# Codes added on top of the maps vocabulary.py generates, keyed by map name
Supplement = {

    # The sex can arrive spelled out instead of coded.
    'administrative_sex': {
        'Female': {'code': 'female', 'system': _administrative_gender},
        'Male': {'code': 'male', 'system': _administrative_gender},
    },

    # Table HL70200 codes the ConceptMap omits - B is the name at birth, an official name.
    'name_type': {
        'B': {'code': 'official', 'system': _name_use},
    },

    # The NET use code of table HL70201 can arrive in equipment slots,
    # where it means an email address.
    'telecom_equipment_type': {
        'NET': {'code': 'email', 'system': _contact_point_system},
    },

    # The patient class can arrive spelled out instead of coded.
    'patient_class': {
        'Inpatient': {'code': 'IMP', 'system': _v3_act_code},
        'Outpatient': {'code': 'AMB', 'system': _v3_act_code},
        'OUTPATIENT': {'code': 'AMB', 'system': _v3_act_code},
        'Emergency': {'code': 'EMER', 'system': _v3_act_code},
    },

    'patient_class_status': {
        'Inpatient': {'code': 'in-progress', 'system': _encounter_status},
        'Outpatient': {'code': 'in-progress', 'system': _encounter_status},
        'OUTPATIENT': {'code': 'in-progress', 'system': _encounter_status},
        'Emergency': {'code': 'in-progress', 'system': _encounter_status},
    },

    # Table HL70085 codes the ConceptMap omits - R is entered but not verified,
    # I and O both mean the result is registered but not yet available.
    'observation_result_status': {
        'R': {'code': 'preliminary', 'system': _observation_status},
        'I': {'code': 'registered', 'system': _observation_status},
        'O': {'code': 'registered', 'system': _observation_status},
    },

    # Table HL70119 order control codes the ConceptMap omits - RE and CN report
    # on a fulfilled order, XO asks for a change to a still-active one.
    'order_status': {
        'RE': {'code': 'completed', 'system': _request_status},
        'CN': {'code': 'completed', 'system': _request_status},
        'XO': {'code': 'active', 'system': _request_status},
        'SC': {'code': 'active', 'system': _request_status},
    },

    # The priority can arrive spelled out instead of coded.
    'order_priority': {
        'STAT': {'code': 'stat', 'system': _request_priority},
        'ROUTINE': {'code': 'routine', 'system': _request_priority},
        'URGENT': {'code': 'urgent', 'system': _request_priority},
        'ASAP': {'code': 'asap', 'system': _request_priority},
    },

    # The report status can arrive spelled out instead of coded.
    'result_status': {
        'Final': {'code': 'final', 'system': _diagnostic_report_status},
    },

    # The filler status codes of table HL70278 can arrive upper-cased,
    # including the single-L spelling of cancelled.
    'filler_status': {
        'BOOKED': {'code': 'booked', 'system': _appointment_status},
        'PENDING': {'code': 'pending', 'system': _appointment_status},
        'CANCELLED': {'code': 'cancelled', 'system': _appointment_status},
        'CANCELED': {'code': 'cancelled', 'system': _appointment_status},
        'COMPLETE': {'code': 'fulfilled', 'system': _appointment_status},
        'NOSHOW': {'code': 'noshow', 'system': _appointment_status},
        'DELETED': {'code': 'entered-in-error', 'system': _appointment_status},
    },

    # Table HL70052 admitting diagnosis, spelled the diagnosis-role way.
    'diagnosis_type': {
        'AD': {'code': 'AD', 'system': _diagnosis_role},
    },

    # The allergy severity can arrive spelled out instead of coded - the
    # criticality follows the ConceptMap, which gives moderate reactions none.
    'allergy_criticality': {
        'SEVERE': {'code': 'high', 'system': _allergy_criticality},
        'MILD': {'code': 'low', 'system': _allergy_criticality},
    },

    'allergy_severity': {
        'SEVERE': {'code': 'severe', 'system': _reaction_event_severity},
        'MODERATE': {'code': 'moderate', 'system': _reaction_event_severity},
        'MILD': {'code': 'mild', 'system': _reaction_event_severity},
    },
}

# ################################################################################################################################
# ################################################################################################################################

# Maps that exist only in this module, with no generated counterpart

# Table HL70283 - referral status from RF1-1 - to request-status
Referral_Status = {
    'A': {'code': 'active', 'system': _request_status},
    'P': {'code': 'draft', 'system': _request_status},
    'R': {'code': 'revoked', 'system': _request_status},
    'E': {'code': 'revoked', 'system': _request_status},
}

# Table HL70038 - order status from ORC-5 - to request-status
Order_State = {
    'A': {'code': 'active', 'system': _request_status},
    'CA': {'code': 'revoked', 'system': _request_status},
    'CM': {'code': 'completed', 'system': _request_status},
    'DC': {'code': 'revoked', 'system': _request_status},
    'ER': {'code': 'entered-in-error', 'system': _request_status},
    'HD': {'code': 'on-hold', 'system': _request_status},
    'IP': {'code': 'active', 'system': _request_status},
    'RP': {'code': 'revoked', 'system': _request_status},
    'SC': {'code': 'active', 'system': _request_status},
    'Pending': {'code': 'active', 'system': _request_status},
    'Final': {'code': 'completed', 'system': _request_status},
    'F': {'code': 'completed', 'system': _request_status},
}

# Table HL70008 - acknowledgment codes from MSA-1 - to MessageHeader response codes
Acknowledgment_Code = {
    'AA': {'code': 'ok', 'system': _response_code},
    'CA': {'code': 'ok', 'system': _response_code},
    'AE': {'code': 'transient-error', 'system': _response_code},
    'CE': {'code': 'transient-error', 'system': _response_code},
    'AR': {'code': 'fatal-error', 'system': _response_code},
    'CR': {'code': 'fatal-error', 'system': _response_code},
}

# Table HL70516 - error severity from ERR-4 - to OperationOutcome issue severity
Error_Severity = {
    'W': {'code': 'warning', 'system': _issue_severity},
    'I': {'code': 'information', 'system': _issue_severity},
    'E': {'code': 'error', 'system': _issue_severity},
    'F': {'code': 'fatal', 'system': _issue_severity},
}

# Table HL70357 - message error condition codes from ERR-3 - to OperationOutcome issue types
Error_Code = {
    '0': {'code': 'informational', 'system': _issue_type},
    '100': {'code': 'structure', 'system': _issue_type},
    '101': {'code': 'required', 'system': _issue_type},
    '102': {'code': 'value', 'system': _issue_type},
    '103': {'code': 'code-invalid', 'system': _issue_type},
    '200': {'code': 'not-supported', 'system': _issue_type},
    '201': {'code': 'not-supported', 'system': _issue_type},
    '202': {'code': 'not-supported', 'system': _issue_type},
    '203': {'code': 'not-supported', 'system': _issue_type},
    '204': {'code': 'not-found', 'system': _issue_type},
    '205': {'code': 'duplicate', 'system': _issue_type},
    '206': {'code': 'lock-error', 'system': _issue_type},
    '207': {'code': 'exception', 'system': _issue_type},
}

# Table HL70017 - transaction types from FT1-6 - to ChargeItem statuses
Transaction_Type = {
    'CG': {'code': 'billable', 'system': _chargeitem_status},
    'CD': {'code': 'not-billable', 'system': _chargeitem_status},
    'CA': {'code': 'not-billable', 'system': _chargeitem_status},
}

# Table HL70271 - document completion status from TXA-17 - to composition status
Document_Completion_Status = {
    'AU': {'code': 'final', 'system': _composition_status},
    'LA': {'code': 'final', 'system': _composition_status},
    'DI': {'code': 'preliminary', 'system': _composition_status},
    'DO': {'code': 'preliminary', 'system': _composition_status},
    'IP': {'code': 'preliminary', 'system': _composition_status},
    'PA': {'code': 'preliminary', 'system': _composition_status},
    'IN': {'code': 'entered-in-error', 'system': _composition_status},
}

# Table HL70273 - document availability status from TXA-19 - to document reference status
Document_Availability_Status = {
    'AV': {'code': 'current', 'system': _document_reference_status},
    'CA': {'code': 'entered-in-error', 'system': _document_reference_status},
    'OB': {'code': 'superseded', 'system': _document_reference_status},
}

# Table HL70063 - personal relationships from NK1-3, GT1-11 and IN1-17.
# The RelatedPerson.relationship value set includes these codes directly,
# so each one keeps itself and gains the table's system.
Personal_Relationship = {
    'ASC': {'code': 'ASC', 'system': _personal_relationship},
    'BRO': {'code': 'BRO', 'system': _personal_relationship},
    'CGV': {'code': 'CGV', 'system': _personal_relationship},
    'CHD': {'code': 'CHD', 'system': _personal_relationship},
    'DEP': {'code': 'DEP', 'system': _personal_relationship},
    'DOM': {'code': 'DOM', 'system': _personal_relationship},
    'EMC': {'code': 'EMC', 'system': _personal_relationship},
    'EME': {'code': 'EME', 'system': _personal_relationship},
    'EMR': {'code': 'EMR', 'system': _personal_relationship},
    'EXF': {'code': 'EXF', 'system': _personal_relationship},
    'FCH': {'code': 'FCH', 'system': _personal_relationship},
    'FND': {'code': 'FND', 'system': _personal_relationship},
    'FTH': {'code': 'FTH', 'system': _personal_relationship},
    'GCH': {'code': 'GCH', 'system': _personal_relationship},
    'GRD': {'code': 'GRD', 'system': _personal_relationship},
    'GRP': {'code': 'GRP', 'system': _personal_relationship},
    'MGR': {'code': 'MGR', 'system': _personal_relationship},
    'MTH': {'code': 'MTH', 'system': _personal_relationship},
    'NCH': {'code': 'NCH', 'system': _personal_relationship},
    'NON': {'code': 'NON', 'system': _personal_relationship},
    'OAD': {'code': 'OAD', 'system': _personal_relationship},
    'OTH': {'code': 'OTH', 'system': _personal_relationship},
    'OWN': {'code': 'OWN', 'system': _personal_relationship},
    'PAR': {'code': 'PAR', 'system': _personal_relationship},
    'SCH': {'code': 'SCH', 'system': _personal_relationship},
    'SEL': {'code': 'SEL', 'system': _personal_relationship},
    'SIB': {'code': 'SIB', 'system': _personal_relationship},
    'SIS': {'code': 'SIS', 'system': _personal_relationship},
    'SPO': {'code': 'SPO', 'system': _personal_relationship},
    'TRA': {'code': 'TRA', 'system': _personal_relationship},
    'UNK': {'code': 'UNK', 'system': _personal_relationship},
    'WRD': {'code': 'WRD', 'system': _personal_relationship},
}

# Table HL70131 - contact roles from NK1-7.
# The RelatedPerson.relationship value set includes these codes directly,
# so each one keeps itself and gains the table's system.
Contact_Role = {
    'BP': {'code': 'BP', 'system': _contact_role},
    'C':  {'code': 'C', 'system': _contact_role},
    'CP': {'code': 'CP', 'system': _contact_role},
    'E':  {'code': 'E', 'system': _contact_role},
    'EP': {'code': 'EP', 'system': _contact_role},
    'F':  {'code': 'F', 'system': _contact_role},
    'I':  {'code': 'I', 'system': _contact_role},
    'N':  {'code': 'N', 'system': _contact_role},
    'O':  {'code': 'O', 'system': _contact_role},
    'PR': {'code': 'PR', 'system': _contact_role},
    'S':  {'code': 'S', 'system': _contact_role},
    'U':  {'code': 'U', 'system': _contact_role},
}

# Table HL70063 - the insured's relationship from IN1-17 - to Coverage's subscriber-relationship.
# The relationship can also arrive spelled out instead of coded.
Subscriber_Relationship = {
    'SEL': {'code': 'self', 'system': _subscriber_relationship},
    'SPO': {'code': 'spouse', 'system': _subscriber_relationship},
    'DOM': {'code': 'common', 'system': _subscriber_relationship},
    'CHD': {'code': 'child', 'system': _subscriber_relationship},
    'NCH': {'code': 'child', 'system': _subscriber_relationship},
    'SCH': {'code': 'child', 'system': _subscriber_relationship},
    'FCH': {'code': 'child', 'system': _subscriber_relationship},
    'MTH': {'code': 'parent', 'system': _subscriber_relationship},
    'FTH': {'code': 'parent', 'system': _subscriber_relationship},
    'PAR': {'code': 'parent', 'system': _subscriber_relationship},
    'OTH': {'code': 'other', 'system': _subscriber_relationship},
    'Self': {'code': 'self', 'system': _subscriber_relationship},
    'Spouse': {'code': 'spouse', 'system': _subscriber_relationship},
    'Child': {'code': 'child', 'system': _subscriber_relationship},
    'Parent': {'code': 'parent', 'system': _subscriber_relationship},
    'Other': {'code': 'other', 'system': _subscriber_relationship},
}

# Table HL70009 - ambulatory status from PV1-15 - to Encounter's special arrangements.
Ambulatory_Status = {
    'A0': {'code': 'A0', 'system': _ambulatory_status},
    'A1': {'code': 'A1', 'system': _ambulatory_status},
    'A2': {'code': 'wheel', 'system': _special_arrangements},
    'A3': {'code': 'A3', 'system': _ambulatory_status},
    'A4': {'code': 'A4', 'system': _ambulatory_status},
    'A5': {'code': 'A5', 'system': _ambulatory_status},
    'A6': {'code': 'A6', 'system': _ambulatory_status},
    'A7': {'code': 'A7', 'system': _ambulatory_status},
    'A8': {'code': 'int', 'system': _special_arrangements},
    'A9': {'code': 'A9', 'system': _ambulatory_status},
    'B1': {'code': 'B1', 'system': _ambulatory_status},
    'B2': {'code': 'B2', 'system': _ambulatory_status},
    'B3': {'code': 'B3', 'system': _ambulatory_status},
    'B4': {'code': 'B4', 'system': _ambulatory_status},
    'B5': {'code': 'B5', 'system': _ambulatory_status},
    'B6': {'code': 'B6', 'system': _ambulatory_status},
}

# Table HL70099 - VIP indicator from PV1-16 - to Encounter's special courtesy.
VIP_Indicator = {
    'VIP': {'code': 'VIP', 'system': _special_courtesy},
    'STF': {'code': 'STF', 'system': _special_courtesy},
    'PRF': {'code': 'PRF', 'system': _special_courtesy},
    'NRM': {'code': 'NRM', 'system': _special_courtesy},
    'EXT': {'code': 'EXT', 'system': _special_courtesy},
    'Y': {'code': 'VIP', 'system': _special_courtesy},
}

# Table HL70092 - re-admission indicator from PV1-13.
Readmission_Indicator = {
    'R': {'code': 'R', 'system': _readmission_indicator},
}

# Table HL70116 - bed status from PV1-40 - to Location's operational status.
Bed_Status = {
    'C': {'code': 'C', 'system': _bed_status},
    'H': {'code': 'H', 'system': _bed_status},
    'I': {'code': 'I', 'system': _bed_status},
    'K': {'code': 'K', 'system': _bed_status},
    'O': {'code': 'O', 'system': _bed_status},
    'U': {'code': 'U', 'system': _bed_status},
}

# The maps above, keyed by the names lookup resolves them under
Standalone_Maps = {
    'ambulatory_status': Ambulatory_Status,
    'vip_indicator': VIP_Indicator,
    'readmission_indicator': Readmission_Indicator,
    'bed_status': Bed_Status,
    'referral_status': Referral_Status,
    'order_state': Order_State,
    'acknowledgment_code': Acknowledgment_Code,
    'contact_role': Contact_Role,
    'error_severity': Error_Severity,
    'error_code': Error_Code,
    'document_completion_status': Document_Completion_Status,
    'document_availability_status': Document_Availability_Status,
    'personal_relationship': Personal_Relationship,
    'subscriber_relationship': Subscriber_Relationship,
    'transaction_type': Transaction_Type,
}

# ################################################################################################################################
# ################################################################################################################################
