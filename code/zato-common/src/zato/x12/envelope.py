# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# stdlib
import json

from datetime import datetime, timezone

# Zato
from zato.x12.base import X12Message, _element_value
from zato.x12.service import GE, GS, IEA, ISA, TA1
from zato.x12.syntax import No_Repetition, RawSegment, Separators, default_separators, parse_isa, parse_segments

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Any  # noqa: F401

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
any_             = 'Any'
intnone          = 'Optional[int]'
strlist          = list[str]
intlist          = list[int]
anylist          = list['Any']
stranydict       = dict[str, 'Any']
raw_segment_list = list[RawSegment]
message_list     = list[X12Message]
group_list       = list['X12FunctionalGroup']
group_none       = 'X12FunctionalGroup | None'
raw_segment_list_none = 'raw_segment_list | None'

# ################################################################################################################################
# ################################################################################################################################

# The functional identifier code each transaction set files under in a GS group.
functional_id_by_set = {
    '270': 'HS',
    '271': 'HB',
    '810': 'IN',
    '835': 'HP',
    '837': 'HC',
    '850': 'PO',
    '855': 'PR',
    '856': 'SH',
    '997': 'FA',
    '999': 'FA',
}

# ################################################################################################################################
# ################################################################################################################################

# Defaults for envelope fields of interchanges built from scratch.
Default_Auth_Qualifier      = '00'
Default_Security_Qualifier  = '00'
Default_ID_Qualifier        = 'ZZ'
Default_Control_Number      = '1'
Default_Ack_Requested       = '0'
Default_Usage_Indicator     = 'P'
Default_Agency_Code         = 'X'

# ISA11 carries the standards identifier in interchange versions without a repetition separator.
Standards_Identifier = 'U'

# Built transaction sets number their ST02 with at least this many digits.
Set_Control_Number_Width = 4

# The wire formats of the envelope date and time fields.
ISA_Date_Format = '%y%m%d'
GS_Date_Format  = '%Y%m%d'
Time_Format     = '%H%M'

# ################################################################################################################################
# ################################################################################################################################

class X12EnvelopeError(Exception):
    """ Raised when the interchange envelope is structurally invalid, e.g. a control number
    does not match between a header and its trailer or a count is wrong.
    """

# ################################################################################################################################
# ################################################################################################################################

class X12FunctionalGroup:
    """ One functional group of an interchange - its GS header, GE trailer
    and the transaction sets inside it.
    """

    def __init__(self) -> 'None':

        # The GS segment
        self.gs:'any_' = None

        # The GE segment
        self.ge:'any_' = None

        # The typed transaction sets of this group
        self.transaction_sets:'message_list' = []

# ################################################################################################################################
# ################################################################################################################################

class X12Interchange:
    """ A parsed or built X12 interchange - the ISA/IEA envelope, any interchange-level
    TA1 acknowledgments and the functional groups with their transaction sets.
    """

    def __init__(self) -> 'None':

        # The syntax characters in effect for this interchange
        self.separators:'Separators' = default_separators

        # The ISA segment
        self.isa:'any_' = ISA()

        # The IEA segment
        self.iea:'any_' = None

        # Interchange-level TA1 acknowledgments, in wire order
        self.ta1_list:'anylist' = []

        # The functional groups of this interchange
        self.groups:'group_list' = []

        # A built interchange computes its counts and control numbers when serialized,
        # a parsed one stays byte-faithful to its wire data.
        self.is_built:'bool' = True

# ################################################################################################################################

    @property
    def transaction_set(self) -> 'X12Message':
        """ The single transaction set of this interchange - for the common case
        of one document per interchange.
        """
        transaction_sets:'message_list' = []

        for group in self.groups:
            transaction_sets.extend(group.transaction_sets)

        set_count = len(transaction_sets)

        if set_count != 1:
            raise X12EnvelopeError(f'Expected exactly 1 transaction set, found {set_count}')

        out = transaction_sets[0]
        return out

