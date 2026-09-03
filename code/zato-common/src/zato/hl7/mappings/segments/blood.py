# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings.concepts import cwe_to_codeable_concept
from zato.hl7.mappings.segments.common import append_to_list_field, preserve_unmapped

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.fhir import ServiceRequest
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    ServiceRequest = ServiceRequest

# ################################################################################################################################
# ################################################################################################################################

# Which field positions the mapper consumes - anything else that carries data is preserved as an extension.
_BPO_Handled = frozenset({1, 2, 3, 4, 7, 13})

# The category a blood product order's ServiceRequest carries
Blood_Product_Category = {'text': 'Blood product'}

# ################################################################################################################################
# ################################################################################################################################

def apply_bpo(accessor:'SegmentAccessor', context:'ConversionContext', service_request:'ServiceRequest') -> 'None':
    """ Applies BPO - a blood product order - to the ServiceRequest its order group produced.
    """
    config = context.config

    service_request.category = [Blood_Product_Category]

    # The universal service identifier is the requested blood product ..
    service_repetition = accessor.first(2)

    if code := cwe_to_codeable_concept(service_repetition, config):
        service_request.code = code

    # .. the processing requirements detail how it is to be prepared ..
    for repetition in accessor.repetitions(3):
        if requirement := cwe_to_codeable_concept(repetition, config):
            append_to_list_field(service_request, 'orderDetail', requirement)

    # .. the quantity says how many units are ordered ..
    quantity = accessor.value(4)
    if quantity:
        if quantity.isdigit():
            service_request.quantityQuantity = {'value': int(quantity)}

    # .. the intended use time is when the product is needed ..
    intended_value = accessor.value(7)
    intended_time = context.datetime(intended_value, 'BPO', 7)

    if intended_time:
        service_request.occurrenceDateTime = intended_time

    # .. and each indication for use completes the picture.
    for repetition in accessor.repetitions(13):
        if indication := cwe_to_codeable_concept(repetition, config):
            append_to_list_field(service_request, 'reasonCode', indication)

    # A non-numeric quantity is preserved along with everything else unconsumed.
    handled = set(_BPO_Handled)

    if quantity:
        if not quantity.isdigit():
            handled.discard(4)

    handled = frozenset(handled)
    preserve_unmapped(accessor, handled, service_request, context)

# ################################################################################################################################
# ################################################################################################################################
