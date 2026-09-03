# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings.segments.common import add_practitioner, preserve_unmapped, preserve_value
from zato.hl7.mappings.segments.orders import ORC_Handled_Immunization

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# What a pharmacy resource consumes of its ORC - the order numbers, and the enterer, verifier
# and entering location that become the order's Provenance.
ORC_Handled_Pharmacy = ORC_Handled_Immunization | frozenset({10, 11, 13})

# A MedicationRequest also takes the transaction time as when it was authored
# and the ordering provider as its requester.
_ORC_Handled_Request = ORC_Handled_Pharmacy | frozenset({9, 12})

# ################################################################################################################################
# ################################################################################################################################

def apply_orc_to_request(orc_accessor:'SegmentAccessor', context:'ConversionContext', request:'any_') -> 'None':
    """ Fills a MedicationRequest in from its ORC - the transaction time is when the request was authored,
    the ordering provider its requester - and preserves whatever else the ORC carries that nothing consumes.
    """
    # A transaction time that is not a date/time at all is preserved as-is ..
    transaction_value = orc_accessor.value(9)
    transaction_time = context.datetime(transaction_value, 'ORC', 9)

    if transaction_time:
        request.authoredOn = transaction_time
    elif transaction_value:
        preserve_value(request, context, 'ORC', 9, transaction_value)

    # .. and the ordering provider is the requester.
    provider_repetition = orc_accessor.first(12)

    if requester := add_practitioner(provider_repetition, context):
        request.requester = requester

    preserve_unmapped(orc_accessor, _ORC_Handled_Request, request, context)

# ################################################################################################################################
# ################################################################################################################################