# ################################################################################################################################

    def add(self, transaction_set:'X12Message') -> 'None':
        """ Adds a transaction set to this interchange, filing it into the functional group
        matching its functional identifier code - one ISA can carry many sets in one group
        and many groups next to each other.
        """
        message_type = transaction_set._message_type

        # The set files under its functional identifier code ..
        if functional_id := functional_id_by_set.get(message_type):

            # .. an existing group with the same identifier receives the set ..
            for group in self.groups:
                if group.gs.functional_id_code == functional_id:
                    group.transaction_sets.append(transaction_set)
                    break

            # .. otherwise a new group is created for it.
            else:
                group = X12FunctionalGroup()
                group.gs = GS(functional_id_code=functional_id, version=transaction_set._message_version)
                group.ge = GE()
                group.transaction_sets.append(transaction_set)

                self.groups.append(group)

        # .. and a set type without a known identifier cannot be enveloped.
        else:
            raise X12EnvelopeError(f'No functional identifier code found for transaction set `{message_type}`')

# ################################################################################################################################

    def _finalize(self) -> 'None':
        """ Computes the counts and control numbers of a built interchange from its actual
        structure - GE01, IEA01, SE01 and every unassigned control number and envelope default.
        """
        separators = self.separators
        now = datetime.now(timezone.utc)

        # Fill in the ISA defaults for anything not assigned explicitly ..
        isa = self.isa

        if isa.auth_qualifier is None:
            isa.auth_qualifier = Default_Auth_Qualifier
        if isa.auth_information is None:
            isa.auth_information = ''
        if isa.security_qualifier is None:
            isa.security_qualifier = Default_Security_Qualifier
        if isa.security_information is None:
            isa.security_information = ''
        if isa.sender_qualifier is None:
            isa.sender_qualifier = Default_ID_Qualifier
        if isa.receiver_qualifier is None:
            isa.receiver_qualifier = Default_ID_Qualifier
        if isa.date is None:
            isa.date = now.strftime(ISA_Date_Format)
        if isa.time is None:
            isa.time = now.strftime(Time_Format)
        if isa.control_number is None:
            isa.control_number = Default_Control_Number
        if isa.ack_requested is None:
            isa.ack_requested = Default_Ack_Requested
        if isa.usage_indicator is None:
            isa.usage_indicator = Default_Usage_Indicator

        # .. the syntax characters always mirror the active separators ..
        if separators.repetition == No_Repetition:
            isa.repetition_separator = Standards_Identifier
        else:
            isa.repetition_separator = separators.repetition

        isa.version = separators.version
        isa.component_separator = separators.component

        # .. each group gets its control number and counts from its actual contents ..
        for group_index, group in enumerate(self.groups):
            gs = group.gs

            if gs.control_number is None:
                gs.control_number = str(group_index + 1)
            if gs.sender_code is None:
                if isa.sender_id is not None:
                    gs.sender_code = isa.sender_id.strip()
            if gs.receiver_code is None:
                if isa.receiver_id is not None:
                    gs.receiver_code = isa.receiver_id.strip()
            if gs.date is None:
                gs.date = now.strftime(GS_Date_Format)
            if gs.time is None:
                gs.time = now.strftime(Time_Format)
            if gs.agency_code is None:
                gs.agency_code = Default_Agency_Code

            # .. each set gets its ST/SE pair numbered and counted ..
            for set_index, transaction_set in enumerate(group.transaction_sets):
                st = transaction_set.st
                se = transaction_set.se

                if st.identifier_code is None:
                    st.identifier_code = transaction_set._message_type
                if st.control_number is None:
                    set_number = set_index + 1
                    st.control_number = f'{set_number:0{Set_Control_Number_Width}d}'

                se.control_number = st.control_number

                # SE01 counts every segment of the set, ST and SE included.
                serialized = transaction_set.serialize(separators)
                segment_count = serialized.count('\n') + 1
                se.segment_count = str(segment_count)

            # .. the GE trailer echoes the group's control number and set count ..
            if group.ge is None:
                group.ge = GE()

            set_count = len(group.transaction_sets)
            group.ge.transaction_set_count = str(set_count)
            group.ge.control_number = gs.control_number

        # .. and the IEA trailer concludes the interchange.
        if self.iea is None:
            self.iea = IEA()

        group_count = len(self.groups)
        self.iea.group_count = str(group_count)
        self.iea.control_number = isa.control_number

