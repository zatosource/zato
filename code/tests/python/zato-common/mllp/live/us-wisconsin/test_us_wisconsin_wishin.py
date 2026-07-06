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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MOC, MSG, PL, PT, VID, XAD, XCN, XPN
from zato.hl7v2.v2_9.groups import MdmT02Observation, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, \
    OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, MDM_T02, ORU_R01
from zato.hl7v2.v2_9.segments import DG1, EVN, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, PV2, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('us-wisconsin', 'us-wisconsin-wishin.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/us-wisconsin/us-wisconsin-wishin.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UWHEALTH')
        msh.receiving_application = HD(hd_1='WISHIN')
        msh.receiving_facility = HD(hd_1='WISHINHUB')
        msh.date_time_of_message = '20260509083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'WISH2026050908300001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509083000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E7829401', cx_4='UWHEALTH', cx_5='MRN'), CX(cx_1='W9928374', cx_4='WISHIN', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='SCHROEDER', xpn_2='KEVIN', xpn_3='THOMAS', xpn_5='')
        pid.date_time_of_birth = '19680423'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1417 Winnebago St', xad_3='Madison', xad_4='WI', xad_5='53704', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^608^2517748921'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='LUT')
        pid.patient_account_number = CX(cx_1='UWH00294781', cx_4='UWHEALTH', cx_5='AN')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6E', pl_2='612', pl_3='1', pl_4='UWHEALTH', pl_8='6E MEDICINE')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='UWH00294781', xcn_4='UWHEALTH', xcn_5='AN')
        pv1.pending_location = PL(pl_1='20260509083000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Chest pain, unspecified', cwe_3='I10')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R07.9', cwe_2='Chest pain, unspecified', cwe_3='I10')
        dg1.diagnosis_date_time = '20260509'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.dg1 = dg1

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
    """ Based on live/us-wisconsin/us-wisconsin-wishin.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='FROEDTERT')
        msh.receiving_application = HD(hd_1='WISHIN')
        msh.receiving_facility = HD(hd_1='WISHINHUB')
        msh.date_time_of_message = '20260508160000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'WISH2026050816000042'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260508160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='F3928401', cx_4='FROEDTERT', cx_5='MRN'), CX(cx_1='W8827463', cx_4='WISHIN', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='VELASQUEZ', xpn_2='ROSA', xpn_3='INEZ', xpn_5='')
        pid.date_time_of_birth = '19750812'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2131-1', cwe_2='Hispanic', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3108 W Burnham St', xad_3='Milwaukee', xad_4='WI', xad_5='53215', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^414^3840091'
        pid.primary_language = CWE(cwe_1='SPA')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='8W', pl_2='802', pl_3='2', pl_4='FROEDTERT')
        pv1.pv1_7 = '67890^KRASINSKI^PAUL^W^^^MD'
        pv1.admitting_doctor = XCN(xcn_1='FRO00187291', xcn_4='FROEDTERT', xcn_5='AN')
        pv1.pending_location = PL(pl_1='20260503141500')
        pv1.total_payments = '20260508160000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='S72.001A', cwe_2='Fracture of unspecified part of neck of right femur', cwe_3='I10')
        dg1.diagnosis_date_time = '20260503'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.dg1_2 = 'I10'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='M87.051', cwe_2='Idiopathic aseptic necrosis of right femur', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20260505'
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
    """ Based on live/us-wisconsin/us-wisconsin-wishin.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='HSHS_STVINC')
        msh.receiving_application = HD(hd_1='WISHIN')
        msh.receiving_facility = HD(hd_1='WISHINHUB')
        msh.date_time_of_message = '20260509213000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'WISH2026050921300088'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260509213000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='SV8827461', cx_4='HSHS_STVINC', cx_5='MRN'), CX(cx_1='W7736251', cx_4='WISHIN', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='ZIELINSKI', xpn_2='RYAN', xpn_3='COLE', xpn_5='')
        pid.date_time_of_birth = '19790115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3817 Church St', xad_3='Stevens Point', xad_4='WI', xad_5='54481', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^715^3426680143'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='S')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='B3', pl_3='1', pl_4='HSHS_STVINC', pl_8='ED BAY')
        pv1.hospital_service = CWE(cwe_1='EM')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='SV00192847', xcn_4='HSHS_STVINC', xcn_5='AN')
        pv1.pending_location = PL(pl_1='20260509213000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R10.9', cwe_2='Unspecified abdominal pain', cwe_3='I10')
        dg1.diagnosis_date_time = '20260509'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/us-wisconsin/us-wisconsin-wishin.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='UWLAB')
        msh.receiving_application = HD(hd_1='WISHIN')
        msh.receiving_facility = HD(hd_1='WISHINHUB')
        msh.date_time_of_message = '20260509130000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'WISH2026050913000055'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='E7829401', cx_4='UWHEALTH', cx_5='MRN'), CX(cx_1='W9928374', cx_4='WISHIN', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='SCHROEDER', xpn_2='KEVIN', xpn_3='THOMAS', xpn_5='')
        pid.date_time_of_birth = '19680423'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1417 Winnebago St', xad_3='Madison', xad_4='WI', xad_5='53704', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^608^2517748921'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6E', pl_2='612', pl_3='1', pl_4='UWHEALTH')
        pv1.pv1_7 = '56789^NAKAMURA^GRACE^M^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD8829471', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKR88291', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509101500'
        orc.orc_12 = '12345^ENGSTROM^DANIEL^R^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD8829471', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKR88291', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='49563-0', cwe_2='TROPONIN I', cwe_3='LN')
        obr.observation_date_time = '20260509101500'
        obr.obr_15 = '12345^ENGSTROM^DANIEL^R^^^MD'
        obr.filler_field_2 = '20260509130000'
        obr.charge_to_practice = MOC(moc_1='LAB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='49563-0', cwe_2='Troponin I, High Sensitivity', cwe_3='LN')
        obx.obx_5 = '2847'
        obx.units = CWE(cwe_1='ng/L')
        obx.reference_range = '<14'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509125000'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.source_of_comment = 'L'
        nte.comment = 'CRITICAL VALUE - notified to PCP via WISHIN alert'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx
        observation.nte = nte

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
    """ Based on live/us-wisconsin/us-wisconsin-wishin.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='AURORA')
        msh.receiving_application = HD(hd_1='WISHIN')
        msh.receiving_facility = HD(hd_1='WISHINHUB')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'WISH2026050914000077'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260509140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='A9182734', cx_4='AURORA', cx_5='MRN'), CX(cx_1='W8736251', cx_4='WISHIN', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='XIONG', xpn_2='MAI', xpn_3='PANG', xpn_5='')
        pid.date_time_of_birth = '19880305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4012 S Layton Blvd', xad_3='Milwaukee', xad_4='WI', xad_5='53215', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^414^6729843501'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='S')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_2='200', pl_3='1', pl_4='AURORA')
        pv1.pv1_7 = '78901^LINDGREN^ERIC^W^^^MD'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='CCD', cwe_2='Continuity of Care Document')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260509130000'
        txa.txa_5 = '78901^LINDGREN^ERIC^W^^^MD'
        txa.transcription_date_time = '20260509140000'
        txa.txa_9 = '78901^LINDGREN^ERIC^W^^^MD'
        txa.placer_order_number = EI(ei_1='DOC88291001')
        txa.document_confidentiality_status = 'AU'
        txa.document_storage_status = 'AV'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'RP'
        obx.observation_identifier = CWE(cwe_1='LOINC34133-9', cwe_2='Summary of Episode Note', cwe_3='LN')
        obx.obx_5 = 'WISHIN/documents/CCD/W8736251_20260509.xml^AP^XML'
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
    """ Based on live/us-wisconsin/us-wisconsin-wishin.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='MARSHFIELD')
        msh.receiving_application = HD(hd_1='WISHIN')
        msh.receiving_facility = HD(hd_1='WISHINHUB')
        msh.date_time_of_message = '20260509093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'WISH2026050909300044'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260509093000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='M2847201', cx_4='MARSHFIELD', cx_5='MRN'), CX(cx_1='W6629183', cx_4='WISHIN', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='PFEIFFER', xpn_2='GERALD', xpn_3='WAYNE', xpn_5='')
        pid.date_time_of_birth = '19520917'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = [
            XAD(xad_1='1105 S Central Ave', xad_3='Marshfield', xad_4='WI', xad_5='54449', xad_7='H'),
            XAD(xad_1='PO Box 221', xad_3='Marshfield', xad_4='WI', xad_5='54449', xad_7='M'),
        ]
        pid.pid_13 = '^PRN^PH^^^715^3843390417~^NET^^gerald.pfeiffer@tds.net'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='LUT')
        pid.last_update_date_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4N', pl_2='402', pl_3='2', pl_4='MARSHFIELD')
        pv1.pv1_7 = '12345^ENGSTROM^DANIEL^R^^^MD'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='PFEIFFER', xpn_2='CAROL', xpn_3='J')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='1105 S Central Ave', xad_3='Marshfield', xad_4='WI', xad_5='54449')
        nk1.nk1_5 = '^PRN^PH^^^715^3843390418'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1]

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
    """ Based on live/us-wisconsin/us-wisconsin-wishin.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='BELLIN')
        msh.receiving_application = HD(hd_1='WISHIN')
        msh.receiving_facility = HD(hd_1='WISHINHUB')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'WISH2026050916000033'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260509160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='B5928173', cx_4='BELLIN', cx_5='MRN'), CX(cx_1='W5528174', cx_4='WISHIN', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='DEBOER', xpn_2='MITCHELL', xpn_3='JAMES', xpn_5='')
        pid.date_time_of_birth = '19790622'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1430 Dousman St', xad_3='Green Bay', xad_4='WI', xad_5='54303', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^920^4317702958'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='I3', pl_3='1', pl_4='BELLIN', pl_8='ICU')
        pv1.hospital_service = CWE(cwe_1='CCM')
        pv1.admit_source = CWE(cwe_1='2')
        pv1.admitting_doctor = XCN(xcn_1='BEL00482001', xcn_4='BELLIN', xcn_5='AN')
        pv1.bad_debt_agency_code = CWE(cwe_1='3W', cwe_2='312', cwe_3='1', cwe_4='BELLIN', cwe_8='3 WEST')
        pv1.pv1_40 = '20260507100000'
        pv1.current_patient_balance = '20260509160000'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
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
    """ Based on live/us-wisconsin/us-wisconsin-wishin.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WSLH')
        msh.sending_facility = HD(hd_1='WIDPH')
        msh.receiving_application = HD(hd_1='WISHIN')
        msh.receiving_facility = HD(hd_1='WISHINHUB')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'WISH2026050910000099'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='WSLH99281', cx_4='WSLH', cx_5='PI'), CX(cx_1='W4427362', cx_4='WISHIN', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='FIEDLER', xpn_2='GRETCHEN', xpn_3='LORRAINE', xpn_5='')
        pid.date_time_of_birth = '19650830'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='607 S 3rd Ave', xad_3='Wausau', xad_4='WI', xad_5='54401', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^715^8457721093'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='WSLH29384', ei_2='WSLH')
        orc.placer_order_group_number = EI(ei_1='WSLHGRP001')
        orc.response_flag = 'CM'
        orc.orc_10 = '20260508090000'
        orc.enterers_location = PL(pl_1='23456', pl_2='MORALES', pl_3='RAFAEL', pl_4='S', pl_7='MD')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='WSLH29384', ei_2='WSLH')
        obr.universal_service_identifier = CWE(cwe_1='543-9', cwe_2='MYCOBACTERIUM CULTURE', cwe_3='LN')
        obr.observation_date_time = '20260501090000'
        obr.obr_15 = '23456^MORALES^RAFAEL^S^^^MD'
        obr.filler_field_2 = '20260509100000'
        obr.charge_to_practice = MOC(moc_1='MB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='543-9', cwe_2='Mycobacterium sp identified', cwe_3='LN')
        obx.obx_5 = '115329001^Mycobacterium tuberculosis complex^SCT'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509090000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='6463-4', cwe_2='Culture comment', cwe_3='LN')
        obx_2.obx_5 = (
            'Mycobacterium tuberculosis complex isolated after 21 days incubation. Susceptibility testing in progress. Case reported to DHS Division of P'
            'ublic Health per Wis. Stat. 252.05.'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509090000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='WSLH-RPT', cwe_2='WSLH Lab Report', cwe_3='WSLH')
        obx_3.obx_5 = (
            'WSLH^AP^PDF^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFdTTEggTXljb2JhY3Rlcmlvbogy IFJlcG9ydCkKL0F1dGhvciAoV2lzY29uc2luIFN0YXRlIExhYm9yYXRvcnkgb2YgSHlnaWVuZSk'
            'KL1N1YmplY3QgKE15Y29iYWN0ZXJpdW0gQ3V'
        )
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509100000'

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

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
