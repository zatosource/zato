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
from zato.hl7v2.v2_9.groups import MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient
from zato.hl7v2.v2_9.messages import ADT_A01, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, EVN, MSH, OBR, OBX, ORC, PID, PV1, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('dk', 'dk-carestream-ris.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/dk/dk-carestream-ris.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='CARESTREAM_RIS')
        msh.receiving_facility = HD(hd_1='AAUH_RAD')
        msh.date_time_of_message = '20260401090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'CSRIS00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2904851778', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Rasmussen', xpn_2='Line', xpn_3='Viola', xpn_5='')
        pid.date_time_of_birth = '19850429'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tolderlundsvej 42', xad_3='København S', xad_5='2300', xad_6='DK')
        pid.pid_13 = '^^PH^+4538399026'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='ORT', pl_3='410', pl_4='D1')
        pv1.attending_doctor = XCN(xcn_1='12001', xcn_2='Bruun', xcn_3='Mette', xcn_6='Dr.')
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
        orc.placer_order_number = EI(ei_1='ORD20260401001', ei_2='COLUMNA_CIS')
        orc.parent_order = EIP(eip_1='20260401090000')
        orc.orc_11 = '12001^Bruun^Mette^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260401001', ei_2='COLUMNA_CIS')
        obr.universal_service_identifier = CWE(cwe_1='XHIP', cwe_2='Røntgen af hofte', cwe_3='LOCAL')
        obr.observation_date_time = '20260401090000'
        obr.relevant_clinical_information = CWE(cwe_1='Hoftesmerter efter fald, mistanke om fraktur')
        obr.obr_14 = '12001^Bruun^Mette^^^Dr.'

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
    """ Based on live/dk/dk-carestream-ris.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='RIGSHOSPITALET')
        msh.receiving_application = HD(hd_1='CARESTREAM_RIS')
        msh.receiving_facility = HD(hd_1='RH_RAD')
        msh.date_time_of_message = '20260402083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'CSRIS00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0508671155', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Skov', xpn_2='Henrik', xpn_3='Bo', xpn_5='')
        pid.date_time_of_birth = '19670805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gammel Kongevej 176', xad_3='Risskov', xad_5='8240', xad_6='DK')
        pid.pid_13 = '^^PH^+4534278055'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='LUN', pl_3='L2031', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='22002', xcn_2='Søndergaard', xcn_3='Lisbeth', xcn_6='Dr.')
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
        orc.placer_order_number = EI(ei_1='ORD20260402001', ei_2='EPIC')
        orc.parent_order = EIP(eip_1='20260402083000')
        orc.orc_11 = '22002^Søndergaard^Lisbeth^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260402001', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='CTCHEST', cwe_2='CT thorax med kontrast', cwe_3='LOCAL')
        obr.observation_date_time = '20260402083000'
        obr.relevant_clinical_information = CWE(cwe_1='Lungeinfiltrat, mistanke om malignitet')
        obr.obr_14 = '22002^Søndergaard^Lisbeth^^^Dr.'

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
    """ Based on live/dk/dk-carestream-ris.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BCC')
        msh.sending_facility = HD(hd_1='OUH')
        msh.receiving_application = HD(hd_1='CARESTREAM_RIS')
        msh.receiving_facility = HD(hd_1='OUH_RAD')
        msh.date_time_of_message = '20260403091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'CSRIS00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1809721083', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Nørgaard', xpn_2='Tobias', xpn_3='Viggo', xpn_5='')
        pid.date_time_of_birth = '19720918'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Borgergade 46', xad_3='Silkeborg', xad_5='8600', xad_6='DK')
        pid.pid_13 = '^^PH^+4563876183'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OUH', pl_2='ORT', pl_3='AMB01')
        pv1.attending_doctor = XCN(xcn_1='33003', xcn_2='Krogh', xcn_3='Tina', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ORT')
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
        orc.placer_order_number = EI(ei_1='ORD20260403001', ei_2='BCC')
        orc.parent_order = EIP(eip_1='20260403091000')
        orc.orc_11 = '33003^Krogh^Tina^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260403001', ei_2='BCC')
        obr.universal_service_identifier = CWE(cwe_1='MRKNEE', cwe_2='MR-scanning af knæ', cwe_3='LOCAL')
        obr.observation_date_time = '20260403091000'
        obr.relevant_clinical_information = CWE(cwe_1='Kontrol efter knæalloplastik, smerter')
        obr.obr_14 = '33003^Krogh^Tina^^^Dr.'

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
    """ Based on live/dk/dk-carestream-ris.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='AAUH_RAD')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260401141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CSRIS00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2904851778', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Rasmussen', xpn_2='Line', xpn_3='Viola', xpn_5='')
        pid.date_time_of_birth = '19850429'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tolderlundsvej 42', xad_3='København S', xad_5='2300', xad_6='DK')
        pid.pid_13 = '^^PH^+4538399026'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='ORT', pl_3='410', pl_4='D1')
        pv1.attending_doctor = XCN(xcn_1='12001', xcn_2='Bruun', xcn_3='Mette', xcn_6='Dr.')
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
        orc.placer_order_number = EI(ei_1='ORD20260401001', ei_2='COLUMNA_CIS')
        orc.parent_order = EIP(eip_1='20260401141500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260401001', ei_2='COLUMNA_CIS')
        obr.universal_service_identifier = CWE(cwe_1='XHIP', cwe_2='Røntgen af hofte', cwe_3='LOCAL')
        obr.observation_date_time = '20260401090000'
        obr.obr_15 = '12001^Bruun^Mette^^^Dr.'
        obr.placer_field_1 = '44001^Iversen^Erik^^^Dr.'
        obr.filler_field_1 = '20260401141500'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Radiologibeskrivelse', cwe_3='LN')
        obx.obx_5 = 'Røntgen af hø. hofte AP og lateral: Collumfraktur, Garden type III. Dislokeret. Anbefaler kirurgisk intervention.'
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
    """ Based on live/dk/dk-carestream-ris.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='RH_RAD')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='RIGSHOSPITALET')
        msh.date_time_of_message = '20260402153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CSRIS00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0508671155', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Skov', xpn_2='Henrik', xpn_3='Bo', xpn_5='')
        pid.date_time_of_birth = '19670805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gammel Kongevej 176', xad_3='Risskov', xad_5='8240', xad_6='DK')
        pid.pid_13 = '^^PH^+4534278055'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='LUN', pl_3='L2031', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='22002', xcn_2='Søndergaard', xcn_3='Lisbeth', xcn_6='Dr.')
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
        orc.placer_order_number = EI(ei_1='ORD20260402001', ei_2='EPIC')
        orc.parent_order = EIP(eip_1='20260402153000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260402001', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='CTCHEST', cwe_2='CT thorax med kontrast', cwe_3='LOCAL')
        obr.observation_date_time = '20260402083000'
        obr.obr_15 = '22002^Søndergaard^Lisbeth^^^Dr.'
        obr.placer_field_1 = '55001^Frandsen^Jonas^^^Dr.'
        obr.filler_field_1 = '20260402153000'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Radiologibeskrivelse', cwe_3='LN')
        obx.obx_5 = (
            'CT thorax med iv kontrast: 3.2 cm spiculeret masse i hø. overlaps posteriore segment. Mediastinal lymfadenopati. Ingen pleuraeffusion. Ingen'
            ' knoglemetastaser. RADS 4B. Anbefaler bronkoskopi med biopsi.'
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
    """ Based on live/dk/dk-carestream-ris.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='RH_RAD')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='RIGSHOSPITALET')
        msh.date_time_of_message = '20260402160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CSRIS00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0508671155', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Skov', xpn_2='Henrik', xpn_3='Bo', xpn_5='')
        pid.date_time_of_birth = '19670805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gammel Kongevej 176', xad_3='Risskov', xad_5='8240', xad_6='DK')
        pid.pid_13 = '^^PH^+4534278055'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='LUN', pl_3='L2031', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='22002', xcn_2='Søndergaard', xcn_3='Lisbeth', xcn_6='Dr.')
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
        orc.placer_order_number = EI(ei_1='ORD20260402002', ei_2='CARESTREAM_RIS')
        orc.parent_order = EIP(eip_1='20260402160000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260402002', ei_2='CARESTREAM_RIS')
        obr.universal_service_identifier = CWE(cwe_1='CTCHEST', cwe_2='CT thorax - komplet rapport', cwe_3='LOCAL')
        obr.observation_date_time = '20260402083000'
        obr.obr_15 = '22002^Søndergaard^Lisbeth^^^Dr.'
        obr.placer_field_1 = '55001^Frandsen^Jonas^^^Dr.'
        obr.filler_field_1 = '20260402160000'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Radiologirapport', cwe_3='LN')
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
    """ Based on live/dk/dk-carestream-ris.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='OUH_RAD')
        msh.receiving_application = HD(hd_1='BCC')
        msh.receiving_facility = HD(hd_1='OUH')
        msh.date_time_of_message = '20260404141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CSRIS00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1809721083', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Nørgaard', xpn_2='Tobias', xpn_3='Viggo', xpn_5='')
        pid.date_time_of_birth = '19720918'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Borgergade 46', xad_3='Silkeborg', xad_5='8600', xad_6='DK')
        pid.pid_13 = '^^PH^+4563876183'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OUH', pl_2='ORT', pl_3='AMB01')
        pv1.attending_doctor = XCN(xcn_1='33003', xcn_2='Krogh', xcn_3='Tina', xcn_6='Dr.')
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
        orc.placer_order_number = EI(ei_1='ORD20260403001', ei_2='BCC')
        orc.parent_order = EIP(eip_1='20260404141500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260403001', ei_2='BCC')
        obr.universal_service_identifier = CWE(cwe_1='MRKNEE', cwe_2='MR-scanning af knæ', cwe_3='LOCAL')
        obr.observation_date_time = '20260403091000'
        obr.obr_15 = '33003^Krogh^Tina^^^Dr.'
        obr.placer_field_1 = '66001^Lund^Bjarne^^^Dr.'
        obr.filler_field_1 = '20260404141500'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Radiologibeskrivelse', cwe_3='LN')
        obx.obx_5 = (
            'MR af hø. knæ: Knæalloplastik in situ uden løsning. Let ødem i omgivende bløddele. Ingen tegn på infektion. Meniskresterne normalt udseende.'
            ' Konkl: Forventelige postoperative forandringer.'
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
    """ Based on live/dk/dk-carestream-ris.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='AAUH_RAD')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260405080000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12')
        msh.message_control_id = 'CSRIS00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='RAD20260410001', ei_2='CARESTREAM_RIS')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='XTHORAX', cwe_2='Røntgen af thorax', cwe_5='CSRIS')
        sch.appointment_type = CWE(cwe_1='15')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='15', cne_4='20260410090000', cne_5='20260410091500')
        sch.filler_contact_person = XCN(xcn_1='44001', xcn_2='Iversen', xcn_3='Erik', xcn_6='Dr.')
        sch.filler_contact_phone_number = XTN(xtn_3='PH', xtn_4='+4595776110')
        sch.filler_contact_address = XAD(xad_1='AAUH', xad_2='RAD', xad_3='XR01')
        sch.filler_contact_location = PL(pl_1='44001', pl_2='Iversen', pl_3='Erik', pl_6='Dr.')
        sch.entered_by_person = XCN(xcn_3='PH', xcn_4='+4595776110')
        sch.sch_21 = 'AAUH^RAD^XR01'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1011922930', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Olsen', xpn_2='Louise', xpn_3='Ellen', xpn_5='')
        pid.date_time_of_birth = '19921110'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Prinsensgade 19', xad_3='Viborg', xad_5='8800', xad_6='DK')
        pid.pid_13 = '^^PH^+4568614245'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='XTHORAX', cwe_2='Røntgen af thorax', cwe_3='LOCAL')
        ais.start_date_time = '20260410090000'
        ais.start_date_time_offset_units = CNE(cne_1='15')
        ais.duration = 'MIN'

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='AAUH', pl_2='RAD', pl_3='XR01')

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='44001', xcn_2='Iversen', xcn_3='Erik', xcn_6='Dr.')

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [ais, ail, aip]

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
    """ Based on live/dk/dk-carestream-ris.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='AAUH_RAD')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260406090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S14')
        msh.message_control_id = 'CSRIS00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='RAD20260410001', ei_2='CARESTREAM_RIS')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='XTHORAX', cwe_2='Røntgen af thorax', cwe_5='CSRIS')
        sch.appointment_type = CWE(cwe_1='15')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='15', cne_4='20260411100000', cne_5='20260411101500')
        sch.filler_contact_person = XCN(xcn_1='44001', xcn_2='Iversen', xcn_3='Erik', xcn_6='Dr.')
        sch.filler_contact_phone_number = XTN(xtn_3='PH', xtn_4='+4595776110')
        sch.filler_contact_address = XAD(xad_1='AAUH', xad_2='RAD', xad_3='XR01')
        sch.filler_contact_location = PL(pl_1='44001', pl_2='Iversen', pl_3='Erik', pl_6='Dr.')
        sch.entered_by_person = XCN(xcn_3='PH', xcn_4='+4595776110')
        sch.sch_21 = 'AAUH^RAD^XR01'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1011922930', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Olsen', xpn_2='Louise', xpn_3='Ellen', xpn_5='')
        pid.date_time_of_birth = '19921110'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Prinsensgade 19', xad_3='Viborg', xad_5='8800', xad_6='DK')
        pid.pid_13 = '^^PH^+4568614245'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='XTHORAX', cwe_2='Røntgen af thorax', cwe_3='LOCAL')
        ais.start_date_time = '20260411100000'
        ais.start_date_time_offset_units = CNE(cne_1='15')
        ais.duration = 'MIN'

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='AAUH', pl_2='RAD', pl_3='XR01')

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='44001', xcn_2='Iversen', xcn_3='Erik', xcn_6='Dr.')

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [ais, ail, aip]

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
    """ Based on live/dk/dk-carestream-ris.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BCC')
        msh.sending_facility = HD(hd_1='OUH')
        msh.receiving_application = HD(hd_1='CARESTREAM_RIS')
        msh.receiving_facility = HD(hd_1='OUH_RAD')
        msh.date_time_of_message = '20260407091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'CSRIS00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1410659824', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Rasmussen', xpn_2='Julie', xpn_3='Margrethe', xpn_5='')
        pid.date_time_of_birth = '19651014'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Frederikssundsvej 100', xad_3='Odense V', xad_5='5210', xad_6='DK')
        pid.pid_13 = '^^PH^+4535612249'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OUH', pl_2='MED', pl_3='A305', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='77002', xcn_2='Thomsen', xcn_3='Clara', xcn_6='Dr.')
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
        orc.placer_order_number = EI(ei_1='ORD20260407001', ei_2='BCC')
        orc.parent_order = EIP(eip_1='20260407091000')
        orc.orc_11 = '77002^Thomsen^Clara^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260407001', ei_2='BCC')
        obr.universal_service_identifier = CWE(cwe_1='ULLEVER', cwe_2='Ultralyd af lever og galdeveje', cwe_3='LOCAL')
        obr.observation_date_time = '20260407091000'
        obr.relevant_clinical_information = CWE(cwe_1='Forhøjede levertal, udredning')
        obr.obr_14 = '77002^Thomsen^Clara^^^Dr.'

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
    """ Based on live/dk/dk-carestream-ris.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='OUH_RAD')
        msh.receiving_application = HD(hd_1='BCC')
        msh.receiving_facility = HD(hd_1='OUH')
        msh.date_time_of_message = '20260407141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CSRIS00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1410659824', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Rasmussen', xpn_2='Julie', xpn_3='Margrethe', xpn_5='')
        pid.date_time_of_birth = '19651014'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Frederikssundsvej 100', xad_3='Odense V', xad_5='5210', xad_6='DK')
        pid.pid_13 = '^^PH^+4535612249'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OUH', pl_2='MED', pl_3='A305', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='77002', xcn_2='Thomsen', xcn_3='Clara', xcn_6='Dr.')
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
        orc.placer_order_number = EI(ei_1='ORD20260407001', ei_2='BCC')
        orc.parent_order = EIP(eip_1='20260407141500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260407001', ei_2='BCC')
        obr.universal_service_identifier = CWE(cwe_1='ULLEVER', cwe_2='Ultralyd af lever og galdeveje', cwe_3='LOCAL')
        obr.observation_date_time = '20260407091000'
        obr.obr_15 = '77002^Thomsen^Clara^^^Dr.'
        obr.placer_field_1 = '88001^Nielsen^Anne^^^Dr.'
        obr.filler_field_1 = '20260407141500'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Radiologibeskrivelse', cwe_3='LN')
        obx.obx_5 = (
            'UL af lever og galdeveje: Leveren let forstørret, hepatomegali. Diffust forøget ekkogenicitet forenelig med steatose. Galdeblæren normal. In'
            'gen dilatation af galdegange. Ingen frie ascites. Konkl: Hepatomegali med steatose.'
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
    """ Based on live/dk/dk-carestream-ris.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='RIGSHOSPITALET')
        msh.receiving_application = HD(hd_1='CARESTREAM_RIS')
        msh.receiving_facility = HD(hd_1='RH_RAD')
        msh.date_time_of_message = '20260408083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'CSRIS00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0508671155', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Skov', xpn_2='Henrik', xpn_3='Bo', xpn_5='')
        pid.date_time_of_birth = '19670805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gammel Kongevej 176', xad_3='Risskov', xad_5='8240', xad_6='DK')
        pid.pid_13 = '^^PH^+4534278055'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='LUN', pl_3='L2031', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='22002', xcn_2='Søndergaard', xcn_3='Lisbeth', xcn_6='Dr.')
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
        orc.placer_order_number = EI(ei_1='ORD20260408001', ei_2='EPIC')
        orc.parent_order = EIP(eip_1='20260408083000')
        orc.orc_11 = '22002^Søndergaard^Lisbeth^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260408001', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='PETCT', cwe_2='FDG PET-CT helkrop', cwe_3='LOCAL')
        obr.observation_date_time = '20260408083000'
        obr.relevant_clinical_information = CWE(cwe_1='Stadieinddeling af lungekarcinom')
        obr.obr_14 = '22002^Søndergaard^Lisbeth^^^Dr.'

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
    """ Based on live/dk/dk-carestream-ris.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='RH_RAD')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='RIGSHOSPITALET')
        msh.date_time_of_message = '20260409141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CSRIS00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0508671155', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Skov', xpn_2='Henrik', xpn_3='Bo', xpn_5='')
        pid.date_time_of_birth = '19670805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gammel Kongevej 176', xad_3='Risskov', xad_5='8240', xad_6='DK')
        pid.pid_13 = '^^PH^+4534278055'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='LUN', pl_3='L2031', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='22002', xcn_2='Søndergaard', xcn_3='Lisbeth', xcn_6='Dr.')
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
        orc.placer_order_number = EI(ei_1='ORD20260408001', ei_2='EPIC')
        orc.parent_order = EIP(eip_1='20260409141500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260408001', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='PETCT', cwe_2='FDG PET-CT helkrop', cwe_3='LOCAL')
        obr.observation_date_time = '20260408083000'
        obr.obr_15 = '22002^Søndergaard^Lisbeth^^^Dr.'
        obr.placer_field_1 = '55001^Frandsen^Jonas^^^Dr.'
        obr.filler_field_1 = '20260409141500'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Radiologibeskrivelse', cwe_3='LN')
        obx.obx_5 = (
            'FDG PET-CT helkrop: Hypermetabol masse i hø. overlaps (SUVmax 12.4). FDG-avide mediastinale lymfeknuder (stationer 4R og 7). Ingen fjernmeta'
            'staser. Lever, binyrer, knogler og hjerne uden patologisk FDG-optag. Stadie: cT2aN2M0, IIIA.'
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
    """ Based on live/dk/dk-carestream-ris.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='RH_RAD')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='RIGSHOSPITALET')
        msh.date_time_of_message = '20260409150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CSRIS00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0508671155', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Skov', xpn_2='Henrik', xpn_3='Bo', xpn_5='')
        pid.date_time_of_birth = '19670805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gammel Kongevej 176', xad_3='Risskov', xad_5='8240', xad_6='DK')
        pid.pid_13 = '^^PH^+4534278055'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='LUN', pl_3='L2031', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='22002', xcn_2='Søndergaard', xcn_3='Lisbeth', xcn_6='Dr.')
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
        orc.placer_order_number = EI(ei_1='ORD20260409001', ei_2='CARESTREAM_RIS')
        orc.parent_order = EIP(eip_1='20260409150000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260409001', ei_2='CARESTREAM_RIS')
        obr.universal_service_identifier = CWE(cwe_1='PETCT', cwe_2='FDG PET-CT helkrop - komplet rapport', cwe_3='LOCAL')
        obr.observation_date_time = '20260408083000'
        obr.obr_15 = '22002^Søndergaard^Lisbeth^^^Dr.'
        obr.placer_field_1 = '55001^Frandsen^Jonas^^^Dr.'
        obr.filler_field_1 = '20260409150000'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='PET-CT rapport', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJd'
            'Ci9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDU5NSA4NDJdCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdl'
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
    """ Based on live/dk/dk-carestream-ris.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='HERLEV_HOSPITAL')
        msh.receiving_application = HD(hd_1='CARESTREAM_RIS')
        msh.receiving_facility = HD(hd_1='HEH_RAD')
        msh.date_time_of_message = '20260410083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'CSRIS00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1303666698', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Friis', xpn_2='Line', xpn_3='Asta', xpn_5='')
        pid.date_time_of_birth = '19660313'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Vesterbrogade 146', xad_3='Valby', xad_5='2500', xad_6='DK')
        pid.pid_13 = '^^PH^+4550711199'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HEH', pl_2='RAD', pl_3='MAMMO')
        pv1.attending_doctor = XCN(xcn_1='99001', xcn_2='Johansen', xcn_3='Clara', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.financial_class = FC(fc_1='HEH202604100001')

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
        orc.placer_order_number = EI(ei_1='ORD20260410001', ei_2='EPIC')
        orc.parent_order = EIP(eip_1='20260410083000')
        orc.orc_11 = '99001^Johansen^Clara^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260410001', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='MAMMO', cwe_2='Mammografi bilateral', cwe_3='LOCAL')
        obr.observation_date_time = '20260410083000'
        obr.relevant_clinical_information = CWE(cwe_1='Screeningmammografi, >50 år')
        obr.obr_14 = '99001^Johansen^Clara^^^Dr.'

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
    """ Based on live/dk/dk-carestream-ris.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='HEH_RAD')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='HERLEV_HOSPITAL')
        msh.date_time_of_message = '20260410141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CSRIS00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1303666698', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Friis', xpn_2='Line', xpn_3='Asta', xpn_5='')
        pid.date_time_of_birth = '19660313'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Vesterbrogade 146', xad_3='Valby', xad_5='2500', xad_6='DK')
        pid.pid_13 = '^^PH^+4550711199'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HEH', pl_2='RAD', pl_3='MAMMO')
        pv1.attending_doctor = XCN(xcn_1='99001', xcn_2='Johansen', xcn_3='Clara', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.financial_class = FC(fc_1='HEH202604100001')

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
        orc.placer_order_number = EI(ei_1='ORD20260410001', ei_2='EPIC')
        orc.parent_order = EIP(eip_1='20260410141500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260410001', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='MAMMO', cwe_2='Mammografi bilateral', cwe_3='LOCAL')
        obr.observation_date_time = '20260410083000'
        obr.obr_15 = '99001^Johansen^Clara^^^Dr.'
        obr.placer_field_1 = '99002^Holm^Rikke^^^Dr.'
        obr.filler_field_1 = '20260410141500'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Radiologibeskrivelse', cwe_3='LN')
        obx.obx_5 = (
            'Mammografi bilateral: Heterogent tæt brystvæv. Ingen suspekte masser eller mikroforkalkninger. Ingen arkitekturforstyrrelser. BI-RADS 2 bila'
            'teralt. Rutinekontrol anbefales om 2 år.'
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
    """ Based on live/dk/dk-carestream-ris.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='AAUH_RAD')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260411080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'CSRIS00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260411080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1011922930', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Olsen', xpn_2='Louise', xpn_3='Ellen', xpn_5='')
        pid.date_time_of_birth = '19921110'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Prinsensgade 19', xad_3='Viborg', xad_5='8800', xad_6='DK')
        pid.pid_13 = '^^PH^+4568614245'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='RAD', pl_3='XR01')
        pv1.attending_doctor = XCN(xcn_1='44001', xcn_2='Iversen', xcn_3='Erik', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.financial_class = FC(fc_1='AAUH202604110001')
        pv1.admit_date_time = '20260411080000'

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/dk/dk-carestream-ris.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='CARESTREAM_RIS')
        msh.receiving_facility = HD(hd_1='AAUH_RAD')
        msh.date_time_of_message = '20260412083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'CSRIS00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0502779886', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Henriksen', xpn_2='Freja', xpn_3='Christina', xpn_5='')
        pid.date_time_of_birth = '19770205'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Park Allé 75', xad_3='Viborg', xad_5='8800', xad_6='DK')
        pid.pid_13 = '^^PH^+4554254594'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='END', pl_3='AMB01')
        pv1.attending_doctor = XCN(xcn_1='12001', xcn_2='Bruun', xcn_3='Mette', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='END')
        pv1.financial_class = FC(fc_1='AAUH202604120001')

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
        orc.placer_order_number = EI(ei_1='ORD20260412001', ei_2='COLUMNA_CIS')
        orc.parent_order = EIP(eip_1='20260412083000')
        orc.orc_11 = '12001^Bruun^Mette^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260412001', ei_2='COLUMNA_CIS')
        obr.universal_service_identifier = CWE(cwe_1='DEXA', cwe_2='DEXA-scanning, lumbal og hofte', cwe_3='LOCAL')
        obr.observation_date_time = '20260412083000'
        obr.relevant_clinical_information = CWE(cwe_1='Osteoporose-udredning')
        obr.obr_14 = '12001^Bruun^Mette^^^Dr.'

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
    """ Based on live/dk/dk-carestream-ris.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='AAUH_RAD')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260412141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CSRIS00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0502779886', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Henriksen', xpn_2='Freja', xpn_3='Christina', xpn_5='')
        pid.date_time_of_birth = '19770205'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Park Allé 75', xad_3='Viborg', xad_5='8800', xad_6='DK')
        pid.pid_13 = '^^PH^+4554254594'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='END', pl_3='AMB01')
        pv1.attending_doctor = XCN(xcn_1='12001', xcn_2='Bruun', xcn_3='Mette', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='END')
        pv1.financial_class = FC(fc_1='AAUH202604120001')

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
        orc.placer_order_number = EI(ei_1='ORD20260412001', ei_2='COLUMNA_CIS')
        orc.parent_order = EIP(eip_1='20260412141500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260412001', ei_2='COLUMNA_CIS')
        obr.universal_service_identifier = CWE(cwe_1='DEXA', cwe_2='DEXA-scanning, lumbal og hofte', cwe_3='LOCAL')
        obr.observation_date_time = '20260412083000'
        obr.obr_15 = '12001^Bruun^Mette^^^Dr.'
        obr.placer_field_1 = '44001^Iversen^Erik^^^Dr.'
        obr.filler_field_1 = '20260412141500'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Radiologibeskrivelse', cwe_3='LN')
        obx.obx_5 = 'DEXA-scanning: L1-L4 T-score -2.8 (osteoporose). Collum femoris T-score -2.1 (osteopeni). Anbefaler behandling med bisfosfonat.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='TSCORE_L', cwe_2='T-score lumbal', cwe_3='LN')
        obx_2.obx_5 = '-2.8'
        obx_2.reference_range = '>-1.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='TSCORE_H', cwe_2='T-score collum femoris', cwe_3='LN')
        obx_3.obx_5 = '-2.1'
        obx_3.reference_range = '>-1.0'
        obx_3.interpretation_codes = CWE(cwe_1='L')
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
    """ Based on live/dk/dk-carestream-ris.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='RH_RAD')
        msh.receiving_application = HD(hd_1='DOKUMENTDELING')
        msh.receiving_facility = HD(hd_1='NSP')
        msh.date_time_of_message = '20260413120000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02')
        msh.message_control_id = 'CSRIS00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260413120000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0508671155', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Skov', xpn_2='Henrik', xpn_3='Bo', xpn_5='')
        pid.date_time_of_birth = '19670805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gammel Kongevej 176', xad_3='Risskov', xad_5='8240', xad_6='DK')
        pid.pid_13 = '^^PH^+4534278055'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='LUN', pl_3='L2031', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='22002', xcn_2='Søndergaard', xcn_3='Lisbeth', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='LUN')
        pv1.financial_class = FC(fc_1='RH202604020001')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='CN', cwe_2='Konferencenotat')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260413120000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='55001', xcn_2='Frandsen', xcn_3='Jonas', xcn_6='Dr.')
        txa.transcription_date_time = '20260413120000'
        txa.unique_document_number = EI(ei_1='DOC20260413001')
        txa.document_confidentiality_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='NOTE', cwe_2='MDT konferencenotat', cwe_3='LN')
        obx.obx_5 = (
            'Multidisciplinær tumorkonference: Pt. med verificeret NSCLC i hø. overlap, cT2aN2M0, stadie IIIA. Diskuteret kirurgisk resektion vs. kemo-st'
            'rålebehandling. Konklusion: Kemo-strålebehandling anbefales grundet N2-sygdom. Henvises til onkologisk afdeling.'
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
