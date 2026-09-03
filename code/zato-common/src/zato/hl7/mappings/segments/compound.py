# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import Medication
from zato.hl7.mappings.concepts import cwe_to_codeable_concept, parse_number, quantity
from zato.hl7.mappings.segments.common import append_to_list_field, preserve_inexact_number, preserve_unmapped, \
    preserve_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictnone, stranydict
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    any_ = any_
    dictnone = dictnone

# ################################################################################################################################
# ################################################################################################################################

# Which RXC field positions the ingredient consumes - the component type, code, amount and its units,
# and the strength volume with its units.
_RXC_Handled = frozenset({1, 2, 3, 4, 8, 9})

# The RXC-1 component types - the base is the vehicle, an additive the active part.
_Base_Component     = 'B'
_Additive_Component = 'A'

# The denominator an ingredient strength gets when the RXC names no volume
_Unit_Denominator = {'value': 1}

# ################################################################################################################################
# ################################################################################################################################

def _component_quantity(
    accessor:'SegmentAccessor',
    amount_position:'int',
    units_position:'int',
    medication:'Medication',
    context:'ConversionContext',
    ) -> 'dictnone':
    """ Builds a Quantity from an RXC amount field and its units field, preserving amounts that are not numbers.
    """
    config = context.config

    # An empty amount builds no quantity ..
    amount = accessor.value(amount_position)

    if not amount:
        return None

    # .. an amount that is not a number is preserved whole ..
    number = parse_number(amount)

    if not number:
        serialized = accessor.serialize(amount_position)
        preserve_value(medication, context, 'RXC', amount_position, serialized)
        return None

    # .. a number the float cannot carry exactly keeps its digits as an extension ..
    if not number.is_exact:
        preserve_inexact_number(medication, context, 'RXC', amount_position, amount)

    # .. and the units field says what the number counts.
    units_repetition = accessor.first(units_position)
    units = cwe_to_codeable_concept(units_repetition, config)

    out = quantity(number.value, units)
    return out

# ################################################################################################################################

def start_compound(pharmacy_resource:'any_', context:'ConversionContext') -> 'Medication':
    """ Opens the compound Medication a pharmacy resource's RXC segments describe - the resource's
    medication code becomes the compound's code and the resource points at the compound instead.
    """
    # Our response to produce
    out = Medication()

    # The resource's own medication code becomes the compound's code ..
    current = pharmacy_resource.to_dict()

    if code := current.get('medicationCodeableConcept'):
        out.code = code

    # .. and the resource points at the compound from then on.
    reference = context.add(out)

    pharmacy_resource.medicationCodeableConcept = None
    pharmacy_resource.medicationReference       = reference

    return out

# ################################################################################################################################

def apply_rxc(accessor:'SegmentAccessor', context:'ConversionContext', compound:'Medication') -> 'None':
    """ Adds one RXC - a pharmacy component - as an ingredient of the compound Medication.
    """
    config = context.config

    ingredient:'stranydict' = {}

    # The component code is the ingredient ..
    code_repetition = accessor.first(2)

    if item := cwe_to_codeable_concept(code_repetition, config):
        ingredient['itemCodeableConcept'] = item

    # .. an additive is the active part, the base the vehicle, other types are preserved as-is ..
    component_type = accessor.value(1)

    if component_type == _Additive_Component:
        ingredient['isActive'] = True
    elif component_type == _Base_Component:
        ingredient['isActive'] = False
    elif component_type:
        preserve_value(compound, context, 'RXC', 1, component_type)

    # .. and the amount over the strength volume - or over one unit of the compound - is the strength.
    if numerator := _component_quantity(accessor, 3, 4, compound, context):
        denominator = _component_quantity(accessor, 8, 9, compound, context)

        if denominator is None:
            denominator = dict(_Unit_Denominator)

        strength = {'numerator': numerator, 'denominator': denominator}
        ingredient['strength'] = strength

    if ingredient:
        append_to_list_field(compound, 'ingredient', ingredient)

    preserve_unmapped(accessor, _RXC_Handled, compound, context)

# ################################################################################################################################
# ################################################################################################################################
