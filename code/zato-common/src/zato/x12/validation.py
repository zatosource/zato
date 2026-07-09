# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# stdlib
from decimal import Decimal

# Zato
from zato.edi.base import EDIElement, EDIGroupAttr, EDISegmentAttr, EDIValidationError, Usage, _composite_classes, \
     _declared_attr_descriptors
from zato.x12.base import X12GenericMessage, X12Message, _element_value
from zato.x12.syntax import RawSegment

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Any  # noqa: F401
    from zato.x12.envelope import X12Interchange
    X12Interchange = X12Interchange

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
any_             = 'Any'
strlist          = list[str]
anylist          = list['Any']
raw_segment_list = list[RawSegment]

issue_list           = list['ValidationIssue']
set_result_list      = list['SetValidationResult']
descriptor_list      = list[EDIElement]
tag_descriptors_dict = dict[str, descriptor_list]

# ################################################################################################################################
# ################################################################################################################################

# Segment-level error codes, the AK304/IK304 code list.
Segment_Unrecognized       = '1'
Segment_Mandatory_Missing  = '3'
Segment_Data_Element_Error = '8'

# Element-level error codes, the AK403/IK403 code list.
Element_Mandatory_Missing = '1'
Element_Too_Short         = '4'
Element_Too_Long          = '5'

# AK502/IK502 reports that one or more segments were in error.
Set_Error_Segments_In_Error = '5'

# ################################################################################################################################

# Where the well-known business reference of each transaction set lives - the segment tag
# and the 1-based element position, e.g. the 850 purchase order number is BEG03.
business_key_locations = {
    '810': ('BIG', 2),
    '835': ('TRN', 2),
    '837': ('CLM', 1),
    '850': ('BEG', 3),
    '856': ('BSN', 2),
}

# The 835 claim status code meaning the claim was denied - a denied claim pays nothing.
Claim_Status_Denied = '4'

# The HL level code of the 270 subscriber loop and the NM1 entity code of the insured subscriber.
Subscriber_Level_Code  = '22'
Subscriber_Entity_Code = 'IL'

# The TDS total is an N2 value - two implied decimal places.
TDS_Implied_Decimals = Decimal(100)

# ################################################################################################################################
# ################################################################################################################################

class X12ValidationError(EDIValidationError):
    """ Raised by parse_x12 in strict mode when at least one transaction set has
    implementation guide syntax issues - the per-set results are on .results.
    """

    def __init__(self, message:'str', results:'set_result_list') -> 'None':
        super().__init__(message)
        self.results = results

# ################################################################################################################################
# ################################################################################################################################

class ValidationIssue:
    """ One validation finding of a transaction set - carries everything an AK3/AK4
    or IK3/IK4 pair needs, plus a human-readable reason.
    """

    def __init__(
        self,
        segment_tag:'str',
        segment_position:'int',
        segment_error_code:'str',
        element_position:'int' = 0,
        component_position:'int' = 0,
        element_error_code:'str' = '',
        value:'str' = '',
        reason:'str' = '',
        ) -> 'None':
        self.segment_tag = segment_tag
        self.segment_position = segment_position
        self.segment_error_code = segment_error_code
        self.element_position = element_position
        self.component_position = component_position
        self.element_error_code = element_error_code
        self.value = value
        self.reason = reason

# ################################################################################################################################

    def __repr__(self) -> 'str':
        out = f'<ValidationIssue {self.segment_tag}@{self.segment_position} {self.reason}>'
        return out

# ################################################################################################################################
# ################################################################################################################################

class SetValidationResult:
    """ The validation outcome of one transaction set within an interchange.
    """

    def __init__(self) -> 'None':

        # Where the set sits - the 0-based group index and the 0-based set index within its group
        self.group_index:'int' = 0
        self.set_index:'int' = 0

        # The ST01 identifier and ST02 control number of the set
        self.identifier_code:'str' = ''
        self.control_number:'str' = ''

        # The typed message the issues apply to
        self.message:'any_' = None

        # Everything found wrong with the set
        self.issues:'issue_list' = []

