# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Functional acknowledgments - the TA1 interchange acknowledgment, the 997 functional
# acknowledgment and the 999 implementation acknowledgment (005010X231A1, mandated
# by HIPAA), each with a build and parse pair. A rejected inbound transaction never
# produces a clean acknowledgment - the AK5/IK5 codes always reflect the validation
# outcome of each set.

from __future__ import annotations

# Zato
from zato.common.typing_ import optional
from zato.x12.base import EDIComponent, EDIComposite, EDIElement, EDIGroup, EDIGroupAttr, EDIRepeatableList, EDISegmentAttr, \
     Usage, X12Message, X12Segment, _element_value
from zato.x12.envelope import X12Interchange
from zato.x12.service import SE, ST, TA1
from zato.x12.validation import Set_Error_Segments_In_Error, SetValidationResult, business_key_context_name, \
     extract_business_key, validate_interchange

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strlist
    any_ = any_
    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
set_result_list      = list[SetValidationResult]
set_result_list_none = optional[set_result_list]

issue_group      = tuple[int, str, 'anylist']
issue_group_list = list[issue_group]

element_note_result_list = list['ElementNoteResult']
segment_note_result_list = list['SegmentNoteResult']
set_ack_result_list      = list['SetAckResult']

# ################################################################################################################################
# ################################################################################################################################

# The acknowledgment codes of AK5/IK5 (per set) and AK9 (per group).
Ack_Accepted             = 'A'
Ack_Accepted_With_Errors = 'E'
Ack_Partial              = 'P'
Ack_Rejected             = 'R'

# The TA1 note code meaning no error was found.
TA1_Note_No_Error = '000'

# The implementation convention reference of the HIPAA 999.
Version_999 = '005010X231A1'

# ################################################################################################################################
# ################################################################################################################################

class X12AckError(Exception):
    """ Raised when an acknowledgment cannot be built or parsed, e.g. the interchange
    carries no TA1 or no 997.
    """

# ################################################################################################################################
# ################################################################################################################################

class PositionInSegment(EDIComposite):
    """ C030 - where in a segment an element error sits, the element position
    with an optional component and repetition position.
    """
    element_position   = EDIComponent[str](position=1, usage=Usage.REQUIRED, format='N0 1/2')
    component_position = EDIComponent[str](position=2, usage=Usage.OPTIONAL, format='N0 1/2')
    repetition         = EDIComponent[str](position=3, usage=Usage.OPTIONAL, format='N0 1/4')

# ################################################################################################################################

class ContextIdentification(EDIComposite):
    """ C998 - the business context of a 999 CTX segment, a name with its reference,
    e.g. CLM01 with the claim id the error belongs to.
    """
    name      = EDIComponent[str](position=1, usage=Usage.REQUIRED, format='AN 1/35')
    reference = EDIComponent[str](position=2, usage=Usage.OPTIONAL, format='AN 1/35')

# ################################################################################################################################
# ################################################################################################################################

class AK1(X12Segment):
    """ Functional group response header - which group is being acknowledged.
    """
    _segment_tag = 'AK1'

    functional_id_code = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/2')
    control_number     = EDIElement[str](position=2, usage=Usage.REQUIRED, format='N0 1/9')
    version            = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='AN 1/12')

# ################################################################################################################################

class AK2(X12Segment):
    """ Transaction set response header - which set is being acknowledged.
    """
    _segment_tag = 'AK2'

    identifier_code          = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 3/3')
    control_number           = EDIElement[str](position=2, usage=Usage.REQUIRED, format='AN 4/9')
    implementation_reference = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='AN 1/35')

# ################################################################################################################################

class AK3(X12Segment):
    """ Data segment note of a 997 - which segment was in error and why.
    """
    _segment_tag = 'AK3'

    segment_id = EDIElement[str](position=1, usage=Usage.REQUIRED, format='AN 2/3')
    position   = EDIElement[str](position=2, usage=Usage.REQUIRED, format='N0 1/10')
    loop_id    = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='AN 1/6')
    error_code = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='ID 1/3')

