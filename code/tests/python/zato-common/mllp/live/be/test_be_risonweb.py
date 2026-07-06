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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A03, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import AL1, DG1, EVN, IN1, MSH, NK1, OBR, OBX, ORC, PID, PRT, PV1
from zato.hl7v2.z_segments import ZDS

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('be', 'be-risonweb.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/be/be-risonweb.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='UZ_BRUSSEL')
        msh.receiving_application = HD(hd_1='PACS_BE')
        msh.receiving_facility = HD(hd_1='UZ_BRUSSEL')
        msh.date_time_of_message = '20260509083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT55932', cx_4='UZB', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Van Damme', xpn_2='Pieter', xpn_3='L', xpn_5='Dhr.')
        pid.date_time_of_birth = '19780312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vlaamsesteenweg 42', xad_3='Brussel', xad_5='1000', xad_6='BE')
        pid.pid_13 = '^^PH^02-512-7834'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='CT-1', pl_3='1', pl_4='Radiologie')
        pv1.attending_doctor = XCN(xcn_1='21345678012', xcn_2='Van Acker', xcn_3='Kristof', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')

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
        orc.placer_order_number = EI(ei_1='ORD88432', ei_2='RISONWEB')
        orc.filler_order_number = EI(ei_1='FIL99321', ei_2='PACS_BE')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20260509083000^^R'
        orc.date_time_of_order_event = '20260509083000'
        orc.orc_10 = '21345678012^Van Acker^Kristof^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD88432', ei_2='RISONWEB')
        obr.filler_order_number = EI(ei_1='FIL99321', ei_2='PACS_BE')
        obr.universal_service_identifier = CWE(cwe_1='70486', cwe_2='CT SINUS ZONDER CONTRAST', cwe_3='CPT4')
        obr.obr_5 = 'R'
        obr.obr_6 = '20260509080000'
        obr.relevant_clinical_information = CWE(cwe_1='21345678012', cwe_2='Van Acker', cwe_3='Kristof', cwe_6='Dr.')
        obr.placer_field_2 = 'CT'
        obr.filler_field_1 = 'SC'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build ZDS ..
        zds = ZDS()
        zds.zds_1 = '1.2.840.113619.2.55.3.604688119.968.2345678901.223^RISONWEB^APPLICATION^DICOM'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [zds]

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
    """ Based on live/be/be-risonweb.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='AZ_SINT_JAN')
        msh.receiving_application = HD(hd_1='PACS_BE')
        msh.receiving_facility = HD(hd_1='AZ_SINT_JAN')
        msh.date_time_of_message = '20260509091500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT66213', cx_4='AZSJ', cx_5='PI')
        pid.patient_name = XPN(xpn_1='De Smedt', xpn_2='Inge', xpn_3='A', xpn_5='Mevr.')
        pid.date_time_of_birth = '19710721'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tiensestraat 87', xad_3='Leuven', xad_5='3000', xad_6='BE')
        pid.pid_13 = '^^PH^016-224589'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PULMO', pl_2='Kamer 302', pl_3='Bed 1', pl_4='Longziekten')
        pv1.attending_doctor = XCN(xcn_1='21456789023', xcn_2='De Backer', xcn_3='Filip', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')

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
        orc.placer_order_number = EI(ei_1='ORD77201', ei_2='RISONWEB')
        orc.filler_order_number = EI(ei_1='FIL88102', ei_2='PACS_BE')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20260509091500^^R'
        orc.date_time_of_order_event = '20260509091500'
        orc.orc_10 = '21456789023^De Backer^Filip^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD77201', ei_2='RISONWEB')
        obr.filler_order_number = EI(ei_1='FIL88102', ei_2='PACS_BE')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='RX THORAX AP EN LATERAAL', cwe_3='CPT4')
        obr.obr_5 = 'R'
        obr.obr_6 = '20260509090000'
        obr.relevant_clinical_information = CWE(cwe_1='21456789023', cwe_2='De Backer', cwe_3='Filip', cwe_6='Dr.')
        obr.placer_field_2 = 'CR'
        obr.filler_field_1 = 'SC'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build ZDS ..
        zds = ZDS()
        zds.zds_1 = '1.2.840.113619.2.55.3.604688119.968.3456789012.334^RISONWEB^APPLICATION^DICOM'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [zds]

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
    """ Based on live/be/be-risonweb.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='AZ_SINT_JAN')
        msh.receiving_application = HD(hd_1='HIS_BE')
        msh.receiving_facility = HD(hd_1='AZ_SINT_JAN')
        msh.date_time_of_message = '20260509141200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT66213', cx_4='AZSJ', cx_5='PI')
        pid.patient_name = XPN(xpn_1='De Smedt', xpn_2='Inge', xpn_3='A', xpn_5='Mevr.')
        pid.date_time_of_birth = '19710721'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tiensestraat 87', xad_3='Leuven', xad_5='3000', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PULMO', pl_2='Kamer 302', pl_3='Bed 1', pl_4='Longziekten')
        pv1.attending_doctor = XCN(xcn_1='21456789023', xcn_2='De Backer', xcn_3='Filip', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')

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
        orc.placer_order_number = EI(ei_1='ORD77201', ei_2='RISONWEB')
        orc.filler_order_number = EI(ei_1='FIL88102', ei_2='PACS_BE')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20260509091500^^R'
        orc.date_time_of_order_event = '20260509141200'
        orc.orc_10 = '21456789023^De Backer^Filip^^^Dr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD77201', ei_2='RISONWEB')
        obr.filler_order_number = EI(ei_1='FIL88102', ei_2='PACS_BE')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='RX THORAX AP EN LATERAAL', cwe_3='CPT4')
        obr.obr_16 = '21567890034^Timmermans^Hilde^^^Dr.'
        obr.results_rpt_status_chng_date_time = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='&GDT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'Thoraxfoto AP en lateraal. Geen focale consolidaties. Normale hartschaduw. Geen pleuravocht.'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='&IMP')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'Normaal thoraxonderzoek, geen bijzonderheden.'
        obx_2.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/be/be-risonweb.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='CHU_LIEGE')
        msh.receiving_application = HD(hd_1='DMP_BE')
        msh.receiving_facility = HD(hd_1='EHEALTH_BE')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT77312', cx_4='CHUL', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Mertens', xpn_2='Wim', xpn_3='F', xpn_5='Dhr.')
        pid.date_time_of_birth = '19840114'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Quai de Rome 33', xad_3='Liege', xad_5='4000', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='IRM-2', pl_3='1', pl_4='Radiologie')
        pv1.attending_doctor = XCN(xcn_1='21678901045', xcn_2='Lejeune', xcn_3='Antoine', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')

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
        orc.placer_order_number = EI(ei_1='ORD99301', ei_2='RISONWEB')
        orc.filler_order_number = EI(ei_1='FIL00201', ei_2='PACS_BE')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD99301', ei_2='RISONWEB')
        obr.filler_order_number = EI(ei_1='FIL00201', ei_2='PACS_BE')
        obr.universal_service_identifier = CWE(cwe_1='18748-4', cwe_2="CR d'imagerie medicale", cwe_3='LN')
        obr.obr_16 = '21678901045^Lejeune^Antoine^^^Dr.'
        obr.results_rpt_status_chng_date_time = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2="CR d'imagerie medicale", cwe_3='LN')
        obx.obx_5 = (
            '^TEXT^XML^Base64^'
            'PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIiB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIj48dGl0bGU+Q29t'
            'cHRlIHJlbmR1IGQnaW1hZ2VyaWUgbWVkaWNhbGU8L3RpdGxlPjwvQ2xpbmljYWxEb2N1bWVudD4='
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='MASQUE_PS', cwe_2='Masque aux professionnels de Sante', cwe_3='MetaDMPMSS')
        obx_2.obx_5 = 'N^^expandedYes-NoIndicator'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='INVISIBLE_PATIENT', cwe_2='Document Non Visible par le patient', cwe_3='MetaDMPMSS')
        obx_3.obx_5 = 'N^^expandedYes-NoIndicator'
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
    """ Based on live/be/be-risonweb.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='UZ_GENT')
        msh.receiving_application = HD(hd_1='HIS_BE')
        msh.receiving_facility = HD(hd_1='UZ_GENT')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT88413', cx_4='UZG', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Michiels', xpn_2='Eline', xpn_3='J', xpn_5='Mevr.')
        pid.date_time_of_birth = '19920605'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Vrijdagmarkt 14', xad_3='Gent', xad_5='9000', xad_6='BE')
        pid.pid_13 = '^^PH^09-267-4521'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='CT-2', pl_3='1', pl_4='Radiologie')
        pv1.attending_doctor = XCN(xcn_1='21789012056', xcn_2='Desmet', xcn_3='Bart', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')

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
        orc.placer_order_number = EI(ei_1='ORD11401', ei_2='RISONWEB')
        orc.filler_order_number = EI(ei_1='FIL22301', ei_2='PACS_BE')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD11401', ei_2='RISONWEB')
        obr.filler_order_number = EI(ei_1='FIL22301', ei_2='PACS_BE')
        obr.universal_service_identifier = CWE(cwe_1='74150', cwe_2='CT ABDOMEN ZONDER CONTRAST', cwe_3='CPT4')
        obr.obr_16 = '21789012056^Desmet^Bart^^^Dr.'
        obr.results_rpt_status_chng_date_time = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='859776-5', cwe_2='Procedure Findings', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'Lever, milt en nieren normaal van grootte en aspect. Geen vrij vocht. Geen lymfadenopathie.'
        obx.interpretation_codes = CWE(cwe_1='N', cwe_2='Normaal', cwe_3='HL70078')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='859776-5', cwe_2='Procedure Findings', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'Kleine cyste rechternier (12mm), klinisch niet significant.'
        obx_2.interpretation_codes = CWE(cwe_1='N', cwe_2='Normaal', cwe_3='HL70078')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='&IMP')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = 'Normaal CT abdomen. Kleine eenvoudige niercyste rechts, geen verdere opvolging nodig.'
        obx_3.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/be/be-risonweb.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='AZ_DELTA')
        msh.receiving_application = HD(hd_1='HIS_BE')
        msh.receiving_facility = HD(hd_1='AZ_DELTA')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04')
        msh.message_control_id = 'MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260509100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT99512', cx_4='AZD', cx_5='PI')
        pid.pid_4 = '92040523178^^^^NN'
        pid.patient_name = XPN(xpn_1='Baert', xpn_2='Koen', xpn_3='M', xpn_5='Dhr.')
        pid.date_time_of_birth = '19920405'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Meensesteenweg 7', xad_3='Roeselare', xad_5='8800', xad_6='BE')
        pid.pid_13 = '^^PH^051-263748'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Baert', xpn_2='Griet', xpn_3='V')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.start_date = '20260509'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='RX-1', pl_3='1', pl_4='Radiologie')
        pv1.attending_doctor = XCN(xcn_1='21890123067', xcn_2='Martens', xcn_3='Eva', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_code_mnemonic_description = CWE(cwe_2='JODIUMHOUDEND CONTRASTMIDDEL')
        al1.allergy_reaction_code = ['URTICARIA', 'NAUSEA']

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.al1 = al1

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
    """ Based on live/be/be-risonweb.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='UZ_ANTWERPEN')
        msh.receiving_application = HD(hd_1='HIS_BE')
        msh.receiving_facility = HD(hd_1='UZ_ANTWERPEN')
        msh.date_time_of_message = '20260509073000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509073000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT00612', cx_4='UZA', cx_5='PI')
        pid.pid_4 = '86071234589^^^^NN'
        pid.patient_name = XPN(xpn_1='Lenaerts', xpn_2='Annelies', xpn_3='T', xpn_5='Mevr.')
        pid.date_time_of_birth = '19860712'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Mechelsesteenweg 55', xad_3='Antwerpen', xad_5='2000', xad_6='BE')
        pid.pid_13 = '^^PH^03-231-8945~^^CP^0476-589321'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='Kamer 201', pl_3='Bed 1', pl_4='Interventionele Radiologie')
        pv1.pv1_7 = '21901234078^Peeters^Luc^^^Dr.^med.'
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='OPNAME20260509')
        pv1.account_status = CWE(cwe_1='RAD', cwe_2='Kamer 201', cwe_3='Bed 1', cwe_4='Interventionele Radiologie')
        pv1.prior_temporary_location = PL(pl_1='20260509073000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='MUT002')
        in1.insurance_company_name = XON(xon_1='SOCIALISTISCHE MUTUALITEIT')
        in1.insurance_company_address = XAD(xad_1='Lambermontlaan 100', xad_3='Brussel', xad_5='1030', xad_6='BE')
        in1.insureds_id_number = CX(cx_1='56')

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
    """ Based on live/be/be-risonweb.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='AZ_KLINA')
        msh.receiving_application = HD(hd_1='PACS_BE')
        msh.receiving_facility = HD(hd_1='AZ_KLINA')
        msh.date_time_of_message = '20260509113000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT21712', cx_4='AZKL', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Wouters', xpn_2='Bram', xpn_3='E', xpn_5='Dhr.')
        pid.date_time_of_birth = '19800923'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bredabaan 33', xad_3='Brasschaat', xad_5='2930', xad_6='BE')
        pid.pid_13 = '^^PH^03-652-1847'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NEURO', pl_2='Consult-2', pl_3='1', pl_4='Neurologie')
        pv1.attending_doctor = XCN(xcn_1='22012345089', xcn_2='Jacobs', xcn_3='Karen', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')

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
        orc.placer_order_number = EI(ei_1='ORD22501', ei_2='RISONWEB')
        orc.filler_order_number = EI(ei_1='FIL33401', ei_2='PACS_BE')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20260509113000^^R'
        orc.date_time_of_order_event = '20260509113000'
        orc.orc_10 = '22012345089^Jacobs^Karen^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD22501', ei_2='RISONWEB')
        obr.filler_order_number = EI(ei_1='FIL33401', ei_2='PACS_BE')
        obr.universal_service_identifier = CWE(cwe_1='70553', cwe_2='MRI HERSENEN MET CONTRAST', cwe_3='CPT4')
        obr.obr_5 = 'R'
        obr.obr_6 = '20260509110000'
        obr.relevant_clinical_information = CWE(cwe_1='22012345089', cwe_2='Jacobs', cwe_3='Karen', cwe_6='Dr.')
        obr.obr_16 = 'Hoofdpijn, vermoeden MS'
        obr.placer_field_1 = 'MR'
        obr.placer_field_2 = 'SC'
        obr.result_status = '22012345089^Jacobs^Karen^^^Dr.'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='G35', cwe_2='Multiple sclerose', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20260509'

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
    """ Based on live/be/be-risonweb.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='AZ_KLINA')
        msh.receiving_application = HD(hd_1='HIS_BE')
        msh.receiving_facility = HD(hd_1='AZ_KLINA')
        msh.date_time_of_message = '20260509163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT21712', cx_4='AZKL', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Wouters', xpn_2='Bram', xpn_3='E', xpn_5='Dhr.')
        pid.date_time_of_birth = '19800923'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bredabaan 33', xad_3='Brasschaat', xad_5='2930', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NEURO', pl_2='Consult-2', pl_3='1', pl_4='Neurologie')
        pv1.attending_doctor = XCN(xcn_1='22012345089', xcn_2='Jacobs', xcn_3='Karen', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')

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
        orc.placer_order_number = EI(ei_1='ORD22501', ei_2='RISONWEB')
        orc.filler_order_number = EI(ei_1='FIL33401', ei_2='PACS_BE')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD22501', ei_2='RISONWEB')
        obr.filler_order_number = EI(ei_1='FIL33401', ei_2='PACS_BE')
        obr.universal_service_identifier = CWE(cwe_1='70553', cwe_2='MRI HERSENEN MET CONTRAST', cwe_3='CPT4')
        obr.obr_16 = '22123456090^Vandenberghe^Elke^^^Dr.'
        obr.results_rpt_status_chng_date_time = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='859776-5', cwe_2='Procedure Findings', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'Meerdere periventriculaire en juxtacorticale T2-hyperintense witte stof laesies, wisselend van grootte (3-12mm). Enkele infratentoriele laes'
            'ies in de pons.'
        )
        obx.interpretation_codes = CWE(cwe_1='A', cwe_2='Abnormaal', cwe_3='HL70078')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='859776-5', cwe_2='Procedure Findings', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'Na contrasttoediening aankleuring van twee periventriculaire laesies, suggestief voor actieve demyelinisatie.'
        obx_2.interpretation_codes = CWE(cwe_1='A', cwe_2='Abnormaal', cwe_3='HL70078')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='&IMP')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = 'Beeld verenigbaar met multipele sclerose volgens McDonald-criteria. Actieve en niet-actieve laesies aanwezig.'
        obx_3.interpretation_codes = CWE(cwe_1='A')
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
    """ Based on live/be/be-risonweb.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='CHR_NAMUR')
        msh.receiving_application = HD(hd_1='DMP_BE')
        msh.receiving_facility = HD(hd_1='EHEALTH_BE')
        msh.date_time_of_message = '20260509170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT32812', cx_4='CHRN', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Renard', xpn_2='Isabelle', xpn_3='C', xpn_5='Mevr.')
        pid.date_time_of_birth = '19890310'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rue de Fer 15', xad_3='Namur', xad_5='5000', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='ECHO-1', pl_3='1', pl_4='Radiologie')
        pv1.attending_doctor = XCN(xcn_1='22234567001', xcn_2='Dupont', xcn_3='Francois', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')

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
        orc.placer_order_number = EI(ei_1='ORD33601', ei_2='RISONWEB')
        orc.filler_order_number = EI(ei_1='FIL44501', ei_2='PACS_BE')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD33601', ei_2='RISONWEB')
        obr.filler_order_number = EI(ei_1='FIL44501', ei_2='PACS_BE')
        obr.universal_service_identifier = CWE(cwe_1='18748-4', cwe_2="CR d'imagerie medicale", cwe_3='LN')
        obr.obr_16 = '22234567001^Dupont^Francois^^^Dr.'
        obr.results_rpt_status_chng_date_time = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2="CR d'imagerie medicale", cwe_3='LN')
        obx.obx_5 = (
            '^TEXT^XML^Base64^'
            'PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj48dGl0bGU+RWNob2dyYXBoaWUgYWJkb21pbmFsZTwvdGl0bGU+PGNvbXBvbmVudD48c2VjdGlvbj48dGV4dD5G'
            'b2llIG5vcm1hbCwgcGFzIGRlIGxpdGhpYXNlIGJpbGlhaXJlPC90ZXh0Pjwvc2VjdGlvbj48L2NvbXBvbmVudD48L0NsaW5pY2FsRG9jdW1lbnQ+'
        )
        obx.observation_result_status = 'F'

        # .. build PRT ..
        prt = PRT()
        prt.action_code = 'UC'
        prt.role_of_participation = CWE(cwe_1='SB', cwe_2='Send by', cwe_3='participation')
        prt.person = XCN(xcn_1='22234567001', xcn_2='Dupont', xcn_3='Francois', xcn_9='NIHDI&2.16.840.1.113883.3.6777.5.2&ISO', xcn_10='D', xcn_13='NIHDI')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx
        observation.prt = prt

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='MASQUE_PS', cwe_2='Masque aux professionnels de Sante', cwe_3='MetaDMPMSS')
        obx_2.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='INVISIBLE_PATIENT', cwe_2='Document Non Visible par le patient', cwe_3='MetaDMPMSS')
        obx_3.obx_5 = 'N^^expandedYes-NoIndicator'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='DESTDMP', cwe_2='Destinataire DMP', cwe_3='MetaDMPMSS')
        obx_4.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CE'
        obx_5.observation_identifier = CWE(cwe_1='DESTMSSANTEPS', cwe_2='Destinataire PS', cwe_3='MetaDMPMSS')
        obx_5.obx_5 = 'N^^expandedYes-NoIndicator'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'CE'
        obx_6.observation_identifier = CWE(cwe_1='DESTMSSANTEPAT', cwe_2='Destinataire Patient', cwe_3='MetaDMPMSS')
        obx_6.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ED'
        obx_7.observation_identifier = CWE(cwe_1='CORPSMAIL_PATIENT', cwe_2='Corps du mail pour le patient', cwe_3='MetaDMPMSS')
        obx_7.obx_5 = '^TEXT^^Base64^Qm9uam91ciBNbWUgRHVtb250LCB2b3VzIHRyb3V2ZXJleiBjaS1qb2ludCB2b3RyZSBjb21wdGUgcmVuZHUgZCdlY2hvZ3JhcGhpZS4='
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
    """ Based on live/be/be-risonweb.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='AZ_GROENINGE')
        msh.receiving_application = HD(hd_1='PACS_BE')
        msh.receiving_facility = HD(hd_1='AZ_GROENINGE')
        msh.date_time_of_message = '20260509080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT43912', cx_4='AZG', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Maes', xpn_2='Ruben', xpn_3='D', xpn_5='Dhr.')
        pid.date_time_of_birth = '19640418'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Doorniksesteenweg 112', xad_3='Kortrijk', xad_5='8500', xad_6='BE')
        pid.pid_13 = '^^PH^056-218734'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='ECHO-2', pl_3='1', pl_4='Radiologie')
        pv1.attending_doctor = XCN(xcn_1='22345678012', xcn_2='Pauwels', xcn_3='Inge', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')

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
        orc.placer_order_number = EI(ei_1='ORD44701', ei_2='RISONWEB')
        orc.filler_order_number = EI(ei_1='FIL55601', ei_2='PACS_BE')
        orc.order_status = 'SC'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD44701', ei_2='RISONWEB')
        obr.filler_order_number = EI(ei_1='FIL55601', ei_2='PACS_BE')
        obr.universal_service_identifier = CWE(cwe_1='76700', cwe_2='ECHOGRAFIE ABDOMEN VOLLEDIG', cwe_3='CPT4')
        obr.obr_5 = 'R'
        obr.obr_6 = '20260509075000'
        obr.relevant_clinical_information = CWE(cwe_1='22345678012', cwe_2='Pauwels', cwe_3='Inge', cwe_6='Dr.')
        obr.obr_16 = 'Abdominale pijn rechts boven, vermoeden cholelithiasis'
        obr.placer_field_1 = 'US'
        obr.placer_field_2 = 'SC'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.2', cwe_2='Cholelithiasis', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20260509'

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
    """ Based on live/be/be-risonweb.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='AZ_GROENINGE')
        msh.receiving_application = HD(hd_1='HIS_BE')
        msh.receiving_facility = HD(hd_1='AZ_GROENINGE')
        msh.date_time_of_message = '20260509143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT43912', cx_4='AZG', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Maes', xpn_2='Ruben', xpn_3='D', xpn_5='Dhr.')
        pid.date_time_of_birth = '19640418'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Doorniksesteenweg 112', xad_3='Kortrijk', xad_5='8500', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='ECHO-2', pl_3='1', pl_4='Radiologie')
        pv1.attending_doctor = XCN(xcn_1='22345678012', xcn_2='Pauwels', xcn_3='Inge', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')

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
        orc.placer_order_number = EI(ei_1='ORD44701', ei_2='RISONWEB')
        orc.filler_order_number = EI(ei_1='FIL55601', ei_2='PACS_BE')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD44701', ei_2='RISONWEB')
        obr.filler_order_number = EI(ei_1='FIL55601', ei_2='PACS_BE')
        obr.universal_service_identifier = CWE(cwe_1='76700', cwe_2='ECHOGRAFIE ABDOMEN VOLLEDIG', cwe_3='CPT4')
        obr.obr_16 = '22456789023^Simon^Benoit^^^Dr.'
        obr.results_rpt_status_chng_date_time = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='&GDT')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'Lever normaal van grootte en echostructuur. Galblaas bevat meerdere echorijke structuren met slagschaduw, diameter grootste steen 14mm.'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='&GDT')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = 'Galwegen niet verwijd. Pancreas normaal. Milt en nieren zonder bijzonderheden.'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='&IMP')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = 'Cholelithiasis met meerdere galstenen. Geen cholecystitis. Verder normaal echografisch abdomenonderzoek.'
        obx_3.interpretation_codes = CWE(cwe_1='A')
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
    """ Based on live/be/be-risonweb.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='UZ_BRUSSEL')
        msh.receiving_application = HD(hd_1='PACS_BE')
        msh.receiving_facility = HD(hd_1='UZ_BRUSSEL')
        msh.date_time_of_message = '20260509111500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT55932', cx_4='UZB', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Van Damme', xpn_2='Pieter', xpn_3='L', xpn_5='Dhr.')
        pid.date_time_of_birth = '19780312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vlaamsesteenweg 42', xad_3='Brussel', xad_5='1000', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='CT-1', pl_3='1', pl_4='Radiologie')
        pv1.attending_doctor = XCN(xcn_1='21345678012', xcn_2='Van Acker', xcn_3='Kristof', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'CA'
        orc.placer_order_number = EI(ei_1='ORD88432', ei_2='RISONWEB')
        orc.filler_order_number = EI(ei_1='FIL99321', ei_2='PACS_BE')
        orc.order_status = 'CA'
        orc.orc_7 = '^^^20260509111500'
        orc.date_time_of_order_event = '20260509111500'
        orc.orc_10 = '21345678012^Van Acker^Kristof^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD88432', ei_2='RISONWEB')
        obr.filler_order_number = EI(ei_1='FIL99321', ei_2='PACS_BE')
        obr.universal_service_identifier = CWE(cwe_1='70486', cwe_2='CT SINUS ZONDER CONTRAST', cwe_3='CPT4')
        obr.obr_5 = 'R'
        obr.obr_6 = '20260509080000'
        obr.relevant_clinical_information = CWE(cwe_1='21345678012', cwe_2='Van Acker', cwe_3='Kristof', cwe_6='Dr.')
        obr.placer_field_2 = 'CT'
        obr.filler_field_1 = 'CA'

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
    """ Based on live/be/be-risonweb.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='AZ_DELTA')
        msh.receiving_application = HD(hd_1='HIS_BE')
        msh.receiving_facility = HD(hd_1='AZ_DELTA')
        msh.date_time_of_message = '20260509123000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260509123000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT99512', cx_4='AZD', cx_5='PI')
        pid.pid_4 = '92040523178^^^^NN'
        pid.patient_name = XPN(xpn_1='Baert-Verbeke', xpn_2='Koen', xpn_3='M', xpn_5='Dhr.')
        pid.date_time_of_birth = '19920405'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Marktplein 7', xad_3='Roeselare', xad_5='8800', xad_6='BE')
        pid.pid_13 = '^^PH^051-263748~^^CP^0479-341256~^^Internet^koen.baert@telenet.be'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='RX-1', pl_3='1', pl_4='Radiologie')
        pv1.attending_doctor = XCN(xcn_1='21890123067', xcn_2='Martens', xcn_3='Eva', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/be/be-risonweb.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='AZ_MARIA')
        msh.receiving_application = HD(hd_1='PACS_BE')
        msh.receiving_facility = HD(hd_1='AZ_MARIA')
        msh.date_time_of_message = '20260509090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT54012', cx_4='AZM', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Coppens', xpn_2='Vera', xpn_3='H', xpn_5='Mevr.')
        pid.date_time_of_birth = '19730815'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Thonissenlaan 8', xad_3='Hasselt', xad_5='3500', xad_6='BE')
        pid.pid_13 = '^^PH^011-423567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='MAMMO-1', pl_3='1', pl_4='Radiologie')
        pv1.attending_doctor = XCN(xcn_1='22567890034', xcn_2='Claes', xcn_3='Katrien', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')

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
        orc.placer_order_number = EI(ei_1='ORD55801', ei_2='RISONWEB')
        orc.filler_order_number = EI(ei_1='FIL66701', ei_2='PACS_BE')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509090000'
        orc.orc_10 = '22567890034^Claes^Katrien^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD55801', ei_2='RISONWEB')
        obr.filler_order_number = EI(ei_1='FIL66701', ei_2='PACS_BE')
        obr.universal_service_identifier = CWE(cwe_1='77067', cwe_2='MAMMOGRAFIE BILATERAAL SCREENING', cwe_3='CPT4')
        obr.obr_5 = 'R'
        obr.obr_6 = '20260509085000'
        obr.relevant_clinical_information = CWE(cwe_1='22567890034', cwe_2='Claes', cwe_3='Katrien', cwe_6='Dr.')
        obr.obr_16 = 'Borstkankerscreening, leeftijd >50'
        obr.placer_field_1 = 'MG'
        obr.placer_field_2 = 'SC'

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
    """ Based on live/be/be-risonweb.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='AZ_MARIA')
        msh.receiving_application = HD(hd_1='HIS_BE')
        msh.receiving_facility = HD(hd_1='AZ_MARIA')
        msh.date_time_of_message = '20260509153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT54012', cx_4='AZM', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Coppens', xpn_2='Vera', xpn_3='H', xpn_5='Mevr.')
        pid.date_time_of_birth = '19730815'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Thonissenlaan 8', xad_3='Hasselt', xad_5='3500', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='MAMMO-1', pl_3='1', pl_4='Radiologie')
        pv1.attending_doctor = XCN(xcn_1='22567890034', xcn_2='Claes', xcn_3='Katrien', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')

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
        orc.placer_order_number = EI(ei_1='ORD55801', ei_2='RISONWEB')
        orc.filler_order_number = EI(ei_1='FIL66701', ei_2='PACS_BE')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD55801', ei_2='RISONWEB')
        obr.filler_order_number = EI(ei_1='FIL66701', ei_2='PACS_BE')
        obr.universal_service_identifier = CWE(cwe_1='77067', cwe_2='MAMMOGRAFIE BILATERAAL SCREENING', cwe_3='CPT4')
        obr.obr_16 = '22678901045^Hendrickx^Sara^^^Dr.'
        obr.results_rpt_status_chng_date_time = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='859776-5', cwe_2='Procedure Findings', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'Bilaterale mammografie. Dicht klierweefsel (ACR-densiteit C). Geen verdachte microcalcificaties. Geen architectuurverstoring. Geen focale as'
            'ymmetrie.'
        )
        obx.interpretation_codes = CWE(cwe_1='N', cwe_2='Normaal', cwe_3='HL70078')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='36625-2', cwe_2='BI-RADS Assessment', cwe_3='LN')
        obx_2.obx_5 = 'BI-RADS 1^Negatief^ACR'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='&IMP')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = 'BI-RADS 1 - Negatief bilateraal mammografisch onderzoek. Volgende screening over 2 jaar aanbevolen.'
        obx_3.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/be/be-risonweb.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='UZ_ANTWERPEN')
        msh.receiving_application = HD(hd_1='HIS_BE')
        msh.receiving_facility = HD(hd_1='UZ_ANTWERPEN')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260509160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT00612', cx_4='UZA', cx_5='PI')
        pid.pid_4 = '86071234589^^^^NN'
        pid.patient_name = XPN(xpn_1='Lenaerts', xpn_2='Annelies', xpn_3='T', xpn_5='Mevr.')
        pid.date_time_of_birth = '19860712'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Mechelsesteenweg 55', xad_3='Antwerpen', xad_5='2000', xad_6='BE')
        pid.pid_13 = '^^PH^03-231-8945~^^CP^0476-589321'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='Kamer 201', pl_3='Bed 1', pl_4='Interventionele Radiologie')
        pv1.pv1_7 = '21901234078^Peeters^Luc^^^Dr.^med.'
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.patient_type = CWE(cwe_1='OPNAME20260509')
        pv1.account_status = CWE(cwe_1='RAD', cwe_2='Kamer 201', cwe_3='Bed 1', cwe_4='Interventionele Radiologie')
        pv1.prior_temporary_location = PL(pl_1='20260509160000')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/be/be-risonweb.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='UZ_GENT')
        msh.receiving_application = HD(hd_1='PACS_BE')
        msh.receiving_facility = HD(hd_1='UZ_GENT')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT65112', cx_4='UZG', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Janssens', xpn_2='Dirk', xpn_3='R', xpn_5='Dhr.')
        pid.date_time_of_birth = '19670302'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Blaarmeersen 18', xad_3='Gent', xad_5='9000', xad_6='BE')
        pid.pid_13 = '^^PH^09-335-7812'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NUCL', pl_2='PET-1', pl_3='1', pl_4='Nucleaire Geneeskunde')
        pv1.pv1_7 = '22789012056^Goossens^Marc^^^Prof.^Dr.'
        pv1.hospital_service = CWE(cwe_1='MED')

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
        orc.placer_order_number = EI(ei_1='ORD66901', ei_2='RISONWEB')
        orc.filler_order_number = EI(ei_1='FIL77801', ei_2='PACS_BE')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20260509140000^^R'
        orc.date_time_of_order_event = '20260509140000'
        orc.orc_10 = '22789012056^Goossens^Marc^^^Prof.^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD66901', ei_2='RISONWEB')
        obr.filler_order_number = EI(ei_1='FIL77801', ei_2='PACS_BE')
        obr.universal_service_identifier = CWE(cwe_1='78816', cwe_2='PET-CT FDG WHOLE BODY', cwe_3='CPT4')
        obr.obr_5 = 'R'
        obr.obr_6 = '20260509130000'
        obr.relevant_clinical_information = CWE(cwe_1='22789012056', cwe_2='Goossens', cwe_3='Marc', cwe_6='Prof.', cwe_7='Dr.')
        obr.obr_16 = 'Stadiering longcarcinoom, histologisch bewezen NSCLC'
        obr.placer_field_1 = 'PT'
        obr.placer_field_2 = 'SC'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C34.1', cwe_2='Maligne neoplasma bovenkwab long', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20260505'

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
    """ Based on live/be/be-risonweb.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='CHU_LIEGE')
        msh.receiving_application = HD(hd_1='DMP_BE')
        msh.receiving_facility = HD(hd_1='EHEALTH_BE')
        msh.date_time_of_message = '20260509180000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT77312', cx_4='CHUL', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Mertens', xpn_2='Wim', xpn_3='F', xpn_5='Dhr.')
        pid.date_time_of_birth = '19840114'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Quai de Rome 33', xad_3='Liege', xad_5='4000', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='IRM-2', pl_3='1', pl_4='Radiologie')
        pv1.attending_doctor = XCN(xcn_1='21678901045', xcn_2='Lejeune', xcn_3='Antoine', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')

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
        orc.placer_order_number = EI(ei_1='ORD99301', ei_2='RISONWEB')
        orc.filler_order_number = EI(ei_1='FIL00201', ei_2='PACS_BE')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD99301', ei_2='RISONWEB')
        obr.filler_order_number = EI(ei_1='FIL00201', ei_2='PACS_BE')
        obr.universal_service_identifier = CWE(cwe_1='18748-4', cwe_2="CR d'imagerie medicale", cwe_3='LN')
        obr.obr_16 = '21678901045^Lejeune^Antoine^^^Dr.'
        obr.results_rpt_status_chng_date_time = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2="CR d'imagerie medicale", cwe_3='LN')
        obx.obx_5 = (
            '^TEXT^XML^Base64^'
            'PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj48cmVsYXRlZERvY3VtZW50IHR5cGVDb2RlPSJSUExDIj48cGFyZW50RG9jdW1lbnQ+PGlkIHJvb3Q9IjEuMi4y'
            'NTAuMS4yMTMuMS4xLjEiLz48L3BhcmVudERvY3VtZW50PjwvcmVsYXRlZERvY3VtZW50PjwvQ2xpbmljYWxEb2N1bWVudD4='
        )
        obx.observation_result_status = 'C'

        # .. build PRT ..
        prt = PRT()
        prt.action_code = 'UC'
        prt.role_of_participation = CWE(cwe_1='SB', cwe_2='Send by', cwe_3='participation')
        prt.person = XCN(xcn_1='21678901045', xcn_2='Lejeune', xcn_3='Antoine', xcn_9='NIHDI&2.16.840.1.113883.3.6777.5.2&ISO', xcn_10='D', xcn_13='NIHDI')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx
        observation.prt = prt

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='MASQUE_PS', cwe_2='Masque aux professionnels de Sante', cwe_3='MetaDMPMSS')
        obx_2.obx_5 = 'N^^expandedYes-NoIndicator'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='DESTDMP', cwe_2='Destinataire DMP', cwe_3='MetaDMPMSS')
        obx_3.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='DESTMSSANTEPS', cwe_2='Destinataire PS', cwe_3='MetaDMPMSS')
        obx_4.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CE'
        obx_5.observation_identifier = CWE(cwe_1='DESTMSSANTEPAT', cwe_2='Destinataire Patient', cwe_3='MetaDMPMSS')
        obx_5.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ED'
        obx_6.observation_identifier = CWE(cwe_1='CORPSMAIL_PS', cwe_2='Corps du mail pour un PS', cwe_3='MetaDMPMSS')
        obx_6.obx_5 = '^TEXT^^Base64^Q2hlciBjb25mcmVyZSwgdm91cyB0cm91dmVyZXogY2ktam9pbnQgbGUgQ1IgY29ycmlnZSBkJ0lSTS4='
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
    """ Based on live/be/be-risonweb.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RISONWEB')
        msh.sending_facility = HD(hd_1='UZ_GENT')
        msh.receiving_application = HD(hd_1='PACS_BE')
        msh.receiving_facility = HD(hd_1='UZ_GENT')
        msh.date_time_of_message = '20260509141500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT65112', cx_4='UZG', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Janssens', xpn_2='Dirk', xpn_3='R', xpn_5='Dhr.')
        pid.date_time_of_birth = '19670302'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Blaarmeersen 18', xad_3='Gent', xad_5='9000', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NUCL', pl_2='PET-1', pl_3='1', pl_4='Nucleaire Geneeskunde')
        pv1.pv1_7 = '22789012056^Goossens^Marc^^^Prof.^Dr.'
        pv1.hospital_service = CWE(cwe_1='MED')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'SC'
        orc.placer_order_number = EI(ei_1='ORD66901', ei_2='RISONWEB')
        orc.filler_order_number = EI(ei_1='FIL77801', ei_2='PACS_BE')
        orc.order_status = 'IP'
        orc.orc_7 = '^^^20260509141500^^R'
        orc.date_time_of_order_event = '20260509141500'
        orc.orc_10 = '22789012056^Goossens^Marc^^^Prof.^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD66901', ei_2='RISONWEB')
        obr.filler_order_number = EI(ei_1='FIL77801', ei_2='PACS_BE')
        obr.universal_service_identifier = CWE(cwe_1='78816', cwe_2='PET-CT FDG WHOLE BODY', cwe_3='CPT4')
        obr.obr_16 = '22789012056^Goossens^Marc^^^Prof.^Dr.'
        obr.results_rpt_status_chng_date_time = 'IP'

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
