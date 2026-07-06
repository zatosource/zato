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
from zato.hl7v2.v2_9.datatypes import AUI, CNE, CWE, CX, EI, EIP, HD, MOC, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA05Insurance, AdtA39Patient, MdmT02Observation, OmbO27Patient, OmbO27PatientVisit, OrmO01Observation, \
    OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, \
    OruR01PatientResult, OruR01Visit, SiuS12Patient, SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, OMB_O27, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, BPO, DG1, EVN, IN1, MRG, MSA, MSH, NTE, OBR, OBX, ORC, PID, PV1, RGS, SCH, SPM, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('es', 'es-salut4d.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/es/es-salut4d.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='HVST')
        msh.receiving_application = HD(hd_1='IS3')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260101120000'
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
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260101120000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='HOPN830752418023', cx_4='SNS', cx_5='HC', cx_8='20070101', cx_9='ESP&&ISO3166'),
            CX(cx_1='00000004T', cx_4='MI', cx_5='NNESP', cx_8='20070101', cx_9='ESP&&ISO3166'),
            CX(cx_1='40009', cx_4='HC', cx_5='PI', cx_9='ESP&&ISO3166'),
            CX(cx_1='2803800997601', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='GISPERT', xpn_2='EULALIA')
        pid.mothers_maiden_name = XPN(xpn_1='TORRENT')
        pid.date_time_of_birth = '19830601'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CL&RAMBLA NOVA&14', xad_2='2nB', xad_3='430040', xad_4='43', xad_5='43004', xad_6='ESP', xad_7='M')
        pid.pid_13 = '^PRN^PH^^^977642318~^ORN^PH^^^977334455~^ORN^CP^^^661223344'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='URG', pl_2='BOX03', pl_3='01', pl_4='HVST')
        pv1.attending_doctor = XCN(xcn_1='18923', xcn_2='QUERALT', xcn_3='JORDI', xcn_4='FONTANA', xcn_8='')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.visit_number = CX(cx_1='EP001', cx_4='HVST')
        pv1.admit_date_time = '20260101115500'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SNS001', cwe_2='SISTEMA NACIONAL DE SALUD')
        in1.insurance_company_id = CX(cx_1='SNS')
        in1.insurance_company_name = XON(xon_1='SERVICIO DE SALUD DE CASTILLA-LA MANCHA')
        in1.plan_expiration_date = '20230101'
        in1.authorization_information = AUI(aui_1='20261231')

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
    """ Based on live/es/es-salut4d.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='HINFANTA')
        msh.receiving_application = HD(hd_1='IS3')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260115083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260115083000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='41827394K', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='CATA987612345077', cx_4='CACT', cx_5='JHN', cx_9='CT&&ISO3166-2'),
            CX(cx_1='061081223456', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
            CX(cx_1='7743218', cx_4='HC', cx_5='PI'),
        ]
        pid.date_time_of_birth = 'COSTA^LLUIS'
        pid.administrative_sex = CWE(cwe_1='FERRER')
        pid.pid_9 = '19810924'
        pid.race = CWE(cwe_1='M')
        pid.pid_13 = 'AV&DIAGONAL&120^3r 1a^080060^08^08006^ESP^H~CL&PROVENCA&85^2n B^080290^08^08029^ESP^M'
        pid.pid_15 = '^PRN^PH^^+34^934553201~^WPN^CP^^+34^667443291~^NET^Internet^lcosta@correu.cat'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CIRUGIA', pl_2='HAB201', pl_3='C1', pl_4='HINFANTA')
        pv1.attending_doctor = XCN(xcn_1='ATT002', xcn_2='BALCELLS', xcn_3='NURIA', xcn_4='CAPDEVILA', xcn_8='')
        pv1.hospital_service = CWE(cwe_1='CIR')
        pv1.visit_number = CX(cx_1='EP002', cx_4='HINFANTA')
        pv1.admit_date_time = '20260115082500'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='CATSALUT', cwe_2='SERVEI CATALA DE LA SALUT')
        in1.insurance_company_id = CX(cx_1='CATSALUT')
        in1.insurance_company_name = XON(xon_1='CATSALUT - DEPARTAMENT DE SALUT')
        in1.insurance_company_address = XAD(xad_1='Travessera de les Corts 131-159', xad_3='Barcelona', xad_5='08028', xad_6='ESP')
        in1.plan_expiration_date = '20240101'
        in1.authorization_information = AUI(aui_1='20261231')

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
    """ Based on live/es/es-salut4d.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='hphis')
        msh.sending_facility = HD(hd_1='192.168.2.203')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.date_time_of_message = '20250911093851'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ITM14AAACVDD'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.pid_2 = '349711'
        pid.pid_4 = 'ROVE0480503001'
        pid.patient_name = XPN(xpn_1='DURAN', xpn_2='LAIA', xpn_3='NURIA')
        pid.date_time_of_birth = '19800417'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='BARCELONA', xad_3='BARCELONA', xad_4='8', xad_5='08620', xad_6='724', xad_8='1')
        pid.pid_13 = '634512789'
        pid.pid_14 = '634512789'
        pid.pid_19 = '08/04481923-71'
        pid.pid_20 = '63847291H'
        pid.pid_28 = '724'
        pid.patient_death_indicator = 'no'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.admission_type = CWE(cwe_1='O')
        pv1.attending_doctor = [XCN(xcn_1='2207', xcn_2='DURAN', xcn_3='LAIA', xcn_4='NURIA'), XCN(xcn_1='2207')]
        pv1.referring_doctor = [XCN(xcn_1='2207', xcn_2='DURAN', xcn_3='LAIA', xcn_4='NURIA'), XCN(xcn_1='2207')]
        pv1.hospital_service = CWE(cwe_1='DIGC')
        pv1.admitting_doctor = [XCN(xcn_1='2207', xcn_2='DURAN', xcn_3='LAIA', xcn_4='NURIA'), XCN(xcn_1='2207')]
        pv1.visit_number = CX(cx_1='408253671')
        pv1.admit_date_time = '20250911104000'

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
        orc.placer_order_group_number = EI(ei_1='2891034')
        orc.order_status = 'HD'
        orc.orc_7 = '^^^^^1'
        orc.date_time_of_order_event = '20250911093800000'
        orc.orc_12 = '3318^DURAN^LAIA'
        orc.enterers_location = PL(pl_1='CIRC')
        orc.order_control_code_reason = CWE(cwe_2='REASON 1')

        # .. build OBR ..
        obr = OBR()
        obr.obr_2 = '\\X00\\'
        obr.universal_service_identifier = CWE(cwe_1='1', cwe_2='INTERTEST')
        obr.collector_identifier = XCN(xcn_2='S/I', xcn_3='S/I')
        obr.obr_16 = '3318^CAMPMANY^MARTA'
        obr.placer_field_2 = 'CIRC'
        obr.filler_field_2 = 'DIGH'
        obr.obr_27 = '^^^^^1'
        obr.reason_for_study = CWE(cwe_1='REASON 2')

        # .. build NTE ..
        nte = NTE()
        nte.comment = 'TEST NOTES'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='4')
        obx.observation_sub_id = OG(og_1='7')
        obx.obx_5 = 'ABCD1234'

        # .. build the OBSERVATION group ..
        observation = OrmO01Observation()
        observation.obx = obx

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.nte = nte
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
    """ Based on live/es/es-salut4d.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS')
        msh.sending_facility = HD(hd_1='HOSPITAL')
        msh.receiving_application = HD(hd_1='BBANK')
        msh.receiving_facility = HD(hd_1='EXTERNO')
        msh.date_time_of_message = '20250829090131'
        msh.message_type = MSG(msg_1='OMB', msg_2='O27', msg_3='OMB_O27')
        msh.message_control_id = '23456789'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='33224455', cx_4='HIS', cx_5='PI', cx_9='2828&&'),
            CX(cx_1='SHJD450901722038', cx_4='MS', cx_5='HC', cx_9='ESP&&ISO3166'),
            CX(cx_1='2220003300', cx_4='CA13', cx_5='JHN', cx_9='CL&&ISO3166-2'),
            CX(cx_1='44335566', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='33/00000002/01', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='CORTADA', xpn_2='ANNA')
        pid.mothers_maiden_name = XPN(xpn_1='ROVIRA')
        pid.date_time_of_birth = '19850713'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [
            XAD(xad_1='CL&ANTONIO MACHADO&45', xad_2='CENTRO SALUD', xad_3='28078', xad_4='28', xad_5='28048', xad_6='ESP', xad_7='H', xad_8='MADRID'),
            XAD(xad_1='&&', xad_6='ESP', xad_7='M', xad_8=''),
        ]
        pid.pid_13 = '^PRN^PH^^^^^^^^^667889900'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_3='405C', pl_4='')
        pv1.attending_doctor = XCN(xcn_1='777', xcn_2='CODINA', xcn_3='MERCE', xcn_4='ARMENGOL', xcn_8='')
        pv1.hospital_service = CWE(cwe_1='MIN')
        pv1.visit_number = CX(cx_1='23456', cx_6='')
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
        spm.specimen_identifier = EIP(eip_1='22345667')

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='22345667')
        orc.filler_order_number = EI(ei_1='22222333')
        orc.date_time_of_order_event = '20250829090000'
        orc.orc_10 = 'CODINA, MERCE'
        orc.orc_11 = 'CODINA, MERCE'
        orc.orc_12 = '7249^CODINA^MERCE^ARMENGOL'
        orc.orc_18 = 'CODINA, MERCE'

        # .. build BPO ..
        bpo = BPO()
        bpo.set_id_bpo = 'CHEM^Concentrado de Hematíes'
        bpo.bp_universal_service_identifier = CWE(cwe_1='2')
        bpo.bp_quantity = '2'
        bpo.bp_units = CWE(cwe_1='20250828200001')
        bpo.bpo_7 = 'P121^^^^'
        bpo.bp_intended_dispense_from_address = XAD(xad_1='20250828211001')
        bpo.bpo_10 = 'P121^^^^'
        bpo.bpo_14 = ''

        # .. build BPO ..
        bpo_2 = BPO()
        bpo_2.set_id_bpo = 'PQ^Pool Plaquetas'
        bpo_2.bp_universal_service_identifier = CWE(cwe_1='1')
        bpo_2.bp_quantity = '1'
        bpo_2.bp_units = CWE(cwe_1='202508281200001')
        bpo_2.bpo_7 = 'P121^^^^'
        bpo_2.bp_intended_dispense_from_address = XAD(xad_1='20250828211001')
        bpo_2.bpo_10 = 'P121^^^^'
        bpo_2.bpo_14 = ''

        # .. assemble the full message ..
        msg = OMB_O27()
        msg.msh = msh
        msg.patient = patient
        msg.extra_segments = [spm, orc, bpo, bpo_2]

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
    """ Based on live/es/es-salut4d.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='HTRUETA')
        msh.receiving_application = HD(hd_1='IS3')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260210091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260210091500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CATA543219876054', cx_4='CACT', cx_5='JHN', cx_9='CT&&ISO3166-2'),
            CX(cx_1='52143678W', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='9876543210', cx_4='HC', cx_5='PI', cx_9='HTRUETA&&'),
            CX(cx_1='280560087654', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='BATET', xpn_2='ARNAU')
        pid.mothers_maiden_name = XPN(xpn_1='PUIGVERT')
        pid.date_time_of_birth = '19910808'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&INDEPENDENCIA&45', xad_2='3r 2a', xad_3='170040', xad_4='17', xad_5='17004', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^+34^972334567~^WPN^CP^^+34^619876543'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CEXT', pl_2='CONS07', pl_3='01', pl_4='HTRUETA')
        pv1.attending_doctor = XCN(xcn_1='91234', xcn_2='CAMPMANY', xcn_3='MARTA', xcn_4='SOBREGRAU', xcn_8='')
        pv1.hospital_service = CWE(cwe_1='DER')
        pv1.visit_number = CX(cx_1='CEX003', cx_4='HTRUETA')
        pv1.admit_date_time = '20260210091000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='CATSALUT', cwe_2='SERVEI CATALA DE LA SALUT')
        in1.insurance_company_id = CX(cx_1='CATSALUT')
        in1.insurance_company_name = XON(xon_1='CATSALUT - DEPARTAMENT DE SALUT')
        in1.insurance_company_address = XAD(xad_1='Travessera de les Corts 131-159', xad_3='Barcelona', xad_5='08028', xad_6='ESP')
        in1.plan_expiration_date = '20250101'
        in1.authorization_information = AUI(aui_1='20261231')

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
    """ Based on live/es/es-salut4d.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='HBELLVITGE')
        msh.receiving_application = HD(hd_1='IS3')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260305143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260305143000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CATA223344556677', cx_4='CACT', cx_5='JHN', cx_9='CT&&ISO3166-2'),
            CX(cx_1='87654321Y', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='6781234', cx_4='HC', cx_5='PI', cx_9='HBELLVITGE&&'),
        ]
        pid.patient_name = XPN(xpn_1='VILADOMAT', xpn_2='CARME')
        pid.mothers_maiden_name = XPN(xpn_1='SOLER')
        pid.date_time_of_birth = '19930227'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV&DIAGONAL&250', xad_2='5e 3a', xad_3='080060', xad_4='08', xad_5='08006', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^+34^935678123~^WPN^CP^^+34^651234567~^NET^Internet^cviladomat@correu.cat'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GINECO', pl_2='HAB305', pl_3='B2', pl_4='HBELLVITGE')
        pv1.attending_doctor = XCN(xcn_1='38901', xcn_2='CODINA', xcn_3='MERCE', xcn_4='ARMENGOL', xcn_8='')
        pv1.hospital_service = CWE(cwe_1='GIN')
        pv1.visit_number = CX(cx_1='EP004', cx_4='HBELLVITGE')
        pv1.admit_date_time = '20260303100000'

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
    """ Based on live/es/es-salut4d.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='HVALLHEBRON')
        msh.receiving_application = HD(hd_1='IS3')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260401160000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260401160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CATA667788990012', cx_4='CACT', cx_5='JHN', cx_9='CT&&ISO3166-2'),
            CX(cx_1='74123698B', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='8901234', cx_4='HC', cx_5='PI', cx_9='HVALLHEBRON&&'),
        ]
        pid.patient_name = XPN(xpn_1='BERTRAN', xpn_2='XAVIER')
        pid.mothers_maiden_name = XPN(xpn_1='CASALS')
        pid.date_time_of_birth = '19710523'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1="PG&VALL D'HEBRON&119-129", xad_3='080350', xad_4='08', xad_5='08035', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^+34^932746111'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCI', pl_2='BOX08', pl_3='01', pl_4='HVALLHEBRON')
        pv1.attending_doctor = XCN(xcn_1='62345', xcn_2='GASULL', xcn_3='PERE', xcn_4='VILADECANS', xcn_8='')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.preadmit_test_indicator = CWE(cwe_1='MED', cwe_2='HAB412', cwe_3='B1', cwe_4='HVALLHEBRON')
        pv1.pv1_20 = 'EP005^^^HVALLHEBRON'
        pv1.discharge_date_time = '20260330080000'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/es/es-salut4d.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='HARNAU')
        msh.receiving_application = HD(hd_1='IS3')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260415120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260415120000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CATA881122990044', cx_4='CACT', cx_5='JHN', cx_9='CT&&ISO3166-2'),
            CX(cx_1='31245678C', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='5678901', cx_4='HC', cx_5='PI', cx_9='HARNAU&&'),
        ]
        pid.patient_name = XPN(xpn_1='OLLER', xpn_2='JUDIT')
        pid.mothers_maiden_name = XPN(xpn_1='PLANA')
        pid.date_time_of_birth = '19840314'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CL&SANT PAU&2', xad_3='250040', xad_4='25', xad_5='25004', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^+34^973567890~^WPN^CP^^+34^679012345'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TRAUMA', pl_2='HAB110', pl_3='A1', pl_4='HARNAU')
        pv1.attending_doctor = XCN(xcn_1='27891', xcn_2='BARGALLO', xcn_3='SERGI', xcn_4='VENDRELL', xcn_8='')
        pv1.hospital_service = CWE(cwe_1='TRA')
        pv1.visit_number = CX(cx_1='EP006', cx_4='HARNAU')
        pv1.admit_date_time = '20260410140000'
        pv1.discharge_date_time = '20260415120000'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/es/es-salut4d.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='HTRUETA')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260220103000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
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
        pid.patient_identifier_list = [
            CX(cx_1='CATA445566778811', cx_4='CACT', cx_5='JHN', cx_9='CT&&ISO3166-2'),
            CX(cx_1='41237890D', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='3456712', cx_4='HC', cx_5='PI', cx_9='HTRUETA&&'),
        ]
        pid.patient_name = XPN(xpn_1='ROURE', xpn_2='GUILLEM')
        pid.mothers_maiden_name = XPN(xpn_1='NADAL')
        pid.date_time_of_birth = '19590218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&MIGDIA&15', xad_3='170020', xad_4='17', xad_5='17002', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^+34^972456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUMO', pl_2='HAB207', pl_3='B1', pl_4='HTRUETA')
        pv1.attending_doctor = XCN(xcn_1='49012', xcn_2='PLANAS', xcn_3='GLORIA', xcn_4='BADIA', xcn_8='')
        pv1.hospital_service = CWE(cwe_1='NEU')
        pv1.visit_number = CX(cx_1='EP007', cx_4='HTRUETA')
        pv1.admit_date_time = '20260218090000'

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
        orc.placer_order_number = EI(ei_1='RAD00123', ei_2='SAP-ISH')
        orc.placer_order_group_number = EI(ei_1='GRP001', ei_2='SAP-ISH')
        orc.date_time_of_order_event = '20260220103000'
        orc.orc_12 = '49012^PLANAS^GLORIA^BADIA^^^^'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD00123', ei_2='SAP-ISH')
        obr.universal_service_identifier = CWE(cwe_1='71046-1', cwe_2='Radiografia torax PA y lateral', cwe_3='LN')
        obr.observation_date_time = '20260220103000'
        obr.obr_16 = '49012^PLANAS^GLORIA^BADIA^^^^'
        obr.obr_27 = '^ROUTINE'

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
        nte.comment = 'Control evolutivo neumonia bilateral'

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
    """ Based on live/es/es-salut4d.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB')
        msh.sending_facility = HD(hd_1='HTRUETA')
        msh.receiving_application = HD(hd_1='SAP-ISH')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260221090000'
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
            CX(cx_1='CATA445566778811', cx_4='CACT', cx_5='JHN', cx_9='CT&&ISO3166-2'),
            CX(cx_1='41237890D', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='3456712', cx_4='HC', cx_5='PI', cx_9='HTRUETA&&'),
        ]
        pid.patient_name = XPN(xpn_1='ROURE', xpn_2='GUILLEM')
        pid.mothers_maiden_name = XPN(xpn_1='NADAL')
        pid.date_time_of_birth = '19590218'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUMO', pl_2='HAB207', pl_3='B1', pl_4='HTRUETA')

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
        orc.placer_order_number = EI(ei_1='LAB00456', ei_2='LAB')
        orc.filler_order_number = EI(ei_1='ORD00789', ei_2='SAP-ISH')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB00456', ei_2='LAB')
        obr.filler_order_number = EI(ei_1='ORD00789', ei_2='SAP-ISH')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Panel metabolico completo', cwe_3='LN')
        obr.observation_date_time = '20260220150000'
        obr.obr_14 = '49012^PLANAS^GLORIA^BADIA^^^^'
        obr.filler_field_1 = '20260221085000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucosa', cwe_3='LN')
        obx.obx_5 = '105'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-100'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinina', cwe_3='LN')
        obx_2.obx_5 = '1.3'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.6-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='BUN', cwe_3='LN')
        obx_3.obx_5 = '22'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '7-20'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodio', cwe_3='LN')
        obx_4.obx_5 = '138'
        obx_4.units = CWE(cwe_1='mEq/L')
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
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potasio', cwe_3='LN')
        obx_5.obx_5 = '4.5'
        obx_5.units = CWE(cwe_1='mEq/L')
        obx_5.reference_range = '3.5-5.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='17861-6', cwe_2='Calcio', cwe_3='LN')
        obx_6.obx_5 = '9.2'
        obx_6.units = CWE(cwe_1='mg/dL')
        obx_6.reference_range = '8.5-10.5'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx_7.obx_5 = '45'
        obx_7.units = CWE(cwe_1='U/L')
        obx_7.reference_range = '7-56'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocitos', cwe_3='LN')
        obx_8.obx_5 = '12800'
        obx_8.units = CWE(cwe_1='/uL')
        obx_8.reference_range = '4000-11000'
        obx_8.interpretation_codes = CWE(cwe_1='H')
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

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
    """ Based on live/es/es-salut4d.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='HBELLVITGE')
        msh.receiving_application = HD(hd_1='IS3')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260501140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260501140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CATA223344556677', cx_4='CACT', cx_5='JHN', cx_9='CT&&ISO3166-2'),
            CX(cx_1='87654321Y', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='6781234', cx_4='HC', cx_5='PI', cx_9='HBELLVITGE&&'),
        ]
        pid.patient_name = XPN(xpn_1='VILADOMAT', xpn_2='CARME')
        pid.mothers_maiden_name = XPN(xpn_1='SOLER')
        pid.date_time_of_birth = '19930227'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV&DIAGONAL&250', xad_2='5e 3a', xad_3='080060', xad_4='08', xad_5='08006', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^+34^935678123'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = [
            CX(cx_1='CATA887766554433', cx_4='CACT', cx_5='JHN'),
            CX(cx_1='8765432', cx_4='HC', cx_5='PI', cx_9='HBELLVITGE&&'),
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
    """ Based on live/es/es-salut4d.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='HJOANXXIII')
        msh.receiving_application = HD(hd_1='IS3')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260610080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A05', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A05'
        evn.recorded_date_time = '20260610080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CATA556677881234', cx_4='CACT', cx_5='JHN', cx_9='CT&&ISO3166-2'),
            CX(cx_1='61234567E', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='4567123', cx_4='HC', cx_5='PI', cx_9='HJOANXXIII&&'),
        ]
        pid.patient_name = XPN(xpn_1='LLOVERAS', xpn_2='ORIOL')
        pid.mothers_maiden_name = XPN(xpn_1='GALLART')
        pid.date_time_of_birth = '19760918'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&RAMBLA NOVA&80', xad_3='430010', xad_4='43', xad_5='43001', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^+34^977567890~^WPN^CP^^+34^624567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='HAB401', pl_3='A2', pl_4='HJOANXXIII')
        pv1.attending_doctor = XCN(xcn_1='71234', xcn_2='ALBAREDA', xcn_3='RAMON', xcn_4='GRACIA', xcn_8='')
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.visit_number = CX(cx_1='PRE001', cx_4='HJOANXXIII')
        pv1.admit_date_time = '20260615'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='CATSALUT', cwe_2='SERVEI CATALA DE LA SALUT')
        in1.insurance_company_id = CX(cx_1='CATSALUT')
        in1.insurance_company_name = XON(xon_1='CATSALUT - DEPARTAMENT DE SALUT')
        in1.insurance_company_address = XAD(xad_1='Travessera de les Corts 131-159', xad_3='Barcelona', xad_5='08028', xad_6='ESP')
        in1.plan_expiration_date = '20250101'
        in1.authorization_information = AUI(aui_1='20261231')

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
    """ Based on live/es/es-salut4d.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='HGIRONA')
        msh.receiving_application = HD(hd_1='IS3')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260720100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260720100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CATA889900112233', cx_4='CACT', cx_5='JHN', cx_9='CT&&ISO3166-2'),
            CX(cx_1='72345678F', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='5678123', cx_4='HC', cx_5='PI', cx_9='HGIRONA&&'),
        ]
        pid.patient_name = XPN(xpn_1='PUJADAS', xpn_2='GEMMA')
        pid.mothers_maiden_name = XPN(xpn_1='ESTANY')
        pid.date_time_of_birth = '19910130'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [
            XAD(xad_1='AV&JAUME I&33', xad_3='170010', xad_4='17', xad_5='17001', xad_6='ESP', xad_7='H'),
            XAD(xad_1='CL&PROVENCA&100', xad_2='2n 1a', xad_3='080290', xad_4='08', xad_5='08029', xad_6='ESP', xad_7='M'),
        ]
        pid.pid_13 = '^PRN^PH^^+34^972678901~^WPN^CP^^+34^635678901~^NET^Internet^gpujadas@gmail.com'

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
    """ Based on live/es/es-salut4d.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='HVALLHEBRON')
        msh.receiving_application = HD(hd_1='IS3')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260801090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='CITA00123', ei_2='SAP-ISH')
        sch.filler_appointment_id = EI(ei_1='CITA00123', ei_2='IS3')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='CCEE', cwe_2='Consulta Externa', cwe_3='LOCAL')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^30^202608150900^202608150930'
        sch.filler_contact_person = XCN(xcn_1='62345', xcn_2='GASULL', xcn_3='PERE', xcn_4='VILADECANS', xcn_8='')
        sch.filler_contact_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_5='+34', xtn_6='932746111')
        sch.filler_contact_address = XAD(xad_1='CEXT', xad_2='HVALLHEBRON')
        sch.entered_by_person = XCN(xcn_1='Reservada')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CATA667788990012', cx_4='CACT', cx_5='JHN', cx_9='CT&&ISO3166-2'),
            CX(cx_1='74123698B', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='8901234', cx_4='HC', cx_5='PI', cx_9='HVALLHEBRON&&'),
        ]
        pid.patient_name = XPN(xpn_1='BERTRAN', xpn_2='XAVIER')
        pid.mothers_maiden_name = XPN(xpn_1='CASALS')
        pid.date_time_of_birth = '19710523'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CEXT', pl_2='CONS12', pl_3='01', pl_4='HVALLHEBRON')
        pv1.attending_doctor = XCN(xcn_1='62345', xcn_2='GASULL', xcn_3='PERE', xcn_4='VILADECANS', xcn_8='')

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
        ais.universal_service_identifier = CWE(cwe_1='CCEE_NEUMO', cwe_2='Consulta Neumologia', cwe_3='LOCAL')
        ais.start_date_time_offset_units = CNE(cne_1='202608150900')
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
        aip.personnel_resource_id = XCN(xcn_1='62345', xcn_2='GASULL', xcn_3='PERE', xcn_4='VILADECANS', xcn_8='')
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
        ail.location_resource_id = PL(pl_1='CEXT', pl_2='CONS12', pl_3='01', pl_4='HVALLHEBRON')
        ail.location_group = CWE(cwe_1='202608150900')
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
    """ Based on live/es/es-salut4d.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB')
        msh.sending_facility = HD(hd_1='HARNAU')
        msh.receiving_application = HD(hd_1='SAP-ISH')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260416100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00015'
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
            CX(cx_1='CATA881122990044', cx_4='CACT', cx_5='JHN', cx_9='CT&&ISO3166-2'),
            CX(cx_1='31245678C', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='5678901', cx_4='HC', cx_5='PI', cx_9='HARNAU&&'),
        ]
        pid.patient_name = XPN(xpn_1='OLLER', xpn_2='JUDIT')
        pid.mothers_maiden_name = XPN(xpn_1='PLANA')
        pid.date_time_of_birth = '19840314'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TRAUMA', pl_2='HAB110', pl_3='A1', pl_4='HARNAU')

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
        orc.placer_order_number = EI(ei_1='LAB00789', ei_2='LAB')
        orc.filler_order_number = EI(ei_1='ORD00321', ei_2='SAP-ISH')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB00789', ei_2='LAB')
        obr.filler_order_number = EI(ei_1='ORD00321', ei_2='SAP-ISH')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Hemograma completo con diferencial', cwe_3='LN')
        obr.observation_date_time = '20260415160000'
        obr.obr_14 = '27891^BARGALLO^SERGI^VENDRELL^^^^'
        obr.filler_field_1 = '20260416095000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobina', cwe_3='LN')
        obx.obx_5 = '11.2'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '12.0-16.0'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrito', cwe_3='LN')
        obx_2.obx_5 = '34.1'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '36.0-46.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='789-8', cwe_2='Eritrocitos', cwe_3='LN')
        obx_3.obx_5 = '3.85'
        obx_3.units = CWE(cwe_1='x10E6/uL')
        obx_3.reference_range = '4.00-5.50'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='787-2', cwe_2='VCM', cwe_3='LN')
        obx_4.obx_5 = '88.6'
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
        obx_5.obx_5 = '7200'
        obx_5.units = CWE(cwe_1='/uL')
        obx_5.reference_range = '4000-11000'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='751-8', cwe_2='Neutrofilos', cwe_3='LN')
        obx_6.obx_5 = '65.3'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '40.0-70.0'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='26515-7', cwe_2='Plaquetas', cwe_3='LN')
        obx_7.obx_5 = '245000'
        obx_7.units = CWE(cwe_1='/uL')
        obx_7.reference_range = '150000-400000'
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
    """ Based on live/es/es-salut4d.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='HBELLVITGE')
        msh.receiving_application = HD(hd_1='IS3')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260501150000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260501150000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CATA223344556677', cx_4='CACT', cx_5='JHN', cx_9='CT&&ISO3166-2'),
            CX(cx_1='87654321Y', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='6781234', cx_4='HC', cx_5='PI', cx_9='HBELLVITGE&&'),
        ]
        pid.patient_name = XPN(xpn_1='VILADOMAT', xpn_2='CARME')
        pid.mothers_maiden_name = XPN(xpn_1='SOLER')
        pid.date_time_of_birth = '19930227'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GINECO', pl_2='HAB305', pl_3='B2', pl_4='HBELLVITGE')
        pv1.attending_doctor = XCN(xcn_1='38901', xcn_2='CODINA', xcn_3='MERCE', xcn_4='ARMENGOL', xcn_8='')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Informe de Alta', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Text^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260501143000')
        txa.assigned_document_authenticator = XCN(xcn_1='38901', xcn_2='CODINA', xcn_3='MERCE', xcn_4='ARMENGOL', xcn_8='')
        txa.placer_order_number = EI(ei_1='DOC98765')
        txa.unique_document_file_name = 'AU^Authenticated^HL70271'
        txa.document_confidentiality_status = '20260501150000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='60591-5', cwe_2='SUMMARY', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjcKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA1OTUgODQyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAxMDUgPj4Kc3RyZWFtCkJUIC9GMSAxNiBUZiA3MiA3NjAgVGQgKEluZm9ybWUgZGUgQWx0YSAt'
            'IEhvc3BpdGFsIFVuaXZlcnNpdGFyaSBkZSBCZWxsdml0Z2UpIFRqIDAgLTIwIFRkIChQYWNpZW50ZTogWElSQVUgQ0FSTEEpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8'
            'PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAw'
            'MCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMxNCAwMDAwMCBuIAowMDAwMDAwNDY5IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAv'
            'Um9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNTU3CiUlRU9GCg=='
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
    """ Based on live/es/es-salut4d.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='HVALLHEBRON')
        msh.receiving_application = HD(hd_1='SAP-ISH')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260410113000'
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
            CX(cx_1='CATA667788990012', cx_4='CACT', cx_5='JHN', cx_9='CT&&ISO3166-2'),
            CX(cx_1='74123698B', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='8901234', cx_4='HC', cx_5='PI', cx_9='HVALLHEBRON&&'),
        ]
        pid.patient_name = XPN(xpn_1='BERTRAN', xpn_2='XAVIER')
        pid.mothers_maiden_name = XPN(xpn_1='CASALS')
        pid.date_time_of_birth = '19710523'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCI', pl_2='BOX08', pl_3='01', pl_4='HVALLHEBRON')

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
        orc.placer_order_number = EI(ei_1='RAD00456', ei_2='RIS')
        orc.filler_order_number = EI(ei_1='ORD00654', ei_2='SAP-ISH')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD00456', ei_2='RIS')
        obr.filler_order_number = EI(ei_1='ORD00654', ei_2='SAP-ISH')
        obr.universal_service_identifier = CWE(cwe_1='71046-1', cwe_2='Radiografia torax PA y lateral', cwe_3='LN')
        obr.observation_date_time = '20260409160000'
        obr.obr_14 = '62345^GASULL^PERE^VILADECANS^^^^'
        obr.filler_field_1 = '20260410112000'
        obr.results_rpt_status_chng_date_time = 'RAD'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='59776-5', cwe_2='Hallazgos', cwe_3='LN')
        obx.obx_5 = (
            'Infiltrado alveolar bilateral en campos medios e inferiores, compatible con neumonia bilateral. No se observa derrame pleural significativo.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Imagen diagnostica', cwe_3='LOCAL')
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
    """ Based on live/es/es-salut4d.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='HJOANXXIII')
        msh.receiving_application = HD(hd_1='LAB-MICRO')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260315141500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00018'
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
            CX(cx_1='CATA556677881234', cx_4='CACT', cx_5='JHN', cx_9='CT&&ISO3166-2'),
            CX(cx_1='61234567E', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='4567123', cx_4='HC', cx_5='PI', cx_9='HJOANXXIII&&'),
        ]
        pid.patient_name = XPN(xpn_1='RICARD', xpn_2='POL')
        pid.mothers_maiden_name = XPN(xpn_1='BOFILL')
        pid.date_time_of_birth = '19760918'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INFEC', pl_2='HAB502', pl_3='C1', pl_4='HJOANXXIII')
        pv1.attending_doctor = XCN(xcn_1='82345', xcn_2='FORNS', xcn_3='ALEIX', xcn_4='CALVET', xcn_8='')
        pv1.hospital_service = CWE(cwe_1='INF')
        pv1.visit_number = CX(cx_1='EP008', cx_4='HJOANXXIII')
        pv1.admit_date_time = '20260312080000'

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
        orc.placer_order_number = EI(ei_1='MICRO001', ei_2='SAP-ISH')
        orc.placer_order_group_number = EI(ei_1='GRP002', ei_2='SAP-ISH')
        orc.date_time_of_order_event = '20260315141500'
        orc.orc_12 = '82345^FORNS^ALEIX^CALVET^^^^'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MICRO001', ei_2='SAP-ISH')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Hemocultivo', cwe_3='LN')
        obr.observation_date_time = '20260315141500'
        obr.obr_16 = '82345^FORNS^ALEIX^CALVET^^^^'
        obr.obr_27 = '^STAT'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='A41.9', cwe_2='Sepsis, no especificada', cwe_3='I10')

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
        nte.comment = 'Fiebre >39C persistente 48h, sospecha de bacteriemia'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/es/es-salut4d.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='HTRUETA')
        msh.receiving_application = HD(hd_1='EMPI')
        msh.receiving_facility = HD(hd_1='ICS')
        msh.date_time_of_message = '20260901100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00019'
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
        pid.patient_identifier_list = [
            CX(cx_1='CATA101122334477', cx_4='CACT', cx_5='JHN', cx_9='CT&&ISO3166-2'),
            CX(cx_1='13579246G', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='9012345', cx_4='HC', cx_5='PI', cx_9='HTRUETA&&'),
            CX(cx_1='280790567890', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='REIXACH', xpn_2='BIEL')
        pid.mothers_maiden_name = XPN(xpn_1='MASSANA')
        pid.date_time_of_birth = '20260830'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&GRAN VIA DE JAUME I&45', xad_3='170010', xad_4='17', xad_5='17001', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^+34^972789012'

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
    """ Based on live/es/es-salut4d.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IS3')
        msh.sending_facility = HD(hd_1='ICS')
        msh.receiving_application = HD(hd_1='SAP-ISH')
        msh.receiving_facility = HD(hd_1='HTRUETA')
        msh.date_time_of_message = '20260901100001'
        msh.message_type = MSG(msg_1='ACK', msg_2='A28', msg_3='ACK')
        msh.message_control_id = 'ACK00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MSG00019'

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
