# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import Condition
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.concepts import cwe_to_codeable_concept
from zato.hl7.mappings.datatypes import ei_to_identifier
from zato.hl7.mappings.segments.common import patient_or_absent_reference, preserve_unmapped, preserve_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    any_ = any_
    stranydict = stranydict
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
dictnone = 'stranydict | None'

# Which field positions the mapper consumes - anything else that carries data is preserved as an extension.
_PRB_Handled = frozenset({1, 2, 3, 4, 7, 9, 13, 14, 16, 17})

# The PRB-1 action codes from table HL70287 - a deleted problem was entered in error,
# the other codes assert the problem as it stands.
_Problem_Deleted = 'DE'
_Problem_Asserted_Actions = ('AD', 'CO', 'LI', 'UC', 'UN', 'UP')

# The verification status a deleted problem gets
_Entered_In_Error_Status = {
    'coding': [{
        'system': 'http://terminology.hl7.org/CodeSystem/condition-ver-status',
        'code': 'entered-in-error',
    }],
}

# A problem list entry's Condition category
_Problem_List_Category = {
    'coding': [{
        'system': 'http://terminology.hl7.org/CodeSystem/condition-category',
        'code': 'problem-list-item',
    }],
}

# When the problem was established - FHIR's standard extension for the date a condition was first asserted
_Asserted_Date_Extension = 'http://hl7.org/fhir/StructureDefinition/condition-assertedDate'

# ################################################################################################################################
# ################################################################################################################################

def _coded_status(
    map_name:'str',
    accessor:'SegmentAccessor',
    position:'int',
    target:'any_',
    context:'ConversionContext',
    ) -> 'dictnone':
    """ Reads one coded PRB status field and returns it as a CodeableConcept - an unknown code
    is preserved as-is on the target and yields nothing.
    """
    code = accessor.component(position, 1)
    if not code:
        return None

    if entry := lookup(map_name, code, context.config):

        out = {'coding': [{'system': entry['system'], 'code': entry['code']}]}
        return out

    # The code has no mapping, so the whole field stays preserved.
    value = accessor.serialize(position)
    preserve_value(target, context, 'PRB', position, value)

    return None

# ################################################################################################################################

def map_prb(accessor:'SegmentAccessor', context:'ConversionContext') -> 'Condition':
    """ Converts PRB - a problem list entry - to a Condition of the problem-list-item category.
    """
    config = context.config

    # Our response to produce
    out = Condition()

    # The patient who has the problem, or the statement that none is known.
    out.subject = patient_or_absent_reference(context)

    if context.encounter_reference:
        out.encounter = context.encounter_reference

    # A problem list entry is exactly what the category says it is.
    out.category = [_Problem_List_Category]

    # The problem ID is the condition code ..
    problem_repetition = accessor.first(3)

    if code := cwe_to_codeable_concept(problem_repetition, config):
        out.code = code

    # .. the problem instance ID identifies this very entry ..
    instance_repetition = accessor.first(4)

    if identifier := ei_to_identifier(instance_repetition, config):
        out.identifier = [identifier]

    # .. the action time is when this entry was recorded ..
    action_value = accessor.value(2)
    action_time = context.datetime(action_value, 'PRB', 2)

    if action_time:
        out.recordedDate = action_time

    # .. when the problem was established goes to the standard asserted-date extension ..
    established_value = accessor.value(7)
    established = context.datetime(established_value, 'PRB', 7)

    if established:
        out.extension = [{'url': _Asserted_Date_Extension, 'valueDateTime': established}]

    # .. the onset is the date when there is one, otherwise the onset text ..
    onset_value = accessor.value(16)
    onset = context.datetime(onset_value, 'PRB', 16)

    onset_text = accessor.value(17)

    if onset:
        out.onsetDateTime = onset

        if onset_text:
            preserve_value(out, context, 'PRB', 17, onset_text)

    elif onset_text:
        out.onsetString = onset_text

    # .. the actual resolution time is when the problem abated ..
    resolution_value = accessor.value(9)
    resolution = context.datetime(resolution_value, 'PRB', 9)

    if resolution:
        out.abatementDateTime = resolution

    # .. the confirmation status is the verification status and the life
    # cycle status the clinical status, unknown codes stay preserved ..
    if verification := _coded_status('problem_confirmation_status', accessor, 13, out, context):
        out.verificationStatus = verification

    if clinical := _coded_status('problem_lifecycle_status', accessor, 14, out, context):
        out.clinicalStatus = clinical

    # .. and a deleted problem was entered in error, overriding the confirmation status -
    # the other action codes assert the problem as it stands and unknown ones are preserved as-is.
    action_code = accessor.value(1)

    if action_code == _Problem_Deleted:
        out.verificationStatus = _Entered_In_Error_Status
    else:
        if action_code:
            if action_code not in _Problem_Asserted_Actions:
                preserve_value(out, context, 'PRB', 1, action_code)

    preserve_unmapped(accessor, _PRB_Handled, out, context)

    return out

# ################################################################################################################################
# ################################################################################################################################
