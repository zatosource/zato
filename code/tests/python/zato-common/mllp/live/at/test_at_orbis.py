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
from zato.hl7v2.v2_9.datatypes import CNE, CP, CWE, CX, DR, EI, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA05Insurance, AdtA39Patient, DftP03Diagnosis, DftP03Financial, DftP03Insurance, DftP03Visit, \
    MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, \
    OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, DFT_P03, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, DG1, EVN, FT1, IN1, MRG, MSA, MSH, NTE, OBR, OBX, ORC, PID, PV1, PV2, RGS, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('at', 'at-orbis.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/at/at-orbis.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='KEPLER_LINZ')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='KEPLER_LINZ')
        msh.date_time_of_message = '20260210083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'ADT20260210001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260210083000'
        evn.event_occurred = '20260210082200'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='456789', cx_4='KEPLER_LINZ', cx_5='PI'), CX(cx_1='4781100175', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Lang', xpn_2='Florian', xpn_3='Leopold', xpn_7='L')
        pid.date_time_of_birth = '19750110'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Landstraße 22', xad_3='Linz', xad_4='4', xad_5='4020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^43^732^654321~^PRN^CP^^43^660^4567890'
        pid.pid_14 = '^WPN^PH^^43^732^7806-0'
        pid.primary_language = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Verheiratet', cwe_3='HL70002')
        pid.veterans_military_status = CWE(cwe_1='AUT', cwe_2='Austrian', cwe_3='HL70171')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEU', pl_2='502', pl_3='1', pl_4='KEPLER_LINZ', pl_6='N', pl_7='A', pl_8='5')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.attending_doctor = XCN(
            xcn_1='20123456',
            xcn_2='Schwarz',
            xcn_3='Heinrich',
            xcn_6='Univ.Prof.Dr.',
            xcn_9='GDA&1.2.40.0.34.3.1.1&ISO',
            xcn_10='L',
            xcn_13='GDA',
        )
        pv1.referring_doctor = XCN(
            xcn_1='20123457',
            xcn_2='Pfeiffer',
            xcn_3='Lieselotte',
            xcn_6='Dr.',
            xcn_9='GDA&1.2.40.0.34.3.1.1&ISO',
            xcn_10='L',
            xcn_13='GDA',
        )
        pv1.hospital_service = CWE(cwe_1='NEU')
        pv1.pv1_20 = 'FN2026-10234^^^KEPLER_LINZ^VN'
        pv1.discharge_date_time = '20260210082200'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.expected_discharge_date_time = '20260217'
        pv2.estimated_length_of_inpatient_stay = '7'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/at/at-orbis.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='KLIN_WELS')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='KLIN_WELS')
        msh.date_time_of_message = '20260318091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'ADT20260318002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260318091500'
        evn.event_occurred = '20260318090800'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='678901', cx_4='KLIN_WELS', cx_5='PI'), CX(cx_1='8923230789', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Brunner', xpn_2='Michaela', xpn_3='Irmgard', xpn_7='L')
        pid.date_time_of_birth = '19890723'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Ringstraße 5', xad_3='Wels', xad_4='4', xad_5='4600', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^43^7242^56789~^PRN^CP^^43^676^2345678'
        pid.primary_language = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Verheiratet', cwe_3='HL70002')
        pid.veterans_military_status = CWE(cwe_1='AUT', cwe_2='Austrian', cwe_3='HL70171')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GYNA', pl_2='208', pl_3='2', pl_4='KLIN_WELS', pl_6='N', pl_7='A', pl_8='3')
        pv1.admission_type = CWE(cwe_1='U')
        pv1.attending_doctor = XCN(xcn_1='20234567', xcn_2='Koller', xcn_3='Silvia', xcn_6='Dr.', xcn_9='GDA&1.2.40.0.34.3.1.1&ISO', xcn_10='L', xcn_13='GDA')
        pv1.consulting_doctor = XCN(xcn_1='IM')
        pv1.hospital_service = CWE(cwe_1='GYNA')
        pv1.pv1_20 = 'FN2026-20567^^^KLIN_WELS^VN'
        pv1.discharge_date_time = '20260318090800'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='04')
        in1.insurance_company_name = XON(xon_1='ÖGK Oberösterreich')
        in1.insurance_company_address = XAD(xad_1='Gruberstraße 77', xad_3='Linz', xad_5='4020', xad_6='AUT')
        in1.insureds_id_number = CX(cx_1='15')

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
    """ Based on live/at/at-orbis.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='KEPLER_LINZ')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='KEPLER_LINZ')
        msh.date_time_of_message = '20260215140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'ADT20260215003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260215140000'
        evn.event_occurred = '20260215135500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='456789', cx_4='KEPLER_LINZ', cx_5='PI'), CX(cx_1='4781100175', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Lang', xpn_2='Florian', xpn_3='Leopold', xpn_7='L')
        pid.date_time_of_birth = '19750110'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Landstraße 22', xad_3='Linz', xad_4='4', xad_5='4020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^CP^^43^660^4567890'
        pid.primary_language = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Verheiratet', cwe_3='HL70002')
        pid.veterans_military_status = CWE(cwe_1='AUT', cwe_2='Austrian', cwe_3='HL70171')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='STROKE', pl_2='601', pl_3='2', pl_4='KEPLER_LINZ', pl_6='N', pl_7='D', pl_8='6')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.prior_patient_location = PL(pl_1='NEU', pl_2='502', pl_3='1', pl_4='KEPLER_LINZ', pl_6='N', pl_7='D', pl_8='5')
        pv1.attending_doctor = XCN(
            xcn_1='20123456',
            xcn_2='Schwarz',
            xcn_3='Heinrich',
            xcn_6='Univ.Prof.Dr.',
            xcn_9='GDA&1.2.40.0.34.3.1.1&ISO',
            xcn_10='L',
            xcn_13='GDA',
        )
        pv1.visit_number = CX(cx_1='FN2026-10234', cx_4='KEPLER_LINZ', cx_5='VN')
        pv1.admit_date_time = '20260215135500'

        # .. assemble the full message ..
        msg = ADT_A02()
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
    """ Based on live/at/at-orbis.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='KEPLER_LINZ')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='KEPLER_LINZ')
        msh.date_time_of_message = '20260220100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'ADT20260220004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260220100000'
        evn.event_occurred = '20260220095500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='456789', cx_4='KEPLER_LINZ', cx_5='PI'), CX(cx_1='4781100175', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Lang', xpn_2='Florian', xpn_3='Leopold', xpn_7='L')
        pid.date_time_of_birth = '19750110'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Landstraße 22', xad_3='Linz', xad_4='4', xad_5='4020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^CP^^43^660^4567890'
        pid.primary_language = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Verheiratet', cwe_3='HL70002')
        pid.veterans_military_status = CWE(cwe_1='AUT', cwe_2='Austrian', cwe_3='HL70171')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='STROKE', pl_2='601', pl_3='2', pl_4='KEPLER_LINZ', pl_6='N', pl_7='B', pl_8='6')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.attending_doctor = XCN(
            xcn_1='20123456',
            xcn_2='Schwarz',
            xcn_3='Heinrich',
            xcn_6='Univ.Prof.Dr.',
            xcn_9='GDA&1.2.40.0.34.3.1.1&ISO',
            xcn_10='L',
            xcn_13='GDA',
        )
        pv1.visit_number = CX(cx_1='FN2026-10234', cx_4='KEPLER_LINZ', cx_5='VN')
        pv1.discharge_disposition = CWE(cwe_1='011')
        pv1.admit_date_time = '20260210082200'
        pv1.discharge_date_time = '20260220095500'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/at/at-orbis.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='SK_VOECKLA')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='SK_VOECKLA')
        msh.date_time_of_message = '20260405143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'ADT20260405005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260405143000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='234567', cx_4='SK_VOECKLA', cx_5='PI'), CX(cx_1='7359120878', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Aigner', xpn_2='Erwin', xpn_7='L')
        pid.date_time_of_birth = '19780812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stadtplatz 15', xad_3='Vöcklabruck', xad_4='4', xad_5='4840', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^CP^^43^664^8765432'
        pid.primary_language = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Verheiratet', cwe_3='HL70002')
        pid.veterans_military_status = CWE(cwe_1='AUT', cwe_2='Austrian', cwe_3='HL70171')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTH', pl_2='304', pl_3='1', pl_4='SK_VOECKLA', pl_6='N', pl_7='A', pl_8='3')
        pv1.admission_type = CWE(cwe_1='U')
        pv1.attending_doctor = XCN(xcn_1='20345678', xcn_2='Thaler', xcn_3='Rainer', xcn_6='Dr.', xcn_9='GDA&1.2.40.0.34.3.1.1&ISO', xcn_10='L', xcn_13='GDA')
        pv1.visit_number = CX(cx_1='FN2026-30789', cx_4='SK_VOECKLA', cx_5='VN')
        pv1.admit_date_time = '20260402100000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='04')
        in1.insurance_company_name = XON(xon_1='ÖGK Oberösterreich')
        in1.insurance_company_address = XAD(xad_1='Gruberstraße 77', xad_3='Linz', xad_5='4020', xad_6='AUT')
        in1.insureds_id_number = CX(cx_1='15')

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
    """ Based on live/at/at-orbis.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='KEPLER_LINZ')
        msh.receiving_application = HD(hd_1='PACS')
        msh.receiving_facility = HD(hd_1='KEPLER_LINZ')
        msh.date_time_of_message = '20260422100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'ADT20260422006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260422100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='890123', cx_4='KEPLER_LINZ', cx_5='PI'), CX(cx_1='6128220691', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Egger', xpn_2='Helga', xpn_7='L')
        pid.date_time_of_birth = '19910622'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Mozartstraße 8', xad_3='Linz', xad_4='4', xad_5='4020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^CP^^43^650^1234567'
        pid.primary_language = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Ledig', cwe_3='HL70002')
        pid.veterans_military_status = CWE(cwe_1='AUT', cwe_2='Austrian', cwe_3='HL70171')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DERMA', pl_2='AMB', pl_3='01', pl_4='KEPLER_LINZ')
        pv1.attending_doctor = XCN(xcn_1='20456789', xcn_2='Hager', xcn_3='Alois', xcn_6='Dr.', xcn_9='GDA&1.2.40.0.34.3.1.1&ISO', xcn_10='L', xcn_13='GDA')
        pv1.visit_number = CX(cx_1='FN2026-11890', cx_4='KEPLER_LINZ', cx_5='VN')
        pv1.admit_date_time = '20260422100000'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/at/at-orbis.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='KLIN_WELS')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='KLIN_WELS')
        msh.date_time_of_message = '20260401153000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'ADT20260401007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260401153000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='678901', cx_4='KLIN_WELS', cx_5='PI'), CX(cx_1='8923230789', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Brunner', xpn_2='Michaela', xpn_3='Irmgard', xpn_7='L')
        pid.date_time_of_birth = '19890723'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Ringstraße 5', xad_3='Wels', xad_4='4', xad_5='4600', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^CP^^43^676^2345678'
        pid.primary_language = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Verheiratet', cwe_3='HL70002')
        pid.veterans_military_status = CWE(cwe_1='AUT', cwe_2='Austrian', cwe_3='HL70171')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = [
            CX(cx_1='678900', cx_4='KLIN_WELS', cx_5='PI'),
            CX(cx_1='8923230789', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS'),
        ]
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
    """ Based on live/at/at-orbis.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='KEPLER_LINZ')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='KEPLER_LINZ')
        msh.date_time_of_message = '20260211093000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ORM20260211001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='456789', cx_4='KEPLER_LINZ', cx_5='PI'), CX(cx_1='4781100175', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Lang', xpn_2='Florian', xpn_3='Leopold', xpn_7='L')
        pid.date_time_of_birth = '19750110'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEU', pl_2='502', pl_3='1', pl_4='KEPLER_LINZ')
        pv1.attending_doctor = XCN(
            xcn_1='20123456',
            xcn_2='Schwarz',
            xcn_3='Heinrich',
            xcn_6='Univ.Prof.Dr.',
            xcn_9='GDA&1.2.40.0.34.3.1.1&ISO',
            xcn_10='L',
            xcn_13='GDA',
        )

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
        orc.placer_order_number = EI(ei_1='ORD56789', ei_2='ORBIS')
        orc.placer_order_group_number = EI(ei_1='GRP001', ei_2='ORBIS')
        orc.date_time_of_order_event = '20260211093000'
        orc.orc_12 = '20123456^Schwarz^Heinrich^^^Univ.Prof.Dr.^^^GDA&1.2.40.0.34.3.1.1&ISO^L^^^GDA'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD56789', ei_2='ORBIS')
        obr.universal_service_identifier = CWE(cwe_1='70553', cwe_2='MR Schädel mit KM', cwe_3='CPT4')
        obr.observation_date_time = '20260211093000'
        obr.obr_16 = '20123456^Schwarz^Heinrich^^^Univ.Prof.Dr.^^^GDA&1.2.40.0.34.3.1.1&ISO^L^^^GDA'
        obr.obr_27 = '^STAT'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I63.9', cwe_2='Hirninfarkt', cwe_3='ICD10BMSGPK')

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
        nte.comment = 'V.a. ischämischer Insult, bitte diffusionsgewichtet.'

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
    """ Based on live/at/at-orbis.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='KLIN_WELS')
        msh.receiving_application = HD(hd_1='LABSYS')
        msh.receiving_facility = HD(hd_1='KLIN_WELS')
        msh.date_time_of_message = '20260319080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ORM20260319002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='678901', cx_4='KLIN_WELS', cx_5='PI'), CX(cx_1='8923230789', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Brunner', xpn_2='Michaela', xpn_3='Irmgard', xpn_7='L')
        pid.date_time_of_birth = '19890723'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GYNA', pl_2='208', pl_3='2', pl_4='KLIN_WELS')
        pv1.attending_doctor = XCN(xcn_1='20234567', xcn_2='Koller', xcn_3='Silvia', xcn_6='Dr.', xcn_9='GDA&1.2.40.0.34.3.1.1&ISO', xcn_10='L', xcn_13='GDA')

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
        orc.placer_order_number = EI(ei_1='ORD34567', ei_2='ORBIS')
        orc.placer_order_group_number = EI(ei_1='GRP002', ei_2='ORBIS')
        orc.date_time_of_order_event = '20260319080000'
        orc.orc_12 = '20234567^Koller^Silvia^^^Dr.^^^GDA&1.2.40.0.34.3.1.1&ISO^L^^^GDA'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD34567', ei_2='ORBIS')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Blutbild komplett', cwe_3='LN')
        obr.observation_date_time = '20260319080000'
        obr.obr_16 = '20234567^Koller^Silvia^^^Dr.^^^GDA&1.2.40.0.34.3.1.1&ISO^L^^^GDA'
        obr.obr_27 = '^ROUTINE'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='O80', cwe_2='Spontangeburt eines Einlings', cwe_3='ICD10BMSGPK')

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
    """ Based on live/at/at-orbis.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='KEPLER_LINZ')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='KEPLER_LINZ')
        msh.date_time_of_message = '20260211163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20260211001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='456789', cx_4='KEPLER_LINZ', cx_5='PI'), CX(cx_1='4781100175', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Lang', xpn_2='Florian', xpn_3='Leopold', xpn_7='L')
        pid.date_time_of_birth = '19750110'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEU', pl_2='502', pl_3='1', pl_4='KEPLER_LINZ')

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
        orc.placer_order_number = EI(ei_1='ORD56001', ei_2='ORBIS')
        orc.filler_order_number = EI(ei_1='FIL88234', ei_2='LABSYS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD56001', ei_2='ORBIS')
        obr.filler_order_number = EI(ei_1='FIL88234', ei_2='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Umfassende Metabolische Analyse', cwe_3='LN')
        obr.observation_date_time = '20260211080000'
        obr.obr_16 = '20123456^Schwarz^Heinrich^^^Univ.Prof.Dr.^^^GDA&1.2.40.0.34.3.1.1&ISO^L^^^GDA'
        obr.results_rpt_status_chng_date_time = '20260211162000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glukose', cwe_3='LN')
        obx.obx_5 = '7.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.9-6.1'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Kreatinin', cwe_3='LN')
        obx_2.obx_5 = '95'
        obx_2.units = CWE(cwe_1='umol/L')
        obx_2.reference_range = '62-106'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Natrium', cwe_3='LN')
        obx_3.obx_5 = '141'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '136-145'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Kalium', cwe_3='LN')
        obx_4.obx_5 = '3.8'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '3.5-5.1'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='14682-9', cwe_2='LDH', cwe_3='LN')
        obx_5.obx_5 = '312'
        obx_5.units = CWE(cwe_1='U/L')
        obx_5.reference_range = '125-243'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2532-0', cwe_2='LDL Cholesterin', cwe_3='LN')
        obx_6.obx_5 = '4.2'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '<3.4'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='30313-1', cwe_2='hsCRP', cwe_3='LN')
        obx_7.obx_5 = '18.5'
        obx_7.units = CWE(cwe_1='mg/L')
        obx_7.reference_range = '<5.0'
        obx_7.interpretation_codes = CWE(cwe_1='H')
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
    """ Based on live/at/at-orbis.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='KLIN_WELS')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='KLIN_WELS')
        msh.date_time_of_message = '20260320141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20260320002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='678901', cx_4='KLIN_WELS', cx_5='PI'), CX(cx_1='8923230789', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Brunner', xpn_2='Michaela', xpn_3='Irmgard', xpn_7='L')
        pid.date_time_of_birth = '19890723'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GYNA', pl_2='208', pl_3='2', pl_4='KLIN_WELS')

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
        orc.placer_order_number = EI(ei_1='ORD34567', ei_2='ORBIS')
        orc.filler_order_number = EI(ei_1='FIL55678', ei_2='LABSYS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD34567', ei_2='ORBIS')
        obr.filler_order_number = EI(ei_1='FIL55678', ei_2='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Blutbild komplett', cwe_3='LN')
        obr.observation_date_time = '20260319080000'
        obr.obr_16 = '20234567^Koller^Silvia^^^Dr.^^^GDA&1.2.40.0.34.3.1.1&ISO^L^^^GDA'
        obr.results_rpt_status_chng_date_time = '20260320140000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hämoglobin', cwe_3='LN')
        obx.obx_5 = '12.8'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '12.0-16.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hämatokrit', cwe_3='LN')
        obx_2.obx_5 = '38.2'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '36.0-46.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukozyten', cwe_3='LN')
        obx_3.obx_5 = '11.4'
        obx_3.units = CWE(cwe_1='10*9/L')
        obx_3.reference_range = '4.5-11.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='787-2', cwe_2='Erythrozyten', cwe_3='LN')
        obx_4.obx_5 = '4.25'
        obx_4.units = CWE(cwe_1='10*12/L')
        obx_4.reference_range = '3.80-5.20'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Thrombozyten', cwe_3='LN')
        obx_5.obx_5 = '278'
        obx_5.units = CWE(cwe_1='10*9/L')
        obx_5.reference_range = '150-400'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='770-8', cwe_2='Neutrophile', cwe_3='LN')
        obx_6.obx_5 = '7.9'
        obx_6.units = CWE(cwe_1='10*9/L')
        obx_6.reference_range = '1.8-7.7'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='731-0', cwe_2='Lymphozyten', cwe_3='LN')
        obx_7.obx_5 = '2.3'
        obx_7.units = CWE(cwe_1='10*9/L')
        obx_7.reference_range = '1.0-4.8'
        obx_7.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/at/at-orbis.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='KEPLER_LINZ')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='KEPLER_LINZ')
        msh.date_time_of_message = '20260212110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD20260212001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='456789', cx_4='KEPLER_LINZ', cx_5='PI'), CX(cx_1='4781100175', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Lang', xpn_2='Florian', xpn_3='Leopold', xpn_7='L')
        pid.date_time_of_birth = '19750110'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEU', pl_2='502', pl_3='1', pl_4='KEPLER_LINZ')

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
        orc.placer_order_number = EI(ei_1='ORD56789', ei_2='ORBIS')
        orc.filler_order_number = EI(ei_1='FIL99123', ei_2='RIS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD56789', ei_2='ORBIS')
        obr.filler_order_number = EI(ei_1='FIL99123', ei_2='RIS')
        obr.universal_service_identifier = CWE(cwe_1='70553', cwe_2='MR Schädel mit KM', cwe_3='CPT4')
        obr.observation_date_time = '20260211093000'
        obr.obr_16 = '20123456^Schwarz^Heinrich^^^Univ.Prof.Dr.^^^GDA&1.2.40.0.34.3.1.1&ISO^L^^^GDA'
        obr.results_rpt_status_chng_date_time = '20260212105500'
        obr.diagnostic_serv_sect_id = 'RAD'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='70553', cwe_2='MR Schädel', cwe_3='CPT4')
        obx.obx_5 = 'Befund: Akuter ischämischer Infarkt im Stromgebiet der A. cerebri media rechts. Keine Einblutung. Kein Midline-Shift.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='MR-Befund', cwe_3='LOCAL')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNTk1IDg0Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA1OTUgODQyXQovQ29udGVudHMg'
            'NCAwIFIKL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA2NCA+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3'
            'MDAgVGQKKEtlcGxlciBVbml2ZXJzaXRhdHNrbGluaWt1bSAtIE1SIFNjaGFkZWwgQmVmdW5kKSBUagoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250Ci9T'
            'dWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTgg'
            'MDAwMDAgbiAKMDAwMDAwMDE1MyAwMDAwMCBuIAowMDAwMDAwMzE0IDAwMDAwIG4gCjAwMDAwMDA0MzMgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0'
            'YXJ0eHJlZgo1MTMKJSVFT0YK'
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
    """ Based on live/at/at-orbis.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='KEPLER_LINZ')
        msh.receiving_application = HD(hd_1='SCHED')
        msh.receiving_facility = HD(hd_1='KEPLER_LINZ')
        msh.date_time_of_message = '20260301100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'SCH20260301001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT90512', ei_2='ORBIS')
        sch.filler_appointment_id = EI(ei_1='APT90512', ei_2='SCHED')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='CONSULT', cwe_2='Kontrolle', cwe_3='LOCAL')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^30^20260315140000^20260315143000'
        sch.filler_contact_person = XCN(
            xcn_1='20123456',
            xcn_2='Schwarz',
            xcn_3='Heinrich',
            xcn_6='Univ.Prof.Dr.',
            xcn_9='GDA&1.2.40.0.34.3.1.1&ISO',
            xcn_10='L',
            xcn_13='GDA',
        )
        sch.filler_contact_address = XAD(xad_1='KEPLER_LINZ')
        sch.entered_by_person = XCN(xcn_1='Booked')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='456789', cx_4='KEPLER_LINZ', cx_5='PI'), CX(cx_1='4781100175', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Lang', xpn_2='Florian', xpn_3='Leopold', xpn_7='L')
        pid.date_time_of_birth = '19750110'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NEU', pl_2='AMB', pl_3='01', pl_4='KEPLER_LINZ')
        pv1.attending_doctor = XCN(
            xcn_1='20123456',
            xcn_2='Schwarz',
            xcn_3='Heinrich',
            xcn_6='Univ.Prof.Dr.',
            xcn_9='GDA&1.2.40.0.34.3.1.1&ISO',
            xcn_10='L',
            xcn_13='GDA',
        )

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
        ais.universal_service_identifier = CWE(cwe_1='CONSULT', cwe_2='Neurologische Kontrolle', cwe_3='LOCAL')
        ais.start_date_time_offset_units = CNE(cne_1='20260315140000')
        ais.duration = '0'
        ais.duration_units = CNE(cne_1='MIN')
        ais.allow_substitution_code = CWE(cwe_1='30')
        ais.filler_status_code = CWE(cwe_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.personnel_resource_id = XCN(
            xcn_1='20123456',
            xcn_2='Schwarz',
            xcn_3='Heinrich',
            xcn_6='Univ.Prof.Dr.',
            xcn_9='GDA&1.2.40.0.34.3.1.1&ISO',
            xcn_10='L',
            xcn_13='GDA',
        )
        aip.resource_type = CWE(cwe_1='ATT', cwe_2='Attending', cwe_3='HL70443')

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.personnel_resource = personnel_resource

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'A'
        ail.location_resource_id = PL(pl_1='NEU', pl_2='AMB', pl_3='01', pl_4='KEPLER_LINZ')
        ail.location_group = CWE(cwe_1='20260315140000')
        ail.start_date_time = '0'
        ail.start_date_time_offset = 'MIN'
        ail.start_date_time_offset_units = CNE(cne_1='30')
        ail.duration = 'MIN'

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources
        msg.extra_segments = [ail]

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
    """ Based on live/at/at-orbis.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='KLIN_WELS')
        msh.receiving_application = HD(hd_1='DMS')
        msh.receiving_facility = HD(hd_1='KLIN_WELS')
        msh.date_time_of_message = '20260322143000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'DOC20260322001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260322143000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='678901', cx_4='KLIN_WELS', cx_5='PI'), CX(cx_1='8923230789', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Brunner', xpn_2='Michaela', xpn_3='Irmgard', xpn_7='L')
        pid.date_time_of_birth = '19890723'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GYNA', pl_2='OR1', pl_3='01', pl_4='KLIN_WELS')
        pv1.attending_doctor = XCN(xcn_1='20234567', xcn_2='Koller', xcn_3='Silvia', xcn_6='Dr.', xcn_9='GDA&1.2.40.0.34.3.1.1&ISO', xcn_10='L', xcn_13='GDA')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='OP', cwe_2='Operationsbericht', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Text^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260320100000')
        txa.assigned_document_authenticator = XCN(
            xcn_1='20234567',
            xcn_2='Koller',
            xcn_3='Silvia',
            xcn_6='Dr.',
            xcn_9='GDA&1.2.40.0.34.3.1.1&ISO',
            xcn_10='L',
            xcn_13='GDA',
        )
        txa.placer_order_number = EI(ei_1='DOC-WELS-2026-567')
        txa.unique_document_file_name = 'AU^Authentifiziert^HL70271'
        txa.document_confidentiality_status = '20260322142000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='OP_NOTE', cwe_2='Operationsbericht', cwe_3='LOCAL')
        obx.obx_5 = (
            'Eingriff: Sectio caesarea\\.br\\Indikation: Beckenendlage\\.br\\Komplikationen: Keine\\.br\\Geschätzter Blutverlust: 400 mL\\.br\\Neugeborenes: männ'
            'lich, 3250 g, APGAR 9/10/10.'
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
    """ Based on live/at/at-orbis.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='SK_VOECKLA')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='SK_VOECKLA')
        msh.date_time_of_message = '20260410163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MICRO20260410001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='234567', cx_4='SK_VOECKLA', cx_5='PI'), CX(cx_1='7359120878', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Aigner', xpn_2='Erwin', xpn_7='L')
        pid.date_time_of_birth = '19780812'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTH', pl_2='304', pl_3='1', pl_4='SK_VOECKLA')

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
        orc.placer_order_number = EI(ei_1='ORD89012', ei_2='ORBIS')
        orc.filler_order_number = EI(ei_1='FIL33456', ei_2='LABSYS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD89012', ei_2='ORBIS')
        obr.filler_order_number = EI(ei_1='FIL33456', ei_2='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Wundabstrich', cwe_3='LN')
        obr.observation_date_time = '20260407100000'
        obr.obr_16 = '20345678^Thaler^Rainer^^^Dr.^^^GDA&1.2.40.0.34.3.1.1&ISO^L^^^GDA'
        obr.results_rpt_status_chng_date_time = '20260410160000'
        obr.diagnostic_serv_sect_id = 'MB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='11475-1', cwe_2='Erregeridentifikation', cwe_3='LN')
        obx.obx_5 = '3092008^Staphylococcus aureus^SCT'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Resistenzprofil', cwe_3='LN')
        obx_2.obx_5 = 'Siehe Antibiogramm'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18862-3', cwe_2='Ampicillin', cwe_3='LN')
        obx_3.obx_5 = 'R^Resistent'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18900-1', cwe_2='Amoxicillin-Clavulansäure', cwe_3='LN')
        obx_4.obx_5 = 'S^Sensibel'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18878-9', cwe_2='Cefazolin', cwe_3='LN')
        obx_5.obx_5 = 'S^Sensibel'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18906-8', cwe_2='Ciprofloxacin', cwe_3='LN')
        obx_6.obx_5 = 'R^Resistent'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='35659-2', cwe_2='MHK Vancomycin', cwe_3='LN')
        obx_7.obx_5 = '1.0'
        obx_7.units = CWE(cwe_1='ug/mL')
        obx_7.reference_range = '<=2'
        obx_7.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/at/at-orbis.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='KLIN_WELS')
        msh.receiving_application = HD(hd_1='BILLING')
        msh.receiving_facility = HD(hd_1='OEGK_OOE')
        msh.date_time_of_message = '20260325180000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'CHG20260325001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20260325180000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='678901', cx_4='KLIN_WELS', cx_5='PI'), CX(cx_1='8923230789', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Brunner', xpn_2='Michaela', xpn_3='Irmgard', xpn_7='L')
        pid.date_time_of_birth = '19890723'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Ringstraße 5', xad_3='Wels', xad_4='4', xad_5='4600', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GYNA', pl_2='208', pl_3='2', pl_4='KLIN_WELS')
        pv1.attending_doctor = XCN(xcn_1='20234567', xcn_2='Koller', xcn_3='Silvia', xcn_6='Dr.', xcn_9='GDA&1.2.40.0.34.3.1.1&ISO', xcn_10='L', xcn_13='GDA')
        pv1.hospital_service = CWE(cwe_1='GYNA')
        pv1.patient_type = CWE(cwe_1='FN2026-20567', cwe_4='KLIN_WELS', cwe_5='VN')
        pv1.prior_temporary_location = PL(pl_1='20260318090800')

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_id = CX(cx_1='CHG001')
        ft1.transaction_batch_id = 'CHG001'
        ft1.transaction_date = DR(dr_1='20260320')
        ft1.transaction_posting_date = '20260325'
        ft1.transaction_type = CWE(cwe_1='CG')
        ft1.transaction_code = CWE(cwe_1='MEL0901', cwe_2='Sectio caesarea', cwe_3='MEL')
        ft1.transaction_amount_extended = CP(cp_1='1')
        ft1.department_code = CWE(cwe_1='GYNA')
        ft1.performed_by_code = XCN(xcn_1='O80', xcn_2='Spontangeburt eines Einlings', xcn_3='ICD10BMSGPK')
        ft1.ordered_by_code = XCN(xcn_1='20234567', xcn_2='Koller', xcn_3='Silvia', xcn_6='Dr.', xcn_9='GDA&1.2.40.0.34.3.1.1&ISO', xcn_10='L', xcn_13='GDA')
        ft1.filler_order_number = EI(ei_1='2850.00')

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_id = CX(cx_1='CHG002')
        ft1_2.transaction_batch_id = 'CHG002'
        ft1_2.transaction_date = DR(dr_1='20260321')
        ft1_2.transaction_posting_date = '20260325'
        ft1_2.transaction_type = CWE(cwe_1='CG')
        ft1_2.transaction_code = CWE(cwe_1='MEL0150', cwe_2='Neonatologische Erstversorgung', cwe_3='MEL')
        ft1_2.transaction_amount_extended = CP(cp_1='1')
        ft1_2.department_code = CWE(cwe_1='NEO')
        ft1_2.performed_by_code = XCN(xcn_1='P96.8', xcn_2='Sonstige Zustände Perinatalperiode', xcn_3='ICD10BMSGPK')
        ft1_2.ordered_by_code = XCN(
            xcn_1='20567890',
            xcn_2='Mitterer',
            xcn_3='Gertraud',
            xcn_6='Dr.',
            xcn_9='GDA&1.2.40.0.34.3.1.1&ISO',
            xcn_10='L',
            xcn_13='GDA',
        )
        ft1_2.filler_order_number = EI(ei_1='480.00')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='O82.0', cwe_2='Entbindung durch Sectio caesarea', cwe_3='ICD10BMSGPK')
        dg1.diagnosis_date_time = '20260320'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the DIAGNOSIS group ..
        diagnosis = DftP03Diagnosis()
        diagnosis.dg1 = dg1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='04')
        in1.insurance_company_name = XON(xon_1='ÖGK Oberösterreich')
        in1.insurance_company_address = XAD(xad_1='Gruberstraße 77', xad_3='Linz', xad_5='4020', xad_6='AUT')
        in1.insureds_id_number = CX(cx_1='15')

        # .. build the INSURANCE group ..
        insurance = DftP03Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = DFT_P03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.visit = visit
        msg.financial = [financial, financial_2]
        msg.diagnosis = diagnosis
        msg.insurance = insurance

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
    """ Based on live/at/at-orbis.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB')
        msh.sending_facility = HD(hd_1='KEPLER_LINZ')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='KEPLER_LINZ')
        msh.date_time_of_message = '20260210083100'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'ACK20260210001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'CA'
        msa.message_control_id = 'ADT20260210001'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/at/at-orbis.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PATH')
        msh.sending_facility = HD(hd_1='KEPLER_LINZ')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='KEPLER_LINZ')
        msh.date_time_of_message = '20260305160000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'DOC20260305002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260305160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='456789', cx_4='KEPLER_LINZ', cx_5='PI'), CX(cx_1='4781100175', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Lang', xpn_2='Florian', xpn_3='Leopold', xpn_7='L')
        pid.date_time_of_birth = '19750110'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEU', pl_2='502', pl_3='1', pl_4='KEPLER_LINZ')
        pv1.attending_doctor = XCN(
            xcn_1='20123456',
            xcn_2='Schwarz',
            xcn_3='Heinrich',
            xcn_6='Univ.Prof.Dr.',
            xcn_9='GDA&1.2.40.0.34.3.1.1&ISO',
            xcn_10='L',
            xcn_13='GDA',
        )

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='PATH', cwe_2='Neuropathologiebefund', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Text^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260304140000')
        txa.assigned_document_authenticator = XCN(
            xcn_1='20678901',
            xcn_2='Griesser',
            xcn_3='Anita',
            xcn_6='Dr.',
            xcn_9='GDA&1.2.40.0.34.3.1.1&ISO',
            xcn_10='L',
            xcn_13='GDA',
        )
        txa.placer_order_number = EI(ei_1='DOC-NEURO-2026-112')
        txa.unique_document_file_name = 'AU^Authentifiziert^HL70271'
        txa.document_confidentiality_status = '20260305155000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='PATH_RPT', cwe_2='Neuropathologiebefund', cwe_3='LOCAL')
        obx.obx_5 = (
            'Material: Stereotaktische Biopsie rechts temporal\\.br\\Makroskopisch: 3 Gewebezylinder, 1.2 cm gesamt\\.br\\Mikroskopisch: Diffuses Astrozytom,'
            ' IDH-mutiert, WHO Grad II\\.br\\Schlussfolgerung: Niedriggradiges Gliom.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Neuropathologie', cwe_3='LOCAL')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNTk1IDg0Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA1OTUgODQyXQovQ29udGVudHMg'
            'NCAwIFIKL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA2MCA+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3'
            'MDAgVGQKKEtlcGxlciBVbml2ZXJzaXRhdHNrbGluaWt1bSAtIE5ldXJvcGF0aG9sb2dpZWJlZnVuZCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250'
            'Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAw'
            'NTggMDAwMDAgbiAKMDAwMDAwMDE1MyAwMDAwMCBuIAowMDAwMDAwMzE0IDAwMDAwIG4gCjAwMDAwMDA0MjkgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2Ci9Sb290IDEgMCBSCj4+'
            'CnN0YXJ0eHJlZgo1MDkKJSVFT0YK'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = MdmT02Observation()
        observation_2.obx = obx_2

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.txa = txa
        msg.observation = [observation, observation_2]

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
    """ Based on live/at/at-orbis.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='KLIN_WELS')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='KLIN_WELS')
        msh.date_time_of_message = '20260319153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD20260319002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='678901', cx_4='KLIN_WELS', cx_5='PI'), CX(cx_1='8923230789', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Brunner', xpn_2='Michaela', xpn_3='Irmgard', xpn_7='L')
        pid.date_time_of_birth = '19890723'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GYNA', pl_2='208', pl_3='2', pl_4='KLIN_WELS')

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
        orc.placer_order_number = EI(ei_1='ORD77890', ei_2='ORBIS')
        orc.filler_order_number = EI(ei_1='FIL66234', ei_2='RIS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD77890', ei_2='ORBIS')
        obr.filler_order_number = EI(ei_1='FIL66234', ei_2='RIS')
        obr.universal_service_identifier = CWE(cwe_1='76805', cwe_2='Geburtshilflicher Ultraschall', cwe_3='CPT4')
        obr.observation_date_time = '20260319100000'
        obr.obr_16 = '20234567^Koller^Silvia^^^Dr.^^^GDA&1.2.40.0.34.3.1.1&ISO^L^^^GDA'
        obr.results_rpt_status_chng_date_time = '20260319152000'
        obr.diagnostic_serv_sect_id = 'RAD'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='76805', cwe_2='Ultraschallbefund', cwe_3='CPT4')
        obx.obx_5 = 'Befund: Einlingsschwangerschaft 38+2 SSW. Schädellage. Geschätztes Gewicht 3100 g. Fruchtwasser normal. Plazenta Hinterwand, Grad II.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Ultraschallbefund', cwe_3='LOCAL')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNTk1IDg0Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA1OTUgODQyXQovQ29udGVudHMg'
            'NCAwIFIKL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1NiA+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3'
            'MDAgVGQKKEtsaW5pa3VtIFdlbHMgLSBHZWJ1cnRzaGlsZmxpY2hlciBVbHRyYXNjaGFsbCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250Ci9TdWJ0'
            'eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAw'
            'MDAgbiAKMDAwMDAwMDE1MyAwMDAwMCBuIAowMDAwMDAwMzE0IDAwMDAwIG4gCjAwMDAwMDA0MjUgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0YXJ0'
            'eHJlZgo1MDUKJSVFT0YK'
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
    """ Based on live/at/at-orbis.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='SK_VOECKLA')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='SK_VOECKLA')
        msh.date_time_of_message = '20260408080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A05', msg_3='ADT_A05')
        msh.message_control_id = 'ADT20260408008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUT'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A05'
        evn.recorded_date_time = '20260408080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='234567', cx_4='SK_VOECKLA', cx_5='PI'), CX(cx_1='7359120878', cx_4='SVNR&1.2.40.0.10.1.4.3.1&ISO', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Aigner', xpn_2='Erwin', xpn_7='L')
        pid.date_time_of_birth = '19780812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stadtplatz 15', xad_3='Vöcklabruck', xad_4='4', xad_5='4840', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^CP^^43^664^8765432'
        pid.primary_language = CWE(cwe_1='DEU', cwe_2='German', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Verheiratet', cwe_3='HL70002')
        pid.veterans_military_status = CWE(cwe_1='AUT', cwe_2='Austrian', cwe_3='HL70171')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='ORTH', pl_2='304', pl_3='1', pl_4='SK_VOECKLA', pl_6='N', pl_7='A', pl_8='3')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.attending_doctor = XCN(xcn_1='20345678', xcn_2='Thaler', xcn_3='Rainer', xcn_6='Dr.', xcn_9='GDA&1.2.40.0.34.3.1.1&ISO', xcn_10='L', xcn_13='GDA')
        pv1.visit_number = CX(cx_1='FN2026-31002', cx_4='SK_VOECKLA', cx_5='VN')
        pv1.admit_date_time = '20260415080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='04')
        in1.insurance_company_name = XON(xon_1='ÖGK Oberösterreich')
        in1.insurance_company_address = XAD(xad_1='Gruberstraße 77', xad_3='Linz', xad_5='4020', xad_6='AUT')
        in1.insureds_id_number = CX(cx_1='15')

        # .. build the INSURANCE group ..
        insurance = AdtA05Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = insurance

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
