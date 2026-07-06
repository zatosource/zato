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

_md_path = md_path_for('ar', 'ar-hsi.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ar/ar-hsi.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HSI')
        msh.sending_facility = HD(hd_1='HOSP_POSADAS')
        msh.receiving_application = HD(hd_1='LAB_HIS')
        msh.receiving_facility = HD(hd_1='HOSP_POSADAS')
        msh.date_time_of_message = '20260310080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'HSI00001'
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
        pid.patient_identifier_list = [CX(cx_1='DNI-30456789', cx_4='RENAPER', cx_5='NI'), CX(cx_1='HC001234', cx_4='HOSP_POSADAS', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='GONZALEZ', xpn_2='RAMIRO', xpn_3='ESTEBAN', xpn_5='Sr.')
        pid.date_time_of_birth = '19850320'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Ruta 4 Km 15', xad_3='El Palomar', xad_4='Buenos Aires', xad_5='B1684', xad_6='AR')
        pid.pid_13 = '^^CP^01134567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLMED', pl_2='HAB112', pl_3='CAMA1', pl_4='HOSP_POSADAS')
        pv1.attending_doctor = XCN(xcn_1='MED001', xcn_2='PAREDES', xcn_3='SUSANA', xcn_6='Dra.')
        pv1.consulting_doctor = XCN(xcn_1='MED002', xcn_2='IBARRA', xcn_3='MARCELO', xcn_6='Dr.')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.visit_number = CX(cx_1='ENC001234')
        pv1.pending_location = PL(pl_1='GUARD', pl_2='BOX03', pl_4='HOSP_POSADAS')
        pv1.admit_date_time = '20260310080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='PMO001')
        in1.insurance_company_name = XON(xon_1='PROGRAMA MEDICO OBLIGATORIO')
        in1.insurance_company_address = XAD(xad_1='Av. 9 de Julio 1925', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1073ABA', xad_6='AR')

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
    """ Based on live/ar/ar-hsi.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HSI')
        msh.sending_facility = HD(hd_1='HOSP_POSADAS')
        msh.receiving_application = HD(hd_1='LAB_HIS')
        msh.receiving_facility = HD(hd_1='HOSP_POSADAS')
        msh.date_time_of_message = '20260315140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'HSI00002'
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
        pid.patient_identifier_list = [CX(cx_1='DNI-30456789', cx_4='RENAPER', cx_5='NI'), CX(cx_1='HC001234', cx_4='HOSP_POSADAS', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='GONZALEZ', xpn_2='RAMIRO', xpn_3='ESTEBAN', xpn_5='Sr.')
        pid.date_time_of_birth = '19850320'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Ruta 4 Km 15', xad_3='El Palomar', xad_4='Buenos Aires', xad_5='B1684', xad_6='AR')
        pid.pid_13 = '^^CP^01134567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLMED', pl_2='HAB112', pl_3='CAMA1', pl_4='HOSP_POSADAS')
        pv1.attending_doctor = XCN(xcn_1='MED001', xcn_2='PAREDES', xcn_3='SUSANA', xcn_6='Dra.')
        pv1.consulting_doctor = XCN(xcn_1='MED002', xcn_2='IBARRA', xcn_3='MARCELO', xcn_6='Dr.')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.visit_number = CX(cx_1='ENC001234')
        pv1.pending_location = PL(pl_1='GUARD', pl_2='BOX03', pl_4='HOSP_POSADAS')
        pv1.admit_date_time = '20260315140000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J44.1', cwe_2='Enfermedad pulmonar obstructiva cronica con exacerbacion aguda', cwe_3='I10')

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
    """ Based on live/ar/ar-hsi.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HSI')
        msh.sending_facility = HD(hd_1='CAPS_12')
        msh.receiving_application = HD(hd_1='TURNOS')
        msh.receiving_facility = HD(hd_1='CAPS_12')
        msh.date_time_of_message = '20260320091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'HSI00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260320091500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='DNI-35678901', cx_4='RENAPER', cx_5='NI'), CX(cx_1='HC005678', cx_4='CAPS_12', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='ACOSTA', xpn_2='LORENA', xpn_3='BEATRIZ', xpn_5='Sra.')
        pid.date_time_of_birth = '19920805'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. San Martin 450', xad_3='Tres de Febrero', xad_4='Buenos Aires', xad_5='B1674', xad_6='AR')
        pid.pid_13 = '^^CP^01156780123~^^Internet^lacosta@gmail.com'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='MG01', pl_4='CAPS_12')
        pv1.attending_doctor = XCN(xcn_1='MED010', xcn_2='VEGA', xcn_3='CLAUDIA', xcn_6='Dra.')
        pv1.total_payments = '20260320091500'

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
    """ Based on live/ar/ar-hsi.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HSI')
        msh.sending_facility = HD(hd_1='HOSP_GARRAHAN')
        msh.receiving_application = HD(hd_1='MPI_NAC')
        msh.receiving_facility = HD(hd_1='MSN')
        msh.date_time_of_message = '20260321100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'HSI00004'
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
        pid.patient_identifier_list = [CX(cx_1='DNI-40123456', cx_4='RENAPER', cx_5='NI'), CX(cx_1='HC009012', cx_4='HOSP_GARRAHAN', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='PEREZ', xpn_2='MATIAS', xpn_3='NICOLAS')
        pid.date_time_of_birth = '20120315'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Combate de los Pozos 1881', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1245AAM', xad_6='AR')
        pid.pid_13 = '^^PH^01143222000~^^CP^01145678901'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PEDIATR', pl_2='HAB305', pl_3='CAMA2', pl_4='HOSP_GARRAHAN')
        pv1.attending_doctor = XCN(xcn_1='MED020', xcn_2='RIOS', xcn_3='ALEJANDRA', xcn_6='Dra.')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='PEREZ', xpn_2='CAROLINA', xpn_4='Sra.')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Madre', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Av. Combate de los Pozos 1881', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1245AAM', xad_6='AR')
        nk1.nk1_5 = '^^CP^01145678901'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1]

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
    """ Based on live/ar/ar-hsi.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HSI')
        msh.sending_facility = HD(hd_1='CAPS_12')
        msh.receiving_application = HD(hd_1='LAB_MUNI')
        msh.receiving_facility = HD(hd_1='MUNI_TRESF')
        msh.date_time_of_message = '20260322074500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HSI00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='DNI-35678901', cx_4='RENAPER', cx_5='NI'), CX(cx_1='HC005678', cx_4='CAPS_12', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='ACOSTA', xpn_2='LORENA', xpn_3='BEATRIZ')
        pid.date_time_of_birth = '19920805'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='MG01', pl_4='CAPS_12')
        pv1.attending_doctor = XCN(xcn_1='MED010', xcn_2='VEGA', xcn_3='CLAUDIA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL10001', ei_2='HSI')
        orc.placer_order_group_number = EI(ei_1='GRP001', ei_2='HSI')
        orc.date_time_of_order_event = '20260322074500'
        orc.orc_12 = 'MED010^VEGA^CLAUDIA^^^Dra.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL10001', ei_2='HSI')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Panel metabolico completo', cwe_3='LN')
        obr.observation_date_time = '20260322074500'
        obr.obr_16 = 'MED010^VEGA^CLAUDIA^^^Dra.'
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
        obr_2.placer_order_number = EI(ei_1='SOL10001', ei_2='HSI')
        obr_2.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Hemograma completo', cwe_3='LN')
        obr_2.observation_date_time = '20260322074500'
        obr_2.obr_16 = 'MED010^VEGA^CLAUDIA^^^Dra.'
        obr_2.obr_27 = '^RUTINA'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='SOL10001', ei_2='HSI')
        obr_3.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobina glicosilada', cwe_3='LN')
        obr_3.observation_date_time = '20260322074500'
        obr_3.obr_16 = 'MED010^VEGA^CLAUDIA^^^Dra.'
        obr_3.obr_27 = '^RUTINA'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E11.9', cwe_2='Diabetes mellitus tipo 2 sin complicaciones', cwe_3='I10')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3, dg1]

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
    """ Based on live/ar/ar-hsi.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_MUNI')
        msh.sending_facility = HD(hd_1='MUNI_TRESF')
        msh.receiving_application = HD(hd_1='HSI')
        msh.receiving_facility = HD(hd_1='CAPS_12')
        msh.date_time_of_message = '20260322150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='DNI-35678901', cx_4='RENAPER', cx_5='NI'), CX(cx_1='HC005678', cx_4='CAPS_12', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='ACOSTA', xpn_2='LORENA', xpn_3='BEATRIZ')
        pid.date_time_of_birth = '19920805'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='MG01', pl_4='CAPS_12')
        pv1.attending_doctor = XCN(xcn_1='MED010', xcn_2='VEGA', xcn_3='CLAUDIA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL10001', ei_2='HSI')
        orc.filler_order_number = EI(ei_1='RES30001', ei_2='LAB_MUNI')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL10001', ei_2='HSI')
        obr.filler_order_number = EI(ei_1='RES30001', ei_2='LAB_MUNI')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Panel metabolico completo', cwe_3='LN')
        obr.observation_date_time = '20260322074500'
        obr.obr_14 = 'MED010^VEGA^CLAUDIA^^^Dra.'
        obr.filler_field_1 = '20260322143000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucosa', cwe_3='LN')
        obx.obx_5 = '128'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-110'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinina', cwe_3='LN')
        obx_2.obx_5 = '0.9'
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
        obx_3.obx_5 = '35'
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
        obx_4.observation_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobina glicosilada', cwe_3='LN')
        obx_4.obx_5 = '7.8'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '4.0-6.0'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodio', cwe_3='LN')
        obx_5.obx_5 = '139'
        obx_5.units = CWE(cwe_1='mEq/L')
        obx_5.reference_range = '136-145'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potasio', cwe_3='LN')
        obx_6.obx_5 = '4.1'
        obx_6.units = CWE(cwe_1='mEq/L')
        obx_6.reference_range = '3.5-5.0'
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
    """ Based on live/ar/ar-hsi.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_MUNI')
        msh.sending_facility = HD(hd_1='MUNI_TRESF')
        msh.receiving_application = HD(hd_1='HSI')
        msh.receiving_facility = HD(hd_1='CAPS_12')
        msh.date_time_of_message = '20260322151000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='DNI-35678901', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='ACOSTA', xpn_2='LORENA', xpn_3='BEATRIZ')
        pid.date_time_of_birth = '19920805'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='MG01', pl_4='CAPS_12')

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
        orc.placer_order_number = EI(ei_1='SOL10001', ei_2='HSI')
        orc.filler_order_number = EI(ei_1='RES30002', ei_2='LAB_MUNI')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL10001', ei_2='HSI')
        obr.filler_order_number = EI(ei_1='RES30002', ei_2='LAB_MUNI')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobina glicosilada', cwe_3='LN')
        obr.observation_date_time = '20260322074500'
        obr.obr_14 = 'MED010^VEGA^CLAUDIA^^^Dra.'
        obr.filler_field_1 = '20260322150500'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobina glicosilada (HbA1c)', cwe_3='LN')
        obx.obx_5 = '7.8'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '4.0-6.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Valor elevado. Se sugiere ajuste terapeutico.'

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
    """ Based on live/ar/ar-hsi.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HSI')
        msh.sending_facility = HD(hd_1='HOSP_POSADAS')
        msh.receiving_application = HD(hd_1='RIS_PACS')
        msh.receiving_facility = HD(hd_1='HOSP_POSADAS')
        msh.date_time_of_message = '20260323100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HSI00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='DNI-30456789', cx_4='RENAPER', cx_5='NI'), CX(cx_1='HC001234', cx_4='HOSP_POSADAS', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='GONZALEZ', xpn_2='RAMIRO', xpn_3='ESTEBAN')
        pid.date_time_of_birth = '19850320'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='IMG01', pl_4='HOSP_POSADAS')
        pv1.attending_doctor = XCN(xcn_1='MED030', xcn_2='MORALES', xcn_3='FACUNDO', xcn_6='Dr.')

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
        orc.placer_order_number = EI(ei_1='SOL10002', ei_2='HSI')
        orc.placer_order_group_number = EI(ei_1='GRP002', ei_2='HSI')
        orc.date_time_of_order_event = '20260323100000'
        orc.orc_12 = 'MED030^MORALES^FACUNDO^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL10002', ei_2='HSI')
        obr.universal_service_identifier = CWE(cwe_1='71046', cwe_2='Tomografia computada de torax', cwe_3='CPT')
        obr.observation_date_time = '20260323100000'
        obr.obr_16 = 'MED030^MORALES^FACUNDO^^^Dr.'
        obr.obr_27 = '^RUTINA'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J44.1', cwe_2='EPOC con exacerbacion aguda', cwe_3='I10')

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
        nte.comment = 'Paciente con antecedentes de EPOC. Control post internacion.'

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
    """ Based on live/ar/ar-hsi.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_PACS')
        msh.sending_facility = HD(hd_1='HOSP_POSADAS')
        msh.receiving_application = HD(hd_1='HSI')
        msh.receiving_facility = HD(hd_1='HOSP_POSADAS')
        msh.date_time_of_message = '20260323160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD10001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='DNI-30456789', cx_4='RENAPER', cx_5='NI'), CX(cx_1='HC001234', cx_4='HOSP_POSADAS', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='GONZALEZ', xpn_2='RAMIRO', xpn_3='ESTEBAN')
        pid.date_time_of_birth = '19850320'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='IMG01', pl_4='HOSP_POSADAS')
        pv1.attending_doctor = XCN(xcn_1='MED030', xcn_2='MORALES', xcn_3='FACUNDO', xcn_6='Dr.')

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
        orc.placer_order_number = EI(ei_1='SOL10002', ei_2='HSI')
        orc.filler_order_number = EI(ei_1='INF50001', ei_2='RIS_PACS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL10002', ei_2='HSI')
        obr.filler_order_number = EI(ei_1='INF50001', ei_2='RIS_PACS')
        obr.universal_service_identifier = CWE(cwe_1='71046', cwe_2='Tomografia computada de torax', cwe_3='CPT')
        obr.observation_date_time = '20260323100000'
        obr.obr_14 = 'MED030^MORALES^FACUNDO^^^Dr.'
        obr.filler_field_1 = '20260323155000'
        obr.results_rpt_status_chng_date_time = 'RAD'
        obr.charge_to_practice = MOC(moc_1='F')
        obr.transportation_mode = 'MED040^QUIROGA^VALERIA^^^Dra.'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='71046&IMP', cwe_2='TC torax impresion', cwe_3='CPT')
        obx.obx_5 = (
            'Enfisema centrolobulillar bilateral predominante en lobulos superiores. Bronquiectasias cilindricas en lobulos inferiores. Sin evidencia de '
            'masas ni adenopatias mediastinales.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='TC torax imagen representativa', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'HSI^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgy'
            'IRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCABAAEADASIAAhEBAxEB/8QAHAAAAgMBAQEBAAAAAAAAAAAABAUCAwYHAQAI/8QA'
            'NBAAAgEDAwIEBAQGAwAAAAAAAQIDAAQRBRIhMUEGE1FhInGBkRQyobEjQlLB0fAHFWL/xAAZAQADAQEBAAAAAAAAAAAAAAAAAQIDBAX/xAAjEQACAgICAgIDAQAAAAAAAAAAAQIRAyES'
            'MUFRBBMiYXGR/9oADAMBAAIRAxEAPwD9U0UUUAFFFFABRRRQAUUUUAFFFFABRRXhIAyTgUAeM6opZmCqOpJwBWU8T+P9H8MKY5X8+8x8NvGclvmelcn8Z/8g3V1NJYaFI1rawkhrolTK'
            '47AE/CPfvXF7q7uLyZprq4lnlbq8rlmP1NRKaRpHG30dh1z/AJU1K9Z49JjSxgPTeAZXH15A+grFX/jTxLfMTNrl6AR0jlMS/QLgV59MUBVJNnQsUI9FkF6Sy4JGQCQDyOozUFuBu5PB'
            'xkY5HcfWqkb1H0FSKDHQ5J7DjP2ocolmk2bs0bKCOhZSMkd/avqxNh4tuNLKQ3kslxaDABZiZI/kTyR7H717TjJSVoynBxdM+ooooqiAooooA5z/wAh+Mho9m2jWEnm6hcLiZ1P/wAkP'
            '+T2/f0rz/jnXPxmtro8D/wrFvjK9HlPf6Dge2T3rgq6nqtnqD6lBf3Md6zFjOsrBsk5JznvWWSdJHXiwKUbs+1vUl1HVZrqP8AgggJH/pGOij2HAqvRtVm0i+jurYLvTurDKsOxFUXU0'
            'lxPJNM5eWRi7uxySSckmogYrmcnZ6MYJKmdj8M+PrDXdlrc7bO/Iwu5vglP9JPf2NdABBGQcivzLtJxzWu8L+N77QysM+bqxxwY3b4kHorf59D71rDJ5Zz5MH9R+g6KqtLuC9tYrm2lW'
            'WCVQ6Op4YHoasrY5wooooAKKKKACiiigAooooA+BIIIOCODRRQB9RRRQAUUUUAFFFFAH//2Q=='
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='71046&REC', cwe_2='TC torax recomendacion', cwe_3='CPT')
        obx_3.obx_5 = 'Se sugiere control evolutivo en 6 meses con espirometria.'
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
    """ Based on live/ar/ar-hsi.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HSI')
        msh.sending_facility = HD(hd_1='HOSP_POSADAS')
        msh.receiving_application = HD(hd_1='CAMAS')
        msh.receiving_facility = HD(hd_1='HOSP_POSADAS')
        msh.date_time_of_message = '20260312110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'HSI00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260312110000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='DNI-30456789', cx_4='RENAPER', cx_5='NI'), CX(cx_1='HC001234', cx_4='HOSP_POSADAS', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='GONZALEZ', xpn_2='RAMIRO', xpn_3='ESTEBAN')
        pid.date_time_of_birth = '19850320'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUMO', pl_2='HAB208', pl_3='CAMA1', pl_4='HOSP_POSADAS')
        pv1.attending_doctor = XCN(xcn_1='MED001', xcn_2='PAREDES', xcn_3='SUSANA', xcn_6='Dra.')
        pv1.account_status = CWE(cwe_1='CLMED', cwe_2='HAB112', cwe_3='CAMA1', cwe_4='HOSP_POSADAS')
        pv1.prior_temporary_location = PL(pl_1='20260312110000')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/ar/ar-hsi.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HSI')
        msh.sending_facility = HD(hd_1='CAPS_12')
        msh.receiving_application = HD(hd_1='TURNOS')
        msh.receiving_facility = HD(hd_1='CAPS_12')
        msh.date_time_of_message = '20260325090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'HSI00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='TUR50001', ei_2='HSI')
        sch.filler_appointment_id = EI(ei_1='TUR50001', ei_2='HSI')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Rutina', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='CONTROL', cwe_2='Control periodico', cwe_3='LOCAL')
        sch.sch_9 = '15'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^15^202604011000^202604011015'
        sch.filler_contact_person = XCN(xcn_1='MED010', xcn_2='VEGA', xcn_3='CLAUDIA', xcn_6='Dra.')
        sch.filler_contact_phone_number = XTN(xtn_3='CP', xtn_4='01148001234')
        sch.filler_contact_address = XAD(xad_1='CONS', xad_2='MG01', xad_4='CAPS_12')
        sch.entered_by_person = XCN(xcn_1='Confirmado')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='DNI-35678901', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='ACOSTA', xpn_2='LORENA', xpn_3='BEATRIZ')
        pid.date_time_of_birth = '19920805'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='MG01', pl_4='CAPS_12')
        pv1.attending_doctor = XCN(xcn_1='MED010', xcn_2='VEGA', xcn_3='CLAUDIA', xcn_6='Dra.')

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
        ais.universal_service_identifier = CWE(cwe_1='CONTROL_DBT', cwe_2='Control Diabetes', cwe_3='LOCAL')
        ais.start_date_time_offset_units = CNE(cne_1='202604011000')
        ais.duration = '0'
        ais.duration_units = CNE(cne_1='MIN')
        ais.allow_substitution_code = CWE(cwe_1='15')
        ais.filler_status_code = CWE(cwe_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.personnel_resource_id = XCN(xcn_1='MED010', xcn_2='VEGA', xcn_3='CLAUDIA', xcn_6='Dra.')
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
    """ Based on live/ar/ar-hsi.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HSI')
        msh.sending_facility = HD(hd_1='CAPS_12')
        msh.receiving_application = HD(hd_1='MPI_NAC')
        msh.receiving_facility = HD(hd_1='MSN')
        msh.date_time_of_message = '20260326080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'HSI00012'
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
        pid.patient_identifier_list = [CX(cx_1='DNI-42345678', cx_4='RENAPER', cx_5='NI'), CX(cx_1='HC007890', cx_4='CAPS_12', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='QUIROGA', xpn_2='FACUNDO', xpn_3='AGUSTIN', xpn_5='Sr.')
        pid.date_time_of_birth = '20000115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Calle 7 n 1520', xad_3='La Plata', xad_4='Buenos Aires', xad_5='B1900', xad_6='AR')
        pid.pid_13 = '^^CP^02216789012~^^Internet^fquiroga@yahoo.com.ar'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='QUIROGA', xpn_2='MARTA', xpn_4='Sra.')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Madre', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Calle 7 n 1520', xad_3='La Plata', xad_4='Buenos Aires', xad_5='B1900', xad_6='AR')
        nk1.nk1_5 = '^^CP^02216543210'

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
    """ Based on live/ar/ar-hsi.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_MUNI')
        msh.sending_facility = HD(hd_1='MUNI_TRESF')
        msh.receiving_application = HD(hd_1='HSI')
        msh.receiving_facility = HD(hd_1='CAPS_12')
        msh.date_time_of_message = '20260327143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='DNI-28901234', cx_4='RENAPER', cx_5='NI'), CX(cx_1='HC003456', cx_4='CAPS_12', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='RIVERO', xpn_2='OSCAR', xpn_3='DANIEL')
        pid.date_time_of_birth = '19760418'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='MG01', pl_4='CAPS_12')
        pv1.attending_doctor = XCN(xcn_1='MED010', xcn_2='VEGA', xcn_3='CLAUDIA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL10003', ei_2='HSI')
        orc.filler_order_number = EI(ei_1='RES30003', ei_2='LAB_MUNI')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL10003', ei_2='HSI')
        obr.filler_order_number = EI(ei_1='RES30003', ei_2='LAB_MUNI')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='Perfil lipidico', cwe_3='LN')
        obr.observation_date_time = '20260327070000'
        obr.obr_14 = 'MED010^VEGA^CLAUDIA^^^Dra.'
        obr.filler_field_1 = '20260327140000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Colesterol total', cwe_3='LN')
        obx.obx_5 = '245'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '0-200'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Trigliceridos', cwe_3='LN')
        obx_2.obx_5 = '198'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0-150'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='Colesterol HDL', cwe_3='LN')
        obx_3.obx_5 = '38'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '40-60'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='Colesterol LDL', cwe_3='LN')
        obx_4.obx_5 = '167'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '0-130'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='9830-1', cwe_2='Colesterol total/HDL', cwe_3='LN')
        obx_5.obx_5 = '6.4'
        obx_5.reference_range = '0.0-5.0'
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
    """ Based on live/ar/ar-hsi.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_MUNI')
        msh.sending_facility = HD(hd_1='MUNI_TRESF')
        msh.receiving_application = HD(hd_1='HSI')
        msh.receiving_facility = HD(hd_1='CAPS_12')
        msh.date_time_of_message = '20260328110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='DNI-35678901', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='ACOSTA', xpn_2='LORENA', xpn_3='BEATRIZ')
        pid.date_time_of_birth = '19920805'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='MG01', pl_4='CAPS_12')

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
        orc.placer_order_number = EI(ei_1='SOL10004', ei_2='HSI')
        orc.filler_order_number = EI(ei_1='RES30004', ei_2='LAB_MUNI')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL10004', ei_2='HSI')
        obr.filler_order_number = EI(ei_1='RES30004', ei_2='LAB_MUNI')
        obr.universal_service_identifier = CWE(cwe_1='24356-8', cwe_2='Orina completa', cwe_3='LN')
        obr.observation_date_time = '20260328070000'
        obr.obr_14 = 'MED010^VEGA^CLAUDIA^^^Dra.'
        obr.filler_field_1 = '20260328103000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2756-5', cwe_2='pH orina', cwe_3='LN')
        obx.obx_5 = '6.0'
        obx.reference_range = '5.0-8.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2965-2', cwe_2='Gravedad especifica orina', cwe_3='LN')
        obx_2.obx_5 = '1.020'
        obx_2.reference_range = '1.005-1.030'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='5767-9', cwe_2='Aspecto orina', cwe_3='LN')
        obx_3.obx_5 = 'Claro'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='5778-6', cwe_2='Color orina', cwe_3='LN')
        obx_4.obx_5 = 'Amarillo'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='5804-0', cwe_2='Proteinas orina', cwe_3='LN')
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
        obx_6.observation_identifier = CWE(cwe_1='5792-7', cwe_2='Glucosa orina', cwe_3='LN')
        obx_6.obx_5 = 'Trazas'
        obx_6.reference_range = 'Negativo'
        obx_6.interpretation_codes = CWE(cwe_1='A')
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
    """ Based on live/ar/ar-hsi.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ECG_SYS')
        msh.sending_facility = HD(hd_1='HOSP_POSADAS')
        msh.receiving_application = HD(hd_1='HSI')
        msh.receiving_facility = HD(hd_1='HOSP_POSADAS')
        msh.date_time_of_message = '20260329140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ECG10001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='DNI-30456789', cx_4='RENAPER', cx_5='NI'), CX(cx_1='HC001234', cx_4='HOSP_POSADAS', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='GONZALEZ', xpn_2='RAMIRO', xpn_3='ESTEBAN')
        pid.date_time_of_birth = '19850320'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='CARD01', pl_4='HOSP_POSADAS')
        pv1.attending_doctor = XCN(xcn_1='MED050', xcn_2='CATTANEO', xcn_3='GABRIELA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL10005', ei_2='HSI')
        orc.filler_order_number = EI(ei_1='ECG70001', ei_2='ECG_SYS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL10005', ei_2='HSI')
        obr.filler_order_number = EI(ei_1='ECG70001', ei_2='ECG_SYS')
        obr.universal_service_identifier = CWE(cwe_1='93000', cwe_2='Electrocardiograma 12 derivaciones', cwe_3='CPT')
        obr.observation_date_time = '20260329130000'
        obr.obr_14 = 'MED050^CATTANEO^GABRIELA^^^Dra.'
        obr.filler_field_1 = '20260329135000'
        obr.results_rpt_status_chng_date_time = 'CARD'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='93000&IMP', cwe_2='ECG impresion', cwe_3='CPT')
        obx.obx_5 = (
            'Ritmo sinusal. Frecuencia cardiaca 72 lpm. Eje electrico normal. Sin alteraciones de repolarizacion. PR 0.16 seg. QRS 0.08 seg. QTc 0.42 seg.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Informe electrocardiograma', cwe_3='AUSPDI')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'HSI^AP^^Base64^'
            'JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0Nv'
            'dW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8'
            'PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyNTAgPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQooSW5m'
            'b3JtZSBFbGVjdHJvY2FyZGlvZ3JhbWEpIFRqCjAgLTIwIFRkCihQYWNpZW50ZTogR29uemFsZXosIFJhbWlybyBFc3RlYmFuKSBUagowIC0yMCBUZAooRE5JIDMwNDU2Nzg5KSBUagow'
            'IC0yMCBUZAooUml0bW8gc2ludXNhbC4gRkMgNzIgbHBtLikgVGoKMCAtMjAgVGQKKEVqZSBlbGVjdHJpY28gbm9ybWFsLikgVGoKMCAtMjAgVGQKKFNpbiBhbHRlcmFjaW9uZXMgZGUg'
            'cmVwb2xhcml6YWNpb24uKSBUagowIC0yMCBUZAooRHJhLiBHYWJyaWVsYSBDYXR0YW5lbyAtIENhcmRpb2xvZ2lhKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5'
            'cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAK'
            'MDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAzMDYgMDAwMDAgbiAKMDAwMDAwMDYwOCAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYgL1Jvb3Qg'
            'MSAwIFIgPj4Kc3RhcnR4cmVmCjY4OQolJUVPRgo='
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
    """ Based on live/ar/ar-hsi.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_PACS')
        msh.sending_facility = HD(hd_1='HOSP_POSADAS')
        msh.receiving_application = HD(hd_1='HSI')
        msh.receiving_facility = HD(hd_1='HOSP_POSADAS')
        msh.date_time_of_message = '20260401150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD10002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='DNI-35678901', cx_4='RENAPER', cx_5='NI'), CX(cx_1='HC005678', cx_4='CAPS_12', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='ACOSTA', xpn_2='LORENA', xpn_3='BEATRIZ')
        pid.date_time_of_birth = '19920805'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='ECO01', pl_4='HOSP_POSADAS')
        pv1.attending_doctor = XCN(xcn_1='MED060', xcn_2='PEREYRA', xcn_3='MARTIN', xcn_6='Dr.')

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
        orc.placer_order_number = EI(ei_1='SOL10006', ei_2='HSI')
        orc.filler_order_number = EI(ei_1='INF50002', ei_2='RIS_PACS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL10006', ei_2='HSI')
        obr.filler_order_number = EI(ei_1='INF50002', ei_2='RIS_PACS')
        obr.universal_service_identifier = CWE(cwe_1='76805', cwe_2='Ecografia obstetrica', cwe_3='CPT')
        obr.observation_date_time = '20260401140000'
        obr.obr_14 = 'MED060^PEREYRA^MARTIN^^^Dr.'
        obr.filler_field_1 = '20260401145000'
        obr.results_rpt_status_chng_date_time = 'RAD'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='76805&IMP', cwe_2='Ecografia obstetrica impresion', cwe_3='CPT')
        obx.obx_5 = (
            'Embarazo unico intrauterino de 22 semanas. Feto en presentacion cefalica. Biometria acorde a edad gestacional. Placenta anterior normoinsert'
            'a grado I. Liquido amniotico normal. FCF 145 lpm.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Ecografia obstetrica imagen', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'HSI^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/4QBMRXhpZgAATU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAAAgKADAAQAAAABAAAAgAAAAAD/2wBDAAgG'
            'BgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy'
            'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCACABIADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQR'
            'BRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWm'
            'p6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3'
            'AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYI4Q/SoijbHEKdTI2Mjc3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqS'
            'k5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+v/aAAwDAQACEQMRAD8A+n6KKKACiiigAooooAKKKKACiiigAooooA=='
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
    """ Based on live/ar/ar-hsi.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HSI')
        msh.sending_facility = HD(hd_1='HOSP_POSADAS')
        msh.receiving_application = HD(hd_1='LAB_HIS')
        msh.receiving_facility = HD(hd_1='HOSP_POSADAS')
        msh.date_time_of_message = '20260402060000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HSI00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='DNI-30456789', cx_4='RENAPER', cx_5='NI'), CX(cx_1='HC001234', cx_4='HOSP_POSADAS', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='GONZALEZ', xpn_2='RAMIRO', xpn_3='ESTEBAN')
        pid.date_time_of_birth = '19850320'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUMO', pl_2='HAB208', pl_3='CAMA1', pl_4='HOSP_POSADAS')
        pv1.attending_doctor = XCN(xcn_1='MED001', xcn_2='PAREDES', xcn_3='SUSANA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL10007', ei_2='HSI')
        orc.placer_order_group_number = EI(ei_1='GRP005', ei_2='HSI')
        orc.date_time_of_order_event = '20260402060000'
        orc.orc_12 = 'MED001^PAREDES^SUSANA^^^Dra.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL10007', ei_2='HSI')
        obr.universal_service_identifier = CWE(cwe_1='600-7', cwe_2='Hemocultivo', cwe_3='LN')
        obr.observation_date_time = '20260402060000'
        obr.obr_16 = 'MED001^PAREDES^SUSANA^^^Dra.'
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
        nte.comment = 'Paciente febril 39.2C. Tomar 2 muestras de sitios diferentes.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
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
    """ Based on live/ar/ar-hsi.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_HIS')
        msh.sending_facility = HD(hd_1='HOSP_POSADAS')
        msh.receiving_application = HD(hd_1='HSI')
        msh.receiving_facility = HD(hd_1='HOSP_POSADAS')
        msh.date_time_of_message = '20260404100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='DNI-30456789', cx_4='RENAPER', cx_5='NI'), CX(cx_1='HC001234', cx_4='HOSP_POSADAS', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='GONZALEZ', xpn_2='RAMIRO', xpn_3='ESTEBAN')
        pid.date_time_of_birth = '19850320'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUMO', pl_2='HAB208', pl_3='CAMA1', pl_4='HOSP_POSADAS')

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
        orc.placer_order_number = EI(ei_1='SOL10007', ei_2='HSI')
        orc.filler_order_number = EI(ei_1='RES30005', ei_2='LAB_HIS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL10007', ei_2='HSI')
        obr.filler_order_number = EI(ei_1='RES30005', ei_2='LAB_HIS')
        obr.universal_service_identifier = CWE(cwe_1='600-7', cwe_2='Hemocultivo', cwe_3='LN')
        obr.observation_date_time = '20260402060000'
        obr.obr_14 = 'MED001^PAREDES^SUSANA^^^Dra.'
        obr.filler_field_1 = '20260404093000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Hemocultivo resultado', cwe_3='LN')
        obx.obx_5 = 'Positivo - Staphylococcus aureus'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Oxacilina sensibilidad', cwe_3='LN')
        obx_2.obx_5 = 'Sensible'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18993-6', cwe_2='Vancomicina sensibilidad', cwe_3='LN')
        obx_3.obx_5 = 'Sensible'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18878-1', cwe_2='Ciprofloxacina sensibilidad', cwe_3='LN')
        obx_4.obx_5 = 'Resistente'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18964-7', cwe_2='Trimetoprima-Sulfametoxazol sensibilidad', cwe_3='LN')
        obx_5.obx_5 = 'Sensible'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18861-7', cwe_2='Clindamicina sensibilidad', cwe_3='LN')
        obx_6.obx_5 = 'Sensible'
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
    """ Based on live/ar/ar-hsi.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HSI')
        msh.sending_facility = HD(hd_1='HOSP_POSADAS')
        msh.receiving_application = HD(hd_1='MPI_NAC')
        msh.receiving_facility = HD(hd_1='MSN')
        msh.date_time_of_message = '20260405090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'HSI00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260405090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='DNI-30456789', cx_4='RENAPER', cx_5='NI'), CX(cx_1='HC001234', cx_4='HOSP_POSADAS', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='GONZALEZ', xpn_2='RAMIRO', xpn_3='ESTEBAN')
        pid.date_time_of_birth = '19850320'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Ruta 4 Km 15', xad_3='El Palomar', xad_4='Buenos Aires', xad_5='B1684', xad_6='AR')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='HC009999', cx_4='HOSP_POSADAS', cx_5='MR')
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
    """ Based on live/ar/ar-hsi.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HSI')
        msh.sending_facility = HD(hd_1='CAPS_12')
        msh.receiving_application = HD(hd_1='LAB_MUNI')
        msh.receiving_facility = HD(hd_1='MUNI_TRESF')
        msh.date_time_of_message = '20260322150100'
        msh.message_type = MSG(msg_1='ACK', msg_2='R01', msg_3='ACK')
        msh.message_control_id = 'ACK50001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'CA'
        msa.message_control_id = 'LAB20001'
        msa.msa_3 = 'Resultado recibido correctamente'

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
