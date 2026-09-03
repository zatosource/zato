# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import AllergyIntolerance, Condition, Procedure
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.concepts import cwe_to_codeable_concept
from zato.hl7.mappings.datatypes import ei_to_identifier
from zato.hl7.mappings.fields import component_value
from zato.hl7.mappings.segments.common import Procedure_Status, add_practitioner, append_to_list_field, \
    patient_or_absent_reference, preserve_unmapped, preserve_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict
    from zato.fhir import Encounter
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    Encounter = Encounter
    SegmentAccessor = SegmentAccessor

# ################################################################################################################################
# ################################################################################################################################

# Which field positions each mapper consumes - anything else that carries data is preserved as an extension.
_AL1_Handled = frozenset({1, 2, 3, 4, 5, 6})
_DG1_Handled = frozenset({1, 3, 4, 5, 6, 15, 16, 19})
_PR1_Handled = frozenset({1, 3, 4, 5, 6, 11})
_IAM_Handled = frozenset({1, 2, 3, 4, 5, 6, 7, 11, 13})

# The IAM-6 action codes - a deleted allergy was entered in error,
# the other codes assert the allergy as it stands.
_Allergy_Deleted = 'D'
_Allergy_Asserted_Actions = ('A', 'U', 'X')

# The verification status a deleted allergy gets
_Entered_In_Error_Status = {
    'coding': [{
        'system': 'http://terminology.hl7.org/CodeSystem/allergyintolerance-verification',
        'code': 'entered-in-error',
    }],
}

# ################################################################################################################################
# ################################################################################################################################

def map_al1(accessor:'SegmentAccessor', context:'ConversionContext') -> 'AllergyIntolerance':
    """ Converts AL1 to an AllergyIntolerance.
    """
    config = context.config

    # Our response to produce
    out = AllergyIntolerance()

    # The patient who has the allergy, or the statement that none is known.
    out.patient = patient_or_absent_reference(context)

    # The allergen code is the substance ..
    allergen_repetition = accessor.first(3)

    if code := cwe_to_codeable_concept(allergen_repetition, config):
        out.code = code

    # .. the allergy type decides both the category and the type,
    # .. unknown codes are preserved as-is ..
    type_code = accessor.value(2)

    category = lookup('allergy_category', type_code, config)
    allergy_type = lookup('allergy_type', type_code, config)

    if category:
        out.category = [category['code']]

    if allergy_type:
        out.type_ = allergy_type['code']

    if type_code:
        if not category:
            if not allergy_type:
                preserve_value(out, context, 'AL1', 2, type_code)

    # .. the severity decides the criticality ..
    severity_code = accessor.value(4)

    criticality = lookup('allergy_criticality', severity_code, config)

    if criticality:
        out.criticality = criticality['code']

    # .. the reaction text becomes a manifestation, with the severity when it maps,
    # .. and a severity that maps to neither is preserved as-is ..
    severity = lookup('allergy_severity', severity_code, config)

    if severity_code:
        if not criticality:
            if not severity:
                preserve_value(out, context, 'AL1', 4, severity_code)

    reactions:'anylist' = []

    for repetition in accessor.repetitions(5):
        reaction_text = component_value(repetition, 1)
        if reaction_text:
            reaction:'stranydict' = {'manifestation': [{'text': reaction_text}]}

            if severity:
                reaction['severity'] = severity['code']

            reactions.append(reaction)

    if reactions:
        out.reaction = reactions

    # .. and the identification date is when the allergy was recorded.
    recorded_value = accessor.value(6)
    recorded = context.datetime(recorded_value, 'AL1', 6)

    if recorded:
        out.recordedDate = recorded

    preserve_unmapped(accessor, _AL1_Handled, out, context)

    return out

# ################################################################################################################################

def map_iam(accessor:'SegmentAccessor', context:'ConversionContext') -> 'AllergyIntolerance':
    """ Converts IAM - the successor of AL1 that carries action codes - to an AllergyIntolerance.
    """
    config = context.config

    # Our response to produce
    out = AllergyIntolerance()

    # The patient who has the allergy, or the statement that none is known.
    out.patient = patient_or_absent_reference(context)

    # The allergen code is the substance ..
    allergen_repetition = accessor.first(3)

    if code := cwe_to_codeable_concept(allergen_repetition, config):
        out.code = code

    # .. the allergen type decides both the category and the type,
    # .. unknown codes are preserved as-is ..
    type_code = accessor.component(2, 1)

    category = lookup('allergy_category', type_code, config)
    allergy_type = lookup('allergy_type', type_code, config)

    if category:
        out.category = [category['code']]

    if allergy_type:
        out.type_ = allergy_type['code']

    if type_code:
        if not category:
            if not allergy_type:
                preserve_value(out, context, 'IAM', 2, type_code)

    # .. the severity decides the criticality and the reaction severity ..
    severity_code = accessor.component(4, 1)

    criticality = lookup('allergy_criticality', severity_code, config)
    severity = lookup('allergy_severity', severity_code, config)

    if criticality:
        out.criticality = criticality['code']

    if severity_code:
        if not criticality:
            if not severity:
                preserve_value(out, context, 'IAM', 4, severity_code)

    # .. each reaction code becomes a manifestation, with the severity when it maps ..
    reactions:'anylist' = []

    for repetition in accessor.repetitions(5):
        reaction_text = component_value(repetition, 1)
        if reaction_text:
            reaction:'stranydict' = {'manifestation': [{'text': reaction_text}]}

            if severity:
                reaction['severity'] = severity['code']

            reactions.append(reaction)

    if reactions:
        out.reaction = reactions

    # .. a deleted allergy was entered in error, the other action codes assert
    # the allergy as it stands and unknown ones are preserved as-is ..
    action_code = accessor.component(6, 1)

    if action_code == _Allergy_Deleted:
        out.verificationStatus = _Entered_In_Error_Status
    else:
        if action_code:
            if action_code not in _Allergy_Asserted_Actions:
                preserve_value(out, context, 'IAM', 6, action_code)

    # .. the unique identifier carries over ..
    identifier_repetition = accessor.first(7)

    if identifier := ei_to_identifier(identifier_repetition, config):
        out.identifier = [identifier]

    # .. and the onset and reported times complete the picture.
    onset_value = accessor.value(11)
    onset = context.datetime(onset_value, 'IAM', 11)

    if onset:
        out.onsetDateTime = onset

    reported_value = accessor.value(13)
    reported = context.datetime(reported_value, 'IAM', 13)

    if reported:
        out.recordedDate = reported

    preserve_unmapped(accessor, _IAM_Handled, out, context)

    return out