# ################################################################################################################################

class AK4(X12Segment):
    """ Data element note of a 997 - which element was in error, why and what it carried.
    """
    _segment_tag = 'AK4'

    position          = EDIElement[PositionInSegment](position=1, usage=Usage.REQUIRED, composite='PositionInSegment')
    element_reference = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='N0 1/4')
    error_code        = EDIElement[str](position=3, usage=Usage.REQUIRED, format='ID 1/3')
    bad_value         = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='AN 1/99')

# ################################################################################################################################

class AK5(X12Segment):
    """ Transaction set response trailer of a 997 - the per-set accepted/rejected code.
    """
    _segment_tag = 'AK5'

    ack_code     = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 1/1')
    error_code_1 = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='ID 1/3')
    error_code_2 = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='ID 1/3')
    error_code_3 = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='ID 1/3')
    error_code_4 = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='ID 1/3')
    error_code_5 = EDIElement[str](position=6, usage=Usage.OPTIONAL, format='ID 1/3')

# ################################################################################################################################

class AK9(X12Segment):
    """ Functional group response trailer - the group-level code and the set counts.
    """
    _segment_tag = 'AK9'

    ack_code       = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 1/1')
    included_count = EDIElement[str](position=2, usage=Usage.REQUIRED, format='N0 1/6')
    received_count = EDIElement[str](position=3, usage=Usage.REQUIRED, format='N0 1/6')
    accepted_count = EDIElement[str](position=4, usage=Usage.REQUIRED, format='N0 1/6')
    error_code_1   = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='ID 1/3')

# ################################################################################################################################

class IK3(X12Segment):
    """ Error identification of a 999 - the implementation counterpart of AK3.
    """
    _segment_tag = 'IK3'

    segment_id = EDIElement[str](position=1, usage=Usage.REQUIRED, format='AN 2/3')
    position   = EDIElement[str](position=2, usage=Usage.REQUIRED, format='N0 1/10')
    loop_id    = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='AN 1/6')
    error_code = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='ID 1/3')

# ################################################################################################################################

class CTX(X12Segment):
    """ Context of a 999 - the business-unit reference the CMS guides require,
    e.g. the claim id the rejected segment belongs to.
    """
    _segment_tag = 'CTX'

    context          = EDIElement[ContextIdentification](position=1, usage=Usage.REQUIRED, composite='ContextIdentification')
    segment_id       = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='AN 2/3')
    segment_position = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='N0 1/10')
    loop_id          = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='AN 1/6')

# ################################################################################################################################

class IK4(X12Segment):
    """ Implementation data element note of a 999 - the counterpart of AK4.
    """
    _segment_tag = 'IK4'

    position          = EDIElement[PositionInSegment](position=1, usage=Usage.REQUIRED, composite='PositionInSegment')
    element_reference = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='N0 1/4')
    error_code        = EDIElement[str](position=3, usage=Usage.REQUIRED, format='ID 1/3')
    bad_value         = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='AN 1/99')

# ################################################################################################################################

class IK5(X12Segment):
    """ Implementation transaction set response trailer of a 999 - the counterpart of AK5.
    """
    _segment_tag = 'IK5'

    ack_code     = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 1/1')
    error_code_1 = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='ID 1/3')
    error_code_2 = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='ID 1/3')
    error_code_3 = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='ID 1/3')
    error_code_4 = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='ID 1/3')
    error_code_5 = EDIElement[str](position=6, usage=Usage.OPTIONAL, format='ID 1/3')

# ################################################################################################################################
# ################################################################################################################################

class SegmentNote997(EDIGroup):
    """ One AK3 loop of a 997 - a segment error with its element-level details.
    """
    _leader_tag = 'AK3'

    ak3           = EDISegmentAttr[AK3](AK3)
    element_notes = EDISegmentAttr[EDIRepeatableList](AK4, optional=True, repeatable=True)

# ################################################################################################################################

