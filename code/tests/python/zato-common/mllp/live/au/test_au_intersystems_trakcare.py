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
from zato.hl7v2.v2_9.datatypes import CNE, CP, CWE, CX, EI, FC, HD, MOC, MSG, PL, PRL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01NextOfKin, AdtA05NextOfKin, AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, \
    OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, \
    SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A09, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIP, AIS, DG1, EVN, IN1, MRG, MSH, NK1, OBR, OBX, ORC, PD1, PID, PV1, PV2, RGS, RXO, RXR, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('au', 'au-intersystems-trakcare.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/au/au-intersystems-trakcare.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TRAKCARE')
        msh.sending_facility = HD(hd_1='RAH', hd_2='Royal Adelaide Hospital')
        msh.receiving_application = HD(hd_1='OACIS')
        msh.receiving_facility = HD(hd_1='SA_HEALTH')
        msh.date_time_of_message = '20250314091200'
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
        evn.recorded_date_time = '20250314091200'
        evn.operator_id = XCN(xcn_1='JSMITH', xcn_2='Smith', xcn_3='Jane', xcn_6='Dr')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN4401928', cx_4='RAH', cx_5='MR'), CX(cx_1='8901234567', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1="O'BRIEN", xpn_2='Liam', xpn_3='Patrick', xpn_5='Mr')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='14 Hutt Street', xad_3='Adelaide', xad_4='SA', xad_5='5000', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0882231456'
        pid.pid_14 = '^WPN^PH^^^^^0884567890'
        pid.religion = CWE(cwe_1='M')
        pid.pid_20 = '8901234567'
        pid.identity_reliability_code = CWE(cwe_1='N')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4WEST', pl_2='412', pl_3='1', pl_4='RAH', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'CON2345^McGregor^Angus^^^Dr^MBBS'
        pv1.pv1_8 = 'CON2345^McGregor^Angus^^^Dr^MBBS'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'CON2345^McGregor^Angus^^^Dr^MBBS'
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.financial_class = FC(fc_1='SA_PUB')
        pv1.pv1_40 = 'RAH'
        pv1.pending_location = PL(pl_1='A')
        pv1.discharge_date_time = '20250314091200'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Chest pain, ?ACS')
        pv2.estimated_length_of_inpatient_stay = '2'
        pv2.admission_level_of_care_code = CWE(cwe_1='N')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1="O'BRIEN", xpn_2='Mary', xpn_3='Ellen')
        nk1.address = XAD(xad_2='PRN', xad_3='PH', xad_8='0882231456')
        nk1.nk1_5 = '^WPN^PH^^^^^0884567891'
        nk1.contact_role = CWE(cwe_1='NOK')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='MCARE')
        in1.insurance_company_id = CX(cx_1='MEDICARE_AUS')
        in1.insurance_company_name = XON(xon_1='Medicare Australia')
        in1.plan_effective_date = '19580312'
        in1.insureds_relationship_to_patient = CWE(cwe_1="O'BRIEN", cwe_2='Liam', cwe_3='Patrick', cwe_5='Mr')
        in1.insureds_date_of_birth = 'SELF'
        in1.insureds_address = XAD(xad_1='19580312')
        in1.policy_deductible = CP(cp_1='8901234567')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.extra_segments = [nk1, in1]

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACACIA')
        msh.sending_facility = HD(hd_1='FMC', hd_2='Flinders Medical Centre')
        msh.receiving_application = HD(hd_1='OACIS')
        msh.receiving_facility = HD(hd_1='SA_HEALTH')
        msh.date_time_of_message = '20250314143000'
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
        evn.recorded_date_time = '20250314143000'
        evn.operator_id = XCN(xcn_1='RBROWN', xcn_2='Brown', xcn_3='Robert', xcn_6='Nurse')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN5502847', cx_4='FMC', cx_5='MR'), CX(cx_1='2345678901', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='NGUYEN', xpn_2='Thi', xpn_3='Mai', xpn_5='Mrs')
        pid.date_time_of_birth = '19720815'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='27 Brighton Road', xad_3='Glenelg', xad_4='SA', xad_5='5045', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0883761234'
        pid.religion = CWE(cwe_1='M')
        pid.pid_20 = '2345678901'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='ICU03', pl_3='1', pl_4='FMC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='U')
        pv1.pv1_7 = 'CON3456^Patel^Rajesh^^^Dr^MBBS'
        pv1.pv1_8 = 'CON3456^Patel^Rajesh^^^Dr^MBBS'
        pv1.hospital_service = CWE(cwe_1='ICU')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'CON3456^Patel^Rajesh^^^Dr^MBBS'
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.financial_class = FC(fc_1='SA_PUB')
        pv1.pv1_40 = 'FMC'
        pv1.pending_location = PL(pl_1='T')
        pv1.discharge_date_time = '20250312080000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Post-operative monitoring')

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TRAKCARE')
        msh.sending_facility = HD(hd_1='TCH', hd_2='The Canberra Hospital')
        msh.receiving_application = HD(hd_1='ACTPAS')
        msh.receiving_facility = HD(hd_1='ACT_HEALTH')
        msh.date_time_of_message = '20250315101500'
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
        evn.recorded_date_time = '20250315101500'
        evn.operator_id = XCN(xcn_1='KLEE', xcn_2='Lee', xcn_3='Karen', xcn_6='RN')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN6603192', cx_4='TCH', cx_5='MR'), CX(cx_1='3456789012', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='WILLIAMS', xpn_2='Sarah', xpn_3='Jane', xpn_5='Ms')
        pid.date_time_of_birth = '19850621'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='8 Lonsdale Street', xad_3='Braddon', xad_4='ACT', xad_5='2612', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0262491234'
        pid.religion = CWE(cwe_1='S')
        pid.pid_20 = '3456789012'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5SOUTH', pl_2='503', pl_3='1', pl_4='TCH', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'CON4567^Hassan^Fatima^^^Dr^MBBS'
        pv1.pv1_8 = 'CON4567^Hassan^Fatima^^^Dr^MBBS'
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'CON4567^Hassan^Fatima^^^Dr^MBBS'
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.financial_class = FC(fc_1='ACT_PUB')
        pv1.pv1_40 = 'TCH'
        pv1.pending_location = PL(pl_1='A')
        pv1.discharge_date_time = '20250312143000'
        pv1.total_adjustments = '20250315101500'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonia, unspecified', cwe_3='I10')
        dg1.diagnosis_type = CWE(cwe_1='F')

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACACIA')
        msh.sending_facility = HD(hd_1='LMH', hd_2='Lyell McEwin Hospital')
        msh.receiving_application = HD(hd_1='OACIS')
        msh.receiving_facility = HD(hd_1='SA_HEALTH')
        msh.date_time_of_message = '20250316083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250316083000'
        evn.operator_id = XCN(xcn_1='AWHITE', xcn_2='White', xcn_3='Amanda', xcn_6='Admin')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN7714003', cx_4='LMH', cx_5='MR'), CX(cx_1='4567890123', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='KUMAR', xpn_2='Arun', xpn_3='Raj', xpn_5='Mr')
        pid.date_time_of_birth = '19900405'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='3 Peachey Road', xad_3='Davoren Park', xad_4='SA', xad_5='5113', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0882551234'
        pid.religion = CWE(cwe_1='S')
        pid.pid_20 = '4567890123'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD', pl_2='CLINIC4', pl_3='1', pl_4='LMH', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'CON5678^Dixon^Michael^^^Dr^MBBS'
        pv1.preadmit_test_indicator = CWE(cwe_1='OPD')
        pv1.vip_indicator = CWE(cwe_1='1')
        pv1.visit_number = CX(cx_1='CON5678', cx_2='Dixon', cx_3='Michael', cx_6='Dr', cx_7='MBBS')
        pv1.financial_class = FC(fc_1='OUT')
        pv1.courtesy_code = CWE(cwe_1='SA_PUB')
        pv1.pending_location = PL(pl_1='LMH')
        pv1.admit_date_time = 'A'
        pv1.total_charges = '20250316083000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Diabetes follow-up review')

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TRAKCARE')
        msh.sending_facility = HD(hd_1='WCH', hd_2="Women's and Children's Hospital")
        msh.receiving_application = HD(hd_1='OACIS')
        msh.receiving_facility = HD(hd_1='SA_HEALTH')
        msh.date_time_of_message = '20250317110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250317110000'
        evn.operator_id = XCN(xcn_1='MCLARK', xcn_2='Clark', xcn_3='Michelle', xcn_6='Admin')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN8825614', cx_4='WCH', cx_5='MR'), CX(cx_1='5678901234', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='JOHNSON', xpn_2='Emily', xpn_3='Rose', xpn_5='Miss')
        pid.date_time_of_birth = '20180923'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='42 King William Road', xad_3='Unley', xad_4='SA', xad_5='5061', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0883721234'
        pid.religion = CWE(cwe_1='S')
        pid.pid_20 = '5678901234'
        pid.identity_reliability_code = CWE(cwe_1='N')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = 'CON6789^Thompson^Laura^^^Dr^MBBS'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='JOHNSON', xpn_2='David', xpn_3='James')
        nk1.address = XAD(xad_2='PRN', xad_3='PH', xad_8='0883721234')
        nk1.contact_role = CWE(cwe_1='NOK')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build NK1 ..
        nk1_2 = NK1()
        nk1_2.set_id_nk1 = '2'
        nk1_2.name = XPN(xpn_1='JOHNSON', xpn_2='Rebecca', xpn_3='Anne')
        nk1_2.address = XAD(xad_2='PRN', xad_3='PH', xad_8='0412345678')
        nk1_2.contact_role = CWE(cwe_1='EMC')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin_2 = AdtA01NextOfKin()
        next_of_kin_2.nk1 = nk1_2

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = [next_of_kin, next_of_kin_2]

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TRAKCARE')
        msh.sending_facility = HD(hd_1='CPHB', hd_2='Calvary Public Hospital Bruce')
        msh.receiving_application = HD(hd_1='ACTPAS')
        msh.receiving_facility = HD(hd_1='ACT_HEALTH')
        msh.date_time_of_message = '20250318090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A28')
        msh.message_control_id = 'MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250318090000'
        evn.operator_id = XCN(xcn_1='SMORRIS', xcn_2='Morris', xcn_3='Susan', xcn_6='Admin')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN9936025', cx_4='CPHB', cx_5='MR'), CX(cx_1='6789012345', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='TAYLOR', xpn_2='James', xpn_3='Robert', xpn_5='Mr')
        pid.date_time_of_birth = '19670214'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='15 Aspinall Street', xad_3='Watson', xad_4='ACT', xad_5='2602', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0262411234'
        pid.religion = CWE(cwe_1='M')
        pid.pid_20 = '6789012345'
        pid.identity_reliability_code = CWE(cwe_1='N')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='TAYLOR', xpn_2='Wendy', xpn_3='Louise')
        nk1.address = XAD(xad_2='PRN', xad_3='PH', xad_8='0412987654')
        nk1.contact_role = CWE(cwe_1='NOK')

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACACIA')
        msh.sending_facility = HD(hd_1='RAH', hd_2='Royal Adelaide Hospital')
        msh.receiving_application = HD(hd_1='OACIS')
        msh.receiving_facility = HD(hd_1='SA_HEALTH')
        msh.date_time_of_message = '20250319140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A40')
        msh.message_control_id = 'MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250319140000'
        evn.operator_id = XCN(xcn_1='PJONES', xcn_2='Jones', xcn_3='Peter', xcn_6='Admin')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN1047236', cx_4='RAH', cx_5='MR'), CX(cx_1='7890123456', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='SMITH', xpn_2='Geoffrey', xpn_3='Allan', xpn_5='Mr')
        pid.date_time_of_birth = '19450728'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='9 Prospect Road', xad_3='Prospect', xad_4='SA', xad_5='5082', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0882691234'
        pid.religion = CWE(cwe_1='W')
        pid.pid_20 = '7890123456'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='MRN1047237', cx_4='RAH', cx_5='MR')
        mrg.mrg_2 = ''

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TRAKCARE')
        msh.sending_facility = HD(hd_1='FMC', hd_2='Flinders Medical Centre')
        msh.receiving_application = HD(hd_1='SAPATHOLOGY')
        msh.receiving_facility = HD(hd_1='SA_PATH')
        msh.date_time_of_message = '20250320083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN2158347', cx_4='FMC', cx_5='MR'), CX(cx_1='8901234568', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='CHEN', xpn_2='Wei', xpn_3='Lin', xpn_5='Mr')
        pid.date_time_of_birth = '19810917'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='31 Diagonal Road', xad_3='Oaklands Park', xad_4='SA', xad_5='5046', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0883741234'
        pid.religion = CWE(cwe_1='M')
        pid.pid_20 = '8901234568'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3EAST', pl_2='305', pl_3='1', pl_4='FMC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'CON7890^Singh^Priya^^^Dr^MBBS'
        pv1.preadmit_test_indicator = CWE(cwe_1='MED')
        pv1.vip_indicator = CWE(cwe_1='1')
        pv1.visit_number = CX(cx_1='CON7890', cx_2='Singh', cx_3='Priya', cx_6='Dr', cx_7='MBBS')
        pv1.financial_class = FC(fc_1='IN')
        pv1.courtesy_code = CWE(cwe_1='SA_PUB')
        pv1.pending_location = PL(pl_1='FMC')
        pv1.admit_date_time = 'A'
        pv1.total_charges = '20250319200000'

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
        orc.placer_order_number = EI(ei_1='ORD20250320-001', ei_2='TRAKCARE')
        orc.orc_7 = '^^^20250320083000^^R'
        orc.date_time_of_order_event = '20250320083000'
        orc.orc_10 = 'JNURSE^Reid^Janet^^^RN'
        orc.orc_12 = 'CON7890^Singh^Priya^^^Dr^MBBS'
        orc.enterers_location = PL(pl_1='FMC')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250320-001', ei_2='TRAKCARE')
        obr.universal_service_identifier = CWE(cwe_1='FBE', cwe_2='Full Blood Examination', cwe_3='SAPATH')
        obr.observation_date_time = '20250320083000'
        obr.obr_15 = '20250320082500'
        obr.obr_16 = 'Blood^Venous^EDTA'
        obr.obr_17 = 'CON7890^Singh^Priya^^^Dr^MBBS'
        obr.charge_to_practice = MOC(moc_1='20250320083000')
        obr.parent_result = PRL(prl_1='F')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='ORD20250320-001', ei_2='TRAKCARE')
        obr_2.universal_service_identifier = CWE(cwe_1='UEC', cwe_2='Urea Electrolytes Creatinine', cwe_3='SAPATH')
        obr_2.observation_date_time = '20250320083000'
        obr_2.obr_15 = '20250320082500'
        obr_2.obr_16 = 'Blood^Venous^SST'
        obr_2.obr_17 = 'CON7890^Singh^Priya^^^Dr^MBBS'
        obr_2.charge_to_practice = MOC(moc_1='20250320083000')
        obr_2.parent_result = PRL(prl_1='F')

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD20250320-001', ei_2='TRAKCARE')
        obr_3.universal_service_identifier = CWE(cwe_1='CRP', cwe_2='C-Reactive Protein', cwe_3='SAPATH')
        obr_3.observation_date_time = '20250320083000'
        obr_3.obr_15 = '20250320082500'
        obr_3.obr_16 = 'Blood^Venous^SST'
        obr_3.obr_17 = 'CON7890^Singh^Priya^^^Dr^MBBS'
        obr_3.charge_to_practice = MOC(moc_1='20250320083000')
        obr_3.parent_result = PRL(prl_1='F')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3]

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACACIA')
        msh.sending_facility = HD(hd_1='TCH', hd_2='The Canberra Hospital')
        msh.receiving_application = HD(hd_1='ACTRAD')
        msh.receiving_facility = HD(hd_1='ACT_RAD')
        msh.date_time_of_message = '20250320100000'
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
        pid.patient_identifier_list = [CX(cx_1='MRN3269458', cx_4='TCH', cx_5='MR'), CX(cx_1='9012345679', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='BAKER', xpn_2='Thomas', xpn_3='William', xpn_5='Mr')
        pid.date_time_of_birth = '19550803'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='22 Limestone Avenue', xad_3='Ainslie', xad_4='ACT', xad_5='2602', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0262481234'
        pid.religion = CWE(cwe_1='M')
        pid.pid_20 = '9012345679'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='ED05', pl_3='1', pl_4='TCH', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'CON8901^Wu^David^^^Dr^MBBS'
        pv1.preadmit_test_indicator = CWE(cwe_1='ED')
        pv1.vip_indicator = CWE(cwe_1='1')
        pv1.visit_number = CX(cx_1='CON8901', cx_2='Wu', cx_3='David', cx_6='Dr', cx_7='MBBS')
        pv1.financial_class = FC(fc_1='EM')
        pv1.courtesy_code = CWE(cwe_1='ACT_PUB')
        pv1.pending_location = PL(pl_1='TCH')
        pv1.admit_date_time = 'A'
        pv1.total_charges = '20250320093000'

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
        orc.placer_order_number = EI(ei_1='ORD20250320-002', ei_2='ACACIA')
        orc.orc_7 = '^^^20250320100000^^S'
        orc.date_time_of_order_event = '20250320100000'
        orc.orc_10 = 'TNURSE^Allan^Theresa^^^RN'
        orc.orc_12 = 'CON8901^Wu^David^^^Dr^MBBS'
        orc.enterers_location = PL(pl_1='TCH')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250320-002', ei_2='ACACIA')
        obr.universal_service_identifier = CWE(cwe_1='CXRAY', cwe_2='Chest X-Ray PA and Lateral', cwe_3='ACTRAD')
        obr.observation_date_time = '20250320100000'
        obr.obr_15 = '20250320095500'
        obr.obr_17 = 'CON8901^Wu^David^^^Dr^MBBS'
        obr.diagnostic_serv_sect_id = '20250320100000'
        obr.obr_27 = 'F'
        obr.transportation_mode = '^SOB and pleuritic chest pain'

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPATHOLOGY')
        msh.sending_facility = HD(hd_1='SAPATH')
        msh.receiving_application = HD(hd_1='TRAKCARE')
        msh.receiving_facility = HD(hd_1='RAH', hd_2='Royal Adelaide Hospital')
        msh.date_time_of_message = '20250320141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN4502184', cx_4='RAH', cx_5='MR'), CX(cx_1='8902345671', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='VASILEIOU', xpn_2='Dimitri', xpn_3='Konstantinos', xpn_5='Mr')
        pid.date_time_of_birth = '19620718'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='58 North Terrace', xad_3='Adelaide', xad_4='SA', xad_5='5000', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0882234578'
        pid.religion = CWE(cwe_1='M')
        pid.pid_20 = '8902345671'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6EAST', pl_2='608', pl_3='2', pl_4='RAH', pl_7='N')
        pv1.pv1_7 = 'CON3120^Andersen^Helena^^^Dr^MBBS'
        pv1.preadmit_test_indicator = CWE(cwe_1='MED')
        pv1.financial_class = FC(fc_1='IN')
        pv1.courtesy_code = CWE(cwe_1='SA_PUB')
        pv1.pending_location = PL(pl_1='RAH')
        pv1.admit_date_time = 'A'
        pv1.total_charges = '20250314091200'

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
        orc.placer_order_number = EI(ei_1='ORD20250314-198', ei_2='TRAKCARE')
        orc.filler_order_number = EI(ei_1='RES20250320-014', ei_2='SAPATH')
        orc.orc_7 = '^^^20250314120000^^R'
        orc.date_time_of_order_event = '20250320141500'
        orc.orc_12 = 'CON3120^Andersen^Helena^^^Dr^MBBS'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250314-198', ei_2='TRAKCARE')
        obr.filler_order_number = EI(ei_1='RES20250320-014', ei_2='SAPATH')
        obr.universal_service_identifier = CWE(cwe_1='FBE', cwe_2='Full Blood Examination', cwe_3='SAPATH')
        obr.observation_date_time = '20250314120000'
        obr.obr_15 = '20250314115500'
        obr.obr_16 = 'Blood^Venous^EDTA'
        obr.obr_17 = 'CON3120^Andersen^Helena^^^Dr^MBBS'
        obr.charge_to_practice = MOC(moc_1='20250320141500')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='WBC', cwe_2='White Blood Cell Count', cwe_3='SAPATH')
        obx.obx_5 = '11.2'
        obx.obx_6 = 'x10\\S\\9/L'
        obx.reference_range = '4.0-11.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250320140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='RBC', cwe_2='Red Blood Cell Count', cwe_3='SAPATH')
        obx_2.obx_5 = '4.85'
        obx_2.obx_6 = 'x10\\S\\12/L'
        obx_2.reference_range = '4.50-6.50'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250320140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='HGB', cwe_2='Haemoglobin', cwe_3='SAPATH')
        obx_3.obx_5 = '148'
        obx_3.units = CWE(cwe_1='g/L')
        obx_3.reference_range = '130-180'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250320140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='HCT', cwe_2='Haematocrit', cwe_3='SAPATH')
        obx_4.obx_5 = '0.44'
        obx_4.units = CWE(cwe_1='L/L')
        obx_4.reference_range = '0.40-0.54'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250320140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='PLT', cwe_2='Platelet Count', cwe_3='SAPATH')
        obx_5.obx_5 = '245'
        obx_5.obx_6 = 'x10\\S\\9/L'
        obx_5.reference_range = '150-400'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250320140000'

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPATHOLOGY')
        msh.sending_facility = HD(hd_1='SAPATH')
        msh.receiving_application = HD(hd_1='ACACIA')
        msh.receiving_facility = HD(hd_1='FMC', hd_2='Flinders Medical Centre')
        msh.date_time_of_message = '20250321091000'
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
        pid.patient_identifier_list = [CX(cx_1='MRN2261507', cx_4='FMC', cx_5='MR'), CX(cx_1='8901456720', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='TARAKI', xpn_2='Mahmoud', xpn_3='Hassan', xpn_5='Mr')
        pid.date_time_of_birth = '19590304'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='7 Halsey Road', xad_3='Elizabeth', xad_4='SA', xad_5='5112', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0883771409'
        pid.religion = CWE(cwe_1='M')
        pid.pid_20 = '8901456720'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='2NORTH', pl_2='214', pl_3='1', pl_4='FMC', pl_7='N')
        pv1.pv1_7 = 'CON7115^Webster^Charlotte^^^Dr^MBBS'
        pv1.preadmit_test_indicator = CWE(cwe_1='REN')
        pv1.financial_class = FC(fc_1='IN')
        pv1.courtesy_code = CWE(cwe_1='SA_PUB')
        pv1.pending_location = PL(pl_1='FMC')
        pv1.admit_date_time = 'A'
        pv1.total_charges = '20250319200000'

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
        orc.placer_order_number = EI(ei_1='ORD20250320-088', ei_2='TRAKCARE')
        orc.filler_order_number = EI(ei_1='RES20250321-022', ei_2='SAPATH')
        orc.orc_7 = '^^^20250320083000^^R'
        orc.date_time_of_order_event = '20250321091000'
        orc.orc_12 = 'CON7115^Webster^Charlotte^^^Dr^MBBS'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250320-088', ei_2='TRAKCARE')
        obr.filler_order_number = EI(ei_1='RES20250321-022', ei_2='SAPATH')
        obr.universal_service_identifier = CWE(cwe_1='UEC', cwe_2='Urea Electrolytes Creatinine', cwe_3='SAPATH')
        obr.observation_date_time = '20250320083000'
        obr.obr_15 = '20250320082500'
        obr.obr_16 = 'Blood^Venous^SST'
        obr.obr_17 = 'CON7115^Webster^Charlotte^^^Dr^MBBS'
        obr.charge_to_practice = MOC(moc_1='20250321091000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='NA', cwe_2='Sodium', cwe_3='SAPATH')
        obx.obx_5 = '128'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '135-145'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250321085000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='K', cwe_2='Potassium', cwe_3='SAPATH')
        obx_2.obx_5 = '5.8'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '3.5-5.2'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250321085000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='CL', cwe_2='Chloride', cwe_3='SAPATH')
        obx_3.obx_5 = '96'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '95-110'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250321085000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='HCO3', cwe_2='Bicarbonate', cwe_3='SAPATH')
        obx_4.obx_5 = '18'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '22-32'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250321085000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='UREA', cwe_2='Urea', cwe_3='SAPATH')
        obx_5.obx_5 = '14.2'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '2.5-8.0'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250321085000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='CREAT', cwe_2='Creatinine', cwe_3='SAPATH')
        obx_6.obx_5 = '185'
        obx_6.units = CWE(cwe_1='umol/L')
        obx_6.reference_range = '60-110'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250321085000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='EGFR', cwe_2='eGFR', cwe_3='SAPATH')
        obx_7.obx_5 = '34'
        obx_7.units = CWE(cwe_1='mL/min/1.73m2')
        obx_7.reference_range = '>90'
        obx_7.interpretation_codes = CWE(cwe_1='L')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250321085000'

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACTRAD')
        msh.sending_facility = HD(hd_1='ACT_RAD')
        msh.receiving_application = HD(hd_1='TRAKCARE')
        msh.receiving_facility = HD(hd_1='TCH', hd_2='The Canberra Hospital')
        msh.date_time_of_message = '20250320153000'
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
        pid.patient_identifier_list = [CX(cx_1='MRN3370116', cx_4='TCH', cx_5='MR'), CX(cx_1='9012678045', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='MAKERETI', xpn_2='Hineamaru', xpn_3='Kahurangi', xpn_5='Mrs')
        pid.date_time_of_birth = '19770211'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='3 Northbourne Avenue', xad_3='Civic', xad_4='ACT', xad_5='2608', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0262489876'
        pid.religion = CWE(cwe_1='M')
        pid.pid_20 = '9012678045'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='ED11', pl_3='1', pl_4='TCH', pl_7='N')
        pv1.pv1_7 = 'CON8245^Hartley^Ruth^^^Dr^MBBS'
        pv1.preadmit_test_indicator = CWE(cwe_1='ED')
        pv1.financial_class = FC(fc_1='EM')
        pv1.courtesy_code = CWE(cwe_1='ACT_PUB')
        pv1.pending_location = PL(pl_1='TCH')
        pv1.admit_date_time = 'A'
        pv1.total_charges = '20250320093000'

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
        orc.placer_order_number = EI(ei_1='ORD20250320-104', ei_2='ACACIA')
        orc.filler_order_number = EI(ei_1='RES20250320-105', ei_2='ACTRAD')
        orc.orc_7 = '^^^20250320100000^^S'
        orc.date_time_of_order_event = '20250320153000'
        orc.orc_12 = 'CON8245^Hartley^Ruth^^^Dr^MBBS'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250320-104', ei_2='ACACIA')
        obr.filler_order_number = EI(ei_1='RES20250320-105', ei_2='ACTRAD')
        obr.universal_service_identifier = CWE(cwe_1='CXRAY', cwe_2='Chest X-Ray PA and Lateral', cwe_3='ACTRAD')
        obr.observation_date_time = '20250320100000'
        obr.obr_15 = '20250320103000'
        obr.obr_17 = 'CON8245^Hartley^Ruth^^^Dr^MBBS'
        obr.filler_field_1 = 'RAD9415^Bui^Henry^^^Dr^FRANZCR'
        obr.filler_field_2 = '20250320153000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='CXRAY', cwe_2='Chest X-Ray Report', cwe_3='ACTRAD')
        obx.obx_5 = (
            'CHEST X-RAY PA AND LATERAL\\.br\\\\.br\\Clinical Indication: SOB and pleuritic chest pain\\.br\\\\.br\\Comparison: Nil prior\\.br\\\\.br\\Findin'
            'gs:\\.br\\Heart size is normal. The mediastinal contour is unremarkable.\\.br\\There is a small left-sided pleural effusion with associated basa'
            'l atelectasis.\\.br\\The right lung is clear. No pneumothorax.\\.br\\\\.br\\Impression:\\.br\\Small left pleural effusion. Clinical correlation '
            'recommended.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250320152000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPATHOLOGY')
        msh.sending_facility = HD(hd_1='SAPATH')
        msh.receiving_application = HD(hd_1='TRAKCARE')
        msh.receiving_facility = HD(hd_1='LMH', hd_2='Lyell McEwin Hospital')
        msh.date_time_of_message = '20250322110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN7821649', cx_4='LMH', cx_5='MR'), CX(cx_1='4568123097', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='MERCURIO', xpn_2='Lorenzo', xpn_3='Antonio', xpn_5='Mr')
        pid.date_time_of_birth = '19641128'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='94 John Rice Avenue', xad_3='Elizabeth Vale', xad_4='SA', xad_5='5112', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0882828105'
        pid.religion = CWE(cwe_1='M')
        pid.pid_20 = '4568123097'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD', pl_2='CLINIC9', pl_3='1', pl_4='LMH', pl_7='N')
        pv1.pv1_7 = 'CON5012^Karageorgis^Stavros^^^Dr^MBBS'
        pv1.preadmit_test_indicator = CWE(cwe_1='OPD')
        pv1.financial_class = FC(fc_1='OUT')
        pv1.courtesy_code = CWE(cwe_1='SA_PUB')
        pv1.pending_location = PL(pl_1='LMH')
        pv1.admit_date_time = 'A'
        pv1.total_charges = '20250316083000'

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
        orc.placer_order_number = EI(ei_1='ORD20250316-067', ei_2='ACACIA')
        orc.filler_order_number = EI(ei_1='RES20250322-031', ei_2='SAPATH')
        orc.orc_7 = '^^^20250316090000^^R'
        orc.date_time_of_order_event = '20250322110000'
        orc.orc_12 = 'CON5012^Karageorgis^Stavros^^^Dr^MBBS'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250316-067', ei_2='ACACIA')
        obr.filler_order_number = EI(ei_1='RES20250322-031', ei_2='SAPATH')
        obr.universal_service_identifier = CWE(cwe_1='HBA1C', cwe_2='Glycated Haemoglobin', cwe_3='SAPATH')
        obr.observation_date_time = '20250316090000'
        obr.obr_15 = '20250316085500'
        obr.obr_16 = 'Blood^Venous^EDTA'
        obr.obr_17 = 'CON5012^Karageorgis^Stavros^^^Dr^MBBS'
        obr.charge_to_practice = MOC(moc_1='20250322110000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='HBA1C', cwe_2='HbA1c', cwe_3='SAPATH')
        obx.obx_5 = '8.2'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '<7.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250322100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='EDAG', cwe_2='Estimated Average Glucose', cwe_3='SAPATH')
        obx_2.obx_5 = '10.2'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250322100000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='PDF', cwe_2='Clinical Document', cwe_3='LN')
        obx_3.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMg'
            'MCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5'
            'IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo='
        )
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TRAKCARE')
        msh.sending_facility = HD(hd_1='RAH', hd_2='Royal Adelaide Hospital')
        msh.receiving_application = HD(hd_1='OACIS')
        msh.receiving_facility = HD(hd_1='SA_HEALTH')
        msh.date_time_of_message = '20250323090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20250410-001')
        sch.filler_appointment_id = EI(ei_1='APT20250410-001')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine Appointment', cwe_3='HL70276')
        sch.appointment_type = CWE(cwe_1='FOLLOWUP', cwe_2='Follow-up', cwe_3='HL70277')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^30^20250410090000^20250410093000'
        sch.sch_13 = 'CON3402^Yusuf^Adila^^^Dr^MBBS'
        sch.placer_contact_address = XAD(xad_2='PRN', xad_3='PH', xad_8='0882227891')
        sch.placer_contact_location = PL(pl_1='6EAST_CLINIC', pl_2='Endocrinology Outpatients', pl_3='RAH')
        sch.sch_16 = 'CON3402^Yusuf^Adila^^^Dr^MBBS'
        sch.filler_contact_address = XAD(xad_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN4615370', cx_4='RAH', cx_5='MR'), CX(cx_1='8903127845', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='CALLAGHAN', xpn_2='Bridget', xpn_3='Imogen', xpn_5='Mrs')
        pid.date_time_of_birth = '19710602'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='21 Halifax Street', xad_3='Adelaide', xad_4='SA', xad_5='5000', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0882236704'
        pid.religion = CWE(cwe_1='M')
        pid.pid_20 = '8903127845'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='6EAST_CLINIC', pl_3='1', pl_4='RAH', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'CON3402^Yusuf^Adila^^^Dr^MBBS'
        pv1.preadmit_test_indicator = CWE(cwe_1='ENDO')
        pv1.financial_class = FC(fc_1='OUT')
        pv1.courtesy_code = CWE(cwe_1='SA_PUB')
        pv1.pending_location = PL(pl_1='RAH')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.segment_action_code = 'A'
        rgs.resource_group_id = CWE(cwe_1='ENDOCRINOLOGY', cwe_2='Endocrinology', cwe_3='HL70572')

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.segment_action_code = 'A'
        ais.universal_service_identifier = CWE(cwe_1='ENDOCONS', cwe_2='Endocrinology Consultation', cwe_3='RAH_SVC')
        ais.start_date_time = '20250410090000'
        ais.duration = '30'
        ais.duration_units = CNE(cne_1='min')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.aip_3 = 'CON3402^Yusuf^Adila^^^Dr^MBBS'
        aip.aip_4 = ''

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACACIA')
        msh.sending_facility = HD(hd_1='TCH', hd_2='The Canberra Hospital')
        msh.receiving_application = HD(hd_1='ACTPAS')
        msh.receiving_facility = HD(hd_1='ACT_HEALTH')
        msh.date_time_of_message = '20250324110000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S15', msg_3='SIU_S15')
        msh.message_control_id = 'MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20250401-017')
        sch.filler_appointment_id = EI(ei_1='APT20250401-017')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine Appointment', cwe_3='HL70276')
        sch.appointment_type = CWE(cwe_1='FOLLOWUP', cwe_2='Follow-up', cwe_3='HL70277')
        sch.sch_9 = '20'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^20^20250401140000^20250401142000'
        sch.sch_13 = 'CON4218^Mehrotra^Vikram^^^Dr^MBBS'
        sch.placer_contact_address = XAD(xad_2='PRN', xad_3='PH', xad_8='0262494582')
        sch.placer_contact_location = PL(pl_1='2NORTH_CLINIC', pl_2='Gastroenterology Outpatients', pl_3='TCH')
        sch.sch_16 = 'CON4218^Mehrotra^Vikram^^^Dr^MBBS'
        sch.filler_contact_address = XAD(xad_1='CANCELLED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN6708425', cx_4='TCH', cx_5='MR'), CX(cx_1='3457120893', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='DELACROIX', xpn_2='Solenne', xpn_3='Margaux', xpn_5='Ms')
        pid.date_time_of_birth = '19940915'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='16 Currie Crescent', xad_3='Kingston', xad_4='ACT', xad_5='2604', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0262959087'
        pid.religion = CWE(cwe_1='S')
        pid.pid_20 = '3457120893'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='2NORTH_CLINIC', pl_3='1', pl_4='TCH', pl_7='N')
        pv1.pv1_7 = 'CON4218^Mehrotra^Vikram^^^Dr^MBBS'
        pv1.preadmit_test_indicator = CWE(cwe_1='GAST')
        pv1.financial_class = FC(fc_1='OUT')
        pv1.courtesy_code = CWE(cwe_1='ACT_PUB')
        pv1.pending_location = PL(pl_1='TCH')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TCA')
        msh.sending_facility = HD(hd_1='WCH', hd_2="Women's and Children's Hospital")
        msh.receiving_application = HD(hd_1='OACIS')
        msh.receiving_facility = HD(hd_1='SA_HEALTH')
        msh.date_time_of_message = '20250325140000'
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
        evn.recorded_date_time = '20250325140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN8930745', cx_4='WCH', cx_5='MR'), CX(cx_1='5679234608', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='OKONKWO', xpn_2='Chinaza', xpn_3='Ifeoma', xpn_5='Miss')
        pid.date_time_of_birth = '20160714'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='10 Devereux Road', xad_3='Beulah Park', xad_4='SA', xad_5='5067', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0883310465'
        pid.religion = CWE(cwe_1='S')
        pid.pid_20 = '5679234608'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PAED_OPD', pl_3='1', pl_4='WCH', pl_7='N')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.pv1_7 = 'CON6210^Marchetti^Sergio^^^Dr^MBBS'
        pv1.preadmit_test_indicator = CWE(cwe_1='PAED')
        pv1.financial_class = FC(fc_1='OUT')
        pv1.courtesy_code = CWE(cwe_1='SA_PUB')
        pv1.pending_location = PL(pl_1='WCH')
        pv1.admit_date_time = 'A'
        pv1.total_charges = '20250325130000'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Discharge Summary', cwe_3='HL70270')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20250325140000'
        txa.txa_5 = 'CON6210^Marchetti^Sergio^^^Dr^MBBS'
        txa.transcription_date_time = '20250325140000'
        txa.txa_9 = 'CON6210^Marchetti^Sergio^^^Dr^MBBS'
        txa.parent_document_number = EI(ei_1='DOC20250325-001')
        txa.unique_document_file_name = 'AU'
        txa.document_confidentiality_status = 'AV'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Clinical Document', cwe_3='LN')
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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TRAKCARE')
        msh.sending_facility = HD(hd_1='FMC', hd_2='Flinders Medical Centre')
        msh.receiving_application = HD(hd_1='OACIS')
        msh.receiving_facility = HD(hd_1='SA_HEALTH')
        msh.date_time_of_message = '20250326160000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A13', msg_3='ADT_A13')
        msh.message_control_id = 'MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A13'
        evn.recorded_date_time = '20250326160000'
        evn.evn_5 = 'CON3456^Patel^Rajesh^^^Dr^MBBS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN5618934', cx_4='FMC', cx_5='MR'), CX(cx_1='2346019785', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='LAZARIDIS', xpn_2='Yannis', xpn_3='Theofanis', xpn_5='Mr')
        pid.date_time_of_birth = '19481119'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='5 Kestrel Avenue', xad_3='Hallett Cove', xad_4='SA', xad_5='5158', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0883815217'
        pid.religion = CWE(cwe_1='W')
        pid.pid_20 = '2346019785'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4WEST', pl_2='410', pl_3='1', pl_4='FMC', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'CON3719^Yamamoto^Akiko^^^Dr^MBBS'
        pv1.pv1_8 = 'CON3719^Yamamoto^Akiko^^^Dr^MBBS'
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'CON3719^Yamamoto^Akiko^^^Dr^MBBS'
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.financial_class = FC(fc_1='SA_PUB')
        pv1.pv1_40 = 'FMC'
        pv1.pending_location = PL(pl_1='A')
        pv1.discharge_date_time = '20250320090000'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TRAK_HIS')
        msh.sending_facility = HD(hd_1='RAH', hd_2='Royal Adelaide Hospital')
        msh.receiving_application = HD(hd_1='SAPHARMA')
        msh.receiving_facility = HD(hd_1='SA_PHARMA')
        msh.date_time_of_message = '20250327083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN4823051', cx_4='RAH', cx_5='MR'), CX(cx_1='8904718206', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='PRENDERGAST', xpn_2='Lachlan', xpn_3='Heath', xpn_5='Mr')
        pid.date_time_of_birth = '19880506'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='7 Sturt Street', xad_3='Adelaide', xad_4='SA', xad_5='5000', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0882264913'
        pid.religion = CWE(cwe_1='S')
        pid.pid_20 = '8904718206'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='7WEST', pl_2='709', pl_3='2', pl_4='RAH', pl_7='N')
        pv1.pv1_7 = 'CON2854^Driscoll^Padraig^^^Dr^MBBS'
        pv1.preadmit_test_indicator = CWE(cwe_1='CARD')
        pv1.financial_class = FC(fc_1='IN')
        pv1.courtesy_code = CWE(cwe_1='SA_PUB')
        pv1.pending_location = PL(pl_1='RAH')
        pv1.admit_date_time = 'A'
        pv1.total_charges = '20250314091200'

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
        orc.placer_order_number = EI(ei_1='ORD20250327-201', ei_2='TRAK_HIS')
        orc.orc_7 = '^^^20250327083000^^R'
        orc.date_time_of_order_event = '20250327083000'
        orc.orc_10 = 'RNURSE^Cole^Imogen^^^RN'
        orc.orc_12 = 'CON2854^Driscoll^Padraig^^^Dr^MBBS'
        orc.enterers_location = PL(pl_1='RAH')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20250327-201', ei_2='TRAK_HIS')
        obr.universal_service_identifier = CWE(cwe_1='RXORD', cwe_2='Pharmacy Order', cwe_3='RAH_PHARMA')
        obr.observation_date_time = '20250327083000'
        obr.obr_15 = '20250327082000'
        obr.obr_17 = 'CON2854^Driscoll^Padraig^^^Dr^MBBS'
        obr.charge_to_practice = MOC(moc_1='20250327083000')
        obr.parent_result = PRL(prl_1='F')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='METOP', cwe_2='Metoprolol Tartrate', cwe_3='PBS')
        rxo.requested_give_amount_minimum = '25'
        rxo.requested_give_amount_maximum = 'mg'
        rxo.requested_dosage_form = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')
        rxo.providers_administration_instructions = CWE(cwe_1='V')
        rxo.allow_substitutions = '0'
        rxo.requested_dispense_code = CWE(cwe_1='TAB', cwe_2='Tablet', cwe_3='HL70235')
        rxo.requested_give_per_time_unit = '1'
        rxo.requested_give_strength = '25'
        rxo.requested_give_strength_units = CWE(cwe_1='mg')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo, rxr]

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TRAKCARE')
        msh.sending_facility = HD(hd_1='CPHB', hd_2='Calvary Public Hospital Bruce')
        msh.receiving_application = HD(hd_1='ACTPAS')
        msh.receiving_facility = HD(hd_1='ACT_HEALTH')
        msh.date_time_of_message = '20250328091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A11', msg_3='ADT_A11')
        msh.message_control_id = 'MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A11'
        evn.recorded_date_time = '20250328091500'
        evn.operator_id = XCN(xcn_1='SMORRIS', xcn_2='Morris', xcn_3='Susan', xcn_6='Admin')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN1004217', cx_4='CPHB', cx_5='MR'), CX(cx_1='6790148532', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='PEREIRA', xpn_2='Cristiano', xpn_3='Joaquim', xpn_5='Mr')
        pid.date_time_of_birth = '19590927'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='31 Hillside Road', xad_3='Hawker', xad_4='ACT', xad_5='2614', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0262784110'
        pid.religion = CWE(cwe_1='M')
        pid.pid_20 = '6790148532'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3NORTH', pl_2='307', pl_3='1', pl_4='CPHB', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'CON1681^Sanders^Geraldine^^^Dr^MBBS'
        pv1.pv1_8 = 'CON1681^Sanders^Geraldine^^^Dr^MBBS'
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'CON1681^Sanders^Geraldine^^^Dr^MBBS'
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.financial_class = FC(fc_1='ACT_PUB')
        pv1.pv1_40 = 'CPHB'
        pv1.pending_location = PL(pl_1='A')
        pv1.discharge_date_time = '20250327200000'

        # .. assemble the full message ..
        msg = ADT_A09()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/au/au-intersystems-trakcare.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TRAKCARE')
        msh.sending_facility = HD(hd_1='TCH', hd_2='The Canberra Hospital')
        msh.receiving_application = HD(hd_1='ACTPAS')
        msh.receiving_facility = HD(hd_1='ACT_HEALTH')
        msh.date_time_of_message = '20250329100000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250329100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN3415802', cx_4='TCH', cx_5='MR'), CX(cx_1='9013561284', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='CAVANOUGH', xpn_2='Reuben', xpn_3='Xavier', xpn_5='Mr')
        pid.date_time_of_birth = '19490428'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='4 Eyre Crescent', xad_3='Lyneham', xad_4='ACT', xad_5='2602', xad_6='AUS')
        pid.pid_13 = '^PRN^PH^^^^^0262575039'
        pid.religion = CWE(cwe_1='W')
        pid.pid_20 = '9013561284'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5SOUTH', pl_2='509', pl_3='1', pl_4='TCH', pl_7='N')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.pv1_7 = 'CON8330^Pavlovic^Mira^^^Dr^MBBS'
        pv1.preadmit_test_indicator = CWE(cwe_1='GEN')
        pv1.financial_class = FC(fc_1='IN')
        pv1.courtesy_code = CWE(cwe_1='ACT_PUB')
        pv1.pending_location = PL(pl_1='TCH')
        pv1.admit_date_time = 'A'
        pv1.total_charges = '20250320093000'
        pv1.alternate_visit_id = CX(cx_1='20250329090000')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Discharge Summary', cwe_3='HL70270')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20250329100000'
        txa.txa_5 = 'CON8330^Pavlovic^Mira^^^Dr^MBBS'
        txa.transcription_date_time = '20250329100000'
        txa.txa_9 = 'CON8330^Pavlovic^Mira^^^Dr^MBBS'
        txa.parent_document_number = EI(ei_1='DOC20250329-001')
        txa.unique_document_file_name = 'AU'
        txa.document_confidentiality_status = 'AV'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='DS', cwe_2='Discharge Summary', cwe_3='LN')
        obx.obx_5 = (
            'DISCHARGE SUMMARY\\.br\\\\.br\\Patient: CAVANOUGH, Reuben Xavier\\.br\\MRN: MRN3415802\\.br\\DOB: 28/04/1949\\.br\\\\.br\\Admission Date: 20/03/'
            '2025\\.br\\Discharge Date: 29/03/2025\\.br\\\\.br\\Admitting Diagnosis: Shortness of breath, pleuritic chest pain\\.br\\\\.br\\Investigations:\\'
            '.br\\- Chest X-Ray: Small left pleural effusion\\.br\\- CT Pulmonary Angiogram: No pulmonary embolism\\.br\\- Pleural fluid analysis: Transudati'
            've\\.br\\\\.br\\Management:\\.br\\- Diuretic therapy with intravenous frusemide\\.br\\- Echocardiogram showed preserved LV function, mild diasto'
            'lic dysfunction\\.br\\- Transitioned to oral frusemide 40mg daily\\.br\\\\.br\\Discharge Medications:\\.br\\1. Frusemide 40mg PO daily\\.br\\2. '
            'Perindopril 5mg PO daily\\.br\\3. Atorvastatin 40mg PO nocte\\.br\\\\.br\\Follow-up:\\.br\\- Cardiology outpatients in 4 weeks\\.br\\- Repeat ch'
            'est X-ray in 2 weeks\\.br\\\\.br\\Prepared by: Dr Mira Pavlovic, MBBS FRACP'
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
