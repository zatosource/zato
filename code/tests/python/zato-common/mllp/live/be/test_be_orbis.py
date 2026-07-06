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
from zato.hl7v2.v2_9.datatypes import CNE, CP, CWE, CX, DR, EI, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA05Insurance, AdtA39Patient, BarP01Diagnosis, BarP01Insurance, BarP01Visit, DftP03Diagnosis, \
    DftP03Financial, DftP03Insurance, DftP03Visit, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, SiuS12PersonnelResource, SiuS12Resources, \
    SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, BAR_P01, DFT_P03, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, DG1, EVN, FT1, GT1, IN1, MRG, MSA, MSH, NTE, OBR, OBX, ORC, PID, PV1, PV2, RGS, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('be', 'be-orbis.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/be/be-orbis.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='AZ_MONICA')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='AZ_MONICA')
        msh.date_time_of_message = '20250310083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'ADT001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'BEL'
        msh.character_set = '8859/15'
        msh.principal_language_of_message = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20250310083000'
        evn.event_occurred = '20250310082500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='234567', cx_4='AZ_MONICA', cx_5='PI'),
            CX(cx_1='86072534218', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Peeters', xpn_2='Ilse', xpn_3='Marleen', xpn_7='L')
        pid.date_time_of_birth = '19860725'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Plantin en Moretuslei 88', xad_3='Borgerhout', xad_4='VAN', xad_5='2140', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^3^2456789~^PRN^CP^^32^476^234567'
        pid.pid_14 = '^WPN^PH^^32^3^2512222'
        pid.primary_language = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='G', cwe_2='Gehuwd', cwe_3='HL70002')
        pid.veterans_military_status = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70171')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='201', pl_3='1', pl_4='AZ_MONICA', pl_6='N', pl_7='A', pl_8='4')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.attending_doctor = XCN(xcn_1='22312345601', xcn_2='Michiels', xcn_3='Dirk', xcn_6='Dr.', xcn_9='AZ_MONICA', xcn_10='L', xcn_13='NIHDI')
        pv1.referring_doctor = XCN(xcn_1='22312345602', xcn_2='Coppens', xcn_3='Frank', xcn_6='Dr.', xcn_9='AZ_MONICA', xcn_10='L', xcn_13='NIHDI')
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.pv1_20 = 'VN2026-5632^^^AZ_MONICA^VN'
        pv1.discharge_date_time = '20250310082500'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.expected_discharge_date_time = '20250317'
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
    """ Based on live/be/be-orbis.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='AZ_GROENINGE')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='AZ_GROENINGE')
        msh.date_time_of_message = '20250415091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'ADT002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'BEL'
        msh.character_set = '8859/15'
        msh.principal_language_of_message = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20250415091500'
        evn.event_occurred = '20250415090800'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='890123', cx_4='AZ_GROENINGE', cx_5='PI'),
            CX(cx_1='91031245679', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Van Hoeck', xpn_2='Wim', xpn_3='Ronny', xpn_7='L')
        pid.date_time_of_birth = '19910312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Doorniksesteenweg 33', xad_3='Kortrijk', xad_4='VWV', xad_5='8500', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^56^345678~^PRN^CP^^32^494^679001'
        pid.pid_14 = '^WPN^PH^^32^56^371222'
        pid.primary_language = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.religion = CWE(cwe_1='CAT', cwe_2='Catholic', cwe_3='HL70006')
        pid.veterans_military_status = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70171')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTH', pl_2='105', pl_3='2', pl_4='AZ_GROENINGE', pl_6='N', pl_7='A', pl_8='3')
        pv1.admission_type = CWE(cwe_1='U')
        pv1.attending_doctor = XCN(xcn_1='22398765401', xcn_2='Mertens', xcn_3='Anke', xcn_6='Dr.', xcn_9='AZ_GROENINGE', xcn_10='L', xcn_13='NIHDI')
        pv1.consulting_doctor = XCN(xcn_1='CAR')
        pv1.hospital_service = CWE(cwe_1='ORTH')
        pv1.pv1_20 = 'VN2026-9944^^^AZ_GROENINGE^VN'
        pv1.discharge_date_time = '20250415090800'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='210')
        in1.insurance_company_name = XON(xon_1='Solidaris')
        in1.insurance_company_address = XAD(xad_1='Lambermontlaan 100', xad_3='Schaarbeek', xad_5='1030', xad_6='BE')
        in1.insureds_id_number = CX(cx_1='33')

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
    """ Based on live/be/be-orbis.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='AZ_IMELDA')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='AZ_IMELDA')
        msh.date_time_of_message = '20250502140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'ADT003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'BEL'
        msh.character_set = '8859/15'
        msh.principal_language_of_message = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20250502140000'
        evn.event_occurred = '20250502135500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='456789', cx_4='AZ_IMELDA', cx_5='PI'),
            CX(cx_1='89061234578', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Claessens', xpn_2='Griet', xpn_7='L')
        pid.date_time_of_birth = '19890612'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Imeldalaan 22', xad_3='Bonheiden', xad_4='VAN', xad_5='2820', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^CP^^32^478^345678'
        pid.primary_language = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='G', cwe_2='Gehuwd', cwe_3='HL70002')
        pid.veterans_military_status = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70171')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='302', pl_3='3', pl_4='AZ_IMELDA', pl_6='N', pl_7='D', pl_8='4')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.prior_patient_location = PL(pl_1='CHI', pl_2='105', pl_3='1', pl_4='AZ_IMELDA', pl_6='N', pl_7='D', pl_8='2')
        pv1.attending_doctor = XCN(xcn_1='22387651201', xcn_2='Hendrickx', xcn_3='Jeroen', xcn_6='Dr.', xcn_9='AZ_IMELDA', xcn_10='L', xcn_13='NIHDI')
        pv1.visit_number = CX(cx_1='VN2026-2358', cx_4='AZ_IMELDA', cx_5='VN')
        pv1.admit_date_time = '20250502135500'

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
    """ Based on live/be/be-orbis.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='AZ_MONICA')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='AZ_MONICA')
        msh.date_time_of_message = '20250318100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'ADT004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'BEL'
        msh.character_set = '8859/15'
        msh.principal_language_of_message = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20250318100000'
        evn.event_occurred = '20250318095500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='234567', cx_4='AZ_MONICA', cx_5='PI'),
            CX(cx_1='86072534218', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Peeters', xpn_2='Ilse', xpn_3='Marleen', xpn_7='L')
        pid.date_time_of_birth = '19860725'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Plantin en Moretuslei 88', xad_3='Borgerhout', xad_4='VAN', xad_5='2140', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^3^2456789~^PRN^CP^^32^476^234567'
        pid.primary_language = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='G', cwe_2='Gehuwd', cwe_3='HL70002')
        pid.veterans_military_status = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70171')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='201', pl_3='1', pl_4='AZ_MONICA', pl_6='N', pl_7='B', pl_8='4')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.attending_doctor = XCN(xcn_1='22312345601', xcn_2='Michiels', xcn_3='Dirk', xcn_6='Dr.', xcn_9='AZ_MONICA', xcn_10='L', xcn_13='NIHDI')
        pv1.visit_number = CX(cx_1='VN2026-5632', cx_4='AZ_MONICA', cx_5='VN')
        pv1.discharge_disposition = CWE(cwe_1='011')
        pv1.admit_date_time = '20250310082500'
        pv1.discharge_date_time = '20250318095500'

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
    """ Based on live/be/be-orbis.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='AZ_GROENINGE')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='AZ_GROENINGE')
        msh.date_time_of_message = '20250420143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'ADT005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'BEL'
        msh.character_set = '8859/15'
        msh.principal_language_of_message = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250420143000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='890123', cx_4='AZ_GROENINGE', cx_5='PI'),
            CX(cx_1='91031245679', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Van Hoeck', xpn_2='Wim', xpn_3='Ronny', xpn_7='L')
        pid.date_time_of_birth = '19910312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Brugsesteenweg 44', xad_3='Kortrijk', xad_4='VWV', xad_5='8500', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^56^345678~^PRN^CP^^32^494^679001'
        pid.pid_14 = '^WPN^PH^^32^56^371222'
        pid.primary_language = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.religion = CWE(cwe_1='CAT', cwe_2='Catholic', cwe_3='HL70006')
        pid.veterans_military_status = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70171')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTH', pl_2='105', pl_3='2', pl_4='AZ_GROENINGE', pl_6='N', pl_7='A', pl_8='3')
        pv1.admission_type = CWE(cwe_1='U')
        pv1.attending_doctor = XCN(xcn_1='22398765401', xcn_2='Mertens', xcn_3='Anke', xcn_6='Dr.', xcn_9='AZ_GROENINGE', xcn_10='L', xcn_13='NIHDI')
        pv1.visit_number = CX(cx_1='VN2026-9944', cx_4='AZ_GROENINGE', cx_5='VN')
        pv1.admit_date_time = '20250415090800'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='210')
        in1.insurance_company_name = XON(xon_1='Solidaris')
        in1.insurance_company_address = XAD(xad_1='Lambermontlaan 100', xad_3='Schaarbeek', xad_5='1030', xad_6='BE')
        in1.insureds_id_number = CX(cx_1='33')

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
    """ Based on live/be/be-orbis.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='AZ_MONICA')
        msh.receiving_application = HD(hd_1='PACS')
        msh.receiving_facility = HD(hd_1='AZ_MONICA')
        msh.date_time_of_message = '20250605100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'ADT006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'BEL'
        msh.character_set = '8859/15'
        msh.principal_language_of_message = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250605100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='678901', cx_4='AZ_MONICA', cx_5='PI'),
            CX(cx_1='79050912345', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Bogaert', xpn_2='Stijn', xpn_7='L')
        pid.date_time_of_birth = '19790509'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Nationalestraat 55', xad_3='Antwerpen', xad_4='VAN', xad_5='2000', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^CP^^32^486^900123'
        pid.primary_language = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.veterans_military_status = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70171')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='RADIO', pl_3='01', pl_4='AZ_MONICA')
        pv1.attending_doctor = XCN(xcn_1='22312345601', xcn_2='Michiels', xcn_3='Dirk', xcn_6='Dr.', xcn_9='AZ_MONICA', xcn_10='L', xcn_13='NIHDI')
        pv1.visit_number = CX(cx_1='VN2026-7788', cx_4='AZ_MONICA', cx_5='VN')
        pv1.admit_date_time = '20250605100000'

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
    """ Based on live/be/be-orbis.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='AZ_IMELDA')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='AZ_IMELDA')
        msh.date_time_of_message = '20250610153000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'ADT007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'BEL'
        msh.character_set = '8859/15'
        msh.principal_language_of_message = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250610153000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='456789', cx_4='AZ_IMELDA', cx_5='PI'),
            CX(cx_1='89061234578', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Claessens', xpn_2='Griet', xpn_7='L')
        pid.date_time_of_birth = '19890612'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Imeldalaan 22', xad_3='Bonheiden', xad_4='VAN', xad_5='2820', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^CP^^32^478^345678'
        pid.primary_language = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='G', cwe_2='Gehuwd', cwe_3='HL70002')
        pid.veterans_military_status = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70171')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = [
            CX(cx_1='456000', cx_4='AZ_IMELDA', cx_5='PI'),
            CX(cx_1='89061234578', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
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
    """ Based on live/be/be-orbis.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='AZ_GROENINGE')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='AZ_GROENINGE')
        msh.date_time_of_message = '20250422093000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ORM001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='890123', cx_4='AZ_GROENINGE', cx_5='PI'),
            CX(cx_1='91031245679', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Van Hoeck', xpn_2='Wim', xpn_3='Ronny', xpn_7='L')
        pid.date_time_of_birth = '19910312'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTH', pl_2='105', pl_3='2', pl_4='AZ_GROENINGE')
        pv1.attending_doctor = XCN(xcn_1='22398765401', xcn_2='Mertens', xcn_3='Anke', xcn_6='Dr.', xcn_9='AZ_GROENINGE', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD4567', ei_2='ORBIS')
        orc.placer_order_group_number = EI(ei_1='GRP001', ei_2='ORBIS')
        orc.date_time_of_order_event = '20250422093000'
        orc.orc_12 = '22398765401^Mertens^Anke^^^Dr.^^^AZ_GROENINGE^L^^^NIHDI'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD4567', ei_2='ORBIS')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='X-ray Chest 2 views', cwe_3='CPT4')
        obr.observation_date_time = '20250422093000'
        obr.obr_16 = '22398765401^Mertens^Anke^^^Dr.^^^AZ_GROENINGE^L^^^NIHDI'
        obr.obr_27 = '^STAT'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M54.5', cwe_2='Lage rugpijn', cwe_3='ICD10BE')

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
        nte.comment = 'Post-operatieve controle na knie-artroscopie.'

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
    """ Based on live/be/be-orbis.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='AZ_MONICA')
        msh.receiving_application = HD(hd_1='GLIMS')
        msh.receiving_facility = HD(hd_1='AZ_MONICA')
        msh.date_time_of_message = '20250311080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ORM002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='234567', cx_4='AZ_MONICA', cx_5='PI'),
            CX(cx_1='86072534218', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Peeters', xpn_2='Ilse', xpn_3='Marleen', xpn_7='L')
        pid.date_time_of_birth = '19860725'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='201', pl_3='1', pl_4='AZ_MONICA')
        pv1.attending_doctor = XCN(xcn_1='22312345601', xcn_2='Michiels', xcn_3='Dirk', xcn_6='Dr.', xcn_9='AZ_MONICA', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD8901', ei_2='ORBIS')
        orc.placer_order_group_number = EI(ei_1='GRP002', ei_2='ORBIS')
        orc.date_time_of_order_event = '20250311080000'
        orc.orc_12 = '22312345601^Michiels^Dirk^^^Dr.^^^AZ_MONICA^L^^^NIHDI'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD8901', ei_2='ORBIS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='CMP', cwe_3='LN')
        obr.observation_date_time = '20250311080000'
        obr.obr_16 = '22312345601^Michiels^Dirk^^^Dr.^^^AZ_MONICA^L^^^NIHDI'
        obr.obr_27 = '^ROUTINE'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.1', cwe_2='Atherosclerotische hartziekte', cwe_3='ICD10BE')

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
    """ Based on live/be/be-orbis.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='AZ_MONICA')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='AZ_MONICA')
        msh.date_time_of_message = '20250311163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB00042'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='234567', cx_4='AZ_MONICA', cx_5='PI'),
            CX(cx_1='86072534218', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Peeters', xpn_2='Ilse', xpn_3='Marleen', xpn_7='L')
        pid.date_time_of_birth = '19860725'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='201', pl_3='1', pl_4='AZ_MONICA')

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
        orc.placer_order_number = EI(ei_1='ORD8901', ei_2='ORBIS')
        orc.filler_order_number = EI(ei_1='FIL5678', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD8901', ei_2='ORBIS')
        obr.filler_order_number = EI(ei_1='FIL5678', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='CMP', cwe_3='LN')
        obr.observation_date_time = '20250311080000'
        obr.obr_16 = '22312345601^Michiels^Dirk^^^Dr.^^^AZ_MONICA^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250311162000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '5.4'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.9-6.1'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_2.obx_5 = '88'
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
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Ureum', cwe_3='LN')
        obx_3.obx_5 = '5.8'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.5-7.5'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Natrium', cwe_3='LN')
        obx_4.obx_5 = '140'
        obx_4.units = CWE(cwe_1='mmol/L')
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
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Kalium', cwe_3='LN')
        obx_5.obx_5 = '4.1'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='17861-6', cwe_2='Calcium', cwe_3='LN')
        obx_6.obx_5 = '2.35'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '2.15-2.55'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALAT', cwe_3='LN')
        obx_7.obx_5 = '28'
        obx_7.units = CWE(cwe_1='U/L')
        obx_7.reference_range = '7-56'
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
    """ Based on live/be/be-orbis.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='AZ_GROENINGE')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='AZ_GROENINGE')
        msh.date_time_of_message = '20250423141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB00099'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='890123', cx_4='AZ_GROENINGE', cx_5='PI'),
            CX(cx_1='91031245679', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Van Hoeck', xpn_2='Wim', xpn_3='Ronny', xpn_7='L')
        pid.date_time_of_birth = '19910312'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTH', pl_2='105', pl_3='2', pl_4='AZ_GROENINGE')

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
        orc.placer_order_number = EI(ei_1='ORD3457', ei_2='ORBIS')
        orc.filler_order_number = EI(ei_1='FIL9012', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD3457', ei_2='ORBIS')
        obr.filler_order_number = EI(ei_1='FIL9012', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC with Diff', cwe_3='LN')
        obr.observation_date_time = '20250423093000'
        obr.obr_16 = '22398765401^Mertens^Anke^^^Dr.^^^AZ_GROENINGE^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250423141000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobine', cwe_3='LN')
        obx.obx_5 = '14.2'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '13.5-17.5'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocriet', cwe_3='LN')
        obx_2.obx_5 = '42.1'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '38.3-48.6'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocyten', cwe_3='LN')
        obx_3.obx_5 = '7.8'
        obx_3.units = CWE(cwe_1='10*9/L')
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
        obx_4.observation_identifier = CWE(cwe_1='787-2', cwe_2='Erytrocyten', cwe_3='LN')
        obx_4.obx_5 = '4.85'
        obx_4.units = CWE(cwe_1='10*12/L')
        obx_4.reference_range = '4.50-5.90'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Trombocyten', cwe_3='LN')
        obx_5.obx_5 = '245'
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
        obx_6.observation_identifier = CWE(cwe_1='770-8', cwe_2='Neutrofielen', cwe_3='LN')
        obx_6.obx_5 = '4.2'
        obx_6.units = CWE(cwe_1='10*9/L')
        obx_6.reference_range = '1.8-7.7'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='731-0', cwe_2='Lymfocyten', cwe_3='LN')
        obx_7.obx_5 = '2.4'
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
    """ Based on live/be/be-orbis.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='AZ_MONICA')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='AZ_MONICA')
        msh.date_time_of_message = '20250612110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='678901', cx_4='AZ_MONICA', cx_5='PI'),
            CX(cx_1='79050912345', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Bogaert', xpn_2='Stijn', xpn_7='L')
        pid.date_time_of_birth = '19790509'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='RADIO', pl_3='01', pl_4='AZ_MONICA')

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
        orc.placer_order_number = EI(ei_1='ORD5611', ei_2='ORBIS')
        orc.filler_order_number = EI(ei_1='FIL7811', ei_2='RIS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD5611', ei_2='ORBIS')
        obr.filler_order_number = EI(ei_1='FIL7811', ei_2='RIS')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Thorax AP en Lat', cwe_3='CPT4')
        obr.observation_date_time = '20250612091500'
        obr.obr_16 = '22312345601^Michiels^Dirk^^^Dr.^^^AZ_MONICA^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250612105500'
        obr.diagnostic_serv_sect_id = 'RAD'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='71020', cwe_2='Thorax AP en Lat', cwe_3='CPT4')
        obx.obx_5 = 'Conclusie: Geen actieve longpathologie. Hart normaal van grootte.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Radiologieverslag', cwe_3='LOCAL')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNTk1IDg0Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA1OTUgODQyXQovQ29udGVudHMg'
            'NCAwIFIKL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3'
            'MDAgVGQKKEFaIE1vbmljYSAtIFJhZGlvbG9naWV2ZXJzbGFnKSBUagoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFz'
            'ZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDE1'
            'MyAwMDAwMCBuIAowMDAwMDAwMzE0IDAwMDAwIG4gCjAwMDAwMDA0MTIgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgo0OTMKJSVFT0YK'
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
    """ Based on live/be/be-orbis.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='AZ_IMELDA')
        msh.receiving_application = HD(hd_1='SCHED')
        msh.receiving_facility = HD(hd_1='AZ_IMELDA')
        msh.date_time_of_message = '20250520100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'SCH00123'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20362', ei_2='ORBIS')
        sch.filler_appointment_id = EI(ei_1='APT20362', ei_2='SCHED')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='CONSULT', cwe_2='Raadpleging', cwe_3='LOCAL')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^30^20250527093000^20250527100000'
        sch.filler_contact_person = XCN(xcn_1='22387651201', xcn_2='Hendrickx', xcn_3='Jeroen', xcn_6='Dr.', xcn_9='AZ_IMELDA', xcn_10='L', xcn_13='NIHDI')
        sch.filler_contact_address = XAD(xad_1='AZ_IMELDA')
        sch.entered_by_person = XCN(xcn_1='Booked')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='456789', cx_4='AZ_IMELDA', cx_5='PI'),
            CX(cx_1='89061234578', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Claessens', xpn_2='Griet', xpn_7='L')
        pid.date_time_of_birth = '19890612'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='ORTHO', pl_3='01', pl_4='AZ_IMELDA')
        pv1.attending_doctor = XCN(xcn_1='22387651201', xcn_2='Hendrickx', xcn_3='Jeroen', xcn_6='Dr.', xcn_9='AZ_IMELDA', xcn_10='L', xcn_13='NIHDI')

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
        ais.universal_service_identifier = CWE(cwe_1='CONSULT', cwe_2='Raadpleging orthopedie', cwe_3='LOCAL')
        ais.start_date_time_offset_units = CNE(cne_1='20250527093000')
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
        aip.personnel_resource_id = XCN(xcn_1='22387651201', xcn_2='Hendrickx', xcn_3='Jeroen', xcn_6='Dr.', xcn_9='AZ_IMELDA', xcn_10='L', xcn_13='NIHDI')
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
        ail.location_resource_id = PL(pl_1='CONS', pl_2='ORTHO', pl_3='01', pl_4='AZ_IMELDA')
        ail.location_group = CWE(cwe_1='20250527093000')
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
    """ Based on live/be/be-orbis.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='AZ_MONICA')
        msh.receiving_application = HD(hd_1='DMS')
        msh.receiving_facility = HD(hd_1='AZ_MONICA')
        msh.date_time_of_message = '20250615143000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'DOC00456'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250615143000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='234567', cx_4='AZ_MONICA', cx_5='PI'),
            CX(cx_1='86072534218', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Peeters', xpn_2='Ilse', xpn_3='Marleen', xpn_7='L')
        pid.date_time_of_birth = '19860725'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='OR2', pl_3='01', pl_4='AZ_MONICA')
        pv1.attending_doctor = XCN(xcn_1='22312345603', xcn_2='Wouters', xcn_3='Pieter', xcn_6='Dr.', xcn_9='AZ_MONICA', xcn_10='L', xcn_13='NIHDI')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='OP', cwe_2='Operatieverslag', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Text^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20250615120000')
        txa.assigned_document_authenticator = XCN(
            xcn_1='22312345603',
            xcn_2='Wouters',
            xcn_3='Pieter',
            xcn_6='Dr.',
            xcn_9='AZ_MONICA',
            xcn_10='L',
            xcn_13='NIHDI',
        )
        txa.placer_order_number = EI(ei_1='DOC09876')
        txa.unique_document_file_name = 'AU^Geauthenticeerd^HL70271'
        txa.document_confidentiality_status = '20250615143000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='OP_NOTE', cwe_2='Operatieverslag', cwe_3='LOCAL')
        obx.obx_5 = (
            'Ingreep: Laparoscopische cholecystectomie\\.br\\Patient verdroeg de procedure goed\\.br\\Geen complicaties\\.br\\Geschat bloedverlies: 50 mL\\.br\\P'
            'reparaten verzonden naar pathologie.'
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
    """ Based on live/be/be-orbis.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='AZ_GROENINGE')
        msh.receiving_application = HD(hd_1='BILLING')
        msh.receiving_facility = HD(hd_1='AZ_GROENINGE')
        msh.date_time_of_message = '20250425180000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'CHG00234'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20250425180000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='890123', cx_4='AZ_GROENINGE', cx_5='PI'),
            CX(cx_1='91031245679', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Van Hoeck', xpn_2='Wim', xpn_3='Ronny', xpn_7='L')
        pid.date_time_of_birth = '19910312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Brugsesteenweg 44', xad_3='Kortrijk', xad_4='VWV', xad_5='8500', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTH', pl_2='105', pl_3='2', pl_4='AZ_GROENINGE')
        pv1.attending_doctor = XCN(xcn_1='22398765401', xcn_2='Mertens', xcn_3='Anke', xcn_6='Dr.', xcn_9='AZ_GROENINGE', xcn_10='L', xcn_13='NIHDI')
        pv1.hospital_service = CWE(cwe_1='ORTH')
        pv1.patient_type = CWE(cwe_1='VN2026-9944', cwe_4='AZ_GROENINGE', cwe_5='VN')
        pv1.prior_temporary_location = PL(pl_1='20250415090800')

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_id = CX(cx_1='CHG012')
        ft1.transaction_batch_id = 'CHG012'
        ft1.transaction_date = DR(dr_1='20250415')
        ft1.transaction_posting_date = '20250425'
        ft1.transaction_type = CWE(cwe_1='CG')
        ft1.transaction_code = CWE(cwe_1='598404', cwe_2='Gewrichtsinfiltratie', cwe_3='RIZIV')
        ft1.transaction_amount_extended = CP(cp_1='1')
        ft1.department_code = CWE(cwe_1='ORTH')
        ft1.performed_by_code = XCN(xcn_1='M54.5', xcn_2='Lage rugpijn', xcn_3='ICD10BE')
        ft1.ordered_by_code = XCN(xcn_1='22398765401', xcn_2='Mertens', xcn_3='Anke', xcn_6='Dr.', xcn_9='AZ_GROENINGE', xcn_10='L', xcn_13='NIHDI')
        ft1.filler_order_number = EI(ei_1='45.50')

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_id = CX(cx_1='CHG023')
        ft1_2.transaction_batch_id = 'CHG023'
        ft1_2.transaction_date = DR(dr_1='20250416')
        ft1_2.transaction_posting_date = '20250425'
        ft1_2.transaction_type = CWE(cwe_1='CG')
        ft1_2.transaction_code = CWE(cwe_1='540153', cwe_2='Kinesitherapie individueel', cwe_3='RIZIV')
        ft1_2.transaction_amount_extended = CP(cp_1='1')
        ft1_2.department_code = CWE(cwe_1='KINE')
        ft1_2.performed_by_code = XCN(xcn_1='M54.5', xcn_2='Lage rugpijn', xcn_3='ICD10BE')
        ft1_2.ordered_by_code = XCN(xcn_1='22398765402', xcn_2='Aerts', xcn_3='Katrien', xcn_6='Kine', xcn_9='AZ_GROENINGE', xcn_10='L', xcn_13='NIHDI')
        ft1_2.filler_order_number = EI(ei_1='22.00')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M54.5', cwe_2='Lage rugpijn', cwe_3='ICD10BE')
        dg1.diagnosis_date_time = '20250415'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the DIAGNOSIS group ..
        diagnosis = DftP03Diagnosis()
        diagnosis.dg1 = dg1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='210')
        in1.insurance_company_name = XON(xon_1='Solidaris')
        in1.insurance_company_address = XAD(xad_1='Lambermontlaan 100', xad_3='Schaarbeek', xad_5='1030', xad_6='BE')
        in1.insureds_id_number = CX(cx_1='33')

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
    """ Based on live/be/be-orbis.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB')
        msh.sending_facility = HD(hd_1='AZ_MONICA')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='AZ_MONICA')
        msh.date_time_of_message = '20250310083100'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'ACK001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'BEL'
        msh.character_set = '8859/15'
        msh.principal_language_of_message = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'CA'
        msa.message_control_id = 'ADT001'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/be/be-orbis.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='AZ_IMELDA')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='AZ_IMELDA')
        msh.date_time_of_message = '20250520080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A05', msg_3='ADT_A05')
        msh.message_control_id = 'ADT008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'BEL'
        msh.character_set = '8859/15'
        msh.principal_language_of_message = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A05'
        evn.recorded_date_time = '20250520080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='456789', cx_4='AZ_IMELDA', cx_5='PI'),
            CX(cx_1='89061234578', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Claessens', xpn_2='Griet', xpn_7='L')
        pid.date_time_of_birth = '19890612'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Imeldalaan 22', xad_3='Bonheiden', xad_4='VAN', xad_5='2820', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^CP^^32^478^345678'
        pid.primary_language = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='G', cwe_2='Gehuwd', cwe_3='HL70002')
        pid.veterans_military_status = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70171')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='ORTH', pl_2='105', pl_3='2', pl_4='AZ_IMELDA', pl_6='N', pl_7='A', pl_8='3')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.attending_doctor = XCN(xcn_1='22387651201', xcn_2='Hendrickx', xcn_3='Jeroen', xcn_6='Dr.', xcn_9='AZ_IMELDA', xcn_10='L', xcn_13='NIHDI')
        pv1.visit_number = CX(cx_1='VN2026-2461', cx_4='AZ_IMELDA', cx_5='VN')
        pv1.admit_date_time = '20250527080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='407')
        in1.insurance_company_name = XON(xon_1='Partenamut')
        in1.insurance_company_address = XAD(xad_1='Rue Royale 55', xad_3='Bruxelles', xad_5='1000', xad_6='BE')
        in1.insureds_id_number = CX(cx_1='33')

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
    """ Based on live/be/be-orbis.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='AZ_GROENINGE')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='AZ_GROENINGE')
        msh.date_time_of_message = '20250428163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MICRO001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='890123', cx_4='AZ_GROENINGE', cx_5='PI'),
            CX(cx_1='91031245679', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Van Hoeck', xpn_2='Wim', xpn_3='Ronny', xpn_7='L')
        pid.date_time_of_birth = '19910312'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTH', pl_2='105', pl_3='2', pl_4='AZ_GROENINGE')

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
        orc.placer_order_number = EI(ei_1='ORD6611', ei_2='ORBIS')
        orc.filler_order_number = EI(ei_1='FIL0011', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD6611', ei_2='ORBIS')
        obr.filler_order_number = EI(ei_1='FIL0011', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Bloedkweek', cwe_3='LN')
        obr.observation_date_time = '20250425100000'
        obr.obr_16 = '22398765401^Mertens^Anke^^^Dr.^^^AZ_GROENINGE^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250428160000'
        obr.diagnostic_serv_sect_id = 'MB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='11475-1', cwe_2='Micro-organisme identificatie', cwe_3='LN')
        obx.obx_5 = '112283005^Staphylococcus aureus^SCT'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Gevoeligheidsprofiel', cwe_3='LN')
        obx_2.obx_5 = 'Zie antibiogram'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18900-1', cwe_2='Amoxicilline-clavulaanzuur', cwe_3='LN')
        obx_3.obx_5 = 'S^Gevoelig'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18903-5', cwe_2='Ciprofloxacine', cwe_3='LN')
        obx_4.obx_5 = 'R^Resistent'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18961-3', cwe_2='Vancomycine', cwe_3='LN')
        obx_5.obx_5 = 'S^Gevoelig'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='35659-2', cwe_2='MIC Vancomycine', cwe_3='LN')
        obx_6.obx_5 = '1.0'
        obx_6.units = CWE(cwe_1='ug/mL')
        obx_6.reference_range = '<=2'
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
    """ Based on live/be/be-orbis.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PATH')
        msh.sending_facility = HD(hd_1='AZ_IMELDA')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='AZ_IMELDA')
        msh.date_time_of_message = '20250604160000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'DOC00789'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250604160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='456789', cx_4='AZ_IMELDA', cx_5='PI'),
            CX(cx_1='89061234578', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Claessens', xpn_2='Griet', xpn_7='L')
        pid.date_time_of_birth = '19890612'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='OR2', pl_3='01', pl_4='AZ_IMELDA')
        pv1.attending_doctor = XCN(xcn_1='22387651201', xcn_2='Hendrickx', xcn_3='Jeroen', xcn_6='Dr.', xcn_9='AZ_IMELDA', xcn_10='L', xcn_13='NIHDI')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='PATH', cwe_2='Pathologieverslag', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Text^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20250603140000')
        txa.assigned_document_authenticator = XCN(
            xcn_1='22387651202',
            xcn_2='Janssens',
            xcn_3='Hilde',
            xcn_6='Dr.',
            xcn_9='AZ_IMELDA',
            xcn_10='L',
            xcn_13='NIHDI',
        )
        txa.placer_order_number = EI(ei_1='DOC44532')
        txa.unique_document_file_name = 'AU^Geauthenticeerd^HL70271'
        txa.document_confidentiality_status = '20250604155000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='PATH_RPT', cwe_2='Pathologieverslag', cwe_3='LOCAL')
        obx.obx_5 = (
            'Macroscopisch: Galblaas, 8.5 cm, serosa glad\\.br\\Microscopisch: Chronische cholecystitis, geen maligniteit\\.br\\Conclusie: Chronische cholecy'
            'stitis.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Pathologierapport', cwe_3='LOCAL')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNTk1IDg0Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA1OTUgODQyXQovQ29udGVudHMg'
            'NCAwIFIKL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1NiA+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3'
            'MDAgVGQKKEFaIEltZWxkYSAtIFBhdGhvbG9naWV2ZXJzbGFnIC0gQ2hvbGVjeXN0ZWN0b21pZSkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250Ci9T'
            'dWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTgg'
            'MDAwMDAgbiAKMDAwMDAwMDE1MyAwMDAwMCBuIAowMDAwMDAwMzE0IDAwMDAwIG4gCjAwMDAwMDA0MjUgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0'
            'YXJ0eHJlZgo1MDYKJSVFT0YK'
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
    """ Based on live/be/be-orbis.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='AZ_MONICA')
        msh.receiving_application = HD(hd_1='BILLING')
        msh.receiving_facility = HD(hd_1='AZ_MONICA')
        msh.date_time_of_message = '20250310090000'
        msh.message_type = MSG(msg_1='BAR', msg_2='P01', msg_3='BAR_P01')
        msh.message_control_id = 'BAR001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P01'
        evn.recorded_date_time = '20250310090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='234567', cx_4='AZ_MONICA', cx_5='PI'),
            CX(cx_1='86072534218', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Peeters', xpn_2='Ilse', xpn_3='Marleen', xpn_7='L')
        pid.date_time_of_birth = '19860725'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Plantin en Moretuslei 88', xad_3='Borgerhout', xad_4='VAN', xad_5='2140', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='201', pl_3='1', pl_4='AZ_MONICA')
        pv1.attending_doctor = XCN(xcn_1='22312345601', xcn_2='Michiels', xcn_3='Dirk', xcn_6='Dr.', xcn_9='AZ_MONICA', xcn_10='L', xcn_13='NIHDI')
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.patient_type = CWE(cwe_1='VN2026-5632', cwe_4='AZ_MONICA', cwe_5='VN')
        pv1.prior_temporary_location = PL(pl_1='20250310082500')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.1', cwe_2='Atherosclerotische hartziekte', cwe_3='ICD10BE')
        dg1.diagnosis_date_time = '20250310'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the DIAGNOSIS group ..
        diagnosis = BarP01Diagnosis()
        diagnosis.dg1 = dg1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='210')
        in1.insurance_company_name = XON(xon_1='Solidaris')
        in1.insurance_company_address = XAD(xad_1='Lambermontlaan 100', xad_3='Schaarbeek', xad_5='1030', xad_6='BE')
        in1.insureds_id_number = CX(cx_1='33')

        # .. build the INSURANCE group ..
        insurance = BarP01Insurance()
        insurance.in1 = in1

        # .. build the VISIT group ..
        visit = BarP01Visit()
        visit.pv1 = pv1
        visit.diagnosis = diagnosis
        visit.insurance = insurance

        # .. build GT1 ..
        gt1 = GT1()
        gt1.set_id_gt1 = '1'
        gt1.guarantor_name = XPN(xpn_1='Peeters', xpn_2='Ilse', xpn_3='Marleen', xpn_7='L')
        gt1.guarantor_address = XAD(xad_1='Plantin en Moretuslei 88', xad_3='Borgerhout', xad_4='VAN', xad_5='2140', xad_6='BE', xad_7='H')
        gt1.guarantor_ph_num_home = XTN(xtn_2='PRN', xtn_3='PH', xtn_5='32', xtn_6='3', xtn_7='2456789')
        gt1.guarantor_type = CWE(cwe_1='SELF')

        # .. assemble the full message ..
        msg = BAR_P01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.visit = visit
        msg.extra_segments = [gt1]

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