class SetResponse997(EDIGroup):
    """ One AK2 loop of a 997 - the response to one transaction set.
    """
    _leader_tag = 'AK2'

    ak2           = EDISegmentAttr[AK2](AK2)
    segment_notes = EDIGroupAttr[EDIRepeatableList](SegmentNote997, optional=True)
    ak5           = EDISegmentAttr[AK5](AK5)

# ################################################################################################################################

class FunctionalAcknowledgment997(X12Message):
    """ 997 functional acknowledgment - the answer to one functional group,
    reporting each of its sets as accepted or rejected.
    """
    _message_type = '997'

    st            = EDISegmentAttr[ST](ST)
    ak1           = EDISegmentAttr[AK1](AK1)
    set_responses = EDIGroupAttr[EDIRepeatableList](SetResponse997, optional=True)
    ak9           = EDISegmentAttr[AK9](AK9)
    se            = EDISegmentAttr[SE](SE)

# ################################################################################################################################
# ################################################################################################################################

class SegmentNote999(EDIGroup):
    """ One IK3 loop of a 999 - a segment error with its business context
    and element-level details.
    """
    _leader_tag = 'IK3'

    ik3           = EDISegmentAttr[IK3](IK3)
    contexts      = EDISegmentAttr[EDIRepeatableList](CTX, optional=True, repeatable=True)
    element_notes = EDISegmentAttr[EDIRepeatableList](IK4, optional=True, repeatable=True)

# ################################################################################################################################

class SetResponse999(EDIGroup):
    """ One AK2 loop of a 999 - the implementation response to one transaction set.
    """
    _leader_tag = 'AK2'

    ak2           = EDISegmentAttr[AK2](AK2)
    segment_notes = EDIGroupAttr[EDIRepeatableList](SegmentNote999, optional=True)
    ik5           = EDISegmentAttr[IK5](IK5)

# ################################################################################################################################

class ImplementationAcknowledgment999(X12Message):
    """ 999 implementation acknowledgment, 005010X231A1 - the HIPAA-mandated answer
    to one functional group, with IK3/CTX/IK4/IK5 detail per set.
    """
    _message_type = '999'
    _message_version = Version_999

    st            = EDISegmentAttr[ST](ST)
    ak1           = EDISegmentAttr[AK1](AK1)
    set_responses = EDIGroupAttr[EDIRepeatableList](SetResponse999, optional=True)
    ak9           = EDISegmentAttr[AK9](AK9)
    se            = EDISegmentAttr[SE](SE)

# ################################################################################################################################
# ################################################################################################################################

class TA1Result:
    """ A parsed TA1 interchange acknowledgment.
    """

    def __init__(self) -> 'None':

        # The interchange control number being acknowledged, as it appeared on the wire
        self.control_number:'str' = ''

        # The date and time echoed from the acknowledged ISA
        self.date:'str' = ''
        self.time:'str' = ''

        # The A/E/R acknowledgment code and the three-digit note code
        self.ack_code:'str' = ''
        self.note_code:'str' = ''

# ################################################################################################################################

    @property
    def is_accepted(self) -> 'bool':
        out = self.ack_code == Ack_Accepted
        return out

# ################################################################################################################################
# ################################################################################################################################

class ElementNoteResult:
    """ One parsed AK4/IK4 - where the element error sits and what the data was.
    """

    def __init__(self) -> 'None':
        self.element_position:'int' = 0
        self.component_position:'int' = 0
        self.error_code:'str' = ''
        self.bad_value:'str' = ''

# ################################################################################################################################

class SegmentNoteResult:
    """ One parsed AK3/IK3 with its element notes.
    """

    def __init__(self) -> 'None':
        self.segment_id:'str' = ''
        self.position:'int' = 0
        self.error_code:'str' = ''
        self.element_notes:'element_note_result_list' = []

# ################################################################################################################################

