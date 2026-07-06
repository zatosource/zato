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
from zato.hl7v2.v2_9.datatypes import AUI, CNE, CWE, CX, EI, EIP, FC, HD, MOC, MSG, OG, PL, PLN, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA01Observation, AdtA01Procedure, AdtA05NextOfKin, MdmT02Observation, MfnM02MfStaff, \
    OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, \
    OruR01PatientResult, OruR01Visit, SiuS12GeneralResource, SiuS12LocationResource, SiuS12Patient, SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A05, MDM_T02, MFN_M02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIG, AIL, AIP, AIS, AL1, DG1, EVN, GT1, IN1, IN2, MFE, MFI, MSH, NK1, NTE, OBR, OBX, ORC, PD1, PID, PR1, PRA, PRT, PV1, \
    PV2, RGS, ROL, SCH, STF, TXA
from zato.hl7v2.z_segments import ZBE, ZFD

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('be', 'be-amaron.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/be/be-amaron.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.msh_2 = '^~&'
        msh.sending_application = HD(hd_1='MESA_ADT')
        msh.sending_facility = HD(hd_1='XYZ_ADMITTING')
        msh.receiving_application = HD(hd_1='iFW')
        msh.receiving_facility = HD(hd_1='ZYX_HOSPITAL')
        msh.message_type = MSG(msg_1='ADT', msg_2='A04')
        msh.message_control_id = '214213'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.msh_20 = ''

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '202601010800'
        evn.event_occurred = '202601010800'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '2331'
        pid.pid_2 = '56'
        pid.patient_identifier_list = CX(cx_1='8294')
        pid.pid_4 = '85071534218^^^^NN'
        pid.patient_name = XPN(xpn_1='Peeters', xpn_2='Wim', xpn_5='Mijnheer')
        pid.mothers_maiden_name = XPN(xpn_1='Janssens', xpn_2='Lies')
        pid.date_time_of_birth = '19740926'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kerkstraat 47', xad_3='Mechelen', xad_5='2800', xad_6='BE', xad_7='Home')
        pid.pid_13 = '+32475123456^^^^^^+3215234567'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='Single')
        pid.patient_account_number = CX(cx_1='91567', cx_5='VN')
        pid.pid_19 = '1974092630401'
        pid.citizenship = CWE(cwe_1='BE')
        pid.patient_death_indicator = 'N'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='WILLEMS', xpn_2='GEORGES', xpn_3='T')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.start_date = '20260105'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.referring_doctor = XCN(xcn_1='6212', xcn_2='CLAES', xcn_3='HENDRIK', xcn_4='R', xcn_6='DR')
        pv1.visit_number = CX(cx_1='V1295', cx_4='ADT1')
        pv1.admit_date_time = '202601010800'
        pv1.pv1_52 = ''

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='ABDOMINAL PAIN')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'HD'
        obx.observation_identifier = CWE(cwe_1='SR Instance UID')
        obx.obx_5 = '1.234567.3.3000.42.3.2'
        obx.observation_result_status = 'F'
        obx.obx_17 = ''

        # .. build the OBSERVATION group ..
        observation = AdtA01Observation()
        observation.obx = obx

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_code_mnemonic_description = CWE(cwe_2='PENICILLIN')
        al1.allergy_reaction_code = ['PRODUCES HIVES', 'RASH']

        # .. build AL1 ..
        al1_2 = AL1()
        al1_2.set_id_al1 = '2'
        al1_2.allergen_code_mnemonic_description = CWE(cwe_2='CAT DANDER')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '001'
        dg1.dg1_2 = 'I9'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='1550')
        dg1.dg1_4 = 'MAL NEO LIVER, PRIMARY'
        dg1.diagnosis_date_time = '20260501103005'
        dg1.diagnosis_type = CWE(cwe_1='F')
        dg1.dg1_8 = ''

        # .. build PR1 ..
        pr1 = PR1()
        pr1.set_id_pr1 = '2234'
        pr1.pr1_2 = 'M11'
        pr1.procedure_code = CNE(cne_1='111', cne_2='CODE151')
        pr1.pr1_4 = 'COMMON PROCEDURES'
        pr1.procedure_date_time = '202609081123'

        # .. build ROL ..
        rol = ROL()
        rol.rol_1 = '45^RECORDER^ROLE MASTER LIST'
        rol.rol_2 = 'AD'
        rol.rol_3 = 'CP'
        rol.rol_4 = 'MAES^INGRID^SOFIE'
        rol.rol_5 = '202605011201'

        # .. build the PROCEDURE group ..
        procedure = AdtA01Procedure()
        procedure.pr1 = pr1
        procedure.rol = rol

        # .. build GT1 ..
        gt1 = GT1()
        gt1.set_id_gt1 = '1122'
        gt1.guarantor_number = CX(cx_1='1519')
        gt1.guarantor_name = XPN(xpn_1='GOOSSENS', xpn_2='PIETER', xpn_3='J')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '001'
        in1.health_plan_id = CWE(cwe_1='A468')
        in1.insurance_company_id = CX(cx_1='2345')
        in1.insurance_company_name = XON(xon_1='BCNE')
        in1.group_name = XON(xon_1='243098')

        # .. build IN2 ..
        in2 = IN2()
        in2.insureds_employee_id = CX(cx_1='ID2662112')
        in2.insureds_social_security_number = 'SSN85071534218'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1
        insurance.in2 = in2

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.observation = observation
        msg.al1 = [al1, al1_2]
        msg.dg1 = dg1
        msg.procedure = procedure
        msg.gt1 = gt1
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
    """ Based on live/be/be-amaron.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PatientManager')
        msh.sending_facility = HD(hd_1='IHE')
        msh.receiving_application = HD(hd_1='PatientManager')
        msh.receiving_facility = HD(hd_1='PAM_F')
        msh.date_time_of_message = '20260325194938'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = '20260325194938'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5', vid_2='FRA', vid_3='2.10')
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260325194938'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='82081012345', cx_4='ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO', cx_5='INS')
        pid.patient_name = XPN(xpn_1='DUPONT', xpn_2='HENRI-LOUIS', xpn_3='GASTON', xpn_7='L')
        pid.date_time_of_birth = '20080324'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Avenue Louise 15', xad_3='Bruxelles', xad_5='1050', xad_6='BEL', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='N')

        # .. build ZFD ..
        zfd = ZFD()
        zfd.zfd_3 = 'N'
        zfd.zfd_4 = 'N'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [zfd]

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
    """ Based on live/be/be-amaron.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MB')
        msh.sending_facility = HD(hd_1='MB')
        msh.receiving_application = HD(hd_1='PatientManager')
        msh.receiving_facility = HD(hd_1='PAM_FR')
        msh.date_time_of_message = '20260706113531'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = '6'
        msh.processing_id = PT(pt_1='D')
        msh.version_id = VID(vid_1='2.5', vid_2='FRA', vid_3='2.10')
        msh.character_set = 'UNICODE UTF-8'
        msh.principal_language_of_message = CWE(cwe_1='FR')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260706113531'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='81f6df3a-c3bf-45a8-b9dc-9dab702e78e7', cx_4='&&M', cx_5='PI')
        pid.patient_name = [XPN(xpn_1='LAMBERT', xpn_2='FRANCOISE', xpn_7='D', xpn_8='A'), XPN(xpn_1='RENARD', xpn_2='COLETTE', xpn_7='L', xpn_8='A')]
        pid.date_time_of_birth = '19980804'
        pid.administrative_sex = CWE(cwe_1='U')
        pid.patient_address = XAD(xad_1='Rue de Namur 22', xad_7='H')
        pid.patient_death_indicator = 'N'
        pid.identity_reliability_code = CWE(cwe_1='PROV')
        pid.last_update_date_time = '20260706113531'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.living_arrangement = CWE(cwe_1='U')
        pd1.protection_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='N')

        # .. build ZFD ..
        zfd = ZFD()
        zfd.zfd_3 = 'N'
        zfd.zfd_4 = 'N'
        zfd.zfd_5 = 'SM'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.pv1 = pv1
        msg.extra_segments = [zfd]

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
    """ Based on live/be/be-amaron.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PAMSimulator')
        msh.sending_facility = HD(hd_1='IHE')
        msh.receiving_application = HD(hd_1='Gazelle')
        msh.receiving_facility = HD(hd_1='IHE_Intl')
        msh.date_time_of_message = '20260532133752'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = '20260532133752'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260532133752'
        evn.event_occurred = '20260532133752'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='EET-64995', cx_4='DDS&1.3.6.1.4.1.12559.11.36.9&ISO', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Moreau', xpn_2='Alberto', xpn_7='L')
        pid.mothers_maiden_name = XPN(xpn_1='Lejeune', xpn_7='M')
        pid.date_time_of_birth = '20170816'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_6='BEL')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='R')
        pv1.admission_type = CWE(cwe_1='L')
        pv1.attending_doctor = XCN(xcn_1='21211520062', xcn_2='Simon', xcn_3='Jacques')
        pv1.referring_doctor = XCN(xcn_1='21112993310', xcn_2='Marchand', xcn_3='Nathalie')
        pv1.admitting_doctor = XCN(xcn_1='21113226833', xcn_2='Dubois', xcn_3='Yves')
        pv1.visit_number = CX(cx_1='VN2882', cx_4='GZL_INTEROP&2.16.840.1.113883.2.8.3.7&ISO', cx_5='VN')
        pv1.visit_indicator = CWE(cwe_1='V')

        # .. build ZBE ..
        zbe = ZBE()
        zbe.zbe_1 = 'MOV4310^GZL_INTEROP^2.16.840.1.113883.2.8.3.7^ISO'
        zbe.zbe_2 = '20260532133752'
        zbe.zbe_4 = 'INSERT'
        zbe.zbe_5 = 'N'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [zbe]

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
    """ Based on live/be/be-amaron.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PAS')
        msh.sending_facility = HD(hd_1='RCB')
        msh.receiving_application = HD(hd_1='ROUTE')
        msh.receiving_facility = HD(hd_1='ROUTE')
        msh.date_time_of_message = '202601021215'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = '24514002431564449186'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.sequence_number = '0'
        msh.continuation_pointer = '20260102121557'
        msh.country_code = 'BEL'
        msh.character_set = 'UNICODE'
        msh.principal_language_of_message = CWE(cwe_1='NL')
        msh.message_profile_identifier = EI(ei_1='iTKv1.0')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '202601021213'
        evn.evn_5 = '72041825391^De Smedt^Charlotte^^Mevr^^UZG'
        evn.event_occurred = '202601021213'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='93060712345', cx_4='RIZIV')
        pid.patient_name = XPN(xpn_1='MERTENS', xpn_2='PATRICIA', xpn_3='ROSALIE', xpn_5='MEVR', xpn_7='L')
        pid.mothers_maiden_name = XPN(xpn_1='COPPENS', xpn_2='ANNELIE', xpn_3='T')
        pid.date_time_of_birth = '197211191621'
        pid.administrative_sex = CWE(cwe_1='2')
        pid.patient_address = XAD(xad_1='Grote Markt 41', xad_3='Antwerpen', xad_5='2000', xad_6='BEL', xad_7='H')
        pid.pid_13 = '+32489567890'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='C22')
        pid.ethnic_group = CWE(cwe_1='A')
        pid.birth_place = 'Antwerpen'
        pid.multiple_birth_indicator = 'N'
        pid.citizenship = CWE(cwe_1='BEL')
        pid.pid_28 = 'BEL'
        pid.identity_reliability_code = CWE(cwe_1='ED')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'HUISARTSENPRAKTIJK CENTRUM^^Y06601'
        pd1.pd1_4 = 'G6723019^Jacobs^Reginald^^^Dr^^^RIZIV'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '2'
        nk1.name = XPN(xpn_1='MERTENS', xpn_2='VICTORIA', xpn_5='MEVR', xpn_7='L')
        nk1.relationship = CWE(cwe_1='16')
        nk1.address = XAD(xad_1='Grote Markt 41', xad_3='Antwerpen', xad_5='2000', xad_6='BEL', xad_7='H')
        nk1.nk1_5 = '+32489567890'
        nk1.administrative_sex = CWE(cwe_1='1')
        nk1.date_time_of_birth = '196311111513'
        nk1.primary_language = CWE(cwe_1='NL')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='N')
        pv1.pv1_3 = ''

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='Z88.5')
        al1.allergy_severity_code = CWE(cwe_1='5')
        al1.al1_6 = '199807011755'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.al1 = al1

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
    """ Based on live/be/be-amaron.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='P0241')
        msh.sending_facility = HD(hd_1='UZ_GENT')
        msh.receiving_application = HD(hd_1='UZ_GENT_TIE')
        msh.receiving_facility = HD(hd_1='UZ_GENT')
        msh.date_time_of_message = '20260209170901'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31')
        msh.message_control_id = 'R222222230U5194604622222222'
        msh.version_id = VID(vid_1='2.3')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260209170901'
        evn.operator_id = XCN(
            xcn_1='212222',
            xcn_2='Willems',
            xcn_3='Trevor',
            xcn_9='PERSONNEL PRIMARY IDENTIFIER',
            xcn_10='Personnel',
            xcn_13='Personnel Primary Identifier',
        )

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '888888^^^UZ Gent Case Note Number^MRN'
        pid.patient_identifier_list = [CX(cx_1='888887', cx_4='UZ Gent Case Note Number', cx_5='CNN'), CX(cx_1='111111', cx_4='Person ID', cx_5='Person ID')]
        pid.patient_name = XPN(xpn_1='DE SMEDT', xpn_2='Fatima', xpn_5='Mevr', xpn_7='Current')
        pid.date_time_of_birth = '19850707000000'
        pid.administrative_sex = CWE(cwe_1='Female')
        pid.patient_address = XAD(xad_1='Coupure Links 1', xad_3='Gent', xad_5='9000', xad_7='home')
        pid.pid_13 = '+32 9 332 2111^Home^Tel~+32476111222^Mobile Number^Tel'
        pid.pid_14 = '^Business'
        pid.primary_language = CWE(cwe_1='Dutch')
        pid.religion = CWE(cwe_1='Not Known')
        pid.patient_account_number = CX(cx_1='888888', cx_4='UZ Gent FIN', cx_5='Encounter No.')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'HUISARTSENPRAKTIJK KOUTER^^F84040'
        pd1.pd1_4 = 'G88888888^GOOSSENS^MARGARET'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='DE SMEDT', xpn_2='Tariq', xpn_7='Current')
        nk1.address = XAD(xad_1='Coupure Links 1', xad_3='Gent', xad_5='9000')
        nk1.nk1_5 = '+32476222333'
        nk1.contact_role = CWE(cwe_1='Next of Kin')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='Inpatient')
        pv1.assigned_patient_location = PL(pl_1='UZG AE OMU', pl_2='OMU B', pl_3='Bed 03', pl_4='UZ GENT', pl_6='Bed(s)', pl_7='UZ Gent')
        pv1.admission_type = CWE(cwe_1='Emergency')
        pv1.attending_doctor = XCN(xcn_1='2233445', xcn_2='Claes', xcn_3='Omar', xcn_9='PERSONNEL PRIMARY IDENTIFIER')
        pv1.referring_doctor = XCN(xcn_1='4444555', xcn_2='Janssens', xcn_3='Priya', xcn_9='PERSONNEL PRIMARY IDENTIFIER')
        pv1.hospital_service = CWE(cwe_1='Accident and Emergency')
        pv1.admit_source = CWE(cwe_1='New Problem/First Attendance')
        pv1.financial_class = FC(fc_1='Inpatient')
        pv1.charge_price_indicator = CWE(cwe_1='5000000', cwe_2='0', cwe_5='Attendance No.')
        pv1.servicing_facility = CWE(cwe_1='Admitted as Inpatient')
        pv1.prior_temporary_location = PL(pl_1='UZ GENT')
        pv1.discharge_date_time = 'Active'
        pv1.total_adjustments = '20260208113419'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.accommodation_code = CWE(cwe_1='RIZIV')
        pv2.admit_reason = CWE(cwe_2='4 UNWELL')
        pv2.transfer_reason = CWE(cwe_1='Transfer from ED')

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/be/be-amaron.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='CHU_LIEGE')
        msh.receiving_application = HD(hd_1='LAB_SYS')
        msh.receiving_facility = HD(hd_1='PATHOLOGY')
        msh.date_time_of_message = '202603011430'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '202603011430'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='LAURENT', xcn_3='CAROL', xcn_6='RN')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN23456', cx_4='CHU_LIEGE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='LEJEUNE', xpn_2='THOMAS', xpn_3='PHILIPPE')
        pid.date_time_of_birth = '19870822'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='Rue de la Station 34', xad_3='Liege', xad_5='4000', xad_6='BEL')
        pid.pid_13 = '^PRN^PH^^^^^+32497812345'
        pid.primary_language = CWE(cwe_1='FRA', cwe_2='French', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.patient_account_number = CX(cx_1='ACCT09876', cx_4='CHU_LIEGE', cx_5='AN')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='0101', pl_3='01', pl_4='CHU_LIEGE', pl_8='NURS')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.attending_doctor = XCN(xcn_1='ATT2345', xcn_2='RENARD', xcn_3='MARGUERITE', xcn_6='MD')
        pv1.referring_doctor = XCN(xcn_1='REF6789', xcn_2='DUBOIS', xcn_3='SYLVAIN', xcn_6='MD')
        pv1.hospital_service = CWE(cwe_1='MED', cwe_2='Medical', cwe_3='HL70069')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='ATT2345', xcn_2='RENARD', xcn_3='MARGUERITE', xcn_6='MD')
        pv1.patient_type = CWE(cwe_1='IP', cwe_2='Inpatient', cwe_3='HL70004')
        pv1.discharge_disposition = CWE(cwe_1='CHU_LIEGE')
        pv1.diet_type = CWE(cwe_1='A')
        pv1.account_status = CWE(cwe_1='202603011415')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='LEJEUNE', xpn_2='SARAH', xpn_3='L')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Rue de la Station 34', xad_3='Liege', xad_5='4000')
        nk1.nk1_5 = '^PRN^PH^^^^^+32497812346'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BCBS001', cwe_2='MUTUALITE CHRETIENNE')
        in1.insurance_company_id = CX(cx_1='MC')
        in1.in1_4 = 'PO BOX 12345^^Liege^^4000'
        in1.insurance_company_address = XAD(xad_2='WPN', xad_3='PH', xad_8='+32497555444')
        in1.in1_7 = 'GRP54321'
        in1.authorization_information = AUI(aui_1='20230101')
        in1.plan_type = CWE(cwe_1='20261231')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SELF', cwe_2='Self', cwe_3='HL70063')
        in1.insureds_date_of_birth = 'LEJEUNE^THOMAS^PHILIPPE'
        in1.insureds_address = XAD(xad_1='SELF')
        in1.assignment_of_benefits = CWE(cwe_1='19870822')

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA', cwe_2='Drug Allergy', cwe_3='HL70127')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='PCN', cwe_2='Penicillin', cwe_3='HL70127')
        al1.allergy_severity_code = CWE(cwe_1='SV', cwe_2='Severe', cwe_3='HL70128')
        al1.allergy_reaction_code = 'Anaphylaxis'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1, in1, al1]

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
    """ Based on live/be/be-amaron.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYS')
        msh.sending_facility = HD(hd_1='CHU_LIEGE')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='CHU_LIEGE')
        msh.date_time_of_message = '202603011630'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB00053'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN23456', cx_4='CHU_LIEGE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='LEJEUNE', xpn_2='THOMAS', xpn_3='PHILIPPE')
        pid.date_time_of_birth = '19870822'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='0101', pl_3='01', pl_4='CHU_LIEGE')

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
        orc.placer_order_number = EI(ei_1='ORD5678', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='FIL9012', ei_2='LAB_SYS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD5678', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='FIL9012', ei_2='LAB_SYS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='CMP', cwe_3='LN')
        obr.observation_date_time = '202603011445'
        obr.obr_14 = 'ATT2345^RENARD^MARGUERITE^^^MD'
        obr.filler_field_1 = '202603011615'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '98'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-100'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_2.obx_5 = '1.1'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.6-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='BUN', cwe_3='LN')
        obx_3.obx_5 = '18'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '7-20'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx_4.obx_5 = '140'
        obx_4.units = CWE(cwe_1='mEq/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_5.obx_5 = '4.2'
        obx_5.units = CWE(cwe_1='mEq/L')
        obx_5.reference_range = '3.5-5.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='17861-6', cwe_2='Calcium', cwe_3='LN')
        obx_6.obx_5 = '9.4'
        obx_6.units = CWE(cwe_1='mg/dL')
        obx_6.reference_range = '8.5-10.5'
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
    """ Based on live/be/be-amaron.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='CHU_LIEGE')
        msh.receiving_application = HD(hd_1='LAB_SYS')
        msh.receiving_facility = HD(hd_1='PATHOLOGY')
        msh.date_time_of_message = '202603011400'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ORD00234'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN23456', cx_4='CHU_LIEGE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='LEJEUNE', xpn_2='THOMAS', xpn_3='PHILIPPE')
        pid.date_time_of_birth = '19870822'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='0101', pl_3='01', pl_4='CHU_LIEGE')
        pv1.attending_doctor = XCN(xcn_1='ATT2345', xcn_2='RENARD', xcn_3='MARGUERITE', xcn_6='MD')

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
        orc.placer_order_number = EI(ei_1='ORD5678', ei_2='EPIC')
        orc.placer_order_group_number = EI(ei_1='GRP001', ei_2='EPIC')
        orc.date_time_of_order_event = '202603011400'
        orc.orc_12 = 'ATT2345^RENARD^MARGUERITE^^^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD5678', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC with Diff', cwe_3='LN')
        obr.observation_date_time = '202603011400'
        obr.obr_16 = 'ATT2345^RENARD^MARGUERITE^^^MD'
        obr.obr_27 = '^STAT'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R50.9', cwe_2='Fever, unspecified', cwe_3='I10')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Patient febrile x 24hrs, rule out infection.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/be/be-amaron.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SCHED_SYS')
        msh.sending_facility = HD(hd_1='AZ_GROENINGE')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='AZ_GROENINGE')
        msh.date_time_of_message = '202603051000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'SCH00567'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT89012', ei_2='SCHED_SYS')
        sch.filler_appointment_id = EI(ei_1='APT89012', ei_2='EPIC')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='OFFICE', cwe_2='Office Visit', cwe_3='LOCAL')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^30^202603101400^202603101430'
        sch.filler_contact_person = XCN(xcn_1='ATT2345', xcn_2='COPPENS', xcn_3='JORIS', xcn_6='MD')
        sch.filler_contact_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_8='+32497555444')
        sch.filler_contact_address = XAD(xad_1='AZ_GROENINGE_KLINIEK', xad_2='AZ_GROENINGE')
        sch.entered_by_person = XCN(xcn_1='Booked')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN23456', cx_4='AZ_GROENINGE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='WILLEMS', xpn_2='BART', xpn_3='KOENRAAD')
        pid.date_time_of_birth = '19870822'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AZ_GROENINGE_KLINIEK', pl_2='EXAM3', pl_3='01', pl_4='AZ_GROENINGE')
        pv1.attending_doctor = XCN(xcn_1='ATT2345', xcn_2='COPPENS', xcn_3='JORIS', xcn_6='MD')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.segment_action_code = 'A'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.segment_action_code = 'A'
        ais.universal_service_identifier = CWE(cwe_1='OFFICE_VISIT', cwe_2='Office Visit', cwe_3='LOCAL')
        ais.start_date_time_offset_units = CNE(cne_1='202603101400')
        ais.duration = '0'
        ais.duration_units = CNE(cne_1='MIN')
        ais.allow_substitution_code = CWE(cwe_1='30')
        ais.filler_status_code = CWE(cwe_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.personnel_resource_id = XCN(xcn_1='ATT2345', xcn_2='COPPENS', xcn_3='JORIS', xcn_6='MD')
        aip.resource_type = CWE(cwe_1='ATT', cwe_2='Attending', cwe_3='HL70443')

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.personnel_resource = personnel_resource

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'A'
        ail.location_resource_id = PL(pl_1='AZ_GROENINGE_KLINIEK', pl_2='EXAM3', pl_3='01', pl_4='AZ_GROENINGE')
        ail.location_group = CWE(cwe_1='202603101400')
        ail.start_date_time = '0'
        ail.start_date_time_offset = 'MIN'
        ail.start_date_time_offset_units = CNE(cne_1='30')
        ail.duration = 'MIN'

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources
        msg.extra_segments = [ail]

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
    """ Based on live/be/be-amaron.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TRANS_SYS')
        msh.sending_facility = HD(hd_1='ERASME')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='ERASME')
        msh.date_time_of_message = '202603021000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'DOC00432'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '202603021000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN23456', cx_4='ERASME', cx_5='MR')
        pid.patient_name = XPN(xpn_1='MICHEL', xpn_2='OLIVIER', xpn_3='JULIEN')
        pid.date_time_of_birth = '19870822'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='OR3', pl_3='01', pl_4='ERASME')
        pv1.attending_doctor = XCN(xcn_1='SUR6789', xcn_2='MARCHAND', xcn_3='PIERRE', xcn_6='MD')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='OP', cwe_2='Operative Note', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Text^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='202603011600')
        txa.assigned_document_authenticator = XCN(xcn_1='SUR6789', xcn_2='MARCHAND', xcn_3='PIERRE', xcn_6='MD')
        txa.placer_order_number = EI(ei_1='DOC65432')
        txa.unique_document_file_name = 'AU^Authenticated^HL70271'
        txa.document_confidentiality_status = '202603021000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='OP_NOTE', cwe_2='Operative Note', cwe_3='LOCAL')
        obx.obx_5 = (
            'Procedure: Laparoscopic cholecystectomy\\.br\\Patient tolerated procedure well\\.br\\No complications\\.br\\EBL: 50mL\\.br\\Specimens sent to pathol'
            'ogy.'
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
    """ Based on live/be/be-amaron.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Ntierprise')
        msh.sending_facility = HD(hd_1='Ntierprise Clinic')
        msh.receiving_application = HD(hd_1='Healthmatics EHR')
        msh.receiving_facility = HD(hd_1='Healthmatics Clinic')
        msh.date_time_of_message = '20260423114643'
        msh.message_type = MSG(msg_1='MFN', msg_2='M02')
        msh.message_control_id = '9026-62'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'

        # .. build MFI ..
        mfi = MFI()
        mfi.master_file_identifier = CWE(cwe_1='REF')
        mfi.file_level_event_code = 'UPD'
        mfi.response_level_code = 'NE'

        # .. build MFE ..
        mfe = MFE()
        mfe.record_level_event_code = 'MAD'
        mfe.mfe_4 = 'provtest'

        # .. build STF ..
        stf = STF()
        stf.primary_key_value_stf = CWE(cwe_1='provtest')
        stf.staff_identifier_list = CX(cx_1='provtest')
        stf.staff_name = XPN(xpn_1='De Smedt', xpn_2='Karel', xpn_3='L')
        stf.staff_type = CWE(cwe_1='R')
        stf.administrative_sex = CWE(cwe_1='M')
        stf.date_time_of_birth = '19871011'
        stf.active_inactive_flag = 'A'
        stf.stf_10 = '(+32)9 332 2222^^PH^k.desmedt@uzgent.be^^32^93322222'
        stf.office_home_address_birthplace = XAD(xad_1='Veldstraat 12', xad_3='Gent', xad_4='OVL', xad_5='9000')

        # .. build PRA ..
        pra = PRA()
        pra.primary_key_value_pra = CWE(cwe_1='provtest')
        pra.practitioner_id_numbers = PLN(pln_1='19876543210', pln_2='RIZIV')

        # .. build the MF_STAFF group ..
        mf_staff = MfnM02MfStaff()
        mf_staff.mfe = mfe
        mf_staff.stf = stf
        mf_staff.pra = pra

        # .. assemble the full message ..
        msg = MFN_M02()
        msg.msh = msh
        msg.mfi = mfi
        msg.mf_staff = mf_staff

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
    """ Based on live/be/be-amaron.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GHH LAB')
        msh.sending_facility = HD(hd_1='ELAB-3')
        msh.receiving_application = HD(hd_1='GHH OE')
        msh.receiving_facility = HD(hd_1='BLDG4')
        msh.date_time_of_message = '202602150930'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'CNTRL-4567'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='79012734589')
        pid.patient_name = XPN(xpn_1='JACOBS', xpn_2='NATHALIE', xpn_3='C', xpn_7='L')
        pid.mothers_maiden_name = XPN(xpn_1='PEETERS')
        pid.date_time_of_birth = '19690127'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Steenweg 264', xad_3='Hasselt', xad_5='3500')
        pid.pid_13 = '(+32)11456343'
        pid.pid_14 = '(+32)11863232'
        pid.patient_account_number = CX(cx_1='AC79012734589')
        pid.pid_20 = '78-B5446^VLG^20260520'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='956540', ei_2='GHH OE')
        obr.filler_order_number = EI(ei_1='2056924', ei_2='GHH LAB')
        obr.universal_service_identifier = CWE(cwe_1='15545', cwe_2='GLUCOSE')
        obr.observation_date_time = '202602150730'
        obr.obr_16 = '19287634105^VERMEERSCH^BEATRICE^K^^^^MD^^'
        obr.result_status = 'F'
        obr.reason_for_study = CWE(cwe_1='84012976543', cwe_2='WOUTERS', cwe_3='FREDERIK', cwe_4='M', cwe_8='MD')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'SN'
        obx.observation_identifier = CWE(cwe_1='1554-5', cwe_2='GLUCOSE', cwe_3='POST 12H CFST:MCNC:PT:SER/PLAS:QN')
        obx.obx_5 = '^182'
        obx.units = CWE(cwe_1='mg/dl')
        obx.reference_range = '70_105'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/be/be-amaron.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='Regional MPI')
        msh.receiving_application = HD(hd_1='Master MPI')
        msh.receiving_facility = HD(hd_1='AZ Sint-Jan')
        msh.date_time_of_message = '20260501140010'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28')
        msh.message_control_id = '5059486'
        msh.processing_id = PT(pt_1='P', pt_2='T')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'ER'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20260501140008'
        evn.operator_id = XCN(xcn_1='11144958600', xcn_2='Maes', xcn_3='Arthur', xcn_8='Regional MPI&2.16.840.1.113883.19.201&ISO', xcn_9='L')
        evn.event_occurred = '20260501140008'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='71080812345', cx_4='NationalPN&2.16.840.1.113883.19.3&ISO', cx_5='PN'),
            CX(cx_1='5643', cx_4='AZ Sint-Jan&2.16.840.1.113883.19.2.400566&ISO', cx_5='PI'),
            CX(cx_1='4353457', cx_4='Huisarts Devos&2.16.840.1.113883.19.2.450998&ISO', cx_5='PI'),
        ]
        pid.patient_name = XPN(xpn_1='Goossens', xpn_2='Beatrice', xpn_7='L')
        pid.date_time_of_birth = '19820810'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Langestraat 34b&Langestraat&34b', xad_3='Brugge', xad_5='8000', xad_7='H')
        pid.pid_13 = '+32 50 465366^ORN^PH~+32 50 465369^ORN^FX'
        pid.pid_14 = '+32 50 666897^WPN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='N')
        pv1.pv1_3 = ''

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/be/be-amaron.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COPRAdetectapi')
        msh.sending_facility = HD(hd_1='001')
        msh.receiving_application = HD(hd_1='detectserver')
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'BE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '2345'
        pid.pid_4 = '86051298765'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.assigned_patient_location = PL(pl_1='SC220')
        pv1.pv1_4 = ''

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='RASS')
        obx.obx_5 = '-4'
        obx.date_time_of_the_observation = '202601010600'

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='PupilleLinks')
        obx_2.obx_5 = 'e+k'
        obx_2.date_time_of_the_observation = '202612301330'

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='PupilleRechts')
        obx_3.obx_5 = 'e+k'
        obx_3.date_time_of_the_observation = '202601010600'

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result
        msg.extra_segments = [obx, obx_2, obx_3]

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
    """ Based on live/be/be-amaron.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SendingApp')
        msh.sending_facility = HD(hd_1='SendingFac')
        msh.receiving_application = HD(hd_1='ReceivingApp')
        msh.receiving_facility = HD(hd_1='ReceivingFac')
        msh.date_time_of_message = '20260613061611'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12')
        msh.message_control_id = '234567890'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.msh_18 = ''

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='12345', ei_2='12345')
        sch.filler_appointment_id = EI(ei_1='2196178', ei_2='2196178')
        sch.schedule_id = CWE(cwe_1='12345')
        sch.event_reason = CWE(cwe_1='OFFICE', cwe_2='Office visit')
        sch.appointment_reason = CWE(cwe_1='reason for the appointment')
        sch.appointment_type = CWE(cwe_1='OFFICE')
        sch.sch_9 = '60'
        sch.appointment_duration_units = CNE(cne_1='m')
        sch.sch_11 = '^^60^20260617084500^20260617093000'
        sch.filler_contact_person = XCN(xcn_1='9', xcn_2='DEVOS', xcn_3='GASTON', xcn_4='')
        sch.entered_by_person = XCN(xcn_1='9', xcn_2='DEVOS', xcn_3='LUCIEN', xcn_4='')
        sch.filler_status_code = CWE(cwe_1='Scheduled')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='53')
        pid.patient_name = XPN(xpn_1='Janssens', xpn_2='Hendrik')
        pid.date_time_of_birth = '19850719'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kerkplein 8', xad_3='Brugge', xad_5='8000')
        pid.pid_13 = '(+32)50 234567'
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='93071912345')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='1', xcn_2='Claes', xcn_3='Ingrid', xcn_4='B', xcn_5='MD', xcn_9='')
        pv1.referring_doctor = XCN(xcn_1='2', xcn_2='Maes', xcn_3='Karel', xcn_4='F', xcn_5='MD', xcn_9='')
        pv1.alternate_visit_id = CX(cx_1='99158')
        pv1.pv1_52 = ''

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
        aig.resource_id = CWE(cwe_1='1', cwe_2='Peeters, Pieter')
        aig.resource_type = CWE(cwe_1='D', cwe_3='')

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SiuS12GeneralResource()
        general_resource.aig = aig

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'A'
        ail.location_resource_id = PL(pl_1='OFFICE', pl_4='OFFICE')
        ail.location_type_ail = CWE(cwe_2='Main Office')
        ail.start_date_time = '20260614084500'
        ail.duration = '45'
        ail.duration_units = CNE(cne_1='m', cne_2='Minutes')
        ail.filler_status_code = CWE(cwe_1='Scheduled')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.personnel_resource_id = XCN(xcn_1='1', xcn_2='Peeters', xcn_3='Pieter', xcn_4='A', xcn_5='MD', xcn_9='')
        aip.resource_type = CWE(cwe_1='D', cwe_2='Willems, Hendrik')
        aip.start_date_time = '20260614084500'
        aip.duration = '45'
        aip.duration_units = CNE(cne_1='m', cne_2='Minutes')
        aip.filler_status_code = CWE(cwe_1='Scheduled')

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
    """ Based on live/be/be-amaron.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIRTH')
        msh.sending_facility = HD(hd_1='MIRTH_CONNECT')
        msh.receiving_application = HD(hd_1='HIS001')
        msh.receiving_facility = HD(hd_1='MIRTH_CONNECT')
        msh.date_time_of_message = '20260510121200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = 'MSG0000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CO'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='NL-BE')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='88042156789', cx_5='NISS')
        pid.patient_name = XPN(xpn_1='COPPENS', xpn_2='Karel')
        pid.date_time_of_birth = '19930412'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='33ddf75d-9fb2-5bd0-0a85-274198282d96')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
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
    """ Based on live/be/be-amaron.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SGL')
        msh.sending_facility = HD(hd_1='SAINT_LUC')
        msh.receiving_application = HD(hd_1='DMP_MSSANTE')
        msh.receiving_facility = HD(hd_1='ASIP')
        msh.date_time_of_message = '20260115120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260115001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5', vid_2='FRA', vid_3='2.10')
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='82081034567', cx_4='ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO', cx_5='INS')
        pid.pid_5 = 'SIMON^MARC^^^^L'
        pid.date_time_of_birth = '19820810'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue du Temple 15', xad_3='Namur', xad_5='5000', xad_6='BEL', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='N')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='11502-2', cwe_2="CR d'examens biologiques", cwe_3='LN')
        obx.obx_5 = '^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ'
        obx.observation_result_status = 'F'
        obx.obx_12 = ''

        # .. build PRT ..
        prt = PRT()
        prt.action_code = 'UC'
        prt.role_of_participation = CWE(cwe_1='SB', cwe_2='Send by', cwe_3='participation')
        prt.person = XCN(xcn_1='91234567890', xcn_2='Simon', xcn_3='Marc', xcn_9='ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO', xcn_10='D', xcn_13='RPPS')
        prt.organization = XON(xon_1='Organisation-Y', xon_6='ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO', xon_7='FINEG', xon_10='400028096')

        # .. build PRT ..
        prt_2 = PRT()
        prt_2.action_code = 'UC'
        prt_2.role_of_participation = CWE(cwe_1='RCT', cwe_2='Results Copies To', cwe_3='participation')
        prt_2.person = XCN(xcn_1='21234567800', xcn_2='Renard', xcn_3='Antoine', xcn_9='ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO', xcn_10='D', xcn_13='RPPS')
        prt_2.telecommunication_address = XTN(xtn_3='X.400', xtn_4='antoine.renard@test-ci-sis.mssante.fr')

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='11502-2', cwe_2="CR d'examens biologiques", cwe_3='LN')
        obx_2.obx_5 = '^TEXT^XML^Base64^RG9jdW1lbnQgbWVkY2lhbCBhdSBmb3JtYXQgQ0RBIG5pdmVhdSAx'
        obx_2.observation_result_status = 'F'
        obx_2.obx_12 = ''

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='MASQUE_PS', cwe_2='Masque aux professionnels de Sante', cwe_3='MetaDMPMSS')
        obx_3.obx_5 = 'N^^expandedYes-NoIndicator'
        obx_3.observation_result_status = 'F'
        obx_3.obx_12 = ''

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='INVISIBLE_PATIENT', cwe_2='Document Non Visible par le patient', cwe_3='MetaDMPMSS')
        obx_4.obx_5 = 'N^^expandedYes-NoIndicator'
        obx_4.observation_result_status = 'F'
        obx_4.obx_12 = ''

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CE'
        obx_5.observation_identifier = CWE(cwe_1='DESTDMP', cwe_2='Destinataire DMP', cwe_3='MetaDMPMSS')
        obx_5.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_5.observation_result_status = 'F'
        obx_5.obx_12 = ''

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'CE'
        obx_6.observation_identifier = CWE(cwe_1='DESTMSSANTEPS', cwe_2='Destinataire PS', cwe_3='MetaDMPMSS')
        obx_6.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_6.observation_result_status = 'F'
        obx_6.obx_12 = ''

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'CE'
        obx_7.observation_identifier = CWE(cwe_1='DESTMSSANTEPAT', cwe_2='Destinataire Patient', cwe_3='MetaDMPMSS')
        obx_7.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_7.observation_result_status = 'F'
        obx_7.obx_12 = ''

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'CE'
        obx_8.observation_identifier = CWE(cwe_1='ACK_RECEPTION', cwe_2='Accuse de reception', cwe_3='MetaDMPMSS')
        obx_8.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_8.observation_result_status = 'F'
        obx_8.obx_12 = ''

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'CE'
        obx_9.observation_identifier = CWE(cwe_1='ACK_LECTURE', cwe_2='Accuse de lecture', cwe_3='MetaDMPMSS')
        obx_9.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_9.observation_result_status = 'F'
        obx_9.obx_12 = ''

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'ED'
        obx_10.observation_identifier = CWE(cwe_1='CORPSMAIL_PS', cwe_2='Corps du mail pour un PS', cwe_3='MetaDMPMSS')
        obx_10.obx_5 = '^TEXT^^Base64^Q2hlciBjb25mcsOocmUsIHZvdXMgdHJvdXZlcmV6IGNpLWpvaW50IGxlIENSIGTigJlpbWFnZXJpZSBkZSBNLkR1cG9udA=='
        obx_10.observation_result_status = 'F'
        obx_10.obx_12 = ''

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result
        msg.extra_segments = [obx, prt, prt_2, obx_2, obx_3, obx_4, obx_5, obx_6, obx_7, obx_8, obx_9, obx_10]

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
    """ Based on live/be/be-amaron.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='CHU_CHARLEROI')
        msh.receiving_application = HD(hd_1='DMP_MSSANTE')
        msh.receiving_facility = HD(hd_1='ASIP')
        msh.date_time_of_message = '20260220090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260220002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5', vid_2='FRA', vid_3='2.10')
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='93051267890', cx_4='ASIP-SANTE-INS-NIR&1.2.250.1.213.1.4.8&ISO', cx_5='INS')
        pid.pid_5 = 'LAURENT^EMILIE^^^^L'
        pid.date_time_of_birth = '19930512'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Boulevard Tirou 25', xad_3='Charleroi', xad_5='6000', xad_6='BEL', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='N')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2="CR d'imagerie medicale", cwe_3='LN')
        obx.obx_5 = '^TEXT^XML^Base64^RG9jdW1lbnQgbcOpZGljYWwgYXUgZm9ybWF0IENEQQ'
        obx.observation_result_status = 'F'
        obx.obx_12 = ''

        # .. build PRT ..
        prt = PRT()
        prt.action_code = 'UC'
        prt.role_of_participation = CWE(cwe_1='SB', cwe_2='Send by', cwe_3='participation')
        prt.person = XCN(xcn_1='91234567890', xcn_2='Laurent', xcn_3='Emilie', xcn_9='ASIP-SANTE-PS&1.2.250.1.71.4.2.1&ISO', xcn_10='D', xcn_13='RPPS')
        prt.organization = XON(xon_1='Organisation-Y', xon_6='ASIP-SANTE-ST&1.2.250.1.71.4.2.2&ISO', xon_7='FINEG', xon_10='400028096')

        # .. build PRT ..
        prt_2 = PRT()
        prt_2.action_code = 'UC'
        prt_2.role_of_participation = CWE(cwe_1='RCT', cwe_2='Results Copies To', cwe_3='participation')
        prt_2.telecommunication_address = XTN(xtn_3='X.400', xtn_4='93051267890@patient.mssante.fr')

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='MASQUE_PS', cwe_2='Masque aux professionnels de Sante', cwe_3='MetaDMPMSS')
        obx_2.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_2.observation_result_status = 'F'
        obx_2.obx_12 = ''

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='INVISIBLE_PATIENT', cwe_2='Document Non Visible par le patient', cwe_3='MetaDMPMSS')
        obx_3.obx_5 = 'N^^expandedYes-NoIndicator'
        obx_3.observation_result_status = 'F'
        obx_3.obx_12 = ''

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='DESTDMP', cwe_2='Destinataire DMP', cwe_3='MetaDMPMSS')
        obx_4.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_4.observation_result_status = 'F'
        obx_4.obx_12 = ''

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CE'
        obx_5.observation_identifier = CWE(cwe_1='DESTMSSANTEPS', cwe_2='Destinataire PS', cwe_3='MetaDMPMSS')
        obx_5.obx_5 = 'N^^expandedYes-NoIndicator'
        obx_5.observation_result_status = 'F'
        obx_5.obx_12 = ''

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'CE'
        obx_6.observation_identifier = CWE(cwe_1='DESTMSSANTEPAT', cwe_2='Destinataire Patient', cwe_3='MetaDMPMSS')
        obx_6.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_6.observation_result_status = 'F'
        obx_6.obx_12 = ''

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'CE'
        obx_7.observation_identifier = CWE(cwe_1='ACK_RECEPTION', cwe_2='Accuse de reception', cwe_3='MetaDMPMSS')
        obx_7.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_7.observation_result_status = 'F'
        obx_7.obx_12 = ''

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'CE'
        obx_8.observation_identifier = CWE(cwe_1='ACK_LECTURE_MSS', cwe_2='Accuse de lecture', cwe_3='MetaDMPMSS')
        obx_8.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_8.observation_result_status = 'F'
        obx_8.obx_12 = ''

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'ED'
        obx_9.observation_identifier = CWE(cwe_1='CORPSMAIL_PATIENT', cwe_2='Corps du mail pour le patient', cwe_3='MetaDMPMSS')
        obx_9.obx_5 = '^TEXT^^Base64^Qm9uam91ciBNLkR1cG9udCwgY2ktam9pbnQgdm90cmUgQ1IgZOKAmWltYWdlcmllLg=='
        obx_9.observation_result_status = 'F'
        obx_9.obx_12 = ''

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result
        msg.extra_segments = [obx, prt, prt_2, obx_2, obx_3, obx_4, obx_5, obx_6, obx_7, obx_8, obx_9]

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
    """ Based on live/be/be-amaron.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IRIS')
        msh.sending_facility = HD(hd_1='IRIS')
        msh.receiving_application = HD(hd_1='VENDOR')
        msh.receiving_facility = HD(hd_1='VENDOR')
        msh.date_time_of_message = '20260515260018'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = '260515260018'
        msh.processing_id = PT(pt_1='T')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.pid_2 = 'ITCC20260515^^^^MRN'
        pid.patient_identifier_list = CX(cx_1='ITCC20260515')
        pid.patient_name = XPN(xpn_1='MERTENS', xpn_2='PAUL')
        pid.date_time_of_birth = '19650719'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='2345')
        pid.pid_19 = '87071923456'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POC02')
        pv1.pv1_7 = 'GR0002^VERMEERSCH^ANNA^^^MD^MD^^^^^^RIZIV'
        pv1.pv1_8 = 'OP0002^WOUTERS^LEON^^^MD^MD^^^^^^RIZIV'
        pv1.pv1_17 = 'GR0002^VERMEERSCH^ANNA^^^MD^MD^^^^^^RIZIV'
        pv1.pv1_60 = '99158'
        pv1.pv1_62 = ''

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
        orc.placer_order_number = EI(ei_1='200030-1', ei_2='EPC')
        orc.placer_order_group_number = EI(ei_1='200030', ei_2='EPC')
        orc.parent_order = EIP(eip_1='20260515260018')
        orc.orc_11 = 'OP0002^WOUTERS^LEON^^^MD^MD^^^^^^RIZIV'
        orc.orc_12 = 'POC02'
        orc.advanced_beneficiary_notice_code = CWE(cwe_1='POC02')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='200030-1', ei_2='EPC')
        obr.universal_service_identifier = CWE(cwe_1='92250', cwe_2='Fundus Photo', cwe_3='CPT4')
        obr.observation_date_time = '20260403145907'
        obr.obr_15 = 'OP0002^WOUTERS^LEON^^^MD^MD^^^^^^RIZIV'
        obr.filler_field_2 = '20260515260018'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='57713-0', cwe_2='LEFT EYE DIABETIC RETINOPATHY SEVERITY', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'LA24865-9^Mild Non-Proliferative^LN'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260403145907'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='57714-8', cwe_2='RIGHT EYE DIABETIC RETINOPATHY SEVERITY', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'LA24868-3^Moderate Non-Proliferative^LN'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260403145907'

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

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E11.319', cwe_2='DM2 W/O DR, UNSP EYE', cwe_3='I10')
        dg1.diagnosis_type = CWE(cwe_1='W')

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '31'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='PDF', cwe_2='Display format in PDF', cwe_3='AUSPDI')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovUmVzb3VyY2Vz'
            'IDw8Cj4+Ci9Db250ZW50cyA0IDAgUgo+PgplbmRvYmoKNCAwIG9iago8PAovTGVuZ3RoIDQ0Cj4+CnN0cmVhbQpCVAovRjEgMTggVGYKMTAwIDcwMCBUZAooSGVsbG8sIFdvcmxkISkg'
            'VGoKRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTUzIDAw'
            'MDAwIG4gCjAwMDAwMDAyODQgMDAwMDAgbiAKdHJhaWxlcgo8PAovU2l6ZSA1Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgozODIKJSVFT0YK'
        )
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260515260018'

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result
        msg.extra_segments = [dg1, obx_3]

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
