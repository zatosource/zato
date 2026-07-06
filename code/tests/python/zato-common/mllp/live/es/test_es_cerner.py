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
from zato.hl7v2.v2_9.datatypes import AUI, CNE, CP, CWE, CX, DR, EI, HD, MOC, MSG, PL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA39Patient, DftP03Diagnosis, DftP03Financial, DftP03Visit, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, \
    OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, \
    SiuS12Patient, SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, DFT_P03, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, AL1, DG1, EVN, FT1, IN1, MRG, MSA, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, RGS, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('es', 'es-cerner.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/es/es-cerner.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNERPM')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='BDAC')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20260301120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'CERN00101'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260301120000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40009823456', cx_4='001'), CX(cx_1='43567891X', cx_4='014&000'), CX(cx_1='BBBBX435678912345', cx_4='025')]
        pid.patient_name = XPN(xpn_1='FIOL', xpn_2='MARGALIDA', xpn_3='ANTONIA')
        pid.date_time_of_birth = '19630512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&SA GERRERIA&12', xad_3='002', xad_4='07', xad_5='07001', xad_6='724', xad_7='H', xad_8='000101')
        pid.pid_13 = '^PRN^PH^^+34^971298745~^WPN^CP^^+34^678298741'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEDI', pl_2='M401', pl_3='M401A', pl_4='HUSE', pl_8='NURS')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '51234^LLABRES^JAUME^BESTARD^^^MD'
        pv1.pv1_8 = '73456^CARBONELL^AINA^COLOM^^^MD'
        pv1.hospital_service = CWE(cwe_1='MED', cwe_2='Medical', cwe_3='HL70069')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = '51234^LLABRES^JAUME^BESTARD^^^MD'
        pv1.patient_type = CWE(cwe_1='IP', cwe_2='Inpatient', cwe_3='HL70004')
        pv1.discharge_disposition = CWE(cwe_1='HUSE')
        pv1.diet_type = CWE(cwe_1='A')
        pv1.account_status = CWE(cwe_1='20260301115500')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='FIOL', xpn_2='FRANCISCA', xpn_3='M')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='CL&SA GERRERIA&12', xad_3='002', xad_4='07', xad_5='07001')
        nk1.nk1_5 = '^PRN^PH^^+34^971298746'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='IBSALUT', cwe_2='SERVEI DE SALUT ILLES BALEARS')
        in1.insurance_company_id = CX(cx_1='IBSALUT')
        in1.insurance_company_name = XON(xon_1='IB-SALUT')
        in1.insurance_company_address = XAD(xad_1='C del Carme 18', xad_3='Palma', xad_5='07003', xad_6='ESP')
        in1.plan_expiration_date = '20250101'
        in1.authorization_information = AUI(aui_1='20261231')

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA', cwe_2='Drug Allergy', cwe_3='HL70127')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='PCN', cwe_2='Penicilina', cwe_3='HL70127')
        al1.allergy_severity_code = CWE(cwe_1='SV', cwe_2='Severe', cwe_3='HL70128')
        al1.allergy_reaction_code = 'Anafilaxia'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1, in1, al1]

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
    """ Based on live/es/es-cerner.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNERPM')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='BDAC')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20260310091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'CERN00102'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260310091500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40011345678', cx_4='001'), CX(cx_1='78234561Z', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='PONS', xpn_2='CATALINA', xpn_3='BEATRIU')
        pid.date_time_of_birth = '19850910'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV&JAUME III&25', xad_2='4t 2a', xad_3='002', xad_4='07', xad_5='07012', xad_6='724', xad_7='H', xad_8='000101')
        pid.pid_13 = '^PRN^PH^^+34^971412389~^WPN^CP^^+34^634789012~^NET^Internet^cpons@gmail.com'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CEXT', pl_2='CONS15', pl_3='01', pl_4='HUSE', pl_8='NURS')
        pv1.pv1_7 = '18765^RIERA^MARGALIDA^FONT^^^MD'
        pv1.hospital_service = CWE(cwe_1='DER', cwe_2='Dermatology', cwe_3='HL70069')
        pv1.patient_type = CWE(cwe_1='CEX20260310', cwe_4='HUSE')
        pv1.prior_temporary_location = PL(pl_1='20260310091000')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/es/es-cerner.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNERPM')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='BDAC')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20260302140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'CERN00103'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260302140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40009823456', cx_4='001'), CX(cx_1='43567891X', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='FIOL', xpn_2='MARGALIDA', xpn_3='ANTONIA')
        pid.date_time_of_birth = '19630512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&SA GERRERIA&12', xad_3='002', xad_4='07', xad_5='07001', xad_6='724', xad_7='H', xad_8='000101')
        pid.pid_13 = '^PRN^PH^^+34^971298745'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCI', pl_2='BOX03', pl_3='01', pl_4='HUSE', pl_8='NURS')
        pv1.pv1_7 = '51234^LLABRES^JAUME^BESTARD^^^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.preadmit_test_indicator = CWE(cwe_1='MEDI', cwe_2='M401', cwe_3='M401A', cwe_4='HUSE')
        pv1.pv1_20 = 'EP101^^^HUSE'
        pv1.discharge_date_time = '20260301115500'

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
    """ Based on live/es/es-cerner.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNERPM')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='BDAC')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20260310120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'CERN00104'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260310120000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40009823456', cx_4='001'), CX(cx_1='43567891X', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='FIOL', xpn_2='MARGALIDA', xpn_3='ANTONIA')
        pid.date_time_of_birth = '19630512'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCI', pl_2='BOX03', pl_3='01', pl_4='HUSE')
        pv1.pv1_7 = '51234^LLABRES^JAUME^BESTARD^^^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.visit_number = CX(cx_1='EP101', cx_4='HUSE')
        pv1.admit_date_time = '20260301115500'
        pv1.discharge_date_time = '20260310120000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Neumonia, no especificada', cwe_3='I10')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/es/es-cerner.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNERPM')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='BDAC')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20260315100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'CERN00105'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260315100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40011345678', cx_4='001'), CX(cx_1='78234561Z', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='PONS', xpn_2='CATALINA', xpn_3='BEATRIU')
        pid.date_time_of_birth = '19850910'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(
            xad_1='CL&ARXIDUC LLUIS SALVADOR&88',
            xad_2='2n A',
            xad_3='002',
            xad_4='07',
            xad_5='07004',
            xad_6='724',
            xad_7='H',
            xad_8='000101',
        )
        pid.pid_13 = '^PRN^PH^^+34^971523890~^WPN^CP^^+34^645890123~^NET^Internet^cpons.nova@gmail.com'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CEXT', pl_2='CONS15', pl_3='01', pl_4='HUSE')
        pv1.pv1_7 = '18765^RIERA^MARGALIDA^FONT^^^MD'
        pv1.hospital_service = CWE(cwe_1='DER')
        pv1.visit_number = CX(cx_1='CEX20260310', cx_4='HUSE')

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
    """ Based on live/es/es-cerner.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNERPM')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='CERNLAB')
        msh.receiving_facility = HD(hd_1='HUSE')
        msh.date_time_of_message = '20260301130000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CERN00106'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40009823456', cx_4='001'), CX(cx_1='43567891X', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='FIOL', xpn_2='MARGALIDA', xpn_3='ANTONIA')
        pid.date_time_of_birth = '19630512'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEDI', pl_2='M401', pl_3='M401A', pl_4='HUSE')
        pv1.pv1_7 = '51234^LLABRES^JAUME^BESTARD^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD20260401', ei_2='CERNERPM')
        orc.placer_order_group_number = EI(ei_1='GRP101', ei_2='CERNERPM')
        orc.date_time_of_order_event = '20260301130000'
        orc.orc_12 = '51234^LLABRES^JAUME^BESTARD^^^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260401', ei_2='CERNERPM')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Hemograma completo con diferencial', cwe_3='LN')
        obr.observation_date_time = '20260301130000'
        obr.obr_16 = '51234^LLABRES^JAUME^BESTARD^^^MD'
        obr.obr_27 = '^STAT'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Neumonia, no especificada', cwe_3='I10')

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
        nte.comment = 'Ingreso urgencias, sospecha neumonia bilateral, control hemograma urgente'

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
    """ Based on live/es/es-cerner.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNLAB')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='CERNERPM')
        msh.receiving_facility = HD(hd_1='HUSE')
        msh.date_time_of_message = '20260301160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CERN00107'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40009823456', cx_4='001'), CX(cx_1='43567891X', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='FIOL', xpn_2='MARGALIDA', xpn_3='ANTONIA')
        pid.date_time_of_birth = '19630512'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEDI', pl_2='M401', pl_3='M401A', pl_4='HUSE')

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
        orc.placer_order_number = EI(ei_1='LABR00223', ei_2='CERNLAB')
        orc.filler_order_number = EI(ei_1='ORD20260401', ei_2='CERNERPM')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LABR00223', ei_2='CERNLAB')
        obr.filler_order_number = EI(ei_1='ORD20260401', ei_2='CERNERPM')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Hemograma completo con diferencial', cwe_3='LN')
        obr.observation_date_time = '20260301140000'
        obr.obr_14 = '51234^LLABRES^JAUME^BESTARD^^^MD'
        obr.filler_field_1 = '20260301155000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobina', cwe_3='LN')
        obx.obx_5 = '13.5'
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
        obx_2.obx_5 = '40.2'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '38.0-50.0'
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
        obx_3.obx_5 = '4.65'
        obx_3.units = CWE(cwe_1='x10E6/uL')
        obx_3.reference_range = '4.50-5.50'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='787-2', cwe_2='VCM', cwe_3='LN')
        obx_4.obx_5 = '86.5'
        obx_4.units = CWE(cwe_1='fL')
        obx_4.reference_range = '80.0-100.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocitos', cwe_3='LN')
        obx_5.obx_5 = '14200'
        obx_5.units = CWE(cwe_1='/uL')
        obx_5.reference_range = '4000-11000'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='751-8', cwe_2='Neutrofilos', cwe_3='LN')
        obx_6.obx_5 = '82.1'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '40.0-70.0'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='731-0', cwe_2='Linfocitos', cwe_3='LN')
        obx_7.obx_5 = '10.3'
        obx_7.units = CWE(cwe_1='%')
        obx_7.reference_range = '20.0-40.0'
        obx_7.interpretation_codes = CWE(cwe_1='L')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='26515-7', cwe_2='Plaquetas', cwe_3='LN')
        obx_8.obx_5 = '198000'
        obx_8.units = CWE(cwe_1='/uL')
        obx_8.reference_range = '150000-400000'
        obx_8.interpretation_codes = CWE(cwe_1='N')
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='4537-7', cwe_2='PCR', cwe_3='LN')
        obx_9.obx_5 = '125.4'
        obx_9.units = CWE(cwe_1='mg/L')
        obx_9.reference_range = '0.0-5.0'
        obx_9.interpretation_codes = CWE(cwe_1='H')
        obx_9.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

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
        order_observation.observation_8 = observation_8
        order_observation.observation_9 = observation_9

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
    """ Based on live/es/es-cerner.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNERPM')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='BDAC')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20260401090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'CERN00108'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='CITA00556', ei_2='CERNERPM')
        sch.filler_appointment_id = EI(ei_1='CITA00556', ei_2='BDAC')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='CCEE', cwe_2='Consulta Externa', cwe_3='LOCAL')
        sch.sch_9 = '20'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^20^202604150930^202604150950'
        sch.sch_16 = '18765^RIERA^MARGALIDA^FONT^^^MD'
        sch.filler_contact_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_5='+34', xtn_6='971175600')
        sch.filler_contact_address = XAD(xad_1='CEXT', xad_2='HUSE')
        sch.entered_by_person = XCN(xcn_1='Reservada')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40011345678', cx_4='001'), CX(cx_1='78234561Z', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='PONS', xpn_2='CATALINA', xpn_3='BEATRIU')
        pid.date_time_of_birth = '19850910'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CEXT', pl_2='CONS15', pl_3='01', pl_4='HUSE')
        pv1.pv1_7 = '18765^RIERA^MARGALIDA^FONT^^^MD'

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
        ais.universal_service_identifier = CWE(cwe_1='CCEE_DERM', cwe_2='Consulta Dermatologia', cwe_3='LOCAL')
        ais.start_date_time_offset_units = CNE(cne_1='202604150930')
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
        aip.aip_3 = '18765^RIERA^MARGALIDA^FONT^^^MD'
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
        ail.location_resource_id = PL(pl_1='CEXT', pl_2='CONS15', pl_3='01', pl_4='HUSE')
        ail.location_group = CWE(cwe_1='202604150930')
        ail.start_date_time = '0'
        ail.start_date_time_offset = 'MIN'
        ail.start_date_time_offset_units = CNE(cne_1='20')
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
    """ Based on live/es/es-cerner.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='POWERCHART')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='HUSE')
        msh.date_time_of_message = '20260301133000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CERN00109'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40009823456', cx_4='001'), CX(cx_1='43567891X', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='FIOL', xpn_2='MARGALIDA', xpn_3='ANTONIA')
        pid.date_time_of_birth = '19630512'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEDI', pl_2='M401', pl_3='M401A', pl_4='HUSE')
        pv1.pv1_7 = '51234^LLABRES^JAUME^BESTARD^^^MD'

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
        orc.placer_order_number = EI(ei_1='RAD20260401', ei_2='POWERCHART')
        orc.placer_order_group_number = EI(ei_1='GRPRAD101', ei_2='POWERCHART')
        orc.date_time_of_order_event = '20260301133000'
        orc.orc_12 = '51234^LLABRES^JAUME^BESTARD^^^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20260401', ei_2='POWERCHART')
        obr.universal_service_identifier = CWE(cwe_1='71046-1', cwe_2='Radiografia torax PA y lateral', cwe_3='LN')
        obr.observation_date_time = '20260301133000'
        obr.obr_16 = '51234^LLABRES^JAUME^BESTARD^^^MD'
        obr.obr_27 = '^STAT'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Neumonia, no especificada', cwe_3='I10')

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
        nte.comment = 'Ingreso urgencias con fiebre y disnea, control Rx torax urgente'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/es/es-cerner.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='POWERCHART')
        msh.receiving_facility = HD(hd_1='HUSE')
        msh.date_time_of_message = '20260301160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CERN00110'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40009823456', cx_4='001'), CX(cx_1='43567891X', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='FIOL', xpn_2='MARGALIDA', xpn_3='ANTONIA')
        pid.date_time_of_birth = '19630512'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEDI', pl_2='M401', pl_3='M401A', pl_4='HUSE')

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
        orc.placer_order_number = EI(ei_1='RADR00556', ei_2='RIS')
        orc.filler_order_number = EI(ei_1='RAD20260401', ei_2='POWERCHART')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RADR00556', ei_2='RIS')
        obr.filler_order_number = EI(ei_1='RAD20260401', ei_2='POWERCHART')
        obr.universal_service_identifier = CWE(cwe_1='71046-1', cwe_2='Radiografia torax PA y lateral', cwe_3='LN')
        obr.observation_date_time = '20260301140000'
        obr.obr_14 = '51234^LLABRES^JAUME^BESTARD^^^MD'
        obr.filler_field_1 = '20260301155500'
        obr.results_rpt_status_chng_date_time = 'RAD'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='59776-5', cwe_2='Hallazgos', cwe_3='LN')
        obx.obx_5 = (
            'Infiltrados bilaterales en campos medios e inferiores de predominio parenquimatoso, compatible con neumonia bilateral de probable etiologia '
            'bacteriana. Silueta cardiaca normal. No derrame pleural. Recomendable control evolutivo.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='19005-8', cwe_2='Impresion diagnostica', cwe_3='LN')
        obx_2.obx_5 = 'Neumonia bilateral'
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
    """ Based on live/es/es-cerner.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='POWERCHART')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='BDAC')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20260310150000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'CERN00111'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260310150000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40009823456', cx_4='001'), CX(cx_1='43567891X', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='FIOL', xpn_2='MARGALIDA', xpn_3='ANTONIA')
        pid.date_time_of_birth = '19630512'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCI', pl_2='BOX03', pl_3='01', pl_4='HUSE')
        pv1.pv1_7 = '51234^LLABRES^JAUME^BESTARD^^^MD'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Informe de Alta', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Text^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260310143000')
        txa.txa_10 = '51234^LLABRES^JAUME^BESTARD^^^MD'
        txa.placer_order_number = EI(ei_1='DOC12445')
        txa.unique_document_file_name = 'AU^Authenticated^HL70271'
        txa.document_confidentiality_status = '20260310150000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='60591-5', cwe_2='SUMMARY', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjcKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA1OTUgODQyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA5OCA+PgpzdHJlYW0KQlQgL0YxIDE2IFRmIDcyIDc2MCBUZCAoSW5mb3JtZSBkZSBBbHRhIC0g'
            'SFVTRSBTb24gRXNwYXNlcykgVGogMCAtMjAgVGQgKFBhY2llbnRlOiBCQVJDRUxPIFRPTkkgTUlRVUVMKSBUaiBFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0Zv'
            'bnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAw'
            'MDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAzMTQgMDAwMDAgbiAKMDAwMDAwMDQ2MiAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYgL1Jvb3QgMSAwIFIg'
            'Pj4Kc3RhcnR4cmVmCjU1MAolJUVPRgo='
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
    """ Based on live/es/es-cerner.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SURGINET')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='CERNERPM')
        msh.receiving_facility = HD(hd_1='HUSE')
        msh.date_time_of_message = '20260305080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CERN00112'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40013567890', cx_4='001'), CX(cx_1='98765432W', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='BARCELO', xpn_2='TONI', xpn_3='MIQUEL')
        pid.date_time_of_birth = '19580917'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CIR', pl_2='HAB503', pl_3='C1', pl_4='HUSE')
        pv1.pv1_7 = '62345^MESQUIDA^NEUS^CRESPI^^^MD'
        pv1.hospital_service = CWE(cwe_1='CIR')
        pv1.visit_number = CX(cx_1='EP102', cx_4='HUSE')
        pv1.admit_date_time = '20260303100000'

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
        orc.placer_order_number = EI(ei_1='SURG20260405', ei_2='SURGINET')
        orc.placer_order_group_number = EI(ei_1='GRPSURG101', ei_2='SURGINET')
        orc.date_time_of_order_event = '20260305080000'
        orc.orc_12 = '62345^MESQUIDA^NEUS^CRESPI^^^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SURG20260405', ei_2='SURGINET')
        obr.universal_service_identifier = CWE(cwe_1='47562', cwe_2='Colecistectomia laparoscopica', cwe_3='CPT')
        obr.observation_date_time = '20260305080000'
        obr.obr_16 = '62345^MESQUIDA^NEUS^CRESPI^^^MD'
        obr.obr_27 = '^ROUTINE'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.1', cwe_2='Colelitiasis con colecistitis cronica', cwe_3='I10')

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
        nte.comment = 'Colecistectomia laparoscopica programada, paciente estable'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/es/es-cerner.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNERPM')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='BDAC')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20260401140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'CERN00113'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260401140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40009823456', cx_4='001'), CX(cx_1='43567891X', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='FIOL', xpn_2='MARGALIDA', xpn_3='ANTONIA')
        pid.date_time_of_birth = '19630512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&SA GERRERIA&12', xad_3='002', xad_4='07', xad_5='07001', xad_6='724', xad_7='H', xad_8='000101')
        pid.pid_13 = '^PRN^PH^^+34^971298745'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = [CX(cx_1='40015432109', cx_4='001'), CX(cx_1='40015432109', cx_4='003')]

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
    """ Based on live/es/es-cerner.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNLAB')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='CERNERPM')
        msh.receiving_facility = HD(hd_1='HUSE')
        msh.date_time_of_message = '20260305120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CERN00114'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40009823456', cx_4='001'), CX(cx_1='43567891X', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='FIOL', xpn_2='MARGALIDA', xpn_3='ANTONIA')
        pid.date_time_of_birth = '19630512'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCI', pl_2='BOX03', pl_3='01', pl_4='HUSE')

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
        orc.placer_order_number = EI(ei_1='MICR00889', ei_2='CERNLAB')
        orc.filler_order_number = EI(ei_1='ORD20260402', ei_2='CERNERPM')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MICR00889', ei_2='CERNLAB')
        obr.filler_order_number = EI(ei_1='ORD20260402', ei_2='CERNERPM')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Hemocultivo', cwe_3='LN')
        obr.observation_date_time = '20260302100000'
        obr.obr_14 = '51234^LLABRES^JAUME^BESTARD^^^MD'
        obr.filler_field_1 = '20260305115000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bacterias identificadas', cwe_3='LN')
        obx.obx_5 = 'Streptococcus pneumoniae'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Sensibilidad antibiotica', cwe_3='LN')
        obx_2.obx_5 = 'Penicilina: R / Amoxicilina-Clavulanico: S / Ceftriaxona: S / Levofloxacino: S / Eritromicina: I'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='35659-2', cwe_2='CMI Penicilina', cwe_3='LN')
        obx_3.obx_5 = '4.0'
        obx_3.units = CWE(cwe_1='ug/mL')
        obx_3.reference_range = '<=0.06'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='35660-0', cwe_2='CMI Ceftriaxona', cwe_3='LN')
        obx_4.obx_5 = '0.5'
        obx_4.units = CWE(cwe_1='ug/mL')
        obx_4.reference_range = '<=1.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/es/es-cerner.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNERPM')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='FACTURACION')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20260310160000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'CERN00115'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20260310160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40009823456', cx_4='001'), CX(cx_1='43567891X', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='FIOL', xpn_2='MARGALIDA', xpn_3='ANTONIA')
        pid.date_time_of_birth = '19630512'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCI', pl_2='BOX03', pl_3='01', pl_4='HUSE')
        pv1.pv1_7 = '51234^LLABRES^JAUME^BESTARD^^^MD'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.visit_number = CX(cx_1='EP101', cx_4='HUSE')
        pv1.admit_date_time = '20260301115500'
        pv1.discharge_date_time = '20260310120000'

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_id = CX(cx_1='20260310')
        ft1.ft1_3 = '20260301~20260310'
        ft1.transaction_date = DR(dr_1='CG')
        ft1.transaction_posting_date = '71046-1^Radiografia torax PA y lateral^LN'
        ft1.transaction_code = CWE(cwe_1='1')
        ft1.transaction_quantity = '51234^LLABRES^JAUME^BESTARD^^^MD'
        ft1.transaction_amount_unit = CP(cp_1='RAD')
        ft1.patient_type = CWE(cwe_1='EP101', cwe_4='HUSE')

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_id = CX(cx_1='20260310')
        ft1_2.ft1_3 = '20260301~20260310'
        ft1_2.transaction_date = DR(dr_1='CG')
        ft1_2.transaction_posting_date = '58410-2^Hemograma completo^LN'
        ft1_2.transaction_code = CWE(cwe_1='2')
        ft1_2.transaction_quantity = '51234^LLABRES^JAUME^BESTARD^^^MD'
        ft1_2.transaction_amount_unit = CP(cp_1='LAB')
        ft1_2.patient_type = CWE(cwe_1='EP101', cwe_4='HUSE')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Neumonia, no especificada', cwe_3='I10')

        # .. build the DIAGNOSIS group ..
        diagnosis = DftP03Diagnosis()
        diagnosis.dg1 = dg1

        # .. assemble the full message ..
        msg = DFT_P03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.visit = visit
        msg.financial = [financial, financial_2]
        msg.diagnosis = diagnosis

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
    """ Based on live/es/es-cerner.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.msh_2 = '^~\\\\&'
        msh.sending_application = HD(hd_1='IBE')
        msh.sending_facility = HD(hd_1='IBE')
        msh.receiving_application = HD(hd_1='CERNERPM')
        msh.receiving_facility = HD(hd_1='HUSE')
        msh.date_time_of_message = '20260302141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'ecgcern20260302141500'
        msh.processing_id = PT(pt_1='P', pt_2='T')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40009823456', cx_4='001'), CX(cx_1='43567891X', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='FIOL', xpn_2='MARGALIDA', xpn_3='ANTONIA')
        pid.date_time_of_birth = '19630512'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEDI', pl_2='M401', pl_3='M401A', pl_4='HUSE')

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
        obr.filler_order_number = EI(ei_1='20260302141200804')
        obr.observation_date_time = '20260302141000'
        obr.filler_field_2 = 'd4e5f6a7-b8c9-0123-4567-890abcdef123'
        obr.results_rpt_status_chng_date_time = '20260302141000'
        obr.result_status = 'F'
        obr.obr_27 = '^^^^20260302141000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='93000', cwe_2='Electrocardiograma interpretacion', cwe_3='CPT')
        obx.obx_5 = 'Ritmo sinusal a 92 lpm. Bloqueo incompleto de rama derecha. Sin alteraciones agudas de la repolarizacion. No signos de isquemia.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Trazado ECG', cwe_3='LOCAL')
        obx_2.obx_5 = (
            '^image^jpeg^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMo'
            'GhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAeADIDASIAAhEBAxEB/8QAGQAAAgMBAAAAAAAAAAAAAAAABQYDBAcI/8QAKxAA'
            'AgEDAwMDBAIDAAAAAAAAAQIDBAURABIhBjFBE1FhByJxgRQjkaGx/8QAGAEAAwEBAAAAAAAAAAAAAAAAAgMEAQX/xAAeEQACAgICAwAAAAAAAAAAAAABAgARAyESMQRBUf/aAAwDAQAC'
            'EQMRAD8AyvpS3Vdzv8FPQ0zVEpOQoI4+STwBrWen/pGamvjWzqCopZohtPpRjexPjnwNVPpZVrQ9RiaopHqITGV2oxXBPHfGtaq+p7XR3AUtTeKCCdvCzoD+M6y3P8Alao//9k='
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/es/es-cerner.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNERPM')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='EMPI')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20260901100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'CERN00117'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20260901100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40014567890', cx_4='001'), CX(cx_1='45678901R', cx_4='014&000'), CX(cx_1='BBBBR456789012345', cx_4='025')]
        pid.patient_name = XPN(xpn_1='SASTRE', xpn_2='LLORENÇ', xpn_3='JOAN')
        pid.date_time_of_birth = '20260830'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&BLANQUERNA&22', xad_3='002', xad_4='07', xad_5='07003', xad_6='724', xad_7='H', xad_8='000101')
        pid.pid_13 = '^PRN^PH^^+34^971745612'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='N')

        # .. assemble the full message ..
        msg = ADT_A05()
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
    """ Based on live/es/es-cerner.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNERPM')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='BDAC')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20260915110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'CERN00118'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260915110000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40013567890', cx_4='001'), CX(cx_1='98765432W', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='BARCELO', xpn_2='TONI', xpn_3='MIQUEL')
        pid.date_time_of_birth = '19580917'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV&GABRIEL ALOMAR&18', xad_2='1r A', xad_3='002', xad_4='07', xad_5='07006', xad_6='724', xad_7='H', xad_8='000101')
        pid.pid_13 = '^PRN^PH^^+34^971856723~^WPN^CP^^+34^656923478'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='N')

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/es/es-cerner.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='POWERCHART')
        msh.sending_facility = HD(hd_1='HUSE')
        msh.receiving_application = HD(hd_1='FARMACIA')
        msh.receiving_facility = HD(hd_1='HUSE')
        msh.date_time_of_message = '20260302090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CERN00119'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='40009823456', cx_4='001'), CX(cx_1='43567891X', cx_4='014&000')]
        pid.patient_name = XPN(xpn_1='FIOL', xpn_2='MARGALIDA', xpn_3='ANTONIA')
        pid.date_time_of_birth = '19630512'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCI', pl_2='BOX03', pl_3='01', pl_4='HUSE')
        pv1.pv1_7 = '51234^LLABRES^JAUME^BESTARD^^^MD'

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
        orc.placer_order_number = EI(ei_1='RX20260402', ei_2='POWERCHART')
        orc.placer_order_group_number = EI(ei_1='GRPRX101', ei_2='POWERCHART')
        orc.date_time_of_order_event = '20260302090000'
        orc.orc_12 = '51234^LLABRES^JAUME^BESTARD^^^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RX20260402', ei_2='POWERCHART')
        obr.universal_service_identifier = CWE(cwe_1='J01DD04', cwe_2='Ceftriaxona', cwe_3='ATC')
        obr.observation_date_time = '20260302090000'
        obr.obr_16 = '51234^LLABRES^JAUME^BESTARD^^^MD'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Ceftriaxona 2g IV cada 24h, neumonia bilateral por S. pneumoniae resistente a penicilina'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.nte = nte

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
    """ Based on live/es/es-cerner.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BDAC')
        msh.sending_facility = HD(hd_1='IBSALUT')
        msh.receiving_application = HD(hd_1='CERNERPM')
        msh.receiving_facility = HD(hd_1='HUSE')
        msh.date_time_of_message = '20260301120001'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'ACK00101'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'CERN00101'
        msa.msa_3 = 'Mensaje procesado correctamente'

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
