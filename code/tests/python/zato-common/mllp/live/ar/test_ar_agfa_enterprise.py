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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, EIP, HD, MSG, OG, PL, PT, VID, XAD, XCN, XPN
from zato.hl7v2.v2_9.groups import OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import DG1, MSH, OBR, OBX, ORC, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ar', 'ar-agfa-enterprise.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_HIGA')
        msh.sending_facility = HD(hd_1='HIGA_SAN_MARTIN')
        msh.receiving_application = HD(hd_1='AGFA_EI')
        msh.receiving_facility = HD(hd_1='HIGA_SAN_MARTIN_RAD')
        msh.date_time_of_message = '20250312091500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='31245678', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='AGUIRRE', xpn_2='MARIANA SOLEDAD')
        pid.date_time_of_birth = '19780315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE 47 NRO 825', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4239012'
        pid.patient_account_number = CX(cx_1='31245678')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='32145698', xcn_2='FERREYRA', xcn_3='GUSTAVO', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='V00012345')
        pv1.prior_temporary_location = PL(pl_1='20250312')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-00891')
        orc.orc_7 = '1^^^20250312091500^^R'
        orc.date_time_of_order_event = '20250312091500'
        orc.orc_10 = '32145698^FERREYRA^GUSTAVO^^^DR'
        orc.orc_12 = '32145698^FERREYRA^GUSTAVO^^^DR'
        orc.enterers_location = PL(pl_1='RAD')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-00891')
        obr.universal_service_identifier = CWE(cwe_1='74177', cwe_2='CT ABDOMEN AND PELVIS WITH CONTRAST', cwe_3='CPT')
        obr.observation_date_time = '20250312091500'
        obr.obr_15 = '32145698^FERREYRA^GUSTAVO^^^DR'
        obr.result_status = '1^^^20250312091500^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R10.9', cwe_2='DOLOR ABDOMINAL NO ESPECIFICADO', cwe_3='ICD10AR')
        dg1.diagnosis_type = CWE(cwe_1='A')

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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_CEMIC')
        msh.sending_facility = HD(hd_1='CEMIC_SEDE_NORTE')
        msh.receiving_application = HD(hd_1='AGFA_EI')
        msh.receiving_facility = HD(hd_1='CEMIC_MAMOGRAFIA')
        msh.date_time_of_message = '20250315083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='30876234', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='BENITEZ', xpn_2='GRACIELA NOEMI')
        pid.date_time_of_birth = '19650822'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV SANTA FE 2890', xad_3='BUENOS AIRES', xad_4='CABA', xad_5='1425', xad_6='AR')
        pid.pid_13 = '011-4824-5610'
        pid.patient_account_number = CX(cx_1='30876234')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MAM', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='31987456', xcn_2='IBARRA', xcn_3='VALERIA', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='MAM')
        pv1.patient_type = CWE(cwe_1='V00012678')
        pv1.prior_temporary_location = PL(pl_1='20250315')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-01023')
        orc.orc_7 = '1^^^20250315083000^^R'
        orc.date_time_of_order_event = '20250315083000'
        orc.orc_10 = '31987456^IBARRA^VALERIA^^^DRA'
        orc.orc_12 = '31987456^IBARRA^VALERIA^^^DRA'
        orc.enterers_location = PL(pl_1='MAM')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-01023')
        obr.universal_service_identifier = CWE(cwe_1='77067', cwe_2='SCREENING MAMMOGRAPHY BILATERAL', cwe_3='CPT')
        obr.observation_date_time = '20250315083000'
        obr.obr_15 = '31987456^IBARRA^VALERIA^^^DRA'
        obr.result_status = '1^^^20250315083000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='Z12.31', cwe_2='EXAMEN DE DETECCION DE NEOPLASIA MALIGNA DE MAMA', cwe_3='ICD10AR')
        dg1.diagnosis_type = CWE(cwe_1='A')

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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AGFA_EI')
        msh.sending_facility = HD(hd_1='FUND_FAVALORO_RAD')
        msh.receiving_application = HD(hd_1='HIS_FAVALORO')
        msh.receiving_facility = HD(hd_1='FUND_FAVALORO')
        msh.date_time_of_message = '20250318141200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='27890432', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='SOSA', xpn_2='EMILIANO RAFAEL')
        pid.date_time_of_birth = '19820614'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CALLE BOLIVAR 478', xad_3='CORDOBA', xad_4='CORDOBA', xad_5='5000', xad_6='AR')
        pid.pid_13 = '0351-4231785'
        pid.patient_account_number = CX(cx_1='27890432')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEU', pl_2='205', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='29345617', xcn_2='MOLINA', xcn_3='HORACIO', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='NEU')
        pv1.patient_type = CWE(cwe_1='V00013001')
        pv1.prior_temporary_location = PL(pl_1='20250318')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-01100')
        orc.placer_order_group_number = EI(ei_1='FIL-2025-01100')
        orc.parent_order = EIP(eip_1='20250318141200')
        orc.date_time_of_order_event = '29345617^MOLINA^HORACIO^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-01100')
        obr.filler_order_number = EI(ei_1='FIL-2025-01100')
        obr.universal_service_identifier = CWE(cwe_1='70553', cwe_2='MRI BRAIN WITHOUT CONTRAST', cwe_3='CPT')
        obr.observation_date_time = '20250318100000'
        obr.obr_14 = '29345617^MOLINA^HORACIO^^^DR'
        obr.obr_16 = 'AC12345'
        obr.placer_field_1 = 'CR'
        obr.diagnostic_serv_sect_id = 'F'
        obr.reason_for_study = CWE(cwe_1='29345617', cwe_2='MOLINA', cwe_3='HORACIO', cwe_6='DR')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18747-6', cwe_2='CT HEAD IMPRESSION', cwe_3='LN')
        obx.obx_5 = 'Sin evidencia de lesion ocupante de espacio. Estructuras de linea media centradas. Sistema ventricular de tamano normal.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='18747-6', cwe_2='CT HEAD IMPRESSION', cwe_3='LN')
        obx_2.obx_5 = 'No se observan colecciones extra ni intracerebrales. Surcos y cisuras de amplitud conservada.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='18747-6', cwe_2='CT HEAD IMPRESSION', cwe_3='LN')
        obx_3.obx_5 = 'CONCLUSION: Estudio tomografico de cerebro dentro de limites normales.'
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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AGFA_EI')
        msh.sending_facility = HD(hd_1='CEMIC_MAMOGRAFIA')
        msh.receiving_application = HD(hd_1='HIS_CEMIC')
        msh.receiving_facility = HD(hd_1='CEMIC_SEDE_NORTE')
        msh.date_time_of_message = '20250320102300'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='30876234', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='BENITEZ', xpn_2='GRACIELA NOEMI')
        pid.date_time_of_birth = '19650822'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV SANTA FE 2890', xad_3='BUENOS AIRES', xad_4='CABA', xad_5='1425', xad_6='AR')
        pid.pid_13 = '011-4824-5610'
        pid.patient_account_number = CX(cx_1='30876234')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MAM', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='31987456', xcn_2='IBARRA', xcn_3='VALERIA', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='MAM')
        pv1.patient_type = CWE(cwe_1='V00012678')
        pv1.prior_temporary_location = PL(pl_1='20250320')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-01023')
        orc.placer_order_group_number = EI(ei_1='FIL-2025-01023')
        orc.parent_order = EIP(eip_1='20250320102300')
        orc.date_time_of_order_event = '31987456^IBARRA^VALERIA^^^DRA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-01023')
        obr.filler_order_number = EI(ei_1='FIL-2025-01023')
        obr.universal_service_identifier = CWE(cwe_1='77067', cwe_2='SCREENING MAMMOGRAPHY BILATERAL', cwe_3='CPT')
        obr.observation_date_time = '20250315083000'
        obr.obr_14 = '31987456^IBARRA^VALERIA^^^DRA'
        obr.obr_16 = 'AC67890'
        obr.placer_field_1 = 'MG'
        obr.diagnostic_serv_sect_id = 'F'
        obr.reason_for_study = CWE(cwe_1='31987456', cwe_2='IBARRA', cwe_3='VALERIA', cwe_6='DRA')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='24606-6', cwe_2='MG BREAST SCREENING', cwe_3='LN')
        obx.obx_5 = 'Mamas de densidad heterogenea (ACR C). Se observan calcificaciones benignas bilaterales dispersas de tipo vascular.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='24606-6', cwe_2='MG BREAST SCREENING', cwe_3='LN')
        obx_2.obx_5 = 'No se identifican masas, distorsiones arquitecturales ni asimetrias sospechosas. Ganglios axilares sin particularidades.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='24606-6', cwe_2='MG BREAST SCREENING', cwe_3='LN')
        obx_3.obx_5 = 'BIRADS 2 - HALLAZGOS BENIGNOS. Control en 12 meses.'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ED'
        obx_4.observation_identifier = CWE(cwe_1='PDF', cwe_2='Informe Mamografia Completo', cwe_3='AUSPDI')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = (
            'AGFA_EI^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzky'
        )
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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_ITALIANO')
        msh.sending_facility = HD(hd_1='HOSP_ITALIANO_BA')
        msh.receiving_application = HD(hd_1='AGFA_EI')
        msh.receiving_facility = HD(hd_1='HOSP_ITALIANO_RAD')
        msh.date_time_of_message = '20250322080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='33564789', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='DIAZ', xpn_2='MAXIMILIANO IGNACIO')
        pid.date_time_of_birth = '19900503'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV CABILDO 3120', xad_3='BUENOS AIRES', xad_4='CABA', xad_5='1429', xad_6='AR')
        pid.pid_13 = '011-4783-2940'
        pid.patient_account_number = CX(cx_1='33564789')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='003', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='30876123', xcn_2='PEREYRA', xcn_3='CECILIA', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='ORT')
        pv1.patient_type = CWE(cwe_1='V00014102')
        pv1.prior_temporary_location = PL(pl_1='20250322')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-01250')
        orc.orc_7 = '1^^^20250322080000^^R'
        orc.date_time_of_order_event = '20250322080000'
        orc.orc_10 = '30876123^PEREYRA^CECILIA^^^DRA'
        orc.orc_12 = '30876123^PEREYRA^CECILIA^^^DRA'
        orc.enterers_location = PL(pl_1='RAD')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-01250')
        obr.universal_service_identifier = CWE(cwe_1='72148', cwe_2='MRI LUMBAR SPINE WITHOUT CONTRAST', cwe_3='CPT')
        obr.observation_date_time = '20250322080000'
        obr.obr_15 = '30876123^PEREYRA^CECILIA^^^DRA'
        obr.result_status = '1^^^20250322080000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M54.5', cwe_2='LUMBAGO NO ESPECIFICADO', cwe_3='ICD10AR')
        dg1.diagnosis_type = CWE(cwe_1='A')

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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AGFA_EI')
        msh.sending_facility = HD(hd_1='HOSP_BRITISH_RAD')
        msh.receiving_application = HD(hd_1='HIS_BRITISH')
        msh.receiving_facility = HD(hd_1='HOSP_BRITISH')
        msh.date_time_of_message = '20250325093000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='21345876', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='VILLALBA', xpn_2='DELIA ESTHER')
        pid.date_time_of_birth = '19550218'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV BELGRANO 1450', xad_3='MENDOZA', xad_4='MENDOZA', xad_5='5500', xad_6='AR')
        pid.pid_13 = '0261-4234560'
        pid.patient_account_number = CX(cx_1='21345876')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CAR', pl_2='312', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='28765432', xcn_2='CABRERA', xcn_3='EDUARDO', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.patient_type = CWE(cwe_1='V00014500')
        pv1.prior_temporary_location = PL(pl_1='20250325')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-01345')
        orc.placer_order_group_number = EI(ei_1='FIL-2025-01345')
        orc.parent_order = EIP(eip_1='20250325093000')
        orc.date_time_of_order_event = '28765432^CABRERA^EDUARDO^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-01345')
        obr.filler_order_number = EI(ei_1='FIL-2025-01345')
        obr.universal_service_identifier = CWE(cwe_1='71046', cwe_2='CHEST X-RAY 2 VIEWS', cwe_3='CPT')
        obr.observation_date_time = '20250325080000'
        obr.obr_14 = '28765432^CABRERA^EDUARDO^^^DR'
        obr.obr_16 = 'AC24680'
        obr.placer_field_1 = 'CR'
        obr.diagnostic_serv_sect_id = 'F'
        obr.reason_for_study = CWE(cwe_1='28765432', cwe_2='CABRERA', cwe_3='EDUARDO', cwe_6='DR')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='CHEST XRAY IMPRESSION', cwe_3='LN')
        obx.obx_5 = 'Silueta cardiaca aumentada de tamano con indice cardio-toracico de 0.58. Elongacion aortica.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='18748-4', cwe_2='CHEST XRAY IMPRESSION', cwe_3='LN')
        obx_2.obx_5 = 'Hilios pulmonares de morfologia vascular. Redistribucion de flujo hacia vertices. Senos costofrenicos libres.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='18748-4', cwe_2='CHEST XRAY IMPRESSION', cwe_3='LN')
        obx_3.obx_5 = 'CONCLUSION: Cardiomegalia grado I. Signos de hipertension venocapilar pulmonar incipiente.'
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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_AUSTRAL')
        msh.sending_facility = HD(hd_1='HOSP_AUSTRAL')
        msh.receiving_application = HD(hd_1='AGFA_EI')
        msh.receiving_facility = HD(hd_1='HOSP_AUSTRAL_RAD')
        msh.date_time_of_message = '20250401070000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='26743219', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='LEDESMA', xpn_2='ROXANA BEATRIZ')
        pid.date_time_of_birth = '19731109'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV INDEPENDENCIA 2350', xad_3='ROSARIO', xad_4='SANTA FE', xad_5='2000', xad_6='AR')
        pid.pid_13 = '0341-4567823'
        pid.patient_account_number = CX(cx_1='26743219')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ECO', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='33129876', xcn_2='OVIEDO', xcn_3='MAURICIO', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='GAS')
        pv1.patient_type = CWE(cwe_1='V00015001')
        pv1.prior_temporary_location = PL(pl_1='20250401')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-01500')
        orc.orc_7 = '1^^^20250401070000^^R'
        orc.date_time_of_order_event = '20250401070000'
        orc.orc_10 = '33129876^OVIEDO^MAURICIO^^^DR'
        orc.orc_12 = '33129876^OVIEDO^MAURICIO^^^DR'
        orc.enterers_location = PL(pl_1='ECO')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-01500')
        obr.universal_service_identifier = CWE(cwe_1='76700', cwe_2='US ABDOMEN COMPLETE', cwe_3='CPT')
        obr.observation_date_time = '20250401070000'
        obr.obr_15 = '33129876^OVIEDO^MAURICIO^^^DR'
        obr.result_status = '1^^^20250401070000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K76.0', cwe_2='HIGADO GRASO NO CLASIFICADO EN OTRA PARTE', cwe_3='ICD10AR')
        dg1.diagnosis_type = CWE(cwe_1='A')

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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AGFA_EI')
        msh.sending_facility = HD(hd_1='DIAG_MAIPU_RAD')
        msh.receiving_application = HD(hd_1='HIS_MAIPU')
        msh.receiving_facility = HD(hd_1='DIAG_MAIPU')
        msh.date_time_of_message = '20250403153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='35012987', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='SUAREZ', xpn_2='TOMAS BENJAMIN')
        pid.date_time_of_birth = '19950728'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV ALEM 1042', xad_3='MAR DEL PLATA', xad_4='BUENOS AIRES', xad_5='7600', xad_6='AR')
        pid.pid_13 = '0223-4910283'
        pid.patient_account_number = CX(cx_1='35012987')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='002', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='32987432', xcn_2='ESCOBAR', xcn_3='FLORENCIA', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='ORT')
        pv1.patient_type = CWE(cwe_1='V00015200')
        pv1.prior_temporary_location = PL(pl_1='20250403')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-01600')
        orc.placer_order_group_number = EI(ei_1='FIL-2025-01600')
        orc.parent_order = EIP(eip_1='20250403153000')
        orc.date_time_of_order_event = '32987432^ESCOBAR^FLORENCIA^^^DRA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-01600')
        obr.filler_order_number = EI(ei_1='FIL-2025-01600')
        obr.universal_service_identifier = CWE(cwe_1='73721', cwe_2='MRI KNEE WITHOUT CONTRAST', cwe_3='CPT')
        obr.observation_date_time = '20250403100000'
        obr.obr_14 = '32987432^ESCOBAR^FLORENCIA^^^DRA'
        obr.obr_16 = 'AC34567'
        obr.placer_field_1 = 'MR'
        obr.diagnostic_serv_sect_id = 'F'
        obr.reason_for_study = CWE(cwe_1='32987432', cwe_2='ESCOBAR', cwe_3='FLORENCIA', cwe_6='DRA')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='24566-2', cwe_2='MRI KNEE', cwe_3='LN')
        obx.obx_5 = 'Rotura del cuerno posterior del menisco interno con patron de tipo complejo. Derrame articular moderado.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='24566-2', cwe_2='MRI KNEE', cwe_3='LN')
        obx_2.obx_5 = 'Ligamentos cruzados anterior y posterior de intensidad de senal y grosor normales. Ligamentos colaterales indemnes.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='24566-2', cwe_2='MRI KNEE', cwe_3='LN')
        obx_3.obx_5 = 'CONCLUSION: Lesion meniscal interna compleja grado III. Derrame articular. Se sugiere valoracion artroscopica.'
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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_FLENI')
        msh.sending_facility = HD(hd_1='FUND_FLENI')
        msh.receiving_application = HD(hd_1='AGFA_EI')
        msh.receiving_facility = HD(hd_1='FUND_FLENI_RAD')
        msh.date_time_of_message = '20250405110000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='10876543', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='ALMIRON', xpn_2='OSVALDO ANIBAL')
        pid.date_time_of_birth = '19480930'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CALLE GENERAL PAZ 845', xad_3='SALTA', xad_4='SALTA', xad_5='4400', xad_6='AR')
        pid.pid_13 = '0387-4218976'
        pid.patient_account_number = CX(cx_1='10876543')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEU', pl_2='410', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='27345601', xcn_2='FRIAS', xcn_3='GERMAN', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='NEU')
        pv1.patient_type = CWE(cwe_1='V00015890')
        pv1.prior_temporary_location = PL(pl_1='20250405')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-01750')
        orc.orc_7 = '1^^^20250405110000^^R'
        orc.date_time_of_order_event = '20250405110000'
        orc.orc_10 = '27345601^FRIAS^GERMAN^^^DR'
        orc.orc_12 = '27345601^FRIAS^GERMAN^^^DR'
        orc.enterers_location = PL(pl_1='ECO')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-01750')
        obr.universal_service_identifier = CWE(cwe_1='93880', cwe_2='DUPLEX SCAN EXTRACRANIAL ARTERIES', cwe_3='CPT')
        obr.observation_date_time = '20250405110000'
        obr.obr_15 = '27345601^FRIAS^GERMAN^^^DR'
        obr.result_status = '1^^^20250405110000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I63.9', cwe_2='INFARTO CEREBRAL NO ESPECIFICADO', cwe_3='ICD10AR')
        dg1.diagnosis_type = CWE(cwe_1='A')

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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AGFA_EI')
        msh.sending_facility = HD(hd_1='HIGA_SAN_MARTIN_RAD')
        msh.receiving_application = HD(hd_1='HIS_HIGA')
        msh.receiving_facility = HD(hd_1='HIGA_SAN_MARTIN')
        msh.date_time_of_message = '20250408164500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='29876543', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='CACERES', xpn_2='ROCIO MAGDALENA')
        pid.date_time_of_birth = '19870412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV SAN JUAN 1620', xad_3='NEUQUEN', xad_4='NEUQUEN', xad_5='8300', xad_6='AR')
        pid.pid_13 = '0299-4423891'
        pid.patient_account_number = CX(cx_1='29876543')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='GUA', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='30543219', xcn_2='QUIROGA', xcn_3='FEDERICO', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='NEU')
        pv1.patient_type = CWE(cwe_1='V00016100')
        pv1.prior_temporary_location = PL(pl_1='20250408')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-01890')
        orc.placer_order_group_number = EI(ei_1='FIL-2025-01890')
        orc.parent_order = EIP(eip_1='20250408164500')
        orc.date_time_of_order_event = '30543219^QUIROGA^FEDERICO^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-01890')
        obr.filler_order_number = EI(ei_1='FIL-2025-01890')
        obr.universal_service_identifier = CWE(cwe_1='71275', cwe_2='CT CHEST ANGIOGRAPHY', cwe_3='CPT')
        obr.observation_date_time = '20250408150000'
        obr.obr_14 = '30543219^QUIROGA^FEDERICO^^^DR'
        obr.obr_16 = 'AC45678'
        obr.placer_field_1 = 'CT'
        obr.diagnostic_serv_sect_id = 'F'
        obr.reason_for_study = CWE(cwe_1='30543219', cwe_2='QUIROGA', cwe_3='FEDERICO', cwe_6='DR')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='CT ANGIO CHEST IMPRESSION', cwe_3='LN')
        obx.obx_5 = 'No se observan defectos de llenado en arterias pulmonares principales, lobares ni segmentarias que sugieran TEP.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='18748-4', cwe_2='CT ANGIO CHEST IMPRESSION', cwe_3='LN')
        obx_2.obx_5 = 'Parenquima pulmonar sin consolidaciones ni opacidades en vidrio esmerilado. Mediastino sin adenomegalias.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='18748-4', cwe_2='CT ANGIO CHEST IMPRESSION', cwe_3='LN')
        obx_3.obx_5 = 'CONCLUSION: Angio-TC de torax sin evidencia de tromboembolismo pulmonar. Estudio dentro de limites normales.'
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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_GERMAN')
        msh.sending_facility = HD(hd_1='HOSP_ALEMAN')
        msh.receiving_application = HD(hd_1='AGFA_EI')
        msh.receiving_facility = HD(hd_1='HOSP_ALEMAN_RAD')
        msh.date_time_of_message = '20250410080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='14678923', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='SCHMIDT', xpn_2='HILDA MARTA')
        pid.date_time_of_birth = '19560712'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV LAS HERAS 2845', xad_3='BUENOS AIRES', xad_4='CABA', xad_5='1425', xad_6='AR')
        pid.pid_13 = '011-4801-3950'
        pid.patient_account_number = CX(cx_1='14678923')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DXA', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='25901876', xcn_2='FISCHER', xcn_3='MATIAS', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='END')
        pv1.patient_type = CWE(cwe_1='V00016500')
        pv1.prior_temporary_location = PL(pl_1='20250410')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-02000')
        orc.orc_7 = '1^^^20250410080000^^R'
        orc.date_time_of_order_event = '20250410080000'
        orc.orc_10 = '25901876^FISCHER^MATIAS^^^DR'
        orc.orc_12 = '25901876^FISCHER^MATIAS^^^DR'
        orc.enterers_location = PL(pl_1='DXA')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-02000')
        obr.universal_service_identifier = CWE(cwe_1='77080', cwe_2='DXA BONE DENSITY AXIAL', cwe_3='CPT')
        obr.observation_date_time = '20250410080000'
        obr.obr_15 = '25901876^FISCHER^MATIAS^^^DR'
        obr.result_status = '1^^^20250410080000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M81.0', cwe_2='OSTEOPOROSIS POSTMENOPAUSICA', cwe_3='ICD10AR')
        dg1.diagnosis_type = CWE(cwe_1='A')

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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AGFA_EI')
        msh.sending_facility = HD(hd_1='HOSP_AUSTRAL_RAD')
        msh.receiving_application = HD(hd_1='HIS_AUSTRAL')
        msh.receiving_facility = HD(hd_1='HOSP_AUSTRAL')
        msh.date_time_of_message = '20250412112000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='26743219', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='LEDESMA', xpn_2='ROXANA BEATRIZ')
        pid.date_time_of_birth = '19731109'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV INDEPENDENCIA 2350', xad_3='ROSARIO', xad_4='SANTA FE', xad_5='2000', xad_6='AR')
        pid.pid_13 = '0341-4567823'
        pid.patient_account_number = CX(cx_1='26743219')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ECO', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='33129876', xcn_2='OVIEDO', xcn_3='MAURICIO', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='GAS')
        pv1.patient_type = CWE(cwe_1='V00015001')
        pv1.prior_temporary_location = PL(pl_1='20250412')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-01500')
        orc.placer_order_group_number = EI(ei_1='FIL-2025-01500')
        orc.parent_order = EIP(eip_1='20250412112000')
        orc.date_time_of_order_event = '33129876^OVIEDO^MAURICIO^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-01500')
        obr.filler_order_number = EI(ei_1='FIL-2025-01500')
        obr.universal_service_identifier = CWE(cwe_1='76700', cwe_2='US ABDOMEN COMPLETE', cwe_3='CPT')
        obr.observation_date_time = '20250401070000'
        obr.obr_14 = '33129876^OVIEDO^MAURICIO^^^DR'
        obr.obr_16 = 'AC56789'
        obr.placer_field_1 = 'US'
        obr.diagnostic_serv_sect_id = 'F'
        obr.reason_for_study = CWE(cwe_1='33129876', cwe_2='OVIEDO', cwe_3='MAURICIO', cwe_6='DR')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18752-6', cwe_2='US ABDOMEN IMPRESSION', cwe_3='LN')
        obx.obx_5 = 'Higado de tamano aumentado con ecogenicidad difusamente incrementada compatible con esteatosis hepatica grado II.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='18752-6', cwe_2='US ABDOMEN IMPRESSION', cwe_3='LN')
        obx_2.obx_5 = 'Vesicula biliar normodistendida sin litiasis. Vias biliares no dilatadas. Pancreas visualizado sin alteraciones.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='18752-6', cwe_2='US ABDOMEN IMPRESSION', cwe_3='LN')
        obx_3.obx_5 = 'CONCLUSION: Hepatomegalia con esteatosis hepatica moderada. Resto del estudio ecografico abdominal sin hallazgos patologicos.'
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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_ROFFO')
        msh.sending_facility = HD(hd_1='INST_ROFFO')
        msh.receiving_application = HD(hd_1='AGFA_EI')
        msh.receiving_facility = HD(hd_1='INST_ROFFO_RAD')
        msh.date_time_of_message = '20250415090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='34567812', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='ACEVEDO', xpn_2='IVAN LEONARDO')
        pid.date_time_of_birth = '19920118'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV 9 DE JULIO 1230', xad_3='SAN MIGUEL DE TUCUMAN', xad_4='TUCUMAN', xad_5='4000', xad_6='AR')
        pid.pid_13 = '0381-4216540'
        pid.patient_account_number = CX(cx_1='34567812')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ONC', pl_2='201', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='28123456', xcn_2='GUTIERREZ', xcn_3='SOLEDAD', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='ONC')
        pv1.patient_type = CWE(cwe_1='V00017000')
        pv1.prior_temporary_location = PL(pl_1='20250415')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-02150')
        orc.orc_7 = '1^^^20250415090000^^R'
        orc.date_time_of_order_event = '20250415090000'
        orc.orc_10 = '28123456^GUTIERREZ^SOLEDAD^^^DRA'
        orc.orc_12 = '28123456^GUTIERREZ^SOLEDAD^^^DRA'
        orc.enterers_location = PL(pl_1='MN')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-02150')
        obr.universal_service_identifier = CWE(cwe_1='78816', cwe_2='PET IMAGING WHOLE BODY', cwe_3='CPT')
        obr.observation_date_time = '20250415090000'
        obr.obr_15 = '28123456^GUTIERREZ^SOLEDAD^^^DRA'
        obr.result_status = '1^^^20250415090000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C83.3', cwe_2='LINFOMA DIFUSO DE CELULAS B GRANDES', cwe_3='ICD10AR')
        dg1.diagnosis_type = CWE(cwe_1='A')

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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AGFA_EI')
        msh.sending_facility = HD(hd_1='FUND_FLENI_RAD')
        msh.receiving_application = HD(hd_1='HIS_FLENI')
        msh.receiving_facility = HD(hd_1='FUND_FLENI')
        msh.date_time_of_message = '20250417143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='10876543', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='ALMIRON', xpn_2='OSVALDO ANIBAL')
        pid.date_time_of_birth = '19480930'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CALLE GENERAL PAZ 845', xad_3='SALTA', xad_4='SALTA', xad_5='4400', xad_6='AR')
        pid.pid_13 = '0387-4218976'
        pid.patient_account_number = CX(cx_1='10876543')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEU', pl_2='410', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='27345601', xcn_2='FRIAS', xcn_3='GERMAN', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='NEU')
        pv1.patient_type = CWE(cwe_1='V00015890')
        pv1.prior_temporary_location = PL(pl_1='20250417')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-01750')
        orc.placer_order_group_number = EI(ei_1='FIL-2025-01750')
        orc.parent_order = EIP(eip_1='20250417143000')
        orc.date_time_of_order_event = '27345601^FRIAS^GERMAN^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-01750')
        obr.filler_order_number = EI(ei_1='FIL-2025-01750')
        obr.universal_service_identifier = CWE(cwe_1='93880', cwe_2='DUPLEX SCAN EXTRACRANIAL ARTERIES', cwe_3='CPT')
        obr.observation_date_time = '20250405110000'
        obr.obr_14 = '27345601^FRIAS^GERMAN^^^DR'
        obr.obr_16 = 'AC67891'
        obr.placer_field_1 = 'US'
        obr.diagnostic_serv_sect_id = 'F'
        obr.reason_for_study = CWE(cwe_1='27345601', cwe_2='FRIAS', cwe_3='GERMAN', cwe_6='DR')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='30878-0', cwe_2='DUPLEX CAROTID', cwe_3='LN')
        obx.obx_5 = (
            'Arteria carotida interna derecha con placa ateromatosa calcificada que genera estenosis estimada en 70% por criterios de velocidad (VPS 245 '
            'cm/s, VDF 89 cm/s).'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='30878-0', cwe_2='DUPLEX CAROTID', cwe_3='LN')
        obx_2.obx_5 = 'Arteria carotida interna izquierda con placa fibrosa que genera estenosis del 40%. Arterias vertebrales con flujo anterogrado bilateral.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='30878-0', cwe_2='DUPLEX CAROTID', cwe_3='LN')
        obx_3.obx_5 = (
            'CONCLUSION: Estenosis significativa (70%) de carotida interna derecha. Se sugiere angiotomografia complementaria y evaluacion por cirugia va'
            'scular.'
        )
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ED'
        obx_4.observation_identifier = CWE(cwe_1='IMG', cwe_2='Doppler Carotideo Derecho', cwe_3='LOCAL')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = (
            'AGFA_EI^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM DQ4SEA0OEQ4LCxAWEBETFBUVFQwPFxgWFBgrFBUWEhITFBcXFxcXFxcXFxc'
            'YGBgaGhocHBwkJCQoKCgwMDAwMDA4ODg8PDxAQEBISEhQUFBgYGBwcHCAg'
        )
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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_CHURRUCA')
        msh.sending_facility = HD(hd_1='HOSP_CHURRUCA')
        msh.receiving_application = HD(hd_1='AGFA_EI')
        msh.receiving_facility = HD(hd_1='HOSP_CHURRUCA_RAD')
        msh.date_time_of_message = '20250420100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='28901456', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='VAZQUEZ', xpn_2='NATALIA CECILIA')
        pid.date_time_of_birth = '19830225'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV RIVADAVIA 5780', xad_3='BAHIA BLANCA', xad_4='BUENOS AIRES', xad_5='8000', xad_6='AR')
        pid.pid_13 = '0291-4569012'
        pid.patient_account_number = CX(cx_1='28901456')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ECO', pl_2='002', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='31345678', xcn_2='MORALES', xcn_3='GONZALO', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='END')
        pv1.patient_type = CWE(cwe_1='V00017500')
        pv1.prior_temporary_location = PL(pl_1='20250420')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-02300')
        orc.orc_7 = '1^^^20250420100000^^R'
        orc.date_time_of_order_event = '20250420100000'
        orc.orc_10 = '31345678^MORALES^GONZALO^^^DR'
        orc.orc_12 = '31345678^MORALES^GONZALO^^^DR'
        orc.enterers_location = PL(pl_1='ECO')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-02300')
        obr.universal_service_identifier = CWE(cwe_1='76536', cwe_2='US SOFT TISSUE HEAD NECK', cwe_3='CPT')
        obr.observation_date_time = '20250420100000'
        obr.obr_15 = '31345678^MORALES^GONZALO^^^DR'
        obr.result_status = '1^^^20250420100000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E04.1', cwe_2='NODULO TIROIDEO SOLITARIO NO TOXICO', cwe_3='ICD10AR')
        dg1.diagnosis_type = CWE(cwe_1='A')

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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AGFA_EI')
        msh.sending_facility = HD(hd_1='HOSP_ALEMAN_RAD')
        msh.receiving_application = HD(hd_1='HIS_GERMAN')
        msh.receiving_facility = HD(hd_1='HOSP_ALEMAN')
        msh.date_time_of_message = '20250422140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='14678923', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='SCHMIDT', xpn_2='HILDA MARTA')
        pid.date_time_of_birth = '19560712'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV LAS HERAS 2845', xad_3='BUENOS AIRES', xad_4='CABA', xad_5='1425', xad_6='AR')
        pid.pid_13 = '011-4801-3950'
        pid.patient_account_number = CX(cx_1='14678923')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DXA', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='25901876', xcn_2='FISCHER', xcn_3='MATIAS', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='END')
        pv1.patient_type = CWE(cwe_1='V00016500')
        pv1.prior_temporary_location = PL(pl_1='20250422')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-02000')
        orc.placer_order_group_number = EI(ei_1='FIL-2025-02000')
        orc.parent_order = EIP(eip_1='20250422140000')
        orc.date_time_of_order_event = '25901876^FISCHER^MATIAS^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-02000')
        obr.filler_order_number = EI(ei_1='FIL-2025-02000')
        obr.universal_service_identifier = CWE(cwe_1='77080', cwe_2='DXA BONE DENSITY AXIAL', cwe_3='CPT')
        obr.observation_date_time = '20250410080000'
        obr.obr_14 = '25901876^FISCHER^MATIAS^^^DR'
        obr.obr_16 = 'AC78901'
        obr.placer_field_1 = 'DX'
        obr.diagnostic_serv_sect_id = 'F'
        obr.reason_for_study = CWE(cwe_1='25901876', cwe_2='FISCHER', cwe_3='MATIAS', cwe_6='DR')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='38263-0', cwe_2='DXA FEMORAL NECK BMD', cwe_3='LN')
        obx.obx_5 = '0.785'
        obx.units = CWE(cwe_1='g/cm2')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='38267-1', cwe_2='DXA FEMORAL NECK T-SCORE', cwe_3='LN')
        obx_2.obx_5 = '-1.8'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='38261-4', cwe_2='DXA L1-L4 BMD', cwe_3='LN')
        obx_3.obx_5 = '0.912'
        obx_3.units = CWE(cwe_1='g/cm2')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='38265-5', cwe_2='DXA L1-L4 T-SCORE', cwe_3='LN')
        obx_4.obx_5 = '-1.5'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'TX'
        obx_5.observation_identifier = CWE(cwe_1='38269-7', cwe_2='DXA IMPRESSION', cwe_3='LN')
        obx_5.obx_5 = (
            'CONCLUSION: Osteopenia en cuello femoral y columna lumbar. T-score mas bajo: -1.8 (cuello femoral derecho). Riesgo de fractura intermedio.'
        )
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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_FAVALORO')
        msh.sending_facility = HD(hd_1='FUND_FAVALORO')
        msh.receiving_application = HD(hd_1='AGFA_EI')
        msh.receiving_facility = HD(hd_1='FUND_FAVALORO_RAD')
        msh.date_time_of_message = '20250425073000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='25678034', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='ROMANO', xpn_2='ALBERTO HUGO')
        pid.date_time_of_birth = '19700805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CALLE SAN LORENZO 367', xad_3='SAN JUAN', xad_4='SAN JUAN', xad_5='5400', xad_6='AR')
        pid.pid_13 = '0264-4231560'
        pid.patient_account_number = CX(cx_1='25678034')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CAR', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='24987651', xcn_2='TARANTINI', xcn_3='LUCIANA', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.patient_type = CWE(cwe_1='V00018000')
        pv1.prior_temporary_location = PL(pl_1='20250425')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-02500')
        orc.orc_7 = '1^^^20250425073000^^R'
        orc.date_time_of_order_event = '20250425073000'
        orc.orc_10 = '24987651^TARANTINI^LUCIANA^^^DRA'
        orc.orc_12 = '24987651^TARANTINI^LUCIANA^^^DRA'
        orc.enterers_location = PL(pl_1='CT')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-02500')
        obr.universal_service_identifier = CWE(cwe_1='75574', cwe_2='CT HEART WITH CONTRAST CARDIAC STRUCTURE AND MORPHOLOGY', cwe_3='CPT')
        obr.observation_date_time = '20250425073000'
        obr.obr_15 = '24987651^TARANTINI^LUCIANA^^^DRA'
        obr.result_status = '1^^^20250425073000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.1', cwe_2='CARDIOPATIA ATEROSCLEROTICA', cwe_3='ICD10AR')
        dg1.diagnosis_type = CWE(cwe_1='A')

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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AGFA_EI')
        msh.sending_facility = HD(hd_1='HOSP_CHURRUCA_RAD')
        msh.receiving_application = HD(hd_1='HIS_CHURRUCA')
        msh.receiving_facility = HD(hd_1='HOSP_CHURRUCA')
        msh.date_time_of_message = '20250427111500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='28901456', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='VAZQUEZ', xpn_2='NATALIA CECILIA')
        pid.date_time_of_birth = '19830225'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV RIVADAVIA 5780', xad_3='BAHIA BLANCA', xad_4='BUENOS AIRES', xad_5='8000', xad_6='AR')
        pid.pid_13 = '0291-4569012'
        pid.patient_account_number = CX(cx_1='28901456')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ECO', pl_2='002', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='31345678', xcn_2='MORALES', xcn_3='GONZALO', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='END')
        pv1.patient_type = CWE(cwe_1='V00017500')
        pv1.prior_temporary_location = PL(pl_1='20250427')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-02300')
        orc.placer_order_group_number = EI(ei_1='FIL-2025-02300')
        orc.parent_order = EIP(eip_1='20250427111500')
        orc.date_time_of_order_event = '31345678^MORALES^GONZALO^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-02300')
        obr.filler_order_number = EI(ei_1='FIL-2025-02300')
        obr.universal_service_identifier = CWE(cwe_1='76536', cwe_2='US SOFT TISSUE HEAD NECK', cwe_3='CPT')
        obr.observation_date_time = '20250420100000'
        obr.obr_14 = '31345678^MORALES^GONZALO^^^DR'
        obr.obr_16 = 'AC89012'
        obr.placer_field_1 = 'US'
        obr.diagnostic_serv_sect_id = 'F'
        obr.reason_for_study = CWE(cwe_1='31345678', cwe_2='MORALES', cwe_3='GONZALO', cwe_6='DR')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='55277-8', cwe_2='THYROID US', cwe_3='LN')
        obx.obx_5 = (
            'Lobulo derecho: nodulo solido hipoecoico de 18 x 14 x 12 mm, bordes irregulares, microcalcificaciones, mas alto que ancho. TI-RADS 4 (modera'
            'damente sospechoso).'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='55277-8', cwe_2='THYROID US', cwe_3='LN')
        obx_2.obx_5 = 'Lobulo izquierdo: nodulo mixto predominantemente quistico de 8 x 6 mm, bordes lisos. TI-RADS 2 (no sospechoso).'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='55277-8', cwe_2='THYROID US', cwe_3='LN')
        obx_3.obx_5 = 'CONCLUSION: Nodulo tiroideo derecho TI-RADS 4, se recomienda puncion aspirativa con aguja fina (PAAF) guiada por ecografia.'
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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AGFA_EI')
        msh.sending_facility = HD(hd_1='INST_ROFFO_RAD')
        msh.receiving_application = HD(hd_1='HIS_ROFFO')
        msh.receiving_facility = HD(hd_1='INST_ROFFO')
        msh.date_time_of_message = '20250430160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='34567812', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='ACEVEDO', xpn_2='IVAN LEONARDO')
        pid.date_time_of_birth = '19920118'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV 9 DE JULIO 1230', xad_3='SAN MIGUEL DE TUCUMAN', xad_4='TUCUMAN', xad_5='4000', xad_6='AR')
        pid.pid_13 = '0381-4216540'
        pid.patient_account_number = CX(cx_1='34567812')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ONC', pl_2='201', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='28123456', xcn_2='GUTIERREZ', xcn_3='SOLEDAD', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='ONC')
        pv1.patient_type = CWE(cwe_1='V00017000')
        pv1.prior_temporary_location = PL(pl_1='20250430')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-02150')
        orc.placer_order_group_number = EI(ei_1='FIL-2025-02150')
        orc.parent_order = EIP(eip_1='20250430160000')
        orc.date_time_of_order_event = '28123456^GUTIERREZ^SOLEDAD^^^DRA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-02150')
        obr.filler_order_number = EI(ei_1='FIL-2025-02150')
        obr.universal_service_identifier = CWE(cwe_1='78816', cwe_2='PET IMAGING WHOLE BODY', cwe_3='CPT')
        obr.observation_date_time = '20250415090000'
        obr.obr_14 = '28123456^GUTIERREZ^SOLEDAD^^^DRA'
        obr.obr_16 = 'AC90123'
        obr.placer_field_1 = 'PT'
        obr.diagnostic_serv_sect_id = 'F'
        obr.reason_for_study = CWE(cwe_1='28123456', cwe_2='GUTIERREZ', cwe_3='SOLEDAD', cwe_6='DRA')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='44136-0', cwe_2='PET WB IMPRESSION', cwe_3='LN')
        obx.obx_5 = 'Multiples adenopatias hipermetabolicas cervicales, axilares, mediastinicas y retroperitoneales (SUVmax 14.2 en conglomerado mediastinico).'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='44136-0', cwe_2='PET WB IMPRESSION', cwe_3='LN')
        obx_2.obx_5 = 'Esplenomegalia con captacion difusa aumentada (SUVmax 6.8). No se observa compromiso oseo ni de organos solidos.'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='44136-0', cwe_2='PET WB IMPRESSION', cwe_3='LN')
        obx_3.obx_5 = (
            'CONCLUSION: PET-CT compatible con linfoma estadio III (Ann Arbor). Compromiso ganglionar supra e infradiafragmatico con afectacion esplenica'
            '. Deauville 5.'
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
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AGFA_EI')
        msh.sending_facility = HD(hd_1='FUND_FAVALORO_RAD')
        msh.receiving_application = HD(hd_1='HIS_FAVALORO')
        msh.receiving_facility = HD(hd_1='FUND_FAVALORO')
        msh.date_time_of_message = '20250503091000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='25678034', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='ROMANO', xpn_2='ALBERTO HUGO')
        pid.date_time_of_birth = '19700805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CALLE SAN LORENZO 367', xad_3='SAN JUAN', xad_4='SAN JUAN', xad_5='5400', xad_6='AR')
        pid.pid_13 = '0264-4231560'
        pid.patient_account_number = CX(cx_1='25678034')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CAR', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='24987651', xcn_2='TARANTINI', xcn_3='LUCIANA', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.patient_type = CWE(cwe_1='V00018000')
        pv1.prior_temporary_location = PL(pl_1='20250503')

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
        orc.placer_order_number = EI(ei_1='ORD-2025-02500')
        orc.placer_order_group_number = EI(ei_1='FIL-2025-02500')
        orc.parent_order = EIP(eip_1='20250503091000')
        orc.date_time_of_order_event = '24987651^TARANTINI^LUCIANA^^^DRA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-02500')
        obr.filler_order_number = EI(ei_1='FIL-2025-02500')
        obr.universal_service_identifier = CWE(cwe_1='75574', cwe_2='CT HEART WITH CONTRAST CARDIAC STRUCTURE AND MORPHOLOGY', cwe_3='CPT')
        obr.observation_date_time = '20250425073000'
        obr.obr_14 = '24987651^TARANTINI^LUCIANA^^^DRA'
        obr.obr_16 = 'AC01234'
        obr.placer_field_1 = 'CT'
        obr.diagnostic_serv_sect_id = 'F'
        obr.reason_for_study = CWE(cwe_1='24987651', cwe_2='TARANTINI', cwe_3='LUCIANA', cwe_6='DRA')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='86974-0', cwe_2='CT CORONARY ARTERY CALCIUM SCORE', cwe_3='LN')
        obx.obx_5 = '287'
        obx.units = CWE(cwe_1='Agatston')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='86974-0', cwe_2='CT CORONARY ANGIO IMPRESSION', cwe_3='LN')
        obx_2.obx_5 = (
            'Arteria descendente anterior con placa mixta en tercio proximal que genera estenosis del 75%. Arteria circunfleja con placa calcificada en t'
            'ercio medio, estenosis 40%.'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='86974-0', cwe_2='CT CORONARY ANGIO IMPRESSION', cwe_3='LN')
        obx_3.obx_5 = 'Coronaria derecha dominante sin lesiones significativas. Calcium score: 287 unidades Agatston (riesgo alto).'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='86974-0', cwe_2='CT CORONARY ANGIO IMPRESSION', cwe_3='LN')
        obx_4.obx_5 = (
            'CONCLUSION: Enfermedad coronaria significativa en DA proximal (estenosis 75%). Se sugiere evaluacion por hemodinamia para eventual angioplastia.'
        )
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ED'
        obx_5.observation_identifier = CWE(cwe_1='PDF', cwe_2='Informe Coronariografia CT Completo', cwe_3='AUSPDI')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = (
            'AGFA_EI^AP^^Base64^'
            'JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgL01hcmtJbmZvIDw8IC9NYXJrZWQgdHJ1ZSA+PiA+PgplbmRvYmoKMiAwIG9iago8PCAv'
            'VHlwZSAvUGFnZXMgL0tpZHMgWzMgMCBSXSAvQ291bnQgMSA+PgplbmRvYmoKMyAwIG9iago8PCAvVHlwZSAvUGFnZSAvUGFyZW50'
        )
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