# ################################################################################################################################

    def serialize(self) -> 'str':
        """ Serializes the whole interchange to its wire form, one segment per line.
        A built interchange computes its counts and control numbers first.
        """
        if self.is_built:
            self._finalize()

        separators = self.separators
        lines:'strlist' = []

        # The ISA comes first ..
        line = self.isa.serialize(separators)
        lines.append(line)

        # .. then any interchange-level TA1 acknowledgments ..
        for ta1 in self.ta1_list:
            line = ta1.serialize(separators)
            lines.append(line)

        # .. then every group with its transaction sets ..
        for group in self.groups:
            line = group.gs.serialize(separators)
            lines.append(line)

            for transaction_set in group.transaction_sets:
                line = transaction_set.serialize(separators)
                lines.append(line)

            line = group.ge.serialize(separators)
            lines.append(line)

        # .. and the IEA trailer concludes the interchange.
        line = self.iea.serialize(separators)
        lines.append(line)

        out = '\n'.join(lines)
        return out

# ################################################################################################################################

    to_x12 = serialize

# ################################################################################################################################

    def to_dict(self, include_empty:'bool'=True) -> 'stranydict':
        """ Converts this interchange to a dictionary representation.
        """

        # Our response to produce
        out:'stranydict' = {}

        out['isa'] = self.isa.to_dict(include_empty=include_empty)

        groups:'anylist' = []

        for group in self.groups:
            transaction_sets:'anylist' = []

            for transaction_set in group.transaction_sets:
                transaction_sets.append(transaction_set.to_dict(include_empty=include_empty))

            group_dict:'stranydict' = {
                'gs': group.gs.to_dict(include_empty=include_empty),
                'transaction_sets': transaction_sets,
            }

            if group.ge is not None:
                group_dict['ge'] = group.ge.to_dict(include_empty=include_empty)

            groups.append(group_dict)

        out['groups'] = groups

        if self.iea is not None:
            out['iea'] = self.iea.to_dict(include_empty=include_empty)

        return out

# ################################################################################################################################

    def to_json(self, indent:'intnone'=None, include_empty:'bool'=True) -> 'str':
        """ Converts this interchange to a JSON string.
        """
        dict_data = self.to_dict(include_empty=include_empty)

        out = json.dumps(dict_data, indent=indent)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _validate_envelope(interchange:'X12Interchange') -> 'None':
    """ Checks the control number echoes and counts of a parsed interchange -
    ISA13=IEA02, GS06=GE02, ST02=SE02, IEA01 is the group count, GE01 the set count,
    SE01 the segment count including ST and SE - and rejects duplicate control numbers.
    """
    isa_control = interchange.isa.control_number
    iea_control = interchange.iea.control_number

    # The IEA must echo the interchange control number ..
    if int(isa_control) != int(iea_control):
        raise X12EnvelopeError(f'ISA13 `{isa_control}` does not match IEA02 `{iea_control}`')

    # .. and carry the actual group count.
    group_count = len(interchange.groups)
    iea_group_count = int(interchange.iea.group_count)

    if iea_group_count != group_count:
        raise X12EnvelopeError(f'IEA01 `{iea_group_count}` does not match the group count {group_count}')

    seen_group_numbers:'intlist' = []

    for group in interchange.groups:
        gs_control = group.gs.control_number
        ge_control = group.ge.control_number

        # The GE must echo the group control number ..
        if int(gs_control) != int(ge_control):
            raise X12EnvelopeError(f'GS06 `{gs_control}` does not match GE02 `{ge_control}`')

        # .. which must be unique within the interchange ..
        group_number = int(gs_control)
        if group_number in seen_group_numbers:
            raise X12EnvelopeError(f'Duplicate group control number `{gs_control}`')
        seen_group_numbers.append(group_number)

        # .. and carry the actual transaction set count.
        set_count = len(group.transaction_sets)
        ge_set_count = int(group.ge.transaction_set_count)

        if ge_set_count != set_count:
            raise X12EnvelopeError(f'GE01 `{ge_set_count}` does not match the transaction set count {set_count}')

        seen_set_numbers:'strlist' = []

        for transaction_set in group.transaction_sets:
            raw_segments = transaction_set._raw_segments

            st_segment = raw_segments[0]
            se_segment = raw_segments[-1]

            st_control = _element_value(st_segment, 2)
            se_control = _element_value(se_segment, 2)

            # The SE must echo the set control number exactly ..
            if st_control != se_control:
                raise X12EnvelopeError(f'ST02 `{st_control}` does not match SE02 `{se_control}`')

            # .. which must be unique within the group ..
            if st_control in seen_set_numbers:
                raise X12EnvelopeError(f'Duplicate transaction set control number `{st_control}`')
            seen_set_numbers.append(st_control)

            # .. and carry the actual segment count, ST and SE included.
            segment_count = len(raw_segments)
            se_segment_count = int(_element_value(se_segment, 1))

            if se_segment_count != segment_count:
                raise X12EnvelopeError(f'SE01 `{se_segment_count}` does not match the segment count {segment_count}')

