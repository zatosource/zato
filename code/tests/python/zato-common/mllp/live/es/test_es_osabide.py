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
    OmlO21OrderPrior, OmlO21Patient, OmlO21PatientVisit, OmlO21PriorResult, OmpO09Observation, OmpO09Order, OmpO09Patient, OmpO09PatientVisit, OmpO09Timing, \
    OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, \
    OruR01PatientResult, OruR01Visit, RspK21QueryResponse
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A39, OMB_O27, OML_O21, OMP_O09, ORM_O01, ORU_R01, QBP_Q21, RSP_K21
from zato.hl7v2.v2_9.segments import BPO, EVN, IN1, MRG, MSA, MSH, OBR, OBX, ORC, PID, PV1, PV2, QAK, QPD, QRI, RCP, RXO, RXR, SPM, TQ1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('es', 'es-osabide.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/es/es-osabide.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EOSABIDE')
        msh.sending_facility = HD(hd_1='HBASURTO')
        msh.receiving_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.receiving_facility = HD(hd_1='OSK')
        msh.date_time_of_message = '20241015084500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'OSK20241015084500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20241015084300'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2031934745', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='31934745B', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='4831934745901', cx_4='MS', cx_5='HC', cx_9='ESP&&ISO3166'),
            CX(cx_1='480319347451', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
            CX(cx_1='NHC031934', cx_4='HBASURTO', cx_5='PI', cx_9='HBASURTO&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='ETXEBARRIA', xpn_2='ANDER')
        pid.mothers_maiden_name = XPN(xpn_1='AGIRREZABAL')
        pid.date_time_of_birth = '19820713'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&GRAN VIA&48', xad_2='3D', xad_3='480200', xad_4='48', xad_5='48010', xad_6='ESP', xad_7='H', xad_8='BILBAO')
        pid.pid_13 = '^PRN^PH^^^944671823~^PRN^CP^^^688371245'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MINTER', pl_2='301', pl_3='A', pl_4='HBASURTO')
        pv1.attending_doctor = XCN(xcn_1='71829456', xcn_2='GAZTANAGA', xcn_3='AINHOA', xcn_4='LAZKANO', xcn_9='MI')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='IMED')
        pv1.admitting_doctor = XCN(xcn_1='71829456', xcn_2='GAZTANAGA', xcn_3='AINHOA', xcn_4='LAZKANO', xcn_9='MI')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='2024101500001', cx_4='HOS', cx_5='VN', cx_9='HBASURTO&&99CENTROSK')
        pv1.total_adjustments = '20241015084500'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SNS', cwe_3='HL70072')
        in1.insurance_company_id = CX(cx_1='OSAKIDETZA001')
        in1.insurance_company_name = XON(xon_1='OSAKIDETZA-SERVICIO VASCO DE SALUD')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20251231'
        in1.policy_number = 'CAPV2031934745'

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
    """ Based on live/es/es-osabide.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EOSABIDE')
        msh.sending_facility = HD(hd_1='HBASURTO')
        msh.receiving_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.receiving_facility = HD(hd_1='OSK')
        msh.date_time_of_message = '20241018140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'OSK20241018140000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20241018135800'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2031934745', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='31934745B', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='NHC031934', cx_4='HBASURTO', cx_5='PI', cx_9='HBASURTO&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='ETXEBARRIA', xpn_2='ANDER')
        pid.mothers_maiden_name = XPN(xpn_1='AGIRREZABAL')
        pid.date_time_of_birth = '19820713'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&GRAN VIA&48', xad_2='3D', xad_3='480200', xad_4='48', xad_5='48010', xad_6='ESP', xad_7='H', xad_8='BILBAO')
        pid.pid_13 = '^PRN^PH^^^944671823'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCI', pl_2='101', pl_3='A', pl_4='HBASURTO')
        pv1.attending_doctor = XCN(xcn_1='83934146', xcn_2='ARIZAGA', xcn_3='GORKA', xcn_4='URRUTIA', xcn_9='MI')
        pv1.hospital_service = CWE(cwe_1='UCI')
        pv1.admit_source = CWE(cwe_1='IUCI')
        pv1.admitting_doctor = XCN(xcn_1='83934146', xcn_2='ARIZAGA', xcn_3='GORKA', xcn_4='URRUTIA', xcn_9='MI')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='2024101500001', cx_4='HOS', cx_5='VN', cx_9='HBASURTO&&99CENTROSK')
        pv1.pv1_25 = 'MINTER^301^A^HBASURTO'
        pv1.total_adjustments = '20241015084500'

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
    """ Based on live/es/es-osabide.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EOSABIDE')
        msh.sending_facility = HD(hd_1='HBASURTO')
        msh.receiving_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.receiving_facility = HD(hd_1='OSK')
        msh.date_time_of_message = '20241025110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'OSK20241025110000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20241025105800'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2031934745', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='31934745B', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='NHC031934', cx_4='HBASURTO', cx_5='PI', cx_9='HBASURTO&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='ETXEBARRIA', xpn_2='ANDER')
        pid.mothers_maiden_name = XPN(xpn_1='AGIRREZABAL')
        pid.date_time_of_birth = '19820713'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&GRAN VIA&48', xad_2='3D', xad_3='480200', xad_4='48', xad_5='48010', xad_6='ESP', xad_7='H', xad_8='BILBAO')
        pid.pid_13 = '^PRN^PH^^^944671823'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCI', pl_2='101', pl_3='A', pl_4='HBASURTO')
        pv1.attending_doctor = XCN(xcn_1='83934146', xcn_2='ARIZAGA', xcn_3='GORKA', xcn_4='URRUTIA', xcn_9='MI')
        pv1.hospital_service = CWE(cwe_1='UCI')
        pv1.admit_source = CWE(cwe_1='IUCI')
        pv1.admitting_doctor = XCN(xcn_1='83934146', xcn_2='ARIZAGA', xcn_3='GORKA', xcn_4='URRUTIA', xcn_9='MI')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='2024101500001', cx_4='HOS', cx_5='VN', cx_9='HBASURTO&&99CENTROSK')
        pv1.total_adjustments = '20241015084500'
        pv1.total_payments = '20241025110000'

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
    """ Based on live/es/es-osabide.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EOSABIDE')
        msh.sending_facility = HD(hd_1='HARABA')
        msh.receiving_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.receiving_facility = HD(hd_1='OSK')
        msh.date_time_of_message = '20241026091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'OSK20241026091500004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20241026091400'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2093618274', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='62481937C', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='4893618274101', cx_4='MS', cx_5='HC', cx_9='ESP&&ISO3166'),
            CX(cx_1='480936182741', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
            CX(cx_1='NHC093618', cx_4='HARABA', cx_5='PI', cx_9='HARABA&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='MENDIOLA', xpn_2='LEIRE')
        pid.mothers_maiden_name = XPN(xpn_1='ARANTZAMENDI')
        pid.date_time_of_birth = '19930508'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(
            xad_1='AV&SANCHO EL SABIO&22',
            xad_2='5C',
            xad_3='010059',
            xad_4='1',
            xad_5='01005',
            xad_6='ESP',
            xad_7='H',
            xad_8='VITORIA-GASTEIZ',
        )
        pid.pid_13 = '^PRN^PH^^^945283716~^PRN^CP^^^677194823~^PRN^Internet^leire.mendiola@correo.eus'
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
    """ Based on live/es/es-osabide.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EOSABIDE')
        msh.sending_facility = HD(hd_1='HGALDAKAO')
        msh.receiving_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.receiving_facility = HD(hd_1='OSK')
        msh.date_time_of_message = '20241028112947'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'OSK20241028112947005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20241028112947'
        evn.operator_id = XCN(xcn_1='EOSABIDE')
        evn.event_occurred = '20241028112947'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2058291473', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='84713926D', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='NHC058291', cx_4='HGALDAKAO', cx_5='PI', cx_9='HGALDAKAO&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='GOIKOETXEA', xpn_2='UNAI', xpn_3='JOKIN')
        pid.date_time_of_birth = '19880921'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&LEHENDAKARI AGUIRRE&15', xad_3='480680', xad_4='48', xad_5='48170', xad_6='ESP', xad_7='H', xad_8='ZAMUDIO')
        pid.pid_13 = '^PRN^PH^^^944827361~^PRN^CP^^^611493827'
        pid.patient_death_date_and_time = 'N'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = [
            CX(cx_1='NHC058292', cx_4='HGALDAKAO', cx_5='PI', cx_9='HGALDAKAO&&99CENTROSK'),
            CX(cx_1='CAPV2058291474', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
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
    """ Based on live/es/es-osabide.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.sending_facility = HD(hd_1='HBASURTO')
        msh.receiving_application = HD(hd_1='GESTLAB')
        msh.receiving_facility = HD(hd_1='OSK_LAB')
        msh.date_time_of_message = '20241101081500'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'OSK20241101081500006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2046139782', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='19372846E', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='NHC046139', cx_4='HBASURTO', cx_5='PI', cx_9='HBASURTO&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='ARANBURU', xpn_2='IKER')
        pid.mothers_maiden_name = XPN(xpn_1='ZUBIZARRETA')
        pid.date_time_of_birth = '19680129'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&ALAMEDA URQUIJO&36', xad_2='2A', xad_3='480130', xad_4='48', xad_5='48008', xad_6='ESP', xad_7='H', xad_8='BILBAO')
        pid.pid_13 = '^PRN^PH^^^944516273'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='201', pl_4='HBASURTO')
        pv1.attending_doctor = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN', xcn_4='ELORTZA', xcn_9='MI')
        pv1.hospital_service = CWE(cwe_1='BIO')
        pv1.admit_source = CWE(cwe_1='CBIO')
        pv1.admitting_doctor = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN', xcn_4='ELORTZA', xcn_9='MI')
        pv1.patient_type = CWE(cwe_1='O')
        pv1.visit_number = CX(cx_1='2024110100001', cx_4='CEX', cx_5='VN', cx_9='HBASURTO&&99CENTROSK')

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
        orc.placer_order_number = EI(ei_1='LABORD2024110100001', ei_3='OSABIDE_GLOBAL')
        orc.date_time_of_order_event = '20241101081500'
        orc.orc_12 = '72953138^BERASATEGI^MIREN^ELORTZA^^^^^MI'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LABORD2024110100001', ei_3='OSABIDE_GLOBAL')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Electrolitos basicos', cwe_3='LN')
        obr.observation_date_time = '20241101081500'
        obr.obr_16 = '72953138^BERASATEGI^MIREN^ELORTZA^^^^^MI'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='LABORD2024110100001', ei_3='OSABIDE_GLOBAL')
        obr_2.universal_service_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinina serica', cwe_3='LN')
        obr_2.observation_date_time = '20241101081500'
        obr_2.obr_16 = '72953138^BERASATEGI^MIREN^ELORTZA^^^^^MI'

        # .. build the ORDER_PRIOR group ..
        order_prior = OmlO21OrderPrior()
        order_prior.obr = obr_2

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='LABORD2024110100001', ei_3='OSABIDE_GLOBAL')
        obr_3.universal_service_identifier = CWE(cwe_1='1742-6', cwe_2='ALT (GPT)', cwe_3='LN')
        obr_3.observation_date_time = '20241101081500'
        obr_3.obr_16 = '72953138^BERASATEGI^MIREN^ELORTZA^^^^^MI'

        # .. build the ORDER_PRIOR group ..
        order_prior_2 = OmlO21OrderPrior()
        order_prior_2.obr = obr_3

        # .. build OBR ..
        obr_4 = OBR()
        obr_4.set_id_obr = '4'
        obr_4.placer_order_number = EI(ei_1='LABORD2024110100001', ei_3='OSABIDE_GLOBAL')
        obr_4.universal_service_identifier = CWE(cwe_1='2345-7', cwe_2='Glucosa', cwe_3='LN')
        obr_4.observation_date_time = '20241101081500'
        obr_4.obr_16 = '72953138^BERASATEGI^MIREN^ELORTZA^^^^^MI'

        # .. build the ORDER_PRIOR group ..
        order_prior_3 = OmlO21OrderPrior()
        order_prior_3.obr = obr_4

        # .. build the PRIOR_RESULT group ..
        prior_result = OmlO21PriorResult()
        prior_result.order_prior = order_prior
        prior_result.order_prior_2 = order_prior_2
        prior_result.order_prior_3 = order_prior_3

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
    """ Based on live/es/es-osabide.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GESTLAB')
        msh.sending_facility = HD(hd_1='OSK_LAB')
        msh.receiving_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.receiving_facility = HD(hd_1='HBASURTO')
        msh.date_time_of_message = '20241102143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20241102143000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2046139782', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='NHC046139', cx_4='HBASURTO', cx_5='PI', cx_9='HBASURTO&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='ARANBURU', xpn_2='IKER')
        pid.mothers_maiden_name = XPN(xpn_1='ZUBIZARRETA')
        pid.date_time_of_birth = '19680129'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='201', pl_4='HBASURTO')
        pv1.attending_doctor = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN', xcn_4='ELORTZA', xcn_9='MI')
        pv1.pv1_20 = '2024110100001^^^CEX^VN^^^^HBASURTO&&99CENTROSK'

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
        orc.placer_order_number = EI(ei_1='LABORD2024110100001', ei_3='OSABIDE_GLOBAL')
        orc.filler_order_number = EI(ei_1='LABRES2024110200001', ei_3='GESTLAB')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LABORD2024110100001', ei_3='OSABIDE_GLOBAL')
        obr.filler_order_number = EI(ei_1='LABRES2024110200001', ei_3='GESTLAB')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Electrolitos basicos', cwe_3='LN')
        obr.observation_date_time = '20241102100000'
        obr.results_rpt_status_chng_date_time = '20241102143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodio', cwe_3='LN')
        obx.obx_5 = '141'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '136 - 145'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241102140000'
        obx.responsible_observer = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potasio', cwe_3='LN')
        obx_2.obx_5 = '4.3'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '3.5 - 5.1'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241102140000'
        obx_2.responsible_observer = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2075-0', cwe_2='Cloro', cwe_3='LN')
        obx_3.obx_5 = '103'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '98 - 107'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20241102140000'
        obx_3.responsible_observer = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN')

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinina', cwe_3='LN')
        obx_4.obx_5 = '0.95'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '0.70 - 1.20'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20241102140000'
        obx_4.responsible_observer = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN')

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT (GPT)', cwe_3='LN')
        obx_5.obx_5 = '28'
        obx_5.units = CWE(cwe_1='U/L')
        obx_5.reference_range = '7 - 56'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20241102140000'
        obx_5.responsible_observer = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN')

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucosa', cwe_3='LN')
        obx_6.obx_5 = '98'
        obx_6.units = CWE(cwe_1='mg/dL')
        obx_6.reference_range = '74 - 106'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20241102140000'
        obx_6.responsible_observer = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN')

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
    """ Based on live/es/es-osabide.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GESTLAB')
        msh.sending_facility = HD(hd_1='OSK_LAB')
        msh.receiving_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.receiving_facility = HD(hd_1='HBASURTO')
        msh.date_time_of_message = '20241103111500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20241103111500008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2031934745', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='NHC031934', cx_4='HBASURTO', cx_5='PI', cx_9='HBASURTO&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='ETXEBARRIA', xpn_2='ANDER')
        pid.mothers_maiden_name = XPN(xpn_1='AGIRREZABAL')
        pid.date_time_of_birth = '19820713'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCI', pl_2='101', pl_3='A', pl_4='HBASURTO')
        pv1.attending_doctor = XCN(xcn_1='83934146', xcn_2='ARIZAGA', xcn_3='GORKA', xcn_4='URRUTIA', xcn_9='MI')
        pv1.pv1_20 = '2024101500001^^^HOS^VN^^^^HBASURTO&&99CENTROSK'

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
        orc.placer_order_number = EI(ei_1='LABORD2024110300001', ei_3='OSABIDE_GLOBAL')
        orc.filler_order_number = EI(ei_1='LABRES2024110300001', ei_3='GESTLAB')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LABORD2024110300001', ei_3='OSABIDE_GLOBAL')
        obr.filler_order_number = EI(ei_1='LABRES2024110300001', ei_3='GESTLAB')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Hemograma completo', cwe_3='LN')
        obr.observation_date_time = '20241103080000'
        obr.results_rpt_status_chng_date_time = '20241103111500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobina', cwe_3='LN')
        obx.obx_5 = '10.2'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '13.0 - 17.5'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241103110000'
        obx.responsible_observer = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='787-2', cwe_2='Eritrocitos', cwe_3='LN')
        obx_2.obx_5 = '3.41'
        obx_2.units = CWE(cwe_1='x10E12/L')
        obx_2.reference_range = '4.50 - 5.90'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241103110000'
        obx_2.responsible_observer = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocitos', cwe_3='LN')
        obx_3.obx_5 = '14.8'
        obx_3.units = CWE(cwe_1='x10E9/L')
        obx_3.reference_range = '4.5 - 11.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20241103110000'
        obx_3.responsible_observer = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN')

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='777-3', cwe_2='Plaquetas', cwe_3='LN')
        obx_4.obx_5 = '178'
        obx_4.units = CWE(cwe_1='x10E9/L')
        obx_4.reference_range = '150 - 400'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20241103110000'
        obx_4.responsible_observer = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN')

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrito', cwe_3='LN')
        obx_5.obx_5 = '31.2'
        obx_5.units = CWE(cwe_1='%')
        obx_5.reference_range = '39.0 - 49.0'
        obx_5.interpretation_codes = CWE(cwe_1='L')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20241103110000'
        obx_5.responsible_observer = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN')

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
    """ Based on live/es/es-osabide.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GESTLAB')
        msh.sending_facility = HD(hd_1='OSK_LAB')
        msh.receiving_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.receiving_facility = HD(hd_1='HARABA')
        msh.date_time_of_message = '20241108101500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20241108101500009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2093618274', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='NHC093618', cx_4='HARABA', cx_5='PI', cx_9='HARABA&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='MENDIOLA', xpn_2='LEIRE')
        pid.mothers_maiden_name = XPN(xpn_1='ARANTZAMENDI')
        pid.date_time_of_birth = '19930508'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUMOL', pl_2='305', pl_3='B', pl_4='HARABA')
        pv1.attending_doctor = XCN(xcn_1='61836374', xcn_2='LIZARRALDE', xcn_3='JOSEBA', xcn_4='ATXURRA', xcn_9='MI')
        pv1.pv1_20 = '2024110500001^^^HOS^VN^^^^HARABA&&99CENTROSK'

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
        orc.placer_order_number = EI(ei_1='LABORD2024110700001', ei_3='OSABIDE_GLOBAL')
        orc.filler_order_number = EI(ei_1='MICRO2024110800001', ei_3='GESTLAB')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LABORD2024110700001', ei_3='OSABIDE_GLOBAL')
        obr.filler_order_number = EI(ei_1='MICRO2024110800001', ei_3='GESTLAB')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Urocultivo', cwe_3='LN')
        obr.observation_date_time = '20241107080000'
        obr.results_rpt_status_chng_date_time = '20241108101500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='11475-1', cwe_2='Microorganismo aislado', cwe_3='LN')
        obx.obx_5 = '75473000^Staphylococcus saprophyticus^SCT'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241108100000'
        obx.responsible_observer = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Antibiograma', cwe_3='LN')
        obx_2.obx_5 = 'Sensible a Nitrofurantoina, Fosfomicina. Resistente a Trimetoprim-Sulfametoxazol.'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241108100000'
        obx_2.responsible_observer = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN')

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
        obx_3.date_time_of_the_observation = '20241108100000'
        obx_3.responsible_observer = XCN(xcn_1='72953138', xcn_2='BERASATEGI', xcn_3='MIREN')

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
    """ Based on live/es/es-osabide.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.sending_facility = HD(hd_1='HBASURTO')
        msh.receiving_application = HD(hd_1='IMPAX')
        msh.receiving_facility = HD(hd_1='OSK_RIS')
        msh.date_time_of_message = '20241110085900'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'OSK20241110085900010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2037481926', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='74819263F', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='NHC037481', cx_4='HBASURTO', cx_5='PI', cx_9='HBASURTO&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='LARRANAGA', xpn_2='AMAIA')
        pid.mothers_maiden_name = XPN(xpn_1='MITXELENA')
        pid.date_time_of_birth = '19751024'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADI', pl_2='001', pl_4='HBASURTO')
        pv1.attending_doctor = XCN(xcn_1='82646147', xcn_2='IRAOLA', xcn_3='INAKI', xcn_4='ZUBIAGA', xcn_9='MI')

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
        orc.placer_order_number = EI(ei_1='RADORD2024111000001', ei_3='OSABIDE_GLOBAL')
        orc.date_time_of_order_event = '20241110085900'
        orc.orc_12 = '82646147^IRAOLA^INAKI^ZUBIAGA^^^^^MI'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RADORD2024111000001', ei_3='OSABIDE_GLOBAL')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='RADIOGRAFIA TORAX PA Y LATERAL', cwe_3='LN')
        obr.observation_date_time = '20241110085900'
        obr.obr_16 = '82646147^IRAOLA^INAKI^ZUBIAGA^^^^^MI'
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
    """ Based on live/es/es-osabide.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IMPAX')
        msh.sending_facility = HD(hd_1='OSK_RIS')
        msh.receiving_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.receiving_facility = HD(hd_1='HBASURTO')
        msh.date_time_of_message = '20241111112000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RIS20241111112000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2037481926', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='NHC037481', cx_4='HBASURTO', cx_5='PI', cx_9='HBASURTO&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='LARRANAGA', xpn_2='AMAIA')
        pid.mothers_maiden_name = XPN(xpn_1='MITXELENA')
        pid.date_time_of_birth = '19751024'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADI', pl_2='001', pl_4='HBASURTO')
        pv1.attending_doctor = XCN(xcn_1='82646147', xcn_2='IRAOLA', xcn_3='INAKI', xcn_4='ZUBIAGA', xcn_9='MI')
        pv1.pv1_20 = '2024111000001^^^CEX^VN^^^^HBASURTO&&99CENTROSK'

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
        orc.placer_order_number = EI(ei_1='RADORD2024111000001', ei_3='OSABIDE_GLOBAL')
        orc.filler_order_number = EI(ei_1='RADRES2024111100001', ei_3='IMPAX')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RADORD2024111000001', ei_3='OSABIDE_GLOBAL')
        obr.filler_order_number = EI(ei_1='RADRES2024111100001', ei_3='IMPAX')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='RADIOGRAFIA TORAX PA Y LATERAL', cwe_3='LN')
        obr.observation_date_time = '20241111100000'
        obr.results_rpt_status_chng_date_time = '20241111112000'
        obr.result_status = 'F'
        obr.obr_27 = '^^^^20241111100000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='71020', cwe_2='Radiografia torax', cwe_3='LN')
        obx.obx_5 = 'Indice cardiotoracio normal. Sin consolidaciones parenquimatosas ni derrame pleural. Hilios de morfologia normal.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241111110000'
        obx.responsible_observer = XCN(xcn_1='82646147', xcn_2='IRAOLA', xcn_3='INAKI')

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
    """ Based on live/es/es-osabide.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TAONET')
        msh.sending_facility = HD(hd_1='OSK_TAO')
        msh.receiving_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.receiving_facility = HD(hd_1='HBASURTO')
        msh.date_time_of_message = '20241112093000'
        msh.message_type = MSG(msg_1='OMP', msg_2='O09', msg_3='OMP_O09')
        msh.message_control_id = 'TAO20241112093000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2082736491', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='27364918G', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='NHC082736', cx_4='HBASURTO', cx_5='PI', cx_9='HBASURTO&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='ALDAZABAL', xpn_2='JOSU')
        pid.mothers_maiden_name = XPN(xpn_1='GARMENDIA')
        pid.date_time_of_birth = '19610225'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&LEDESMA&10', xad_2='1B', xad_3='480130', xad_4='48', xad_5='48009', xad_6='ESP', xad_7='H', xad_8='BILBAO')
        pid.pid_13 = '^PRN^PH^^^944738291'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.re_admission_indicator = CWE(cwe_1='73925264', cwe_2='AGIRIANO', cwe_3='NAIARA', cwe_4='LOIZAGA', cwe_9='MI')
        pv1.vip_indicator = CWE(cwe_1='HEMA')
        pv1.financial_class = FC(fc_1='HEMA')
        pv1.credit_rating = CWE(cwe_1='73925264', cwe_2='AGIRIANO', cwe_3='NAIARA', cwe_4='LOIZAGA', cwe_9='MI')
        pv1.contract_code = CWE(cwe_1='O')
        pv1.pv1_25 = '2024111200001^^^CEX^VN^^^^HBASURTO&&99CENTROSK'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.expected_admit_date_time = '20241212'

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
        orc.filler_order_number = EI(ei_1='PRESCR20241112001', ei_3='TAONET')
        orc.orc_10 = '20241112093000'
        orc.enterers_location = PL(pl_1='73925264', pl_2='AGIRIANO', pl_3='NAIARA', pl_4='LOIZAGA', pl_9='MI')

        # .. build TQ1 ..
        tq1 = TQ1()
        tq1.set_id_tq1 = '1'
        tq1.tq1_2 = '4^^mg^miligramos^ISO+'
        tq1.end_datetime = '20241112'

        # .. build the TIMING group ..
        timing = OmpO09Timing()
        timing.tq1 = tq1

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='654321', cwe_2='ACENOCUMAROL 4MG', cwe_3='99001')
        rxo.requested_give_units = CWE(cwe_1='mg', cwe_2='miligramos', cwe_3='ISO+')
        rxo.pharmacist_treatment_suppliers_verifier_id = XCN(xcn_1='73925264', xcn_2='AGIRIANO', xcn_3='NAIARA', xcn_4='LOIZAGA', xcn_9='MI')
        rxo.requested_give_per_time_unit = 'W1'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx.obx_5 = '3.1'
        obx.reference_range = '2.0 - 3.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.observation_method = CWE(cwe_1='20241112090000')

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
        tq1_2.tq1_2 = '2^^mg^miligramos^ISO+'
        tq1_2.end_datetime = '20241113'

        # .. build TQ1 ..
        tq1_3 = TQ1()
        tq1_3.set_id_tq1 = '3'
        tq1_3.tq1_2 = '4^^mg^miligramos^ISO+'
        tq1_3.end_datetime = '20241114'

        # .. build TQ1 ..
        tq1_4 = TQ1()
        tq1_4.set_id_tq1 = '4'
        tq1_4.tq1_2 = '2^^mg^miligramos^ISO+'
        tq1_4.end_datetime = '20241115'

        # .. assemble the full message ..
        msg = OMP_O09()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [tq1_2, tq1_3, tq1_4]

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
    """ Based on live/es/es-osabide.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.sending_facility = HD(hd_1='HGALDAKAO')
        msh.receiving_application = HD(hd_1='EOSABIDE_FARMA')
        msh.receiving_facility = HD(hd_1='HGALDAKAO')
        msh.date_time_of_message = '20241114160000'
        msh.message_type = MSG(msg_1='OMP', msg_2='O09', msg_3='OMP_O09')
        msh.message_control_id = 'FARMA20241114160013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2064927381', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='49273818H', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='NHC064927', cx_4='HGALDAKAO', cx_5='PI', cx_9='HGALDAKAO&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='SARASOLA', xpn_2='OLATZ')
        pid.mothers_maiden_name = XPN(xpn_1='IZAGUIRRE')
        pid.date_time_of_birth = '19840619'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CL&AUTONOMIA&55', xad_2='4C', xad_3='480680', xad_4='48', xad_5='48170', xad_6='ESP', xad_7='H', xad_8='ZAMUDIO')
        pid.pid_13 = '^PRN^PH^^^944829371'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CIRGEN', pl_2='501', pl_3='A', pl_4='HGALDAKAO')
        pv1.attending_doctor = XCN(xcn_1='84636173', xcn_2='OLABARRI', xcn_3='ANDONI', xcn_4='KORTAJARENA', xcn_9='MI')
        pv1.hospital_service = CWE(cwe_1='CIR')
        pv1.admit_source = CWE(cwe_1='ICIR')
        pv1.admitting_doctor = XCN(xcn_1='84636173', xcn_2='OLABARRI', xcn_3='ANDONI', xcn_4='KORTAJARENA', xcn_9='MI')
        pv1.patient_type = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='2024111200001', cx_4='HOS', cx_5='VN', cx_9='HGALDAKAO&&99CENTROSK')
        pv1.total_adjustments = '20241112092000'

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
        orc.filler_order_number = EI(ei_1='RXORD2024111400001', ei_3='EOSABIDE_FARMA')
        orc.orc_10 = '20241114160000'
        orc.enterers_location = PL(pl_1='84636173', pl_2='OLABARRI', pl_3='ANDONI', pl_4='KORTAJARENA', pl_9='MI')

        # .. build TQ1 ..
        tq1 = TQ1()
        tq1.set_id_tq1 = '1'
        tq1.tq1_2 = '1^^SF30^COMPRIMIDO^99RDHCU'
        tq1.tq1_4 = 'BID^Dos veces al dia^HL70335'
        tq1.priority = CWE(cwe_1='20241114180000')
        tq1.condition_text = '20241124180000'

        # .. build the TIMING group ..
        timing = OmpO09Timing()
        timing.tq1 = tq1

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='812345', cwe_2='PARACETAMOL 1G COMPRIMIDOS', cwe_3='99001')
        rxo.requested_give_amount_minimum = '1000'
        rxo.requested_give_units = CWE(cwe_1='mg', cwe_2='miligramos', cwe_3='ISO+')
        rxo.pharmacist_treatment_suppliers_verifier_id = XCN(xcn_1='84636173', xcn_2='OLABARRI', xcn_3='ANDONI', xcn_4='KORTAJARENA', xcn_9='MI')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='272102008', cwe_2='Peso', cwe_3='SNM3')
        obx.obx_5 = '72'
        obx.probability = 'F'
        obx.producers_id = CWE(cwe_1='20241114')

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

        # .. assemble the full message ..
        msg = OMP_O09()
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
    """ Based on live/es/es-osabide.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='VITROPATH')
        msh.sending_facility = HD(hd_1='OSK_ANAT')
        msh.receiving_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.receiving_facility = HD(hd_1='HBASURTO')
        msh.date_time_of_message = '20241118153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ANAT20241118153000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2053718294', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='NHC053718', cx_4='HBASURTO', cx_5='PI', cx_9='HBASURTO&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='GALDOS', xpn_2='KOLDOBIKA')
        pid.mothers_maiden_name = XPN(xpn_1='ARTEAGA')
        pid.date_time_of_birth = '19730512'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CIRGEN', pl_2='502', pl_3='A', pl_4='HBASURTO')
        pv1.attending_doctor = XCN(xcn_1='63824294', xcn_2='ARREGUI', xcn_3='AMETS', xcn_4='BERECIARTUA', xcn_9='MI')
        pv1.pv1_20 = '2024111500001^^^HOS^VN^^^^HBASURTO&&99CENTROSK'

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
        orc.placer_order_number = EI(ei_1='LABORD2024111600001', ei_3='OSABIDE_GLOBAL')
        orc.filler_order_number = EI(ei_1='ANAT2024111800001', ei_3='VITROPATH')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LABORD2024111600001', ei_3='OSABIDE_GLOBAL')
        obr.filler_order_number = EI(ei_1='ANAT2024111800001', ei_3='VITROPATH')
        obr.universal_service_identifier = CWE(cwe_1='11529-5', cwe_2='Informe de anatomia patologica', cwe_3='LN')
        obr.observation_date_time = '20241116120000'
        obr.results_rpt_status_chng_date_time = '20241118153000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Diagnostico anatomopatologico', cwe_3='LN')
        obx.obx_5 = 'Adenoma tubulovelloso con displasia de bajo grado. Margenes de reseccion libres.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241118150000'
        obx.responsible_observer = XCN(xcn_1='63824294', xcn_2='ARREGUI', xcn_3='AMETS')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='18630-4', cwe_2='Diagnostico principal', cwe_3='LN')
        obx_2.obx_5 = '211.3^Neoplasia benigna de colon^I9C'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241118150000'
        obx_2.responsible_observer = XCN(xcn_1='63824294', xcn_2='ARREGUI', xcn_3='AMETS')

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
    """ Based on live/es/es-osabide.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IMPAX')
        msh.sending_facility = HD(hd_1='OSK_RIS')
        msh.receiving_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.receiving_facility = HD(hd_1='HARABA')
        msh.date_time_of_message = '20241120112000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RIS20241120112000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2093618274', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='NHC093618', cx_4='HARABA', cx_5='PI', cx_9='HARABA&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='MENDIOLA', xpn_2='LEIRE')
        pid.mothers_maiden_name = XPN(xpn_1='ARANTZAMENDI')
        pid.date_time_of_birth = '19930508'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUMOL', pl_2='305', pl_3='B', pl_4='HARABA')
        pv1.attending_doctor = XCN(xcn_1='61836374', xcn_2='LIZARRALDE', xcn_3='JOSEBA', xcn_4='ATXURRA', xcn_9='MI')
        pv1.pv1_20 = '2024110500001^^^HOS^VN^^^^HARABA&&99CENTROSK'

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
        orc.placer_order_number = EI(ei_1='RADORD2024111900001', ei_3='OSABIDE_GLOBAL')
        orc.filler_order_number = EI(ei_1='RADRES2024112000001', ei_3='IMPAX')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RADORD2024111900001', ei_3='OSABIDE_GLOBAL')
        obr.filler_order_number = EI(ei_1='RADRES2024112000001', ei_3='IMPAX')
        obr.universal_service_identifier = CWE(cwe_1='71260', cwe_2='TAC TORAX CON CONTRASTE', cwe_3='LN')
        obr.observation_date_time = '20241120093000'
        obr.results_rpt_status_chng_date_time = '20241120112000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='71260', cwe_2='TAC torax', cwe_3='LN')
        obx.obx_5 = 'Hallazgo de nodulo pulmonar solitario en lobulo inferior derecho de 12mm. Se recomienda seguimiento con PET-TC.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241120110000'
        obx.responsible_observer = XCN(xcn_1='61836374', xcn_2='LIZARRALDE', xcn_3='JOSEBA')

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
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKEluZm9ybWUgUmFkaW9sb2dp'
            'YSBPc2FraWRldHphKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9i'
            'agp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA2NSAwMDAwMCBuIAowMDAwMDAwMTIyIDAwMDAwIG4gCjAwMDAwMDAyOTYgMDAw'
            'MDAgbiAKMDAwMDAwMDM5OSAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjQ4MgolJUVPRg=='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241120112000'
        obx_2.responsible_observer = XCN(xcn_1='61836374', xcn_2='LIZARRALDE', xcn_3='JOSEBA')

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
    """ Based on live/es/es-osabide.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.sending_facility = HD(hd_1='HBASURTO')
        msh.receiving_application = HD(hd_1='BBANK_OSK')
        msh.receiving_facility = HD(hd_1='HBASURTO')
        msh.date_time_of_message = '20241122090131'
        msh.message_type = MSG(msg_1='OMB', msg_2='O27', msg_3='OMB_O27')
        msh.message_control_id = 'OSK20241122090131016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2031934745', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='NHC031934', cx_4='HBASURTO', cx_5='PI', cx_9='HBASURTO&&99CENTROSK'),
            CX(cx_1='31934745B', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='ETXEBARRIA', xpn_2='ANDER')
        pid.mothers_maiden_name = XPN(xpn_1='AGIRREZABAL')
        pid.date_time_of_birth = '19820713'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&GRAN VIA&48', xad_2='3D', xad_3='480200', xad_4='48', xad_5='48010', xad_6='ESP', xad_7='H', xad_8='BILBAO')
        pid.pid_13 = '^PRN^PH^^^944671823'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCI', pl_2='101', pl_3='A', pl_4='HBASURTO')
        pv1.attending_doctor = XCN(xcn_1='83934146', xcn_2='ARIZAGA', xcn_3='GORKA', xcn_4='URRUTIA', xcn_9='MI')
        pv1.hospital_service = CWE(cwe_1='UCI')
        pv1.visit_number = CX(cx_1='2024101500001', cx_4='HOS', cx_5='VN', cx_9='HBASURTO&&99CENTROSK')
        pv1.total_adjustments = '20241015084500'

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
        spm.specimen_identifier = EIP(eip_1='SPM20241122001')

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD20241122001')
        orc.filler_order_number = EI(ei_1='BB20241122001')
        orc.date_time_of_order_event = '20241122090000'
        orc.orc_12 = '83934146^ARIZAGA^GORKA^URRUTIA^^^^^MI'

        # .. build BPO ..
        bpo = BPO()
        bpo.set_id_bpo = '1'
        bpo.bp_universal_service_identifier = CWE(cwe_1='CHEM', cwe_2='Concentrado de Hematies', cwe_3='99BBANK')
        bpo.bp_processing_requirements = CWE(cwe_1='3')
        bpo.bp_amount = '3'
        bpo.bp_intended_use_date_time = '20241121200001'
        bpo.bp_intended_dispense_from_location = PL(pl_1='P101', pl_5='')
        bpo.bp_requested_dispense_date_time = '20241121220001'
        bpo.bp_requested_dispense_to_location = PL(pl_1='P101', pl_5='')

        # .. build BPO ..
        bpo_2 = BPO()
        bpo_2.set_id_bpo = '2'
        bpo_2.bp_universal_service_identifier = CWE(cwe_1='PFC', cwe_2='Plasma Fresco Congelado', cwe_3='99BBANK')
        bpo_2.bp_processing_requirements = CWE(cwe_1='2')
        bpo_2.bp_amount = '2'
        bpo_2.bp_intended_use_date_time = '20241121200001'
        bpo_2.bp_intended_dispense_from_location = PL(pl_1='P101', pl_5='')
        bpo_2.bp_requested_dispense_date_time = '20241121220001'
        bpo_2.bp_requested_dispense_to_location = PL(pl_1='P101', pl_5='')

        # .. assemble the full message ..
        msg = OMB_O27()
        msg.msh = msh
        msg.patient = patient
        msg.extra_segments = [spm, orc, bpo, bpo_2]

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
    """ Based on live/es/es-osabide.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MONITOR_UCI')
        msh.sending_facility = HD(hd_1='HBASURTO')
        msh.receiving_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.receiving_facility = HD(hd_1='HBASURTO')
        msh.date_time_of_message = '20241123061500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MON20241123061500017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2031934745', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='NHC031934', cx_4='HBASURTO', cx_5='PI', cx_9='HBASURTO&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='ETXEBARRIA', xpn_2='ANDER')
        pid.mothers_maiden_name = XPN(xpn_1='AGIRREZABAL')
        pid.date_time_of_birth = '19820713'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCI', pl_2='101', pl_3='A', pl_4='HBASURTO')
        pv1.attending_doctor = XCN(xcn_1='83934146', xcn_2='ARIZAGA', xcn_3='GORKA', xcn_4='URRUTIA', xcn_9='MI')
        pv1.pv1_20 = '2024101500001^^^HOS^VN^^^^HBASURTO&&99CENTROSK'

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.universal_service_identifier = CWE(cwe_1='VITALS', cwe_2='Signos vitales', cwe_3='LN')
        obr.observation_date_time = '20241123061500'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='8480-6', cwe_2='Presion arterial sistolica', cwe_3='LN')
        obx.obx_5 = '128'
        obx.units = CWE(cwe_1='mmHg')
        obx.reference_range = '90 - 140'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241123061500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='8462-4', cwe_2='Presion arterial diastolica', cwe_3='LN')
        obx_2.obx_5 = '78'
        obx_2.units = CWE(cwe_1='mmHg')
        obx_2.reference_range = '60 - 90'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241123061500'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='8867-4', cwe_2='Frecuencia cardiaca', cwe_3='LN')
        obx_3.obx_5 = '82'
        obx_3.units = CWE(cwe_1='/min')
        obx_3.reference_range = '60 - 100'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20241123061500'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='9279-1', cwe_2='Frecuencia respiratoria', cwe_3='LN')
        obx_4.obx_5 = '18'
        obx_4.units = CWE(cwe_1='/min')
        obx_4.reference_range = '12 - 20'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20241123061500'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='8310-5', cwe_2='Temperatura corporal', cwe_3='LN')
        obx_5.obx_5 = '37.2'
        obx_5.units = CWE(cwe_1='Cel')
        obx_5.reference_range = '36.1 - 37.2'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20241123061500'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2708-6', cwe_2='Saturacion oxigeno (SpO2)', cwe_3='LN')
        obx_6.obx_5 = '96'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '95 - 100'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20241123061500'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/es/es-osabide.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RADELEC_OSK')
        msh.sending_facility = HD(hd_1='OSK_ECG')
        msh.receiving_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.receiving_facility = HD(hd_1='HBASURTO')
        msh.date_time_of_message = '20241125143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ECG20241125143000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2082736491', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='NHC082736', cx_4='HBASURTO', cx_5='PI', cx_9='HBASURTO&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='ALDAZABAL', xpn_2='JOSU')
        pid.mothers_maiden_name = XPN(xpn_1='GARMENDIA')
        pid.date_time_of_birth = '19610225'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='001', pl_4='HBASURTO')
        pv1.attending_doctor = XCN(xcn_1='73925264', xcn_2='AGIRIANO', xcn_3='NAIARA', xcn_4='LOIZAGA', xcn_9='MI')

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
        orc.placer_order_number = EI(ei_1='ECGORD2024112500001', ei_3='OSABIDE_GLOBAL')
        orc.filler_order_number = EI(ei_1='ECGRES2024112500001', ei_3='RADELEC_OSK')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ECGORD2024112500001', ei_3='OSABIDE_GLOBAL')
        obr.filler_order_number = EI(ei_1='ECGRES2024112500001', ei_3='RADELEC_OSK')
        obr.universal_service_identifier = CWE(cwe_1='93000', cwe_2='Electrocardiograma', cwe_3='LN')
        obr.observation_date_time = '20241125140000'
        obr.results_rpt_status_chng_date_time = '20241125143000'
        obr.result_status = 'F'
        obr.obr_27 = '^^^^20241125140000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='93000', cwe_2='ECG informe', cwe_3='LN')
        obx.obx_5 = 'Ritmo sinusal a 72 lpm. Eje normal. Sin alteraciones de repolarizacion. QTc 420ms.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241125142000'
        obx.responsible_observer = XCN(xcn_1='73925264', xcn_2='AGIRIANO', xcn_3='NAIARA')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='93000', cwe_2='ECG imagen', cwe_3='LN')
        obx_2.obx_5 = (
            '^image^png^Base64^'
            'iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAMAAABrrFhUAAAABGdBTUEAALGPC/xhBQAAAAlwSFlzAAAOwQAADsEBuJFr7QAAABl0RVh0U29mdHdhcmUAcGFpbnQubmV0IDQuMC4xNkRp'
            'r/UAAAB+UExURf///+/v78fHx7+/v7e3t6+vr6enp5+fn5eXl4+Pj4eHh39/f3d3d29vb2dnZ19fX1dXV09PT0tLS0dHR0NDQz8/Pzs7Ozc3NzMzMyMjIx8fHxsbGxUVFRQUFBMTExIS'
            'EhERERAPDw8PDw4ODg0NDQwMDAoKCgkJCQgICAcHBwYGBgUFBQQEBAMDAwICAgEBAQAAAJDKmlQAAABcklEQVR42u3dW3LCIBSG4UNiYqK2HjC17/9GG0iAQAh45u5vvhk6Y2f+BRAIl'
            'ORNFIvGGLPqeDv2L4+R9bOA2pjVe+wDSLPq+PY2sq58jmwAfRrj++LJWaLzLYNRV3bWkv2MXQJ1/fy3sU7ABNBh42i7jF0CVXN/tPbVaQIm'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241125143000'
        obx_2.responsible_observer = XCN(xcn_1='73925264', xcn_2='AGIRIANO', xcn_3='NAIARA')

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
    """ Based on live/es/es-osabide.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.sending_facility = HD(hd_1='HBASURTO')
        msh.receiving_application = HD(hd_1='EMPI_OSK')
        msh.receiving_facility = HD(hd_1='OSK')
        msh.date_time_of_message = '20241128101935'
        msh.message_type = MSG(msg_1='QBP', msg_2='Q22', msg_3='QBP_Q21')
        msh.message_control_id = 'OSK20241128101935019'
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
        qpd.qpd_3 = '@PID.3.1^CAPV2037481926~@PID.3.4.1^CAPV~@PID.3.5^JHN'

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
    """ Based on live/es/es-osabide.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMPI_OSK')
        msh.sending_facility = HD(hd_1='OSK')
        msh.receiving_application = HD(hd_1='OSABIDE_GLOBAL')
        msh.receiving_facility = HD(hd_1='HBASURTO')
        msh.date_time_of_message = '20241128101936'
        msh.message_type = MSG(msg_1='RSP', msg_2='K22', msg_3='RSP_K21')
        msh.message_control_id = 'OSK20241128101936020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = '8859/1'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'OSK20241128101935019'

        # .. build QAK ..
        qak = QAK()
        qak.query_tag = 'QRY20241128001'
        qak.query_response_status = 'OK'

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='1', cwe_2='IHE PDQ Query', cwe_3='HL70471')
        qpd.query_tag = 'QRY20241128001'
        qpd.qpd_3 = '@PID.3.1^CAPV2037481926~@PID.3.4.1^CAPV~@PID.3.5^JHN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAPV2037481926', cx_4='CAPV', cx_5='JHN', cx_9='PV&&ISO3166-2'),
            CX(cx_1='74819263F', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='4837481926001', cx_4='MS', cx_5='HC', cx_9='ESP&&ISO3166'),
            CX(cx_1='NHC037481', cx_4='HBASURTO', cx_5='PI', cx_9='HBASURTO&&99CENTROSK'),
        ]
        pid.patient_name = XPN(xpn_1='LARRANAGA', xpn_2='AMAIA')
        pid.mothers_maiden_name = XPN(xpn_1='MITXELENA')
        pid.date_time_of_birth = '19751024'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CL&ALAMEDA RECALDE&18', xad_2='7A', xad_3='480130', xad_4='48', xad_5='48009', xad_6='ESP', xad_7='H', xad_8='BILBAO')
        pid.pid_13 = '^PRN^PH^^^944918273~^PRN^CP^^^622471938'
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
