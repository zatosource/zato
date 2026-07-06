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
from zato.hl7v2.v2_9.datatypes import CWE, CX, DR, EI, EIP, HD, MSG, OG, PL, PT, VID, XAD, XCN, XON
from zato.hl7v2.v2_9.groups import OmlO21Insurance, OmlO21Observation, OmlO21ObservationPrior, OmlO21ObservationRequest, OmlO21Order, OmlO21OrderPrior, \
    OmlO21Patient, OmlO21PatientVisit, OmlO21PriorResult, OmlO21Specimen, OrlO22ObservationRequest, OrlO22Order, OrlO22Response, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, OulR22CommonOrder, OulR22Order, OulR22OrderDocument, \
    OulR22Patient, OulR22Result, OulR22Specimen, OulR22Visit
from zato.hl7v2.v2_9.messages import OML_O21, ORL_O22, ORU_R01, OUL_R22
from zato.hl7v2.v2_9.segments import IN1, MSA, MSH, NTE, OBR, OBX, ORC, PID, PV1, PV2, SPM

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('nl', 'nl-clinisys-glims.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/nl/nl-clinisys-glims.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='101')
        msh.sending_facility = HD(hd_1='UMCU_LAB')
        msh.receiving_application = HD(hd_1='202')
        msh.receiving_facility = HD(hd_1='ERASMUS_LAB')
        msh.date_time_of_message = '20260509083000'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'MSG20260509001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.4.3.11.60.25.10.31', ei_2='Nictiz', ei_3='2.16.840.1.113883.2.4.3.11', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='246813579', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT001', cx_4='UMCU', cx_5='PI')]
        pid.pid_5 = 'de Jong^Anneke^W^^^Mevr.'
        pid.date_time_of_birth = '19780315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Lange Nieuwstraat 15', xad_3='Utrecht', xad_5='3512PN', xad_6='NLD', xad_7='H')
        pid.pid_13 = '^^PH^0302531847'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI KLC', pl_2='Klinische Chemie', pl_3='1')
        pv1.pv1_8 = '10045^Visser^Hendrik^^^Dr.^arts'

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
        orc.placer_order_number = EI(ei_1='ORD2026001')
        orc.orc_7 = '^^^20260509083000^^R'
        orc.date_time_of_order_event = '20260509083000'
        orc.orc_11 = '10045^Visser^Hendrik^^^Dr.^arts'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026001')
        obr.universal_service_identifier = CWE(cwe_1='24325-3', cwe_2='Electrolyte panel - Serum or Plasma', cwe_3='LN')
        obr.observation_date_time = '20260509080000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = '10045^Visser^Hendrik^^^Dr.^arts'

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_type = CWE(cwe_1='BLDV', cwe_2='Blood venous', cwe_3='HL70487')
        spm.specimen_collection_date_time = DR(dr_1='20260509080000')
        spm.specimen_received_date_time = '20260509081500'

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

        # .. assemble the full message ..
        msg = OML_O21()
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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='305')
        msh.sending_facility = HD(hd_1='OLVG_LAB')
        msh.receiving_application = HD(hd_1='912')
        msh.receiving_facility = HD(hd_1='RIVM_IDS')
        msh.date_time_of_message = '20260509091500'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'MSG20260509002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.4.3.11.60.25.10.31', ei_2='Nictiz', ei_3='2.16.840.1.113883.2.4.3.11', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='135792468', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT002', cx_4='OLVG', cx_5='PI')]
        pid.pid_5 = 'Smit^Pieter^J^^^Dhr.'
        pid.date_time_of_birth = '19650722'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Prinsengracht 312', xad_3='Amsterdam', xad_5='1016HX', xad_6='NLD', xad_7='H')
        pid.pid_13 = '^^PH^0206641827'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IC', pl_2='Intensive Care', pl_3='Bed 3')
        pv1.pv1_7 = '20010^Dekker^Elisabeth^^^Dr.^arts'

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
        orc.placer_order_number = EI(ei_1='ORD2026002')
        orc.orc_7 = '^^^20260509091500^^R'
        orc.date_time_of_order_event = '20260509091500'
        orc.orc_11 = '20010^Dekker^Elisabeth^^^Dr.^arts'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026002')
        obr.universal_service_identifier = CWE(cwe_1='29576-6', cwe_2='Bacterial susceptibility panel', cwe_3='LN')
        obr.observation_date_time = '20260509090000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = '20010^Dekker^Elisabeth^^^Dr.^arts'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='46239-0', cwe_2='Chief complaint', cwe_3='LN')
        obx.obx_5 = 'Urineweginfectie, recidiverend'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OmlO21Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='8251-1', cwe_2='Service comment', cwe_3='LN')
        obx_2.obx_5 = 'Resistentiebepaling gevraagd na kweek positief E.coli'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OmlO21Observation()
        observation_2.obx = obx_2

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_type = CWE(cwe_1='UR', cwe_2='Urine', cwe_3='HL70487')
        spm.specimen_collection_date_time = DR(dr_1='20260509085500')
        spm.specimen_received_date_time = '20260509090000'

        # .. build the SPECIMEN group ..
        specimen = OmlO21Specimen()
        specimen.spm = spm

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='ORD2026002')
        obr_2.universal_service_identifier = CWE(cwe_1='29576-6', cwe_2='Bacterial susceptibility panel', cwe_3='LN')

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '1'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='6652-2', cwe_2='Meropenem [Susceptibility] by Minimum inhibitory concentration (MIC)', cwe_3='LN')
        obx_3.obx_5 = '>=16'
        obx_3.units = CWE(cwe_1='mg/L')
        obx_3.interpretation_codes = CWE(cwe_1='null')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior = OmlO21ObservationPrior()
        observation_prior.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '2'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='7029-2', cwe_2='Meropenem [Susceptibility] by Gradient strip', cwe_3='LN')
        obx_4.obx_5 = '8.0'
        obx_4.units = CWE(cwe_1='mg/L')
        obx_4.interpretation_codes = CWE(cwe_1='null')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior_2 = OmlO21ObservationPrior()
        observation_prior_2.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '3'
        obx_5.observation_identifier = CWE(cwe_1='18943-1', cwe_2='Meropenem [Susceptibility]', cwe_3='LN')
        obx_5.interpretation_codes = CWE(cwe_1='R')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior_3 = OmlO21ObservationPrior()
        observation_prior_3.obx = obx_5

        # .. build the ORDER_PRIOR group ..
        order_prior = OmlO21OrderPrior()
        order_prior.obr = obr_2
        order_prior.observation_prior = observation_prior
        order_prior.observation_prior_2 = observation_prior_2
        order_prior.observation_prior_3 = observation_prior_3

        # .. build the PRIOR_RESULT group ..
        prior_result = OmlO21PriorResult()
        prior_result.order_prior = order_prior

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OmlO21ObservationRequest()
        observation_request.obr = obr
        observation_request.observation = observation
        observation_request.observation_2 = observation_2
        observation_request.specimen = specimen
        observation_request.prior_result = prior_result

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc
        order.observation_request = observation_request

        # .. assemble the full message ..
        msg = OML_O21()
        msg.msh = msh
        msg.patient = patient
        msg.order = order

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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='202')
        msh.sending_facility = HD(hd_1='ERASMUS_LAB')
        msh.receiving_application = HD(hd_1='101')
        msh.receiving_facility = HD(hd_1='UMCU_LAB')
        msh.date_time_of_message = '20260509103000'
        msh.message_type = MSG(msg_1='OUL', msg_2='R22', msg_3='OUL_R22')
        msh.message_control_id = 'MSG20260509003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.4.3.11.60.25.10.32', ei_2='Nictiz', ei_3='2.16.840.1.113883.2.4.3.11', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='246813579', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT001', cx_4='UMCU', cx_5='PI')]
        pid.pid_5 = 'de Jong^Anneke^W^^^Mevr.'
        pid.date_time_of_birth = '19780315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Lange Nieuwstraat 15', xad_3='Utrecht', xad_5='3512PN', xad_6='NLD', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI KLC', pl_2='Klinische Chemie', pl_3='1')

        # .. build the VISIT group ..
        visit = OulR22Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OulR22Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_type = CWE(cwe_1='BLDV', cwe_2='Blood venous', cwe_3='HL70487')
        spm.specimen_collection_date_time = DR(dr_1='20260509080000')
        spm.specimen_received_date_time = '20260509081500'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026001')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel - Blood by Automated count', cwe_3='LN')
        obr.observation_date_time = '20260509090000'
        obr.results_rpt_status_chng_date_time = '20260509103000'
        obr.result_status = 'F'

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD2026001')
        orc.parent_order = EIP(eip_1='20260509103000')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin [Mass/volume] in Blood', cwe_3='LN')
        obx.obx_5 = '8.2'
        obx.units = CWE(cwe_1='mmol/L', cwe_2='mmol/L', cwe_3='UCUM')
        obx.reference_range = '7.5-10.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509100000'

        # .. build the ORDER_DOCUMENT group ..
        order_document = OulR22OrderDocument()
        order_document.obx = obx

        # .. build the COMMON_ORDER group ..
        common_order = OulR22CommonOrder()
        common_order.orc = orc
        common_order.order_document = order_document

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocytes [#/volume] in Blood by Automated count', cwe_3='LN')
        obx_2.obx_5 = '7.3'
        obx_2.units = CWE(cwe_1='10*9/L', cwe_2='10*9/L', cwe_3='UCUM')
        obx_2.reference_range = '4.0-10.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509100000'

        # .. build the RESULT group ..
        result = OulR22Result()
        result.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='26515-7', cwe_2='Platelets [#/volume] in Blood by Automated count', cwe_3='LN')
        obx_3.obx_5 = '245'
        obx_3.units = CWE(cwe_1='10*9/L', cwe_2='10*9/L', cwe_3='UCUM')
        obx_3.reference_range = '150-400'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509100000'

        # .. build the RESULT group ..
        result_2 = OulR22Result()
        result_2.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrocytes [#/volume] in Blood by Automated count', cwe_3='LN')
        obx_4.obx_5 = '4.85'
        obx_4.units = CWE(cwe_1='10*12/L', cwe_2='10*12/L', cwe_3='UCUM')
        obx_4.reference_range = '3.90-5.50'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509100000'

        # .. build the RESULT group ..
        result_3 = OulR22Result()
        result_3.obx = obx_4

        # .. build the ORDER group ..
        order = OulR22Order()
        order.obr = obr
        order.common_order = common_order
        order.result = result
        order.result_2 = result_2
        order.result_3 = result_3

        # .. build the SPECIMEN group ..
        specimen = OulR22Specimen()
        specimen.spm = spm
        specimen.order = order

        # .. assemble the full message ..
        msg = OUL_R22()
        msg.msh = msh
        msg.patient = patient
        msg.specimen = specimen

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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='VUMC_LAB')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='VUMC')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260509004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='357924681', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT003', cx_4='VUMC', cx_5='PI')]
        pid.pid_5 = 'Bos^Willem^F^^^Dhr.'
        pid.date_time_of_birth = '19520410'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stadionplein 44', xad_3='Amsterdam', xad_5='1076CM', xad_6='NLD', xad_7='H')
        pid.pid_13 = '^^PH^0206448821'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4W', pl_2='Interne Geneeskunde', pl_3='Bed 12')
        pv1.pv1_7 = '30020^van der Laan^Cornelia^^^Dr.^arts'

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
        orc.placer_order_number = EI(ei_1='ORD2026003')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026003')
        obr.universal_service_identifier = CWE(cwe_1='24325-3', cwe_2='Electrolyte panel - Serum or Plasma', cwe_3='LN')
        obr.observation_date_time = '20260509100000'
        obr.results_rpt_status_chng_date_time = '20260509110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium [Moles/volume] in Serum or Plasma', cwe_3='LN')
        obx.obx_5 = '139'
        obx.units = CWE(cwe_1='mmol/L', cwe_2='mmol/L', cwe_3='UCUM')
        obx.reference_range = '135-145'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509104500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium [Moles/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.obx_5 = '4.1'
        obx_2.units = CWE(cwe_1='mmol/L', cwe_2='mmol/L', cwe_3='UCUM')
        obx_2.reference_range = '3.5-5.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509104500'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2075-0', cwe_2='Chloride [Moles/volume] in Serum or Plasma', cwe_3='LN')
        obx_3.obx_5 = '101'
        obx_3.units = CWE(cwe_1='mmol/L', cwe_2='mmol/L', cwe_3='UCUM')
        obx_3.reference_range = '98-107'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509104500'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_4.obx_5 = '89'
        obx_4.units = CWE(cwe_1='umol/L', cwe_2='umol/L', cwe_3='UCUM')
        obx_4.reference_range = '62-106'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509104500'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea nitrogen [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_5.obx_5 = '5.8'
        obx_5.units = CWE(cwe_1='mmol/L', cwe_2='mmol/L', cwe_3='UCUM')
        obx_5.reference_range = '2.5-7.5'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509104500'

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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='RIJNSTATE_LAB')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='RIJNSTATE')
        msh.date_time_of_message = '20260509113000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260509005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='864209753', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT004', cx_4='RIJNSTATE', cx_5='PI')]
        pid.pid_5 = 'Janssen^Theodora^L^^^Mevr.'
        pid.date_time_of_birth = '19870603'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Velperplein 18', xad_3='Arnhem', xad_5='6811AG', xad_6='NLD', xad_7='H')
        pid.pid_13 = '^^PH^0263541289'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI MDL', pl_2='Maag-Darm-Leverziekten', pl_3='1')
        pv1.pv1_7 = '40030^Kuiper^Adriaan^^^Dr.^arts'

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
        orc.placer_order_number = EI(ei_1='ORD2026004')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026004')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Electrolytes 1998 panel - Serum or Plasma', cwe_3='LN')
        obr.observation_date_time = '20260509101500'
        obr.results_rpt_status_chng_date_time = '20260509113000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1920-8', cwe_2='Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma', cwe_3='LN')
        obx.obx_5 = '28'
        obx.units = CWE(cwe_1='U/L', cwe_2='U/L', cwe_3='UCUM')
        obx.reference_range = '0-35'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509111000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1742-6', cwe_2='Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.obx_5 = '32'
        obx_2.units = CWE(cwe_1='U/L', cwe_2='U/L', cwe_3='UCUM')
        obx_2.reference_range = '0-45'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509111000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6768-6', cwe_2='Alkaline phosphatase [Enzymatic activity/volume] in Serum or Plasma', cwe_3='LN')
        obx_3.obx_5 = '78'
        obx_3.units = CWE(cwe_1='U/L', cwe_2='U/L', cwe_3='UCUM')
        obx_3.reference_range = '40-120'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509111000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Bilirubin.total [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_4.obx_5 = '12'
        obx_4.units = CWE(cwe_1='umol/L', cwe_2='umol/L', cwe_3='UCUM')
        obx_4.reference_range = '0-17'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509111000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2336-6', cwe_2='Gamma glutamyl transferase [Enzymatic activity/volume] in Serum or Plasma', cwe_3='LN')
        obx_5.obx_5 = '45'
        obx_5.units = CWE(cwe_1='U/L', cwe_2='U/L', cwe_3='UCUM')
        obx_5.reference_range = '0-55'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509111000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1751-7', cwe_2='Albumin [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_6.obx_5 = '42'
        obx_6.units = CWE(cwe_1='g/L', cwe_2='g/L', cwe_3='UCUM')
        obx_6.reference_range = '35-52'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509111000'

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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.receiving_application = HD(hd_1='GLIMS')
        msh.receiving_facility = HD(hd_1='ANTONIUS_LAB')
        msh.date_time_of_message = '20260509090000+0200'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'ZD20260509001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.source_of_comment = 'P'
        nte.comment = 'Klinische Chemie'
        nte.comment_type = CWE(cwe_1='ZD_CLUSTER_NAME', cwe_2='ZorgDomein clusternaam', cwe_3='L')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='579246813', cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.pid_5 = 'Hoekstra^Geertje^M^^^Mevr.'
        pid.date_time_of_birth = '19900512'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Plompetorengracht 7', xad_3='Utrecht', xad_5='3512CA', xad_6='NLD')
        pid.pid_13 = '^^PH^0302345678'
        pid.primary_language = CWE(cwe_1='NLD')
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.pv1_7 = '50040^Kok^Margaretha^^^Dr.^huisarts'
        pv1.visit_number = CX(cx_1='V20260509001')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.newborn_baby_indicator = 'Vermoeden diabetes mellitus type 2'

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO21PatientVisit()
        patient_visit.pv1 = pv1
        patient_visit.pv2 = pv2

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_id = CX(cx_1='3311', cx_2='VGZ Zorgverzekering')
        in1.insurance_company_name = XON(xon_1='VGZ')
        in1.coverage_type = CWE(cwe_1='NLD')

        # .. build the INSURANCE group ..
        insurance = OmlO21Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ZD20260509001')
        orc.orc_7 = '^^^20260509090000^^R'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD20260509001')
        obr.universal_service_identifier = CWE(cwe_1='GLU', cwe_2='Glucose nuchter', cwe_3='L')
        obr.observation_date_time = '20260509085000'
        obr.specimen_action_code = 'A'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='CLIN', cwe_2='Klinische vraag', cwe_3='L')
        obx.obx_5 = 'Nuchter glucose ter uitsluiting DM2, patient klaagt over polyurie en polydipsie'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OmlO21Observation()
        observation.obx = obx

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OmlO21ObservationRequest()
        observation_request.obr = obr
        observation_request.observation = observation

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc
        order.observation_request = observation_request

        # .. assemble the full message ..
        msg = OML_O21()
        msg.msh = msh
        msg.nte = nte
        msg.patient = patient
        msg.order = order

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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='202')
        msh.sending_facility = HD(hd_1='ERASMUS_LAB')
        msh.receiving_application = HD(hd_1='101')
        msh.receiving_facility = HD(hd_1='UMCU_LAB')
        msh.date_time_of_message = '20260509084500'
        msh.message_type = MSG(msg_1='ORL', msg_2='O22', msg_3='ORL_O22')
        msh.message_control_id = 'MSG20260509007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.4.3.11.60.25.10.33', ei_2='Nictiz', ei_3='2.16.840.1.113883.2.4.3.11', ei_4='ISO')

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MSG20260509001'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='246813579', cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.pid_5 = 'de Jong^Anneke^W^^^Mevr.'
        pid.date_time_of_birth = '19780315'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'OK'
        orc.placer_order_number = EI(ei_1='ORD2026001')
        orc.parent_order = EIP(eip_1='20260509084500')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026001')
        obr.universal_service_identifier = CWE(cwe_1='24325-3', cwe_2='Electrolyte panel - Serum or Plasma', cwe_3='LN')

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OrlO22ObservationRequest()
        observation_request.obr = obr

        # .. build the ORDER group ..
        order = OrlO22Order()
        order.orc = orc
        order.observation_request = observation_request

        # .. build the RESPONSE group ..
        response = OrlO22Response()
        response.pid = pid
        response.order = order

        # .. assemble the full message ..
        msg = ORL_O22()
        msg.msh = msh
        msg.msa = msa
        msg.response = response

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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='ISALA_LAB')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='ISALA')
        msh.date_time_of_message = '20260509130000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260509008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='648201357', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT005', cx_4='ISALA', cx_5='PI')]
        pid.pid_5 = 'Meijer^Geert^B^^^Dhr.'
        pid.date_time_of_birth = '19710918'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Grote Markt 9', xad_3='Zwolle', xad_5='8011LV', xad_6='NLD', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3A', pl_2='Chirurgie', pl_3='Bed 8')
        pv1.pv1_7 = '60050^van Beek^Johanna^^^Dr.^arts'

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
        orc.placer_order_number = EI(ei_1='ORD2026005')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026005')
        obr.universal_service_identifier = CWE(cwe_1='630-4', cwe_2='Bacteria identified in Urine by Culture', cwe_3='LN')
        obr.observation_date_time = '20260508150000'
        obr.results_rpt_status_chng_date_time = '20260509130000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='Bacteria identified in Urine by Culture', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '112283007^Escherichia coli^SCT'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509120000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18907-6', cwe_2='Ampicillin [Susceptibility] by Minimum inhibitory concentration (MIC)', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = '>32'
        obx_2.units = CWE(cwe_1='mg/L')
        obx_2.nature_of_abnormal_test = 'R'
        obx_2.user_defined_access_checks = 'F'
        obx_2.responsible_observer = XCN(xcn_1='20260509123000')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18928-2', cwe_2='Gentamicin [Susceptibility] by Minimum inhibitory concentration (MIC)', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = '0.5'
        obx_3.units = CWE(cwe_1='mg/L')
        obx_3.nature_of_abnormal_test = 'S'
        obx_3.user_defined_access_checks = 'F'
        obx_3.responsible_observer = XCN(xcn_1='20260509123000')

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18932-4', cwe_2='Ciprofloxacin [Susceptibility] by Minimum inhibitory concentration (MIC)', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = '0.25'
        obx_4.units = CWE(cwe_1='mg/L')
        obx_4.nature_of_abnormal_test = 'S'
        obx_4.user_defined_access_checks = 'F'
        obx_4.responsible_observer = XCN(xcn_1='20260509123000')

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(
            cwe_1='18862-3',
            cwe_2='Amoxicillin+Clavulanate [Susceptibility] by Minimum inhibitory concentration (MIC)',
            cwe_3='LN',
        )
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = '4'
        obx_5.units = CWE(cwe_1='mg/L')
        obx_5.nature_of_abnormal_test = 'S'
        obx_5.user_defined_access_checks = 'F'
        obx_5.responsible_observer = XCN(xcn_1='20260509123000')

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18996-9', cwe_2='Nitrofurantoin [Susceptibility] by Minimum inhibitory concentration (MIC)', cwe_3='LN')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = '16'
        obx_6.units = CWE(cwe_1='mg/L')
        obx_6.nature_of_abnormal_test = 'S'
        obx_6.user_defined_access_checks = 'F'
        obx_6.responsible_observer = XCN(xcn_1='20260509123000')

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='6652-2', cwe_2='Meropenem [Susceptibility] by Minimum inhibitory concentration (MIC)', cwe_3='LN')
        obx_7.observation_sub_id = OG(og_1='1')
        obx_7.obx_5 = '0.03'
        obx_7.units = CWE(cwe_1='mg/L')
        obx_7.nature_of_abnormal_test = 'S'
        obx_7.user_defined_access_checks = 'F'
        obx_7.responsible_observer = XCN(xcn_1='20260509123000')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.nte_3 = 'Kweek >10^5 KVE/mL. Monomicrobieel. Resistentie conform EUCAST.'

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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='ETZ_LAB')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='ETZ')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260509009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='753108642', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT006', cx_4='ETZ', cx_5='PI')]
        pid.pid_5 = 'van der Heijden^Cornelia^G^^^Mevr.'
        pid.date_time_of_birth = '19450817'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Spoorlaan 25', xad_3='Tilburg', xad_5='5038CB', xad_6='NLD', xad_7='H')
        pid.pid_13 = '^^PH^0134627100'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI HEM', pl_2='Hematologie', pl_3='1')
        pv1.pv1_7 = '70060^Timmermans^Jacobus^^^Prof.Dr.^arts'

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
        orc.placer_order_number = EI(ei_1='ORD2026006')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026006')
        obr.universal_service_identifier = CWE(cwe_1='LA11803-5', cwe_2='Coagulation panel', cwe_3='LN')
        obr.observation_date_time = '20260509120000'
        obr.results_rpt_status_chng_date_time = '20260509140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='Prothrombin time (PT)', cwe_3='LN')
        obx.obx_5 = '13.5'
        obx.units = CWE(cwe_1='s', cwe_2='s', cwe_3='UCUM')
        obx.reference_range = '11.0-15.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509133000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR in Platelet poor plasma by Coagulation assay', cwe_3='LN')
        obx_2.obx_5 = '1.1'
        obx_2.units = CWE(cwe_1='{INR}', cwe_2='{INR}', cwe_3='UCUM')
        obx_2.reference_range = '0.9-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509133000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='aPTT in Platelet poor plasma by Coagulation assay', cwe_3='LN')
        obx_3.obx_5 = '31'
        obx_3.units = CWE(cwe_1='s', cwe_2='s', cwe_3='UCUM')
        obx_3.reference_range = '25-38'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509133000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3255-7', cwe_2='Fibrinogen [Mass/volume] in Platelet poor plasma by Coagulation assay', cwe_3='LN')
        obx_4.obx_5 = '3.2'
        obx_4.units = CWE(cwe_1='g/L', cwe_2='g/L', cwe_3='UCUM')
        obx_4.reference_range = '2.0-4.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509133000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='3174-0', cwe_2='D-dimer DDU [Mass/volume] in Platelet poor plasma', cwe_3='LN')
        obx_5.obx_5 = '0.35'
        obx_5.units = CWE(cwe_1='mg/L', cwe_2='mg/L', cwe_3='UCUM')
        obx_5.reference_range = '<0.50'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509133000'

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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='UMCG_LAB')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='UMCG')
        msh.date_time_of_message = '20260509143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260509010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='912345678', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT007', cx_4='UMCG', cx_5='PI')]
        pid.pid_5 = 'Veenstra^Maria^K^^^Mevr.'
        pid.date_time_of_birth = '19620124'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Oosterstraat 22', xad_3='Groningen', xad_5='9711NR', xad_6='NLD', xad_7='H')
        pid.pid_13 = '^^PH^0503124567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI END', pl_2='Endocrinologie', pl_3='1')
        pv1.pv1_7 = '80070^Boersma^Adriaan^^^Prof.Dr.^arts'

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
        orc.placer_order_number = EI(ei_1='ORD2026007')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026007')
        obr.universal_service_identifier = CWE(cwe_1='55231-5', cwe_2='Thyroid panel - Serum or Plasma', cwe_3='LN')
        obr.observation_date_time = '20260509130000'
        obr.results_rpt_status_chng_date_time = '20260509143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='Thyrotropin [Units/volume] in Serum or Plasma', cwe_3='LN')
        obx.obx_5 = '2.8'
        obx.units = CWE(cwe_1='mU/L', cwe_2='mU/L', cwe_3='UCUM')
        obx.reference_range = '0.4-4.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509141000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3026-2', cwe_2='Thyroxine (T4) free [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.obx_5 = '15.2'
        obx_2.units = CWE(cwe_1='pmol/L', cwe_2='pmol/L', cwe_3='UCUM')
        obx_2.reference_range = '11.0-22.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509141000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='Triiodothyronine (T3) free [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_3.obx_5 = '4.8'
        obx_3.units = CWE(cwe_1='pmol/L', cwe_2='pmol/L', cwe_3='UCUM')
        obx_3.reference_range = '3.1-6.8'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509141000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='5385-0', cwe_2='Thyroid peroxidase Ab [Units/volume] in Serum', cwe_3='LN')
        obx_4.obx_5 = '12'
        obx_4.units = CWE(cwe_1='kU/L', cwe_2='kU/L', cwe_3='UCUM')
        obx_4.reference_range = '<34'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509141000'

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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='305')
        msh.sending_facility = HD(hd_1='OLVG_LAB')
        msh.receiving_application = HD(hd_1='912')
        msh.receiving_facility = HD(hd_1='RIVM_IDS')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='OUL', msg_2='R22', msg_3='OUL_R22')
        msh.message_control_id = 'MSG20260509011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.4.3.11.60.25.10.32', ei_2='Nictiz', ei_3='2.16.840.1.113883.2.4.3.11', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='481623957', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT008', cx_4='OLVG', cx_5='PI')]
        pid.pid_5 = 'Hendriks^Jan^R^^^Dhr.'
        pid.date_time_of_birth = '19880201'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Javastraat 100', xad_3='Amsterdam', xad_5='1094HG', xad_6='NLD', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='SEH', pl_2='Spoedeisende Hulp', pl_3='1')

        # .. build the VISIT group ..
        visit = OulR22Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OulR22Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_type = CWE(cwe_1='NAS', cwe_2='Nasopharyngeal swab', cwe_3='HL70487')
        spm.specimen_collection_date_time = DR(dr_1='20260509143000')
        spm.specimen_received_date_time = '20260509143500'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026008')
        obr.universal_service_identifier = CWE(cwe_1='94500-6', cwe_2='SARS-CoV-2 RNA NAA+probe Ql (Resp)', cwe_3='LN')
        obr.observation_date_time = '20260509143500'
        obr.results_rpt_status_chng_date_time = '20260509150000'
        obr.result_status = 'F'

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD2026008')
        orc.parent_order = EIP(eip_1='20260509150000')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(
            cwe_1='94500-6',
            cwe_2='SARS-CoV-2 (COVID-19) RNA [Presence] in Respiratory specimen by NAA with probe detection',
            cwe_3='LN',
        )
        obx.obx_5 = '260415000^Not detected^SCT'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509145500'

        # .. build the ORDER_DOCUMENT group ..
        order_document = OulR22OrderDocument()
        order_document.obx = obx

        # .. build the COMMON_ORDER group ..
        common_order = OulR22CommonOrder()
        common_order.orc = orc
        common_order.order_document = order_document

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Sneltest PCR methode, GeneXpert Xpress SARS-CoV-2. Detectielimiet 250 kopieën/mL.'

        # .. build the ORDER group ..
        order = OulR22Order()
        order.obr = obr
        order.common_order = common_order
        order.nte = nte

        # .. build the SPECIMEN group ..
        specimen = OulR22Specimen()
        specimen.spm = spm
        specimen.order = order

        # .. assemble the full message ..
        msg = OUL_R22()
        msg.msh = msh
        msg.patient = patient
        msg.specimen = specimen

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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='UMCU_LAB')
        msh.receiving_application = HD(hd_1='OSIRIS')
        msh.receiving_facility = HD(hd_1='RIVM')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260509012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='294817365', cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.pid_5 = 'Wolters^Hendrik^P^^^Dhr.'
        pid.date_time_of_birth = '19430512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Catharijnesingel 77', xad_3='Utrecht', xad_5='3511GE', xad_6='NLD', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IC', pl_2='Intensive Care', pl_3='Bed 5')
        pv1.pv1_7 = '90080^Scholten^Adriana^^^Dr.^arts'

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
        orc.placer_order_number = EI(ei_1='ORD2026009')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026009')
        obr.universal_service_identifier = CWE(cwe_1='20897-4', cwe_2='Legionella pneumophila Ag [Presence] in Urine', cwe_3='LN')
        obr.observation_date_time = '20260509140000'
        obr.results_rpt_status_chng_date_time = '20260509160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='20897-4', cwe_2='Legionella pneumophila Ag [Presence] in Urine', cwe_3='LN')
        obx.obx_5 = '260373001^Detected^SCT'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509155000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='8251-1', cwe_2='Service comment', cwe_3='LN')
        obx_2.obx_5 = 'Meldingsplichtig conform Wet publieke gezondheid groep B2. GGD en RIVM zijn geïnformeerd.'
        obx_2.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Bepaling uitgevoerd met BinaxNOW Legionella immunochromatografische assay.'

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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='MST_LAB')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='MST')
        msh.date_time_of_message = '20260509162000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260509013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='618273945', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT009', cx_4='MST', cx_5='PI')]
        pid.pid_5 = 'Dijkstra^Jacobus^N^^^Dhr.'
        pid.date_time_of_birth = '19580831'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Oldenzaalsestraat 55', xad_3='Enschede', xad_5='7511DV', xad_6='NLD', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IC', pl_2='Intensive Care', pl_3='Bed 2')
        pv1.pv1_7 = '11090^Mulder^Anneke^^^Dr.^arts'

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
        orc.placer_order_number = EI(ei_1='ORD2026010')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026010')
        obr.universal_service_identifier = CWE(cwe_1='24336-0', cwe_2='Gas panel - Arterial blood', cwe_3='LN')
        obr.observation_date_time = '20260509155000'
        obr.results_rpt_status_chng_date_time = '20260509162000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='pH of Arterial blood', cwe_3='LN')
        obx.obx_5 = '7.38'
        obx.reference_range = '7.35-7.45'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='Carbon dioxide [Partial pressure] in Arterial blood', cwe_3='LN')
        obx_2.obx_5 = '42'
        obx_2.units = CWE(cwe_1='mm[Hg]', cwe_2='mm[Hg]', cwe_3='UCUM')
        obx_2.reference_range = '35-45'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2703-7', cwe_2='Oxygen [Partial pressure] in Arterial blood', cwe_3='LN')
        obx_3.obx_5 = '88'
        obx_3.units = CWE(cwe_1='mm[Hg]', cwe_2='mm[Hg]', cwe_3='UCUM')
        obx_3.reference_range = '75-100'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1959-6', cwe_2='Bicarbonate [Moles/volume] in Arterial blood', cwe_3='LN')
        obx_4.obx_5 = '24.5'
        obx_4.units = CWE(cwe_1='mmol/L', cwe_2='mmol/L', cwe_3='UCUM')
        obx_4.reference_range = '22.0-26.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2708-6', cwe_2='Oxygen saturation in Arterial blood', cwe_3='LN')
        obx_5.obx_5 = '96'
        obx_5.units = CWE(cwe_1='%', cwe_2='%', cwe_3='UCUM')
        obx_5.reference_range = '95-100'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2714-4', cwe_2='Base excess in Arterial blood by calculation', cwe_3='LN')
        obx_6.obx_5 = '0.8'
        obx_6.units = CWE(cwe_1='mmol/L', cwe_2='mmol/L', cwe_3='UCUM')
        obx_6.reference_range = '-2.0-3.0'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='59274-1', cwe_2='Lactate [Moles/volume] in Arterial blood', cwe_3='LN')
        obx_7.obx_5 = '1.2'
        obx_7.units = CWE(cwe_1='mmol/L', cwe_2='mmol/L', cwe_3='UCUM')
        obx_7.reference_range = '0.5-2.2'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260509160000'

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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='AMPHIA_LAB')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='AMPHIA')
        msh.date_time_of_message = '20260509170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260509014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='537294816', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT010', cx_4='AMPHIA', cx_5='PI')]
        pid.pid_5 = 'Vermeulen^Elisabeth^C^^^Mevr.'
        pid.date_time_of_birth = '19750929'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Ginnekenweg 12', xad_3='Breda', xad_5='4835NA', xad_6='NLD', xad_7='H')
        pid.pid_13 = '^^PH^0765214389'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI NEF', pl_2='Nefrologie', pl_3='1')
        pv1.pv1_7 = '12100^Peters^Theodorus^^^Dr.^arts'

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
        orc.placer_order_number = EI(ei_1='ORD2026011')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026011')
        obr.universal_service_identifier = CWE(cwe_1='24356-8', cwe_2='Urinalysis complete panel in Urine', cwe_3='LN')
        obr.observation_date_time = '20260509153000'
        obr.results_rpt_status_chng_date_time = '20260509170000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2756-5', cwe_2='pH of Urine by Test strip', cwe_3='LN')
        obx.obx_5 = '6.0'
        obx.reference_range = '5.0-8.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509163000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='20454-5', cwe_2='Protein [Presence] in Urine by Test strip', cwe_3='LN')
        obx_2.obx_5 = 'Negatief'
        obx_2.reference_range = 'Negatief'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509163000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='25428-4', cwe_2='Glucose [Presence] in Urine by Test strip', cwe_3='LN')
        obx_3.obx_5 = 'Negatief'
        obx_3.reference_range = 'Negatief'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509163000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='30405-5', cwe_2='Leukocytes [#/area] in Urine sediment by Microscopy high power field', cwe_3='LN')
        obx_4.obx_5 = '3'
        obx_4.units = CWE(cwe_1='/[HPF]', cwe_2='/[HPF]', cwe_3='UCUM')
        obx_4.reference_range = '0-5'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509163000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='13945-1', cwe_2='Erythrocytes [#/area] in Urine sediment by Microscopy high power field', cwe_3='LN')
        obx_5.obx_5 = '1'
        obx_5.units = CWE(cwe_1='/[HPF]', cwe_2='/[HPF]', cwe_3='UCUM')
        obx_5.reference_range = '0-3'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509163000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='5811-5', cwe_2='Specific gravity of Urine by Test strip', cwe_3='LN')
        obx_6.obx_5 = '1.018'
        obx_6.reference_range = '1.005-1.030'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509163000'

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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='103')
        msh.sending_facility = HD(hd_1='MAASTRICHT_LAB')
        msh.receiving_application = HD(hd_1='202')
        msh.receiving_facility = HD(hd_1='ERASMUS_LAB')
        msh.date_time_of_message = '20260509171500'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'MSG20260509015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.4.3.11.60.25.10.31', ei_2='Nictiz', ei_3='2.16.840.1.113883.2.4.3.11', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='462918375', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT011', cx_4='MUMC', cx_5='PI')]
        pid.pid_5 = 'Claessen^Petrus^H^^^Dhr.'
        pid.date_time_of_birth = '19681104'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vrijthof 3', xad_3='Maastricht', xad_5='6211LE', xad_6='NLD', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5B', pl_2='Nefrologie', pl_3='Bed 6')
        pv1.pv1_7 = '13110^Gielen^Margaretha^^^Dr.^arts'

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
        orc.placer_order_number = EI(ei_1='ORD2026012')
        orc.orc_7 = '^^^20260509171500^^R'
        orc.date_time_of_order_event = '20260509171500'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026012')
        obr.universal_service_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obr.observation_date_time = '20260509165000'
        obr.specimen_action_code = 'A'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='29463-7', cwe_2='Body weight', cwe_3='LN')
        obx.obx_5 = '82.5'
        obx.units = CWE(cwe_1='kg', cwe_2='kg', cwe_3='UCUM')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OmlO21Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='8302-2', cwe_2='Body height', cwe_3='LN')
        obx_2.obx_5 = '178'
        obx_2.units = CWE(cwe_1='cm', cwe_2='cm', cwe_3='UCUM')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OmlO21Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='46239-0', cwe_2='Chief complaint', cwe_3='LN')
        obx_3.obx_5 = 'Controle nierfunctie, chronische nierinsufficiëntie stadium 3'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OmlO21Observation()
        observation_3.obx = obx_3

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_type = CWE(cwe_1='SER', cwe_2='Serum', cwe_3='HL70487')
        spm.specimen_collection_date_time = DR(dr_1='20260509165000')
        spm.specimen_received_date_time = '20260509165500'

        # .. build the SPECIMEN group ..
        specimen = OmlO21Specimen()
        specimen.spm = spm

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OmlO21ObservationRequest()
        observation_request.obr = obr
        observation_request.observation = observation
        observation_request.observation_2 = observation_2
        observation_request.observation_3 = observation_3
        observation_request.specimen = specimen

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc
        order.observation_request = observation_request

        # .. assemble the full message ..
        msg = OML_O21()
        msg.msh = msh
        msg.patient = patient
        msg.order = order

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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='CATHARINA_LAB')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='CATHARINA')
        msh.date_time_of_message = '20260509174500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260509016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='183746529', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT012', cx_4='CATHARINA', cx_5='PI')]
        pid.pid_5 = 'Willems^Johanna^B^^^Mevr.'
        pid.date_time_of_birth = '19550320'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Gestelsestraat 2', xad_3='Eindhoven', xad_5='5615LC', xad_6='NLD', xad_7='H')
        pid.pid_13 = '^^PH^0402389156'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI INT', pl_2='Interne Geneeskunde', pl_3='1')
        pv1.pv1_7 = '14120^van Oort^Paulus^^^Dr.^arts'

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
        orc.placer_order_number = EI(ei_1='ORD2026013')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026013')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobin A1c/Hemoglobin.total in Blood', cwe_3='LN')
        obr.observation_date_time = '20260509160000'
        obr.results_rpt_status_chng_date_time = '20260509174500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobin A1c/Hemoglobin.total in Blood', cwe_3='LN')
        obx.obx_5 = '52'
        obx.units = CWE(cwe_1='mmol/mol', cwe_2='mmol/mol', cwe_3='UCUM')
        obx.reference_range = '<53'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509172000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_2.obx_5 = '7.2'
        obx_2.units = CWE(cwe_1='mmol/L', cwe_2='mmol/L', cwe_3='UCUM')
        obx_2.reference_range = '3.1-6.1'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509172000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx_3.obx_5 = '95'
        obx_3.units = CWE(cwe_1='umol/L', cwe_2='umol/L', cwe_3='UCUM')
        obx_3.reference_range = '62-106'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509172000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(
            cwe_1='62238-1',
            cwe_2='Glomerular filtration rate/1.73 sq M.predicted [Volume Rate/Area] in Serum, Plasma or Blood by Creatinine-based formula (CKD-EPI 2021)',
            cwe_3='LN',
        )
        obx_4.obx_5 = '68'
        obx_4.units = CWE(cwe_1='mL/min/1.73m2', cwe_2='mL/min/1.73m2', cwe_3='UCUM')
        obx_4.reference_range = '>60'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509172000'

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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='UMCU_LAB')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='UMCU')
        msh.date_time_of_message = '20260509180000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260509017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='729461835', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT013', cx_4='UMCU', cx_5='PI')]
        pid.pid_5 = 'Brouwer^Adriaan^J^^^Dhr.'
        pid.date_time_of_birth = '19401212'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Heidelberglaan 100', xad_3='Utrecht', xad_5='3584CX', xad_6='NLD', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='2N', pl_2='Neurologie', pl_3='Bed 11')
        pv1.pv1_7 = '15130^ter Haar^Margaretha^^^Dr.^arts'

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
        orc.placer_order_number = EI(ei_1='ORD2026014')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026014')
        obr.universal_service_identifier = CWE(cwe_1='4090-7', cwe_2='Valproate [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obr.observation_date_time = '20260509163000'
        obr.results_rpt_status_chng_date_time = '20260509180000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4090-7', cwe_2='Valproate [Mass/volume] in Serum or Plasma', cwe_3='LN')
        obx.obx_5 = '72'
        obx.units = CWE(cwe_1='mg/L', cwe_2='mg/L', cwe_3='UCUM')
        obx.reference_range = '50-100'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509174500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='8251-1', cwe_2='Service comment', cwe_3='LN')
        obx_2.obx_5 = 'Dalconcentratie. Therapeutisch bereik valproïnezuur: 50-100 mg/L. Concentratie passend bij adequate dosering.'
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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='SANQUIN_LAB')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='AMC')
        msh.date_time_of_message = '20260509183000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260509018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='351849627', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT014', cx_4='AMC', cx_5='PI')]
        pid.pid_5 = 'van Dijk^Grietje^S^^^Mevr.'
        pid.date_time_of_birth = '19830714'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Meibergdreef 9', xad_3='Amsterdam', xad_5='1105AZ', xad_6='NLD', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3A', pl_2='Chirurgie', pl_3='Bed 4')
        pv1.pv1_7 = '16140^Jansen^Frederikus^^^Dr.^arts'

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
        orc.placer_order_number = EI(ei_1='ORD2026015')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026015')
        obr.universal_service_identifier = CWE(cwe_1='882-1', cwe_2='ABO and Rh group [Type] in Blood', cwe_3='LN')
        obr.observation_date_time = '20260509170000'
        obr.results_rpt_status_chng_date_time = '20260509183000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='883-9', cwe_2='ABO group [Type] in Blood', cwe_3='LN')
        obx.obx_5 = '278149003^Blood group A^SCT'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509180000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CWE'
        obx_2.observation_identifier = CWE(cwe_1='10331-7', cwe_2='Rh [Type] in Blood', cwe_3='LN')
        obx_2.obx_5 = '165747007^RhD positive^SCT'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509180000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CWE'
        obx_3.observation_identifier = CWE(cwe_1='1250-0', cwe_2='Direct antiglobulin test.IgG specific reagent [Interpretation] in Blood', cwe_3='LN')
        obx_3.obx_5 = '260385009^Negative^SCT'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509181000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='890-4', cwe_2='Ab screen [Presence] in Serum or Plasma', cwe_3='LN')
        obx_4.obx_5 = 'Negatief'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509181500'

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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='RADBOUD_LAB')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='RADBOUDUMC')
        msh.date_time_of_message = '20260509190000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260509019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='842916375', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT015', cx_4='RADBOUD', cx_5='PI')]
        pid.pid_5 = 'Hermsen^Gerardus^T^^^Dhr.'
        pid.date_time_of_birth = '19470305'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Geert Grooteplein 10', xad_3='Nijmegen', xad_5='6525GA', xad_6='NLD', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6B', pl_2='Oncologie', pl_3='Bed 7')
        pv1.pv1_7 = '17150^van den Broek^Suzanne^^^Prof.Dr.^arts'

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
        orc.placer_order_number = EI(ei_1='ORD2026016')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026016')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel - Blood by Automated count', cwe_3='LN')
        obr.observation_date_time = '20260509173000'
        obr.results_rpt_status_chng_date_time = '20260509190000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin [Mass/volume] in Blood', cwe_3='LN')
        obx.obx_5 = '6.1'
        obx.units = CWE(cwe_1='mmol/L', cwe_2='mmol/L', cwe_3='UCUM')
        obx.reference_range = '7.5-10.0'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509183000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocytes [#/volume] in Blood by Automated count', cwe_3='LN')
        obx_2.obx_5 = '2.1'
        obx_2.units = CWE(cwe_1='10*9/L', cwe_2='10*9/L', cwe_3='UCUM')
        obx_2.reference_range = '4.0-10.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509183000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='26515-7', cwe_2='Platelets [#/volume] in Blood by Automated count', cwe_3='LN')
        obx_3.obx_5 = '89'
        obx_3.units = CWE(cwe_1='10*9/L', cwe_2='10*9/L', cwe_3='UCUM')
        obx_3.reference_range = '150-400'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509183000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ED'
        obx_4.observation_identifier = CWE(cwe_1='PDF', cwe_2='Display format in PDF', cwe_3='AUSPDI')
        obx_4.obx_5 = (
            'GLIMS^Application^PDF^Base64^'
            'JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0Nv'
            'dW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8'
            'PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAxMTMgPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxMDAgNzAwIFRkCihSYWRib3VkdW1j'
            'IExhYm9yYXRvcml1bSkgVGoKMTAwIDY4MCBUZAooQ3VtdWxhdGlldiBMYWJvdmVyemljaHQpIFRqCjEwMCA2NjAgVGQKKFBhdGllbnQ6IFdpbGxlbXMsIEcuSC4pIFRqCkVUCmVuZHN0'
            'cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1'
            'MzUgZiAKMDAwMDAwMDAxNSAwMDAwMCBuIAowMDAwMDAwMDY2IDAwMDAwIG4gCjAwMDAwMDAxMjUgMDAwMDAgbiAKMDAwMDAwMDMwMiAwMDAwMCBuIAowMDAwMDAwNDY3IDAwMDAwIG4g'
            'CnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNTU2CiUlRU9GCg=='
        )
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
    """ Based on live/nl/nl-clinisys-glims.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='LUMC_PATHOLOGIE')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='LUMC')
        msh.date_time_of_message = '20260509193000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260509020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='275839164', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='PAT016', cx_4='LUMC', cx_5='PI')]
        pid.pid_5 = 'de Groot^Wilhelmina^A^^^Mevr.'
        pid.date_time_of_birth = '19580611'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rapenburg 2', xad_3='Leiden', xad_5='2311EW', xad_6='NLD', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4C', pl_2='Pathologie', pl_3='Bed 2')
        pv1.pv1_7 = '18160^Vos^Cornelis^^^Prof.Dr.^arts'

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
        orc.placer_order_number = EI(ei_1='ORD2026017')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026017')
        obr.universal_service_identifier = CWE(cwe_1='33717-0', cwe_2='Pathology study', cwe_3='LN')
        obr.observation_date_time = '20260508100000'
        obr.results_rpt_status_chng_date_time = '20260509193000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Pathology report final diagnosis', cwe_3='LN')
        obx.obx_5 = (
            'Colonbiopt: adenocarcinoom, matig gedifferentieerd (G2), invasie in submucosa.\\.br\\Resectievlakken vrij. Lymfangioinvasie afwezig.\\.br\\Concl'
            'usie: pT1 NX MX coloncarcinoom.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509190000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMGHL7', cwe_2='Histopathology image', cwe_3='L')
        obx_2.obx_5 = (
            'LUMC_PATHOLOGIE^Image^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM DQ4SEA0OEQ4LCxAWEBETFBUVFQwPFxgWFBgSFBX/2wBDAQMEBAUEBQkFBQk'
            'VDQsNFRUVFRUVFRUV FQUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRX/wAARCAAoACgDASIAAhEBAxEB/8QA HwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/'
            '8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQR BRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdI SUpTVFVWV1hZWmNkZWZnaGlqc3R'
            '1dnd4eXp/xAAfAQADAQEBAQEBAQEBAAAAAAAAAQIDBAUGBwgJ Cgv/xAC1EQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVi ctEKFiQ04SXxF'
            'xgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqC g4SFhoeIiYqSk5SVlpeYmZqio6SlpqeoqaqyS7O0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk'
            ' 5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD7yooooAKKKKACiiigD//Z'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509191500'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Microscoopfoto HE-kleuring 40x vergroting, colonbiopt S2026-12345.'

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
