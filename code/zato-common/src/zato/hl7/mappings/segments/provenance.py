# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import Provenance
from zato.hl7.mappings.concepts import cwe_to_codeable_concept
from zato.hl7.mappings.datatypes import xtn_to_contact_points
from zato.hl7.mappings.datetimes import dtm_to_instant
from zato.hl7.mappings.segments.common import No_Consumed_Fields, absent_value, add_location, add_practitioner, \
    add_xon_organization, append_to_list_field, preserve_unmapped, preserve_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# Which PRT field positions apply_prt consumes - the role, the person,
# the organization, the location and the contact points.
_PRT_Role    = 4
_PRT_Telecom = 15
_PRT_Handled = frozenset({_PRT_Role, 5, 8, 9, _PRT_Telecom})

# Which ORC fields the Provenance consumes - who entered the order, who verified it and where it was entered
_ORC_Enterer           = 10
_ORC_Verifier          = 11
_ORC_Enterer_Location  = 13
_ORC_Provenance_Fields = (_ORC_Enterer, _ORC_Verifier, _ORC_Enterer_Location)

# The system of Provenance agent type codes
_Participant_Type_System = 'http://terminology.hl7.org/CodeSystem/provenance-participant-type'

# The agent types the ORC people take
_Enterer_Type  = 'enterer'
_Verifier_Type = 'verifier'

# The list field an Organization from a PRT joins, by the type of the resource it concerns
_Organization_Field_By_Type = {
    'DocumentReference': 'author',
    'ServiceRequest':    'performer',
    'DiagnosticReport':  'performer',
    'Observation':       'performer',
}

# ################################################################################################################################
# ################################################################################################################################

def _agent(type_code:'str', who:'stranydict') -> 'stranydict':
    """ Builds one Provenance agent of the given type.
    """
    coding = {'system': _Participant_Type_System, 'code': type_code}
    agent_type = {'coding': [coding]}

    out = {'type': agent_type, 'who': who}
    return out

# ################################################################################################################################

def add_order_provenance(orc_accessor:'SegmentAccessor', service_request:'any_', context:'ConversionContext') -> 'None':
    """ Builds the Provenance an ORC attests to - who entered the order, who verified it and where it was
    entered - and adds it to the bundle pointing at the ServiceRequest, which must be in the bundle already.
    The recorded time is the transaction time, or the message time when the ORC carries none - with
    neither there is no valid Provenance and the fields are preserved on the request.
    """

    # Our response to produce
    out = Provenance()

    config = context.config

    # Nothing to attest to when none of the provenance fields carries data ..
    populated = orc_accessor.populated_positions()

    if populated.isdisjoint(_ORC_Provenance_Fields):
        return

    # .. the recorded time is the transaction time, or the message time when the ORC carries none ..
    transaction_value = orc_accessor.value(9)
    recorded = dtm_to_instant(transaction_value, config)

    if not recorded:
        recorded = context.message_instant

    # .. with neither there is no time to record and the fields stay on the request ..
    if not recorded:
        for position in _ORC_Provenance_Fields:
            if position in populated:
                serialized = orc_accessor.serialize(position)
                preserve_value(service_request, context, 'ORC', position, serialized)
        return

    target_reference = context.reference_to(service_request)

    out.target = [target_reference]
    out.recorded = recorded

    # .. the people become agents of their kind ..
    agents:'anylist' = []

    enterer_repetition = orc_accessor.first(_ORC_Enterer)

    if enterer := add_practitioner(enterer_repetition, context):
        enterer_agent = _agent(_Enterer_Type, enterer)
        agents.append(enterer_agent)

    verifier_repetition = orc_accessor.first(_ORC_Verifier)

    if verifier := add_practitioner(verifier_repetition, context):
        verifier_agent = _agent(_Verifier_Type, verifier)
        agents.append(verifier_agent)

    # .. an ORC that names only the location still gets an agent, one that says nobody is known ..
    if not agents:
        who = absent_value()
        absent_agent = {'who': who}
        agents.append(absent_agent)

    out.agent = agents

    # .. and the enterer's location is where it all happened.
    location_repetition = orc_accessor.first(_ORC_Enterer_Location)

    if location := add_location(location_repetition, context):
        out.location = location

    _ = context.add(out)

# ################################################################################################################################

def _prt_telecoms(accessor:'SegmentAccessor', context:'ConversionContext') -> 'anylist':
    """ Collects the contact points a PRT carries for its participant.
    """
    config = context.config

    # Our response to produce
    out:'anylist' = []

    for repetition in accessor.repetitions(_PRT_Telecom):
        for telecom in xtn_to_contact_points(repetition, config, default_use='work'):
            out.append(telecom)

    return out

# ################################################################################################################################

