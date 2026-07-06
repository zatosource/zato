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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MOC, MSG, OG, PL, PRL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import DG1, EVN, IN1, MSH, NK1, OBR, OBX, ORC, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ar', 'ar-centralab-dnlab.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='LAB_STAMBOULIAN')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='LAB_STAMBOULIAN')
        msh.date_time_of_message = '20250305074500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'STB20250305074500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80012345', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='28456712', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'MARTINEZ^Lorena^Beatriz^^^Sra.'
        pid.date_time_of_birth = '19800115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Cabildo 2310', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1428AAS', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^47832500'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casada', cwe_3='HL70002')
        pid.pid_19 = '28456712'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LABEXT', pl_2='EXTR1', pl_3='A', pl_4='STAMBOULIAN', pl_8='LABEXT')
        pv1.attending_doctor = XCN(xcn_1='1100112233', xcn_2='Sosa', xcn_3='Ariel', xcn_4='M', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='MED', xcn_2='Medicina Interna', xcn_3='STBSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90012345', xcn_4='STBENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 310', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250305074500')

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
        orc.placer_order_number = EI(ei_1='ORD801001', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601001', ei_2='DNLAB')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250305080000^^R'
        orc.date_time_of_order_event = '20250305074500'
        orc.orc_10 = 'JBROWN^Brown^Julia^M^^Lic.'
        orc.enterers_location = PL(pl_1='20250305074500')
        orc.order_effective_date_time = 'LAB_STAMBOULIAN'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801001', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601001', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Panel Metabolico Completo', cwe_3='LN')
        obr.observation_end_date_time = '20250305075000'
        obr.obr_15 = '1100112233^Sosa^Ariel^M^^Dr.^^^MN'
        obr.filler_field_2 = '20250305080000'
        obr.diagnostic_serv_sect_id = 'NI^No Information^HL70507'

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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='LAB_STAMBOULIAN')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='LAB_STAMBOULIAN')
        msh.date_time_of_message = '20250305141200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'STB20250305141200001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80012345', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='28456712', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'MARTINEZ^Lorena^Beatriz^^^Sra.'
        pid.date_time_of_birth = '19800115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Cabildo 2310', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1428AAS', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^11^47832500'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casada', cwe_3='HL70002')
        pid.pid_19 = '28456712'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LABEXT', pl_2='EXTR1', pl_3='A', pl_4='STAMBOULIAN', pl_8='LABEXT')
        pv1.attending_doctor = XCN(xcn_1='1100112233', xcn_2='Sosa', xcn_3='Ariel', xcn_4='M', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='MED', xcn_2='Medicina Interna', xcn_3='STBSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90012345', xcn_4='STBENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 310', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250305074500')

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
        orc.placer_order_number = EI(ei_1='ORD801001', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601001', ei_2='DNLAB')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250305080000^^R'
        orc.date_time_of_order_event = '20250305141200'
        orc.orc_10 = 'JBROWN^Brown^Julia^M^^Lic.'
        orc.enterers_location = PL(pl_1='20250305141200')
        orc.order_effective_date_time = 'LAB_STAMBOULIAN'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801001', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601001', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Panel Metabolico Completo', cwe_3='LN')
        obr.observation_date_time = '20250305075000'
        obr.obr_16 = '1100112233^Sosa^Ariel^M^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250305141000'
        obr.diagnostic_serv_sect_id = 'CH'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucosa', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '98'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-110'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinina', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '0.9'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.6-1.2'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '32'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '15-45'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='17861-6', cwe_2='Calcio', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '9.4'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '8.5-10.5'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potasio', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = '4.2'
        obx_5.units = CWE(cwe_1='mEq/L')
        obx_5.reference_range = '3.5-5.5'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodio', cwe_3='LN')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = '141'
        obx_6.units = CWE(cwe_1='mEq/L')
        obx_6.reference_range = '135-145'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT (GPT)', cwe_3='LN')
        obx_7.observation_sub_id = OG(og_1='1')
        obx_7.obx_5 = '24'
        obx_7.units = CWE(cwe_1='U/L')
        obx_7.reference_range = '7-56'
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST (GOT)', cwe_3='LN')
        obx_8.observation_sub_id = OG(og_1='1')
        obx_8.obx_5 = '19'
        obx_8.units = CWE(cwe_1='U/L')
        obx_8.reference_range = '10-40'
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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='HOSP_RAMOS_MEJIA')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_RAMOS_MEJIA')
        msh.date_time_of_message = '20250312063000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HRM20250312063000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80023456', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='33126587', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'TORRES^Emiliano^Joaquin^^^Sr.'
        pid.date_time_of_birth = '19870623'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Calle Florida 825', xad_3='Cordoba', xad_4='Cordoba', xad_5='X5000FAA', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^351^4221540'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltero', cwe_3='HL70002')
        pid.pid_19 = '33126587'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='LABINT', pl_2='HEMA1', pl_3='A', pl_4='HRMEJIA', pl_8='LABINT')
        pv1.attending_doctor = XCN(xcn_1='1100223344', xcn_2='Romero', xcn_3='Marcela', xcn_4='E', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='HEM', xcn_2='Hematologia', xcn_3='HRMSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90023456', xcn_4='HRMENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250312063000')

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
        orc.placer_order_number = EI(ei_1='ORD801002', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601002', ei_2='DNLAB')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250312070000^^R'
        orc.date_time_of_order_event = '20250312063000'
        orc.orc_10 = 'PCOSTA^Costa^Patricia^L^^Lic.'
        orc.enterers_location = PL(pl_1='20250312063000')
        orc.order_effective_date_time = 'HOSP_RAMOS_MEJIA'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801002', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601002', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Hemograma Completo con Recuento Diferencial', cwe_3='LN')
        obr.observation_end_date_time = '20250312064000'
        obr.obr_15 = '1100223344^Romero^Marcela^E^^Dra.^^^MN'
        obr.filler_field_2 = '20250312070000'
        obr.diagnostic_serv_sect_id = 'NI^No Information^HL70507'

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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='HOSP_RAMOS_MEJIA')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_RAMOS_MEJIA')
        msh.date_time_of_message = '20250312102000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HRM20250312102000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80023456', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='33126587', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'TORRES^Emiliano^Joaquin^^^Sr.'
        pid.date_time_of_birth = '19870623'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Calle Florida 825', xad_3='Cordoba', xad_4='Cordoba', xad_5='X5000FAA', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^351^4221540'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltero', cwe_3='HL70002')
        pid.pid_19 = '33126587'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='LABINT', pl_2='HEMA1', pl_3='A', pl_4='HRMEJIA', pl_8='LABINT')
        pv1.attending_doctor = XCN(xcn_1='1100223344', xcn_2='Romero', xcn_3='Marcela', xcn_4='E', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='HEM', xcn_2='Hematologia', xcn_3='HRMSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90023456', xcn_4='HRMENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250312063000')

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
        orc.placer_order_number = EI(ei_1='ORD801002', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601002', ei_2='DNLAB')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250312070000^^R'
        orc.date_time_of_order_event = '20250312102000'
        orc.orc_10 = 'PCOSTA^Costa^Patricia^L^^Lic.'
        orc.enterers_location = PL(pl_1='20250312102000')
        orc.order_effective_date_time = 'HOSP_RAMOS_MEJIA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801002', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601002', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Hemograma Completo con Recuento Diferencial', cwe_3='LN')
        obr.observation_date_time = '20250312064000'
        obr.obr_16 = '1100223344^Romero^Marcela^E^^Dra.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250312101800'
        obr.diagnostic_serv_sect_id = 'HM'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobina', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '14.2'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '13.5-17.5'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrito', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '42.1'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '40-54'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='789-8', cwe_2='Eritrocitos', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '4.85'
        obx_3.units = CWE(cwe_1='x10', cwe_2='6/uL')
        obx_3.reference_range = '4.5-5.9'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocitos', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '7.2'
        obx_4.units = CWE(cwe_1='x10', cwe_2='3/uL')
        obx_4.reference_range = '4.5-11.0'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Plaquetas', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = '245'
        obx_5.units = CWE(cwe_1='x10', cwe_2='3/uL')
        obx_5.reference_range = '150-400'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='770-8', cwe_2='Neutrofilos', cwe_3='LN')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = '62'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '40-70'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='736-9', cwe_2='Linfocitos', cwe_3='LN')
        obx_7.observation_sub_id = OG(og_1='1')
        obx_7.obx_5 = '28'
        obx_7.units = CWE(cwe_1='%')
        obx_7.reference_range = '20-40'
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='5905-5', cwe_2='Monocitos', cwe_3='LN')
        obx_8.observation_sub_id = OG(og_1='1')
        obx_8.obx_5 = '7'
        obx_8.units = CWE(cwe_1='%')
        obx_8.reference_range = '2-8'
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='713-8', cwe_2='Eosinofilos', cwe_3='LN')
        obx_9.observation_sub_id = OG(og_1='1')
        obx_9.obx_5 = '2'
        obx_9.units = CWE(cwe_1='%')
        obx_9.reference_range = '1-4'
        obx_9.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'NM'
        obx_10.observation_identifier = CWE(cwe_1='706-2', cwe_2='Basofilos', cwe_3='LN')
        obx_10.observation_sub_id = OG(og_1='1')
        obx_10.obx_5 = '1'
        obx_10.units = CWE(cwe_1='%')
        obx_10.reference_range = '0-2'
        obx_10.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_10 = OruR01Observation()
        observation_10.obx = obx_10

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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='HOSP_ALEMAN')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_ALEMAN')
        msh.date_time_of_message = '20250318090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HAL20250318090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80034567', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='21678934', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'GONZALEZ^Hector^Ruben^^^Sr.'
        pid.date_time_of_birth = '19700302'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. de Mayo 1234', xad_3='Mar del Plata', xad_4='Buenos Aires', xad_5='B7600DRC', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^223^4923810'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '21678934'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='LABINT', pl_2='COAG1', pl_3='A', pl_4='HALEMAN', pl_8='LABINT')
        pv1.attending_doctor = XCN(xcn_1='1100334455', xcn_2='Aguirre', xcn_3='Mariana', xcn_4='R', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='CIR', xcn_2='Cirugia', xcn_3='HALSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90034567', xcn_4='HALENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='SWISS_MEDICAL', cwe_2='Swiss Medical', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250318090000')

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
        orc.placer_order_number = EI(ei_1='ORD801003', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601003', ei_2='DNLAB')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250318093000^^R'
        orc.date_time_of_order_event = '20250318090000'
        orc.orc_10 = 'RGARCIA^Garcia^Rosa^M^^Lic.'
        orc.enterers_location = PL(pl_1='20250318090000')
        orc.order_effective_date_time = 'HOSP_ALEMAN'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801003', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601003', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='38875-1', cwe_2='Coagulograma Basico', cwe_3='LN')
        obr.observation_end_date_time = '20250318091000'
        obr.obr_15 = '1100334455^Aguirre^Mariana^R^^Dra.^^^MN'
        obr.filler_field_2 = '20250318093000'
        obr.diagnostic_serv_sect_id = 'NI^No Information^HL70507'

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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='HOSP_ALEMAN')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_ALEMAN')
        msh.date_time_of_message = '20250318133000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HAL20250318133000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80034567', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='21678934', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'GONZALEZ^Hector^Ruben^^^Sr.'
        pid.date_time_of_birth = '19700302'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. de Mayo 1234', xad_3='Mar del Plata', xad_4='Buenos Aires', xad_5='B7600DRC', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^223^4923810'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '21678934'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='LABINT', pl_2='COAG1', pl_3='A', pl_4='HALEMAN', pl_8='LABINT')
        pv1.attending_doctor = XCN(xcn_1='1100334455', xcn_2='Aguirre', xcn_3='Mariana', xcn_4='R', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='CIR', xcn_2='Cirugia', xcn_3='HALSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90034567', xcn_4='HALENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='SWISS_MEDICAL', cwe_2='Swiss Medical', cwe_3='HL70072')
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
        orc.placer_order_number = EI(ei_1='ORD801003', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601003', ei_2='DNLAB')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250318093000^^R'
        orc.date_time_of_order_event = '20250318133000'
        orc.orc_10 = 'RGARCIA^Garcia^Rosa^M^^Lic.'
        orc.enterers_location = PL(pl_1='20250318133000')
        orc.order_effective_date_time = 'HOSP_ALEMAN'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801003', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601003', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='38875-1', cwe_2='Coagulograma Basico', cwe_3='LN')
        obr.observation_date_time = '20250318091000'
        obr.obr_16 = '1100334455^Aguirre^Mariana^R^^Dra.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250318132800'
        obr.diagnostic_serv_sect_id = 'COAG'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='Tiempo de Protrombina', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '12.5'
        obx.units = CWE(cwe_1='seg')
        obx.reference_range = '11-14'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '1.05'
        obx_2.reference_range = '0.8-1.2'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='KPTT', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '32'
        obx_3.units = CWE(cwe_1='seg')
        obx_3.reference_range = '25-38'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3255-7', cwe_2='Fibrinogeno', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '285'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '200-400'
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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='LAB_CEMIC')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='LAB_CEMIC')
        msh.date_time_of_message = '20250322080500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'CEM20250322080500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80045678', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='37012458', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'FLORES^Ailen^Macarena^^^Sra.'
        pid.date_time_of_birth = '19930421'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. 9 de Julio 540', xad_3='Rosario', xad_4='Santa Fe', xad_5='S2000ABC', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^341^4256089'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltera', cwe_3='HL70002')
        pid.pid_19 = '37012458'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LABEXT', pl_2='URIN1', pl_3='A', pl_4='CEMIC', pl_8='LABEXT')
        pv1.attending_doctor = XCN(xcn_1='1100445566', xcn_2='Sanchez', xcn_3='Brenda', xcn_4='E', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='NEF', xcn_2='Nefrologia', xcn_3='CEMSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90045678', xcn_4='CEMENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 210', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250322080500')

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
        orc.placer_order_number = EI(ei_1='ORD801004', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601004', ei_2='DNLAB')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250322090000^^R'
        orc.date_time_of_order_event = '20250322080500'
        orc.orc_10 = 'MRUIZ^Ruiz^Marta^G^^Lic.'
        orc.enterers_location = PL(pl_1='20250322080500')
        orc.order_effective_date_time = 'LAB_CEMIC'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801004', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601004', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='24357-6', cwe_2='Orina Completa', cwe_3='LN')
        obr.observation_end_date_time = '20250322081500'
        obr.obr_15 = '1100445566^Sanchez^Brenda^E^^Dra.^^^MN'
        obr.filler_field_2 = '20250322090000'
        obr.diagnostic_serv_sect_id = 'NI^No Information^HL70507'

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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='LAB_CEMIC')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='LAB_CEMIC')
        msh.date_time_of_message = '20250322143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CEM20250322143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80045678', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='37012458', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'FLORES^Ailen^Macarena^^^Sra.'
        pid.date_time_of_birth = '19930421'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. 9 de Julio 540', xad_3='Rosario', xad_4='Santa Fe', xad_5='S2000ABC', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^341^4256089'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltera', cwe_3='HL70002')
        pid.pid_19 = '37012458'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LABEXT', pl_2='URIN1', pl_3='A', pl_4='CEMIC', pl_8='LABEXT')
        pv1.attending_doctor = XCN(xcn_1='1100445566', xcn_2='Sanchez', xcn_3='Brenda', xcn_4='E', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='NEF', xcn_2='Nefrologia', xcn_3='CEMSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90045678', xcn_4='CEMENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 210', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250322080500')

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
        orc.placer_order_number = EI(ei_1='ORD801004', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601004', ei_2='DNLAB')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250322090000^^R'
        orc.date_time_of_order_event = '20250322143000'
        orc.orc_10 = 'MRUIZ^Ruiz^Marta^G^^Lic.'
        orc.enterers_location = PL(pl_1='20250322143000')
        orc.order_effective_date_time = 'LAB_CEMIC'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801004', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601004', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='24357-6', cwe_2='Orina Completa', cwe_3='LN')
        obr.observation_date_time = '20250322081500'
        obr.obr_16 = '1100445566^Sanchez^Brenda^E^^Dra.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250322142800'
        obr.diagnostic_serv_sect_id = 'UA'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5778-6', cwe_2='Color', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'Amarillo'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='5767-9', cwe_2='Aspecto', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'Limpido'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='5803-2', cwe_2='pH', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '6.0'
        obx_3.reference_range = '5.0-8.0'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2965-2', cwe_2='Densidad', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '1.020'
        obx_4.reference_range = '1.005-1.030'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='5804-0', cwe_2='Proteinas', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = 'Negativo'
        obx_5.reference_range = 'Negativo'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='5792-7', cwe_2='Glucosa', cwe_3='LN')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = 'Negativo'
        obx_6.reference_range = 'Negativo'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='5821-4', cwe_2='Leucocitos', cwe_3='LN')
        obx_7.observation_sub_id = OG(og_1='1')
        obx_7.obx_5 = '2'
        obx_7.units = CWE(cwe_1='/campo')
        obx_7.reference_range = '0-5'
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='5808-1', cwe_2='Hematies', cwe_3='LN')
        obx_8.observation_sub_id = OG(og_1='1')
        obx_8.obx_5 = '1'
        obx_8.units = CWE(cwe_1='/campo')
        obx_8.reference_range = '0-3'
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'ST'
        obx_9.observation_identifier = CWE(cwe_1='5769-5', cwe_2='Bacterias', cwe_3='LN')
        obx_9.observation_sub_id = OG(og_1='1')
        obx_9.obx_5 = 'Escasas'
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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='HOSP_CLINICAS')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_CLINICAS')
        msh.date_time_of_message = '20250401071500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HCL20250401071500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80056789', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='22456789', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'PEREZ^Susana^Adriana^^^Sra.'
        pid.date_time_of_birth = '19660810'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Las Heras 1820', xad_3='Mendoza', xad_4='Mendoza', xad_5='M5500ACE', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^261^4287612'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casada', cwe_3='HL70002')
        pid.pid_19 = '22456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LABEXT', pl_2='EXTR2', pl_3='A', pl_4='HCLINICAS', pl_8='LABEXT')
        pv1.attending_doctor = XCN(xcn_1='1100556677', xcn_2='Medina', xcn_3='Esteban', xcn_4='H', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiologia', xcn_3='HCLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90056789', xcn_4='HCLENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='IOMA', cwe_2='IOMA', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250401071500')

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
        orc.placer_order_number = EI(ei_1='ORD801005', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601005', ei_2='DNLAB')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250401080000^^R'
        orc.date_time_of_order_event = '20250401071500'
        orc.orc_10 = 'AMORENO^Moreno^Adriana^S^^Lic.'
        orc.enterers_location = PL(pl_1='20250401071500')
        orc.order_effective_date_time = 'HOSP_CLINICAS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801005', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601005', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='Perfil Lipidico', cwe_3='LN')
        obr.observation_end_date_time = '20250401072500'
        obr.obr_15 = '1100556677^Medina^Esteban^H^^Dr.^^^MN'
        obr.filler_field_2 = '20250401080000'
        obr.diagnostic_serv_sect_id = 'NI^No Information^HL70507'

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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='HOSP_CLINICAS')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_CLINICAS')
        msh.date_time_of_message = '20250401140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HCL20250401140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80056789', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='22456789', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'PEREZ^Susana^Adriana^^^Sra.'
        pid.date_time_of_birth = '19660810'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Las Heras 1820', xad_3='Mendoza', xad_4='Mendoza', xad_5='M5500ACE', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^261^4287612'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casada', cwe_3='HL70002')
        pid.pid_19 = '22456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LABEXT', pl_2='EXTR2', pl_3='A', pl_4='HCLINICAS', pl_8='LABEXT')
        pv1.attending_doctor = XCN(xcn_1='1100556677', xcn_2='Medina', xcn_3='Esteban', xcn_4='H', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiologia', xcn_3='HCLSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90056789', xcn_4='HCLENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='IOMA', cwe_2='IOMA', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250401071500')

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
        orc.placer_order_number = EI(ei_1='ORD801005', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601005', ei_2='DNLAB')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250401080000^^R'
        orc.date_time_of_order_event = '20250401140000'
        orc.orc_10 = 'AMORENO^Moreno^Adriana^S^^Lic.'
        orc.enterers_location = PL(pl_1='20250401140000')
        orc.order_effective_date_time = 'HOSP_CLINICAS'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801005', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601005', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='Perfil Lipidico', cwe_3='LN')
        obr.observation_date_time = '20250401072500'
        obr.obr_16 = '1100556677^Medina^Esteban^H^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250401135800'
        obr.diagnostic_serv_sect_id = 'CH'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Colesterol Total', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '218'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '<200'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Trigliceridos', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '165'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '<150'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL Colesterol', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '52'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '>40'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL Colesterol (calculado)', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '133'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '<130'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='9830-1', cwe_2='Colesterol Total/HDL', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = '4.2'
        obx_5.reference_range = '<5.0'
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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='LAB_HIDALGO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='LAB_HIDALGO')
        msh.date_time_of_message = '20250408060000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'LHD20250408060000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250408060000'
        evn.operator_id = XCN(xcn_1='GFERNANDEZ', xcn_2='Fernandez', xcn_3='Graciela', xcn_4='N', xcn_6='Lic.')
        evn.event_occurred = '20250408055500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80067890', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='41234567', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'RUIZ^Bautista^Federico^^^Sr.'
        pid.date_time_of_birth = '19980803'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Corrientes 3450', xad_3='San Miguel de Tucuman', xad_4='Tucuman', xad_5='T4000IAB', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^381^4218903'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltero', cwe_3='HL70002')
        pid.pid_19 = '41234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LABEXT', pl_2='EXTR3', pl_3='A', pl_4='LHIDALGO', pl_8='LABEXT')
        pv1.attending_doctor = XCN(xcn_1='1100667788', xcn_2='Acosta', xcn_3='Liliana', xcn_4='B', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='MED', xcn_2='Medicina General', xcn_3='LHDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90067890', xcn_4='LHDENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 310', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250408060000')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='LAB_HIDALGO')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='LAB_HIDALGO')
        msh.date_time_of_message = '20250408061500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'LHD20250408061500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80067890', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='41234567', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'RUIZ^Bautista^Federico^^^Sr.'
        pid.date_time_of_birth = '19980803'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Corrientes 3450', xad_3='San Miguel de Tucuman', xad_4='Tucuman', xad_5='T4000IAB', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^381^4218903'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltero', cwe_3='HL70002')
        pid.pid_19 = '41234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LABEXT', pl_2='EXTR3', pl_3='A', pl_4='LHIDALGO', pl_8='LABEXT')
        pv1.attending_doctor = XCN(xcn_1='1100667788', xcn_2='Acosta', xcn_3='Liliana', xcn_4='B', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='END', xcn_2='Endocrinologia', xcn_3='LHDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90067890', xcn_4='LHDENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 310', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250408060000')

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
        orc.placer_order_number = EI(ei_1='ORD801006', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601006', ei_2='DNLAB')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250408070000^^R'
        orc.date_time_of_order_event = '20250408061500'
        orc.orc_10 = 'GFERNANDEZ^Fernandez^Graciela^N^^Lic.'
        orc.enterers_location = PL(pl_1='20250408061500')
        orc.order_effective_date_time = 'LAB_HIDALGO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801006', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601006', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='24348-5', cwe_2='Panel Tiroideo', cwe_3='LN')
        obr.observation_end_date_time = '20250408062000'
        obr.obr_15 = '1100667788^Acosta^Liliana^B^^Dra.^^^MN'
        obr.filler_field_2 = '20250408070000'
        obr.diagnostic_serv_sect_id = 'NI^No Information^HL70507'

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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='LAB_HIDALGO')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='LAB_HIDALGO')
        msh.date_time_of_message = '20250408153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LHD20250408153000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80067890', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='41234567', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'RUIZ^Bautista^Federico^^^Sr.'
        pid.date_time_of_birth = '19980803'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Corrientes 3450', xad_3='San Miguel de Tucuman', xad_4='Tucuman', xad_5='T4000IAB', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^381^4218903'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltero', cwe_3='HL70002')
        pid.pid_19 = '41234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LABEXT', pl_2='EXTR3', pl_3='A', pl_4='LHIDALGO', pl_8='LABEXT')
        pv1.attending_doctor = XCN(xcn_1='1100667788', xcn_2='Acosta', xcn_3='Liliana', xcn_4='B', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='END', xcn_2='Endocrinologia', xcn_3='LHDSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90067890', xcn_4='LHDENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='OSDE', cwe_2='OSDE 310', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250408060000')

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
        orc.placer_order_number = EI(ei_1='ORD801006', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601006', ei_2='DNLAB')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250408070000^^R'
        orc.date_time_of_order_event = '20250408153000'
        orc.orc_10 = 'GFERNANDEZ^Fernandez^Graciela^N^^Lic.'
        orc.enterers_location = PL(pl_1='20250408153000')
        orc.order_effective_date_time = 'LAB_HIDALGO'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801006', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601006', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='24348-5', cwe_2='Panel Tiroideo', cwe_3='LN')
        obr.observation_date_time = '20250408062000'
        obr.obr_16 = '1100667788^Acosta^Liliana^B^^Dra.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250408152800'
        obr.diagnostic_serv_sect_id = 'IMM'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '2.35'
        obx.units = CWE(cwe_1='mUI/L')
        obx.reference_range = '0.4-4.0'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3026-2', cwe_2='T4 Libre', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '1.15'
        obx_2.units = CWE(cwe_1='ng/dL')
        obx_2.reference_range = '0.8-1.8'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='T3 Total', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '125'
        obx_3.units = CWE(cwe_1='ng/dL')
        obx_3.reference_range = '80-200'
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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='HOSP_MUNIZ')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_MUNIZ')
        msh.date_time_of_message = '20250415093000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HMU20250415093000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80078901', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='30123987', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'ALVAREZ^Walter^Damian^^^Sr.'
        pid.date_time_of_birth = '19820914'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Pueyrredon 980', xad_3='La Plata', xad_4='Buenos Aires', xad_5='B1900AAA', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^221^4823715'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltero', cwe_3='HL70002')
        pid.pid_19 = '30123987'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='LABINT', pl_2='MICRO1', pl_3='A', pl_4='HMUNIZ', pl_8='LABINT')
        pv1.attending_doctor = XCN(xcn_1='1100778899', xcn_2='Ramirez', xcn_3='Cristian', xcn_4='D', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='INF', xcn_2='Infectologia', xcn_3='HMUSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90078901', xcn_4='HMUENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250415093000')

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
        orc.placer_order_number = EI(ei_1='ORD801007', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601007', ei_2='DNLAB')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250415100000^^R'
        orc.date_time_of_order_event = '20250415093000'
        orc.orc_10 = 'LDIAZ^Diaz^Liliana^S^^Lic.'
        orc.enterers_location = PL(pl_1='20250415093000')
        orc.order_effective_date_time = 'HOSP_MUNIZ'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801007', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601007', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='600-7', cwe_2='Hemocultivo', cwe_3='LN')
        obr.observation_end_date_time = '20250415094000'
        obr.obr_17 = '1100778899^Ramirez^Cristian^D^^Dr.^^^MN'
        obr.charge_to_practice = MOC(moc_1='20250415100000')
        obr.parent_result = PRL(prl_1='NI', prl_2='No Information', prl_3='HL70507')

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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='HOSP_MUNIZ')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_MUNIZ')
        msh.date_time_of_message = '20250418161500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HMU20250418161500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80078901', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='30123987', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'ALVAREZ^Walter^Damian^^^Sr.'
        pid.date_time_of_birth = '19820914'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Pueyrredon 980', xad_3='La Plata', xad_4='Buenos Aires', xad_5='B1900AAA', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^221^4823715'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Soltero', cwe_3='HL70002')
        pid.pid_19 = '30123987'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='LABINT', pl_2='MICRO1', pl_3='A', pl_4='HMUNIZ', pl_8='LABINT')
        pv1.attending_doctor = XCN(xcn_1='1100778899', xcn_2='Ramirez', xcn_3='Cristian', xcn_4='D', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='INF', xcn_2='Infectologia', xcn_3='HMUSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90078901', xcn_4='HMUENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250415093000')

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
        orc.placer_order_number = EI(ei_1='ORD801007', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601007', ei_2='DNLAB')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250415100000^^R'
        orc.date_time_of_order_event = '20250418161500'
        orc.orc_10 = 'LDIAZ^Diaz^Liliana^S^^Lic.'
        orc.enterers_location = PL(pl_1='20250418161500')
        orc.order_effective_date_time = 'HOSP_MUNIZ'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801007', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601007', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='600-7', cwe_2='Hemocultivo', cwe_3='LN')
        obr.observation_date_time = '20250415094000'
        obr.obr_16 = '1100778899^Ramirez^Cristian^D^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250418161300'
        obr.diagnostic_serv_sect_id = 'MB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Hemocultivo Resultado', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'POSITIVO - Staphylococcus aureus'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='29576-6', cwe_2='Antibiograma', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'Oxacilina: S, Vancomicina: S, Gentamicina: S, Ciprofloxacina: S, TMS: S, Eritromicina: R, Clindamicina: R'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='PDF', cwe_2='Informe Microbiologia Completo', cwe_3='AUSPDI')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = (
            'DNLAB^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA1IDAgUgo+'
            'PgplbmRvYmoKNCAwIG9iago8PAovTGVuZ3RoIDQ0Cj4+CnN0cmVhbQpCVAovRjEgMTggVGYKMTAwIDcwMCBUZAooSGVtb2N1bHRpdm8gLSBJbmZvcm1lKSBUagpFVAplbmRzdHJlYW0K'
        )
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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='LAB_TCBA')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='LAB_TCBA')
        msh.date_time_of_message = '20250422110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TCB20250422110000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80089012', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='25890123', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'DIAZ^Norma^Susana^^^Sra.'
        pid.date_time_of_birth = '19730520'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Belgrano 920', xad_3='Salta', xad_4='Salta', xad_5='A4400ABC', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^387^4319825'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casada', cwe_3='HL70002')
        pid.pid_19 = '25890123'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LABEXT', pl_2='EXTR4', pl_3='A', pl_4='LTCBA', pl_8='LABEXT')
        pv1.attending_doctor = XCN(xcn_1='1100889900', xcn_2='Sosa', xcn_3='Andres', xcn_4='J', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='END', xcn_2='Endocrinologia', xcn_3='TCBSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90089012', xcn_4='TCBENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250422110000')

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
        orc.placer_order_number = EI(ei_1='ORD801008', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601008', ei_2='DNLAB')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250422090000^^R'
        orc.date_time_of_order_event = '20250422110000'
        orc.orc_10 = 'HCASTRO^Castro^Hector^P^^Lic.'
        orc.enterers_location = PL(pl_1='20250422110000')
        orc.order_effective_date_time = 'LAB_TCBA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801008', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601008', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobina Glicosilada A1c', cwe_3='LN')
        obr.observation_date_time = '20250422080000'
        obr.obr_16 = '1100889900^Sosa^Andres^J^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250422105800'
        obr.diagnostic_serv_sect_id = 'CH'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '7.2'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '<6.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucosa en Ayunas', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '142'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '70-110'
        obx_2.interpretation_codes = CWE(cwe_1='H')
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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='HOSP_POSADAS')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_POSADAS')
        msh.date_time_of_message = '20250428080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HPO20250428080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80090123', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='35012890', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'LOPEZ^Marcos^Sebastian^^^Sr.'
        pid.date_time_of_birth = '19880110'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Calle Lavalle 360', xad_3='Posadas', xad_4='Misiones', xad_5='N3300CDE', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^376^4421730'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '35012890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LABEXT', pl_2='SERO1', pl_3='A', pl_4='HPOSADAS', pl_8='LABEXT')
        pv1.attending_doctor = XCN(xcn_1='1100990011', xcn_2='Benitez', xcn_3='Yanina', xcn_4='V', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='GAS', xcn_2='Gastroenterologia', xcn_3='HPOSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90090123', xcn_4='HPOENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250428080000')

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
        orc.placer_order_number = EI(ei_1='ORD801009', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601009', ei_2='DNLAB')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250428090000^^R'
        orc.date_time_of_order_event = '20250428080000'
        orc.orc_10 = 'FVEGA^Vega^Federico^A^^Lic.'
        orc.enterers_location = PL(pl_1='20250428080000')
        orc.order_effective_date_time = 'HOSP_POSADAS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801009', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601009', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='24360-0', cwe_2='Panel Hepatitis', cwe_3='LN')
        obr.observation_end_date_time = '20250428081000'
        obr.obr_15 = '1100990011^Benitez^Yanina^V^^Dra.^^^MN'
        obr.filler_field_2 = '20250428090000'
        obr.diagnostic_serv_sect_id = 'NI^No Information^HL70507'

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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='HOSP_POSADAS')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_POSADAS')
        msh.date_time_of_message = '20250429150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HPO20250429150000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80090123', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='35012890', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'LOPEZ^Marcos^Sebastian^^^Sr.'
        pid.date_time_of_birth = '19880110'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Calle Lavalle 360', xad_3='Posadas', xad_4='Misiones', xad_5='N3300CDE', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^376^4421730'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='C', cwe_2='Casado', cwe_3='HL70002')
        pid.pid_19 = '35012890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LABEXT', pl_2='SERO1', pl_3='A', pl_4='HPOSADAS', pl_8='LABEXT')
        pv1.attending_doctor = XCN(xcn_1='1100990011', xcn_2='Benitez', xcn_3='Yanina', xcn_4='V', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='GAS', xcn_2='Gastroenterologia', xcn_3='HPOSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90090123', xcn_4='HPOENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250428080000')

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
        orc.placer_order_number = EI(ei_1='ORD801009', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601009', ei_2='DNLAB')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250428090000^^R'
        orc.date_time_of_order_event = '20250429150000'
        orc.orc_10 = 'FVEGA^Vega^Federico^A^^Lic.'
        orc.enterers_location = PL(pl_1='20250429150000')
        orc.order_effective_date_time = 'HOSP_POSADAS'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801009', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601009', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='24360-0', cwe_2='Panel Hepatitis', cwe_3='LN')
        obr.observation_date_time = '20250428081000'
        obr.obr_16 = '1100990011^Benitez^Yanina^V^^Dra.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250429145800'
        obr.diagnostic_serv_sect_id = 'SER'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5196-1', cwe_2='HBsAg', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'No Reactivo'
        obx.reference_range = 'No Reactivo'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='16935-9', cwe_2='Anti-HBs', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'Reactivo (>100 mUI/mL)'
        obx_2.reference_range = 'Reactivo'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='13955-0', cwe_2='Anti-HCV', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = 'No Reactivo'
        obx_3.reference_range = 'No Reactivo'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='40726-2', cwe_2='Anti-HAV IgG', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = 'Reactivo'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='40725-4', cwe_2='Anti-HAV IgM', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = 'No Reactivo'
        obx_5.reference_range = 'No Reactivo'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ED'
        obx_6.observation_identifier = CWE(cwe_1='PDF', cwe_2='Informe Serologia Hepatitis', cwe_3='AUSPDI')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = (
            'DNLAB^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA1IDAgUgo+'
            'PgplbmRvYmoKNCAwIG9iago8PAovTGVuZ3RoIDUyCj4+CnN0cmVhbQpCVAovRjEgMTggVGYKMTAwIDcwMCBUZAooUGFuZWwgSGVwYXRpdGlzIC0gSW5mb3JtZSkgVGoKRVQKZW5kc3Ry'
            'ZWFtCg=='
        )
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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='HOSP_ARGERICH')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HOSP_ARGERICH')
        msh.date_time_of_message = '20250503052000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'HAR20250503052000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250503052000'
        evn.operator_id = XCN(xcn_1='RMEDINA', xcn_2='Medina', xcn_3='Roberto', xcn_4='C', xcn_6='Lic.')
        evn.event_occurred = '20250503050000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80101234', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='26789012', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'AGUERO^Mirta^Yolanda^^^Sra.'
        pid.date_time_of_birth = '19770218'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. San Juan 1845', xad_3='Resistencia', xad_4='Chaco', xad_5='H3500ABC', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^362^4421875'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='D', cwe_2='Divorciada', cwe_3='HL70002')
        pid.pid_19 = '26789012'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='AGUERO', xpn_2='Tobias', xpn_3='Joaquin')
        nk1.relationship = CWE(cwe_1='HIJ', cwe_2='Hijo', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Av. San Juan 1845', xad_3='Resistencia', xad_4='Chaco', xad_5='H3500ABC', xad_6='AR', xad_7='L')
        nk1.nk1_5 = '^PRN^PH^^^362^4421876'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='U301', pl_3='A', pl_4='HARGERICH', pl_8='UTI')
        pv1.attending_doctor = XCN(xcn_1='1101101122', xcn_2='Vega', xcn_3='Pablo', xcn_4='L', xcn_6='Dr.', xcn_9='MN')
        pv1.referring_doctor = XCN(xcn_1='1101101123', xcn_2='Cabrera', xcn_3='Estefania', xcn_4='A', xcn_6='Dra.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='INF', xcn_2='Infectologia', xcn_3='HARSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90101234', xcn_4='HARENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250503052000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='PAMI001', cwe_2='PAMI', cwe_4='PAMI')
        in1.insurance_company_id = CX(cx_1='60001')
        in1.insurance_company_name = XON(xon_1='PAMI')
        in1.insurance_company_address = XAD(xad_1='Av. Corrientes 655', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1043AAG', xad_6='AR')
        in1.in1_6 = '^PRN^PH^^^138'
        in1.name_of_insured = XPN(xpn_1='20240101')
        in1.insureds_relationship_to_patient = CWE(cwe_1='20251231')
        in1.assignment_of_benefits = CWE(cwe_1='1', cwe_2='Titular', cwe_3='HL70072')
        in1.coordination_of_benefits = CWE(cwe_1='AGUERO', cwe_2='Mirta', cwe_3='Yolanda')
        in1.coord_of_ben_priority = '01^Self^HL70063'
        in1.notice_of_admission_flag = '19770218'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='A41.9', cwe_2='Sepsis no especificada', cwe_3='I10')
        dg1.diagnosis_date_time = '20250503'
        dg1.diagnosis_type = CWE(cwe_1='A', cwe_2='Admitting', cwe_3='HL70052')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance
        msg.extra_segments = [dg1]

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
    """ Based on live/ar/ar-centralab-dnlab.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DNLAB')
        msh.sending_facility = HD(hd_1='HOSP_ARGERICH')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='HOSP_ARGERICH')
        msh.date_time_of_message = '20250503064500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HAR20250503064500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LAB80101234', cx_4='DNLAB', cx_5='MRN'), CX(cx_1='26789012', cx_4='RENAPER', cx_5='NI')]
        pid.pid_5 = 'AGUERO^Mirta^Yolanda^^^Sra.'
        pid.date_time_of_birth = '19770218'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. San Juan 1845', xad_3='Resistencia', xad_4='Chaco', xad_5='H3500ABC', xad_6='AR', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^362^4421875'
        pid.primary_language = CWE(cwe_1='spa', cwe_2='Spanish', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='D', cwe_2='Divorciada', cwe_3='HL70002')
        pid.pid_19 = '26789012'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='U301', pl_3='A', pl_4='HARGERICH', pl_8='UTI')
        pv1.attending_doctor = XCN(xcn_1='1101101122', xcn_2='Vega', xcn_3='Pablo', xcn_4='L', xcn_6='Dr.', xcn_9='MN')
        pv1.consulting_doctor = XCN(xcn_1='INF', xcn_2='Infectologia', xcn_3='HARSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90101234', xcn_4='HARENC', xcn_5='VN')
        pv1.patient_type = CWE(cwe_1='PAMI', cwe_2='PAMI', cwe_3='HL70072')
        pv1.pending_location = PL(pl_1='20250503052000')

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
        orc.placer_order_number = EI(ei_1='ORD801010', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='LAB601010', ei_2='DNLAB')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250503060000^^R'
        orc.date_time_of_order_event = '20250503064500'
        orc.orc_10 = 'LDIAZ^Diaz^Liliana^S^^Lic.'
        orc.enterers_location = PL(pl_1='20250503064500')
        orc.order_effective_date_time = 'HOSP_ARGERICH'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD801010', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='LAB601010', ei_2='DNLAB')
        obr.universal_service_identifier = CWE(cwe_1='24336-0', cwe_2='Gases en Sangre Arterial', cwe_3='LN')
        obr.observation_date_time = '20250503060500'
        obr.obr_16 = '1101101122^Vega^Pablo^L^^Dr.^^^MN'
        obr.results_rpt_status_chng_date_time = '20250503064300'
        obr.diagnostic_serv_sect_id = 'BGA'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='pH Arterial', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '7.32'
        obx.reference_range = '7.35-7.45'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='pCO2', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '48'
        obx_2.units = CWE(cwe_1='mmHg')
        obx_2.reference_range = '35-45'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2703-7', cwe_2='pO2', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '68'
        obx_3.units = CWE(cwe_1='mmHg')
        obx_3.reference_range = '80-100'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1959-6', cwe_2='Bicarbonato', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '24.1'
        obx_4.units = CWE(cwe_1='mEq/L')
        obx_4.reference_range = '22-26'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2708-6', cwe_2='Saturacion O2', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = '91'
        obx_5.units = CWE(cwe_1='%')
        obx_5.reference_range = '95-100'
        obx_5.interpretation_codes = CWE(cwe_1='L')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2713-6', cwe_2='Exceso de Base', cwe_3='LN')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = '-1.8'
        obx_6.units = CWE(cwe_1='mEq/L')
        obx_6.reference_range = '-2 a +2'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potasio', cwe_3='LN')
        obx_7.observation_sub_id = OG(og_1='1')
        obx_7.obx_5 = '4.8'
        obx_7.units = CWE(cwe_1='mEq/L')
        obx_7.reference_range = '3.5-5.5'
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodio', cwe_3='LN')
        obx_8.observation_sub_id = OG(og_1='1')
        obx_8.obx_5 = '138'
        obx_8.units = CWE(cwe_1='mEq/L')
        obx_8.reference_range = '135-145'
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='2000-8', cwe_2='Calcio Ionico', cwe_3='LN')
        obx_9.observation_sub_id = OG(og_1='1')
        obx_9.obx_5 = '1.12'
        obx_9.units = CWE(cwe_1='mmol/L')
        obx_9.reference_range = '1.05-1.30'
        obx_9.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'NM'
        obx_10.observation_identifier = CWE(cwe_1='2947-0', cwe_2='Lactato', cwe_3='LN')
        obx_10.observation_sub_id = OG(og_1='1')
        obx_10.obx_5 = '3.8'
        obx_10.units = CWE(cwe_1='mmol/L')
        obx_10.reference_range = '0.5-2.0'
        obx_10.interpretation_codes = CWE(cwe_1='H')
        obx_10.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_10 = OruR01Observation()
        observation_10.obx = obx_10

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