# ################################################################################################################################

    @property
    def is_accepted(self) -> 'bool':
        out = not self.issues
        return out

# ################################################################################################################################
# ################################################################################################################################

class _MessageSchema:
    """ What one transaction set class declares - collected once per class and cached.
    """

    def __init__(self) -> 'None':

        # Every tag the class or its groups declare
        self.known_tags:'strlist' = []

        # The tags that must appear at least once - message-level segments and group leaders
        self.required_tags:'strlist' = []

        # The element descriptors to validate each tag against, sorted by position
        self.descriptors_by_tag:'tag_descriptors_dict' = {}

# ################################################################################################################################

_schema_cache:'dict[type, _MessageSchema]' = {}

# ################################################################################################################################

def _element_descriptors_of(segment_class:'type') -> 'descriptor_list':
    """ Returns the element descriptors of a segment class, sorted by position.
    """
    descriptors:'descriptor_list' = []

    for name in dir(segment_class):
        attribute = getattr(segment_class, name)
        if isinstance(attribute, EDIElement):
            descriptors.append(attribute)

    descriptors.sort(key=lambda descriptor: descriptor.position)

    out = descriptors
    return out

# ################################################################################################################################

def _collect_schema_from(source_class:'type', schema:'_MessageSchema', is_top_level:'bool') -> 'None':
    """ Walks the declared attributes of a message or group class, recording every tag,
    its element descriptors and, at the top level, which tags are mandatory.
    """
    for descriptor in _declared_attr_descriptors(source_class):

        # A segment reference contributes its tag and element layout ..
        if isinstance(descriptor, EDISegmentAttr):
            tag = descriptor.tag

            if tag not in schema.known_tags:
                schema.known_tags.append(tag)
                schema.descriptors_by_tag[tag] = _element_descriptors_of(descriptor.segment_class)

            if is_top_level:
                if not descriptor.optional:
                    schema.required_tags.append(tag)

        # .. and a group reference contributes its leader plus everything inside it.
        elif isinstance(descriptor, EDIGroupAttr):
            group_class = descriptor.group_class
            leader_tag = group_class._leader_tag

            if is_top_level:
                if not descriptor.optional:
                    schema.required_tags.append(leader_tag)

            _collect_schema_from(group_class, schema, False)

# ################################################################################################################################

def _get_schema(message_class:'type') -> '_MessageSchema':
    """ Returns the cached schema of a transaction set class, building it on first use.
    """
    if schema := _schema_cache.get(message_class):
        out = schema
        return out

    schema = _MessageSchema()
    _collect_schema_from(message_class, schema, True)

    _schema_cache[message_class] = schema

    out = schema
    return out

# ################################################################################################################################
# ################################################################################################################################

def _parse_length_bounds(format:'str') -> 'tuple[int, int] | None':
    """ Reads the min/max lengths out of an X12 format string like `AN 1/22` or `1/1`.
    Formats without a length pair yield None and no length check applies.
    """
    if '/' not in format:
        return None

    length_part = format.split(' ')[-1]
    min_text, max_text = length_part.split('/')

    out = (int(min_text), int(max_text))
    return out

# ################################################################################################################################

def _check_length(
    issues:'issue_list',
    descriptor_format:'str',
    value:'str',
    tag:'str',
    segment_position:'int',
    element_position:'int',
    component_position:'int',
    ) -> 'None':
    """ Appends a too-short or too-long issue when the value violates its format's length bounds.
    """
    bounds = _parse_length_bounds(descriptor_format)
    if bounds is None:
        return

    min_length, max_length = bounds
    value_length = len(value)

    if value_length < min_length:
        issue = ValidationIssue(tag, segment_position, Segment_Data_Element_Error, element_position, component_position,
            Element_Too_Short, value,
            f'{tag}{element_position:02d} `{value}` is shorter than {min_length} character(s)')
        issues.append(issue)

    elif value_length > max_length:
        issue = ValidationIssue(tag, segment_position, Segment_Data_Element_Error, element_position, component_position,
            Element_Too_Long, value,
            f'{tag}{element_position:02d} `{value}` is longer than {max_length} character(s)')
        issues.append(issue)