# ################################################################################################################################

def map_dg1(accessor:'SegmentAccessor', context:'ConversionContext', encounter:'Encounter | None') -> 'Condition':
    """ Converts DG1 to a Condition, also recording it as an encounter diagnosis.
    The Condition adds itself to the bundle so the encounter can point at it.
    """
    config = context.config

    # Our response to produce
    out = Condition()

    # The patient who has the condition, or the statement that none is known.
    out.subject = patient_or_absent_reference(context)

    if context.encounter_reference:
        out.encounter = context.encounter_reference

    # The coded diagnosis is the condition code, the description backs it up.
    diagnosis_repetition = accessor.first(3)
    description = accessor.value(4)

    if code := cwe_to_codeable_concept(diagnosis_repetition, config):
        out.code = code
    elif description:
        out.code = {'text': description}

    onset_value = accessor.value(5)
    onset_datetime = context.datetime(onset_value, 'DG1', 5)

    if onset_datetime:
        out.onsetDateTime = onset_datetime

    # The diagnosing clinician asserts the condition.
    clinician_repetition = accessor.first(16)

    if asserter := add_practitioner(clinician_repetition, context):
        out.asserter = asserter

    recorded_value = accessor.value(19)
    recorded_date = context.datetime(recorded_value, 'DG1', 19)

    if recorded_date:
        out.recordedDate = recorded_date

    # The diagnosis type maps to the encounter diagnosis role, unknown codes are preserved as-is.
    diagnosis_type_code = accessor.value(6)
    diagnosis_role = lookup('diagnosis_type', diagnosis_type_code, config)

    if diagnosis_type_code:
        if not diagnosis_role:
            preserve_value(out, context, 'DG1', 6, diagnosis_type_code)

    preserve_unmapped(accessor, _DG1_Handled, out, context)

    condition_reference = context.add(out)

    # The diagnosis also joins the encounter, with its role and priority when present.
    if encounter:
        diagnosis:'stranydict' = {'condition': condition_reference}

        if diagnosis_role:
            coding = {'system': diagnosis_role['system'], 'code': diagnosis_role['code']}
            diagnosis['use'] = {'coding': [coding]}

        # A numeric priority is the rank, anything else is preserved as-is.
        priority = accessor.value(15)
        if priority:
            if priority.isdigit():
                diagnosis['rank'] = int(priority)
            else:
                preserve_value(out, context, 'DG1', 15, priority)

        append_to_list_field(encounter, 'diagnosis', diagnosis)

    return out

# ################################################################################################################################

def map_pr1(accessor:'SegmentAccessor', context:'ConversionContext') -> 'Procedure':
    """ Converts PR1 to a Procedure.
    """
    config = context.config

    # Our response to produce
    out = Procedure()

    out.status = Procedure_Status

    # The patient the procedure was performed on, or the statement that none is known.
    out.subject = patient_or_absent_reference(context)

    if context.encounter_reference:
        out.encounter = context.encounter_reference

    # The coded procedure is the procedure code, the description backs it up.
    procedure_repetition = accessor.first(3)
    description = accessor.value(4)

    if code := cwe_to_codeable_concept(procedure_repetition, config):
        out.code = code
    elif description:
        out.code = {'text': description}

    performed_value = accessor.value(5)
    performed = context.datetime(performed_value, 'PR1', 5)

    if performed:
        out.performedDateTime = performed

    # The functional type is the category.
    functional_type_repetition = accessor.first(6)

    if category := cwe_to_codeable_concept(functional_type_repetition, config):
        out.category = category

    performers:'anylist' = []

    for repetition in accessor.repetitions(11):
        if reference := add_practitioner(repetition, context):
            performers.append({'actor': reference})

    if performers:
        out.performer = performers

    preserve_unmapped(accessor, _PR1_Handled, out, context)

    return out

# ################################################################################################################################
# ################################################################################################################################
