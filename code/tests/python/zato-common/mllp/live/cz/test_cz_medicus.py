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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, HD, MOC, MSG, PL, PRL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA03Insurance, AdtA03Procedure, AdtA05Insurance, AdtA05NextOfKin, AdtA39Patient, \
    MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, \
    OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12LocationResource, SiuS12Patient, SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, DG1, EVN, IN1, MRG, MSA, MSH, NK1, OBR, OBX, ORC, PD1, PID, PR1, PV1, PV2, RGS, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('cz', 'cz-medicus.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/cz/cz-medicus.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='THOMAYER_NEM')
        msh.receiving_application = HD(hd_1='NIS_THOM')
        msh.receiving_facility = HD(hd_1='THOMAYER_NEM')
        msh.date_time_of_message = '20250308074500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MED20250308074500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250308074500'
        evn.operator_id = XCN(xcn_1='PRIJEM01', xcn_2='Navrátilová', xcn_3='Jaroslava', xcn_6='Bc.')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='9509241095', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='TH13365166', cx_4='THOMAYER', cx_5='MRN')]
        pid.pid_5 = 'ŠTĚPÁN^Václav^Filip^^^'
        pid.date_time_of_birth = '19950924'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Riegrova 98', xad_3='Praha', xad_4='CZ', xad_5='11000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^609936894~^NET^Internet^vaclav.stepan@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '9509241095'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'THOMAYEROVA NEMOCNICE^^10345'
        pd1.pd1_4 = '4713017024^Šťastná^Pavla^Jaroslava^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='ŠTĚPÁNOVÁ', xpn_2='Zdeňka', xpn_3='Klára')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Riegrova 98', xad_3='Praha', xad_4='CZ', xad_5='11000', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^609936894'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT1', pl_2='102', pl_3='A', pl_4='THOMAYER_NEM', pl_8='INT1')
        pv1.attending_doctor = XCN(xcn_1='4713017024', xcn_2='Šťastná', xcn_3='Pavla', xcn_4='Jaroslava', xcn_6='MUDr.', xcn_9='IČP')
        pv1.referring_doctor = XCN(xcn_1='9387731367', xcn_2='Vacek', xcn_3='David', xcn_4='Štěpán', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10023456', xcn_4='THOMENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250308074500')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Fibrilace síní, paroxysmální', cwe_3='I48.0')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='111', cwe_2='VZP', cwe_4='VZP')
        in1.insurance_company_id = CX(cx_1='111')
        in1.insurance_company_name = XON(xon_1='VŠEOBECNÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Orlická 4', xad_3='Praha 3', xad_4='CZ', xad_5='13000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^952222222'
        in1.assignment_of_benefits = CWE(cwe_1='ŠTĚPÁN', cwe_2='Václav', cwe_3='Filip')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19950924'
        in1.notice_of_admission_flag = 'Riegrova 98^^Praha^CZ^11000^CZ'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.pv2 = pv2
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
    """ Based on live/cz/cz-medicus.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='NEM_JIHLAVA')
        msh.receiving_application = HD(hd_1='EDIS_JI')
        msh.receiving_facility = HD(hd_1='NEM_JIHLAVA')
        msh.date_time_of_message = '20250415183000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MED20250415183000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250415183000'
        evn.operator_id = XCN(xcn_1='PRIJEM02', xcn_2='Němcová', xcn_3='Helena', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5412258402', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='JI50558745', cx_4='NEMJI', cx_5='MRN')]
        pid.pid_5 = 'SVOBODA^Bohumil^Dalibor^^^'
        pid.date_time_of_birth = '19541225'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hradební 178', xad_3='Teplice', xad_4='CZ', xad_5='41501', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^634079957'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '5412258402'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'NEMOCNICE JIHLAVA^^20456'
        pd1.pd1_4 = '4324826331^Novotný^Bohumil^Daniel^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='SVOBODOVÁ', xpn_2='Radka', xpn_3='Zuzana')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Hradební 178', xad_3='Teplice', xad_4='CZ', xad_5='41501', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^634079957'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='EDJI', pl_2='ED02', pl_3='A', pl_4='NEM_JIHLAVA', pl_8='EDJI')
        pv1.attending_doctor = XCN(xcn_1='4324826331', xcn_2='Novotný', xcn_3='Bohumil', xcn_4='Daniel', xcn_6='MUDr.', xcn_9='IČP')
        pv1.referring_doctor = XCN(xcn_1='9151150113', xcn_2='Konečný', xcn_3='Roman', xcn_4='Jakub', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='EM', xcn_2='Urgentní příjem', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V20034567', xcn_4='JIENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250415183000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Akutní pankreatitida', cwe_3='K85.9')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='207', cwe_2='OZP', cwe_4='OZP')
        in1.insurance_company_id = CX(cx_1='207')
        in1.insurance_company_name = XON(xon_1='OBOROVÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Roškotova 1225/1', xad_3='Praha 4', xad_4='CZ', xad_5='14000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^261105555'
        in1.assignment_of_benefits = CWE(cwe_1='SVOBODA', cwe_2='Bohumil', cwe_3='Dalibor')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19541225'
        in1.notice_of_admission_flag = 'Hradební 178^^Teplice^CZ^41501^CZ'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.pv2 = pv2
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
    """ Based on live/cz/cz-medicus.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='THOMAYER_NEM')
        msh.receiving_application = HD(hd_1='DISCHARGE')
        msh.receiving_facility = HD(hd_1='THOMAYER_NEM')
        msh.date_time_of_message = '20250315141500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MED20250315141500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250315141500'
        evn.operator_id = XCN(xcn_1='SESTRA01', xcn_2='Čermák', xcn_3='Radek', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='9509241095', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='TH13365166', cx_4='THOMAYER', cx_5='MRN')]
        pid.pid_5 = 'ŠTĚPÁN^Václav^Filip^^^'
        pid.date_time_of_birth = '19950924'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Riegrova 98', xad_3='Praha', xad_4='CZ', xad_5='11000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^609936894'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '9509241095'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT1', pl_2='102', pl_3='A', pl_4='THOMAYER_NEM', pl_8='INT1')
        pv1.attending_doctor = XCN(xcn_1='4713017024', xcn_2='Šťastná', xcn_3='Pavla', xcn_4='Jaroslava', xcn_6='MUDr.', xcn_9='IČP')
        pv1.referring_doctor = XCN(xcn_1='9387731367', xcn_2='Vacek', xcn_3='David', xcn_4='Štěpán', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10023456', xcn_4='THOMENC', xcn_5='VN')
        pv1.visit_number = CX(cx_1='DO', cx_2='Discharged to Home', cx_3='HL70112')
        pv1.prior_temporary_location = PL(pl_1='20250308074500')
        pv1.admit_date_time = '20250315141500'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I48.0', cwe_2='Fibrilace síní, paroxysmální', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250308'
        dg1.diagnosis_type = CWE(cwe_1='A', cwe_2='Admitting', cwe_3='HL70052')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='I48.0', cwe_2='Fibrilace síní, paroxysmální', cwe_3='MKN10')
        dg1_2.diagnosis_date_time = '20250315'
        dg1_2.diagnosis_type = CWE(cwe_1='F', cwe_2='Final', cwe_3='HL70052')

        # .. build PR1 ..
        pr1 = PR1()
        pr1.set_id_pr1 = '1'
        pr1.procedure_code = CNE(cne_1='37.34', cne_2='Katetrizační ablace', cne_3='MKN10PCS')
        pr1.pr1_4 = 'Katetrizační ablace pro fibrilaci síní'
        pr1.procedure_date_time = '20250310080000'
        pr1.pr1_12 = '4713017024^Šťastná^Pavla^Jaroslava^^MUDr.^^^IČP'

        # .. build the PROCEDURE group ..
        procedure = AdtA03Procedure()
        procedure.pr1 = pr1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='111', cwe_2='VZP', cwe_4='VZP')
        in1.insurance_company_id = CX(cx_1='111')
        in1.insurance_company_name = XON(xon_1='VŠEOBECNÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Orlická 4', xad_3='Praha 3', xad_4='CZ', xad_5='13000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^952222222'
        in1.assignment_of_benefits = CWE(cwe_1='ŠTĚPÁN', cwe_2='Václav', cwe_3='Filip')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19950924'
        in1.notice_of_admission_flag = 'Riegrova 98^^Praha^CZ^11000^CZ'

        # .. build the INSURANCE group ..
        insurance = AdtA03Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = [dg1, dg1_2]
        msg.procedure = procedure
        msg.insurance = insurance

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
    """ Based on live/cz/cz-medicus.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='AMB_PARDUBICE')
        msh.receiving_application = HD(hd_1='MPI_PA')
        msh.receiving_facility = HD(hd_1='AMB_PARDUBICE')
        msh.date_time_of_message = '20250520100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MED20250520100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250520100000'
        evn.operator_id = XCN(xcn_1='ADMIN01', xcn_2='Sedláčková', xcn_3='Monika', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='9809021849', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='PA56333005', cx_4='PARDUBICE', cx_5='MRN')]
        pid.pid_5 = 'MAREČEK^Dalibor^Jakub^^^'
        pid.date_time_of_birth = '19980902'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Žižkova 181', xad_3='Liberec', xad_4='CZ', xad_5='46001', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^720313456~^NET^Internet^dalibor.marecek@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '9809021849'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'AMBULANCE PARDUBICE^^30567'
        pd1.pd1_4 = '9664706726^Bouška^Josef^Karel^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='MAREČKOVÁ', xpn_2='Veronika', xpn_3='Lucie')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Žižkova 181', xad_3='Liberec', xad_4='CZ', xad_5='46001', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^720313456'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB1', pl_2='ORD01', pl_3='A', pl_4='AMB_PARDUBICE', pl_8='AMB1')
        pv1.attending_doctor = XCN(xcn_1='9664706726', xcn_2='Bouška', xcn_3='Josef', xcn_4='Karel', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V30045678', xcn_4='PAENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250520100000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='211', cwe_2='ZPMV', cwe_4='ZPMV')
        in1.insurance_company_id = CX(cx_1='211')
        in1.insurance_company_name = XON(xon_1='ZDRAVOTNÍ POJIŠŤOVNA MINISTERSTVA VNITRA')
        in1.insurance_company_address = XAD(xad_1='Kodaňská 46', xad_3='Praha 10', xad_4='CZ', xad_5='10100', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^267205555'
        in1.assignment_of_benefits = CWE(cwe_1='MAREČEK', cwe_2='Dalibor', cwe_3='Jakub')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19980902'
        in1.notice_of_admission_flag = 'Žižkova 181^^Liberec^CZ^46001^CZ'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
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
    """ Based on live/cz/cz-medicus.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='NEM_JIHLAVA')
        msh.receiving_application = HD(hd_1='LABLIS')
        msh.receiving_facility = HD(hd_1='NEM_JIHLAVA')
        msh.date_time_of_message = '20250416060000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MED20250416060000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5412258402', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='JI50558745', cx_4='NEMJI', cx_5='MRN')]
        pid.pid_5 = 'SVOBODA^Bohumil^Dalibor^^^'
        pid.date_time_of_birth = '19541225'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hradební 178', xad_3='Teplice', xad_4='CZ', xad_5='41501', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^634079957'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '5412258402'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT2', pl_2='205', pl_3='A', pl_4='NEM_JIHLAVA', pl_8='INT2')
        pv1.attending_doctor = XCN(xcn_1='4324826331', xcn_2='Novotný', xcn_3='Bohumil', xcn_4='Daniel', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V20034567', xcn_4='JIENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250415183000')

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
        orc.placer_order_number = EI(ei_1='ORD101234', ei_2='MEDICUS')
        orc.filler_order_number = EI(ei_1='LAB201234', ei_2='LABLIS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250416063000^^R'
        orc.date_time_of_order_event = '20250416060000'
        orc.orc_10 = 'KOUSALOVAPE^Pospíšil^Filip^^^'
        orc.order_control_code_reason = CWE(cwe_1='NEM_JIHLAVA')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD101234', ei_2='MEDICUS')
        obr.filler_order_number = EI(ei_1='LAB201234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='80053', cwe_2='Komplexní metabolický panel', cwe_3='CPT')
        obr.obr_16 = '4324826331^Novotný^Bohumil^Daniel^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250416063000'
        obr.result_status = 'NI^No Information^HL70507'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K85.9', cwe_2='Akutní pankreatitida, neurčená', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250415'
        dg1.diagnosis_type = CWE(cwe_1='W', cwe_2='Working', cwe_3='HL70052')

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
    """ Based on live/cz/cz-medicus.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='NEM_JIHLAVA')
        msh.receiving_application = HD(hd_1='NIS_JI')
        msh.receiving_facility = HD(hd_1='NEM_JIHLAVA')
        msh.date_time_of_message = '20250416143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MED20250416143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5412258402', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='JI50558745', cx_4='NEMJI', cx_5='MRN')]
        pid.pid_5 = 'SVOBODA^Bohumil^Dalibor^^^'
        pid.date_time_of_birth = '19541225'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hradební 178', xad_3='Teplice', xad_4='CZ', xad_5='41501', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^634079957'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '5412258402'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT2', pl_2='205', pl_3='A', pl_4='NEM_JIHLAVA', pl_8='INT2')
        pv1.attending_doctor = XCN(xcn_1='4324826331', xcn_2='Novotný', xcn_3='Bohumil', xcn_4='Daniel', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V20034567', xcn_4='JIENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250415183000')

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
        orc.placer_order_number = EI(ei_1='ORD101234', ei_2='MEDICUS')
        orc.filler_order_number = EI(ei_1='LAB201234', ei_2='LABLIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250416063000^^R'
        orc.date_time_of_order_event = '20250416143000'
        orc.orc_18 = 'NEM_JIHLAVA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD101234', ei_2='MEDICUS')
        obr.filler_order_number = EI(ei_1='LAB201234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='80053', cwe_2='Komplexní metabolický panel', cwe_3='CPT')
        obr.observation_date_time = '20250416063500'
        obr.obr_17 = '4324826331^Novotný^Bohumil^Daniel^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250416143000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1798-8', cwe_2='Amyláza v séru', cwe_3='LN')
        obx.obx_5 = '12.5'
        obx.units = CWE(cwe_1='ukat/L')
        obx.reference_range = '0.47-1.67'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250416140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3040-3', cwe_2='Lipáza v séru', cwe_3='LN')
        obx_2.obx_5 = '28.4'
        obx_2.units = CWE(cwe_1='ukat/L')
        obx_2.reference_range = '0.22-1.00'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250416140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Celkový bilirubin', cwe_3='LN')
        obx_3.obx_5 = '35.2'
        obx_3.units = CWE(cwe_1='umol/L')
        obx_3.reference_range = '3.4-17.1'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250416140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT v séru', cwe_3='LN')
        obx_4.obx_5 = '2.85'
        obx_4.units = CWE(cwe_1='ukat/L')
        obx_4.reference_range = '0.10-0.75'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250416140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST v séru', cwe_3='LN')
        obx_5.obx_5 = '3.10'
        obx_5.units = CWE(cwe_1='ukat/L')
        obx_5.reference_range = '0.10-0.72'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250416140000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='4537-7', cwe_2='CRP', cwe_3='LN')
        obx_6.obx_5 = '125.3'
        obx_6.units = CWE(cwe_1='mg/L')
        obx_6.reference_range = '<5.0'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250416140000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocyty', cwe_3='LN')
        obx_7.obx_5 = '15.8'
        obx_7.units = CWE(cwe_1='10*9/L')
        obx_7.reference_range = '4.0-10.0'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250416140000'

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
    """ Based on live/cz/cz-medicus.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='AMB_PARDUBICE')
        msh.receiving_application = HD(hd_1='SCHEDMGR')
        msh.receiving_facility = HD(hd_1='AMB_PARDUBICE')
        msh.date_time_of_message = '20250601080000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MED20250601080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='SCH40045678', ei_2='MEDICUS')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70276')
        sch.appointment_type = CWE(cwe_1='30', cwe_2='min')
        sch.sch_9 = 'MIN^^ISO+'
        sch.placer_contact_person = XCN(xcn_1='RECEPCE', xcn_2='Horák', xcn_3='Adam', xcn_6='')
        sch.placer_contact_phone_number = XTN(xtn_2='PRN', xtn_3='PH', xtn_6='420', xtn_7='466345678')
        sch.filler_contact_address = XAD(xad_1='9664706726', xad_2='Bouška', xad_3='Josef', xad_4='Karel', xad_6='MUDr.', xad_9='IČP')
        sch.filler_contact_location = PL(pl_2='PRN', pl_3='PH', pl_6='420', pl_7='466123456')
        sch.entered_by_person = XCN(xcn_1='AMBULANCE PARDUBICE')
        sch.entered_by_location = PL(pl_1='BOOKED', pl_2='Booked', pl_3='HL70278')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='9809021849', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='PA56333005', cx_4='PARDUBICE', cx_5='MRN')]
        pid.pid_5 = 'MAREČEK^Dalibor^Jakub^^^'
        pid.date_time_of_birth = '19980902'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Žižkova 181', xad_3='Liberec', xad_4='CZ', xad_5='46001', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^720313456'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '9809021849'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB1', pl_2='ORD01', pl_3='A', pl_4='AMB_PARDUBICE', pl_8='AMB1')
        pv1.attending_doctor = XCN(xcn_1='9664706726', xcn_2='Bouška', xcn_3='Josef', xcn_4='Karel', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V30045679', xcn_4='PAENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250610090000')

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
        ais.universal_service_identifier = CWE(cwe_1='VSE01', cwe_2='Preventivní prohlídka', cwe_3='MEDSERV')
        ais.start_date_time_offset = '20250610090000'
        ais.start_date_time_offset_units = CNE(cne_1='30', cne_2='min')
        ais.duration = 'MIN^^ISO+'

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'A'
        ail.location_resource_id = PL(pl_1='AMB1', pl_2='ORD01', pl_3='A', pl_4='AMB_PARDUBICE', pl_8='AMB1')
        ail.location_group = CWE(cwe_1='20250610090000')
        ail.start_date_time = '30^min'
        ail.start_date_time_offset = 'MIN^^ISO+'

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.personnel_resource_id = XCN(xcn_1='9664706726', xcn_2='Bouška', xcn_3='Josef', xcn_4='Karel', xcn_6='MUDr.', xcn_9='IČP')
        aip.resource_group = CWE(cwe_1='20250610090000')
        aip.start_date_time = '30^min'
        aip.start_date_time_offset = 'MIN^^ISO+'

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
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
    """ Based on live/cz/cz-medicus.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='NEM_HB')
        msh.receiving_application = HD(hd_1='MPI_HB')
        msh.receiving_facility = HD(hd_1='NEM_HB')
        msh.date_time_of_message = '20250301090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'MED20250301090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250301090000'
        evn.operator_id = XCN(xcn_1='PRIJEM03', xcn_2='Kolářová', xcn_3='Klára', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='0909263958', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='HB84035894', cx_4='NEMHB', cx_5='MRN')]
        pid.pid_5 = 'ČERMÁK^Václav^Filip^^^'
        pid.date_time_of_birth = '20090926'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Dlouhá 225', xad_3='Praha 5', xad_4='CZ', xad_5='15000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^626206789~^NET^Internet^vaclav.cermak@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '0909263958'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'NEMOCNICE HAVLÍČKŮV BROD^^40678'
        pd1.pd1_4 = '3700773975^Lukášová^Petra^Eva^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='ČERMÁKOVÁ', xpn_2='Iveta', xpn_3='Lenka')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Dlouhá 225', xad_3='Praha 5', xad_4='CZ', xad_5='15000', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^626206789'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB2', pl_2='ORD03', pl_3='A', pl_4='NEM_HB', pl_8='AMB2')
        pv1.attending_doctor = XCN(xcn_1='3700773975', xcn_2='Lukášová', xcn_3='Petra', xcn_4='Eva', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V40056789', xcn_4='HBENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250301090000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='205', cwe_2='ČPZP', cwe_4='CPZP')
        in1.insurance_company_id = CX(cx_1='205')
        in1.insurance_company_name = XON(xon_1='ČESKÁ PRŮMYSLOVÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Jeremenkova 11', xad_3='Ostrava', xad_4='CZ', xad_5='70300', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^596256511'
        in1.assignment_of_benefits = CWE(cwe_1='ČERMÁK', cwe_2='Václav', cwe_3='Filip')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '20090926'
        in1.notice_of_admission_flag = 'Dlouhá 225^^Praha 5^CZ^15000^CZ'

        # .. build the INSURANCE group ..
        insurance = AdtA05Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance

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
    """ Based on live/cz/cz-medicus.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='THOMAYER_NEM')
        msh.receiving_application = HD(hd_1='RADRIS')
        msh.receiving_facility = HD(hd_1='THOMAYER_NEM')
        msh.date_time_of_message = '20250309080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MED20250309080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='9509241095', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='TH13365166', cx_4='THOMAYER', cx_5='MRN')]
        pid.pid_5 = 'ŠTĚPÁN^Václav^Filip^^^'
        pid.date_time_of_birth = '19950924'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Riegrova 98', xad_3='Praha', xad_4='CZ', xad_5='11000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^609936894'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '9509241095'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT1', pl_2='102', pl_3='A', pl_4='THOMAYER_NEM', pl_8='INT1')
        pv1.attending_doctor = XCN(xcn_1='4713017024', xcn_2='Šťastná', xcn_3='Pavla', xcn_4='Jaroslava', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10023456', xcn_4='THOMENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250308074500')

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
        orc.placer_order_number = EI(ei_1='ORD201234', ei_2='MEDICUS')
        orc.filler_order_number = EI(ei_1='RAD301234', ei_2='RADRIS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250309100000^^R'
        orc.date_time_of_order_event = '20250309080000'
        orc.orc_10 = 'PROCHAZKOVARK^Černá^Markéta^^^'
        orc.order_control_code_reason = CWE(cwe_1='THOMAYER_NEM')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD201234', ei_2='MEDICUS')
        obr.filler_order_number = EI(ei_1='RAD301234', ei_2='RADRIS')
        obr.universal_service_identifier = CWE(cwe_1='93350', cwe_2='Transezofageální echokardiografie', cwe_3='CPT')
        obr.obr_16 = '4713017024^Šťastná^Pavla^Jaroslava^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250309100000'
        obr.result_status = 'NI^No Information^HL70507'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I48.0', cwe_2='Fibrilace síní, paroxysmální', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250308'
        dg1.diagnosis_type = CWE(cwe_1='W', cwe_2='Working', cwe_3='HL70052')

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
    """ Based on live/cz/cz-medicus.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='THOMAYER_NEM')
        msh.receiving_application = HD(hd_1='NIS_THOM')
        msh.receiving_facility = HD(hd_1='THOMAYER_NEM')
        msh.date_time_of_message = '20250309150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MED20250309150000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='9509241095', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='TH13365166', cx_4='THOMAYER', cx_5='MRN')]
        pid.pid_5 = 'ŠTĚPÁN^Václav^Filip^^^'
        pid.date_time_of_birth = '19950924'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Riegrova 98', xad_3='Praha', xad_4='CZ', xad_5='11000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^609936894'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '9509241095'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT1', pl_2='102', pl_3='A', pl_4='THOMAYER_NEM', pl_8='INT1')
        pv1.attending_doctor = XCN(xcn_1='4713017024', xcn_2='Šťastná', xcn_3='Pavla', xcn_4='Jaroslava', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10023456', xcn_4='THOMENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250308074500')

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
        orc.placer_order_number = EI(ei_1='ORD201234', ei_2='MEDICUS')
        orc.filler_order_number = EI(ei_1='RAD301234', ei_2='RADRIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250309100000^^R'
        orc.date_time_of_order_event = '20250309150000'
        orc.orc_18 = 'THOMAYER_NEM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD201234', ei_2='MEDICUS')
        obr.filler_order_number = EI(ei_1='RAD301234', ei_2='RADRIS')
        obr.universal_service_identifier = CWE(cwe_1='93350', cwe_2='Transezofageální echokardiografie', cwe_3='CPT')
        obr.observation_date_time = '20250309100500'
        obr.obr_17 = '4713017024^Šťastná^Pavla^Jaroslava^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250309150000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18782-3', cwe_2='Kardiologický nález', cwe_3='LN')
        obx.obx_5 = 'TEE - levá síň 48 mm, bez trombu v oušku, EF LK 55%, mitrální regurgitace gr. I-II, aortální chlopeň bez patologie.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250309140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Laboratorní zpráva', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYXRvcm5pIHpwcmF2YSkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAw'
            'MDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8'
            'PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNDIKJSVFT0YK'
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
    """ Based on live/cz/cz-medicus.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='NEM_JIHLAVA')
        msh.receiving_application = HD(hd_1='NIS_JI')
        msh.receiving_facility = HD(hd_1='NEM_JIHLAVA')
        msh.date_time_of_message = '20250418080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MED20250418080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250418080000'
        evn.operator_id = XCN(xcn_1='SESTRA02', xcn_2='Matoušková', xcn_3='Dana', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5412258402', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='JI50558745', cx_4='NEMJI', cx_5='MRN')]
        pid.pid_5 = 'SVOBODA^Bohumil^Dalibor^^^'
        pid.date_time_of_birth = '19541225'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hradební 178', xad_3='Teplice', xad_4='CZ', xad_5='41501', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^634079957'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '5412258402'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR1', pl_2='308', pl_3='A', pl_4='NEM_JIHLAVA', pl_8='CHIR1')
        pv1.attending_doctor = XCN(xcn_1='9151150113', xcn_2='Konečný', xcn_3='Roman', xcn_4='Jakub', xcn_6='MUDr.', xcn_9='IČP')
        pv1.referring_doctor = XCN(xcn_1='4324826331', xcn_2='Novotný', xcn_3='Bohumil', xcn_4='Daniel', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='CHI', xcn_2='Chirurgie', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='T', cwe_2='Transfer', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V20034567', xcn_4='JIENC', xcn_5='VN')
        pv1.delete_account_indicator = CWE(cwe_1='INT2', cwe_2='205', cwe_3='A', cwe_4='NEM_JIHLAVA', cwe_8='INT2')
        pv1.pv1_40 = '20250418080000'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/cz/cz-medicus.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='NEM_JIHLAVA')
        msh.receiving_application = HD(hd_1='DOCSYS')
        msh.receiving_facility = HD(hd_1='NEM_JIHLAVA')
        msh.date_time_of_message = '20250420100000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MED20250420100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250420100000'
        evn.operator_id = XCN(xcn_1='LEKAR01', xcn_2='Bartošová', xcn_3='Markéta', xcn_6='MUDr.')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5412258402', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='JI50558745', cx_4='NEMJI', cx_5='MRN')]
        pid.pid_5 = 'SVOBODA^Bohumil^Dalibor^^^'
        pid.date_time_of_birth = '19541225'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hradební 178', xad_3='Teplice', xad_4='CZ', xad_5='41501', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^634079957'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '5412258402'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR1', pl_2='308', pl_3='A', pl_4='NEM_JIHLAVA', pl_8='CHIR1')
        pv1.attending_doctor = XCN(xcn_1='9151150113', xcn_2='Konečný', xcn_3='Roman', xcn_4='Jakub', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='CHI', xcn_2='Chirurgie', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V20034567', xcn_4='JIENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250415183000')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='OP', cwe_2='Operační protokol', cwe_3='HL70270')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20250420100000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='9151150113', xcn_2='Konečný', xcn_3='Roman', xcn_4='Jakub', xcn_6='MUDr.', xcn_9='IČP')
        txa.origination_date_time = '20250420100000'
        txa.unique_document_number = EI(ei_1='DOC40056789', ei_2='MEDICUS')
        txa.document_storage_status = 'AV^Available^HL70271'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Laboratorní zpráva', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYXRvcm5pIHpwcmF2YSkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAw'
            'MDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8'
            'PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNDIKJSVFT0YK'
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
    """ Based on live/cz/cz-medicus.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='NEM_HB')
        msh.receiving_application = HD(hd_1='MPI_HB')
        msh.receiving_facility = HD(hd_1='NEM_HB')
        msh.date_time_of_message = '20250401140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'MED20250401140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250401140000'
        evn.operator_id = XCN(xcn_1='ADMIN02', xcn_2='Marečková', xcn_3='Tereza', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='0909263958', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='HB84035894', cx_4='NEMHB', cx_5='MRN')]
        pid.pid_5 = 'ČERMÁK^Václav^Filip^^^'
        pid.date_time_of_birth = '20090926'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Dlouhá 225', xad_3='Praha 5', xad_4='CZ', xad_5='15000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^626206789~^NET^Internet^vaclav.cermak@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '0909263958'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'NEMOCNICE HAVLÍČKŮV BROD^^40678'
        pd1.pd1_4 = '3700773975^Lukášová^Petra^Eva^^MUDr.^^^IČP'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB2', pl_2='ORD03', pl_3='A', pl_4='NEM_HB', pl_8='AMB2')
        pv1.attending_doctor = XCN(xcn_1='3700773975', xcn_2='Lukášová', xcn_3='Petra', xcn_4='Eva', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V40056789', xcn_4='HBENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250401140000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='205', cwe_2='ČPZP', cwe_4='CPZP')
        in1.insurance_company_id = CX(cx_1='205')
        in1.insurance_company_name = XON(xon_1='ČESKÁ PRŮMYSLOVÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Jeremenkova 11', xad_3='Ostrava', xad_4='CZ', xad_5='70300', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^596256511'
        in1.assignment_of_benefits = CWE(cwe_1='ČERMÁK', cwe_2='Václav', cwe_3='Filip')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '20090926'
        in1.notice_of_admission_flag = 'Dlouhá 225^^Praha 5^CZ^15000^CZ'

        # .. build the INSURANCE group ..
        insurance = AdtA05Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.pv1 = pv1
        msg.insurance = insurance

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
    """ Based on live/cz/cz-medicus.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NIS_THOM')
        msh.sending_facility = HD(hd_1='THOMAYER_NEM')
        msh.receiving_application = HD(hd_1='MEDICUS')
        msh.receiving_facility = HD(hd_1='THOMAYER_NEM')
        msh.date_time_of_message = '20250308074505'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'NIS20250308074505001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MED20250308074500001'
        msa.expected_sequence_number = '0'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/cz/cz-medicus.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='THOMAYER_NEM')
        msh.receiving_application = HD(hd_1='MPI_THOM')
        msh.receiving_facility = HD(hd_1='THOMAYER_NEM')
        msh.date_time_of_message = '20250505110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'MED20250505110000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250505110000'
        evn.operator_id = XCN(xcn_1='ADMIN03', xcn_2='Štěpán', xcn_3='David', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='0905172262', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='TH68225182', cx_4='THOMAYER', cx_5='MRN')]
        pid.pid_5 = 'HORÁK^Ondřej^Cyril^^^'
        pid.date_time_of_birth = '20090517'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kollárova 199', xad_3='Most', xad_4='CZ', xad_5='43401', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^615612816'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '0905172262'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='TH53184598', cx_4='THOMAYER', cx_5='MRN')
        mrg.mrg_2 = '9509241095'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB3', pl_2='ORD05', pl_3='A', pl_4='THOMAYER_NEM', pl_8='AMB3')
        pv1.attending_doctor = XCN(xcn_1='9561699699', xcn_2='Urbanová', xcn_3='Kateřina', xcn_4='Renata', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V50067890', xcn_4='THOMENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250505110000')

        # .. build the PATIENT group ..
        patient = AdtA39Patient()
        patient.pid = pid
        patient.mrg = mrg
        patient.pv1 = pv1

        # .. assemble the full message ..
        msg = ADT_A39()
        msg.msh = msh
        msg.evn = evn
        msg.patient = patient

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
    """ Based on live/cz/cz-medicus.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='NEM_HB')
        msh.receiving_application = HD(hd_1='NIS_HB')
        msh.receiving_facility = HD(hd_1='NEM_HB')
        msh.date_time_of_message = '20250402150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MED20250402150000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='0909263958', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='HB84035894', cx_4='NEMHB', cx_5='MRN')]
        pid.pid_5 = 'ČERMÁK^Václav^Filip^^^'
        pid.date_time_of_birth = '20090926'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Dlouhá 225', xad_3='Praha 5', xad_4='CZ', xad_5='15000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^626206789'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '0909263958'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB2', pl_2='ORD03', pl_3='A', pl_4='NEM_HB', pl_8='AMB2')
        pv1.attending_doctor = XCN(xcn_1='3700773975', xcn_2='Lukášová', xcn_3='Petra', xcn_4='Eva', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V40056789', xcn_4='HBENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250401140000')

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
        orc.placer_order_number = EI(ei_1='ORD301234', ei_2='MEDICUS')
        orc.filler_order_number = EI(ei_1='LAB401234', ei_2='LABLIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250401143000^^R'
        orc.date_time_of_order_event = '20250402150000'
        orc.orc_18 = 'NEM_HB'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD301234', ei_2='MEDICUS')
        obr.filler_order_number = EI(ei_1='LAB401234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='85025', cwe_2='Krevní obraz kompletní', cwe_3='CPT')
        obr.observation_date_time = '20250401143500'
        obr.obr_17 = '3700773975^Lukášová^Petra^Eva^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250402150000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx.obx_5 = '155'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '130-170'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250402140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematokrit', cwe_3='LN')
        obx_2.obx_5 = '0.46'
        obx_2.units = CWE(cwe_1='L/L')
        obx_2.reference_range = '0.39-0.50'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250402140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocyty', cwe_3='LN')
        obx_3.obx_5 = '6.8'
        obx_3.units = CWE(cwe_1='10*9/L')
        obx_3.reference_range = '4.0-10.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250402140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='777-3', cwe_2='Trombocyty', cwe_3='LN')
        obx_4.obx_5 = '245'
        obx_4.units = CWE(cwe_1='10*9/L')
        obx_4.reference_range = '150-400'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250402140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erytrocyty', cwe_3='LN')
        obx_5.obx_5 = '5.10'
        obx_5.units = CWE(cwe_1='10*12/L')
        obx_5.reference_range = '4.2-5.8'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250402140000'

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
    """ Based on live/cz/cz-medicus.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='AMB_PARDUBICE')
        msh.receiving_application = HD(hd_1='RADRIS')
        msh.receiving_facility = HD(hd_1='AMB_PARDUBICE')
        msh.date_time_of_message = '20250525090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MED20250525090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='7311050819', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='PA69414157', cx_4='PARDUBICE', cx_5='MRN')]
        pid.pid_5 = 'VLČEK^Štěpán^Stanislav^^^'
        pid.date_time_of_birth = '19731105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bezručova 152', xad_3='Kladno', xad_4='CZ', xad_5='27201', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^796959536'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '7311050819'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB4', pl_2='ORD07', pl_3='A', pl_4='AMB_PARDUBICE', pl_8='AMB4')
        pv1.attending_doctor = XCN(xcn_1='9664706726', xcn_2='Bouška', xcn_3='Josef', xcn_4='Karel', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V60078901', xcn_4='PAENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250525090000')

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
        orc.placer_order_number = EI(ei_1='ORD401234', ei_2='MEDICUS')
        orc.filler_order_number = EI(ei_1='RAD501234', ei_2='RADRIS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250525100000^^R'
        orc.date_time_of_order_event = '20250525090000'
        orc.orc_10 = 'MARESOVAHA^Poláková^Marie^^^'
        orc.order_control_code_reason = CWE(cwe_1='AMB_PARDUBICE')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD401234', ei_2='MEDICUS')
        obr.filler_order_number = EI(ei_1='RAD501234', ei_2='RADRIS')
        obr.universal_service_identifier = CWE(cwe_1='76700', cwe_2='UZ břicha kompletní', cwe_3='CPT')
        obr.obr_16 = '9664706726^Bouška^Josef^Karel^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250525100000'
        obr.result_status = 'NI^No Information^HL70507'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K76.0', cwe_2='Steatóza jater', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250525'
        dg1.diagnosis_type = CWE(cwe_1='W', cwe_2='Working', cwe_3='HL70052')

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
    """ Based on live/cz/cz-medicus.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='THOMAYER_NEM')
        msh.receiving_application = HD(hd_1='NIS_THOM')
        msh.receiving_facility = HD(hd_1='THOMAYER_NEM')
        msh.date_time_of_message = '20250315100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MED20250315100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='0905172262', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='TH68225182', cx_4='THOMAYER', cx_5='MRN')]
        pid.pid_5 = 'HORÁK^Ondřej^Cyril^^^'
        pid.date_time_of_birth = '20090517'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kollárova 199', xad_3='Most', xad_4='CZ', xad_5='43401', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^615612816'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '0905172262'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HEP1', pl_2='HEP01', pl_3='A', pl_4='THOMAYER_NEM', pl_8='HEP1')
        pv1.attending_doctor = XCN(xcn_1='2789186071', xcn_2='Boušková', xcn_3='Alena', xcn_4='Marie', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='HEP', xcn_2='Hepatologie', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V50067890', xcn_4='THOMENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250314080000')

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
        orc.placer_order_number = EI(ei_1='ORD501234', ei_2='MEDICUS')
        orc.filler_order_number = EI(ei_1='LAB601234', ei_2='LABLIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250314083000^^R'
        orc.date_time_of_order_event = '20250315100000'
        orc.orc_18 = 'THOMAYER_NEM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD501234', ei_2='MEDICUS')
        obr.filler_order_number = EI(ei_1='LAB601234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='80076', cwe_2='Jaterní panel', cwe_3='CPT')
        obr.observation_date_time = '20250314083500'
        obr.obr_17 = '2789186071^Boušková^Alena^Marie^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250315100000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT v séru', cwe_3='LN')
        obx.obx_5 = '1.85'
        obx.units = CWE(cwe_1='ukat/L')
        obx.reference_range = '0.10-0.75'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250315090000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST v séru', cwe_3='LN')
        obx_2.obx_5 = '1.42'
        obx_2.units = CWE(cwe_1='ukat/L')
        obx_2.reference_range = '0.10-0.72'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250315090000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6768-6', cwe_2='ALP v séru', cwe_3='LN')
        obx_3.obx_5 = '2.85'
        obx_3.units = CWE(cwe_1='ukat/L')
        obx_3.reference_range = '0.67-2.15'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250315090000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2324-2', cwe_2='GGT v séru', cwe_3='LN')
        obx_4.obx_5 = '3.20'
        obx_4.units = CWE(cwe_1='ukat/L')
        obx_4.reference_range = '0.17-1.19'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250315090000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Celkový bilirubin', cwe_3='LN')
        obx_5.obx_5 = '28.5'
        obx_5.units = CWE(cwe_1='umol/L')
        obx_5.reference_range = '3.4-17.1'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250315090000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1968-7', cwe_2='Přímý bilirubin', cwe_3='LN')
        obx_6.obx_5 = '12.3'
        obx_6.units = CWE(cwe_1='umol/L')
        obx_6.reference_range = '<5.1'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250315090000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2862-1', cwe_2='Albumin v séru', cwe_3='LN')
        obx_7.obx_5 = '32'
        obx_7.units = CWE(cwe_1='g/L')
        obx_7.reference_range = '35-52'
        obx_7.interpretation_codes = CWE(cwe_1='L')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250315090000'

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
    """ Based on live/cz/cz-medicus.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='NEM_HB')
        msh.receiving_application = HD(hd_1='REGSYS')
        msh.receiving_facility = HD(hd_1='NEM_HB')
        msh.date_time_of_message = '20250610080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MED20250610080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250610080000'
        evn.operator_id = XCN(xcn_1='PRIJEM04', xcn_2='Tomková', xcn_3='Radka', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='0504079412', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='HB71922524', cx_4='NEMHB', cx_5='MRN')]
        pid.pid_5 = 'SVOBODA^David^Michal^^^'
        pid.date_time_of_birth = '20050407'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Smetanova 65', xad_3='Hradec Králové', xad_4='CZ', xad_5='50002', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^737737463~^NET^Internet^david.svoboda@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '0504079412'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'NEMOCNICE HAVLÍČKŮV BROD^^40678'
        pd1.pd1_4 = '3700773975^Lukášová^Petra^Eva^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='SVOBODOVÁ', xpn_2='Radka', xpn_3='Eliška')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Smetanova 65', xad_3='Hradec Králové', xad_4='CZ', xad_5='50002', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^737737463'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB5', pl_2='ORD09', pl_3='A', pl_4='NEM_HB', pl_8='AMB5')
        pv1.attending_doctor = XCN(xcn_1='3700773975', xcn_2='Lukášová', xcn_3='Petra', xcn_4='Eva', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='ORT', xcn_2='Ortopedie', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80090123', xcn_4='HBENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250610080000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='201', cwe_2='VoZP', cwe_4='VOZP')
        in1.insurance_company_id = CX(cx_1='201')
        in1.insurance_company_name = XON(xon_1='VOJENSKÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Drahobejlova 1404/4', xad_3='Praha 9', xad_4='CZ', xad_5='19000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^284091111'
        in1.assignment_of_benefits = CWE(cwe_1='SVOBODA', cwe_2='David', cwe_3='Michal')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '20050407'
        in1.notice_of_admission_flag = 'Smetanova 65^^Hradec Králové^CZ^50002^CZ'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance

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
    """ Based on live/cz/cz-medicus.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICUS')
        msh.sending_facility = HD(hd_1='NEM_JIHLAVA')
        msh.receiving_application = HD(hd_1='NIS_JI')
        msh.receiving_facility = HD(hd_1='NEM_JIHLAVA')
        msh.date_time_of_message = '20250425160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MED20250425160000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5405198334', cx_4='MEDICUS', cx_5='RC'), CX(cx_1='JI41855547', cx_4='NEMJI', cx_5='MRN')]
        pid.pid_5 = 'BARTOŠ^Matěj^Stanislav^^^'
        pid.date_time_of_birth = '19540519'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vinohradská 127', xad_3='Liberec', xad_4='CZ', xad_5='46001', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^683986530'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5405198334'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR1', pl_2='310', pl_3='A', pl_4='NEM_JIHLAVA', pl_8='CHIR1')
        pv1.attending_doctor = XCN(xcn_1='9151150113', xcn_2='Konečný', xcn_3='Roman', xcn_4='Jakub', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='CHI', xcn_2='Chirurgie', xcn_3='MEDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90101234', xcn_4='JIENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250420090000')

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
        orc.placer_order_number = EI(ei_1='ORD601234', ei_2='MEDICUS')
        orc.filler_order_number = EI(ei_1='MIC701234', ei_2='LABLIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250421100000^^R'
        orc.date_time_of_order_event = '20250425160000'
        orc.orc_18 = 'NEM_JIHLAVA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD601234', ei_2='MEDICUS')
        obr.filler_order_number = EI(ei_1='MIC701234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='87070', cwe_2='Kultivace z rány', cwe_3='CPT')
        obr.observation_date_time = '20250421100500'
        obr.obr_17 = '9151150113^Konečný^Roman^Jakub^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250425160000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='Bakterie identifikované', cwe_3='LN')
        obx.obx_5 = 'Pseudomonas aeruginosa'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250425150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Citlivost na antibiotika', cwe_3='LN')
        obx_2.obx_5 = 'Piperacilin/tazobaktam: S, Ceftazidim: S, Meropenem: S, Ciprofloxacin: R, Gentamicin: S, Amikacin: S, Kolistin: S'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250425150000'

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
