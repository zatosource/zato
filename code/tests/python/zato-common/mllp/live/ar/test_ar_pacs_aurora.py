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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import DG1, EVN, IN1, MSH, NK1, OBR, OBX, ORC, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ar', 'ar-pacs-aurora.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ar/ar-pacs-aurora.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='HOSP_ITALIANO_BA')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='HOSP_ITALIANO_BA')
        msh.date_time_of_message = '20250310083012'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HIBA20250310083012001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40129385', cx_4='AURORA', cx_5='MRN'), CX(cx_1='25678934', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'GONZALEZ^Maria^Elena^^^Sra.'
        pid.date_time_of_birth = '19720418'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Pueyrredon 1640', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1118AAT', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^49590300'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casada', cwe_3='HL70002')
        pid.pid_19 = '25678934'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='CT01', pl_3='A', pl_4='HIBA', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1100234567', xcn_2='Martinez', xcn_3='Carlos', xcn_4='A', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='RAD', xcn_2='Radiologia', xcn_3='HIBASERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80012345', xcn_4='HIBAENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 310', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250310083000')

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
        orc.placer_order_number = EI(ei_1='ORD901001', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501001', ei_2='AURORA')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250310090000^^R'
        orc.date_time_of_order_event = '20250310083012'
        orc.orc_10 = 'LRODRIGUEZ^Rodriguez^Laura^M^^Lic.'
        orc.enterers_location = PL(pl_1='20250310083012')
        orc.order_effective_date_time = 'HOSP_ITALIANO_BA'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901001', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501001', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='71260', cwe_2='TC Torax con Contraste', cwe_3='CPT')
        obr.obr_16 = '1100234567^Martinez^Carlos^A^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250310090000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250310090000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R91.8', cwe_2='Otros hallazgos anormales no especificos del campo pulmonar', cwe_3='I10')
        dg1.diagnosis_date_time = '20250310'
        dg1.diagnosis_type = CWE(cwe_1='W', cwe_2='Working', cwe_3='HL70052')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='HOSP_CLINICAS')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='HOSP_CLINICAS')
        msh.date_time_of_message = '20250315101530'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HCL20250315101530001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40230198', cx_4='AURORA', cx_5='MRN'), CX(cx_1='31456789', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'FERNANDEZ^Juan^Carlos^^^Sr.'
        pid.date_time_of_birth = '19840225'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Cordoba 2351', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1120AAR', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^59508000'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltero', cwe_3='HL70002')
        pid.pid_19 = '31456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='MR02', pl_3='A', pl_4='HCLINICAS', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1100345678', xcn_2='Lopez', xcn_3='Alejandro', xcn_4='R', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='NEU', xcn_2='Neurologia', xcn_3='HCLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80023456', xcn_4='HCLENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250315101500')

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
        orc.placer_order_number = EI(ei_1='ORD901002', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501002', ei_2='AURORA')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250315110000^^R'
        orc.date_time_of_order_event = '20250315101530'
        orc.orc_10 = 'MPEREZ^Perez^Marcela^B^^Lic.'
        orc.enterers_location = PL(pl_1='20250315101530')
        orc.order_effective_date_time = 'HOSP_CLINICAS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901002', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501002', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='70553', cwe_2='RM Cerebro con y sin Contraste', cwe_3='CPT')
        obr.obr_16 = '1100345678^Lopez^Alejandro^R^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250315110000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250315110000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='G43.909', cwe_2='Migrana no especificada, no intratable, sin estado migrañoso', cwe_3='I10')
        dg1.diagnosis_date_time = '20250315'
        dg1.diagnosis_type = CWE(cwe_1='W', cwe_2='Working', cwe_3='HL70052')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='SANATORIO_GUEMES')
        msh.receiving_application = HD(hd_1='WORKLIST')
        msh.receiving_facility = HD(hd_1='SANATORIO_GUEMES')
        msh.date_time_of_message = '20250322141200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'SGU20250322141200001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250322141200'
        evn.operator_id = XCN(xcn_1='CMORALES', xcn_2='Morales', xcn_3='Claudia', xcn_4='S', xcn_6='Lic.')
        evn.event_occurred = '20250322140500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40331245', cx_4='AURORA', cx_5='MRN'), CX(cx_1='28934512', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'RODRIGUEZ^Ana^Beatriz^^^Sra.'
        pid.date_time_of_birth = '19780612'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Sanchez de Bustamante 1955', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1425DUA', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^48271900'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casada', cwe_3='HL70002')
        pid.pid_19 = '28934512'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='US01', pl_3='A', pl_4='SGUEMES', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1100456789', xcn_2='Diaz', xcn_3='Roberto', xcn_4='M', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='RAD', xcn_2='Radiologia', xcn_3='SGUSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80034567', xcn_4='SGUENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='SWISS_MEDICAL', cwe_2='Swiss Medical', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250322141200')

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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='HOSP_ITALIANO_BA')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_ITALIANO_BA')
        msh.date_time_of_message = '20250325163045'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HIBA20250325163045001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40129385', cx_4='AURORA', cx_5='MRN'), CX(cx_1='25678934', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'GONZALEZ^Maria^Elena^^^Sra.'
        pid.date_time_of_birth = '19720418'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Pueyrredon 1640', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1118AAT', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^49590300'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casada', cwe_3='HL70002')
        pid.pid_19 = '25678934'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='CT01', pl_3='A', pl_4='HIBA', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1100234567', xcn_2='Martinez', xcn_3='Carlos', xcn_4='A', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='RAD', xcn_2='Radiologia', xcn_3='HIBASERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80012345', xcn_4='HIBAENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 310', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250310083000')

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
        orc.placer_order_number = EI(ei_1='ORD901001', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501001', ei_2='AURORA')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250310090000^^R'
        orc.date_time_of_order_event = '20250325163045'
        orc.orc_10 = 'JGARCIA^Garcia^Jorge^L^^Lic.'
        orc.enterers_location = PL(pl_1='20250325163045')
        orc.order_effective_date_time = 'HOSP_ITALIANO_BA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901001', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501001', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='71260', cwe_2='TC Torax con Contraste', cwe_3='CPT')
        obr.observation_date_time = '20250310091500'
        obr.obr_16 = '1100234567^Martinez^Carlos^A^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250325163000'
        obr.diagnostic_serv_sect_id = 'CT'
        obr.result_status = 'F'
        obr.obr_27 = '^^^20250310090000^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='71260', cwe_2='TC Torax con Contraste', cwe_3='CPT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'HALLAZGOS: Se observa opacidad nodular de 12mm en lobulo inferior derecho. Sin adenopatias mediastinicas significativas. Parénquima pulmonar'
            ' restante sin alteraciones. CONCLUSION: Nodulo pulmonar solitario en LID. Se sugiere seguimiento con TC en 3 meses.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='TC Torax Imagen Clave', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'PACS_AURORA^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDABQODxIPDRQSEBIXFRQYHjIhHhwcHj0sLiQySUBMS0dARkVQWnNiUFVtVkVGZIhlbXd7gYKBTmCNl4x9lnN+gXz/2wBDARUXFx4aHjshITt8'
            'U0ZTfHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHx8fHz/wAARCABAAEADASIAAhEBAxEB/8QAGgAAAgMBAQAAAAAAAAAAAAAAAAUCBAYBA//EAC4Q'
            'AAIBAwIEBAUFAQAAAAAAAAECAwAEERIhBRMxQSJRYXEGFDKBkRUjQlLh8P/EABkBAAMBAQEAAAAAAAAAAAAAAAABAgMEBf/EAB4RAAICAgMBAQAAAAAAAAAAAAABAhEDIRIxQSJR/9oA'
            'DAMBAAIRAxEAPwC7xC9uXvpba3cxqnclQ2e+MnyrMXf'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='71260', cwe_2='TC Torax con Contraste', cwe_3='CPT')
        obx_3.observation_sub_id = OG(og_1='2')
        obx_3.obx_5 = 'R91.1^Nodulo pulmonar solitario^I10'
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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='HOSP_FERNANDEZ')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='HOSP_FERNANDEZ')
        msh.date_time_of_message = '20250401092300'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HFZ20250401092300001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40442356', cx_4='AURORA', cx_5='MRN'), CX(cx_1='22345678', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'MARTINEZ^Silvia^Graciela^^^Sra.'
        pid.date_time_of_birth = '19680903'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Cervino 3356', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1425AHN', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^48085000'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casada', cwe_3='HL70002')
        pid.pid_19 = '22345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='MG01', pl_3='A', pl_4='HFERNANDEZ', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1100567890', xcn_2='Gutierrez', xcn_3='Patricia', xcn_4='L', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='GIN', xcn_2='Ginecologia', xcn_3='HFZSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80045678', xcn_4='HFZENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='IOMA', cwe_2='IOMA', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250401092300')

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
        orc.placer_order_number = EI(ei_1='ORD901003', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501003', ei_2='AURORA')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250401100000^^R'
        orc.date_time_of_order_event = '20250401092300'
        orc.orc_10 = 'VLOPEZ^Lopez^Valeria^N^^Lic.'
        orc.enterers_location = PL(pl_1='20250401092300')
        orc.order_effective_date_time = 'HOSP_FERNANDEZ'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901003', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501003', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='77067', cwe_2='Mamografia Bilateral de Screening', cwe_3='CPT')
        obr.obr_16 = '1100567890^Gutierrez^Patricia^L^^Dra.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250401100000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250401100000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='Z12.31', cwe_2='Screening de neoplasia maligna de mama', cwe_3='I10')
        dg1.diagnosis_date_time = '20250401'
        dg1.diagnosis_type = CWE(cwe_1='W', cwe_2='Working', cwe_3='HL70052')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='HOSP_FERNANDEZ')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_FERNANDEZ')
        msh.date_time_of_message = '20250403110830'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HFZ20250403110830001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40442356', cx_4='AURORA', cx_5='MRN'), CX(cx_1='22345678', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'MARTINEZ^Silvia^Graciela^^^Sra.'
        pid.date_time_of_birth = '19680903'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Cervino 3356', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1425AHN', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^48085000'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casada', cwe_3='HL70002')
        pid.pid_19 = '22345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='MG01', pl_3='A', pl_4='HFERNANDEZ', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1100567890', xcn_2='Gutierrez', xcn_3='Patricia', xcn_4='L', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='GIN', xcn_2='Ginecologia', xcn_3='HFZSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80045678', xcn_4='HFZENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='IOMA', cwe_2='IOMA', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250401092300')

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
        orc.placer_order_number = EI(ei_1='ORD901003', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501003', ei_2='AURORA')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250401100000^^R'
        orc.date_time_of_order_event = '20250403110830'
        orc.orc_10 = 'JPEREZ^Perez^Julia^M^^Lic.'
        orc.enterers_location = PL(pl_1='20250403110830')
        orc.order_effective_date_time = 'HOSP_FERNANDEZ'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901003', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501003', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='77067', cwe_2='Mamografia Bilateral de Screening', cwe_3='CPT')
        obr.observation_date_time = '20250401101200'
        obr.obr_16 = '1100567890^Gutierrez^Patricia^L^^Dra.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250403110800'
        obr.diagnostic_serv_sect_id = 'MG'
        obr.result_status = 'F'
        obr.obr_27 = '^^^20250401100000^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='77067', cwe_2='Mamografia Bilateral', cwe_3='CPT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'HALLAZGOS: Mamas de densidad heterogenea (ACR tipo C). No se identifican masas, distorsiones arquitecturales ni microcalcificaciones sospech'
            'osas. Ganglios axilares de aspecto habitual. CONCLUSION: BI-RADS 1 - Negativo. Control anual.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='77067', cwe_2='Mamografia Bilateral', cwe_3='CPT')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'BI-RADS 1^Negativo^ACR'
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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='HOSP_AUSTRAL')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='HOSP_AUSTRAL')
        msh.date_time_of_message = '20250410143500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HAU20250410143500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40553467', cx_4='AURORA', cx_5='MRN'), CX(cx_1='35789012', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'ALVAREZ^Pablo^Daniel^^^Sr.'
        pid.date_time_of_birth = '19900114'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Juan D. Peron 1500', xad_3='Pilar', xad_4='Buenos Aires', xad_5='B1629AHJ', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^230^4482000'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '35789012'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='ECO1', pl_3='A', pl_4='HAUSTRAL', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1100678901', xcn_2='Rossi', xcn_3='Marcelo', xcn_4='F', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiologia', xcn_3='HAUSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80056789', xcn_4='HAUENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 450', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250410143500')

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
        orc.placer_order_number = EI(ei_1='ORD901004', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501004', ei_2='AURORA')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250410150000^^R'
        orc.date_time_of_order_event = '20250410143500'
        orc.orc_10 = 'AFERNANDEZ^Fernandez^Andrea^C^^Lic.'
        orc.enterers_location = PL(pl_1='20250410143500')
        orc.order_effective_date_time = 'HOSP_AUSTRAL'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901004', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501004', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='93306', cwe_2='Ecocardiograma Transtorácico Completo', cwe_3='CPT')
        obr.obr_16 = '1100678901^Rossi^Marcelo^F^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250410150000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250410150000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I50.9', cwe_2='Insuficiencia cardiaca no especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250410'
        dg1.diagnosis_type = CWE(cwe_1='W', cwe_2='Working', cwe_3='HL70052')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='HOSP_AUSTRAL')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_AUSTRAL')
        msh.date_time_of_message = '20250412091500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HAU20250412091500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40553467', cx_4='AURORA', cx_5='MRN'), CX(cx_1='35789012', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'ALVAREZ^Pablo^Daniel^^^Sr.'
        pid.date_time_of_birth = '19900114'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Juan D. Peron 1500', xad_3='Pilar', xad_4='Buenos Aires', xad_5='B1629AHJ', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^230^4482000'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '35789012'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='ECO1', pl_3='A', pl_4='HAUSTRAL', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1100678901', xcn_2='Rossi', xcn_3='Marcelo', xcn_4='F', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiologia', xcn_3='HAUSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80056789', xcn_4='HAUENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 450', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250410143500')

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
        orc.placer_order_number = EI(ei_1='ORD901004', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501004', ei_2='AURORA')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250410150000^^R'
        orc.date_time_of_order_event = '20250412091500'
        orc.orc_10 = 'JGARCIA^Garcia^Jorge^L^^Lic.'
        orc.enterers_location = PL(pl_1='20250412091500')
        orc.order_effective_date_time = 'HOSP_AUSTRAL'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901004', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501004', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='93306', cwe_2='Ecocardiograma Transtorácico Completo', cwe_3='CPT')
        obr.observation_date_time = '20250410151000'
        obr.obr_16 = '1100678901^Rossi^Marcelo^F^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250412091400'
        obr.diagnostic_serv_sect_id = 'US'
        obr.result_status = 'F'
        obr.obr_27 = '^^^20250410150000^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='93306', cwe_2='Ecocardiograma TT', cwe_3='CPT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'VI: Dimensiones normales. FEVI 62% (Simpson). Motilidad parietal global conservada. Patron diastolico de relajacion prolongada. AI levemente'
            ' dilatada (42mm). Cavidades derechas normales. Valvulas sin alteraciones significativas. Sin derrame pericardico. CONCLUSION: Disfuncion dia'
            'stolica grado I. AI levemente dilatada.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Informe Ecocardiograma', cwe_3='AUSPDI')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'PACS_AURORA^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovUmVzb3VyY2VzIDQgMCBSCi9NZWRpYUJveCBbMCAwIDYx'
            'MiA3OTJdCi9Db250ZW50cyA2IDAgUgo+PgplbmRvYmoK'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='8867-4', cwe_2='Frecuencia Cardiaca', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '72'
        obx_3.units = CWE(cwe_1='lpm')
        obx_3.reference_range = '60-100'
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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='HOSP_BRITANICO')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='HOSP_BRITANICO')
        msh.date_time_of_message = '20250418080045'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HBR20250418080045001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40664578', cx_4='AURORA', cx_5='MRN'), CX(cx_1='20123456', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'LOPEZ^Roberto^Enrique^^^Sr.'
        pid.date_time_of_birth = '19650721'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Solis 2081', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1134ACL', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^43091600'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '20123456'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='RX01', pl_3='A', pl_4='HBRITANICO', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1100789012', xcn_2='Sanchez', xcn_3='Eduardo', xcn_4='J', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='TRA', xcn_2='Traumatologia', xcn_3='HBRSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80067890', xcn_4='HBRENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250418080000')

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
        orc.placer_order_number = EI(ei_1='ORD901005', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501005', ei_2='AURORA')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250418083000^^R'
        orc.date_time_of_order_event = '20250418080045'
        orc.orc_10 = 'RGIMENEZ^Gimenez^Raquel^A^^Lic.'
        orc.enterers_location = PL(pl_1='20250418080045')
        orc.order_effective_date_time = 'HOSP_BRITANICO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901005', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501005', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='72170', cwe_2='Rx Pelvis AP y Lateral', cwe_3='CPT')
        obr.obr_16 = '1100789012^Sanchez^Eduardo^J^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250418083000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250418083000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M16.9', cwe_2='Coxartrosis no especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250418'
        dg1.diagnosis_type = CWE(cwe_1='W', cwe_2='Working', cwe_3='HL70052')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='HOSP_BRITANICO')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_BRITANICO')
        msh.date_time_of_message = '20250418110500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HBR20250418110500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40664578', cx_4='AURORA', cx_5='MRN'), CX(cx_1='20123456', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'LOPEZ^Roberto^Enrique^^^Sr.'
        pid.date_time_of_birth = '19650721'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Solis 2081', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1134ACL', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^43091600'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '20123456'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='RX01', pl_3='A', pl_4='HBRITANICO', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1100789012', xcn_2='Sanchez', xcn_3='Eduardo', xcn_4='J', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='TRA', xcn_2='Traumatologia', xcn_3='HBRSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80067890', xcn_4='HBRENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250418080000')

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
        orc.placer_order_number = EI(ei_1='ORD901005', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501005', ei_2='AURORA')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250418083000^^R'
        orc.date_time_of_order_event = '20250418110500'
        orc.orc_10 = 'JGARCIA^Garcia^Jorge^L^^Lic.'
        orc.enterers_location = PL(pl_1='20250418110500')
        orc.order_effective_date_time = 'HOSP_BRITANICO'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901005', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501005', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='72170', cwe_2='Rx Pelvis AP y Lateral', cwe_3='CPT')
        obr.observation_date_time = '20250418083500'
        obr.obr_16 = '1100789012^Sanchez^Eduardo^J^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250418110400'
        obr.diagnostic_serv_sect_id = 'CR'
        obr.result_status = 'F'
        obr.obr_27 = '^^^20250418083000^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='72170', cwe_2='Rx Pelvis', cwe_3='CPT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'HALLAZGOS: Disminucion del espacio articular coxofemoral bilateral, mas marcado a derecha. Osteofitos marginales en acetabulo y cabeza femor'
            'al. Esclerosis subcondral. CONCLUSION: Coxartrosis bilateral, predominio derecho, grado III de Kellgren-Lawrence.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='72170', cwe_2='Rx Pelvis', cwe_3='CPT')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'M16.0^Coxartrosis bilateral primaria^I10'
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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='FUND_FAVALORO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='FUND_FAVALORO')
        msh.date_time_of_message = '20250502060030'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'FFV20250502060030001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250502060000'
        evn.operator_id = XCN(xcn_1='MSILVA', xcn_2='Silva', xcn_3='Marina', xcn_4='C', xcn_6='Lic.')
        evn.event_occurred = '20250502055000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40775689', cx_4='AURORA', cx_5='MRN'), CX(cx_1='18567890', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'PEREZ^Jorge^Alberto^^^Sr.'
        pid.date_time_of_birth = '19590312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Belgrano 1746', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1093AAO', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^43781200'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='V', cwe_2='Viudo', cwe_3='HL70002')
        pid.pid_19 = '18567890'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='PEREZ', xpn_2='Claudia', xpn_3='Ines')
        nk1.relationship = CWE(cwe_1='HIJ', cwe_2='Hija', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Av. Belgrano 1746', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1093AAO', xad_6='AR', xad_7='L')
        nk1.nk1_5 = '^PRN^PH^^^11^43781201'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HEMO', pl_2='H201', pl_3='A', pl_4='FFAVALORO', pl_8='HEMO')
        pv1.attending_doctor = XCN(xcn_1='1100890123', xcn_2='Bianchi', xcn_3='Ricardo', xcn_4='H', xcn_6='Dr.', xcn_9='MN')
        pv1.referring_doctor = XCN(xcn_1='1100890124', xcn_2='Torres', xcn_3='Lucia', xcn_4='M', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiologia', xcn_3='FFVSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80078901', xcn_4='FFVENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 210', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250502060000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='OSDE210', cwe_2='OSDE Plan 210', cwe_4='OSDE')
        in1.insurance_company_id = CX(cx_1='50001')
        in1.insurance_company_name = XON(xon_1='OSDE')
        in1.insurance_company_address = XAD(xad_1='Av. Leandro N. Alem 1067', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1001AAF', xad_6='AR')
        in1.in1_6 = '^PRN^PH^^^11^52399000'
        in1.name_of_insured = XPN(xpn_1='20240101')
        in1.insureds_relationship_to_patient = CWE(cwe_1='20251231')
        in1.assignment_of_benefits = CWE(cwe_1='1', cwe_2='Titular', cwe_3='HL70072')
        in1.coordination_of_benefits = CWE(cwe_1='PEREZ', cwe_2='Jorge', cwe_3='Alberto')
        in1.coord_of_ben_priority = '01^Self^HL70063'
        in1.notice_of_admission_flag = '19590312'

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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='FUND_FAVALORO')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='FUND_FAVALORO')
        msh.date_time_of_message = '20250502071500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'FFV20250502071500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40775689', cx_4='AURORA', cx_5='MRN'), CX(cx_1='18567890', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'PEREZ^Jorge^Alberto^^^Sr.'
        pid.date_time_of_birth = '19590312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Belgrano 1746', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1093AAO', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^43781200'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='V', cwe_2='Viudo', cwe_3='HL70002')
        pid.pid_19 = '18567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HEMO', pl_2='H201', pl_3='A', pl_4='FFAVALORO', pl_8='HEMO')
        pv1.attending_doctor = XCN(xcn_1='1100890123', xcn_2='Bianchi', xcn_3='Ricardo', xcn_4='H', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiologia', xcn_3='FFVSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80078901', xcn_4='FFVENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 210', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250502060000')

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
        orc.placer_order_number = EI(ei_1='ORD901006', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501006', ei_2='AURORA')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250502080000^^R'
        orc.date_time_of_order_event = '20250502071500'
        orc.orc_10 = 'AFERNANDEZ^Fernandez^Andrea^C^^Lic.'
        orc.enterers_location = PL(pl_1='20250502071500')
        orc.order_effective_date_time = 'FUND_FAVALORO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901006', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501006', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='93458', cwe_2='Cateterismo Cardiaco Izq con Coronariografia', cwe_3='CPT')
        obr.obr_16 = '1100890123^Bianchi^Ricardo^H^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250502080000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250502080000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.10', cwe_2='Enfermedad cardiaca ateroesclerotica', cwe_3='I10')
        dg1.diagnosis_date_time = '20250502'
        dg1.diagnosis_type = CWE(cwe_1='W', cwe_2='Working', cwe_3='HL70052')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='FUND_FAVALORO')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='FUND_FAVALORO')
        msh.date_time_of_message = '20250502143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'FFV20250502143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40775689', cx_4='AURORA', cx_5='MRN'), CX(cx_1='18567890', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'PEREZ^Jorge^Alberto^^^Sr.'
        pid.date_time_of_birth = '19590312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Belgrano 1746', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1093AAO', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^43781200'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='V', cwe_2='Viudo', cwe_3='HL70002')
        pid.pid_19 = '18567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HEMO', pl_2='H201', pl_3='A', pl_4='FFAVALORO', pl_8='HEMO')
        pv1.attending_doctor = XCN(xcn_1='1100890123', xcn_2='Bianchi', xcn_3='Ricardo', xcn_4='H', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiologia', xcn_3='FFVSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80078901', xcn_4='FFVENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 210', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250502060000')

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
        orc.placer_order_number = EI(ei_1='ORD901006', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501006', ei_2='AURORA')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250502080000^^R'
        orc.date_time_of_order_event = '20250502143000'
        orc.orc_10 = 'JGARCIA^Garcia^Jorge^L^^Lic.'
        orc.enterers_location = PL(pl_1='20250502143000')
        orc.order_effective_date_time = 'FUND_FAVALORO'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901006', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501006', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='93458', cwe_2='Cateterismo Cardiaco Izq con Coronariografia', cwe_3='CPT')
        obr.observation_date_time = '20250502081500'
        obr.obr_16 = '1100890123^Bianchi^Ricardo^H^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250502142900'
        obr.diagnostic_serv_sect_id = 'XA'
        obr.result_status = 'F'
        obr.obr_27 = '^^^20250502080000^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='93458', cwe_2='Cateterismo Cardiaco', cwe_3='CPT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'HALLAZGOS: TCI sin lesiones. DA con estenosis severa (85%) en tercio proximal. Cx sin lesiones significativas. CD con estenosis moderada (50'
            '%) en tercio medio. FEVI por ventriculografia: 55%. CONCLUSION: Enfermedad coronaria severa de un vaso (DA proximal). Se indica angioplastia'
            ' con stent.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Coronariografia Imagen', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'PACS_AURORA^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEBLAEsAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMo'
            'GhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCABAAEADASIAAhEBAxEB/8QAGwABAAIDAQEAAAAAAAAAAAAAAAUGAQQHAwj/xAAz'
            'EAABAwIDBQUHBQEAAAAAAAABAAID'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='8867-4', cwe_2='Frecuencia Cardiaca', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '68'
        obx_3.units = CWE(cwe_1='lpm')
        obx_3.reference_range = '60-100'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='75994-4', cwe_2='FEVI', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '55'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '55-70'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='HOSP_GARRAHAN')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='HOSP_GARRAHAN')
        msh.date_time_of_message = '20250508141200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HGA20250508141200001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40886701', cx_4='AURORA', cx_5='MRN'), CX(cx_1='55123456', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='ROMERO', xpn_2='Valentina', xpn_4='')
        pid.date_time_of_birth = '20180506'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Combate de los Pozos 1881', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1245AAM', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^43089300'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltero', cwe_3='HL70002')
        pid.pid_19 = '55123456'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='US02', pl_3='A', pl_4='HGARRAHAN', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1100901234', xcn_2='Vega', xcn_3='Carolina', xcn_4='P', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='PED', xcn_2='Pediatria', xcn_3='HGASERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80089012', xcn_4='HGAENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250508141200')

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
        orc.placer_order_number = EI(ei_1='ORD901007', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501007', ei_2='AURORA')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250508143000^^R'
        orc.date_time_of_order_event = '20250508141200'
        orc.orc_10 = 'SMORENO^Moreno^Sofia^R^^Lic.'
        orc.enterers_location = PL(pl_1='20250508141200')
        orc.order_effective_date_time = 'HOSP_GARRAHAN'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901007', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501007', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='76700', cwe_2='Ecografia Abdominal Completa', cwe_3='CPT')
        obr.obr_16 = '1100901234^Vega^Carolina^P^^Dra.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250508143000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250508143000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R10.9', cwe_2='Dolor abdominal no especificado', cwe_3='I10')
        dg1.diagnosis_date_time = '20250508'
        dg1.diagnosis_type = CWE(cwe_1='W', cwe_2='Working', cwe_3='HL70052')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='HOSP_GARRAHAN')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_GARRAHAN')
        msh.date_time_of_message = '20250508154500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HGA20250508154500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40886701', cx_4='AURORA', cx_5='MRN'), CX(cx_1='55123456', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='ROMERO', xpn_2='Valentina', xpn_4='')
        pid.date_time_of_birth = '20180506'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Combate de los Pozos 1881', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1245AAM', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^43089300'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltero', cwe_3='HL70002')
        pid.pid_19 = '55123456'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='US02', pl_3='A', pl_4='HGARRAHAN', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1100901234', xcn_2='Vega', xcn_3='Carolina', xcn_4='P', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='PED', xcn_2='Pediatria', xcn_3='HGASERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80089012', xcn_4='HGAENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250508141200')

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
        orc.placer_order_number = EI(ei_1='ORD901007', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501007', ei_2='AURORA')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250508143000^^R'
        orc.date_time_of_order_event = '20250508154500'
        orc.orc_10 = 'JGARCIA^Garcia^Jorge^L^^Lic.'
        orc.enterers_location = PL(pl_1='20250508154500')
        orc.order_effective_date_time = 'HOSP_GARRAHAN'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901007', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501007', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='76700', cwe_2='Ecografia Abdominal Completa', cwe_3='CPT')
        obr.observation_date_time = '20250508143500'
        obr.obr_16 = '1100901234^Vega^Carolina^P^^Dra.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250508154400'
        obr.diagnostic_serv_sect_id = 'US'
        obr.result_status = 'F'
        obr.obr_27 = '^^^20250508143000^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='76700', cwe_2='Ecografia Abdominal', cwe_3='CPT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'HALLAZGOS: Higado de ecoestructura homogenea, tamaño conservado para la edad. Vesicula biliar normodistendida sin litiasis. Vias biliares no'
            ' dilatadas. Pancreas y bazo sin alteraciones. Riñones de forma y tamaño conservados, sin dilatacion pielocalicial. No se observa liquido lib'
            're. CONCLUSION: Ecografia abdominal dentro de limites normales.'
        )
        obx.observation_result_status = 'F'

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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='SANATORIO_ANCHORENA')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='SANATORIO_ANCHORENA')
        msh.date_time_of_message = '20250512091800'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SAN20250512091800001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40997812', cx_4='AURORA', cx_5='MRN'), CX(cx_1='17890123', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'GIMENEZ^Hector^Oscar^^^Sr.'
        pid.date_time_of_birth = '19570828'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Tomas de Anchorena 1872', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1425ELF', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^43093500'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '17890123'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='DOP1', pl_3='A', pl_4='SANCHORENA', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1101012345', xcn_2='Mendez', xcn_3='Gabriel', xcn_4='A', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='ANG', xcn_2='Angiologia', xcn_3='SANSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80090123', xcn_4='SANENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='SWISS_MEDICAL', cwe_2='Swiss Medical', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250512091800')

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
        orc.placer_order_number = EI(ei_1='ORD901008', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501008', ei_2='AURORA')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250512100000^^R'
        orc.date_time_of_order_event = '20250512091800'
        orc.orc_10 = 'LRUIZ^Ruiz^Lorena^E^^Lic.'
        orc.enterers_location = PL(pl_1='20250512091800')
        orc.order_effective_date_time = 'SANATORIO_ANCHORENA'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901008', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501008', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='93880', cwe_2='Eco Doppler Vasos de Cuello Bilateral', cwe_3='CPT')
        obr.obr_16 = '1101012345^Mendez^Gabriel^A^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250512100000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250512100000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I65.29', cwe_2='Oclusion y estenosis de arteria carotida no especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250512'
        dg1.diagnosis_type = CWE(cwe_1='W', cwe_2='Working', cwe_3='HL70052')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='SANATORIO_ANCHORENA')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='SANATORIO_ANCHORENA')
        msh.date_time_of_message = '20250512113000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SAN20250512113000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC40997812', cx_4='AURORA', cx_5='MRN'), CX(cx_1='17890123', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'GIMENEZ^Hector^Oscar^^^Sr.'
        pid.date_time_of_birth = '19570828'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Tomas de Anchorena 1872', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1425ELF', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^43093500'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '17890123'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='DOP1', pl_3='A', pl_4='SANCHORENA', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1101012345', xcn_2='Mendez', xcn_3='Gabriel', xcn_4='A', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='ANG', xcn_2='Angiologia', xcn_3='SANSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80090123', xcn_4='SANENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='SWISS_MEDICAL', cwe_2='Swiss Medical', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250512091800')

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
        orc.placer_order_number = EI(ei_1='ORD901008', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501008', ei_2='AURORA')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250512100000^^R'
        orc.date_time_of_order_event = '20250512113000'
        orc.orc_10 = 'JGARCIA^Garcia^Jorge^L^^Lic.'
        orc.enterers_location = PL(pl_1='20250512113000')
        orc.order_effective_date_time = 'SANATORIO_ANCHORENA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901008', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501008', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='93880', cwe_2='Eco Doppler Vasos de Cuello Bilateral', cwe_3='CPT')
        obr.observation_date_time = '20250512101000'
        obr.obr_16 = '1101012345^Mendez^Gabriel^A^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250512112900'
        obr.diagnostic_serv_sect_id = 'US'
        obr.result_status = 'F'
        obr.obr_27 = '^^^20250512100000^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='93880', cwe_2='Eco Doppler Carotideo', cwe_3='CPT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'HALLAZGOS: Carotida comun derecha con placa fibrocalcificada que genera estenosis del 45%. Carotida interna derecha permeable. Carotida comu'
            'n izquierda con placa blanda que genera estenosis del 30%. Vertebrales permeables con flujo anterogrado. CONCLUSION: Ateromatosis carotidea '
            'bilateral leve a moderada. Sin criterios hemodinamicos de estenosis significativa.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='93880', cwe_2='VPS Carotida Interna Derecha', cwe_3='CPT')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '95'
        obx_2.units = CWE(cwe_1='cm/s')
        obx_2.reference_range = '<125'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='93880', cwe_2='VPS Carotida Interna Izquierda', cwe_3='CPT')
        obx_3.observation_sub_id = OG(og_1='2')
        obx_3.obx_5 = '78'
        obx_3.units = CWE(cwe_1='cm/s')
        obx_3.reference_range = '<125'
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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='HOSP_EL_CRUCE')
        msh.receiving_application = HD(hd_1='WORKLIST')
        msh.receiving_facility = HD(hd_1='HOSP_EL_CRUCE')
        msh.date_time_of_message = '20250520103000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'HEC20250520103000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250520103000'
        evn.operator_id = XCN(xcn_1='DCASTRO', xcn_2='Castro', xcn_3='Diana', xcn_4='M', xcn_6='Lic.')
        evn.event_occurred = '20250520102000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC41108923', cx_4='AURORA', cx_5='MRN'), CX(cx_1='38901234', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'ACOSTA^Luciana^Soledad^^^Sra.'
        pid.date_time_of_birth = '19920707'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Calchaqui 5401', xad_3='Florencio Varela', xad_4='Buenos Aires', xad_5='B1888AAE', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^42109000'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltera', cwe_3='HL70002')
        pid.pid_19 = '38901234'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='MR01', pl_3='A', pl_4='HELCRUCE', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1101123456', xcn_2='Rios', xcn_3='Fernando', xcn_4='D', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='NEU', xcn_2='Neurologia', xcn_3='HECSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80101234', xcn_4='HECENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='IOMA', cwe_2='IOMA', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250520103000')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='HOSP_POSADAS')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='HOSP_POSADAS')
        msh.date_time_of_message = '20250525082000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HPO20250525082000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC41219034', cx_4='AURORA', cx_5='MRN'), CX(cx_1='27654321', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'TORRES^Miguel^Angel^^^Sr.'
        pid.date_time_of_birth = '19770415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Presidente Illia s/n', xad_3='El Palomar', xad_4='Buenos Aires', xad_5='B1684', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^44697500'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '27654321'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='CT02', pl_3='A', pl_4='HPOSADAS', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1101234567', xcn_2='Castillo', xcn_3='Andres', xcn_4='M', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='GAS', xcn_2='Gastroenterologia', xcn_3='HPOSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80112345', xcn_4='HPOENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250525082000')

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
        orc.placer_order_number = EI(ei_1='ORD901009', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501009', ei_2='AURORA')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250525090000^^R'
        orc.date_time_of_order_event = '20250525082000'
        orc.orc_10 = 'MDIAZ^Diaz^Mariana^L^^Lic.'
        orc.enterers_location = PL(pl_1='20250525082000')
        orc.order_effective_date_time = 'HOSP_POSADAS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901009', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501009', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='74178', cwe_2='TC Abdomen y Pelvis con Contraste', cwe_3='CPT')
        obr.obr_16 = '1101234567^Castillo^Andres^M^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250525090000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250525090000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.20', cwe_2='Calculo de vesicula biliar sin colecistitis', cwe_3='I10')
        dg1.diagnosis_date_time = '20250525'
        dg1.diagnosis_type = CWE(cwe_1='W', cwe_2='Working', cwe_3='HL70052')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/ar/ar-pacs-aurora.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_AURORA')
        msh.sending_facility = HD(hd_1='HOSP_POSADAS')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_POSADAS')
        msh.date_time_of_message = '20250525134500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HPO20250525134500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAC41219034', cx_4='AURORA', cx_5='MRN'), CX(cx_1='27654321', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'TORRES^Miguel^Angel^^^Sr.'
        pid.date_time_of_birth = '19770415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Presidente Illia s/n', xad_3='El Palomar', xad_4='Buenos Aires', xad_5='B1684', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^44697500'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '27654321'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='CT02', pl_3='A', pl_4='HPOSADAS', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1101234567', xcn_2='Castillo', xcn_3='Andres', xcn_4='M', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='GAS', xcn_2='Gastroenterologia', xcn_3='HPOSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80112345', xcn_4='HPOENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250525082000')

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
        orc.placer_order_number = EI(ei_1='ORD901009', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='RAD501009', ei_2='AURORA')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250525090000^^R'
        orc.date_time_of_order_event = '20250525134500'
        orc.orc_10 = 'JGARCIA^Garcia^Jorge^L^^Lic.'
        orc.enterers_location = PL(pl_1='20250525134500')
        orc.order_effective_date_time = 'HOSP_POSADAS'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901009', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='RAD501009', ei_2='AURORA')
        obr.universal_service_identifier = CWE(cwe_1='74178', cwe_2='TC Abdomen y Pelvis con Contraste', cwe_3='CPT')
        obr.observation_date_time = '20250525091000'
        obr.obr_16 = '1101234567^Castillo^Andres^M^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250525134400'
        obr.diagnostic_serv_sect_id = 'CT'
        obr.result_status = 'F'
        obr.obr_27 = '^^^20250525090000^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='74178', cwe_2='TC Abdomen y Pelvis', cwe_3='CPT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'HALLAZGOS: Higado de tamaño normal con densidad homogenea. Vesicula biliar con multiples imagenes litiasicas de hasta 15mm. Vias biliares no'
            ' dilatadas. Pancreas, bazo y suprarrenales sin alteraciones. Riñones con buena diferenciacion corticomedular. No se observan adenopatias ret'
            'roperitoneales. CONCLUSION: Litiasis vesicular multiple. Sin otras alteraciones significativas.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='TC Abdomen Reconstruccion', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'PACS_AURORA^IMAGE^PNG^Base64^'
            'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEwAACxMBAJqcGAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vu'
            'PBoAAARsSURBVHic7ZtNaBxlGMd/M5vdTTbZbJI2bWxia1tbP1C0VmxRxINVFBEPnlT04kG8eFBP4kUQ8eDRg4cKgnhRUAQVUbGK2ipaW6nVWmPTmDRtk002m49NstmZ8eBMM7OZ3e7s'
            '7Mxm438OM++87/N/n//zzrwzQ4T/OTT'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='74178', cwe_2='TC Abdomen y Pelvis', cwe_3='CPT')
        obx_3.observation_sub_id = OG(og_1='2')
        obx_3.obx_5 = 'K80.20^Litiasis vesicular sin colecistitis^I10'
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
