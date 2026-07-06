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
from zato.hl7v2.v2_9.datatypes import CWE, CX, DLD, EI, HD, MOC, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import OrmO01Insurance, OrmO01Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import EVN, IN1, MSH, NK1, OBR, OBX, ORC, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('nl', 'nl-zorgplatform.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/nl/nl-zorgplatform.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20160324163509+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'ZD200046119'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='van der Berg&van der&Berg', xpn_2='J', xpn_3='M', xpn_7='L')
        pid.date_time_of_birth = '20000101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Keizersgracht 120&Keizersgracht&120', xad_2='bis', xad_3='Amsterdam', xad_5='1015CZ', xad_6='NL', xad_7='H')
        pid.pid_13 = '020-6891345_^NET^Internet^j.vanderberg@voorbeeld.nl'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ZD200046119')
        orc.date_time_of_order_event = '20160324163432+0100'
        orc.orc_10 = '^&&het Willems^D.E.F.'
        orc.orc_12 = '01004567^&&van Hoekstra^P.Q.^^^^^^VEKTIS'
        orc.orc_14 = '015-2222222'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD200046119')
        obr.universal_service_identifier = CWE(cwe_1='CIS', cwe_2='Cardiologie', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20160324163432+0100'
        obr.obr_16 = '01004567^&&van Hoekstra^P.Q.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='VB', cwe_3='123')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='CARHAR', cwe_2='Hartfalen', cwe_3='ZORGDOMEIN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUHJvZHVjZXIgKP7/AFEAdAAg'
            'ADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzUwOCswMScwMCcpCj4+CmVuZG9iag=='
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='CARCOA001', cwe_2='consult cardioloog', cwe_3='ZORGDOMEIN')
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
    """ Based on live/nl/nl-zorgplatform.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20160324163441+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'ZD200046119'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='van der Berg&van der&Berg', xpn_2='J', xpn_3='M', xpn_7='L')
        pid.date_time_of_birth = '20000101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Keizersgracht 120&Keizersgracht&120', xad_2='bis', xad_3='Amsterdam', xad_5='1015CZ', xad_6='NL', xad_7='H')
        pid.pid_13 = '020-6891345'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ZD200046119')
        orc.date_time_of_order_event = '20160324163432+0100'
        orc.orc_10 = '^&&het Willems^D.E.F.'
        orc.orc_12 = '01004567^&&van Hoekstra^P.Q.^^^^^^VEKTIS'
        orc.orc_14 = '015-2222222'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD200046119')
        obr.universal_service_identifier = CWE(cwe_1='CIS', cwe_2='Cardiologie', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20160324163432+0100'
        obr.obr_16 = '01004567^&&van Hoekstra^P.Q.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='AF', cwe_3='123')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='CARHAR', cwe_2='Hartfalen', cwe_3='ZORGDOMEIN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUHJvZHVjZXIgKP7/AFEAdAAg'
            'ADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzQ0MSswMScwMCcpCj4+CmVuZG9iag=='
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='CARCOA001', cwe_2='consult cardioloog', cwe_3='ZORGDOMEIN')
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
    """ Based on live/nl/nl-zorgplatform.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20220410143000+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ZD300012345'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='123456782', cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='de Wit&de&Wit', xpn_2='Johanna', xpn_3='M', xpn_7='L')
        pid.date_time_of_birth = '19751220'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kerkstraat 45', xad_3='Rotterdam', xad_5='3011CD', xad_6='NL', xad_7='H')
        pid.pid_13 = '010-4445566^PRN^PH~^^^j.dewit@email.nl^NET^Internet'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_name = XON(xon_1='VGZ', xon_2='VGZ Zorgverzekeraar')
        in1.insureds_group_emp_id = CX(cx_1='123456789')

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ZD300012345')
        orc.date_time_of_order_event = '20220410143000+0200'
        orc.orc_10 = '^&&van Groenendaal^B.C.'
        orc.orc_12 = '01234567^&&van Leeuwen^A.B.^^^^^^VEKTIS'
        orc.orc_14 = '010-7778899'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD300012345')
        obr.universal_service_identifier = CWE(cwe_1='DER', cwe_2='Dermatologie', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20220410143000+0200'
        obr.obr_16 = '01234567^&&van Leeuwen^A.B.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='DERMOA001', cwe_2='Consult dermatoloog', cwe_3='ZORGDOMEIN')
        obx.obx_5 = 'Verdachte moedervlek rechter schouder, groei in afgelopen 3 maanden'
        obx.user_defined_access_checks = 'F'

        # .. build the OBSERVATION group ..
        observation = OrmO01Observation()
        observation.obx = obx

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
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
    """ Based on live/nl/nl-zorgplatform.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20220601101500+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ZD300054321'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='666777888', cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='Pietersen', xpn_2='Maria', xpn_3='A', xpn_7='L')
        pid.date_time_of_birth = '19830415'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Singel 100', xad_3='Amsterdam', xad_5='1012AB', xad_6='NL', xad_7='H')
        pid.pid_13 = '020-5551234'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

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
        orc.placer_order_number = EI(ei_1='ZD300054321')
        orc.date_time_of_order_event = '20220601101500+0200'
        orc.orc_10 = '^&&van de Broek^C.D.'
        orc.orc_12 = '09876543^&&Evers^E.F.^^^^^^VEKTIS'
        orc.orc_14 = '020-3334444'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD300054321')
        obr.universal_service_identifier = CWE(cwe_1='RAD', cwe_2='Radiologie', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20220601101500+0200'
        obr.obr_16 = '09876543^&&Evers^E.F.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='RADMRI001', cwe_2='MRI knie rechts', cwe_3='ZORGDOMEIN')
        obx.obx_5 = 'Patiente klaagt over aanhoudende kniepijn rechts na sportblessure. Verdenking meniscusletsel.'
        obx.user_defined_access_checks = 'F'

        # .. build the OBSERVATION group ..
        observation = OrmO01Observation()
        observation.obx = obx

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
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
    """ Based on live/nl/nl-zorgplatform.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='OLVG')
        msh.receiving_application = HD(hd_1='ZORGPLATFORM')
        msh.receiving_facility = HD(hd_1='CHIPSOFT')
        msh.date_time_of_message = '20220115080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'HIX20220115001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20220115080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT10001', cx_4='OLVG', cx_5='PI'), CX(cx_1='371926485', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='van der Linden', xpn_2='Cornelis', xpn_3='J')
        pid.date_time_of_birth = '19520310'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Oosterpark 50', xad_3='Amsterdam', xad_5='1091AC', xad_6='NL', xad_7='H')
        pid.pid_13 = '020-5993000^PRN^PH'
        pid.religion = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='401', pl_3='2', pl_4='OLVG')
        pv1.attending_doctor = XCN(xcn_1='10001', xcn_2='de Graaf', xcn_3='Floor', xcn_6='dr.')
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.admit_source = CWE(cwe_1='ADM')
        pv1.admitting_doctor = XCN(xcn_1='10001', xcn_2='de Graaf', xcn_3='Floor', xcn_6='dr.')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.delete_account_date = 'OLVG'
        pv1.discharged_to_location = DLD(dld_1='A')
        pv1.pv1_40 = '20220115075000'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='van der Linden', xpn_2='Elisabeth', xpn_3='A')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Echtgenote')
        nk1.address = XAD(xad_1='Oosterpark 50', xad_3='Amsterdam', xad_5='1091AC', xad_6='NL')
        nk1.nk1_5 = '020-5993001'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='MENZIS001', cwe_2='Menzis')
        in1.insurance_company_id = CX(cx_1='MENZIS')
        in1.insurance_company_address = XAD(xad_1='Postbus 75000', xad_3='Enschede', xad_5='7500KA', xad_6='NL')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1, in1]

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
    """ Based on live/nl/nl-zorgplatform.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='OLVG')
        msh.receiving_application = HD(hd_1='ZORGPLATFORM')
        msh.receiving_facility = HD(hd_1='CHIPSOFT')
        msh.date_time_of_message = '20220120140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'HIX20220120001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20220120140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT10001', cx_4='OLVG', cx_5='PI'), CX(cx_1='371926485', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='van der Linden', xpn_2='Cornelis', xpn_3='J')
        pid.date_time_of_birth = '19520310'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='401', pl_3='2', pl_4='OLVG')
        pv1.attending_doctor = XCN(xcn_1='10001', xcn_2='de Graaf', xcn_3='Floor', xcn_6='dr.')
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.admit_source = CWE(cwe_1='ADM')
        pv1.admitting_doctor = XCN(xcn_1='10001', xcn_2='de Graaf', xcn_3='Floor', xcn_6='dr.')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.delete_account_date = 'OLVG'
        pv1.discharged_to_location = DLD(dld_1='D')
        pv1.pv1_40 = '20220115075000'
        pv1.prior_temporary_location = PL(pl_1='20220120133000')

        # .. assemble the full message ..
        msg = ADT_A03()
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
    """ Based on live/nl/nl-zorgplatform.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='OLVG')
        msh.receiving_application = HD(hd_1='ZORGPLATFORM')
        msh.receiving_facility = HD(hd_1='CHIPSOFT')
        msh.date_time_of_message = '20220201093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'HIX20220201001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20220201093000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT10001', cx_4='OLVG', cx_5='PI'), CX(cx_1='371926485', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='van der Linden', xpn_2='Cornelis', xpn_3='J')
        pid.date_time_of_birth = '19520310'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Waterlooplein 15', xad_3='Amsterdam', xad_5='1011NZ', xad_6='NL', xad_7='H')
        pid.pid_13 = '020-6001234^PRN^PH~^^^c.vanderlinden@email.nl'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI', pl_2='CARD', pl_3='01', pl_4='OLVG')
        pv1.attending_doctor = XCN(xcn_1='10001', xcn_2='de Graaf', xcn_3='Floor', xcn_6='dr.')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/nl/nl-zorgplatform.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='ANTONIUS')
        msh.receiving_application = HD(hd_1='ZORGPLATFORM')
        msh.receiving_facility = HD(hd_1='CHIPSOFT')
        msh.date_time_of_message = '20220315100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'HIX20220315001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20220315100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT20001', cx_4='ANTONIUS', cx_5='PI'), CX(cx_1='482917365', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Kok', xpn_2='Lisette', xpn_3='M')
        pid.date_time_of_birth = '19880520'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Soestdijkseweg Zuid 40', xad_3='Bilthoven', xad_5='3721AA', xad_6='NL', xad_7='H')
        pid.pid_13 = '030-2345678^PRN^PH'
        pid.religion = CWE(cwe_1='O')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI', pl_2='GYNA', pl_3='01', pl_4='ANTONIUS')
        pv1.attending_doctor = XCN(xcn_1='20002', xcn_2='Willems', xcn_3='Anke', xcn_6='dr.')
        pv1.hospital_service = CWE(cwe_1='GYN')
        pv1.admit_source = CWE(cwe_1='REG')
        pv1.admitting_doctor = XCN(xcn_1='20002', xcn_2='Willems', xcn_3='Anke', xcn_6='dr.')
        pv1.patient_type = CWE(cwe_1='OP')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/nl/nl-zorgplatform.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='CATHARINA')
        msh.receiving_application = HD(hd_1='ZORGPLATFORM')
        msh.receiving_facility = HD(hd_1='CHIPSOFT')
        msh.date_time_of_message = '20220420140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'HIX20220420001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20220420140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT30001', cx_4='CATHARINA', cx_5='PI'), CX(cx_1='639184275', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Hermans', xpn_2='Willem', xpn_3='F')
        pid.date_time_of_birth = '19700901'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT', pl_2='201', pl_3='1', pl_4='CATHARINA')
        pv1.attending_doctor = XCN(xcn_1='30003', xcn_2='Jacobs', xcn_3='Martijn', xcn_6='dr.')
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.admit_source = CWE(cwe_1='ADM')
        pv1.admitting_doctor = XCN(xcn_1='30003', xcn_2='Jacobs', xcn_3='Martijn', xcn_6='dr.')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.bad_debt_transfer_amount = 'IC^101^1^CATHARINA'
        pv1.delete_account_date = 'CATHARINA'
        pv1.discharged_to_location = DLD(dld_1='A')
        pv1.pv1_40 = '20220418060000'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/nl/nl-zorgplatform.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX_LAB')
        msh.sending_facility = HD(hd_1='AMPHIA')
        msh.receiving_application = HD(hd_1='HIX_EPD')
        msh.receiving_facility = HD(hd_1='AMPHIA')
        msh.date_time_of_message = '20220505080000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HLAB20220505001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT40001', cx_4='AMPHIA', cx_5='PI'), CX(cx_1='724185936', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Brouwer', xpn_2='Thomas', xpn_3='G')
        pid.date_time_of_birth = '19650415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Molenberg 1', xad_3='Breda', xad_5='4817JA', xad_6='NL')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='301', pl_3='1', pl_4='AMPHIA')
        pv1.attending_doctor = XCN(xcn_1='40004', xcn_2='Martens', xcn_3='Pieter', xcn_6='dr.')

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
        orc.placer_order_number = EI(ei_1='ORD1001', ei_2='HIX_EPD')
        orc.filler_order_number = EI(ei_1='FILL2001', ei_2='HIX_LAB')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1001', ei_2='HIX_EPD')
        obr.filler_order_number = EI(ei_1='FILL2001', ei_2='HIX_LAB')
        obr.universal_service_identifier = CWE(cwe_1='57021-8', cwe_2='CBC', cwe_3='LN')
        obr.observation_date_time = '20220505060000'
        obr.obr_14 = '40004^Martens^Pieter^^^dr.'
        obr.filler_field_1 = '20220505075000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocyten', cwe_3='LN')
        obx.obx_5 = '8.5'
        obx.units = CWE(cwe_1='10*9/l')
        obx.reference_range = '4.0-10.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobine', cwe_3='LN')
        obx_2.obx_5 = '9.2'
        obx_2.units = CWE(cwe_1='mmol/l')
        obx_2.reference_range = '8.5-11.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocriet', cwe_3='LN')
        obx_3.obx_5 = '0.44'
        obx_3.units = CWE(cwe_1='l/l')
        obx_3.reference_range = '0.41-0.51'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='777-3', cwe_2='Trombocyten', cwe_3='LN')
        obx_4.obx_5 = '210'
        obx_4.units = CWE(cwe_1='10*9/l')
        obx_4.reference_range = '150-400'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Kreatinine', cwe_3='LN')
        obx_5.obx_5 = '95'
        obx_5.units = CWE(cwe_1='umol/l')
        obx_5.reference_range = '62-106'
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
    """ Based on live/nl/nl-zorgplatform.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX_DIET')
        msh.sending_facility = HD(hd_1='RIJNSTATE')
        msh.receiving_application = HD(hd_1='ZORGPLATFORM')
        msh.receiving_facility = HD(hd_1='CHIPSOFT')
        msh.date_time_of_message = '20220610120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HDIET20220610001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT50001', cx_4='RIJNSTATE', cx_5='PI'), CX(cx_1='856349172', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Smeets', xpn_2='Anna', xpn_3='K')
        pid.date_time_of_birth = '19450320'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Velperweg 50', xad_3='Arnhem', xad_5='6824BM', xad_6='NL')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT', pl_2='502', pl_3='1', pl_4='RIJNSTATE')
        pv1.attending_doctor = XCN(xcn_1='50005', xcn_2='Janssen', xcn_3='Erik', xcn_6='dr.')

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
        orc.placer_order_number = EI(ei_1='ORD1101', ei_2='HIX')
        orc.filler_order_number = EI(ei_1='FILL2101', ei_2='HIX_DIET')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1101', ei_2='HIX')
        obr.filler_order_number = EI(ei_1='FILL2101', ei_2='HIX_DIET')
        obr.universal_service_identifier = CWE(cwe_1='75282-4', cwe_2='Nutrition assessment', cwe_3='LN')
        obr.observation_date_time = '20220610100000'
        obr.obr_14 = '50005^Janssen^Erik^^^dr.'
        obr.filler_field_1 = '20220610115000'
        obr.results_rpt_status_chng_date_time = 'DIET'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='29463-7', cwe_2='Body weight', cwe_3='LN')
        obx.obx_5 = '52.3'
        obx.units = CWE(cwe_1='kg')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='8302-2', cwe_2='Body height', cwe_3='LN')
        obx_2.obx_5 = '1.62'
        obx_2.units = CWE(cwe_1='m')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='39156-5', cwe_2='BMI', cwe_3='LN')
        obx_3.obx_5 = '19.9'
        obx_3.units = CWE(cwe_1='kg/m2')
        obx_3.reference_range = '18.5-25.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='75303-8', cwe_2='Nutrition screening status', cwe_3='LN')
        obx_4.obx_5 = 'Score 3: matig risico op ondervoeding'
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
    """ Based on live/nl/nl-zorgplatform.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX_FUNC')
        msh.sending_facility = HD(hd_1='DEVENTER_ZH')
        msh.receiving_application = HD(hd_1='ZORGPLATFORM')
        msh.receiving_facility = HD(hd_1='CHIPSOFT')
        msh.date_time_of_message = '20220720150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HFUNC20220720001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT60001', cx_4='DEVENTER_ZH', cx_5='PI'), CX(cx_1='913527486', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Dekker', xpn_2='Robert', xpn_3='H')
        pid.date_time_of_birth = '19580830'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Brinkgreverweg 100', xad_3='Deventer', xad_5='7413AA', xad_6='NL')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LONG', pl_2='FUNC', pl_3='01', pl_4='DEVENTER_ZH')
        pv1.attending_doctor = XCN(xcn_1='60006', xcn_2='de Boer', xcn_3='Henk', xcn_6='dr.')

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
        orc.placer_order_number = EI(ei_1='ORD1201', ei_2='HIX')
        orc.filler_order_number = EI(ei_1='FILL2201', ei_2='HIX_FUNC')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1201', ei_2='HIX')
        obr.filler_order_number = EI(ei_1='FILL2201', ei_2='HIX_FUNC')
        obr.universal_service_identifier = CWE(cwe_1='81459-0', cwe_2='Spirometry panel', cwe_3='LN')
        obr.observation_date_time = '20220720130000'
        obr.obr_14 = '60006^de Boer^Henk^^^dr.'
        obr.filler_field_1 = '20220720145000'
        obr.results_rpt_status_chng_date_time = 'FUNC'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='19868-9', cwe_2='FEV1', cwe_3='LN')
        obx.obx_5 = '2.45'
        obx.units = CWE(cwe_1='L')
        obx.reference_range = '2.80-4.20'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='19870-5', cwe_2='FVC', cwe_3='LN')
        obx_2.obx_5 = '3.85'
        obx_2.units = CWE(cwe_1='L')
        obx_2.reference_range = '3.50-5.20'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='19926-5', cwe_2='FEV1/FVC', cwe_3='LN')
        obx_3.obx_5 = '63.6'
        obx_3.units = CWE(cwe_1='%')
        obx_3.reference_range = '>70'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='SPIRO_INTERP', cwe_2='Interpretation', cwe_3='LOCAL')
        obx_4.obx_5 = 'Matig obstructief longfunctiepatroon. Advies: bronchusverwijdingstest.'
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
    """ Based on live/nl/nl-zorgplatform.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20220801090000+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ZD300098765'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='291638574', cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='van Dijk', xpn_2='Pieter', xpn_3='M', xpn_7='L')
        pid.date_time_of_birth = '19700620'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Stadhouderslaan 20', xad_3='Den Haag', xad_5='2517HZ', xad_6='NL', xad_7='H')
        pid.pid_13 = '070-3456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

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
        orc.placer_order_number = EI(ei_1='ZD300098765')
        orc.date_time_of_order_event = '20220801090000+0200'
        orc.orc_10 = '^&&Vermeulen^A.B.'
        orc.orc_12 = '11223344^&&van Kamp^G.H.^^^^^^VEKTIS'
        orc.orc_14 = '070-1112222'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD300098765')
        obr.universal_service_identifier = CWE(cwe_1='ORT', cwe_2='Orthopedie', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20220801090000+0200'
        obr.obr_16 = '11223344^&&van Kamp^G.H.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='ORTCON001', cwe_2='consult orthopeed', cwe_3='ZORGDOMEIN')
        obx.obx_5 = 'Patient klaagt over chronische lage rugpijn, uitstralend naar links been. Lasegue positief links. Verdenking HNP L4-L5.'
        obx.user_defined_access_checks = 'F'

        # .. build the OBSERVATION group ..
        observation = OrmO01Observation()
        observation.obx = obx

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
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
    """ Based on live/nl/nl-zorgplatform.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20220915110000+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ZD300076543'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='472816953', cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='Hendriks', xpn_2='Gerda', xpn_3='W', xpn_7='L')
        pid.date_time_of_birth = '19500105'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Burg. de Monchyplein 10', xad_3='Den Haag', xad_5='2585BE', xad_6='NL', xad_7='H')
        pid.pid_13 = '070-9998877'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_name = XON(xon_1='ONVZ', xon_2='ONVZ Ziektekostenverzekeraar')
        in1.insureds_group_emp_id = CX(cx_1='987654321')

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ZD300076543')
        orc.date_time_of_order_event = '20220915110000+0200'
        orc.orc_10 = '^&&de Ruiter^I.J.'
        orc.orc_12 = '55667788^&&Kramer^K.L.^^^^^^VEKTIS'
        orc.orc_14 = '070-5556666'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD300076543')
        obr.universal_service_identifier = CWE(cwe_1='CAR', cwe_2='Cardiologie', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20220915110000+0200'
        obr.obr_16 = '55667788^&&Kramer^K.L.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='CARECHO01', cwe_2='Echocardiografie', cwe_3='ZORGDOMEIN')
        obx.obx_5 = "Patiente met dyspnoe d'effort en enkelvocht. Verdenking hartfalen. Graag echocardiografie."
        obx.user_defined_access_checks = 'F'

        # .. build the OBSERVATION group ..
        observation = OrmO01Observation()
        observation.obx = obx

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
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
    """ Based on live/nl/nl-zorgplatform.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX_MULTI')
        msh.sending_facility = HD(hd_1='MEANDER_MC')
        msh.receiving_application = HD(hd_1='ZORGPLATFORM')
        msh.receiving_facility = HD(hd_1='CHIPSOFT')
        msh.date_time_of_message = '20221001090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HMULT20221001001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT70001', cx_4='MEANDER_MC', cx_5='PI'), CX(cx_1='518462937', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Bakker', xpn_2='Johannes', xpn_3='L')
        pid.date_time_of_birth = '19750430'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Maatweg 3', xad_3='Amersfoort', xad_5='3813TJ', xad_6='NL')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='WOND', pl_3='01', pl_4='MEANDER_MC')
        pv1.attending_doctor = XCN(xcn_1='70007', xcn_2='Kuiper', xcn_3='Frank', xcn_6='dr.')

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
        orc.placer_order_number = EI(ei_1='ORD1301', ei_2='HIX')
        orc.filler_order_number = EI(ei_1='FILL2301', ei_2='HIX_MULTI')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1301', ei_2='HIX')
        obr.filler_order_number = EI(ei_1='FILL2301', ei_2='HIX_MULTI')
        obr.universal_service_identifier = CWE(cwe_1='72170-4', cwe_2='Photo documentation', cwe_3='LN')
        obr.observation_date_time = '20221001083000'
        obr.obr_14 = '70007^Kuiper^Frank^^^dr.'
        obr.filler_field_1 = '20221001085000'
        obr.results_rpt_status_chng_date_time = 'DOC'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='72170-4', cwe_2='Photo documentation', cwe_3='LN')
        obx.obx_5 = 'Wondcontrole linker onderbeen, 3 weken post-operatief. Goede genezing.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Wound Photo', cwe_3='LOCAL')
        obx_2.obx_5 = (
            '^image^jpeg^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMo'
            'GhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAoACgDASIAAhEBAxEB/8QAGAABAAMBAAAAAAAAAAAAAAAAAAUHCAb/xAAsEAAB'
            'AwIFAgUFAQAAAAAAAAABAgMEAAURBhIhMQdBExQiUWEIFTKBkaH/xAAYAQADAQEAAAAAAAAAAAAAAAACAwQFAf/EAB8RAAICAgIDAQAAAAAAAAAAAAECAAMREgQhIjFBcf/aAAwDAQAC'
            'EQMRAD8AtGlKVRwmJzxBa0q0bpOdEfQ0jO84R+KR3P8AKy/1I6p3G/XB+1WaU9EtcZxTQDDhQt9YOCVKHYHsBt71Z/VbqPE6f2cvshuXJk+EWYjOBzgEblR7AE/2sZ3G5y7vcZNxnOl2'
            'VKdU8+s9yo5NSck6N0mR8OoLYXf2Jjp9cL1a+o9lk2+4SWQmS2l1pt0pQ6gqAKVJzQQRWu6xn0Wsq7x1OsDAOEtSPOOnsCy2VJH9UgVsylFLkQR5FIrsUDUUV56h3tOHMJ3a7LbQ4YMN'
            '2QEK2C8iCcH9180bzfJ97uMm5XKQuTNlOKdffdOVLWo7kmpH6g8cm6dMLy0welzFMi3LHqcSFHOP4M1XvSTqld+n16MuCEyYchIRMhOK9LqR2I7EHcGoj3LNtMR8PhJSSNjLrsnUK+3y'
            '4T7tfJ781yYcPqkPFRA7J3OEgdgNhVldD+ksjo7Y1F5xqVdZmEyphQcICRulCO+AT+zVK9bupUjqNeRJDbjFrhBSIsJxWepB3Uo+5Nh+q5qjrtyNugVVVBQmX704utq6edRLRL0/MlFM'
            'd9K3WG3CG30hQJSpOCD/AKKKNM7zzr+f/9k='
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
    """ Based on live/nl/nl-zorgplatform.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX_CARD')
        msh.sending_facility = HD(hd_1='ISALA')
        msh.receiving_application = HD(hd_1='ZORGPLATFORM')
        msh.receiving_facility = HD(hd_1='CHIPSOFT')
        msh.date_time_of_message = '20221110150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HCARD20221110001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT80001', cx_4='ISALA', cx_5='PI'), CX(cx_1='736291548', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Bosman', xpn_2='Hendrik', xpn_3='K')
        pid.date_time_of_birth = '19550120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='IJsselkade 10', xad_3='Zwolle', xad_5='8011AR', xad_6='NL')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='PACE', pl_3='01', pl_4='ISALA')
        pv1.attending_doctor = XCN(xcn_1='80008', xcn_2='Verhoeven', xcn_3='Willem', xcn_6='dr.')

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
        orc.placer_order_number = EI(ei_1='ORD1401', ei_2='HIX')
        orc.filler_order_number = EI(ei_1='FILL2401', ei_2='HIX_CARD')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1401', ei_2='HIX')
        obr.filler_order_number = EI(ei_1='FILL2401', ei_2='HIX_CARD')
        obr.universal_service_identifier = CWE(cwe_1='75042-2', cwe_2='Cardiac device check', cwe_3='LN')
        obr.observation_date_time = '20221110130000'
        obr.obr_14 = '80008^Verhoeven^Willem^^^dr.'
        obr.filler_field_1 = '20221110145000'
        obr.results_rpt_status_chng_date_time = 'CARD'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='PACE_REPORT', cwe_2='Pacemaker Report', cwe_3='LOCAL')
        obx.obx_5 = (
            'Medtronic Advisa DR MRI, implantatie 2019-03-15\\.br\\Batterijstatus: 2.78V, geschatte levensduur >4 jaar\\.br\\Sensing: A 2.5mV, V 12.0mV\\.br'
            '\\Drempels: A 0.75V/0.4ms, V 1.0V/0.4ms\\.br\\Modus: DDD 60-130/min\\.br\\Conclusie: Goede pacemakerfunctie, volgende controle over 6 maanden.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
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
    """ Based on live/nl/nl-zorgplatform.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX_PATH')
        msh.sending_facility = HD(hd_1='ERASMUS')
        msh.receiving_application = HD(hd_1='ZORGPLATFORM')
        msh.receiving_facility = HD(hd_1='CHIPSOFT')
        msh.date_time_of_message = '20221201110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HPATH20221201001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT90001', cx_4='ERASMUS', cx_5='PI'), CX(cx_1='847261935', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Mulder', xpn_2='Kees', xpn_3='P')
        pid.date_time_of_birth = '19800305'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Westzeedijk 100', xad_3='Rotterdam', xad_5='3016AH', xad_6='NL')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='601', pl_3='1', pl_4='ERASMUS')
        pv1.attending_doctor = XCN(xcn_1='90009', xcn_2='van Rijn', xcn_3='Sandra', xcn_6='dr.')

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
        orc.placer_order_number = EI(ei_1='ORD1501', ei_2='HIX')
        orc.filler_order_number = EI(ei_1='FILL2501', ei_2='HIX_PATH')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD1501', ei_2='HIX')
        obr.filler_order_number = EI(ei_1='FILL2501', ei_2='HIX_PATH')
        obr.universal_service_identifier = CWE(cwe_1='22637-3', cwe_2='Pathology report', cwe_3='LN')
        obr.observation_date_time = '20221130090000'
        obr.obr_14 = '90009^van Rijn^Sandra^^^dr.'
        obr.filler_field_1 = '20221201103000'
        obr.results_rpt_status_chng_date_time = 'PATH'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Pathology report', cwe_3='LN')
        obx.obx_5 = (
            'Materiaal: Colonbiopt sigmoideum\\.br\\Macroscopie: 3 biopten, 2-4mm\\.br\\Microscopie: Slijmvliesfragmenten met actieve chronische ontsteking, '
            'cryptabcessen\\.br\\Conclusie: Colitis ulcerosa, actief.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
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

class TestMsg19(unittest.TestCase):
    """ Based on live/nl/nl-zorgplatform.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20221001080000+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ZD400011111'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='583719264', cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='Kuiper', xpn_2='Frank', xpn_3='J', xpn_7='L')
        pid.date_time_of_birth = '19650210'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Lange Voorhout 15', xad_3='Den Haag', xad_5='2514EA', xad_6='NL', xad_7='H')
        pid.pid_13 = '070-1234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

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
        orc.placer_order_number = EI(ei_1='ZD400011111')
        orc.date_time_of_order_event = '20221001080000+0200'
        orc.orc_10 = '^&&Scholten^M.N.'
        orc.orc_12 = '22334455^&&Peeters^O.P.^^^^^^VEKTIS'
        orc.orc_14 = '070-2223333'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD400011111')
        obr.universal_service_identifier = CWE(cwe_1='LAB', cwe_2='Klinische Chemie', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20221001080000+0200'
        obr.obr_16 = '22334455^&&Peeters^O.P.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='LABBLOED01', cwe_2='Bloedonderzoek', cwe_3='ZORGDOMEIN')
        obx.obx_5 = 'Gaarne volledig bloedbeeld, nierfunctie, leverfunctie, glucose nuchter. Patient gebruikt metformine.'
        obx.user_defined_access_checks = 'F'

        # .. build the OBSERVATION group ..
        observation = OrmO01Observation()
        observation.obx = obx

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
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
    """ Based on live/nl/nl-zorgplatform.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIX')
        msh.sending_facility = HD(hd_1='TERGOOI')
        msh.receiving_application = HD(hd_1='ZORGPLATFORM')
        msh.receiving_facility = HD(hd_1='CHIPSOFT')
        msh.date_time_of_message = '20230201100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A05', msg_3='ADT_A05')
        msh.message_control_id = 'HIX20230201001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A05'
        evn.recorded_date_time = '20230201100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT99001', cx_4='TERGOOI', cx_5='PI'), CX(cx_1='847362915', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Schouten', xpn_2='Elisabeth', xpn_3='W')
        pid.date_time_of_birth = '19600715'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Utrechtseweg 100', xad_3='Hilversum', xad_5='1213CL', xad_6='NL', xad_7='H')
        pid.pid_13 = '035-6012345^PRN^PH'
        pid.religion = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORT', pl_2='201', pl_3='1', pl_4='TERGOOI')
        pv1.attending_doctor = XCN(xcn_1='99010', xcn_2='Groen', xcn_3='Adriaan', xcn_6='dr.')
        pv1.hospital_service = CWE(cwe_1='ORT')
        pv1.admit_source = CWE(cwe_1='PREADM')
        pv1.admitting_doctor = XCN(xcn_1='99010', xcn_2='Groen', xcn_3='Adriaan', xcn_6='dr.')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.delete_account_date = 'TERGOOI'
        pv1.discharged_to_location = DLD(dld_1='P')
        pv1.pv1_40 = '20230210080000'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Schouten', xpn_2='Jan', xpn_3='J')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Echtgenoot')
        nk1.address = XAD(xad_1='Utrechtseweg 100', xad_3='Hilversum', xad_5='1213CL', xad_6='NL')
        nk1.nk1_5 = '035-6012346'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='CZ001', cwe_2='CZ Zorgverzekeraar')
        in1.insurance_company_id = CX(cx_1='CZ')
        in1.insurance_company_address = XAD(xad_1='Postbus 100', xad_3='Tilburg', xad_5='5000AC', xad_6='NL')

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1, in1]

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
