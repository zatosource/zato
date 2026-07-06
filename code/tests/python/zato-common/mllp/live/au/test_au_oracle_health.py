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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA03NextOfKin, AdtA05NextOfKin, AdtA39Patient, MdmT02Observation, OrmO01Order, \
    OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, \
    OruR01Visit, SiuS12GeneralResource, SiuS12LocationResource, SiuS12Patient, SiuS12PersonnelResource, SiuS12Resources
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, REF_I12, SIU_S12
from zato.hl7v2.v2_9.segments import AIG, AIL, AIP, DG1, EVN, IN1, MRG, MSH, NK1, OBR, OBX, ORC, PID, PRD, PV1, PV2, RF1, RGS, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('au', 'au-oracle-health.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/au/au-oracle-health.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='ROYAL_ADELAIDE')
        msh.receiving_application = HD(hd_1='OACIS')
        msh.receiving_facility = HD(hd_1='SA_HEALTH')
        msh.date_time_of_message = '20260509083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509083000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='MRN445921', cx_4='RAH', cx_5='MR'),
            CX(cx_1='8003608833357361', cx_4='AUSHIC', cx_5='NI'),
            CX(cx_1='32788511952', cx_4='AUSHIC', cx_5='MC'),
        ]
        pid.patient_name = XPN(xpn_1='Thompson', xpn_2='Sarah', xpn_3='Jane', xpn_5='Mrs')
        pid.date_time_of_birth = '19780314'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='42 Hutt Street', xad_3='Adelaide', xad_4='SA', xad_5='5000', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^+61882231456'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '307111942H'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Thompson', xpn_2='David', xpn_3='Michael')
        nk1.address = XAD(xad_2='PRN', xad_3='PH', xad_4='+61883345678')
        nk1.nk1_6 = 'NOK'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4WEST', pl_2='RM412', pl_3='BED01', pl_4='RAH', pl_8='4 West General')
        pv1.attending_doctor = XCN(xcn_1='PRV40012', xcn_2="O'Brien", xcn_3='Fiona', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='PRV40012', xcn_2="O'Brien", xcn_3='Fiona', xcn_6='Dr')
        pv1.visit_number = CX(cx_1='VN90001234')
        pv1.pending_location = PL(pl_1='20260509083000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Acute exacerbation of asthma')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='MCARE')
        in1.insurance_company_id = CX(cx_1='MEDICARE_AU')
        in1.insurance_company_name = XON(xon_1='Medicare Australia')
        in1.insurance_company_address = XAD(xad_1='GPO Box 9822', xad_3='Adelaide', xad_4='SA', xad_5='5001', xad_6='AUS')
        in1.insureds_address = XAD(xad_1='32788511952')
        in1.insureds_administrative_sex = CWE(cwe_1='AUS')

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
        msg.pv2 = pv2
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
    """ Based on live/au/au-oracle-health.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='FLINDERS_MC')
        msh.receiving_application = HD(hd_1='OACIS')
        msh.receiving_facility = HD(hd_1='SA_HEALTH')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260509110000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN556032', cx_4='FMC', cx_5='MR'), CX(cx_1='8003608833468472', cx_4='AUSHIC', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='Nguyen', xpn_2='Thanh', xpn_3='Minh', xpn_5='Mr')
        pid.date_time_of_birth = '19650821'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='18 Jetty Road', xad_3='Glenelg', xad_4='SA', xad_5='5045', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^+61884567890'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='RM03', pl_3='BED01', pl_4='FMC', pl_8='Intensive Care')
        pv1.attending_doctor = XCN(xcn_1='PRV50023', xcn_2='Kaplan', xcn_3='Raymond', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='PRV50023', xcn_2='Kaplan', xcn_3='Raymond', xcn_6='Dr')
        pv1.visit_number = CX(cx_1='VN90002345')
        pv1.pending_location = PL(pl_1='20260509110000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Post-operative cardiac monitoring')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/au/au-oracle-health.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='ROYAL_CHILDRENS')
        msh.receiving_application = HD(hd_1='POWERCHART')
        msh.receiving_facility = HD(hd_1='RCH_MEL')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260509140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='MRN667143', cx_4='RCH', cx_5='MR'),
            CX(cx_1='8003608833579583', cx_4='AUSHIC', cx_5='NI'),
            CX(cx_1='21677823451', cx_4='AUSHIC', cx_5='MC'),
        ]
        pid.patient_name = XPN(xpn_1='Williams', xpn_2='Olivia', xpn_3='Grace')
        pid.date_time_of_birth = '20180612'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='7 Lygon Street', xad_3='Carlton', xad_4='VIC', xad_5='3053', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^+61393456789'
        pid.marital_status = CWE(cwe_1='S')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Williams', xpn_2='Rebecca', xpn_3='Louise')
        nk1.address = XAD(xad_2='PRN', xad_3='PH', xad_4='+61412345678')
        nk1.nk1_6 = 'MTH'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA03NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3SOUTH', pl_2='RM305', pl_3='BED02', pl_4='RCH', pl_8='3 South Paediatrics')
        pv1.attending_doctor = XCN(xcn_1='PRV60034', xcn_2='Chen', xcn_3='Wei-Lin', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='PED')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='PRV60034', xcn_2='Chen', xcn_3='Wei-Lin', xcn_6='Dr')
        pv1.visit_number = CX(cx_1='VN90003456')
        pv1.diet_type = CWE(cwe_1='20260507120000')
        pv1.current_patient_balance = '20260509140000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Acute bronchiolitis')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J21.0', cwe_2='Acute bronchiolitis due to respiratory syncytial virus', cwe_3='I10')
        dg1.diagnosis_date_time = '20260507'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.pv2 = pv2
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
    """ Based on live/au/au-oracle-health.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FIRSTNET')
        msh.sending_facility = HD(hd_1='PRINCESS_ALEX')
        msh.receiving_application = HD(hd_1='MILLENNIUM')
        msh.receiving_facility = HD(hd_1='QLD_HEALTH')
        msh.date_time_of_message = '20260509060000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260509060000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='MRN778254', cx_4='PAH', cx_5='MR'),
            CX(cx_1='8003608833680694', cx_4='AUSHIC', cx_5='NI'),
            CX(cx_1='43566934562', cx_4='AUSHIC', cx_5='MC'),
        ]
        pid.patient_name = XPN(xpn_1='Brown', xpn_2='James', xpn_3='Robert', xpn_5='Mr')
        pid.date_time_of_birth = '19910427'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='155 Ipswich Road', xad_3='Woolloongabba', xad_4='QLD', xad_5='4102', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^+61732109876'
        pid.marital_status = CWE(cwe_1='S')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='TRIAGE', pl_3='BAY03', pl_4='PAH', pl_8='Emergency')
        pv1.attending_doctor = XCN(xcn_1='PRV70045', xcn_2='Patel', xcn_3='Sanjay', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='EM')
        pv1.admit_source = CWE(cwe_1='5')
        pv1.admitting_doctor = XCN(xcn_1='PRV70045', xcn_2='Patel', xcn_3='Sanjay', xcn_6='Dr')
        pv1.visit_number = CX(cx_1='VN90004567')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Chest pain - to be investigated')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/au/au-oracle-health.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='WESTMEAD')
        msh.receiving_application = HD(hd_1='POWERCHART')
        msh.receiving_facility = HD(hd_1='WSLHD')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260509150000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='MRN889365', cx_4='WMD', cx_5='MR'),
            CX(cx_1='8003608833791705', cx_4='AUSHIC', cx_5='NI'),
            CX(cx_1='54455845673', cx_4='AUSHIC', cx_5='MC'),
        ]
        pid.patient_name = XPN(xpn_1='Kowalski', xpn_2='Maria', xpn_3='Anna', xpn_5='Ms')
        pid.date_time_of_birth = '19850916'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='23 Church Street', xad_3='Parramatta', xad_4='NSW', xad_5='2150', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^+61298765432~^PRN^CP^+61422334455'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6NORTH', pl_2='RM610', pl_3='BED03', pl_4='WMD', pl_8='6 North Surgical')
        pv1.attending_doctor = XCN(xcn_1='PRV80056', xcn_2='Singh', xcn_3='Gurpreet', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='SUR')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Kowalski', xpn_2='Tomasz', xpn_3='Jan')
        nk1.address = XAD(xad_2='PRN', xad_3='PH', xad_4='+61423456789')
        nk1.nk1_6 = 'SPO'

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
    """ Based on live/au/au-oracle-health.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNERPM')
        msh.sending_facility = HD(hd_1='MATER_HOSP')
        msh.receiving_application = HD(hd_1='MILLENNIUM')
        msh.receiving_facility = HD(hd_1='MATER_BNE')
        msh.date_time_of_message = '20260509091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20260509091500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN990476', cx_4='MATER', cx_5='MR'), CX(cx_1='8003608833802816', cx_4='AUSHIC', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='Mitchell', xpn_2='Liam', xpn_3='Patrick', xpn_5='Mr')
        pid.date_time_of_birth = '20000803'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='88 Stanley Street', xad_3='South Brisbane', xad_4='QLD', xad_5='4101', xad_6='AUS')
        pid.pid_13 = '^PRN^CP^+61478901234'
        pid.marital_status = CWE(cwe_1='S')

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid

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
    """ Based on live/au/au-oracle-health.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNERPM')
        msh.sending_facility = HD(hd_1='ROYAL_PERTH')
        msh.receiving_application = HD(hd_1='MILLENNIUM')
        msh.receiving_facility = HD(hd_1='WA_HEALTH')
        msh.date_time_of_message = '20260509102000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260509102000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='MRN101587', cx_4='RPH', cx_5='MR'),
            CX(cx_1='8003608833913927', cx_4='AUSHIC', cx_5='NI'),
            CX(cx_1='65344756784', cx_4='AUSHIC', cx_5='MC'),
        ]
        pid.patient_name = XPN(xpn_1='Campbell', xpn_2='Angus', xpn_3='David', xpn_5='Mr')
        pid.date_time_of_birth = '19721105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='12 Hay Street', xad_3='Perth', xad_4='WA', xad_5='6000', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^+61892345678~^PRN^CP^+61409876543'
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Campbell', xpn_2='Jessica', xpn_3='Maree')
        nk1.address = XAD(xad_2='PRN', xad_3='CP', xad_4='+61431234567')
        nk1.nk1_6 = 'SPO'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin

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
    """ Based on live/au/au-oracle-health.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNERPM')
        msh.sending_facility = HD(hd_1='ROYAL_HOBART')
        msh.receiving_application = HD(hd_1='MILLENNIUM')
        msh.receiving_facility = HD(hd_1='TAS_HEALTH')
        msh.date_time_of_message = '20260509130000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260509130000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN212698', cx_4='RHH', cx_5='MR'), CX(cx_1='8003608834024038', cx_4='AUSHIC', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='Taylor', xpn_2='Emily', xpn_3='Rose', xpn_5='Ms')
        pid.date_time_of_birth = '19930217'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='5 Salamanca Place', xad_3='Hobart', xad_4='TAS', xad_5='7000', xad_6='AUS')
        pid.pid_13 = '^PRN^CP^+61436789012'
        pid.marital_status = CWE(cwe_1='S')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='MRN999888', cx_4='RHH', cx_5='MR')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='2EAST', pl_2='RM204', pl_3='BED01', pl_4='RHH', pl_8='2 East Medical')
        pv1.attending_doctor = XCN(xcn_1='PRV90067', xcn_2='Burke', xcn_3='Patrick', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='MED')

        # .. build the PATIENT group ..
        patient = AdtA39Patient()
        patient.pid = pid
        patient.mrg = mrg
        patient.pv1 = pv1

        # .. assemble the full message ..
        msg = ADT_A39()
        msg.msh = msh
        msg.evn = evn
        msg.patient = patient

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
    """ Based on live/au/au-oracle-health.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='POWERCHART')
        msh.sending_facility = HD(hd_1='JOHN_HUNTER')
        msh.receiving_application = HD(hd_1='PATHLAB')
        msh.receiving_facility = HD(hd_1='HUNTER_PATH')
        msh.date_time_of_message = '20260509071500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='MRN323709', cx_4='JHH', cx_5='MR'),
            CX(cx_1='8003608834135149', cx_4='AUSHIC', cx_5='NI'),
            CX(cx_1='76233667895', cx_4='AUSHIC', cx_5='MC'),
        ]
        pid.patient_name = XPN(xpn_1='Robinson', xpn_2='Daniel', xpn_3='Scott', xpn_5='Mr')
        pid.date_time_of_birth = '19880630'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='31 Hunter Street', xad_3='Newcastle', xad_4='NSW', xad_5='2300', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^+61249876543'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5WEST', pl_2='RM506', pl_3='BED02', pl_4='JHH', pl_8='5 West Haematology')
        pv1.attending_doctor = XCN(xcn_1='PRV11078', xcn_2='Lee', xcn_3='Soo-Young', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='HEM')

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
        orc.placer_order_number = EI(ei_1='ORD50001', ei_2='POWERCHART')
        orc.orc_12 = 'PRV11078^Lee^Soo-Young^^^Dr'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD50001', ei_2='POWERCHART')
        obr.universal_service_identifier = CWE(cwe_1='26604007', cwe_2='Complete blood count', cwe_3='SCT')
        obr.observation_date_time = '20260509071500'
        obr.obr_15 = 'PRV11078^Lee^Soo-Young^^^Dr'
        obr.result_status = '1^^^20260509071500^^R'

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
    """ Based on live/au/au-oracle-health.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='POWERCHART')
        msh.sending_facility = HD(hd_1='CONCORD_HOSP')
        msh.receiving_application = HD(hd_1='RADIS')
        msh.receiving_facility = HD(hd_1='SLHD_RAD')
        msh.date_time_of_message = '20260509082000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN434810', cx_4='CRGH', cx_5='MR'), CX(cx_1='8003608834246250', cx_4='AUSHIC', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='Garcia', xpn_2='Isabella', xpn_3='Sofia', xpn_5='Ms')
        pid.date_time_of_birth = '19750412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='9 Burwood Road', xad_3='Concord', xad_4='NSW', xad_5='2137', xad_6='AUS')
        pid.pid_13 = '^PRN^CP^+61415678901'
        pid.marital_status = CWE(cwe_1='D')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='RESUS', pl_3='BAY01', pl_4='CRGH', pl_8='Emergency')
        pv1.attending_doctor = XCN(xcn_1='PRV22089', xcn_2='Adams', xcn_3='Joanne', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='EM')

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
        orc.placer_order_number = EI(ei_1='ORD60002', ei_2='POWERCHART')
        orc.orc_12 = 'PRV22089^Adams^Joanne^^^Dr'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD60002', ei_2='POWERCHART')
        obr.universal_service_identifier = CWE(cwe_1='399208008', cwe_2='Chest X-ray PA', cwe_3='SCT')
        obr.observation_date_time = '20260509082000'
        obr.obr_15 = 'PRV22089^Adams^Joanne^^^Dr'
        obr.result_status = '1^^^20260509082000^^S'

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
    """ Based on live/au/au-oracle-health.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='AUSTIN_HEALTH')
        msh.receiving_application = HD(hd_1='POWERCHART')
        msh.receiving_facility = HD(hd_1='AUSTIN_MEL')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='MRN545921', cx_4='AUSTIN', cx_5='MR'),
            CX(cx_1='8003608834357361', cx_4='AUSHIC', cx_5='NI'),
            CX(cx_1='87122578906', cx_4='AUSHIC', cx_5='MC'),
        ]
        pid.patient_name = XPN(xpn_1='Phan', xpn_2='Thi', xpn_3='Ngoc', xpn_5='Ms')
        pid.date_time_of_birth = '19690103'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='14 Burgundy Street', xad_3='Heidelberg', xad_4='VIC', xad_5='3084', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^+61394567890'
        pid.marital_status = CWE(cwe_1='W')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='7NORTH', pl_2='RM712', pl_3='BED01', pl_4='AUSTIN', pl_8='7 North General')
        pv1.attending_doctor = XCN(xcn_1='PRV33090', xcn_2='Kelly', xcn_3='Brendan', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='GEN')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD50001', ei_2='POWERCHART')
        orc.filler_order_number = EI(ei_1='LAB80001', ei_2='PATHLAB')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD50001', ei_2='POWERCHART')
        obr.filler_order_number = EI(ei_1='LAB80001', ei_2='PATHLAB')
        obr.universal_service_identifier = CWE(cwe_1='26604007', cwe_2='Complete blood count', cwe_3='SCT')
        obr.observation_date_time = '20260509071500'
        obr.obr_14 = '20260509080000'
        obr.obr_15 = 'Blood^Whole blood'
        obr.obr_16 = 'PRV33090^Kelly^Brendan^^^Dr'
        obr.results_rpt_status_chng_date_time = '20260509100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx.obx_5 = '128'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '120-160'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509093000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocytes', cwe_3='LN')
        obx_2.obx_5 = '7.2'
        obx_2.units = CWE(cwe_1='x10*9/L')
        obx_2.reference_range = '4.0-11.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509093000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelets', cwe_3='LN')
        obx_3.obx_5 = '245'
        obx_3.units = CWE(cwe_1='x10*9/L')
        obx_3.reference_range = '150-400'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509093000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrocytes', cwe_3='LN')
        obx_4.obx_5 = '4.35'
        obx_4.units = CWE(cwe_1='x10*12/L')
        obx_4.reference_range = '3.80-5.20'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509093000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrit', cwe_3='LN')
        obx_5.obx_5 = '0.39'
        obx_5.units = CWE(cwe_1='L/L')
        obx_5.reference_range = '0.36-0.46'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509093000'

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
    """ Based on live/au/au-oracle-health.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='GOLD_COAST_UH')
        msh.receiving_application = HD(hd_1='POWERCHART')
        msh.receiving_facility = HD(hd_1='GC_HEALTH')
        msh.date_time_of_message = '20260509113000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN657032', cx_4='GCUH', cx_5='MR'), CX(cx_1='8003608834468472', cx_4='AUSHIC', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='Walker', xpn_2='Thomas', xpn_3='James', xpn_5='Mr')
        pid.date_time_of_birth = '19550718'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='27 Cavill Avenue', xad_3='Surfers Paradise', xad_4='QLD', xad_5='4217', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^+61755432109'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3EAST', pl_2='RM310', pl_3='BED03', pl_4='GCUH', pl_8='3 East Renal')
        pv1.attending_doctor = XCN(xcn_1='PRV44101', xcn_2='Murray', xcn_3='Alison', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='REN')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD70003', ei_2='POWERCHART')
        orc.filler_order_number = EI(ei_1='LAB90002', ei_2='LABCORE')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD70003', ei_2='POWERCHART')
        obr.filler_order_number = EI(ei_1='LAB90002', ei_2='LABCORE')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='Basic metabolic panel', cwe_3='LN')
        obr.observation_date_time = '20260509080000'
        obr.obr_14 = '20260509085000'
        obr.obr_15 = 'Blood^Serum'
        obr.obr_16 = 'PRV44101^Murray^Alison^^^Dr'
        obr.results_rpt_status_chng_date_time = '20260509113000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx.obx_5 = '139'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '135-145'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_2.obx_5 = '4.5'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '3.5-5.2'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2075-0', cwe_2='Chloride', cwe_3='LN')
        obx_3.obx_5 = '102'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '95-110'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_4.obx_5 = '12.8'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '2.5-8.0'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_5.obx_5 = '185'
        obx_5.units = CWE(cwe_1='umol/L')
        obx_5.reference_range = '60-110'
        obx_5.interpretation_codes = CWE(cwe_1='HH')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='33914-3', cwe_2='eGFR', cwe_3='LN')
        obx_6.obx_5 = '28'
        obx_6.units = CWE(cwe_1='mL/min/1.73m2')
        obx_6.reference_range = '>90'
        obx_6.interpretation_codes = CWE(cwe_1='LL')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

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
    """ Based on live/au/au-oracle-health.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='LIVERPOOL_HOSP')
        msh.receiving_application = HD(hd_1='POWERCHART')
        msh.receiving_facility = HD(hd_1='SWSLHD')
        msh.date_time_of_message = '20260509120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='MRN768143', cx_4='LIV', cx_5='MR'),
            CX(cx_1='8003608834579583', cx_4='AUSHIC', cx_5='NI'),
            CX(cx_1='98011489017', cx_4='AUSHIC', cx_5='MC'),
        ]
        pid.patient_name = XPN(xpn_1='Ahmed', xpn_2='Fatima', xpn_3='Zahra', xpn_5='Mrs')
        pid.date_time_of_birth = '19820225'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='61 Bigge Street', xad_3='Liverpool', xad_4='NSW', xad_5='2170', xad_6='AUS')
        pid.pid_13 = '^PRN^CP^+61423456789'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIOL', pl_2='RM01', pl_3='SCAN02', pl_4='LIV', pl_8='Radiology')
        pv1.attending_doctor = XCN(xcn_1='PRV55112', xcn_2='Jones', xcn_3='Christopher', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='RAD')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD80004', ei_2='POWERCHART')
        orc.filler_order_number = EI(ei_1='RAD70003', ei_2='RADIS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD80004', ei_2='POWERCHART')
        obr.filler_order_number = EI(ei_1='RAD70003', ei_2='RADIS')
        obr.universal_service_identifier = CWE(cwe_1='399208008', cwe_2='Chest X-ray PA', cwe_3='SCT')
        obr.observation_date_time = '20260509082000'
        obr.obr_14 = '20260509090000'
        obr.obr_16 = 'PRV55112^Jones^Christopher^^^Dr'
        obr.results_rpt_status_chng_date_time = '20260509120000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='399208008', cwe_2='Chest X-ray PA', cwe_3='SCT')
        obx.obx_5 = (
            'Findings: Heart size normal. Lungs clear bilaterally. No pleural effusion. No pneumothorax. Mediastinal contours normal.\\.br\\Impression: Nor'
            'mal chest X-ray.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509115000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Radiology Report PDF', cwe_3='AUSPDI')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMg'
            'MCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5'
            'IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo='
        )
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
    """ Based on live/au/au-oracle-health.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='ROYAL_NORTH_SHORE')
        msh.receiving_application = HD(hd_1='POWERCHART')
        msh.receiving_facility = HD(hd_1='NSLHD')
        msh.date_time_of_message = '20260509090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='SCH40001', ei_2='MILLENNIUM')
        sch.filler_appointment_id = EI(ei_1='APT40001', ei_2='MILLENNIUM')
        sch.schedule_id = CWE(cwe_1='CONSULT')
        sch.event_reason = CWE(cwe_1='FOLLOWUP', cwe_2='Follow-up Consultation')
        sch.appointment_reason = CWE(cwe_2='Follow-up post surgery')
        sch.appointment_type = CWE(cwe_1='CONSULT')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^30^20260520093000^20260520100000'
        sch.filler_contact_person = XCN(xcn_1='PRV66123', xcn_2='Walsh', xcn_3='Margaret', xcn_6='Dr')
        sch.entered_by_person = XCN(xcn_1='PRV66123', xcn_2='Walsh', xcn_3='Margaret', xcn_6='Dr')
        sch.filler_status_code = CWE(cwe_1='Booked')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN879254', cx_4='RNS', cx_5='MR'), CX(cx_1='8003608834680694', cx_4='AUSHIC', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='Harris', xpn_2='Chloe', xpn_3='Elizabeth', xpn_5='Ms')
        pid.date_time_of_birth = '19950814'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='3 Pacific Highway', xad_3='St Leonards', xad_4='NSW', xad_5='2065', xad_6='AUS')
        pid.pid_13 = '^PRN^CP^+61402345678'
        pid.marital_status = CWE(cwe_1='S')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORTHO_OPD', pl_2='CLINIC3', pl_4='RNS', pl_8='Orthopaedic Outpatients')
        pv1.attending_doctor = XCN(xcn_1='PRV66123', xcn_2='Walsh', xcn_3='Margaret', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='ORT')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.segment_action_code = 'A'

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.segment_action_code = 'A'
        aig.resource_id = CWE(cwe_1='PRV66123', cwe_2='Walsh', cwe_3='Margaret', cwe_6='Dr')
        aig.resource_type = CWE(cwe_1='D')

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SiuS12GeneralResource()
        general_resource.aig = aig

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'A'
        ail.location_resource_id = PL(pl_1='ORTHO_OPD', pl_2='CLINIC3', pl_4='RNS')
        ail.location_type_ail = CWE(cwe_2='Orthopaedic Outpatients')
        ail.start_date_time = '20260520093000'
        ail.duration = '30'
        ail.duration_units = CNE(cne_1='min')
        ail.filler_status_code = CWE(cwe_1='Booked')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.personnel_resource_id = XCN(xcn_1='PRV66123', xcn_2='Walsh', xcn_3='Margaret', xcn_6='Dr')
        aip.resource_type = CWE(cwe_1='D')
        aip.start_date_time = '20260520093000'
        aip.duration = '30'
        aip.duration_units = CNE(cne_1='min')
        aip.filler_status_code = CWE(cwe_1='Booked')

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.general_resource = general_resource
        resources.location_resource = location_resource
        resources.personnel_resource = personnel_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/au/au-oracle-health.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='DARWIN_HOSP')
        msh.receiving_application = HD(hd_1='POWERCHART')
        msh.receiving_facility = HD(hd_1='NT_HEALTH')
        msh.date_time_of_message = '20260509143000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='SCH50002', ei_2='MILLENNIUM')
        sch.filler_appointment_id = EI(ei_1='APT50002', ei_2='MILLENNIUM')
        sch.schedule_id = CWE(cwe_1='SURGERY')
        sch.event_reason = CWE(cwe_1='ELECTIVE', cwe_2='Elective Surgery')
        sch.appointment_reason = CWE(cwe_2='Right total knee replacement')
        sch.appointment_type = CWE(cwe_1='SURGERY')
        sch.sch_9 = '120'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^120^20260604080000^20260604100000'
        sch.filler_contact_person = XCN(xcn_1='PRV77134', xcn_2='Dixon', xcn_3='Stuart', xcn_6='Dr')
        sch.entered_by_person = XCN(xcn_1='PRV77134', xcn_2='Dixon', xcn_3='Stuart', xcn_6='Dr')
        sch.filler_status_code = CWE(cwe_1='Booked')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN980365', cx_4='RDH', cx_5='MR'), CX(cx_1='8003608834791705', cx_4='AUSHIC', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='McDonald', xpn_2='Bruce', xpn_3='William', xpn_5='Mr')
        pid.date_time_of_birth = '19580322'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='44 Mitchell Street', xad_3='Darwin', xad_4='NT', xad_5='0800', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^+61889012345'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='OT3', pl_4='RDH', pl_8='Operating Theatre 3')
        pv1.attending_doctor = XCN(xcn_1='PRV77134', xcn_2='Dixon', xcn_3='Stuart', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='ORT')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.segment_action_code = 'A'

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.segment_action_code = 'A'
        aig.resource_id = CWE(cwe_1='PRV77134', cwe_2='Dixon', cwe_3='Stuart', cwe_6='Dr')
        aig.resource_type = CWE(cwe_1='D')

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SiuS12GeneralResource()
        general_resource.aig = aig

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'A'
        ail.location_resource_id = PL(pl_1='SURG', pl_2='OT3', pl_4='RDH')
        ail.location_type_ail = CWE(cwe_2='Operating Theatre 3')
        ail.start_date_time = '20260604080000'
        ail.duration = '120'
        ail.duration_units = CNE(cne_1='min')
        ail.filler_status_code = CWE(cwe_1='Booked')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.personnel_resource_id = XCN(xcn_1='PRV77134', xcn_2='Dixon', xcn_3='Stuart', xcn_6='Dr')
        aip.resource_type = CWE(cwe_1='D')
        aip.start_date_time = '20260604080000'
        aip.duration = '120'
        aip.duration_units = CNE(cne_1='min')
        aip.filler_status_code = CWE(cwe_1='Booked')

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.general_resource = general_resource
        resources.location_resource = location_resource
        resources.personnel_resource = personnel_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/au/au-oracle-health.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='CANBERRA_HOSP')
        msh.receiving_application = HD(hd_1='SECMSG')
        msh.receiving_facility = HD(hd_1='ACT_HEALTH')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260509160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='MRN091476', cx_4='TCH', cx_5='MR'),
            CX(cx_1='8003608834902816', cx_4='AUSHIC', cx_5='NI'),
            CX(cx_1='10988400128', cx_4='AUSHIC', cx_5='MC'),
        ]
        pid.patient_name = XPN(xpn_1='Evans', xpn_2='Sophie', xpn_3='Marie', xpn_5='Ms')
        pid.date_time_of_birth = '19870619'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='15 Bunda Street', xad_3='Canberra', xad_4='ACT', xad_5='2601', xad_6='AUS')
        pid.pid_13 = '^PRN^CP^+61411234567'
        pid.marital_status = CWE(cwe_1='S')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4WEST', pl_2='RM402', pl_3='BED02', pl_4='TCH', pl_8='4 West General')
        pv1.attending_doctor = XCN(xcn_1='PRV88145', xcn_2='Barrett', xcn_3='Louise', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='GEN')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Discharge Summary')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260509160000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='PRV88145', xcn_2='Barrett', xcn_3='Louise', xcn_6='Dr')
        txa.transcription_date_time = '20260509160000'
        txa.unique_document_number = EI(ei_1='DOC90001')
        txa.document_confidentiality_status = 'AU'
        txa.document_storage_status = 'AV'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='18842-5', cwe_2='Discharge Summary', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMg'
            'MCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5'
            'IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo='
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
    """ Based on live/au/au-oracle-health.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='ROYAL_BRIS')
        msh.receiving_application = HD(hd_1='POWERCHART')
        msh.receiving_facility = HD(hd_1='QLD_HEALTH')
        msh.date_time_of_message = '20260509093000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260509093000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN202587', cx_4='RBWH', cx_5='MR'), CX(cx_1='8003608835013927', cx_4='AUSHIC', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='Clark', xpn_2='Ethan', xpn_3='James', xpn_5='Mr')
        pid.date_time_of_birth = '19480511'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='22 Bowen Bridge Road', xad_3='Herston', xad_4='QLD', xad_5='4006', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^+61732198765'
        pid.marital_status = CWE(cwe_1='W')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='WOUND', pl_2='RM108', pl_3='BED01', pl_4='RBWH', pl_8='Wound Care Unit')
        pv1.attending_doctor = XCN(xcn_1='PRV99156', xcn_2='Lloyd', xcn_3='Catherine', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='SUR')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='WP', cwe_2='Wound Photograph')
        txa.document_content_presentation = 'IM'
        txa.activity_date_time = '20260509093000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='PRV99156', xcn_2='Lloyd', xcn_3='Catherine', xcn_6='Dr')
        txa.transcription_date_time = '20260509093000'
        txa.unique_document_number = EI(ei_1='DOC90002')
        txa.document_confidentiality_status = 'AU'
        txa.document_storage_status = 'AV'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='72170-4', cwe_2='Photographic image', cwe_3='LN')
        obx.obx_5 = (
            '^image^jpeg^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgy'
            'IRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAA'
            'AAAAAAAAAAAAAAD/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AKwA//9k='
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
    """ Based on live/au/au-oracle-health.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='MONASH_MC')
        msh.receiving_application = HD(hd_1='POWERCHART')
        msh.receiving_facility = HD(hd_1='MONASH_HEALTH')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='MRN313698', cx_4='MMC', cx_5='MR'),
            CX(cx_1='8003608835124038', cx_4='AUSHIC', cx_5='NI'),
            CX(cx_1='21866712562', cx_4='AUSHIC', cx_5='MC'),
        ]
        pid.patient_name = XPN(xpn_1="O'Sullivan", xpn_2='Declan', xpn_3='Patrick', xpn_5='Mr')
        pid.date_time_of_birth = '19770809'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='51 Princes Highway', xad_3='Dandenong', xad_4='VIC', xad_5='3175', xad_6='AUS')
        pid.pid_13 = '^PRN^CP^+61398765432'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ID_WARD', pl_2='RM203', pl_3='BED01', pl_4='MMC', pl_8='Infectious Diseases')
        pv1.attending_doctor = XCN(xcn_1='PRV10167', xcn_2='Ramirez', xcn_3='Carlos', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='ID')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD90005', ei_2='POWERCHART')
        orc.filler_order_number = EI(ei_1='LAB10004', ei_2='MICROLAB')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD90005', ei_2='POWERCHART')
        obr.filler_order_number = EI(ei_1='LAB10004', ei_2='MICROLAB')
        obr.universal_service_identifier = CWE(cwe_1='630-4', cwe_2='Bacteria identified', cwe_3='LN')
        obr.observation_date_time = '20260507100000'
        obr.obr_14 = '20260507103000'
        obr.obr_15 = 'Urine^Midstream urine'
        obr.obr_16 = 'PRV10167^Ramirez^Carlos^^^Dr'
        obr.results_rpt_status_chng_date_time = '20260509140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='Bacteria identified', cwe_3='LN')
        obx.obx_5 = '112283007^Escherichia coli^SCT'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509130000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18907-6', cwe_2='Colony count', cwe_3='LN')
        obx_2.obx_5 = '>10*5 CFU/mL'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509130000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Susceptibility - Amoxicillin', cwe_3='LN')
        obx_3.obx_5 = 'Resistant'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509133000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18886-2', cwe_2='Susceptibility - Trimethoprim', cwe_3='LN')
        obx_4.obx_5 = 'Resistant'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509133000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18864-9', cwe_2='Susceptibility - Nitrofurantoin', cwe_3='LN')
        obx_5.obx_5 = 'Sensitive'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509133000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18993-6', cwe_2='Susceptibility - Cefalexin', cwe_3='LN')
        obx_6.obx_5 = 'Sensitive'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509133000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

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
    """ Based on live/au/au-oracle-health.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='ALFRED_HOSP')
        msh.receiving_application = HD(hd_1='POWERCHART')
        msh.receiving_facility = HD(hd_1='ALFRED_HEALTH')
        msh.date_time_of_message = '20260509153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='MRN424709', cx_4='ALFRED', cx_5='MR'),
            CX(cx_1='8003608835235149', cx_4='AUSHIC', cx_5='NI'),
            CX(cx_1='32755623673', cx_4='AUSHIC', cx_5='MC'),
        ]
        pid.patient_name = XPN(xpn_1='Fraser', xpn_2='Malcolm', xpn_3='Andrew', xpn_5='Mr')
        pid.date_time_of_birth = '19610930'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='8 St Kilda Road', xad_3='Melbourne', xad_4='VIC', xad_5='3004', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^+61395678901'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UROL', pl_2='RM505', pl_3='BED01', pl_4='ALFRED', pl_8='Urology Ward')
        pv1.attending_doctor = XCN(xcn_1='PRV21178', xcn_2='Tan', xcn_3='Hong-Wei', xcn_6='Dr')
        pv1.hospital_service = CWE(cwe_1='URO')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD10006', ei_2='POWERCHART')
        orc.filler_order_number = EI(ei_1='LAB20005', ei_2='HISTOPATH')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD10006', ei_2='POWERCHART')
        obr.filler_order_number = EI(ei_1='LAB20005', ei_2='HISTOPATH')
        obr.universal_service_identifier = CWE(cwe_1='11529-5', cwe_2='Surgical pathology', cwe_3='LN')
        obr.observation_date_time = '20260506080000'
        obr.obr_14 = '20260506090000'
        obr.obr_15 = 'Tissue^Prostate biopsy'
        obr.obr_16 = 'PRV21178^Tan^Hong-Wei^^^Dr'
        obr.results_rpt_status_chng_date_time = '20260509153000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='59847-4', cwe_2='Histologic type', cwe_3='LN')
        obx.obx_5 = '399490008^Adenocarcinoma, acinar^SCT'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='44648-4', cwe_2='Primary Gleason pattern', cwe_3='LN')
        obx_2.obx_5 = 'LA12701-5^3^LN'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='44649-2', cwe_2='Secondary Gleason pattern', cwe_3='LN')
        obx_3.obx_5 = 'LA12702-3^4^LN'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='35266-6', cwe_2='Gleason score', cwe_3='LN')
        obx_4.obx_5 = '7'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CE'
        obx_5.observation_identifier = CWE(cwe_1='59776-5', cwe_2='Grade Group', cwe_3='LN')
        obx_5.obx_5 = 'LA25159-9^Grade Group 3^LN'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='44650-0', cwe_2='Cores positive', cwe_3='LN')
        obx_6.obx_5 = '4'
        obx_6.units = CWE(cwe_1='/{total}')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='44651-8', cwe_2='Cores examined', cwe_3='LN')
        obx_7.obx_5 = '12'
        obx_7.units = CWE(cwe_1='/{total}')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='44652-6', cwe_2='Greatest percentage core involvement', cwe_3='LN')
        obx_8.obx_5 = '45'
        obx_8.units = CWE(cwe_1='%')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20260509150000'

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
    """ Based on live/au/au-oracle-health.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='POWERCHART')
        msh.sending_facility = HD(hd_1='WOLLONGONG_HOSP')
        msh.receiving_application = HD(hd_1='MILLENNIUM')
        msh.receiving_facility = HD(hd_1='ISLHD')
        msh.date_time_of_message = '20260509101500'
        msh.message_type = MSG(msg_1='REF', msg_2='I12', msg_3='REF_I12')
        msh.message_control_id = 'MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build RF1 ..
        rf1 = RF1()
        rf1.referral_status = CWE(cwe_1='SS')
        rf1.referral_priority = CWE(cwe_1='RoutineReferral', cwe_2='Routine Referral')
        rf1.referral_category = CWE(cwe_1='20260509')
        rf1.originating_referral_identifier = EI(ei_1='20260709')
        rf1.expiration_date = 'Referral for specialist cardiology review'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='MRN535820', cx_4='WGH', cx_5='MR'),
            CX(cx_1='8003608835346250', cx_4='AUSHIC', cx_5='NI'),
            CX(cx_1='43644534784', cx_4='AUSHIC', cx_5='MC'),
        ]
        pid.patient_name = XPN(xpn_1='Murray', xpn_2='Helen', xpn_3='Patricia', xpn_5='Mrs')
        pid.date_time_of_birth = '19710406'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='19 Crown Street', xad_3='Wollongong', xad_4='NSW', xad_5='2500', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^+61242345678~^PRN^CP^+61418765432'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PRD ..
        prd = PRD()
        prd.provider_role = CWE(cwe_1='RP')
        prd.provider_name = XPN(xpn_1="O'Reilly", xpn_2='Siobhan', xpn_5='Dr')
        prd.provider_address = XAD(xad_1='12 Church Street', xad_3='Wollongong', xad_4='NSW', xad_5='2500', xad_6='AUS')
        prd.provider_communication_information = XTN(xtn_2='WPN', xtn_3='PH', xtn_4='+61242109876')
        prd.preferred_method_of_contact = CWE(cwe_1='PRV32189', cwe_4='AUSHICPR', cwe_5='UPIN')

        # .. build PRD ..
        prd_2 = PRD()
        prd_2.provider_role = CWE(cwe_1='RT')
        prd_2.provider_name = XPN(xpn_1='Kapoor', xpn_2='Ravi', xpn_5='Dr')
        prd_2.provider_address = XAD(xad_1='Suite 4, 88 Crown Street', xad_3='Wollongong', xad_4='NSW', xad_5='2500', xad_6='AUS')
        prd_2.provider_communication_information = XTN(xtn_2='WPN', xtn_3='PH', xtn_4='+61242987654')
        prd_2.preferred_method_of_contact = CWE(cwe_1='PRV43290', cwe_4='AUSHICPR', cwe_5='UPIN')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I10', cwe_2='Essential (primary) hypertension', cwe_3='I10')
        dg1.diagnosis_date_time = '20260401'

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='I48.0', cwe_2='Paroxysmal atrial fibrillation', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20260501'

        # .. assemble the full message ..
        msg = REF_I12()
        msg.msh = msh
        msg.rf1 = rf1
        msg.pid = pid
        msg.extra_segments = [prd, prd_2, dg1, dg1_2]

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
