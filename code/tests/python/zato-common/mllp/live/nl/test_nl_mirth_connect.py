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
from zato.hl7v2.v2_9.datatypes import CNE, CP, CQ, CWE, CX, DR, EI, HD, MSG, OG, PL, PPN, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, DftP03Financial, DftP03FinancialProcedure, MdmT02CommonOrder, MdmT02Observation, \
    MdmT02Timing, OrmO01Insurance, OrmO01Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12LocationResource, SiuS12Patient, \
    SiuS12PersonnelResource, SiuS12Resources, VxuV04Observation, VxuV04Order
from zato.hl7v2.v2_9.messages import ADT_A01, DFT_P03, MDM_T02, ORM_O01, ORU_R01, SIU_S12, VXU_V04
from zato.hl7v2.v2_9.segments import AIL, AIP, DG1, EVN, FT1, GT1, IN1, MSH, NK1, NTE, OBR, OBX, ORC, PD1, PID, PR1, PV1, RGS, RXA, RXR, SCH, TQ1, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('nl', 'nl-mirth-connect.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/nl/nl-mirth-connect.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ADT1')
        msh.sending_facility = HD(hd_1='ERASMUS MC')
        msh.receiving_application = HD(hd_1='GHH LAB, INC.')
        msh.receiving_facility = HD(hd_1='ERASMUS MC')
        msh.date_time_of_message = '198808181126'
        msh.security = 'SECURITY'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8')
        msh.msh_14 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '200708181123'
        evn.evn_4 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='PATID1234', cx_2='5', cx_3='M11', cx_4='ADT1', cx_5='MR', cx_6='ERASMUS MC'),
            CX(cx_1='287456912', cx_4='NLMINBIZA', cx_5='NNNLD'),
        ]
        pid.patient_name = XPN(xpn_1='van Dijk', xpn_2='Adriaan', xpn_3='J', xpn_4='III')
        pid.date_time_of_birth = '19610615'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='C')
        pid.patient_address = XAD(xad_1='Westersingel 42', xad_3='Rotterdam', xad_4='ZH', xad_5='3015BA')
        pid.pid_12 = 'GL'
        pid.pid_13 = '+31 10-4567890'
        pid.pid_14 = '+31 10-4567891'
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='PATID12345001', cx_2='2', cx_3='M10', cx_4='ADT1', cx_5='AN', cx_6='A')
        pid.pid_19 = '287456912'
        pid.pid_20 = '12345678^ZH'
        pid.pid_21 = ''

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='van Dijk', xpn_2='Cornelia', xpn_3='M')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='SPOUSE')
        nk1.contact_role = CWE(cwe_1='NK', cwe_2='NEXT OF KIN')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='2000', pl_2='2012', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='004777', xcn_2='Brouwer', xcn_3='Theodora', xcn_4='A')
        pv1.hospital_service = CWE(cwe_1='SUR')
        pv1.admit_source = CWE(cwe_1='ADM')
        pv1.ambulatory_status = CWE(cwe_1='A0')
        pv1.pv1_16 = ''

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1

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
    """ Based on live/nl/nl-mirth-connect.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIMHOSP')
        msh.sending_facility = HD(hd_1='SFAC')
        msh.receiving_application = HD(hd_1='RAPP')
        msh.receiving_facility = HD(hd_1='RFAC')
        msh.date_time_of_message = '20200508130643'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = '5'
        msh.processing_id = PT(pt_1='T')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.country_code = '44'
        msh.character_set = 'ASCII'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20200508130643'
        evn.operator_id = XCN(xcn_1='C006', xcn_2='Wolters', xcn_3='Femke', xcn_6='Dr', xcn_9='DRNBR', xcn_10='PRSNL', xcn_13='ORGDR')
        evn.evn_6 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '2590157853^^^SIMULATOR MRN^MRN'
        pid.patient_identifier_list = [CX(cx_1='2590157853', cx_4='SIMULATOR MRN', cx_5='MRN'), CX(cx_1='2478684691', cx_4='NHSNBR', cx_5='NHSNMBR')]
        pid.pid_5 = 'de Vries^Saskia^M^^^Miss^^CURRENT'
        pid.date_time_of_birth = '19890118000000'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Prinsengracht 263', xad_3='Amsterdam', xad_5='1016GV', xad_6='NLD', xad_7='HOME')
        pid.pid_13 = '020-5368 1665^HOME'
        pid.ethnic_group = CWE(cwe_1='R', cwe_2='Other - Chinese', cwe_5='')
        pid.pid_32 = ''

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'FAMILY PRACTICE^^12345'
        pd1.pd1_4 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(
            pl_1='RenalWard',
            pl_2='MainRoom',
            pl_3='Bed 1',
            pl_4='Simulated Hospital',
            pl_6='BED',
            pl_7='Main Building',
            pl_8='5',
        )
        pv1.admission_type = CWE(cwe_1='28b')
        pv1.attending_doctor = XCN(xcn_1='C006', xcn_2='Wolters', xcn_3='Femke', xcn_6='Dr', xcn_9='DRNBR', xcn_10='PRSNL', xcn_13='ORGDR')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.visit_number = CX(cx_1='6145914547062969032', cx_5='visitid')
        pv1.account_status = CWE(cwe_1='ARRIVED')
        pv1.admit_date_time = '20200508130643'
        pv1.pv1_46 = ''

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
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
    """ Based on live/nl/nl-mirth-connect.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SOURCEEHR')
        msh.sending_facility = HD(hd_1='WA')
        msh.receiving_application = HD(hd_1='MIRTHDST')
        msh.receiving_facility = HD(hd_1='WA')
        msh.date_time_of_message = '201611111111'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = 'MSGID10001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.msh_13 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '201611111111'
        evn.evn_4 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '100001^^^1^MRN1'
        pid.patient_identifier_list = CX(cx_1='900001')
        pid.pid_5 = 'Jansen^Willem^^^^'
        pid.date_time_of_birth = '19601111'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='WH')
        pid.patient_address = XAD(xad_1='Kerkstraat 15', xad_3='Utrecht', xad_4='UT', xad_5='3512AB', xad_6='NLD')
        pid.pid_13 = '(030)555-2309'
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='NON')
        pid.patient_account_number = CX(cx_1='384921756')
        pid.pid_19 = ''

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Jansen', xpn_2='Johanna', xpn_3='')
        nk1.relationship = CWE(cwe_1='WIFE')
        nk1.nk1_5 = '(030)555-5555'
        nk1.end_date = 'NK^NEXT OF KIN'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='1001', pl_2='2002', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='123456', xcn_2='Meijer', xcn_3='Hendrik', xcn_4='T', xcn_6='DR')
        pv1.admit_source = CWE(cwe_1='ADM')
        pv1.ambulatory_status = CWE(cwe_1='A0')
        pv1.pv1_16 = ''

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
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
    """ Based on live/nl/nl-mirth-connect.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WCDataSend')
        msh.sending_facility = HD(hd_1='MIE')
        msh.receiving_application = HD(hd_1='wc_hl7d')
        msh.receiving_facility = HD(hd_1='recv_facil')
        msh.date_time_of_message = '20210701123459'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'DSD1625157299701062'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.msh_25 = ''

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20210701123459'
        evn.evn_4 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '1059319'
        pid.patient_identifier_list = [
            CX(cx_1='1059319', cx_4='MR&1.2.840.114398.1.90.1&ISO', cx_5='MR', cx_6='1.2.840.114398.1.90.1&MR&ISO'),
            CX(cx_1='523718649', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Dekker', xpn_2='Anneke', xpn_4='')
        pid.date_time_of_birth = '19640423000000'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Singel 105', xad_3='Amsterdam', xad_4='NH', xad_5='1012AB', xad_6='NL')
        pid.pid_13 = '+31 20-5557091^PRN^PH~+31 6-12345678^PRN^CP'
        pid.marital_status = CWE(cwe_1='W')
        pid.pid_19 = '523718649'
        pid.pid_39 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.assigned_patient_location = PL(pl_4='MIE')
        pv1.pv1_7 = '15104^Visser^Geert^^^^dr.'
        pv1.referring_doctor = XCN(xcn_1='89', xcn_2='Timmerman', xcn_3='Jacobus')
        pv1.pv1_9 = '123^Bakker^Pieter^^^^dr.'
        pv1.pv1_52 = ''

        # .. build GT1 ..
        gt1 = GT1()
        gt1.set_id_gt1 = '1'
        gt1.guarantor_name = XPN(xpn_1='DEKKER', xpn_2='ANNEKE')
        gt1.guarantor_address = XAD(xad_1='SINGEL 105', xad_3='AMSTERDAM', xad_4='NH', xad_5='1012AB')
        gt1.gt1_6 = '+31 20-5557091'
        gt1.guarantor_date_time_of_birth = '19640423000000'
        gt1.guarantor_administrative_sex = CWE(cwe_1='F')
        gt1.gt1_55 = ''

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='5273')
        in1.insurance_company_name = XON(xon_1='ZILVEREN KRUIS')
        in1.insurance_company_address = XAD(xad_1='Postbus 444', xad_3='Leiden', xad_4='ZH', xad_5='2300AK')
        in1.group_number = '100000291006'
        in1.plan_type = CWE(cwe_1='ZILVEREN KRUIS')
        in1.name_of_insured = XPN(xpn_1='Dekker', xpn_2='Anneke')
        in1.insureds_relationship_to_patient = CWE(cwe_1='Self')
        in1.insureds_date_of_birth = '19640423000000'
        in1.insureds_address = XAD(xad_1='Singel 105', xad_3='Amsterdam', xad_4='NH', xad_5='1012AB')
        in1.policy_number = '10122060000'
        in1.insureds_administrative_sex = CWE(cwe_1='F')
        in1.in1_49 = ''

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.gt1 = gt1
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
    """ Based on live/nl/nl-mirth-connect.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBCHART')
        msh.sending_facility = HD(hd_1='OLVG')
        msh.receiving_application = HD(hd_1='RECEIVING_APPLICATION')
        msh.receiving_facility = HD(hd_1='RECEIVING_FACILITY')
        msh.date_time_of_message = '20210701123459'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'DSD1625157299704299'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.msh_25 = ''

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20210701123459'
        evn.evn_4 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '1025209'
        pid.patient_identifier_list = [
            CX(cx_1='1025209', cx_4='MR&1.2.840.114398.1.90.1&ISO', cx_5='MR', cx_6='1.2.840.114398.1.90.1&MR&ISO'),
            CX(cx_1='841672935', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Mulder', xpn_2='Bram', xpn_3='Jan')
        pid.date_time_of_birth = '19461001000000'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='White')
        pid.patient_address = XAD(xad_1='Hofweg 12', xad_3='Den Haag', xad_4='ZH', xad_5='2511AA', xad_6='NL')
        pid.pid_13 = '+31 70-5553241^PRN^PH^b.mulder@email.nl~+31 6-98765432^PRN^CP'
        pid.primary_language = CWE(cwe_1='Dutch')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '841672935'
        pid.ethnic_group = CWE(cwe_1='Not Hispanic or Latino')
        pid.pid_39 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.assigned_patient_location = PL(pl_4='OLVG')
        pv1.pv1_7 = '6^van der Linden^Elisabeth^H.^^^dr.'
        pv1.referring_doctor = XCN(xcn_1='269', xcn_2='Hoekstra', xcn_3='Daan', xcn_4='D.')
        pv1.consulting_doctor = XCN(xcn_1='231', xcn_2='Kuipers', xcn_3='Floor')
        pv1.pv1_52 = ''

        # .. build GT1 ..
        gt1 = GT1()
        gt1.set_id_gt1 = '1'
        gt1.guarantor_name = XPN(xpn_1='MULDER', xpn_2='BRAM', xpn_3='JAN')
        gt1.guarantor_address = XAD(xad_1='HOFWEG 12', xad_3='DEN HAAG', xad_4='ZH', xad_5='2511AA')
        gt1.gt1_6 = '+31 70-5553241'
        gt1.guarantor_date_time_of_birth = '19461001000000'
        gt1.guarantor_administrative_sex = CWE(cwe_1='M')
        gt1.gt1_55 = ''

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='4751')
        in1.insurance_company_id = CX(cx_1='14079')
        in1.insurance_company_name = XON(xon_1='VGZ')
        in1.insurance_company_address = XAD(xad_1='Postbus 202', xad_3='Arnhem', xad_4='GE', xad_5='6800AE')
        in1.plan_type = CWE(cwe_1='VGZ')
        in1.name_of_insured = XPN(xpn_1='Mulder', xpn_2='Bram', xpn_3='Jan')
        in1.insureds_relationship_to_patient = CWE(cwe_1='Self')
        in1.insureds_date_of_birth = '19461001000000'
        in1.insureds_address = XAD(xad_1='Hofweg 12', xad_3='Den Haag', xad_4='ZH', xad_5='2511AA')
        in1.policy_number = 'W255837512'
        in1.insureds_administrative_sex = CWE(cwe_1='M')
        in1.in1_49 = ''

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.gt1 = gt1
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
    """ Based on live/nl/nl-mirth-connect.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='sendFac')
        msh.sending_facility = HD(hd_1='SendApp')
        msh.date_time_of_message = '20170822095500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = '64517000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.msh_14 = ''

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='1234567', cx_5='PI'), CX(cx_1='328917456', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Bakker&&Bakker&&', xpn_2='Margaretha', xpn_7='L')
        pid.date_time_of_birth = '19500101'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.pid_11 = ''

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='123')
        obr.filler_order_number = EI(ei_1='20050701015070', ei_2='Labosys')
        obr.observation_date_time = '200507010907'
        obr.relevant_clinical_information = CWE(cwe_1='""')
        obr.obr_16 = '3004^van den Ende'
        obr.filler_field_1 = '200507010907'
        obr.results_rpt_status_chng_date_time = '201708220955'
        obr.diagnostic_serv_sect_id = 'S'
        obr.result_status = 'F'
        obr.obr_27 = '^^^^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='266', cwe_2='Bezinking', cwe_3='L', cwe_4='BSE')
        obx.obx_5 = '2'
        obx.units = CWE(cwe_1='mm/uur')
        obx.reference_range = '0 - 15'
        obx.interpretation_codes = CWE(cwe_1='""')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='325', cwe_2='Leucocyten', cwe_3='L', cwe_4='LEU')
        obx_2.obx_5 = '6.7'
        obx_2.units = CWE(cwe_1='/nl')
        obx_2.reference_range = '4.0 - 10.0'
        obx_2.interpretation_codes = CWE(cwe_1='""')
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
    """ Based on live/nl/nl-mirth-connect.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.msh_2 = '^_\\&'
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20160324163441+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'ZD200046119'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='van den Berg&van den&Berg', xpn_2='P', xpn_3='J', xpn_7='L')
        pid.date_time_of_birth = '20000101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Leidsestraat 88  bis&Leidsestraat&88', xad_2='bis', xad_3='Eindhoven', xad_5='5611AA', xad_6='NL', xad_7='H')
        pid.pid_13 = '040-2839174'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ZD200046119')
        orc.date_time_of_order_event = '20160324163432+0100'
        orc.orc_10 = '^&&de Groot^A.B.C.'
        orc.orc_12 = '01004567^&&van der Meer^Z.Z.^^^^^^VEKTIS'
        orc.orc_14 = '015-2222222'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD200046119')
        obr.universal_service_identifier = CWE(cwe_1='CIS', cwe_2='Cardiologie', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20160324163432+0100'
        obr.obr_16 = '01004567^&&van der Meer^Z.Z.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='AF', cwe_3='123')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='CARHAR', cwe_2='Hartfalen', cwe_3='ZORGDOMEIN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUHJvZHVjZXIgKP7/AFEAdAAg'
            'ADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzQ0MSswMScwMCcpCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9FeHRHU3RhdGUKL1NBIHRydWUKL1NNIDAu'
            'MDIKL2NhIDEuMAovQ0EgMS4wCi9BSVMgZmFsc2UKL1NNYXNrIC9Ob25lPj4KZW5kb2JqCjQgMCBvYmoKWy9QYXR0ZXJuIC9EZXZpY2VSR0JdCmVuZG9iago4IDAgb2JqClswIC9YWVog'
            'MzUuMDM5OTk5OSAgCjc3My4zNTk5OTkgIDBdCmVuZG9iago5IDAgb2Jq'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='CARCOA001', cwe_2='consult cardioloog', cwe_3='ZORGDOMEIN')
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
    """ Based on live/nl/nl-mirth-connect.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WCDataSend')
        msh.sending_facility = HD(hd_1='omg')
        msh.receiving_application = HD(hd_1='wc_hl7d')
        msh.receiving_facility = HD(hd_1='recv_facil')
        msh.date_time_of_message = '20210709080455'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DSD1625832295118172'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.msh_25 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '5007'
        pid.patient_identifier_list = CX(cx_1='5007', cx_4='MR&1.2.840.114398.1.5110.1&ISO', cx_5='MR', cx_6='MR&1.2.840.114398.1.5110.1&ISO')
        pid.patient_name = XPN(xpn_1='Smit', xpn_2='Thijs', xpn_4='')
        pid.date_time_of_birth = '19830101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Herengracht 200', xad_3='Amsterdam', xad_4='NH', xad_5='1016BS')
        pid.pid_39 = ''

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'CN'
        orc.filler_order_number = EI(ei_1='211820124', ei_2='hexlab-lab')
        orc.orc_12 = '6^van der Linden^Elisabeth^H.^^^dr.'
        orc.enterers_location = PL(pl_5='BIO', pl_10='Biotech Labs')
        orc.order_effective_date_time = '20210701120200'
        orc.orc_31 = ''

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='GROUP320', ei_2='100')
        obr.universal_service_identifier = CWE(cwe_2='H O R M O N E S')
        obr.obr_6 = '20210701120200'
        obr.observation_date_time = '20210701120200'
        obr.obr_13 = (
            'Patient: Smit, Thijs\\X0A\\Ordering Physician: van der Linden, Elisabeth\\X0A\\\\X0A\\----------------------------------------------------------'
            '-------------------------\\X0A\\211820124'
        )
        obr.obr_14 = '20210701180500'
        obr.results_rpt_status_chng_date_time = '20210709080400'
        obr.result_status = 'F'
        obr.procedure_code = CNE(cne_1='1')
        obr.obr_50 = ''

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.observation_identifier = CWE(cwe_1='3676', cwe_2='TESTOSTERONE, TOTAL')
        obx.observation_sub_id = OG(og_1='0')
        obx.obx_5 = '531.17'
        obx.units = CWE(cwe_1='ng/dL')
        obx.reference_range = '220 - 715'
        obx.observation_result_status = 'F'
        obx.effective_date_of_reference_range = '20210701180500'
        obx.user_defined_access_checks = '0'
        obx.date_time_of_the_observation = '20210701120200'
        obx.producers_id = CWE(cwe_1='00004140', cwe_3='MS4R')
        obx.obx_25 = ''

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.filler_order_number = EI(ei_1='GROUP400', ei_2='100')
        obr_2.universal_service_identifier = CWE(cwe_2='INFECTIOUS DISEASE')
        obr_2.obr_6 = '20210701120200'
        obr_2.observation_date_time = '20210701120200'
        obr_2.obr_13 = 'Patient: Smit, Thijs\\X0A\\Ordering Physician: van der Linden, Elisabeth'
        obr_2.obr_14 = '20210701180500'
        obr_2.results_rpt_status_chng_date_time = '20210709080400'
        obr_2.result_status = 'F'
        obr_2.procedure_code = CNE(cne_1='2')
        obr_2.obr_50 = ''

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.observation_identifier = CWE(cwe_1='9472', cwe_2='*ACUTE HEPATITIS PANEL*')
        obx_2.observation_sub_id = OG(og_1='0')
        obx_2.observation_result_status = 'I'
        obx_2.effective_date_of_reference_range = '20210701180500'
        obx_2.user_defined_access_checks = '0'
        obx_2.date_time_of_the_observation = '20210701120200'
        obx_2.producers_id = CWE(cwe_1='HDR80074', cwe_3='MS4R')
        obx_2.obx_25 = ''

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.observation_identifier = CWE(cwe_1='1139', cwe_2='HEP A IgM')
        obx_3.observation_sub_id = OG(og_1='0')
        obx_3.obx_5 = 'NON-REACTIVE'
        obx_3.reference_range = 'NON-REACTI'
        obx_3.observation_result_status = 'F'
        obx_3.effective_date_of_reference_range = '20210701180500'
        obx_3.user_defined_access_checks = '0'
        obx_3.date_time_of_the_observation = '20210701120200'
        obx_3.producers_id = CWE(cwe_1='00001048', cwe_3='MS4R')
        obx_3.obx_25 = ''

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.observation_identifier = CWE(cwe_1='579', cwe_2='HEP B SURF AG')
        obx_4.observation_sub_id = OG(og_1='0')
        obx_4.obx_5 = 'NON-REACTIVE'
        obx_4.reference_range = 'NON-REACTI'
        obx_4.observation_result_status = 'F'
        obx_4.effective_date_of_reference_range = '20210701180500'
        obx_4.user_defined_access_checks = '0'
        obx_4.date_time_of_the_observation = '20210701120200'
        obx_4.producers_id = CWE(cwe_1='00002042', cwe_3='MS4R')
        obx_4.obx_25 = ''

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.observation_identifier = CWE(cwe_1='699', cwe_2='HEP B CORE IGM')
        obx_5.observation_sub_id = OG(og_1='0')
        obx_5.obx_5 = 'NON-REACTIVE'
        obx_5.reference_range = 'NON-REACTI'
        obx_5.observation_result_status = 'F'
        obx_5.effective_date_of_reference_range = '20210701180500'
        obx_5.user_defined_access_checks = '0'
        obx_5.date_time_of_the_observation = '20210701120200'
        obx_5.producers_id = CWE(cwe_1='00001049', cwe_3='MS4R')
        obx_5.obx_25 = ''

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.observation_identifier = CWE(cwe_1='581', cwe_2='ANTI-HCV')
        obx_6.observation_sub_id = OG(og_1='0')
        obx_6.obx_5 = 'NON-REACTIVE'
        obx_6.reference_range = 'NON-REACTI'
        obx_6.observation_result_status = 'F'
        obx_6.effective_date_of_reference_range = '20210701180500'
        obx_6.user_defined_access_checks = '0'
        obx_6.date_time_of_the_observation = '20210701120200'
        obx_6.producers_id = CWE(cwe_1='00002044', cwe_3='MS4R')
        obx_6.obx_25 = ''

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.nte_3 = (
            'This test was performed using the Siemens Advia Centaur immunoassay\\X0A\\method. Values obtained from different assay methods cannot be used\\'
            'X0A\\interchangeably.'
        )
        nte.comment_type = CWE(cwe_1='TC')

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6
        observation_6.nte = nte

        # .. build the ORDER_OBSERVATION group ..
        order_observation_2 = OruR01OrderObservation()
        order_observation_2.obr = obr_2
        order_observation_2.observation = observation_2
        order_observation_2.observation_2 = observation_3
        order_observation_2.observation_3 = observation_4
        order_observation_2.observation_4 = observation_5
        order_observation_2.observation_5 = observation_6

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation
        patient_result.order_observation_2 = order_observation_2

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
    """ Based on live/nl/nl-mirth-connect.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIE')
        msh.sending_facility = HD(hd_1='SHC')
        msh.receiving_application = HD(hd_1='MIE')
        msh.receiving_facility = HD(hd_1='SU')
        msh.date_time_of_message = '20210621214932'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DSD1624337372374298'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.msh_25 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '5007'
        pid.patient_identifier_list = CX(cx_1='5007', cx_4='MR&1.2.840.114398.1.5110.1&ISO', cx_5='MR', cx_6='MR&1.2.840.114398.1.5110.1&ISO')
        pid.patient_name = XPN(xpn_1='Smit', xpn_2='Thijs', xpn_4='')
        pid.date_time_of_birth = '19830101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Herengracht 200', xad_3='Amsterdam', xad_4='NH', xad_5='1016BS')
        pid.pid_39 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.attending_doctor = XCN(xcn_1='40', xcn_2='Kuipers', xcn_3='Daan', xcn_4='I.', xcn_5='dr.')
        pv1.pv1_52 = ''

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
        orc.placer_order_number = EI(ei_1='7913')
        orc.filler_order_number = EI(ei_1='21S-160VI0363')
        orc.order_status = 'CM'
        orc.orc_31 = ''

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='7913')
        obr.filler_order_number = EI(ei_1='21S-160VI0363')
        obr.universal_service_identifier = CWE(cwe_1='LABSARSCOV2', cwe_2='NOVEL CORONAVIRUS 2019 (SARS-COV-2), RT PCR')
        obr.obr_6 = '20210609114100'
        obr.observation_date_time = '20210609114100'
        obr.obr_16 = '40^Kuipers^Daan^I.^dr.'
        obr.filler_field_1 = '0'
        obr.result_status = 'F'
        obr.obr_32 = '40^20210614112732'
        obr.scheduled_date_time = '20210609231214'
        obr.obr_50 = ''

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Patient: Smit, Thijs'
        nte.nte_4 = ''

        # .. build NTE ..
        nte_2 = NTE()
        nte_2.set_id_nte = '2'
        nte_2.comment = 'MR #: 5007'
        nte_2.nte_4 = ''

        # .. build NTE ..
        nte_3 = NTE()
        nte_3.set_id_nte = '3'
        nte_3.comment = 'Ordering Physician: Kuipers, Daan Isaac'
        nte_3.nte_4 = ''

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(
            cwe_1='1230303009',
            cwe_2='SPECIMEN TYPE (SARS-COV-2)',
            cwe_3='MIE',
            cwe_4='7918',
            cwe_5='SPECIMEN TYPE (SARS-COV-2)',
            cwe_6='WEBCHART',
        )
        obx.obx_5 = 'Resp, Upper'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20210609114100'
        obx.producers_id = CWE(cwe_1='1020', cwe_2='Verhoeven, Lotte Radboudumc Department of Pathology Nijmegen, 6525GA')
        obx.responsible_observer = XCN(xcn_1='1020')
        obx.obx_25 = ''

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(
            cwe_1='1230303010',
            cwe_2='SPECIMEN SOURCE (SARS-COV-2)',
            cwe_3='MIE',
            cwe_4='7919',
            cwe_5='SPECIMEN SOURCE (SARS-COV-2)',
            cwe_6='WEBCHART',
        )
        obx_2.obx_5 = 'Mid Turbinate Nasal Swab'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20210609114100'
        obx_2.producers_id = CWE(cwe_1='1020', cwe_2='Verhoeven, Lotte Radboudumc Department of Pathology Nijmegen, 6525GA')
        obx_2.responsible_observer = XCN(xcn_1='1020')
        obx_2.obx_25 = ''

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='1230303011', cwe_2='SARS-COV-2 RNA', cwe_3='MIE', cwe_4='7920', cwe_5='SARS-COV-2 RNA', cwe_6='WEBCHART')
        obx_3.obx_5 = 'Not Detected'
        obx_3.reference_range = 'Not Detected'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20210609114100'
        obx_3.producers_id = CWE(cwe_1='1020', cwe_2='Verhoeven, Lotte Radboudumc Department of Pathology Nijmegen, 6525GA')
        obx_3.responsible_observer = XCN(xcn_1='1020')
        obx_3.obx_25 = ''

        # .. build NTE ..
        nte_4 = NTE()
        nte_4.set_id_nte = '1'
        nte_4.comment = 'Methodology: Nucleic Acid Amplification Test (NAAT): RT-PCR or TMA;(Hologic Panther System)'
        nte_4.nte_4 = ''

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3
        observation_3.nte = nte_4

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.nte = nte
        order_observation.nte_2 = nte_2
        order_observation.nte_3 = nte_3
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
    """ Based on live/nl/nl-mirth-connect.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WCDataSend')
        msh.sending_facility = HD(hd_1='DEV')
        msh.receiving_application = HD(hd_1='wc_hl7d')
        msh.receiving_facility = HD(hd_1='recv_facil')
        msh.date_time_of_message = '20210413152312'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'DSD1618345392293653'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.msh_25 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '10018'
        pid.patient_identifier_list = CX(cx_1='10018', cx_4='MR&1.2.840.114398.1.6629.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Wolters', xpn_2='Floor', xpn_7='L')
        pid.date_time_of_birth = '20210413000000'
        pid.patient_address = XAD(xad_1='Dorpsstraat 22', xad_3='Deventer', xad_4='OV', xad_5='7411HP', xad_6='NL', xad_9='OV')
        pid.pid_13 = '^PRN^PH'
        pid.pid_14 = '^WPN^PH'
        pid.pid_39 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.assigned_patient_location = PL(pl_4='FREELM')
        pv1.alternate_visit_id = CX(cx_6='1.2.840.114398.1.6629')
        pv1.pv1_52 = ''

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.coverage_type = CWE(cwe_1='C')
        in1.in1_49 = ''

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='22')
        orc.order_status = 'Pending'
        orc.orc_7 = '^^^^^0'
        orc.date_time_of_order_event = '20210413152252'
        orc.orc_10 = '89^Medical Informatics Engineering^MIE'
        orc.orc_12 = '8^Hoekstra^Bram^B^^^dr.'
        orc.enterers_location = PL(pl_5='OFFICE', pl_10='Huisartsenpraktijk Hoekstra, Bram B. Hoekstra, dr.')
        orc.orc_17 = 'OFFICE'
        orc.orc_21 = 'Huisartsenpraktijk Hoekstra, Bram B. Hoekstra, dr.'
        orc.orc_22 = 'Stationsstraat 10^Suite 2^Deventer^OV^7411HK^NL'
        orc.orc_23 = '0570-612345'
        orc.orc_24 = 'Stationsstraat 10^Suite 2^Deventer^OV^7411HK'
        orc.orc_31 = ''

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='22')
        obr.universal_service_identifier = CWE(cwe_1='E693', cwe_2='PORPHOBILINOGEN (PBG) URINE - AEL')
        obr.obr_5 = '0'
        obr.obr_6 = '20210413152252'
        obr.observation_date_time = '20210413161900'
        obr.obr_16 = '8^Hoekstra^Bram^B^^^dr.'
        obr.obr_50 = ''

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R05', cwe_2='COUGH', cwe_3='I10')
        dg1.dg1_4 = 'COUGH'
        dg1.dg1_16 = ''

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='C6806', cwe_2='HOURS COLLECTED')
        obx.obx_5 = '0.25'
        obx.obx_25 = ''

        # .. build the OBSERVATION group ..
        observation = OrmO01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='C6804', cwe_2='TOTAL VOLUME')
        obx_2.obx_5 = '4'
        obx_2.obx_25 = ''

        # .. build the OBSERVATION group ..
        observation_2 = OrmO01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1
        order_detail.observation = observation
        order_detail.observation_2 = observation_2

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
    """ Based on live/nl/nl-mirth-connect.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EH')
        msh.sending_facility = HD(hd_1='EH')
        msh.receiving_application = HD(hd_1='COVID LAB')
        msh.receiving_facility = HD(hd_1='COVID LAB')
        msh.date_time_of_message = '20210311091929'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'DSD1615472369786270'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.msh_25 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '101394'
        pid.patient_identifier_list = CX(cx_1='101394', cx_4='MR&1.2.840.114398.1.6391.5&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='de Jong', xpn_2='Geert', xpn_7='L')
        pid.date_time_of_birth = '19820101000000'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Marktplein 7', xad_3='Groningen', xad_4='GR', xad_5='9711CV', xad_6='NL')
        pid.pid_13 = '+31 50-1234567^PRN^PH^g.dejong@email.nl'
        pid.pid_14 = '+31 50-1234568^WPN^PH'
        pid.pid_39 = ''

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.source_of_comment = 'I'
        nte.comment = 'COMMENTS'
        nte.nte_4 = ''

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.coverage_type = CWE(cwe_1='C')
        in1.in1_49 = ''

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.nte = nte
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='75055')
        orc.order_status = 'Pending'
        orc.orc_7 = '^^^^^0'
        orc.date_time_of_order_event = '20210311061912'
        orc.orc_10 = '12137^Visser^Maria'
        orc.orc_12 = '1972697324^Bakker^Lotte^^^^^N^NPI'
        orc.enterers_location = PL(pl_5='GRONINGEN', pl_10='Groningen')
        orc.orc_17 = 'GRONINGEN'
        orc.orc_21 = 'Groningen'
        orc.orc_22 = 'Herestraat 50^^Groningen^GR^9713GZ^NL'
        orc.orc_24 = 'Postbus 997377^^Groningen^GR'
        orc.orc_31 = ''

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='75055')
        obr.universal_service_identifier = CWE(cwe_1='94500-6', cwe_2='SARS coronavirus')
        obr.obr_5 = '0'
        obr.obr_6 = '20210311061912'
        obr.observation_date_time = '20210311061900'
        obr.obr_15 = '^^^covid_anterior_nares_swab'
        obr.obr_16 = '1972697324^Bakker^Lotte^^^^^N^NPI'
        obr.reason_for_study = CWE(cwe_1='COMMENTS')
        obr.obr_50 = ''

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_2='BODY SITE')
        obx.obx_5 = 'COVID_ANTERIOR_NARES_SWAB'
        obx.obx_25 = ''

        # .. build the OBSERVATION group ..
        observation = OrmO01Observation()
        observation.obx = obx

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.observation = observation

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
    """ Based on live/nl/nl-mirth-connect.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MESA_OP')
        msh.sending_facility = HD(hd_1='CATHARINA')
        msh.receiving_application = HD(hd_1='iFW')
        msh.receiving_facility = HD(hd_1='ABC_RADIOLOGY')
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = '101104'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.msh_20 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='20891312', cx_5='EPI')
        pid.pid_5 = 'Brouwer^Pieter^H^^dhr.^'
        pid.date_time_of_birth = '19661201'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='AfrAm')
        pid.patient_address = XAD(xad_1='Vestdijk 50', xad_3='Eindhoven', xad_4='NB', xad_5='5611AZ', xad_6='NL', xad_9='NB')
        pid.pid_12 = 'NB'
        pid.pid_13 = '+31 40-2345678'
        pid.pid_14 = '+31 40-2345679'
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1=' 11480003')
        pid.pid_19 = '471829365'
        pid.pid_23 = '^^^NB^^'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.assigned_patient_location = PL(pl_4='CATHARINA ZIEKENHUIS', pl_9='')
        pv1.prior_patient_location = PL(pl_1=' ')
        pv1.pv1_7 = '1173^Timmerman^Jacobus^A^^^'
        pv1.visit_number = CX(cx_1='610613')
        pv1.visit_indicator = CWE(cwe_1='V')

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
        orc.placer_order_number = EI(ei_1='987654', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='76543', ei_2='EPC')
        orc.order_status = 'Final'
        orc.orc_7 = '^^^20140418170014^^^^'
        orc.date_time_of_order_event = '20140418173314'
        orc.orc_10 = '1148^de Wit^Saskia^^^^'
        orc.orc_12 = '1173^Timmerman^Jacobus^A^^^'
        orc.enterers_location = PL(pl_1='1133', pl_4='222', pl_9='')
        orc.orc_14 = '(040)222-1122'
        orc.orc_16 = ''

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='363463', ei_2='EPC')
        obr.filler_order_number = EI(ei_1='1858', ei_2='EPC')
        obr.universal_service_identifier = CWE(cwe_1='73610', cwe_2='X-RAY ANKLE 3+ VW', cwe_5='X-RAY ANKLE ')
        obr.obr_16 = '1173^Timmerman^Jacobus^A^^^'
        obr.obr_17 = '(040)258-8866'
        obr.result_status = 'Final'
        obr.obr_27 = '^^^20140418170014^^^^'
        obr.obr_32 = '6064^Hendriks^Adriaan^^^^'
        obr.obr_34 = '1148010^1A^EAST^X-RAY^^^'
        obr.obr_35 = '^'
        obr.obr_36 = ''

        # .. build DG1 ..
        dg1 = DG1()
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='S82', cwe_2='ANKLE FRACTURE', cwe_3='I10')
        dg1.dg1_4 = 'ANKLE FRACTURE'
        dg1.dg1_6 = ''

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
    """ Based on live/nl/nl-mirth-connect.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WCDataSend')
        msh.sending_facility = HD(hd_1='handle')
        msh.receiving_application = HD(hd_1='wc_hl7d')
        msh.receiving_facility = HD(hd_1='recv_facil')
        msh.date_time_of_message = '20210423091057'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'DSD1619205057152978'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.msh_25 = ''

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='2588939')
        sch.filler_appointment_id = EI(ei_1='2677255')
        sch.appointment_reason = CWE(cwe_1='ppd 2nd step')
        sch.appointment_type = CWE(cwe_1='NURS', cwe_2='Nurse Encounter')
        sch.sch_9 = '15'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^^202104270815^202104270830'
        sch.filler_status_code = CWE(cwe_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '123456'
        pid.patient_identifier_list = [
            CX(cx_1='123456', cx_4='MR&1.2.840.114398.1.5881.2&ISO', cx_5='MR', cx_6='1.2.840.114398.1.5881.2&MR&ISO'),
            CX(cx_1='963258', cx_4='ECW&1.2.840.114398.1.5881.3&ISO', cx_5='MR', cx_6='1.2.840.114398.1.5881.3&ECW&ISO'),
            CX(cx_1='517263849', cx_5='SS'),
        ]
        pid.pid_4 = '123456^^^MR&1.2.840.114398.1.5881.1&ISO'
        pid.patient_name = XPN(xpn_1='Vermeer', xpn_2='Femke', xpn_3='L')
        pid.date_time_of_birth = '19830711000000'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='Asian')
        pid.patient_address = XAD(xad_1='Oudegracht 30', xad_3='Utrecht', xad_4='UT', xad_5='3511AR', xad_6='NL')
        pid.pid_13 = '+31 30-5550101^PRN^PH^f.vermeer@email.nl~+31 6-55500202^PRN^CP'
        pid.pid_14 = '+31 30-5550303^WPN^PH'
        pid.primary_language = CWE(cwe_1='EN')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '517263849'
        pid.ethnic_group = CWE(cwe_1='Not Hispanic or Latino')
        pid.tribal_citizenship = CWE(cwe_1='NK1')
        pid.pid_40 = '1'
        pid.pid_78 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.assigned_patient_location = PL(pl_4='handle')
        pv1.pv1_52 = ''

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.rgs_3 = ''

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_2='30', pl_9='Amphia Ziekenhuis')
        ail.ail_12 = ''

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.aip_3 = '12029^van Leeuwen^Theodora^V^^^dr.'
        aip.resource_type = CWE(cwe_1='RESOURCE')
        aip.allow_substitution_code = CWE(cwe_1='SUBSTITUTE')
        aip.aip_12 = ''

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.location_resource = location_resource
        resources.personnel_resource = personnel_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/nl/nl-mirth-connect.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WCDataSend')
        msh.sending_facility = HD(hd_1='maui')
        msh.receiving_application = HD(hd_1='wc_hl7d')
        msh.receiving_facility = HD(hd_1='recv_facil')
        msh.date_time_of_message = '20210428235041'
        msh.message_type = MSG(msg_1='SIU', msg_2='S15', msg_3='SIU_S12')
        msh.message_control_id = 'DSD1619689841639741'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.msh_25 = ''

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='2588939')
        sch.filler_appointment_id = EI(ei_1='2677255')
        sch.event_reason = CWE(cwe_1='NOSHOW', cwe_2='NO SHOW')
        sch.appointment_reason = CWE(cwe_1='ppd 2nd step')
        sch.appointment_type = CWE(cwe_1='NURS', cwe_2='Nurse Encounter')
        sch.sch_9 = '15'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^^202104270815^202104270830'
        sch.entered_by_person = XCN(xcn_1='29', xcn_2='Cronjobs')
        sch.filler_status_code = CWE(cwe_1='CANCELED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '123456'
        pid.patient_identifier_list = [
            CX(cx_1='123456', cx_4='MR&1.2.840.114398.1.5881.2&ISO', cx_5='MR', cx_6='1.2.840.114398.1.5881.2&MR&ISO'),
            CX(cx_1='963258', cx_4='ECW&1.2.840.114398.1.5881.3&ISO', cx_5='MR', cx_6='1.2.840.114398.1.5881.3&ECW&ISO'),
            CX(cx_1='517263849', cx_5='SS'),
        ]
        pid.pid_4 = '123456^^^MR&1.2.840.114398.1.5881.1&ISO'
        pid.patient_name = XPN(xpn_1='Vermeer', xpn_2='Femke', xpn_3='L')
        pid.date_time_of_birth = '19830711000000'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='Asian')
        pid.patient_address = XAD(xad_1='Oudegracht 30', xad_3='Utrecht', xad_4='UT', xad_5='3511AR', xad_6='NL')
        pid.pid_13 = '+31 30-5550101^PRN^PH^f.vermeer@email.nl~+31 6-55500202^PRN^CP'
        pid.pid_14 = '+31 30-5550303^WPN^PH'
        pid.primary_language = CWE(cwe_1='EN')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '517263849'
        pid.ethnic_group = CWE(cwe_1='Not Hispanic or Latino')
        pid.tribal_citizenship = CWE(cwe_1='NK1')
        pid.pid_40 = '1'
        pid.pid_78 = ''

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.nk1_39 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.assigned_patient_location = PL(pl_4='maui')
        pv1.pv1_52 = ''

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.rgs_3 = ''

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_2='30', pl_9='Amphia Ziekenhuis')
        ail.ail_12 = ''

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.aip_3 = '12029^van Leeuwen^Theodora^V^^^dr.'
        aip.resource_type = CWE(cwe_1='RESOURCE')
        aip.allow_substitution_code = CWE(cwe_1='SUBSTITUTE')
        aip.aip_12 = ''

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [nk1, pv1, rgs, ail, aip]

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
    """ Based on live/nl/nl-mirth-connect.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WCDataSend')
        msh.receiving_application = HD(hd_1='wc_hl7d')
        msh.receiving_facility = HD(hd_1='recv_facil')
        msh.date_time_of_message = '20210716121708'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'DSD1626452228213830'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.msh_21 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '55555'
        pid.patient_identifier_list = [
            CX(cx_1='55555', cx_4='FWR&1.2.840.114398.1.13.1&ISO', cx_5='MR', cx_6='1.2.840.114398.1.13.1&FWR&ISO'),
            CX(cx_1='55555', cx_4='TSMI&1.2.840.114398.1.77.1&ISO', cx_5='MR', cx_6='1.2.840.114398.1.77.1&TSMI&ISO'),
            CX(cx_1='88888', cx_4='CAMHBOC&1.2.840.114398.1.4.1&ISO', cx_5='MR', cx_6='1.2.840.114398.1.4.1&CAMHBOC&ISO'),
            CX(cx_1='649271835', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Janssen', xpn_2='Lotte', xpn_3='K')
        pid.date_time_of_birth = '19961110000000'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='W')
        pid.patient_address = XAD(xad_1='Nassaulaan 5', xad_2='Apt 705', xad_3='Breda', xad_4='NB', xad_5='4811TC', xad_6='NL')
        pid.pid_13 = '+31 76-5554073^PRN^PH'
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '649271835'
        pid.pid_39 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='OUTPATIENT')
        pv1.assigned_patient_location = PL(pl_1='CAM', pl_9='Amphia Ziekenhuis', pl_10='fwr')
        pv1.hospital_service = CWE(cwe_1='XR')
        pv1.pv1_17 = '11094^Bos^Hendrik^^^^dr.'
        pv1.visit_number = CX(cx_1='10391981')
        pv1.delete_account_indicator = CWE(cwe_1='0')
        pv1.account_status = CWE(cwe_1='1')
        pv1.admit_date_time = '20160502121300'
        pv1.alternate_visit_id = CX(cx_1='341623620160502', cx_6='CPSI')
        pv1.pv1_52 = ''

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='PS')
        txa.document_content_presentation = 'FT'
        txa.activity_date_time = '20160502121300'
        txa.origination_date_time = '20160502142755'
        txa.transcription_date_time = '20160502142755'
        txa.edit_date_time = '20160502142755'
        txa.txa_9 = '11094^Bos^Hendrik^^^^dr.'
        txa.unique_document_number = EI(ei_1='918711', ei_2='Powerscribe')
        txa.document_completion_status = 'LA'
        txa.authentication_person_time_stamp_set = PPN(ppn_1='11094', ppn_2='Bos', ppn_3='Hendrik', ppn_11='1', ppn_15='20160502124809')
        txa.distributed_copies_code_and_name_of_recipients = XCN(xcn_1='9290', xcn_2='BREDA', xcn_3='RADIOLOGY')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='14')
        obx.observation_sub_id = OG(og_1='PS')
        obx.obx_5 = (
            'Amphia Ziekenhuis\\X0A\\Molengracht 21\\X0A\\Breda, NB 4818CK\\X0A\\ORDERING PROVIDER: de Vries, Willem, dr.\\X0A\\\\X0A\\PATIENT NAME: Lotte Ja'
            'nssen\\X0A\\MR: 85459\\X0A\\DOB: Nov 10, 1996\\X0A\\\\X0A\\EXAMINATION: CR THORACIC SPINE 3 VIEW.\\X0A\\DATE OF EXAM: May 02, 2016 12:13:00 PM.'
            '\\X0A\\INDICATION: back pain, nki, hx arthritis\\X0A\\Comparison: Chest x-ray 12/3/2014, 4/27/2015, nuclear medicine bone\\X0A\\scan 4/26/2016.'
            '\\X0A\\NUMBER OF IMAGES: 4\\X0A\\\\X0A\\DISCUSSION: There is diffuse bony demineralization, which limits\\X0A\\evaluation for nondisplaced fract'
            'ures. Within this limitation,\\X0A\\vertebral body heights are grossly preserved, as well as can be seen.\\X0A\\There is multilevel disc space n'
            'arrowing and associated endplate\\X0A\\degenerative changes in the thoracic and visualized upper lumbar\\X0A\\spine. There is mild dextro scolio'
            'tic curvature of the upper and mid\\X0A\\thoracic spine. Small focus of radiotracer activity in the mid\\X0A\\thoracic spine left of midline cou'
            'ld represent chronic changes\\X0A\\associated with the mild dextroscoliotic curvature. Left ureteral\\X0A\\stent is incidentally noted.\\X0A\\\\'
            'X0A\\IMPRESSION: Diffuse bony demineralization, which limits evaluation for\\X0A\\nondisplaced fractures. No significant compression fracture\\X'
            '0A\\identified. Multilevel degenerative changes. See discussion above.\\X0A\\\\X0A\\\\X0A\\Professional Interpretation by BREDA RADIOLOGY\\X0A\\'
            'Electronically signed by: Bos, dr., Hendrik\\X0A\\'
        )
        obx.obx_25 = ''

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'CR THORACIC SPINE 3 VIEW'
        nte.comment_type = CWE(cwe_1='RE')

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx
        observation.nte = nte

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.pid = pid
        msg.pv1 = pv1
        msg.txa = txa
        msg.observation = observation

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
    """ Based on live/nl/nl-mirth-connect.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EH_MDM')
        msh.sending_facility = HD(hd_1='BCC')
        msh.receiving_application = HD(hd_1='POST_MEDIA')
        msh.receiving_facility = HD(hd_1='recv_facil')
        msh.date_time_of_message = '20220613153036'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'DSD1655148636292112'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.msh_25 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '10019'
        pid.patient_identifier_list = [
            CX(cx_1='10019', cx_4='MIE&1.2.840.114398.1.6885.2&ISO', cx_5='MR', cx_6='1.2.840.114398.1.6885.2&MIE&ISO'),
            CX(cx_1='291485736', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='de Groot', xpn_2='Willem', xpn_3='S.')
        pid.date_time_of_birth = '19541130000000'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='White')
        pid.patient_address = XAD(xad_1='Plein 1953 nr 1', xad_3='Tilburg', xad_4='NB', xad_5='5038EK', xad_6='NL')
        pid.pid_13 = '+31 13-4440099^PRN^PH^w.degroot@email.nl~+31 6-30700001^PRN^CP'
        pid.primary_language = CWE(cwe_1='Dutch')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '291485736'
        pid.ethnic_group = CWE(cwe_1='Not Hispanic or Latino')
        pid.pid_39 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='HISTEXAM')
        pv1.assigned_patient_location = PL(pl_1='OFFICE', pl_9='Rijnstate', pl_10='BCC')
        pv1.attending_doctor = XCN(xcn_1='8', xcn_2='Dekker', xcn_3='Cornelia')
        pv1.pv1_9 = '9^Jansen^Pieter^M.^^^dr.'
        pv1.admitting_doctor = XCN(xcn_1='8', xcn_2='Dekker', xcn_3='Cornelia')
        pv1.delete_account_indicator = CWE(cwe_1='0')
        pv1.account_status = CWE(cwe_1='1')
        pv1.admit_date_time = '20100225000000'
        pv1.alternate_visit_id = CX(cx_1='11', cx_6='1.2.840.114398.1.6885')
        pv1.pv1_52 = ''

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='REGFORM')
        txa.document_content_presentation = 'AP'
        txa.activity_date_time = '20100312000000'
        txa.origination_date_time = '20100323202954'
        txa.transcription_date_time = '20100323202954'
        txa.edit_date_time = '20100324101735'
        txa.originator_code_name = XCN(xcn_1='8', xcn_2='Dekker', xcn_3='Cornelia')
        txa.transcriptionist_code_name = XCN(xcn_1='2', xcn_2='Engineering', xcn_3='Medical', xcn_4='Informatics')
        txa.unique_document_number = EI(ei_1='298', ei_2='1.2.840.114398.1.6885')
        txa.document_completion_status = 'DO'
        txa.txa_23 = ''

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='17')
        obx.observation_sub_id = OG(og_1='REGFORM')
        obx.obx_5 = (
            '^^^Base64^'
            'JVBERi0xLjEgDSXi48/TDQoxIDAgb2JqDTw8IA0vVHlwZSAvQ2F0YWxvZyANL1BhZ2VzIDMgMCBSIA0+Pg1lbmRvYmoNMiAwIG9iag08PCANL0NyZWF0aW9uRGF0ZSAoRDoyMDIyMDYx'
            'MzE1MzAzOSkNL01vZERhdGUgKEQ6MjAyMjA2MTMxNTMwMzkpDS9Qcm9kdWNlciAoTUlFIGltZ2ZpbHRlciB2MS43LjApDS9DcmVhdG9yIChNSUUgaW1nZmlsdGVyIHYxLjcuMCkNPj4g'
            'DWVuZG9iag0zIDAgb2JqDTw8IA0vVHlwZSAvUGFnZXMgDS9LaWRzIFsgNCAwIFIgXSANL0NvdW50IDEgDT4+IA1lbmRvYmoNNCAwIG9iag08PA0vVHlwZSAvUGFnZSANL1BhcmVudCAz'
            'IDAgUiANL01lZGlhQm94IFswLjAwMDAgMC4wMDAwIDYxMi4wMDAwIDc5Mi4wMDAwXSANL0NvbnRlbnRzIDUgMCBSIA0vUmVzb3VyY2VzIDw8IA0vWE9iamVjdCA8PA0vSW0xIDcgMCBS'
            'ID4+DS9Qcm9jU2V0IFsgL0ltYWdlQiBdDT4+DT4+DWVuZG9iag01IDAgb2JqDTw8IA0vTGVuZ3RoIDYgMCBSIA0gPj4Nc3RyZWFtDQpxICA2MTIuMDAwMCAwLjAwMDAgMC4wMDAwIDc5'
            'Mi4wMDAwIDAuMDAwMCAwLjAwMDAgY20gL0ltMSBEbyBRDQ1lbmRzdHJlYW0NZW5kb2JqDTYgMCBvYmoNNjINZW5kb2JqDTcgMCBvYmoNPDwgDS9MZW5ndGggOCAwIFIgDS9UeXBlIC9Y'
            'T2JqZWN0IA0vU3VidHlwZSAvSW1hZ2UgDS9OYW1lIC9JbTENL1dpZHRoIDE3MDANL0hlaWdodCAyMjAwDS9CaXRzUGVyQ29tcG9uZW50IDgNL0NvbG9yU3BhY2UgL0RldmljZUdyYXkg'
            'DS9GaWx0ZXIgL0ZsYXRlRGVjb2RlICA+Pg1zdHJlYW0NCnic7d1viBznfQfwp7ix5UryGZdLiHBVk0NIlS1hvziwgtCVYPtAC5ZKsQKH3TioYCQ3GCdxfKDWsrFgjVq7pfUthggsRxxx'
            'RYItuqJqRDjMkkvRCwVfctgEieMsITeHhaToj2WpYfvMzO7d7mlPJ6eWZlp/Pi9u5pln5pnf7ov9MnPPztbrAAAAAAAAAAAAAAAAAAAAAAA'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.pid = pid
        msg.pv1 = pv1
        msg.txa = txa
        msg.observation = observation

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
    """ Based on live/nl/nl-mirth-connect.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIE')
        msh.sending_facility = HD(hd_1='ISALA')
        msh.date_time_of_message = '20230814022400'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = '10819306'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20230814022400'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='000322330', cx_4='ISALA&1.1.1.1&GUID', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Visser', xpn_2='Jan', xpn_3='Hendrik', xpn_4='Jr.', xpn_7='D')
        pid.date_time_of_birth = '19941201'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kamperweg 92', xad_3='Zwolle', xad_4='OV', xad_5='8011AB', xad_6='NL', xad_7='P', xad_9='OV')
        pid.pid_13 = '(038)144-1441^P^H^^^038^1443441'
        pid.patient_account_number = CX(cx_1='1055989633', cx_5='HAR')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='F1N', pl_2='F151', pl_3='F151-01', pl_4='FTH', pl_9='HILLS 1 North Oncolog')
        pv1.attending_doctor = XCN(xcn_1='1123456771', xcn_2='Bakker', xcn_3='Maria', xcn_4='K', xcn_9='NPI', xcn_13='NPI')
        pv1.visit_number = CX(cx_1='1234567891')
        pv1.admit_date_time = '20230729081300'

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD777999', ei_2='SndFac', ei_3='1.2.3.4.5', ei_4='ISO')
        orc.filler_order_number = EI(ei_1='432344432', ei_2='FillerFac', ei_3='8.7.6.5.4', ei_4='ISO')
        orc.placer_order_group_number = EI(ei_1='GORD874299', ei_2='SndFac', ei_3='1.2.3.4.5', ei_4='ISO')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20230814011500+0000'
        orc.orc_12 = '5742200012^Verhoeven^Adriaan^^^^^^&372526&L^L^^^NPI'
        orc.orc_17 = 'Isala^L'
        orc.order_type = CWE(cwe_1='I')
        orc.orc_30 = ''

        # .. build TQ1 ..
        tq1 = TQ1()
        tq1.set_id_tq1 = '1'
        tq1.quantity = CQ(cq_1='1')

        # .. build the TIMING group ..
        timing = MdmT02Timing()
        timing.tq1 = tq1

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='432344432', ei_2='FillerFac', ei_3='8.7.6.5.4', ei_4='ISO')
        obr.universal_service_identifier = CWE(cwe_1='11502-2', cwe_3='LN', cwe_5='Laboratory Report')
        obr.observation_date_time = '20130408141909.0+0000'
        obr.observation_end_date_time = '20130411154157.0+0000'
        obr.obr_16 = '5742200012^Verhoeven^Adriaan^^^^^^&372526&L^L^^^NPI'
        obr.result_status = 'F'
        obr.obr_26 = ''

        # .. build the COMMON_ORDER group ..
        common_order = MdmT02CommonOrder()
        common_order.orc = orc
        common_order.timing = timing
        common_order.obr = obr

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='PN')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20230820174913'
        txa.primary_activity_provider_code_name = XCN(xcn_1='1780850958', xcn_2='Timmerman', xcn_3='Margaretha', xcn_13='TIMMERMAN, MARGARETHA')
        txa.origination_date_time = '20230820174913'
        txa.edit_date_time = '20230820191149'
        txa.originator_code_name = XCN(xcn_1='5742200012', xcn_2='Verhoeven', xcn_3='Adriaan', xcn_9='&372526&L', xcn_10='L', xcn_13='NPI')
        txa.assigned_document_authenticator = XCN(xcn_1='1123456771', xcn_2='Bakker', xcn_3='Maria', xcn_4='K', xcn_9='NPI', xcn_13='NPI')
        txa.unique_document_number = EI(ei_1='3738931392', ei_2='ISALA&1.1.1.1&GUID')
        txa.unique_document_file_name = 'PN_Verhoeven_20230820174913.RTF'
        txa.document_completion_status = 'AU'
        txa.document_confidentiality_status = 'R'
        txa.document_availability_status = 'AV'
        txa.distributed_copies_code_and_name_of_recipients = XCN(xcn_2='TIMMERMAN, MARGARETHA')
        txa.folder_assignment = CWE(cwe_1='PHYSICIAN')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='85202', cwe_2='Transcription Authentication Interface Message Text')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'Transcription Authentication Interface Message Text'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='1055860039', cwe_2='Critical Values - Text')
        obx_2.obx_5 = 'Critical Values Entered On: 08/22/2023 2:11 EDT \\.br\\ Performed On: 08/22/2023 2:11 EDT by WOLTERS, JOHANNA C'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20230822021111'
        obx_2.obx_16 = ''

        # .. build the OBSERVATION group ..
        observation_2 = MdmT02Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='&GDT', cwe_2='Critical Values-String')
        obx_3.obx_5 = 'Table formatting from the original result was not included.'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = MdmT02Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ED'
        obx_4.observation_identifier = CWE(
            cwe_1='1111.2',
            cwe_2='PHQ-9 Depression Screen PDF',
            cwe_3='L',
            cwe_4='44249-1',
            cwe_5='PHQ-9 quick depression assessment panel [Reported.PHQ]',
            cwe_6='LN',
        )
        obx_4.obx_5 = 'CareCoordination^AP^PDF^Base64^'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = MdmT02Observation()
        observation_4.obx = obx_4

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.common_order = common_order
        msg.txa = txa
        msg.observation = [observation, observation_2, observation_3, observation_4]

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
    """ Based on live/nl/nl-mirth-connect.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WCDataSend')
        msh.sending_facility = HD(hd_1='SENDING_FACILITY')
        msh.receiving_application = HD(hd_1='wc_hl7d')
        msh.receiving_facility = HD(hd_1='recv_facil')
        msh.date_time_of_message = '20210723040307'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'DSD1627027387370313'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.msh_25 = ''

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20210723040307'
        evn.evn_4 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='222222', cx_4='MR&1.2.840.114398.1.6421.1&ISO', cx_5='MR', cx_6='1.2.840.114398.1.6421.1&MR&ISO'),
            CX(cx_1='736514289', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Vermeer', xpn_2='Anneke', xpn_4='')
        pid.date_time_of_birth = '19860214000000'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rijnkade 10', xad_3='Arnhem', xad_4='GE', xad_5='6811HA', xad_6='NL')
        pid.pid_13 = '+31 26-5551416^PRN^PH'
        pid.patient_account_number = CX(cx_1='506214', cx_4='MNGWCTR1D')
        pid.pid_19 = '736514289'
        pid.pid_39 = ''

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_id = CX(cx_1='506214')
        ft1.transaction_date = DR(dr_1='20210719154000')
        ft1.transaction_type = CWE(cwe_1='CG')
        ft1.transaction_code = CWE(cwe_1='HAIR5PAN')
        ft1.ft1_8 = 'Hair Test 5 Panel'
        ft1.transaction_quantity = '1'
        ft1.transaction_amount_extended = CP(cp_1='79.000000')
        ft1.transaction_amount_unit = CP(cp_1='79.000000')
        ft1.assigned_patient_location = PL(pl_5='MNGWCTR1D', pl_9='WorkHealth Arnhem')
        ft1.patient_type = CWE(cwe_1='VISIT')
        ft1.performed_by_code = XCN(xcn_1='220', xcn_2='Verpleegkundige', xcn_3='WH Arnhem')
        ft1.filler_order_number = EI(ei_1='506214')
        ft1.ft1_24 = '47600^Dekker^Femke^^^Mevr.^LPN'
        ft1.procedure_code = CNE(cne_1='HAIR5PAN')
        ft1.ft1_29 = ''

        # .. build PR1 ..
        pr1 = PR1()
        pr1.set_id_pr1 = '1'
        pr1.pr1_2 = 'CPT'
        pr1.procedure_code = CNE(cne_1='HAIR5PAN')
        pr1.pr1_4 = 'Hair Test 5 Panel'
        pr1.procedure_date_time = '20210719154000'
        pr1.pr1_12 = '220^Verpleegkundige^WH Arnhem'
        pr1.pr1_16 = ''

        # .. build the FINANCIAL_PROCEDURE group ..
        financial_procedure = DftP03FinancialProcedure()
        financial_procedure.pr1 = pr1

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1
        financial.financial_procedure = financial_procedure

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_id = CX(cx_1='506214')
        ft1_2.transaction_date = DR(dr_1='20210719154000')
        ft1_2.transaction_type = CWE(cwe_1='CG')
        ft1_2.transaction_code = CWE(cwe_1='NON9')
        ft1_2.ft1_8 = 'NONDOT 9 Panel (30GQ)'
        ft1_2.transaction_quantity = '1'
        ft1_2.transaction_amount_extended = CP(cp_1='46.000000')
        ft1_2.transaction_amount_unit = CP(cp_1='46.000000')
        ft1_2.assigned_patient_location = PL(pl_5='MNGWCTR1D', pl_9='WorkHealth Arnhem')
        ft1_2.patient_type = CWE(cwe_1='VISIT')
        ft1_2.performed_by_code = XCN(xcn_1='220', xcn_2='Verpleegkundige', xcn_3='WH Arnhem')
        ft1_2.filler_order_number = EI(ei_1='506214')
        ft1_2.ft1_24 = '47600^Dekker^Femke^^^Mevr.^LPN'
        ft1_2.procedure_code = CNE(cne_1='NON9')
        ft1_2.ft1_29 = ''

        # .. build PR1 ..
        pr1_2 = PR1()
        pr1_2.set_id_pr1 = '2'
        pr1_2.pr1_2 = 'CPT'
        pr1_2.procedure_code = CNE(cne_1='NON9')
        pr1_2.pr1_4 = 'NONDOT 9 Panel (30GQ)'
        pr1_2.procedure_date_time = '20210719154000'
        pr1_2.pr1_12 = '220^Verpleegkundige^WH Arnhem'
        pr1_2.pr1_16 = ''

        # .. build the FINANCIAL_PROCEDURE group ..
        financial_procedure_2 = DftP03FinancialProcedure()
        financial_procedure_2.pr1 = pr1_2

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2
        financial_2.financial_procedure = financial_procedure_2

        # .. assemble the full message ..
        msg = DFT_P03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.financial = [financial, financial_2]

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
    """ Based on live/nl/nl-mirth-connect.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WebChart')
        msh.sending_facility = HD(hd_1='SIISCLIENT23068')
        msh.receiving_application = HD(hd_1='Impact')
        msh.receiving_facility = HD(hd_1='SIIS')
        msh.date_time_of_message = '20210723110514-0400'
        msh.message_type = MSG(msg_1='VXU', msg_2='V04', msg_3='VXU_V04')
        msh.message_control_id = 'WCCHIRPA740231627052714'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.message_profile_identifier = EI(ei_1='Z22', ei_2='CDCPHINVS')
        msh.sending_responsible_organization = XON(
            xon_1='SIISCLIENT23068',
            xon_6='NIST-AA-IZ-1&2.16.840.1.113883.3.72.5.40.9&ISO',
            xon_7='XX',
            xon_10='ohioHealth',
        )

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='88888', cx_4='MR', cx_5='MR'), CX(cx_1='836291475', cx_4='MAA', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Bosman', xpn_2='Daan', xpn_7='L')
        pid.date_time_of_birth = '19890513000000'
        pid.administrative_sex = CWE(cwe_1='U')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='Hoofdstraat 45', xad_3='Tilburg', xad_4='NB', xad_5='5038AE', xad_6='NL', xad_7='L', xad_9='NB')
        pid.pid_13 = '^PRN^PH^^^013^5555394'
        pid.ethnic_group = CWE(cwe_1='2186-5', cwe_2='Not Hispanic or Latino', cwe_3='HL70189')

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.filler_order_number = EI(ei_1='74023', ei_2='ohiohealth', ei_3='1.2.840.114398.1.6426', ei_4='ISO')
        orc.orc_10 = '81^Mulder^Saskia^^^^^^ohiohealth&1.2.840.114398.1.6426&ISO^L^^^PRN^^^^^^^^RN'
        orc.orc_12 = '1669786117^Wolters^Elisabeth^^^^^^NPI^L^^^NPI^^^^^^^^CNP'

        # .. build RXA ..
        rxa = RXA()
        rxa.give_sub_id_counter = '0'
        rxa.administration_sub_id_counter = '999'
        rxa.date_time_start_of_administration = '20210723110400'
        rxa.date_time_end_of_administration = '20210723110400'
        rxa.administered_code = CWE(cwe_1='115', cwe_2='Tdap', cwe_3='CVX')
        rxa.administered_amount = '0.5'
        rxa.administered_units = CWE(cwe_1='mL', cwe_2='MilliLiter [SI Volume Units]', cwe_3='UCUM')
        rxa.administration_notes = CWE(cwe_1='00', cwe_2='New immunization record', cwe_3='NIP001')
        rxa.administering_provider = XCN(
            xcn_1='81',
            xcn_2='Mulder',
            xcn_3='Saskia',
            xcn_9='ohiohealth&1.2.840.114398.1.6426&ISO',
            xcn_10='L',
            xcn_13='PRN',
            xcn_21='RN',
        )
        rxa.substance_lot_number = 'U6964AA'
        rxa.substance_expiration_date = '52020223000000'
        rxa.substance_manufacturer_name = CWE(cwe_1='PMC', cwe_2='Sanofi Pasteur', cwe_3='MVX')
        rxa.completion_status = 'CP'
        rxa.action_code_rxa = 'A'
        rxa.system_entry_date_time = '20210723110508'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IM', cwe_2='Intramuscular', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='RD', cwe_2='Right Deltoid', cwe_3='HL70163')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='VFC-STATUS', cwe_2='VFC STATUS', cwe_3='STC')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'V00'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20210723'
        obx.observation_method = CWE(cwe_1='VXC40', cwe_2='Eligibility captured at the immunization level', cwe_3='CDCPHINVS')

        # .. build the OBSERVATION group ..
        observation = VxuV04Observation()
        observation.obx = obx

        # .. build the ORDER group ..
        order = VxuV04Order()
        order.orc = orc
        order.rxa = rxa
        order.rxr = rxr
        order.observation = observation

        # .. assemble the full message ..
        msg = VXU_V04()
        msg.msh = msh
        msg.pid = pid
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
    """ Based on live/nl/nl-mirth-connect.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.msh_2 = '^\\~\\&'
        msh.sending_application = HD(hd_1='IRIS')
        msh.sending_facility = HD(hd_1='IRIS')
        msh.receiving_application = HD(hd_1='Vendor')
        msh.receiving_facility = HD(hd_1='Vendor')
        msh.date_time_of_message = '20191223193115'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = '191223193115'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.pid_2 = 'MRNtest123'
        pid.patient_identifier_list = CX(cx_1='MRNtest123')
        pid.patient_name = XPN(xpn_1='de Vries', xpn_2='Cornelia', xpn_4='')
        pid.date_time_of_birth = '19391126'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_account_number = CX(cx_1='593172846')
        pid.pid_19 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='WRSIM')
        pv1.pv1_7 = 'NPI5556666^Hendriks^Pieter^^^dr.^dr.^^^^^^NPI'
        pv1.pv1_8 = 'NPI5556666^Hendriks^Pieter^^^dr.^dr.^^^^^^NPI'
        pv1.pv1_17 = 'NPI5556666^Hendriks^Pieter^^^dr.^dr.^^^^^^NPI'
        pv1.visit_number = CX(cx_1='593172846')
        pv1.admit_date_time = '20191223012424'
        pv1.discharge_date_time = '20191223012424'

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
        orc.placer_order_number = EI(ei_1='12378912')
        orc.filler_order_number = EI(ei_1='799932', ei_2='IRIS')
        orc.order_status = 'F'
        orc.date_time_of_order_event = '20191223193115'
        orc.orc_12 = 'NPI5556666^Hendriks^Pieter^^^dr.^dr.^^^^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='12378912')
        obr.filler_order_number = EI(ei_1='799932', ei_2='IRIS')
        obr.universal_service_identifier = CWE(cwe_2='FUNDUS PHOTOGRAPHY', cwe_3='EAP', cwe_5='FUNDAL PHOTO')
        obr.observation_date_time = '20191223012424'
        obr.obr_14 = '20191223012424'
        obr.obr_16 = 'NPI5556666^Hendriks^Pieter^^^dr.^dr.^^^^^^NPI'
        obr.results_rpt_status_chng_date_time = '20191223012555'
        obr.result_status = 'F'
        obr.obr_32 = '1234567890^Meijer^Geert^^^dr.^dr.^^^^^^NPI'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='SEVERITY', cwe_3='IRIS')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'CRITICAL'
        obx.interpretation_codes = CWE(cwe_1='AA')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='LEFTDIABRETIN', cwe_3='IRIS')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'Severe'
        obx_2.interpretation_codes = CWE(cwe_1='AA')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='LEFTMACEDEMA', cwe_3='IRIS')
        obx_3.observation_sub_id = OG(og_1='3')
        obx_3.obx_5 = 'Severe'
        obx_3.interpretation_codes = CWE(cwe_1='AA')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='LEFTOTHERRETIN', cwe_3='IRIS')
        obx_4.observation_sub_id = OG(og_1='4')
        obx_4.obx_5 = 'Suspected Vein Occlusion'
        obx_4.interpretation_codes = CWE(cwe_1='A')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='LEFTQUALAPP', cwe_3='IRIS')
        obx_5.observation_sub_id = OG(og_1='5')
        obx_5.obx_5 = 'Gradable Image'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='RIGHTDIABRETIN', cwe_3='IRIS')
        obx_6.observation_sub_id = OG(og_1='6')
        obx_6.obx_5 = 'Moderate'
        obx_6.interpretation_codes = CWE(cwe_1='A')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='RIGHTMACEDEMA', cwe_3='IRIS')
        obx_7.observation_sub_id = OG(og_1='7')
        obx_7.obx_5 = 'Moderate'
        obx_7.interpretation_codes = CWE(cwe_1='A')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'ST'
        obx_8.observation_identifier = CWE(cwe_1='RIGHTOTHERRETIN', cwe_3='IRIS')
        obx_8.observation_sub_id = OG(og_1='8')
        obx_8.obx_5 = 'Suspected Dry AMD'
        obx_8.interpretation_codes = CWE(cwe_1='A')
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'ST'
        obx_9.observation_identifier = CWE(cwe_1='RIGHTQUALAPP', cwe_3='IRIS')
        obx_9.observation_sub_id = OG(og_1='9')
        obx_9.obx_5 = 'Gradable Image'
        obx_9.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'FT'
        obx_10.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_10.observation_sub_id = OG(og_1='001')
        obx_10.obx_5 = 'Retinal Study Result for Cornelia de Vries'
        obx_10.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_10 = OruR01Observation()
        observation_10.obx = obx_10

        # .. build OBX ..
        obx_11 = OBX()
        obx_11.set_id_obx = '11'
        obx_11.value_type = 'FT'
        obx_11.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_11.observation_sub_id = OG(og_1='002')
        obx_11.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_11 = OruR01Observation()
        observation_11.obx = obx_11

        # .. build OBX ..
        obx_12 = OBX()
        obx_12.set_id_obx = '12'
        obx_12.value_type = 'FT'
        obx_12.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_12.observation_sub_id = OG(og_1='003')
        obx_12.obx_5 = 'Cornelia de Vries, a 80 y/o, F (DOB: 11-26-1939, MRN: MRNtest123)'
        obx_12.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_12 = OruR01Observation()
        observation_12.obx = obx_12

        # .. build OBX ..
        obx_13 = OBX()
        obx_13.set_id_obx = '13'
        obx_13.value_type = 'FT'
        obx_13.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_13.observation_sub_id = OG(og_1='004')
        obx_13.obx_5 = 'presented to Rijnstate Oogheelkunde on 12-23-2019 for a retinal imaging study of the left and right eyes.'
        obx_13.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_13 = OruR01Observation()
        observation_13.obx = obx_13

        # .. build OBX ..
        obx_14 = OBX()
        obx_14.set_id_obx = '14'
        obx_14.value_type = 'FT'
        obx_14.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_14.observation_sub_id = OG(og_1='005')
        obx_14.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_14 = OruR01Observation()
        observation_14.obx = obx_14

        # .. build OBX ..
        obx_15 = OBX()
        obx_15.set_id_obx = '15'
        obx_15.value_type = 'FT'
        obx_15.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_15.observation_sub_id = OG(og_1='006')
        obx_15.obx_5 = 'Based on the findings of the study, the following is recommended for Cornelia de Vries'
        obx_15.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_15 = OruR01Observation()
        observation_15.obx = obx_15

        # .. build OBX ..
        obx_16 = OBX()
        obx_16.set_id_obx = '16'
        obx_16.value_type = 'FT'
        obx_16.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_16.observation_sub_id = OG(og_1='007')
        obx_16.obx_5 = 'Next Available Appointment: Refer patient to a retina specialist, next available appointment.'
        obx_16.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_16 = OruR01Observation()
        observation_16.obx = obx_16

        # .. build OBX ..
        obx_17 = OBX()
        obx_17.set_id_obx = '17'
        obx_17.value_type = 'FT'
        obx_17.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_17.observation_sub_id = OG(og_1='008')
        obx_17.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_17 = OruR01Observation()
        observation_17.obx = obx_17

        # .. build OBX ..
        obx_18 = OBX()
        obx_18.set_id_obx = '18'
        obx_18.value_type = 'FT'
        obx_18.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_18.observation_sub_id = OG(og_1='009')
        obx_18.obx_5 = "Interpreting Provider's Comments: No comments provided"
        obx_18.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_18 = OruR01Observation()
        observation_18.obx = obx_18

        # .. build OBX ..
        obx_19 = OBX()
        obx_19.set_id_obx = '19'
        obx_19.value_type = 'FT'
        obx_19.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_19.observation_sub_id = OG(og_1='010')
        obx_19.obx_5 = (
            'Diagnoses Present: E11.3311 - Type 2 diabetes mellitus with moderate nonproliferative diabetic retinopathy with macular edema, right eye'
        )
        obx_19.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_19 = OruR01Observation()
        observation_19.obx = obx_19

        # .. build OBX ..
        obx_20 = OBX()
        obx_20.set_id_obx = '20'
        obx_20.value_type = 'FT'
        obx_20.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_20.observation_sub_id = OG(og_1='011')
        obx_20.obx_5 = 'E11.3412 - Type 2 diabetes mellitus with severe nonproliferative diabetic retinopathy with macular edema, left eye'
        obx_20.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_20 = OruR01Observation()
        observation_20.obx = obx_20

        # .. build OBX ..
        obx_21 = OBX()
        obx_21.set_id_obx = '21'
        obx_21.value_type = 'FT'
        obx_21.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_21.observation_sub_id = OG(og_1='012')
        obx_21.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_21 = OruR01Observation()
        observation_21.obx = obx_21

        # .. build OBX ..
        obx_22 = OBX()
        obx_22.set_id_obx = '22'
        obx_22.value_type = 'FT'
        obx_22.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_22.observation_sub_id = OG(og_1='013')
        obx_22.obx_5 = 'Right eye findings: Diabetic Retinopathy: Moderate'
        obx_22.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_22 = OruR01Observation()
        observation_22.obx = obx_22

        # .. build OBX ..
        obx_23 = OBX()
        obx_23.set_id_obx = '23'
        obx_23.value_type = 'FT'
        obx_23.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_23.observation_sub_id = OG(og_1='014')
        obx_23.obx_5 = 'Macular Edema: Moderate'
        obx_23.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_23 = OruR01Observation()
        observation_23.obx = obx_23

        # .. build OBX ..
        obx_24 = OBX()
        obx_24.set_id_obx = '24'
        obx_24.value_type = 'FT'
        obx_24.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_24.observation_sub_id = OG(og_1='015')
        obx_24.obx_5 = 'Other: Suspected Dry AMD'
        obx_24.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_24 = OruR01Observation()
        observation_24.obx = obx_24

        # .. build OBX ..
        obx_25 = OBX()
        obx_25.set_id_obx = '25'
        obx_25.value_type = 'FT'
        obx_25.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_25.observation_sub_id = OG(og_1='016')
        obx_25.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_25 = OruR01Observation()
        observation_25.obx = obx_25

        # .. build OBX ..
        obx_26 = OBX()
        obx_26.set_id_obx = '26'
        obx_26.value_type = 'FT'
        obx_26.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_26.observation_sub_id = OG(og_1='017')
        obx_26.obx_5 = 'Left eye findings: Diabetic Retinopathy: Severe'
        obx_26.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_26 = OruR01Observation()
        observation_26.obx = obx_26

        # .. build OBX ..
        obx_27 = OBX()
        obx_27.set_id_obx = '27'
        obx_27.value_type = 'FT'
        obx_27.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_27.observation_sub_id = OG(og_1='018')
        obx_27.obx_5 = 'Macular Edema: Severe'
        obx_27.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_27 = OruR01Observation()
        observation_27.obx = obx_27

        # .. build OBX ..
        obx_28 = OBX()
        obx_28.set_id_obx = '28'
        obx_28.value_type = 'FT'
        obx_28.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_28.observation_sub_id = OG(og_1='019')
        obx_28.obx_5 = 'Other: Suspected Vein Occlusion'
        obx_28.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_28 = OruR01Observation()
        observation_28.obx = obx_28

        # .. build OBX ..
        obx_29 = OBX()
        obx_29.set_id_obx = '29'
        obx_29.value_type = 'FT'
        obx_29.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_29.observation_sub_id = OG(og_1='020')
        obx_29.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_29 = OruR01Observation()
        observation_29.obx = obx_29

        # .. build OBX ..
        obx_30 = OBX()
        obx_30.set_id_obx = '30'
        obx_30.value_type = 'FT'
        obx_30.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_30.observation_sub_id = OG(og_1='021')
        obx_30.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_30 = OruR01Observation()
        observation_30.obx = obx_30

        # .. build OBX ..
        obx_31 = OBX()
        obx_31.set_id_obx = '31'
        obx_31.value_type = 'FT'
        obx_31.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_31.observation_sub_id = OG(og_1='022')
        obx_31.obx_5 = 'This result was electronically signed by Meijer, Geert, on 12-23-2019 07:25:55 UTC time.'
        obx_31.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_31 = OruR01Observation()
        observation_31.obx = obx_31

        # .. build OBX ..
        obx_32 = OBX()
        obx_32.set_id_obx = '32'
        obx_32.value_type = 'FT'
        obx_32.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_32.observation_sub_id = OG(og_1='023')
        obx_32.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_32 = OruR01Observation()
        observation_32.obx = obx_32

        # .. build OBX ..
        obx_33 = OBX()
        obx_33.set_id_obx = '33'
        obx_33.value_type = 'FT'
        obx_33.observation_identifier = CWE(cwe_1='Result', cwe_3='IRIS')
        obx_33.observation_sub_id = OG(og_1='024')
        obx_33.obx_5 = 'NOTE: Any pathology noted on this diabetic retinal evaluation should be confirmed by an appropriate ophthalmic examination.'
        obx_33.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_33 = OruR01Observation()
        observation_33.obx = obx_33

        # .. build OBX ..
        obx_34 = OBX()
        obx_34.set_id_obx = '34'
        obx_34.value_type = 'RP'
        obx_34.observation_identifier = CWE(cwe_1='LINK', cwe_3='PDFLINK')
        obx_34.observation_sub_id = OG(og_1='34')
        obx_34.obx_5 = (
            'https://api.retinalscreenings.com/api/PatientOrders/GetSingleResultForDisplayInEmr?patientOrderId=799932\\T\\asPdf=True\\T\\isPreliminary=False'
            '\\T\\auth=6DCAFF6AC2A555F00F9E470D221B6A077C3497A668B1EEBBB4983C8D98672F8FBA00707190026B817325C2A088725B5A0E5D7AB659AC0790C1C1D22B2C50F897\\T\\a'
            'sAddendum=False'
        )
        obx_34.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_34 = OruR01Observation()
        observation_34.obx = obx_34

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
        order_observation.observation_10 = observation_10
        order_observation.observation_11 = observation_11
        order_observation.observation_12 = observation_12
        order_observation.observation_13 = observation_13
        order_observation.observation_14 = observation_14
        order_observation.observation_15 = observation_15
        order_observation.observation_16 = observation_16
        order_observation.observation_17 = observation_17
        order_observation.observation_18 = observation_18
        order_observation.observation_19 = observation_19
        order_observation.observation_20 = observation_20
        order_observation.observation_21 = observation_21
        order_observation.observation_22 = observation_22
        order_observation.observation_23 = observation_23
        order_observation.observation_24 = observation_24
        order_observation.observation_25 = observation_25
        order_observation.observation_26 = observation_26
        order_observation.observation_27 = observation_27
        order_observation.observation_28 = observation_28
        order_observation.observation_29 = observation_29
        order_observation.observation_30 = observation_30
        order_observation.observation_31 = observation_31
        order_observation.observation_32 = observation_32
        order_observation.observation_33 = observation_33
        order_observation.observation_34 = observation_34

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
