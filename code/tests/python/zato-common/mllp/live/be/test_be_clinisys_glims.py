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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MSG, PL, PT, VID, XCN, XPN
from zato.hl7v2.v2_9.groups import OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ACK, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import DG1, MSA, MSH, NTE, OBR, OBX, ORC, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('be', 'be-clinisys-glims.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/be/be-clinisys-glims.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='AZ_TURNHOUT')
        msh.receiving_application = HD(hd_1='GLIMS')
        msh.receiving_facility = HD(hd_1='AZ_TURNHOUT')
        msh.date_time_of_message = '20250410083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ORM001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='612345', cx_4='AZ_TURNHOUT', cx_5='PI'),
            CX(cx_1='85061234567', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Janssens', xpn_2='Griet', xpn_7='L')
        pid.date_time_of_birth = '19850612'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='204', pl_3='1', pl_4='AZ_TURNHOUT')
        pv1.attending_doctor = XCN(xcn_1='22315678901', xcn_2='Coppens', xcn_3='Dirk', xcn_6='Dr.', xcn_9='AZ_TURNHOUT', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD1001', ei_2='ORBIS')
        orc.placer_order_group_number = EI(ei_1='GRP001', ei_2='ORBIS')
        orc.date_time_of_order_event = '20250410083000'
        orc.orc_12 = '22315678901^Coppens^Dirk^^^Dr.^^^AZ_TURNHOUT^L^^^NIHDI'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1001', ei_2='ORBIS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='CMP', cwe_3='LN')
        obr.observation_date_time = '20250410083000'
        obr.obr_16 = '22315678901^Coppens^Dirk^^^Dr.^^^AZ_TURNHOUT^L^^^NIHDI'
        obr.obr_27 = '^ROUTINE'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E11.9', cwe_2='Diabetes mellitus type 2', cwe_3='ICD10BE')

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
        nte.comment = 'Nuchtere bloedafname. Controle diabetesinstellingen.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/be/be-clinisys-glims.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPD')
        msh.sending_facility = HD(hd_1='UZ_GENT')
        msh.receiving_application = HD(hd_1='GLIMS')
        msh.receiving_facility = HD(hd_1='UZ_GENT')
        msh.date_time_of_message = '20250512090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ORM002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='H890567', cx_4='UZ_GENT', cx_5='PI'),
            CX(cx_1='78052345678', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Goossens', xpn_2='Pieter', xpn_7='L')
        pid.date_time_of_birth = '19780523'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HEMA', pl_2='301', pl_3='2', pl_4='UZ_GENT')
        pv1.attending_doctor = XCN(xcn_1='22319876543', xcn_2='De Smet', xcn_3='Katrien', xcn_6='Prof.Dr.', xcn_9='UZ_GENT', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD2001', ei_2='EPD')
        orc.placer_order_group_number = EI(ei_1='GRP002', ei_2='EPD')
        orc.date_time_of_order_event = '20250512090000'
        orc.orc_12 = '22319876543^De Smet^Katrien^^^Prof.Dr.^^^UZ_GENT^L^^^NIHDI'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2001', ei_2='EPD')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC with Diff', cwe_3='LN')
        obr.observation_date_time = '20250512090000'
        obr.obr_16 = '22319876543^De Smet^Katrien^^^Prof.Dr.^^^UZ_GENT^L^^^NIHDI'
        obr.obr_27 = '^STAT'

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
        obr_2.placer_order_number = EI(ei_1='ORD2001', ei_2='EPD')
        obr_2.universal_service_identifier = CWE(cwe_1='34714-6', cwe_2='INR', cwe_3='LN')
        obr_2.observation_date_time = '20250512090000'
        obr_2.obr_16 = '22319876543^De Smet^Katrien^^^Prof.Dr.^^^UZ_GENT^L^^^NIHDI'
        obr_2.obr_27 = '^STAT'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Spoedaanvraag. Patient onder anticoagulantia.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, nte]

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
    """ Based on live/be/be-clinisys-glims.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='AZ_TURNHOUT')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='AZ_TURNHOUT')
        msh.date_time_of_message = '20250410153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='612345', cx_4='AZ_TURNHOUT', cx_5='PI'),
            CX(cx_1='85061234567', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Janssens', xpn_2='Griet', xpn_7='L')
        pid.date_time_of_birth = '19850612'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='204', pl_3='1', pl_4='AZ_TURNHOUT')

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
        orc.placer_order_number = EI(ei_1='ORD1001', ei_2='ORBIS')
        orc.filler_order_number = EI(ei_1='FIL3001', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1001', ei_2='ORBIS')
        obr.filler_order_number = EI(ei_1='FIL3001', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='CMP', cwe_3='LN')
        obr.observation_date_time = '20250410083000'
        obr.obr_16 = '22315678901^Coppens^Dirk^^^Dr.^^^AZ_TURNHOUT^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250410150000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '8.2'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.9-6.1'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obx_2.obx_5 = '58'
        obx_2.units = CWE(cwe_1='mmol/mol')
        obx_2.reference_range = '20-42'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_3.obx_5 = '72'
        obx_3.units = CWE(cwe_1='umol/L')
        obx_3.reference_range = '45-84'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Ureum', cwe_3='LN')
        obx_4.obx_5 = '6.1'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '2.5-7.5'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Natrium', cwe_3='LN')
        obx_5.obx_5 = '141'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '136-145'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Kalium', cwe_3='LN')
        obx_6.obx_5 = '4.5'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '3.5-5.1'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='17861-6', cwe_2='Calcium', cwe_3='LN')
        obx_7.obx_5 = '2.38'
        obx_7.units = CWE(cwe_1='mmol/L')
        obx_7.reference_range = '2.15-2.55'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALAT', cwe_3='LN')
        obx_8.obx_5 = '32'
        obx_8.units = CWE(cwe_1='U/L')
        obx_8.reference_range = '7-56'
        obx_8.interpretation_codes = CWE(cwe_1='N')
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='1920-8', cwe_2='ASAT', cwe_3='LN')
        obx_9.obx_5 = '25'
        obx_9.units = CWE(cwe_1='U/L')
        obx_9.reference_range = '10-40'
        obx_9.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/be/be-clinisys-glims.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='UZ_GENT')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='UZ_GENT')
        msh.date_time_of_message = '20250512141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='H890567', cx_4='UZ_GENT', cx_5='PI'),
            CX(cx_1='78052345678', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Goossens', xpn_2='Pieter', xpn_7='L')
        pid.date_time_of_birth = '19780523'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HEMA', pl_2='301', pl_3='2', pl_4='UZ_GENT')

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
        orc.placer_order_number = EI(ei_1='ORD2001', ei_2='EPD')
        orc.filler_order_number = EI(ei_1='FIL4001', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2001', ei_2='EPD')
        obr.filler_order_number = EI(ei_1='FIL4001', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC with Diff', cwe_3='LN')
        obr.observation_date_time = '20250512090000'
        obr.obr_16 = '22319876543^De Smet^Katrien^^^Prof.Dr.^^^UZ_GENT^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250512140000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobine', cwe_3='LN')
        obx.obx_5 = '9.8'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '13.5-17.5'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocriet', cwe_3='LN')
        obx_2.obx_5 = '30.2'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '38.3-48.6'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocyten', cwe_3='LN')
        obx_3.obx_5 = '12.5'
        obx_3.units = CWE(cwe_1='10*9/L')
        obx_3.reference_range = '4.5-11.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='787-2', cwe_2='Erytrocyten', cwe_3='LN')
        obx_4.obx_5 = '3.42'
        obx_4.units = CWE(cwe_1='10*12/L')
        obx_4.reference_range = '4.50-5.90'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Trombocyten', cwe_3='LN')
        obx_5.obx_5 = '156'
        obx_5.units = CWE(cwe_1='10*9/L')
        obx_5.reference_range = '150-400'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='770-8', cwe_2='Neutrofielen', cwe_3='LN')
        obx_6.obx_5 = '8.9'
        obx_6.units = CWE(cwe_1='10*9/L')
        obx_6.reference_range = '1.8-7.7'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='731-0', cwe_2='Lymfocyten', cwe_3='LN')
        obx_7.obx_5 = '1.8'
        obx_7.units = CWE(cwe_1='10*9/L')
        obx_7.reference_range = '1.0-4.8'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='742-7', cwe_2='Monocyten', cwe_3='LN')
        obx_8.obx_5 = '1.2'
        obx_8.units = CWE(cwe_1='10*9/L')
        obx_8.reference_range = '0.2-0.8'
        obx_8.interpretation_codes = CWE(cwe_1='H')
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='713-8', cwe_2='Eosinofielen', cwe_3='LN')
        obx_9.obx_5 = '0.4'
        obx_9.units = CWE(cwe_1='10*9/L')
        obx_9.reference_range = '0.0-0.5'
        obx_9.interpretation_codes = CWE(cwe_1='N')
        obx_9.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'NM'
        obx_10.observation_identifier = CWE(cwe_1='704-7', cwe_2='Basofielen', cwe_3='LN')
        obx_10.obx_5 = '0.2'
        obx_10.units = CWE(cwe_1='10*9/L')
        obx_10.reference_range = '0.0-0.1'
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

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'RE'
        orc_2.placer_order_number = EI(ei_1='ORD2001', ei_2='EPD')
        orc_2.filler_order_number = EI(ei_1='FIL4002', ei_2='GLIMS')
        orc_2.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order_2 = OruR01CommonOrder()
        common_order_2.orc = orc_2

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='ORD2001', ei_2='EPD')
        obr_2.filler_order_number = EI(ei_1='FIL4002', ei_2='GLIMS')
        obr_2.universal_service_identifier = CWE(cwe_1='34714-6', cwe_2='INR', cwe_3='LN')
        obr_2.observation_date_time = '20250512090000'
        obr_2.obr_16 = '22319876543^De Smet^Katrien^^^Prof.Dr.^^^UZ_GENT^L^^^NIHDI'
        obr_2.results_rpt_status_chng_date_time = '20250512140500'
        obr_2.diagnostic_serv_sect_id = 'LAB'
        obr_2.result_status = 'F'

        # .. build OBX ..
        obx_11 = OBX()
        obx_11.set_id_obx = '11'
        obx_11.value_type = 'NM'
        obx_11.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_11.obx_5 = '2.8'
        obx_11.units = CWE(cwe_1='{INR}')
        obx_11.reference_range = '2.0-3.0'
        obx_11.interpretation_codes = CWE(cwe_1='N')
        obx_11.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_11 = OruR01Observation()
        observation_11.obx = obx_11

        # .. build OBX ..
        obx_12 = OBX()
        obx_12.set_id_obx = '12'
        obx_12.value_type = 'NM'
        obx_12.observation_identifier = CWE(cwe_1='5902-2', cwe_2='PT', cwe_3='LN')
        obx_12.obx_5 = '28.5'
        obx_12.units = CWE(cwe_1='sec')
        obx_12.reference_range = '11.0-15.0'
        obx_12.interpretation_codes = CWE(cwe_1='H')
        obx_12.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_12 = OruR01Observation()
        observation_12.obx = obx_12

        # .. build the ORDER_OBSERVATION group ..
        order_observation_2 = OruR01OrderObservation()
        order_observation_2.common_order = common_order_2
        order_observation_2.obr = obr_2
        order_observation_2.observation = observation_11
        order_observation_2.observation_2 = observation_12

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
    """ Based on live/be/be-clinisys-glims.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='CHU_CHARLEROI')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='CHU_CHARLEROI')
        msh.date_time_of_message = '20250318110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='D567890', cx_4='CHU_CHARLEROI', cx_5='PI'),
            CX(cx_1='72111567890', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Dupont', xpn_2='Claudine', xpn_7='L')
        pid.date_time_of_birth = '19721115'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='ENDO', pl_3='01', pl_4='CHU_CHARLEROI')
        pv1.attending_doctor = XCN(xcn_1='22324567890', xcn_2='Simon', xcn_3='Philippe', xcn_6='Dr.', xcn_9='CHU_CHARLEROI', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD3001', ei_2='EPD')
        orc.filler_order_number = EI(ei_1='FIL5001', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD3001', ei_2='EPD')
        obr.filler_order_number = EI(ei_1='FIL5001', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='34528-0', cwe_2='Bilan thyroïdien', cwe_3='LN')
        obr.observation_date_time = '20250318083000'
        obr.obr_16 = '22324567890^Simon^Philippe^^^Dr.^^^CHU_CHARLEROI^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250318105000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '6.8'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.27-4.20'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='T4 Libre', cwe_3='LN')
        obx_2.obx_5 = '10.2'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '12.0-22.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='T3 Libre', cwe_3='LN')
        obx_3.obx_5 = '3.8'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '3.1-6.8'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Hypothyroïdie subclinique. Contrôle recommandé dans 6 semaines.'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3
        observation_3.nte = nte

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
    """ Based on live/be/be-clinisys-glims.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='AZ_HERENTALS')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='AZ_HERENTALS')
        msh.date_time_of_message = '20250605143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='J223344', cx_4='AZ_HERENTALS', cx_5='PI'),
            CX(cx_1='97050312345', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Mertens', xpn_2='Elien', xpn_7='L')
        pid.date_time_of_birth = '19970503'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='110', pl_3='1', pl_4='AZ_HERENTALS')
        pv1.attending_doctor = XCN(xcn_1='22354321987', xcn_2='Willems', xcn_3='Tom', xcn_6='Dr.', xcn_9='AZ_HERENTALS', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD6001', ei_2='ORBIS')
        orc.filler_order_number = EI(ei_1='FIL7001', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD6001', ei_2='ORBIS')
        obr.filler_order_number = EI(ei_1='FIL7001', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='24356-8', cwe_2='Urineonderzoek', cwe_3='LN')
        obr.observation_date_time = '20250605080000'
        obr.obr_16 = '22354321987^Willems^Tom^^^Dr.^^^AZ_HERENTALS^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250605140000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5778-6', cwe_2='Kleur', cwe_3='LN')
        obx.obx_5 = 'Donkergeel'
        obx.reference_range = 'Strohalm-geel'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='5767-9', cwe_2='Aspect', cwe_3='LN')
        obx_2.obx_5 = 'Troebel'
        obx_2.reference_range = 'Helder'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2756-5', cwe_2='pH', cwe_3='LN')
        obx_3.obx_5 = '5.5'
        obx_3.reference_range = '5.0-8.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2965-2', cwe_2='Soortelijk gewicht', cwe_3='LN')
        obx_4.obx_5 = '1.025'
        obx_4.reference_range = '1.005-1.030'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='20454-5', cwe_2='Eiwit', cwe_3='LN')
        obx_5.obx_5 = '2+'
        obx_5.reference_range = 'Negatief'
        obx_5.interpretation_codes = CWE(cwe_1='A')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='5792-7', cwe_2='Glucose', cwe_3='LN')
        obx_6.obx_5 = 'Negatief'
        obx_6.reference_range = 'Negatief'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='5811-5', cwe_2='Leukocyten', cwe_3='LN')
        obx_7.obx_5 = '25'
        obx_7.units = CWE(cwe_1='/HPF')
        obx_7.reference_range = '0-5'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='5804-0', cwe_2='Erytrocyten', cwe_3='LN')
        obx_8.obx_5 = '15'
        obx_8.units = CWE(cwe_1='/HPF')
        obx_8.reference_range = '0-3'
        obx_8.interpretation_codes = CWE(cwe_1='H')
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'ST'
        obx_9.observation_identifier = CWE(cwe_1='5802-4', cwe_2='Nitriet', cwe_3='LN')
        obx_9.obx_5 = 'Positief'
        obx_9.reference_range = 'Negatief'
        obx_9.interpretation_codes = CWE(cwe_1='A')
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
    """ Based on live/be/be-clinisys-glims.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='CHU_CHARLEROI')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='CHU_CHARLEROI')
        msh.date_time_of_message = '20250322163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MICRO001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='D901234', cx_4='CHU_CHARLEROI', cx_5='PI'),
            CX(cx_1='74030967890', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Lejeune', xpn_2='Thierry', xpn_7='L')
        pid.date_time_of_birth = '19740309'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='205', pl_3='3', pl_4='CHU_CHARLEROI')
        pv1.attending_doctor = XCN(xcn_1='22327890123', xcn_2='Dubois', xcn_3='Veronique', xcn_6='Dr.', xcn_9='CHU_CHARLEROI', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD7001', ei_2='EPD')
        orc.filler_order_number = EI(ei_1='FIL8001', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD7001', ei_2='EPD')
        obr.filler_order_number = EI(ei_1='FIL8001', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Hémoculture', cwe_3='LN')
        obr.observation_date_time = '20250320090000'
        obr.obr_16 = '22327890123^Dubois^Veronique^^^Dr.^^^CHU_CHARLEROI^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250322160000'
        obr.diagnostic_serv_sect_id = 'MB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='11475-1', cwe_2='Identification micro-organisme', cwe_3='LN')
        obx.obx_5 = '91302008^Escherichia coli^SCT'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Profil de sensibilité', cwe_3='LN')
        obx_2.obx_5 = 'Voir antibiogramme'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18862-3', cwe_2='Amoxicilline', cwe_3='LN')
        obx_3.obx_5 = 'R^Résistant'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18900-1', cwe_2='Amoxicilline-clavulanate', cwe_3='LN')
        obx_4.obx_5 = 'S^Sensible'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18928-2', cwe_2='Gentamicine', cwe_3='LN')
        obx_5.obx_5 = 'S^Sensible'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18903-5', cwe_2='Ciprofloxacine', cwe_3='LN')
        obx_6.obx_5 = 'I^Intermédiaire'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='18961-3', cwe_2='Vancomycine', cwe_3='LN')
        obx_7.obx_5 = 'S^Sensible'
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='35659-2', cwe_2='CMI Ciprofloxacine', cwe_3='LN')
        obx_8.obx_5 = '0.5'
        obx_8.units = CWE(cwe_1='ug/mL')
        obx_8.reference_range = '<=0.25'
        obx_8.interpretation_codes = CWE(cwe_1='H')
        obx_8.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'BLSE négatif. Recommandation: Amoxicilline-clavulanate IV.'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8
        observation_8.nte = nte

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
    """ Based on live/be/be-clinisys-glims.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='AZ_ALMA')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='AZ_ALMA')
        msh.date_time_of_message = '20250714110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='B445566', cx_4='AZ_ALMA', cx_5='PI'),
            CX(cx_1='62081245678', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Claes', xpn_2='Hilde', xpn_7='L')
        pid.date_time_of_birth = '19620812'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='GASTRO', pl_3='01', pl_4='AZ_ALMA')
        pv1.attending_doctor = XCN(xcn_1='22368901234', xcn_2='Maes', xcn_3='Joris', xcn_6='Dr.', xcn_9='AZ_ALMA', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD8001', ei_2='EPD')
        orc.filler_order_number = EI(ei_1='FIL9001', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD8001', ei_2='EPD')
        obr.filler_order_number = EI(ei_1='FIL9001', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='24325-3', cwe_2='Leverfunctie panel', cwe_3='LN')
        obr.observation_date_time = '20250714083000'
        obr.obr_16 = '22368901234^Maes^Joris^^^Dr.^^^AZ_ALMA^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250714105000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALAT', cwe_3='LN')
        obx.obx_5 = '125'
        obx.units = CWE(cwe_1='U/L')
        obx.reference_range = '7-56'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1920-8', cwe_2='ASAT', cwe_3='LN')
        obx_2.obx_5 = '98'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '10-40'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6768-6', cwe_2='Alkalische fosfatase', cwe_3='LN')
        obx_3.obx_5 = '310'
        obx_3.units = CWE(cwe_1='U/L')
        obx_3.reference_range = '44-147'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Totaal bilirubine', cwe_3='LN')
        obx_4.obx_5 = '42'
        obx_4.units = CWE(cwe_1='umol/L')
        obx_4.reference_range = '5-21'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1968-7', cwe_2='Direct bilirubine', cwe_3='LN')
        obx_5.obx_5 = '28'
        obx_5.units = CWE(cwe_1='umol/L')
        obx_5.reference_range = '0-5'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2324-2', cwe_2='GGT', cwe_3='LN')
        obx_6.obx_5 = '185'
        obx_6.units = CWE(cwe_1='U/L')
        obx_6.reference_range = '8-61'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1751-7', cwe_2='Albumine', cwe_3='LN')
        obx_7.obx_5 = '32'
        obx_7.units = CWE(cwe_1='g/L')
        obx_7.reference_range = '35-52'
        obx_7.interpretation_codes = CWE(cwe_1='L')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='2885-2', cwe_2='Totaal eiwit', cwe_3='LN')
        obx_8.obx_5 = '62'
        obx_8.units = CWE(cwe_1='g/L')
        obx_8.reference_range = '64-83'
        obx_8.interpretation_codes = CWE(cwe_1='L')
        obx_8.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Cholestasebeeld. Echografie lever aangevraagd.'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8
        observation_8.nte = nte

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
    """ Based on live/be/be-clinisys-glims.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='AZ_DELTA')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='AZ_DELTA')
        msh.date_time_of_message = '20250901220000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='E667788', cx_4='AZ_DELTA', cx_5='PI'),
            CX(cx_1='57061245678', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Peeters', xpn_2='Hendrik', xpn_7='L')
        pid.date_time_of_birth = '19570612'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='SPOED', pl_2='01', pl_3='1', pl_4='AZ_DELTA')
        pv1.attending_doctor = XCN(xcn_1='22379012345', xcn_2='Vermeersch', xcn_3='Anja', xcn_6='Dr.', xcn_9='AZ_DELTA', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD9001', ei_2='EPD')
        orc.filler_order_number = EI(ei_1='FIL1101', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD9001', ei_2='EPD')
        obr.filler_order_number = EI(ei_1='FIL1101', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='89579-7', cwe_2='Cardiale merkers', cwe_3='LN')
        obr.observation_date_time = '20250901210000'
        obr.obr_16 = '22379012345^Vermeersch^Anja^^^Dr.^^^AZ_DELTA^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250901215500'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6598-7', cwe_2='Troponine T hs', cwe_3='LN')
        obx.obx_5 = '285'
        obx.units = CWE(cwe_1='ng/L')
        obx.reference_range = '0-14'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='30522-7', cwe_2='CRP hs', cwe_3='LN')
        obx_2.obx_5 = '18.5'
        obx_2.units = CWE(cwe_1='mg/L')
        obx_2.reference_range = '0-5.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='42637-9', cwe_2='NT-proBNP', cwe_3='LN')
        obx_3.obx_5 = '1250'
        obx_3.units = CWE(cwe_1='pg/mL')
        obx_3.reference_range = '0-125'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2157-6', cwe_2='CK', cwe_3='LN')
        obx_4.obx_5 = '420'
        obx_4.units = CWE(cwe_1='U/L')
        obx_4.reference_range = '30-200'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='13969-1', cwe_2='CK-MB', cwe_3='LN')
        obx_5.obx_5 = '45'
        obx_5.units = CWE(cwe_1='U/L')
        obx_5.reference_range = '0-25'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Verhoogde cardiale merkers. Klinisch beeld suggestief voor acuut coronair syndroom.'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5
        observation_5.nte = nte

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
    """ Based on live/be/be-clinisys-glims.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='CHU_UCL_NAMUR')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='CHU_UCL_NAMUR')
        msh.date_time_of_message = '20250220143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='P889900', cx_4='CHU_UCL_NAMUR', cx_5='PI'),
            CX(cx_1='90121534567', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Michel', xpn_2='Aurelie', xpn_7='L')
        pid.date_time_of_birth = '19901215'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='110', pl_3='2', pl_4='CHU_UCL_NAMUR')
        pv1.attending_doctor = XCN(xcn_1='22390123456', xcn_2='Lambert', xcn_3='Etienne', xcn_6='Dr.', xcn_9='CHU_UCL_NAMUR', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD1101', ei_2='EPD')
        orc.filler_order_number = EI(ei_1='FIL1201', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1101', ei_2='EPD')
        obr.filler_order_number = EI(ei_1='FIL1201', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='62854-0', cwe_2='Panel coagulation', cwe_3='LN')
        obr.observation_date_time = '20250220090000'
        obr.obr_16 = '22390123456^Lambert^Etienne^^^Dr.^^^CHU_UCL_NAMUR^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250220141500'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='TP (temps de prothrombine)', cwe_3='LN')
        obx.obx_5 = '18.5'
        obx.units = CWE(cwe_1='sec')
        obx.reference_range = '11.0-15.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '1.5'
        obx_2.units = CWE(cwe_1='{INR}')
        obx_2.reference_range = '0.8-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='TCA (temps de céphaline activée)', cwe_3='LN')
        obx_3.obx_5 = '42'
        obx_3.units = CWE(cwe_1='sec')
        obx_3.reference_range = '25-35'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3255-7', cwe_2='Fibrinogène', cwe_3='LN')
        obx_4.obx_5 = '1.8'
        obx_4.units = CWE(cwe_1='g/L')
        obx_4.reference_range = '2.0-4.0'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='5942-8', cwe_2='D-dimères', cwe_3='LN')
        obx_5.obx_5 = '2.4'
        obx_5.units = CWE(cwe_1='mg/L')
        obx_5.reference_range = '0-0.5'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Coagulopathie. Bilan pré-opératoire à compléter.'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5
        observation_5.nte = nte

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
    """ Based on live/be/be-clinisys-glims.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='AZ_TURNHOUT')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='AZ_TURNHOUT')
        msh.date_time_of_message = '20250615162000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='U001122', cx_4='AZ_TURNHOUT', cx_5='PI'),
            CX(cx_1='72031245678', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Maes', xpn_2='Bram', xpn_7='L')
        pid.date_time_of_birth = '19720312'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='SPOED', pl_2='02', pl_3='1', pl_4='AZ_TURNHOUT')
        pv1.attending_doctor = XCN(xcn_1='22316789012', xcn_2='Vandenberghe', xcn_3='Liesbeth', xcn_6='Dr.', xcn_9='AZ_TURNHOUT', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD1201', ei_2='ORBIS')
        orc.filler_order_number = EI(ei_1='FIL1301', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1201', ei_2='ORBIS')
        obr.filler_order_number = EI(ei_1='FIL1301', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='24336-0', cwe_2='Arteriële bloedgas', cwe_3='LN')
        obr.observation_date_time = '20250615160000'
        obr.obr_16 = '22316789012^Vandenberghe^Liesbeth^^^Dr.^^^AZ_TURNHOUT^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250615161500'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='pH', cwe_3='LN')
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
        obx_2.obx_5 = '52'
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
        obx_4.observation_identifier = CWE(cwe_1='1959-6', cwe_2='HCO3', cwe_3='LN')
        obx_4.obx_5 = '26'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '22-26'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2708-6', cwe_2='Base Excess', cwe_3='LN')
        obx_5.obx_5 = '-1.5'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '-2.0-2.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2713-6', cwe_2='SaO2', cwe_3='LN')
        obx_6.obx_5 = '91'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '95-100'
        obx_6.interpretation_codes = CWE(cwe_1='L')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2947-0', cwe_2='Lactaat', cwe_3='LN')
        obx_7.obx_5 = '3.8'
        obx_7.units = CWE(cwe_1='mmol/L')
        obx_7.reference_range = '0.5-2.2'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Respiratoire acidose met hypoxemie. Verhoogd lactaat.'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7
        observation_7.nte = nte

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
    """ Based on live/be/be-clinisys-glims.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='AZ_TURNHOUT')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='AZ_TURNHOUT')
        msh.date_time_of_message = '20250411160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='612345', cx_4='AZ_TURNHOUT', cx_5='PI'),
            CX(cx_1='85061234567', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Janssens', xpn_2='Griet', xpn_7='L')
        pid.date_time_of_birth = '19850612'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='204', pl_3='1', pl_4='AZ_TURNHOUT')

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
        orc.placer_order_number = EI(ei_1='ORD1001', ei_2='ORBIS')
        orc.filler_order_number = EI(ei_1='FIL3001', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1001', ei_2='ORBIS')
        obr.filler_order_number = EI(ei_1='FIL3001', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='CMP', cwe_3='LN')
        obr.observation_date_time = '20250410083000'
        obr.obr_16 = '22315678901^Coppens^Dirk^^^Dr.^^^AZ_TURNHOUT^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250411155000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '8.2'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.9-6.1'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obx_2.obx_5 = '58'
        obx_2.units = CWE(cwe_1='mmol/mol')
        obx_2.reference_range = '20-42'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='PDF', cwe_2='Laboratoriumrapport', cwe_3='LOCAL')
        obx_3.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNTk1IDg0Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA1OTUgODQyXQovQ29udGVudHMg'
            'NCAwIFIKL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3'
            'MDAgVGQKKEFaIFR1cm5ob3V0IC0gTGFib3JhdG9yaXVtcmFwcG9ydCkgVGoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQov'
            'QmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAw'
            'MDE1MyAwMDAwMCBuIAowMDAwMDAwMzE0IDAwMDAwIG4gCjAwMDAwMDA0MTIgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgo0OTMKJSVFT0YK'
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
    """ Based on live/be/be-clinisys-glims.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='UZ_GENT')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='UZ_GENT')
        msh.date_time_of_message = '20250620110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='H445566', cx_4='UZ_GENT', cx_5='PI'),
            CX(cx_1='94071545678', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Willems', xpn_2='Jolien', xpn_7='L')
        pid.date_time_of_birth = '19940715'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='REUMA', pl_3='01', pl_4='UZ_GENT')
        pv1.attending_doctor = XCN(xcn_1='22311234567', xcn_2='Baert', xcn_3='Frederik', xcn_6='Prof.Dr.', xcn_9='UZ_GENT', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD1301', ei_2='EPD')
        orc.filler_order_number = EI(ei_1='FIL1401', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1301', ei_2='EPD')
        obr.filler_order_number = EI(ei_1='FIL1401', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='57021-8', cwe_2='Immunologisch panel', cwe_3='LN')
        obr.observation_date_time = '20250620083000'
        obr.obr_16 = '22311234567^Baert^Frederik^^^Prof.Dr.^^^UZ_GENT^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250620105000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='13965-9', cwe_2='CRP', cwe_3='LN')
        obx.obx_5 = '45'
        obx.units = CWE(cwe_1='mg/L')
        obx.reference_range = '0-5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4537-7', cwe_2='BSE', cwe_3='LN')
        obx_2.obx_5 = '68'
        obx_2.units = CWE(cwe_1='mm/h')
        obx_2.reference_range = '0-20'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='5130-0', cwe_2='ANA (IF)', cwe_3='LN')
        obx_3.obx_5 = 'Positief 1:320 homogeen'
        obx_3.reference_range = 'Negatief'
        obx_3.interpretation_codes = CWE(cwe_1='A')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='11572-5', cwe_2='Anti-dsDNA', cwe_3='LN')
        obx_4.obx_5 = '85'
        obx_4.units = CWE(cwe_1='IU/mL')
        obx_4.reference_range = '0-25'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='33935-8', cwe_2='Anti-SSA/Ro', cwe_3='LN')
        obx_5.obx_5 = 'Positief'
        obx_5.reference_range = 'Negatief'
        obx_5.interpretation_codes = CWE(cwe_1='A')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='31695-9', cwe_2='Anti-SSB/La', cwe_3='LN')
        obx_6.obx_5 = 'Negatief'
        obx_6.reference_range = 'Negatief'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='4485-9', cwe_2='Complement C3', cwe_3='LN')
        obx_7.obx_5 = '0.55'
        obx_7.units = CWE(cwe_1='g/L')
        obx_7.reference_range = '0.90-1.80'
        obx_7.interpretation_codes = CWE(cwe_1='L')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='4498-2', cwe_2='Complement C4', cwe_3='LN')
        obx_8.obx_5 = '0.08'
        obx_8.units = CWE(cwe_1='g/L')
        obx_8.reference_range = '0.10-0.40'
        obx_8.interpretation_codes = CWE(cwe_1='L')
        obx_8.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'ANA positief met anti-dsDNA en laag complement. Suggestief voor SLE.'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8
        observation_8.nte = nte

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
    """ Based on live/be/be-clinisys-glims.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='CHU_CHARLEROI')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='CHU_CHARLEROI')
        msh.date_time_of_message = '20250802230000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='D223344', cx_4='CHU_CHARLEROI', cx_5='PI'),
            CX(cx_1='92050112345', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Renard', xpn_2='Maxime', xpn_7='L')
        pid.date_time_of_birth = '19920501'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='URGENCES', pl_2='01', pl_3='1', pl_4='CHU_CHARLEROI')
        pv1.attending_doctor = XCN(xcn_1='22328901234', xcn_2='Collin', xcn_3='Sandrine', xcn_6='Dr.', xcn_9='CHU_CHARLEROI', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD1401', ei_2='EPD')
        orc.filler_order_number = EI(ei_1='FIL1501', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1401', ei_2='EPD')
        obr.filler_order_number = EI(ei_1='FIL1501', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='75695-2', cwe_2='Screening toxicologique', cwe_3='LN')
        obr.observation_date_time = '20250802220000'
        obr.obr_16 = '22328901234^Collin^Sandrine^^^Dr.^^^CHU_CHARLEROI^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250802225500'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='3426-4', cwe_2='Ethanol', cwe_3='LN')
        obx.obx_5 = '1.85'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '0-0'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='19659-2', cwe_2='Benzodiazépines (urine)', cwe_3='LN')
        obx_2.obx_5 = 'Positif'
        obx_2.reference_range = 'Négatif'
        obx_2.interpretation_codes = CWE(cwe_1='A')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='14314-4', cwe_2='Opiacés (urine)', cwe_3='LN')
        obx_3.obx_5 = 'Négatif'
        obx_3.reference_range = 'Négatif'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='16254-0', cwe_2='Cannabis (urine)', cwe_3='LN')
        obx_4.obx_5 = 'Négatif'
        obx_4.reference_range = 'Négatif'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='19658-4', cwe_2='Cocaïne métabolites (urine)', cwe_3='LN')
        obx_5.obx_5 = 'Négatif'
        obx_5.reference_range = 'Négatif'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='14325-0', cwe_2='Amphétamines (urine)', cwe_3='LN')
        obx_6.obx_5 = 'Négatif'
        obx_6.reference_range = 'Négatif'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1558-6', cwe_2='Glucose (sang)', cwe_3='LN')
        obx_7.obx_5 = '4.8'
        obx_7.units = CWE(cwe_1='mmol/L')
        obx_7.reference_range = '3.9-6.1'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Alcoolémie élevée. Benzodiazépines détectés. Confirmer par méthode quantitative.'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7
        observation_7.nte = nte

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
    """ Based on live/be/be-clinisys-glims.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='UZ_GENT')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='UZ_GENT')
        msh.date_time_of_message = '20250905160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'GEN001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='H001122', cx_4='UZ_GENT', cx_5='PI'),
            CX(cx_1='87032145678', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Claes', xpn_2='Stef', xpn_7='L')
        pid.date_time_of_birth = '19870321'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HEMA', pl_2='305', pl_3='1', pl_4='UZ_GENT')
        pv1.attending_doctor = XCN(xcn_1='22312345098', xcn_2='Peeters', xcn_3='Annelies', xcn_6='Prof.Dr.', xcn_9='UZ_GENT', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD1501', ei_2='EPD')
        orc.filler_order_number = EI(ei_1='FIL1601', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1501', ei_2='EPD')
        obr.filler_order_number = EI(ei_1='FIL1601', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='13303-3', cwe_2='HLA typing panel', cwe_3='LN')
        obr.observation_date_time = '20250903090000'
        obr.obr_16 = '22312345098^Peeters^Annelies^^^Prof.Dr.^^^UZ_GENT^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250905155000'
        obr.diagnostic_serv_sect_id = 'GEN'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='59021-7', cwe_2='HLA-A', cwe_3='LN')
        obx.obx_5 = 'A*02:01, A*24:02'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='46995-7', cwe_2='HLA-B', cwe_3='LN')
        obx_2.obx_5 = 'B*07:02, B*44:02'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='59022-5', cwe_2='HLA-C', cwe_3='LN')
        obx_3.obx_5 = 'C*05:01, C*07:02'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='46996-5', cwe_2='HLA-DRB1', cwe_3='LN')
        obx_4.obx_5 = 'DRB1*04:01, DRB1*15:01'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='59023-3', cwe_2='HLA-DQB1', cwe_3='LN')
        obx_5.obx_5 = 'DQB1*03:02, DQB1*06:02'
        obx_5.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'HLA-typering voor transplantatie-evaluatie.'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5
        observation_5.nte = nte

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
    """ Based on live/be/be-clinisys-glims.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPD')
        msh.sending_facility = HD(hd_1='CHU_CHARLEROI')
        msh.receiving_application = HD(hd_1='GLIMS')
        msh.receiving_facility = HD(hd_1='CHU_CHARLEROI')
        msh.date_time_of_message = '20250320083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ORM003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='D901234', cx_4='CHU_CHARLEROI', cx_5='PI'),
            CX(cx_1='74030967890', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Lejeune', xpn_2='Thierry', xpn_7='L')
        pid.date_time_of_birth = '19740309'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='205', pl_3='3', pl_4='CHU_CHARLEROI')
        pv1.attending_doctor = XCN(xcn_1='22327890123', xcn_2='Dubois', xcn_3='Veronique', xcn_6='Dr.', xcn_9='CHU_CHARLEROI', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD7001', ei_2='EPD')
        orc.placer_order_group_number = EI(ei_1='GRP003', ei_2='EPD')
        orc.date_time_of_order_event = '20250320083000'
        orc.orc_12 = '22327890123^Dubois^Veronique^^^Dr.^^^CHU_CHARLEROI^L^^^NIHDI'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD7001', ei_2='EPD')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Hémoculture', cwe_3='LN')
        obr.observation_date_time = '20250320083000'
        obr.obr_16 = '22327890123^Dubois^Veronique^^^Dr.^^^CHU_CHARLEROI^L^^^NIHDI'
        obr.obr_27 = '^STAT'

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
        obr_2.placer_order_number = EI(ei_1='ORD7001', ei_2='EPD')
        obr_2.universal_service_identifier = CWE(cwe_1='87070', cwe_2='Culture de plaie', cwe_3='LN')
        obr_2.observation_date_time = '20250320083000'
        obr_2.obr_16 = '22327890123^Dubois^Veronique^^^Dr.^^^CHU_CHARLEROI^L^^^NIHDI'
        obr_2.obr_27 = '^STAT'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = "Patient fébrile à 39.2. Plaie abdominale post-opératoire suspecte d'infection."

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, nte]

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
    """ Based on live/be/be-clinisys-glims.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='AZ_ALMA')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='AZ_ALMA')
        msh.date_time_of_message = '20250718143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='B667788', cx_4='AZ_ALMA', cx_5='PI'),
            CX(cx_1='74050545678', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Coppens', xpn_2='Ruben', xpn_7='L')
        pid.date_time_of_birth = '19740505'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='CARDIO', pl_3='01', pl_4='AZ_ALMA')
        pv1.attending_doctor = XCN(xcn_1='22369012345', xcn_2='Goossens', xcn_3='Veerle', xcn_6='Dr.', xcn_9='AZ_ALMA', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD1601', ei_2='EPD')
        orc.filler_order_number = EI(ei_1='FIL1701', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1601', ei_2='EPD')
        obr.filler_order_number = EI(ei_1='FIL1701', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='57698-3', cwe_2='Lipidenprofiel', cwe_3='LN')
        obr.observation_date_time = '20250718083000'
        obr.obr_16 = '22369012345^Goossens^Veerle^^^Dr.^^^AZ_ALMA^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250718141500'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Totaal cholesterol', cwe_3='LN')
        obx.obx_5 = '6.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '0-5.2'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Triglyceriden', cwe_3='LN')
        obx_2.obx_5 = '2.9'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '0-1.7'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL-cholesterol', cwe_3='LN')
        obx_3.obx_5 = '0.95'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '1.0-999'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL-cholesterol (berekend)', cwe_3='LN')
        obx_4.obx_5 = '4.53'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '0-3.0'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='9830-1', cwe_2='Cholesterol/HDL ratio', cwe_3='LN')
        obx_5.obx_5 = '7.2'
        obx_5.reference_range = '0-5.0'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Uitgesproken dyslipidemie. Starten met statines overwegen.'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5
        observation_5.nte = nte

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
    """ Based on live/be/be-clinisys-glims.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='CHU_UCL_NAMUR')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='CHU_UCL_NAMUR')
        msh.date_time_of_message = '20250305160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PATH001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='P334455', cx_4='CHU_UCL_NAMUR', cx_5='PI'),
            CX(cx_1='67071234567', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Bodart', xpn_2='Mireille', xpn_7='L')
        pid.date_time_of_birth = '19670712'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='201', pl_3='1', pl_4='CHU_UCL_NAMUR')
        pv1.attending_doctor = XCN(xcn_1='22391234567', xcn_2='Renard', xcn_3='Guillaume', xcn_6='Dr.', xcn_9='CHU_UCL_NAMUR', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD1701', ei_2='EPD')
        orc.filler_order_number = EI(ei_1='FIL1801', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1701', ei_2='EPD')
        obr.filler_order_number = EI(ei_1='FIL1801', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='11529-5', cwe_2='Examen anatomopathologique', cwe_3='LN')
        obr.observation_date_time = '20250303100000'
        obr.obr_16 = '22391234567^Renard^Guillaume^^^Dr.^^^CHU_UCL_NAMUR^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250305155000'
        obr.diagnostic_serv_sect_id = 'AP'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Diagnostic anatomopathologique', cwe_3='LN')
        obx.obx_5 = (
            'Macroscopie: Fragment colique, 12 cm\\.br\\Microscopie: Adénocarcinome modérément différencié, infiltrant la sous-muqueuse\\.br\\Marges de résec'
            'tion libres\\.br\\Classification pTNM: pT2 N0 Mx'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Rapport anatomopathologique', cwe_3='LOCAL')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNTk1IDg0Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA1OTUgODQyXQovQ29udGVudHMg'
            'NCAwIFIKL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA2MCA+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3'
            'MDAgVGQKKENIVSBVQ0wgTmFtdXIgLSBSYXBwb3J0IGFuYXRvbW9wYXRob2xvZ2lxdWUpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udAovU3VidHlw'
            'ZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXRpY2EKPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAw'
            'IG4gCjAwMDAwMDAxNTMgMDAwMDAgbiAKMDAwMDAwMDMxNCAwMDAwMCBuIAowMDAwMDAwNDI4IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNgovUm9vdCAxIDAgUgo+PgpzdGFydHhy'
            'ZWYKNTA5CiUlRU9GCg=='
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
    """ Based on live/be/be-clinisys-glims.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='AZ_DELTA')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='AZ_DELTA')
        msh.date_time_of_message = '20250910110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='E990011', cx_4='AZ_DELTA', cx_5='PI'),
            CX(cx_1='60031245678', cx_4='SSIN&2.16.840.1.113883.3.6777.5.1&ISO', cx_5='NNNBE'),
        ]
        pid.patient_name = XPN(xpn_1='Vandamme', xpn_2='Roger', xpn_7='L')
        pid.date_time_of_birth = '19600312'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='NEFRO', pl_3='01', pl_4='AZ_DELTA')
        pv1.attending_doctor = XCN(xcn_1='22370123456', xcn_2='Declercq', xcn_3='Nele', xcn_6='Dr.', xcn_9='AZ_DELTA', xcn_10='L', xcn_13='NIHDI')

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
        orc.placer_order_number = EI(ei_1='ORD1801', ei_2='EPD')
        orc.filler_order_number = EI(ei_1='FIL1901', ei_2='GLIMS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1801', ei_2='EPD')
        obr.filler_order_number = EI(ei_1='FIL1901', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='34555-3', cwe_2='Nierfunctie panel', cwe_3='LN')
        obr.observation_date_time = '20250910083000'
        obr.obr_16 = '22370123456^Declercq^Nele^^^Dr.^^^AZ_DELTA^L^^^NIHDI'
        obr.results_rpt_status_chng_date_time = '20250910105000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx.obx_5 = '185'
        obx.units = CWE(cwe_1='umol/L')
        obx.reference_range = '62-106'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Ureum', cwe_3='LN')
        obx_2.obx_5 = '18.5'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '2.5-7.5'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='33914-3', cwe_2='eGFR (CKD-EPI)', cwe_3='LN')
        obx_3.obx_5 = '28'
        obx_3.units = CWE(cwe_1='mL/min/1.73m2')
        obx_3.reference_range = '>60'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='14959-1', cwe_2='Albumine/creatinine ratio (urine)', cwe_3='LN')
        obx_4.obx_5 = '45'
        obx_4.units = CWE(cwe_1='mg/mmol')
        obx_4.reference_range = '0-3'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Natrium', cwe_3='LN')
        obx_5.obx_5 = '138'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '136-145'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Kalium', cwe_3='LN')
        obx_6.obx_5 = '5.4'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '3.5-5.1'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='17861-6', cwe_2='Calcium', cwe_3='LN')
        obx_7.obx_5 = '2.05'
        obx_7.units = CWE(cwe_1='mmol/L')
        obx_7.reference_range = '2.15-2.55'
        obx_7.interpretation_codes = CWE(cwe_1='L')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='2777-1', cwe_2='Fosfaat', cwe_3='LN')
        obx_8.obx_5 = '1.85'
        obx_8.units = CWE(cwe_1='mmol/L')
        obx_8.reference_range = '0.81-1.45'
        obx_8.interpretation_codes = CWE(cwe_1='H')
        obx_8.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'CKD stadium 4. Fosfaat verhoogd, calcium verlaagd. Nefrologisch advies.'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8
        observation_8.nte = nte

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
    """ Based on live/be/be-clinisys-glims.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORBIS')
        msh.sending_facility = HD(hd_1='AZ_TURNHOUT')
        msh.receiving_application = HD(hd_1='GLIMS')
        msh.receiving_facility = HD(hd_1='AZ_TURNHOUT')
        msh.date_time_of_message = '20250410153100'
        msh.message_type = MSG(msg_1='ACK', msg_2='R01', msg_3='ACK')
        msh.message_control_id = 'ACK001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'CA'
        msa.message_control_id = 'LAB001'

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
