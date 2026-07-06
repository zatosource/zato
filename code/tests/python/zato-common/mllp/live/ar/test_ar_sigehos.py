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
from zato.hl7v2.v2_9.segments import AIP, AIS, DG1, EVN, IN1, MRG, MSA, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, RGS, SCH

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ar', 'ar-sigehos.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ar/ar-sigehos.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIGEHOS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='LAB_SIS')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260310080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'SGH00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260310080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC112345', cx_4='HOSP_DURAND', cx_5='MR'), CX(cx_1='DNI-27890123', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='MOLINA', xpn_2='CARLOS', xpn_3='ALBERTO', xpn_5='Sr.')
        pid.date_time_of_birth = '19770614'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Diaz Velez 5044', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1405DCD', xad_6='AR')
        pid.pid_13 = '^^PH^01149827500~^^CP^01156789012'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLMED', pl_2='HAB205', pl_3='CAMA2', pl_4='HOSP_DURAND')
        pv1.attending_doctor = XCN(xcn_1='MED101', xcn_2='SANCHEZ', xcn_3='MARIA', xcn_6='Dra.')
        pv1.consulting_doctor = XCN(xcn_1='MED102', xcn_2='NAVARRO', xcn_3='JORGE', xcn_6='Dr.')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.visit_number = CX(cx_1='ENC112345')
        pv1.pending_location = PL(pl_1='GUARD', pl_2='BOX02', pl_4='HOSP_DURAND')
        pv1.admit_date_time = '20260310080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='OS003')
        in1.insurance_company_name = XON(xon_1='PAMI')
        in1.insurance_company_address = XAD(xad_1='Peru 169', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1067AAC', xad_6='AR')

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
    """ Based on live/ar/ar-sigehos.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIGEHOS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='LAB_SIS')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260317140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'SGH00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260317140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC112345', cx_4='HOSP_DURAND', cx_5='MR'), CX(cx_1='DNI-27890123', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='MOLINA', xpn_2='CARLOS', xpn_3='ALBERTO', xpn_5='Sr.')
        pid.date_time_of_birth = '19770614'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Diaz Velez 5044', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1405DCD', xad_6='AR')
        pid.pid_13 = '^^CP^01156789012'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLMED', pl_2='HAB205', pl_3='CAMA2', pl_4='HOSP_DURAND')
        pv1.attending_doctor = XCN(xcn_1='MED101', xcn_2='SANCHEZ', xcn_3='MARIA', xcn_6='Dra.')
        pv1.consulting_doctor = XCN(xcn_1='MED102', xcn_2='NAVARRO', xcn_3='JORGE', xcn_6='Dr.')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.visit_number = CX(cx_1='ENC112345')
        pv1.charge_price_indicator = CWE(cwe_1='20260317140000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K29.7', cwe_2='Gastritis, no especificada', cwe_3='I10')

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
    """ Based on live/ar/ar-sigehos.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIGEHOS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='TRIAGE')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260318220000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'SGH00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260318220000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC223456', cx_4='HOSP_DURAND', cx_5='MR'), CX(cx_1='DNI-38901234', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='TORRES', xpn_2='LUCIA', xpn_3='VALENTINA', xpn_5='Sra.')
        pid.date_time_of_birth = '19940315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Yerbal 1500', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1406GLJ', xad_6='AR')
        pid.pid_13 = '^^CP^01167890123'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='GUARD', pl_2='BOX05', pl_4='HOSP_DURAND')
        pv1.attending_doctor = XCN(xcn_1='MED103', xcn_2='CASTRO', xcn_3='PABLO', xcn_6='Dr.')
        pv1.total_payments = '20260318220000'

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
    """ Based on live/ar/ar-sigehos.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIGEHOS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='MPI_CABA')
        msh.receiving_facility = HD(hd_1='DGSISIN')
        msh.date_time_of_message = '20260319100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'SGH00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260319100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC112345', cx_4='HOSP_DURAND', cx_5='MR'), CX(cx_1='DNI-27890123', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='MOLINA', xpn_2='CARLOS', xpn_3='ALBERTO', xpn_5='Sr.')
        pid.date_time_of_birth = '19770614'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Rivadavia 8900', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1407FEF', xad_6='AR')
        pid.pid_13 = '^^PH^01146001234~^^CP^01156789012~^^Internet^cmolina@hotmail.com'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='C101', pl_4='HOSP_DURAND')
        pv1.attending_doctor = XCN(xcn_1='MED101', xcn_2='SANCHEZ', xcn_3='MARIA', xcn_6='Dra.')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='OS003')
        in1.insurance_company_name = XON(xon_1='PAMI')
        in1.insurance_company_address = XAD(xad_1='Peru 169', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1067AAC', xad_6='AR')

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
    """ Based on live/ar/ar-sigehos.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIGEHOS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='LAB_SIS')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260320070000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SGH00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC112345', cx_4='HOSP_DURAND', cx_5='MR')
        pid.patient_name = XPN(xpn_1='MOLINA', xpn_2='CARLOS', xpn_3='ALBERTO')
        pid.date_time_of_birth = '19770614'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLMED', pl_2='HAB205', pl_3='CAMA2', pl_4='HOSP_DURAND')
        pv1.attending_doctor = XCN(xcn_1='MED101', xcn_2='SANCHEZ', xcn_3='MARIA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL20001', ei_2='SIGEHOS')
        orc.placer_order_group_number = EI(ei_1='GRP001', ei_2='SIGEHOS')
        orc.date_time_of_order_event = '20260320070000'
        orc.orc_12 = 'MED101^SANCHEZ^MARIA^^^Dra.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL20001', ei_2='SIGEHOS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Panel metabolico basico', cwe_3='LN')
        obr.observation_date_time = '20260320070000'
        obr.obr_16 = 'MED101^SANCHEZ^MARIA^^^Dra.'
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
        obr_2.placer_order_number = EI(ei_1='SOL20001', ei_2='SIGEHOS')
        obr_2.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Hemograma completo', cwe_3='LN')
        obr_2.observation_date_time = '20260320070000'
        obr_2.obr_16 = 'MED101^SANCHEZ^MARIA^^^Dra.'
        obr_2.obr_27 = '^RUTINA'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K29.7', cwe_2='Gastritis, no especificada', cwe_3='I10')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, dg1]

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
    """ Based on live/ar/ar-sigehos.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SIS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='SIGEHOS')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260320140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB30001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC112345', cx_4='HOSP_DURAND', cx_5='MR')
        pid.patient_name = XPN(xpn_1='MOLINA', xpn_2='CARLOS', xpn_3='ALBERTO')
        pid.date_time_of_birth = '19770614'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLMED', pl_2='HAB205', pl_3='CAMA2', pl_4='HOSP_DURAND')

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
        orc.placer_order_number = EI(ei_1='SOL20001', ei_2='SIGEHOS')
        orc.filler_order_number = EI(ei_1='RES40001', ei_2='LAB_SIS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL20001', ei_2='SIGEHOS')
        obr.filler_order_number = EI(ei_1='RES40001', ei_2='LAB_SIS')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Hemograma completo', cwe_3='LN')
        obr.observation_date_time = '20260320070000'
        obr.obr_14 = 'MED101^SANCHEZ^MARIA^^^Dra.'
        obr.filler_field_1 = '20260320132000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobina', cwe_3='LN')
        obx.obx_5 = '14.5'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '13.0-17.0'
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
        obx_2.obx_5 = '43.2'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '39.0-49.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='789-8', cwe_2='Eritrocitos', cwe_3='LN')
        obx_3.obx_5 = '4.85'
        obx_3.units = CWE(cwe_1='x10E6/uL')
        obx_3.reference_range = '4.30-5.70'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocitos', cwe_3='LN')
        obx_4.obx_5 = '8.9'
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
        obx_5.obx_5 = '210'
        obx_5.units = CWE(cwe_1='x10E3/uL')
        obx_5.reference_range = '150-400'
        obx_5.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/ar/ar-sigehos.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SIS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='SIGEHOS')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260320141000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB30002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC112345', cx_4='HOSP_DURAND', cx_5='MR')
        pid.patient_name = XPN(xpn_1='MOLINA', xpn_2='CARLOS', xpn_3='ALBERTO')
        pid.date_time_of_birth = '19770614'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLMED', pl_2='HAB205', pl_3='CAMA2', pl_4='HOSP_DURAND')

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
        orc.placer_order_number = EI(ei_1='SOL20001', ei_2='SIGEHOS')
        orc.filler_order_number = EI(ei_1='RES40002', ei_2='LAB_SIS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL20001', ei_2='SIGEHOS')
        obr.filler_order_number = EI(ei_1='RES40002', ei_2='LAB_SIS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Panel metabolico basico', cwe_3='LN')
        obr.observation_date_time = '20260320070000'
        obr.obr_14 = 'MED101^SANCHEZ^MARIA^^^Dra.'
        obr.filler_field_1 = '20260320133000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucosa', cwe_3='LN')
        obx.obx_5 = '102'
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
        obx_2.obx_5 = '1.0'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.7-1.3'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_3.obx_5 = '42'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '10-50'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST (TGO)', cwe_3='LN')
        obx_4.obx_5 = '28'
        obx_4.units = CWE(cwe_1='U/L')
        obx_4.reference_range = '5-40'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT (TGP)', cwe_3='LN')
        obx_5.obx_5 = '35'
        obx_5.units = CWE(cwe_1='U/L')
        obx_5.reference_range = '7-56'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Bilirrubina total', cwe_3='LN')
        obx_6.obx_5 = '0.8'
        obx_6.units = CWE(cwe_1='mg/dL')
        obx_6.reference_range = '0.1-1.2'
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
    """ Based on live/ar/ar-sigehos.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIGEHOS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='RIS_PACS')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260321090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SGH00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC334567', cx_4='HOSP_DURAND', cx_5='MR'), CX(cx_1='DNI-25678901', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='RAMIREZ', xpn_2='MARTIN', xpn_3='OSCAR')
        pid.date_time_of_birth = '19730228'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='GUARD', pl_2='BOX03', pl_4='HOSP_DURAND')
        pv1.attending_doctor = XCN(xcn_1='MED103', xcn_2='CASTRO', xcn_3='PABLO', xcn_6='Dr.')

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
        orc.placer_order_number = EI(ei_1='SOL20002', ei_2='SIGEHOS')
        orc.placer_order_group_number = EI(ei_1='GRP002', ei_2='SIGEHOS')
        orc.date_time_of_order_event = '20260321090000'
        orc.orc_12 = 'MED103^CASTRO^PABLO^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL20002', ei_2='SIGEHOS')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Radiografia de torax', cwe_3='CPT')
        obr.observation_date_time = '20260321090000'
        obr.obr_16 = 'MED103^CASTRO^PABLO^^^Dr.'
        obr.obr_27 = '^URGENTE'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R06.0', cwe_2='Disnea', cwe_3='I10')

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
        nte.comment = 'Paciente con disnea subita. Descartar neumotorax.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/ar/ar-sigehos.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_PACS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='SIGEHOS')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260321120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD20001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC334567', cx_4='HOSP_DURAND', cx_5='MR')
        pid.patient_name = XPN(xpn_1='RAMIREZ', xpn_2='MARTIN', xpn_3='OSCAR')
        pid.date_time_of_birth = '19730228'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='GUARD', pl_2='BOX03', pl_4='HOSP_DURAND')
        pv1.attending_doctor = XCN(xcn_1='MED103', xcn_2='CASTRO', xcn_3='PABLO', xcn_6='Dr.')

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
        orc.placer_order_number = EI(ei_1='SOL20002', ei_2='SIGEHOS')
        orc.filler_order_number = EI(ei_1='INF60001', ei_2='RIS_PACS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL20002', ei_2='SIGEHOS')
        obr.filler_order_number = EI(ei_1='INF60001', ei_2='RIS_PACS')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Radiografia de torax', cwe_3='CPT')
        obr.observation_date_time = '20260321090000'
        obr.obr_14 = 'MED103^CASTRO^PABLO^^^Dr.'
        obr.filler_field_1 = '20260321113000'
        obr.results_rpt_status_chng_date_time = 'RAD'
        obr.charge_to_practice = MOC(moc_1='F')
        obr.transportation_mode = 'MED104^HERRERA^DANIELA^^^Dra.'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='71020&IMP', cwe_2='Rx torax impresion', cwe_3='CPT')
        obx.obx_5 = (
            'Campos pulmonares expandidos sin condensaciones. Senos costodiafragmaticos libres. Silueta cardiaca de tamano normal. Sin evidencia de neumo'
            'torax.'
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
    """ Based on live/ar/ar-sigehos.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIGEHOS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='TURNOS')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260322100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'SGH00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='TUR60001', ei_2='SIGEHOS')
        sch.filler_appointment_id = EI(ei_1='TUR60001', ei_2='SIGEHOS')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Rutina', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='CONSUL', cwe_2='Consulta', cwe_3='LOCAL')
        sch.sch_9 = '20'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^20^202604011430^202604011450'
        sch.filler_contact_person = XCN(xcn_1='MED101', xcn_2='SANCHEZ', xcn_3='MARIA', xcn_6='Dra.')
        sch.filler_contact_phone_number = XTN(xtn_3='PH', xtn_4='01149827500')
        sch.filler_contact_address = XAD(xad_1='CONSUL', xad_2='C101', xad_4='HOSP_DURAND')
        sch.entered_by_person = XCN(xcn_1='Confirmado')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC112345', cx_4='HOSP_DURAND', cx_5='MR')
        pid.patient_name = XPN(xpn_1='MOLINA', xpn_2='CARLOS', xpn_3='ALBERTO')
        pid.date_time_of_birth = '19770614'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='C101', pl_4='HOSP_DURAND')
        pv1.attending_doctor = XCN(xcn_1='MED101', xcn_2='SANCHEZ', xcn_3='MARIA', xcn_6='Dra.')

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
        ais.universal_service_identifier = CWE(cwe_1='GASTRO', cwe_2='Gastroenterologia', cwe_3='LOCAL')
        ais.start_date_time_offset_units = CNE(cne_1='202604011430')
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
        aip.personnel_resource_id = XCN(xcn_1='MED101', xcn_2='SANCHEZ', xcn_3='MARIA', xcn_6='Dra.')
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
    """ Based on live/ar/ar-sigehos.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIGEHOS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='LAB_SIS')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260323020000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SGH00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC445678', cx_4='HOSP_DURAND', cx_5='MR'), CX(cx_1='DNI-32456789', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='LUNA', xpn_2='AGUSTINA', xpn_3='SOLEDAD')
        pid.date_time_of_birth = '19880915'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='HAB001', pl_3='CAMA3', pl_4='HOSP_DURAND')
        pv1.attending_doctor = XCN(xcn_1='MED105', xcn_2='PERALTA', xcn_3='HUGO', xcn_6='Dr.')

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
        orc.placer_order_number = EI(ei_1='SOL20003', ei_2='SIGEHOS')
        orc.placer_order_group_number = EI(ei_1='GRP003', ei_2='SIGEHOS')
        orc.date_time_of_order_event = '20260323020000'
        orc.orc_12 = 'MED105^PERALTA^HUGO^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL20003', ei_2='SIGEHOS')
        obr.universal_service_identifier = CWE(cwe_1='600-7', cwe_2='Hemocultivo', cwe_3='LN')
        obr.observation_date_time = '20260323020000'
        obr.obr_16 = 'MED105^PERALTA^HUGO^^^Dr.'
        obr.obr_27 = '^URGENTE'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='A41.9', cwe_2='Sepsis, no especificada', cwe_3='I10')

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
        nte.comment = 'Paciente en ARM con fiebre 39.8C. Tomar 2 muestras aerobicas y 1 anaerobica.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/ar/ar-sigehos.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SIS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='SIGEHOS')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260323043000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB30003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC445678', cx_4='HOSP_DURAND', cx_5='MR')
        pid.patient_name = XPN(xpn_1='LUNA', xpn_2='AGUSTINA', xpn_3='SOLEDAD')
        pid.date_time_of_birth = '19880915'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='HAB001', pl_3='CAMA3', pl_4='HOSP_DURAND')

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
        orc.placer_order_number = EI(ei_1='SOL20004', ei_2='SIGEHOS')
        orc.filler_order_number = EI(ei_1='RES40003', ei_2='LAB_SIS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL20004', ei_2='SIGEHOS')
        obr.filler_order_number = EI(ei_1='RES40003', ei_2='LAB_SIS')
        obr.universal_service_identifier = CWE(cwe_1='24336-0', cwe_2='Gases en sangre arterial', cwe_3='LN')
        obr.observation_date_time = '20260323040000'
        obr.obr_14 = 'MED105^PERALTA^HUGO^^^Dr.'
        obr.filler_field_1 = '20260323042000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='pH arterial', cwe_3='LN')
        obx.obx_5 = '7.32'
        obx.units = CWE(cwe_1='pH')
        obx.reference_range = '7.35-7.45'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='pCO2', cwe_3='LN')
        obx_2.obx_5 = '52'
        obx_2.units = CWE(cwe_1='mmHg')
        obx_2.reference_range = '35-45'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2703-7', cwe_2='pO2', cwe_3='LN')
        obx_3.obx_5 = '68'
        obx_3.units = CWE(cwe_1='mmHg')
        obx_3.reference_range = '80-100'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1959-6', cwe_2='Bicarbonato', cwe_3='LN')
        obx_4.obx_5 = '26'
        obx_4.units = CWE(cwe_1='mEq/L')
        obx_4.reference_range = '22-26'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2708-6', cwe_2='Saturacion O2', cwe_3='LN')
        obx_5.obx_5 = '91'
        obx_5.units = CWE(cwe_1='%')
        obx_5.reference_range = '95-100'
        obx_5.interpretation_codes = CWE(cwe_1='L')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1960-4', cwe_2='Exceso de base', cwe_3='LN')
        obx_6.obx_5 = '-2'
        obx_6.units = CWE(cwe_1='mEq/L')
        obx_6.reference_range = '-2-2'
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
    """ Based on live/ar/ar-sigehos.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIGEHOS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='CAMAS')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260323010000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'SGH00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260323010000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC445678', cx_4='HOSP_DURAND', cx_5='MR'), CX(cx_1='DNI-32456789', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='LUNA', xpn_2='AGUSTINA', xpn_3='SOLEDAD')
        pid.date_time_of_birth = '19880915'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='HAB001', pl_3='CAMA3', pl_4='HOSP_DURAND')
        pv1.attending_doctor = XCN(xcn_1='MED105', xcn_2='PERALTA', xcn_3='HUGO', xcn_6='Dr.')
        pv1.account_status = CWE(cwe_1='CLMED', cwe_2='HAB310', cwe_3='CAMA1', cwe_4='HOSP_DURAND')
        pv1.prior_temporary_location = PL(pl_1='20260323010000')

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
    """ Based on live/ar/ar-sigehos.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_PACS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='SIGEHOS')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260324150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD20002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC556789', cx_4='HOSP_DURAND', cx_5='MR'), CX(cx_1='DNI-29012345', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='VARGAS', xpn_2='DIEGO', xpn_3='SEBASTIAN')
        pid.date_time_of_birth = '19790810'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CIRUGIA', pl_2='HAB402', pl_3='CAMA1', pl_4='HOSP_DURAND')
        pv1.attending_doctor = XCN(xcn_1='MED106', xcn_2='COLOMBO', xcn_3='ANDREA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL20005', ei_2='SIGEHOS')
        orc.filler_order_number = EI(ei_1='INF60002', ei_2='RIS_PACS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL20005', ei_2='SIGEHOS')
        obr.filler_order_number = EI(ei_1='INF60002', ei_2='RIS_PACS')
        obr.universal_service_identifier = CWE(cwe_1='74177', cwe_2='TC abdomen y pelvis con contraste', cwe_3='CPT')
        obr.observation_date_time = '20260324100000'
        obr.obr_14 = 'MED106^COLOMBO^ANDREA^^^Dra.'
        obr.filler_field_1 = '20260324143000'
        obr.results_rpt_status_chng_date_time = 'RAD'
        obr.charge_to_practice = MOC(moc_1='F')
        obr.transportation_mode = 'MED104^HERRERA^DANIELA^^^Dra.'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='74177&IMP', cwe_2='TC abdomen impresion', cwe_3='CPT')
        obx.obx_5 = (
            'Higado de tamano normal sin lesiones focales. Vesicula biliar con litiasis multiple. Pancreas, bazo y rinones sin alteraciones. Sin liquido '
            'libre peritoneal. Sin adenopatias retroperitoneales.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Informe TC abdomen completo', cwe_3='AUSPDI')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'SIGEHOS^AP^^Base64^'
            'JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0Nv'
            'dW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8'
            'PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyODAgPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQooSW5m'
            'b3JtZSBUb21vZ3JhZmlhIENvbXB1dGFkYSBkZSBBYmRvbWVuIHkgUGVsdmlzKSBUagowIC0yMCBUZAooUGFjaWVudGU6IFZhcmdhcywgRGllZ28gU2ViYXN0aWFuKSBUagowIC0yMCBU'
            'ZAooSEMgNTU2Nzg5IC0gRE5JIDI5MDEyMzQ1KSBUagowIC0yMCBUZAooSGlnYWRvIGRlIHRhbWFubyBub3JtYWwgc2luIGxlc2lvbmVzIGZvY2FsZXMuKSBUagowIC0yMCBUZAooVmVz'
            'aWN1bGEgYmlsaWFyIGNvbiBsaXRpYXNpcyBtdWx0aXBsZS4pIFRqCjAgLTIwIFRkCihGaXJtYTogRHJhLiBEYW5pZWxhIEhlcnJlcmEgLSBEaWFnbm9zdGljbyBwb3IgSW1hZ2VuZXMp'
            'IFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAw'
            'MDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAw'
            'NjM4IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNzE5CiUlRU9GCg=='
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
    """ Based on live/ar/ar-sigehos.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_PACS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='SIGEHOS')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260321121000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD20003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC334567', cx_4='HOSP_DURAND', cx_5='MR')
        pid.patient_name = XPN(xpn_1='RAMIREZ', xpn_2='MARTIN', xpn_3='OSCAR')
        pid.date_time_of_birth = '19730228'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='GUARD', pl_2='BOX03', pl_4='HOSP_DURAND')

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
        orc.placer_order_number = EI(ei_1='SOL20002', ei_2='SIGEHOS')
        orc.filler_order_number = EI(ei_1='INF60003', ei_2='RIS_PACS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL20002', ei_2='SIGEHOS')
        obr.filler_order_number = EI(ei_1='INF60003', ei_2='RIS_PACS')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Radiografia de torax', cwe_3='CPT')
        obr.observation_date_time = '20260321090000'
        obr.obr_14 = 'MED103^CASTRO^PABLO^^^Dr.'
        obr.filler_field_1 = '20260321113000'
        obr.results_rpt_status_chng_date_time = 'RAD'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='71020&IMP', cwe_2='Rx torax impresion', cwe_3='CPT')
        obx.obx_5 = 'Campos pulmonares sin condensaciones. Sin neumotorax.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Rx torax PA imagen', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'SIGEHOS^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgy'
            'IRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCABAAEADASIAAhEBAxEB/8QAGwAAAgMBAQEAAAAAAAAAAAAABAUCAwYHAQj/xAAx'
            'EAACAQMDAwIFAwMFAAAAAAABAgMABBEFEiExQVFhcQYTIoGRFDKhscHhI0JS0fD/xAAYAQADAQEAAAAAAAAAAAAAAAABAgMABP/EACERAAICAgICAwEAAAAAAAAAAAABAhEDIRIxQVET'
            'ImFx/9oADAMBAAIRAxEAPwD6pooooAKKKKACvCQBknAFRlljhjaWV1jjQZZ3OAB7mvnz4w+P5NQlk0vRZmjsVJSW4Q4MvqoPYevc0G0lbGjFydI6J4i+MdE8OBo55/1F4OlrAQzZ9T2X'
            '3NcW8VfHev6+Xhgl/QWTcCKBiGYejN1/FYAknqck9yaSa3rEGkQeZLh5W4jiU8sfX0FclkyeEdsMEV2a2DxHqUcm/9dO5/5Fsj7Gug+BfjR7u4TTNckUSudsN2owr+jj19elfPdFJY8s'
            'HdFpYYSVUfpWiub/BPxj+pEej6xNm4GEt7hzzcDsGPr6+tdIrqjJSVo5JRcXTCiiigRCiiigDC/G/xUvh7SjbWsgGp3SkRYPMSdC/v2H/AHFfNzu8jtJI7O7kszMckk9Sa1HxrcTXPj3'
            'WnuGLMl0YlJ/lRhR9sVlqwUdOx+h6K3/AIJTUv8AT1zRtF0a+sL3Uri0WJ+Nql96hoySeD7de9elNSCk0jfT3OjFcj0UlZgaSa3rEGkQeZNh5W4jiU/Ufb29aKzPxjdzWumW0cOVNxKV'
            'Zh/tAH9yKMpKMbYUOUuKPn8knJJye9eUUVxnpBRRRQB//Z'
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
    """ Based on live/ar/ar-sigehos.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIGEHOS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='RIS_PACS')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260325100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SGH00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC556789', cx_4='HOSP_DURAND', cx_5='MR'), CX(cx_1='DNI-29012345', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='VARGAS', xpn_2='DIEGO', xpn_3='SEBASTIAN')
        pid.date_time_of_birth = '19790810'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CIRUGIA', pl_2='HAB402', pl_3='CAMA1', pl_4='HOSP_DURAND')
        pv1.attending_doctor = XCN(xcn_1='MED106', xcn_2='COLOMBO', xcn_3='ANDREA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL20006', ei_2='SIGEHOS')
        orc.placer_order_group_number = EI(ei_1='GRP004', ei_2='SIGEHOS')
        orc.date_time_of_order_event = '20260325100000'
        orc.orc_12 = 'MED106^COLOMBO^ANDREA^^^Dra.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL20006', ei_2='SIGEHOS')
        obr.universal_service_identifier = CWE(cwe_1='76700', cwe_2='Ecografia abdominal completa', cwe_3='CPT')
        obr.observation_date_time = '20260325100000'
        obr.obr_16 = 'MED106^COLOMBO^ANDREA^^^Dra.'
        obr.obr_27 = '^RUTINA'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.2', cwe_2='Colelitiasis sin obstruccion', cwe_3='I10')

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
        nte.comment = 'Pre-quirurgico para colecistectomia programada.'

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
    """ Based on live/ar/ar-sigehos.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SIS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='SIGEHOS')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260325150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB30004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC556789', cx_4='HOSP_DURAND', cx_5='MR')
        pid.patient_name = XPN(xpn_1='VARGAS', xpn_2='DIEGO', xpn_3='SEBASTIAN')
        pid.date_time_of_birth = '19790810'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CIRUGIA', pl_2='HAB402', pl_3='CAMA1', pl_4='HOSP_DURAND')

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
        orc.placer_order_number = EI(ei_1='SOL20007', ei_2='SIGEHOS')
        orc.filler_order_number = EI(ei_1='RES40004', ei_2='LAB_SIS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL20007', ei_2='SIGEHOS')
        obr.filler_order_number = EI(ei_1='RES40004', ei_2='LAB_SIS')
        obr.universal_service_identifier = CWE(cwe_1='24325-3', cwe_2='Hepatograma', cwe_3='LN')
        obr.observation_date_time = '20260325070000'
        obr.obr_14 = 'MED106^COLOMBO^ANDREA^^^Dra.'
        obr.filler_field_1 = '20260325143000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST (TGO)', cwe_3='LN')
        obx.obx_5 = '25'
        obx.units = CWE(cwe_1='U/L')
        obx.reference_range = '5-40'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT (TGP)', cwe_3='LN')
        obx_2.obx_5 = '30'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '7-56'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Bilirrubina total', cwe_3='LN')
        obx_3.obx_5 = '1.0'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '0.1-1.2'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1968-7', cwe_2='Bilirrubina directa', cwe_3='LN')
        obx_4.obx_5 = '0.3'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '0.0-0.3'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='6768-6', cwe_2='Fosfatasa alcalina', cwe_3='LN')
        obx_5.obx_5 = '85'
        obx_5.units = CWE(cwe_1='U/L')
        obx_5.reference_range = '44-147'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2324-2', cwe_2='GGT', cwe_3='LN')
        obx_6.obx_5 = '45'
        obx_6.units = CWE(cwe_1='U/L')
        obx_6.reference_range = '8-61'
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
    """ Based on live/ar/ar-sigehos.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIGEHOS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='MPI_CABA')
        msh.receiving_facility = HD(hd_1='DGSISIN')
        msh.date_time_of_message = '20260326080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'SGH00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20260326080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC667890', cx_4='HOSP_DURAND', cx_5='MR'), CX(cx_1='DNI-43567890', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='MEDINA', xpn_2='SOFIA', xpn_3='CAROLINA', xpn_5='Sra.')
        pid.date_time_of_birth = '19980220'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Directorio 3400', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1406FZB', xad_6='AR')
        pid.pid_13 = '^^CP^01178901234~^^Internet^smedina@gmail.com'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='MEDINA', xpn_2='ROBERTO', xpn_4='Sr.')
        nk1.relationship = CWE(cwe_1='FTH', cwe_2='Padre', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Av. Directorio 3400', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1406FZB', xad_6='AR')
        nk1.nk1_5 = '^^PH^01145678901'

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
    """ Based on live/ar/ar-sigehos.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIGEHOS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='MPI_CABA')
        msh.receiving_facility = HD(hd_1='DGSISIN')
        msh.date_time_of_message = '20260327090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'SGH00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260327090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC112345', cx_4='HOSP_DURAND', cx_5='MR'), CX(cx_1='DNI-27890123', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='MOLINA', xpn_2='CARLOS', xpn_3='ALBERTO')
        pid.date_time_of_birth = '19770614'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Rivadavia 8900', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1407FEF', xad_6='AR')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='HC998877', cx_4='HOSP_DURAND', cx_5='MR')
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
    """ Based on live/ar/ar-sigehos.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SIS')
        msh.sending_facility = HD(hd_1='HOSP_DURAND')
        msh.receiving_application = HD(hd_1='SIGEHOS')
        msh.receiving_facility = HD(hd_1='HOSP_DURAND')
        msh.date_time_of_message = '20260320070100'
        msh.message_type = MSG(msg_1='ACK', msg_2='O01', msg_3='ACK')
        msh.message_control_id = 'ACK60001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'CA'
        msa.message_control_id = 'SGH00005'
        msa.msa_3 = 'Pedido recibido correctamente'

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