# ################################################################################################################################

def _validate_segment_elements(
    issues:'issue_list',
    raw_segment:'RawSegment',
    segment_position:'int',
    descriptors:'descriptor_list',
    ) -> 'None':
    """ Checks the elements of one raw segment against its class's descriptors -
    mandatory presence and length bounds, for scalars and composite components alike.
    """
    tag = raw_segment.tag
    elements = raw_segment.elements
    element_count = len(elements)

    for descriptor in descriptors:
        element_position = descriptor.position
        index = element_position - 1

        # Establish whether the element is present at all ..
        if index < element_count:
            components = elements[index]
        else:
            components = []

        has_value = False
        for component_value in components:
            if component_value:
                has_value = True
                break

        # .. an absent element is only an issue when it is mandatory ..
        if not has_value:
            if descriptor.usage is Usage.REQUIRED:
                issue = ValidationIssue(tag, segment_position, Segment_Data_Element_Error, element_position, 0,
                    Element_Mandatory_Missing, '',
                    f'Mandatory element {tag}{element_position:02d} is missing')
                issues.append(issue)
            continue

        # .. a composite element checks each of its components ..
        if descriptor.composite:
            composite_class = _composite_classes[descriptor.composite]
            component_descriptors = _element_descriptors_of_composite(composite_class)
            component_count = len(components)

            for component_descriptor in component_descriptors:
                component_position = component_descriptor.position
                component_index = component_position - 1

                if component_index < component_count:
                    component_value = components[component_index]
                else:
                    component_value = ''

                if not component_value:
                    if component_descriptor.usage is Usage.REQUIRED:
                        issue = ValidationIssue(tag, segment_position, Segment_Data_Element_Error,
                            element_position, component_position, Element_Mandatory_Missing, '',
                            f'Mandatory component {component_position} of {tag}{element_position:02d} is missing')
                        issues.append(issue)
                    continue

                _check_length(issues, component_descriptor.format, component_value, tag, segment_position,
                    element_position, component_position)

        # .. and a simple element checks its scalar value.
        else:
            value = components[0]
            _check_length(issues, descriptor.format, value, tag, segment_position, element_position, 0)

# ################################################################################################################################

def _element_descriptors_of_composite(composite_class:'type') -> 'anylist':
    """ Returns the component descriptors of a composite class, sorted by position.
    """
    from zato.edi.base import EDIComponent

    descriptors:'anylist' = []

    for name in dir(composite_class):
        attribute = getattr(composite_class, name)
        if isinstance(attribute, EDIComponent):
            descriptors.append(attribute)

    descriptors.sort(key=lambda descriptor: descriptor.position)

    out = descriptors
    return out

# ################################################################################################################################
# ################################################################################################################################

def validate_transaction_set(message:'X12Message') -> 'issue_list':
    """ Checks one typed transaction set against its dictionary - unknown segments,
    mandatory segments and elements that are absent, and length violations - collecting
    every issue instead of stopping at the first one. Generic messages have no dictionary
    to check against and always come back clean.
    """

    # Our response to produce
    out:'issue_list' = []

    # A set without a dictionary cannot be validated in strict mode
    if isinstance(message, X12GenericMessage):
        return out

    schema = _get_schema(type(message))
    raw_segments = message._raw_segments

    # A message built from scratch has no wire data to check
    if raw_segments is None:
        return out

    seen_tags:'strlist' = []

    # The transaction set header is count position 1
    for segment_index, raw_segment in enumerate(raw_segments):
        segment_position = segment_index + 1
        tag = raw_segment.tag

        if tag not in seen_tags:
            seen_tags.append(tag)

        # A tag the dictionary does not declare is an unrecognized segment ..
        if tag not in schema.known_tags:
            issue = ValidationIssue(tag, segment_position, Segment_Unrecognized, 0, 0, '', '',
                f'Segment `{tag}` is not defined for transaction set {message._message_type}')
            out.append(issue)
            continue

        # .. and a declared one has its elements checked.
        descriptors = schema.descriptors_by_tag[tag]
        _validate_segment_elements(out, raw_segment, segment_position, descriptors)

    # Mandatory segments and group leaders must appear at least once.
    for required_tag in schema.required_tags:
        if required_tag not in seen_tags:
            issue = ValidationIssue(required_tag, 0, Segment_Mandatory_Missing, 0, 0, '', '',
                f'Mandatory segment `{required_tag}` is missing')
            out.append(issue)

    return out

