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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, EIP, FC, HD, MOC, MSG, PL, PT, VID, XAD, XCN, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, EVN, MRG, MSH, OBR, OBX, ORC, PID, PV1, PV2, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('dk', 'dk-sectra.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/dk/dk-sectra.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='AAUH_RAD')
        msh.receiving_application = HD(hd_1='SECTRA_PACS')
        msh.receiving_facility = HD(hd_1='AAUH_RAD')
        msh.date_time_of_message = '20260401091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'SEC00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0803853928', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Bruun', xpn_2='Sofie', xpn_3='Esther', xpn_5='')
        pid.date_time_of_birth = '19850308'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Marselis Boulevard 1', xad_3='Roskilde', xad_5='4000', xad_6='DK')
        pid.pid_13 = '^^PH^+4556117681'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='ORT', pl_3='410', pl_4='D1')
        pv1.attending_doctor = XCN(xcn_1='12001', xcn_2='Bang', xcn_3='Andreas', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ORT')
        pv1.financial_class = FC(fc_1='AAUH202604010001')

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
        orc.placer_order_number = EI(ei_1='ORD20260401001', ei_2='CARESTREAM_RIS')
        orc.parent_order = EIP(eip_1='20260401091000')
        orc.orc_11 = '12001^Bang^Andreas^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260401001', ei_2='CARESTREAM_RIS')
        obr.universal_service_identifier = CWE(cwe_1='XHIP', cwe_2='Røntgen af hofte', cwe_3='LOCAL')
        obr.observation_date_time = '20260401091000'
        obr.relevant_clinical_information = CWE(cwe_1='Collumfraktur, garden III')
        obr.obr_14 = '12001^Bang^Andreas^^^Dr.'

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
    """ Based on live/dk/dk-sectra.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='RH_RAD')
        msh.receiving_application = HD(hd_1='SECTRA_PACS')
        msh.receiving_facility = HD(hd_1='RH_RAD')
        msh.date_time_of_message = '20260402090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'SEC00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1205672217', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Hansen', xpn_2='Morten', xpn_3='Henning', xpn_5='')
        pid.date_time_of_birth = '19670512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Valby Langgade 141', xad_3='Aalborg Ø', xad_5='9210', xad_6='DK')
        pid.pid_13 = '^^PH^+4560835930'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='LUN', pl_3='L2031', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='22002', xcn_2='Christensen', xcn_3='Jørgen', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='LUN')
        pv1.financial_class = FC(fc_1='RH202604020001')

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
        orc.placer_order_number = EI(ei_1='ORD20260402001', ei_2='CARESTREAM_RIS')
        orc.parent_order = EIP(eip_1='20260402090000')
        orc.orc_11 = '22002^Christensen^Jørgen^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260402001', ei_2='CARESTREAM_RIS')
        obr.universal_service_identifier = CWE(cwe_1='CTCHEST', cwe_2='CT thorax med kontrast', cwe_3='LOCAL')
        obr.observation_date_time = '20260402090000'
        obr.relevant_clinical_information = CWE(cwe_1='Lungeinfiltrat, stadieinddeling')
        obr.obr_14 = '22002^Christensen^Jørgen^^^Dr.'

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
    """ Based on live/dk/dk-sectra.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_PACS')
        msh.sending_facility = HD(hd_1='AAUH_RAD')
        msh.receiving_application = HD(hd_1='CARESTREAM_RIS')
        msh.receiving_facility = HD(hd_1='AAUH_RAD')
        msh.date_time_of_message = '20260401100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SEC00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0803853928', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Bruun', xpn_2='Sofie', xpn_3='Esther', xpn_5='')
        pid.date_time_of_birth = '19850308'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Marselis Boulevard 1', xad_3='Roskilde', xad_5='4000', xad_6='DK')
        pid.pid_13 = '^^PH^+4556117681'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='ORT', pl_3='410', pl_4='D1')
        pv1.attending_doctor = XCN(xcn_1='12001', xcn_2='Bang', xcn_3='Andreas', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ORT')
        pv1.financial_class = FC(fc_1='AAUH202604010001')

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
        orc.placer_order_number = EI(ei_1='ORD20260401001', ei_2='CARESTREAM_RIS')
        orc.parent_order = EIP(eip_1='20260401100000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260401001', ei_2='CARESTREAM_RIS')
        obr.universal_service_identifier = CWE(cwe_1='XHIP', cwe_2='Røntgen af hofte', cwe_3='LOCAL')
        obr.observation_date_time = '20260401091000'
        obr.obr_15 = '12001^Bang^Andreas^^^Dr.'
        obr.filler_field_2 = '20260401100000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='IMGSTATUS', cwe_2='Billedstatus', cwe_3='LN')
        obx.obx_5 = 'Billeder tilgængelige i PACS. Studienummer: 1.2.826.0.1.3680043.8.1055.1.20260401.1001'
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
    """ Based on live/dk/dk-sectra.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_PACS')
        msh.sending_facility = HD(hd_1='RH_RAD')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='RIGSHOSPITALET')
        msh.date_time_of_message = '20260402140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SEC00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1205672217', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Hansen', xpn_2='Morten', xpn_3='Henning', xpn_5='')
        pid.date_time_of_birth = '19670512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Valby Langgade 141', xad_3='Aalborg Ø', xad_5='9210', xad_6='DK')
        pid.pid_13 = '^^PH^+4560835930'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='LUN', pl_3='L2031', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='22002', xcn_2='Christensen', xcn_3='Jørgen', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='LUN')
        pv1.financial_class = FC(fc_1='RH202604020001')

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
        orc.placer_order_number = EI(ei_1='ORD20260402001', ei_2='CARESTREAM_RIS')
        orc.parent_order = EIP(eip_1='20260402140000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260402001', ei_2='CARESTREAM_RIS')
        obr.universal_service_identifier = CWE(cwe_1='CTCHEST', cwe_2='CT thorax med kontrast', cwe_3='LOCAL')
        obr.observation_date_time = '20260402090000'
        obr.obr_15 = '22002^Christensen^Jørgen^^^Dr.'
        obr.placer_field_1 = '55001^Thomsen^Birgit^^^Dr.'
        obr.filler_field_1 = '20260402140000'
        obr.charge_to_practice = MOC(moc_1='P')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Foreløbig beskrivelse', cwe_3='LN')
        obx.obx_5 = 'Foreløbig: Suspekt masse i hø. overlaps posteriore segment ca. 3 cm. Mediastinal lymfadenopati. Endelig beskrivelse følger.'
        obx.observation_result_status = 'P'

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
    """ Based on live/dk/dk-sectra.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_PACS')
        msh.sending_facility = HD(hd_1='RH_RAD')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='RIGSHOSPITALET')
        msh.date_time_of_message = '20260402160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SEC00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1205672217', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Hansen', xpn_2='Morten', xpn_3='Henning', xpn_5='')
        pid.date_time_of_birth = '19670512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Valby Langgade 141', xad_3='Aalborg Ø', xad_5='9210', xad_6='DK')
        pid.pid_13 = '^^PH^+4560835930'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='LUN', pl_3='L2031', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='22002', xcn_2='Christensen', xcn_3='Jørgen', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='LUN')
        pv1.financial_class = FC(fc_1='RH202604020001')

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
        orc.placer_order_number = EI(ei_1='ORD20260402001', ei_2='CARESTREAM_RIS')
        orc.parent_order = EIP(eip_1='20260402160000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260402001', ei_2='CARESTREAM_RIS')
        obr.universal_service_identifier = CWE(cwe_1='CTCHEST', cwe_2='CT thorax med kontrast', cwe_3='LOCAL')
        obr.observation_date_time = '20260402090000'
        obr.obr_15 = '22002^Christensen^Jørgen^^^Dr.'
        obr.placer_field_1 = '55001^Thomsen^Birgit^^^Dr.'
        obr.filler_field_1 = '20260402160000'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Radiologibeskrivelse', cwe_3='LN')
        obx.obx_5 = (
            'CT thorax med iv kontrast: 3.2 cm spiculeret masse i hø. overlaps posteriore segment. Mediastinale lymfeknuder op til 18 mm i station 4R og '
            '7. Ingen pleuraeffusion. Ingen knoglemetastaser i scannet område. Lever og binyrer normalt udseende. Lung-RADS 4B.'
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
    """ Based on live/dk/dk-sectra.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_PACS')
        msh.sending_facility = HD(hd_1='RH_RAD')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='RIGSHOSPITALET')
        msh.date_time_of_message = '20260402163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SEC00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1205672217', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Hansen', xpn_2='Morten', xpn_3='Henning', xpn_5='')
        pid.date_time_of_birth = '19670512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Valby Langgade 141', xad_3='Aalborg Ø', xad_5='9210', xad_6='DK')
        pid.pid_13 = '^^PH^+4560835930'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='LUN', pl_3='L2031', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='22002', xcn_2='Christensen', xcn_3='Jørgen', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='LUN')
        pv1.financial_class = FC(fc_1='RH202604020001')

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
        orc.placer_order_number = EI(ei_1='ORD20260402003', ei_2='SECTRA_PACS')
        orc.parent_order = EIP(eip_1='20260402163000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260402003', ei_2='SECTRA_PACS')
        obr.universal_service_identifier = CWE(cwe_1='CTCHEST', cwe_2='CT thorax - endelig rapport', cwe_3='LOCAL')
        obr.observation_date_time = '20260402090000'
        obr.obr_15 = '22002^Christensen^Jørgen^^^Dr.'
        obr.placer_field_1 = '55001^Thomsen^Birgit^^^Dr.'
        obr.filler_field_1 = '20260402163000'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='CT thorax rapport', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK'
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
    """ Based on live/dk/dk-sectra.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_PACS')
        msh.sending_facility = HD(hd_1='OUH_RAD')
        msh.receiving_application = HD(hd_1='BCC')
        msh.receiving_facility = HD(hd_1='OUH')
        msh.date_time_of_message = '20260403080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'SEC00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260403080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2608729035', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Svendsen', xpn_2='Jonas', xpn_3='Carsten', xpn_5='')
        pid.date_time_of_birth = '19720826'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Strandgade 170', xad_3='Aalborg Ø', xad_5='9210', xad_6='DK')
        pid.pid_13 = '^^PH^+4585801969'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OUH', pl_2='RAD', pl_3='MR01')
        pv1.attending_doctor = XCN(xcn_1='66001', xcn_2='Bach', xcn_3='Morten', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.financial_class = FC(fc_1='OUH202604030001')
        pv1.admit_date_time = '20260403080000'

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
    """ Based on live/dk/dk-sectra.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='OUH_RAD')
        msh.receiving_application = HD(hd_1='SECTRA_PACS')
        msh.receiving_facility = HD(hd_1='OUH_RAD')
        msh.date_time_of_message = '20260403091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'SEC00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2608729035', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Svendsen', xpn_2='Jonas', xpn_3='Carsten', xpn_5='')
        pid.date_time_of_birth = '19720826'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Strandgade 170', xad_3='Aalborg Ø', xad_5='9210', xad_6='DK')
        pid.pid_13 = '^^PH^+4585801969'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OUH', pl_2='RAD', pl_3='MR01')
        pv1.attending_doctor = XCN(xcn_1='66001', xcn_2='Bach', xcn_3='Morten', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.financial_class = FC(fc_1='OUH202604030001')

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
        orc.placer_order_number = EI(ei_1='ORD20260403001', ei_2='CARESTREAM_RIS')
        orc.parent_order = EIP(eip_1='20260403091000')
        orc.orc_11 = '33003^Søndergaard^Karen^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260403001', ei_2='CARESTREAM_RIS')
        obr.universal_service_identifier = CWE(cwe_1='MRKNEE', cwe_2='MR-scanning af knæ', cwe_3='LOCAL')
        obr.observation_date_time = '20260403091000'
        obr.relevant_clinical_information = CWE(cwe_1='Postoperativ kontrol')
        obr.obr_14 = '33003^Søndergaard^Karen^^^Dr.'

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
    """ Based on live/dk/dk-sectra.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_PACS')
        msh.sending_facility = HD(hd_1='OUH_RAD')
        msh.receiving_application = HD(hd_1='CARESTREAM_RIS')
        msh.receiving_facility = HD(hd_1='OUH_RAD')
        msh.date_time_of_message = '20260403110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SEC00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2608729035', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Svendsen', xpn_2='Jonas', xpn_3='Carsten', xpn_5='')
        pid.date_time_of_birth = '19720826'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Strandgade 170', xad_3='Aalborg Ø', xad_5='9210', xad_6='DK')
        pid.pid_13 = '^^PH^+4585801969'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OUH', pl_2='RAD', pl_3='MR01')
        pv1.attending_doctor = XCN(xcn_1='66001', xcn_2='Bach', xcn_3='Morten', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.financial_class = FC(fc_1='OUH202604030001')

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
        orc.placer_order_number = EI(ei_1='ORD20260403001', ei_2='CARESTREAM_RIS')
        orc.parent_order = EIP(eip_1='20260403110000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260403001', ei_2='CARESTREAM_RIS')
        obr.universal_service_identifier = CWE(cwe_1='MRKNEE', cwe_2='MR-scanning af knæ', cwe_3='LOCAL')
        obr.observation_date_time = '20260403091000'
        obr.obr_15 = '33003^Søndergaard^Karen^^^Dr.'
        obr.filler_field_2 = '20260403110000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='IMGSTATUS', cwe_2='Billedstatus', cwe_3='LN')
        obx.obx_5 = 'MR-serier tilgængelige i PACS. 4 serier, 256 billeder. Studienummer: 1.2.826.0.1.3680043.8.1055.1.20260403.2001'
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
    """ Based on live/dk/dk-sectra.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_PACS')
        msh.sending_facility = HD(hd_1='OUH_RAD')
        msh.receiving_application = HD(hd_1='BCC')
        msh.receiving_facility = HD(hd_1='OUH')
        msh.date_time_of_message = '20260404150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SEC00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2608729035', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Svendsen', xpn_2='Jonas', xpn_3='Carsten', xpn_5='')
        pid.date_time_of_birth = '19720826'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Strandgade 170', xad_3='Aalborg Ø', xad_5='9210', xad_6='DK')
        pid.pid_13 = '^^PH^+4585801969'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OUH', pl_2='ORT', pl_3='AMB01')
        pv1.attending_doctor = XCN(xcn_1='33003', xcn_2='Søndergaard', xcn_3='Karen', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ORT')
        pv1.financial_class = FC(fc_1='OUH202604030001')

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
        orc.placer_order_number = EI(ei_1='ORD20260403002', ei_2='SECTRA_PACS')
        orc.parent_order = EIP(eip_1='20260404150000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260403002', ei_2='SECTRA_PACS')
        obr.universal_service_identifier = CWE(cwe_1='MRKNEE', cwe_2='MR knæ - komplet rapport', cwe_3='LOCAL')
        obr.observation_date_time = '20260403091000'
        obr.obr_15 = '33003^Søndergaard^Karen^^^Dr.'
        obr.placer_field_1 = '66001^Bach^Morten^^^Dr.'
        obr.filler_field_1 = '20260404150000'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Radiologibeskrivelse', cwe_3='LN')
        obx.obx_5 = (
            'MR af hø. knæ: Knæalloplastik in situ. Let periprostetisk ødem. Ingen løsning. Ingen tegn på infektion. Resterende meniskvæv normalt. Forven'
            'telige postoperative forandringer.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='MR knæ rapport', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJd'
            'Ci9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDU5NSA4NDJdCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdl'
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
    """ Based on live/dk/dk-sectra.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_PACS')
        msh.sending_facility = HD(hd_1='AAUH_RAD')
        msh.receiving_application = HD(hd_1='CARESTREAM_RIS')
        msh.receiving_facility = HD(hd_1='AAUH_RAD')
        msh.date_time_of_message = '20260405080000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12')
        msh.message_control_id = 'SEC00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='IMG20260410001', ei_2='SECTRA_PACS')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='CTABD', cwe_2='CT abdomen', cwe_5='SECTRA')
        sch.appointment_type = CWE(cwe_1='30')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='30', cne_4='20260410100000', cne_5='20260410103000')
        sch.filler_contact_person = XCN(xcn_1='55002', xcn_2='Vinther', xcn_3='Magnus', xcn_6='Dr.')
        sch.filler_contact_phone_number = XTN(xtn_3='PH', xtn_4='+4570535539')
        sch.filler_contact_address = XAD(xad_1='AAUH', xad_2='RAD', xad_3='CT01')
        sch.filler_contact_location = PL(pl_1='55002', pl_2='Vinther', pl_3='Magnus', pl_6='Dr.')
        sch.entered_by_person = XCN(xcn_3='PH', xcn_4='+4570535539')
        sch.sch_21 = 'AAUH^RAD^CT01'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1811929976', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Holm', xpn_2='Ida', xpn_3='Edith', xpn_5='')
        pid.date_time_of_birth = '19921118'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Klosterstræde 218', xad_3='Helsingør', xad_5='3000', xad_6='DK')
        pid.pid_13 = '^^PH^+4558869941'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='CTABD', cwe_2='CT abdomen med kontrast', cwe_3='LOCAL')
        ais.start_date_time = '20260410100000'
        ais.start_date_time_offset_units = CNE(cne_1='30')
        ais.duration = 'MIN'

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='AAUH', pl_2='RAD', pl_3='CT01')

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='55002', xcn_2='Vinther', xcn_3='Magnus', xcn_6='Dr.')

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [ais, ail, aip]

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
    """ Based on live/dk/dk-sectra.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_PACS')
        msh.sending_facility = HD(hd_1='AAUH_RAD')
        msh.receiving_application = HD(hd_1='CARESTREAM_RIS')
        msh.receiving_facility = HD(hd_1='AAUH_RAD')
        msh.date_time_of_message = '20260406090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S14')
        msh.message_control_id = 'SEC00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='IMG20260410001', ei_2='SECTRA_PACS')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='CTABD', cwe_2='CT abdomen', cwe_5='SECTRA')
        sch.appointment_type = CWE(cwe_1='30')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='30', cne_4='20260411100000', cne_5='20260411103000')
        sch.filler_contact_person = XCN(xcn_1='55002', xcn_2='Vinther', xcn_3='Magnus', xcn_6='Dr.')
        sch.filler_contact_phone_number = XTN(xtn_3='PH', xtn_4='+4570535539')
        sch.filler_contact_address = XAD(xad_1='AAUH', xad_2='RAD', xad_3='CT01')
        sch.filler_contact_location = PL(pl_1='55002', pl_2='Vinther', pl_3='Magnus', pl_6='Dr.')
        sch.entered_by_person = XCN(xcn_3='PH', xcn_4='+4570535539')
        sch.sch_21 = 'AAUH^RAD^CT01'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1811929976', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Holm', xpn_2='Ida', xpn_3='Edith', xpn_5='')
        pid.date_time_of_birth = '19921118'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Klosterstræde 218', xad_3='Helsingør', xad_5='3000', xad_6='DK')
        pid.pid_13 = '^^PH^+4558869941'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='CTABD', cwe_2='CT abdomen med kontrast', cwe_3='LOCAL')
        ais.start_date_time = '20260411100000'
        ais.start_date_time_offset_units = CNE(cne_1='30')
        ais.duration = 'MIN'

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='AAUH', pl_2='RAD', pl_3='CT01')

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='55002', xcn_2='Vinther', xcn_3='Magnus', xcn_6='Dr.')

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [ais, ail, aip]

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
    """ Based on live/dk/dk-sectra.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='SECTRA_PACS')
        msh.receiving_facility = HD(hd_1='AAUH_RAD')
        msh.date_time_of_message = '20260407091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'SEC00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260407091500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0803853928', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Bruun', xpn_2='Sofie', xpn_3='Esther', xpn_5='')
        pid.date_time_of_birth = '19850308'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Boulevarden 6', xad_3='København N', xad_5='2200', xad_6='DK')
        pid.pid_13 = '^^PH^+4587591439~^^CP^+4521353195'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='ORT', pl_3='410', pl_4='D1')
        pv1.attending_doctor = XCN(xcn_1='12001', xcn_2='Bang', xcn_3='Andreas', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ORT')
        pv1.financial_class = FC(fc_1='AAUH202604010001')
        pv1.admit_date_time = '20260407091500'

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/dk/dk-sectra.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='SECTRA_PACS')
        msh.receiving_facility = HD(hd_1='AAUH_RAD')
        msh.date_time_of_message = '20260408060000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'SEC00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260408060000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0803853928', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Bruun', xpn_2='Sofie', xpn_3='Esther', xpn_5='')
        pid.date_time_of_birth = '19850308'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Boulevarden 6', xad_3='København N', xad_5='2200', xad_6='DK')
        pid.pid_13 = '^^PH^+4587591439'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='2124752087', cx_4='CPR', cx_5='NNDN')
        mrg.prior_patient_account_number = CX(cx_1='AAUH202602010001')

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
    """ Based on live/dk/dk-sectra.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='OUH_RAD')
        msh.receiving_application = HD(hd_1='SECTRA_PACS')
        msh.receiving_facility = HD(hd_1='OUH_RAD')
        msh.date_time_of_message = '20260409091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'SEC00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0707651428', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Iversen', xpn_2='Line', xpn_3='Edith', xpn_5='')
        pid.date_time_of_birth = '19650707'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hasserisgade 83', xad_3='Aarhus V', xad_5='8210', xad_6='DK')
        pid.pid_13 = '^^PH^+4534956124'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OUH', pl_2='MED', pl_3='A305', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='77002', xcn_2='Jensen', xcn_3='Kasper', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.financial_class = FC(fc_1='OUH202604070001')

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
        orc.placer_order_number = EI(ei_1='ORD20260409001', ei_2='CARESTREAM_RIS')
        orc.parent_order = EIP(eip_1='20260409091000')
        orc.orc_11 = '77002^Jensen^Kasper^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260409001', ei_2='CARESTREAM_RIS')
        obr.universal_service_identifier = CWE(cwe_1='ULLEVER', cwe_2='Ultralyd lever og galdeveje', cwe_3='LOCAL')
        obr.observation_date_time = '20260409091000'
        obr.relevant_clinical_information = CWE(cwe_1='Steatose-kontrol')
        obr.obr_14 = '77002^Jensen^Kasper^^^Dr.'

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
    """ Based on live/dk/dk-sectra.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_PACS')
        msh.sending_facility = HD(hd_1='OUH_RAD')
        msh.receiving_application = HD(hd_1='BCC')
        msh.receiving_facility = HD(hd_1='OUH')
        msh.date_time_of_message = '20260409141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SEC00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0707651428', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Iversen', xpn_2='Line', xpn_3='Edith', xpn_5='')
        pid.date_time_of_birth = '19650707'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hasserisgade 83', xad_3='Aarhus V', xad_5='8210', xad_6='DK')
        pid.pid_13 = '^^PH^+4534956124'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OUH', pl_2='MED', pl_3='A305', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='77002', xcn_2='Jensen', xcn_3='Kasper', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.financial_class = FC(fc_1='OUH202604070001')

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
        orc.placer_order_number = EI(ei_1='ORD20260409001', ei_2='CARESTREAM_RIS')
        orc.parent_order = EIP(eip_1='20260409141500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260409001', ei_2='CARESTREAM_RIS')
        obr.universal_service_identifier = CWE(cwe_1='ULLEVER', cwe_2='Ultralyd lever og galdeveje', cwe_3='LOCAL')
        obr.observation_date_time = '20260409091000'
        obr.obr_15 = '77002^Jensen^Kasper^^^Dr.'
        obr.placer_field_1 = '88001^Svendsen^Niels^^^Dr.'
        obr.filler_field_1 = '20260409141500'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Radiologibeskrivelse', cwe_3='LN')
        obx.obx_5 = (
            'UL af lever: Leveren normalstørrelse, 14.5 cm. Let forøget ekkogenicitet forenelig med let steatose, uændret sammenlignet med undersøgelse f'
            'ra 20251015. Ingen fokale læsioner. Galdeblæren normal. Galdegange ikke dilaterede. Konkl: Stationær let steatose.'
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
    """ Based on live/dk/dk-sectra.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='RH_RAD')
        msh.receiving_application = HD(hd_1='SECTRA_PACS')
        msh.receiving_facility = HD(hd_1='RH_RAD')
        msh.date_time_of_message = '20260410083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'SEC00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1205672217', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Hansen', xpn_2='Morten', xpn_3='Henning', xpn_5='')
        pid.date_time_of_birth = '19670512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Valby Langgade 141', xad_3='Aalborg Ø', xad_5='9210', xad_6='DK')
        pid.pid_13 = '^^PH^+4560835930'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='LUN', pl_3='L2031', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='22002', xcn_2='Christensen', xcn_3='Jørgen', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='LUN')
        pv1.financial_class = FC(fc_1='RH202604020001')

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
        orc.placer_order_number = EI(ei_1='ORD20260410001', ei_2='CARESTREAM_RIS')
        orc.parent_order = EIP(eip_1='20260410083000')
        orc.orc_11 = '22002^Christensen^Jørgen^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260410001', ei_2='CARESTREAM_RIS')
        obr.universal_service_identifier = CWE(cwe_1='PETCT', cwe_2='FDG PET-CT helkrop', cwe_3='LOCAL')
        obr.observation_date_time = '20260410083000'
        obr.relevant_clinical_information = CWE(cwe_1='Lungecancer stadieinddeling')
        obr.obr_14 = '22002^Christensen^Jørgen^^^Dr.'

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
    """ Based on live/dk/dk-sectra.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_PACS')
        msh.sending_facility = HD(hd_1='RH_RAD')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='RIGSHOSPITALET')
        msh.date_time_of_message = '20260411141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SEC00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1205672217', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Hansen', xpn_2='Morten', xpn_3='Henning', xpn_5='')
        pid.date_time_of_birth = '19670512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Valby Langgade 141', xad_3='Aalborg Ø', xad_5='9210', xad_6='DK')
        pid.pid_13 = '^^PH^+4560835930'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='LUN', pl_3='L2031', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='22002', xcn_2='Christensen', xcn_3='Jørgen', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='LUN')
        pv1.financial_class = FC(fc_1='RH202604020001')

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
        orc.placer_order_number = EI(ei_1='ORD20260410001', ei_2='CARESTREAM_RIS')
        orc.parent_order = EIP(eip_1='20260411141500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260410001', ei_2='CARESTREAM_RIS')
        obr.universal_service_identifier = CWE(cwe_1='PETCT', cwe_2='FDG PET-CT helkrop', cwe_3='LOCAL')
        obr.observation_date_time = '20260410083000'
        obr.obr_15 = '22002^Christensen^Jørgen^^^Dr.'
        obr.placer_field_1 = '55001^Thomsen^Birgit^^^Dr.'
        obr.filler_field_1 = '20260411141500'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Radiologibeskrivelse', cwe_3='LN')
        obx.obx_5 = (
            'FDG PET-CT helkrop: Hypermetabol masse i hø. overlaps (SUVmax 11.8). FDG-avide mediastinale lymfeknuder station 4R (SUVmax 8.2) og 7 (SUVmax'
            ' 7.6). Ingen fjernmetastaser. Stadie: cT2aN2M0, IIIA.'
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
    """ Based on live/dk/dk-sectra.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_PACS')
        msh.sending_facility = HD(hd_1='AAUH_RAD')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260412120000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02')
        msh.message_control_id = 'SEC00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260412120000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0803853928', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Bruun', xpn_2='Sofie', xpn_3='Esther', xpn_5='')
        pid.date_time_of_birth = '19850308'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Boulevarden 6', xad_3='København N', xad_5='2200', xad_6='DK')
        pid.pid_13 = '^^PH^+4587591439'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='ORT', pl_3='410', pl_4='D1')
        pv1.attending_doctor = XCN(xcn_1='12001', xcn_2='Bang', xcn_3='Andreas', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ORT')
        pv1.financial_class = FC(fc_1='AAUH202604010001')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='AD', cwe_2='Addendum')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260412120000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='44001', xcn_2='Vinther', xcn_3='Magnus', xcn_6='Dr.')
        txa.transcription_date_time = '20260412120000'
        txa.unique_document_number = EI(ei_1='DOC20260412001')
        txa.document_confidentiality_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='NOTE', cwe_2='Addendum til røntgenbeskrivelse', cwe_3='LN')
        obx.obx_5 = (
            'Addendum: Ved fornyet gennemgang af røntgen hofte bemærkes desuden let osteoporotisk knoglestruktur i proximale femur. Anbefaler DEXA-scanni'
            'ng til vurdering af knogletæthed.'
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
    """ Based on live/dk/dk-sectra.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='RIGSHOSPITALET')
        msh.receiving_application = HD(hd_1='SECTRA_PACS')
        msh.receiving_facility = HD(hd_1='RH_RAD')
        msh.date_time_of_message = '20260413070000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'SEC00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260413070000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2406873706', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Jensen', xpn_2='Britt', xpn_3='Ellen', xpn_5='')
        pid.date_time_of_birth = '19870624'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Park Allé 130', xad_3='Odense V', xad_5='5210', xad_6='DK')
        pid.pid_13 = '^^PH^+4586449935~^^CP^+4551529964'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='NEU', pl_3='N1041', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='33003', xcn_2='Berg', xcn_3='Flemming', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='NEU')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='33003', xcn_2='Berg', xcn_3='Flemming', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='RH202604130001')
        pv1.prior_temporary_location = PL(pl_1='20260413070000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Subaraknoidal blødning')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