def _attach_organization(
    accessor:'SegmentAccessor',
    context:'ConversionContext',
    target:'any_',
    resource_type:'str',
    reference:'stranydict',
    ) -> 'None':
    """ Points a resource at the Organization a PRT names - an Encounter through its service provider,
    a document through its authors, an order, a report or an observation through its performers.
    A slot already taken means the organization is preserved as-is.
    """

    # An Encounter names one service provider, a second one is preserved as-is ..
    if resource_type == 'Encounter':
        current = target.to_dict()

        if 'serviceProvider' in current:
            serialized = accessor.serialize(8)
            preserve_value(target, context, 'PRT', 8, serialized)
        else:
            target.serviceProvider = reference

        return

    # .. everything else appends the organization to the list field it keeps such references in ..
    field_name = _Organization_Field_By_Type.get(resource_type)

    if field_name:
        append_to_list_field(target, field_name, reference)

    # .. and a resource with no such field preserves it as-is.
    else:
        serialized = accessor.serialize(8)
        preserve_value(target, context, 'PRT', 8, serialized)

# ################################################################################################################################

def _attach_location(
    accessor:'SegmentAccessor',
    context:'ConversionContext',
    target:'any_',
    resource_type:'str',
    reference:'stranydict',
    ) -> 'None':
    """ Points a resource at the Location a PRT names - an Encounter through its locations,
    an order through its requested location. Other resources have no place for one, so it is preserved as-is.
    """

    # An Encounter records the place as one of its locations ..
    if resource_type == 'Encounter':
        location_entry = {'location': reference}
        append_to_list_field(target, 'location', location_entry)

    # .. an order records it as where the service is requested ..
    elif resource_type == 'ServiceRequest':
        append_to_list_field(target, 'locationReference', reference)

    # .. and anything else preserves it as-is.
    else:
        serialized = accessor.serialize(9)
        preserve_value(target, context, 'PRT', 9, serialized)

# ################################################################################################################################

def _attach_person(
    accessor:'SegmentAccessor',
    context:'ConversionContext',
    target:'any_',
    resource_type:'str',
    reference:'stranydict',
    ) -> 'None':
    """ Points a resource at the Practitioner a PRT names - an Encounter records a participant
    in the PRT's role, a document an author, everything else a performer - the role then has
    no place of its own and is preserved as-is.
    """
    config = context.config

    role_repetition = accessor.first(_PRT_Role)
    role = cwe_to_codeable_concept(role_repetition, config)

    # An Encounter participant carries the role along ..
    if resource_type == 'Encounter':
        participant:'stranydict' = {'individual': reference}

        if role:
            participant['type'] = [role]

        append_to_list_field(target, 'participant', participant)
        return

    # .. a document records the person as an author, everything else as a performer ..
    if resource_type == 'DocumentReference':
        append_to_list_field(target, 'author', reference)
    else:
        append_to_list_field(target, 'performer', reference)

    # .. and the role has nowhere to go on either of them.
    if role:
        serialized = accessor.serialize(_PRT_Role)
        preserve_value(target, context, 'PRT', _PRT_Role, serialized)

# ################################################################################################################################

def apply_prt(accessor:'SegmentAccessor', context:'ConversionContext', target:'any_') -> 'bool':
    """ Applies PRT - a participation - to the resource the participation is about. The participant
    is the person, the organization or the location the segment names, in that order of preference,
    with the segment's contact points as its own. Every other populated field is preserved on the
    resource. Tells the caller whether the segment was consumed - a PRT with no resource stays whole.
    """

    # Our response to produce
    out = False

    # A PRT with no resource to concern is not consumed here ..
    if not target:
        return out

    out = True

    telecoms = _prt_telecoms(accessor, context)

    target_dict = target.to_dict()
    resource_type = target_dict['resourceType']

    # .. a person is the participant of choice, taking the role along with it ..
    person_repetition = accessor.first(5)

    if reference := add_practitioner(person_repetition, context, telecoms):
        _attach_person(accessor, context, target, resource_type, reference)

        preserve_unmapped(accessor, _PRT_Handled, target, context)
        return out

    # .. an organization comes next, leaving the role behind ..
    organization_repetition = accessor.first(8)

    if reference := add_xon_organization(organization_repetition, context, telecoms):
        _attach_organization(accessor, context, target, resource_type, reference)

        handled = _PRT_Handled - {_PRT_Role}
        preserve_unmapped(accessor, handled, target, context)
        return out

    # .. then a location, which takes neither the role nor the contact points ..
    location_repetition = accessor.first(9)

    if reference := add_location(location_repetition, context):
        _attach_location(accessor, context, target, resource_type, reference)

        handled = _PRT_Handled - {_PRT_Role, _PRT_Telecom}
        preserve_unmapped(accessor, handled, target, context)
        return out

    # .. and a participation that names none of them still concerns the resource,
    # .. so it is preserved there whole.
    preserve_unmapped(accessor, No_Consumed_Fields, target, context)
    return out

# ################################################################################################################################
# ################################################################################################################################
