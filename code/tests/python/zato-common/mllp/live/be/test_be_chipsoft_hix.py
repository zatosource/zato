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
from zato.hl7v2.v2_9.datatypes import CNE, CP, CWE, CX, EI, FC, HD, MOC, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA05NextOfKin, AdtA39Patient, MfnM02MfStaff, OmlO21Insurance, OmlO21Observation, \
    OmlO21ObservationRequest, OmlO21Order, OmlO21Patient, OmlO21PatientVisit, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12LocationResource, SiuS12Patient, \
    SiuS12Resources, SiuS12Service, VxuV04Observation, VxuV04Order, VxuV04PatientVisit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MFN_M02, OML_O21, ORM_O01, ORU_R01, SIU_S12, VXU_V04
from zato.hl7v2.v2_9.segments import AIL, AIS, DG1, EVN, IN1, MFE, MFI, MRG, MSH, NK1, NTE, OBR, OBX, ORC, PD1, PID, PV1, PV2, RGS, RXA, RXR, SCH, STF

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('be', 'be-chipsoft-hix.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/be/be-chipsoft-hix.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='ZNA_MIDDELHEIM')
        msh.receiving_application = HD(hd_1='CDR')
        msh.receiving_facility = HD(hd_1='ZNA')
        msh.date_time_of_message = '20220923080100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'ZNA20220923080100001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_PAM', ei_2='IHE')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20220923080000'
        evn.operator_id = XCN(xcn_1='admin01', xcn_2='Bogaert', xcn_3='Leen')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='314789256', cx_4='ZNA', cx_5='PI'), CX(cx_1='81061534217', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'PEETERS^Wim^J^^^Mr'
        pid.date_time_of_birth = '19810123'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Turnhoutsebaan 87', xad_3='Antwerpen', xad_5='2140', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^3^2481736~^NET^Internet^wim.peeters@example.be'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='KAT')
        pid.pid_28 = 'N'
        pid.identity_unknown_indicator = 'BE'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MIDH', pl_2='0312', pl_3='001', pl_4='ZNA')
        pv1.attending_doctor = XCN(xcn_1='41827365', xcn_2='Coppens', xcn_3='Marc', xcn_5='Dr', xcn_8='RIZIV')
        pv1.consulting_doctor = XCN(xcn_1='58203946', xcn_2='Michiels', xcn_3='Hilde', xcn_5='Dr', xcn_8='RIZIV')
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='41827365', xcn_2='Coppens', xcn_3='Marc', xcn_5='Dr', xcn_8='RIZIV')
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.pv1_40 = '20220923080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='311', cwe_4='MUTBE')
        in1.insurance_company_id = CX(cx_1='CM412')
        in1.insurance_company_name = XON(xon_1='CM Brabant')
        in1.plan_effective_date = '20220101'
        in1.plan_expiration_date = '20221231'
        in1.insureds_relationship_to_patient = CWE(cwe_1='PEETERS', cwe_2='Wim')
        in1.insureds_address = XAD(xad_1='19810123')
        in1.assignment_of_benefits = CWE(cwe_1='Turnhoutsebaan 87', cwe_3='Antwerpen', cwe_5='2140', cwe_6='BE')
        in1.notice_of_admission_flag = '1'
        in1.policy_deductible = CP(cp_1='314-7892561-45')

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
    """ Based on live/be/be-chipsoft-hix.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='ZNA_STUIVENBERG')
        msh.receiving_application = HD(hd_1='CDR')
        msh.receiving_facility = HD(hd_1='ZNA')
        msh.date_time_of_message = '20221015143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'ZNA20221015143000042'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20221015142800'
        evn.operator_id = XCN(xcn_1='admin02', xcn_2='Wouters', xcn_3='Griet')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='482916730', cx_4='ZNA', cx_5='PI'), CX(cx_1='88061223145', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'JANSSENS^Marie^L^^^Mevr'
        pid.date_time_of_birth = '19880612'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Lange Kievitstraat 40', xad_3='Antwerpen', xad_5='2018', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^3^7614829'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='S')
        pid.identity_reliability_code = CWE(cwe_1='N')
        pid.taxonomic_classification_code = CWE(cwe_1='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='STUV', pl_2='0501', pl_3='003', pl_4='ZNA')
        pv1.attending_doctor = XCN(xcn_1='62937418', xcn_2='Aerts', xcn_3='Dirk', xcn_5='Dr', xcn_8='RIZIV')
        pv1.consulting_doctor = XCN(xcn_1='73048291', xcn_2='Lenaerts', xcn_3='Sabine', xcn_5='Dr', xcn_8='RIZIV')
        pv1.hospital_service = CWE(cwe_1='GER')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='62937418', xcn_2='Aerts', xcn_3='Dirk', xcn_5='Dr', xcn_8='RIZIV')
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.discharge_disposition = CWE(cwe_1='20221005120000')
        pv1.servicing_facility = CWE(cwe_1='20221015142800')
        pv1.pv1_44 = ''

        # .. build PV2 ..
        pv2 = PV2()
        pv2.clinic_organization_name = XON(xon_1='Y')
        pv2.expected_surgery_date_and_time = '20221005'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonie, niet gespecificeerd', cwe_3='ICD10BE')
        dg1.diagnosis_type = CWE(cwe_1='F')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
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
    """ Based on live/be/be-chipsoft-hix.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='GZA_AUGUSTINUS')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='GZA')
        msh.date_time_of_message = '20221110091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'GZA20221110091500017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20221110091400'
        evn.operator_id = XCN(xcn_1='admin03', xcn_2='Hendrickx', xcn_3='Ilse')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='539274816', cx_4='GZA', cx_5='PI'), CX(cx_1='93030912478', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'MAES^Bram^T^^^Dhr'
        pid.date_time_of_birth = '19930309'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = [
            XAD(xad_1='Boomsesteenweg 152', xad_3='Wilrijk', xad_5='2610', xad_6='BE', xad_7='H'),
            XAD(xad_1='Postbus 17', xad_3='Wilrijk', xad_5='2610', xad_6='BE', xad_7='M'),
        ]
        pid.pid_13 = '^PRN^PH^^32^3^8295147~^ORN^CP^^32^477^381926'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='KAT')
        pid.pid_28 = 'N'
        pid.identity_unknown_indicator = 'BE'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AUGW', pl_2='CONS', pl_3='001', pl_4='GZA')
        pv1.attending_doctor = XCN(xcn_1='84516273', xcn_2='De Smedt', xcn_3='Veronique', xcn_5='Dr', xcn_8='RIZIV')
        pv1.preadmit_test_indicator = CWE(cwe_1='AMB')
        pv1.vip_indicator = CWE(cwe_1='5')
        pv1.pending_location = PL(pl_1='20221110091500')

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
    """ Based on live/be/be-chipsoft-hix.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='ZNA_MIDDELHEIM')
        msh.receiving_application = HD(hd_1='CDR')
        msh.receiving_facility = HD(hd_1='ZNA')
        msh.date_time_of_message = '20230215163000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'ZNA20230215163000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20230215162800'
        evn.operator_id = XCN(xcn_1='admin04', xcn_2='Jacobs', xcn_3='Elien')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='617283940', cx_4='ZNA', cx_5='PI'), CX(cx_1='78082536214', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'WILLEMS^Geert^P^^^Dhr'
        pid.date_time_of_birth = '19780825'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Brederodestraat 19', xad_3='Antwerpen', xad_5='2018', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^3^4172835'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='M')
        pid.identity_reliability_code = CWE(cwe_1='N')
        pid.taxonomic_classification_code = CWE(cwe_1='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MIDH', pl_2='ICU', pl_3='002', pl_4='ZNA')
        pv1.attending_doctor = XCN(xcn_1='95061248', xcn_2='Van Damme', xcn_3='Inge', xcn_5='Dr', xcn_8='RIZIV')
        pv1.preadmit_test_indicator = CWE(cwe_1='MED')
        pv1.vip_indicator = CWE(cwe_1='3')
        pv1.visit_number = CX(cx_1='95061248', cx_2='Van Damme', cx_3='Inge', cx_5='Dr', cx_8='RIZIV')
        pv1.financial_class = FC(fc_1='IN')
        pv1.diet_type = CWE(cwe_1='20230210090000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.military_partnership_code = '20230210'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/be/be-chipsoft-hix.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='ZOL_GENK')
        msh.receiving_application = HD(hd_1='PACS')
        msh.receiving_facility = HD(hd_1='ZOL')
        msh.date_time_of_message = '20230310141500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ZOL20230310141500003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='725816394', cx_4='ZOL', cx_5='PI'), CX(cx_1='85110523176', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='GOOSSENS', xpn_2='Raf', xpn_4='Dhr')
        pid.date_time_of_birth = '19851105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vennestraat 61', xad_3='Genk', xad_5='3600', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^89^517382'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='M')
        pid.identity_reliability_code = CWE(cwe_1='N')
        pid.taxonomic_classification_code = CWE(cwe_1='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ZOL', pl_2='RAD', pl_3='001', pl_4='ZOL')
        pv1.attending_doctor = XCN(xcn_1='36281947', xcn_2='Claes', xcn_3='Pieter', xcn_5='Dr', xcn_8='RIZIV')
        pv1.preadmit_test_indicator = CWE(cwe_1='RAD')
        pv1.vip_indicator = CWE(cwe_1='1')

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
        orc.placer_order_number = EI(ei_1='ORD20230001')
        orc.filler_order_number = EI(ei_1='ORD20230001')
        orc.order_status = 'SC'
        orc.orc_8 = '1^^^20230310142000^^R'
        orc.orc_10 = '20230310141500'
        orc.orc_11 = 'admin05^Mertens^Katja'
        orc.enterers_location = PL(pl_1='36281947', pl_2='Claes', pl_3='Pieter', pl_5='Dr', pl_8='RIZIV')
        orc.call_back_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_5='32', xtn_6='89', xtn_7='294173')
        orc.orc_17 = 'ZOL_GENK'
        orc.orc_18 = 'Vennestraat 61^^Genk^^3600^BE'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20230001')
        obr.filler_order_number = EI(ei_1='ORD20230001')
        obr.universal_service_identifier = CWE(cwe_1='459003', cwe_2='RX Thorax PA+LAT', cwe_3='RIZIV_NOM')
        obr.obr_6 = '20230310142000'
        obr.specimen_action_code = 'L'
        obr.relevant_clinical_information = CWE(cwe_1='pijn op de borst na inspanning')
        obr.obr_17 = '36281947^Claes^Pieter^^Dr^^^RIZIV'
        obr.placer_field_2 = 'RAD001'
        obr.result_status = '1^^^20230310142000^^R'

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
    """ Based on live/be/be-chipsoft-hix.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='ZNA_LAB')
        msh.receiving_application = HD(hd_1='HIX')
        msh.receiving_facility = HD(hd_1='ZNA')
        msh.date_time_of_message = '20230412100500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ZNA_LAB20230412100500012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='836192475', cx_4='ZNA', cx_5='PI'), CX(cx_1='91051523698', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='DE SMEDT', xpn_2='Elke', xpn_4='Mevr')
        pid.date_time_of_birth = '19910515'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Belgiëlei 72', xad_3='Antwerpen', xad_5='2018', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MIDH', pl_2='0312', pl_3='002', pl_4='ZNA')
        pv1.attending_doctor = XCN(xcn_1='41827365', xcn_2='Coppens', xcn_3='Marc', xcn_5='Dr', xcn_8='RIZIV')

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
        orc.placer_order_number = EI(ei_1='LAB20230001')
        orc.filler_order_number = EI(ei_1='LAB20230001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20230001')
        obr.filler_order_number = EI(ei_1='LAB20230001')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel', cwe_3='LN')
        obr.obr_6 = '20230412080000'
        obr.obr_17 = '41827365^Coppens^Marc^^Dr^^^RIZIV'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocyten', cwe_3='LN')
        obx.obx_5 = '7.2'
        obx.units = CWE(cwe_1='10*9/L')
        obx.reference_range = '4.0-10.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20230412093000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erytrocyten', cwe_3='LN')
        obx_2.obx_5 = '4.55'
        obx_2.units = CWE(cwe_1='10*12/L')
        obx_2.reference_range = '3.80-5.50'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20230412093000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobine', cwe_3='LN')
        obx_3.obx_5 = '13.8'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '11.5-16.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20230412093000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocriet', cwe_3='LN')
        obx_4.obx_5 = '41.2'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '36.0-46.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20230412093000'

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
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20230412093000'

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
    """ Based on live/be/be-chipsoft-hix.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='GZA_LAB')
        msh.receiving_application = HD(hd_1='HIX')
        msh.receiving_facility = HD(hd_1='GZA')
        msh.date_time_of_message = '20230520093000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'GZA_LAB20230520093000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='948362517', cx_4='GZA', cx_5='PI'), CX(cx_1='94021814263', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='BOGAERT', xpn_2='Robbe', xpn_4='Dhr')
        pid.date_time_of_birth = '19940218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Edegem Drie Eikenstraat 12', xad_3='Wilrijk', xad_5='2650', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AUGW', pl_2='CONS', pl_3='002', pl_4='GZA')
        pv1.attending_doctor = XCN(xcn_1='84516273', xcn_2='De Smedt', xcn_3='Veronique', xcn_5='Dr', xcn_8='RIZIV')

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
        orc.placer_order_number = EI(ei_1='LAB20230100')
        orc.filler_order_number = EI(ei_1='LAB20230100')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB20230100')
        obr.filler_order_number = EI(ei_1='LAB20230100')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='CMP', cwe_3='LN')
        obr.obr_6 = '20230520080000'
        obr.obr_17 = '84516273^De Smedt^Veronique^^Dr^^^RIZIV'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '5.6'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.9-5.8'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20230520090000'

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
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20230520090000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Ureum', cwe_3='LN')
        obx_3.obx_5 = '6.1'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.5-7.5'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20230520090000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Natrium', cwe_3='LN')
        obx_4.obx_5 = '141'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20230520090000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Kalium', cwe_3='LN')
        obx_5.obx_5 = '4.3'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20230520090000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALAT', cwe_3='LN')
        obx_6.obx_5 = '28'
        obx_6.units = CWE(cwe_1='U/L')
        obx_6.reference_range = '0-41'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20230520090000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1920-8', cwe_2='ASAT', cwe_3='LN')
        obx_7.obx_5 = '24'
        obx_7.units = CWE(cwe_1='U/L')
        obx_7.reference_range = '0-40'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20230520090000'

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
    """ Based on live/be/be-chipsoft-hix.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='ZNA_STUIVENBERG')
        msh.receiving_application = HD(hd_1='LIS')
        msh.receiving_facility = HD(hd_1='ZNA_LAB')
        msh.date_time_of_message = '20230601110000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ZNA20230601110000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='159374826', cx_4='ZNA', cx_5='PI'), CX(cx_1='98070312589', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='CLAES', xpn_2='Eva', xpn_4='Mevr')
        pid.date_time_of_birth = '19980703'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Van Schoonhovenstraat 8', xad_3='Antwerpen', xad_5='2000', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^3^6381247'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='STUV', pl_2='0601', pl_3='001', pl_4='ZNA')
        pv1.attending_doctor = XCN(xcn_1='27493861', xcn_2='Wouters', xcn_3='Jan', xcn_5='Dr', xcn_8='RIZIV')
        pv1.preadmit_test_indicator = CWE(cwe_1='MED')
        pv1.vip_indicator = CWE(cwe_1='2')

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
        orc.placer_order_number = EI(ei_1='ORD20230501')
        orc.filler_order_number = EI(ei_1='ORD20230501')
        orc.order_status = 'IP'
        orc.orc_8 = '1^^^20230601113000^^R'
        orc.orc_10 = '20230601110000'
        orc.orc_11 = 'admin06^Michiels^Tine'
        orc.enterers_location = PL(pl_1='27493861', pl_2='Wouters', pl_3='Jan', pl_5='Dr', pl_8='RIZIV')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20230501')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC + Diff', cwe_3='LN')
        obr.obr_6 = '20230601113000'
        obr.specimen_action_code = 'L'
        obr.relevant_clinical_information = CWE(cwe_1='koorts en vermoeidheid')
        obr.obr_17 = '27493861^Wouters^Jan^^Dr^^^RIZIV'

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
        obr_2.placer_order_number = EI(ei_1='ORD20230501')
        obr_2.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='CMP', cwe_3='LN')
        obr_2.obr_6 = '20230601113000'
        obr_2.specimen_action_code = 'L'
        obr_2.obr_17 = '27493861^Wouters^Jan^^Dr^^^RIZIV'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD20230501')
        obr_3.universal_service_identifier = CWE(cwe_1='30341-2', cwe_2='ESR', cwe_3='LN')
        obr_3.obr_6 = '20230601113000'
        obr_3.specimen_action_code = 'L'
        obr_3.obr_17 = '27493861^Wouters^Jan^^Dr^^^RIZIV'

        # .. build OBR ..
        obr_4 = OBR()
        obr_4.set_id_obr = '4'
        obr_4.placer_order_number = EI(ei_1='ORD20230501')
        obr_4.universal_service_identifier = CWE(cwe_1='1988-5', cwe_2='CRP', cwe_3='LN')
        obr_4.obr_6 = '20230601113000'
        obr_4.specimen_action_code = 'L'
        obr_4.obr_17 = '27493861^Wouters^Jan^^Dr^^^RIZIV'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3, obr_4]

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
    """ Based on live/be/be-chipsoft-hix.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='ZOL_GENK')
        msh.receiving_application = HD(hd_1='AGENDA')
        msh.receiving_facility = HD(hd_1='ZOL')
        msh.date_time_of_message = '20230705090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'ZOL20230705090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20230501')
        sch.appointment_reason = CWE(cwe_1='ROUTINE')
        sch.appointment_type = CWE(cwe_1='30')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='30', cne_4='20230710140000', cne_5='20230710143000')
        sch.placer_contact_location = PL(pl_1='48173926', pl_2='Hendrickx', pl_3='Filip', pl_5='Dr', pl_8='RIZIV')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='261847395', cx_4='ZOL', cx_5='PI'), CX(cx_1='83122236914', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='VAN DAMME', xpn_2='Kris', xpn_4='Dhr')
        pid.date_time_of_birth = '19831222'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stalenstraat 27', xad_3='Genk', xad_5='3600', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^89^174293'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ZOL', pl_2='CARD', pl_3='001', pl_4='ZOL')
        pv1.attending_doctor = XCN(xcn_1='48173926', xcn_2='Hendrickx', xcn_3='Filip', xcn_5='Dr', xcn_8='RIZIV')
        pv1.preadmit_test_indicator = CWE(cwe_1='CAR')
        pv1.vip_indicator = CWE(cwe_1='1')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='CARDCONS', cwe_2='Consultatie Cardiologie', cwe_3='L')
        ais.start_date_time = '20230710140000'
        ais.duration = '30'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='ZOL', pl_2='CARD', pl_3='001', pl_4='ZOL')
        ail.filler_status_code = CWE(cwe_1='F')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.location_resource = location_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/be/be-chipsoft-hix.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='ZNA')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='ZNA_REG')
        msh.date_time_of_message = '20230801100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'ZNA20230801100000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_PAM', ei_2='IHE')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20230801100000'
        evn.operator_id = XCN(xcn_1='admin07', xcn_2='Lenaerts', xcn_3='Sarah')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='371649258', cx_4='ZNA', cx_5='PI'), CX(cx_1='03062923185', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'MERTENS^Lotte^R^^^Mevr'
        pid.date_time_of_birth = '20030629'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Borsbeeksebrug 14', xad_3='Deurne', xad_5='2100', xad_6='BE', xad_7='H')
        pid.pid_13 = '^PRN^PH^^32^3^9317428~^ORN^CP^^32^468^271849~^NET^Internet^lotte.mertens@example.be'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='S')
        pid.religion = CWE(cwe_1='KAT')
        pid.pid_28 = 'N'
        pid.identity_unknown_indicator = 'BE'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = '59274183^Jacobs^Ruben^^Dr^^^RIZIV'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='MERTENS', xpn_2='Frank', xpn_5='Dhr')
        nk1.relationship = CWE(cwe_1='FTH')
        nk1.address = XAD(xad_1='Borsbeeksebrug 14', xad_3='Deurne', xad_5='2100', xad_6='BE', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^32^3^9317455'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin

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
    """ Based on live/be/be-chipsoft-hix.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='ZNA_MICRO')
        msh.receiving_application = HD(hd_1='HIX')
        msh.receiving_facility = HD(hd_1='ZNA')
        msh.date_time_of_message = '20230905153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ZNA_MICRO20230905153000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='314789256', cx_4='ZNA', cx_5='PI'), CX(cx_1='81061534217', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'PEETERS^Wim^J^^^Mr'
        pid.date_time_of_birth = '19810123'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Turnhoutsebaan 87', xad_3='Antwerpen', xad_5='2140', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MIDH', pl_2='0312', pl_3='001', pl_4='ZNA')
        pv1.attending_doctor = XCN(xcn_1='41827365', xcn_2='Coppens', xcn_3='Marc', xcn_5='Dr', xcn_8='RIZIV')

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
        orc.placer_order_number = EI(ei_1='MICRO20230001')
        orc.filler_order_number = EI(ei_1='MICRO20230001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MICRO20230001')
        obr.filler_order_number = EI(ei_1='MICRO20230001')
        obr.universal_service_identifier = CWE(cwe_1='630-4', cwe_2='Urinekweek', cwe_3='LN')
        obr.obr_6 = '20230904080000'
        obr.obr_17 = '41827365^Coppens^Marc^^Dr^^^RIZIV'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='Bacterie identificatie', cwe_3='LN')
        obx.obx_5 = '112283005^Escherichia coli^SCT'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20230905140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Antibiogram', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'Amoxicilline/Clavulaanzuur: S'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20230905140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Antibiogram', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='2')
        obx_3.obx_5 = 'Ciprofloxacine: R'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20230905140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Antibiogram', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='3')
        obx_4.obx_5 = 'Nitrofurantoine: S'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20230905140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Antibiogram', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='4')
        obx_5.obx_5 = 'Trimethoprim/Sulfamethoxazol: I'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20230905140000'

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
    """ Based on live/be/be-chipsoft-hix.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PATH')
        msh.sending_facility = HD(hd_1='GZA_PATH')
        msh.receiving_application = HD(hd_1='HIX')
        msh.receiving_facility = HD(hd_1='GZA')
        msh.date_time_of_message = '20231010160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'GZA_PATH20231010160000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='539274816', cx_4='GZA', cx_5='PI'), CX(cx_1='93030912478', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'MAES^Bram^T^^^Dhr'
        pid.date_time_of_birth = '19930309'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Boomsesteenweg 152', xad_3='Wilrijk', xad_5='2610', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AUGW', pl_2='CHIR', pl_3='003', pl_4='GZA')
        pv1.attending_doctor = XCN(xcn_1='58203946', xcn_2='Michiels', xcn_3='Hilde', xcn_5='Dr', xcn_8='RIZIV')

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
        orc.placer_order_number = EI(ei_1='PATH20230050')
        orc.filler_order_number = EI(ei_1='PATH20230050')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PATH20230050')
        obr.filler_order_number = EI(ei_1='PATH20230050')
        obr.universal_service_identifier = CWE(cwe_1='22634-0', cwe_2='Pathologisch onderzoek', cwe_3='LN')
        obr.obr_6 = '20231005120000'
        obr.obr_17 = '58203946^Michiels^Hilde^^Dr^^^RIZIV'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22634-0', cwe_2='Pathologie conclusie', cwe_3='LN')
        obx.obx_5 = 'Colon biopsie: chronische actieve colitis, geen dysplasie, geen maligniteit'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20231010150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Pathologie verslag', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFBhdGhvbG9naXNjaCB2ZXJzbGFnKQovQ3JlYXRvciAoR1pBIFBhdGhvbG9naWUpCi9Qcm9kdWNlciAoQ2hpcFNvZnQgSGlYKQovQ3Jl'
            'YXRpb25EYXRlIChEOjIwMjMxMDEwMTUwMDAwKzAxJzAwJykKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDMgMCBSID4+CmVuZG9iagozIDAgb2JqCjw8'
            'IC9UeXBlIC9QYWdlcyAvS2lkcyBbNCAwIFJdIC9Db3VudCAxID4+CmVuZG9iago0IDAgb2JqCjw8IC9UeXBlIC9QYWdlIC9QYXJlbnQgMyAwIFIgL01lZGlhQm94IFswIDAgNTk1IDg0'
            'Ml0gPj4KZW5kb2JqCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMTcwIDAwMDAwIG4gCjAwMDAwMDAyMjEgMDAwMDAgbiAKMDAw'
            'MDAwMDI4MCAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDUgL1Jvb3QgMiAwIFIgPj4Kc3RhcnR4cmVmCjM3MAolJUVPRgo='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20231010150000'

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
    """ Based on live/be/be-chipsoft-hix.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='ZOL_RAD')
        msh.receiving_application = HD(hd_1='HIX')
        msh.receiving_facility = HD(hd_1='ZOL')
        msh.date_time_of_message = '20231115110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ZOL_RAD20231115110000022'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='725816394', cx_4='ZOL', cx_5='PI'), CX(cx_1='85110523176', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='GOOSSENS', xpn_2='Raf', xpn_4='Dhr')
        pid.date_time_of_birth = '19851105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vennestraat 61', xad_3='Genk', xad_5='3600', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ZOL', pl_2='RAD', pl_3='001', pl_4='ZOL')
        pv1.attending_doctor = XCN(xcn_1='36281947', xcn_2='Claes', xcn_3='Pieter', xcn_5='Dr', xcn_8='RIZIV')

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
        orc.placer_order_number = EI(ei_1='RAD20230300')
        orc.filler_order_number = EI(ei_1='RAD20230300')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20230300')
        obr.filler_order_number = EI(ei_1='RAD20230300')
        obr.universal_service_identifier = CWE(cwe_1='459003', cwe_2='RX Thorax PA+LAT', cwe_3='RIZIV_NOM')
        obr.obr_6 = '20230310142000'
        obr.obr_17 = '36281947^Claes^Pieter^^Dr^^^RIZIV'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='59776-5', cwe_2='Radiologisch verslag', cwe_3='LN')
        obx.obx_5 = 'Thorax PA en LAT: geen aanwijzingen voor infiltraat of pneumothorax. Normaal hartsilhouet. Geen pleurale effusie.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20231115100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Radiologisch verslag', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFJhZGlvbG9naXNjaCB2ZXJzbGFnKQovQ3JlYXRvciAoWk9MIFJhZGlvbG9naWUpCi9Qcm9kdWNlciAoQ2hpcFNvZnQgSGlYKQovQ3Jl'
            'YXRpb25EYXRlIChEOjIwMjMxMTE1MTAwMDAwKzAxJzAwJykKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDMgMCBSID4+CmVuZG9iagozIDAgb2JqCjw8'
            'IC9UeXBlIC9QYWdlcyAvS2lkcyBbNCAwIFJdIC9Db3VudCAxID4+CmVuZG9iago0IDAgb2JqCjw8IC9UeXBlIC9QYWdlIC9QYXJlbnQgMyAwIFIgL01lZGlhQm94IFswIDAgNTk1IDg0'
            'Ml0gPj4KZW5kb2JqCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMTcyIDAwMDAwIG4gCjAwMDAwMDAyMjMgMDAwMDAgbiAKMDAw'
            'MDAwMDI4MiAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDUgL1Jvb3QgMiAwIFIgPj4Kc3RhcnR4cmVmCjM3MgolJUVPRgo='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20231115100000'

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
    """ Based on live/be/be-chipsoft-hix.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20210407153459+0200'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = '23c517a5fc6a437cb05b'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.source_of_comment = 'P'
        nte.comment = 'KC en MMB'
        nte.comment_type = CWE(cwe_1='ZD_CLUSTER_NAME', cwe_2='ZorgDomein clusternaam', cwe_3='L')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='222333444', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='ZD345671140', cx_4='ZorgDomein', cx_5='VN')]
        pid.patient_name = XPN(xpn_1='de Teststam - van Proefnaam&van&Proefnaam&de&Teststam', xpn_2='G', xpn_3='A', xpn_7='L')
        pid.date_time_of_birth = '20030101'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [
            XAD(xad_1='Proefstraat 22 B&Proefstraat&22', xad_2='B', xad_3='WoonplaatsProef', xad_5='2222BB', xad_6='NL', xad_7='M'),
            XAD(xad_1='Woonadresweg 33 C&Woonadresweg&33', xad_2='C', xad_3='WoonplaatsProef', xad_5='3333CC', xad_6='NL', xad_7='H'),
        ]
        pid.pid_13 = '07-23456789^ORN^CP~021-5826394^PRN^PH~^NET^Internet^prullenbak@zorgdomein.nl'
        pid.identity_unknown_indicator = 'Y'
        pid.identity_reliability_code = CWE(cwe_1='NNNLD')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.visit_indicator = CWE(cwe_1='V')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='LABEDG001', cwe_2='klinische chemie en medische microbiologie onderzoek', cwe_3='L')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO21PatientVisit()
        patient_visit.pv1 = pv1
        patient_visit.pv2 = pv2

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_2='null')
        in1.insurance_company_id = CX(cx_1='0102', cx_4='VEKTIS', cx_5='UZOVI')
        in1.insurance_company_name = XON(xon_1='Zorgverzekeraarnaam')
        in1.policy_number = '953513'

        # .. build the INSURANCE group ..
        insurance = OmlO21Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ZD345671140')
        orc.placer_order_group_number = EI(ei_1='ZD345671140')
        orc.orc_7 = '^^^^^C'
        orc.date_time_of_order_event = '20210407153428+0200'
        orc.orc_10 = '^de Proefassistent^A.B.C.'
        orc.orc_12 = '02115678^van Proefhuisarts^A.B.^^^^^^VEKTIS'
        orc.enterers_location = PL(pl_9='Huisartspraktijk Proefdomein, locatie Breukelen', pl_10='02123451&VEKTIS')
        orc.orc_14 = '0212345673^WPN^PH~0212345674^WPN^FX'
        orc.orc_17 = '02123452^Huisartspraktijk Proefdomein^VEKTIS'
        orc.orc_21 = 'Huisartspraktijk Proefdomein^^02123452^^^VEKTIS'
        orc.orc_22 = 'Besteldersweg 88 B&Besteldersweg&88^B^Besteldersplaats^^3333CC^NL'
        orc.orc_23 = '0212345671^WPN^PH~0212345672^WPN^FX'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD345671140')
        obr.universal_service_identifier = CWE(cwe_1='LABEDG001', cwe_2='klinische chemie en medische microbiologie', cwe_3='L')
        obr.specimen_action_code = 'L'
        obr.obr_16 = '02115678^van Proefhuisarts^A.B.^^^^^^VEKTIS'
        obr.obr_17 = '0212345673^WPN^PH~0212345674^WPN^FX'
        obr.obr_28 = '02115679^Proefbehandelaar^A.^^^^^^VEKTIS^^^^^^^Verpleeghuis Proefdomein^^^^^Specialisme'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='AI', cwe_2='opmerkingen / klinische gegevens', cwe_3='L')
        obx.obx_5 = 'opmerking van verwijzer'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OmlO21Observation()
        observation.obx = obx

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OmlO21ObservationRequest()
        observation_request.obr = obr
        observation_request.observation = observation

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc
        order.observation_request = observation_request

        # .. assemble the full message ..
        msg = OML_O21()
        msg.msh = msh
        msg.nte = nte
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
    """ Based on live/be/be-chipsoft-hix.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20160324163509+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'ZD200046119'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='de Teststam&de&Teststam', xpn_2='G', xpn_3='A', xpn_7='L')
        pid.date_time_of_birth = '20030101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(
            xad_1='StraatnaamProef 777  ter&StraatnaamProef&777',
            xad_2='ter',
            xad_3='WoonplaatsProef',
            xad_5='2222BB',
            xad_6='NL',
            xad_7='H',
        )
        pid.pid_13 = '021-5826394_^NET^Internet^prullenbak@zorgdomein.nl'

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
        orc.orc_10 = '^&&het Proefassistent^A.B.C.'
        orc.orc_12 = '02115678^&&van Proefhuisarts^A.B.^^^^^^VEKTIS'
        orc.orc_14 = '016-3333333'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD200046119')
        obr.universal_service_identifier = CWE(cwe_1='CIS', cwe_2='Cardiologie', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20160324163432+0100'
        obr.obr_16 = '02115678^&&van Proefhuisarts^A.B.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='VB', cwe_3='123')
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
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFZlcndpanpicmllZikKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL0NhdGFsb2cgL1BhZ2VzIDMgMCBSID4+CmVuZG9iagozIDAg'
            'b2JqCjw8IC9UeXBlIC9QYWdlcyAvS2lkcyBbNCAwIFJdIC9Db3VudCAxID4+CmVuZG9iago0IDAgb2JqCjw8IC9UeXBlIC9QYWdlIC9QYXJlbnQgMyAwIFIgL01lZGlhQm94IFswIDAg'
            'NTk1IDg0Ml0gPj4KZW5kb2JqCnhyZWYKMCA1CnRyYWlsZXIKPDwgL1NpemUgNSAvUm9vdCAyIDAgUiA+PgpzdGFydHhyZWYKMjUwCiUlRU9GCg=='
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
    """ Based on live/be/be-chipsoft-hix.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='ZNA')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='ZNA_REG')
        msh.date_time_of_message = '20231201080000'
        msh.message_type = MSG(msg_1='MFN', msg_2='M02', msg_3='MFN_M02')
        msh.message_control_id = 'ZNA20231201080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build MFI ..
        mfi = MFI()
        mfi.master_file_identifier = CWE(cwe_1='PRA', cwe_2='Practitioners', cwe_3='HL70175')
        mfi.master_file_application_identifier = HD(hd_1='ZNA_ARTS')
        mfi.file_level_event_code = 'UPD'
        mfi.response_level_code = 'NE'

        # .. build MFE ..
        mfe = MFE()
        mfe.record_level_event_code = 'MAD'
        mfe.mfn_control_id = '20231201080000'
        mfe.effective_date_time = '20231201'
        mfe.mfe_5 = '41827365^Coppens^Marc^^Dr'

        # .. build STF ..
        stf = STF()
        stf.primary_key_value_stf = CWE(cwe_1='41827365', cwe_2='Coppens', cwe_3='Marc', cwe_5='Dr', cwe_7='RIZIV')
        stf.staff_identifier_list = CX(cx_1='41827365')
        stf.staff_name = [XPN(xpn_1='INT', xpn_2='Interne Geneeskunde', xpn_3='L'), XPN(xpn_1='CAR', xpn_2='Cardiologie', xpn_3='L')]
        stf.staff_type = CWE(cwe_1='Dr')
        stf.administrative_sex = CWE(cwe_1='M')
        stf.date_time_of_birth = '19730515'
        stf.active_inactive_flag = 'A'
        stf.hospital_service_stf = CWE(cwe_2='WPN', cwe_3='PH', cwe_5='32', cwe_6='3', cwe_7='7182934')
        stf.stf_10 = 'Italielei 44^^Antwerpen^^2000^BE^B'
        stf.office_home_address_birthplace = XAD(xad_1='20000101')

        # .. build the MF_STAFF group ..
        mf_staff = MfnM02MfStaff()
        mf_staff.mfe = mfe
        mf_staff.stf = stf

        # .. build MFE ..
        mfe_2 = MFE()
        mfe_2.record_level_event_code = 'MAD'
        mfe_2.mfn_control_id = '20231201080000'
        mfe_2.effective_date_time = '20231201'
        mfe_2.mfe_5 = '62937418^Aerts^Dirk^^Dr'

        # .. build STF ..
        stf_2 = STF()
        stf_2.primary_key_value_stf = CWE(cwe_1='62937418', cwe_2='Aerts', cwe_3='Dirk', cwe_5='Dr', cwe_7='RIZIV')
        stf_2.staff_identifier_list = CX(cx_1='62937418')
        stf_2.staff_name = XPN(xpn_1='GER', xpn_2='Geriatrie', xpn_3='L')
        stf_2.staff_type = CWE(cwe_1='Dr')
        stf_2.administrative_sex = CWE(cwe_1='M')
        stf_2.date_time_of_birth = '19780310'
        stf_2.active_inactive_flag = 'A'
        stf_2.hospital_service_stf = CWE(cwe_2='WPN', cwe_3='PH', cwe_5='32', cwe_6='3', cwe_7='2839174')
        stf_2.stf_10 = 'Kipdorpvest 30^^Antwerpen^^2000^BE^B'
        stf_2.office_home_address_birthplace = XAD(xad_1='20050601')

        # .. build the MF_STAFF group ..
        mf_staff_2 = MfnM02MfStaff()
        mf_staff_2.mfe = mfe_2
        mf_staff_2.stf = stf_2

        # .. assemble the full message ..
        msg = MFN_M02()
        msg.msh = msh
        msg.mfi = mfi
        msg.mf_staff = [mf_staff, mf_staff_2]

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
    """ Based on live/be/be-chipsoft-hix.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='ZNA')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='ZNA_REG')
        msh.date_time_of_message = '20231215120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'ZNA20231215120000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='IHE_PAM', ei_2='IHE')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20231215120000'
        evn.operator_id = XCN(xcn_1='admin08', xcn_2='Aerts', xcn_3='Yannick')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='314789256', cx_4='ZNA', cx_5='PI'), CX(cx_1='81061534217', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'PEETERS^Wim^J^^^Mr'
        pid.date_time_of_birth = '19810123'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Turnhoutsebaan 87', xad_3='Antwerpen', xad_5='2140', xad_6='BE', xad_7='H')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='999888777', cx_4='ZNA', cx_5='PI')
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
    """ Based on live/be/be-chipsoft-hix.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20160324163507+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'ZD200046119'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='de Teststam&de&Teststam', xpn_2='G', xpn_3='A', xpn_7='L')
        pid.date_time_of_birth = '20030101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(
            xad_1='StraatnaamProef 777  ter&StraatnaamProef&777',
            xad_2='ter',
            xad_3='WoonplaatsProef',
            xad_5='2222BB',
            xad_6='NL',
            xad_7='H',
        )
        pid.pid_13 = '021-5826394'

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
        orc.order_control = 'XO'
        orc.placer_order_number = EI(ei_1='ZD200046119')
        orc.date_time_of_order_event = '20160324163432+0100'
        orc.orc_10 = '^&&het Proefassistent^A.B.C.'
        orc.orc_12 = '02115678^&&van Proefhuisarts^A.B.^^^^^^VEKTIS'
        orc.orc_14 = '016-3333333'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD200046119')
        obr.universal_service_identifier = CWE(cwe_1='CARCOA001', cwe_2='zorgproductcode', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20160324163432+0100'
        obr.relevant_clinical_information = CWE(cwe_1='Mijn toelichting op de bijlagen.')
        obr.obr_16 = '02115678^&&van Proefhuisarts^A.B.^^^^^^VEKTIS'
        obr.result_status = 'F'
        obr.placer_supplemental_service_information = CWE(
            cwe_2=(
                'Overzicht van de bijlagen:\\.br\\De volgende bijlage(n) behorend bij de verwijzing met ZD200046119 is/zijn verzonden\\.br\\- HL7.doc\\.br\\-'
                ' logo.png\\.br\\'
            ),
        )

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='BLOB', cwe_2='Bijlage', cwe_3='ZORGDOMEIN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '^application^msword^Base64^0M8R4KGxGuEAAAAAAAAAAAAAAAAAAAAAPgADAP7/CQAGAAAAAAAAAAAAAAABAAAA'
        obx.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.source_of_comment = 'P'
        nte.comment = 'HL7.doc'
        nte.comment_type = CWE(cwe_1='RE')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx
        observation.nte = nte

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='BLOB', cwe_2='Bijlage', cwe_3='ZORGDOMEIN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = '^image^png^Base64^iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
        obx_2.observation_result_status = 'F'

        # .. build NTE ..
        nte_2 = NTE()
        nte_2.set_id_nte = '2'
        nte_2.source_of_comment = 'P'
        nte_2.comment = 'logo.png'
        nte_2.comment_type = CWE(cwe_1='RE')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2
        observation_2.nte = nte_2

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
    """ Based on live/be/be-chipsoft-hix.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='ZNA')
        msh.receiving_application = HD(hd_1='VACCINNET')
        msh.receiving_facility = HD(hd_1='EHEALTH_BE')
        msh.date_time_of_message = '20230915100000'
        msh.message_type = MSG(msg_1='VXU', msg_2='V04', msg_3='VXU_V04')
        msh.message_control_id = 'ZNA20230915100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='314789256', cx_4='ZNA', cx_5='PI'), CX(cx_1='81061534217', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'PEETERS^Wim^J^^^Mr'
        pid.date_time_of_birth = '19810123'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Turnhoutsebaan 87', xad_3='Antwerpen', xad_5='2140', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ZNA', pl_2='VACC', pl_3='001', pl_4='ZNA')

        # .. build the PATIENT_VISIT group ..
        patient_visit = VxuV04PatientVisit()
        patient_visit.pv1 = pv1

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='VACC20230001')
        orc.order_status = 'CM'
        orc.orc_11 = '41827365^Coppens^Marc^^Dr^^^RIZIV'

        # .. build RXA ..
        rxa = RXA()
        rxa.give_sub_id_counter = '0'
        rxa.administration_sub_id_counter = '1'
        rxa.date_time_start_of_administration = '20230915093000'
        rxa.date_time_end_of_administration = '20230915093000'
        rxa.administered_code = CWE(cwe_1='08', cwe_2='Hepatitis B', cwe_3='CVX')
        rxa.administered_amount = '1'
        rxa.administered_units = CWE(cwe_1='mL')
        rxa.administered_dosage_form = CWE(cwe_1='IM')
        rxa.administered_strength = 'LOT2023HB01'
        rxa.administered_strength_units = CWE(cwe_1='20241231')
        rxa.rxa_15 = 'MSD^Merck Sharp and Dohme^MVX'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IM', cwe_2='Intramuscular', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='LD', cwe_2='Left Deltoid', cwe_3='HL70163')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='64994-7', cwe_2='Vaccine funding source', cwe_3='LN')
        obx.obx_5 = 'VXC30^State Other^CDCPHINVS'
        obx.observation_result_status = 'F'

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
        msg.patient_visit = patient_visit
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
    """ Based on live/be/be-chipsoft-hix.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARDIO')
        msh.sending_facility = HD(hd_1='ZNA_CARD')
        msh.receiving_application = HD(hd_1='HIX')
        msh.receiving_facility = HD(hd_1='ZNA')
        msh.date_time_of_message = '20240115140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ZNA_CARD20240115140000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='617283940', cx_4='ZNA', cx_5='PI'), CX(cx_1='78082536214', cx_4='NISS_BE', cx_5='NNNLD')]
        pid.pid_5 = 'WILLEMS^Geert^P^^^Dhr'
        pid.date_time_of_birth = '19780825'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Brederodestraat 19', xad_3='Antwerpen', xad_5='2018', xad_6='BE', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MIDH', pl_2='CARD', pl_3='001', pl_4='ZNA')
        pv1.attending_doctor = XCN(xcn_1='95061248', xcn_2='Van Damme', xcn_3='Inge', xcn_5='Dr', xcn_8='RIZIV')

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
        orc.placer_order_number = EI(ei_1='ECG20240001')
        orc.filler_order_number = EI(ei_1='ECG20240001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ECG20240001')
        obr.filler_order_number = EI(ei_1='ECG20240001')
        obr.universal_service_identifier = CWE(cwe_1='93000', cwe_2='Electrocardiogram', cwe_3='RIZIV_NOM')
        obr.obr_6 = '20240115130000'
        obr.obr_17 = '95061248^Van Damme^Inge^^Dr^^^RIZIV'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='93000', cwe_2='ECG Interpretatie', cwe_3='L')
        obx.obx_5 = 'Sinusritme 72/min. Normale as. Geen ST-elevatie of -depressie. Geen geleidingsstoornissen. Conclusie: normaal ECG.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240115133000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='ECG Rapport', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKEVDRyBSYXBwb3J0KQovQ3JlYXRvciAoWk5BIENhcmRpb2xvZ2llKQovUHJvZHVjZXIgKENoaXBTb2Z0IEhpWCkKL0NyZWF0aW9uRGF0'
            'ZSAoRDoyMDI0MDExNTEzMDAwMCswMScwMCcpCj4+CmVuZG9iagoyIDAgb2JqCjw8IC9UeXBlIC9DYXRhbG9nIC9QYWdlcyAzIDAgUiA+PgplbmRvYmoKMyAwIG9iago8PCAvVHlwZSAv'
            'UGFnZXMgL0tpZHMgWzQgMCBSXSAvQ291bnQgMSA+PgplbmRvYmoKNCAwIG9iago8PCAvVHlwZSAvUGFnZSAvUGFyZW50IDMgMCBSIC9NZWRpYUJveCBbMCAwIDU5NSA4NDJdID4+CmVu'
            'ZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDE3MCAwMDAwMCBuIAowMDAwMDAwMjIxIDAwMDAwIG4gCjAwMDAwMDAyODAg'
            'MDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA1IC9Sb290IDIgMCBSID4+CnN0YXJ0eHJlZgozNjkKJSVFT0YK'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240115133000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='8867-4', cwe_2='Hartfrequentie', cwe_3='LN')
        obx_3.obx_5 = '72'
        obx_3.units = CWE(cwe_1='/min')
        obx_3.reference_range = '60-100'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240115133000'

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
