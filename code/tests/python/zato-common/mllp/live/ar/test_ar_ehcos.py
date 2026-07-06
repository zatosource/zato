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
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA05NextOfKin, AdtA39Patient, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, SiuS12PersonnelResource, \
    SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIP, AIS, DG1, EVN, IN1, MRG, MSA, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, RGS, RXO, RXR, SCH

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ar', 'ar-ehcos.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ar/ar-ehcos.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHCOS')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='LAB_PROV')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260310090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'EHC00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260310090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC200001', cx_4='HOSP_RAWSON', cx_5='MR'), CX(cx_1='DNI-26789012', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='BUSTOS', xpn_2='DANIEL', xpn_3='ALEJANDRO', xpn_5='Sr.')
        pid.date_time_of_birth = '19780520'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Velez Sarsfield 800', xad_3='Cordoba', xad_4='Cordoba', xad_5='X5000', xad_6='AR')
        pid.pid_13 = '^^PH^03514567890~^^CP^03516789012'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLMED', pl_2='HAB102', pl_3='CAMA1', pl_4='HOSP_RAWSON')
        pv1.attending_doctor = XCN(xcn_1='MED201', xcn_2='GIMENEZ', xcn_3='ESTELA', xcn_6='Dra.')
        pv1.consulting_doctor = XCN(xcn_1='MED202', xcn_2='ROJAS', xcn_3='FEDERICO', xcn_6='Dr.')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.visit_number = CX(cx_1='ENC200001')
        pv1.pending_location = PL(pl_1='GUARD', pl_2='BOX01', pl_4='HOSP_RAWSON')
        pv1.admit_date_time = '20260310090000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='OS004')
        in1.insurance_company_name = XON(xon_1='APROSS')
        in1.insurance_company_address = XAD(xad_1='Av. Poeta Lugones 401', xad_3='Cordoba', xad_4='Cordoba', xad_5='X5000', xad_6='AR')

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
    """ Based on live/ar/ar-ehcos.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHCOS')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='LAB_PROV')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260316150000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'EHC00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260316150000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC200001', cx_4='HOSP_RAWSON', cx_5='MR'), CX(cx_1='DNI-26789012', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='BUSTOS', xpn_2='DANIEL', xpn_3='ALEJANDRO', xpn_5='Sr.')
        pid.date_time_of_birth = '19780520'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Velez Sarsfield 800', xad_3='Cordoba', xad_4='Cordoba', xad_5='X5000', xad_6='AR')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLMED', pl_2='HAB102', pl_3='CAMA1', pl_4='HOSP_RAWSON')
        pv1.attending_doctor = XCN(xcn_1='MED201', xcn_2='GIMENEZ', xcn_3='ESTELA', xcn_6='Dra.')
        pv1.consulting_doctor = XCN(xcn_1='MED202', xcn_2='ROJAS', xcn_3='FEDERICO', xcn_6='Dr.')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.visit_number = CX(cx_1='ENC200001')
        pv1.charge_price_indicator = CWE(cwe_1='20260316150000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I10', cwe_2='Hipertension arterial esencial', cwe_3='I10')

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
    """ Based on live/ar/ar-ehcos.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHCOS')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='TURNOS')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260317093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'EHC00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260317093000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC200100', cx_4='HOSP_RAWSON', cx_5='MR'), CX(cx_1='DNI-33456789', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='PEREYRA', xpn_2='ROMINA', xpn_3='SOLEDAD', xpn_5='Sra.')
        pid.date_time_of_birth = '19890612'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Bv. San Juan 1200', xad_3='Cordoba', xad_4='Cordoba', xad_5='X5000', xad_6='AR')
        pid.pid_13 = '^^CP^03517890123'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='END01', pl_4='HOSP_RAWSON')
        pv1.attending_doctor = XCN(xcn_1='MED203', xcn_2='VILLEGAS', xcn_3='CAROLINA', xcn_6='Dra.')
        pv1.total_payments = '20260317093000'

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
    """ Based on live/ar/ar-ehcos.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHCOS')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='LAB_PROV')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260318074500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EHC00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC200001', cx_4='HOSP_RAWSON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BUSTOS', xpn_2='DANIEL', xpn_3='ALEJANDRO')
        pid.date_time_of_birth = '19780520'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLMED', pl_2='HAB102', pl_3='CAMA1', pl_4='HOSP_RAWSON')
        pv1.attending_doctor = XCN(xcn_1='MED201', xcn_2='GIMENEZ', xcn_3='ESTELA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL30001', ei_2='EHCOS')
        orc.placer_order_group_number = EI(ei_1='GRP001', ei_2='EHCOS')
        orc.date_time_of_order_event = '20260318074500'
        orc.orc_12 = 'MED201^GIMENEZ^ESTELA^^^Dra.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL30001', ei_2='EHCOS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Panel metabolico', cwe_3='LN')
        obr.observation_date_time = '20260318074500'
        obr.obr_16 = 'MED201^GIMENEZ^ESTELA^^^Dra.'
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
        obr_2.placer_order_number = EI(ei_1='SOL30001', ei_2='EHCOS')
        obr_2.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Hemograma completo', cwe_3='LN')
        obr_2.observation_date_time = '20260318074500'
        obr_2.obr_16 = 'MED201^GIMENEZ^ESTELA^^^Dra.'
        obr_2.obr_27 = '^RUTINA'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I10', cwe_2='Hipertension arterial esencial', cwe_3='I10')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, dg1]

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
    """ Based on live/ar/ar-ehcos.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_PROV')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='EHCOS')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260318143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB40001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC200001', cx_4='HOSP_RAWSON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BUSTOS', xpn_2='DANIEL', xpn_3='ALEJANDRO')
        pid.date_time_of_birth = '19780520'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLMED', pl_2='HAB102', pl_3='CAMA1', pl_4='HOSP_RAWSON')

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
        orc.placer_order_number = EI(ei_1='SOL30001', ei_2='EHCOS')
        orc.filler_order_number = EI(ei_1='RES50001', ei_2='LAB_PROV')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL30001', ei_2='EHCOS')
        obr.filler_order_number = EI(ei_1='RES50001', ei_2='LAB_PROV')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Panel metabolico', cwe_3='LN')
        obr.observation_date_time = '20260318074500'
        obr.obr_14 = 'MED201^GIMENEZ^ESTELA^^^Dra.'
        obr.filler_field_1 = '20260318140000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucosa', cwe_3='LN')
        obx.obx_5 = '110'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-110'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinina', cwe_3='LN')
        obx_2.obx_5 = '1.4'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.7-1.3'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_3.obx_5 = '55'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '10-50'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodio', cwe_3='LN')
        obx_4.obx_5 = '137'
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
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potasio', cwe_3='LN')
        obx_5.obx_5 = '5.2'
        obx_5.units = CWE(cwe_1='mEq/L')
        obx_5.reference_range = '3.5-5.0'
        obx_5.interpretation_codes = CWE(cwe_1='H')
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
    """ Based on live/ar/ar-ehcos.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHCOS')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='MPI_PROV')
        msh.receiving_facility = HD(hd_1='GOB_CBA')
        msh.date_time_of_message = '20260319100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'EHC00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260319100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC200001', cx_4='HOSP_RAWSON', cx_5='MR'), CX(cx_1='DNI-26789012', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='BUSTOS', xpn_2='DANIEL', xpn_3='ALEJANDRO', xpn_5='Sr.')
        pid.date_time_of_birth = '19780520'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Dean Funes 500', xad_3='Cordoba', xad_4='Cordoba', xad_5='X5000', xad_6='AR')
        pid.pid_13 = '^^PH^03514567890~^^CP^03516789012~^^Internet^dbustos@outlook.com'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='NEFRO', pl_4='HOSP_RAWSON')
        pv1.attending_doctor = XCN(xcn_1='MED204', xcn_2='AGUIRRE', xcn_3='PABLO', xcn_6='Dr.')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='OS004')
        in1.insurance_company_name = XON(xon_1='APROSS')
        in1.insurance_company_address = XAD(xad_1='Av. Poeta Lugones 401', xad_3='Cordoba', xad_4='Cordoba', xad_5='X5000', xad_6='AR')

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
    """ Based on live/ar/ar-ehcos.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHCOS')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='RIS_PACS')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260320090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EHC00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC200001', cx_4='HOSP_RAWSON', cx_5='MR'), CX(cx_1='DNI-26789012', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='BUSTOS', xpn_2='DANIEL', xpn_3='ALEJANDRO')
        pid.date_time_of_birth = '19780520'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='NEFRO', pl_4='HOSP_RAWSON')
        pv1.attending_doctor = XCN(xcn_1='MED204', xcn_2='AGUIRRE', xcn_3='PABLO', xcn_6='Dr.')

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
        orc.placer_order_number = EI(ei_1='SOL30002', ei_2='EHCOS')
        orc.placer_order_group_number = EI(ei_1='GRP002', ei_2='EHCOS')
        orc.date_time_of_order_event = '20260320090000'
        orc.orc_12 = 'MED204^AGUIRRE^PABLO^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL30002', ei_2='EHCOS')
        obr.universal_service_identifier = CWE(cwe_1='76775', cwe_2='Ecografia renal bilateral', cwe_3='CPT')
        obr.observation_date_time = '20260320090000'
        obr.obr_16 = 'MED204^AGUIRRE^PABLO^^^Dr.'
        obr.obr_27 = '^RUTINA'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='N18.3', cwe_2='Enfermedad renal cronica estadio 3', cwe_3='I10')

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
    """ Based on live/ar/ar-ehcos.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_PACS')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='EHCOS')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260320140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD30001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC200001', cx_4='HOSP_RAWSON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BUSTOS', xpn_2='DANIEL', xpn_3='ALEJANDRO')
        pid.date_time_of_birth = '19780520'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='NEFRO', pl_4='HOSP_RAWSON')
        pv1.attending_doctor = XCN(xcn_1='MED204', xcn_2='AGUIRRE', xcn_3='PABLO', xcn_6='Dr.')

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
        orc.placer_order_number = EI(ei_1='SOL30002', ei_2='EHCOS')
        orc.filler_order_number = EI(ei_1='INF70001', ei_2='RIS_PACS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL30002', ei_2='EHCOS')
        obr.filler_order_number = EI(ei_1='INF70001', ei_2='RIS_PACS')
        obr.universal_service_identifier = CWE(cwe_1='76775', cwe_2='Ecografia renal bilateral', cwe_3='CPT')
        obr.observation_date_time = '20260320090000'
        obr.obr_14 = 'MED204^AGUIRRE^PABLO^^^Dr.'
        obr.filler_field_1 = '20260320133000'
        obr.results_rpt_status_chng_date_time = 'RAD'
        obr.charge_to_practice = MOC(moc_1='F')
        obr.transportation_mode = 'MED205^QUIROGA^MARTIN^^^Dr.'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='76775&IMP', cwe_2='Ecografia renal impresion', cwe_3='CPT')
        obx.obx_5 = (
            'Rinon derecho 10.2 cm, rinon izquierdo 9.8 cm. Aumento difuso de ecogenicidad cortical bilateral compatible con nefropatia cronica. Sin dila'
            'tacion pielocalicea. Sin litiasis.'
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
    """ Based on live/ar/ar-ehcos.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_PROV')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='EHCOS')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260321110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB40002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC200001', cx_4='HOSP_RAWSON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BUSTOS', xpn_2='DANIEL', xpn_3='ALEJANDRO')
        pid.date_time_of_birth = '19780520'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='NEFRO', pl_4='HOSP_RAWSON')

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
        orc.placer_order_number = EI(ei_1='SOL30003', ei_2='EHCOS')
        orc.filler_order_number = EI(ei_1='RES50002', ei_2='LAB_PROV')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL30003', ei_2='EHCOS')
        obr.filler_order_number = EI(ei_1='RES50002', ei_2='LAB_PROV')
        obr.universal_service_identifier = CWE(cwe_1='34555-3', cwe_2='Panel renal', cwe_3='LN')
        obr.observation_date_time = '20260321070000'
        obr.obr_14 = 'MED204^AGUIRRE^PABLO^^^Dr.'
        obr.filler_field_1 = '20260321103000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinina serica', cwe_3='LN')
        obx.obx_5 = '1.5'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '0.7-1.3'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_2.obx_5 = '58'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '10-50'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='33914-3', cwe_2='Tasa de filtracion glomerular estimada', cwe_3='LN')
        obx_3.obx_5 = '52'
        obx_3.units = CWE(cwe_1='mL/min/1.73m2')
        obx_3.reference_range = '>60'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2889-4', cwe_2='Proteina orina 24h', cwe_3='LN')
        obx_4.obx_5 = '450'
        obx_4.units = CWE(cwe_1='mg/24h')
        obx_4.reference_range = '0-150'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='14959-1', cwe_2='Microalbuminuria', cwe_3='LN')
        obx_5.obx_5 = '85'
        obx_5.units = CWE(cwe_1='mg/L')
        obx_5.reference_range = '0-30'
        obx_5.interpretation_codes = CWE(cwe_1='H')
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
    """ Based on live/ar/ar-ehcos.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHCOS')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='TURNOS')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260322100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'EHC00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='TUR70001', ei_2='EHCOS')
        sch.filler_appointment_id = EI(ei_1='TUR70001', ei_2='EHCOS')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Rutina', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='CONTROL', cwe_2='Control nefrologia', cwe_3='LOCAL')
        sch.sch_9 = '20'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^20^202604051000^202604051020'
        sch.filler_contact_person = XCN(xcn_1='MED204', xcn_2='AGUIRRE', xcn_3='PABLO', xcn_6='Dr.')
        sch.filler_contact_phone_number = XTN(xtn_3='PH', xtn_4='03514567890')
        sch.filler_contact_address = XAD(xad_1='CONSUL', xad_2='NEFRO', xad_4='HOSP_RAWSON')
        sch.entered_by_person = XCN(xcn_1='Confirmado')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC200001', cx_4='HOSP_RAWSON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BUSTOS', xpn_2='DANIEL', xpn_3='ALEJANDRO')
        pid.date_time_of_birth = '19780520'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='NEFRO', pl_4='HOSP_RAWSON')
        pv1.attending_doctor = XCN(xcn_1='MED204', xcn_2='AGUIRRE', xcn_3='PABLO', xcn_6='Dr.')

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
        ais.universal_service_identifier = CWE(cwe_1='NEFRO', cwe_2='Nefrologia', cwe_3='LOCAL')
        ais.start_date_time_offset_units = CNE(cne_1='202604051000')
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
        aip.personnel_resource_id = XCN(xcn_1='MED204', xcn_2='AGUIRRE', xcn_3='PABLO', xcn_6='Dr.')
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
    """ Based on live/ar/ar-ehcos.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHCOS')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='FARMACIA')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260311083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EHC00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC200001', cx_4='HOSP_RAWSON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BUSTOS', xpn_2='DANIEL', xpn_3='ALEJANDRO')
        pid.date_time_of_birth = '19780520'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLMED', pl_2='HAB102', pl_3='CAMA1', pl_4='HOSP_RAWSON')
        pv1.attending_doctor = XCN(xcn_1='MED201', xcn_2='GIMENEZ', xcn_3='ESTELA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='RX002001', ei_2='EHCOS')
        orc.placer_order_group_number = EI(ei_1='GRP003', ei_2='EHCOS')
        orc.date_time_of_order_event = '20260311083000'
        orc.orc_12 = 'MED201^GIMENEZ^ESTELA^^^Dra.'

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='1')
        rxo.requested_give_amount_minimum = '27658^Losartan 50mg^VADEMECUM'
        rxo.requested_give_units = CWE(cwe_1='50')
        rxo.requested_dosage_form = CWE(cwe_1='mg')
        rxo.providers_pharmacy_treatment_instructions = CWE(cwe_1='TAB', cwe_2='Comprimido', cwe_3='HL70323')
        rxo.number_of_refills = '1'
        rxo.pharmacist_treatment_suppliers_verifier_id = XCN(xcn_1='0')
        rxo.requested_give_strength = '20260311083000'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Administrar cada 12 hs. Control de presion arterial y funcion renal.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo, rxr, nte]

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
    """ Based on live/ar/ar-ehcos.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_PROV')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='EHCOS')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260318144000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB40003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC200001', cx_4='HOSP_RAWSON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BUSTOS', xpn_2='DANIEL', xpn_3='ALEJANDRO')
        pid.date_time_of_birth = '19780520'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLMED', pl_2='HAB102', pl_3='CAMA1', pl_4='HOSP_RAWSON')

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
        orc.placer_order_number = EI(ei_1='SOL30001', ei_2='EHCOS')
        orc.filler_order_number = EI(ei_1='RES50003', ei_2='LAB_PROV')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL30001', ei_2='EHCOS')
        obr.filler_order_number = EI(ei_1='RES50003', ei_2='LAB_PROV')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Hemograma completo', cwe_3='LN')
        obr.observation_date_time = '20260318074500'
        obr.obr_14 = 'MED201^GIMENEZ^ESTELA^^^Dra.'
        obr.filler_field_1 = '20260318141000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobina', cwe_3='LN')
        obx.obx_5 = '10.2'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '13.0-17.0'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrito', cwe_3='LN')
        obx_2.obx_5 = '31.5'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '39.0-49.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='789-8', cwe_2='Eritrocitos', cwe_3='LN')
        obx_3.obx_5 = '3.45'
        obx_3.units = CWE(cwe_1='x10E6/uL')
        obx_3.reference_range = '4.30-5.70'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocitos', cwe_3='LN')
        obx_4.obx_5 = '6.8'
        obx_4.units = CWE(cwe_1='x10E3/uL')
        obx_4.reference_range = '4.5-11.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Plaquetas', cwe_3='LN')
        obx_5.obx_5 = '195'
        obx_5.units = CWE(cwe_1='x10E3/uL')
        obx_5.reference_range = '150-400'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Anemia normocitica normocromica. Correlacionar con funcion renal.'

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
    """ Based on live/ar/ar-ehcos.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHCOS')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='CAMAS')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260312150000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'EHC00013'
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
        pid.patient_identifier_list = [CX(cx_1='HC200001', cx_4='HOSP_RAWSON', cx_5='MR'), CX(cx_1='DNI-26789012', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='BUSTOS', xpn_2='DANIEL', xpn_3='ALEJANDRO')
        pid.date_time_of_birth = '19780520'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEFRO', pl_2='HAB205', pl_3='CAMA1', pl_4='HOSP_RAWSON')
        pv1.attending_doctor = XCN(xcn_1='MED204', xcn_2='AGUIRRE', xcn_3='PABLO', xcn_6='Dr.')
        pv1.account_status = CWE(cwe_1='CLMED', cwe_2='HAB102', cwe_3='CAMA1', cwe_4='HOSP_RAWSON')
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
    """ Based on live/ar/ar-ehcos.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ANAT_PAT')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='EHCOS')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260325160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AP30001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC200001', cx_4='HOSP_RAWSON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BUSTOS', xpn_2='DANIEL', xpn_3='ALEJANDRO')
        pid.date_time_of_birth = '19780520'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEFRO', pl_2='HAB205', pl_3='CAMA1', pl_4='HOSP_RAWSON')

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
        orc.placer_order_number = EI(ei_1='SOL30004', ei_2='EHCOS')
        orc.filler_order_number = EI(ei_1='AP50001', ei_2='ANAT_PAT')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL30004', ei_2='EHCOS')
        obr.filler_order_number = EI(ei_1='AP50001', ei_2='ANAT_PAT')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='Biopsia renal', cwe_3='CPT')
        obr.observation_date_time = '20260322100000'
        obr.obr_14 = 'MED204^AGUIRRE^PABLO^^^Dr.'
        obr.filler_field_1 = '20260325153000'
        obr.results_rpt_status_chng_date_time = 'AP'
        obr.charge_to_practice = MOC(moc_1='F')
        obr.transportation_mode = 'MED206^LUCERO^GABRIEL^^^Dr.'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='88305&IMP', cwe_2='Biopsia renal impresion', cwe_3='CPT')
        obx.obx_5 = (
            'Nefropatia membranosa estadio II. Engrosamiento difuso de membranas basales glomerulares con depositos subepiteliales. Fibrosis intersticial'
            ' leve (15%). Inmunofluorescencia positiva para IgG y C3 en patron granular.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Informe biopsia renal', cwe_3='AUSPDI')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'EHCOS^AP^^Base64^'
            'JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0Nv'
            'dW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8'
            'PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAzMjAgPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQooSW5m'
            'b3JtZSBkZSBCaW9wc2lhIFJlbmFsKSBUagowIC0yMCBUZAooUGFjaWVudGU6IEJ1c3RvcywgRGFuaWVsIEFsZWphbmRybykgVGoKMCAtMjAgVGQKKEhDIDIwMDAwMSAtIEhvc3BpdGFs'
            'IFJhd3NvbikgVGoKMCAtMjAgVGQKKERpYWdub3N0aWNvOiBOZWZyb3BhdGlhIG1lbWJyYW5vc2EgZXN0YWRpbyBJSSkgVGoKMCAtMjAgVGQKKEVuZ3Jvc2FtaWVudG8gZGlmdXNvIGRl'
            'IG1lbWJyYW5hcyBiYXNhbGVzKSBUagowIC0yMCBUZAooRmlicm9zaXMgaW50ZXJzdGljaWFsIGxldmUgMTUlKSBUagowIC0yMCBUZAooSUYgcG9zaXRpdmEgcGFyYSBJZ0cgeSBDMykg'
            'VGoKMCAtMjAgVGQKKERyLiBHYWJyaWVsIEx1Y2VybyAtIEFuYXRvbWlhIFBhdG9sb2dpY2EpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3Vi'
            'dHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAw'
            'MDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNjc4IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFy'
            'dHhyZWYKNzU5CiUlRU9GCg=='
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
    """ Based on live/ar/ar-ehcos.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ANAT_PAT')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='EHCOS')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260325161000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AP30002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC200001', cx_4='HOSP_RAWSON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BUSTOS', xpn_2='DANIEL', xpn_3='ALEJANDRO')
        pid.date_time_of_birth = '19780520'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEFRO', pl_2='HAB205', pl_3='CAMA1', pl_4='HOSP_RAWSON')

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
        orc.placer_order_number = EI(ei_1='SOL30004', ei_2='EHCOS')
        orc.filler_order_number = EI(ei_1='AP50002', ei_2='ANAT_PAT')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL30004', ei_2='EHCOS')
        obr.filler_order_number = EI(ei_1='AP50002', ei_2='ANAT_PAT')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='Biopsia renal microscopia', cwe_3='CPT')
        obr.observation_date_time = '20260322100000'
        obr.obr_14 = 'MED204^AGUIRRE^PABLO^^^Dr.'
        obr.filler_field_1 = '20260325155000'
        obr.results_rpt_status_chng_date_time = 'AP'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='88305&MIC', cwe_2='Microscopia descripcion', cwe_3='CPT')
        obx.obx_5 = 'Glomeros con engrosamiento difuso de MBG y espigas subepiteliales. Tubulos con atrofia focal. Intersticio con fibrosis leve.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Microscopia renal imagen', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'EHCOS^IMAGE^PNG^Base64^'
            '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'
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
    """ Based on live/ar/ar-ehcos.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHCOS')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='MPI_PROV')
        msh.receiving_facility = HD(hd_1='GOB_CBA')
        msh.date_time_of_message = '20260326080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'EHC00016'
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
        pid.patient_identifier_list = [CX(cx_1='HC200200', cx_4='HOSP_RAWSON', cx_5='MR'), CX(cx_1='DNI-44567890', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='AREVALO', xpn_2='CAMILA', xpn_3='MICAELA', xpn_5='Sra.')
        pid.date_time_of_birth = '19990315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Colon 1500', xad_3='Cordoba', xad_4='Cordoba', xad_5='X5000', xad_6='AR')
        pid.pid_13 = '^^CP^03518901234~^^Internet^carevalo@gmail.com'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='AREVALO', xpn_2='JORGE', xpn_4='Sr.')
        nk1.relationship = CWE(cwe_1='FTH', cwe_2='Padre', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Av. Colon 1500', xad_3='Cordoba', xad_4='Cordoba', xad_5='X5000', xad_6='AR')
        nk1.nk1_5 = '^^PH^03514567890'

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
    """ Based on live/ar/ar-ehcos.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHCOS')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='LAB_PROV')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260327074500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EHC00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC200100', cx_4='HOSP_RAWSON', cx_5='MR'), CX(cx_1='DNI-33456789', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='PEREYRA', xpn_2='ROMINA', xpn_3='SOLEDAD')
        pid.date_time_of_birth = '19890612'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='END01', pl_4='HOSP_RAWSON')
        pv1.attending_doctor = XCN(xcn_1='MED203', xcn_2='VILLEGAS', xcn_3='CAROLINA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL30005', ei_2='EHCOS')
        orc.placer_order_group_number = EI(ei_1='GRP005', ei_2='EHCOS')
        orc.date_time_of_order_event = '20260327074500'
        orc.orc_12 = 'MED203^VILLEGAS^CAROLINA^^^Dra.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL30005', ei_2='EHCOS')
        obr.universal_service_identifier = CWE(cwe_1='83519', cwe_2='TSH', cwe_3='CPT')
        obr.observation_date_time = '20260327074500'
        obr.obr_16 = 'MED203^VILLEGAS^CAROLINA^^^Dra.'
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
        obr_2.placer_order_number = EI(ei_1='SOL30005', ei_2='EHCOS')
        obr_2.universal_service_identifier = CWE(cwe_1='84439', cwe_2='T4 libre', cwe_3='CPT')
        obr_2.observation_date_time = '20260327074500'
        obr_2.obr_16 = 'MED203^VILLEGAS^CAROLINA^^^Dra.'
        obr_2.obr_27 = '^RUTINA'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E03.9', cwe_2='Hipotiroidismo, no especificado', cwe_3='I10')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, dg1]

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
    """ Based on live/ar/ar-ehcos.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_PROV')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='EHCOS')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260327140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB40004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC200100', cx_4='HOSP_RAWSON', cx_5='MR')
        pid.patient_name = XPN(xpn_1='PEREYRA', xpn_2='ROMINA', xpn_3='SOLEDAD')
        pid.date_time_of_birth = '19890612'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='END01', pl_4='HOSP_RAWSON')

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
        orc.placer_order_number = EI(ei_1='SOL30005', ei_2='EHCOS')
        orc.filler_order_number = EI(ei_1='RES50004', ei_2='LAB_PROV')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL30005', ei_2='EHCOS')
        obr.filler_order_number = EI(ei_1='RES50004', ei_2='LAB_PROV')
        obr.universal_service_identifier = CWE(cwe_1='83519', cwe_2='TSH', cwe_3='CPT')
        obr.observation_date_time = '20260327074500'
        obr.obr_14 = 'MED203^VILLEGAS^CAROLINA^^^Dra.'
        obr.filler_field_1 = '20260327133000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '8.5'
        obx.units = CWE(cwe_1='mUI/L')
        obx.reference_range = '0.4-4.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='T4 libre', cwe_3='LN')
        obx_2.obx_5 = '0.7'
        obx_2.units = CWE(cwe_1='ng/dL')
        obx_2.reference_range = '0.8-1.8'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'TSH elevada con T4L baja. Compatible con hipotiroidismo primario.'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2
        observation_2.nte = nte

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
    """ Based on live/ar/ar-ehcos.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHCOS')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='MPI_PROV')
        msh.receiving_facility = HD(hd_1='GOB_CBA')
        msh.date_time_of_message = '20260328090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'EHC00019'
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
        pid.patient_identifier_list = [CX(cx_1='HC200001', cx_4='HOSP_RAWSON', cx_5='MR'), CX(cx_1='DNI-26789012', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='BUSTOS', xpn_2='DANIEL', xpn_3='ALEJANDRO')
        pid.date_time_of_birth = '19780520'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Dean Funes 500', xad_3='Cordoba', xad_4='Cordoba', xad_5='X5000', xad_6='AR')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='HC200999', cx_4='HOSP_RAWSON', cx_5='MR')
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
    """ Based on live/ar/ar-ehcos.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_PROV')
        msh.sending_facility = HD(hd_1='HOSP_RAWSON')
        msh.receiving_application = HD(hd_1='EHCOS')
        msh.receiving_facility = HD(hd_1='HOSP_RAWSON')
        msh.date_time_of_message = '20260318074600'
        msh.message_type = MSG(msg_1='ACK', msg_2='O01', msg_3='ACK')
        msh.message_control_id = 'ACK70001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'CA'
        msa.message_control_id = 'EHC00004'
        msa.msa_3 = 'Orden recibida correctamente'

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