# ################################################################################################################################

def validate_interchange(interchange:'X12Interchange') -> 'set_result_list':
    """ Validates every transaction set of a parsed interchange, returning one result
    per set - this is what strict parsing raises on and what 997/999 building consumes.
    """

    # Our response to produce
    out:'set_result_list' = []

    for group_index, group in enumerate(interchange.groups):
        for set_index, transaction_set in enumerate(group.transaction_sets):

            result = SetValidationResult()
            result.group_index = group_index
            result.set_index = set_index
            result.message = transaction_set

            raw_segments = transaction_set._raw_segments
            st_segment = raw_segments[0]
            result.identifier_code = _element_value(st_segment, 1)
            result.control_number = _element_value(st_segment, 2)

            result.issues = validate_transaction_set(transaction_set)

            out.append(result)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _set_type(message:'X12Message') -> 'str':
    """ Returns the transaction set identifier of a message - the declared type
    of a typed message or the ST01 of a generic one.
    """
    if message._message_type:
        out = message._message_type
        return out

    raw_segments = message._raw_segments
    for raw_segment in raw_segments:
        if raw_segment.tag == 'ST':
            out = _element_value(raw_segment, 1)
            return out

    return ''

# ################################################################################################################################

def _sum_element(raw_segments:'raw_segment_list', tag:'str', position:'int') -> 'Decimal':
    """ Sums the decimal values of one element across every segment with the given tag.
    """
    out = Decimal(0)

    for raw_segment in raw_segments:
        if raw_segment.tag == tag:
            value = _element_value(raw_segment, position)
            if value:
                out += Decimal(value)

    return out

# ################################################################################################################################

def _count_segments(raw_segments:'raw_segment_list', tag:'str') -> 'int':
    """ Counts the segments with the given tag.
    """
    out = 0

    for raw_segment in raw_segments:
        if raw_segment.tag == tag:
            out += 1

    return out

# ################################################################################################################################

def _find_first(raw_segments:'raw_segment_list', tag:'str') -> 'RawSegment | None':
    """ Returns the first segment with the given tag, or None.
    """
    for raw_segment in raw_segments:
        if raw_segment.tag == tag:
            return raw_segment

    return None

# ################################################################################################################################

def _check_ctt_count(out:'strlist', raw_segments:'raw_segment_list', line_tag:'str') -> 'None':
    """ Compares CTT01 with the actual count of line leader segments.
    """
    ctt = _find_first(raw_segments, 'CTT')
    if ctt is None:
        return

    declared_count = int(_element_value(ctt, 1))
    actual_count = _count_segments(raw_segments, line_tag)

    if declared_count != actual_count:
        out.append(f'CTT01 `{declared_count}` does not match the {line_tag} count {actual_count}')

# ################################################################################################################################

def _balance_810(out:'strlist', raw_segments:'raw_segment_list') -> 'None':
    """ TDS01 must equal the sum of the IT1 line amounts (quantity times unit price)
    and CTT01 must match the IT1 line count.
    """
    _check_ctt_count(out, raw_segments, 'IT1')

    tds = _find_first(raw_segments, 'TDS')
    if tds is None:
        return

    # TDS01 has two implied decimal places
    declared_total = Decimal(_element_value(tds, 1)) / TDS_Implied_Decimals

    line_total = Decimal(0)
    for raw_segment in raw_segments:
        if raw_segment.tag == 'IT1':
            quantity = Decimal(_element_value(raw_segment, 2))
            unit_price = Decimal(_element_value(raw_segment, 4))
            line_total += quantity * unit_price

    if declared_total != line_total:
        out.append(f'TDS01 `{declared_total}` does not match the sum of line amounts {line_total}')

