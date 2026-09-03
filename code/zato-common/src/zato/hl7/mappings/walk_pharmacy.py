# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings.segments import No_Consumed_Fields, add_order_provenance, apply_rxc, map_rxa, \
    map_rxa_to_administration, map_rxd, map_rxe, map_rxg, map_rxo, preserve_unmapped, start_compound
from zato.hl7.mappings.walk import add_basic, apply_pending_tq1_to_medication, attach_pending_notes

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    from zato.hl7.mappings.walk import WalkState
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    WalkState = WalkState

# ################################################################################################################################
# ################################################################################################################################

# The pharmacy resources whose medication an RXC can turn into a compound
Compound_Owner_Types = frozenset({'MedicationRequest', 'MedicationDispense', 'MedicationAdministration'})

# ################################################################################################################################
# ################################################################################################################################

def _pharmacy_orc(state:'WalkState') -> 'SegmentAccessor | None':
    """ The ORC a pharmacy segment belongs to - the pending one
    or the one the same group's RXO already consumed.
    """
    out = state.pending_orc

    if not out:
        out = state.current_pharmacy_orc

    return out

# ################################################################################################################################

def _add_pharmacy_resource(resource:'any_', state:'WalkState', context:'ConversionContext') -> 'None':
    """ Enters a pharmacy resource into the bundle as the current medication, with the Provenance
    its ORC attests to, and gives it the notes and timing held back for that ORC.
    """
    state.current_medication = resource
    _ = context.add(resource)

    # The pending ORC only attests to the first resource of its group, an RXO's ORC stays for the rest.
    if state.pending_orc:
        add_order_provenance(state.pending_orc, resource, context)

    state.pending_orc = None

    attach_pending_notes(state, resource)
    apply_pending_tq1_to_medication(state, context, resource)

# ################################################################################################################################

def handle_rxa(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    orc = _pharmacy_orc(state)

    # In an immunization message an RXA is an Immunization, anywhere else it records a medication administration.
    if family == 'immunization':
        resource = map_rxa(accessor, orc, context)
    else:
        resource = map_rxa_to_administration(accessor, orc, context)

    _add_pharmacy_resource(resource, state, context)

# ################################################################################################################################

def handle_rxd(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    orc = _pharmacy_orc(state)
    resource = map_rxd(accessor, orc, context)

    _add_pharmacy_resource(resource, state, context)

# ################################################################################################################################

def handle_rxe(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    orc = _pharmacy_orc(state)
    resource = map_rxe(accessor, orc, context)

    _add_pharmacy_resource(resource, state, context)

# ################################################################################################################################

def handle_rxg(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    orc = _pharmacy_orc(state)
    resource = map_rxg(accessor, orc, context)

    _add_pharmacy_resource(resource, state, context)

# ################################################################################################################################

def handle_rxo(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    orc = _pharmacy_orc(state)
    resource = map_rxo(accessor, orc, context)

    _add_pharmacy_resource(resource, state, context)

    # The ORC stays around for the RXE, RXD, RXG or RXA of the same order group.
    state.current_pharmacy_orc = orc

# ################################################################################################################################

def handle_rxc(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    medication = state.current_medication

    # A component with no pharmacy resource to belong to stays whole ..
    if not medication:
        add_basic(accessor, context)
        return

    # .. an Immunization names a vaccine, not a compound, so its components are preserved on it ..
    current = medication.to_dict()
    resource_type = current['resourceType']

    if resource_type not in Compound_Owner_Types:
        preserve_unmapped(accessor, No_Consumed_Fields, medication, context)
        return

    # .. and the first component of a pharmacy resource opens the compound the rest join.
    if state.current_compound_owner is not medication:
        state.current_compound = start_compound(medication, context)
        state.current_compound_owner = medication

    apply_rxc(accessor, context, state.current_compound)

# ################################################################################################################################
# ################################################################################################################################
