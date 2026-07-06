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
from zato.hl7v2.v2_9.datatypes import CQ, CWE, CX, EI, EIP, FC, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA39Patient, OmbO27Patient, OmbO27PatientVisit, OmlO21ObservationRequest, OmlO21Order, \
    OmlO21OrderPrior, OmlO21Patient, OmlO21PatientVisit, OmlO21PriorResult, OmlO21Specimen, OmpO09Observation, OmpO09Order, OmpO09Patient, \
    OmpO09PatientVisit, OmpO09Timing, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OrpO10Order, OrpO10Patient, OrpO10Response, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RspK21QueryResponse
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A39, OMB_O27, OML_O21, OMP_O09, ORM_O01, ORP_O10, ORU_R01, QBP_Q21, RSP_K21
from zato.hl7v2.v2_9.segments import BPO, ERR, EVN, IN1, MRG, MSA, MSH, OBR, OBX, ORC, PID, PV1, PV2, QAK, QPD, QRI, RCP, RXO, RXR, SPM, TQ1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('es', 'es-jimena.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/es/es-jimena.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='JIMENA')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='ADT_SACYL')
        msh.receiving_facility = HD(hd_1='GRS_SACYL')
        msh.date_time_of_message = '20241015083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'SACYL20241015083000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20241015082900'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CACL876543210', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='71245667X', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='4798765432101', cx_4='MS', cx_5='HC', cx_9='ESP&&ISO3166'),
            CX(cx_1='280876543210', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC002468', cx_4='HCUVA', cx_5='PI', cx_9='HCUVA&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='SEDANO', xpn_2='ROSARIO')
        pid.mothers_maiden_name = XPN(xpn_1='IGLESIAS')
        pid.date_time_of_birth = '19670815'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(
            xad_1='CL&PASEO ZORRILLA&45',
            xad_2='3B',
            xad_3='470186',
            xad_4='47',
            xad_5='47002',
            xad_6='ESP',
            xad_7='H',
            xad_8='VALLADOLID',
        )
        pid.pid_13 = '^PRN^PH^^^983445566~^PRN^CP^^^666334455~^PRN^Internet^rsedano@correo.es'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MINTER', pl_2='301', pl_3='A', pl_4='HCUVA')
        pv1.attending_doctor = XCN(xcn_1='23456789', xcn_2='LINARES', xcn_3='PEDRO', xcn_4='ARCE', xcn_9='MI')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='IMED')
        pv1.admitting_doctor = XCN(xcn_1='23456789', xcn_2='LINARES', xcn_3='PEDRO', xcn_4='ARCE', xcn_9='MI')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='2024101500001', cx_4='HOS', cx_5='VN', cx_9='HCUVA&&99CENTROSACYL')
        pv1.total_adjustments = '20241015083000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SNS', cwe_3='HL70072')
        in1.insurance_company_id = CX(cx_1='SNS001')
        in1.insurance_company_name = XON(xon_1='SERVICIO NACIONAL DE SALUD')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20251231'
        in1.policy_number = 'CACL876543210'

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
    """ Based on live/es/es-jimena.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='JIMENA')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='ADT_SACYL')
        msh.receiving_facility = HD(hd_1='GRS_SACYL')
        msh.date_time_of_message = '20241018140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'SACYL20241018140000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20241018135500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CACL876543210', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='71245667X', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC002468', cx_4='HCUVA', cx_5='PI', cx_9='HCUVA&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='SEDANO', xpn_2='ROSARIO')
        pid.mothers_maiden_name = XPN(xpn_1='IGLESIAS')
        pid.date_time_of_birth = '19670815'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(
            xad_1='CL&PASEO ZORRILLA&45',
            xad_2='3B',
            xad_3='470186',
            xad_4='47',
            xad_5='47002',
            xad_6='ESP',
            xad_7='H',
            xad_8='VALLADOLID',
        )
        pid.pid_13 = '^PRN^PH^^^983445566'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='205', pl_3='B', pl_4='HCUVA')
        pv1.attending_doctor = XCN(xcn_1='98765432', xcn_2='BERMUDEZ', xcn_3='CONSUELO', xcn_4='OTERO', xcn_9='MI')
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.admit_source = CWE(cwe_1='ICAR')
        pv1.admitting_doctor = XCN(xcn_1='98765432', xcn_2='BERMUDEZ', xcn_3='CONSUELO', xcn_4='OTERO', xcn_9='MI')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='2024101500001', cx_4='HOS', cx_5='VN', cx_9='HCUVA&&99CENTROSACYL')
        pv1.pv1_25 = 'MINTER^301^A^HCUVA'
        pv1.total_adjustments = '20241015083000'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/es/es-jimena.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='JIMENA')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='ADT_SACYL')
        msh.receiving_facility = HD(hd_1='GRS_SACYL')
        msh.date_time_of_message = '20241022110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'SACYL20241022110000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20241022105800'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CACL876543210', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='71245667X', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC002468', cx_4='HCUVA', cx_5='PI', cx_9='HCUVA&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='SEDANO', xpn_2='ROSARIO')
        pid.mothers_maiden_name = XPN(xpn_1='IGLESIAS')
        pid.date_time_of_birth = '19670815'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(
            xad_1='CL&PASEO ZORRILLA&45',
            xad_2='3B',
            xad_3='470186',
            xad_4='47',
            xad_5='47002',
            xad_6='ESP',
            xad_7='H',
            xad_8='VALLADOLID',
        )
        pid.pid_13 = '^PRN^PH^^^983445566'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='205', pl_3='B', pl_4='HCUVA')
        pv1.attending_doctor = XCN(xcn_1='98765432', xcn_2='BERMUDEZ', xcn_3='CONSUELO', xcn_4='OTERO', xcn_9='MI')
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.admit_source = CWE(cwe_1='ICAR')
        pv1.admitting_doctor = XCN(xcn_1='98765432', xcn_2='BERMUDEZ', xcn_3='CONSUELO', xcn_4='OTERO', xcn_9='MI')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='2024101500001', cx_4='HOS', cx_5='VN', cx_9='HCUVA&&99CENTROSACYL')
        pv1.total_adjustments = '20241015083000'
        pv1.total_payments = '20241022110000'

        # .. assemble the full message ..
        msg = ADT_A03()
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
    """ Based on live/es/es-jimena.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='JIMENA')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='ADT_SACYL')
        msh.receiving_facility = HD(hd_1='GRS_SACYL')
        msh.date_time_of_message = '20241023091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'SACYL20241023091500004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20241023091400'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CACL876543210', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='71245667X', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='4798765432101', cx_4='MS', cx_5='HC', cx_9='ESP&&ISO3166'),
            CX(cx_1='280876543210', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC002468', cx_4='HCUVA', cx_5='PI', cx_9='HCUVA&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='SEDANO', xpn_2='ROSARIO')
        pid.mothers_maiden_name = XPN(xpn_1='IGLESIAS')
        pid.date_time_of_birth = '19670815'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(
            xad_1='AV&REYES CATOLICOS&12',
            xad_2='1A',
            xad_3='470186',
            xad_4='47',
            xad_5='47002',
            xad_6='ESP',
            xad_7='H',
            xad_8='VALLADOLID',
        )
        pid.pid_13 = '^PRN^PH^^^983778899~^PRN^CP^^^666334455~^PRN^Internet^r.sedano@nuevocorreo.es'
        pid.mothers_identifier = CX(cx_1='ESP', cx_2='Espana', cx_3='ISO3166')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid

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
    """ Based on live/es/es-jimena.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='JIMENA')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='MPI_SACYL')
        msh.receiving_facility = HD(hd_1='GRS_SACYL')
        msh.date_time_of_message = '20241024112947'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'SACYL20241024112947005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20241024112947'
        evn.operator_id = XCN(xcn_1='JIMENA')
        evn.event_occurred = '20241024112947'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='CACL234567891', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='44556677H', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC008765', cx_4='HCUVA', cx_5='PI', cx_9='HCUVA&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='LOZANO', xpn_2='ENRIQUE', xpn_3='VALENTIN')
        pid.date_time_of_birth = '19910304'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&AMPLE&1', xad_3='470186', xad_4='47', xad_5='47730', xad_6='ESP', xad_7='H', xad_8='MEDINA DEL CAMPO')
        pid.pid_13 = '^PRN^PH^^^983223344~^PRN^CP^^^600334455'
        pid.patient_death_date_and_time = 'N'
        pid.identity_reliability_code = CWE(cwe_1='20120628')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = [
            CX(cx_1='HC008766', cx_4='HCUVA', cx_5='PI', cx_9='HCUVA&&99CENTROSACYL'),
            CX(cx_1='CACL234567892', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
        ]

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
    """ Based on live/es/es-jimena.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TAOSACYL')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='JIMENA')
        msh.receiving_facility = HD(hd_1='HCUVA')
        msh.date_time_of_message = '20241101093000'
        msh.message_type = MSG(msg_1='OMP', msg_2='O09', msg_3='OMP_O09')
        msh.message_control_id = 'TAO20241101093000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CACL345678912', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='22334455B', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC003579', cx_4='HCUVA', cx_5='PI', cx_9='HCUVA&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='HIGUERAS', xpn_2='DIONISIO')
        pid.mothers_maiden_name = XPN(xpn_1='ACEBEDO')
        pid.date_time_of_birth = '19570923'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&GRAN VIA&22', xad_2='4D', xad_3='090059', xad_4='9', xad_5='09002', xad_6='ESP', xad_7='H', xad_8='BURGOS')
        pid.pid_13 = '^PRN^PH^^^947334455'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.re_admission_indicator = CWE(cwe_1='22334455', cwe_2='PAREDES', cwe_3='BRAULIO', cwe_4='GALVAN', cwe_9='MI')
        pv1.vip_indicator = CWE(cwe_1='HEMA')
        pv1.financial_class = FC(fc_1='HEMA')
        pv1.credit_rating = CWE(cwe_1='22334455', cwe_2='PAREDES', cwe_3='BRAULIO', cwe_4='GALVAN', cwe_9='MI')
        pv1.contract_code = CWE(cwe_1='O')
        pv1.pv1_25 = '2024110100001^^^CEX^VN^^^^HCUVA&&99CENTROSACYL'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.expected_admit_date_time = '20241201'

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmpO09PatientVisit()
        patient_visit.pv1 = pv1
        patient_visit.pv2 = pv2

        # .. build the PATIENT group ..
        patient = OmpO09Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.filler_order_number = EI(ei_1='PRESCR20241101001', ei_3='TAOSACYL')
        orc.orc_10 = '20241101093000'
        orc.enterers_location = PL(pl_1='44556677', pl_2='CEPEDA', pl_3='GASPAR', pl_4='PALENCIA', pl_9='MI')
        orc.orc_19 = '13001^Hospital Universitario de Burgos^99CENTROSACYL'

        # .. build TQ1 ..
        tq1 = TQ1()
        tq1.set_id_tq1 = '1'
        tq1.tq1_2 = '4^^mg^miligramos^ISO+'
        tq1.end_datetime = '20241101'

        # .. build the TIMING group ..
        timing = OmpO09Timing()
        timing.tq1 = tq1

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='654321', cwe_2='ACENOCUMAROL 4MG', cwe_3='99001')
        rxo.requested_give_units = CWE(cwe_1='mg', cwe_2='miligramos', cwe_3='ISO+')
        rxo.pharmacist_treatment_suppliers_verifier_id = XCN(xcn_1='44556677', xcn_2='CEPEDA', xcn_3='GASPAR', xcn_4='PALENCIA', xcn_9='MI')
        rxo.requested_give_per_time_unit = 'W1'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx.obx_5 = '2.8'
        obx.reference_range = '2.0 - 3.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.observation_method = CWE(cwe_1='20241101090000')

        # .. build the OBSERVATION group ..
        observation = OmpO09Observation()
        observation.obx = obx

        # .. build the ORDER group ..
        order = OmpO09Order()
        order.orc = orc
        order.timing = timing
        order.rxo = rxo
        order.rxr = rxr
        order.observation = observation

        # .. build TQ1 ..
        tq1_2 = TQ1()
        tq1_2.set_id_tq1 = '2'
        tq1_2.tq1_2 = '4^^mg^miligramos^ISO+'
        tq1_2.end_datetime = '20241102'

        # .. build TQ1 ..
        tq1_3 = TQ1()
        tq1_3.set_id_tq1 = '3'
        tq1_3.tq1_2 = '2^^mg^miligramos^ISO+'
        tq1_3.end_datetime = '20241103'

        # .. build TQ1 ..
        tq1_4 = TQ1()
        tq1_4.set_id_tq1 = '4'
        tq1_4.tq1_2 = '4^^mg^miligramos^ISO+'
        tq1_4.end_datetime = '20241104'

        # .. assemble the full message ..
        msg = OMP_O09()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [tq1_2, tq1_3, tq1_4]

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
    """ Based on live/es/es-jimena.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='JIMENA')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='TAOSACYL')
        msh.receiving_facility = HD(hd_1='HCUVA')
        msh.date_time_of_message = '20241101094500'
        msh.message_type = MSG(msg_1='ORP', msg_2='O10', msg_3='ORP_O10')
        msh.message_control_id = 'SACYL20241101094500002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AE'
        msa.message_control_id = 'TAO20241101093000001'

        # .. build ERR ..
        err = ERR()
        err.hl7_error_code = CWE(cwe_1='207', cwe_2='Error interno de la aplicacion', cwe_3='HL70357')
        err.severity = 'E'
        err.diagnostic_information = 'Codigo de medicamento no encontrado en el catalogo local'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CACL345678912', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='HC003579', cx_4='HCUVA', cx_5='PI', cx_9='HCUVA&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='HIGUERAS', xpn_2='DIONISIO')
        pid.mothers_maiden_name = XPN(xpn_1='ACEBEDO')
        pid.date_time_of_birth = '19570923'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build the PATIENT group ..
        patient = OrpO10Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'UA'
        orc.filler_order_number = EI(ei_1='PRESCR20241101001', ei_3='TAOSACYL')
        orc.order_status = 'CA'

        # .. build the ORDER group ..
        order = OrpO10Order()
        order.orc = orc

        # .. build the RESPONSE group ..
        response = OrpO10Response()
        response.patient = patient
        response.order = order

        # .. assemble the full message ..
        msg = ORP_O10()
        msg.msh = msh
        msg.msa = msa
        msg.err = err
        msg.response = response

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
    """ Based on live/es/es-jimena.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='JIMENA')
        msh.sending_facility = HD(hd_1='CAULE')
        msh.receiving_application = HD(hd_1='FARMA_SACYL')
        msh.receiving_facility = HD(hd_1='CAULE')
        msh.date_time_of_message = '20241105160000'
        msh.message_type = MSG(msg_1='OMP', msg_2='O09', msg_3='OMP_O09')
        msh.message_control_id = 'FARMA20241105160001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CACL456789123', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='33445566C', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC004680', cx_4='CAULE', cx_5='PI', cx_9='CAULE&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='OCANA', xpn_2='ADELA')
        pid.mothers_maiden_name = XPN(xpn_1='GRANADOS')
        pid.date_time_of_birth = '19740512'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CL&ORDONO II&15', xad_2='2C', xad_3='240089', xad_4='24', xad_5='24004', xad_6='ESP', xad_7='H', xad_8='LEON')
        pid.pid_13 = '^PRN^PH^^^987223344'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEURO', pl_2='402', pl_3='A', pl_4='CAULE')
        pv1.attending_doctor = XCN(xcn_1='22334455', xcn_2='PAREDES', xcn_3='BRAULIO', xcn_4='GALVAN', xcn_9='MI')
        pv1.hospital_service = CWE(cwe_1='NEU')
        pv1.admit_source = CWE(cwe_1='INEU')
        pv1.admitting_doctor = XCN(xcn_1='22334455', xcn_2='PAREDES', xcn_3='BRAULIO', xcn_4='GALVAN', xcn_9='MI')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='2024110300001', cx_4='HOS', cx_5='VN', cx_9='CAULE&&99CENTROSACYL')
        pv1.total_adjustments = '20241103092000'

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmpO09PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OmpO09Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.filler_order_number = EI(ei_1='RXORD2024110500001', ei_3='FARMA_SACYL')
        orc.orc_10 = '20241105160000'
        orc.enterers_location = PL(pl_1='22334455', pl_2='PAREDES', pl_3='BRAULIO', pl_4='GALVAN', pl_9='MI')
        orc.orc_18 = 'NEU^NEUROLOGIA^99SVC'
        orc.orc_19 = '24001^Hospital de Leon^99CENTROSACYL'

        # .. build TQ1 ..
        tq1 = TQ1()
        tq1.set_id_tq1 = '1'
        tq1.tq1_2 = '1^^SF30^COMPRIMIDO^99RDHCU'
        tq1.priority = CWE(cwe_1='20241105180000')
        tq1.condition_text = '20241115180000'

        # .. build the TIMING group ..
        timing = OmpO09Timing()
        timing.tq1 = tq1

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='712345', cwe_2='LEVETIRACETAM 500MG COMPRIMIDOS', cwe_3='99001')
        rxo.requested_give_amount_minimum = '500'
        rxo.requested_give_amount_maximum = '500'
        rxo.requested_give_units = CWE(cwe_1='mg', cwe_2='miligramos', cwe_3='ISO+')
        rxo.pharmacist_treatment_suppliers_verifier_id = XCN(xcn_1='22334455', xcn_2='PAREDES', xcn_3='BRAULIO', xcn_4='GALVAN', xcn_9='MI')
        rxo.requested_give_per_time_unit = 'D1'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='301898006', cwe_2='Superficie corporal', cwe_3='SNM3')
        obx.obx_5 = '1.72'
        obx.probability = 'F'
        obx.producers_id = CWE(cwe_1='20241105')

        # .. build the OBSERVATION group ..
        observation = OmpO09Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='272102008', cwe_2='Peso', cwe_3='SNM3')
        obx_2.obx_5 = '68'
        obx_2.probability = 'F'
        obx_2.producers_id = CWE(cwe_1='20241105')

        # .. build the OBSERVATION group ..
        observation_2 = OmpO09Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='248328003', cwe_2='Talla', cwe_3='SNM3')
        obx_3.obx_5 = '170'
        obx_3.probability = 'F'
        obx_3.producers_id = CWE(cwe_1='20241105')

        # .. build the OBSERVATION group ..
        observation_3 = OmpO09Observation()
        observation_3.obx = obx_3

        # .. build the ORDER group ..
        order = OmpO09Order()
        order.orc = orc
        order.timing = timing
        order.rxo = rxo
        order.rxr = rxr
        order.observation = observation
        order.observation_2 = observation_2
        order.observation_3 = observation_3

        # .. assemble the full message ..
        msg = OMP_O09()
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
    """ Based on live/es/es-jimena.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='JIMENA')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='TAOSACYL')
        msh.receiving_facility = HD(hd_1='HCUVA')
        msh.date_time_of_message = '20241101093005'
        msh.message_type = MSG(msg_1='ACK', msg_2='O09', msg_3='ACK')
        msh.message_control_id = 'SACYL20241101093005003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'CA'
        msa.message_control_id = 'TAO20241101093000001'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/es/es-jimena.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='JIMENA')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='BBANK_SACYL')
        msh.receiving_facility = HD(hd_1='HCUVA')
        msh.date_time_of_message = '20241110090131'
        msh.message_type = MSG(msg_1='OMB', msg_2='O27', msg_3='OMB_O27')
        msh.message_control_id = 'SACYL20241110090131006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='HC003456', cx_4='HCUVA', cx_5='PI', cx_9='HCUVA&&99CENTROSACYL'),
            CX(cx_1='CACL456789123', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='44556677D', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='280045678901', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='ESPINO', xpn_2='JACINTO')
        pid.mothers_maiden_name = XPN(xpn_1='MOLINERO')
        pid.date_time_of_birth = '19820718'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(
            xad_1='CL&ERNESTO GUEVARA&202',
            xad_2='CENTRO SALUD',
            xad_3='470186',
            xad_4='47',
            xad_5='47048',
            xad_6='ESP',
            xad_7='H',
            xad_8='VALLADOLID',
        )
        pid.pid_13 = '^PRN^PH^^^983777223'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCI', pl_2='405', pl_3='C', pl_4='HCUVA')
        pv1.attending_doctor = XCN(xcn_1='77723456', xcn_2='RIBERA', xcn_3='CLEMENTE', xcn_4='DE PEDRAZA', xcn_9='MI')
        pv1.hospital_service = CWE(cwe_1='UCI')
        pv1.visit_number = CX(cx_1='2024111000001', cx_4='HOS', cx_5='VN', cx_9='HCUVA&&99CENTROSACYL')
        pv1.total_adjustments = '20241108200000'

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmbO27PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OmbO27Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_identifier = EIP(eip_1='SPM11234556')

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD11234556')
        orc.filler_order_number = EI(ei_1='BB11111222')
        orc.date_time_of_order_event = '20241110090000'
        orc.orc_12 = '77723456^RIBERA^CLEMENTE^DE PEDRAZA^^^^^MI'

        # .. build BPO ..
        bpo = BPO()
        bpo.set_id_bpo = '1'
        bpo.bp_universal_service_identifier = CWE(cwe_1='CHEM', cwe_2='Concentrado de Hematies', cwe_3='99BBANK')
        bpo.bp_processing_requirements = CWE(cwe_1='2')
        bpo.bp_amount = '2'
        bpo.bp_intended_use_date_time = '20241109200001'
        bpo.bp_intended_dispense_from_location = PL(pl_1='P121', pl_5='')
        bpo.bp_requested_dispense_date_time = '20241109211001'
        bpo.bp_requested_dispense_to_location = PL(pl_1='P121', pl_5='')

        # .. build BPO ..
        bpo_2 = BPO()
        bpo_2.set_id_bpo = '2'
        bpo_2.bp_universal_service_identifier = CWE(cwe_1='PQ', cwe_2='Pool Plaquetas', cwe_3='99BBANK')
        bpo_2.bp_processing_requirements = CWE(cwe_1='1')
        bpo_2.bp_amount = '1'
        bpo_2.bp_intended_use_date_time = '20241109120001'
        bpo_2.bp_intended_dispense_from_location = PL(pl_1='P121', pl_5='')
        bpo_2.bp_requested_dispense_date_time = '20241109211001'
        bpo_2.bp_requested_dispense_to_location = PL(pl_1='P121', pl_5='')

        # .. assemble the full message ..
        msg = OMB_O27()
        msg.msh = msh
        msg.patient = patient
        msg.extra_segments = [spm, orc, bpo, bpo_2]

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
    """ Based on live/es/es-jimena.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='JIMENA')
        msh.sending_facility = HD(hd_1='CAUSA')
        msh.receiving_application = HD(hd_1='LAB_SACYL')
        msh.receiving_facility = HD(hd_1='CAUSA')
        msh.date_time_of_message = '20241112081500'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'SACYL20241112081500007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CACL567891234', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='66778899E', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC005567', cx_4='CAUSA', cx_5='PI', cx_9='CAUSA&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='VALBUENA', xpn_2='LORETO')
        pid.mothers_maiden_name = XPN(xpn_1='PRESA')
        pid.date_time_of_birth = '19500219'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='PZ&MAYOR&3', xad_2='1B', xad_3='370186', xad_4='37', xad_5='37002', xad_6='ESP', xad_7='H', xad_8='SALAMANCA')
        pid.pid_13 = '^PRN^PH^^^923223344'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='101', pl_4='CAUSA')
        pv1.attending_doctor = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA', xcn_4='ZAMORA', xcn_9='MI')
        pv1.hospital_service = CWE(cwe_1='BIO')
        pv1.admit_source = CWE(cwe_1='CBIO')
        pv1.admitting_doctor = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA', xcn_4='ZAMORA', xcn_9='MI')
        pv1.patient_type = CWE(cwe_1='O')
        pv1.visit_number = CX(cx_1='2024111200001', cx_4='CEX', cx_5='VN', cx_9='CAUSA&&99CENTROSACYL')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO21PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='LABORD2024111200001', ei_3='JIMENA')
        orc.date_time_of_order_event = '20241112081500'
        orc.orc_12 = '33445566^MATEOS^JOSEFA^ZAMORA^^^^^MI'
        orc.orc_17 = 'BIO^BIOQUIMICA^99SVC'
        orc.orc_18 = '37001^Hospital Universitario de Salamanca^99CENTROSACYL'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LABORD2024111200001', ei_3='JIMENA')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Electrolitos basicos', cwe_3='LN')
        obr.observation_date_time = '20241112081500'
        obr.obr_16 = '33445566^MATEOS^JOSEFA^ZAMORA^^^^^MI'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='LABORD2024111200001', ei_3='JIMENA')
        obr_2.universal_service_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinina serica', cwe_3='LN')
        obr_2.observation_date_time = '20241112081500'
        obr_2.obr_16 = '33445566^MATEOS^JOSEFA^ZAMORA^^^^^MI'

        # .. build the ORDER_PRIOR group ..
        order_prior = OmlO21OrderPrior()
        order_prior.obr = obr_2

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='LABORD2024111200001', ei_3='JIMENA')
        obr_3.universal_service_identifier = CWE(cwe_1='2345-7', cwe_2='Glucosa', cwe_3='LN')
        obr_3.observation_date_time = '20241112081500'
        obr_3.obr_16 = '33445566^MATEOS^JOSEFA^ZAMORA^^^^^MI'

        # .. build the ORDER_PRIOR group ..
        order_prior_2 = OmlO21OrderPrior()
        order_prior_2.obr = obr_3

        # .. build the PRIOR_RESULT group ..
        prior_result = OmlO21PriorResult()
        prior_result.order_prior = order_prior
        prior_result.order_prior_2 = order_prior_2

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OmlO21ObservationRequest()
        observation_request.obr = obr
        observation_request.prior_result = prior_result

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc
        order.observation_request = observation_request

        # .. assemble the full message ..
        msg = OML_O21()
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
    """ Based on live/es/es-jimena.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SACYL')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='JIMENA')
        msh.receiving_facility = HD(hd_1='HCUVA')
        msh.date_time_of_message = '20241113143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20241113143000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CACL567891234', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='HC005567', cx_4='CAUSA', cx_5='PI', cx_9='CAUSA&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='ESPINO', xpn_2='JACINTO')
        pid.mothers_maiden_name = XPN(xpn_1='MOLINERO')
        pid.date_time_of_birth = '19820718'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='101', pl_4='CAUSA')
        pv1.attending_doctor = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA', xcn_4='ZAMORA', xcn_9='MI')
        pv1.pv1_20 = '2024111200001^^^CEX^VN^^^^CAUSA&&99CENTROSACYL'

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
        orc.placer_order_number = EI(ei_1='LABORD2024111200001', ei_3='JIMENA')
        orc.filler_order_number = EI(ei_1='LABRES2024111300001', ei_3='LAB_SACYL')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LABORD2024111200001', ei_3='JIMENA')
        obr.filler_order_number = EI(ei_1='LABRES2024111300001', ei_3='LAB_SACYL')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Hemograma completo', cwe_3='LN')
        obr.observation_date_time = '20241113100000'
        obr.results_rpt_status_chng_date_time = '20241113143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobina', cwe_3='LN')
        obx.obx_5 = '13.5'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '13.0 - 17.5'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241113140000'
        obx.responsible_observer = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='787-2', cwe_2='Eritrocitos', cwe_3='LN')
        obx_2.obx_5 = '4.52'
        obx_2.units = CWE(cwe_1='x10E12/L')
        obx_2.reference_range = '4.50 - 5.90'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241113140000'
        obx_2.responsible_observer = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocitos', cwe_3='LN')
        obx_3.obx_5 = '7.2'
        obx_3.units = CWE(cwe_1='x10E9/L')
        obx_3.reference_range = '4.5 - 11.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20241113140000'
        obx_3.responsible_observer = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA')

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='777-3', cwe_2='Plaquetas', cwe_3='LN')
        obx_4.obx_5 = '245'
        obx_4.units = CWE(cwe_1='x10E9/L')
        obx_4.reference_range = '150 - 400'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20241113140000'
        obx_4.responsible_observer = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA')

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrito', cwe_3='LN')
        obx_5.obx_5 = '40.1'
        obx_5.units = CWE(cwe_1='%')
        obx_5.reference_range = '39.0 - 49.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20241113140000'
        obx_5.responsible_observer = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA')

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
    """ Based on live/es/es-jimena.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SACYL')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='JIMENA')
        msh.receiving_facility = HD(hd_1='HCUVA')
        msh.date_time_of_message = '20241115101500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20241115101500009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CACL456789123', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='HC004680', cx_4='CAULE', cx_5='PI', cx_9='CAULE&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='OCANA', xpn_2='ADELA')
        pid.mothers_maiden_name = XPN(xpn_1='GRANADOS')
        pid.date_time_of_birth = '19740512'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEURO', pl_2='402', pl_3='A', pl_4='CAULE')
        pv1.attending_doctor = XCN(xcn_1='22334455', xcn_2='PAREDES', xcn_3='BRAULIO', xcn_4='GALVAN', xcn_9='MI')
        pv1.pv1_20 = '2024110300001^^^HOS^VN^^^^CAULE&&99CENTROSACYL'

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
        orc.placer_order_number = EI(ei_1='LABORD2024111400001', ei_3='JIMENA')
        orc.filler_order_number = EI(ei_1='MICRO2024111500001', ei_3='LAB_SACYL')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LABORD2024111400001', ei_3='JIMENA')
        obr.filler_order_number = EI(ei_1='MICRO2024111500001', ei_3='LAB_SACYL')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Urocultivo', cwe_3='LN')
        obr.observation_date_time = '20241114080000'
        obr.results_rpt_status_chng_date_time = '20241115101500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='11475-1', cwe_2='Microorganismo aislado', cwe_3='LN')
        obx.obx_5 = '112283005^Escherichia coli^SCT'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241115100000'
        obx.responsible_observer = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Antibiograma comentario', cwe_3='LN')
        obx_2.obx_5 = 'Sensible a Amoxicilina/Clavulanico, Ciprofloxacino. Resistente a Ampicilina.'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241115100000'
        obx_2.responsible_observer = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='30145-4', cwe_2='Recuento colonias', cwe_3='LN')
        obx_3.obx_5 = '>100000'
        obx_3.units = CWE(cwe_1='UFC/mL')
        obx_3.reference_range = '<10000'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20241115100000'
        obx_3.responsible_observer = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA')

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
    """ Based on live/es/es-jimena.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='JIMENA')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='RIS_SACYL')
        msh.receiving_facility = HD(hd_1='HCUVA')
        msh.date_time_of_message = '20241118085900'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SACYL20241118085900010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CACL887766554', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='88776655F', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC006789', cx_4='HCUVA', cx_5='PI', cx_9='HCUVA&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='TAMAYO', xpn_2='SOLEDAD')
        pid.mothers_maiden_name = XPN(xpn_1='BECERRA')
        pid.date_time_of_birth = '19850911'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADI', pl_2='001', pl_4='HCUVA')
        pv1.attending_doctor = XCN(xcn_1='55667788', xcn_2='HUERTAS', xcn_3='RODRIGO', xcn_4='DUENAS', xcn_9='MI')

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
        orc.placer_order_number = EI(ei_1='RADORD2024111800001', ei_3='JIMENA')
        orc.date_time_of_order_event = '20241118085900'
        orc.orc_12 = '55667788^HUERTAS^RODRIGO^DUENAS^^^^^MI'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RADORD2024111800001', ei_3='JIMENA')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='RADIOGRAFIA TORAX PA Y LATERAL', cwe_3='LN')
        obr.observation_date_time = '20241118085900'
        obr.obr_16 = '55667788^HUERTAS^RODRIGO^DUENAS^^^^^MI'
        obr.obr_27 = '^^^^^1'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

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
    """ Based on live/es/es-jimena.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_SACYL')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='JIMENA')
        msh.receiving_facility = HD(hd_1='HCUVA')
        msh.date_time_of_message = '20241119112000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RIS20241119112000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CACL887766554', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='HC006789', cx_4='HCUVA', cx_5='PI', cx_9='HCUVA&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='TAMAYO', xpn_2='SOLEDAD')
        pid.mothers_maiden_name = XPN(xpn_1='BECERRA')
        pid.date_time_of_birth = '19850911'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADI', pl_2='001', pl_4='HCUVA')
        pv1.attending_doctor = XCN(xcn_1='55667788', xcn_2='HUERTAS', xcn_3='RODRIGO', xcn_4='DUENAS', xcn_9='MI')
        pv1.pv1_20 = '2024111800001^^^CEX^VN^^^^HCUVA&&99CENTROSACYL'

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
        orc.placer_order_number = EI(ei_1='RADORD2024111800001', ei_3='JIMENA')
        orc.filler_order_number = EI(ei_1='RADRES2024111900001', ei_3='RIS_SACYL')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RADORD2024111800001', ei_3='JIMENA')
        obr.filler_order_number = EI(ei_1='RADRES2024111900001', ei_3='RIS_SACYL')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='RADIOGRAFIA TORAX PA Y LATERAL', cwe_3='LN')
        obr.observation_date_time = '20241119100000'
        obr.results_rpt_status_chng_date_time = '20241119112000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='71020', cwe_2='Radiografia torax', cwe_3='LN')
        obx.obx_5 = 'Sin hallazgos patologicos significativos. Silueta cardiaca de tamano normal. Campos pulmonares libres.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241119110000'
        obx.responsible_observer = XCN(xcn_1='55667788', xcn_2='HUERTAS', xcn_3='RODRIGO')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Informe de resultados de laboratorio', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKEluZm9ybWUgUmFkaW9sb2dp'
            'YSBTQUNZTCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250IC9TdWJ0eXBlIC9UeXBlMSAvQmFzZUZvbnQgL0hlbHZldGljYSA+PgplbmRvYmoKeHJl'
            'ZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNjUgMDAwMDAgbiAKMDAwMDAwMDEyMiAwMDAwMCBuIAowMDAwMDAwMjk2IDAwMDAwIG4g'
            'CjAwMDAwMDAzOTMgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgo0NzYKJSVFT0Y='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241119112000'
        obx_2.responsible_observer = XCN(xcn_1='55667788', xcn_2='HUERTAS', xcn_3='RODRIGO')

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
    """ Based on live/es/es-jimena.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SACYL')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='JIMENA')
        msh.receiving_facility = HD(hd_1='HCUVA')
        msh.date_time_of_message = '20241120153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20241120153000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CACL678912345', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='HC007891', cx_4='HCUVA', cx_5='PI', cx_9='HCUVA&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='ZAMORANO', xpn_2='LEOPOLDO')
        pid.mothers_maiden_name = XPN(xpn_1='CALZADA')
        pid.date_time_of_birth = '19700327'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CIRGEN', pl_2='503', pl_3='A', pl_4='HCUVA')
        pv1.attending_doctor = XCN(xcn_1='66778899', xcn_2='TEJERO', xcn_3='MARCELINA', xcn_4='VILLALBA', xcn_9='MI')
        pv1.pv1_20 = '2024111800001^^^HOS^VN^^^^HCUVA&&99CENTROSACYL'

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
        orc.placer_order_number = EI(ei_1='LABORD2024111900001', ei_3='JIMENA')
        orc.filler_order_number = EI(ei_1='ANAT2024112000001', ei_3='LAB_SACYL')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LABORD2024111900001', ei_3='JIMENA')
        obr.filler_order_number = EI(ei_1='ANAT2024112000001', ei_3='LAB_SACYL')
        obr.universal_service_identifier = CWE(cwe_1='11529-5', cwe_2='Informe de anatomia patologica', cwe_3='LN')
        obr.observation_date_time = '20241119120000'
        obr.results_rpt_status_chng_date_time = '20241120153000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Diagnostico anatomopatologico', cwe_3='LN')
        obx.obx_5 = 'Adenocarcinoma de colon, moderadamente diferenciado. Margen de reseccion libre.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241120150000'
        obx.responsible_observer = XCN(xcn_1='66778899', xcn_2='TEJERO', xcn_3='MARCELINA')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='18630-4', cwe_2='Diagnostico principal', cwe_3='LN')
        obx_2.obx_5 = '153.2^Neoplasia maligna de colon ascendente^I9C'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241120150000'
        obx_2.responsible_observer = XCN(xcn_1='66778899', xcn_2='TEJERO', xcn_3='MARCELINA')

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
    """ Based on live/es/es-jimena.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SACYL')
        msh.sending_facility = HD(hd_1='CAUSA')
        msh.receiving_application = HD(hd_1='JIMENA')
        msh.receiving_facility = HD(hd_1='CAUSA')
        msh.date_time_of_message = '20241122094500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20241122094500013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CACL789123456', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='HC008901', cx_4='CAUSA', cx_5='PI', cx_9='CAUSA&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='TORRECILLA', xpn_2='YOLANDA')
        pid.mothers_maiden_name = XPN(xpn_1='CEBRIAN')
        pid.date_time_of_birth = '19770605'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='102', pl_4='CAUSA')
        pv1.attending_doctor = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA', xcn_4='ZAMORA', xcn_9='MI')
        pv1.pv1_20 = '2024112100001^^^CEX^VN^^^^CAUSA&&99CENTROSACYL'

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
        orc.placer_order_number = EI(ei_1='LABORD2024112100001', ei_3='JIMENA')
        orc.filler_order_number = EI(ei_1='LABRES2024112200001', ei_3='LAB_SACYL')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LABORD2024112100001', ei_3='JIMENA')
        obr.filler_order_number = EI(ei_1='LABRES2024112200001', ei_3='LAB_SACYL')
        obr.universal_service_identifier = CWE(cwe_1='2731-8', cwe_2='Electroforesis proteinas sericas', cwe_3='LN')
        obr.observation_date_time = '20241122080000'
        obr.results_rpt_status_chng_date_time = '20241122094500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2731-8', cwe_2='Albumina', cwe_3='LN')
        obx.obx_5 = '4.2'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '3.5 - 5.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241122090000'
        obx.responsible_observer = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2732-6', cwe_2='Alfa-1 globulina', cwe_3='LN')
        obx_2.obx_5 = '0.3'
        obx_2.units = CWE(cwe_1='g/dL')
        obx_2.reference_range = '0.1 - 0.3'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241122090000'
        obx_2.responsible_observer = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2733-4', cwe_2='Alfa-2 globulina', cwe_3='LN')
        obx_3.obx_5 = '0.8'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '0.6 - 1.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20241122090000'
        obx_3.responsible_observer = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA')

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2734-2', cwe_2='Beta globulina', cwe_3='LN')
        obx_4.obx_5 = '0.9'
        obx_4.units = CWE(cwe_1='g/dL')
        obx_4.reference_range = '0.7 - 1.2'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20241122090000'
        obx_4.responsible_observer = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA')

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2735-9', cwe_2='Gamma globulina', cwe_3='LN')
        obx_5.obx_5 = '1.1'
        obx_5.units = CWE(cwe_1='g/dL')
        obx_5.reference_range = '0.7 - 1.6'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20241122090000'
        obx_5.responsible_observer = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA')

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ED'
        obx_6.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Informe de resultados analiticos', cwe_3='LN')
        obx_6.obx_5 = (
            '^image^png^Base64^'
            'iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAABGdBTUEAALGPC/xhBQAAAAlwSFlzAAAOwQAADsEBuJFr7QAAABl0RVh0U29mdHdhcmUAcGFpbnQubmV0IDQuMC4xNkRp'
            'r/UAAAB+UExURf///+/v7+fn5+Hh4dvb28/Pz8PDw7u7u7Ozs6urq6Ojo5ubm5OTk4uLi4ODg3t7e3Nzc2tra2NjY1tbW1NTU0tLS0NDQzs7Ozc3NzMzMyMjIx8fHx0dHRkZGRcXFxQU'
            'FBMTExISEhAQEA8PDw4ODg0NDQwMDAoKCgkJCQgICAcHBwAAAHCkOCoAAACDklEQVR42u3d63KCMBAFYKJUqYq1tV7b+v4P2ZVL2M1uYkDnD98MAwN7TgKE0PQyS4dhCqYxxlyyOHiS5'
            'TI3+/tDY2ArJhtsOaHGptU4j6mMNcYbFOhPnbw3uI+x7UHN93/ekgDwEwB+AsA3iScAfBz/8bAqwM8DPICfB3gAPw/wAHYCLCfa3rS/6e3WZ7Zd/P6PBD8B4CcA/ASAnwDwEwB+As5Os'
            'J9ofwOoAXcW8Ax+HuAB/DzAA/h5gAfw8wAP4OcBHsDPAzyAnwd4AD8P8AB+HuAB/DzAA/h5gAeYDnA45wDnE/0cwLOAZ/DzAA/g5wEewM8DPICfB3gAPw/wAH4e4AH8PEAGuBkdsAY/D'
            '/AAfh7gAfw8wAP4eYAH8PMAD+DnAR7AzwM8gJ8HeAA/D/AAfh7gAfw8wAP4eYAHSAK2o+9iA/4UwDf4eYAH8PMAD+DnAR7AzwM8gJ8HeAA/D/AA'
        )
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20241122093000'
        obx_6.responsible_observer = XCN(xcn_1='33445566', xcn_2='MATEOS', xcn_3='JOSEFA')

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
    """ Based on live/es/es-jimena.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='JIMENA')
        msh.sending_facility = HD(hd_1='CAULE')
        msh.receiving_application = HD(hd_1='LAB_SACYL')
        msh.receiving_facility = HD(hd_1='CAULE')
        msh.date_time_of_message = '20241125073000'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'SACYL20241125073000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CACL891234567', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='77889900G', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC009012', cx_4='CAULE', cx_5='PI', cx_9='CAULE&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='COVARRUBIAS', xpn_2='RAMON')
        pid.mothers_maiden_name = XPN(xpn_1='SALCEDO')
        pid.date_time_of_birth = '19920108'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&SAN CLAUDIO&8', xad_2='5A', xad_3='240089', xad_4='24', xad_5='24002', xad_6='ESP', xad_7='H', xad_8='LEON')
        pid.pid_13 = '^PRN^PH^^^987445566'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MINTER', pl_2='201', pl_3='B', pl_4='CAULE')
        pv1.attending_doctor = XCN(xcn_1='66778899', xcn_2='TEJERO', xcn_3='MARCELINA', xcn_4='VILLALBA', xcn_9='MI')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='IMED')
        pv1.admitting_doctor = XCN(xcn_1='66778899', xcn_2='TEJERO', xcn_3='MARCELINA', xcn_4='VILLALBA', xcn_9='MI')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='2024112400001', cx_4='HOS', cx_5='VN', cx_9='CAULE&&99CENTROSACYL')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO21PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='LABORD2024112500001', ei_3='JIMENA')
        orc.date_time_of_order_event = '20241125073000'
        orc.orc_12 = '66778899^TEJERO^MARCELINA^VILLALBA^^^^^MI'
        orc.orc_17 = 'MED^MEDICINA INTERNA^99SVC'
        orc.orc_18 = '24001^Hospital de Leon^99CENTROSACYL'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LABORD2024112500001', ei_3='JIMENA')
        obr.universal_service_identifier = CWE(cwe_1='600-7', cwe_2='Hemocultivo', cwe_3='LN')
        obr.observation_date_time = '20241125073000'
        obr.obr_16 = '66778899^TEJERO^MARCELINA^VILLALBA^^^^^MI'

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_type = CWE(cwe_1='BLD', cwe_2='Blood', cwe_3='HL70487')

        # .. build the SPECIMEN group ..
        specimen = OmlO21Specimen()
        specimen.spm = spm

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OmlO21ObservationRequest()
        observation_request.obr = obr
        observation_request.specimen = specimen

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc
        order.observation_request = observation_request

        # .. assemble the full message ..
        msg = OML_O21()
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
    """ Based on live/es/es-jimena.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='JIMENA')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='MPI_SACYL')
        msh.receiving_facility = HD(hd_1='GRS_SACYL')
        msh.date_time_of_message = '20241128101935'
        msh.message_type = MSG(msg_1='QBP', msg_2='Q22', msg_3='QBP_Q21')
        msh.message_control_id = 'SACYL20241128101935015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='1', cwe_2='IHE PDQ Query', cwe_3='HL70471')
        qpd.query_tag = 'QRY20241128001'
        qpd.qpd_3 = '@PID.3.1^CACL887766554~@PID.3.4.1^CACL~@PID.3.5^JHN'

        # .. build RCP ..
        rcp = RCP()
        rcp.query_priority = 'I'
        rcp.quantity_limited_request = CQ(cq_1='20', cq_2='RD&Records&HL70126')

        # .. assemble the full message ..
        msg = QBP_Q21()
        msg.msh = msh
        msg.qpd = qpd
        msg.rcp = rcp

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
    """ Based on live/es/es-jimena.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MPI_SACYL')
        msh.sending_facility = HD(hd_1='GRS_SACYL')
        msh.receiving_application = HD(hd_1='JIMENA')
        msh.receiving_facility = HD(hd_1='HCUVA')
        msh.date_time_of_message = '20241128101936'
        msh.message_type = MSG(msg_1='RSP', msg_2='K22', msg_3='RSP_K21')
        msh.message_control_id = 'SACYL20241128101936016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'SACYL20241128101935015'

        # .. build QAK ..
        qak = QAK()
        qak.query_tag = 'QRY20241128001'
        qak.query_response_status = 'OK'

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='1', cwe_2='IHE PDQ Query', cwe_3='HL70471')
        qpd.query_tag = 'QRY20241128001'
        qpd.qpd_3 = '@PID.3.1^CACL887766554~@PID.3.4.1^CACL~@PID.3.5^JHN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CACL887766554', cx_4='CACL', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='88776655F', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC006789', cx_4='HCUVA', cx_5='PI', cx_9='HCUVA&&99CENTROSACYL'),
        ]
        pid.patient_name = XPN(xpn_1='TAMAYO', xpn_2='SOLEDAD')
        pid.mothers_maiden_name = XPN(xpn_1='BECERRA')
        pid.date_time_of_birth = '19850911'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(
            xad_1='CL&PASEO ZORRILLA&45',
            xad_2='3B',
            xad_3='470186',
            xad_4='47',
            xad_5='47002',
            xad_6='ESP',
            xad_7='H',
            xad_8='VALLADOLID',
        )
        pid.pid_13 = '^PRN^PH^^^983778899~^PRN^CP^^^666223344'
        pid.pid_19 = 'ESP^Espana^ISO3166'

        # .. build QRI ..
        qri = QRI()
        qri.candidate_confidence = '100'

        # .. build the QUERY_RESPONSE group ..
        query_response = RspK21QueryResponse()
        query_response.pid = pid
        query_response.qri = qri

        # .. assemble the full message ..
        msg = RSP_K21()
        msg.msh = msh
        msg.msa = msa
        msg.qak = qak
        msg.qpd = qpd
        msg.query_response = query_response

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
