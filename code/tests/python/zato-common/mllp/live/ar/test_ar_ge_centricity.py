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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, HD, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA03Procedure, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A03, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import DG1, EVN, IN1, MSH, NK1, OBR, OBX, ORC, PID, PR1, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ar', 'ar-ge-centricity.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ar/ar-ge-centricity.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='HOSP_ITALIANO_BA')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='HOSP_ITALIANO_BA')
        msh.date_time_of_message = '20250303080500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HIBA20250303080500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70012345', cx_4='GECENT', cx_5='MRN'), CX(cx_1='32456789', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'RAMIREZ^Federico^Luis^^^Sr.'
        pid.date_time_of_birth = '19850917'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gascon 450', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1181ACH', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^49590300'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '32456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='CT01', pl_3='A', pl_4='HIBA', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1102012345', xcn_2='Colombo', xcn_3='Alejandro', xcn_4='M', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='EME', xcn_2='Emergencias', xcn_3='HIBASERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70012345', xcn_4='HIBAENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 410', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250303080500')

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
        orc.placer_order_number = EI(ei_1='ORD701001', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='GE501001', ei_2='GE_CENT')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250303083000^^R'
        orc.date_time_of_order_event = '20250303080500'
        orc.orc_10 = 'LMORETTI^Moretti^Lucia^A^^Lic.'
        orc.enterers_location = PL(pl_1='20250303080500')
        orc.order_effective_date_time = 'HOSP_ITALIANO_BA'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701001', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='GE501001', ei_2='GE_CENT')
        obr.universal_service_identifier = CWE(cwe_1='70450', cwe_2='TC Cerebro sin Contraste', cwe_3='CPT')
        obr.obr_16 = '1102012345^Colombo^Alejandro^M^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250303083000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250303083000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='S06.9', cwe_2='Traumatismo intracraneal no especificado', cwe_3='I10')
        dg1.diagnosis_date_time = '20250303'
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
    """ Based on live/ar/ar-ge-centricity.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='HOSP_ITALIANO_BA')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_ITALIANO_BA')
        msh.date_time_of_message = '20250303103000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HIBA20250303103000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70012345', cx_4='GECENT', cx_5='MRN'), CX(cx_1='32456789', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'RAMIREZ^Federico^Luis^^^Sr.'
        pid.date_time_of_birth = '19850917'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gascon 450', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1181ACH', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^49590300'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '32456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='CT01', pl_3='A', pl_4='HIBA', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1102012345', xcn_2='Colombo', xcn_3='Alejandro', xcn_4='M', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='EME', xcn_2='Emergencias', xcn_3='HIBASERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70012345', xcn_4='HIBAENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 410', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250303080500')

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
        orc.placer_order_number = EI(ei_1='ORD701001', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='GE501001', ei_2='GE_CENT')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250303083000^^R'
        orc.date_time_of_order_event = '20250303103000'
        orc.orc_10 = 'LMORETTI^Moretti^Lucia^A^^Lic.'
        orc.enterers_location = PL(pl_1='20250303103000')
        orc.order_effective_date_time = 'HOSP_ITALIANO_BA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701001', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='GE501001', ei_2='GE_CENT')
        obr.universal_service_identifier = CWE(cwe_1='70450', cwe_2='TC Cerebro sin Contraste', cwe_3='CPT')
        obr.observation_date_time = '20250303083500'
        obr.obr_16 = '1102012345^Colombo^Alejandro^M^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250303102800'
        obr.diagnostic_serv_sect_id = 'CT'
        obr.result_status = 'F'
        obr.obr_27 = '^^^20250303083000^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='70450', cwe_2='TC Cerebro', cwe_3='CPT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'HALLAZGOS: Estructuras de linea media centradas. Sin colecciones intra ni extraaxiales. Cisterna basal y surcos corticales de amplitud conse'
            'rvada. Fosa posterior sin alteraciones. Calota sin trazos fracturarios. CONCLUSION: TC cerebro sin evidencia de lesion aguda postraumatica.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='TC Cerebro Imagen Axial', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'GE_CENT^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEB'
            'AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCABAAEADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL'
            '/8QAtRAAAgEDAwIEAw'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='70450', cwe_2='TC Cerebro', cwe_3='CPT')
        obx_3.observation_sub_id = OG(og_1='2')
        obx_3.obx_5 = 'Z03.3^Observacion por sospecha de trastorno del sistema nervioso^I10'
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
    """ Based on live/ar/ar-ge-centricity.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='SANATORIO_TRINIDAD_P')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='SANATORIO_TRINIDAD_P')
        msh.date_time_of_message = '20250310141500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'STP20250310141500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70023456', cx_4='GECENT', cx_5='MRN'), CX(cx_1='28567890', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'HERRERA^Gabriela^Alejandra^^^Sra.'
        pid.date_time_of_birth = '19790405'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Cervino 4720', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1425BEJ', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^52399500'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casada', cwe_3='HL70002')
        pid.pid_19 = '28567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='MR01', pl_3='A', pl_4='STRINIDAD', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1102123456', xcn_2='Ferreyra', xcn_3='Pablo', xcn_4='A', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiologia', xcn_3='STPSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70023456', xcn_4='STPENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='SWISS_MEDICAL', cwe_2='Swiss Medical', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250310141500')

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
        orc.placer_order_number = EI(ei_1='ORD701002', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='GE501002', ei_2='GE_CENT')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250310150000^^R'
        orc.date_time_of_order_event = '20250310141500'
        orc.orc_10 = 'NROJAS^Rojas^Natalia^M^^Lic.'
        orc.enterers_location = PL(pl_1='20250310141500')
        orc.order_effective_date_time = 'SANATORIO_TRINIDAD_P'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701002', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='GE501002', ei_2='GE_CENT')
        obr.universal_service_identifier = CWE(cwe_1='75561', cwe_2='RM Cardiaca con Contraste', cwe_3='CPT')
        obr.obr_16 = '1102123456^Ferreyra^Pablo^A^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250310150000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250310150000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I42.0', cwe_2='Miocardiopatia dilatada', cwe_3='I10')
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
    """ Based on live/ar/ar-ge-centricity.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='SANATORIO_TRINIDAD_P')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='SANATORIO_TRINIDAD_P')
        msh.date_time_of_message = '20250312094500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'STP20250312094500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70023456', cx_4='GECENT', cx_5='MRN'), CX(cx_1='28567890', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'HERRERA^Gabriela^Alejandra^^^Sra.'
        pid.date_time_of_birth = '19790405'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Cervino 4720', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1425BEJ', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^52399500'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casada', cwe_3='HL70002')
        pid.pid_19 = '28567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='MR01', pl_3='A', pl_4='STRINIDAD', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1102123456', xcn_2='Ferreyra', xcn_3='Pablo', xcn_4='A', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiologia', xcn_3='STPSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70023456', xcn_4='STPENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='SWISS_MEDICAL', cwe_2='Swiss Medical', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250310141500')

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
        orc.placer_order_number = EI(ei_1='ORD701002', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='GE501002', ei_2='GE_CENT')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250310150000^^R'
        orc.date_time_of_order_event = '20250312094500'
        orc.orc_10 = 'NROJAS^Rojas^Natalia^M^^Lic.'
        orc.enterers_location = PL(pl_1='20250312094500')
        orc.order_effective_date_time = 'SANATORIO_TRINIDAD_P'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701002', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='GE501002', ei_2='GE_CENT')
        obr.universal_service_identifier = CWE(cwe_1='75561', cwe_2='RM Cardiaca con Contraste', cwe_3='CPT')
        obr.observation_date_time = '20250310151500'
        obr.obr_16 = '1102123456^Ferreyra^Pablo^A^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250312094300'
        obr.diagnostic_serv_sect_id = 'MR'
        obr.result_status = 'F'
        obr.obr_27 = '^^^20250310150000^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='75561', cwe_2='RM Cardiaca', cwe_3='CPT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'HALLAZGOS: VI dilatado con diametro diastolico de 62mm. FEVI 38% por metodo de Simpson. Adelgazamiento de pared inferolateral con realce tar'
            'dio transmural compatible con fibrosis. Motilidad global reducida. VD de dimensiones conservadas con funcion sistolica normal. Valvulas sin '
            'regurgitacion significativa. Sin derrame pericardico. CONCLUSION: Miocardiopatia dilatada con FEVI severamente reducida. Patron de realce ta'
            'rdio compatible con etiologia isquemica.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='8867-4', cwe_2='Frecuencia Cardiaca', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '78'
        obx_2.units = CWE(cwe_1='lpm')
        obx_2.reference_range = '60-100'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='75994-4', cwe_2='FEVI RM', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '38'
        obx_3.units = CWE(cwe_1='%')
        obx_3.reference_range = '55-70'
        obx_3.interpretation_codes = CWE(cwe_1='L')
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
    """ Based on live/ar/ar-ge-centricity.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='FLENI')
        msh.receiving_application = HD(hd_1='WORKLIST')
        msh.receiving_facility = HD(hd_1='FLENI')
        msh.date_time_of_message = '20250318100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'FLE20250318100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250318100000'
        evn.operator_id = XCN(xcn_1='PVILLALBA', xcn_2='Villalba', xcn_3='Paula', xcn_4='S', xcn_6='Lic.')
        evn.event_occurred = '20250318095000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70034567', cx_4='GECENT', cx_5='MRN'), CX(cx_1='23678901', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'CASTRO^Horacio^Nestor^^^Sr.'
        pid.date_time_of_birth = '19640215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Montañeses 2325', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1428AQK', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^57773200'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '23678901'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='PET1', pl_3='A', pl_4='FLENI', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1102234567', xcn_2='Bustamante', xcn_3='Eduardo', xcn_4='R', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='ONC', xcn_2='Oncologia', xcn_3='FLESERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70034567', xcn_4='FLEENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 510', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250318100000')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/ar/ar-ge-centricity.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='FLENI')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='FLENI')
        msh.date_time_of_message = '20250318101500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'FLE20250318101500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70034567', cx_4='GECENT', cx_5='MRN'), CX(cx_1='23678901', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'CASTRO^Horacio^Nestor^^^Sr.'
        pid.date_time_of_birth = '19640215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Montañeses 2325', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1428AQK', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^57773200'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '23678901'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='PET1', pl_3='A', pl_4='FLENI', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1102234567', xcn_2='Bustamante', xcn_3='Eduardo', xcn_4='R', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='ONC', xcn_2='Oncologia', xcn_3='FLESERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70034567', xcn_4='FLEENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 510', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250318100000')

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
        orc.placer_order_number = EI(ei_1='ORD701003', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='GE501003', ei_2='GE_CENT')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250318110000^^R'
        orc.date_time_of_order_event = '20250318101500'
        orc.orc_10 = 'PVILLALBA^Villalba^Paula^S^^Lic.'
        orc.enterers_location = PL(pl_1='20250318101500')
        orc.order_effective_date_time = 'FLENI'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701003', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='GE501003', ei_2='GE_CENT')
        obr.universal_service_identifier = CWE(cwe_1='78816', cwe_2='PET/CT Cuerpo Entero con FDG', cwe_3='CPT')
        obr.obr_16 = '1102234567^Bustamante^Eduardo^R^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250318110000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250318110000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C34.90', cwe_2='Neoplasia maligna de pulmon no especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250318'
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
    """ Based on live/ar/ar-ge-centricity.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='FLENI')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='FLENI')
        msh.date_time_of_message = '20250320143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'FLE20250320143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70034567', cx_4='GECENT', cx_5='MRN'), CX(cx_1='23678901', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'CASTRO^Horacio^Nestor^^^Sr.'
        pid.date_time_of_birth = '19640215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Montañeses 2325', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1428AQK', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^57773200'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '23678901'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='PET1', pl_3='A', pl_4='FLENI', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1102234567', xcn_2='Bustamante', xcn_3='Eduardo', xcn_4='R', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='ONC', xcn_2='Oncologia', xcn_3='FLESERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70034567', xcn_4='FLEENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 510', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250318100000')

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
        orc.placer_order_number = EI(ei_1='ORD701003', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='GE501003', ei_2='GE_CENT')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250318110000^^R'
        orc.date_time_of_order_event = '20250320143000'
        orc.orc_10 = 'PVILLALBA^Villalba^Paula^S^^Lic.'
        orc.enterers_location = PL(pl_1='20250320143000')
        orc.order_effective_date_time = 'FLENI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701003', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='GE501003', ei_2='GE_CENT')
        obr.universal_service_identifier = CWE(cwe_1='78816', cwe_2='PET/CT Cuerpo Entero con FDG', cwe_3='CPT')
        obr.observation_date_time = '20250318112000'
        obr.obr_16 = '1102234567^Bustamante^Eduardo^R^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250320142800'
        obr.diagnostic_serv_sect_id = 'PT'
        obr.result_status = 'F'
        obr.obr_27 = '^^^20250318110000^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='78816', cwe_2='PET/CT', cwe_3='CPT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'HALLAZGOS: Masa pulmonar en lobulo superior derecho de 35x28mm con hipermetabolismo intenso (SUVmax 12.4). Adenopatia mediastinica paratraqu'
            'eal derecha de 18mm con SUVmax 8.2. Adenopatia subcarinal de 15mm con SUVmax 6.8. Sin captacion patologica hepatica, osea ni suprarrenal. CO'
            'NCLUSION: Neoplasia pulmonar metabolicamente activa con compromiso ganglionar mediastinico (N2). Estadificacion sugerida: T2aN2M0 (IIIA).'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='78816', cwe_2='SUVmax Lesion Primaria', cwe_3='CPT')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '12.4'
        obx_2.units = CWE(cwe_1='SUV')
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
    """ Based on live/ar/ar-ge-centricity.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='HOSP_AUSTRAL')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='HOSP_AUSTRAL')
        msh.date_time_of_message = '20250325093000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HAU20250325093000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70045678', cx_4='GECENT', cx_5='MRN'), CX(cx_1='26789012', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'SILVA^Adriana^Beatriz^^^Sra.'
        pid.date_time_of_birth = '19750130'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Los Cardos 287', xad_3='Pilar', xad_4='Buenos Aires', xad_5='B1629', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^230^4482000'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casada', cwe_3='HL70002')
        pid.pid_19 = '26789012'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='MR02', pl_3='A', pl_4='HAUSTRAL', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1102345678', xcn_2='Gallo', xcn_3='Roberto', xcn_4='M', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='NEU', xcn_2='Neurocirugia', xcn_3='HAUSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70045678', xcn_4='HAUENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 310', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250325093000')

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
        orc.placer_order_number = EI(ei_1='ORD701004', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='GE501004', ei_2='GE_CENT')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250325100000^^R'
        orc.date_time_of_order_event = '20250325093000'
        orc.orc_10 = 'CFIGUEROA^Figueroa^Carolina^L^^Lic.'
        orc.enterers_location = PL(pl_1='20250325093000')
        orc.order_effective_date_time = 'HOSP_AUSTRAL'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701004', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='GE501004', ei_2='GE_CENT')
        obr.universal_service_identifier = CWE(cwe_1='72148', cwe_2='RM Columna Lumbar sin Contraste', cwe_3='CPT')
        obr.obr_16 = '1102345678^Gallo^Roberto^M^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250325100000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250325100000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M54.5', cwe_2='Lumbago no especificado', cwe_3='I10')
        dg1.diagnosis_date_time = '20250325'
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
    """ Based on live/ar/ar-ge-centricity.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='HOSP_AUSTRAL')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_AUSTRAL')
        msh.date_time_of_message = '20250326100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HAU20250326100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70045678', cx_4='GECENT', cx_5='MRN'), CX(cx_1='26789012', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'SILVA^Adriana^Beatriz^^^Sra.'
        pid.date_time_of_birth = '19750130'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Los Cardos 287', xad_3='Pilar', xad_4='Buenos Aires', xad_5='B1629', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^230^4482000'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casada', cwe_3='HL70002')
        pid.pid_19 = '26789012'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='MR02', pl_3='A', pl_4='HAUSTRAL', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1102345678', xcn_2='Gallo', xcn_3='Roberto', xcn_4='M', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='NEU', xcn_2='Neurocirugia', xcn_3='HAUSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70045678', xcn_4='HAUENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 310', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250325093000')

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
        orc.placer_order_number = EI(ei_1='ORD701004', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='GE501004', ei_2='GE_CENT')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250325100000^^R'
        orc.date_time_of_order_event = '20250326100000'
        orc.orc_10 = 'CFIGUEROA^Figueroa^Carolina^L^^Lic.'
        orc.enterers_location = PL(pl_1='20250326100000')
        orc.order_effective_date_time = 'HOSP_AUSTRAL'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701004', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='GE501004', ei_2='GE_CENT')
        obr.universal_service_identifier = CWE(cwe_1='72148', cwe_2='RM Columna Lumbar sin Contraste', cwe_3='CPT')
        obr.observation_date_time = '20250325101000'
        obr.obr_16 = '1102345678^Gallo^Roberto^M^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250326095800'
        obr.diagnostic_serv_sect_id = 'MR'
        obr.result_status = 'F'
        obr.obr_27 = '^^^20250325100000^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='72148', cwe_2='RM Columna Lumbar', cwe_3='CPT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'HALLAZGOS: Discopatia degenerativa L4-L5 y L5-S1. Hernia discal posterolateral izquierda L5-S1 que contacta raiz S1 homolateral. Estenosis f'
            'oraminal izquierda L5-S1 moderada. Canal raquideo de calibre conservado. Cono medular de señal normal. CONCLUSION: Hernia discal L5-S1 con c'
            'ompromiso radicular S1 izquierda.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='72148', cwe_2='RM Columna Lumbar', cwe_3='CPT')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'M51.16^Trastorno de disco intervertebral lumbar con radiculopatia^I10'
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
    """ Based on live/ar/ar-ge-centricity.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='HOSP_EL_CRUCE')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HOSP_EL_CRUCE')
        msh.date_time_of_message = '20250401054500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'HEC20250401054500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250401054500'
        evn.operator_id = XCN(xcn_1='ESUAREZ', xcn_2='Suarez', xcn_3='Esteban', xcn_4='R', xcn_6='Lic.')
        evn.event_occurred = '20250401050000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70056789', cx_4='GECENT', cx_5='MRN'), CX(cx_1='35890123', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'MANSILLA^Esteban^Roberto^^^Sr.'
        pid.date_time_of_birth = '19910822'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Calchaqui 5401', xad_3='Florencio Varela', xad_4='Buenos Aires', xad_5='B1888AAE', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^42109000'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltero', cwe_3='HL70002')
        pid.pid_19 = '35890123'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='MANSILLA', xpn_2='Estela', xpn_3='Rosa')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Madre', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Av. Calchaqui 5401', xad_3='Florencio Varela', xad_4='Buenos Aires', xad_5='B1888AAE', xad_6='AR', xad_7='L')
        nk1.nk1_5 = '^PRN^PH^^^11^42109001'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NCIR', pl_2='N501', pl_3='A', pl_4='HELCRUCE', pl_8='NCIR')
        pv1.attending_doctor = XCN(xcn_1='1102456789', xcn_2='Lucero', xcn_3='Damian', xcn_4='G', xcn_6='Dr.', xcn_9='MN')
        pv1.referring_doctor = XCN(xcn_1='1102456790', xcn_2='Ojeda', xcn_3='Marina', xcn_4='F', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='NCR', xcn_2='Neurocirugia', xcn_3='HECSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70056789', xcn_4='HECENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='IOMA', cwe_2='IOMA', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250401054500')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='IOMA001', cwe_2='IOMA', cwe_4='IOMA')
        in1.insurance_company_id = CX(cx_1='70001')
        in1.insurance_company_name = XON(xon_1='IOMA')
        in1.insurance_company_address = XAD(xad_1='Calle 46 N 886', xad_3='La Plata', xad_4='Buenos Aires', xad_5='B1900', xad_6='AR')
        in1.in1_6 = '^PRN^PH^^^221^4211111'
        in1.name_of_insured = XPN(xpn_1='20240101')
        in1.insureds_relationship_to_patient = CWE(cwe_1='20251231')
        in1.assignment_of_benefits = CWE(cwe_1='1', cwe_2='Titular', cwe_3='HL70072')
        in1.coordination_of_benefits = CWE(cwe_1='MANSILLA', cwe_2='Esteban', cwe_3='Roberto')
        in1.coord_of_ben_priority = '01^Self^HL70063'
        in1.notice_of_admission_flag = '19910822'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C71.1', cwe_2='Neoplasia maligna del lobulo frontal', cwe_3='I10')
        dg1.diagnosis_date_time = '20250401'
        dg1.diagnosis_type = CWE(cwe_1='A', cwe_2='Admitting', cwe_3='HL70052')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance
        msg.extra_segments = [dg1]

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
    """ Based on live/ar/ar-ge-centricity.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='HOSP_EL_CRUCE')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='HOSP_EL_CRUCE')
        msh.date_time_of_message = '20250404080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HEC20250404080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70056789', cx_4='GECENT', cx_5='MRN'), CX(cx_1='35890123', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'MANSILLA^Esteban^Roberto^^^Sr.'
        pid.date_time_of_birth = '19910822'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Calchaqui 5401', xad_3='Florencio Varela', xad_4='Buenos Aires', xad_5='B1888AAE', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^42109000'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltero', cwe_3='HL70002')
        pid.pid_19 = '35890123'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NCIR', pl_2='N501', pl_3='A', pl_4='HELCRUCE', pl_8='NCIR')
        pv1.attending_doctor = XCN(xcn_1='1102456789', xcn_2='Lucero', xcn_3='Damian', xcn_4='G', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='NCR', xcn_2='Neurocirugia', xcn_3='HECSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70056789', xcn_4='HECENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='IOMA', cwe_2='IOMA', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250401054500')

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
        orc.placer_order_number = EI(ei_1='ORD701005', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='GE501005', ei_2='GE_CENT')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250404090000^^R'
        orc.date_time_of_order_event = '20250404080000'
        orc.orc_10 = 'ESUAREZ^Suarez^Esteban^R^^Lic.'
        orc.enterers_location = PL(pl_1='20250404080000')
        orc.order_effective_date_time = 'HOSP_EL_CRUCE'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701005', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='GE501005', ei_2='GE_CENT')
        obr.universal_service_identifier = CWE(cwe_1='70553', cwe_2='RM Cerebro con y sin Contraste', cwe_3='CPT')
        obr.obr_16 = '1102456789^Lucero^Damian^G^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250404090000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250404090000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C71.1', cwe_2='Neoplasia maligna del lobulo frontal - control postquirurgico', cwe_3='I10')
        dg1.diagnosis_date_time = '20250404'
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
    """ Based on live/ar/ar-ge-centricity.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='HOSP_EL_CRUCE')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_EL_CRUCE')
        msh.date_time_of_message = '20250404150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HEC20250404150000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70056789', cx_4='GECENT', cx_5='MRN'), CX(cx_1='35890123', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'MANSILLA^Esteban^Roberto^^^Sr.'
        pid.date_time_of_birth = '19910822'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Calchaqui 5401', xad_3='Florencio Varela', xad_4='Buenos Aires', xad_5='B1888AAE', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^42109000'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltero', cwe_3='HL70002')
        pid.pid_19 = '35890123'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NCIR', pl_2='N501', pl_3='A', pl_4='HELCRUCE', pl_8='NCIR')
        pv1.attending_doctor = XCN(xcn_1='1102456789', xcn_2='Lucero', xcn_3='Damian', xcn_4='G', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='NCR', xcn_2='Neurocirugia', xcn_3='HECSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70056789', xcn_4='HECENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='IOMA', cwe_2='IOMA', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250401054500')

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
        orc.placer_order_number = EI(ei_1='ORD701005', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='GE501005', ei_2='GE_CENT')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250404090000^^R'
        orc.date_time_of_order_event = '20250404150000'
        orc.orc_10 = 'ESUAREZ^Suarez^Esteban^R^^Lic.'
        orc.enterers_location = PL(pl_1='20250404150000')
        orc.order_effective_date_time = 'HOSP_EL_CRUCE'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701005', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='GE501005', ei_2='GE_CENT')
        obr.universal_service_identifier = CWE(cwe_1='70553', cwe_2='RM Cerebro con y sin Contraste', cwe_3='CPT')
        obr.observation_date_time = '20250404091500'
        obr.obr_16 = '1102456789^Lucero^Damian^G^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250404145800'
        obr.diagnostic_serv_sect_id = 'MR'
        obr.result_status = 'F'
        obr.obr_27 = '^^^20250404090000^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='70553', cwe_2='RM Cerebro', cwe_3='CPT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'HALLAZGOS: Cambios postquirurgicos en lobulo frontal derecho con cavidad quirurgica de 32x25mm. Realce periferico fino sin nodularidad que s'
            'ugiere cambios postoperatorios esperados. Sin restriccion en difusion. Sin efecto de masa significativo. Linea media centrada. CONCLUSION: C'
            'ontrol postquirurgico de reseccion tumoral frontal derecha. Cambios esperables sin signos sugestivos de recidiva tumoral precoz.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='RM Cerebro Post-Op', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'GE_CENT^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM DQ4SEA8OEQ4LCxAWEBETFBUVFQwPFxgWFBgSFBT/2wBDAQMEBAUEBQkFBQk'
            'UDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCABAAEADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQo'
            'L/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIh'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='70553', cwe_2='RM Cerebro', cwe_3='CPT')
        obx_3.observation_sub_id = OG(og_1='2')
        obx_3.obx_5 = 'Z48.89^Cuidados posteriores a otra cirugia especificada^I10'
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
    """ Based on live/ar/ar-ge-centricity.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='HOSP_CLINICAS')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='HOSP_CLINICAS')
        msh.date_time_of_message = '20250410112000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HCL20250410112000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70067890', cx_4='GECENT', cx_5='MRN'), CX(cx_1='31234567', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'PEREYRA^Daniela^Solange^^^Sra.'
        pid.date_time_of_birth = '19830619'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Cordoba 2351', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1120AAR', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^59508000'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltera', cwe_3='HL70002')
        pid.pid_19 = '31234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='CT02', pl_3='A', pl_4='HCLINICAS', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1102567890', xcn_2='Mancini', xcn_3='Sergio', xcn_4='F', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='NEU', xcn_2='Neumologia', xcn_3='HCLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70067890', xcn_4='HCLENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250410112000')

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
        orc.placer_order_number = EI(ei_1='ORD701006', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='GE501006', ei_2='GE_CENT')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250410113000^^R'
        orc.date_time_of_order_event = '20250410112000'
        orc.orc_10 = 'AGARCIA^Garcia^Alejandra^V^^Lic.'
        orc.enterers_location = PL(pl_1='20250410112000')
        orc.order_effective_date_time = 'HOSP_CLINICAS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701006', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='GE501006', ei_2='GE_CENT')
        obr.universal_service_identifier = CWE(cwe_1='71275', cwe_2='Angio TC Torax (TEP)', cwe_3='CPT')
        obr.obr_16 = '1102567890^Mancini^Sergio^F^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250410113000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250410113000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I26.99', cwe_2='Embolia pulmonar sin cor pulmonale agudo', cwe_3='I10')
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
    """ Based on live/ar/ar-ge-centricity.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='HOSP_CLINICAS')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_CLINICAS')
        msh.date_time_of_message = '20250410133000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HCL20250410133000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70067890', cx_4='GECENT', cx_5='MRN'), CX(cx_1='31234567', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'PEREYRA^Daniela^Solange^^^Sra.'
        pid.date_time_of_birth = '19830619'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Cordoba 2351', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1120AAR', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^59508000'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltera', cwe_3='HL70002')
        pid.pid_19 = '31234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='CT02', pl_3='A', pl_4='HCLINICAS', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1102567890', xcn_2='Mancini', xcn_3='Sergio', xcn_4='F', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='NEU', xcn_2='Neumologia', xcn_3='HCLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70067890', xcn_4='HCLENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250410112000')

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
        orc.placer_order_number = EI(ei_1='ORD701006', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='GE501006', ei_2='GE_CENT')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250410113000^^R'
        orc.date_time_of_order_event = '20250410133000'
        orc.orc_10 = 'AGARCIA^Garcia^Alejandra^V^^Lic.'
        orc.enterers_location = PL(pl_1='20250410133000')
        orc.order_effective_date_time = 'HOSP_CLINICAS'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701006', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='GE501006', ei_2='GE_CENT')
        obr.universal_service_identifier = CWE(cwe_1='71275', cwe_2='Angio TC Torax (TEP)', cwe_3='CPT')
        obr.observation_date_time = '20250410113500'
        obr.obr_16 = '1102567890^Mancini^Sergio^F^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250410132800'
        obr.diagnostic_serv_sect_id = 'CT'
        obr.result_status = 'F'
        obr.obr_27 = '^^^20250410113000^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='71275', cwe_2='Angio TC TEP', cwe_3='CPT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'HALLAZGOS: Defecto de relleno intraluminal en arteria pulmonar lobar inferior derecha y segmentaria medial del lobulo medio compatible con t'
            'romboembolismo pulmonar agudo. Arteria pulmonar principal de calibre conservado. Relacion VD/VI <1. Sin derrame pleural. CONCLUSION: TEP agu'
            'do en territorio lobar inferior derecho y segmentario del lobulo medio. Sin signos de sobrecarga de cavidades derechas.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='71275', cwe_2='Angio TC TEP', cwe_3='CPT')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'I26.99^Embolia pulmonar sin cor pulmonale agudo^I10'
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
    """ Based on live/ar/ar-ge-centricity.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='FUND_FAVALORO')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='FUND_FAVALORO')
        msh.date_time_of_message = '20250415140000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'FFV20250415140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70078901', cx_4='GECENT', cx_5='MRN'), CX(cx_1='22345678', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'LUNA^Sergio^Ariel^^^Sr.'
        pid.date_time_of_birth = '19680403'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Belgrano 1746', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1093AAO', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^43781200'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '22345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='CT03', pl_3='A', pl_4='FFAVALORO', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1102678901', xcn_2='Paredes', xcn_3='Victoria', xcn_4='L', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiologia', xcn_3='FFVSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70078901', xcn_4='FFVENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='SWISS_MEDICAL', cwe_2='Swiss Medical', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250415140000')

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
        orc.placer_order_number = EI(ei_1='ORD701007', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='GE501007', ei_2='GE_CENT')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250415143000^^R'
        orc.date_time_of_order_event = '20250415140000'
        orc.orc_10 = 'MMORALES^Morales^Miguel^E^^Lic.'
        orc.enterers_location = PL(pl_1='20250415140000')
        orc.order_effective_date_time = 'FUND_FAVALORO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701007', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='GE501007', ei_2='GE_CENT')
        obr.universal_service_identifier = CWE(cwe_1='75574', cwe_2='Angio TC Coronarias con Calcio Score', cwe_3='CPT')
        obr.obr_16 = '1102678901^Paredes^Victoria^L^^Dra.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250415143000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250415143000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.10', cwe_2='Enfermedad cardiaca ateroesclerotica sin angina', cwe_3='I10')
        dg1.diagnosis_date_time = '20250415'
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
    """ Based on live/ar/ar-ge-centricity.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='FUND_FAVALORO')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='FUND_FAVALORO')
        msh.date_time_of_message = '20250416091500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'FFV20250416091500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70078901', cx_4='GECENT', cx_5='MRN'), CX(cx_1='22345678', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'LUNA^Sergio^Ariel^^^Sr.'
        pid.date_time_of_birth = '19680403'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Belgrano 1746', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1093AAO', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^43781200'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '22345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='CT03', pl_3='A', pl_4='FFAVALORO', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1102678901', xcn_2='Paredes', xcn_3='Victoria', xcn_4='L', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiologia', xcn_3='FFVSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70078901', xcn_4='FFVENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='SWISS_MEDICAL', cwe_2='Swiss Medical', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250415140000')

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
        orc.placer_order_number = EI(ei_1='ORD701007', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='GE501007', ei_2='GE_CENT')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250415143000^^R'
        orc.date_time_of_order_event = '20250416091500'
        orc.orc_10 = 'MMORALES^Morales^Miguel^E^^Lic.'
        orc.enterers_location = PL(pl_1='20250416091500')
        orc.order_effective_date_time = 'FUND_FAVALORO'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701007', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='GE501007', ei_2='GE_CENT')
        obr.universal_service_identifier = CWE(cwe_1='75574', cwe_2='Angio TC Coronarias con Calcio Score', cwe_3='CPT')
        obr.observation_date_time = '20250415144000'
        obr.obr_16 = '1102678901^Paredes^Victoria^L^^Dra.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250416091300'
        obr.diagnostic_serv_sect_id = 'CT'
        obr.result_status = 'F'
        obr.obr_27 = '^^^20250415143000^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='75574', cwe_2='Angio TC Coronaria', cwe_3='CPT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'HALLAZGOS: Calcium Score Agatston: 185 (percentil alto para edad y sexo). TCI sin lesiones. DA con placa mixta en tercio proximal que genera'
            ' estenosis moderada (50-69%). Cx sin lesiones significativas. CD con placa calcificada no significativa en tercio medio. CONCLUSION: Enferme'
            'dad coronaria aterosclerotica moderada en DA proximal. Score de calcio elevado. Se sugiere evaluacion funcional.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='75574', cwe_2='Calcium Score Agatston', cwe_3='CPT')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '185'
        obx_2.units = CWE(cwe_1='AU')
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
    """ Based on live/ar/ar-ge-centricity.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='HOSP_BRITANICO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HOSP_BRITANICO')
        msh.date_time_of_message = '20250420090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'HBR20250420090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250420090000'
        evn.operator_id = XCN(xcn_1='JORTEGA', xcn_2='Ortega', xcn_3='Julia', xcn_4='A', xcn_6='Lic.')
        evn.event_occurred = '20250420085000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70089012', cx_4='GECENT', cx_5='MRN'), CX(cx_1='19456789', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'BRANDONI^Oscar^Mario^^^Sr.'
        pid.date_time_of_birth = '19610530'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Solis 2081', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1134ACL', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^43091600'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '19456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='CT01', pl_3='A', pl_4='HBRITANICO', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1102789012', xcn_2='Guzman', xcn_3='Patricia', xcn_4='R', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='URO', xcn_2='Urologia', xcn_3='HBRSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70089012', xcn_4='HBRENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 310', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250420090000')

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
    """ Based on live/ar/ar-ge-centricity.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='HOSP_BRITANICO')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='HOSP_BRITANICO')
        msh.date_time_of_message = '20250420093000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HBR20250420093000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70089012', cx_4='GECENT', cx_5='MRN'), CX(cx_1='19456789', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'BRANDONI^Oscar^Mario^^^Sr.'
        pid.date_time_of_birth = '19610530'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Solis 2081', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1134ACL', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^43091600'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '19456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='CT01', pl_3='A', pl_4='HBRITANICO', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1102789012', xcn_2='Guzman', xcn_3='Patricia', xcn_4='R', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='URO', xcn_2='Urologia', xcn_3='HBRSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70089012', xcn_4='HBRENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 310', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250420090000')

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
        orc.placer_order_number = EI(ei_1='ORD701008', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='GE501008', ei_2='GE_CENT')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250420100000^^R'
        orc.date_time_of_order_event = '20250420093000'
        orc.orc_10 = 'JORTEGA^Ortega^Julia^A^^Lic.'
        orc.enterers_location = PL(pl_1='20250420093000')
        orc.order_effective_date_time = 'HOSP_BRITANICO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701008', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='GE501008', ei_2='GE_CENT')
        obr.universal_service_identifier = CWE(cwe_1='74178', cwe_2='Uro TC con Contraste Trifasica', cwe_3='CPT')
        obr.obr_16 = '1102789012^Guzman^Patricia^R^^Dra.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250420100000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_28 = '^^^20250420100000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='N20.0', cwe_2='Calculo del riñon', cwe_3='I10')
        dg1.diagnosis_date_time = '20250420'
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
    """ Based on live/ar/ar-ge-centricity.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='HOSP_BRITANICO')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_BRITANICO')
        msh.date_time_of_message = '20250420150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HBR20250420150000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70089012', cx_4='GECENT', cx_5='MRN'), CX(cx_1='19456789', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'BRANDONI^Oscar^Mario^^^Sr.'
        pid.date_time_of_birth = '19610530'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Solis 2081', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1134ACL', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^43091600'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '19456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIMG', pl_2='CT01', pl_3='A', pl_4='HBRITANICO', pl_8='RADIMG')
        pv1.attending_doctor = XCN(xcn_1='1102789012', xcn_2='Guzman', xcn_3='Patricia', xcn_4='R', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='URO', xcn_2='Urologia', xcn_3='HBRSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70089012', xcn_4='HBRENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 310', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250420090000')

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
        orc.placer_order_number = EI(ei_1='ORD701008', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='GE501008', ei_2='GE_CENT')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250420100000^^R'
        orc.date_time_of_order_event = '20250420150000'
        orc.orc_10 = 'JORTEGA^Ortega^Julia^A^^Lic.'
        orc.enterers_location = PL(pl_1='20250420150000')
        orc.order_effective_date_time = 'HOSP_BRITANICO'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701008', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='GE501008', ei_2='GE_CENT')
        obr.universal_service_identifier = CWE(cwe_1='74178', cwe_2='Uro TC con Contraste Trifasica', cwe_3='CPT')
        obr.observation_date_time = '20250420101000'
        obr.obr_16 = '1102789012^Guzman^Patricia^R^^Dra.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250420145800'
        obr.diagnostic_serv_sect_id = 'CT'
        obr.result_status = 'F'
        obr.obr_27 = '^^^20250420100000^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='74178', cwe_2='Uro TC', cwe_3='CPT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'HALLAZGOS: Riñon derecho con imagen calicica de 8mm en grupo calicial inferior compatible con litiasis. Leve dilatacion pielo-calicial derec'
            'ha (grado II). Riñon izquierdo sin alteraciones. Ureteres permeables sin defectos de relleno. Vejiga normodistendida sin alteraciones pariet'
            'ales. CONCLUSION: Litiasis calicial inferior derecha de 8mm con hidronefrosis leve asociada.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Informe Uro TC Completo', cwe_3='AUSPDI')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'GE_CENT^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA1IDAgUgo+'
            'PgplbmRvYmoKNCAwIG9iago8PAovTGVuZ3RoIDQ4Cj4+CnN0cmVhbQpCVAovRjEgMTggVGYKMTAwIDcwMCBUZAooVXJvIFRDIC0gSW5mb3JtZSBDb21wbGV0bykgVGoKRVQKZW5kc3Ry'
            'ZWFtCg=='
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='74178', cwe_2='Uro TC', cwe_3='CPT')
        obx_3.observation_sub_id = OG(og_1='2')
        obx_3.obx_5 = 'N20.0^Calculo del riñon^I10'
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
    """ Based on live/ar/ar-ge-centricity.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GE_CENT')
        msh.sending_facility = HD(hd_1='HOSP_EL_CRUCE')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HOSP_EL_CRUCE')
        msh.date_time_of_message = '20250408151500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'HEC20250408151500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250408151500'
        evn.operator_id = XCN(xcn_1='ESUAREZ', xcn_2='Suarez', xcn_3='Esteban', xcn_4='R', xcn_6='Lic.')
        evn.event_occurred = '20250408150000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='GE70056789', cx_4='GECENT', cx_5='MRN'), CX(cx_1='35890123', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'MANSILLA^Esteban^Roberto^^^Sr.'
        pid.date_time_of_birth = '19910822'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Calchaqui 5401', xad_3='Florencio Varela', xad_4='Buenos Aires', xad_5='B1888AAE', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^42109000'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltero', cwe_3='HL70002')
        pid.pid_19 = '35890123'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NCIR', pl_2='N501', pl_3='A', pl_4='HELCRUCE', pl_8='NCIR')
        pv1.attending_doctor = XCN(xcn_1='1102456789', xcn_2='Lucero', xcn_3='Damian', xcn_4='G', xcn_6='Dr.', xcn_9='MN')
        pv1.referring_doctor = XCN(xcn_1='1102456790', xcn_2='Ojeda', xcn_3='Marina', xcn_4='F', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='NCR', xcn_2='Neurocirugia', xcn_3='HECSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70056789', xcn_4='HECENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='IOMA', cwe_2='IOMA', cwe_3='HL70072')
        pv1.pv1_20 = 'DI^Alta a Domicilio^HL70112'
        pv1.admit_date_time = '20250401054500'
        pv1.discharge_date_time = '20250408151500'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C71.1', cwe_2='Neoplasia maligna del lobulo frontal', cwe_3='I10')
        dg1.diagnosis_date_time = '20250401'
        dg1.diagnosis_type = CWE(cwe_1='A', cwe_2='Admitting', cwe_3='HL70052')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='Z48.89', cwe_2='Cuidados posteriores a otra cirugia especificada', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20250408'
        dg1_2.diagnosis_type = CWE(cwe_1='F', cwe_2='Final', cwe_3='HL70052')

        # .. build PR1 ..
        pr1 = PR1()
        pr1.set_id_pr1 = '1'
        pr1.procedure_code = CNE(cne_1='01N00ZZ', cne_2='Reseccion de Cerebro, Abordaje Abierto', cne_3='ICD10PCS')
        pr1.pr1_4 = 'Reseccion tumoral frontal derecha'
        pr1.procedure_date_time = '20250402080000'
        pr1.procedure_functional_type = CWE(cwe_1='A', cwe_2='Anesthesia', cwe_3='HL70230')
        pr1.pr1_12 = '1102456789^Lucero^Damian^G^^Dr.^^^MN'

        # .. build the PROCEDURE group ..
        procedure = AdtA03Procedure()
        procedure.pr1 = pr1

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = [dg1, dg1_2]
        msg.procedure = procedure

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