class SetAckResult:
    """ The parsed response to one transaction set - AK2 through AK5 or IK5.
    """

    def __init__(self) -> 'None':
        self.identifier_code:'str' = ''
        self.control_number:'str' = ''
        self.ack_code:'str' = ''
        self.error_codes:'strlist' = []
        self.segment_notes:'segment_note_result_list' = []

# ################################################################################################################################

    @property
    def is_accepted(self) -> 'bool':
        out = self.ack_code == Ack_Accepted
        return out

# ################################################################################################################################

class AckResult:
    """ A parsed 997 or 999 - the group-level outcome with the per-set results.
    """

    def __init__(self) -> 'None':
        self.functional_id_code:'str' = ''
        self.group_control_number:'str' = ''
        self.ack_code:'str' = ''
        self.included_count:'int' = 0
        self.received_count:'int' = 0
        self.accepted_count:'int' = 0
        self.set_results:'set_ack_result_list' = []

# ################################################################################################################################

    @property
    def is_accepted(self) -> 'bool':
        out = self.ack_code == Ack_Accepted
        return out

# ################################################################################################################################
# ################################################################################################################################

def _swap_envelope(source:'X12Interchange', target:'X12Interchange') -> 'None':
    """ Addresses the target interchange back at the sender of the source one,
    keeping the syntax characters and the test-vs-production indicator of the original.
    """
    target.separators = source.separators

    source_isa = source.isa
    target_isa = target.isa

    target_isa.sender_qualifier = source_isa.receiver_qualifier
    target_isa.sender_id = source_isa.receiver_id
    target_isa.receiver_qualifier = source_isa.sender_qualifier
    target_isa.receiver_id = source_isa.sender_id
    target_isa.usage_indicator = source_isa.usage_indicator

# ################################################################################################################################

def build_ta1(interchange:'X12Interchange', ack_code:'str'=Ack_Accepted, note_code:'str'=TA1_Note_No_Error) -> 'X12Interchange':
    """ Builds a TA1 interchange acknowledgment for a parsed interchange - a single
    segment without GS/GE wrapping, echoing the ISA13 control number with the date,
    time and the A/E/R code.
    """

    # Our response to produce
    out = X12Interchange()

    _swap_envelope(interchange, out)

    source_isa = interchange.isa

    ta1 = TA1()
    ta1.control_number = source_isa.control_number
    ta1.date = source_isa.date
    ta1.time = source_isa.time
    ta1.ack_code = ack_code
    ta1.note_code = note_code

    out.ta1_list.append(ta1)

    return out

# ################################################################################################################################

def parse_ta1(interchange:'X12Interchange') -> 'TA1Result':
    """ Parses the TA1 of an interchange back into a result object.
    """
    if not interchange.ta1_list:
        raise X12AckError('No TA1 found in interchange')

    ta1 = interchange.ta1_list[0]

    # Our response to produce
    out = TA1Result()

    out.control_number = ta1.control_number
    out.date = ta1.date
    out.time = ta1.time
    out.ack_code = ta1.ack_code
    out.note_code = ta1.note_code

    return out

# ################################################################################################################################
# ################################################################################################################################

def _group_issues_by_segment(issues:'anylist') -> 'issue_group_list':
    """ Groups validation issues by the segment they belong to, preserving wire order -
    one AK3/IK3 per segment with its element-level issues underneath.
    """

    # Our response to produce
    out:'issue_group_list' = []

    for issue in issues:
        for position, tag, grouped in out:
            if position == issue.segment_position:
                if tag == issue.segment_tag:
                    grouped.append(issue)
                    break
        else:
            out.append((issue.segment_position, issue.segment_tag, [issue]))

    return out

# ################################################################################################################################

def _build_element_note(note_class:'any_', issue:'any_') -> 'any_':
    """ Builds one AK4 or IK4 from an element-level validation issue.
    """
    position = PositionInSegment()
    position.element_position = str(issue.element_position)

    if issue.component_position:
        position.component_position = str(issue.component_position)

    note = note_class()
    note.position = position
    note.error_code = issue.element_error_code

    if issue.value:
        note.bad_value = issue.value

    out = note
    return out

