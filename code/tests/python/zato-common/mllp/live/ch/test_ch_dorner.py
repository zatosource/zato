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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MSG, PL, PT, VID, XAD, XPN
from zato.hl7v2.v2_9.groups import OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ACK, ORU_R01
from zato.hl7v2.v2_9.segments import MSA, MSH, OBR, OBX, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ch', 'ch-dorner.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ch/ch-dorner.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='ABL90_FLEX')
        msh.receiving_application = HD(hd_1='KISIM')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260301090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101001', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Burgener', xpn_2='Ernst', xpn_3='Fritz', xpn_5='Herr')
        pid.date_time_of_birth = '19580415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Dorfstrasse 10', xad_3='Biel/Bienne', xad_5='2502', xad_6='CH')
        pid.pid_13 = '^^CP^0766503584'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IPS', pl_2='Zimmer 3', pl_3='Bett 1', pl_4='Intensivstation')
        pv1.pv1_7 = 'ARZ700^Egger^Otto^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70001')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD101', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES101', ei_4='ABL90')
        obr.universal_service_identifier = CWE(cwe_1='BGA', cwe_2='Blutgasanalyse', cwe_3='LN')
        obr.observation_date_time = '20260301085500'
        obr.obr_16 = 'ARZ700^Egger^Otto^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260301090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='pH arteriell', cwe_3='LN')
        obx.obx_5 = '7.35'
        obx.reference_range = '7.35-7.45'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='pCO2 arteriell', cwe_3='LN')
        obx_2.obx_5 = '5.8'
        obx_2.units = CWE(cwe_1='kPa')
        obx_2.reference_range = '4.7-6.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2703-7', cwe_2='pO2 arteriell', cwe_3='LN')
        obx_3.obx_5 = '9.5'
        obx_3.units = CWE(cwe_1='kPa')
        obx_3.reference_range = '10.0-13.3'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1960-4', cwe_2='Bicarbonat', cwe_3='LN')
        obx_4.obx_5 = '22'
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
        obx_5.observation_identifier = CWE(cwe_1='1925-7', cwe_2='Base Excess', cwe_3='LN')
        obx_5.obx_5 = '-2.5'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '-2.0-2.0'
        obx_5.interpretation_codes = CWE(cwe_1='L')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2713-6', cwe_2='Sauerstoffsättigung', cwe_3='LN')
        obx_6.obx_5 = '92'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '95-99'
        obx_6.interpretation_codes = CWE(cwe_1='L')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ch/ch-dorner.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='ACCUCHEK_INFORM')
        msh.receiving_application = HD(hd_1='KISIM')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260301100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101002', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Stauffer', xpn_2='Johanna', xpn_3='Robert', xpn_5='Frau')
        pid.date_time_of_birth = '19700622'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Marktgasse 177', xad_3='Baden', xad_5='5400', xad_6='CH')
        pid.pid_13 = '^^CP^0791602346'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='Zimmer 310', pl_3='Bett A', pl_4='Innere Medizin')
        pv1.pv1_7 = 'ARZ701^Liechti^Cornelia^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70002')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD102', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES102', ei_4='ACCUCHEK')
        obr.universal_service_identifier = CWE(cwe_1='GLU', cwe_2='Glukose POCT', cwe_3='LN')
        obr.observation_date_time = '20260301095500'
        obr.obr_16 = 'ARZ701^Liechti^Cornelia^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260301100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glukose', cwe_3='LN')
        obx.obx_5 = '12.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.9-5.6'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/ch/ch-dorner.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='COAGUCHEK_PRO')
        msh.receiving_application = HD(hd_1='KISIM')
        msh.receiving_facility = HD(hd_1='INSEL_BERN')
        msh.date_time_of_message = '20260305110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101003', cx_4='INSEL&2.16.756.5.30.1.128.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Schueler', xpn_2='Franz', xpn_3='Verena', xpn_5='Herr')
        pid.date_time_of_birth = '19480310'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Eichenstrasse 133', xad_3='Nidau', xad_5='2560', xad_6='CH')
        pid.pid_13 = '^^PH^0325263443'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='KARD', pl_2='Zimmer 601', pl_3='Bett A', pl_4='Kardiologie')
        pv1.pv1_7 = 'ARZ702^Frei^Margrit^^^Prof.^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70003')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD103', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES103', ei_4='COAGUCHEK')
        obr.universal_service_identifier = CWE(cwe_1='COAG', cwe_2='Gerinnung POCT', cwe_3='LN')
        obr.observation_date_time = '20260305105500'
        obr.obr_16 = 'ARZ702^Frei^Margrit^^^Prof.^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260305110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx.obx_5 = '2.8'
        obx.reference_range = '2.0-3.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='5902-2', cwe_2='Prothrombinzeit', cwe_3='LN')
        obx_2.obx_5 = '32'
        obx_2.units = CWE(cwe_1='s')
        obx_2.reference_range = '11-15'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
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
    """ Based on live/ch/ch-dorner.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='CLINITEK_STATUS')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='KSSG_STGALLEN')
        msh.date_time_of_message = '20260310083000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101004', cx_4='KSSG&2.16.756.5.30.1.150.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Widmer', xpn_2='Sandra', xpn_3='Elisabeth', xpn_5='Frau')
        pid.date_time_of_birth = '19620915'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Dorfstrasse 188', xad_3='Chur', xad_5='7000', xad_6='CH')
        pid.pid_13 = '^^PH^0817574503'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='Zimmer 205', pl_3='Bett B', pl_4='Innere Medizin')
        pv1.pv1_7 = 'ARZ703^Wyss^Viktor^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70004')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD104', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES104', ei_4='CLINITEK')
        obr.universal_service_identifier = CWE(cwe_1='UA', cwe_2='Urinstreifentest POCT', cwe_3='LN')
        obr.observation_date_time = '20260310082500'
        obr.obr_16 = 'ARZ703^Wyss^Viktor^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260310083000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5811-5', cwe_2='Urin pH', cwe_3='LN')
        obx.obx_5 = '5.5'
        obx.reference_range = '5.0-8.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='2965-2', cwe_2='Spezifisches Gewicht', cwe_3='LN')
        obx_2.obx_5 = '1.025'
        obx_2.reference_range = '1.005-1.030'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='5804-0', cwe_2='Protein', cwe_3='LN')
        obx_3.obx_5 = 'Spur'
        obx_3.reference_range = 'Negativ'
        obx_3.interpretation_codes = CWE(cwe_1='A')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='5794-3', cwe_2='Glukose', cwe_3='LN')
        obx_4.obx_5 = 'Negativ'
        obx_4.reference_range = 'Negativ'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='5802-4', cwe_2='Nitrit', cwe_3='LN')
        obx_5.obx_5 = 'Negativ'
        obx_5.reference_range = 'Negativ'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='5799-2', cwe_2='Leukozyten', cwe_3='LN')
        obx_6.obx_5 = 'Negativ'
        obx_6.reference_range = 'Negativ'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='5797-6', cwe_2='Blut', cwe_3='LN')
        obx_7.obx_5 = 'Spur'
        obx_7.reference_range = 'Negativ'
        obx_7.interpretation_codes = CWE(cwe_1='A')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ch/ch-dorner.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='ISTAT_ALINITY')
        msh.receiving_application = HD(hd_1='KISIM')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260315060000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101005', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Eberle', xpn_2='Bruno', xpn_3='Hans', xpn_5='Herr')
        pid.date_time_of_birth = '19520810'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Spalenberg 20', xad_3='Basel', xad_5='4001', xad_6='CH')
        pid.pid_13 = '^^PH^0611064361'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='NOTFALL', pl_2='Box 1', pl_4='Notfallstation')
        pv1.pv1_7 = 'ARZ704^Walder^Urs^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70005')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD105', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES105', ei_4='ISTAT')
        obr.universal_service_identifier = CWE(cwe_1='CARD', cwe_2='Kardiale Marker POCT', cwe_3='LN')
        obr.observation_date_time = '20260315055500'
        obr.obr_16 = 'ARZ704^Walder^Urs^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260315060000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='49563-0', cwe_2='Troponin I hs', cwe_3='LN')
        obx.obx_5 = '85'
        obx.units = CWE(cwe_1='ng/L')
        obx.reference_range = '0-14'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='33762-6', cwe_2='NT-proBNP', cwe_3='LN')
        obx_2.obx_5 = '1250'
        obx_2.units = CWE(cwe_1='pg/mL')
        obx_2.reference_range = '0-125'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
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
    """ Based on live/ch/ch-dorner.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='EUROLYSER_CUBE')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='KSSG_STGALLEN')
        msh.date_time_of_message = '20260320090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101006', cx_4='KSSG&2.16.756.5.30.1.150.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Marti', xpn_2='Karin', xpn_3='Peter', xpn_5='Frau')
        pid.date_time_of_birth = '19750505'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Eichenstrasse 130', xad_3='Koniz', xad_5='3098', xad_6='CH')
        pid.pid_13 = '^^CP^0796682954'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='NOTFALL', pl_2='Box 3', pl_4='Notfallstation')
        pv1.pv1_7 = 'ARZ705^Studer^Daniel^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70006')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD106', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES106', ei_4='EUROLYSER')
        obr.universal_service_identifier = CWE(cwe_1='CRP', cwe_2='CRP POCT', cwe_3='LN')
        obr.observation_date_time = '20260320085500'
        obr.obr_16 = 'ARZ705^Studer^Daniel^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260320090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='17861-6', cwe_2='CRP', cwe_3='LN')
        obx.obx_5 = '45'
        obx.units = CWE(cwe_1='mg/L')
        obx.reference_range = '0-5'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/ch/ch-dorner.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='ABL90_FLEX')
        msh.receiving_application = HD(hd_1='ISHMED')
        msh.receiving_facility = HD(hd_1='LUKS_LUZERN')
        msh.date_time_of_message = '20260322080000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101007', cx_4='LUKS&2.16.756.5.30.1.160.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Schaerer', xpn_2='Andreas', xpn_3='Fritz', xpn_5='Herr')
        pid.date_time_of_birth = '19620318'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tessinerplatz 36', xad_3='Thalwil', xad_5='8800', xad_6='CH')
        pid.pid_13 = '^^CP^0795377473'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IPS', pl_2='Zimmer 5', pl_3='Bett 1', pl_4='Intensivstation')
        pv1.pv1_7 = 'ARZ706^Brunner^Jakob^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70007')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD107', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES107', ei_4='ABL90')
        obr.universal_service_identifier = CWE(cwe_1='BGA_EXT', cwe_2='Blutgasanalyse erweitert', cwe_3='LN')
        obr.observation_date_time = '20260322075500'
        obr.obr_16 = 'ARZ706^Brunner^Jakob^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260322080000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='pH arteriell', cwe_3='LN')
        obx.obx_5 = '7.42'
        obx.reference_range = '7.35-7.45'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='pCO2 arteriell', cwe_3='LN')
        obx_2.obx_5 = '4.8'
        obx_2.units = CWE(cwe_1='kPa')
        obx_2.reference_range = '4.7-6.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2703-7', cwe_2='pO2 arteriell', cwe_3='LN')
        obx_3.obx_5 = '12.0'
        obx_3.units = CWE(cwe_1='kPa')
        obx_3.reference_range = '10.0-13.3'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Kalium', cwe_3='LN')
        obx_4.obx_5 = '3.8'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '3.5-5.1'
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
        obx_6.observation_identifier = CWE(cwe_1='17861-4', cwe_2='Ionisiertes Calcium', cwe_3='LN')
        obx_6.obx_5 = '1.18'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '1.15-1.30'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glukose', cwe_3='LN')
        obx_7.obx_5 = '6.2'
        obx_7.units = CWE(cwe_1='mmol/L')
        obx_7.reference_range = '3.9-5.6'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='2714-4', cwe_2='Laktat', cwe_3='LN')
        obx_8.obx_5 = '1.5'
        obx_8.units = CWE(cwe_1='mmol/L')
        obx_8.reference_range = '0.5-2.0'
        obx_8.interpretation_codes = CWE(cwe_1='N')
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ch/ch-dorner.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='DCA_VANTAGE')
        msh.receiving_application = HD(hd_1='KISIM')
        msh.receiving_facility = HD(hd_1='KSW_WINTERTHUR')
        msh.date_time_of_message = '20260325100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101008', cx_4='KSW&2.16.756.5.30.1.129.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Roth', xpn_2='Irene', xpn_3='Margrit', xpn_5='Frau')
        pid.date_time_of_birth = '19550830'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Gloriastrasse 52', xad_3='Koniz', xad_5='3098', xad_6='CH')
        pid.pid_13 = '^^PH^0315555598'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB', pl_2='Sprechzimmer 8', pl_4='Diabetologie')
        pv1.pv1_7 = 'ARZ707^Hess^Silvia^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70008')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD108', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES108', ei_4='DCA')
        obr.universal_service_identifier = CWE(cwe_1='HBA1C', cwe_2='HbA1c POCT', cwe_3='LN')
        obr.observation_date_time = '20260325095500'
        obr.obr_16 = 'ARZ707^Hess^Silvia^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260325100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obx.obx_5 = '7.2'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '4.0-6.0'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='59261-8', cwe_2='HbA1c (IFCC)', cwe_3='LN')
        obx_2.obx_5 = '55'
        obx_2.units = CWE(cwe_1='mmol/mol')
        obx_2.reference_range = '20-42'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
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
    """ Based on live/ch/ch-dorner.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='ABL90_FLEX')
        msh.receiving_application = HD(hd_1='KISIM')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260401090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101001', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Burgener', xpn_2='Ernst', xpn_3='Fritz', xpn_5='Herr')
        pid.date_time_of_birth = '19580415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Dorfstrasse 10', xad_3='Biel/Bienne', xad_5='2502', xad_6='CH')
        pid.pid_13 = '^^CP^0766503584'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IPS', pl_2='Zimmer 3', pl_3='Bett 1', pl_4='Intensivstation')
        pv1.pv1_7 = 'ARZ700^Egger^Otto^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70001')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD109', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES109', ei_4='ABL90')
        obr.universal_service_identifier = CWE(cwe_1='11502-2', cwe_2='Blutgasprotokoll', cwe_3='LN')
        obr.observation_date_time = '20260401085500'
        obr.obr_16 = 'ARZ700^Egger^Otto^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260401090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Blutgasprotokoll', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA1NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKEJsdXRnYXNwcm90b2tvbGwpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAw'
            'MDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAgbiAKMDAwMDAwMDE0MiAwMDAwMCBuIAowMDAwMDAwMjQyIDAwMDAwIG4gCnRyYWlsZXIKPDwg'
            'L1NpemUgNSAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMzQ2CiUlRU9GCg=='
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/ch/ch-dorner.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='COBAS_B221')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='KSSG_STGALLEN')
        msh.date_time_of_message = '20260403080000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101009', cx_4='KSSG&2.16.756.5.30.1.150.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Steiner', xpn_2='Christian', xpn_3='Karl', xpn_5='Herr')
        pid.date_time_of_birth = '19680120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kornhausstrasse 13', xad_3='Solothurn', xad_5='4500', xad_6='CH')
        pid.pid_13 = '^^CP^0763137401'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='Zimmer 308', pl_3='Bett A', pl_4='Innere Medizin')
        pv1.pv1_7 = 'ARZ703^Wyss^Viktor^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70009')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD110', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES110', ei_4='COBAS')
        obr.universal_service_identifier = CWE(cwe_1='ELYTE', cwe_2='Elektrolyte POCT', cwe_3='LN')
        obr.observation_date_time = '20260403075500'
        obr.obr_16 = 'ARZ703^Wyss^Viktor^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260403080000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Kalium', cwe_3='LN')
        obx.obx_5 = '5.2'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.5-5.1'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Natrium', cwe_3='LN')
        obx_2.obx_5 = '132'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '136-145'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='17861-4', cwe_2='Ionisiertes Calcium', cwe_3='LN')
        obx_3.obx_5 = '1.22'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '1.15-1.30'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2075-0', cwe_2='Chlorid', cwe_3='LN')
        obx_4.obx_5 = '98'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '98-107'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ch/ch-dorner.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='RAPID_TEST')
        msh.receiving_application = HD(hd_1='NEXUS_KIS')
        msh.receiving_facility = HD(hd_1='SPITAL_FRAUENFELD')
        msh.date_time_of_message = '20260405100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101010', cx_4='SPITAL_FRAUENFELD&2.16.756.5.30.1.210.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Schmid', xpn_2='Therese', xpn_3='Rosa', xpn_5='Frau')
        pid.date_time_of_birth = '19920715'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Limmatquai 162', xad_3='St. Gallen', xad_5='9000', xad_6='CH')
        pid.pid_13 = '^^CP^0785844563'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='NOTFALL', pl_2='Box 2', pl_4='Notfallstation')
        pv1.pv1_7 = 'ARZ708^Fischer^Martin^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70010')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD111', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES111', ei_4='RAPID')
        obr.universal_service_identifier = CWE(cwe_1='2106-3', cwe_2='beta-HCG POCT', cwe_3='LN')
        obr.observation_date_time = '20260405095500'
        obr.obr_16 = 'ARZ708^Fischer^Martin^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260405100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='2106-3', cwe_2='beta-HCG qualitativ', cwe_3='LN')
        obx.obx_5 = 'Positiv'
        obx.reference_range = 'Negativ'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/ch/ch-dorner.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='SOFIA_2')
        msh.receiving_application = HD(hd_1='KISIM')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260407090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101011', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Berger', xpn_2='Lisa', xpn_3='Otto', xpn_5='Frau')
        pid.date_time_of_birth = '19650930'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Schulstrasse 106', xad_3='Basel', xad_5='4001', xad_6='CH')
        pid.pid_13 = '^^PH^0614587910'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='NOTFALL', pl_2='Box 5', pl_4='Notfallstation')
        pv1.pv1_7 = 'ARZ704^Walder^Urs^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70011')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD112', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES112', ei_4='SOFIA')
        obr.universal_service_identifier = CWE(cwe_1='FLU', cwe_2='Influenza-Schnelltest POCT', cwe_3='LN')
        obr.observation_date_time = '20260407085500'
        obr.obr_16 = 'ARZ704^Walder^Urs^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260407090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='80382-5', cwe_2='Influenza A Antigen', cwe_3='LN')
        obx.obx_5 = 'Positiv'
        obx.reference_range = 'Negativ'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='80383-3', cwe_2='Influenza B Antigen', cwe_3='LN')
        obx_2.obx_5 = 'Negativ'
        obx_2.reference_range = 'Negativ'
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
    """ Based on live/ch/ch-dorner.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='POCH_100I')
        msh.receiving_application = HD(hd_1='ISHMED')
        msh.receiving_facility = HD(hd_1='LUKS_LUZERN')
        msh.date_time_of_message = '20260409090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101012', cx_4='LUKS&2.16.756.5.30.1.160.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Weber', xpn_2='Stefan', xpn_3='Verena', xpn_5='Herr')
        pid.date_time_of_birth = '19700505'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stauffacherstrasse 40', xad_3='Solothurn', xad_5='4500', xad_6='CH')
        pid.pid_13 = '^^CP^0768262872'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='NOTFALL', pl_2='Box 2', pl_4='Notfallstation')
        pv1.pv1_7 = 'ARZ709^Kaufmann^Karl^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70012')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD113', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES113', ei_4='POCH')
        obr.universal_service_identifier = CWE(cwe_1='CBC_POCT', cwe_2='Blutbild POCT', cwe_3='LN')
        obr.observation_date_time = '20260409085500'
        obr.obr_16 = 'ARZ709^Kaufmann^Karl^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260409090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hämoglobin', cwe_3='LN')
        obx.obx_5 = '105'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '135-175'
        obx.interpretation_codes = CWE(cwe_1='LL')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukozyten', cwe_3='LN')
        obx_2.obx_5 = '18.5'
        obx_2.units = CWE(cwe_1='10*9/L')
        obx_2.reference_range = '4.0-10.0'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='789-8', cwe_2='Thrombozyten', cwe_3='LN')
        obx_3.obx_5 = '85'
        obx_3.units = CWE(cwe_1='10*9/L')
        obx_3.reference_range = '150-400'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ch/ch-dorner.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='PATHFAST')
        msh.receiving_application = HD(hd_1='KISIM')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260410070000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101013', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Suter', xpn_2='Gabriela', xpn_3='Margrit', xpn_5='Frau')
        pid.date_time_of_birth = '19580220'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Junkerngasse 192', xad_3='Wil', xad_5='9500', xad_6='CH')
        pid.pid_13 = '^^PH^0714584776'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='NOTFALL', pl_2='Box 4', pl_4='Notfallstation')
        pv1.pv1_7 = 'ARZ704^Walder^Urs^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70013')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD114', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES114', ei_4='PATHFAST')
        obr.universal_service_identifier = CWE(cwe_1='DDIM', cwe_2='D-Dimer POCT', cwe_3='LN')
        obr.observation_date_time = '20260410065500'
        obr.obr_16 = 'ARZ704^Walder^Urs^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260410070000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='48066-5', cwe_2='D-Dimer', cwe_3='LN')
        obx.obx_5 = '2.5'
        obx.units = CWE(cwe_1='mg/L FEU')
        obx.reference_range = '0-0.5'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/ch/ch-dorner.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='SOFIA_2')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='KSSG_STGALLEN')
        msh.date_time_of_message = '20260412090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101014', cx_4='KSSG&2.16.756.5.30.1.150.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Meyer', xpn_2='Sebastian', xpn_3='Maria', xpn_5='Herr')
        pid.date_time_of_birth = '19750312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Marktgasse 19', xad_3='Aarau', xad_5='5000', xad_6='CH')
        pid.pid_13 = '^^CP^0798450862'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='NOTFALL', pl_2='Box 1', pl_4='Notfallstation')
        pv1.pv1_7 = 'ARZ705^Studer^Daniel^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70014')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD115', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES115', ei_4='SOFIA')
        obr.universal_service_identifier = CWE(cwe_1='COVID', cwe_2='SARS-CoV-2 Antigen POCT', cwe_3='LN')
        obr.observation_date_time = '20260412085500'
        obr.obr_16 = 'ARZ705^Studer^Daniel^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260412090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='94558-4', cwe_2='SARS-CoV-2 Antigen', cwe_3='LN')
        obx.obx_5 = 'Negativ'
        obx.reference_range = 'Negativ'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/ch/ch-dorner.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='LACTATE_PRO2')
        msh.receiving_application = HD(hd_1='KISIM')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260413060000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101001', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Burgener', xpn_2='Ernst', xpn_3='Fritz', xpn_5='Herr')
        pid.date_time_of_birth = '19580415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Dorfstrasse 10', xad_3='Biel/Bienne', xad_5='2502', xad_6='CH')
        pid.pid_13 = '^^CP^0766503584'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IPS', pl_2='Zimmer 3', pl_3='Bett 1', pl_4='Intensivstation')
        pv1.pv1_7 = 'ARZ700^Egger^Otto^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70001')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD116', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES116', ei_4='LACTATE')
        obr.universal_service_identifier = CWE(cwe_1='LAC', cwe_2='Laktat POCT', cwe_3='LN')
        obr.observation_date_time = '20260413055500'
        obr.obr_16 = 'ARZ700^Egger^Otto^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260413060000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2714-4', cwe_2='Laktat', cwe_3='LN')
        obx.obx_5 = '4.2'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '0.5-2.0'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/ch/ch-dorner.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='BRAHMS_PCT')
        msh.receiving_application = HD(hd_1='ISHMED')
        msh.receiving_facility = HD(hd_1='LUKS_LUZERN')
        msh.date_time_of_message = '20260414080000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101012', cx_4='LUKS&2.16.756.5.30.1.160.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Weber', xpn_2='Stefan', xpn_3='Verena', xpn_5='Herr')
        pid.date_time_of_birth = '19700505'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stauffacherstrasse 40', xad_3='Solothurn', xad_5='4500', xad_6='CH')
        pid.pid_13 = '^^CP^0768262872'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IPS', pl_2='Zimmer 2', pl_3='Bett 1', pl_4='Intensivstation')
        pv1.pv1_7 = 'ARZ706^Brunner^Jakob^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70012')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD117', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES117', ei_4='BRAHMS')
        obr.universal_service_identifier = CWE(cwe_1='PCT', cwe_2='Procalcitonin POCT', cwe_3='LN')
        obr.observation_date_time = '20260414075500'
        obr.obr_16 = 'ARZ706^Brunner^Jakob^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260414080000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='75241-0', cwe_2='Procalcitonin', cwe_3='LN')
        obx.obx_5 = '8.5'
        obx.units = CWE(cwe_1='ng/mL')
        obx.reference_range = '0-0.5'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/ch/ch-dorner.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='QC_MANAGER')
        msh.receiving_application = HD(hd_1='KISIM')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260415060000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='QC_INTERNAL', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='QC')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='QC001', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='QC001', ei_4='QC_MANAGER')
        obr.universal_service_identifier = CWE(cwe_1='QC', cwe_2='Qualitätskontrolle ABL90', cwe_3='LN')
        obr.observation_date_time = '20260415055500'
        obr.filler_field_2 = '20260415060000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='pH QC Level 1', cwe_3='LN')
        obx.obx_5 = '7.382'
        obx.reference_range = '7.370-7.400'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='pCO2 QC Level 1', cwe_3='LN')
        obx_2.obx_5 = '5.35'
        obx_2.units = CWE(cwe_1='kPa')
        obx_2.reference_range = '5.10-5.60'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='11502-2', cwe_2='QC-Protokoll', cwe_3='LN')
        obx_3.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA1NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKFFDLVByb3Rva29sbCBBQkw5MCkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAw'
            'MDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8'
            'PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNDYKJSVFT0YK'
        )
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ch/ch-dorner.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORNER_POCT')
        msh.sending_facility = HD(hd_1='ALERE_I')
        msh.receiving_application = HD(hd_1='NEXUS_KIS')
        msh.receiving_facility = HD(hd_1='SPITAL_FRAUENFELD')
        msh.date_time_of_message = '20260416090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORN00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT101015', cx_4='SPITAL_FRAUENFELD&2.16.756.5.30.1.210.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Glaus', xpn_2='Martha', xpn_3='Heinz', xpn_5='Frau')
        pid.date_time_of_birth = '20160305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Birkenstrasse 172', xad_3='Schaffhausen', xad_5='8200', xad_6='CH')
        pid.pid_13 = '^^CP^0799103301'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='NOTFALL', pl_2='Box 1', pl_4='Notfallstation')
        pv1.pv1_7 = 'ARZ708^Fischer^Martin^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL70015')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD118', ei_4='DORNER_POCT')
        obr.filler_order_number = EI(ei_1='RES118', ei_4='ALERE')
        obr.universal_service_identifier = CWE(cwe_1='STREP', cwe_2='Streptococcus A POCT', cwe_3='LN')
        obr.observation_date_time = '20260416085500'
        obr.obr_16 = 'ARZ708^Fischer^Martin^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260416090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='31971-5', cwe_2='Streptococcus Gruppe A Antigen', cwe_3='LN')
        obx.obx_5 = 'Positiv'
        obx.reference_range = 'Negativ'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/ch/ch-dorner.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KISIM')
        msh.sending_facility = HD(hd_1='USZ_ZUERICH')
        msh.receiving_application = HD(hd_1='DORNER_POCT')
        msh.receiving_facility = HD(hd_1='ABL90_FLEX')
        msh.date_time_of_message = '20260417080100'
        msh.message_type = MSG(msg_1='ACK', msg_2='R01', msg_3='ACK')
        msh.message_control_id = 'ACK70001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'DORN00001'
        msa.msa_3 = 'POCT-Ergebnis erfolgreich empfangen'

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