# ################################################################################################################################

def parse_x12(raw:'str', strict:'bool'=False) -> 'X12Interchange':
    """ Parses wire text into an X12Interchange - the single public entry point.
    The separators come from the fixed-width ISA, each ST/SE slice resolves to its
    registered transaction set class by ST01 plus the GS08 version of its group,
    and the envelope control numbers and counts are validated on the way.

    The default lenient mode keeps unknown segments and unmapped elements reachable
    positionally - nothing is ever unparseable. Strict mode additionally applies
    the implementation guide syntax checks (SNIP type 2) to every typed transaction
    set and raises X12ValidationError with all the issues collected per set.
    """

    # Our response to produce
    out = X12Interchange()
    out.is_built = False

    # Leading whitespace never carries meaning in an interchange
    raw = raw.lstrip()

    # The ISA dictates the syntax characters of everything that follows ..
    separators = parse_isa(raw)
    out.separators = separators

    # .. so the whole interchange can now be split into raw segments.
    raw_segments = parse_segments(raw, separators)

    current_group:'group_none' = None
    current_set:'raw_segment_list_none' = None

    for raw_segment in raw_segments:
        tag = raw_segment.tag

        # The interchange envelope ..
        if tag == 'ISA':
            out.isa = ISA.from_raw(raw_segment)
            continue

        if tag == 'IEA':
            out.iea = IEA.from_raw(raw_segment)
            continue

        # .. interchange-level acknowledgments live between ISA and the first GS ..
        if tag == 'TA1':
            if current_set is None:
                ta1 = TA1.from_raw(raw_segment)
                out.ta1_list.append(ta1)
                continue

        # .. the group envelope ..
        if tag == 'GS':
            if current_group is not None:
                raise X12EnvelopeError('GS found before the previous group was closed with GE')

            current_group = X12FunctionalGroup()
            current_group.gs = GS.from_raw(raw_segment)
            continue

        if tag == 'GE':
            if current_group is None:
                raise X12EnvelopeError('GE found without a matching GS')

            current_group.ge = GE.from_raw(raw_segment)
            out.groups.append(current_group)
            current_group = None
            continue

        # .. and the transaction sets themselves.
        if tag == 'ST':
            if current_group is None:
                raise X12EnvelopeError('ST found outside of a functional group')
            if current_set is not None:
                raise X12EnvelopeError('ST found before the previous transaction set was closed with SE')

            current_set = [raw_segment]
            continue

        if current_set is None:
            raise X12EnvelopeError(f'Segment `{tag}` found outside of a transaction set')

        current_set.append(raw_segment)

        # An SE concludes the current set, which resolves to its registered class.
        if tag == 'SE':
            group_version = current_group.gs.version
            message_class = X12Message.resolve_class(current_set, group_version)
            message = message_class.from_raw(current_set, separators)

            current_group.transaction_sets.append(message)
            current_set = None

    # Whatever remains open at this point means a missing trailer.
    if current_set is not None:
        raise X12EnvelopeError('Transaction set not closed with SE')

    if current_group is not None:
        raise X12EnvelopeError('Functional group not closed with GE')

    if out.iea is None:
        raise X12EnvelopeError('Interchange not closed with IEA')

    # The envelope is structurally complete - now its numbers must agree.
    _validate_envelope(out)

    # Strict mode applies the dictionary-level checks on top of the envelope ones.
    if strict:

        # Imported here because zato.x12.validation itself imports this module
        from zato.x12.validation import X12ValidationError, validate_interchange

        results = validate_interchange(out)

        issue_count = 0
        for result in results:
            issue_count += len(result.issues)

        if issue_count:
            raise X12ValidationError(f'Found {issue_count} validation issue(s)', results)

    return out

# ################################################################################################################################
# ################################################################################################################################