# ################################################################################################################################

def _build_ack_sets(
    interchange:'X12Interchange',
    results:'set_result_list_none',
    is_999:'bool',
    ) -> 'X12Interchange':
    """ The shared 997/999 builder - one acknowledgment set per received functional
    group, with the per-set responses reflecting each set's validation outcome.
    """
    if results is None:
        results = validate_interchange(interchange)

    # Our response to produce
    out = X12Interchange()

    _swap_envelope(interchange, out)

    for group_index, group in enumerate(interchange.groups):

        # Only the results of this group apply here
        group_results:'set_result_list' = []
        for result in results:
            if result.group_index == group_index:
                group_results.append(result)

        if is_999:
            message:'any_' = ImplementationAcknowledgment999()
            message.st.implementation_reference = Version_999
        else:
            message = FunctionalAcknowledgment997()

        # AK1 names the group being acknowledged
        ak1 = AK1()
        ak1.functional_id_code = group.gs.functional_id_code
        ak1.control_number = group.gs.control_number

        if is_999:
            ak1.version = group.gs.version

        message.ak1 = ak1

        # One AK2 loop per transaction set
        responses:'anylist' = []
        accepted_count = 0

        for result in group_results:

            if is_999:
                response:'any_' = SetResponse999()
            else:
                response = SetResponse997()

            ak2 = AK2()
            ak2.identifier_code = result.identifier_code
            ak2.control_number = result.control_number
            response.ak2 = ak2

            # The response reflects the validation outcome - a rejected set
            # never produces a clean acknowledgment.
            if result.issues:
                notes:'anylist' = []

                for segment_position, segment_tag, segment_issues in _group_issues_by_segment(result.issues):

                    first_issue = segment_issues[0]

                    if is_999:
                        note:'any_' = SegmentNote999()
                        segment_note = IK3()
                    else:
                        note = SegmentNote997()
                        segment_note = AK3()

                    segment_note.segment_id = segment_tag
                    segment_note.position = str(segment_position)
                    segment_note.error_code = first_issue.segment_error_code

                    if is_999:
                        note.ik3 = segment_note

                        # The CTX carries the business reference the CMS guides require
                        business_key = extract_business_key(result.message)
                        if business_key:
                            context = ContextIdentification()
                            context.name = business_key_context_name(result.identifier_code)
                            context.reference = business_key

                            ctx = CTX()
                            ctx.context = context
                            note.contexts = [ctx]
                    else:
                        note.ak3 = segment_note

                    element_notes:'anylist' = []

                    for issue in segment_issues:
                        if issue.element_error_code:
                            if is_999:
                                element_note = _build_element_note(IK4, issue)
                            else:
                                element_note = _build_element_note(AK4, issue)
                            element_notes.append(element_note)

                    if element_notes:
                        note.element_notes = element_notes

                    notes.append(note)

                response.segment_notes = notes

                if is_999:
                    trailer:'any_' = IK5()
                else:
                    trailer = AK5()

                trailer.ack_code = Ack_Rejected
                trailer.error_code_1 = Set_Error_Segments_In_Error

            else:
                accepted_count += 1

                if is_999:
                    trailer = IK5()
                else:
                    trailer = AK5()

                trailer.ack_code = Ack_Accepted

            if is_999:
                response.ik5 = trailer
            else:
                response.ak5 = trailer

            responses.append(response)

        message.set_responses = responses

        # AK9 concludes the group response with its counts
        set_count = len(group_results)

        if accepted_count == set_count:
            group_code = Ack_Accepted
        elif accepted_count == 0:
            group_code = Ack_Rejected
        else:
            group_code = Ack_Partial

        ak9 = AK9()
        ak9.ack_code = group_code
        ak9.included_count = str(set_count)
        ak9.received_count = str(set_count)
        ak9.accepted_count = str(accepted_count)
        message.ak9 = ak9

        out.add(message)

    # A 997 group echoes the version of the interchange it acknowledges -
    # a 999 group already declares its own implementation reference.
    if not is_999:
        out.groups[0].gs.version = interchange.groups[0].gs.version

    return out

