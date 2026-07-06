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
from zato.hl7v2.v2_9.datatypes import CNE, CQ, CWE, CX, EI, EIP, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA39Patient, MdmT02Observation, OmbO27Patient, OmbO27PatientVisit, OrmO01Order, OrmO01OrderDetail, \
    OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, \
    RspK22QueryResponse, SiuS12GeneralResource, SiuS12LocationResource, SiuS12Patient, SiuS12Resources
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A39, MDM_T02, OMB_O27, ORM_O01, ORU_R01, QBP_Q21, RSP_K22, SIU_S12
from zato.hl7v2.v2_9.segments import AIG, AIL, BPO, ERR, EVN, IN1, MRG, MSA, MSH, OBR, OBX, ORC, PID, PV1, QAK, QPD, QRI, RCP, RGS, SCH, SPM, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('es', 'es-ianus.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/es/es-ianus.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IANUS')
        msh.sending_facility = HD(hd_1='SERGAS_CHUAC')
        msh.receiving_application = HD(hd_1='HIS_RECEPTOR')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260315083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260315083000'
        evn.event_occurred = '20260315083000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAGAL610293847561', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2'),
            CX(cx_1='28924563P', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='071385660429', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC770582', cx_4='CHUAC', cx_5='PI'),
        ]
        pid.patient_name = XPN(xpn_1='CARREIRA', xpn_2='ANXO')
        pid.mothers_maiden_name = XPN(xpn_1='DOVAL')
        pid.date_time_of_birth = '19870419'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV&ROSALIA DE CASTRO&14', xad_2='2o-1a Escalera A', xad_3='15001', xad_4='15', xad_5='15001', xad_6='ESP', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHUAC', pl_2='PLANTA3', pl_3='CAMA301', pl_4='Medicina Interna')
        pv1.attending_doctor = XCN(xcn_1='54821', xcn_2='OTERO', xcn_3='XOAN', xcn_4='BAAMONDE', xcn_9='CHUAC')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='EPIS20260315001', cwe_4='SERGAS')
        pv1.prior_temporary_location = PL(pl_1='20260315083000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SNS')
        in1.insurance_company_id = CX(cx_1='SERGAS001')
        in1.insurance_company_name = XON(xon_1='SERVIZO GALEGO DE SAUDE')
        in1.insurance_company_address = XAD(xad_1='Edificio Administrativo San Lazaro s/n', xad_3='Santiago de Compostela', xad_5='15703', xad_6='ESP')

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
    """ Based on live/es/es-ianus.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IANUS')
        msh.sending_facility = HD(hd_1='SERGAS_CHUAC')
        msh.receiving_application = HD(hd_1='HIS_RECEPTOR')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260316093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260316093000'
        evn.event_occurred = '20260316093000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAGAL610293847561', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2'),
            CX(cx_1='28924563P', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='CARREIRA', xpn_2='ANXO')
        pid.mothers_maiden_name = XPN(xpn_1='DOVAL')
        pid.date_time_of_birth = '19870419'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV&ROSALIA DE CASTRO&14', xad_2='2o-1a Escalera A', xad_3='15001', xad_4='15', xad_5='15001', xad_6='ESP', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHUAC', pl_2='PLANTA5', pl_3='CAMA512', pl_4='Cirugia General')
        pv1.attending_doctor = XCN(xcn_1='54821', xcn_2='OTERO', xcn_3='XOAN', xcn_4='BAAMONDE', xcn_9='CHUAC')
        pv1.hospital_service = CWE(cwe_1='CIR')
        pv1.patient_type = CWE(cwe_1='EPIS20260315001', cwe_4='SERGAS')
        pv1.prior_temporary_location = PL(pl_1='20260316093000')

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
    """ Based on live/es/es-ianus.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IANUS')
        msh.sending_facility = HD(hd_1='SERGAS_CHUAC')
        msh.receiving_application = HD(hd_1='HIS_RECEPTOR')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260320140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260320140000'
        evn.event_occurred = '20260320140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAGAL610293847561', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2'),
            CX(cx_1='28924563P', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='CARREIRA', xpn_2='ANXO')
        pid.mothers_maiden_name = XPN(xpn_1='DOVAL')
        pid.date_time_of_birth = '19870419'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV&ROSALIA DE CASTRO&14', xad_2='2o-1a Escalera A', xad_3='15001', xad_4='15', xad_5='15001', xad_6='ESP', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHUAC', pl_2='PLANTA3', pl_3='CAMA301', pl_4='Medicina Interna')
        pv1.attending_doctor = XCN(xcn_1='54821', xcn_2='OTERO', xcn_3='XOAN', xcn_4='BAAMONDE', xcn_9='CHUAC')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='EPIS20260315001', cwe_4='SERGAS')
        pv1.prior_temporary_location = PL(pl_1='20260315083000')
        pv1.admit_date_time = '20260320140000'

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
    """ Based on live/es/es-ianus.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IANUS')
        msh.sending_facility = HD(hd_1='SERGAS_CHUS')
        msh.receiving_application = HD(hd_1='HIS_RECEPTOR')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260321100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260321100000'
        evn.event_occurred = '20260321100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='HOPN830752814027', cx_4='SNS', cx_5='HC', cx_8='20070101', cx_9='ESP&&ISO3166'),
            CX(cx_1='43917852K', cx_4='MI', cx_5='NNESP', cx_8='20070101', cx_9='ESP&&ISO3166'),
            CX(cx_1='51009', cx_4='HC', cx_5='PI', cx_9='ESP&&ISO3166'),
            CX(cx_1='2815400672301', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='FARIÑA', xpn_2='ANTIA')
        pid.mothers_maiden_name = XPN(xpn_1='PIÑEIRO')
        pid.date_time_of_birth = '19830712'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='PL&OBRADOIRO&7', xad_2='3oB', xad_3='150001', xad_4='15', xad_5='15001', xad_6='ESP', xad_7='M')
        pid.pid_13 = '^PRN^PH^^^981234567~^ORN^PH^^^981765432~^ORN^CP^^^678112233'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CHUS', pl_2='CCEE', pl_3='CONS12', pl_4='Consultas Externas')
        pv1.attending_doctor = XCN(xcn_1='78234', xcn_2='IGLESIAS', xcn_3='IRIA', xcn_4='NEIRA', xcn_9='CHUS')
        pv1.hospital_service = CWE(cwe_1='AMB')
        pv1.patient_type = CWE(cwe_1='EPIS20260321001', cwe_4='SERGAS')
        pv1.prior_temporary_location = PL(pl_1='20260321100000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SNS')
        in1.insurance_company_id = CX(cx_1='SERGAS001')
        in1.insurance_company_name = XON(xon_1='SERVIZO GALEGO DE SAUDE')
        in1.insurance_company_address = XAD(xad_1='Edificio Administrativo San Lazaro s/n', xad_3='Santiago de Compostela', xad_5='15703', xad_6='ESP')

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
    """ Based on live/es/es-ianus.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IANUS')
        msh.sending_facility = HD(hd_1='SERGAS_CHUVI')
        msh.receiving_application = HD(hd_1='HIS_RECEPTOR')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260322090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260322090000'
        evn.event_occurred = '20260322090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAGAL734859162037', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2'),
            CX(cx_1='51847293F', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='89012345', cx_4='HC', cx_5='PI', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='SEOANE', xpn_2='ROI')
        pid.mothers_maiden_name = XPN(xpn_1='VILABOA')
        pid.date_time_of_birth = '19790628'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = [
            XAD(xad_1='CL&PRINCIPE&18', xad_2='3o-B', xad_3='360001', xad_4='36', xad_5='36003', xad_6='ESP', xad_7='H'),
            XAD(xad_1='&&', xad_6='ESP', xad_7='M'),
        ]
        pid.pid_13 = '^PRN^PH^^^986234567~^WPN^CP^^^671988344~^NET^Internet^rseoane@sergas.gal'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHUVI', pl_2='PLANTA7', pl_3='CAMA722', pl_4='Traumatologia')
        pv1.attending_doctor = XCN(xcn_1='41298', xcn_2='CARBALLO', xcn_3='UXIA', xcn_4='PENA', xcn_9='CHUVI')
        pv1.hospital_service = CWE(cwe_1='TRA')
        pv1.patient_type = CWE(cwe_1='EPIS20260320001', cwe_4='SERGAS')
        pv1.prior_temporary_location = PL(pl_1='20260320110000')

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
    """ Based on live/es/es-ianus.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IANUS')
        msh.sending_facility = HD(hd_1='SERGAS_CHUAC')
        msh.receiving_application = HD(hd_1='HIS_RECEPTOR')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260323112947'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260323112947'
        evn.operator_id = XCN(xcn_1='IANUS')
        evn.event_occurred = '20260323112947'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='CAGAL610293847561', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2'),
            CX(cx_1='28924563P', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC770582', cx_4='CHUAC', cx_5='PI', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='CARREIRA', xpn_2='ANXO')
        pid.mothers_maiden_name = XPN(xpn_1='DOVAL')
        pid.date_time_of_birth = '19870419'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV&ROSALIA DE CASTRO&14', xad_3='15001', xad_4='15', xad_5='15001', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^^PH^^^^~^^CP^^^^~^^Internet^'
        pid.patient_death_date_and_time = 'N'
        pid.identity_reliability_code = CWE(cwe_1='20260101')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = [CX(cx_1='HC660899', cx_4='CHUAC', cx_5='PI'), CX(cx_1='CAGAL222333444555', cx_4='CAGA', cx_5='JHN')]

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
    """ Based on live/es/es-ianus.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IANUS')
        msh.sending_facility = HD(hd_1='SERGAS_CHUAC')
        msh.receiving_application = HD(hd_1='RADELEC')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260401085928'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='CAGAL610293847561', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2')
        pid.pid_4 = '28924563P^^^MI^NNESP'
        pid.patient_name = XPN(xpn_1='CARREIRA', xpn_2='ANXO')
        pid.mothers_maiden_name = XPN(xpn_1='DOVAL')
        pid.date_time_of_birth = '19870419'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHUAC', pl_2='PLANTA3', pl_3='CAMA301', pl_4='Medicina Interna')

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
        orc.placer_order_number = EI(ei_1='PET93071284', ei_2='IANUS')
        orc.parent_order = EIP(eip_1='20260401085928')
        orc.orc_11 = '54821^OTERO^XOAN^BAAMONDE^^^^^CHUAC'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET93071284', ei_2='IANUS')
        obr.universal_service_identifier = CWE(cwe_1='89001', cwe_2='Electrocardiograma 12 derivaciones', cwe_3='L')
        obr.observation_date_time = '20260401085928'

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
    """ Based on live/es/es-ianus.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IANUS')
        msh.sending_facility = HD(hd_1='SERGAS_CHUS')
        msh.receiving_application = HD(hd_1='RADELEC')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260402145211'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='CAGAL610293847561', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2')
        pid.pid_4 = '28924563P^^^MI^NNESP'
        pid.patient_name = XPN(xpn_1='CARREIRA', xpn_2='ANXO')
        pid.mothers_maiden_name = XPN(xpn_1='DOVAL')
        pid.date_time_of_birth = '19870419'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='CHUS', pl_2='UEPE', pl_3='0117M', pl_4='Urgencias')
        pv1.attending_doctor = XCN(xcn_1='78234', xcn_2='IGLESIAS', xcn_3='IRIA', xcn_4='NEIRA', xcn_9='CHUS')
        pv1.hospital_service = CWE(cwe_1='URGN')
        pv1.admit_source = CWE(cwe_1='PEDC')
        pv1.admitting_doctor = XCN(xcn_1='78234', xcn_2='IGLESIAS', xcn_3='IRIA', xcn_4='NEIRA', xcn_9='CHUS')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='EPIS2026040201', cx_4='CHUS')
        pv1.admit_date_time = '20260402112800'

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
        orc.placer_order_number = EI(ei_1='PET18894327', ei_2='IANUS')
        orc.placer_order_group_number = EI(ei_1='8421970', ei_2='IANUS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20260402134031^^1'
        orc.date_time_of_order_event = '20260402134031'
        orc.orc_12 = '78234^IGLESIAS^IRIA^NEIRA^^^^^CHUS'
        orc.orc_17 = '15705^Hospital Clinico Universitario Santiago^SERGAS_CHUS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET18894327', ei_2='IANUS')
        obr.universal_service_identifier = CWE(cwe_1='21780', cwe_2='Electrocardiograma (Radelec)', cwe_3='L')
        obr.observation_date_time = '20260402134031'
        obr.obr_16 = '78234^IGLESIAS^IRIA^NEIRA^^^^^CHUS'
        obr.obr_27 = '^^^^^1'
        obr.scheduled_date_time = '20260402134031'

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
    """ Based on live/es/es-ianus.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RADELEC')
        msh.sending_facility = HD(hd_1='SERGAS')
        msh.receiving_application = HD(hd_1='IANUS')
        msh.receiving_facility = HD(hd_1='SERGAS_CHUAC')
        msh.date_time_of_message = '20260403111704'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='CAGAL610293847561', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2')
        pid.pid_4 = '28924563P^^^MI^NNESP'
        pid.patient_name = XPN(xpn_1='CARREIRA', xpn_2='ANXO')
        pid.mothers_maiden_name = XPN(xpn_1='DOVAL')
        pid.date_time_of_birth = '19870419'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHUAC', pl_2='PLANTA3', pl_3='CAMA301', pl_4='Medicina Interna')

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
        orc.placer_order_number = EI(ei_1='PET93071284', ei_2='IANUS')
        orc.filler_order_number = EI(ei_1='RES202604030001', ei_2='RADELEC')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET93071284', ei_2='IANUS')
        obr.filler_order_number = EI(ei_1='RES202604030001', ei_2='RADELEC')
        obr.universal_service_identifier = CWE(cwe_1='89001', cwe_2='Electrocardiograma 12 derivaciones', cwe_3='L')
        obr.observation_date_time = '20260403111513'
        obr.filler_field_2 = 'bf7f74a0-c767-43af-9366-54fcc2db2b21'
        obr.results_rpt_status_chng_date_time = '20260403111513'
        obr.result_status = 'F'
        obr.obr_27 = '^^^^20260403111513'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='89001-1', cwe_2='Ritmo', cwe_3='L')
        obx.obx_5 = 'Ritmo sinusal, frecuencia 72 lpm'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='89001-2', cwe_2='Eje', cwe_3='L')
        obx_2.obx_5 = 'Eje normal, 60 grados'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='89001-3', cwe_2='Conclusion', cwe_3='L')
        obx_3.obx_5 = 'ECG dentro de limites normales. Sin alteraciones de la repolarizacion'
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
    """ Based on live/es/es-ianus.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABCORE')
        msh.sending_facility = HD(hd_1='SERGAS_CHUAC')
        msh.receiving_application = HD(hd_1='IANUS')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260404160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAGAL610293847561', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2'),
            CX(cx_1='28924563P', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='CARREIRA', xpn_2='ANXO')
        pid.mothers_maiden_name = XPN(xpn_1='DOVAL')
        pid.date_time_of_birth = '19870419'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHUAC', pl_2='PLANTA3', pl_3='CAMA301', pl_4='Medicina Interna')
        pv1.attending_doctor = XCN(xcn_1='54821', xcn_2='OTERO', xcn_3='XOAN', xcn_4='BAAMONDE', xcn_9='CHUAC')

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
        orc.placer_order_number = EI(ei_1='PET20260404001', ei_2='IANUS')
        orc.filler_order_number = EI(ei_1='LAB20260404001', ei_2='LABCORE')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET20260404001', ei_2='IANUS')
        obr.filler_order_number = EI(ei_1='LAB20260404001', ei_2='LABCORE')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Panel metabolico completo', cwe_3='LN')
        obr.observation_date_time = '20260404140000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucosa', cwe_3='LN')
        obx.obx_5 = '98'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-100'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinina', cwe_3='LN')
        obx_2.obx_5 = '0.9'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.7-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_3.obx_5 = '35'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '10-50'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Colesterol total', cwe_3='LN')
        obx_4.obx_5 = '210'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '<200'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Trigliceridos', cwe_3='LN')
        obx_5.obx_5 = '145'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '<150'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

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
    """ Based on live/es/es-ianus.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABHEMAT')
        msh.sending_facility = HD(hd_1='SERGAS_CHUS')
        msh.receiving_application = HD(hd_1='IANUS')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260405100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAGAL734859162037', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2'),
            CX(cx_1='51847293F', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='SEOANE', xpn_2='ROI')
        pid.mothers_maiden_name = XPN(xpn_1='VILABOA')
        pid.date_time_of_birth = '19950508'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CHUS', pl_2='CCEE', pl_3='CONS05', pl_4='Hematologia')

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
        orc.placer_order_number = EI(ei_1='PET20260405001', ei_2='IANUS')
        orc.filler_order_number = EI(ei_1='LAB20260405001', ei_2='LABHEMAT')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET20260405001', ei_2='IANUS')
        obr.filler_order_number = EI(ei_1='LAB20260405001', ei_2='LABHEMAT')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Hemograma completo', cwe_3='LN')
        obr.observation_date_time = '20260405090000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocitos', cwe_3='LN')
        obx.obx_5 = '7.2'
        obx.units = CWE(cwe_1='10*3/uL')
        obx.reference_range = '4.0-11.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Eritrocitos', cwe_3='LN')
        obx_2.obx_5 = '4.5'
        obx_2.units = CWE(cwe_1='10*6/uL')
        obx_2.reference_range = '3.8-5.2'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobina', cwe_3='LN')
        obx_3.obx_5 = '13.8'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '12.0-16.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrito', cwe_3='LN')
        obx_4.obx_5 = '41.2'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '36.0-46.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Plaquetas', cwe_3='LN')
        obx_5.obx_5 = '245'
        obx_5.units = CWE(cwe_1='10*3/uL')
        obx_5.reference_range = '150-400'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

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
    """ Based on live/es/es-ianus.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IANUS')
        msh.sending_facility = HD(hd_1='SERGAS_CHUAC')
        msh.receiving_application = HD(hd_1='EMPI')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260406101935'
        msh.message_type = MSG(msg_1='QBP', msg_2='Q22')
        msh.message_control_id = 'MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='1', cwe_2='IHE PDQ Query', cwe_3='HL70471')
        qpd.query_tag = 'QRY20260406001'
        qpd.qpd_3 = 'CIPAUT^CAGAL610293847561'

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
    """ Based on live/es/es-ianus.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMPI')
        msh.sending_facility = HD(hd_1='SERGAS')
        msh.receiving_application = HD(hd_1='IANUS')
        msh.receiving_facility = HD(hd_1='SERGAS_CHUAC')
        msh.date_time_of_message = '20260406101936'
        msh.message_type = MSG(msg_1='RSP', msg_2='K22')
        msh.message_control_id = 'MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MSG00012'

        # .. build ERR ..
        err = ERR()
        err.hl7_error_code = CWE(cwe_1='0', cwe_2='Message accepted', cwe_3='HL70357', cwe_4='0', cwe_5='Procesado correctamente', cwe_6='SERGAS_ERROR')
        err.severity = 'I'

        # .. build QAK ..
        qak = QAK()
        qak.query_tag = 'QRY20260406001'
        qak.query_response_status = 'OK'

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='1', cwe_2='IHE PDQ Query', cwe_3='HL70471')
        qpd.query_tag = 'QRY20260406001'
        qpd.qpd_3 = 'CIPAUT^CAGAL610293847561'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAGAL610293847561', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2'),
            CX(cx_1='28924563P', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC770582', cx_4='CHUAC', cx_5='PI', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='CARREIRA', xpn_2='ANXO')
        pid.mothers_maiden_name = XPN(xpn_1='DOVAL')
        pid.date_time_of_birth = '19870419'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV&ROSALIA DE CASTRO&14', xad_2='2o-1a', xad_3='15001', xad_4='15', xad_5='15001', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^981345678'
        pid.patient_death_date_and_time = 'N'

        # .. build QRI ..
        qri = QRI()
        qri.candidate_confidence = '1'

        # .. build the QUERY_RESPONSE group ..
        query_response = RspK22QueryResponse()
        query_response.pid = pid
        query_response.qri = qri

        # .. assemble the full message ..
        msg = RSP_K22()
        msg.msh = msh
        msg.msa = msa
        msg.err = err
        msg.qak = qak
        msg.qpd = qpd
        msg.query_response = query_response

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
    """ Based on live/es/es-ianus.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IANUS')
        msh.sending_facility = HD(hd_1='SERGAS_CHUAC')
        msh.receiving_application = HD(hd_1='BBANK')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260407090131'
        msh.message_type = MSG(msg_1='OMB', msg_2='O27', msg_3='OMB_O27')
        msh.message_control_id = 'MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAGAL610293847561', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2'),
            CX(cx_1='SHJD420903821037', cx_4='MS', cx_5='HC', cx_9='ESP&&ISO3166'),
            CX(cx_1='28924563P', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='071385660429', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='CARREIRA', xpn_2='ANXO')
        pid.mothers_maiden_name = XPN(xpn_1='DOVAL')
        pid.date_time_of_birth = '19870419'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = [
            XAD(xad_1='CL&CURROS ENRIQUEZ&55', xad_2='CENTRO SALUD', xad_3='15001', xad_4='15', xad_5='15001', xad_6='ESP', xad_7='H'),
            XAD(xad_1='&&', xad_6='ESP', xad_7='M'),
        ]
        pid.pid_13 = '^PRN^PH^^^^^^^^^981223344'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHUAC', pl_2='PLANTA3', pl_3='CAMA301', pl_4='Medicina Interna')
        pv1.attending_doctor = XCN(xcn_1='54821', xcn_2='OTERO', xcn_3='XOAN', xcn_4='BAAMONDE', xcn_9='CHUAC')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.visit_number = CX(cx_1='EPIS20260315001', cx_4='SERGAS')
        pv1.pv1_51 = ''

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
        spm.specimen_identifier = EIP(eip_1='PET13567892')

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='PET13567892', ei_2='IANUS')
        orc.filler_order_number = EI(ei_1='RES22233444', ei_2='BBANK')
        orc.date_time_of_order_event = '20260407090000'
        orc.orc_10 = 'OTERO, XOAN'
        orc.orc_11 = 'OTERO, XOAN'
        orc.orc_12 = '54821^OTERO^XOAN^BAAMONDE^^^^^CHUAC'
        orc.orc_18 = 'OTERO, XOAN'

        # .. build BPO ..
        bpo = BPO()
        bpo.set_id_bpo = 'CHEM^Concentrado de Hematies'
        bpo.bp_universal_service_identifier = CWE(cwe_1='2')
        bpo.bp_quantity = '2'
        bpo.bp_units = CWE(cwe_1='20260406200001')
        bpo.bpo_7 = 'P121^^^^'
        bpo.bp_intended_dispense_from_address = XAD(xad_1='20260406211001')
        bpo.bpo_10 = 'P121^^^^'
        bpo.bpo_14 = ''

        # .. build BPO ..
        bpo_2 = BPO()
        bpo_2.set_id_bpo = 'PQ^Pool Plaquetas'
        bpo_2.bp_universal_service_identifier = CWE(cwe_1='1')
        bpo_2.bp_quantity = '1'
        bpo_2.bp_units = CWE(cwe_1='20260406120001')
        bpo_2.bpo_7 = 'P121^^^^'
        bpo_2.bp_intended_dispense_from_address = XAD(xad_1='20260406211001')
        bpo_2.bpo_10 = 'P121^^^^'
        bpo_2.bpo_14 = ''

        # .. assemble the full message ..
        msg = OMB_O27()
        msg.msh = msh
        msg.patient = patient
        msg.extra_segments = [spm, orc, bpo, bpo_2]

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
    """ Based on live/es/es-ianus.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IANUS')
        msh.sending_facility = HD(hd_1='SERGAS_CHUAC')
        msh.receiving_application = HD(hd_1='BBANK')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260407090200'
        msh.message_type = MSG(msg_1='ACK', msg_3='ACK')
        msh.message_control_id = 'MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AR'
        msa.message_control_id = 'MSG00014'

        # .. build ERR ..
        err = ERR()
        err.err_1 = 'PID^1^16^103&Table value not found&HL70357'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa
        msg.err = err

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
    """ Based on live/es/es-ianus.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IANUS')
        msh.sending_facility = HD(hd_1='SERGAS_CHUVI')
        msh.receiving_application = HD(hd_1='RIS_RECEPTOR')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260408113000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAGAL734859162037', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2'),
            CX(cx_1='51847293F', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='SEOANE', xpn_2='ROI')
        pid.mothers_maiden_name = XPN(xpn_1='VILABOA')
        pid.date_time_of_birth = '19790628'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&PRINCIPE&18', xad_2='3o-B', xad_3='360001', xad_4='36', xad_5='36003', xad_6='ESP', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='CHUVI', pl_2='URG', pl_3='BOX03', pl_4='Urgencias')
        pv1.attending_doctor = XCN(xcn_1='41298', xcn_2='CARBALLO', xcn_3='UXIA', xcn_4='PENA', xcn_9='CHUVI')
        pv1.hospital_service = CWE(cwe_1='URG')

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
        orc.placer_order_number = EI(ei_1='PET20260408001', ei_2='IANUS')
        orc.parent_order = EIP(eip_1='20260408113000')
        orc.orc_11 = '41298^CARBALLO^UXIA^PENA^^^^^CHUVI'
        orc.order_control_code_reason = CWE(cwe_1='36204', cwe_2='Hospital Alvaro Cunqueiro', cwe_3='SERGAS_CHUVI')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET20260408001', ei_2='IANUS')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Radiografia torax PA y lateral', cwe_3='SERAM')
        obr.observation_date_time = '20260408113000'
        obr.danger_code = CWE(cwe_1='STAT')
        obr.obr_14 = '41298^CARBALLO^UXIA^PENA^^^^^CHUVI'

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
    """ Based on live/es/es-ianus.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS_XESTION')
        msh.sending_facility = HD(hd_1='SERGAS_CHUAC')
        msh.receiving_application = HD(hd_1='IANUS')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260409150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAGAL734859162037', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2'),
            CX(cx_1='51847293F', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='SEOANE', xpn_2='ROI')
        pid.mothers_maiden_name = XPN(xpn_1='VILABOA')
        pid.date_time_of_birth = '19790628'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='CHUVI', pl_2='URG', pl_3='BOX03', pl_4='Urgencias')

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
        orc.placer_order_number = EI(ei_1='PET20260408001', ei_2='IANUS')
        orc.filler_order_number = EI(ei_1='INF20260409001', ei_2='RIS_XESTION')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET20260408001', ei_2='IANUS')
        obr.filler_order_number = EI(ei_1='INF20260409001', ei_2='RIS_XESTION')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Radiografia torax PA y lateral', cwe_3='SERAM')
        obr.observation_date_time = '20260409143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='71020-1', cwe_2='Hallazgos', cwe_3='L')
        obx.obx_5 = 'Indice cardiotoracio normal. Campos pulmonares sin infiltrados. Senos costodiafragmaticos libres. Sin derrame pleural.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'RP'
        obx_2.observation_identifier = CWE(cwe_1='71020-2', cwe_2='Informe PDF', cwe_3='L')
        obx_2.obx_5 = 'https://ianus.sergas.gal/informes/INF20260409001.pdf^^APPLICATION^^'
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
    """ Based on live/es/es-ianus.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IANUS')
        msh.sending_facility = HD(hd_1='SERGAS_CHUAC')
        msh.receiving_application = HD(hd_1='HCE_RECEPTOR')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260410100000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260410100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAGAL610293847561', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2'),
            CX(cx_1='28924563P', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='CARREIRA', xpn_2='ANXO')
        pid.mothers_maiden_name = XPN(xpn_1='DOVAL')
        pid.date_time_of_birth = '19870419'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHUAC', pl_2='PLANTA3', pl_3='CAMA301', pl_4='Medicina Interna')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='HP', cwe_2='Informe de Alta', cwe_3='L')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260410100000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='54821', xcn_2='OTERO', xcn_3='XOAN', xcn_4='BAAMONDE', xcn_9='CHUAC')
        txa.transcription_date_time = '20260410100000'
        txa.parent_document_number = EI(ei_1='DOC20260410001')
        txa.document_confidentiality_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='18842-5', cwe_2='Informe de alta hospitalaria', cwe_3='LN')
        obx.obx_5 = (
            '^APPLICATION^PDF^Base64^'
            'JVBERi0xLjcNCiW1tbW1DQoxIDAgb2JqDQo8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4NCmVuZG9iag0KDQoyIDAgb2JqDQo8PCAvVHlwZSAvUGFnZXMgL0tpZHMgWzMg'
            'MCBSXSAvQ291bnQgMSA+Pg0KZW5kb2JqDQoNCjMgMCBvYmoNCjw8IC9UeXBlIC9QYWdlIC9QYXJlbnQgMiAwIFIgL01lZGlhQm94IFswIDAgNjEyIDc5Ml0gPj4NCmVuZG9iag0KDQp4'
            'cmVmDQowIDQNCjAwMDAwMDAwMDAgNjU1MzUgZg0KMDAwMDAwMDAxNSAwMDAwMCBuDQowMDAwMDAwMDc0IDAwMDAwIG4NCjAwMDAwMDAxNDMgMDAwMDAgbg0KDQp0cmFpbGVyDQo8PCAv'
            'U2l6ZSA0IC9Sb290IDEgMCBSID4+DQpzdGFydHhyZWYNCjIzNg0KJSVFT0YNCg=='
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
    """ Based on live/es/es-ianus.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENDOSC')
        msh.sending_facility = HD(hd_1='SERGAS_CHUAC')
        msh.receiving_application = HD(hd_1='IANUS')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260411140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAGAL610293847561', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2'),
            CX(cx_1='28924563P', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='CARREIRA', xpn_2='ANXO')
        pid.mothers_maiden_name = XPN(xpn_1='DOVAL')
        pid.date_time_of_birth = '19870419'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHUAC', pl_2='PLANTA3', pl_3='CAMA301', pl_4='Medicina Interna')

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
        orc.placer_order_number = EI(ei_1='PET20260411001', ei_2='IANUS')
        orc.filler_order_number = EI(ei_1='END20260411001', ei_2='ENDOSC')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET20260411001', ei_2='IANUS')
        obr.filler_order_number = EI(ei_1='END20260411001', ei_2='ENDOSC')
        obr.universal_service_identifier = CWE(cwe_1='43239', cwe_2='Esofagogastroduodenoscopia diagnostica', cwe_3='CPT')
        obr.observation_date_time = '20260411130000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='43239-1', cwe_2='Hallazgos', cwe_3='L')
        obx.obx_5 = (
            'Mucosa esofagica de aspecto normal. Hernia de hiato por deslizamiento de 2 cm. Mucosa gastrica con eritema leve antral. Duodeno sin alteraci'
            'ones.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='43239-2', cwe_2='Imagen endoscopica', cwe_3='L')
        obx_2.obx_5 = (
            '^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/4gIcSUNDX1BST0ZJTEUAAQEAAAIMbGNtcwIQAABtbnRyUkdCIFhZWiAH3AABABkAAwApADlhY3NwQVBQTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            'APbWAAEAAAAA0y1sY21zAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKZGVzYwAAAP/aAAwDAQACEQMRAD8A3+AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH//Z'
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
    """ Based on live/es/es-ianus.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IANUS')
        msh.sending_facility = HD(hd_1='SERGAS_CHUS')
        msh.receiving_application = HD(hd_1='CITAWEB')
        msh.receiving_facility = HD(hd_1='SERGAS')
        msh.date_time_of_message = '20260412080000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='CITA20260420001', ei_2='IANUS')
        sch.appointment_reason = CWE(cwe_1='CONSULTA', cwe_2='Consulta Cardiologia', cwe_4='20', cwe_5='MIN')
        sch.appointment_type = CWE(cwe_4='20260420090000', cwe_5='20260420091500')
        sch.sch_9 = '54821^OTERO^XOAN^BAAMONDE^^^^^CHUS'
        sch.appointment_duration_units = CNE(cne_3='PH', cne_6='981876543')
        sch.sch_11 = '54821^OTERO^XOAN^BAAMONDE^^^^^CHUS'
        sch.placer_contact_person = XCN(xcn_3='PH', xcn_6='981876543')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CAGAL610293847561', cx_4='CAGA', cx_5='JHN', cx_9='GA&&ISO3166-2'),
            CX(cx_1='28924563P', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='CARREIRA', xpn_2='ANXO')
        pid.mothers_maiden_name = XPN(xpn_1='DOVAL')
        pid.date_time_of_birth = '19870419'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV&ROSALIA DE CASTRO&14', xad_2='2o-1a', xad_3='15001', xad_4='15', xad_5='15001', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^981345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CHUS', pl_2='CCEE', pl_3='CONS03', pl_4='Cardiologia')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.resource_id = CWE(cwe_1='54821', cwe_2='OTERO', cwe_3='XOAN', cwe_4='BAAMONDE', cwe_9='CHUS')

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SiuS12GeneralResource()
        general_resource.aig = aig

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='CHUS', pl_2='CCEE', pl_3='CONS03', pl_4='Cardiologia')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.general_resource = general_resource
        resources.location_resource = location_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
