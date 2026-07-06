# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.hl7v2 import parse_hl7
from zato.hl7v2.testing.live_util import load_message, md_path_for
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA06NextOfKin, OruR01Observation, OruR01OrderObservation, OruR01Patient, \
    OruR01PatientResult
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A06, ORU_R01
from zato.hl7v2.v2_9.segments import AL1, EVN, IN1, MSH, NK1, OBR, OBX, PID, PV1, PV2

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ca', 'ca-pointclickcare.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PCC')
        msh.sending_facility = HD(hd_1='SUNSET MANOR LTC')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='LHIN_CENTRAL')
        msh.date_time_of_message = '20260401100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'PCC00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260401100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1234567890', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Gauthier', xpn_2='Lucienne', xpn_3='Marie', xpn_5='Mme')
        pid.date_time_of_birth = '19350812'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [XAD(xad_1='SUNSET MANOR'), XAD(xad_1='250 Sunset Dr', xad_3='Niagara Falls', xad_4='ON', xad_5='L2G 1A4', xad_6='CA')]
        pid.pid_13 = '^^PH^9055551234'
        pid.primary_language = CWE(cwe_1='F')
        pid.marital_status = CWE(cwe_1='WID')
        pid.pid_36 = ''

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Gauthier', xpn_2='Philippe', xpn_4='Mr')
        nk1.relationship = CWE(cwe_1='SON')
        nk1.address = XAD(xad_1='88 Queen St', xad_3='St. Catharines', xad_4='ON', xad_5='L2R 5G3', xad_6='CA')
        nk1.nk1_5 = '^^PH^9055559876~^^CP^9055558765'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='2EAST', pl_2='201', pl_3='A', pl_4='Sunset Manor LTC')
        pv1.attending_doctor = XCN(xcn_1='34567', xcn_2='Simard', xcn_3='Nicole', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='LTC')
        pv1.patient_type = CWE(cwe_1='VN20260401001')
        pv1.discharge_date_time = '20260401100000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_id = CX(cx_1='OHIP')
        in1.insurance_company_name = XON(xon_1='Ontario Health Insurance Plan')
        in1.insurance_company_address = XAD(xad_1="49 Place d'Armes", xad_3='Kingston', xad_4='ON', xad_5='K7L 5J2', xad_6='CA')
        in1.verification_status = '1234567890'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 1)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 1)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg02(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='POINTCLICKCARE')
        msh.sending_facility = HD(hd_1='SILVER CREEK LODGE')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='AHS_CONNECT')
        msh.date_time_of_message = '20260402083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'PCC00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260402083000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2345678901', cx_4='AB_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Ferguson', xpn_2='William', xpn_3='James', xpn_5='Mr')
        pid.date_time_of_birth = '19410604'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = [XAD(xad_1='SILVER CREEK LODGE'), XAD(xad_1='100 Silver Creek Rd', xad_3='Red Deer', xad_4='AB', xad_5='T4N 5E5', xad_6='CA')]
        pid.pid_13 = '^^PH^4035552345'
        pid.primary_language = CWE(cwe_1='M')
        pid.marital_status = CWE(cwe_1='WID')
        pid.pid_36 = ''

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Ferguson', xpn_2='Sandra', xpn_4='Ms')
        nk1.relationship = CWE(cwe_1='DAU')
        nk1.address = XAD(xad_1='340 Gaetz Ave', xad_3='Red Deer', xad_4='AB', xad_5='T4N 3Y3', xad_6='CA')
        nk1.nk1_5 = '^^PH^4035559876~^^CP^4035558765'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MAPLE', pl_2='102', pl_3='A', pl_4='Silver Creek Lodge')
        pv1.attending_doctor = XCN(xcn_1='45678', xcn_2='Gupta', xcn_3='Rajesh', xcn_6='Dr.', xcn_8='CPSA')
        pv1.hospital_service = CWE(cwe_1='LTC')
        pv1.patient_type = CWE(cwe_1='VN20260402001')
        pv1.discharge_date_time = '20260402083000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_id = CX(cx_1='AHCIP')
        in1.insurance_company_name = XON(xon_1='Alberta Health Care Insurance Plan')
        in1.insurance_company_address = XAD(xad_1='10025 Jasper Ave', xad_3='Edmonton', xad_4='AB', xad_5='T5J 1S6', xad_6='CA')
        in1.verification_status = '2345678901'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 2)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 2)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg03(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PCC')
        msh.sending_facility = HD(hd_1='MAPLE GROVE RESIDENCE')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='LHIN_SOUTH_WEST')
        msh.date_time_of_message = '20260403140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'PCC00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260403140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3456789012', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Boucher', xpn_2='Therese', xpn_3='Anne', xpn_5='Mme')
        pid.date_time_of_birth = '19280917'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [XAD(xad_1='MAPLE GROVE RESIDENCE'), XAD(xad_1='75 Maple Grove Rd', xad_3='London', xad_4='ON', xad_5='N6G 1E7', xad_6='CA')]
        pid.pid_13 = '^^PH^5195553456'
        pid.primary_language = CWE(cwe_1='F')
        pid.marital_status = CWE(cwe_1='WID')
        pid.pid_36 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='BIRCH', pl_2='301', pl_3='B', pl_4='Maple Grove Residence')
        pv1.attending_doctor = XCN(xcn_1='56789', xcn_2='Chen', xcn_3='Li', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='LTC')
        pv1.patient_type = CWE(cwe_1='VN20260403001')
        pv1.discharge_disposition = CWE(cwe_1='OAK', cwe_2='203', cwe_3='A', cwe_4='Maple Grove Residence')
        pv1.account_status = CWE(cwe_1='20260403140000')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 3)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 3)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg04(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PCC')
        msh.sending_facility = HD(hd_1='LAKEVIEW TERRACE')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='LHIN_CENTRAL_EAST')
        msh.date_time_of_message = '20260404060000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'PCC00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260404060000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4567890123', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Levesque', xpn_2='Henri', xpn_3='Marcel', xpn_5='Mr')
        pid.date_time_of_birth = '19300215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = [XAD(xad_1='LAKEVIEW TERRACE'), XAD(xad_1='400 Lakeshore Rd E', xad_3='Oakville', xad_4='ON', xad_5='L6J 1J5', xad_6='CA')]
        pid.pid_13 = '^^PH^9055554567'
        pid.primary_language = CWE(cwe_1='M')
        pid.marital_status = CWE(cwe_1='MAR')
        pid.religion = CWE(cwe_1='CAT')
        pid.breed_code = CWE(cwe_1='20260404053000')
        pid.strain = 'Y'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PINE', pl_2='105', pl_3='A', pl_4='Lakeview Terrace')
        pv1.attending_doctor = XCN(xcn_1='67890', xcn_2='Patel', xcn_3='Sanjay', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='LTC')
        pv1.patient_type = CWE(cwe_1='VN20260404001')
        pv1.discharge_date_time = '20260404060000'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 4)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 4)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg05(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='POINTCLICKCARE')
        msh.sending_facility = HD(hd_1='HERITAGE GREEN LTC')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='HNHB_LHIN')
        msh.date_time_of_message = '20260405100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A06', msg_3='ADT_A06')
        msh.message_control_id = 'PCC00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A06'
        evn.recorded_date_time = '20260405100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5678901234', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Thibault', xpn_2='Yvette', xpn_3='Louise', xpn_5='Mme')
        pid.date_time_of_birth = '19380721'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='55 Wilson St', xad_3='Hamilton', xad_4='ON', xad_5='L8R 1C4', xad_6='CA')
        pid.pid_13 = '^^PH^9055555678'
        pid.primary_language = CWE(cwe_1='F')
        pid.marital_status = CWE(cwe_1='WID')
        pid.pid_36 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='78901', xcn_2='Morin', xcn_3='Claude', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='LTC')
        pv1.patient_type = CWE(cwe_1='VN20260405001')
        pv1.discharge_date_time = '20260405100000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.expected_admit_date_time = '20260401100000'
        pv2.expected_discharge_date_time = '20260405100000'
        pv2.visit_description = 'Respite care completed'

        # .. assemble the full message ..
        msg = ADT_A06()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 5)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 5)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg06(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PCC')
        msh.sending_facility = HD(hd_1='PARKWOOD SUITES')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='LHIN_SOUTH_WEST')
        msh.date_time_of_message = '20260406080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A07', msg_3='ADT_A07')
        msh.message_control_id = 'PCC00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A07'
        evn.recorded_date_time = '20260406080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='6789012345', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lalonde', xpn_2='Gerald', xpn_3='Robert', xpn_5='Mr')
        pid.date_time_of_birth = '19360413'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = [XAD(xad_1='PARKWOOD SUITES'), XAD(xad_1='180 Commissioners Rd W', xad_3='London', xad_4='ON', xad_5='N6J 1Y4', xad_6='CA')]
        pid.pid_13 = '^^PH^5195556789'
        pid.primary_language = CWE(cwe_1='M')
        pid.marital_status = CWE(cwe_1='MAR')
        pid.pid_36 = ''

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Lalonde', xpn_2='Diane', xpn_4='Mme')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='180 Commissioners Rd W', xad_3='London', xad_4='ON', xad_5='N6J 1Y4', xad_6='CA')
        nk1.nk1_5 = '^^PH^5195556790~^^CP^5195558901'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA06NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='WILLOW', pl_2='205', pl_3='A', pl_4='Parkwood Suites')
        pv1.attending_doctor = XCN(xcn_1='89012', xcn_2='Roy', xcn_3='Francois', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='LTC')
        pv1.patient_type = CWE(cwe_1='VN20260406001')
        pv1.discharge_date_time = '20260406080000'

        # .. assemble the full message ..
        msg = ADT_A06()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 6)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 6)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg07(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PCC')
        msh.sending_facility = HD(hd_1='RIVERDALE PLACE LTC')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='LHIN_CENTRAL')
        msh.date_time_of_message = '20260407143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'PCC00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260407143000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7890123456', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Santos', xpn_2='Maria', xpn_3='Elena', xpn_5='Ms')
        pid.date_time_of_birth = '19420509'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [XAD(xad_1='RIVERDALE PLACE'), XAD(xad_1='60 Broadview Ave', xad_3='Toronto', xad_4='ON', xad_5='M4M 2G4', xad_6='CA')]
        pid.pid_13 = '^^PH^4165557890'
        pid.primary_language = CWE(cwe_1='F')
        pid.marital_status = CWE(cwe_1='WID')
        pid.pid_36 = ''

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Santos', xpn_2='Carlos', xpn_4='Mr')
        nk1.relationship = CWE(cwe_1='SON')
        nk1.address = XAD(xad_1='25 Danforth Ave', xad_3='Toronto', xad_4='ON', xad_5='M4K 1N2', xad_6='CA')
        nk1.nk1_5 = '^^PH^4165559012~^^CP^4165558234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build NK1 ..
        nk1_2 = NK1()
        nk1_2.set_id_nk1 = '2'
        nk1_2.name = XPN(xpn_1='Santos', xpn_2='Elena', xpn_4='Ms')
        nk1_2.relationship = CWE(cwe_1='DAU')
        nk1_2.address = XAD(xad_1='110 Pape Ave', xad_3='Toronto', xad_4='ON', xad_5='M4M 2V8', xad_6='CA')
        nk1_2.nk1_5 = '^^PH^4165559345~^^CP^4165557654'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin_2 = AdtA01NextOfKin()
        next_of_kin_2.nk1 = nk1_2

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3SOUTH', pl_2='315', pl_3='A', pl_4='Riverdale Place LTC')
        pv1.attending_doctor = XCN(xcn_1='90123', xcn_2='Lee', xcn_3='Jennifer', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='LTC')
        pv1.patient_type = CWE(cwe_1='VN20260407001')
        pv1.discharge_date_time = '20260407143000'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = [next_of_kin, next_of_kin_2]
        msg.pv1 = pv1

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 7)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 7)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg08(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='POINTCLICKCARE')
        msh.sending_facility = HD(hd_1='CHARTWELL RESIDENCE')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='LHIN_MISSISSAUGA')
        msh.date_time_of_message = '20260408110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'PCC00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260408110000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8901234567', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Pelletier', xpn_2='Germaine', xpn_3='Marguerite', xpn_5='Mme')
        pid.date_time_of_birth = '19310828'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [XAD(xad_1='CHARTWELL RESIDENCE'), XAD(xad_1='450 Dundas St E', xad_3='Mississauga', xad_4='ON', xad_5='L5A 4A1', xad_6='CA')]
        pid.pid_13 = '^^PH^9055558901'
        pid.primary_language = CWE(cwe_1='F')
        pid.marital_status = CWE(cwe_1='WID')
        pid.pid_36 = ''

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='PCN', cwe_2='Penicillin', cwe_3='MED')
        al1.allergy_reaction_code = 'Anaphylaxis'

        # .. build AL1 ..
        al1_2 = AL1()
        al1_2.set_id_al1 = '2'
        al1_2.allergen_type_code = CWE(cwe_1='DA')
        al1_2.allergen_code_mnemonic_description = CWE(cwe_1='SUL', cwe_2='Sulfa', cwe_3='MED')
        al1_2.allergy_reaction_code = 'Rash'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CEDAR', pl_2='110', pl_3='A', pl_4='Chartwell Residence')
        pv1.attending_doctor = XCN(xcn_1='01234', xcn_2='Sharma', xcn_3='Vikram', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='LTC')
        pv1.patient_type = CWE(cwe_1='VN20260408001')
        pv1.discharge_date_time = '20260408110000'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.al1 = [al1, al1_2]
        msg.extra_segments = [pv1]

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 8)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 8)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg09(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PCC')
        msh.sending_facility = HD(hd_1='VILLAGE OF WENTWORTH HEIGHTS')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='HAMILTON_HEALTH_SCI')
        msh.date_time_of_message = '20260409023000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'PCC00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260409023000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='9012345678', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Crawford', xpn_2='Dorothy', xpn_3='Mae', xpn_5='Ms')
        pid.date_time_of_birth = '19320604'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [
            XAD(xad_1='VILLAGE OF WENTWORTH HEIGHTS'),
            XAD(xad_1='1020 Upper Gage Ave', xad_3='Hamilton', xad_4='ON', xad_5='L8V 4R3', xad_6='CA'),
        ]
        pid.pid_13 = '^^PH^9055559012'
        pid.primary_language = CWE(cwe_1='F')
        pid.marital_status = CWE(cwe_1='WID')
        pid.pid_36 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ELM', pl_2='208', pl_3='A', pl_4='Village of Wentworth Heights')
        pv1.attending_doctor = XCN(xcn_1='12345', xcn_2='Bhatt', xcn_3='Anand', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='LTC')
        pv1.patient_type = CWE(cwe_1='VN20260409001')
        pv1.discharge_date_time = '20260409023000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.clinic_organization_name = XON(xon_1='Transfer to Hamilton General Hospital for chest pain evaluation')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 9)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 9)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg10(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFELABS')
        msh.sending_facility = HD(hd_1='LIFELABS_ON')
        msh.receiving_application = HD(hd_1='PCC')
        msh.receiving_facility = HD(hd_1='SUNSET MANOR LTC')
        msh.date_time_of_message = '20260410091500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PCC00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0123456789', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fortin', xpn_2='Beatrice', xpn_3='Helene', xpn_5='Mme')
        pid.date_time_of_birth = '19360113'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [XAD(xad_1='SUNSET MANOR'), XAD(xad_1='250 Sunset Dr', xad_3='Niagara Falls', xad_4='ON', xad_5='L2G 1A4', xad_6='CA')]
        pid.pid_13 = '^^PH^9055550123'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260410001', ei_2='PCC')
        obr.filler_order_number = EI(ei_1='SPE20260410001', ei_2='LIFELABS_ON')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Complete Blood Count', cwe_3='LN')
        obr.observation_date_time = '20260410074500'
        obr.obr_16 = '0123456789^Fortin^Beatrice H^^^^'
        obr.results_rpt_status_chng_date_time = '20260410091500'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='WBC', cwe_3='LN')
        obx.obx_5 = '5.9'
        obx.units = CWE(cwe_1='x10*9/L')
        obx.reference_range = '4.0-11.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='RBC', cwe_3='LN')
        obx_2.obx_5 = '3.95'
        obx_2.units = CWE(cwe_1='x10*12/L')
        obx_2.reference_range = '3.80-5.80'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx_3.obx_5 = '118'
        obx_3.units = CWE(cwe_1='g/L')
        obx_3.reference_range = '120-160'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrit', cwe_3='LN')
        obx_4.obx_5 = '0.35'
        obx_4.units = CWE(cwe_1='L/L')
        obx_4.reference_range = '0.36-0.46'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelets', cwe_3='LN')
        obx_5.obx_5 = '178'
        obx_5.units = CWE(cwe_1='x10*9/L')
        obx_5.reference_range = '150-400'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3
        order_observation.observation_4 = observation_4
        order_observation.observation_5 = observation_5

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 10)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 10)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg11(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFELABS')
        msh.sending_facility = HD(hd_1='LIFELABS_ON')
        msh.receiving_application = HD(hd_1='PCC')
        msh.receiving_facility = HD(hd_1='MAPLE GROVE RESIDENCE')
        msh.date_time_of_message = '20260411101000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PCC00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1122334455', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Desjardins', xpn_2='Roland', xpn_3='Albert', xpn_5='Mr')
        pid.date_time_of_birth = '19290320'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = [XAD(xad_1='MAPLE GROVE RESIDENCE'), XAD(xad_1='75 Maple Grove Rd', xad_3='London', xad_4='ON', xad_5='N6G 1E7', xad_6='CA')]
        pid.pid_13 = '^^PH^5195551122'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260411001', ei_2='PCC')
        obr.filler_order_number = EI(ei_1='SPE20260411001', ei_2='LIFELABS_ON')
        obr.universal_service_identifier = CWE(cwe_1='COAG', cwe_2='Coagulation', cwe_3='LN')
        obr.observation_date_time = '20260411080000'
        obr.obr_16 = '1122334455^Desjardins^Roland A^^^^'
        obr.results_rpt_status_chng_date_time = '20260411101000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='PT', cwe_3='LN')
        obx.obx_5 = '19.8'
        obx.units = CWE(cwe_1='s')
        obx.reference_range = '11.0-13.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '3.2'
        obx_2.reference_range = '2.0-3.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 11)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 11)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg12(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GAMMA_DYNACARE')
        msh.sending_facility = HD(hd_1='DYNACARE_ON')
        msh.receiving_application = HD(hd_1='PCC')
        msh.receiving_facility = HD(hd_1='LAKEVIEW TERRACE')
        msh.date_time_of_message = '20260412140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PCC00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2233445566', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Arsenault', xpn_2='Marguerite', xpn_3='Claire', xpn_5='Mme')
        pid.date_time_of_birth = '19340725'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [XAD(xad_1='LAKEVIEW TERRACE'), XAD(xad_1='400 Lakeshore Rd E', xad_3='Oakville', xad_4='ON', xad_5='L6J 1J5', xad_6='CA')]
        pid.pid_13 = '^^PH^9055552233'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260412001', ei_2='PCC')
        obr.filler_order_number = EI(ei_1='SPE20260412001', ei_2='DYNACARE_ON')
        obr.universal_service_identifier = CWE(cwe_1='RENAL', cwe_2='Renal Function Panel', cwe_3='LN')
        obr.observation_date_time = '20260412081000'
        obr.obr_16 = '2233445566^Arsenault^Marguerite C^^^^'
        obr.results_rpt_status_chng_date_time = '20260412140000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx.obx_5 = '210'
        obx.units = CWE(cwe_1='umol/L')
        obx.reference_range = '50-98'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='48642-3', cwe_2='eGFR', cwe_3='LN')
        obx_2.obx_5 = '18'
        obx_2.units = CWE(cwe_1='mL/min/1.73m2')
        obx_2.reference_range = '>60'
        obx_2.interpretation_codes = CWE(cwe_1='LL')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_3.obx_5 = '22.5'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.1-8.5'
        obx_3.interpretation_codes = CWE(cwe_1='HH')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_4.obx_5 = '5.4'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '3.5-5.1'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3
        order_observation.observation_4 = observation_4

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 12)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 12)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg13(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PCC')
        msh.sending_facility = HD(hd_1='SHAUGHNESSY CARE CENTRE')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='PHSA')
        msh.date_time_of_message = '20260413090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'PCC00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260413090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3344556677', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Wong', xpn_2='Florence', xpn_3='Mei', xpn_5='Ms')
        pid.date_time_of_birth = '19370918'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [
            XAD(xad_1='SHAUGHNESSY CARE CENTRE'),
            XAD(xad_1='4867 Marguerite St', xad_3='Vancouver', xad_4='BC', xad_5='V6J 4L5', xad_6='CA'),
        ]
        pid.pid_13 = '^^PH^6045553344'
        pid.primary_language = CWE(cwe_1='F')
        pid.marital_status = CWE(cwe_1='WID')
        pid.pid_36 = ''

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Wong', xpn_2='David', xpn_4='Mr')
        nk1.relationship = CWE(cwe_1='SON')
        nk1.address = XAD(xad_1='230 Burrard St', xad_3='Vancouver', xad_4='BC', xad_5='V6C 3L6', xad_6='CA')
        nk1.nk1_5 = '^^PH^6045559876~^^CP^6045558765'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MAGNOLIA', pl_2='102', pl_3='A', pl_4='Shaughnessy Care Centre')
        pv1.attending_doctor = XCN(xcn_1='23456', xcn_2='Leung', xcn_3='Andrew', xcn_6='Dr.', xcn_8='CPSBC')
        pv1.hospital_service = CWE(cwe_1='LTC')
        pv1.patient_type = CWE(cwe_1='VN20260413001')
        pv1.discharge_date_time = '20260413090000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_id = CX(cx_1='MSP')
        in1.insurance_company_name = XON(xon_1='BC Medical Services Plan')
        in1.insurance_company_address = XAD(xad_1='1515 Blanshard St', xad_3='Victoria', xad_4='BC', xad_5='V8W 3C8', xad_6='CA')
        in1.verification_status = '3344556677'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 13)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 13)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg14(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PHARMACY')
        msh.sending_facility = HD(hd_1='REXALL_LTC')
        msh.receiving_application = HD(hd_1='PCC')
        msh.receiving_facility = HD(hd_1='SUNSET MANOR LTC')
        msh.date_time_of_message = '20260414153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PCC00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4455667788', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Tardif', xpn_2='Jeannine', xpn_3='Lise', xpn_5='Mme')
        pid.date_time_of_birth = '19310502'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [XAD(xad_1='SUNSET MANOR'), XAD(xad_1='250 Sunset Dr', xad_3='Niagara Falls', xad_4='ON', xad_5='L2G 1A4', xad_6='CA')]
        pid.pid_13 = '^^PH^9055554455'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260414001', ei_2='PHARMACY')
        obr.filler_order_number = EI(ei_1='DOC20260414001', ei_2='REXALL_LTC')
        obr.universal_service_identifier = CWE(cwe_1='MEDREV', cwe_2='Medication Review', cwe_3='LN')
        obr.observation_date_time = '20260414130000'
        obr.obr_16 = '4455667788^Tardif^Jeannine L^^^^'
        obr.results_rpt_status_chng_date_time = '20260414153000'
        obr.diagnostic_serv_sect_id = 'PHARM'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='29553-5', cwe_2='Medication Summary', cwe_3='LN')
        obx.obx_5 = (
            '15 active medications reviewed. Identified 2 potential drug interactions: amlodipine/simvastatin dose concern, metformin/contrast dye precau'
            'tion. Recommended vitamin D supplementation.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Medication Review Report', cwe_3='LN')
        obx_2.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2Jq'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 14)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 14)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg15(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PCC')
        msh.sending_facility = HD(hd_1='HERITAGE GREEN LTC')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='HNHB_LHIN')
        msh.date_time_of_message = '20260415110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'PCC00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260415110000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5566778899', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Gagnon', xpn_2='Lucien', xpn_3='Paul', xpn_5='Mr')
        pid.date_time_of_birth = '19330107'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = [XAD(xad_1='HERITAGE GREEN'), XAD(xad_1='350 Isaac Brock Dr', xad_3='Stoney Creek', xad_4='ON', xad_5='L8J 2P8', xad_6='CA')]
        pid.pid_13 = '^^PH^9055555566'
        pid.primary_language = CWE(cwe_1='M')
        pid.marital_status = CWE(cwe_1='MAR')
        pid.pid_36 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SPRUCE', pl_2='404', pl_3='A', pl_4='Heritage Green LTC')
        pv1.attending_doctor = XCN(xcn_1='34567', xcn_2='Kim', xcn_3='Soo-Yeon', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='LTC')
        pv1.patient_type = CWE(cwe_1='VN20260415001')
        pv1.discharge_date_time = '20260415110000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.patient_status_code = CWE(cwe_1='Level of care changed from C to D effective 2026-04-15')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 15)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 15)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg16(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIFELABS')
        msh.sending_facility = HD(hd_1='LIFELABS_ON')
        msh.receiving_application = HD(hd_1='PCC')
        msh.receiving_facility = HD(hd_1='RIVERDALE PLACE LTC')
        msh.date_time_of_message = '20260416093000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PCC00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='6677889900', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Cormier', xpn_2='Alphonse', xpn_3='Joseph', xpn_5='Mr')
        pid.date_time_of_birth = '19350419'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = [XAD(xad_1='RIVERDALE PLACE'), XAD(xad_1='60 Broadview Ave', xad_3='Toronto', xad_4='ON', xad_5='M4M 2G4', xad_6='CA')]
        pid.pid_13 = '^^PH^4165556677'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260416001', ei_2='PCC')
        obr.filler_order_number = EI(ei_1='SPE20260416001', ei_2='LIFELABS_ON')
        obr.universal_service_identifier = CWE(cwe_1='CHEM', cwe_2='Chemistry Panel', cwe_3='LN')
        obr.observation_date_time = '20260416074500'
        obr.obr_16 = '6677889900^Cormier^Alphonse J^^^^'
        obr.results_rpt_status_chng_date_time = '20260416093000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose Fasting', cwe_3='LN')
        obx.obx_5 = '12.5'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.3-5.5'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx_2.obx_5 = '137'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '136-145'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_3.obx_5 = '4.6'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '3.5-5.1'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_4.obx_5 = '105'
        obx_4.units = CWE(cwe_1='umol/L')
        obx_4.reference_range = '62-115'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3
        order_observation.observation_4 = observation_4

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 16)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 16)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg17(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='POINTCLICKCARE')
        msh.sending_facility = HD(hd_1='BAYCREST CENTRE')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='LHIN_TORONTO_CENTRAL')
        msh.date_time_of_message = '20260417073000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'PCC00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260417073000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7788990011', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Singh', xpn_2='Harjit', xpn_3='Kaur', xpn_5='Ms')
        pid.date_time_of_birth = '19440622'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [XAD(xad_1='BAYCREST CENTRE'), XAD(xad_1='3560 Bathurst St', xad_3='Toronto', xad_4='ON', xad_5='M6A 2E1', xad_6='CA')]
        pid.pid_13 = '^^PH^4165557788'
        pid.primary_language = CWE(cwe_1='F')
        pid.marital_status = CWE(cwe_1='WID')
        pid.pid_36 = ''

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Singh', xpn_2='Ranjit', xpn_4='Mr')
        nk1.relationship = CWE(cwe_1='SON')
        nk1.address = XAD(xad_1='45 Finch Ave W', xad_3='Toronto', xad_4='ON', xad_5='M2N 2H4', xad_6='CA')
        nk1.nk1_5 = '^^PH^4165559012~^^CP^4165558234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CONV', pl_2='302', pl_3='A', pl_4='Baycrest Centre')
        pv1.attending_doctor = XCN(xcn_1='45678', xcn_2='Shapiro', xcn_3='David', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='LTC')
        pv1.patient_type = CWE(cwe_1='VN20260417001')
        pv1.discharge_date_time = '20260417073000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.expected_admit_date_time = '20260417073000'
        pv2.expected_discharge_date_time = '20260515073000'
        pv2.visit_description = 'Convalescent care post hip replacement, 28-day stay'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.pv2 = pv2

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 17)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 17)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg18(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PCC')
        msh.sending_facility = HD(hd_1='PARKWOOD SUITES')
        msh.receiving_application = HD(hd_1='WOUND_SYS')
        msh.receiving_facility = HD(hd_1='WOUND_CARE')
        msh.date_time_of_message = '20260418140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PCC00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8899001122', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Belanger', xpn_2='Raymond', xpn_3='Edouard', xpn_5='Mr')
        pid.date_time_of_birth = '19290814'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = [XAD(xad_1='PARKWOOD SUITES'), XAD(xad_1='180 Commissioners Rd W', xad_3='London', xad_4='ON', xad_5='N6J 1Y4', xad_6='CA')]
        pid.pid_13 = '^^PH^5195558899'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260418001', ei_2='PCC')
        obr.filler_order_number = EI(ei_1='WND20260418001', ei_2='WOUND_CARE')
        obr.universal_service_identifier = CWE(cwe_1='WOUND', cwe_2='Wound Assessment', cwe_3='LN')
        obr.observation_date_time = '20260418100000'
        obr.obr_16 = '8899001122^Belanger^Raymond E^^^^'
        obr.results_rpt_status_chng_date_time = '20260418140000'
        obr.diagnostic_serv_sect_id = 'NURS'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='72170-4', cwe_2='Wound Assessment', cwe_3='LN')
        obx.obx_5 = (
            'Left sacral pressure injury, Stage 3. Dimensions 3.5 x 2.8 x 0.5 cm. Wound bed 80% granulation, 20% slough. Moderate serous drainage. Periwo'
            'und intact.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Wound Photograph', cwe_3='LN')
        obx_2.obx_5 = '^IM^PNG^Base64^iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=='
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 18)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 18)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg19(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PCC')
        msh.sending_facility = HD(hd_1='CHARTWELL RESIDENCE')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='LHIN_MISSISSAUGA')
        msh.date_time_of_message = '20260419150000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'PCC00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260419150000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='9900112233', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Dupuis', xpn_2='Annette', xpn_3='Bernadette', xpn_5='Mme')
        pid.date_time_of_birth = '19400305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='125 Lakeshore Rd W', xad_3='Mississauga', xad_4='ON', xad_5='L5H 1E9', xad_6='CA')
        pid.pid_13 = '^^PH^9055559900'
        pid.primary_language = CWE(cwe_1='F')
        pid.marital_status = CWE(cwe_1='WID')
        pid.pid_36 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CEDAR', pl_2='110', pl_3='A', pl_4='Chartwell Residence')
        pv1.attending_doctor = XCN(xcn_1='01234', xcn_2='Sharma', xcn_3='Vikram', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='LTC')
        pv1.patient_type = CWE(cwe_1='VN20260419001')
        pv1.discharge_date_time = '20260419150000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.patient_status_code = CWE(cwe_1='Discharged home with CCAC home care supports. Follow-up with family physician within 7 days.')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 19)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 19)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg20(unittest.TestCase):
    """ Based on live/ca/ca-pointclickcare.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RAD_SYS')
        msh.sending_facility = HD(hd_1='HAMILTON_RAD')
        msh.receiving_application = HD(hd_1='PCC')
        msh.receiving_facility = HD(hd_1='VILLAGE OF WENTWORTH HEIGHTS')
        msh.date_time_of_message = '20260420163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PCC00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0011223344', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Boudreau', xpn_2='Edith', xpn_3='Marie', xpn_5='Mme')
        pid.date_time_of_birth = '19310920'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [
            XAD(xad_1='VILLAGE OF WENTWORTH HEIGHTS'),
            XAD(xad_1='1020 Upper Gage Ave', xad_3='Hamilton', xad_4='ON', xad_5='L8V 4R3', xad_6='CA'),
        ]
        pid.pid_13 = '^^PH^9055550011'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260420001', ei_2='PCC')
        obr.filler_order_number = EI(ei_1='RAD20260420001', ei_2='HAMILTON_RAD')
        obr.universal_service_identifier = CWE(cwe_1='XCHEST', cwe_2='Portable Chest Xray', cwe_3='LN')
        obr.observation_date_time = '20260420140000'
        obr.obr_16 = '0011223344^Boudreau^Edith M^^^^'
        obr.results_rpt_status_chng_date_time = '20260420163000'
        obr.diagnostic_serv_sect_id = 'RAD'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic Imaging Report', cwe_3='LN')
        obx.obx_5 = (
            'Portable AP chest. Patchy opacity in the right lower lobe consistent with aspiration pneumonitis. No pleural effusion. Heart size upper limi'
            'ts of normal. Chronic degenerative changes thoracic spine.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Chest Xray Image', cwe_3='LN')
        obx_2.obx_5 = (
            '^IM^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgy'
            'IRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 20)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 20)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
