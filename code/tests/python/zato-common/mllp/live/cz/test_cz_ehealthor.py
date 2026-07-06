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

_md_path = md_path_for('cz', 'cz-ehealthor.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/cz/cz-ehealthor.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='KN_LIBEREC')
        msh.receiving_application = HD(hd_1='NIS_LBC')
        msh.receiving_facility = HD(hd_1='KN_LIBEREC')
        msh.date_time_of_message = '20250312074500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'EH20250312074500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250312074500'
        evn.operator_id = XCN(xcn_1='SESTRA01', xcn_2='Bartošová', xcn_3='Kateřina', xcn_6='Bc.')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5405178404', cx_4='EHOR', cx_5='RC'), CX(cx_1='LBC15005253', cx_4='KNL', cx_5='MRN')]
        pid.pid_5 = 'SVOBODA^Vlastimil^Filip^^^'
        pid.date_time_of_birth = '19540517'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Českobratrská 80', xad_3='Most', xad_4='CZ', xad_5='43401', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^655368341~^NET^Internet^vlastimil.svoboda@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5405178404'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'KRAJSKÁ NEMOCNICE LIBEREC^^11234'
        pd1.pd1_4 = '8669593665^Novotná^Zdeňka^Alena^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='SVOBODOVÁ', xpn_2='Helena', xpn_3='Tereza')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Českobratrská 80', xad_3='Most', xad_4='CZ', xad_5='43401', xad_6='CZ', xad_7='L')
        nk1.nk1_5 = '^PRN^PH^^^420^655368341'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT2', pl_2='205', pl_3='A', pl_4='KN_LIBEREC', pl_8='INT2')
        pv1.attending_doctor = XCN(xcn_1='8669593665', xcn_2='Novotná', xcn_3='Zdeňka', xcn_4='Alena', xcn_6='MUDr.', xcn_9='IČP')
        pv1.referring_doctor = XCN(xcn_1='7734417476', xcn_2='Němcová', xcn_3='Drahomíra', xcn_4='Alena', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10023456', xcn_4='KNLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250312074500')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Pneumonie, neurčená', cwe_3='J18.9')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='111', cwe_2='VZP', cwe_4='VZP')
        in1.insurance_company_id = CX(cx_1='111')
        in1.insurance_company_name = XON(xon_1='VŠEOBECNÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Orlická 4', xad_3='Praha 3', xad_4='CZ', xad_5='13000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^952222222'
        in1.assignment_of_benefits = CWE(cwe_1='SVOBODA', cwe_2='Vlastimil', cwe_3='Filip')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19540517'
        in1.notice_of_admission_flag = 'Českobratrská 80^^Most^CZ^43401^CZ'

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
    """ Based on live/cz/cz-ehealthor.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='FN_OSTRAVA')
        msh.receiving_application = HD(hd_1='EDIS_OST')
        msh.receiving_facility = HD(hd_1='FN_OSTRAVA')
        msh.date_time_of_message = '20250418162030'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'EH20250418162030001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250418162000'
        evn.operator_id = XCN(xcn_1='PRIJEM01', xcn_2='Benešová', xcn_3='Hana', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='1305270000', cx_4='EHOR', cx_5='RC'), CX(cx_1='OST49870229', cx_4='FNO', cx_5='MRN')]
        pid.pid_5 = 'LUKÁŠ^Ondřej^Cyril^^^'
        pid.date_time_of_birth = '20130527'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Třída Svobody 63', xad_3='Praha 2', xad_4='CZ', xad_5='12000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^655286810'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '1305270000'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'FN OSTRAVA^^22345'
        pd1.pd1_4 = '8929750386^Černá^Magdalena^Jaroslava^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='LUKÁŠOVÁ', xpn_2='Monika', xpn_3='Jaroslava')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Třída Svobody 63', xad_3='Praha 2', xad_4='CZ', xad_5='12000', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^655286810'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='EDFNO', pl_2='ED03', pl_3='A', pl_4='FN_OSTRAVA', pl_8='EDFNO')
        pv1.attending_doctor = XCN(xcn_1='8929750386', xcn_2='Černá', xcn_3='Magdalena', xcn_4='Jaroslava', xcn_6='MUDr.', xcn_9='IČP')
        pv1.referring_doctor = XCN(xcn_1='7026004573', xcn_2='Novák', xcn_3='Štěpán', xcn_4='Zdeněk', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='EM', xcn_2='Urgentní příjem', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V20034567', xcn_4='FNOENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250418162000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Fraktura radia', cwe_3='S52.5')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='207', cwe_2='OZP', cwe_4='OZP')
        in1.insurance_company_id = CX(cx_1='207')
        in1.insurance_company_name = XON(xon_1='OBOROVÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Roškotova 1225/1', xad_3='Praha 4', xad_4='CZ', xad_5='14000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^261105555'
        in1.assignment_of_benefits = CWE(cwe_1='LUKÁŠ', cwe_2='Ondřej', cwe_3='Cyril')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '20130527'
        in1.notice_of_admission_flag = 'Třída Svobody 63^^Praha 2^CZ^12000^CZ'

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
    """ Based on live/cz/cz-ehealthor.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='NEM_UNL')
        msh.receiving_application = HD(hd_1='DISCHARGE')
        msh.receiving_facility = HD(hd_1='NEM_UNL')
        msh.date_time_of_message = '20250505151500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'EH20250505151500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250505151500'
        evn.operator_id = XCN(xcn_1='SESTRA02', xcn_2='Brožová', xcn_3='Zdeňka', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='1806127492', cx_4='EHOR', cx_5='RC'), CX(cx_1='UNL02451129', cx_4='NEMUNL', cx_5='MRN')]
        pid.pid_5 = 'DOLEŽAL^Antonín^Vojtěch^^^'
        pid.date_time_of_birth = '20180612'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Budějovická 12', xad_3='Ostrava', xad_4='CZ', xad_5='70300', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^631180980'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '1806127492'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR1', pl_2='108', pl_3='B', pl_4='NEM_UNL', pl_8='CHIR1')
        pv1.attending_doctor = XCN(xcn_1='8043455864', xcn_2='Urbanová', xcn_3='Radka', xcn_4='Veronika', xcn_6='MUDr.', xcn_9='IČP')
        pv1.referring_doctor = XCN(xcn_1='2847757661', xcn_2='Krejčí', xcn_3='Hana', xcn_4='Anna', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='CHI', xcn_2='Chirurgie', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V30045678', xcn_4='UNLENC', xcn_5='VN')
        pv1.visit_number = CX(cx_1='DO', cx_2='Discharged to Home', cx_3='HL70112')
        pv1.prior_temporary_location = PL(pl_1='20250501090000')
        pv1.admit_date_time = '20250505151500'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.1', cwe_2='Cholecystolitiáza s cholecystitidou', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250501'
        dg1.diagnosis_type = CWE(cwe_1='A', cwe_2='Admitting', cwe_3='HL70052')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='K80.1', cwe_2='Cholecystolitiáza s cholecystitidou', cwe_3='MKN10')
        dg1_2.diagnosis_date_time = '20250505'
        dg1_2.diagnosis_type = CWE(cwe_1='F', cwe_2='Final', cwe_3='HL70052')

        # .. build PR1 ..
        pr1 = PR1()
        pr1.set_id_pr1 = '1'
        pr1.procedure_code = CNE(cne_1='51.23', cne_2='Laparoskopická cholecystektomie', cne_3='MKN10PCS')
        pr1.pr1_4 = 'Laparoskopická cholecystektomie'
        pr1.procedure_date_time = '20250502080000'
        pr1.pr1_12 = '8043455864^Urbanová^Radka^Veronika^^MUDr.^^^IČP'

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
        in1.assignment_of_benefits = CWE(cwe_1='DOLEŽAL', cwe_2='Antonín', cwe_3='Vojtěch')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '20180612'
        in1.notice_of_admission_flag = 'Budějovická 12^^Ostrava^CZ^70300^CZ'

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
    """ Based on live/cz/cz-ehealthor.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='NEM_KLADNO')
        msh.receiving_application = HD(hd_1='LABLIS')
        msh.receiving_facility = HD(hd_1='NEM_KLADNO')
        msh.date_time_of_message = '20250321091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EH20250321091000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5711271230', cx_4='EHOR', cx_5='RC'), CX(cx_1='KL56373038', cx_4='NEMKL', cx_5='MRN')]
        pid.pid_5 = 'BENEŠ^Bohumil^Michal^^^'
        pid.date_time_of_birth = '19571127'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Korunní 120', xad_3='Karlovy Vary', xad_4='CZ', xad_5='36001', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^664873080'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '5711271230'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT1', pl_2='102', pl_3='A', pl_4='NEM_KLADNO', pl_8='INT1')
        pv1.attending_doctor = XCN(xcn_1='6742709756', xcn_2='Růžičková', xcn_3='Renata', xcn_4='Olga', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V40056789', xcn_4='KLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250320080000')

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
        orc.placer_order_number = EI(ei_1='ORD201234', ei_2='EHOR')
        orc.filler_order_number = EI(ei_1='LAB301234', ei_2='LABLIS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250321093000^^R'
        orc.date_time_of_order_event = '20250321091000'
        orc.orc_10 = 'BREZINAKV^Křížková^Gabriela^^^'
        orc.order_control_code_reason = CWE(cwe_1='NEM_KLADNO')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD201234', ei_2='EHOR')
        obr.filler_order_number = EI(ei_1='LAB301234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Kompletní metabolický panel', cwe_3='LN')
        obr.obr_16 = '6742709756^Růžičková^Renata^Olga^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250321093000'
        obr.result_status = 'NI^No Information^HL70507'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='N18.3', cwe_2='Chronické onemocnění ledvin, stádium 3', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250320'
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
    """ Based on live/cz/cz-ehealthor.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='NEM_KLADNO')
        msh.receiving_application = HD(hd_1='NIS_KL')
        msh.receiving_facility = HD(hd_1='NEM_KLADNO')
        msh.date_time_of_message = '20250322143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EH20250322143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5711271230', cx_4='EHOR', cx_5='RC'), CX(cx_1='KL56373038', cx_4='NEMKL', cx_5='MRN')]
        pid.pid_5 = 'BENEŠ^Bohumil^Michal^^^'
        pid.date_time_of_birth = '19571127'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Korunní 120', xad_3='Karlovy Vary', xad_4='CZ', xad_5='36001', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^664873080'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '5711271230'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT1', pl_2='102', pl_3='A', pl_4='NEM_KLADNO', pl_8='INT1')
        pv1.attending_doctor = XCN(xcn_1='6742709756', xcn_2='Růžičková', xcn_3='Renata', xcn_4='Olga', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V40056789', xcn_4='KLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250320080000')

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
        orc.placer_order_number = EI(ei_1='ORD201234', ei_2='EHOR')
        orc.filler_order_number = EI(ei_1='LAB301234', ei_2='LABLIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250321093000^^R'
        orc.date_time_of_order_event = '20250322143000'
        orc.orc_18 = 'NEM_KLADNO'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD201234', ei_2='EHOR')
        obr.filler_order_number = EI(ei_1='LAB301234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Kompletní metabolický panel', cwe_3='LN')
        obr.observation_date_time = '20250321093500'
        obr.obr_17 = '6742709756^Růžičková^Renata^Olga^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250322143000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Kreatinin v séru', cwe_3='LN')
        obx.obx_5 = '185'
        obx.units = CWE(cwe_1='umol/L')
        obx.reference_range = '62-106'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250322140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea v séru', cwe_3='LN')
        obx_2.obx_5 = '12.8'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '2.8-7.2'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250322140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='33914-3', cwe_2='eGFR', cwe_3='LN')
        obx_3.obx_5 = '35'
        obx_3.units = CWE(cwe_1='mL/min/1.73m2')
        obx_3.reference_range = '>60'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250322140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glukóza v séru', cwe_3='LN')
        obx_4.obx_5 = '5.1'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '3.9-5.8'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250322140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodík v séru', cwe_3='LN')
        obx_5.obx_5 = '139'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '136-145'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250322140000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Draslík v séru', cwe_3='LN')
        obx_6.obx_5 = '5.4'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '3.5-5.1'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250322140000'

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
    """ Based on live/cz/cz-ehealthor.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='NEM_OPAVA')
        msh.receiving_application = HD(hd_1='MPI_OPAVA')
        msh.receiving_facility = HD(hd_1='NEM_OPAVA')
        msh.date_time_of_message = '20250610090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'EH20250610090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250610090000'
        evn.operator_id = XCN(xcn_1='PRIJEM02', xcn_2='Nováková', xcn_3='Zuzana', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='7408141829', cx_4='EHOR', cx_5='RC'), CX(cx_1='OP01711345', cx_4='NEMOP', cx_5='MRN')]
        pid.pid_5 = 'VACEK^Aleš^Martin^^^'
        pid.date_time_of_birth = '19740814'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='T.G. Masaryka 237', xad_3='Praha 5', xad_4='CZ', xad_5='15000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^621528517~^NET^Internet^ales.vacek@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '7408141829'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'NEMOCNICE OPAVA^^33456'
        pd1.pd1_4 = '7544314051^Benešová^Renata^Petra^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='VACKOVÁ', xpn_2='Eva', xpn_3='Dana')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='T.G. Masaryka 237', xad_3='Praha 5', xad_4='CZ', xad_5='15000', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^621528517'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB1', pl_2='ORD01', pl_3='A', pl_4='NEM_OPAVA', pl_8='AMB1')
        pv1.attending_doctor = XCN(xcn_1='7544314051', xcn_2='Benešová', xcn_3='Renata', xcn_4='Petra', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V50067890', xcn_4='OPENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250610090000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='211', cwe_2='ZPMV', cwe_4='ZPMV')
        in1.insurance_company_id = CX(cx_1='211')
        in1.insurance_company_name = XON(xon_1='ZDRAVOTNÍ POJIŠŤOVNA MINISTERSTVA VNITRA')
        in1.insurance_company_address = XAD(xad_1='Kodaňská 46', xad_3='Praha 10', xad_4='CZ', xad_5='10100', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^267205555'
        in1.assignment_of_benefits = CWE(cwe_1='VACEK', cwe_2='Aleš', cwe_3='Martin')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19740814'
        in1.notice_of_admission_flag = 'T.G. Masaryka 237^^Praha 5^CZ^15000^CZ'

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
    """ Based on live/cz/cz-ehealthor.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='FN_OSTRAVA')
        msh.receiving_application = HD(hd_1='SCHEDMGR')
        msh.receiving_facility = HD(hd_1='FN_OSTRAVA')
        msh.date_time_of_message = '20250515080000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'EH20250515080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='SCH20023456', ei_2='EHOR')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70276')
        sch.appointment_type = CWE(cwe_1='45', cwe_2='min')
        sch.sch_9 = 'MIN^^ISO+'
        sch.placer_contact_person = XCN(xcn_1='RECEPCE', xcn_2='Hájek', xcn_3='Adam', xcn_6='')
        sch.placer_contact_phone_number = XTN(xtn_2='PRN', xtn_3='PH', xtn_6='420', xtn_7='596345678')
        sch.filler_contact_address = XAD(xad_1='8929750386', xad_2='Černá', xad_3='Magdalena', xad_4='Jaroslava', xad_6='MUDr.', xad_9='IČP')
        sch.filler_contact_location = PL(pl_2='PRN', pl_3='PH', pl_6='420', pl_7='596123456')
        sch.entered_by_person = XCN(xcn_1='FN OSTRAVA')
        sch.entered_by_location = PL(pl_1='BOOKED', pl_2='Booked', pl_3='HL70278')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='0111049331', cx_4='EHOR', cx_5='RC'), CX(cx_1='OST17751882', cx_4='FNO', cx_5='MRN')]
        pid.pid_5 = 'KRÁL^Rostislav^František^^^'
        pid.date_time_of_birth = '20011104'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Čankovská 158', xad_3='Hradec Králové', xad_4='CZ', xad_5='50002', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^746160286'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '0111049331'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORTO1', pl_2='ORT01', pl_3='A', pl_4='FN_OSTRAVA', pl_8='ORTO1')
        pv1.attending_doctor = XCN(xcn_1='8929750386', xcn_2='Černá', xcn_3='Magdalena', xcn_4='Jaroslava', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='ORT', xcn_2='Ortopedie', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V60078901', xcn_4='FNOENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250520090000')

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
        ais.universal_service_identifier = CWE(cwe_1='ORT01', cwe_2='Ortopedické vyšetření', cwe_3='EHSERV')
        ais.start_date_time_offset = '20250520090000'
        ais.start_date_time_offset_units = CNE(cne_1='45', cne_2='min')
        ais.duration = 'MIN^^ISO+'

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'A'
        ail.location_resource_id = PL(pl_1='ORTO1', pl_2='ORT01', pl_3='A', pl_4='FN_OSTRAVA', pl_8='ORTO1')
        ail.location_group = CWE(cwe_1='20250520090000')
        ail.start_date_time = '45^min'
        ail.start_date_time_offset = 'MIN^^ISO+'

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.personnel_resource_id = XCN(xcn_1='8929750386', xcn_2='Černá', xcn_3='Magdalena', xcn_4='Jaroslava', xcn_6='MUDr.', xcn_9='IČP')
        aip.resource_group = CWE(cwe_1='20250520090000')
        aip.start_date_time = '45^min'
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
    """ Based on live/cz/cz-ehealthor.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='NEM_KV')
        msh.receiving_application = HD(hd_1='MPI_KV')
        msh.receiving_facility = HD(hd_1='NEM_KV')
        msh.date_time_of_message = '20250201100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'EH20250201100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250201100000'
        evn.operator_id = XCN(xcn_1='PRIJEM03', xcn_2='Bláhová', xcn_3='Dana', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='9804116519', cx_4='EHOR', cx_5='RC'), CX(cx_1='KV90770439', cx_4='NEMKV', cx_5='MRN')]
        pid.pid_5 = 'NĚMEC^Štěpán^Adam^^^'
        pid.date_time_of_birth = '19980411'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hrnčířská 114', xad_3='Náchod', xad_4='CZ', xad_5='54701', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^775856698~^NET^Internet^stepan.nemec@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '9804116519'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'NEMOCNICE KARLOVY VARY^^44567'
        pd1.pd1_4 = '9803760885^Horák^Rostislav^Tomáš^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='NĚMCOVÁ', xpn_2='Tereza', xpn_3='Věra')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Hrnčířská 114', xad_3='Náchod', xad_4='CZ', xad_5='54701', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^775856698'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB2', pl_2='ORD03', pl_3='A', pl_4='NEM_KV', pl_8='AMB2')
        pv1.attending_doctor = XCN(xcn_1='9803760885', xcn_2='Horák', xcn_3='Rostislav', xcn_4='Tomáš', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70089012', xcn_4='KVENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250201100000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='205', cwe_2='ČPZP', cwe_4='CPZP')
        in1.insurance_company_id = CX(cx_1='205')
        in1.insurance_company_name = XON(xon_1='ČESKÁ PRŮMYSLOVÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Jeremenkova 11', xad_3='Ostrava', xad_4='CZ', xad_5='70300', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^596256511'
        in1.assignment_of_benefits = CWE(cwe_1='NĚMEC', cwe_2='Štěpán', cwe_3='Adam')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19980411'
        in1.notice_of_admission_flag = 'Hrnčířská 114^^Náchod^CZ^54701^CZ'

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
    """ Based on live/cz/cz-ehealthor.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='KN_LIBEREC')
        msh.receiving_application = HD(hd_1='NIS_LBC')
        msh.receiving_facility = HD(hd_1='KN_LIBEREC')
        msh.date_time_of_message = '20250420140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EH20250420140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5405178404', cx_4='EHOR', cx_5='RC'), CX(cx_1='LBC15005253', cx_4='KNL', cx_5='MRN')]
        pid.pid_5 = 'SVOBODA^Vlastimil^Filip^^^'
        pid.date_time_of_birth = '19540517'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Českobratrská 80', xad_3='Most', xad_4='CZ', xad_5='43401', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^655368341'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5405178404'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT2', pl_2='205', pl_3='A', pl_4='KN_LIBEREC', pl_8='INT2')
        pv1.attending_doctor = XCN(xcn_1='8669593665', xcn_2='Novotná', xcn_3='Zdeňka', xcn_4='Alena', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10023456', xcn_4='KNLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250312074500')

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
        orc.placer_order_number = EI(ei_1='ORD301234', ei_2='EHOR')
        orc.filler_order_number = EI(ei_1='RAD401234', ei_2='RADRIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250419120000^^R'
        orc.date_time_of_order_event = '20250420140000'
        orc.orc_18 = 'KN_LIBEREC'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD301234', ei_2='EHOR')
        obr.filler_order_number = EI(ei_1='RAD401234', ei_2='RADRIS')
        obr.universal_service_identifier = CWE(cwe_1='71046', cwe_2='RTG hrudníku 2 projekce', cwe_3='CPT')
        obr.observation_date_time = '20250419120500'
        obr.obr_17 = '8669593665^Novotná^Zdeňka^Alena^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250420140000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18782-3', cwe_2='Radiologický nález', cwe_3='LN')
        obx.obx_5 = 'RTG hrudníku - bilaterální perihilózní zastínění, suspektní oboustranná bronchopneumonie, bez pleurálního výpotku.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250420130000'

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
    """ Based on live/cz/cz-ehealthor.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='FN_OSTRAVA')
        msh.receiving_application = HD(hd_1='NIS_OST')
        msh.receiving_facility = HD(hd_1='FN_OSTRAVA')
        msh.date_time_of_message = '20250419083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'EH20250419083000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250419083000'
        evn.operator_id = XCN(xcn_1='SESTRA03', xcn_2='Šťastná', xcn_3='Jana', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='1305270000', cx_4='EHOR', cx_5='RC'), CX(cx_1='OST49870229', cx_4='FNO', cx_5='MRN')]
        pid.pid_5 = 'LUKÁŠ^Ondřej^Cyril^^^'
        pid.date_time_of_birth = '20130527'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Třída Svobody 63', xad_3='Praha 2', xad_4='CZ', xad_5='12000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^655286810'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '1305270000'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR2', pl_2='210', pl_3='A', pl_4='FN_OSTRAVA', pl_8='CHIR2')
        pv1.attending_doctor = XCN(xcn_1='7026004573', xcn_2='Novák', xcn_3='Štěpán', xcn_4='Zdeněk', xcn_6='MUDr.', xcn_9='IČP')
        pv1.referring_doctor = XCN(xcn_1='8929750386', xcn_2='Černá', xcn_3='Magdalena', xcn_4='Jaroslava', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='CHI', xcn_2='Chirurgie', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='T', cwe_2='Transfer', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V20034567', xcn_4='FNOENC', xcn_5='VN')
        pv1.delete_account_indicator = CWE(cwe_1='EDFNO', cwe_2='ED03', cwe_3='A', cwe_4='FN_OSTRAVA', cwe_8='EDFNO')
        pv1.pv1_40 = '20250419083000'

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
    """ Based on live/cz/cz-ehealthor.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='NEM_UNL')
        msh.receiving_application = HD(hd_1='DOCSYS')
        msh.receiving_facility = HD(hd_1='NEM_UNL')
        msh.date_time_of_message = '20250506090000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'EH20250506090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250506090000'
        evn.operator_id = XCN(xcn_1='LEKAR01', xcn_2='Tichá', xcn_3='Gabriela', xcn_6='MUDr.')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='1806127492', cx_4='EHOR', cx_5='RC'), CX(cx_1='UNL02451129', cx_4='NEMUNL', cx_5='MRN')]
        pid.pid_5 = 'DOLEŽAL^Antonín^Vojtěch^^^'
        pid.date_time_of_birth = '20180612'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Budějovická 12', xad_3='Ostrava', xad_4='CZ', xad_5='70300', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^631180980'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '1806127492'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR1', pl_2='108', pl_3='B', pl_4='NEM_UNL', pl_8='CHIR1')
        pv1.attending_doctor = XCN(xcn_1='8043455864', xcn_2='Urbanová', xcn_3='Radka', xcn_4='Veronika', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='CHI', xcn_2='Chirurgie', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V30045678', xcn_4='UNLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250501090000')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Propouštěcí zpráva', cwe_3='HL70270')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20250506090000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='8043455864', xcn_2='Urbanová', xcn_3='Radka', xcn_4='Veronika', xcn_6='MUDr.', xcn_9='IČP')
        txa.origination_date_time = '20250506090000'
        txa.unique_document_number = EI(ei_1='DOC20034567', ei_2='EHOR')
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
    """ Based on live/cz/cz-ehealthor.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='NEM_OPAVA')
        msh.receiving_application = HD(hd_1='RADRIS')
        msh.receiving_facility = HD(hd_1='NEM_OPAVA')
        msh.date_time_of_message = '20250611080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EH20250611080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='7408141829', cx_4='EHOR', cx_5='RC'), CX(cx_1='OP01711345', cx_4='NEMOP', cx_5='MRN')]
        pid.pid_5 = 'VACEK^Aleš^Martin^^^'
        pid.date_time_of_birth = '19740814'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='T.G. Masaryka 237', xad_3='Praha 5', xad_4='CZ', xad_5='15000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^621528517'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '7408141829'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB1', pl_2='ORD01', pl_3='A', pl_4='NEM_OPAVA', pl_8='AMB1')
        pv1.attending_doctor = XCN(xcn_1='7544314051', xcn_2='Benešová', xcn_3='Renata', xcn_4='Petra', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V50067890', xcn_4='OPENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250611080000')

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
        orc.placer_order_number = EI(ei_1='ORD401234', ei_2='EHOR')
        orc.filler_order_number = EI(ei_1='RAD501234', ei_2='RADRIS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250611100000^^R'
        orc.date_time_of_order_event = '20250611080000'
        orc.orc_10 = 'SEDIVYJP^Jelínek^Martin^^^'
        orc.order_control_code_reason = CWE(cwe_1='NEM_OPAVA')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD401234', ei_2='EHOR')
        obr.filler_order_number = EI(ei_1='RAD501234', ei_2='RADRIS')
        obr.universal_service_identifier = CWE(cwe_1='74177', cwe_2='CT břicha s kontrastem', cwe_3='CPT')
        obr.obr_16 = '7544314051^Benešová^Renata^Petra^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250611100000'
        obr.result_status = 'NI^No Information^HL70507'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K57.3', cwe_2='Divertikulóza tlustého střeva bez perforace', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250611'
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
    """ Based on live/cz/cz-ehealthor.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='FN_OSTRAVA')
        msh.receiving_application = HD(hd_1='MPI_OST')
        msh.receiving_facility = HD(hd_1='FN_OSTRAVA')
        msh.date_time_of_message = '20250520110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'EH20250520110000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250520110000'
        evn.operator_id = XCN(xcn_1='ADMIN01', xcn_2='Janda', xcn_3='Antonín', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='8801035676', cx_4='EHOR', cx_5='RC'), CX(cx_1='OST45369457', cx_4='FNO', cx_5='MRN')]
        pid.pid_5 = 'ŠIMEK^Václav^Michal^^^'
        pid.date_time_of_birth = '19880103'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Nerudova 117', xad_3='Praha', xad_4='CZ', xad_5='11000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^737219617~^NET^Internet^vaclav.simek@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '8801035676'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'FN OSTRAVA^^22345'
        pd1.pd1_4 = '8929750386^Černá^Magdalena^Jaroslava^^MUDr.^^^IČP'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB3', pl_2='ORD05', pl_3='A', pl_4='FN_OSTRAVA', pl_8='AMB3')
        pv1.attending_doctor = XCN(xcn_1='8929750386', xcn_2='Černá', xcn_3='Magdalena', xcn_4='Jaroslava', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80090123', xcn_4='FNOENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250520110000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='111', cwe_2='VZP', cwe_4='VZP')
        in1.insurance_company_id = CX(cx_1='111')
        in1.insurance_company_name = XON(xon_1='VŠEOBECNÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Orlická 4', xad_3='Praha 3', xad_4='CZ', xad_5='13000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^952222222'
        in1.assignment_of_benefits = CWE(cwe_1='ŠIMEK', cwe_2='Václav', cwe_3='Michal')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19880103'
        in1.notice_of_admission_flag = 'Nerudova 117^^Praha^CZ^11000^CZ'

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
    """ Based on live/cz/cz-ehealthor.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NIS_LBC')
        msh.sending_facility = HD(hd_1='KN_LIBEREC')
        msh.receiving_application = HD(hd_1='EHEALTHOR')
        msh.receiving_facility = HD(hd_1='KN_LIBEREC')
        msh.date_time_of_message = '20250312074505'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'NIS20250312074505001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'EH20250312074500001'
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
    """ Based on live/cz/cz-ehealthor.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='NEM_KV')
        msh.receiving_application = HD(hd_1='MPI_KV')
        msh.receiving_facility = HD(hd_1='NEM_KV')
        msh.date_time_of_message = '20250305140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'EH20250305140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250305140000'
        evn.operator_id = XCN(xcn_1='ADMIN02', xcn_2='Marečková', xcn_3='Iveta', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='9804116519', cx_4='EHOR', cx_5='RC'), CX(cx_1='KV90770439', cx_4='NEMKV', cx_5='MRN')]
        pid.pid_5 = 'NĚMEC^Štěpán^Adam^^^'
        pid.date_time_of_birth = '19980411'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hrnčířská 114', xad_3='Náchod', xad_4='CZ', xad_5='54701', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^775856698'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '9804116519'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='KV85697281', cx_4='NEMKV', cx_5='MRN')
        mrg.mrg_2 = '5405178404'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB2', pl_2='ORD03', pl_3='A', pl_4='NEM_KV', pl_8='AMB2')
        pv1.attending_doctor = XCN(xcn_1='9803760885', xcn_2='Horák', xcn_3='Rostislav', xcn_4='Tomáš', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70089012', xcn_4='KVENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250305140000')

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
    """ Based on live/cz/cz-ehealthor.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='FN_OSTRAVA')
        msh.receiving_application = HD(hd_1='NIS_OST')
        msh.receiving_facility = HD(hd_1='FN_OSTRAVA')
        msh.date_time_of_message = '20250420150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EH20250420150000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='1305270000', cx_4='EHOR', cx_5='RC'), CX(cx_1='OST49870229', cx_4='FNO', cx_5='MRN')]
        pid.pid_5 = 'LUKÁŠ^Ondřej^Cyril^^^'
        pid.date_time_of_birth = '20130527'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Třída Svobody 63', xad_3='Praha 2', xad_4='CZ', xad_5='12000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^655286810'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '1305270000'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR2', pl_2='210', pl_3='A', pl_4='FN_OSTRAVA', pl_8='CHIR2')
        pv1.attending_doctor = XCN(xcn_1='7026004573', xcn_2='Novák', xcn_3='Štěpán', xcn_4='Zdeněk', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='CHI', xcn_2='Chirurgie', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V20034567', xcn_4='FNOENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250418162000')

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
        orc.placer_order_number = EI(ei_1='ORD501234', ei_2='EHOR')
        orc.filler_order_number = EI(ei_1='LAB601234', ei_2='LABLIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250419090000^^R'
        orc.date_time_of_order_event = '20250420150000'
        orc.orc_18 = 'FN_OSTRAVA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD501234', ei_2='EHOR')
        obr.filler_order_number = EI(ei_1='LAB601234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='85025', cwe_2='Krevní obraz kompletní', cwe_3='CPT')
        obr.observation_date_time = '20250419090500'
        obr.obr_17 = '7026004573^Novák^Štěpán^Zdeněk^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250420150000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx.obx_5 = '125'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '130-170'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250420140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematokrit', cwe_3='LN')
        obx_2.obx_5 = '0.37'
        obx_2.units = CWE(cwe_1='L/L')
        obx_2.reference_range = '0.39-0.50'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250420140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocyty', cwe_3='LN')
        obx_3.obx_5 = '14.8'
        obx_3.units = CWE(cwe_1='10*9/L')
        obx_3.reference_range = '4.0-10.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250420140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='777-3', cwe_2='Trombocyty', cwe_3='LN')
        obx_4.obx_5 = '198'
        obx_4.units = CWE(cwe_1='10*9/L')
        obx_4.reference_range = '150-400'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250420140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='770-8', cwe_2='Neutrofily', cwe_3='LN')
        obx_5.obx_5 = '82'
        obx_5.units = CWE(cwe_1='%')
        obx_5.reference_range = '40-75'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250420140000'

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
    """ Based on live/cz/cz-ehealthor.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='KN_LIBEREC')
        msh.receiving_application = HD(hd_1='CARDIS')
        msh.receiving_facility = HD(hd_1='KN_LIBEREC')
        msh.date_time_of_message = '20250410090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EH20250410090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='9410243197', cx_4='EHOR', cx_5='RC'), CX(cx_1='LBC94955275', cx_4='KNL', cx_5='MRN')]
        pid.pid_5 = 'BARTOŠ^Michal^Aleš^^^'
        pid.date_time_of_birth = '19941024'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Havlíčkova 112', xad_3='Tábor', xad_4='CZ', xad_5='39001', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^665655975'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '9410243197'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='KARD1', pl_2='KAR01', pl_3='A', pl_4='KN_LIBEREC', pl_8='KARD1')
        pv1.attending_doctor = XCN(xcn_1='8669593665', xcn_2='Novotná', xcn_3='Zdeňka', xcn_4='Alena', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='KAR', xcn_2='Kardiologie', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10034567', xcn_4='KNLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250410090000')

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
        orc.placer_order_number = EI(ei_1='ORD601234', ei_2='EHOR')
        orc.filler_order_number = EI(ei_1='ECHO701234', ei_2='CARDIS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250410110000^^R'
        orc.date_time_of_order_event = '20250410090000'
        orc.orc_10 = 'FIALOVATA^Křížková^Lenka^^^'
        orc.order_control_code_reason = CWE(cwe_1='KN_LIBEREC')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD601234', ei_2='EHOR')
        obr.filler_order_number = EI(ei_1='ECHO701234', ei_2='CARDIS')
        obr.universal_service_identifier = CWE(cwe_1='93306', cwe_2='Transtorakální echokardiografie', cwe_3='CPT')
        obr.obr_16 = '8669593665^Novotná^Zdeňka^Alena^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250410110000'
        obr.result_status = 'NI^No Information^HL70507'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I50.9', cwe_2='Srdeční selhání, neurčené', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250410'
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
    """ Based on live/cz/cz-ehealthor.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='NEM_OPAVA')
        msh.receiving_application = HD(hd_1='NIS_OP')
        msh.receiving_facility = HD(hd_1='NEM_OPAVA')
        msh.date_time_of_message = '20250525073000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'EH20250525073000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250525073000'
        evn.operator_id = XCN(xcn_1='SESTRA04', xcn_2='Boušková', xcn_3='Zdeňka', xcn_6='Bc.')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='6107064424', cx_4='EHOR', cx_5='RC'), CX(cx_1='OP04652797', cx_4='NEMOP', cx_5='MRN')]
        pid.pid_5 = 'ŠIMEK^Vlastimil^Jakub^^^'
        pid.date_time_of_birth = '19610706'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vinohradská 4', xad_3='Šumperk', xad_4='CZ', xad_5='78701', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^656208577'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '6107064424'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'NEMOCNICE OPAVA^^33456'
        pd1.pd1_4 = '7544314051^Benešová^Renata^Petra^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='ŠIMKOVÁ', xpn_2='Dana', xpn_3='Eva')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Vinohradská 4', xad_3='Šumperk', xad_4='CZ', xad_5='78701', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^656208577'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PED1', pl_2='305', pl_3='A', pl_4='NEM_OPAVA', pl_8='PED1')
        pv1.attending_doctor = XCN(xcn_1='7544314051', xcn_2='Benešová', xcn_3='Renata', xcn_4='Petra', xcn_6='MUDr.', xcn_9='IČP')
        pv1.referring_doctor = XCN(xcn_1='3969144830', xcn_2='Janoušková', xcn_3='Zdeňka', xcn_4='Olga', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='PED', xcn_2='Pediatrie', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90101234', xcn_4='OPENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250525073000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Akutní bronchitida, neurčená', cwe_3='J20.9')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='111', cwe_2='VZP', cwe_4='VZP')
        in1.insurance_company_id = CX(cx_1='111')
        in1.insurance_company_name = XON(xon_1='VŠEOBECNÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Orlická 4', xad_3='Praha 3', xad_4='CZ', xad_5='13000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^952222222'
        in1.assignment_of_benefits = CWE(cwe_1='ŠIMEK', cwe_2='Vlastimil', cwe_3='Jakub')
        in1.coordination_of_benefits = CWE(cwe_1='19', cwe_2='Child', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19610706'
        in1.notice_of_admission_flag = 'Vinohradská 4^^Šumperk^CZ^78701^CZ'

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
    """ Based on live/cz/cz-ehealthor.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='NEM_KLADNO')
        msh.receiving_application = HD(hd_1='NIS_KL')
        msh.receiving_facility = HD(hd_1='NEM_KLADNO')
        msh.date_time_of_message = '20250401160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EH20250401160000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='1404283898', cx_4='EHOR', cx_5='RC'), CX(cx_1='KL67520816', cx_4='NEMKL', cx_5='MRN')]
        pid.pid_5 = 'FIALA^Vlastimil^Štěpán^^^'
        pid.date_time_of_birth = '20140428'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Na Příkopě 224', xad_3='Liberec', xad_4='CZ', xad_5='46001', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^680548357'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '1404283898'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT1', pl_2='106', pl_3='A', pl_4='NEM_KLADNO', pl_8='INT1')
        pv1.attending_doctor = XCN(xcn_1='6742709756', xcn_2='Růžičková', xcn_3='Renata', xcn_4='Olga', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90112345', xcn_4='KLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250328080000')

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
        orc.placer_order_number = EI(ei_1='ORD701234', ei_2='EHOR')
        orc.filler_order_number = EI(ei_1='MIC801234', ei_2='LABLIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250329100000^^R'
        orc.date_time_of_order_event = '20250401160000'
        orc.orc_18 = 'NEM_KLADNO'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701234', ei_2='EHOR')
        obr.filler_order_number = EI(ei_1='MIC801234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Hemokultivace', cwe_3='CPT')
        obr.observation_date_time = '20250329100500'
        obr.obr_17 = '6742709756^Růžičková^Renata^Olga^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250401160000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bakterie identifikované hemokultivací', cwe_3='LN')
        obx.obx_5 = 'Staphylococcus aureus'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250401150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Citlivost na antibiotika', cwe_3='LN')
        obx_2.obx_5 = 'Oxacilin: S, Vankomycin: S, Klindamycin: S, Gentamicin: S, Cotrimoxazol: S, Rifampicin: S'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250401150000'

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
    """ Based on live/cz/cz-ehealthor.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EHEALTHOR')
        msh.sending_facility = HD(hd_1='NEM_KV')
        msh.receiving_application = HD(hd_1='REGSYS')
        msh.receiving_facility = HD(hd_1='NEM_KV')
        msh.date_time_of_message = '20250610140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'EH20250610140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250610140000'
        evn.operator_id = XCN(xcn_1='PRIJEM04', xcn_2='Dvořák', xcn_3='Karel', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='1012065079', cx_4='EHOR', cx_5='RC'), CX(cx_1='KV16493795', cx_4='NEMKV', cx_5='MRN')]
        pid.pid_5 = 'KONEČNÝ^Bedřich^Filip^^^'
        pid.date_time_of_birth = '20101206'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Českobratrská 76', xad_3='Ostrava', xad_4='CZ', xad_5='70200', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^761219589~^NET^Internet^bedrich.konecny@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '1012065079'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'NEMOCNICE KARLOVY VARY^^44567'
        pd1.pd1_4 = '9803760885^Horák^Rostislav^Tomáš^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='KONEČNÁ', xpn_2='Anna', xpn_3='Věra')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Českobratrská 76', xad_3='Ostrava', xad_4='CZ', xad_5='70200', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^761219589'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB4', pl_2='ORD07', pl_3='A', pl_4='NEM_KV', pl_8='AMB4')
        pv1.attending_doctor = XCN(xcn_1='9803760885', xcn_2='Horák', xcn_3='Rostislav', xcn_4='Tomáš', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='DER', xcn_2='Dermatologie', xcn_3='EHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10123456', xcn_4='KVENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250610140000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='201', cwe_2='VoZP', cwe_4='VOZP')
        in1.insurance_company_id = CX(cx_1='201')
        in1.insurance_company_name = XON(xon_1='VOJENSKÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Drahobejlova 1404/4', xad_3='Praha 9', xad_4='CZ', xad_5='19000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^284091111'
        in1.assignment_of_benefits = CWE(cwe_1='KONEČNÝ', cwe_2='Bedřich', cwe_3='Filip')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '20101206'
        in1.notice_of_admission_flag = 'Českobratrská 76^^Ostrava^CZ^70200^CZ'

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
