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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, HD, MOC, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA05NextOfKin, AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, \
    OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, \
    SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIP, AIS, DG1, EVN, IN1, MRG, MSA, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, RGS, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ar', 'ar-lamansys.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ar/ar-lamansys.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAMANSYS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='LAB_HIS')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260310080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'LMS00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260310080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC300001', cx_4='HOSP_TANDIL', cx_5='MR'), CX(cx_1='DNI-31234567', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='AGUIRRE', xpn_2='PABLO', xpn_3='MARTIN', xpn_5='Sr.')
        pid.date_time_of_birth = '19810415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Espana 780', xad_3='Tandil', xad_4='Buenos Aires', xad_5='B7000', xad_6='AR')
        pid.pid_13 = '^^PH^02494567890~^^CP^02496789012'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLMED', pl_2='HAB201', pl_3='CAMA1', pl_4='HOSP_TANDIL')
        pv1.attending_doctor = XCN(xcn_1='MED301', xcn_2='SILVA', xcn_3='MARINA', xcn_6='Dra.')
        pv1.consulting_doctor = XCN(xcn_1='MED302', xcn_2='PAZ', xcn_3='RICARDO', xcn_6='Dr.')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.visit_number = CX(cx_1='ENC300001')
        pv1.pending_location = PL(pl_1='GUARD', pl_2='BOX01', pl_4='HOSP_TANDIL')
        pv1.admit_date_time = '20260310080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='OS005')
        in1.insurance_company_name = XON(xon_1='IOMA')
        in1.insurance_company_address = XAD(xad_1='Calle 46 n 886', xad_3='La Plata', xad_4='Buenos Aires', xad_5='B1900', xad_6='AR')

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
    """ Based on live/ar/ar-lamansys.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAMANSYS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='LAB_HIS')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260315140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'LMS00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260315140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC300001', cx_4='HOSP_TANDIL', cx_5='MR'), CX(cx_1='DNI-31234567', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='AGUIRRE', xpn_2='PABLO', xpn_3='MARTIN')
        pid.date_time_of_birth = '19810415'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLMED', pl_2='HAB201', pl_3='CAMA1', pl_4='HOSP_TANDIL')
        pv1.attending_doctor = XCN(xcn_1='MED301', xcn_2='SILVA', xcn_3='MARINA', xcn_6='Dra.')
        pv1.consulting_doctor = XCN(xcn_1='MED302', xcn_2='PAZ', xcn_3='RICARDO', xcn_6='Dr.')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.visit_number = CX(cx_1='ENC300001')
        pv1.charge_price_indicator = CWE(cwe_1='20260315140000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J15.9', cwe_2='Neumonia bacteriana, no especificada', cwe_3='I10')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
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
    """ Based on live/ar/ar-lamansys.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAMANSYS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='TURNOS')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260316093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'LMS00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260316093000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC300100', cx_4='HOSP_TANDIL', cx_5='MR'), CX(cx_1='DNI-36789012', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='SORIA', xpn_2='VALERIA', xpn_3='ANDREA', xpn_5='Sra.')
        pid.date_time_of_birth = '19910720'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Gral. Rodriguez 450', xad_3='Tandil', xad_4='Buenos Aires', xad_5='B7000', xad_6='AR')
        pid.pid_13 = '^^CP^02497890123'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='GIN01', pl_4='HOSP_TANDIL')
        pv1.attending_doctor = XCN(xcn_1='MED303', xcn_2='LUNA', xcn_3='GABRIELA', xcn_6='Dra.')
        pv1.total_payments = '20260316093000'

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
    """ Based on live/ar/ar-lamansys.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAMANSYS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='LAB_HIS')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260317074500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'LMS00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC300100', cx_4='HOSP_TANDIL', cx_5='MR')
        pid.patient_name = XPN(xpn_1='SORIA', xpn_2='VALERIA', xpn_3='ANDREA')
        pid.date_time_of_birth = '19910720'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='GIN01', pl_4='HOSP_TANDIL')
        pv1.attending_doctor = XCN(xcn_1='MED303', xcn_2='LUNA', xcn_3='GABRIELA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL40001', ei_2='LAMANSYS')
        orc.placer_order_group_number = EI(ei_1='GRP001', ei_2='LAMANSYS')
        orc.date_time_of_order_event = '20260317074500'
        orc.orc_12 = 'MED303^LUNA^GABRIELA^^^Dra.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL40001', ei_2='LAMANSYS')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Hemograma completo', cwe_3='LN')
        obr.observation_date_time = '20260317074500'
        obr.obr_16 = 'MED303^LUNA^GABRIELA^^^Dra.'
        obr.obr_27 = '^RUTINA'

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
        obr_2.placer_order_number = EI(ei_1='SOL40001', ei_2='LAMANSYS')
        obr_2.universal_service_identifier = CWE(cwe_1='5196-1', cwe_2='Grupo y factor', cwe_3='LN')
        obr_2.observation_date_time = '20260317074500'
        obr_2.obr_16 = 'MED303^LUNA^GABRIELA^^^Dra.'
        obr_2.obr_27 = '^RUTINA'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='SOL40001', ei_2='LAMANSYS')
        obr_3.universal_service_identifier = CWE(cwe_1='7905-3', cwe_2='VDRL', cwe_3='LN')
        obr_3.observation_date_time = '20260317074500'
        obr_3.obr_16 = 'MED303^LUNA^GABRIELA^^^Dra.'
        obr_3.obr_27 = '^RUTINA'

        # .. build OBR ..
        obr_4 = OBR()
        obr_4.set_id_obr = '4'
        obr_4.placer_order_number = EI(ei_1='SOL40001', ei_2='LAMANSYS')
        obr_4.universal_service_identifier = CWE(cwe_1='5220-9', cwe_2='HIV 1+2 Ac', cwe_3='LN')
        obr_4.observation_date_time = '20260317074500'
        obr_4.obr_16 = 'MED303^LUNA^GABRIELA^^^Dra.'
        obr_4.obr_27 = '^RUTINA'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='Z34.0', cwe_2='Supervision embarazo normal, primer trimestre', cwe_3='I10')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3, obr_4, dg1]

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
    """ Based on live/ar/ar-lamansys.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_HIS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='LAMANSYS')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260317143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB50001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC300100', cx_4='HOSP_TANDIL', cx_5='MR')
        pid.patient_name = XPN(xpn_1='SORIA', xpn_2='VALERIA', xpn_3='ANDREA')
        pid.date_time_of_birth = '19910720'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='GIN01', pl_4='HOSP_TANDIL')

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
        orc.placer_order_number = EI(ei_1='SOL40001', ei_2='LAMANSYS')
        orc.filler_order_number = EI(ei_1='RES60001', ei_2='LAB_HIS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL40001', ei_2='LAMANSYS')
        obr.filler_order_number = EI(ei_1='RES60001', ei_2='LAB_HIS')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Hemograma completo', cwe_3='LN')
        obr.observation_date_time = '20260317074500'
        obr.obr_14 = 'MED303^LUNA^GABRIELA^^^Dra.'
        obr.filler_field_1 = '20260317140000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobina', cwe_3='LN')
        obx.obx_5 = '11.8'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '11.0-16.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrito', cwe_3='LN')
        obx_2.obx_5 = '35.5'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '33.0-46.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocitos', cwe_3='LN')
        obx_3.obx_5 = '9.8'
        obx_3.units = CWE(cwe_1='x10E3/uL')
        obx_3.reference_range = '4.5-11.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='777-3', cwe_2='Plaquetas', cwe_3='LN')
        obx_4.obx_5 = '220'
        obx_4.units = CWE(cwe_1='x10E3/uL')
        obx_4.reference_range = '150-400'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='5196-1', cwe_2='Grupo sanguineo', cwe_3='LN')
        obx_5.obx_5 = 'A Rh Positivo'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='7905-3', cwe_2='VDRL', cwe_3='LN')
        obx_6.obx_5 = 'No reactivo'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='5220-9', cwe_2='HIV 1+2 Ac', cwe_3='LN')
        obx_7.obx_5 = 'No reactivo'
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
    """ Based on live/ar/ar-lamansys.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAMANSYS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='RIS_PACS')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260320100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'LMS00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC300100', cx_4='HOSP_TANDIL', cx_5='MR'), CX(cx_1='DNI-36789012', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='SORIA', xpn_2='VALERIA', xpn_3='ANDREA')
        pid.date_time_of_birth = '19910720'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='GIN01', pl_4='HOSP_TANDIL')
        pv1.attending_doctor = XCN(xcn_1='MED303', xcn_2='LUNA', xcn_3='GABRIELA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL40002', ei_2='LAMANSYS')
        orc.placer_order_group_number = EI(ei_1='GRP002', ei_2='LAMANSYS')
        orc.date_time_of_order_event = '20260320100000'
        orc.orc_12 = 'MED303^LUNA^GABRIELA^^^Dra.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL40002', ei_2='LAMANSYS')
        obr.universal_service_identifier = CWE(cwe_1='76801', cwe_2='Ecografia obstetrica primer trimestre', cwe_3='CPT')
        obr.observation_date_time = '20260320100000'
        obr.obr_16 = 'MED303^LUNA^GABRIELA^^^Dra.'
        obr.obr_27 = '^RUTINA'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='Z34.0', cwe_2='Supervision embarazo normal, primer trimestre', cwe_3='I10')

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
        nte.comment = 'Primer control ecografico. FUM 20260115.'

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
    """ Based on live/ar/ar-lamansys.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_PACS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='LAMANSYS')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260320140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD40001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC300100', cx_4='HOSP_TANDIL', cx_5='MR')
        pid.patient_name = XPN(xpn_1='SORIA', xpn_2='VALERIA', xpn_3='ANDREA')
        pid.date_time_of_birth = '19910720'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='GIN01', pl_4='HOSP_TANDIL')
        pv1.attending_doctor = XCN(xcn_1='MED303', xcn_2='LUNA', xcn_3='GABRIELA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL40002', ei_2='LAMANSYS')
        orc.filler_order_number = EI(ei_1='INF80001', ei_2='RIS_PACS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL40002', ei_2='LAMANSYS')
        obr.filler_order_number = EI(ei_1='INF80001', ei_2='RIS_PACS')
        obr.universal_service_identifier = CWE(cwe_1='76801', cwe_2='Ecografia obstetrica primer trimestre', cwe_3='CPT')
        obr.observation_date_time = '20260320100000'
        obr.obr_14 = 'MED303^LUNA^GABRIELA^^^Dra.'
        obr.filler_field_1 = '20260320133000'
        obr.results_rpt_status_chng_date_time = 'RAD'
        obr.charge_to_practice = MOC(moc_1='F')
        obr.transportation_mode = 'MED304^FERRARI^MARTIN^^^Dr.'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='76801&IMP', cwe_2='Ecografia obstetrica impresion', cwe_3='CPT')
        obx.obx_5 = (
            'Embarazo unico intrauterino de 9 semanas por LCN de 23mm. Actividad cardiaca embrionaria presente. FCE 165 lpm. Saco gestacional y saco vite'
            'lino normales. Sin hallazgos patologicos.'
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
    """ Based on live/ar/ar-lamansys.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_PACS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='LAMANSYS')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260320141000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD40002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC300100', cx_4='HOSP_TANDIL', cx_5='MR')
        pid.patient_name = XPN(xpn_1='SORIA', xpn_2='VALERIA', xpn_3='ANDREA')
        pid.date_time_of_birth = '19910720'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='GIN01', pl_4='HOSP_TANDIL')

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
        orc.placer_order_number = EI(ei_1='SOL40002', ei_2='LAMANSYS')
        orc.filler_order_number = EI(ei_1='INF80002', ei_2='RIS_PACS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL40002', ei_2='LAMANSYS')
        obr.filler_order_number = EI(ei_1='INF80002', ei_2='RIS_PACS')
        obr.universal_service_identifier = CWE(cwe_1='76801', cwe_2='Ecografia obstetrica imagen', cwe_3='CPT')
        obr.observation_date_time = '20260320100000'
        obr.obr_14 = 'MED303^LUNA^GABRIELA^^^Dra.'
        obr.filler_field_1 = '20260320134000'
        obr.results_rpt_status_chng_date_time = 'RAD'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='IMG', cwe_2='Ecografia obstetrica primer trimestre', cwe_3='LOCAL')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'LAMANSYS^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/4QBMRXhpZgAATU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAAAYKADAAQAAAABAAAAYAAAAAD/2wBDAAgG'
            'BgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy'
            'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCABgAGADASIAAhEBAxEB/8QAHAAAAgIDAQEAAAAAAAAAAAAABQYEBwIDCAEA/8QANRAAAgEDAwIEBAQFBQEAAAAAAQIDAAQRBRIh'
            'MUEGE1FhByJxgRQykfAjQqGxwRUzNNHh8f/EABkBAAMBAQEAAAAAAAAAAAAAAAIDBAEABf/EACQRAAICAgICAgIDAAAAAAAAAAABAgADERIhMUEEURMiMmFx/9oADAMBAAIRAxEAPwCw'
            'tR1uw0pPMu7mOBB/M7Yr5PN8SdJjGPxAPphNZ6n4F0HVZjPc2KmVvzOrlGP3BFLWofB/S5sy2Nxc2jnsGDr+hx/asIYjky2umtuRLZ8M/GDTfEEoszbzWV8VLEN0ZW7EHnH0/xR6uSPg'
            'TY2l79qXttMyH5I2hK7vqSf8UweCvBa+F/xJmuI7ieVdqMydFH+4mgfIrrfcLIqN+IktiiiiuhiiiigIooooAxZVZSrAMp6gjINcx1rw9d6DrN7ZNbSxol5LGCVO05bsfvXUhHNKnjzw'
            'z/AKxo8wgTN3bnfDj+bHVf1H9qVcgZeC3+sQ7zL58EWepagXgtmaJmJP4dyhH/E9R9DQ4aLqVmMpM2QOhfIP6ihreLr+PU9MjubJpEn2gPBIuGVu44PPuc0y2msanp+0XtmJ0H/JtiS4'
            '/unIrZ5H6mQrV3iV3f+G9aTdMttcRRj+eWMoB9yKC3/h3VtOjL3VhcRRDq7IcD7jiu29E17TNetfP028iuYs4JRuVPow6g/Wj5Gea2u5rPBl74iVR8J/CtlcaItxfQJPcXBLLvGdi9gP'
            'vzWHxX+FGnwaDdX+kwyQ3Nqhk8suXVgOoGeSfbvXQ7daxv7GC/spbS6iWWCVCjow4YHqKNbWY4MBqVX8okBRRRVsqiiiigIooooA8IzXlFFAIr8QfBOn6/p90yw+VqkUREM6ngkj+Vvb'
            '/FcsRxJHiJU+m05I3n7dv1ooqe78S6l4s6P+H8cUHhzToYQAFtkHH2r0+FtHfObCBj7hcmiiqL2cqZJShQATR/wBD0SDltPtx7eUuKKoohSB1G7s6CiiiiI//2Q=='
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
    """ Based on live/ar/ar-lamansys.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAMANSYS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='MPI_PROV')
        msh.receiving_facility = HD(hd_1='MSN')
        msh.date_time_of_message = '20260321100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'LMS00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260321100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC300001', cx_4='HOSP_TANDIL', cx_5='MR'), CX(cx_1='DNI-31234567', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='AGUIRRE', xpn_2='PABLO', xpn_3='MARTIN', xpn_5='Sr.')
        pid.date_time_of_birth = '19810415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='9 de Julio 1200', xad_3='Tandil', xad_4='Buenos Aires', xad_5='B7000', xad_6='AR')
        pid.pid_13 = '^^PH^02494567890~^^CP^02496789012~^^Internet^paguirre@gmail.com'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='C101', pl_4='HOSP_TANDIL')
        pv1.attending_doctor = XCN(xcn_1='MED301', xcn_2='SILVA', xcn_3='MARINA', xcn_6='Dra.')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='OS005')
        in1.insurance_company_name = XON(xon_1='IOMA')
        in1.insurance_company_address = XAD(xad_1='Calle 46 n 886', xad_3='La Plata', xad_4='Buenos Aires', xad_5='B1900', xad_6='AR')

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
    """ Based on live/ar/ar-lamansys.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAMANSYS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='TURNOS')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260322100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'LMS00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='TUR80001', ei_2='LAMANSYS')
        sch.filler_appointment_id = EI(ei_1='TUR80001', ei_2='LAMANSYS')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Rutina', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='CONTROL', cwe_2='Control prenatal', cwe_3='LOCAL')
        sch.sch_9 = '20'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^20^202604011000^202604011020'
        sch.filler_contact_person = XCN(xcn_1='MED303', xcn_2='LUNA', xcn_3='GABRIELA', xcn_6='Dra.')
        sch.filler_contact_phone_number = XTN(xtn_3='PH', xtn_4='02494567890')
        sch.filler_contact_address = XAD(xad_1='CONSUL', xad_2='GIN01', xad_4='HOSP_TANDIL')
        sch.entered_by_person = XCN(xcn_1='Confirmado')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC300100', cx_4='HOSP_TANDIL', cx_5='MR')
        pid.patient_name = XPN(xpn_1='SORIA', xpn_2='VALERIA', xpn_3='ANDREA')
        pid.date_time_of_birth = '19910720'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='GIN01', pl_4='HOSP_TANDIL')
        pv1.attending_doctor = XCN(xcn_1='MED303', xcn_2='LUNA', xcn_3='GABRIELA', xcn_6='Dra.')

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
        ais.universal_service_identifier = CWE(cwe_1='OBSTET', cwe_2='Control prenatal', cwe_3='LOCAL')
        ais.start_date_time_offset_units = CNE(cne_1='202604011000')
        ais.duration = '0'
        ais.duration_units = CNE(cne_1='MIN')
        ais.allow_substitution_code = CWE(cwe_1='20')
        ais.filler_status_code = CWE(cwe_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.personnel_resource_id = XCN(xcn_1='MED303', xcn_2='LUNA', xcn_3='GABRIELA', xcn_6='Dra.')
        aip.resource_type = CWE(cwe_1='ATT', cwe_2='Medico tratante', cwe_3='HL70443')

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
    """ Based on live/ar/ar-lamansys.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_HIS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='LAMANSYS')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260323150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB50002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC300100', cx_4='HOSP_TANDIL', cx_5='MR')
        pid.patient_name = XPN(xpn_1='SORIA', xpn_2='VALERIA', xpn_3='ANDREA')
        pid.date_time_of_birth = '19910720'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='GIN01', pl_4='HOSP_TANDIL')

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
        orc.placer_order_number = EI(ei_1='SOL40003', ei_2='LAMANSYS')
        orc.filler_order_number = EI(ei_1='RES60002', ei_2='LAB_HIS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL40003', ei_2='LAMANSYS')
        obr.filler_order_number = EI(ei_1='RES60002', ei_2='LAB_HIS')
        obr.universal_service_identifier = CWE(cwe_1='57728-2', cwe_2='Serologia TORCH', cwe_3='LN')
        obr.observation_date_time = '20260323074500'
        obr.obr_14 = 'MED303^LUNA^GABRIELA^^^Dra.'
        obr.filler_field_1 = '20260323143000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5121-9', cwe_2='Toxoplasma IgG', cwe_3='LN')
        obx.obx_5 = 'Positivo'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='5122-7', cwe_2='Toxoplasma IgM', cwe_3='LN')
        obx_2.obx_5 = 'Negativo'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='5132-6', cwe_2='Rubeola IgG', cwe_3='LN')
        obx_3.obx_5 = 'Positivo'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='5133-4', cwe_2='Rubeola IgM', cwe_3='LN')
        obx_4.obx_5 = 'Negativo'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='5180-5', cwe_2='Chagas IgG', cwe_3='LN')
        obx_5.obx_5 = 'Negativo'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='7906-1', cwe_2='Hepatitis B HBsAg', cwe_3='LN')
        obx_6.obx_5 = 'No reactivo'
        obx_6.observation_result_status = 'F'

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
    """ Based on live/ar/ar-lamansys.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_HIS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='LAMANSYS')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260324100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB50003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC300001', cx_4='HOSP_TANDIL', cx_5='MR')
        pid.patient_name = XPN(xpn_1='AGUIRRE', xpn_2='PABLO', xpn_3='MARTIN')
        pid.date_time_of_birth = '19810415'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLMED', pl_2='HAB201', pl_3='CAMA1', pl_4='HOSP_TANDIL')

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
        orc.placer_order_number = EI(ei_1='SOL40004', ei_2='LAMANSYS')
        orc.filler_order_number = EI(ei_1='RES60003', ei_2='LAB_HIS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL40004', ei_2='LAMANSYS')
        obr.filler_order_number = EI(ei_1='RES60003', ei_2='LAB_HIS')
        obr.universal_service_identifier = CWE(cwe_1='600-7', cwe_2='Hemocultivo', cwe_3='LN')
        obr.observation_date_time = '20260312060000'
        obr.obr_14 = 'MED301^SILVA^MARINA^^^Dra.'
        obr.filler_field_1 = '20260324093000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Hemocultivo resultado', cwe_3='LN')
        obx.obx_5 = 'Positivo - Streptococcus pneumoniae'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18993-6', cwe_2='Penicilina sensibilidad', cwe_3='LN')
        obx_2.obx_5 = 'Sensible'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Ceftriaxona sensibilidad', cwe_3='LN')
        obx_3.obx_5 = 'Sensible'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ED'
        obx_4.observation_identifier = CWE(cwe_1='PDF', cwe_2='Informe microbiologia completo', cwe_3='AUSPDI')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = (
            'LAMANSYS^AP^^Base64^'
            'JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0Nv'
            'dW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8'
            'PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyMjAgPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQooSW5m'
            'b3JtZSBkZSBNaWNyb2Jpb2xvZ2lhKSBUagowIC0yMCBUZAooUGFjaWVudGU6IEFndWlycmUsIFBhYmxvIE1hcnRpbikgVGoKMCAtMjAgVGQKKEhDIDMwMDAwMSkgVGoKMCAtMjAgVGQK'
            'KEhlbW9jdWx0aXZvOiBQb3NpdGl2bykgVGoKMCAtMjAgVGQKKEdlcm1lbjogU3RyZXB0b2NvY2N1cyBwbmV1bW9uaWFlKSBUagowIC0yMCBUZAooQW50aWJpb2dyYW1hOiBQZW5pY2ls'
            'aW5hIFMsIENlZnRyaWF4b25hIFMpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2Eg'
            'Pj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAw'
            'MDMwNiAwMDAwMCBuIAowMDAwMDAwNTc4IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNjU5CiUlRU9GCg=='
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
    """ Based on live/ar/ar-lamansys.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAMANSYS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='CAMAS')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260312150000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'LMS00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260312150000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC300001', cx_4='HOSP_TANDIL', cx_5='MR'), CX(cx_1='DNI-31234567', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='AGUIRRE', xpn_2='PABLO', xpn_3='MARTIN')
        pid.date_time_of_birth = '19810415'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUMO', pl_2='HAB105', pl_3='CAMA2', pl_4='HOSP_TANDIL')
        pv1.attending_doctor = XCN(xcn_1='MED301', xcn_2='SILVA', xcn_3='MARINA', xcn_6='Dra.')
        pv1.account_status = CWE(cwe_1='CLMED', cwe_2='HAB201', cwe_3='CAMA1', cwe_4='HOSP_TANDIL')
        pv1.prior_temporary_location = PL(pl_1='20260312150000')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/ar/ar-lamansys.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_HIS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='LAMANSYS')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260325110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB50004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC300100', cx_4='HOSP_TANDIL', cx_5='MR')
        pid.patient_name = XPN(xpn_1='SORIA', xpn_2='VALERIA', xpn_3='ANDREA')
        pid.date_time_of_birth = '19910720'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='GIN01', pl_4='HOSP_TANDIL')

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
        orc.placer_order_number = EI(ei_1='SOL40005', ei_2='LAMANSYS')
        orc.filler_order_number = EI(ei_1='RES60004', ei_2='LAB_HIS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL40005', ei_2='LAMANSYS')
        obr.filler_order_number = EI(ei_1='RES60004', ei_2='LAB_HIS')
        obr.universal_service_identifier = CWE(cwe_1='24356-8', cwe_2='Orina completa', cwe_3='LN')
        obr.observation_date_time = '20260325070000'
        obr.obr_14 = 'MED303^LUNA^GABRIELA^^^Dra.'
        obr.filler_field_1 = '20260325103000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2756-5', cwe_2='pH orina', cwe_3='LN')
        obx.obx_5 = '6.5'
        obx.reference_range = '5.0-8.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='5767-9', cwe_2='Aspecto orina', cwe_3='LN')
        obx_2.obx_5 = 'Claro'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='5778-6', cwe_2='Color orina', cwe_3='LN')
        obx_3.obx_5 = 'Amarillo'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='5804-0', cwe_2='Proteinas orina', cwe_3='LN')
        obx_4.obx_5 = 'Negativo'
        obx_4.reference_range = 'Negativo'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='5792-7', cwe_2='Glucosa orina', cwe_3='LN')
        obx_5.obx_5 = 'Negativo'
        obx_5.reference_range = 'Negativo'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='20454-5', cwe_2='Leucocitos orina', cwe_3='LN')
        obx_6.obx_5 = '2'
        obx_6.units = CWE(cwe_1='/campo')
        obx_6.reference_range = '0-5'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

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
    """ Based on live/ar/ar-lamansys.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAMANSYS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='MPI_PROV')
        msh.receiving_facility = HD(hd_1='MSN')
        msh.date_time_of_message = '20260326080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'LMS00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20260326080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC300200', cx_4='HOSP_TANDIL', cx_5='MR'), CX(cx_1='DNI-45678901', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='ROMERO', xpn_2='LUCAS', xpn_3='EZEQUIEL', xpn_5='Sr.')
        pid.date_time_of_birth = '20010520'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Belgrano 890', xad_3='Tandil', xad_4='Buenos Aires', xad_5='B7000', xad_6='AR')
        pid.pid_13 = '^^CP^02498901234~^^Internet^lromero@gmail.com'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='ROMERO', xpn_2='PATRICIA', xpn_4='Sra.')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Madre', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Belgrano 890', xad_3='Tandil', xad_4='Buenos Aires', xad_5='B7000', xad_6='AR')
        nk1.nk1_5 = '^^CP^02497654321'

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
    """ Based on live/ar/ar-lamansys.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAMANSYS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='RIS_PACS')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260327090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'LMS00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC300001', cx_4='HOSP_TANDIL', cx_5='MR'), CX(cx_1='DNI-31234567', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='AGUIRRE', xpn_2='PABLO', xpn_3='MARTIN')
        pid.date_time_of_birth = '19810415'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUMO', pl_2='HAB105', pl_3='CAMA2', pl_4='HOSP_TANDIL')
        pv1.attending_doctor = XCN(xcn_1='MED301', xcn_2='SILVA', xcn_3='MARINA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL40006', ei_2='LAMANSYS')
        orc.placer_order_group_number = EI(ei_1='GRP003', ei_2='LAMANSYS')
        orc.date_time_of_order_event = '20260327090000'
        orc.orc_12 = 'MED301^SILVA^MARINA^^^Dra.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL40006', ei_2='LAMANSYS')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Radiografia de torax PA y lateral', cwe_3='CPT')
        obr.observation_date_time = '20260327090000'
        obr.obr_16 = 'MED301^SILVA^MARINA^^^Dra.'
        obr.obr_27 = '^RUTINA'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J15.9', cwe_2='Neumonia bacteriana', cwe_3='I10')

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
        nte.comment = 'Control evolutivo de neumonia.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/ar/ar-lamansys.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_PACS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='LAMANSYS')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260327150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD40003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC300001', cx_4='HOSP_TANDIL', cx_5='MR')
        pid.patient_name = XPN(xpn_1='AGUIRRE', xpn_2='PABLO', xpn_3='MARTIN')
        pid.date_time_of_birth = '19810415'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUMO', pl_2='HAB105', pl_3='CAMA2', pl_4='HOSP_TANDIL')

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
        orc.placer_order_number = EI(ei_1='SOL40006', ei_2='LAMANSYS')
        orc.filler_order_number = EI(ei_1='INF80003', ei_2='RIS_PACS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL40006', ei_2='LAMANSYS')
        obr.filler_order_number = EI(ei_1='INF80003', ei_2='RIS_PACS')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Radiografia de torax', cwe_3='CPT')
        obr.observation_date_time = '20260327090000'
        obr.obr_14 = 'MED301^SILVA^MARINA^^^Dra.'
        obr.filler_field_1 = '20260327143000'
        obr.results_rpt_status_chng_date_time = 'RAD'
        obr.charge_to_practice = MOC(moc_1='F')
        obr.transportation_mode = 'MED305^GARCIA^ALEJANDRO^^^Dr.'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='71020&IMP', cwe_2='Rx torax impresion', cwe_3='CPT')
        obx.obx_5 = 'Mejoria con respecto a estudio previo. Resolucion parcial del infiltrado en base derecha. Sin derrame pleural. Silueta cardiaca normal.'
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
    """ Based on live/ar/ar-lamansys.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAMANSYS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='MPI_PROV')
        msh.receiving_facility = HD(hd_1='MSN')
        msh.date_time_of_message = '20260328090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'LMS00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260328090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC300001', cx_4='HOSP_TANDIL', cx_5='MR'), CX(cx_1='DNI-31234567', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='AGUIRRE', xpn_2='PABLO', xpn_3='MARTIN')
        pid.date_time_of_birth = '19810415'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='HC300999', cx_4='HOSP_TANDIL', cx_5='MR')
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
    """ Based on live/ar/ar-lamansys.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAMANSYS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='REPOSITORIO')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260315150000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'LMS00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260315150000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC300001', cx_4='HOSP_TANDIL', cx_5='MR')
        pid.patient_name = XPN(xpn_1='AGUIRRE', xpn_2='PABLO', xpn_3='MARTIN')
        pid.date_time_of_birth = '19810415'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUMO', pl_2='HAB105', pl_3='CAMA2', pl_4='HOSP_TANDIL')
        pv1.attending_doctor = XCN(xcn_1='MED301', xcn_2='SILVA', xcn_3='MARINA', xcn_6='Dra.')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Epicrisis', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Texto^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260315143000')
        txa.assigned_document_authenticator = XCN(xcn_1='MED301', xcn_2='SILVA', xcn_3='MARINA', xcn_6='Dra.')
        txa.placer_order_number = EI(ei_1='DOC90001')
        txa.unique_document_file_name = 'AU^Autenticado^HL70271'
        txa.document_confidentiality_status = '20260315150000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='DS', cwe_2='Epicrisis', cwe_3='LOCAL')
        obx.obx_5 = (
            'Paciente masculino de 44 anios internado por neumonia bacteriana adquirida en comunidad. Hemocultivo positivo para S. pneumoniae sensible a '
            'penicilina. Tratamiento con ampicilina-sulbactam EV 7 dias con buena evolucion. Alta con amoxicilina VO 7 dias mas.'
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
    """ Based on live/ar/ar-lamansys.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_HIS')
        msh.sending_facility = HD(hd_1='HOSP_TANDIL')
        msh.receiving_application = HD(hd_1='LAMANSYS')
        msh.receiving_facility = HD(hd_1='HOSP_TANDIL')
        msh.date_time_of_message = '20260310080100'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'ACK80001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'CA'
        msa.message_control_id = 'LMS00001'
        msa.msa_3 = 'Admision recibida correctamente'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
