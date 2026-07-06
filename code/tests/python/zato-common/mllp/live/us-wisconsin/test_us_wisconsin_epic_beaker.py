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
from zato.hl7v2.v2_9.datatypes import CWE, CX, DR, EI, HD, MOC, MSG, PL, PT, VID, XAD, XPN
from zato.hl7v2.v2_9.groups import OmlO21Container, OmlO21ObservationRequest, OmlO21Order, OmlO21OrderPrior, OmlO21Patient, OmlO21PatientVisit, \
    OmlO21PriorResult, OmlO21Specimen, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import OML_O21, ORU_R01
from zato.hl7v2.v2_9.segments import BPO, MSH, NTE, OBR, OBX, ORC, PID, PV1, SAC, SPM

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('us-wisconsin', 'us-wisconsin-epic-beaker.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='UWLAB')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UWHEALTH')
        msh.date_time_of_message = '20260509130000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'BKR2026050913000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='E7829401', cx_4='UWHEALTH', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='SCHROEDER', xpn_2='KEVIN', xpn_3='THOMAS', xpn_5='')
        pid.date_time_of_birth = '19680423'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1417 Winnebago St', xad_3='Madison', xad_4='WI', xad_5='53704', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^608^2517748921'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6E', pl_2='612', pl_3='1', pl_4='UWHEALTH')
        pv1.pv1_7 = '56789^NAKAMURA^GRACE^M^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD8829471', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKR88291', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509101500'
        orc.orc_12 = '12345^ENGSTROM^DANIEL^R^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD8829471', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKR88291', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='80053', cwe_2='COMPREHENSIVE METABOLIC PANEL', cwe_3='CPT')
        obr.observation_date_time = '20260509101500'
        obr.obr_16 = '12345^ENGSTROM^DANIEL^R^^^MD'
        obr.results_rpt_status_chng_date_time = '20260509130000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'
        obr.reason_for_study = CWE(cwe_1='20260509103000')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '98'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '74-106'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509123000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3094-0', cwe_2='BUN', cwe_3='LN')
        obx_2.obx_5 = '18'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '6-24'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509123000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_3.obx_5 = '1.1'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '0.7-1.3'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509123000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx_4.obx_5 = '140'
        obx_4.units = CWE(cwe_1='mEq/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509123000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_5.obx_5 = '4.2'
        obx_5.units = CWE(cwe_1='mEq/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509123000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2075-0', cwe_2='Chloride', cwe_3='LN')
        obx_6.obx_5 = '102'
        obx_6.units = CWE(cwe_1='mEq/L')
        obx_6.reference_range = '98-106'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509123000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2028-9', cwe_2='CO2', cwe_3='LN')
        obx_7.obx_5 = '24'
        obx_7.units = CWE(cwe_1='mEq/L')
        obx_7.reference_range = '20-29'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260509123000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='17861-6', cwe_2='Calcium', cwe_3='LN')
        obx_8.obx_5 = '9.4'
        obx_8.units = CWE(cwe_1='mg/dL')
        obx_8.reference_range = '8.5-10.5'
        obx_8.interpretation_codes = CWE(cwe_1='N')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20260509123000'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='2885-2', cwe_2='Total Protein', cwe_3='LN')
        obx_9.obx_5 = '7.1'
        obx_9.units = CWE(cwe_1='g/dL')
        obx_9.reference_range = '6.0-8.3'
        obx_9.interpretation_codes = CWE(cwe_1='N')
        obx_9.observation_result_status = 'F'
        obx_9.date_time_of_the_observation = '20260509123000'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'NM'
        obx_10.observation_identifier = CWE(cwe_1='1751-7', cwe_2='Albumin', cwe_3='LN')
        obx_10.obx_5 = '4.0'
        obx_10.units = CWE(cwe_1='g/dL')
        obx_10.reference_range = '3.5-5.5'
        obx_10.interpretation_codes = CWE(cwe_1='N')
        obx_10.observation_result_status = 'F'
        obx_10.date_time_of_the_observation = '20260509123000'

        # .. build the OBSERVATION group ..
        observation_10 = OruR01Observation()
        observation_10.obx = obx_10

        # .. build OBX ..
        obx_11 = OBX()
        obx_11.set_id_obx = '11'
        obx_11.value_type = 'NM'
        obx_11.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Total Bilirubin', cwe_3='LN')
        obx_11.obx_5 = '0.8'
        obx_11.units = CWE(cwe_1='mg/dL')
        obx_11.reference_range = '0.1-1.2'
        obx_11.interpretation_codes = CWE(cwe_1='N')
        obx_11.observation_result_status = 'F'
        obx_11.date_time_of_the_observation = '20260509123000'

        # .. build the OBSERVATION group ..
        observation_11 = OruR01Observation()
        observation_11.obx = obx_11

        # .. build OBX ..
        obx_12 = OBX()
        obx_12.set_id_obx = '12'
        obx_12.value_type = 'NM'
        obx_12.observation_identifier = CWE(cwe_1='6768-6', cwe_2='Alkaline Phosphatase', cwe_3='LN')
        obx_12.obx_5 = '72'
        obx_12.units = CWE(cwe_1='U/L')
        obx_12.reference_range = '44-147'
        obx_12.interpretation_codes = CWE(cwe_1='N')
        obx_12.observation_result_status = 'F'
        obx_12.date_time_of_the_observation = '20260509123000'

        # .. build the OBSERVATION group ..
        observation_12 = OruR01Observation()
        observation_12.obx = obx_12

        # .. build OBX ..
        obx_13 = OBX()
        obx_13.set_id_obx = '13'
        obx_13.value_type = 'NM'
        obx_13.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx_13.obx_5 = '28'
        obx_13.units = CWE(cwe_1='U/L')
        obx_13.reference_range = '7-56'
        obx_13.interpretation_codes = CWE(cwe_1='N')
        obx_13.observation_result_status = 'F'
        obx_13.date_time_of_the_observation = '20260509123000'

        # .. build the OBSERVATION group ..
        observation_13 = OruR01Observation()
        observation_13.obx = obx_13

        # .. build OBX ..
        obx_14 = OBX()
        obx_14.set_id_obx = '14'
        obx_14.value_type = 'NM'
        obx_14.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST', cwe_3='LN')
        obx_14.obx_5 = '31'
        obx_14.units = CWE(cwe_1='U/L')
        obx_14.reference_range = '10-40'
        obx_14.interpretation_codes = CWE(cwe_1='N')
        obx_14.observation_result_status = 'F'
        obx_14.date_time_of_the_observation = '20260509123000'

        # .. build the OBSERVATION group ..
        observation_14 = OruR01Observation()
        observation_14.obx = obx_14

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
        order_observation.observation_11 = observation_11
        order_observation.observation_12 = observation_12
        order_observation.observation_13 = observation_13
        order_observation.observation_14 = observation_14

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UWHEALTH')
        msh.receiving_application = HD(hd_1='BEAKER')
        msh.receiving_facility = HD(hd_1='UWLAB')
        msh.date_time_of_message = '20260509080000'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'BKO2026050908000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='E4829173', cx_4='UWHEALTH', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='BERGSTROM', xpn_2='ALLEN', xpn_3='RAYMOND', xpn_5='')
        pid.date_time_of_birth = '19710603'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2204 Monroe St', xad_3='Madison', xad_4='WI', xad_5='53711', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^608^2413378102'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='UWLABDRAW', pl_2='LD2', pl_3='1', pl_4='UWHEALTH')
        pv1.pv1_7 = '12345^ENGSTROM^DANIEL^R^^^MD'

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO21PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD9928477', ei_2='EPIC')
        orc.placer_order_group_number = EI(ei_1='BKRGRP002')
        orc.date_time_of_order_event = '20260509080000'
        orc.orc_12 = '12345^ENGSTROM^DANIEL^R^^^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD9928477', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='80061', cwe_2='LIPID PANEL', cwe_3='CPT')
        obr.observation_date_time = '20260509080000'
        obr.obr_15 = '12345^ENGSTROM^DANIEL^R^^^MD'
        obr.filler_field_2 = '20260509'
        obr.charge_to_practice = MOC(moc_1='LAB')

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_type = CWE(cwe_1='BLD', cwe_2='Blood', cwe_3='HL70487')
        spm.specimen_risk_code = CWE(cwe_1='20260509080000')
        spm.specimen_collection_date_time = DR(dr_1='20260509080500')

        # .. build SAC ..
        sac = SAC()
        sac.container_identifier = EI(ei_1='CONTAINER001')
        sac.registration_date_time = 'SST^Serum Separator Tube^HL70378'
        sac.container_status = CWE(cwe_1='5')
        sac.carrier_type = CWE(cwe_1='mL')

        # .. build the CONTAINER group ..
        container = OmlO21Container()
        container.sac = sac

        # .. build the SPECIMEN group ..
        specimen = OmlO21Specimen()
        specimen.spm = spm
        specimen.container = container

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='ORD9928478', ei_2='EPIC')
        orc_2.placer_order_group_number = EI(ei_1='BKRGRP002')
        orc_2.date_time_of_order_event = '20260509080000'
        orc_2.orc_12 = '12345^ENGSTROM^DANIEL^R^^^MD'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='ORD9928478', ei_2='EPIC')
        obr_2.universal_service_identifier = CWE(cwe_1='85025', cwe_2='CBC WITH DIFF', cwe_3='CPT')
        obr_2.observation_date_time = '20260509080000'
        obr_2.obr_15 = '12345^ENGSTROM^DANIEL^R^^^MD'
        obr_2.filler_field_2 = '20260509'
        obr_2.charge_to_practice = MOC(moc_1='LAB')

        # .. build the ORDER_PRIOR group ..
        order_prior = OmlO21OrderPrior()
        order_prior.orc = orc_2
        order_prior.obr = obr_2

        # .. build the PRIOR_RESULT group ..
        prior_result = OmlO21PriorResult()
        prior_result.order_prior = order_prior

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OmlO21ObservationRequest()
        observation_request.obr = obr
        observation_request.specimen = specimen
        observation_request.prior_result = prior_result

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc
        order.observation_request = observation_request

        # .. build SPM ..
        spm_2 = SPM()
        spm_2.set_id_spm = '2'
        spm_2.specimen_type = CWE(cwe_1='BLD', cwe_2='Blood', cwe_3='HL70487')
        spm_2.specimen_risk_code = CWE(cwe_1='20260509080000')
        spm_2.specimen_collection_date_time = DR(dr_1='20260509080500')

        # .. build SAC ..
        sac_2 = SAC()
        sac_2.container_identifier = EI(ei_1='CONTAINER002')
        sac_2.registration_date_time = 'LAV^Lavender Top EDTA^HL70378'
        sac_2.container_status = CWE(cwe_1='3')
        sac_2.carrier_type = CWE(cwe_1='mL')

        # .. assemble the full message ..
        msg = OML_O21()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [spm_2, sac_2]

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='UWBLOODBANK')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UWHEALTH')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'BKB2026050911000033'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='E7829401', cx_4='UWHEALTH', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='SCHROEDER', xpn_2='KEVIN', xpn_3='THOMAS', xpn_5='')
        pid.date_time_of_birth = '19680423'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='1417 Winnebago St', xad_3='Madison', xad_4='WI', xad_5='53704', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^608^2517748921'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6E', pl_2='612', pl_3='1', pl_4='UWHEALTH')
        pv1.pv1_7 = '56789^NAKAMURA^GRACE^M^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD8829555', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKB001', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509090000'
        orc.orc_12 = '56789^NAKAMURA^GRACE^M^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD8829555', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKB001', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='86900', cwe_2='BLOOD TYPE AND SCREEN', cwe_3='CPT')
        obr.observation_date_time = '20260509090000'
        obr.obr_15 = '56789^NAKAMURA^GRACE^M^^^MD'
        obr.filler_field_2 = '20260509110000'
        obr.charge_to_practice = MOC(moc_1='BB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='882-1', cwe_2='ABO Group', cwe_3='LN')
        obx.obx_5 = 'A^Group A^HL70116'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509103000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='10331-7', cwe_2='Rh Type', cwe_3='LN')
        obx_2.obx_5 = 'POS^Positive^HL70116'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509103000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='890-4', cwe_2='Antibody Screen', cwe_3='LN')
        obx_3.obx_5 = 'NEG^Negative^HL70116'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509104500'

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='AURORALAB')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='AURORA')
        msh.date_time_of_message = '20260509143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AUL2026050914300044'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='A9182734', cx_4='AURORA', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='XIONG', xpn_2='MAI', xpn_3='PANG', xpn_5='')
        pid.date_time_of_birth = '19880305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4012 S Layton Blvd', xad_3='Milwaukee', xad_4='WI', xad_5='53215', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^414^6729843501'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='S')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_2='200', pl_3='1', pl_4='AURORA')
        pv1.pv1_7 = '78901^LINDGREN^ERIC^W^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD7738300', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='AURLAB020', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509120000'
        orc.orc_12 = '78901^LINDGREN^ERIC^W^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD7738300', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='AURLAB020', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='81001', cwe_2='URINALYSIS WITH MICRO', cwe_3='CPT')
        obr.observation_date_time = '20260509120000'
        obr.obr_15 = '78901^LINDGREN^ERIC^W^^^MD'
        obr.filler_field_2 = '20260509143000'
        obr.charge_to_practice = MOC(moc_1='LAB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='5767-9', cwe_2='Appearance', cwe_3='LN')
        obx.obx_5 = 'CLOUDY^Cloudy^HL70080'
        obx.reference_range = 'CLEAR'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='5778-6', cwe_2='Color', cwe_3='LN')
        obx_2.obx_5 = 'YELLOW^Yellow^HL70080'
        obx_2.reference_range = 'YELLOW'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2965-2', cwe_2='Specific Gravity', cwe_3='LN')
        obx_3.obx_5 = '1.025'
        obx_3.reference_range = '1.005-1.030'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2756-5', cwe_2='pH', cwe_3='LN')
        obx_4.obx_5 = '6.0'
        obx_4.reference_range = '5.0-8.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CE'
        obx_5.observation_identifier = CWE(cwe_1='20405-7', cwe_2='WBC Urine', cwe_3='LN')
        obx_5.obx_5 = 'TNTC^Too numerous to count^HL70080'
        obx_5.reference_range = '0-5'
        obx_5.interpretation_codes = CWE(cwe_1='HH')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509141000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'CE'
        obx_6.observation_identifier = CWE(cwe_1='20409-9', cwe_2='RBC Urine', cwe_3='LN')
        obx_6.obx_5 = '5-10^5-10/HPF^HL70080'
        obx_6.reference_range = '0-2'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509141000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'CE'
        obx_7.observation_identifier = CWE(cwe_1='5794-3', cwe_2='Bacteria', cwe_3='LN')
        obx_7.obx_5 = 'MANY^Many^HL70080'
        obx_7.reference_range = 'NONE'
        obx_7.interpretation_codes = CWE(cwe_1='A')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260509141000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'CE'
        obx_8.observation_identifier = CWE(cwe_1='25145-4', cwe_2='Nitrite', cwe_3='LN')
        obx_8.obx_5 = 'POS^Positive^HL70136'
        obx_8.reference_range = 'NEG'
        obx_8.interpretation_codes = CWE(cwe_1='A')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'CE'
        obx_9.observation_identifier = CWE(cwe_1='5799-2', cwe_2='Leukocyte Esterase', cwe_3='LN')
        obx_9.obx_5 = '3+^3+^HL70136'
        obx_9.reference_range = 'NEG'
        obx_9.interpretation_codes = CWE(cwe_1='A')
        obx_9.observation_result_status = 'F'
        obx_9.date_time_of_the_observation = '20260509140000'

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='FROEDLAB')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='FROEDTERT')
        msh.date_time_of_message = '20260509091500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'FRL2026050909150088'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='F4829174', cx_4='FROEDTERT', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='WASHINGTON', xpn_2='TERRENCE', xpn_3='MARCUS', xpn_5='')
        pid.date_time_of_birth = '19560203'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2741 N Palmer St', xad_3='Milwaukee', xad_4='WI', xad_5='53212', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^414^3729915507'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5N', pl_2='510', pl_3='1', pl_4='FROEDTERT')
        pv1.pv1_7 = '34567^OLAWALE^CHIDI^A^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD9938500', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='FRL500', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509073000'
        orc.orc_12 = '34567^OLAWALE^CHIDI^A^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD9938500', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='FRL500', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='85610', cwe_2='PROTHROMBIN TIME', cwe_3='CPT')
        obr.observation_date_time = '20260509073000'
        obr.obr_15 = '34567^OLAWALE^CHIDI^A^^^MD'
        obr.filler_field_2 = '20260509091500'
        obr.charge_to_practice = MOC(moc_1='LAB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='PT', cwe_3='LN')
        obx.obx_5 = '14.8'
        obx.units = CWE(cwe_1='seconds')
        obx.reference_range = '11.0-13.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509090000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '1.3'
        obx_2.reference_range = '0.9-1.1'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509090000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='aPTT', cwe_3='LN')
        obx_3.obx_5 = '34'
        obx_3.units = CWE(cwe_1='seconds')
        obx_3.reference_range = '25-35'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509090000'

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='MCLLAB')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='MARSHFIELD')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MCB2026050910000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='M5829174', cx_4='MARSHFIELD', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='KRUEGER', xpn_2='BEVERLY', xpn_3='RUTH', xpn_5='')
        pid.date_time_of_birth = '19650420'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='504 W Arnold St', xad_3='Marshfield', xad_4='WI', xad_5='54449', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^715^3876641208'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MCLENDO', pl_2='100', pl_3='1', pl_4='MARSHFIELD')
        pv1.pv1_7 = '23456^HAGEN^PETER^J^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD8847555', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='MCLAB100', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260508150000'
        orc.orc_12 = '23456^HAGEN^PETER^J^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD8847555', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='MCLAB100', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='83036', cwe_2='HEMOGLOBIN A1C', cwe_3='CPT')
        obr.observation_date_time = '20260508150000'
        obr.obr_15 = '23456^HAGEN^PETER^J^^^MD'
        obr.filler_field_2 = '20260509100000'
        obr.charge_to_practice = MOC(moc_1='LAB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobin A1c', cwe_3='LN')
        obx.obx_5 = '7.8'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '<5.7'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509093000'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.source_of_comment = 'L'
        nte.comment = 'Hemoglobin A1c 7.8% corresponds to estimated average glucose of 177 mg/dL'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx
        observation.nte = nte

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='27353-2', cwe_2='Estimated Average Glucose', cwe_3='LN')
        obx_2.obx_5 = '177'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '<117'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509093000'

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='UWLAB')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UWHEALTH')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'BKT2026050916000055'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='E8827364', cx_4='UWHEALTH', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='HALVERSON', xpn_2='TYLER', xpn_3='JOSEPH', xpn_5='')
        pid.date_time_of_birth = '19920814'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='518 N Frances St', xad_3='Madison', xad_4='WI', xad_5='53703', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^608^2098816234'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='S')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='T5', pl_3='1', pl_4='UWHEALTH')
        pv1.pv1_7 = '67890^ABRAMS^VICTORIA^L^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD8899102', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKTOX001', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509130000'
        orc.orc_12 = '67890^ABRAMS^VICTORIA^L^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD8899102', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKTOX001', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='80307', cwe_2='DRUG SCREEN PANEL', cwe_3='CPT')
        obr.observation_date_time = '20260509130000'
        obr.obr_15 = '67890^ABRAMS^VICTORIA^L^^^MD'
        obr.filler_field_2 = '20260509160000'
        obr.charge_to_practice = MOC(moc_1='LAB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='3426-4', cwe_2='Amphetamines Urine', cwe_3='LN')
        obx.obx_5 = 'NEG^Negative^HL70136'
        obx.reference_range = 'NEG'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509153000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='3427-2', cwe_2='Barbiturates Urine', cwe_3='LN')
        obx_2.obx_5 = 'NEG^Negative^HL70136'
        obx_2.reference_range = 'NEG'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509153000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='3428-0', cwe_2='Benzodiazepines Urine', cwe_3='LN')
        obx_3.obx_5 = 'NEG^Negative^HL70136'
        obx_3.reference_range = 'NEG'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509153000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='3397-7', cwe_2='Cocaine Urine', cwe_3='LN')
        obx_4.obx_5 = 'NEG^Negative^HL70136'
        obx_4.reference_range = 'NEG'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509153000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CE'
        obx_5.observation_identifier = CWE(cwe_1='19295-5', cwe_2='Opiates Urine', cwe_3='LN')
        obx_5.obx_5 = 'POS^Positive^HL70136'
        obx_5.reference_range = 'NEG'
        obx_5.interpretation_codes = CWE(cwe_1='A')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509153000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'CE'
        obx_6.observation_identifier = CWE(cwe_1='3878-6', cwe_2='THC Urine', cwe_3='LN')
        obx_6.obx_5 = 'NEG^Negative^HL70136'
        obx_6.reference_range = 'NEG'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509153000'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.source_of_comment = 'L'
        nte.comment = 'Confirmatory testing ordered for Opiates positive screen'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6
        observation_6.nte = nte

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='UWMICRO')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UWHEALTH')
        msh.date_time_of_message = '20260509200000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'BKM2026050920000077'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='A9182734', cx_4='AURORA', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='XIONG', xpn_2='MAI', xpn_3='PANG', xpn_5='')
        pid.date_time_of_birth = '19880305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4012 S Layton Blvd', xad_3='Milwaukee', xad_4='WI', xad_5='53215', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^414^6729843501'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='S')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_2='200', pl_3='1', pl_4='AURORA')
        pv1.pv1_7 = '78901^LINDGREN^ERIC^W^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD7738301', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKMICRO01', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260507100000'
        orc.orc_12 = '78901^LINDGREN^ERIC^W^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD7738301', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKMICRO01', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='87088', cwe_2='URINE CULTURE', cwe_3='CPT')
        obr.observation_date_time = '20260507100000'
        obr.obr_15 = '78901^LINDGREN^ERIC^W^^^MD'
        obr.filler_field_2 = '20260509200000'
        obr.charge_to_practice = MOC(moc_1='MB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='6463-4', cwe_2='Bacteria identified', cwe_3='LN')
        obx.obx_5 = 'Escherichia coli >100,000 CFU/mL'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='18907-6', cwe_2='Ampicillin Susceptibility', cwe_3='LN')
        obx_2.obx_5 = 'R^Resistant^HL70136'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509180000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='18928-2', cwe_2='Ceftriaxone Susceptibility', cwe_3='LN')
        obx_3.obx_5 = 'S^Susceptible^HL70136'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509180000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='18945-6', cwe_2='Ciprofloxacin Susceptibility', cwe_3='LN')
        obx_4.obx_5 = 'S^Susceptible^HL70136'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509180000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CE'
        obx_5.observation_identifier = CWE(cwe_1='18961-3', cwe_2='Nitrofurantoin Susceptibility', cwe_3='LN')
        obx_5.obx_5 = 'S^Susceptible^HL70136'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509180000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'CE'
        obx_6.observation_identifier = CWE(cwe_1='18993-6', cwe_2='Trimethoprim-Sulfa Susceptibility', cwe_3='LN')
        obx_6.obx_5 = 'R^Resistant^HL70136'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509180000'

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='FROEDPATH')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='FROEDTERT')
        msh.date_time_of_message = '20260508160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'BKP2026050816000044'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='F3928401', cx_4='FROEDTERT', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='VELASQUEZ', xpn_2='ROSA', xpn_3='INEZ', xpn_5='')
        pid.date_time_of_birth = '19750812'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2131-1', cwe_2='Hispanic', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3108 W Burnham St', xad_3='Milwaukee', xad_4='WI', xad_5='53215', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^414^3840091'
        pid.primary_language = CWE(cwe_1='SPA')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='8W', pl_2='802', pl_3='2', pl_4='FROEDTERT')
        pv1.pv1_7 = '67890^KRASINSKI^PAUL^W^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD9928473', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKPATH01', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260506100000'
        orc.orc_12 = '67890^KRASINSKI^PAUL^W^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD9928473', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKPATH01', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='SURGICAL PATHOLOGY', cwe_3='CPT')
        obr.observation_date_time = '20260506100000'
        obr.obr_15 = '67890^KRASINSKI^PAUL^W^^^MD'
        obr.filler_field_2 = '20260508160000'
        obr.charge_to_practice = MOC(moc_1='SP')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='22634-0', cwe_2='Pathology Gross Description', cwe_3='LN')
        obx.obx_5 = (
            'Received in formalin labeled "right femoral head" is a 4.5 x 4.2 x 3.8 cm femoral head with attached neck fragment. The articular surface sh'
            'ows areas of flattening and yellow-tan discoloration involving approximately 40% of the surface.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260507090000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='22635-7', cwe_2='Pathology Microscopic Description', cwe_3='LN')
        obx_2.obx_5 = (
            'Sections demonstrate extensive osteonecrosis with empty lacunae, fibrosis of the marrow space, and reactive new bone formation at the periph'
            'ery. No viable tumor identified.'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260508100000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='PATH-GROSS', cwe_2='Gross Photo', cwe_3='BEAKER')
        obx_3.obx_5 = (
            'FROEDTERT^IM^PNG^Base64^'
            'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vu'
            'PBoAAANqSURBVGiB7ZlNaBNBFMd/s0mTpmnaWg9aLYp+oNiqIKIgggcP4kURvQgKHjx4EbwIPYgexIuoIJ68ePEiIiIiIiKCIKKIioh+oNVaq7Vt2jRpvnZnPGw2bpJN0sZufOD/YJjZ'
            'nTf/eW925s0uKKVUFcICKbEw1l+GGCWK9rr08GD0xYS+WT6pjH8kq/vQanLkEo4sQNdTomjNmxcnHcaqlFJlhNsGc23SUpNLOYLfFQKrG5wIqayMUKmMCnH+XFIZBzs0CQDqRqjUxb9d'
            'GkBQN2rPiylVEkBtVSAIHzeBMC0yDhRvLNUvV/9P6T5KVKpgJ1tVKqXEMquVoILF5xobEzEz/tWfycqUKXJjEelUlklSnuZm29Pq//8C5JE1i6HkykVU1UAsO8qW2hnb8DaAXd3HtO3K'
            'lu2MNHXBCqzYhRVvL2uikrgOb7cLk0xFuKYjQVw/AAZO7xvjxgc/s8Z5TSqmyAKi5YhYZkigRSQVSKSWl1aMvEk8mcv/LJNEkKE+h3BdANfNRz4UicF2dXFdKqZJK9L/IlcqkSqR8v5y'
            '8q+t0tGfykYj8TZZP9eoymHOD2R30emSNqyxQOqMqACyU35/6nKqZ2YWZ0V8+FNIplVIlAFj/GCx/zAUSOIeigSn2r6nPNJT7n/TgcjjqSsIBt/u3yTqeqhYKAFYLF2J6PRDAK1UKAFY'
            '/RipIh7HWy+ZTBVFKaVKKrHi5v4aq5STm0z3Bz6fEE+kVEqVAPBuOTMoqUxYt0qJxJNpsP7epXJcUkqpEgC8PjTcp4pibz1vMtUfkpNfJqVUqaC3+9rDftlV/18h/g9YFwmGE0Mn/Ovq'
            'T+eJaVnHo0k5eVappUoqMcpbh7NTIm+k3WT7u8OQZFIqpVRJJSbdHRz+rJj2LXBL12HfoJckYDKlUkqVAOD8ygkfrpNJx3Tfv/GVzaLjFBNcGc3xyJJI0y6dUimlSgCwfWnk58Tz5lm/'
            '6GW/8j03kkiplFIlADi+aeRXe+1/y/37OByOulJwQARVKMN8FNXMrZJKKVVSiYlXH5m3p/cAa+s7rZVfcjBWSqmUUiUABL5f3axLSCRVBUDgUmR0FgCAPrQyZmopNbGUUimlSirR9y1Y'
            '3atcqNVVl1k1pJRSKaVKAPgHnV5qkwHNb5oAAAAASUVORK5CYII='
        )
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260507091500'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Pathology Diagnosis', cwe_3='LN')
        obx_4.obx_5 = 'FINAL DIAGNOSIS: Right femoral head, excision - Avascular necrosis (osteonecrosis), extensive, with no evidence of malignancy.'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260508160000'

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='UWLAB')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UWHEALTH')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'BKL2026050914000022'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='E4829173', cx_4='UWHEALTH', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='BERGSTROM', xpn_2='ALLEN', xpn_3='RAYMOND', xpn_5='')
        pid.date_time_of_birth = '19710603'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2204 Monroe St', xad_3='Madison', xad_4='WI', xad_5='53711', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^608^2413378102'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='UWLABDRAW', pl_2='LD2', pl_3='1', pl_4='UWHEALTH')
        pv1.pv1_7 = '12345^ENGSTROM^DANIEL^R^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD9928477', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKLIP001', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509080000'
        orc.orc_12 = '12345^ENGSTROM^DANIEL^R^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD9928477', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKLIP001', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='80061', cwe_2='LIPID PANEL', cwe_3='CPT')
        obr.observation_date_time = '20260509080000'
        obr.obr_15 = '12345^ENGSTROM^DANIEL^R^^^MD'
        obr.filler_field_2 = '20260509140000'
        obr.charge_to_practice = MOC(moc_1='LAB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Total Cholesterol', cwe_3='LN')
        obx.obx_5 = '224'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '<200'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509130000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Triglycerides', cwe_3='LN')
        obx_2.obx_5 = '185'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '<150'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509130000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL Cholesterol', cwe_3='LN')
        obx_3.obx_5 = '42'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '>40'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509130000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL Cholesterol (calculated)', cwe_3='LN')
        obx_4.obx_5 = '145'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '<100'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509130000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='43396-1', cwe_2='Non-HDL Cholesterol', cwe_3='LN')
        obx_5.obx_5 = '182'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '<130'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509130000'

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='AURORALAB')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='AURORA')
        msh.date_time_of_message = '20260509113000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AUB2026050911300066'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='A1029384', cx_4='AURORA', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='VANG', xpn_2='CHOUA', xpn_3='SEE', xpn_5='')
        pid.date_time_of_birth = '19910117'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='5722 W Mitchell St', xad_3='West Allis', xad_4='WI', xad_5='53214', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^414^5281973604'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='S')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='WAUKESHA', pl_2='300', pl_3='1', pl_4='AURORA')
        pv1.pv1_7 = '34567^SVENDSEN^LARS^P^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD7738400', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='AURLAB030', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509080000'
        orc.orc_12 = '34567^SVENDSEN^LARS^P^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD7738400', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='AURLAB030', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='84443', cwe_2='TSH', cwe_3='CPT')
        obr.observation_date_time = '20260509080000'
        obr.obr_15 = '34567^SVENDSEN^LARS^P^^^MD'
        obr.filler_field_2 = '20260509113000'
        obr.charge_to_practice = MOC(moc_1='LAB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '6.8'
        obx.units = CWE(cwe_1='uIU/mL')
        obx.reference_range = '0.27-4.20'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3026-2', cwe_2='Free T4', cwe_3='LN')
        obx_2.obx_5 = '0.7'
        obx_2.units = CWE(cwe_1='ng/dL')
        obx_2.reference_range = '0.9-1.7'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='Free T3', cwe_3='LN')
        obx_3.obx_5 = '2.1'
        obx_3.units = CWE(cwe_1='pg/mL')
        obx_3.reference_range = '2.0-4.4'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509110000'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.source_of_comment = 'L'
        nte.comment = 'Results suggest primary hypothyroidism. Clinical correlation recommended.'

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='UWLAB')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UWHEALTH')
        msh.date_time_of_message = '20260508170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'BKN2026050817000033'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='E5928173', cx_4='UWHEALTH', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='BRANDT', xpn_2='MEGAN', xpn_3='RENEE', xpn_5='')
        pid.date_time_of_birth = '19940312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3410 Atwood Ave', xad_3='Madison', xad_4='WI', xad_5='53714', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^608^2440027891'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='UWOBGYN', pl_2='OB1', pl_3='1', pl_4='UWHEALTH')
        pv1.pv1_7 = '45678^OKONKWO^AMARA^T^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD8855010', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKPREN01', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260506090000'
        orc.orc_12 = '45678^OKONKWO^AMARA^T^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD8855010', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKPREN01', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='81420', cwe_2='CELL-FREE DNA SCREENING', cwe_3='CPT')
        obr.observation_date_time = '20260506090000'
        obr.obr_15 = '45678^OKONKWO^AMARA^T^^^MD'
        obr.filler_field_2 = '20260508170000'
        obr.charge_to_practice = MOC(moc_1='LAB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='21893-3', cwe_2='Trisomy 21 Risk', cwe_3='LN')
        obx.obx_5 = 'NEG^Low Risk^HL70136'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260508160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='21894-1', cwe_2='Trisomy 18 Risk', cwe_3='LN')
        obx_2.obx_5 = 'NEG^Low Risk^HL70136'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260508160000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='21895-8', cwe_2='Trisomy 13 Risk', cwe_3='LN')
        obx_3.obx_5 = 'NEG^Low Risk^HL70136'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260508160000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='86664-5', cwe_2='Fetal Sex', cwe_3='LN')
        obx_4.obx_5 = 'LA14042-8^Female^LN'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260508160000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='92133-8', cwe_2='Fetal Fraction', cwe_3='LN')
        obx_5.obx_5 = '12.4'
        obx_5.units = CWE(cwe_1='%')
        obx_5.reference_range = '>4.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260508160000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ED'
        obx_6.observation_identifier = CWE(cwe_1='PRENATAL-RPT', cwe_2='Prenatal Screening Report', cwe_3='BEAKER')
        obx_6.obx_5 = (
            'UWHEALTH^AP^PDF^Base64^'
            'JVBERi0xLjUKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwKL0xlbmd0aCAzMDAKPj4Kc3RyZWFtCkJUCi9GMSAxNCBUZgoxIDAgMCAxIDcyIDcyMCBUbQooQ2VsbC1GcmVlIEROQSBTY3JlZW5pbmcgUmVwb3J0KSBUagowIC0yNCBUZAooUGF0'
            'aWVudDogSG9mZm1hbiwgSmVzc2ljYSBMeW5uKSBUagowIC0yMCBUZAooRE9COiAwMy8xMi8xOTk0KSBUagowIC0yMCBUZAooQ29sbGVjdGlvbiBEYXRlOiAwNS8wNi8yMDI2KSBUagow'
            'IC0yMCBUZAooR2VzdGF0aW9uYWwgQWdlOiAxMiB3ZWVrcyA0IGRheXMpIFRqCjAgLTMwIFRkCihSZXN1bHRzOikgVGoKMCAtMjAgVGQKKFRyaXNvbXkgMjEgLSBMT1cgUklTSykgVGoK'
            'MCAtMjAgVGQKKFRyaXNvbXkgMTggLSBMT1cgUklTSykgVGoKMCAtMjAgVGQKKFRyaXNvbXkgMTMgLSBMT1cgUklTSykgVGoKMCAtMjAgVGQKKEZldGFsIFNleDogRmVtYWxlKSBUagpF'
            'VAplbmRzdHJlYW0KZW5kb2JqCmVuZG9mCg=='
        )
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260508170000'

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='UWMOLECULAR')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UWHEALTH')
        msh.date_time_of_message = '20260509063000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'BKC2026050906300011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='E6729183', cx_4='UWHEALTH', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='STEINBERG', xpn_2='NATHAN', xpn_3='CLARK', xpn_5='')
        pid.date_time_of_birth = '19801109'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='705 Regent St', xad_3='Madison', xad_4='WI', xad_5='53715', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^608^2617743920'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='R8', pl_3='1', pl_4='UWHEALTH')
        pv1.pv1_7 = '89012^DIETRICH^LAURA^K^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD8872100', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKCOV001', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509010000'
        orc.orc_12 = '89012^DIETRICH^LAURA^K^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD8872100', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKCOV001', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='94500-6', cwe_2='SARS-COV-2 RNA', cwe_3='LN')
        obr.observation_date_time = '20260509010000'
        obr.obr_15 = '89012^DIETRICH^LAURA^K^^^MD'
        obr.filler_field_2 = '20260509063000'
        obr.charge_to_practice = MOC(moc_1='LAB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='94500-6', cwe_2='SARS-CoV-2 RNA NAA+probe Ql', cwe_3='LN')
        obx.obx_5 = '260373001^Detected^SCT'
        obx.reference_range = 'Not Detected'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509060000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='94745-7', cwe_2='SARS-CoV-2 RNA Ct value', cwe_3='LN')
        obx_2.obx_5 = '22.4'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509060000'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.source_of_comment = 'L'
        nte.comment = 'Low Ct value indicates high viral load. Patient should isolate per current guidelines.'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2
        observation_2.nte = nte

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='FROEDTERT')
        msh.receiving_application = HD(hd_1='BEAKER')
        msh.receiving_facility = HD(hd_1='FROBLOODBANK')
        msh.date_time_of_message = '20260509144500'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'FBB2026050914450022'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='F4829174', cx_4='FROEDTERT', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='WASHINGTON', xpn_2='TERRENCE', xpn_3='MARCUS', xpn_5='')
        pid.date_time_of_birth = '19560203'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2741 N Palmer St', xad_3='Milwaukee', xad_4='WI', xad_5='53212', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^414^3729915507'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5N', pl_2='510', pl_3='1', pl_4='FROEDTERT')
        pv1.pv1_7 = '34567^OLAWALE^CHIDI^A^^^MD'

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO21PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD9938600', ei_2='EPIC')
        orc.placer_order_group_number = EI(ei_1='FBBGRP001')
        orc.date_time_of_order_event = '20260509144500'
        orc.orc_12 = '34567^OLAWALE^CHIDI^A^^^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD9938600', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='86920', cwe_2='CROSSMATCH', cwe_3='CPT')
        obr.observation_date_time = '20260509144500'
        obr.relevant_clinical_information = CWE(cwe_1='STAT')
        obr.obr_16 = '34567^OLAWALE^CHIDI^A^^^MD'
        obr.results_rpt_status_chng_date_time = '20260509'
        obr.diagnostic_serv_sect_id = 'BB'

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_type = CWE(cwe_1='BLD', cwe_2='Blood', cwe_3='HL70487')
        spm.specimen_risk_code = CWE(cwe_1='20260509144500')
        spm.specimen_collection_date_time = DR(dr_1='20260509145000')

        # .. build the SPECIMEN group ..
        specimen = OmlO21Specimen()
        specimen.spm = spm

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OmlO21ObservationRequest()
        observation_request.obr = obr
        observation_request.specimen = specimen

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc
        order.observation_request = observation_request

        # .. build BPO ..
        bpo = BPO()
        bpo.set_id_bpo = '1'
        bpo.bp_universal_service_identifier = CWE(cwe_1='OP', cwe_2='Packed Red Blood Cells', cwe_3='HL70426')
        bpo.bp_quantity = '2'
        bpo.bp_amount = 'U'
        bpo.bp_requested_dispense_to_location = PL(pl_1='20260510')

        # .. assemble the full message ..
        msg = OML_O21()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [bpo]

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='UWCYTOPATH')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UWHEALTH')
        msh.date_time_of_message = '20260507150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'BKY2026050715000088'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='E5928173', cx_4='UWHEALTH', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='BRANDT', xpn_2='MEGAN', xpn_3='RENEE', xpn_5='')
        pid.date_time_of_birth = '19940312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3410 Atwood Ave', xad_3='Madison', xad_4='WI', xad_5='53714', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^608^2440027891'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='UWOBGYN', pl_2='OB1', pl_3='1', pl_4='UWHEALTH')
        pv1.pv1_7 = '45678^OKONKWO^AMARA^T^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD8854001', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKCYTO01', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260505140000'
        orc.orc_12 = '45678^OKONKWO^AMARA^T^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD8854001', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKCYTO01', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='88141', cwe_2='PAP SMEAR', cwe_3='CPT')
        obr.observation_date_time = '20260505140000'
        obr.obr_15 = '45678^OKONKWO^AMARA^T^^^MD'
        obr.filler_field_2 = '20260507150000'
        obr.charge_to_practice = MOC(moc_1='CY')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='19762-4', cwe_2='General Categorization', cwe_3='LN')
        obx.obx_5 = 'NILM^Negative for Intraepithelial Lesion or Malignancy^HL70136'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260507143000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='19764-0', cwe_2='Statement of adequacy', cwe_3='LN')
        obx_2.obx_5 = 'Satisfactory for evaluation. Endocervical/transformation zone component present.'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260507143000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='19774-9', cwe_2='HPV High Risk', cwe_3='LN')
        obx_3.obx_5 = '260385009^Negative^SCT'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260507144000'

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='UWFLOWCYTO')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UWHEALTH')
        msh.date_time_of_message = '20260508180000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'BKF2026050818000099'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='E3827461', cx_4='UWHEALTH', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='GUSTAFSON', xpn_2='DALE', xpn_3='WILLIAM', xpn_5='')
        pid.date_time_of_birth = '19580901'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='4209 Nakoma Rd', xad_3='Madison', xad_4='WI', xad_5='53711', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^608^2335509817'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='7W', pl_2='710', pl_3='1', pl_4='UWHEALTH')
        pv1.pv1_7 = '34567^BHATT^NISHA^R^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD8866200', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKFLOW01', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260507130000'
        orc.orc_12 = '34567^BHATT^NISHA^R^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD8866200', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKFLOW01', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='88184', cwe_2='FLOW CYTOMETRY', cwe_3='CPT')
        obr.observation_date_time = '20260507130000'
        obr.obr_15 = '34567^BHATT^NISHA^R^^^MD'
        obr.filler_field_2 = '20260508180000'
        obr.charge_to_practice = MOC(moc_1='HM')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='8116-7', cwe_2='CD3+', cwe_3='LN')
        obx.obx_5 = '78'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '60-85'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260508150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='8117-5', cwe_2='CD4+', cwe_3='LN')
        obx_2.obx_5 = '52'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '30-60'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260508150000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='8118-3', cwe_2='CD8+', cwe_3='LN')
        obx_3.obx_5 = '24'
        obx_3.units = CWE(cwe_1='%')
        obx_3.reference_range = '15-40'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260508150000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='8119-1', cwe_2='CD19+', cwe_3='LN')
        obx_4.obx_5 = '8'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '5-20'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260508150000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='8120-9', cwe_2='CD56+/CD16+', cwe_3='LN')
        obx_5.obx_5 = '12'
        obx_5.units = CWE(cwe_1='%')
        obx_5.reference_range = '5-25'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260508150000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='32623-1', cwe_2='CD4/CD8 Ratio', cwe_3='LN')
        obx_6.obx_5 = '2.2'
        obx_6.reference_range = '1.0-4.0'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260508150000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ED'
        obx_7.observation_identifier = CWE(cwe_1='FLOW-SCATTER', cwe_2='Flow Cytometry Scatterplot', cwe_3='BEAKER')
        obx_7.obx_5 = (
            'UWHEALTH^IM^PNG^Base64^'
            'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEwAACxMBAJqcGAAAA8hJREFUSIm1lU1oXFUUx3/nvsmbZJJMHJOZxCQaE2NT'
            'sUFXIgiCCxVB3YggLlzpwoULVy5cuBJ0I4qIiIig4AcqiFhQsIiColYRk9baxjZJm4+ZZJLJzLz37r2uu5hkMjNJG/EHh3vOvff8/+d+vTFKKcqJAMyJ9AKXA4eAbcB24Bzwh1LqZ6XU'
            'klJqMV9s5rNoVmyT/6aFdgkhHlZKfQWglPouV/A5OfjwUOz2c0YzRSlBU9k5+T9bsVl6gDeAA8CYEOJlpdStSqnnAfm/LHjpSPbE+6+uVqQMoV3KFbgJuBf4CDAA3KSUOglcaLPpV8TK'
            'TzC/OJt//eHmXYEr7lgYfcOJD1/B7bEjNwB3AlcppRaA/w1gLPlvXFX2WjIi+4VQ6vnF0ckzE6f4MJx7Lmu6UgP73BgB/CuVvmCBd4FGmxn4qFAKndAPfKqUOlkf8O+v8j57IEpzrQeY'
            'AR5RSv0mhHgPmFJKJbdb8POxzKkvTi2FdVsCjjqFd4A7gL3ASaXUp8BfSqm5cgB3e7omlr4dvhqxNKaAbflgCXAUOAR8Bxj/jcLjhzOnP35nTajMqOWI3QF8DnwMHFdKLW3oQf7d5WNO'
            'zIp2Ea8QXwF3A18BzwKvK6VO58dWy78OB+P0LN6gGewzKwLAi8qkf+n8wixfVGSfbANeBg4DXwIvKaXOAbqsP/h6hS/zW3cFd4fmJo8pJb/wlFqWUi4qpVaUUpmyAOBGJRLvKqWigLYT'
            'lAD3AJ8DRimVKr/kI6DgJCFE8oPjtcEHuiK6NiKF3BdY0yBStGqNurJWqVRVwVo6IVbL/qGUShUqvLqcdEf5s2LjWDaZfaiqp1Ea0P2XBKDvAu5TSk0Cd5cEIIQ4D0QBbyuAVIb4/Gwt'
            'IpvBjwFvAKeBz5VSsyUA+L/ULn7qHkwXeUvNpbhSSl4J3KOUulkIsRt4E3hNKZXeCqCwH0h+sXM4uqN0qEBfBL4E/gAygO4PwZEJhBBPKKUeAh5USn3aClAU4JWRDJ2LuVaK7DcZKRaB'
            'm4ADwLNKqTml1NUAwLfnqm+ZXo6HA3ib1FZKfAAsBfYDn5WbxHi1AEwNpvhmOBvB0fUCnAR+KzuJNymlFrYEAHDyZP28kydbbhLuCvCLEOIt4HfgVaVUusxOXAdeF0LcIoR4Uin1BPCo'
            'UuoY5QD+OhFPf/b5Ui05V3+5K7r+CaDxBuCEUioDPAY8rpQ6EvhfAIqL+uxk8oYfBxM3SFOTbTQxCVeXnRf/W/4GuZjNJXa0AAAAElFTkSuQmCC'
        )
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260508160000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'TX'
        obx_8.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Interpretation', cwe_3='LN')
        obx_8.obx_5 = 'INTERPRETATION: Normal T-cell, B-cell, and NK-cell populations. No immunophenotypic evidence of lymphoproliferative disorder.'
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20260508180000'

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='MCLLAB')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='MARSHFIELD')
        msh.date_time_of_message = '20260509153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MCN2026050915300044'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='M5829174', cx_4='MARSHFIELD', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='KRUEGER', xpn_2='BEVERLY', xpn_3='RUTH', xpn_5='')
        pid.date_time_of_birth = '19650420'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='504 W Arnold St', xad_3='Marshfield', xad_4='WI', xad_5='54449', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^715^3876641208'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MCLENDO', pl_2='100', pl_3='1', pl_4='MARSHFIELD')
        pv1.pv1_7 = '23456^HAGEN^PETER^J^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD8847600', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='MCLAB200', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260508150000'
        orc.orc_12 = '23456^HAGEN^PETER^J^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD8847600', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='MCLAB200', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='82306', cwe_2='VITAMIN D 25-HYDROXY', cwe_3='CPT')
        obr.observation_date_time = '20260508150000'
        obr.obr_15 = '23456^HAGEN^PETER^J^^^MD'
        obr.filler_field_2 = '20260509153000'
        obr.charge_to_practice = MOC(moc_1='LAB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1989-3', cwe_2='Vitamin D, 25-OH Total', cwe_3='LN')
        obx.obx_5 = '18'
        obx.units = CWE(cwe_1='ng/mL')
        obx.reference_range = '30-100'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2498-4', cwe_2='Iron', cwe_3='LN')
        obx_2.obx_5 = '35'
        obx_2.units = CWE(cwe_1='ug/dL')
        obx_2.reference_range = '37-145'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2500-7', cwe_2='Iron Binding Capacity', cwe_3='LN')
        obx_3.obx_5 = '410'
        obx_3.units = CWE(cwe_1='ug/dL')
        obx_3.reference_range = '250-370'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2502-3', cwe_2='Iron Saturation', cwe_3='LN')
        obx_4.obx_5 = '9'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '15-55'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2276-4', cwe_2='Ferritin', cwe_3='LN')
        obx_5.obx_5 = '8'
        obx_5.units = CWE(cwe_1='ng/mL')
        obx_5.reference_range = '12-150'
        obx_5.interpretation_codes = CWE(cwe_1='L')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509150000'

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='FROEDLAB')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='FROEDTERT')
        msh.date_time_of_message = '20260509111500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'FRH2026050911150077'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='F5829174', cx_4='FROEDTERT', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='KOWALCZYK', xpn_2='STANLEY', xpn_3='VICTOR', xpn_5='')
        pid.date_time_of_birth = '19480725'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='2918 S Howell Ave', xad_3='Milwaukee', xad_4='WI', xad_5='53207', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^414^4810093527'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3E', pl_2='302', pl_3='1', pl_4='FROEDTERT')
        pv1.pv1_7 = '56789^ADEBAYO^TEMITOPE^N^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD9938700', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='FRL700', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509070000'
        orc.orc_12 = '56789^ADEBAYO^TEMITOPE^N^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD9938700', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='FRL700', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='80076', cwe_2='HEPATIC FUNCTION PANEL', cwe_3='CPT')
        obr.observation_date_time = '20260509070000'
        obr.obr_15 = '56789^ADEBAYO^TEMITOPE^N^^^MD'
        obr.filler_field_2 = '20260509111500'
        obr.charge_to_practice = MOC(moc_1='LAB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1751-7', cwe_2='Albumin', cwe_3='LN')
        obx.obx_5 = '2.8'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '3.5-5.5'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509103000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Total Bilirubin', cwe_3='LN')
        obx_2.obx_5 = '3.4'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.1-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509103000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1968-7', cwe_2='Direct Bilirubin', cwe_3='LN')
        obx_3.obx_5 = '2.1'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '0.0-0.3'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509103000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='6768-6', cwe_2='Alkaline Phosphatase', cwe_3='LN')
        obx_4.obx_5 = '312'
        obx_4.units = CWE(cwe_1='U/L')
        obx_4.reference_range = '44-147'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509103000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx_5.obx_5 = '187'
        obx_5.units = CWE(cwe_1='U/L')
        obx_5.reference_range = '7-56'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509103000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST', cwe_3='LN')
        obx_6.obx_5 = '224'
        obx_6.units = CWE(cwe_1='U/L')
        obx_6.reference_range = '10-40'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509103000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2885-2', cwe_2='Total Protein', cwe_3='LN')
        obx_7.obx_5 = '5.8'
        obx_7.units = CWE(cwe_1='g/dL')
        obx_7.reference_range = '6.0-8.3'
        obx_7.interpretation_codes = CWE(cwe_1='L')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260509103000'

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='UWLAB')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UWHEALTH')
        msh.date_time_of_message = '20260509070000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'BKC2026050907000066'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='E9273648', cx_4='UWHEALTH', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='HANSEN', xpn_2='ELAINE', xpn_3='MARGARET', xpn_5='')
        pid.date_time_of_birth = '19450811'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='302 N Midvale Blvd', xad_3='Madison', xad_4='WI', xad_5='53705', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^608^2389941006'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='W')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='R12', pl_3='1', pl_4='UWHEALTH')
        pv1.pv1_7 = '23456^MORALES^RAFAEL^S^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD8876400', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKCARD01', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509050000'
        orc.orc_12 = '23456^MORALES^RAFAEL^S^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD8876400', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKCARD01', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='30934-4', cwe_2='BNP PANEL', cwe_3='LN')
        obr.observation_date_time = '20260509050000'
        obr.obr_15 = '23456^MORALES^RAFAEL^S^^^MD'
        obr.filler_field_2 = '20260509070000'
        obr.charge_to_practice = MOC(moc_1='LAB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='30934-4', cwe_2='NT-proBNP', cwe_3='LN')
        obx.obx_5 = '4820'
        obx.units = CWE(cwe_1='pg/mL')
        obx.reference_range = '<300'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509063000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='49563-0', cwe_2='Troponin I HS', cwe_3='LN')
        obx_2.obx_5 = '2847'
        obx_2.units = CWE(cwe_1='ng/L')
        obx_2.reference_range = '<14'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509063000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2157-6', cwe_2='CK-MB', cwe_3='LN')
        obx_3.obx_5 = '18.4'
        obx_3.units = CWE(cwe_1='ng/mL')
        obx_3.reference_range = '<5.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509063000'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.source_of_comment = 'L'
        nte.comment = 'CRITICAL: NT-proBNP markedly elevated consistent with acute heart failure. Troponin critically elevated - STEMI protocol activated.'

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
    """ Based on live/us-wisconsin/us-wisconsin-epic-beaker.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEAKER')
        msh.sending_facility = HD(hd_1='UWMOLGEN')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UWHEALTH')
        msh.date_time_of_message = '20260505140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'BKG2026050514000022'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='E5928173', cx_4='UWHEALTH', cx_5='MRN')
        pid.patient_name = XPN(xpn_1='BRANDT', xpn_2='MEGAN', xpn_3='RENEE', xpn_5='')
        pid.date_time_of_birth = '19940312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='3410 Atwood Ave', xad_3='Madison', xad_4='WI', xad_5='53714', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^608^2440027891'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='UWGENETICS', pl_2='GEN1', pl_3='1', pl_4='UWHEALTH')
        pv1.pv1_7 = '56789^SORENSEN^INGRID^C^^^MD'

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
        orc.placer_order_number = EI(ei_1='ORD8844001', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='BKGEN001', ei_2='BEAKER')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260420100000'
        orc.orc_12 = '56789^SORENSEN^INGRID^C^^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD8844001', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='BKGEN001', ei_2='BEAKER')
        obr.universal_service_identifier = CWE(cwe_1='81162', cwe_2='BRCA1 BRCA2 FULL GENE SEQUENCE', cwe_3='CPT')
        obr.observation_date_time = '20260420100000'
        obr.obr_15 = '56789^SORENSEN^INGRID^C^^^MD'
        obr.filler_field_2 = '20260505140000'
        obr.charge_to_practice = MOC(moc_1='GEN')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='55233-1', cwe_2='BRCA1 Gene Mutation Analysis', cwe_3='LN')
        obx.obx_5 = 'LA6577-6^Negative^LN'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260505130000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='55234-9', cwe_2='BRCA2 Gene Mutation Analysis', cwe_3='LN')
        obx_2.obx_5 = 'LA6577-6^Negative^LN'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260505130000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='51969-4', cwe_2='Genetic Analysis Summary', cwe_3='LN')
        obx_3.obx_5 = (
            'No pathogenic or likely pathogenic variants identified in BRCA1 or BRCA2. Two variants of uncertain significance (VUS) detected: BRCA2 c.752'
            '2G>A (p.Gly2508Ser) and BRCA1 c.4837A>G (p.Ser1613Gly). Clinical significance unknown at this time.'
        )
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260505133000'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.source_of_comment = 'L'
        nte.comment = 'Genetic counseling recommended to discuss VUS findings and family history implications.'

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
