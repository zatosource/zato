# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.x12.ack import AckResult, ElementNoteResult, FunctionalAcknowledgment997, ImplementationAcknowledgment999, \
     SegmentNoteResult, SetAckResult, TA1Result, X12AckError, build_997, build_999, build_ta1, parse_997, parse_999, parse_ta1
from zato.x12.base import X12GenericMessage, X12GenericSegment, X12HierarchicalLoop, X12Message, X12Segment
from zato.x12.control import ControlNumberStore, SequenceDetails, get_control_db_path
from zato.x12.envelope import X12EnvelopeError, X12FunctionalGroup, X12Interchange, parse_x12
from zato.x12.preflight import check_usage_indicator, gs1_check_digit, is_valid_gtin, is_valid_sscc, preflight_invoice, \
     preflight_purchase_order, preflight_ship_notice
from zato.x12.service import GE, GS, IEA, ISA, SE, ST, TA1
from zato.x12.syntax import RawSegment, Separators, X12SyntaxError, default_separators, parse_isa, parse_segment, \
     parse_segments, serialize_segment, split_segments
from zato.x12.validation import SetValidationResult, ValidationIssue, X12ValidationError, extract_business_key, \
     parse_x12_strict, validate_interchange, validate_snip_1, validate_snip_2, validate_snip_3, validate_snip_4, \
     validate_transaction_set

# ################################################################################################################################
# ################################################################################################################################

__all__ = [
    'AckResult',
    'ControlNumberStore',
    'ElementNoteResult',
    'FunctionalAcknowledgment997',
    'GE',
    'GS',
    'IEA',
    'ISA',
    'ImplementationAcknowledgment999',
    'RawSegment',
    'SE',
    'ST',
    'SegmentNoteResult',
    'Separators',
    'SequenceDetails',
    'SetAckResult',
    'SetValidationResult',
    'TA1',
    'TA1Result',
    'ValidationIssue',
    'X12AckError',
    'X12EnvelopeError',
    'X12FunctionalGroup',
    'X12GenericMessage',
    'X12GenericSegment',
    'X12HierarchicalLoop',
    'X12Interchange',
    'X12Message',
    'X12Segment',
    'X12SyntaxError',
    'X12ValidationError',
    'build_997',
    'build_999',
    'build_ta1',
    'check_usage_indicator',
    'default_separators',
    'extract_business_key',
    'get_control_db_path',
    'gs1_check_digit',
    'is_valid_gtin',
    'is_valid_sscc',
    'parse_997',
    'parse_999',
    'parse_isa',
    'parse_segment',
    'parse_segments',
    'parse_ta1',
    'parse_x12',
    'parse_x12_strict',
    'preflight_invoice',
    'preflight_purchase_order',
    'preflight_ship_notice',
    'serialize_segment',
    'split_segments',
    'validate_interchange',
    'validate_snip_1',
    'validate_snip_2',
    'validate_snip_3',
    'validate_snip_4',
    'validate_transaction_set',
]

# ################################################################################################################################
# ################################################################################################################################
