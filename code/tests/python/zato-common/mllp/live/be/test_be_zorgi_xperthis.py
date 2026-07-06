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
from zato.hl7v2.v2_9.datatypes import CNE, CP, CWE, CX, EI, FC, HD, MOC, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA05NextOfKin, AdtA39Patient, MfnM02MfStaff, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, \
    OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, \
    SiuS12LocationResource, SiuS12Patient, SiuS12Resources, SiuS12Service, VxuV04Observation, VxuV04Order, VxuV04PatientVisit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MFN_M02, ORM_O01, ORU_R01, SIU_S12, VXU_V04
from zato.hl7v2.v2_9.segments import AIL, AIS, DG1, EVN, IN1, MFE, MFI, MRG, MSH, NK1, OBR, OBX, ORC, PD1, PID, PV1, PV2, RGS, RXA, RXR, SCH, STF

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('be', 'be-zorgi-xperthis.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/be/be-zorgi-xperthis.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='XPERTHIS')
        msh.sending_facility = HD(hd_1='CHU_LIEGE')
        msh.receiving_application = HD(hd_1='EAI')
        msh.receiving_facility = HD(hd_1='CHU')
        msh.date_time_of_message = '20220315080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'CHU20220315080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20220315075500'
        evn.operator_id = XCN(xcn_1='admin01', xcn_2='Tossaint', xcn_3='Jacques')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='211311411', cx_4='CHU', cx_5='PI'), CX(cx_1='76031523178', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'DUPONT^Pierre^R^^^M'
        pid.date_time_of_birth = '19760315'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Quai de Rome 14', xad_3='Liege', xad_5='4000', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^4^3456789~^ORN^CP^^32^476^234567'
        pid.primary_language = CWE(cwe_1='FR')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='KAT')
        pid.pid_28 = 'N'
        pid.identity_unknown_indicator = 'BE'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHU', pl_2='MED1', pl_3='012', pl_4='CHU')
        pv1.attending_doctor = XCN(xcn_1='22334455', xcn_2='Henrotte', xcn_3='Luc', xcn_5='Dr', xcn_8='INAMI')
        pv1.consulting_doctor = XCN(xcn_1='33445566', xcn_2='Franssen', xcn_3='Véronique', xcn_5='Dr', xcn_8='INAMI')
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='22334455', xcn_2='Henrotte', xcn_3='Luc', xcn_5='Dr', xcn_8='INAMI')
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.pv1_40 = '20220315080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='200', cwe_4='MUTBE')
        in1.insurance_company_id = CX(cx_1='MC200')
        in1.insurance_company_name = XON(xon_1='MC Liege')
        in1.plan_effective_date = '20220101'
        in1.plan_expiration_date = '20221231'
        in1.insureds_relationship_to_patient = CWE(cwe_1='DUPONT', cwe_2='Pierre')
        in1.insureds_address = XAD(xad_1='19760315')
        in1.assignment_of_benefits = CWE(cwe_1='Quai de Rome 14', cwe_3='Liege', cwe_5='4000', cwe_6='BE')
        in1.notice_of_admission_flag = '1'
        in1.policy_deductible = CP(cp_1='200-3456789-01')

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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='XPERTHIS')
        msh.sending_facility = HD(hd_1='STLUC_BXL')
        msh.receiving_application = HD(hd_1='EAI')
        msh.receiving_facility = HD(hd_1='STLUC')
        msh.date_time_of_message = '20220501153000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'STLUC20220501153000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20220501152800'
        evn.operator_id = XCN(xcn_1='admin02', xcn_2='Claessens', xcn_3='Claire')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='311411522', cx_4='STLUC', cx_5='PI'), CX(cx_1='83061829845', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'MOREAU^Isabelle^G^^^Mme'
        pid.date_time_of_birth = '19830618'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Chaussée de Charleroi 88', xad_3='Saint-Gilles', xad_5='1060', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^2^4567890'
        pid.primary_language = CWE(cwe_1='FR')
        pid.marital_status = CWE(cwe_1='S')
        pid.identity_reliability_code = CWE(cwe_1='N')
        pid.taxonomic_classification_code = CWE(cwe_1='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='STLUC', pl_2='CHIR', pl_3='005', pl_4='STLUC')
        pv1.attending_doctor = XCN(xcn_1='44556677', xcn_2='Delvaux', xcn_3='Thomas', xcn_5='Dr', xcn_8='INAMI')
        pv1.consulting_doctor = XCN(xcn_1='55667788', xcn_2='Wathelet', xcn_3='Yves', xcn_5='Dr', xcn_8='INAMI')
        pv1.hospital_service = CWE(cwe_1='CHI')
        pv1.admit_source = CWE(cwe_1='5')
        pv1.admitting_doctor = XCN(xcn_1='44556677', xcn_2='Delvaux', xcn_3='Thomas', xcn_5='Dr', xcn_8='INAMI')
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.discharge_disposition = CWE(cwe_1='20220420120000')
        pv1.servicing_facility = CWE(cwe_1='20220501152800')
        pv1.pv1_44 = ''

        # .. build PV2 ..
        pv2 = PV2()
        pv2.clinic_organization_name = XON(xon_1='Y')
        pv2.expected_surgery_date_and_time = '20220420'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.1', cwe_2='Calculs de la vesicule biliaire avec cholecystite', cwe_3='ICD10BE')
        dg1.diagnosis_type = CWE(cwe_1='F')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.dg1 = dg1

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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='XPERTHIS')
        msh.sending_facility = HD(hd_1='GHDC')
        msh.receiving_application = HD(hd_1='EAI')
        msh.receiving_facility = HD(hd_1='GHDC')
        msh.date_time_of_message = '20220710091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'GHDC20220710091500008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20220710091400'
        evn.operator_id = XCN(xcn_1='admin03', xcn_2='Delcourt', xcn_3='Isabelle')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='411522633', cx_4='GHDC', cx_5='PI'), CX(cx_1='89050916734', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'GILLES^François^D^^^M'
        pid.date_time_of_birth = '19890509'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = [
            XAD(xad_1='Boulevard Tirou 33', xad_3='Charleroi', xad_5='6000', xad_6='BE', xad_7='H'),
            XAD(xad_1='Boite postale 33', xad_3='Charleroi', xad_5='6000', xad_6='BE', xad_7='M'),
        ]
        pid.pid_13 = '^PRN^PH^^32^71^456789~^ORN^CP^^32^480^098765'
        pid.primary_language = CWE(cwe_1='FR')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='KAT')
        pid.pid_28 = 'N'
        pid.identity_unknown_indicator = 'BE'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GHDC', pl_2='CONS', pl_3='001', pl_4='GHDC')
        pv1.attending_doctor = XCN(xcn_1='66778899', xcn_2='Collignon', xcn_3='Thierry', xcn_5='Dr', xcn_8='INAMI')
        pv1.preadmit_test_indicator = CWE(cwe_1='AMB')
        pv1.vip_indicator = CWE(cwe_1='3')
        pv1.pending_location = PL(pl_1='20220710091500')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='XPERTHIS')
        msh.sending_facility = HD(hd_1='CHR_NAMUR')
        msh.receiving_application = HD(hd_1='EAI')
        msh.receiving_facility = HD(hd_1='CHR')
        msh.date_time_of_message = '20221101163000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'CHR20221101163000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20221101162800'
        evn.operator_id = XCN(xcn_1='admin04', xcn_2='Lefebvre', xcn_3='Michel')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='522633744', cx_4='CHR', cx_5='PI'), CX(cx_1='82091224563', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'LAURENT^Anne^S^^^Mme'
        pid.date_time_of_birth = '19820912'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rue de Bruxelles 22', xad_3='Namur', xad_5='5000', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^81^345678'
        pid.primary_language = CWE(cwe_1='FR')
        pid.marital_status = CWE(cwe_1='M')
        pid.identity_reliability_code = CWE(cwe_1='N')
        pid.taxonomic_classification_code = CWE(cwe_1='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHR', pl_2='USI', pl_3='002', pl_4='CHR')
        pv1.attending_doctor = XCN(xcn_1='77889900', xcn_2='Baudouin', xcn_3='Patrick', xcn_5='Dr', xcn_8='INAMI')
        pv1.preadmit_test_indicator = CWE(cwe_1='REA')
        pv1.vip_indicator = CWE(cwe_1='2')
        pv1.visit_number = CX(cx_1='77889900', cx_2='Baudouin', cx_3='Patrick', cx_5='Dr', cx_8='INAMI')
        pv1.financial_class = FC(fc_1='IN')
        pv1.diet_type = CWE(cwe_1='20221025090000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.military_partnership_code = '20221025'

        # .. assemble the full message ..
        msg = ADT_A02()
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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='XPERTHIS')
        msh.sending_facility = HD(hd_1='CHU_LIEGE')
        msh.receiving_application = HD(hd_1='LIS')
        msh.receiving_facility = HD(hd_1='CHU_LAB')
        msh.date_time_of_message = '20230201110000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CHU20230201110000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='633744855', cx_4='CHU', cx_5='PI'), CX(cx_1='94070314289', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='SIMON', xpn_2='Charlotte', xpn_4='Mme')
        pid.date_time_of_birth = '19940703'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rue Cathédrale 33', xad_3='Liege', xad_5='4000', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^4^6789012'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHU', pl_2='MED2', pl_3='008', pl_4='CHU')
        pv1.attending_doctor = XCN(xcn_1='88990011', xcn_2='Geerts', xcn_3='Antoine', xcn_5='Dr', xcn_8='INAMI')
        pv1.preadmit_test_indicator = CWE(cwe_1='MED')
        pv1.vip_indicator = CWE(cwe_1='4')

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
        orc.placer_order_number = EI(ei_1='ORD20230100')
        orc.filler_order_number = EI(ei_1='ORD20230100')
        orc.order_status = 'IP'
        orc.orc_8 = '1^^^20230201113000^^R'
        orc.orc_10 = '20230201110000'
        orc.orc_11 = 'admin05^Gustin^Isabelle'
        orc.enterers_location = PL(pl_1='88990011', pl_2='Geerts', pl_3='Antoine', pl_5='Dr', pl_8='INAMI')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20230100')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='NFS + formule', cwe_3='LN')
        obr.obr_6 = '20230201113000'
        obr.specimen_action_code = 'L'
        obr.relevant_clinical_information = CWE(cwe_1='fievre et asthenie')
        obr.obr_17 = '88990011^Geerts^Antoine^^Dr^^^INAMI'

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
        obr_2.placer_order_number = EI(ei_1='ORD20230100')
        obr_2.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Bilan metabolique', cwe_3='LN')
        obr_2.obr_6 = '20230201113000'
        obr_2.specimen_action_code = 'L'
        obr_2.obr_17 = '88990011^Geerts^Antoine^^Dr^^^INAMI'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD20230100')
        obr_3.universal_service_identifier = CWE(cwe_1='1988-5', cwe_2='CRP', cwe_3='LN')
        obr_3.obr_6 = '20230201113000'
        obr_3.specimen_action_code = 'L'
        obr_3.obr_17 = '88990011^Geerts^Antoine^^Dr^^^INAMI'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3]

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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='CHU_LAB')
        msh.receiving_application = HD(hd_1='XPERTHIS')
        msh.receiving_facility = HD(hd_1='CHU_LIEGE')
        msh.date_time_of_message = '20230202093000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CHU_LAB20230202093000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='633744855', cx_4='CHU', cx_5='PI'), CX(cx_1='94070314289', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='SIMON', xpn_2='Charlotte', xpn_4='Mme')
        pid.date_time_of_birth = '19940703'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rue Cathédrale 33', xad_3='Liege', xad_5='4000', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHU', pl_2='MED2', pl_3='008', pl_4='CHU')
        pv1.attending_doctor = XCN(xcn_1='88990011', xcn_2='Geerts', xcn_3='Antoine', xcn_5='Dr', xcn_8='INAMI')

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
        orc.placer_order_number = EI(ei_1='LAB20230200')
        orc.filler_order_number = EI(ei_1='LAB20230200')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20230200')
        obr.filler_order_number = EI(ei_1='LAB20230200')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='NFS + formule', cwe_3='LN')
        obr.obr_6 = '20230201113000'
        obr.obr_17 = '88990011^Geerts^Antoine^^Dr^^^INAMI'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocytes', cwe_3='LN')
        obx.obx_5 = '11.8'
        obx.units = CWE(cwe_1='10*9/L')
        obx.reference_range = '4.0-10.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20230202090000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrocytes', cwe_3='LN')
        obx_2.obx_5 = '4.32'
        obx_2.units = CWE(cwe_1='10*12/L')
        obx_2.reference_range = '3.80-5.50'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20230202090000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobine', cwe_3='LN')
        obx_3.obx_5 = '12.9'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '11.5-16.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20230202090000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrite', cwe_3='LN')
        obx_4.obx_5 = '38.6'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '36.0-46.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20230202090000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Thrombocytes', cwe_3='LN')
        obx_5.obx_5 = '298'
        obx_5.units = CWE(cwe_1='10*9/L')
        obx_5.reference_range = '150-400'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20230202090000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1988-5', cwe_2='CRP', cwe_3='LN')
        obx_6.obx_5 = '45.2'
        obx_6.units = CWE(cwe_1='mg/L')
        obx_6.reference_range = '0.0-5.0'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20230202090000'

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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='XPERTHIS')
        msh.sending_facility = HD(hd_1='GHDC')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='GHDC_RAD')
        msh.date_time_of_message = '20230315141500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'GHDC20230315141500005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='744855966', cx_4='GHDC', cx_5='PI'), CX(cx_1='87042315678', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='MARCHAND', xpn_2='Julien', xpn_4='M')
        pid.date_time_of_birth = '19870423'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue de Montigny 44', xad_3='Charleroi', xad_5='6000', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^71^567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GHDC', pl_2='RAD', pl_3='001', pl_4='GHDC')
        pv1.attending_doctor = XCN(xcn_1='99001122', xcn_2='Noel', xcn_3='François', xcn_5='Dr', xcn_8='INAMI')
        pv1.preadmit_test_indicator = CWE(cwe_1='RAD')
        pv1.vip_indicator = CWE(cwe_1='1')

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
        orc.placer_order_number = EI(ei_1='RAD20230200')
        orc.filler_order_number = EI(ei_1='RAD20230200')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20230315142000^^R'
        orc.orc_10 = '20230315141500'
        orc.orc_11 = 'admin06^Gustin^Sophie'
        orc.enterers_location = PL(pl_1='99001122', pl_2='Noel', pl_3='François', pl_5='Dr', pl_8='INAMI')
        orc.call_back_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_5='32', xtn_6='71', xtn_7='765432')
        orc.orc_17 = 'GHDC'
        orc.orc_18 = 'Boulevard Tirou 33^^Charleroi^^6000^BE'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20230200')
        obr.filler_order_number = EI(ei_1='RAD20230200')
        obr.universal_service_identifier = CWE(cwe_1='459003', cwe_2='RX Thorax face+profil', cwe_3='INAMI_NOM')
        obr.obr_6 = '20230315142000'
        obr.specimen_action_code = 'L'
        obr.relevant_clinical_information = CWE(cwe_1='douleur thoracique atypique')
        obr.obr_17 = '99001122^Noel^François^^Dr^^^INAMI'
        obr.placer_field_2 = 'RAD001'
        obr.result_status = '1^^^20230315142000^^R'

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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='CSJ_LAB')
        msh.receiving_application = HD(hd_1='XPERTHIS')
        msh.receiving_facility = HD(hd_1='CSJ_BXL')
        msh.date_time_of_message = '20230420100500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CSJ_LAB20230420100500009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='855966077', cx_4='CSJ', cx_5='PI'), CX(cx_1='92031526734', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='LACROIX', xpn_2='Marine', xpn_4='Mme')
        pid.date_time_of_birth = '19920315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rue Neuve 22', xad_3='Bruxelles', xad_5='1000', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CSJ', pl_2='CONS', pl_3='002', pl_4='CSJ')
        pv1.attending_doctor = XCN(xcn_1='00112233', xcn_2='Defays', xcn_3='Michel', xcn_5='Dr', xcn_8='INAMI')

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
        orc.placer_order_number = EI(ei_1='LAB20230300')
        orc.filler_order_number = EI(ei_1='LAB20230300')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20230300')
        obr.filler_order_number = EI(ei_1='LAB20230300')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Bilan metabolique complet', cwe_3='LN')
        obr.obr_6 = '20230420080000'
        obr.obr_17 = '00112233^Defays^Michel^^Dr^^^INAMI'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '6.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.9-5.8'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20230420093000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_2.obx_5 = '95'
        obx_2.units = CWE(cwe_1='umol/L')
        obx_2.reference_range = '62-106'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20230420093000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Uree', cwe_3='LN')
        obx_3.obx_5 = '7.0'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.5-7.5'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20230420093000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx_4.obx_5 = '139'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20230420093000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_5.obx_5 = '4.8'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20230420093000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALAT (GPT)', cwe_3='LN')
        obx_6.obx_5 = '52'
        obx_6.units = CWE(cwe_1='U/L')
        obx_6.reference_range = '0-41'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20230420093000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1920-8', cwe_2='ASAT (GOT)', cwe_3='LN')
        obx_7.obx_5 = '48'
        obx_7.units = CWE(cwe_1='U/L')
        obx_7.reference_range = '0-40'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20230420093000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Bilirubine totale', cwe_3='LN')
        obx_8.obx_5 = '22'
        obx_8.units = CWE(cwe_1='umol/L')
        obx_8.reference_range = '3-21'
        obx_8.interpretation_codes = CWE(cwe_1='H')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20230420093000'

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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='XPERTHIS')
        msh.sending_facility = HD(hd_1='CHR_NAMUR')
        msh.receiving_application = HD(hd_1='AGENDA')
        msh.receiving_facility = HD(hd_1='CHR')
        msh.date_time_of_message = '20230605090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'CHR20230605090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20230300')
        sch.appointment_reason = CWE(cwe_1='ROUTINE')
        sch.appointment_type = CWE(cwe_1='20')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='20', cne_4='20230612100000', cne_5='20230612102000')
        sch.placer_contact_location = PL(pl_1='23344556', pl_2='Tonglet', pl_3='Catherine', pl_5='Dr', pl_8='INAMI')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='966077188', cx_4='CHR', cx_5='PI'), CX(cx_1='88090127845', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='GIRARD', xpn_2='Amelie', xpn_4='Mme')
        pid.date_time_of_birth = '19880901'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1="Place de l'Ange 8", xad_3='Namur', xad_5='5000', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^81^678901'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CHR', pl_2='DERM', pl_3='001', pl_4='CHR')
        pv1.attending_doctor = XCN(xcn_1='23344556', xcn_2='Tonglet', xcn_3='Catherine', xcn_5='Dr', xcn_8='INAMI')
        pv1.preadmit_test_indicator = CWE(cwe_1='DER')
        pv1.vip_indicator = CWE(cwe_1='1')

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
        ais.universal_service_identifier = CWE(cwe_1='DERMCONS', cwe_2='Consultation Dermatologie', cwe_3='L')
        ais.start_date_time = '20230612100000'
        ais.duration = '20'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='CHR', pl_2='DERM', pl_3='001', pl_4='CHR')
        ail.filler_status_code = CWE(cwe_1='F')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.location_resource = location_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='XPERTHIS')
        msh.sending_facility = HD(hd_1='CHU_LIEGE')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='CHU_REG')
        msh.date_time_of_message = '20230801100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'CHU20230801100000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_PAM', ei_2='IHE')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20230801100000'
        evn.operator_id = XCN(xcn_1='admin07', xcn_2='Masson', xcn_3='Nathalie')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='077188299', cx_4='CHU', cx_5='PI'), CX(cx_1='03061226734', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'PICARD^Marie^T^^^Mme'
        pid.date_time_of_birth = '20030612'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rue Haute Sauvenière 6', xad_3='Liege', xad_5='4000', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^4^7890123~^ORN^CP^^32^487^234567~^NET^Internet^marie.picard@example.be'
        pid.primary_language = CWE(cwe_1='FR')
        pid.marital_status = CWE(cwe_1='S')
        pid.religion = CWE(cwe_1='KAT')
        pid.pid_28 = 'N'
        pid.identity_unknown_indicator = 'BE'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = '00998877^Vandenberghe^Alain^^Dr^^^INAMI'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='PICARD', xpn_2='Henri', xpn_5='M')
        nk1.relationship = CWE(cwe_1='FTH')
        nk1.address = XAD(xad_1='Rue Haute Sauvenière 6', xad_3='Liege', xad_5='4000', xad_6='BE', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^32^4^7890111'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin

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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='CHU_MICRO')
        msh.receiving_application = HD(hd_1='XPERTHIS')
        msh.receiving_facility = HD(hd_1='CHU_LIEGE')
        msh.date_time_of_message = '20230905153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CHU_MICRO20230905153000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='211311411', cx_4='CHU', cx_5='PI'), CX(cx_1='76031523178', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'DUPONT^Pierre^R^^^M'
        pid.date_time_of_birth = '19760315'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Quai de Rome 14', xad_3='Liege', xad_5='4000', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHU', pl_2='MED1', pl_3='012', pl_4='CHU')
        pv1.attending_doctor = XCN(xcn_1='22334455', xcn_2='Henrotte', xcn_3='Luc', xcn_5='Dr', xcn_8='INAMI')

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
        orc.placer_order_number = EI(ei_1='MICRO20230100')
        orc.filler_order_number = EI(ei_1='MICRO20230100')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MICRO20230100')
        obr.filler_order_number = EI(ei_1='MICRO20230100')
        obr.universal_service_identifier = CWE(cwe_1='600-7', cwe_2='Hemoculture', cwe_3='LN')
        obr.obr_6 = '20230904080000'
        obr.obr_17 = '22334455^Henrotte^Luc^^Dr^^^INAMI'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Identification bacterienne', cwe_3='LN')
        obx.obx_5 = '3092008^Staphylococcus aureus^SCT'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20230905140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Antibiogramme', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'Oxacilline: S (MSSA)'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20230905140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Antibiogramme', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='2')
        obx_3.obx_5 = 'Vancomycine: S'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20230905140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Antibiogramme', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='3')
        obx_4.obx_5 = 'Clindamycine: S'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20230905140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Antibiogramme', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='4')
        obx_5.obx_5 = 'Trimethoprime/Sulfamethoxazole: S'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20230905140000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Antibiogramme', cwe_3='LN')
        obx_6.observation_sub_id = OG(og_1='5')
        obx_6.obx_5 = 'Erythromycine: R'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20230905140000'

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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PATH')
        msh.sending_facility = HD(hd_1='GHDC_PATH')
        msh.receiving_application = HD(hd_1='XPERTHIS')
        msh.receiving_facility = HD(hd_1='GHDC')
        msh.date_time_of_message = '20231015160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'GHDC_PATH20231015160000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='744855966', cx_4='GHDC', cx_5='PI'), CX(cx_1='87042315678', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='MARCHAND', xpn_2='Julien', xpn_4='M')
        pid.date_time_of_birth = '19870423'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue de Montigny 44', xad_3='Charleroi', xad_5='6000', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GHDC', pl_2='CHIR', pl_3='003', pl_4='GHDC')
        pv1.attending_doctor = XCN(xcn_1='55667788', xcn_2='Wathelet', xcn_3='Yves', xcn_5='Dr', xcn_8='INAMI')

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
        orc.placer_order_number = EI(ei_1='PATH20230100')
        orc.filler_order_number = EI(ei_1='PATH20230100')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PATH20230100')
        obr.filler_order_number = EI(ei_1='PATH20230100')
        obr.universal_service_identifier = CWE(cwe_1='22634-0', cwe_2='Examen anatomopathologique', cwe_3='LN')
        obr.obr_6 = '20231010120000'
        obr.obr_17 = '55667788^Wathelet^Yves^^Dr^^^INAMI'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22634-0', cwe_2='Conclusion anatomopathologique', cwe_3='LN')
        obx.obx_5 = 'Biopsie colique: colite chronique active, pas de dysplasie, pas de malignite'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20231015150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Rapport anatomopathologique', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFJhcHBvcnQgYW5hdG9tb3BhdGhvbG9naXF1ZSkKL0NyZWF0b3IgKEdIREMgQW5hdG9tb3BhdGhvbG9naWUpCi9Qcm9kdWNlciAoWE9S'
            'R0kgQ2FyZSkKL0NyZWF0aW9uRGF0ZSAoRDoyMDIzMTAxNTE1MDAwMCswMScwMCcpCj4+CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9DYXRhbG9nIC9QYWdlcyAzIDAgUiA+PgplbmRv'
            'YmoKMyAwIG9iago8PCAvVHlwZSAvUGFnZXMgL0tpZHMgWzQgMCBSXSAvQ291bnQgMSA+PgplbmRvYmoKNCAwIG9iago8PCAvVHlwZSAvUGFnZSAvUGFyZW50IDMgMCBSIC9NZWRpYUJv'
            'eCBbMCAwIDU5NSA4NDJdID4+CmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDE4NiAwMDAwMCBuIAowMDAwMDAwMjM3'
            'IDAwMDAwIG4gCjAwMDAwMDAyOTYgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA1IC9Sb290IDIgMCBSID4+CnN0YXJ0eHJlZgozODYKJSVFT0YK'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20231015150000'

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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='CHR_RAD')
        msh.receiving_application = HD(hd_1='XPERTHIS')
        msh.receiving_facility = HD(hd_1='CHR_NAMUR')
        msh.date_time_of_message = '20231120110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CHR_RAD20231120110000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='522633744', cx_4='CHR', cx_5='PI'), CX(cx_1='82091224563', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'LAURENT^Anne^S^^^Mme'
        pid.date_time_of_birth = '19820912'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rue de Bruxelles 22', xad_3='Namur', xad_5='5000', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CHR', pl_2='RAD', pl_3='001', pl_4='CHR')
        pv1.attending_doctor = XCN(xcn_1='99001122', xcn_2='Noel', xcn_3='François', xcn_5='Dr', xcn_8='INAMI')

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
        orc.placer_order_number = EI(ei_1='RAD20230400')
        orc.filler_order_number = EI(ei_1='RAD20230400')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20230400')
        obr.filler_order_number = EI(ei_1='RAD20230400')
        obr.universal_service_identifier = CWE(cwe_1='24725-4', cwe_2='CT abdomen avec contraste', cwe_3='LN')
        obr.obr_6 = '20231118090000'
        obr.obr_17 = '99001122^Noel^François^^Dr^^^INAMI'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='59776-5', cwe_2='Compte-rendu radiologique', cwe_3='LN')
        obx.obx_5 = "CT abdominal: foie, rate et reins sans anomalie. Pas d'adenopathie retroperitoneale. Pas d'epanchement. Conclusion: examen normal."
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20231120100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Rapport radiologique', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFJhcHBvcnQgcmFkaW9sb2dpcXVlKQovQ3JlYXRvciAoQ0hSIE5hbXVyIFJhZGlvbG9naWUpCi9Qcm9kdWNlciAoWE9SR0kgQ2FyZSkK'
            'L0NyZWF0aW9uRGF0ZSAoRDoyMDIzMTEyMDEwMDAwMCswMScwMCcpCj4+CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9DYXRhbG9nIC9QYWdlcyAzIDAgUiA+PgplbmRvYmoKMyAwIG9i'
            'ago8PCAvVHlwZSAvUGFnZXMgL0tpZHMgWzQgMCBSXSAvQ291bnQgMSA+PgplbmRvYmoKNCAwIG9iago8PCAvVHlwZSAvUGFnZSAvUGFyZW50IDMgMCBSIC9NZWRpYUJveCBbMCAwIDU5'
            'NSA4NDJdID4+CmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDE3OSAwMDAwMCBuIAowMDAwMDAwMjMwIDAwMDAwIG4g'
            'CjAwMDAwMDAyODkgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA1IC9Sb290IDIgMCBSID4+CnN0YXJ0eHJlZgozNzkKJSVFT0YK'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20231120100000'

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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='XPERTHIS')
        msh.sending_facility = HD(hd_1='CHU_LIEGE')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='CHU_REG')
        msh.date_time_of_message = '20231201080000'
        msh.message_type = MSG(msg_1='MFN', msg_2='M02', msg_3='MFN_M02')
        msh.message_control_id = 'CHU20231201080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build MFI ..
        mfi = MFI()
        mfi.master_file_identifier = CWE(cwe_1='PRA', cwe_2='Practitioners', cwe_3='HL70175')
        mfi.master_file_application_identifier = HD(hd_1='CHU_ARTS')
        mfi.file_level_event_code = 'UPD'
        mfi.response_level_code = 'NE'

        # .. build MFE ..
        mfe = MFE()
        mfe.record_level_event_code = 'MAD'
        mfe.mfn_control_id = '20231201080000'
        mfe.effective_date_time = '20231201'
        mfe.mfe_5 = '22334455^Henrotte^Luc^^Dr'

        # .. build STF ..
        stf = STF()
        stf.primary_key_value_stf = CWE(cwe_1='22334455', cwe_2='Henrotte', cwe_3='Luc', cwe_5='Dr', cwe_7='INAMI')
        stf.staff_identifier_list = CX(cx_1='22334455')
        stf.staff_name = [XPN(xpn_1='MED', xpn_2='Medecine Interne', xpn_3='L'), XPN(xpn_1='CAR', xpn_2='Cardiologie', xpn_3='L')]
        stf.staff_type = CWE(cwe_1='Dr')
        stf.administrative_sex = CWE(cwe_1='M')
        stf.date_time_of_birth = '19700720'
        stf.active_inactive_flag = 'A'
        stf.hospital_service_stf = CWE(cwe_2='WPN', cwe_3='PH', cwe_5='32', cwe_6='4', cwe_7='2345678')
        stf.stf_10 = 'Quai de Rome 14^^Liege^^4000^BE^B'
        stf.office_home_address_birthplace = XAD(xad_1='19980601')

        # .. build the MF_STAFF group ..
        mf_staff = MfnM02MfStaff()
        mf_staff.mfe = mfe
        mf_staff.stf = stf

        # .. build MFE ..
        mfe_2 = MFE()
        mfe_2.record_level_event_code = 'MAD'
        mfe_2.mfn_control_id = '20231201080000'
        mfe_2.effective_date_time = '20231201'
        mfe_2.mfe_5 = '33445566^Franssen^Véronique^^Dr'

        # .. build STF ..
        stf_2 = STF()
        stf_2.primary_key_value_stf = CWE(cwe_1='33445566', cwe_2='Franssen', cwe_3='Véronique', cwe_5='Dr', cwe_7='INAMI')
        stf_2.staff_identifier_list = CX(cx_1='33445566')
        stf_2.staff_name = XPN(xpn_1='MED', xpn_2='Medecine Interne', xpn_3='L')
        stf_2.staff_type = CWE(cwe_1='Dr')
        stf_2.administrative_sex = CWE(cwe_1='F')
        stf_2.date_time_of_birth = '19730415'
        stf_2.active_inactive_flag = 'A'
        stf_2.hospital_service_stf = CWE(cwe_2='WPN', cwe_3='PH', cwe_5='32', cwe_6='4', cwe_7='3456789')
        stf_2.stf_10 = 'Rue Cathédrale 33^^Liege^^4000^BE^B'
        stf_2.office_home_address_birthplace = XAD(xad_1='20020901')

        # .. build the MF_STAFF group ..
        mf_staff_2 = MfnM02MfStaff()
        mf_staff_2.mfe = mfe_2
        mf_staff_2.stf = stf_2

        # .. assemble the full message ..
        msg = MFN_M02()
        msg.msh = msh
        msg.mfi = mfi
        msg.mf_staff = [mf_staff, mf_staff_2]

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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='XPERTHIS')
        msh.sending_facility = HD(hd_1='CHU_LIEGE')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='CHU_REG')
        msh.date_time_of_message = '20231215120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'CHU20231215120000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_PAM', ei_2='IHE')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20231215120000'
        evn.operator_id = XCN(xcn_1='admin08', xcn_2='Masson', xcn_3='Eric')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='211311411', cx_4='CHU', cx_5='PI'), CX(cx_1='76031523178', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'DUPONT^Pierre^R^^^M'
        pid.date_time_of_birth = '19760315'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Quai de Rome 14', xad_3='Liege', xad_5='4000', xad_6='BE', xad_7='H')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='999888777', cx_4='CHU', cx_5='PI')
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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='STLUC_LAB')
        msh.receiving_application = HD(hd_1='XPERTHIS')
        msh.receiving_facility = HD(hd_1='STLUC_BXL')
        msh.date_time_of_message = '20231005110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'STLUC_LAB20231005110000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='311411522', cx_4='STLUC', cx_5='PI'), CX(cx_1='83061829845', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'MOREAU^Isabelle^G^^^Mme'
        pid.date_time_of_birth = '19830618'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Chaussée de Charleroi 88', xad_3='Saint-Gilles', xad_5='1060', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='STLUC', pl_2='ENDO', pl_3='001', pl_4='STLUC')
        pv1.attending_doctor = XCN(xcn_1='21223344', xcn_2='Carlier', xcn_3='Bruno', xcn_5='Dr', xcn_8='INAMI')

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
        orc.placer_order_number = EI(ei_1='LAB20230400')
        orc.filler_order_number = EI(ei_1='LAB20230400')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20230400')
        obr.filler_order_number = EI(ei_1='LAB20230400')
        obr.universal_service_identifier = CWE(cwe_1='10230-1', cwe_2='Bilan thyroidien', cwe_3='LN')
        obr.obr_6 = '20231005080000'
        obr.obr_17 = '21223344^Carlier^Bruno^^Dr^^^INAMI'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '0.35'
        obx.units = CWE(cwe_1='mUI/L')
        obx.reference_range = '0.27-4.20'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20231005100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='T4 libre', cwe_3='LN')
        obx_2.obx_5 = '22.5'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '12.0-22.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20231005100000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='T3 libre', cwe_3='LN')
        obx_3.obx_5 = '6.8'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '3.1-6.8'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20231005100000'

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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='XPERTHIS')
        msh.sending_facility = HD(hd_1='CHU_LIEGE')
        msh.receiving_application = HD(hd_1='VACCINNET')
        msh.receiving_facility = HD(hd_1='EHEALTH_BE')
        msh.date_time_of_message = '20231001100000'
        msh.message_type = MSG(msg_1='VXU', msg_2='V04', msg_3='VXU_V04')
        msh.message_control_id = 'CHU20231001100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='211311411', cx_4='CHU', cx_5='PI'), CX(cx_1='76031523178', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'DUPONT^Pierre^R^^^M'
        pid.date_time_of_birth = '19760315'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Quai de Rome 14', xad_3='Liege', xad_5='4000', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CHU', pl_2='VACC', pl_3='001', pl_4='CHU')

        # .. build the PATIENT_VISIT group ..
        patient_visit = VxuV04PatientVisit()
        patient_visit.pv1 = pv1

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='VACC20230100')
        orc.order_status = 'CM'
        orc.orc_11 = '22334455^Henrotte^Luc^^Dr^^^INAMI'

        # .. build RXA ..
        rxa = RXA()
        rxa.give_sub_id_counter = '0'
        rxa.administration_sub_id_counter = '1'
        rxa.date_time_start_of_administration = '20231001093000'
        rxa.date_time_end_of_administration = '20231001093000'
        rxa.administered_code = CWE(cwe_1='140', cwe_2='Influenza quadrivalent', cwe_3='CVX')
        rxa.administered_amount = '1'
        rxa.administered_units = CWE(cwe_1='mL')
        rxa.administered_dosage_form = CWE(cwe_1='IM')
        rxa.administered_strength = 'LOT2023FL01'
        rxa.administered_strength_units = CWE(cwe_1='20240630')
        rxa.rxa_15 = 'SNF^Sanofi Pasteur^MVX'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IM', cwe_2='Intramusculaire', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='LD', cwe_2='Deltoide Gauche', cwe_3='HL70163')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='64994-7', cwe_2='Source de financement vaccin', cwe_3='LN')
        obx.obx_5 = 'VXC30^Etat Autre^CDCPHINVS'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = VxuV04Observation()
        observation.obx = obx

        # .. build the ORDER group ..
        order = VxuV04Order()
        order.orc = orc
        order.rxa = rxa
        order.rxr = rxr
        order.observation = observation

        # .. assemble the full message ..
        msg = VXU_V04()
        msg.msh = msh
        msg.pid = pid
        msg.patient_visit = patient_visit
        msg.order = order

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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='GHDC_LAB')
        msh.receiving_application = HD(hd_1='XPERTHIS')
        msh.receiving_facility = HD(hd_1='GHDC')
        msh.date_time_of_message = '20231201093000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'GHDC_LAB20231201093000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='411522633', cx_4='GHDC', cx_5='PI'), CX(cx_1='89050916734', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'GILLES^François^D^^^M'
        pid.date_time_of_birth = '19890509'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Boulevard Tirou 33', xad_3='Charleroi', xad_5='6000', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GHDC', pl_2='CHIR', pl_3='002', pl_4='GHDC')
        pv1.attending_doctor = XCN(xcn_1='66778899', xcn_2='Collignon', xcn_3='Thierry', xcn_5='Dr', xcn_8='INAMI')

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
        orc.placer_order_number = EI(ei_1='LAB20230500')
        orc.filler_order_number = EI(ei_1='LAB20230500')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20230500')
        obr.filler_order_number = EI(ei_1='LAB20230500')
        obr.universal_service_identifier = CWE(cwe_1='38875-1', cwe_2='Bilan de coagulation', cwe_3='LN')
        obr.obr_6 = '20231201080000'
        obr.obr_17 = '66778899^Collignon^Thierry^^Dr^^^INAMI'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='Temps de prothrombine', cwe_3='LN')
        obx.obx_5 = '13.2'
        obx.units = CWE(cwe_1='s')
        obx.reference_range = '11.0-13.5'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20231201090000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '1.05'
        obx_2.reference_range = '0.80-1.20'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20231201090000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='aPTT', cwe_3='LN')
        obx_3.obx_5 = '32'
        obx_3.units = CWE(cwe_1='s')
        obx_3.reference_range = '25-36'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20231201090000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3255-7', cwe_2='Fibrinogene', cwe_3='LN')
        obx_4.obx_5 = '3.2'
        obx_4.units = CWE(cwe_1='g/L')
        obx_4.reference_range = '2.0-4.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20231201090000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='48065-7', cwe_2='D-Dimeres', cwe_3='LN')
        obx_5.obx_5 = '0.45'
        obx_5.units = CWE(cwe_1='mg/L')
        obx_5.reference_range = '0.00-0.50'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20231201090000'

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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARDIO')
        msh.sending_facility = HD(hd_1='CHR_CARD')
        msh.receiving_application = HD(hd_1='XPERTHIS')
        msh.receiving_facility = HD(hd_1='CHR_NAMUR')
        msh.date_time_of_message = '20240201140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CHR_CARD20240201140000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='522633744', cx_4='CHR', cx_5='PI'), CX(cx_1='82091224563', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'LAURENT^Anne^S^^^Mme'
        pid.date_time_of_birth = '19820912'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rue de Bruxelles 22', xad_3='Namur', xad_5='5000', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHR', pl_2='CARD', pl_3='001', pl_4='CHR')
        pv1.attending_doctor = XCN(xcn_1='77889900', xcn_2='Baudouin', xcn_3='Patrick', xcn_5='Dr', xcn_8='INAMI')

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
        orc.placer_order_number = EI(ei_1='ECG20240100')
        orc.filler_order_number = EI(ei_1='ECG20240100')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ECG20240100')
        obr.filler_order_number = EI(ei_1='ECG20240100')
        obr.universal_service_identifier = CWE(cwe_1='93000', cwe_2='Electrocardiogramme', cwe_3='INAMI_NOM')
        obr.obr_6 = '20240201130000'
        obr.obr_17 = '77889900^Baudouin^Patrick^^Dr^^^INAMI'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='93000', cwe_2='Interpretation ECG', cwe_3='L')
        obx.obx_5 = "Rythme sinusal 78/min. Axe normal. Pas d'anomalie de repolarisation. Pas de trouble de conduction. Conclusion: ECG normal."
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240201133000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Rapport ECG', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFJhcHBvcnQgRUNHKQovQ3JlYXRvciAoQ0hSIE5hbXVyIENhcmRpb2xvZ2llKQovUHJvZHVjZXIgKFpPUkdJIENhcmUpCi9DcmVhdGlv'
            'bkRhdGUgKEQ6MjAyNDAyMDExMzAwMDArMDEnMDAnKQo+PgplbmRvYmoKMiAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMyAwIFIgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5'
            'cGUgL1BhZ2VzIC9LaWRzIFs0IDAgUl0gL0NvdW50IDEgPj4KZW5kb2JqCjQgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAzIDAgUiAvTWVkaWFCb3ggWzAgMCA1OTUgODQyXSA+'
            'PgplbmRvYmoKeHJlZgowIDUKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAxNzMgMDAwMDAgbiAKMDAwMDAwMDIyNCAwMDAwMCBuIAowMDAwMDAw'
            'MjgzIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNSAvUm9vdCAyIDAgUiA+PgpzdGFydHhyZWYKMzczCiUlRU9GCg=='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240201133000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='8867-4', cwe_2='Frequence cardiaque', cwe_3='LN')
        obx_3.obx_5 = '78'
        obx_3.units = CWE(cwe_1='/min')
        obx_3.reference_range = '60-100'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240201133000'

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
    """ Based on live/be/be-zorgi-xperthis.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='XPERTHIS')
        msh.sending_facility = HD(hd_1='CHU_LIEGE')
        msh.receiving_application = HD(hd_1='SUMEHR')
        msh.receiving_facility = HD(hd_1='EHEALTH_BE')
        msh.date_time_of_message = '20240115160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CHU20240115160000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'FRA'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='211311411', cx_4='CHU', cx_5='PI'), CX(cx_1='76031523178', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'DUPONT^Pierre^R^^^M'
        pid.date_time_of_birth = '19760315'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Quai de Rome 14', xad_3='Liege', xad_5='4000', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHU', pl_2='MED1', pl_3='012', pl_4='CHU')
        pv1.attending_doctor = XCN(xcn_1='22334455', xcn_2='Henrotte', xcn_3='Luc', xcn_5='Dr', xcn_8='INAMI')

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
        orc.placer_order_number = EI(ei_1='DOC20240001')
        orc.filler_order_number = EI(ei_1='DOC20240001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='DOC20240001')
        obr.filler_order_number = EI(ei_1='DOC20240001')
        obr.universal_service_identifier = CWE(cwe_1='34133-9', cwe_2='Lettre de sortie', cwe_3='LN')
        obr.obr_6 = '20240115150000'
        obr.obr_17 = '22334455^Henrotte^Luc^^Dr^^^INAMI'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='34133-9', cwe_2='Resume de sortie', cwe_3='LN')
        obx.obx_5 = (
            'Patient admis pour pneumonie communautaire le 05/01/2024. Traitement par amoxicilline/clavulanate IV puis relais PO. Evolution favorable. So'
            'rtie le 15/01/2024.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240115150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Lettre de sortie', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKExldHRyZSBkZSBzb3J0aWUpCi9DcmVhdG9yIChDSFUgZGUgTGllZ2UpCi9Qcm9kdWNlciAoWk9SR0kgQ2FyZSkKL0NyZWF0aW9uRGF0'
            'ZSAoRDoyMDI0MDExNTE1MDAwMCswMScwMCcpCj4+CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9DYXRhbG9nIC9QYWdlcyAzIDAgUiA+PgplbmRvYmoKMyAwIG9iago8PCAvVHlwZSAv'
            'UGFnZXMgL0tpZHMgWzQgMCBSXSAvQ291bnQgMSA+PgplbmRvYmoKNCAwIG9iago8PCAvVHlwZSAvUGFnZSAvUGFyZW50IDMgMCBSIC9NZWRpYUBveCBbMCAwIDU5NSA4NDJdID4+CmVu'
            'ZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDE2NiAwMDAwMCBuIAowMDAwMDAwMjE3IDAwMDAwIG4gCjAwMDAwMDAyNzYg'
            'MDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA1IC9Sb290IDIgMCBSID4+CnN0YXJ0eHJlZgozNjYKJSVFT0YK'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240115150000'

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
