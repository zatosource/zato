# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.hl7.display import build_display_tree
from zato.hl7v2 import parse_hl7

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# An admission with a repeating PID-3, a composite PID-5 and a Z-segment the structure does not know
_adt_a01 = (
    'MSH|^~\\&|HIS|GENERAL_HOSPITAL|LAB_SYSTEM|CENTRAL_LAB|20260115103000||ADT^A01^ADT_A01|MSG000001|P|2.9\r'
    'EVN|A01|20260115103000\r'
    'PID|1||NHS7788990^^^NHS^NH~445566^^^GENERAL_HOSPITAL^MR||SMITH^JOHN^A||19850315|M\r'
    'PV1|1|I|ICU^101^A\r'
    'ZAU|1|CUSTOM_VALUE\r'
)

# A lab result whose OBX segments live inside message groups, not at the top level
_oru_r01 = (
    'MSH|^~\\&|LAB_SYSTEM|CENTRAL_LAB|HIS|GENERAL_HOSPITAL|20260115110000||ORU^R01^ORU_R01|MSG000002|P|2.9\r'
    'PID|1||334455^^^CLINIC^MR||DOE^JANE||19900101|F\r'
    'OBR|1|ORDER001||24331-1^Lipid panel^LN\r'
    'OBX|1|NM|2093-3^Cholesterol^LN||182|mg/dL|||||F\r'
    'OBX|2|NM|2085-9^HDL^LN||58|mg/dL|||||F\r'
)

# ################################################################################################################################
# ################################################################################################################################

def _get_segment(tree:'stranydict', segment_id:'str') -> 'stranydict':
    for segment in tree['segments']:
        if segment['segment_id'] == segment_id:
            return segment
    raise Exception(f'Segment `{segment_id}` not found in `{tree}`')

# ################################################################################################################################

def _get_field(segment:'stranydict', position:'int') -> 'stranydict':
    for field in segment['fields']:
        if field['position'] == position:
            return field
    raise Exception(f'Field `{position}` not found in `{segment}`')

# ################################################################################################################################
# ################################################################################################################################

class TestHeader:

    def test_header_identifies_the_message(self) -> 'None':

        msg = parse_hl7(_adt_a01, validate=False)
        tree = build_display_tree(msg)

        assert tree['structure_id'] == 'ADT_A01'
        assert tree['msg_type'] == 'ADT^A01'
        assert tree['control_id'] == 'MSG000001'

# ################################################################################################################################
# ################################################################################################################################

class TestSegments:

    def test_segments_come_in_wire_order_with_z_segments_last(self) -> 'None':

        msg = parse_hl7(_adt_a01, validate=False)
        tree = build_display_tree(msg)

        segment_ids = [segment['segment_id'] for segment in tree['segments']]
        assert segment_ids == ['MSH', 'EVN', 'PID', 'PV1', 'ZAU']

    def test_group_nested_segments_are_walked_in_order(self) -> 'None':

        msg = parse_hl7(_oru_r01, validate=False)
        tree = build_display_tree(msg)

        segment_ids = [segment['segment_id'] for segment in tree['segments']]
        assert segment_ids == ['MSH', 'PID', 'OBR', 'OBX', 'OBX']

# ################################################################################################################################
# ################################################################################################################################

class TestFields:

    def test_named_field_carries_its_label_and_wire_value(self) -> 'None':

        msg = parse_hl7(_adt_a01, validate=False)
        tree = build_display_tree(msg)

        pid = _get_segment(tree, 'PID')
        patient_name = _get_field(pid, 5)

        assert patient_name['reference'] == 'PID-5'
        assert patient_name['name'] == 'patient_name'
        assert patient_name['label'] == 'Patient Name'
        assert patient_name['value'] == 'SMITH^JOHN^A'

    def test_msh_positions_account_for_the_field_separator(self) -> 'None':

        msg = parse_hl7(_adt_a01, validate=False)
        tree = build_display_tree(msg)

        msh = _get_segment(tree, 'MSH')

        sending_facility = _get_field(msh, 4)
        assert sending_facility['name'] == 'sending_facility'
        assert sending_facility['value'] == 'GENERAL_HOSPITAL'

        message_type = _get_field(msh, 9)
        assert message_type['name'] == 'message_type'
        assert message_type['value'] == 'ADT^A01^ADT_A01'

    def test_repeating_field_keeps_each_repetition(self) -> 'None':

        msg = parse_hl7(_adt_a01, validate=False)
        tree = build_display_tree(msg)

        pid = _get_segment(tree, 'PID')
        identifier_list = _get_field(pid, 3)

        assert identifier_list['value'] == 'NHS7788990^^^NHS^NH~445566^^^GENERAL_HOSPITAL^MR'

        repetitions = identifier_list['repetitions']
        assert len(repetitions) == 2
        assert repetitions[0]['value'] == 'NHS7788990^^^NHS^NH'
        assert repetitions[1]['value'] == '445566^^^GENERAL_HOSPITAL^MR'

    def test_unknown_field_keeps_its_wire_reference_as_the_label(self) -> 'None':

        msg = parse_hl7(_adt_a01, validate=False)
        tree = build_display_tree(msg)

        zau = _get_segment(tree, 'ZAU')
        custom = _get_field(zau, 2)

        assert custom['name'] == ''
        assert custom['label'] == 'ZAU-2'
        assert custom['value'] == 'CUSTOM_VALUE'

    def test_empty_fields_are_left_out(self) -> 'None':

        msg = parse_hl7(_adt_a01, validate=False)
        tree = build_display_tree(msg)

        pid = _get_segment(tree, 'PID')
        positions = [field['position'] for field in pid['fields']]

        # PID-2 and PID-4 are empty on the wire and PID-9 onwards is absent
        assert positions == [1, 3, 5, 7, 8]

# ################################################################################################################################
# ################################################################################################################################

class TestComponents:

    def test_composite_field_names_its_components(self) -> 'None':

        msg = parse_hl7(_adt_a01, validate=False)
        tree = build_display_tree(msg)

        pid = _get_segment(tree, 'PID')
        patient_name = _get_field(pid, 5)

        components = patient_name['repetitions'][0]['components']
        by_position = {component['position']: component for component in components}

        assert by_position[1]['name'] == 'family_name'
        assert by_position[1]['label'] == 'Family Name'
        assert by_position[1]['value'] == 'SMITH'

        assert by_position[2]['name'] == 'given_name'
        assert by_position[2]['value'] == 'JOHN'

    def test_empty_components_are_left_out(self) -> 'None':

        msg = parse_hl7(_adt_a01, validate=False)
        tree = build_display_tree(msg)

        pid = _get_segment(tree, 'PID')
        identifier_list = _get_field(pid, 3)

        # NHS7788990^^^NHS^NH - components 2 and 3 are empty on the wire
        components = identifier_list['repetitions'][0]['components']
        positions = [component['position'] for component in components]
        assert positions == [1, 4, 5]

    def test_scalar_field_has_no_component_children(self) -> 'None':

        msg = parse_hl7(_adt_a01, validate=False)
        tree = build_display_tree(msg)

        pid = _get_segment(tree, 'PID')
        sex = _get_field(pid, 8)

        assert sex['value'] == 'M'
        assert sex['repetitions'][0]['components'] == []

# ################################################################################################################################
# ################################################################################################################################
