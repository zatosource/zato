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
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, DG1, EVN, IN1, MRG, MSA, MSH, NK1, OBR, OBX, ORC, PD1, PID, PR1, PV1, PV2, RGS, RXO, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('cz', 'cz-fons-akord.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/cz/cz-fons-akord.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='POLIKL_BUDEJOVICKA')
        msh.receiving_application = HD(hd_1='NISZDR')
        msh.receiving_facility = HD(hd_1='POLIKL_BUDEJOVICKA')
        msh.date_time_of_message = '20250310083012'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'FA20250310083012001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250310083000'
        evn.operator_id = XCN(xcn_1='NOVAKOVA', xcn_2='Matoušková', xcn_3='Gabriela', xcn_6='Bc.')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='9508093049', cx_4='FONS', cx_5='RC'), CX(cx_1='PB29639702', cx_4='POLIKL', cx_5='MRN')]
        pid.pid_5 = 'POLÁK^Matěj^Vojtěch^^^Ing.'
        pid.date_time_of_birth = '19950809'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Žitavská 43', xad_3='Praha 4', xad_4='CZ', xad_5='14000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^768955352~^NET^Internet^matej.polak@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '9508093049'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'POLIKLINIKA BUDĚJOVICKÁ^^12345'
        pd1.pd1_4 = '3569850898^Kučerová^Eliška^Marie^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='POLÁKOVÁ', xpn_2='Iveta', xpn_3='Jana')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Žitavská 43', xad_3='Praha 4', xad_4='CZ', xad_5='14000', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^768955352'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB1', pl_2='ORD01', pl_3='A', pl_4='POLIKL_BUDEJOVICKA', pl_8='AMB1')
        pv1.attending_doctor = XCN(xcn_1='3569850898', xcn_2='Kučerová', xcn_3='Eliška', xcn_4='Marie', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10012345', xcn_4='FONSENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250310083000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='111', cwe_2='VZP', cwe_4='VZP')
        in1.insurance_company_id = CX(cx_1='111')
        in1.insurance_company_name = XON(xon_1='VŠEOBECNÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Orlická 4', xad_3='Praha 3', xad_4='CZ', xad_5='13000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^952222222'
        in1.assignment_of_benefits = CWE(cwe_1='POLÁK', cwe_2='Matěj', cwe_3='Vojtěch')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19950809'
        in1.notice_of_admission_flag = 'Žitavská 43^^Praha 4^CZ^14000^CZ'

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
    """ Based on live/cz/cz-fons-akord.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='FN_MOTOL')
        msh.receiving_application = HD(hd_1='NIS_MOTOL')
        msh.receiving_facility = HD(hd_1='FN_MOTOL')
        msh.date_time_of_message = '20250415091530'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'FA20250415091530001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250415091500'
        evn.operator_id = XCN(xcn_1='DVORAKOVA', xcn_2='Černá', xcn_3='Monika', xcn_6='Mgr.')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5304209261', cx_4='FONS', cx_5='RC'), CX(cx_1='MOT66102185', cx_4='MOTOL', cx_5='MRN')]
        pid.pid_5 = 'HRUŠKA^Vladimír^Matěj^^^'
        pid.date_time_of_birth = '19530420'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Národní třída 54', xad_3='Hradec Králové', xad_4='CZ', xad_5='50002', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^657353793'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5304209261'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'FN MOTOL^^67890'
        pd1.pd1_4 = '0026351455^Konečný^Michal^Vojtěch^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='HRUŠKOVÁ', xpn_2='Iveta', xpn_3='Zuzana')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Národní třída 54', xad_3='Hradec Králové', xad_4='CZ', xad_5='50002', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^657353793'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR2', pl_2='201', pl_3='A', pl_4='FN_MOTOL', pl_8='CHIR2')
        pv1.attending_doctor = XCN(xcn_1='0026351455', xcn_2='Konečný', xcn_3='Michal', xcn_4='Vojtěch', xcn_6='MUDr.', xcn_9='IČP')
        pv1.referring_doctor = XCN(xcn_1='4534678627', xcn_2='Marek', xcn_3='Rostislav', xcn_4='Lukáš', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='CHI', xcn_2='Chirurgie', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V20034567', xcn_4='MOTOLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250415091500')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Akutní apendicitida', cwe_3='K35.80')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='111', cwe_2='VZP', cwe_4='VZP')
        in1.insurance_company_id = CX(cx_1='111')
        in1.insurance_company_name = XON(xon_1='VŠEOBECNÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Orlická 4', xad_3='Praha 3', xad_4='CZ', xad_5='13000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^952222222'
        in1.assignment_of_benefits = CWE(cwe_1='HRUŠKA', cwe_2='Vladimír', cwe_3='Matěj')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19530420'
        in1.notice_of_admission_flag = 'Národní třída 54^^Hradec Králové^CZ^50002^CZ'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build IN1 ..
        in1_2 = IN1()
        in1_2.set_id_in1 = '2'
        in1_2.health_plan_id = CWE(cwe_1='205', cwe_2='ČPZP', cwe_4='CPZP')
        in1_2.insurance_company_id = CX(cx_1='205')
        in1_2.insurance_company_name = XON(xon_1='ČESKÁ PRŮMYSLOVÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1_2.insurance_company_address = XAD(xad_1='Jeremenkova 11', xad_3='Ostrava', xad_4='CZ', xad_5='70300', xad_6='CZ')
        in1_2.in1_6 = '^PRN^PH^^^420^596256511'

        # .. build the INSURANCE group ..
        insurance_2 = AdtA01Insurance()
        insurance_2.in1 = in1_2

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.insurance = [insurance, insurance_2]

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
    """ Based on live/cz/cz-fons-akord.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='NNH_PRAHA')
        msh.receiving_application = HD(hd_1='DISCHARGE')
        msh.receiving_facility = HD(hd_1='NNH_PRAHA')
        msh.date_time_of_message = '20250322163045'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'FA20250322163045001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250322163000'
        evn.operator_id = XCN(xcn_1='BARTOSOVA', xcn_2='Marek', xcn_3='Vladimír', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='7602060701', cx_4='FONS', cx_5='RC'), CX(cx_1='NNH18998495', cx_4='NNH', cx_5='MRN')]
        pid.pid_5 = 'SEDLÁČEK^Tomáš^Radek^^^'
        pid.date_time_of_birth = '19760206'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Smilova 3', xad_3='Brno', xad_4='CZ', xad_5='60300', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^677648653'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='D', cwe_2='Divorced', cwe_3='HL70002')
        pid.pid_19 = '7602060701'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='KARD3', pl_2='312', pl_3='B', pl_4='NNH_PRAHA', pl_8='KARD3')
        pv1.attending_doctor = XCN(xcn_1='6941110095', xcn_2='Pavlíková', xcn_3='Pavla', xcn_4='Zuzana', xcn_6='MUDr.', xcn_9='IČP')
        pv1.referring_doctor = XCN(xcn_1='6264628072', xcn_2='Doležalová', xcn_3='Věra', xcn_4='Tereza', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='KAR', xcn_2='Kardiologie', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V30045678', xcn_4='NNHENC', xcn_5='VN')
        pv1.visit_number = CX(cx_1='DO', cx_2='Discharged to Home', cx_3='HL70112')
        pv1.prior_temporary_location = PL(pl_1='20250318090000')
        pv1.admit_date_time = '20250322163000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.1', cwe_2='Aterosklerotická choroba srdeční', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250318'
        dg1.diagnosis_type = CWE(cwe_1='A', cwe_2='Admitting', cwe_3='HL70052')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='Z95.1', cwe_2='Přítomnost aortokoronárního bypassu', cwe_3='MKN10')
        dg1_2.diagnosis_date_time = '20250322'
        dg1_2.diagnosis_type = CWE(cwe_1='F', cwe_2='Final', cwe_3='HL70052')

        # .. build PR1 ..
        pr1 = PR1()
        pr1.set_id_pr1 = '1'
        pr1.procedure_code = CNE(cne_1='36.15', cne_2='Jednoduchý aortokoronární bypass', cne_3='MKN10PCS')
        pr1.pr1_4 = 'Aortokoronární bypass'
        pr1.procedure_date_time = '20250319080000'
        pr1.pr1_12 = '6941110095^Pavlíková^Pavla^Zuzana^^MUDr.^^^IČP'

        # .. build the PROCEDURE group ..
        procedure = AdtA03Procedure()
        procedure.pr1 = pr1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='207', cwe_2='OZP', cwe_4='OZP')
        in1.insurance_company_id = CX(cx_1='207')
        in1.insurance_company_name = XON(xon_1='OBOROVÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Roškotova 1225/1', xad_3='Praha 4', xad_4='CZ', xad_5='14000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^261105555'
        in1.assignment_of_benefits = CWE(cwe_1='SEDLÁČEK', cwe_2='Tomáš', cwe_3='Radek')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19760206'
        in1.notice_of_admission_flag = 'Smilova 3^^Brno^CZ^60300^CZ'

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
    """ Based on live/cz/cz-fons-akord.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='AMB_PLZEN')
        msh.receiving_application = HD(hd_1='NIS_PLZEN')
        msh.receiving_facility = HD(hd_1='AMB_PLZEN')
        msh.date_time_of_message = '20250501141200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'FA20250501141200001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250501141200'
        evn.operator_id = XCN(xcn_1='TOMANOVA', xcn_2='Horáková', xcn_3='Gabriela', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='4306107574', cx_4='FONS', cx_5='RC'), CX(cx_1='PL44374841', cx_4='PLZEN', cx_5='MRN')]
        pid.pid_5 = 'BARTOŠ^Miroslav^Bohumil^^^'
        pid.date_time_of_birth = '19430610'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hradební 218', xad_3='Praha 5', xad_4='CZ', xad_5='15000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^762607680~^NET^Internet^miroslav.bartos@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '4306107574'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'AMBULANCE PLZEŇ^^34567'
        pd1.pd1_4 = '8735717789^Křížková^Marie^Pavla^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='BARTOŠOVÁ', xpn_2='Tereza', xpn_3='Klára')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Hradební 218', xad_3='Praha 5', xad_4='CZ', xad_5='15000', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^762607680'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB2', pl_2='ORD03', pl_3='A', pl_4='AMB_PLZEN', pl_8='AMB2')
        pv1.attending_doctor = XCN(xcn_1='8735717789', xcn_2='Křížková', xcn_3='Marie', xcn_4='Pavla', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V40056789', xcn_4='PLZENENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250501141200')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='211', cwe_2='ZPMV', cwe_4='ZPMV')
        in1.insurance_company_id = CX(cx_1='211')
        in1.insurance_company_name = XON(xon_1='ZDRAVOTNÍ POJIŠŤOVNA MINISTERSTVA VNITRA')
        in1.insurance_company_address = XAD(xad_1='Kodaňská 46', xad_3='Praha 10', xad_4='CZ', xad_5='10100', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^267205555'
        in1.assignment_of_benefits = CWE(cwe_1='BARTOŠ', cwe_2='Miroslav', cwe_3='Bohumil')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19430610'
        in1.notice_of_admission_flag = 'Hradební 218^^Praha 5^CZ^15000^CZ'

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
    """ Based on live/cz/cz-fons-akord.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='POLIKL_LIBEREC')
        msh.receiving_application = HD(hd_1='LABLIS')
        msh.receiving_facility = HD(hd_1='POLIKL_LIBEREC')
        msh.date_time_of_message = '20250218094530'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'FA20250218094530001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5112205741', cx_4='FONS', cx_5='RC'), CX(cx_1='LB58941418', cx_4='LIBEREC', cx_5='MRN')]
        pid.pid_5 = 'HOLUB^Václav^Bohumil^^^'
        pid.date_time_of_birth = '19511220'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vinohradská 215', xad_3='Havířov', xad_4='CZ', xad_5='73601', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^731015457'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '5112205741'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB3', pl_2='ORD05', pl_3='A', pl_4='POLIKL_LIBEREC', pl_8='AMB3')
        pv1.attending_doctor = XCN(xcn_1='9719926324', xcn_2='Konečný', xcn_3='Vojtěch', xcn_4='Pavel', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V50067890', xcn_4='LIBENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250218094500')

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
        orc.placer_order_number = EI(ei_1='ORD601234', ei_2='FONS')
        orc.filler_order_number = EI(ei_1='LAB801234', ei_2='LABLIS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250218100000^^R'
        orc.date_time_of_order_event = '20250218094530'
        orc.orc_10 = 'NOVAKJ^Holub^Roman^^^'
        orc.order_control_code_reason = CWE(cwe_1='POLIKL_LIBEREC')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD601234', ei_2='FONS')
        obr.filler_order_number = EI(ei_1='LAB801234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='80053', cwe_2='Komplexní metabolický panel', cwe_3='CPT')
        obr.obr_16 = '9719926324^Konečný^Vojtěch^Pavel^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250218100000'
        obr.result_status = 'NI^No Information^HL70507'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E11.9', cwe_2='Diabetes mellitus 2. typu bez komplikací', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250218'
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
    """ Based on live/cz/cz-fons-akord.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='NEM_LIBEREC')
        msh.receiving_application = HD(hd_1='AMBSYS')
        msh.receiving_facility = HD(hd_1='NEM_LIBEREC')
        msh.date_time_of_message = '20250219152300'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'FA20250219152300001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5112205741', cx_4='FONS', cx_5='RC'), CX(cx_1='LB58941418', cx_4='LIBEREC', cx_5='MRN')]
        pid.pid_5 = 'HOLUB^Václav^Bohumil^^^'
        pid.date_time_of_birth = '19511220'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vinohradská 215', xad_3='Havířov', xad_4='CZ', xad_5='73601', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^731015457'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '5112205741'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB3', pl_2='ORD05', pl_3='A', pl_4='NEM_LIBEREC', pl_8='AMB3')
        pv1.attending_doctor = XCN(xcn_1='9719926324', xcn_2='Konečný', xcn_3='Vojtěch', xcn_4='Pavel', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V50067890', xcn_4='LIBENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250218094500')

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
        orc.placer_order_number = EI(ei_1='ORD601234', ei_2='FONS')
        orc.filler_order_number = EI(ei_1='LAB801234', ei_2='LABLIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250218100000^^R'
        orc.date_time_of_order_event = '20250219152300'
        orc.orc_18 = 'NEM_LIBEREC'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD601234', ei_2='FONS')
        obr.filler_order_number = EI(ei_1='LAB801234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='80053', cwe_2='Komplexní metabolický panel', cwe_3='CPT')
        obr.observation_date_time = '20250218100500'
        obr.obr_17 = '9719926324^Konečný^Vojtěch^Pavel^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250219152300')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glukóza v séru', cwe_3='LN')
        obx.obx_5 = '6.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.9-5.8'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250219150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Kreatinin v séru', cwe_3='LN')
        obx_2.obx_5 = '92'
        obx_2.units = CWE(cwe_1='umol/L')
        obx_2.reference_range = '62-106'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250219150000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea v séru', cwe_3='LN')
        obx_3.obx_5 = '5.2'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.8-7.2'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250219150000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodík v séru', cwe_3='LN')
        obx_4.obx_5 = '141'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250219150000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Draslík v séru', cwe_3='LN')
        obx_5.obx_5 = '4.3'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250219150000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobin A1c', cwe_3='LN')
        obx_6.obx_5 = '7.2'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '4.0-5.6'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250219150000'

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
    """ Based on live/cz/cz-fons-akord.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='FN_MOTOL')
        msh.receiving_application = HD(hd_1='PATHSYS')
        msh.receiving_facility = HD(hd_1='FN_MOTOL')
        msh.date_time_of_message = '20250328110045'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'FA20250328110045001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5304209261', cx_4='FONS', cx_5='RC'), CX(cx_1='MOT66102185', cx_4='MOTOL', cx_5='MRN')]
        pid.pid_5 = 'HRUŠKA^Vladimír^Matěj^^^'
        pid.date_time_of_birth = '19530420'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Národní třída 54', xad_3='Hradec Králové', xad_4='CZ', xad_5='50002', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^657353793'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5304209261'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PAT1', pl_2='101', pl_3='A', pl_4='FN_MOTOL', pl_8='PAT1')
        pv1.attending_doctor = XCN(xcn_1='6194845854', xcn_2='Němec', xcn_3='Vlastimil', xcn_4='Vojtěch', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='PAT', xcn_2='Patologie', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V20034568', xcn_4='MOTOLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250326090000')

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
        orc.placer_order_number = EI(ei_1='ORD701234', ei_2='FONS')
        orc.filler_order_number = EI(ei_1='PAT901234', ei_2='PATHSYS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250326100000^^R'
        orc.date_time_of_order_event = '20250328110045'
        orc.orc_18 = 'FN_MOTOL'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701234', ei_2='FONS')
        obr.filler_order_number = EI(ei_1='PAT901234', ei_2='PATHSYS')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='Histopatologické vyšetření', cwe_3='CPT')
        obr.observation_date_time = '20250326100500'
        obr.obr_17 = '6194845854^Němec^Vlastimil^Vojtěch^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250328110045')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Nález patologie', cwe_3='LN')
        obx.obx_5 = 'Benigní leiomyom děložní, bez známek malignity.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250328100000'

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
    """ Based on live/cz/cz-fons-akord.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='AMB_BRNO')
        msh.receiving_application = HD(hd_1='SCHEDMGR')
        msh.receiving_facility = HD(hd_1='AMB_BRNO')
        msh.date_time_of_message = '20250612080015'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'FA20250612080015001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='SCH10012345', ei_2='FONS')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70276')
        sch.appointment_type = CWE(cwe_1='30', cwe_2='min')
        sch.sch_9 = 'MIN^^ISO+'
        sch.placer_contact_person = XCN(xcn_1='NOVOTNA', xcn_2='Beneš', xcn_3='Roman', xcn_6='')
        sch.placer_contact_phone_number = XTN(xtn_2='PRN', xtn_3='PH', xtn_6='420', xtn_7='602345678')
        sch.filler_contact_address = XAD(xad_1='3569850898', xad_2='Kučerová', xad_3='Eliška', xad_4='Marie', xad_6='MUDr.', xad_9='IČP')
        sch.filler_contact_location = PL(pl_2='PRN', pl_3='PH', pl_6='420', pl_7='541234567')
        sch.entered_by_person = XCN(xcn_1='AMBULANCE BRNO')
        sch.entered_by_location = PL(pl_1='BOOKED', pl_2='Booked', pl_3='HL70278')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5004114802', cx_4='FONS', cx_5='RC'), CX(cx_1='BR41659311', cx_4='BRNO', cx_5='MRN')]
        pid.pid_5 = 'NOVÁK^Rostislav^David^^^'
        pid.date_time_of_birth = '19500411'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gočárova 82', xad_3='Plzeň', xad_4='CZ', xad_5='30100', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^757835192'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5004114802'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB4', pl_2='ORD07', pl_3='A', pl_4='AMB_BRNO', pl_8='AMB4')
        pv1.attending_doctor = XCN(xcn_1='3569850898', xcn_2='Kučerová', xcn_3='Eliška', xcn_4='Marie', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V60078901', xcn_4='BRNOENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250612090000')

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
        ais.universal_service_identifier = CWE(cwe_1='INT01', cwe_2='Interní vyšetření', cwe_3='FONSSERV')
        ais.start_date_time_offset = '20250612090000'
        ais.start_date_time_offset_units = CNE(cne_1='30', cne_2='min')
        ais.duration = 'MIN^^ISO+'

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'A'
        ail.location_resource_id = PL(pl_1='AMB4', pl_2='ORD07', pl_3='A', pl_4='AMB_BRNO', pl_8='AMB4')
        ail.location_group = CWE(cwe_1='20250612090000')
        ail.start_date_time = '30^min'
        ail.start_date_time_offset = 'MIN^^ISO+'

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.personnel_resource_id = XCN(xcn_1='3569850898', xcn_2='Kučerová', xcn_3='Eliška', xcn_4='Marie', xcn_6='MUDr.', xcn_9='IČP')
        aip.resource_group = CWE(cwe_1='20250612090000')
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
    """ Based on live/cz/cz-fons-akord.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='POLIKL_OLOMOUC')
        msh.receiving_application = HD(hd_1='MPI_CENTRAL')
        msh.receiving_facility = HD(hd_1='POLIKL_OLOMOUC')
        msh.date_time_of_message = '20250125101530'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'FA20250125101530001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250125101500'
        evn.operator_id = XCN(xcn_1='MALIKOVA', xcn_2='Fialová', xcn_3='Dana', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='6206021310', cx_4='FONS', cx_5='RC'), CX(cx_1='OL34838437', cx_4='OLOMOUC', cx_5='MRN')]
        pid.pid_5 = 'KOLÁŘ^Bedřich^Filip^^^'
        pid.date_time_of_birth = '19620602'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Dlouhá 197', xad_3='Kladno', xad_4='CZ', xad_5='27201', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^657155871~^NET^Internet^bedrich.kolar@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '6206021310'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'POLIKLINIKA OLOMOUC^^56789'
        pd1.pd1_4 = '0726242179^Křížková^Eliška^Markéta^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='KOLÁŘOVÁ', xpn_2='Ivana', xpn_3='Eliška')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Dlouhá 197', xad_3='Kladno', xad_4='CZ', xad_5='27201', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^657155871'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB5', pl_2='ORD09', pl_3='A', pl_4='POLIKL_OLOMOUC', pl_8='AMB5')
        pv1.attending_doctor = XCN(xcn_1='0726242179', xcn_2='Křížková', xcn_3='Eliška', xcn_4='Markéta', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70089012', xcn_4='OLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250125101500')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='201', cwe_2='VoZP', cwe_4='VOZP')
        in1.insurance_company_id = CX(cx_1='201')
        in1.insurance_company_name = XON(xon_1='VOJENSKÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Drahobejlova 1404/4', xad_3='Praha 9', xad_4='CZ', xad_5='19000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^284091111'
        in1.assignment_of_benefits = CWE(cwe_1='KOLÁŘ', cwe_2='Bedřich', cwe_3='Filip')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19620602'
        in1.notice_of_admission_flag = 'Dlouhá 197^^Kladno^CZ^27201^CZ'

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
    """ Based on live/cz/cz-fons-akord.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='AMB_CB')
        msh.receiving_application = HD(hd_1='RADRIS')
        msh.receiving_facility = HD(hd_1='AMB_CB')
        msh.date_time_of_message = '20250407113045'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'FA20250407113045001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5212235404', cx_4='FONS', cx_5='RC'), CX(cx_1='CB20150788', cx_4='CB', cx_5='MRN')]
        pid.pid_5 = 'VESELÝ^Tomáš^Marek^^^'
        pid.date_time_of_birth = '19521223'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Žitavská 43', xad_3='Praha 1', xad_4='CZ', xad_5='11000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^720305517'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5212235404'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB6', pl_2='ORD11', pl_3='A', pl_4='AMB_CB', pl_8='AMB6')
        pv1.attending_doctor = XCN(xcn_1='8523453476', xcn_2='Jelínková', xcn_3='Anna', xcn_4='Bohuslava', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='ORT', xcn_2='Ortopedie', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80090123', xcn_4='CBENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250407113000')

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
        orc.placer_order_number = EI(ei_1='ORD801234', ei_2='FONS')
        orc.filler_order_number = EI(ei_1='RAD901234', ei_2='RADRIS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250407120000^^R'
        orc.date_time_of_order_event = '20250407113045'
        orc.orc_10 = 'DVORAKJ^Jandová^Marie^^^'
        orc.order_control_code_reason = CWE(cwe_1='AMB_CB')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801234', ei_2='FONS')
        obr.filler_order_number = EI(ei_1='RAD901234', ei_2='RADRIS')
        obr.universal_service_identifier = CWE(cwe_1='73562', cwe_2='RTG kolenního kloubu', cwe_3='CPT')
        obr.obr_16 = '8523453476^Jelínková^Anna^Bohuslava^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250407120000'
        obr.result_status = 'NI^No Information^HL70507'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M17.1', cwe_2='Primární gonartroza', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250407'
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
    """ Based on live/cz/cz-fons-akord.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='NEM_HK')
        msh.receiving_application = HD(hd_1='MPI_HK')
        msh.receiving_facility = HD(hd_1='NEM_HK')
        msh.date_time_of_message = '20250530155000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'FA20250530155000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250530155000'
        evn.operator_id = XCN(xcn_1='HRUBYM', xcn_2='Polák', xcn_3='Antonín', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='9705136617', cx_4='FONS', cx_5='RC'), CX(cx_1='HK28502106', cx_4='HK', cx_5='MRN')]
        pid.pid_5 = 'PAVLÍK^Vlastimil^Vojtěch^^^'
        pid.date_time_of_birth = '19970513'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Štefánikova 76', xad_3='Příbram', xad_4='CZ', xad_5='26101', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^787005034~^NET^Internet^vlastimil.pavlik@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '9705136617'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'NEMOCNICE HRADEC KRÁLOVÉ^^78901'
        pd1.pd1_4 = '2642539274^Brož^Vojtěch^Rostislav^^MUDr.^^^IČP'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB7', pl_2='ORD13', pl_3='A', pl_4='NEM_HK', pl_8='AMB7')
        pv1.attending_doctor = XCN(xcn_1='2642539274', xcn_2='Brož', xcn_3='Vojtěch', xcn_4='Rostislav', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90101234', xcn_4='HKENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250530155000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='111', cwe_2='VZP', cwe_4='VZP')
        in1.insurance_company_id = CX(cx_1='111')
        in1.insurance_company_name = XON(xon_1='VŠEOBECNÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Orlická 4', xad_3='Praha 3', xad_4='CZ', xad_5='13000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^952222222'
        in1.assignment_of_benefits = CWE(cwe_1='PAVLÍK', cwe_2='Vlastimil', cwe_3='Vojtěch')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19970513'
        in1.notice_of_admission_flag = 'Štefánikova 76^^Příbram^CZ^26101^CZ'

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
    """ Based on live/cz/cz-fons-akord.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='AMB_PARDUBICE')
        msh.receiving_application = HD(hd_1='DOCSYS')
        msh.receiving_facility = HD(hd_1='AMB_PARDUBICE')
        msh.date_time_of_message = '20250415134500'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'FA20250415134500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250415134500'
        evn.operator_id = XCN(xcn_1='BURESOVA', xcn_2='Konečná', xcn_3='Eliška', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='8003115488', cx_4='FONS', cx_5='RC'), CX(cx_1='PA59021332', cx_4='PARDUBICE', cx_5='MRN')]
        pid.pid_5 = 'BOUŠKA^Aleš^Matěj^^^'
        pid.date_time_of_birth = '19800311'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='28. října 130', xad_3='Karviná', xad_4='CZ', xad_5='73301', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^665159762'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '8003115488'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB8', pl_2='ORD15', pl_3='A', pl_4='AMB_PARDUBICE', pl_8='AMB8')
        pv1.attending_doctor = XCN(xcn_1='7215562846', xcn_2='Vacková', xcn_3='Veronika', xcn_4='Hana', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10112345', xcn_4='PAENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250415134500')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='HP', cwe_2='Propouštěcí zpráva', cwe_3='HL70270')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20250415134500'
        txa.primary_activity_provider_code_name = XCN(xcn_1='7215562846', xcn_2='Vacková', xcn_3='Veronika', xcn_4='Hana', xcn_6='MUDr.', xcn_9='IČP')
        txa.origination_date_time = '20250415134500'
        txa.unique_document_number = EI(ei_1='DOC10012345', ei_2='FONS')
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
    """ Based on live/cz/cz-fons-akord.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='FN_MOTOL')
        msh.receiving_application = HD(hd_1='NIS_MOTOL')
        msh.receiving_facility = HD(hd_1='FN_MOTOL')
        msh.date_time_of_message = '20250416143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'FA20250416143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250416143000'
        evn.operator_id = XCN(xcn_1='KREJCIM', xcn_2='Tichá', xcn_3='Zdeňka', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5304209261', cx_4='FONS', cx_5='RC'), CX(cx_1='MOT66102185', cx_4='MOTOL', cx_5='MRN')]
        pid.pid_5 = 'HRUŠKA^Vladimír^Matěj^^^'
        pid.date_time_of_birth = '19530420'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Národní třída 54', xad_3='Hradec Králové', xad_4='CZ', xad_5='50002', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^657353793'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5304209261'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='JIP1', pl_2='102', pl_3='A', pl_4='FN_MOTOL', pl_8='JIP1')
        pv1.attending_doctor = XCN(xcn_1='0026351455', xcn_2='Konečný', xcn_3='Michal', xcn_4='Vojtěch', xcn_6='MUDr.', xcn_9='IČP')
        pv1.referring_doctor = XCN(xcn_1='4534678627', xcn_2='Marek', xcn_3='Rostislav', xcn_4='Lukáš', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='CHI', xcn_2='Chirurgie', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='T', cwe_2='Transfer', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V20034567', xcn_4='MOTOLENC', xcn_5='VN')
        pv1.delete_account_indicator = CWE(cwe_1='CHIR2', cwe_2='201', cwe_3='A', cwe_4='FN_MOTOL', cwe_8='CHIR2')
        pv1.pv1_40 = '20250416143000'

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
    """ Based on live/cz/cz-fons-akord.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NIS_MOTOL')
        msh.sending_facility = HD(hd_1='FN_MOTOL')
        msh.receiving_application = HD(hd_1='FONS_AKORD')
        msh.receiving_facility = HD(hd_1='FN_MOTOL')
        msh.date_time_of_message = '20250415091535'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'NIS20250415091535001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'FA20250415091530001'
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
    """ Based on live/cz/cz-fons-akord.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='NEM_LIBEREC')
        msh.receiving_application = HD(hd_1='AMBSYS')
        msh.receiving_facility = HD(hd_1='NEM_LIBEREC')
        msh.date_time_of_message = '20250301141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'FA20250301141500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='8310125010', cx_4='FONS', cx_5='RC'), CX(cx_1='LB26093826', cx_4='LIBEREC', cx_5='MRN')]
        pid.pid_5 = 'PROCHÁZKA^Dalibor^František^^^'
        pid.date_time_of_birth = '19831012'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Studentská 237', xad_3='Pardubice', xad_4='CZ', xad_5='53002', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^613287983'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '8310125010'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB3', pl_2='ORD05', pl_3='A', pl_4='NEM_LIBEREC', pl_8='AMB3')
        pv1.attending_doctor = XCN(xcn_1='9719926324', xcn_2='Konečný', xcn_3='Vojtěch', xcn_4='Pavel', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V50078901', xcn_4='LIBENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250225094500')

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
        orc.placer_order_number = EI(ei_1='ORD901234', ei_2='FONS')
        orc.filler_order_number = EI(ei_1='MIC801234', ei_2='LABLIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250225100000^^R'
        orc.date_time_of_order_event = '20250301141500'
        orc.orc_18 = 'NEM_LIBEREC'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901234', ei_2='FONS')
        obr.filler_order_number = EI(ei_1='MIC801234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='87086', cwe_2='Kultivace moči', cwe_3='CPT')
        obr.observation_date_time = '20250225100500'
        obr.obr_17 = '9719926324^Konečný^Vojtěch^Pavel^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250301141500')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='Bakterie identifikované v moči kultivací', cwe_3='LN')
        obx.obx_5 = 'Escherichia coli > 10^5 CFU/ml'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250301140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Citlivost na antibiotika', cwe_3='LN')
        obx_2.obx_5 = 'Ampicilin: R, Ciprofloxacin: S, Nitrofurantoin: S, Cotrimoxazol: I'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250301140000'

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
    """ Based on live/cz/cz-fons-akord.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='FN_BRNO')
        msh.receiving_application = HD(hd_1='MPI_BRNO')
        msh.receiving_facility = HD(hd_1='FN_BRNO')
        msh.date_time_of_message = '20250610110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'FA20250610110000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250610110000'
        evn.operator_id = XCN(xcn_1='ADMINKA', xcn_2='Fialová', xcn_3='Alena', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='7808269560', cx_4='FONS', cx_5='RC'), CX(cx_1='BR91863103', cx_4='BRNO', cx_5='MRN')]
        pid.pid_5 = 'BARTOŠ^Daniel^Filip^^^'
        pid.date_time_of_birth = '19780826'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vinohradská 60', xad_3='Pardubice', xad_4='CZ', xad_5='53002', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^687183374'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '7808269560'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='BR35008238', cx_4='BRNO', cx_5='MRN')
        mrg.mrg_2 = '9508093049'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB9', pl_2='ORD17', pl_3='A', pl_4='FN_BRNO', pl_8='AMB9')
        pv1.attending_doctor = XCN(xcn_1='6164917260', xcn_2='Vlčková', xcn_3='Věra', xcn_4='Marie', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V20034567', xcn_4='BRNOENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250610110000')

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
    """ Based on live/cz/cz-fons-akord.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='AMB_ZLIN')
        msh.receiving_application = HD(hd_1='PHARMSYS')
        msh.receiving_facility = HD(hd_1='AMB_ZLIN')
        msh.date_time_of_message = '20250520093000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'FA20250520093000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='4410085561', cx_4='FONS', cx_5='RC'), CX(cx_1='ZL60978999', cx_4='ZLIN', cx_5='MRN')]
        pid.pid_5 = 'DVOŘÁK^Matěj^Lukáš^^^'
        pid.date_time_of_birth = '19441008'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Nádražní 162', xad_3='Havířov', xad_4='CZ', xad_5='73601', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^781713730'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '4410085561'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB10', pl_2='ORD19', pl_3='A', pl_4='AMB_ZLIN', pl_8='AMB10')
        pv1.attending_doctor = XCN(xcn_1='8264178197', xcn_2='Krejčí', xcn_3='Miroslav', xcn_4='Daniel', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V30045678', xcn_4='ZLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250520093000')

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
        orc.placer_order_number = EI(ei_1='ORD111234', ei_2='FONS')
        orc.filler_order_number = EI(ei_1='PH901234', ei_2='PHARMSYS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250520^^R'
        orc.date_time_of_order_event = '20250520093000'
        orc.orc_10 = 'KOPECKAH^Janoušek^David^^^'
        orc.order_control_code_reason = CWE(cwe_1='AMB_ZLIN')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD111234', ei_2='FONS')
        obr.filler_order_number = EI(ei_1='PH901234', ei_2='PHARMSYS')
        obr.universal_service_identifier = CWE(cwe_1='RX001', cwe_2='Předpis léku', cwe_3='LOCAL')
        obr.obr_16 = '8264178197^Krejčí^Miroslav^Daniel^^MUDr.^^^IČP'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='1')
        rxo.requested_give_amount_minimum = 'METFORMIN^Metformin 500mg^SUKL'
        rxo.requested_give_units = CWE(cwe_1='500')
        rxo.requested_dosage_form = CWE(cwe_1='mg')
        rxo.providers_administration_instructions = CWE(cwe_1='PO', cwe_2='Per os', cwe_3='HL70162')
        rxo.allow_substitutions = '1-0-1'
        rxo.needs_human_review = 'G'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E11.9', cwe_2='Diabetes mellitus 2. typu bez komplikací', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250520'
        dg1.diagnosis_type = CWE(cwe_1='W', cwe_2='Working', cwe_3='HL70052')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo, dg1]

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
    """ Based on live/cz/cz-fons-akord.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='FN_BRNO')
        msh.receiving_application = HD(hd_1='AMBSYS')
        msh.receiving_facility = HD(hd_1='FN_BRNO')
        msh.date_time_of_message = '20250412160030'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'FA20250412160030001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='8712136994', cx_4='FONS', cx_5='RC'), CX(cx_1='BR20488603', cx_4='BRNO', cx_5='MRN')]
        pid.pid_5 = 'KRÁL^Zdeněk^Jiří^^^'
        pid.date_time_of_birth = '19871213'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tylova 118', xad_3='Praha 3', xad_4='CZ', xad_5='13000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^618986774'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '8712136994'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HEM1', pl_2='HEM01', pl_3='A', pl_4='FN_BRNO', pl_8='HEM1')
        pv1.attending_doctor = XCN(xcn_1='1746567864', xcn_2='Urban', xcn_3='Radek', xcn_4='Jaroslav', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='HEM', xcn_2='Hematologie', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V20056789', xcn_4='BRNOENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250410083000')

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
        orc.placer_order_number = EI(ei_1='ORD121234', ei_2='FONS')
        orc.filler_order_number = EI(ei_1='LAB121234', ei_2='LABLIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250410090000^^R'
        orc.date_time_of_order_event = '20250412160030'
        orc.orc_18 = 'FN_BRNO'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD121234', ei_2='FONS')
        obr.filler_order_number = EI(ei_1='LAB121234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='85025', cwe_2='Krevní obraz kompletní', cwe_3='CPT')
        obr.observation_date_time = '20250410090500'
        obr.obr_17 = '1746567864^Urban^Radek^Jaroslav^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250412160030')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx.obx_5 = '148'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '130-170'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250412150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematokrit', cwe_3='LN')
        obx_2.obx_5 = '0.44'
        obx_2.units = CWE(cwe_1='L/L')
        obx_2.reference_range = '0.39-0.50'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250412150000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocyty', cwe_3='LN')
        obx_3.obx_5 = '7.2'
        obx_3.units = CWE(cwe_1='10*9/L')
        obx_3.reference_range = '4.0-10.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250412150000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='777-3', cwe_2='Trombocyty', cwe_3='LN')
        obx_4.obx_5 = '235'
        obx_4.units = CWE(cwe_1='10*9/L')
        obx_4.reference_range = '150-400'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250412150000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erytrocyty', cwe_3='LN')
        obx_5.obx_5 = '4.85'
        obx_5.units = CWE(cwe_1='10*12/L')
        obx_5.reference_range = '4.2-5.8'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250412150000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_6.obx_5 = '90.7'
        obx_6.units = CWE(cwe_1='fL')
        obx_6.reference_range = '80-100'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250412150000'

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
    """ Based on live/cz/cz-fons-akord.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='AMB_JIHLAVA')
        msh.receiving_application = HD(hd_1='REGSYS')
        msh.receiving_facility = HD(hd_1='AMB_JIHLAVA')
        msh.date_time_of_message = '20250603080030'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'FA20250603080030001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250603080000'
        evn.operator_id = XCN(xcn_1='STRNADJ', xcn_2='Beneš', xcn_3='Václav', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='0910259533', cx_4='FONS', cx_5='RC'), CX(cx_1='JI03333310', cx_4='JIHLAVA', cx_5='MRN')]
        pid.pid_5 = 'KRÁL^Roman^Cyril^^^'
        pid.date_time_of_birth = '20091025'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Palackého 104', xad_3='Praha 10', xad_4='CZ', xad_5='10100', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^760933913~^NET^Internet^roman.kral@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '0910259533'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'AMBULANCE JIHLAVA^^89012'
        pd1.pd1_4 = '7510296752^Horák^Karel^Martin^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='KRÁLOVÁ', xpn_2='Kateřina', xpn_3='Zdeňka')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Palackého 104', xad_3='Praha 10', xad_4='CZ', xad_5='10100', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^760933913'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB11', pl_2='ORD21', pl_3='A', pl_4='AMB_JIHLAVA', pl_8='AMB11')
        pv1.attending_doctor = XCN(xcn_1='7510296752', xcn_2='Horák', xcn_3='Karel', xcn_4='Martin', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V40056789', xcn_4='JIENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250603080000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='205', cwe_2='ČPZP', cwe_4='CPZP')
        in1.insurance_company_id = CX(cx_1='205')
        in1.insurance_company_name = XON(xon_1='ČESKÁ PRŮMYSLOVÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Jeremenkova 11', xad_3='Ostrava', xad_4='CZ', xad_5='70300', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^596256511'
        in1.assignment_of_benefits = CWE(cwe_1='KRÁL', cwe_2='Roman', cwe_3='Cyril')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '20091025'
        in1.notice_of_admission_flag = 'Palackého 104^^Praha 10^CZ^10100^CZ'

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
    """ Based on live/cz/cz-fons-akord.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FONS_AKORD')
        msh.sending_facility = HD(hd_1='NEM_PLZEN')
        msh.receiving_application = HD(hd_1='RADSYS')
        msh.receiving_facility = HD(hd_1='NEM_PLZEN')
        msh.date_time_of_message = '20250408151500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'FA20250408151500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5212235404', cx_4='FONS', cx_5='RC'), CX(cx_1='CB20150788', cx_4='CB', cx_5='MRN')]
        pid.pid_5 = 'VESELÝ^Tomáš^Marek^^^'
        pid.date_time_of_birth = '19521223'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Žitavská 43', xad_3='Praha 1', xad_4='CZ', xad_5='11000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^720305517'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5212235404'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD1', pl_2='RAD01', pl_3='A', pl_4='NEM_PLZEN', pl_8='RAD1')
        pv1.attending_doctor = XCN(xcn_1='8523453476', xcn_2='Jelínková', xcn_3='Anna', xcn_4='Bohuslava', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='RAD', xcn_2='Radiologie', xcn_3='FONSSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80090124', xcn_4='PLZENENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250407120000')

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
        orc.placer_order_number = EI(ei_1='ORD801234', ei_2='FONS')
        orc.filler_order_number = EI(ei_1='RAD901234', ei_2='RADRIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250407120000^^R'
        orc.date_time_of_order_event = '20250408151500'
        orc.orc_18 = 'NEM_PLZEN'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801234', ei_2='FONS')
        obr.filler_order_number = EI(ei_1='RAD901234', ei_2='RADRIS')
        obr.universal_service_identifier = CWE(cwe_1='73562', cwe_2='RTG kolenního kloubu', cwe_3='CPT')
        obr.observation_date_time = '20250407120500'
        obr.obr_17 = '8523453476^Jelínková^Anna^Bohuslava^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250408151500')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18782-3', cwe_2='Radiologický nález', cwe_3='LN')
        obx.obx_5 = 'RTG pravého kolene - gonartroza gr. II dle Kellgrena-Lawrence, zúžení kloubní štěrbiny mediálně, marginální osteofyty.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250408150000'

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