# ################################################################################################################################

def _balance_850(out:'strlist', raw_segments:'raw_segment_list') -> 'None':
    """ CTT01 must match the PO1 line count and CTT02, when present, must match
    the hash total of the PO102 quantities.
    """
    _check_ctt_count(out, raw_segments, 'PO1')

    ctt = _find_first(raw_segments, 'CTT')
    if ctt is None:
        return

    declared_hash = _element_value(ctt, 2)
    if not declared_hash:
        return

    quantity_total = _sum_element(raw_segments, 'PO1', 2)

    if Decimal(declared_hash) != quantity_total:
        out.append(f'CTT02 `{declared_hash}` does not match the quantity hash total {quantity_total}')

# ################################################################################################################################

def _balance_856(out:'strlist', raw_segments:'raw_segment_list') -> 'None':
    """ CTT01 of an 856 counts the HL segments.
    """
    _check_ctt_count(out, raw_segments, 'HL')

# ################################################################################################################################

def _balance_835(out:'strlist', raw_segments:'raw_segment_list') -> 'None':
    """ BPR02 must equal the sum of the CLP04 claim payments minus the PLB provider-level
    adjustments - a positive PLB amount is a deduction from the payment.
    """
    bpr = _find_first(raw_segments, 'BPR')
    if bpr is None:
        return

    declared_payment = Decimal(_element_value(bpr, 2))

    claim_total = _sum_element(raw_segments, 'CLP', 4)
    adjustment_total = _sum_element(raw_segments, 'PLB', 4)

    computed_payment = claim_total - adjustment_total

    if declared_payment != computed_payment:
        out.append(f'BPR02 `{declared_payment}` does not match CLP04 minus PLB adjustments, which is {computed_payment}')

# ################################################################################################################################

# Which balancing function applies to which transaction set.
_balance_by_set = {
    '810': _balance_810,
    '835': _balance_835,
    '850': _balance_850,
    '856': _balance_856,
}

# ################################################################################################################################
# ################################################################################################################################

def _situational_837(out:'strlist', raw_segments:'raw_segment_list') -> 'None':
    """ TR3 situational rules of an 837 - every claim must carry at least one HI diagnosis
    and at least one LX service line.
    """
    claim_id = ''
    has_diagnosis = False
    has_service_line = False
    in_claim = False

    def _flush() -> 'None':
        if in_claim:
            if not has_diagnosis:
                out.append(f'Claim `{claim_id}` has no HI diagnosis codes')
            if not has_service_line:
                out.append(f'Claim `{claim_id}` has no LX service lines')

    for raw_segment in raw_segments:
        tag = raw_segment.tag

        # A CLM starts a new claim - conclude the checks of the previous one
        if tag == 'CLM':
            _flush()
            claim_id = _element_value(raw_segment, 1)
            has_diagnosis = False
            has_service_line = False
            in_claim = True
            continue

        if tag == 'HI':
            has_diagnosis = True
        elif tag == 'LX':
            has_service_line = True
        elif tag == 'SE':
            break

    _flush()

# ################################################################################################################################

def _situational_835(out:'strlist', raw_segments:'raw_segment_list') -> 'None':
    """ TR3 situational rules of an 835 - a denied claim (CLP02 = 4) pays nothing.
    """
    for raw_segment in raw_segments:
        if raw_segment.tag == 'CLP':
            status_code = _element_value(raw_segment, 2)
            if status_code == Claim_Status_Denied:
                payment = Decimal(_element_value(raw_segment, 4))
                if payment != 0:
                    claim_id = _element_value(raw_segment, 1)
                    out.append(f'Denied claim `{claim_id}` has a non-zero payment amount {payment}')

# ################################################################################################################################