# ################################################################################################################################

def build_997(interchange:'X12Interchange', results:'set_result_list_none'=None) -> 'X12Interchange':
    """ Builds a 997 functional acknowledgment for a parsed interchange. The validation
    results may be passed in, otherwise the interchange is validated here - either way
    the AK5 and AK9 codes always reflect the outcome per set.
    """
    out = _build_ack_sets(interchange, results, False)
    return out

# ################################################################################################################################

def build_999(interchange:'X12Interchange', results:'set_result_list_none'=None) -> 'X12Interchange':
    """ Builds a 999 implementation acknowledgment (005010X231A1) for a parsed interchange,
    with the CTX context segments populated automatically from the validation context.
    """
    out = _build_ack_sets(interchange, results, True)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _find_single_set(interchange:'X12Interchange', set_type:'str') -> 'any_':
    """ Returns the single transaction set of the given type, raising when there is
    none or more than one.
    """
    matches:'anylist' = []

    for group in interchange.groups:
        for transaction_set in group.transaction_sets:
            st_segment = transaction_set._raw_segments[0]
            identifier_code = _element_value(st_segment, 1)

            if identifier_code == set_type:
                matches.append(transaction_set)

    match_count = len(matches)

    if match_count != 1:
        raise X12AckError(f'Expected exactly 1 `{set_type}` transaction set, found {match_count}')

    out = matches[0]
    return out

# ################################################################################################################################

def _parse_ack(message:'any_', is_999:'bool') -> 'AckResult':
    """ The shared 997/999 parser - reads the typed message back into a result object.
    """

    # Our response to produce
    out = AckResult()

    ak1 = message.ak1
    out.functional_id_code = ak1.functional_id_code
    out.group_control_number = ak1.control_number

    ak9 = message.ak9
    out.ack_code = ak9.ack_code
    out.included_count = int(ak9.included_count)
    out.received_count = int(ak9.received_count)
    out.accepted_count = int(ak9.accepted_count)

    for response in message.set_responses:

        set_result = SetAckResult()
        set_result.identifier_code = response.ak2.identifier_code
        set_result.control_number = response.ak2.control_number

        if is_999:
            trailer = response.ik5
        else:
            trailer = response.ak5

        set_result.ack_code = trailer.ack_code

        for error_code in (trailer.error_code_1, trailer.error_code_2, trailer.error_code_3,
                trailer.error_code_4, trailer.error_code_5):
            if error_code:
                set_result.error_codes.append(error_code)

        for note in response.segment_notes:

            if is_999:
                segment_note = note.ik3
            else:
                segment_note = note.ak3

            note_result = SegmentNoteResult()
            note_result.segment_id = segment_note.segment_id
            note_result.position = int(segment_note.position)

            if segment_note.error_code:
                note_result.error_code = segment_note.error_code

            for element_note in note.element_notes:

                element_result = ElementNoteResult()
                element_result.element_position = int(element_note.position.element_position)

                if element_note.position.component_position:
                    element_result.component_position = int(element_note.position.component_position)

                element_result.error_code = element_note.error_code

                if element_note.bad_value:
                    element_result.bad_value = element_note.bad_value

                note_result.element_notes.append(element_result)

            set_result.segment_notes.append(note_result)

        out.set_results.append(set_result)

    return out

# ################################################################################################################################

def parse_997(interchange:'X12Interchange') -> 'AckResult':
    """ Parses the single 997 of an interchange back into a result object.
    """
    message = _find_single_set(interchange, '997')

    out = _parse_ack(message, False)
    return out

# ################################################################################################################################

def parse_999(interchange:'X12Interchange') -> 'AckResult':
    """ Parses the single 999 of an interchange back into a result object.
    """
    message = _find_single_set(interchange, '999')

    out = _parse_ack(message, True)
    return out

# ################################################################################################################################
# ################################################################################################################################
