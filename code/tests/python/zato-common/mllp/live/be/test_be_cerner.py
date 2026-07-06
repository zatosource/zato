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
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA05Insurance, AdtA05NextOfKin, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, \
    OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, \
    SiuS12LocationResource, SiuS12Patient, SiuS12Resources, SiuS12Service, VxuV04Observation, VxuV04Order, VxuV04PatientVisit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, MDM_T02, ORM_O01, ORU_R01, SIU_S12, VXU_V04
from zato.hl7v2.v2_9.segments import AIL, AIS, AL1, DG1, EVN, GT1, IN1, MSH, NK1, NTE, OBR, OBX, ORC, PD1, PID, PV1, PV2, RGS, RXA, RXR, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('be', 'be-cerner.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/be/be-cerner.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='AZSTJAN')
        msh.receiving_application = HD(hd_1='MEDBRIDGE')
        msh.receiving_facility = HD(hd_1='AZSTJAN')
        msh.date_time_of_message = '20250415093045+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = '2025041509304500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250415093000'
        evn.event_occurred = '20250415092500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='2345678', cx_4='AZSTJAN&33D7890123&L', cx_5='MR', cx_6='AZSTJAN&33D7890123&L')
        pid.pid_4 = '8901^^^CERNER'
        pid.patient_name = XPN(xpn_1='Peeters', xpn_2='Wout', xpn_3='J', xpn_7='L')
        pid.date_time_of_birth = '19701224'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Langestraat 18', xad_3='Brugge', xad_5='8000', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '051334278^PRN^PH~0478512349^PRN^CP'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='CAT')
        pid.pid_19 = '70122443217^^^NISS'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='412', pl_3='A', pl_4='AZSTJAN', pl_9='CARD')
        pv1.pv1_7 = '21098^Bogaert^Filip^^^Dr.^MD^^^AZSTJAN^^^^NIHDI'
        pv1.pv1_8 = '87654^Michiels^Sofie^^^Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='CAR')
        pv1.re_admission_indicator = CWE(cwe_1='A')
        pv1.vip_indicator = CWE(cwe_1='21098', cwe_2='Bogaert', cwe_3='Filip', cwe_6='Dr.', cwe_7='MD', cwe_10='AZSTJAN')
        pv1.bad_debt_transfer_amount = 'A'
        pv1.discharge_disposition = CWE(cwe_1='20250415093000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Acute myocardinfarct')
        pv2.visit_description = '2'
        pv2.visit_protection_indicator = 'N'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.nk1_2 = 'Peeters^Hanne^^^Mevr.^'
        nk1.address = XAD(xad_1='051223847', xad_2='PRN', xad_3='PH')
        nk1.nk1_6 = 'NOK'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='310', cwe_2='Partena')
        in1.insurance_company_id = CX(cx_1='310')
        in1.insurance_company_name = XON(xon_1='Partena West-Vlaanderen')
        in1.plan_effective_date = '20250101'
        in1.plan_expiration_date = '99991231'
        in1.delay_before_lr_day = '310/00764523'

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='0002', cwe_2='ASA', cwe_3='CERNER')
        al1.allergy_reaction_code = 'Urticaria'

        # .. build GT1 ..
        gt1 = GT1()
        gt1.set_id_gt1 = '1'
        gt1.guarantor_name = XPN(xpn_1='Peeters', xpn_2='Wout', xpn_3='J', xpn_7='L')
        gt1.guarantor_address = XAD(xad_1='Langestraat 18', xad_3='Brugge', xad_5='8000', xad_6='BE', xad_7='H')
        gt1.gt1_6 = '051334278^PRN^PH'
        gt1.guarantor_date_time_of_birth = '19701224'
        gt1.guarantor_administrative_sex = CWE(cwe_1='M')
        gt1.guarantor_relationship = CWE(cwe_1='SE')
        gt1.guarantor_date_begin = '70122443217^^^NISS'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.extra_segments = [nk1, in1, al1, gt1]

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
    """ Based on live/be/be-cerner.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='AZSTLUCASBR')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='AZSTLUCASBR')
        msh.date_time_of_message = '20250523141230+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = '2025052314123000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250523141200'
        evn.event_occurred = '20250523141100'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='3456789', cx_4='AZSTLUCASBR&33D7890456&L', cx_5='MR', cx_6='AZSTLUCASBR&33D7890456&L')
        pid.patient_name = XPN(xpn_1='Janssens', xpn_2='Liesbeth', xpn_3='R', xpn_7='L')
        pid.date_time_of_birth = '19790814'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Dijkweg 42', xad_3='Damme', xad_5='8340', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '051278934^PRN^PH~0480617823^PRN^CP'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='CAT')
        pid.pid_19 = '79081423891^^^NISS'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='201', pl_3='B', pl_4='AZSTLUCASBR')
        pv1.pv1_7 = '32109^Coppens^Hendrik^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='SUR')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = '32109^Coppens^Hendrik^^^Dr.^MD'
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.delete_account_date = 'AZSTLUCASBR'
        pv1.pv1_40 = '20250520080000'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.nk1_2 = 'Janssens^Koen^^^Dhr.^'
        nk1.address = XAD(xad_1='051345912', xad_2='PRN', xad_3='PH')
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
    """ Based on live/be/be-cerner.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='CHUUCLNAMUR')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='CHUUCLNAMUR')
        msh.date_time_of_message = '20250618172500+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = '2025061817250000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250618172500'
        evn.event_occurred = '20250618170000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='4567890', cx_4='CHUUCLNAMUR&33D7890789&L', cx_5='MR', cx_6='CHUUCLNAMUR&33D7890789&L')
        pid.patient_name = XPN(xpn_1='Lejeune', xpn_2='Aurelie', xpn_3='M', xpn_7='L')
        pid.date_time_of_birth = '19870322'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Rue de Bruxelles 14', xad_3='Andenne', xad_5='5300', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '082473219^PRN^PH'
        pid.primary_language = CWE(cwe_1='FR')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='CAT')
        pid.pid_19 = '87032256781^^^NISS'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GAST', pl_2='301', pl_3='A', pl_4='CHUUCLNAMUR')
        pv1.pv1_7 = '43210^Marchand^Thierry^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = '43210^Marchand^Thierry^^^Dr.^MD'
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.delete_account_date = 'CHUUCLNAMUR'
        pv1.pv1_40 = '20250614090000'
        pv1.prior_temporary_location = PL(pl_1='20250618172500')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.1', cwe_2='Cholecystolithiasis met cholecystitis', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20250614'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='K81.0', cwe_2='Acute cholecystitis', cwe_3='ICD10')
        dg1_2.diagnosis_date_time = '20250614'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = [dg1, dg1_2]

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
    """ Based on live/be/be-cerner.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABCERNER')
        msh.sending_facility = HD(hd_1='AZMONICA')
        msh.receiving_application = HD(hd_1='MILLENNIUM')
        msh.receiving_facility = HD(hd_1='AZMONICA')
        msh.date_time_of_message = '20250709084530+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = '2025070908453000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='5678901', cx_4='AZMONICA&33D7891011&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Maes', xpn_2='Pieter', xpn_3='L', xpn_7='L')
        pid.date_time_of_birth = '19940403'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Grotesteenweg 31', xad_3='Berchem', xad_5='2600', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '03456218^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEFRO', pl_2='401', pl_3='C', pl_4='AZMONICA')
        pv1.pv1_7 = '54321^Wouters^Bert^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='8901234')
        orc.filler_order_number = EI(ei_1='CLAB8901235')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20250709080000+0200'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='8901234')
        obr.filler_order_number = EI(ei_1='CLAB8901235')
        obr.universal_service_identifier = CWE(cwe_1='80048', cwe_2='Basic Metabolic Panel', cwe_3='CPT4')
        obr.observation_date_time = '20250709073000+0200'
        obr.obr_15 = '54321^Wouters^Bert^^^Dr.^MD'
        obr.filler_field_2 = '20250709084500+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '95'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-105'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250709082000+0200'
        obx.responsible_observer = XCN(xcn_1='CLAB')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_2.obx_5 = '2.4'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.7-1.3'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250709082000+0200'
        obx_2.responsible_observer = XCN(xcn_1='CLAB')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='BUN', cwe_3='LN')
        obx_3.obx_5 = '68'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '7-20'
        obx_3.interpretation_codes = CWE(cwe_1='HH')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250709082000+0200'
        obx_3.responsible_observer = XCN(xcn_1='CLAB')

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx_4.obx_5 = '131'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250709082000+0200'
        obx_4.responsible_observer = XCN(xcn_1='CLAB')

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_5.obx_5 = '5.9'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.interpretation_codes = CWE(cwe_1='HH')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250709082000+0200'
        obx_5.responsible_observer = XCN(xcn_1='CLAB')

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1751-7', cwe_2='Albumin', cwe_3='LN')
        obx_6.obx_5 = '2.8'
        obx_6.units = CWE(cwe_1='g/dL')
        obx_6.reference_range = '3.5-5.5'
        obx_6.interpretation_codes = CWE(cwe_1='L')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250709082000+0200'
        obx_6.responsible_observer = XCN(xcn_1='CLAB')

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2000-8', cwe_2='Calcium', cwe_3='LN')
        obx_7.obx_5 = '7.8'
        obx_7.units = CWE(cwe_1='mg/dL')
        obx_7.reference_range = '8.5-10.5'
        obx_7.interpretation_codes = CWE(cwe_1='L')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250709082000+0200'
        obx_7.responsible_observer = XCN(xcn_1='CLAB')

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
    """ Based on live/be/be-cerner.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABCERNER')
        msh.sending_facility = HD(hd_1='ZNAMIDDEL')
        msh.receiving_application = HD(hd_1='MILLENNIUM')
        msh.receiving_facility = HD(hd_1='ZNAMIDDEL')
        msh.date_time_of_message = '20250812103045+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = '2025081210304500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6789012', cx_4='ZNAMIDDEL&33D7891213&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='De Smedt', xpn_2='Katrien', xpn_3='V', xpn_7='L')
        pid.date_time_of_birth = '19900916'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Eikenlaan 9', xad_3='Mortsel', xad_5='2640', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '03512478^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ONCO', pl_2='CONSULT', pl_3='1', pl_4='ZNAMIDDEL')
        pv1.pv1_7 = '65432^Goossens^Annelies^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='9012345')
        orc.filler_order_number = EI(ei_1='CLAB9012346')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='9012345')
        obr.filler_order_number = EI(ei_1='CLAB9012346')
        obr.universal_service_identifier = CWE(cwe_1='85025', cwe_2='CBC w/ auto diff', cwe_3='CPT4')
        obr.observation_date_time = '20250812094000+0200'
        obr.obr_15 = '65432^Goossens^Annelies^^^Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='WBC', cwe_3='LN')
        obx.obx_5 = '3.1'
        obx.units = CWE(cwe_1='10*9/L')
        obx.reference_range = '4.0-10.0'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='RBC', cwe_3='LN')
        obx_2.obx_5 = '3.62'
        obx_2.units = CWE(cwe_1='10*12/L')
        obx_2.reference_range = '3.80-5.20'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx_3.obx_5 = '10.8'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '12.0-16.0'
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
        obx_4.obx_5 = '32.4'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '36.0-46.0'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_5.obx_5 = '89.5'
        obx_5.units = CWE(cwe_1='fL')
        obx_5.reference_range = '80.0-100.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelet', cwe_3='LN')
        obx_6.obx_5 = '98'
        obx_6.units = CWE(cwe_1='10*9/L')
        obx_6.reference_range = '150-400'
        obx_6.interpretation_codes = CWE(cwe_1='L')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='751-8', cwe_2='Neutrophils', cwe_3='LN')
        obx_7.obx_5 = '1.2'
        obx_7.units = CWE(cwe_1='10*9/L')
        obx_7.reference_range = '1.8-7.7'
        obx_7.interpretation_codes = CWE(cwe_1='L')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='731-0', cwe_2='Lymphocytes', cwe_3='LN')
        obx_8.obx_5 = '1.4'
        obx_8.units = CWE(cwe_1='10*9/L')
        obx_8.reference_range = '1.0-4.0'
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
    """ Based on live/be/be-cerner.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='AZKLINA')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='AZKLINA')
        msh.date_time_of_message = '20250305143015+0100'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = '2025030514301500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7890123', cx_4='AZKLINA&33D7891415&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Willems', xpn_2='Tom', xpn_3='F', xpn_7='L')
        pid.date_time_of_birth = '19770608'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Kapelstraat 12', xad_3='Schoten', xad_5='2900', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '03891247^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='SPOED', pl_2='BED', pl_3='3', pl_4='AZKLINA')
        pv1.pv1_7 = '76543^Claes^Dieter^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='RAD20250305002')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250305143000+0100'
        orc.orc_12 = '76543^Claes^Dieter^^^Dr.^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20250305002')
        obr.universal_service_identifier = CWE(cwe_1='74177', cwe_2='CT Abdomen met contrast', cwe_3='CPT4')
        obr.observation_date_time = '20250305143000+0100'
        obr.obr_16 = '76543^Claes^Dieter^^^Dr.^MD'
        obr.results_rpt_status_chng_date_time = 'CT'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R10.3', cwe_2='Pijn gelokaliseerd in overig deel van onderbuik', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20250305'
        dg1.diagnosis_type = CWE(cwe_1='A')

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
        nte.comment = 'Urgente CT. Vermoeden appendicitis. Patient nuchter. Creatinine 0.9 mg/dL.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/be/be-cerner.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABCERNER')
        msh.sending_facility = HD(hd_1='OLVZAALST')
        msh.receiving_application = HD(hd_1='MILLENNIUM')
        msh.receiving_facility = HD(hd_1='OLVZAALST')
        msh.date_time_of_message = '20250420222015+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = '2025042022201500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='8901234', cx_4='OLVZAALST&33D7891617&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Mertens', xpn_2='Edmond', xpn_3='C', xpn_7='L')
        pid.date_time_of_birth = '19650714'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Stationsstraat 37', xad_3='Dendermonde', xad_5='9200', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '054218734^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='SPOED', pl_2='BED', pl_3='5', pl_4='OLVZAALST')
        pv1.pv1_7 = '87654^Van Damme^Kristof^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='1234560')
        orc.filler_order_number = EI(ei_1='CLAB1234560')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='1234560')
        obr.filler_order_number = EI(ei_1='CLAB1234560')
        obr.universal_service_identifier = CWE(cwe_1='89579-7', cwe_2='Troponin I.cardiac', cwe_3='LN')
        obr.observation_date_time = '20250420220000+0200'
        obr.obr_15 = '87654^Van Damme^Kristof^^^Dr.^MD'
        obr.filler_field_2 = '20250420221500+0200'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='89579-7', cwe_2='Troponin I hs', cwe_3='LN')
        obx.obx_5 = '2847'
        obx.units = CWE(cwe_1='ng/L')
        obx.reference_range = '0-34'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250420221500+0200'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='30934-4', cwe_2='BNP', cwe_3='LN')
        obx_2.obx_5 = '856'
        obx_2.units = CWE(cwe_1='pg/mL')
        obx_2.reference_range = '0-100'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250420221500+0200'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2157-6', cwe_2='CK', cwe_3='LN')
        obx_3.obx_5 = '580'
        obx_3.units = CWE(cwe_1='U/L')
        obx_3.reference_range = '30-200'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250420221500+0200'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13969-1', cwe_2='CK-MB', cwe_3='LN')
        obx_4.obx_5 = '68'
        obx_4.units = CWE(cwe_1='U/L')
        obx_4.reference_range = '0-25'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250420221500+0200'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='48065-7', cwe_2='D-dimeer', cwe_3='LN')
        obx_5.obx_5 = '0.42'
        obx_5.units = CWE(cwe_1='mg/L FEU')
        obx_5.reference_range = '0.00-0.50'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250420221500+0200'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Sterk verhoogd troponine I. Klinische correlatie met acuut coronair syndroom aanbevolen.'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5
        observation_5.nte = nte

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
    """ Based on live/be/be-cerner.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='IMELDA')
        msh.receiving_application = HD(hd_1='LABSYS')
        msh.receiving_facility = HD(hd_1='IMELDA')
        msh.date_time_of_message = '20250901081530+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = '2025090108153000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='9012345', cx_4='IMELDA&33D7891819&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Jacobs', xpn_2='Raf', xpn_3='D', xpn_7='L')
        pid.date_time_of_birth = '19821125'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Provinciebaan 21', xad_3='Bonheiden', xad_5='2820', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '016378945^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='REUM', pl_2='CONSULT', pl_3='2', pl_4='IMELDA')
        pv1.pv1_7 = '98765^Mertens^Griet^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='LABORD20250901002')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250901081500+0200'
        orc.orc_12 = '98765^Mertens^Griet^^^Dr.^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LABORD20250901002')
        obr.universal_service_identifier = CWE(cwe_1='86039', cwe_2='Anti-CCP', cwe_3='CPT4')
        obr.observation_date_time = '20250901081500+0200'
        obr.obr_16 = '98765^Mertens^Griet^^^Dr.^MD'

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
        obr_2.placer_order_number = EI(ei_1='LABORD20250901002')
        obr_2.universal_service_identifier = CWE(cwe_1='86200', cwe_2='CRP kwantitatief', cwe_3='CPT4')
        obr_2.observation_date_time = '20250901081500+0200'
        obr_2.obr_16 = '98765^Mertens^Griet^^^Dr.^MD'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='LABORD20250901002')
        obr_3.universal_service_identifier = CWE(cwe_1='86431', cwe_2='Reumafactor', cwe_3='CPT4')
        obr_3.observation_date_time = '20250901081500+0200'
        obr_3.obr_16 = '98765^Mertens^Griet^^^Dr.^MD'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Vermoeden reumatoide artritis. Gewrichtsklachten > 6 weken.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3, nte]

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
    """ Based on live/be/be-cerner.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='STLUC')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='STLUC')
        msh.date_time_of_message = '20250217101200+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = '2025021710120000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250217101200'
        evn.event_occurred = '20250217100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='1234560', cx_4='STLUC&33D7892021&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Dupont', xpn_2='Sylvie', xpn_3='G', xpn_7='L')
        pid.date_time_of_birth = '19710930'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Avenue Louise 52', xad_3='Forest', xad_5='1190', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '03267184^PRN^PH'
        pid.primary_language = CWE(cwe_1='FR')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='CAT')
        pid.pid_19 = '71093078234^^^NISS'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DERMA', pl_2='CONSULT', pl_3='3', pl_4='STLUC')
        pv1.pv1_7 = '09876^Moreau^Philippe^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='DERM')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = '09876^Moreau^Philippe^^^Dr.^MD'
        pv1.patient_type = CWE(cwe_1='OUT')
        pv1.delete_account_date = 'STLUC'
        pv1.pv1_40 = '20250217101200'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='MC101', cwe_2='MC Bruxelles')
        in1.insurance_company_id = CX(cx_1='101')
        in1.insurance_company_name = XON(xon_1='Solidaris')
        in1.plan_effective_date = '20250101'
        in1.plan_expiration_date = '99991231'
        in1.company_plan_code = CWE(cwe_1='101/33517842')

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
    """ Based on live/be/be-cerner.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='AZSTBLAS')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='AZSTBLAS')
        msh.date_time_of_message = '20250610141530+0200'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = '2025061014153000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APPT20250610002')
        sch.event_reason = CWE(cwe_1='ROUTINE')
        sch.appointment_reason = CWE(cwe_2='Consultatie orthopedie')
        sch.appointment_type = CWE(cwe_1='20')
        sch.sch_9 = 'min'
        sch.appointment_duration_units = CNE(cne_1='1')
        sch.sch_12 = '10987^Michiels^Geert^^^Dr.^MD'
        sch.sch_17 = '10987^Michiels^Geert^^^Dr.^MD'
        sch.entered_by_person = XCN(xcn_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='1234509', cx_4='AZSTBLAS&33D7892223&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Goossens', xpn_2='Kevin', xpn_3='N', xpn_7='L')
        pid.date_time_of_birth = '19970312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Kerkstraat 44', xad_3='Aalst', xad_5='9300', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '053234891^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORTHO', pl_2='RAAD', pl_3='2', pl_4='AZSTBLAS')
        pv1.pv1_7 = '10987^Michiels^Geert^^^Dr.^MD'

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
        ais.universal_service_identifier = CWE(cwe_1='ORTHCONSULT', cwe_2='Orthopedie Consultatie', cwe_3='CERNER')
        ais.start_date_time = '20250625093000+0200'
        ais.start_date_time_offset_units = CNE(cne_1='20')
        ais.duration = 'min'

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='ORTHO', pl_2='RAAD', pl_3='2', pl_4='AZSTBLAS')
        ail.location_type_ail = CWE(cwe_1='20250625093000+0200')

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
    """ Based on live/be/be-cerner.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABCERNER')
        msh.sending_facility = HD(hd_1='UZBRUSSELVUB')
        msh.receiving_application = HD(hd_1='MILLENNIUM')
        msh.receiving_facility = HD(hd_1='UZBRUSSELVUB')
        msh.date_time_of_message = '20250503155500+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = '2025050315550000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='2233445', cx_4='UZBRUSSELVUB&33D7892425&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Lambert', xpn_2='Jean-Pierre', xpn_3='W', xpn_7='L')
        pid.date_time_of_birth = '19601019'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Rogierlaan 28', xad_3='Schaarbeek', xad_5='1030', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '03812934^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='VAATCHIR', pl_2='201', pl_3='B', pl_4='UZBRUSSELVUB')
        pv1.pv1_7 = '21098^Simon^Olivier^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='5567890')
        orc.filler_order_number = EI(ei_1='CLAB5567891')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='5567890')
        obr.filler_order_number = EI(ei_1='CLAB5567891')
        obr.universal_service_identifier = CWE(cwe_1='85730', cwe_2='PTT', cwe_3='CPT4')
        obr.observation_date_time = '20250503150000+0200'
        obr.obr_15 = '21098^Simon^Olivier^^^Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='PT', cwe_3='LN')
        obx.obx_5 = '18.5'
        obx.units = CWE(cwe_1='sec')
        obx.reference_range = '9.4-12.5'
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
        obx_2.obx_5 = '1.8'
        obx_2.reference_range = '0.8-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='aPTT', cwe_3='LN')
        obx_3.obx_5 = '42.3'
        obx_3.units = CWE(cwe_1='sec')
        obx_3.reference_range = '25.1-36.5'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3255-7', cwe_2='Fibrinogen', cwe_3='LN')
        obx_4.obx_5 = '5.8'
        obx_4.units = CWE(cwe_1='g/L')
        obx_4.reference_range = '2.0-4.0'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='48065-7', cwe_2='D-dimeer', cwe_3='LN')
        obx_5.obx_5 = '3.45'
        obx_5.units = CWE(cwe_1='mg/L FEU')
        obx_5.reference_range = '0.00-0.50'
        obx_5.interpretation_codes = CWE(cwe_1='HH')
        obx_5.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Sterk verhoogd D-dimeer. Klinisch correleren met DVT/PE.'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5
        observation_5.nte = nte

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
    """ Based on live/be/be-cerner.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='AZALMA')
        msh.receiving_application = HD(hd_1='BLOEDBANK')
        msh.receiving_facility = HD(hd_1='AZALMA')
        msh.date_time_of_message = '20250722192030+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = '2025072219203000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='3344556', cx_4='AZALMA&33D7892627&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Claes', xpn_2='Marleen', xpn_3='H', xpn_7='L')
        pid.date_time_of_birth = '19571228'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Marktplein 5', xad_3='Lokeren', xad_5='9160', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '08671234^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='OP', pl_3='1', pl_4='AZALMA')
        pv1.pv1_7 = '32109^Bogaert^Thomas^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='BB20250722002')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20250722192000+0200'
        orc.orc_12 = '32109^Bogaert^Thomas^^^Dr.^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='BB20250722002')
        obr.universal_service_identifier = CWE(cwe_1='86900', cwe_2='Bloedgroepbepaling', cwe_3='CPT4')
        obr.observation_date_time = '20250722192000+0200'
        obr.obr_16 = '32109^Bogaert^Thomas^^^Dr.^MD'

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
        obr_2.placer_order_number = EI(ei_1='BB20250722002')
        obr_2.universal_service_identifier = CWE(cwe_1='86901', cwe_2='Antistofscreening', cwe_3='CPT4')
        obr_2.observation_date_time = '20250722192000+0200'
        obr_2.obr_16 = '32109^Bogaert^Thomas^^^Dr.^MD'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='BB20250722002')
        obr_3.universal_service_identifier = CWE(cwe_1='86920', cwe_2='Kruisproef 2E', cwe_3='CPT4')
        obr_3.observation_date_time = '20250722192000+0200'
        obr_3.obr_16 = '32109^Bogaert^Thomas^^^Dr.^MD'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Preoperatief. Geplande totale heupprothese morgen 08:00. 2 eenheden EC aanvragen.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3, nte]

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
    """ Based on live/be/be-cerner.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABCERNER')
        msh.sending_facility = HD(hd_1='HHZLIER')
        msh.receiving_application = HD(hd_1='MILLENNIUM')
        msh.receiving_facility = HD(hd_1='HHZLIER')
        msh.date_time_of_message = '20250830141500+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = '2025083014150000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='4455667', cx_4='HHZLIER&33D7892829&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Van Damme', xpn_2='Rudy', xpn_3='E', xpn_7='L')
        pid.date_time_of_birth = '19740405'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Antwerpsesteenweg 7', xad_3='Boom', xad_5='2850', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '04923178^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PNEUMO', pl_2='CONSULT', pl_3='1', pl_4='HHZLIER')
        pv1.pv1_7 = '43210^Coppens^Werner^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='6678901')
        orc.filler_order_number = EI(ei_1='CLAB6678902')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='6678901')
        obr.filler_order_number = EI(ei_1='CLAB6678902')
        obr.universal_service_identifier = CWE(cwe_1='94010', cwe_2='Spirometrie', cwe_3='CPT4')
        obr.observation_date_time = '20250830133000+0200'
        obr.obr_15 = '43210^Coppens^Werner^^^Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='19868-9', cwe_2='FEV1', cwe_3='LN')
        obx.obx_5 = '2.45'
        obx.units = CWE(cwe_1='L')
        obx.reference_range = '3.20-4.80'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='19876-2', cwe_2='FVC', cwe_3='LN')
        obx_2.obx_5 = '3.82'
        obx_2.units = CWE(cwe_1='L')
        obx_2.reference_range = '4.00-5.60'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='19926-5', cwe_2='FEV1/FVC', cwe_3='LN')
        obx_3.obx_5 = '64'
        obx_3.units = CWE(cwe_1='%')
        obx_3.reference_range = '>70'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ED'
        obx_4.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx_4.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFNwaXJvbWV0cmllIFJhcHBvcnQgLSBIZWlsaWcgSGFydCBaaWVrZW5odWlzIExpZXIpCi9DcmVhdG9yIChDZXJuZXIgTWlsbGVubml1'
            'bSBSZXBvcnQgR2VuZXJhdG9yKQovUHJvZHVjZXIgKE9yYWNsZSBIZWFsdGggQ2VybmVyIDIwMjUuMSkKL0NyZWF0aW9uRGF0ZSAoRDoyMDI1MDgzMDE0MTUwMCswMicwMCcpCj4+CmVu'
            'ZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9FeHRHU3RhdGUKL1NBIGZhbHNlCi9TTSAwLjAyCi9jYSAxLjAKL0NBIDEuMAo+PgplbmRvYmoKNCAwIG9iagpbL1BhdHRlcm4gL0RldmljZVJH'
            'Ql0KZW5kb2JqCjUgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNiAwIFIKL1Jlc291cmNlcyA4IDAgUgovTWVkaWFCb3ggWzAgMCA1OTUgODQyXQo+'
            'PgplbmRvYmoKU3Bpcm9tZXRyaWUgUmFwcG9ydAotLS0tLS0tLS0tLS0tLS0tLS0tCkRhdHVtOiAzMC8wOC8yMDI1CgpQYXRpZW50OiBXb3V0ZXJzIE1hcmMKR2Vib29ydGVkYXR1bTog'
            'MDUvMDQvMTk3NApHZXNsYWNodDogTWFuCkxlbmd0ZTogMTc4IGNtCkdld2ljaHQ6IDgyIGtnCgpSZXN1bHRhdGVuOgpGRVYxOiAyLjQ1IEwgKDY1JSB2b29yc3BlbGQpCkZWQzogMy44'
            'MiBMICg3OCUgdm9vcnNwZWxkKQpGRVYxL0ZWQzogNjQlCgpJbnRlcnByZXRhdGllOiBNYXRpZyBvYnN0cnVjdGllZiBwYXRyb29uLgpHZWVuIHNpZ25pZmljYW50ZSByZXZlcnNpYmls'
            'aXRlaXQgbmEgc2FsYnV0YW1vbC4KQ29uY2x1c2llOiBNYXRpZyBDT1BEIChHT0xEIElJKS4='
        )
        obx_4.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Matig obstructief. Compatibel met COPD GOLD II. Geen reversibiliteit.'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4
        observation_4.nte = nte

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
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
    """ Based on live/be/be-cerner.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='CHUBRUGMANN')
        msh.receiving_application = HD(hd_1='DOCMGMT')
        msh.receiving_facility = HD(hd_1='CHUBRUGMANN')
        msh.date_time_of_message = '20250928101045+0200'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = '2025092810104500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250928101000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='5566778', cx_4='CHUBRUGMANN&33D7893031&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Renard', xpn_2='Olivier', xpn_3='T', xpn_7='L')
        pid.date_time_of_birth = '19850211'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Boulevard Leopold II 45', xad_3='Koekelberg', xad_5='1081', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '03548219^PRN^PH'
        pid.primary_language = CWE(cwe_1='FR')
        pid.marital_status = CWE(cwe_1='S')
        pid.religion = CWE(cwe_1='CAT')
        pid.pid_19 = '85021134782^^^NISS'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEURO', pl_2='301', pl_3='A', pl_4='CHUBRUGMANN')
        pv1.pv1_7 = '54321^Picard^Nathalie^^^Dr.^MD'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Lettre de sortie', cwe_3='LOCAL')
        txa.document_content_presentation = 'TX'
        txa.transcription_date_time = '20250928100000+0200'
        txa.txa_9 = '54321^Picard^Nathalie^^^Dr.^MD'
        txa.parent_document_number = EI(ei_1='DOC-2025-65432')
        txa.document_availability_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='11490-0', cwe_2='Discharge summarization note', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKExldHRyZSBkZSBTb3J0aWUgLSBTZXJ2aWNlIGRlIE5ldXJvbG9naWUpCi9DcmVhdG9yIChDZXJuZXIgTWlsbGVubml1bSBEb2N1bWVu'
            'dCBHZW5lcmF0b3IpCi9Qcm9kdWNlciAoT3JhY2xlIEhlYWx0aCBDZXJuZXIgMjAyNS4xKQovQ3JlYXRpb25EYXRlIChEOjIwMjUwOTI4MTAxMDAwKzAyJzAwJykKPj4KZW5kb2JqCkxl'
            'dHRyZSBkZSBTb3J0aWUKLS0tLS0tLS0tLS0tLS0tLS0tLQpQYXRpZW50OiBNQkVLSSBDaGFybGVzCkRhdGUgZGUgbmFpc3NhbmNlOiAxMS8wMi8xOTg1Ck51bWVybyBOSVNTOiA4NDEz'
            'MjIyMzQ1NgoKU2VydmljZTogTmV1cm9sb2dpZQpNZWRlY2luIHRyYWl0YW50OiBEci4gTGVm6HZyZSBWZXJvbmlxdWUKCkRhdGUgZCdhZG1pc3Npb246IDIyLzA5LzIwMjUKRGF0ZSBk'
            'ZSBzb3J0aWU6IDI4LzA5LzIwMjUKCkRpYWdub3N0aWMgcHJpbmNpcGFsOiBBVkMgaXNjaGVtaXF1ZSB0ZXJyaXRvaXJlIHN5bHZpZW4gZ2F1Y2hlCgpUcmFpdGVtZW50IGEgbGEgc29y'
            'dGllOgotIEFzcGlyaW5lIDE2MG1nIDF4L2pvdXIKLSBBdG9ydmFzdGF0aW5lIDQwbWcgMS9qb3VyCgpSZW5kZXotdm91cyBkZSBjb250cm9sZTogMTUvMTAvMjAyNSBhIDEwaDAwCg=='
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
    """ Based on live/be/be-cerner.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='GZAANTW')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='GZAANTW')
        msh.date_time_of_message = '20250714063045+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = '2025071406304500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250714063000'
        evn.event_occurred = '20250714062500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6677889', cx_4='GZAANTW&33D7893233&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Coppens', xpn_2='Ilse', xpn_3='A', xpn_7='L')
        pid.date_time_of_birth = '19630802'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Desguinlei 17', xad_3='Wilrijk', xad_5='2610', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '04312587^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='101', pl_3='A', pl_4='GZAANTW', pl_8='ICU')
        pv1.prior_patient_location = PL(pl_1='65432', pl_2='Jacobs', pl_3='Luc', pl_6='Dr.', pl_7='MD')
        pv1.referring_doctor = XCN(xcn_1='INT')
        pv1.preadmit_test_indicator = CWE(cwe_1='7')
        pv1.ambulatory_status = CWE(cwe_1='65432', cwe_2='Jacobs', cwe_3='Luc', cwe_6='Dr.', cwe_7='MD')
        pv1.vip_indicator = CWE(cwe_1='IN')
        pv1.bad_debt_recovery_amount = 'GZAANTW'
        pv1.diet_type = CWE(cwe_1='20250712140000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Transfer van IC naar medium care')
        pv2.expected_discharge_disposition = CWE(cwe_1='MEDCAR', cwe_2='201', cwe_3='B', cwe_4='GZAANTW')

        # .. assemble the full message ..
        msg = ADT_A02()
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
    """ Based on live/be/be-cerner.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABCERNER')
        msh.sending_facility = HD(hd_1='AZDAMIAAN')
        msh.receiving_application = HD(hd_1='MILLENNIUM')
        msh.receiving_facility = HD(hd_1='AZDAMIAAN')
        msh.date_time_of_message = '20250411093045+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = '2025041109304500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7788990', cx_4='AZDAMIAAN&33D7893435&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Wouters', xpn_2='Nele', xpn_3='B', xpn_7='L')
        pid.date_time_of_birth = '19800523'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Zeedijk 58', xad_3='Oostende', xad_5='8400', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '060312478^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ENDO', pl_2='CONSULT', pl_3='1', pl_4='AZDAMIAAN')
        pv1.pv1_7 = '76543^De Smedt^Hans^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='7789012')
        orc.filler_order_number = EI(ei_1='CLAB7789013')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='7789012')
        obr.filler_order_number = EI(ei_1='CLAB7789013')
        obr.universal_service_identifier = CWE(cwe_1='84443', cwe_2='TSH', cwe_3='CPT4')
        obr.observation_date_time = '20250411084500+0200'
        obr.obr_15 = '76543^De Smedt^Hans^^^Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='11580-8', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '8.92'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.27-4.20'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='FT4', cwe_3='LN')
        obx_2.obx_5 = '8.5'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '12.0-22.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='FT3', cwe_3='LN')
        obx_3.obx_5 = '3.1'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '3.1-6.8'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='5382-7', cwe_2='Anti-TPO', cwe_3='LN')
        obx_4.obx_5 = '412'
        obx_4.units = CWE(cwe_1='IU/mL')
        obx_4.reference_range = '0-34'
        obx_4.interpretation_codes = CWE(cwe_1='HH')
        obx_4.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Verhoogd TSH met verlaagd FT4 en sterk positieve anti-TPO. Compatibel met hypothyreoidie op basis van Hashimoto.'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4
        observation_4.nte = nte

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
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
    """ Based on live/be/be-cerner.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='AZRIVIEREN')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='AZRIVIEREN')
        msh.date_time_of_message = '20250819152200+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A13', msg_3='ADT_A01')
        msh.message_control_id = '2025081915220000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A13'
        evn.recorded_date_time = '20250819152200'
        evn.event_occurred = '20250819151500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='8899001', cx_4='AZRIVIEREN&33D7893637&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Janssens', xpn_2='Roger', xpn_3='P', xpn_7='L')
        pid.date_time_of_birth = '19580420'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Kasteelstraat 8', xad_3='Puurs', xad_5='2870', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '04287631^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='401', pl_3='A', pl_4='AZRIVIEREN')
        pv1.pv1_7 = '87654^Willems^Stefaan^^^Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = '87654^Willems^Stefaan^^^Dr.^MD'
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.delete_account_date = 'AZRIVIEREN'
        pv1.pv1_40 = '20250816090000'
        pv1.pv1_43 = ''

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Ontslag geannuleerd wegens recidief borstpijn. Opname verlengd.'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nte]

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
    """ Based on live/be/be-cerner.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABCERNER')
        msh.sending_facility = HD(hd_1='AZJPGENT')
        msh.receiving_application = HD(hd_1='MILLENNIUM')
        msh.receiving_facility = HD(hd_1='AZJPGENT')
        msh.date_time_of_message = '20250603112030+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = '2025060311203000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='9900112', cx_4='AZJPGENT&33D7893839&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Dubois', xpn_2='Isabelle', xpn_3='C', xpn_7='L')
        pid.date_time_of_birth = '19840911'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Korenmarkt 7', xad_3='Gent', xad_5='9000', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '08478123^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NEFRO', pl_2='CONSULT', pl_3='2', pl_4='AZJPGENT')
        pv1.pv1_7 = '98765^Peeters^Dirk^^^Dr.^MD'

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
        orc.placer_order_number = EI(ei_1='8890123')
        orc.filler_order_number = EI(ei_1='CLAB8890124')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='8890123')
        obr.filler_order_number = EI(ei_1='CLAB8890124')
        obr.universal_service_identifier = CWE(cwe_1='81003', cwe_2='Urinalysis', cwe_3='CPT4')
        obr.observation_date_time = '20250603100000+0200'
        obr.obr_15 = '98765^Peeters^Dirk^^^Dr.^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5767-9', cwe_2='Urine aspect', cwe_3='LN')
        obx.obx_5 = 'Troebel'
        obx.reference_range = 'Helder'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2756-5', cwe_2='pH urine', cwe_3='LN')
        obx_2.obx_5 = '5.5'
        obx_2.reference_range = '5.0-8.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='20454-5', cwe_2='Proteinen urine', cwe_3='LN')
        obx_3.obx_5 = '2+'
        obx_3.reference_range = 'Negatief'
        obx_3.interpretation_codes = CWE(cwe_1='A')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='5794-3', cwe_2='Glucose urine', cwe_3='LN')
        obx_4.obx_5 = 'Negatief'
        obx_4.reference_range = 'Negatief'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='5821-4', cwe_2='Leukocyten urine', cwe_3='LN')
        obx_5.obx_5 = '85'
        obx_5.units = CWE(cwe_1='/HPF')
        obx_5.reference_range = '0-5'
        obx_5.interpretation_codes = CWE(cwe_1='HH')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='5804-0', cwe_2='Erythrocyten urine', cwe_3='LN')
        obx_6.obx_5 = '15'
        obx_6.units = CWE(cwe_1='/HPF')
        obx_6.reference_range = '0-3'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='5769-5', cwe_2='Bacterien urine', cwe_3='LN')
        obx_7.obx_5 = '3+'
        obx_7.reference_range = 'Negatief'
        obx_7.interpretation_codes = CWE(cwe_1='A')
        obx_7.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Sterk afwijkend sediment. Waarschijnlijk urineweginfectie. Urinekweek ingezet.'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7
        observation_7.nte = nte

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
    """ Based on live/be/be-cerner.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='KINDENGESZ')
        msh.receiving_application = HD(hd_1='VACCINNET')
        msh.receiving_facility = HD(hd_1='BENAT')
        msh.date_time_of_message = '20250515100030+0200'
        msh.message_type = MSG(msg_1='VXU', msg_2='V04', msg_3='VXU_V04')
        msh.message_control_id = '2025051510003000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='1122330', cx_4='KINDENGESZ&33D7894041&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Maes', xpn_2='Thibault', xpn_3='S', xpn_7='L')
        pid.date_time_of_birth = '20250315'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Bruul 22', xad_3='Mechelen', xad_5='2800', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '016489231^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PEDIATRIE', pl_2='CONSULT', pl_3='1', pl_4='KINDENGESZ')
        pv1.pv1_7 = '09876^Goossens^Elke^^^Dr.^MD'

        # .. build the PATIENT_VISIT group ..
        patient_visit = VxuV04PatientVisit()
        patient_visit.pv1 = pv1

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='VAX20250515002')
        orc.order_status = 'CM'

        # .. build RXA ..
        rxa = RXA()
        rxa.give_sub_id_counter = '0'
        rxa.administration_sub_id_counter = '1'
        rxa.date_time_start_of_administration = '20250515095500+0200'
        rxa.administered_code = CWE(cwe_1='20', cwe_2='DTaP-IPV-Hib-HepB', cwe_3='CVX')
        rxa.administered_amount = '0.5'
        rxa.administered_units = CWE(cwe_1='mL')
        rxa.administered_dosage_form = CWE(cwe_1='IM')
        rxa.administration_notes = CWE(cwe_1='INFANRIXHEXA', cwe_2='Infanrix Hexa', cwe_3='LOCAL')
        rxa.administered_strength = 'GSK^GlaxoSmithKline^MVX'
        rxa.rxa_16 = 'BT20250101^20260601'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IM', cwe_2='Intramusculair', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='RT', cwe_2='Rechter dij', cwe_3='HL70163')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='64994-7', cwe_2='Vaccine funding source', cwe_3='LN')
        obx.obx_5 = 'VXC1^Public^CDCPHINVS'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Basisvaccinatie 14 maanden. Geen bijwerkingen.'

        # .. build the OBSERVATION group ..
        observation = VxuV04Observation()
        observation.obx = obx
        observation.nte = nte

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
    """ Based on live/be/be-cerner.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MILLENNIUM')
        msh.sending_facility = HD(hd_1='BENAT')
        msh.receiving_application = HD(hd_1='INTERFACE')
        msh.receiving_facility = HD(hd_1='EHEALTH')
        msh.date_time_of_message = '20250110080015+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = '2025011008001500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250110080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='1122309', cx_4='BENAT&33D7894243&L', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Michel', xpn_2='Caroline', xpn_3='F', xpn_7='L')
        pid.date_time_of_birth = '19931107'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='CA')
        pid.patient_address = XAD(xad_1='Avenue de Tervueren 83', xad_3='Etterbeek', xad_5='1040', xad_6='BE', xad_7='H', xad_8='')
        pid.pid_13 = '03671284^PRN^PH~0499312876^PRN^CP'
        pid.primary_language = CWE(cwe_1='FR')
        pid.marital_status = CWE(cwe_1='S')
        pid.religion = CWE(cwe_1='CAT')
        pid.pid_19 = '93110756123^^^NISS'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = '10987^Laurent^Benoit^^^Dr.^MD^^^^RIZIV&2.16.840.1.113883.3.6777.5.2&ISO^NIHDI'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.nk1_2 = 'Michel^Francois^^^M.^'
        nk1.address = XAD(xad_1='03671284', xad_2='PRN', xad_3='PH')
        nk1.nk1_6 = 'FTH'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='MC101', cwe_2='MC Bruxelles')
        in1.insurance_company_id = CX(cx_1='101')
        in1.insurance_company_name = XON(xon_1='Solidaris')
        in1.plan_effective_date = '20250101'
        in1.plan_expiration_date = '99991231'
        in1.company_plan_code = CWE(cwe_1='101/78234156')

        # .. build the INSURANCE group ..
        insurance = AdtA05Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.insurance = insurance

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
