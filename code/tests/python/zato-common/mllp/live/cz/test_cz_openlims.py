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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MOC, MSG, PL, PRL, PT, VID, XAD, XCN
from zato.hl7v2.v2_9.groups import OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ACK, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import DG1, MSA, MSH, OBR, OBX, ORC, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('cz', 'cz-openlims.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/cz/cz-openlims.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='FN_BRNO_LAB')
        msh.receiving_application = HD(hd_1='NIS_BRNO')
        msh.receiving_facility = HD(hd_1='FN_BRNO')
        msh.date_time_of_message = '20250310060000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'OL20250310060000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='8308028917', cx_4='OLIMS', cx_5='RC'), CX(cx_1='BR85525143', cx_4='FNBRNO', cx_5='MRN')]
        pid.pid_5 = 'KOPECKÝ^Zdeněk^Lukáš^^^'
        pid.date_time_of_birth = '19830802'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='T.G. Masaryka 79', xad_3='Pardubice', xad_4='CZ', xad_5='53002', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^745547062'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '8308028917'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT3', pl_2='302', pl_3='A', pl_4='FN_BRNO', pl_8='INT3')
        pv1.attending_doctor = XCN(xcn_1='1257652343', xcn_2='Hájek', xcn_3='Jan', xcn_4='Antonín', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10023456', xcn_4='BRNOENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250308080000')

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
        orc.placer_order_number = EI(ei_1='ORD101234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='LAB201234', ei_2='OPENLIMS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250310063000^^R'
        orc.date_time_of_order_event = '20250310060000'
        orc.orc_10 = 'NOVOTNYPM^Černý^Josef^^^'
        orc.order_control_code_reason = CWE(cwe_1='FN_BRNO_LAB')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD101234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='LAB201234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Kompletní metabolický panel', cwe_3='LN')
        obr.obr_16 = '1257652343^Hájek^Jan^Antonín^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250310063000'
        obr.result_status = 'NI^No Information^HL70507'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E11.65', cwe_2='Diabetes mellitus 2. typu s hyperglykémií', cwe_3='MKN10')
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
    """ Based on live/cz/cz-openlims.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='FN_BRNO_LAB')
        msh.receiving_application = HD(hd_1='NIS_BRNO')
        msh.receiving_facility = HD(hd_1='FN_BRNO')
        msh.date_time_of_message = '20250310143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL20250310143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='8308028917', cx_4='OLIMS', cx_5='RC'), CX(cx_1='BR85525143', cx_4='FNBRNO', cx_5='MRN')]
        pid.pid_5 = 'KOPECKÝ^Zdeněk^Lukáš^^^'
        pid.date_time_of_birth = '19830802'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='T.G. Masaryka 79', xad_3='Pardubice', xad_4='CZ', xad_5='53002', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^745547062'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '8308028917'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT3', pl_2='302', pl_3='A', pl_4='FN_BRNO', pl_8='INT3')
        pv1.attending_doctor = XCN(xcn_1='1257652343', xcn_2='Hájek', xcn_3='Jan', xcn_4='Antonín', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10023456', xcn_4='BRNOENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250308080000')

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
        orc.placer_order_number = EI(ei_1='ORD101234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='LAB201234', ei_2='OPENLIMS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250310063000^^R'
        orc.date_time_of_order_event = '20250310143000'
        orc.orc_18 = 'FN_BRNO_LAB'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD101234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='LAB201234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Kompletní metabolický panel', cwe_3='LN')
        obr.observation_date_time = '20250310063500'
        obr.obr_17 = '1257652343^Hájek^Jan^Antonín^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250310143000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glukóza v séru', cwe_3='LN')
        obx.obx_5 = '11.2'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.9-5.8'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250310140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Kreatinin v séru', cwe_3='LN')
        obx_2.obx_5 = '78'
        obx_2.units = CWE(cwe_1='umol/L')
        obx_2.reference_range = '62-106'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250310140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea v séru', cwe_3='LN')
        obx_3.obx_5 = '6.1'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.8-7.2'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250310140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodík v séru', cwe_3='LN')
        obx_4.obx_5 = '140'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250310140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Draslík v séru', cwe_3='LN')
        obx_5.obx_5 = '4.5'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250310140000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT v séru', cwe_3='LN')
        obx_6.obx_5 = '0.45'
        obx_6.units = CWE(cwe_1='ukat/L')
        obx_6.reference_range = '0.10-0.75'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250310140000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST v séru', cwe_3='LN')
        obx_7.obx_5 = '0.38'
        obx_7.units = CWE(cwe_1='ukat/L')
        obx_7.reference_range = '0.10-0.72'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250310140000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobin A1c', cwe_3='LN')
        obx_8.obx_5 = '9.1'
        obx_8.units = CWE(cwe_1='%')
        obx_8.reference_range = '4.0-5.6'
        obx_8.interpretation_codes = CWE(cwe_1='H')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20250310140000'

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
    """ Based on live/cz/cz-openlims.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='NEM_CB_LAB')
        msh.receiving_application = HD(hd_1='NIS_CB')
        msh.receiving_facility = HD(hd_1='NEM_CB')
        msh.date_time_of_message = '20250415103000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL20250415103000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5404254552', cx_4='OLIMS', cx_5='RC'), CX(cx_1='CB83043255', cx_4='NEMCB', cx_5='MRN')]
        pid.pid_5 = 'JANDA^Josef^Antonín^^^'
        pid.date_time_of_birth = '19540425'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gočárova 164', xad_3='Náchod', xad_4='CZ', xad_5='54701', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^754135498'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5404254552'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HEM1', pl_2='HEM01', pl_3='A', pl_4='NEM_CB', pl_8='HEM1')
        pv1.attending_doctor = XCN(xcn_1='2751081703', xcn_2='Němcová', xcn_3='Zuzana', xcn_4='Věra', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='HEM', xcn_2='Hematologie', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V20034567', xcn_4='CBENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250414080000')

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
        orc.placer_order_number = EI(ei_1='ORD201234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='LAB301234', ei_2='OPENLIMS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250414083000^^R'
        orc.date_time_of_order_event = '20250415103000'
        orc.orc_18 = 'NEM_CB_LAB'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD201234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='LAB301234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='85025', cwe_2='Krevní obraz kompletní', cwe_3='CPT')
        obr.observation_date_time = '20250414083500'
        obr.obr_17 = '2751081703^Němcová^Zuzana^Věra^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250415103000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx.obx_5 = '98'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '120-160'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250415100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematokrit', cwe_3='LN')
        obx_2.obx_5 = '0.30'
        obx_2.units = CWE(cwe_1='L/L')
        obx_2.reference_range = '0.37-0.47'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250415100000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocyty', cwe_3='LN')
        obx_3.obx_5 = '3.2'
        obx_3.units = CWE(cwe_1='10*9/L')
        obx_3.reference_range = '4.0-10.0'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250415100000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='777-3', cwe_2='Trombocyty', cwe_3='LN')
        obx_4.obx_5 = '145'
        obx_4.units = CWE(cwe_1='10*9/L')
        obx_4.reference_range = '150-400'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250415100000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erytrocyty', cwe_3='LN')
        obx_5.obx_5 = '3.15'
        obx_5.units = CWE(cwe_1='10*12/L')
        obx_5.reference_range = '3.8-5.2'
        obx_5.interpretation_codes = CWE(cwe_1='L')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250415100000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_6.obx_5 = '95.2'
        obx_6.units = CWE(cwe_1='fL')
        obx_6.reference_range = '80-100'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250415100000'

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
    """ Based on live/cz/cz-openlims.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='FN_MOTOL_LAB')
        msh.receiving_application = HD(hd_1='NIS_MOTOL')
        msh.receiving_facility = HD(hd_1='FN_MOTOL')
        msh.date_time_of_message = '20250502074500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'OL20250502074500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='7859149024', cx_4='OLIMS', cx_5='RC'), CX(cx_1='MOT95574872', cx_4='MOTOL', cx_5='MRN')]
        pid.pid_5 = 'VACKOVÁ^Marie^Lucie^^^'
        pid.date_time_of_birth = '19780914'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Čankovská 47', xad_3='Karlovy Vary', xad_4='CZ', xad_5='36001', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^765478829'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='W', cwe_2='Widowed', cwe_3='HL70002')
        pid.pid_19 = '7859149024'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR3', pl_2='408', pl_3='A', pl_4='FN_MOTOL', pl_8='CHIR3')
        pv1.attending_doctor = XCN(xcn_1='1925743254', xcn_2='Kolář', xcn_3='Bohumil', xcn_4='Roman', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='CHI', xcn_2='Chirurgie', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V30045678', xcn_4='MOTOLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250501090000')

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
        orc.placer_order_number = EI(ei_1='ORD301234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='MIC401234', ei_2='OPENLIMS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250502080000^^R'
        orc.date_time_of_order_event = '20250502074500'
        orc.orc_10 = 'PESKOVAIM^Polák^Matěj^^^'
        orc.order_control_code_reason = CWE(cwe_1='FN_MOTOL_LAB')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD301234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='MIC401234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='87070', cwe_2='Kultivace z rány', cwe_3='CPT')
        obr.obr_16 = '1925743254^Kolář^Bohumil^Roman^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250502080000'
        obr.result_status = 'NI^No Information^HL70507'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='T81.4', cwe_2='Infekce po výkonu', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250501'
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
    """ Based on live/cz/cz-openlims.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='FN_MOTOL_LAB')
        msh.receiving_application = HD(hd_1='NIS_MOTOL')
        msh.receiving_facility = HD(hd_1='FN_MOTOL')
        msh.date_time_of_message = '20250505140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL20250505140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='7859149024', cx_4='OLIMS', cx_5='RC'), CX(cx_1='MOT95574872', cx_4='MOTOL', cx_5='MRN')]
        pid.pid_5 = 'VACKOVÁ^Marie^Lucie^^^'
        pid.date_time_of_birth = '19780914'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Čankovská 47', xad_3='Karlovy Vary', xad_4='CZ', xad_5='36001', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^765478829'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='W', cwe_2='Widowed', cwe_3='HL70002')
        pid.pid_19 = '7859149024'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR3', pl_2='408', pl_3='A', pl_4='FN_MOTOL', pl_8='CHIR3')
        pv1.attending_doctor = XCN(xcn_1='1925743254', xcn_2='Kolář', xcn_3='Bohumil', xcn_4='Roman', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='CHI', xcn_2='Chirurgie', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V30045678', xcn_4='MOTOLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250501090000')

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
        orc.placer_order_number = EI(ei_1='ORD301234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='MIC401234', ei_2='OPENLIMS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250502080000^^R'
        orc.date_time_of_order_event = '20250505140000'
        orc.orc_18 = 'FN_MOTOL_LAB'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD301234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='MIC401234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='87070', cwe_2='Kultivace z rány', cwe_3='CPT')
        obr.observation_date_time = '20250502080500'
        obr.obr_17 = '1925743254^Kolář^Bohumil^Roman^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250505140000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='Bakterie identifikované', cwe_3='LN')
        obx.obx_5 = 'Staphylococcus aureus (MSSA)'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250505130000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Citlivost na antibiotika', cwe_3='LN')
        obx_2.obx_5 = 'Oxacilin: S, Vankomycin: S, Klindamycin: S, Gentamicin: S, Ciprofloxacin: S, Cotrimoxazol: S'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250505130000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='19146-0', cwe_2='Poznámka', cwe_3='LN')
        obx_3.obx_5 = 'Doporučení: léčba oxacilinem nebo cefalosporinem 1. generace.'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250505130000'

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
    """ Based on live/cz/cz-openlims.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='NEM_PLZEN_LAB')
        msh.receiving_application = HD(hd_1='NIS_PLZEN')
        msh.receiving_facility = HD(hd_1='NEM_PLZEN')
        msh.date_time_of_message = '20250320110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL20250320110000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='7312160300', cx_4='OLIMS', cx_5='RC'), CX(cx_1='PL72502191', cx_4='NEMPLZ', cx_5='MRN')]
        pid.pid_5 = 'POLÁK^Michal^Zdeněk^^^'
        pid.date_time_of_birth = '19731216'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Husovo náměstí 163', xad_3='Tábor', xad_4='CZ', xad_5='39001', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^730610380'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '7312160300'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='KARD1', pl_2='201', pl_3='B', pl_4='NEM_PLZEN', pl_8='KARD1')
        pv1.attending_doctor = XCN(xcn_1='0215133801', xcn_2='Procházka', xcn_3='Karel', xcn_4='Antonín', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='KAR', xcn_2='Kardiologie', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V40056789', xcn_4='PLZENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250318090000')

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
        orc.placer_order_number = EI(ei_1='ORD401234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='LAB501234', ei_2='OPENLIMS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250319070000^^R'
        orc.date_time_of_order_event = '20250320110000'
        orc.orc_18 = 'NEM_PLZEN_LAB'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD401234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='LAB501234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='85610', cwe_2='Koagulační panel', cwe_3='CPT')
        obr.observation_date_time = '20250319070500'
        obr.obr_17 = '0215133801^Procházka^Karel^Antonín^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250320110000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='Protrombinový čas', cwe_3='LN')
        obx.obx_5 = '14.5'
        obx.units = CWE(cwe_1='s')
        obx.reference_range = '11.0-13.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250320100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '1.35'
        obx_2.reference_range = '0.85-1.15'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250320100000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='APTT', cwe_3='LN')
        obx_3.obx_5 = '38.2'
        obx_3.units = CWE(cwe_1='s')
        obx_3.reference_range = '25.0-36.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250320100000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3255-7', cwe_2='Fibrinogen', cwe_3='LN')
        obx_4.obx_5 = '4.8'
        obx_4.units = CWE(cwe_1='g/L')
        obx_4.reference_range = '2.0-4.0'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250320100000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='5385-0', cwe_2='D-dimer', cwe_3='LN')
        obx_5.obx_5 = '1.85'
        obx_5.units = CWE(cwe_1='mg/L')
        obx_5.reference_range = '<0.50'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250320100000'

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
    """ Based on live/cz/cz-openlims.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='NEM_HK_LAB')
        msh.receiving_application = HD(hd_1='NIS_HK')
        msh.receiving_facility = HD(hd_1='NEM_HK')
        msh.date_time_of_message = '20250601022000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'OL20250601022000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='8805058167', cx_4='OLIMS', cx_5='RC'), CX(cx_1='HK59236899', cx_4='NEMHK', cx_5='MRN')]
        pid.pid_5 = 'PROCHÁZKA^Lukáš^Dalibor^^^'
        pid.date_time_of_birth = '19880505'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Lidická 154', xad_3='Plzeň', xad_4='CZ', xad_5='32000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^703796358'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='W', cwe_2='Widowed', cwe_3='HL70002')
        pid.pid_19 = '8805058167'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='EDHK', pl_2='ED01', pl_3='A', pl_4='NEM_HK', pl_8='EDHK')
        pv1.attending_doctor = XCN(xcn_1='2752889579', xcn_2='Černý', xcn_3='Bohumil', xcn_4='Roman', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='EM', xcn_2='Urgentní příjem', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V50067890', xcn_4='HKENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250601020000')

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
        orc.placer_order_number = EI(ei_1='ORD501234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='LAB601234', ei_2='OPENLIMS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250601023000^^S'
        orc.date_time_of_order_event = '20250601022000'
        orc.orc_10 = 'JELINKOVAMP^Kolářová^Jaroslava^^^'
        orc.order_control_code_reason = CWE(cwe_1='NEM_HK_LAB')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD501234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='LAB601234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='49498-9', cwe_2='Troponin I', cwe_3='LN')
        obr.obr_16 = '2752889579^Černý^Bohumil^Roman^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250601023000'
        obr.result_status = 'NI^No Information^HL70507'
        obr.obr_27 = 'S^STAT^HL70078'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I21.9', cwe_2='Akutní infarkt myokardu, neurčený', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250601'
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
    """ Based on live/cz/cz-openlims.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='NEM_HK_LAB')
        msh.receiving_application = HD(hd_1='NIS_HK')
        msh.receiving_facility = HD(hd_1='NEM_HK')
        msh.date_time_of_message = '20250601030000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL20250601030000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='8805058167', cx_4='OLIMS', cx_5='RC'), CX(cx_1='HK59236899', cx_4='NEMHK', cx_5='MRN')]
        pid.pid_5 = 'PROCHÁZKA^Lukáš^Dalibor^^^'
        pid.date_time_of_birth = '19880505'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Lidická 154', xad_3='Plzeň', xad_4='CZ', xad_5='32000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^703796358'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='W', cwe_2='Widowed', cwe_3='HL70002')
        pid.pid_19 = '8805058167'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='EDHK', pl_2='ED01', pl_3='A', pl_4='NEM_HK', pl_8='EDHK')
        pv1.attending_doctor = XCN(xcn_1='2752889579', xcn_2='Černý', xcn_3='Bohumil', xcn_4='Roman', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='EM', xcn_2='Urgentní příjem', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V50067890', xcn_4='HKENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250601020000')

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
        orc.placer_order_number = EI(ei_1='ORD501234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='LAB601234', ei_2='OPENLIMS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250601023000^^S'
        orc.date_time_of_order_event = '20250601030000'
        orc.orc_18 = 'NEM_HK_LAB'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD501234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='LAB601234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='49498-9', cwe_2='Troponin I', cwe_3='LN')
        obr.observation_date_time = '20250601023500'
        obr.obr_17 = '2752889579^Černý^Bohumil^Roman^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250601030000')
        obr.parent_result = PRL(prl_1='F')
        obr.obr_28 = 'S^STAT^HL70078'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='49498-9', cwe_2='Troponin I, vysokosenzitivní', cwe_3='LN')
        obx.obx_5 = '2580'
        obx.units = CWE(cwe_1='ng/L')
        obx.reference_range = '<14'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250601025000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='30522-7', cwe_2='CK-MB', cwe_3='LN')
        obx_2.obx_5 = '45.2'
        obx_2.units = CWE(cwe_1='ug/L')
        obx_2.reference_range = '<5.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250601025000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='42757-5', cwe_2='NT-proBNP', cwe_3='LN')
        obx_3.obx_5 = '8450'
        obx_3.units = CWE(cwe_1='ng/L')
        obx_3.reference_range = '<125'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250601025000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Draslík v séru', cwe_3='LN')
        obx_4.obx_5 = '3.8'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '3.5-5.1'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250601025000'

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
    """ Based on live/cz/cz-openlims.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='FN_BRNO_LAB')
        msh.receiving_application = HD(hd_1='NIS_BRNO')
        msh.receiving_facility = HD(hd_1='FN_BRNO')
        msh.date_time_of_message = '20250422140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL20250422140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5259267661', cx_4='OLIMS', cx_5='RC'), CX(cx_1='BR04571811', cx_4='FNBRNO', cx_5='MRN')]
        pid.pid_5 = 'DOLEŽALOVÁ^Eva^Monika^^^'
        pid.date_time_of_birth = '19520926'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Mánesova 137', xad_3='Cheb', xad_4='CZ', xad_5='35002', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^750199040'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5259267661'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='END1', pl_2='END01', pl_3='A', pl_4='FN_BRNO', pl_8='END1')
        pv1.attending_doctor = XCN(xcn_1='9272584546', xcn_2='Lukáš', xcn_3='Ondřej', xcn_4='Marek', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='END', xcn_2='Endokrinologie', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V60078901', xcn_4='BRNOENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250421080000')

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
        orc.placer_order_number = EI(ei_1='ORD601234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='LAB701234', ei_2='OPENLIMS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250421083000^^R'
        orc.date_time_of_order_event = '20250422140000'
        orc.orc_18 = 'FN_BRNO_LAB'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD601234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='LAB701234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='84443', cwe_2='TSH a volné hormony', cwe_3='CPT')
        obr.observation_date_time = '20250421083500'
        obr.obr_17 = '9272584546^Lukáš^Ondřej^Marek^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250422140000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '8.45'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.27-4.20'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250422130000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='fT4', cwe_3='LN')
        obx_2.obx_5 = '10.2'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '12.0-22.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250422130000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3051-0', cwe_2='fT3', cwe_3='LN')
        obx_3.obx_5 = '3.8'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '3.1-6.8'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250422130000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='5384-3', cwe_2='Anti-TPO', cwe_3='LN')
        obx_4.obx_5 = '385'
        obx_4.units = CWE(cwe_1='kIU/L')
        obx_4.reference_range = '<34'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250422130000'

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
    """ Based on live/cz/cz-openlims.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='FN_BRNO_LAB')
        msh.receiving_application = HD(hd_1='NIS_BRNO')
        msh.receiving_facility = HD(hd_1='FN_BRNO')
        msh.date_time_of_message = '20250310150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL20250310150000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='8308028917', cx_4='OLIMS', cx_5='RC'), CX(cx_1='BR85525143', cx_4='FNBRNO', cx_5='MRN')]
        pid.pid_5 = 'KOPECKÝ^Zdeněk^Lukáš^^^'
        pid.date_time_of_birth = '19830802'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='T.G. Masaryka 79', xad_3='Pardubice', xad_4='CZ', xad_5='53002', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^745547062'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '8308028917'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT3', pl_2='302', pl_3='A', pl_4='FN_BRNO', pl_8='INT3')
        pv1.attending_doctor = XCN(xcn_1='1257652343', xcn_2='Hájek', xcn_3='Jan', xcn_4='Antonín', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10023456', xcn_4='BRNOENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250308080000')

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
        orc.placer_order_number = EI(ei_1='ORD101234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='LAB201234', ei_2='OPENLIMS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250310063000^^R'
        orc.date_time_of_order_event = '20250310150000'
        orc.orc_18 = 'FN_BRNO_LAB'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD101234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='LAB201234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Kompletní metabolický panel', cwe_3='LN')
        obr.observation_date_time = '20250310063500'
        obr.obr_17 = '1257652343^Hájek^Jan^Antonín^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250310150000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='24323-8', cwe_2='Souhrnný nález', cwe_3='LN')
        obx.obx_5 = 'Výsledky metabolického panelu ukazují zvýšenou glykémii a HbA1c, svědčící pro nedostatečnou kompenzaci DM 2. typu.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250310143000'

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
    """ Based on live/cz/cz-openlims.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='NEM_OL_LAB')
        msh.receiving_application = HD(hd_1='NIS_OL')
        msh.receiving_facility = HD(hd_1='NEM_OL')
        msh.date_time_of_message = '20250515080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'OL20250515080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='1707125347', cx_4='OLIMS', cx_5='RC'), CX(cx_1='OL00103382', cx_4='NEMOL', cx_5='MRN')]
        pid.pid_5 = 'KONEČNÝ^Jaroslav^Vladimír^^^'
        pid.date_time_of_birth = '20170712'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Nábřežní 228', xad_3='Brno', xad_4='CZ', xad_5='60200', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^746276889'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '1707125347'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='IMU1', pl_2='IMU01', pl_3='A', pl_4='NEM_OL', pl_8='IMU1')
        pv1.attending_doctor = XCN(xcn_1='4611481265', xcn_2='Vacková', xcn_3='Lucie', xcn_4='Alena', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='IMU', xcn_2='Imunologie', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70089012', xcn_4='OLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250515080000')

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
        orc.placer_order_number = EI(ei_1='ORD701234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='LAB801234', ei_2='OPENLIMS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250515083000^^R'
        orc.date_time_of_order_event = '20250515080000'
        orc.orc_10 = 'SULCOVAR^Doležalová^Veronika^^^'
        orc.order_control_code_reason = CWE(cwe_1='NEM_OL_LAB')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='LAB801234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='86235', cwe_2='Antinukleární protilátky', cwe_3='CPT')
        obr.obr_16 = '4611481265^Vacková^Lucie^Alena^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250515083000'
        obr.result_status = 'NI^No Information^HL70507'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M32.9', cwe_2='Systémový lupus erytematodes, neurčený', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250515'
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
    """ Based on live/cz/cz-openlims.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='NEM_OL_LAB')
        msh.receiving_application = HD(hd_1='NIS_OL')
        msh.receiving_facility = HD(hd_1='NEM_OL')
        msh.date_time_of_message = '20250517140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL20250517140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='1707125347', cx_4='OLIMS', cx_5='RC'), CX(cx_1='OL00103382', cx_4='NEMOL', cx_5='MRN')]
        pid.pid_5 = 'KONEČNÝ^Jaroslav^Vladimír^^^'
        pid.date_time_of_birth = '20170712'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Nábřežní 228', xad_3='Brno', xad_4='CZ', xad_5='60200', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^746276889'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '1707125347'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='IMU1', pl_2='IMU01', pl_3='A', pl_4='NEM_OL', pl_8='IMU1')
        pv1.attending_doctor = XCN(xcn_1='4611481265', xcn_2='Vacková', xcn_3='Lucie', xcn_4='Alena', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='IMU', xcn_2='Imunologie', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70089012', xcn_4='OLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250515080000')

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
        orc.placer_order_number = EI(ei_1='ORD701234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='LAB801234', ei_2='OPENLIMS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250515083000^^R'
        orc.date_time_of_order_event = '20250517140000'
        orc.orc_18 = 'NEM_OL_LAB'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='LAB801234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='86235', cwe_2='Antinukleární protilátky', cwe_3='CPT')
        obr.observation_date_time = '20250515083500'
        obr.obr_17 = '4611481265^Vacková^Lucie^Alena^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250517140000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='86235-5', cwe_2='ANA IF', cwe_3='LN')
        obx.obx_5 = 'Pozitivní, titr 1:640, homogenní vzor'
        obx.observation_result_status = 'A'
        obx.date_time_of_the_observation = 'F'
        obx.observation_method = CWE(cwe_1='20250517130000')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='56782-8', cwe_2='Anti-dsDNA', cwe_3='LN')
        obx_2.obx_5 = '185'
        obx_2.units = CWE(cwe_1='IU/mL')
        obx_2.reference_range = '<30'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250517130000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='53972-7', cwe_2='Komplement C3', cwe_3='LN')
        obx_3.obx_5 = '0.52'
        obx_3.units = CWE(cwe_1='g/L')
        obx_3.reference_range = '0.90-1.80'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250517130000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4485-9', cwe_2='Komplement C4', cwe_3='LN')
        obx_4.obx_5 = '0.08'
        obx_4.units = CWE(cwe_1='g/L')
        obx_4.reference_range = '0.10-0.40'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250517130000'

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
    """ Based on live/cz/cz-openlims.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='FN_BRNO_LAB')
        msh.receiving_application = HD(hd_1='NIS_BRNO')
        msh.receiving_facility = HD(hd_1='FN_BRNO')
        msh.date_time_of_message = '20250310060005'
        msh.message_type = MSG(msg_1='ACK', msg_2='O01', msg_3='ACK')
        msh.message_control_id = 'OL20250310060005001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'ORD101234'
        msa.expected_sequence_number = '0'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/cz/cz-openlims.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='NEM_CB_LAB')
        msh.receiving_application = HD(hd_1='NIS_CB')
        msh.receiving_facility = HD(hd_1='NEM_CB')
        msh.date_time_of_message = '20250510150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL20250510150000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5712226550', cx_4='OLIMS', cx_5='RC'), CX(cx_1='CB80131615', cx_4='NEMCB', cx_5='MRN')]
        pid.pid_5 = 'KRATOCHVÍL^Pavel^Adam^^^'
        pid.date_time_of_birth = '19571222'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hrnčířská 36', xad_3='Náchod', xad_4='CZ', xad_5='54701', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^797279855'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '5712226550'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='URO1', pl_2='URO01', pl_3='A', pl_4='NEM_CB', pl_8='URO1')
        pv1.attending_doctor = XCN(xcn_1='7832081753', xcn_2='Štěpánová', xcn_3='Hana', xcn_4='Monika', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='URO', xcn_2='Urologie', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80090123', xcn_4='CBENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250509080000')

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
        orc.placer_order_number = EI(ei_1='ORD801234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='LAB901234', ei_2='OPENLIMS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250509083000^^R'
        orc.date_time_of_order_event = '20250510150000'
        orc.orc_18 = 'NEM_CB_LAB'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='LAB901234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='81001', cwe_2='Vyšetření moči', cwe_3='CPT')
        obr.observation_date_time = '20250509083500'
        obr.obr_17 = '7832081753^Štěpánová^Hana^Monika^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250510150000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='5778-6', cwe_2='Barva moči', cwe_3='LN')
        obx.obx_5 = 'Žlutá'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250510140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='5803-2', cwe_2='pH moči', cwe_3='LN')
        obx_2.obx_5 = '5.5'
        obx_2.reference_range = '5.0-8.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250510140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2965-2', cwe_2='Specifická hmotnost moči', cwe_3='LN')
        obx_3.obx_5 = '1.025'
        obx_3.reference_range = '1.005-1.030'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250510140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='5804-0', cwe_2='Bílkovina v moči', cwe_3='LN')
        obx_4.obx_5 = 'Negativní'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250510140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'TX'
        obx_5.observation_identifier = CWE(cwe_1='5792-7', cwe_2='Glukóza v moči', cwe_3='LN')
        obx_5.obx_5 = 'Negativní'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250510140000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='5821-4', cwe_2='Leukocyty v moči sediment', cwe_3='LN')
        obx_6.obx_5 = '2'
        obx_6.units = CWE(cwe_1='/zorné pole')
        obx_6.reference_range = '<5'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250510140000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='5808-1', cwe_2='Erytrocyty v moči sediment', cwe_3='LN')
        obx_7.obx_5 = '15'
        obx_7.units = CWE(cwe_1='/zorné pole')
        obx_7.reference_range = '<3'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250510140000'

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
    """ Based on live/cz/cz-openlims.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='FN_MOTOL_LAB')
        msh.receiving_application = HD(hd_1='NIS_MOTOL')
        msh.receiving_facility = HD(hd_1='FN_MOTOL')
        msh.date_time_of_message = '20250603043000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL20250603043000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='4601194769', cx_4='OLIMS', cx_5='RC'), CX(cx_1='MOT18079179', cx_4='MOTOL', cx_5='MRN')]
        pid.pid_5 = 'KŘÍŽEK^Adam^Dalibor^^^'
        pid.date_time_of_birth = '19460119'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Na Příkopě 22', xad_3='Pardubice', xad_4='CZ', xad_5='53002', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^667702757'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '4601194769'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='JIP2', pl_2='JIP03', pl_3='A', pl_4='FN_MOTOL', pl_8='JIP2')
        pv1.attending_doctor = XCN(xcn_1='1499252733', xcn_2='Bartoš', xcn_3='Aleš', xcn_4='Martin', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='ARO', xcn_2='Anesteziologie a resuscitace', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V40056789', xcn_4='MOTOLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250603020000')

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
        orc.placer_order_number = EI(ei_1='ORD901234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='LAB001234', ei_2='OPENLIMS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250603040000^^S'
        orc.date_time_of_order_event = '20250603043000'
        orc.orc_18 = 'FN_MOTOL_LAB'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD901234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='LAB001234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='24338-6', cwe_2='Krevní plyny', cwe_3='LN')
        obr.observation_date_time = '20250603040500'
        obr.obr_17 = '1499252733^Bartoš^Aleš^Martin^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250603043000')
        obr.parent_result = PRL(prl_1='F')
        obr.obr_28 = 'S^STAT^HL70078'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='pH krve', cwe_3='LN')
        obx.obx_5 = '7.28'
        obx.reference_range = '7.35-7.45'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250603042000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='pCO2', cwe_3='LN')
        obx_2.obx_5 = '7.8'
        obx_2.units = CWE(cwe_1='kPa')
        obx_2.reference_range = '4.7-6.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250603042000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2703-7', cwe_2='pO2', cwe_3='LN')
        obx_3.obx_5 = '7.2'
        obx_3.units = CWE(cwe_1='kPa')
        obx_3.reference_range = '10.0-13.3'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250603042000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1960-4', cwe_2='Bikarbonát', cwe_3='LN')
        obx_4.obx_5 = '18.5'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '22.0-26.0'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250603042000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1925-7', cwe_2='Base excess', cwe_3='LN')
        obx_5.obx_5 = '-7.2'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '-2.0-2.0'
        obx_5.interpretation_codes = CWE(cwe_1='L')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250603042000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2708-6', cwe_2='Saturace O2', cwe_3='LN')
        obx_6.obx_5 = '85'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '95-99'
        obx_6.interpretation_codes = CWE(cwe_1='L')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250603042000'

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
    """ Based on live/cz/cz-openlims.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='NEM_PLZEN_LAB')
        msh.receiving_application = HD(hd_1='NIS_PLZEN')
        msh.receiving_facility = HD(hd_1='NEM_PLZEN')
        msh.date_time_of_message = '20250425080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'OL20250425080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='6610128256', cx_4='OLIMS', cx_5='RC'), CX(cx_1='PL26703773', cx_4='NEMPLZ', cx_5='MRN')]
        pid.pid_5 = 'HOLUB^Ondřej^Miroslav^^^'
        pid.date_time_of_birth = '19661012'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Žitavská 129', xad_3='Praha 5', xad_4='CZ', xad_5='15000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^746084293'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '6610128256'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT2', pl_2='202', pl_3='A', pl_4='NEM_PLZEN', pl_8='INT2')
        pv1.attending_doctor = XCN(xcn_1='4744526584', xcn_2='Vacek', xcn_3='Martin', xcn_4='Dalibor', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90101234', xcn_4='PLZENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250424090000')

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
        orc.placer_order_number = EI(ei_1='ORD011234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='LAB111234', ei_2='OPENLIMS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250425083000^^R'
        orc.date_time_of_order_event = '20250425080000'
        orc.orc_10 = 'KADLECOVAJ^Svobodová^Tereza^^^'
        orc.order_control_code_reason = CWE(cwe_1='NEM_PLZEN_LAB')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD011234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='LAB111234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='80320', cwe_2='Hladina léčiv v séru', cwe_3='CPT')
        obr.obr_16 = '4744526584^Vacek^Martin^Dalibor^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250425083000'
        obr.result_status = 'NI^No Information^HL70507'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I48.0', cwe_2='Paroxysmální fibrilace síní', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250424'
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
    """ Based on live/cz/cz-openlims.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='NEM_PLZEN_LAB')
        msh.receiving_application = HD(hd_1='NIS_PLZEN')
        msh.receiving_facility = HD(hd_1='NEM_PLZEN')
        msh.date_time_of_message = '20250426140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL20250426140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='6610128256', cx_4='OLIMS', cx_5='RC'), CX(cx_1='PL26703773', cx_4='NEMPLZ', cx_5='MRN')]
        pid.pid_5 = 'HOLUB^Ondřej^Miroslav^^^'
        pid.date_time_of_birth = '19661012'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Žitavská 129', xad_3='Praha 5', xad_4='CZ', xad_5='15000', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^746084293'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '6610128256'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT2', pl_2='202', pl_3='A', pl_4='NEM_PLZEN', pl_8='INT2')
        pv1.attending_doctor = XCN(xcn_1='4744526584', xcn_2='Vacek', xcn_3='Martin', xcn_4='Dalibor', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90101234', xcn_4='PLZENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250424090000')

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
        orc.placer_order_number = EI(ei_1='ORD011234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='LAB111234', ei_2='OPENLIMS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250425083000^^R'
        orc.date_time_of_order_event = '20250426140000'
        orc.orc_18 = 'NEM_PLZEN_LAB'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD011234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='LAB111234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='80320', cwe_2='Hladina léčiv v séru', cwe_3='CPT')
        obr.observation_date_time = '20250425083500'
        obr.obr_17 = '4744526584^Vacek^Martin^Dalibor^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250426140000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3663-2', cwe_2='Digoxin v séru', cwe_3='LN')
        obx.obx_5 = '2.8'
        obx.units = CWE(cwe_1='nmol/L')
        obx.reference_range = '1.0-2.6'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250426130000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='19146-0', cwe_2='Poznámka', cwe_3='LN')
        obx_2.obx_5 = 'Hladina digoxinu mírně nad terapeutickým rozmezím. Doporučení: snížení dávky a kontrola za 48 hodin.'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250426130000'

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
    """ Based on live/cz/cz-openlims.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='NEM_OL_LAB')
        msh.receiving_application = HD(hd_1='NIS_OL')
        msh.receiving_facility = HD(hd_1='NEM_OL')
        msh.date_time_of_message = '20250518100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL20250518100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='1707125347', cx_4='OLIMS', cx_5='RC'), CX(cx_1='OL00103382', cx_4='NEMOL', cx_5='MRN')]
        pid.pid_5 = 'KONEČNÝ^Jaroslav^Vladimír^^^'
        pid.date_time_of_birth = '20170712'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Nábřežní 228', xad_3='Brno', xad_4='CZ', xad_5='60200', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^746276889'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '1707125347'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='IMU1', pl_2='IMU01', pl_3='A', pl_4='NEM_OL', pl_8='IMU1')
        pv1.attending_doctor = XCN(xcn_1='4611481265', xcn_2='Vacková', xcn_3='Lucie', xcn_4='Alena', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='IMU', xcn_2='Imunologie', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70089012', xcn_4='OLENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250515080000')

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
        orc.placer_order_number = EI(ei_1='ORD701234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='LAB801234', ei_2='OPENLIMS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250515083000^^R'
        orc.date_time_of_order_event = '20250518100000'
        orc.orc_18 = 'NEM_OL_LAB'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD701234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='LAB801234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='86235', cwe_2='Imunologické vyšetření - souhrnná zpráva', cwe_3='CPT')
        obr.observation_date_time = '20250515083500'
        obr.obr_17 = '4611481265^Vacková^Lucie^Alena^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250518100000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='86235-5', cwe_2='Souhrnný nález', cwe_3='LN')
        obx.obx_5 = 'ANA pozitivní 1:640, anti-dsDNA výrazně zvýšené, snížený komplement C3 a C4. Nález svědčí pro aktivní SLE.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250518090000'

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
    """ Based on live/cz/cz-openlims.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='NEM_CB_LAB')
        msh.receiving_application = HD(hd_1='NIS_CB')
        msh.receiving_facility = HD(hd_1='NEM_CB')
        msh.date_time_of_message = '20250605080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'OL20250605080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5801099208', cx_4='OLIMS', cx_5='RC'), CX(cx_1='CB24992622', cx_4='NEMCB', cx_5='MRN')]
        pid.pid_5 = 'SEDLÁČEK^Rostislav^Jan^^^'
        pid.date_time_of_birth = '19580109'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Nerudova 78', xad_3='Třebíč', xad_4='CZ', xad_5='67401', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^775013223'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5801099208'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR2', pl_2='306', pl_3='A', pl_4='NEM_CB', pl_8='CHIR2')
        pv1.attending_doctor = XCN(xcn_1='1257652343', xcn_2='Hájek', xcn_3='Jan', xcn_4='Antonín', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='CHI', xcn_2='Chirurgie', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10112345', xcn_4='CBENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250604090000')

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
        orc.placer_order_number = EI(ei_1='ORD121234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='PAT131234', ei_2='OPENLIMS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250605083000^^R'
        orc.date_time_of_order_event = '20250605080000'
        orc.orc_10 = 'NOVOTNYPM^Černý^Josef^^^'
        orc.order_control_code_reason = CWE(cwe_1='NEM_CB_LAB')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD121234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='PAT131234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='Histopatologické vyšetření', cwe_3='CPT')
        obr.obr_16 = '1257652343^Hájek^Jan^Antonín^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250605083000'
        obr.result_status = 'NI^No Information^HL70507'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C18.0', cwe_2='Zhoubný novotvar céka', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250604'
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
    """ Based on live/cz/cz-openlims.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OPENLIMS')
        msh.sending_facility = HD(hd_1='NEM_CB_LAB')
        msh.receiving_application = HD(hd_1='NIS_CB')
        msh.receiving_facility = HD(hd_1='NEM_CB')
        msh.date_time_of_message = '20250612140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OL20250612140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = '8859/2'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5801099208', cx_4='OLIMS', cx_5='RC'), CX(cx_1='CB24992622', cx_4='NEMCB', cx_5='MRN')]
        pid.pid_5 = 'SEDLÁČEK^Rostislav^Jan^^^'
        pid.date_time_of_birth = '19580109'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Nerudova 78', xad_3='Třebíč', xad_4='CZ', xad_5='67401', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^775013223'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5801099208'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR2', pl_2='306', pl_3='A', pl_4='NEM_CB', pl_8='CHIR2')
        pv1.attending_doctor = XCN(xcn_1='1257652343', xcn_2='Hájek', xcn_3='Jan', xcn_4='Antonín', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='CHI', xcn_2='Chirurgie', xcn_3='OLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10112345', xcn_4='CBENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250604090000')

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
        orc.placer_order_number = EI(ei_1='ORD121234', ei_2='NIS')
        orc.filler_order_number = EI(ei_1='PAT131234', ei_2='OPENLIMS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250605083000^^R'
        orc.date_time_of_order_event = '20250612140000'
        orc.orc_18 = 'NEM_CB_LAB'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD121234', ei_2='NIS')
        obr.filler_order_number = EI(ei_1='PAT131234', ei_2='OPENLIMS')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='Histopatologické vyšetření', cwe_3='CPT')
        obr.observation_date_time = '20250605083500'
        obr.obr_17 = '1257652343^Hájek^Jan^Antonín^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250612140000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Nález patologie', cwe_3='LN')
        obx.obx_5 = (
            'Adenokarcinom céka, středně diferencovaný (G2), invaze do subserózy (pT3), bez metastáz v 18 vyšetřených lymfatických uzlinách (pN0). Resekč'
            'ní okraje bez nádoru.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250612130000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='33731-1', cwe_2='Imunohistochemie', cwe_3='LN')
        obx_2.obx_5 = 'CK20+, CDX2+, CK7-, MSI stabilní (MSS), KRAS wild-type.'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250612130000'

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
