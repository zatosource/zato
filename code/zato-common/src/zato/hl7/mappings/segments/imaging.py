# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings.concepts import cwe_to_codeable_concept
from zato.hl7.mappings.datatypes import ei_to_identifier
from zato.hl7.mappings.fields import component_value
from zato.hl7.mappings.segments.common import append_to_list_field, preserve_unmapped

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    from zato.fhir import ServiceRequest
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    ServiceRequest = ServiceRequest

# ################################################################################################################################
# ################################################################################################################################

# Which field positions each mapper consumes - anything else that carries data is preserved as an extension.
_IPC_Handled = frozenset({1, 2, 3, 5, 6})
_ZDS_Handled = frozenset({1})

# The system a DICOM study instance UID identifier carries and the prefix its value gets
_Dicom_UID_System = 'urn:dicom:uid'
_Dicom_UID_Prefix = 'urn:oid:'

# The identifier type of an accession number
_Identifier_Type_System = 'http://terminology.hl7.org/CodeSystem/v2-0203'
_Accession_Type_Code = 'ACSN'

# ################################################################################################################################
# ################################################################################################################################

def _study_uid_identifier(uid:'str') -> 'stranydict':
    """ Builds the identifier a DICOM study instance UID becomes.
    """
    out = {'system': _Dicom_UID_System, 'value': _Dicom_UID_Prefix + uid}
    return out

# ################################################################################################################################

def apply_ipc(accessor:'SegmentAccessor', context:'ConversionContext', service_request:'ServiceRequest') -> 'None':
    """ Applies IPC - imaging procedure control - to the ServiceRequest its order group produced.
    """
    config = context.config

    # The accession number identifies the imaging order ..
    accession_repetition = accessor.first(1)

    if accession := ei_to_identifier(accession_repetition, config):
        accession['type'] = {'coding': [{'system': _Identifier_Type_System, 'code': _Accession_Type_Code}]}
        append_to_list_field(service_request, 'identifier', accession)

    # .. the requested procedure ID follows it ..
    procedure_repetition = accessor.first(2)

    if procedure_id := ei_to_identifier(procedure_repetition, config):
        append_to_list_field(service_request, 'identifier', procedure_id)

    # .. the study instance UID identifies the DICOM study the order will produce ..
    study_uid = accessor.component(3, 1)

    if study_uid:
        append_to_list_field(service_request, 'identifier', _study_uid_identifier(study_uid))

    # .. and the modality and the protocol codes detail what is ordered.
    modality_repetition = accessor.first(5)

    if modality := cwe_to_codeable_concept(modality_repetition, config):
        append_to_list_field(service_request, 'orderDetail', modality)

    for repetition in accessor.repetitions(6):
        if protocol := cwe_to_codeable_concept(repetition, config):
            append_to_list_field(service_request, 'orderDetail', protocol)

    preserve_unmapped(accessor, _IPC_Handled, service_request, context)

# ################################################################################################################################

def apply_zds(accessor:'SegmentAccessor', context:'ConversionContext', service_request:'ServiceRequest') -> 'None':
    """ Applies ZDS - the quasi-standard imaging Z-segment - to the ServiceRequest its
    order group produced. Its first field carries the DICOM study instance UID.
    """
    uid_repetition = accessor.first(1)
    study_uid = component_value(uid_repetition, 1)

    if study_uid:
        append_to_list_field(service_request, 'identifier', _study_uid_identifier(study_uid))

    preserve_unmapped(accessor, _ZDS_Handled, service_request, context)

# ################################################################################################################################
# ################################################################################################################################
