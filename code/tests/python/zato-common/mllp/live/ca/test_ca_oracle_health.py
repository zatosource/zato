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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, SiuS12Patient, SiuS12PersonnelResource, \
    SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIP, AIS, DG1, EVN, IN1, MRG, MSH, NK1, OBR, OBX, ORC, PID, PV1, RGS, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ca', 'ca-oracle-health.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ca/ca-oracle-health.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='SUNNYBROOK_HIS')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='PACS_SYS')
        msh.date_time_of_message = '20260509081500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509081500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7812345678', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Thompson', xpn_2='Margaret', xpn_3='Anne', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2075 Bayview Ave', xad_3='Toronto', xad_4='ON', xad_5='M4N 3M5', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^416^4804100'
        pid.pid_14 = '^WPN^PH^^1^416^4804200'
        pid.patient_account_number = CX(cx_1='AC100234567')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4EAST', pl_2='401', pl_3='A', pl_4='SUNNYBROOK')
        pv1.attending_doctor = XCN(xcn_1='12345', xcn_2='Chen', xcn_3='David', xcn_6='Dr.', xcn_8='MD')
        pv1.referring_doctor = XCN(xcn_1='67890', xcn_2='Patel', xcn_3='Anita', xcn_6='Dr.', xcn_8='MD')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.ambulatory_status = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='VIS2026050901')
        pv1.admit_date_time = '20260509081500'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_id = CX(cx_1='OHIPplan')
        in1.insurance_company_name = XON(xon_1='Ontario Health Insurance Plan')
        in1.insurance_company_address = XAD(xad_1="49 Place d'Armes", xad_3='Kingston', xad_4='ON', xad_5='K7L 5J3', xad_6='CA')
        in1.verification_status = '7812345678'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
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
    """ Based on live/ca/ca-oracle-health.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='SUNNYBROOK_HIS')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='PACS_SYS')
        msh.date_time_of_message = '20260509093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260509093000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7812345678', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Thompson', xpn_2='Margaret', xpn_3='Anne', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2075 Bayview Ave', xad_3='Toronto', xad_4='ON', xad_5='M4N 3M5', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^416^4804100'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5ICU', pl_2='501', pl_3='A', pl_4='SUNNYBROOK')
        pv1.attending_doctor = XCN(xcn_1='12345', xcn_2='Chen', xcn_3='David', xcn_6='Dr.', xcn_8='MD')
        pv1.referring_doctor = XCN(xcn_1='67890', xcn_2='Patel', xcn_3='Anita', xcn_6='Dr.', xcn_8='MD')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.ambulatory_status = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='VIS2026050901')
        pv1.admit_date_time = '20260509093000'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/ca/ca-oracle-health.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='SUNNYBROOK_HIS')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='PACS_SYS')
        msh.date_time_of_message = '20260512140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260512140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7812345678', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Thompson', xpn_2='Margaret', xpn_3='Anne', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2075 Bayview Ave', xad_3='Toronto', xad_4='ON', xad_5='M4N 3M5', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^416^4804100'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4EAST', pl_2='401', pl_3='A', pl_4='SUNNYBROOK')
        pv1.attending_doctor = XCN(xcn_1='12345', xcn_2='Chen', xcn_3='David', xcn_6='Dr.', xcn_8='MD')
        pv1.referring_doctor = XCN(xcn_1='67890', xcn_2='Patel', xcn_3='Anita', xcn_6='Dr.', xcn_8='MD')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.ambulatory_status = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='VIS2026050901')
        pv1.admit_date_time = '20260512140000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonia unspecified organism', cwe_3='I10')
        dg1.diagnosis_date_time = '20260509'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/ca/ca-oracle-health.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='AHS_HOSP')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='LAB_SYS')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260509100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='123456789', cx_4='AB_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='MacDonald', xpn_2='James', xpn_3='Robert')
        pid.date_time_of_birth = '19750823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='14520 Stony Plain Rd NW', xad_3='Edmonton', xad_4='AB', xad_5='T5N 3Z4', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^780^5551234'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OUTPT', pl_2='CLINIC3', pl_3='1', pl_4='AHS_ROYAL_ALEX')
        pv1.attending_doctor = XCN(xcn_1='33445', xcn_2='Singh', xcn_3='Harpreet', xcn_6='Dr.', xcn_8='MD')
        pv1.hospital_service = CWE(cwe_1='ORTHO')
        pv1.admit_source = CWE(cwe_1='9')
        pv1.vip_indicator = CWE(cwe_1='VIS2026050902')
        pv1.prior_temporary_location = PL(pl_1='20260509100000')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/ca/ca-oracle-health.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='SUNNYBROOK_HIS')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='PACS_SYS')
        msh.date_time_of_message = '20260510083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260510083000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7812345678', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Thompson', xpn_2='Margaret', xpn_3='Anne', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='100 Wellesley St E', xad_3='Toronto', xad_4='ON', xad_5='M4Y 1H5', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^416^9221234'
        pid.pid_14 = '^WPN^PH^^1^416^9225678'
        pid.patient_account_number = CX(cx_1='AC100234567')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4EAST', pl_2='401', pl_3='A', pl_4='SUNNYBROOK')
        pv1.attending_doctor = XCN(xcn_1='12345', xcn_2='Chen', xcn_3='David', xcn_6='Dr.', xcn_8='MD')
        pv1.referring_doctor = XCN(xcn_1='67890', xcn_2='Patel', xcn_3='Anita', xcn_6='Dr.', xcn_8='MD')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.ambulatory_status = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='VIS2026050901')
        pv1.admit_date_time = '20260510083000'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Thompson', xpn_2='Harold')
        nk1.address = XAD(xad_2='PRN', xad_3='PH', xad_5='1', xad_6='416', xad_7='4804300')
        nk1.next_of_kin_associated_partys_identifiers = CX(cx_1='SPO')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1]

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
    """ Based on live/ca/ca-oracle-health.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='AHS_HOSP')
        msh.receiving_application = HD(hd_1='PROV_REG')
        msh.receiving_facility = HD(hd_1='AB_AHW')
        msh.date_time_of_message = '20260510090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260510090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='987654321', cx_4='AB_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Leblanc', xpn_2='Marie', xpn_3='Claire')
        pid.date_time_of_birth = '19901115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='238 11 Ave SE', xad_3='Calgary', xad_4='AB', xad_5='T2G 0X8', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^403^5559876'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='N')

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
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
    """ Based on live/ca/ca-oracle-health.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='SUNNYBROOK_HIS')
        msh.receiving_application = HD(hd_1='MPI_SYS')
        msh.receiving_facility = HD(hd_1='REG_SYS')
        msh.date_time_of_message = '20260511100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260511100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7812345678', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Thompson', xpn_2='Margaret', xpn_3='Anne', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2075 Bayview Ave', xad_3='Toronto', xad_4='ON', xad_5='M4N 3M5', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^416^4804100'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='9988776655', cx_4='ON_HN', cx_5='JHN')
        mrg.prior_patient_account_number = CX(cx_1='VIS2025120301')

        # .. build the PATIENT group ..
        patient = AdtA39Patient()
        patient.pid = pid
        patient.mrg = mrg

        # .. assemble the full message ..
        msg = ADT_A39()
        msg.msh = msh
        msg.evn = evn
        msg.patient = patient

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
    """ Based on live/ca/ca-oracle-health.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='SUNNYBROOK_HIS')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260509113000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7812345678', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Thompson', xpn_2='Margaret', xpn_3='Anne', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2075 Bayview Ave', xad_3='Toronto', xad_4='ON', xad_5='M4N 3M5', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD100234')
        orc.filler_order_number = EI(ei_1='FIL200567')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509080000'
        orc.orc_12 = '12345^Chen^David^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD100234')
        obr.filler_order_number = EI(ei_1='FIL200567')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel', cwe_3='LN')
        obr.observation_date_time = '20260509073000'
        obr.obr_16 = '12345^Chen^David^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260509110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx.obx_5 = '128'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '120-160'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocytes', cwe_3='LN')
        obx_2.obx_5 = '7.2'
        obx_2.units = CWE(cwe_1='x10E9/L')
        obx_2.reference_range = '4.0-11.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrocytes', cwe_3='LN')
        obx_3.obx_5 = '4.15'
        obx_3.units = CWE(cwe_1='x10E12/L')
        obx_3.reference_range = '3.80-5.20'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_4.obx_5 = '88.5'
        obx_4.units = CWE(cwe_1='fL')
        obx_4.reference_range = '80.0-100.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelets', cwe_3='LN')
        obx_5.obx_5 = '245'
        obx_5.units = CWE(cwe_1='x10E9/L')
        obx_5.reference_range = '150-400'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
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
    """ Based on live/ca/ca-oracle-health.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='SUNNYBROOK_HIS')
        msh.receiving_application = HD(hd_1='RAD_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260509153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7812345678', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Thompson', xpn_2='Margaret', xpn_3='Anne', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2075 Bayview Ave', xad_3='Toronto', xad_4='ON', xad_5='M4N 3M5', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD100300')
        orc.filler_order_number = EI(ei_1='FIL200700')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509120000'
        orc.orc_12 = '55667^Nguyen^Thi^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD100300')
        obr.filler_order_number = EI(ei_1='FIL200700')
        obr.universal_service_identifier = CWE(cwe_1='71046-8', cwe_2='CT Chest', cwe_3='LN')
        obr.observation_date_time = '20260509120000'
        obr.obr_16 = '55667^Nguyen^Thi^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260509150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Radiology Report', cwe_3='MILLENNIUM')
        obx.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2Jq'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='71046-8', cwe_2='CT Chest Impression', cwe_3='LN')
        obx_2.obx_5 = 'No acute cardiopulmonary process. Mild dependent atelectasis bilateral bases.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
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
    """ Based on live/ca/ca-oracle-health.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='AHS_HOSP')
        msh.receiving_application = HD(hd_1='PATH_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260510091500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='987654321', cx_4='AB_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Leblanc', xpn_2='Marie', xpn_3='Claire')
        pid.date_time_of_birth = '19901115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='238 11 Ave SE', xad_3='Calgary', xad_4='AB', xad_5='T2G 0X8', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD100400')
        orc.filler_order_number = EI(ei_1='FIL200800')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509140000'
        orc.orc_12 = '77889^Roy^Francois^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD100400')
        obr.filler_order_number = EI(ei_1='FIL200800')
        obr.universal_service_identifier = CWE(cwe_1='88305-8', cwe_2='Surgical pathology', cwe_3='LN')
        obr.observation_date_time = '20260509140000'
        obr.obr_16 = '77889^Roy^Francois^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='IMG', cwe_2='Pathology Slide Image', cwe_3='AHS')
        obx.obx_5 = (
            '^IM^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsNCwsMDQ4SEA0OEQ4LCxAWEBETFBUVFRQOFxcXFBT/2wBDAQMEBAUEBQkFBQkU'
            'DQsNFBQ'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='88305-8', cwe_2='Surgical pathology interpretation', cwe_3='LN')
        obx_2.obx_5 = 'Left breast excision: Invasive ductal carcinoma, grade 2, 1.8 cm. Margins clear. ER positive, PR positive, HER2 negative.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
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
    """ Based on live/ca/ca-oracle-health.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='SUNNYBROOK_HIS')
        msh.receiving_application = HD(hd_1='LAB_SYS')
        msh.receiving_facility = HD(hd_1='CORE_LAB')
        msh.date_time_of_message = '20260509070000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7812345678', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Thompson', xpn_2='Margaret', xpn_3='Anne', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2075 Bayview Ave', xad_3='Toronto', xad_4='ON', xad_5='M4N 3M5', xad_6='CA')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4EAST', pl_2='401', pl_3='A', pl_4='SUNNYBROOK')
        pv1.attending_doctor = XCN(xcn_1='12345', xcn_2='Chen', xcn_3='David', xcn_6='Dr.', xcn_8='MD')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD100500')
        orc.placer_order_group_number = EI(ei_1='GRP001')
        orc.date_time_of_order_event = '20260509065500'
        orc.orc_12 = '12345^Chen^David^^^Dr.^^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD100500')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel', cwe_3='LN')
        obr.observation_date_time = '20260509070000'
        obr.obr_16 = '12345^Chen^David^^^Dr.^^MD'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='ORD100501')
        orc_2.placer_order_group_number = EI(ei_1='GRP001')
        orc_2.date_time_of_order_event = '20260509065500'
        orc_2.orc_12 = '12345^Chen^David^^^Dr.^^MD'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='ORD100501')
        obr_2.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='CMP', cwe_3='LN')
        obr_2.observation_date_time = '20260509070000'
        obr_2.obr_16 = '12345^Chen^David^^^Dr.^^MD'

        # .. build the ORDER_DETAIL group ..
        order_detail_2 = OrmO01OrderDetail()
        order_detail_2.obr = obr_2

        # .. build the ORDER group ..
        order_2 = OrmO01Order()
        order_2.orc = orc_2
        order_2.order_detail = order_detail_2

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = [order, order_2]

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
    """ Based on live/ca/ca-oracle-health.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='AHS_HOSP')
        msh.receiving_application = HD(hd_1='RIS_SYS')
        msh.receiving_facility = HD(hd_1='RAD_DEPT')
        msh.date_time_of_message = '20260510080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='123456789', cx_4='AB_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='MacDonald', xpn_2='James', xpn_3='Robert')
        pid.date_time_of_birth = '19750823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='14520 Stony Plain Rd NW', xad_3='Edmonton', xad_4='AB', xad_5='T5N 3Z4', xad_6='CA')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OUTPT', pl_2='CLINIC3', pl_3='1', pl_4='AHS_ROYAL_ALEX')
        pv1.attending_doctor = XCN(xcn_1='33445', xcn_2='Singh', xcn_3='Harpreet', xcn_6='Dr.', xcn_8='MD')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD100600')
        orc.date_time_of_order_event = '20260510075000'
        orc.orc_12 = '33445^Singh^Harpreet^^^Dr.^^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD100600')
        obr.universal_service_identifier = CWE(cwe_1='71046-8', cwe_2='CT Chest with contrast', cwe_3='LN')
        obr.observation_date_time = '20260510080000'
        obr.obr_16 = '33445^Singh^Harpreet^^^Dr.^^MD'
        obr.obr_28 = 'ROUTINE'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order

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
    """ Based on live/ca/ca-oracle-health.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='SUNNYBROOK_HIS')
        msh.receiving_application = HD(hd_1='SCHED_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260511140000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20260515001')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70276')
        sch.appointment_type = CWE(cwe_1='FOLLOWUP', cwe_2='Follow-up visit', cwe_3='HL70277')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^30^20260515090000^20260515093000'
        sch.placer_contact_person = XCN(xcn_1='12345', xcn_2='Chen', xcn_3='David', xcn_6='Dr.', xcn_8='MD')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7812345678', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Thompson', xpn_2='Margaret', xpn_3='Anne', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2075 Bayview Ave', xad_3='Toronto', xad_4='ON', xad_5='M4N 3M5', xad_6='CA')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OUTPT', pl_2='CARDIO', pl_3='1', pl_4='SUNNYBROOK')
        pv1.attending_doctor = XCN(xcn_1='12345', xcn_2='Chen', xcn_3='David', xcn_6='Dr.', xcn_8='MD')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='CARDIO_CONSULT', cwe_2='Cardiology Consultation', cwe_3='LOCAL')
        ais.start_date_time = '20260515090000'
        ais.start_date_time_offset = '0'
        ais.start_date_time_offset_units = CNE(cne_1='MIN')
        ais.duration = '30'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='12345', xcn_2='Chen', xcn_3='David', xcn_6='Dr.', xcn_8='MD')
        aip.start_date_time_offset_units = CNE(cne_1='20260515090000')
        aip.duration = '0'
        aip.duration_units = CNE(cne_1='MIN')
        aip.allow_substitution_code = CWE(cwe_1='30')
        aip.filler_status_code = CWE(cwe_1='MIN')

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.personnel_resource = personnel_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/ca/ca-oracle-health.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='SUNNYBROOK_HIS')
        msh.receiving_application = HD(hd_1='DOC_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260512100000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260512100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7812345678', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Thompson', xpn_2='Margaret', xpn_3='Anne', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2075 Bayview Ave', xad_3='Toronto', xad_4='ON', xad_5='M4N 3M5', xad_6='CA')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4EAST', pl_2='401', pl_3='A', pl_4='SUNNYBROOK')
        pv1.attending_doctor = XCN(xcn_1='12345', xcn_2='Chen', xcn_3='David', xcn_6='Dr.', xcn_8='MD')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Discharge Summary', cwe_3='HL70270')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260512090000'
        txa.origination_date_time = '20260512100000'
        txa.transcriptionist_code_name = XCN(xcn_1='12345', xcn_2='Chen', xcn_3='David', xcn_6='Dr.', xcn_8='MD')
        txa.parent_document_number = EI(ei_1='DOC3456789')
        txa.document_availability_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Discharge Summary Document', cwe_3='MILLENNIUM')
        obx.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFI+PgplbmRvYmoKMiAwIG9iago8PC9UeXBlL1BhZ2VzL0tpZHNbMyAwIFJdL0NvdW50IDE+Pgpl'
            'bmRvYmoKMyAwIG9iago8PC9UeXBl'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.txa = txa
        msg.observation = observation

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
    """ Based on live/ca/ca-oracle-health.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='AHS_HOSP')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260510160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='123456789', cx_4='AB_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='MacDonald', xpn_2='James', xpn_3='Robert')
        pid.date_time_of_birth = '19750823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='14520 Stony Plain Rd NW', xad_3='Edmonton', xad_4='AB', xad_5='T5N 3Z4', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD100700')
        orc.filler_order_number = EI(ei_1='FIL200900')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510080000'
        orc.orc_12 = '33445^Singh^Harpreet^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD100700')
        obr.filler_order_number = EI(ei_1='FIL200900')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Comprehensive metabolic panel', cwe_3='LN')
        obr.observation_date_time = '20260510073000'
        obr.obr_16 = '33445^Singh^Harpreet^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510153000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '5.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.3-5.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_2.obx_5 = '92'
        obx_2.units = CWE(cwe_1='umol/L')
        obx_2.reference_range = '62-115'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea nitrogen', cwe_3='LN')
        obx_3.obx_5 = '6.1'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.5-8.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='17861-6', cwe_2='Calcium', cwe_3='LN')
        obx_4.obx_5 = '2.35'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '2.10-2.55'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx_5.obx_5 = '140'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '136-145'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_6.obx_5 = '4.2'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '3.5-5.0'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx_7.obx_5 = '28'
        obx_7.units = CWE(cwe_1='U/L')
        obx_7.reference_range = '7-56'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST', cwe_3='LN')
        obx_8.obx_5 = '24'
        obx_8.units = CWE(cwe_1='U/L')
        obx_8.reference_range = '10-40'
        obx_8.interpretation_codes = CWE(cwe_1='N')
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3
        order_observation.observation_4 = observation_4
        order_observation.observation_5 = observation_5
        order_observation.observation_6 = observation_6
        order_observation.observation_7 = observation_7
        order_observation.observation_8 = observation_8

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
    """ Based on live/ca/ca-oracle-health.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='SUNNYBROOK_HIS')
        msh.receiving_application = HD(hd_1='MICRO_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260511120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7812345678', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Thompson', xpn_2='Margaret', xpn_3='Anne', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2075 Bayview Ave', xad_3='Toronto', xad_4='ON', xad_5='M4N 3M5', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD100800')
        orc.filler_order_number = EI(ei_1='FIL201000')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509090000'
        orc.orc_12 = '12345^Chen^David^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD100800')
        obr.filler_order_number = EI(ei_1='FIL201000')
        obr.universal_service_identifier = CWE(cwe_1='87040-2', cwe_2='Blood culture', cwe_3='LN')
        obr.observation_date_time = '20260509090000'
        obr.obr_16 = '12345^Chen^David^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511113000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bacteria identified', cwe_3='LN')
        obx.obx_5 = 'No growth^^L'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='19146-0', cwe_2='Reference lab', cwe_3='LN')
        obx_2.obx_5 = 'Aerobic bottle: No growth after 5 days incubation.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
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
    """ Based on live/ca/ca-oracle-health.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='AHS_HOSP')
        msh.receiving_application = HD(hd_1='SCHED_RECV')
        msh.receiving_facility = HD(hd_1='OR_SYS')
        msh.date_time_of_message = '20260512083000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20260520001')
        sch.appointment_reason = CWE(cwe_1='ELECTIVE', cwe_2='Elective', cwe_3='HL70276')
        sch.appointment_type = CWE(cwe_1='SURGERY', cwe_2='Surgical procedure', cwe_3='HL70277')
        sch.sch_9 = '120'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^120^20260520073000^20260520093000'
        sch.placer_contact_person = XCN(xcn_1='77889', xcn_2='Roy', xcn_3='Francois', xcn_6='Dr.', xcn_8='MD')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='987654321', cx_4='AB_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Leblanc', xpn_2='Marie', xpn_3='Claire')
        pid.date_time_of_birth = '19901115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='238 11 Ave SE', xad_3='Calgary', xad_4='AB', xad_5='T2G 0X8', xad_6='CA')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='OR3', pl_3='1', pl_4='AHS_FOOTHILLS')
        pv1.attending_doctor = XCN(xcn_1='77889', xcn_2='Roy', xcn_3='Francois', xcn_6='Dr.', xcn_8='MD')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='KNEE_ARTHRO', cwe_2='Knee Arthroscopy', cwe_3='LOCAL')
        ais.start_date_time = '20260520073000'
        ais.start_date_time_offset = '0'
        ais.start_date_time_offset_units = CNE(cne_1='MIN')
        ais.duration = '120'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='77889', xcn_2='Roy', xcn_3='Francois', xcn_6='Dr.', xcn_8='MD')
        aip.start_date_time_offset_units = CNE(cne_1='20260520073000')
        aip.duration = '0'
        aip.duration_units = CNE(cne_1='MIN')
        aip.allow_substitution_code = CWE(cwe_1='120')
        aip.filler_status_code = CWE(cwe_1='MIN')

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.personnel_resource = personnel_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/ca/ca-oracle-health.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='SUNNYBROOK_HIS')
        msh.receiving_application = HD(hd_1='DOC_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260511160000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260511160000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7812345678', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Thompson', xpn_2='Margaret', xpn_3='Anne', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2075 Bayview Ave', xad_3='Toronto', xad_4='ON', xad_5='M4N 3M5', xad_6='CA')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4EAST', pl_2='401', pl_3='A', pl_4='SUNNYBROOK')
        pv1.attending_doctor = XCN(xcn_1='12345', xcn_2='Chen', xcn_3='David', xcn_6='Dr.', xcn_8='MD')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='CN', cwe_2='Consultation Note', cwe_3='HL70270')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260511150000'
        txa.origination_date_time = '20260511160000'
        txa.transcriptionist_code_name = XCN(xcn_1='67890', xcn_2='Patel', xcn_3='Anita', xcn_6='Dr.', xcn_8='MD')
        txa.parent_document_number = EI(ei_1='DOC3456790')
        txa.document_availability_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='CN', cwe_2='Consultation Note Text', cwe_3='LOCAL')
        obx.obx_5 = (
            'Consultation requested for management of new-onset atrial fibrillation in setting of pneumonia. Rate control with metoprolol recommended. An'
            'ticoagulation to be addressed after acute infection resolved.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.txa = txa
        msg.observation = observation

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
    """ Based on live/ca/ca-oracle-health.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='SUNNYBROOK_HIS')
        msh.receiving_application = HD(hd_1='CARDIO_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260510144500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7812345678', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Thompson', xpn_2='Margaret', xpn_3='Anne', xpn_5='Mrs.')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2075 Bayview Ave', xad_3='Toronto', xad_4='ON', xad_5='M4N 3M5', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD100900')
        orc.filler_order_number = EI(ei_1='FIL201100')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510140000'
        orc.orc_12 = '12345^Chen^David^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD100900')
        obr.filler_order_number = EI(ei_1='FIL201100')
        obr.universal_service_identifier = CWE(cwe_1='93000-1', cwe_2='Electrocardiogram', cwe_3='LN')
        obr.observation_date_time = '20260510140000'
        obr.obr_16 = '12345^Chen^David^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='IMG', cwe_2='ECG Tracing', cwe_3='MILLENNIUM')
        obx.obx_5 = (
            '^IM^TIFF^Base64^SUkqAAgAAAAIAAABAwABAAAAgAcAAAEBAwABAAAAXAUAAAIBAwABAAAAAQAAAwEDAAEAAAABAAAABgEDAAEAAAACAAAAEQEEAAEAAAAIAAAAFQEDAAEAAAABAAAAFgED'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='93000-1', cwe_2='ECG Interpretation', cwe_3='LN')
        obx_2.obx_5 = 'Normal sinus rhythm. Rate 78 bpm. Normal axis. No ST changes. QTc 420 ms.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
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
    """ Based on live/ca/ca-oracle-health.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='AHS_HOSP')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260511093000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='123456789', cx_4='AB_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='MacDonald', xpn_2='James', xpn_3='Robert')
        pid.date_time_of_birth = '19750823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='14520 Stony Plain Rd NW', xad_3='Edmonton', xad_4='AB', xad_5='T5N 3Z4', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD101000')
        orc.filler_order_number = EI(ei_1='FIL201200')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260511070000'
        orc.orc_12 = '33445^Singh^Harpreet^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD101000')
        obr.filler_order_number = EI(ei_1='FIL201200')
        obr.universal_service_identifier = CWE(cwe_1='24356-8', cwe_2='Urinalysis complete', cwe_3='LN')
        obr.observation_date_time = '20260511070000'
        obr.obr_16 = '33445^Singh^Harpreet^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='5767-9', cwe_2='Appearance', cwe_3='LN')
        obx.obx_5 = 'Clear^^L'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CWE'
        obx_2.observation_identifier = CWE(cwe_1='5778-6', cwe_2='Color', cwe_3='LN')
        obx_2.obx_5 = 'Yellow^^L'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2756-5', cwe_2='pH', cwe_3='LN')
        obx_3.obx_5 = '6.0'
        obx_3.reference_range = '5.0-8.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2965-2', cwe_2='Specific gravity', cwe_3='LN')
        obx_4.obx_5 = '1.015'
        obx_4.reference_range = '1.005-1.030'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CWE'
        obx_5.observation_identifier = CWE(cwe_1='5792-7', cwe_2='Glucose UA', cwe_3='LN')
        obx_5.obx_5 = 'Negative^^L'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'CWE'
        obx_6.observation_identifier = CWE(cwe_1='20405-7', cwe_2='Leukocytes UA', cwe_3='LN')
        obx_6.obx_5 = 'Negative^^L'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'CWE'
        obx_7.observation_identifier = CWE(cwe_1='5802-4', cwe_2='Nitrite UA', cwe_3='LN')
        obx_7.obx_5 = 'Negative^^L'
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3
        order_observation.observation_4 = observation_4
        order_observation.observation_5 = observation_5
        order_observation.observation_6 = observation_6
        order_observation.observation_7 = observation_7

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