def _situational_270(out:'strlist', raw_segments:'raw_segment_list') -> 'None':
    """ TR3 situational rules of a 270 - the subscriber loop (HL level 22) must carry
    an NM1 identifying the insured subscriber (entity code IL).
    """
    in_subscriber_loop = False
    has_subscriber_name = False
    has_subscriber_loop = False

    for raw_segment in raw_segments:
        tag = raw_segment.tag

        if tag == 'HL':
            level_code = _element_value(raw_segment, 3)
            in_subscriber_loop = level_code == Subscriber_Level_Code
            if in_subscriber_loop:
                has_subscriber_loop = True
            continue

        if in_subscriber_loop:
            if tag == 'NM1':
                entity_code = _element_value(raw_segment, 1)
                if entity_code == Subscriber_Entity_Code:
                    has_subscriber_name = True

    if not has_subscriber_loop:
        out.append('No subscriber loop (HL level 22) found')
    elif not has_subscriber_name:
        out.append('Subscriber loop has no NM1 with entity code IL')

# ################################################################################################################################

# Which situational rule list applies to which transaction set.
_situational_by_set = {
    '270': _situational_270,
    '835': _situational_835,
    '837': _situational_837,
}

# ################################################################################################################################
# ################################################################################################################################

def validate_snip_1(raw:'str') -> 'strlist':
    """ SNIP type 1 - EDI syntax integrity. The envelope layer performs it during parsing:
    separators, control number echoes and segment counts. Returns the errors found,
    an empty list meaning the interchange is syntactically sound.
    """
    from zato.x12.envelope import X12EnvelopeError, parse_x12
    from zato.x12.syntax import X12SyntaxError

    # Our response to produce
    out:'strlist' = []

    try:
        _ = parse_x12(raw)
    except (X12EnvelopeError, X12SyntaxError) as e:
        out.append(e.args[0])

    return out

# ################################################################################################################################

def validate_snip_2(message:'X12Message') -> 'issue_list':
    """ SNIP type 2 - implementation guide syntax. The strict mode over the dictionaries:
    unknown segments, usage violations and length violations, all collected per set.
    """
    out = validate_transaction_set(message)
    return out

# ################################################################################################################################

def validate_snip_3(message:'X12Message') -> 'strlist':
    """ SNIP type 3 - balancing. TDS01 against the sum of the line amounts, CTT counts
    and hash totals, and 835 claim payments reconciling to BPR02.
    """

    # Our response to produce
    out:'strlist' = []

    set_type = _set_type(message)

    if balance := _balance_by_set.get(set_type):
        balance(out, message._raw_segments)

    return out

# ################################################################################################################################

def validate_snip_4(message:'X12Message') -> 'strlist':
    """ SNIP type 4 - inter-segment situational rules from the implementation guides,
    one rule list per HIPAA transaction set.
    """

    # Our response to produce
    out:'strlist' = []

    set_type = _set_type(message)

    if situational := _situational_by_set.get(set_type):
        situational(out, message._raw_segments)

    return out

# ################################################################################################################################
# ################################################################################################################################

def extract_business_key(message:'X12Message') -> 'str':
    """ Lifts the well-known business reference out of a transaction set - the BEG03
    purchase order number of an 850, the BIG02 invoice number of an 810, the BSN02
    shipment id of an 856, the CLM01 claim id of an 837 and the TRN02 trace number
    of an 835. This is what makes the audit log searchable by the reference
    the customer is on the phone about.
    """
    set_type = _set_type(message)

    location = business_key_locations.get(set_type)
    if location is None:
        return ''

    tag, position = location

    for raw_segment in message._raw_segments:
        if raw_segment.tag == tag:
            out = _element_value(raw_segment, position)
            return out

    return ''

# ################################################################################################################################

def business_key_context_name(set_type:'str') -> 'str':
    """ The CTX-style name of the business reference location of a transaction set,
    e.g. CLM01 for an 837 - what a 999 CTX segment carries next to the reference itself.
    """
    location = business_key_locations.get(set_type)
    if location is None:
        return ''

    tag, position = location

    out = f'{tag}{position:02d}'
    return out

# ################################################################################################################################
# ################################################################################################################################
