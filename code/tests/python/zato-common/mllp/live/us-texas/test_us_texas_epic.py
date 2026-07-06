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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, DR, EI, EIP, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA03Procedure, AdtA05NextOfKin, AdtA39Patient, DftP03Diagnosis, DftP03Financial, \
    DftP03Visit, MdmT02Observation, MfnM02MfStaff, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RdeO11Order, RdeO11Patient, RdeO11PatientVisit, SiuS12GeneralResource, \
    SiuS12LocationResource, SiuS12Patient, SiuS12Resources, SiuS12Service, VxuV04Observation, VxuV04Order, VxuV04PatientVisit
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, DFT_P03, MDM_T02, MFN_M02, ORM_O01, ORU_R01, RDE_O11, SIU_S12, VXU_V04
from zato.hl7v2.v2_9.segments import AIG, AIL, AIS, DG1, EVN, FT1, GT1, IN1, IN2, MFE, MFI, MRG, MSA, MSH, NK1, NTE, OBR, OBX, ORC, PD1, PID, PR1, PRA, PV1, \
    PV2, RGS, RXA, RXE, RXR, SCH, STF, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('us-texas', 'us-texas-epic.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/us-texas/us-texas-epic.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='BSWMC', hd_2='2.16.840.1.113883.3.787', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260415093012'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20260415093012001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260415092500'
        evn.evn_5 = 'GALLAGHER^Gallagher^Fiona^R^^^MD'
        evn.event_occurred = '20260415092500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN10234567', cx_4='BSWMC', cx_5='MR'), CX(cx_1='471-38-9206', cx_4='USSSA', cx_5='SS')]
        pid.pid_5 = 'Sepulveda^Graciela^Yolanda^^Mrs.^'
        pid.date_time_of_birth = '19780514'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='4521 Bluebonnet Ln', xad_3='Dallas', xad_4='TX', xad_5='75201', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^214^5559823'
        pid.pid_14 = '^WPN^PH^^1^214^5550142'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '471-38-9206'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'Baylor Scott and White Medical Center^^^^NPI'
        pd1.pd1_4 = '1234567890^Fitzgerald^Owen^A^^^MD^^^^NPI'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Sepulveda', xpn_2='Marco', xpn_3='Renaldo', xpn_5='Mr.')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='4521 Bluebonnet Ln', xad_3='Dallas', xad_4='TX', xad_5='75201', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^214^5559824'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='4102', pl_3='01', pl_4='BSWMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '9876543210^Drummond^Cedric^K^^^MD^^^^NPI^L^^^EI'
        pv1.pv1_8 = '5432109876^Whitmore^Leslie^M^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiology', xcn_3='HL70069')
        pv1.ambulatory_status = CWE(cwe_1='A', cwe_2='Accident', cwe_3='HL70007')
        pv1.pv1_20 = 'VN20260415001^^^BSWMC^VN'
        pv1.discharge_date_time = '20260415092500'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Chest pain with shortness of breath')
        pv2.expected_discharge_date_time = '20260415'
        pv2.estimated_length_of_inpatient_stay = '3'
        pv2.visit_protection_indicator = 'N'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.10', cwe_2='Atherosclerotic heart disease of native coronary artery without angina pectoris', cwe_3='I10')
        dg1.diagnosis_date_time = '20260415'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build GT1 ..
        gt1 = GT1()
        gt1.set_id_gt1 = '1'
        gt1.guarantor_name = XPN(xpn_1='Sepulveda', xpn_2='Graciela', xpn_3='Yolanda', xpn_5='Mrs.')
        gt1.guarantor_address = XAD(xad_1='4521 Bluebonnet Ln', xad_3='Dallas', xad_4='TX', xad_5='75201', xad_6='US')
        gt1.guarantor_ph_num_home = XTN(xtn_2='PRN', xtn_3='PH', xtn_5='1', xtn_6='214', xtn_7='5559823')
        gt1.guarantor_relationship = CWE(cwe_1='SE', cwe_2='Self', cwe_3='HL70063')
        gt1.nationality = CWE(cwe_1='12345678')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BCBS001')
        in1.insurance_company_id = CX(cx_1='60054', cx_2='Blue Cross Blue Shield of Texas')
        in1.in1_4 = 'BCBSTX^^Dallas^TX^75201'
        in1.group_name = XON(xon_1='GRP123456')
        in1.plan_type = CWE(cwe_1='Sepulveda', cwe_2='Graciela', cwe_3='Yolanda')
        in1.name_of_insured = XPN(xpn_1='SE', xpn_2='Self', xpn_3='HL70063')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19780514')
        in1.insureds_date_of_birth = '4521 Bluebonnet Ln^^Dallas^TX^75201^US'
        in1.insureds_address = XAD(xad_1='Y')
        in1.coordination_of_benefits = CWE(cwe_1='1')
        in1.company_plan_code = CWE(cwe_1='POL998877')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.dg1 = dg1
        msg.gt1 = gt1
        msg.insurance = insurance

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UTSW', hd_2='2.16.840.1.113883.3.8765', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260418141530'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG20260418141530002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260418141000'
        evn.evn_5 = 'ANSWORTH^Answorth^Colleen^L^^^MD'
        evn.event_occurred = '20260418141000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN20345678', cx_4='UTSW', cx_5='MR')
        pid.pid_5 = 'Mukherjee^Debashis^Arjun^^Mr.^'
        pid.date_time_of_birth = '19650923'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='8712 Preston Rd', xad_3='Dallas', xad_4='TX', xad_5='75225', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^469^5553847'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '632-47-8195'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTH', pl_2='3201', pl_3='02', pl_4='UTSW', pl_8='N')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent', cwe_3='HL70007')
        pv1.pv1_7 = '2345678901^Blackburn^Howard^F^^^MD^^^^NPI'
        pv1.pv1_8 = '3456789012^Calderwood^Helen^J^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='ORT', xcn_2='Orthopedics', xcn_3='HL70069')
        pv1.ambulatory_status = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.pv1_20 = 'VN20260414002^^^UTSW^VN'
        pv1.servicing_facility = CWE(cwe_1='01', cwe_2='Discharged to home', cwe_3='HL70112')
        pv1.prior_temporary_location = PL(pl_1='20260414110000')
        pv1.admit_date_time = '20260418141000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Right total knee arthroplasty recovery')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M17.11', cwe_2='Primary osteoarthritis right knee', cwe_3='I10')
        dg1.diagnosis_date_time = '20260414'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='Z96.651', cwe_2='Presence of right artificial knee joint', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20260414'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. build PR1 ..
        pr1 = PR1()
        pr1.set_id_pr1 = '1'
        pr1.procedure_code = CNE(cne_1='27447', cne_2='Total knee replacement right', cne_3='CPT4')
        pr1.pr1_4 = '^Right total knee arthroplasty'
        pr1.procedure_date_time = '20260414130000'
        pr1.anesthesia_minutes = '2345678901^Blackburn^Howard^F^^^MD^^^^NPI'

        # .. build the PROCEDURE group ..
        procedure = AdtA03Procedure()
        procedure.pr1 = pr1

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.dg1 = [dg1, dg1_2]
        msg.procedure = procedure

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='MHH', hd_2='2.16.840.1.113883.3.4422', hd_3='ISO')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260420083045'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260420083045003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30456789', cx_4='MHH', cx_5='MR')
        pid.pid_5 = 'Lattimore^Shavonne^Denise^^Ms.^'
        pid.date_time_of_birth = '19900217'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='1503 Westheimer Rd', xad_3='Houston', xad_4='TX', xad_5='77006', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^713^5557261'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '518-73-2640'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='0001', pl_3='01', pl_4='MHH', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '4567890123^Hargrave^Linh^H^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='HEM', xcn_2='Hematology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260420003', cx_4='MHH', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD40001', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='FIL40001', ei_2='LAB')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260420070000')
        orc.orc_11 = '4567890123^Hargrave^Linh^H^^^MD^^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD40001', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='FIL40001', ei_2='LAB')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC with differential', cwe_3='LN')
        obr.observation_date_time = '20260420070000'
        obr.obr_16 = '4567890123^Hargrave^Linh^H^^^MD^^^^NPI'
        obr.results_rpt_status_chng_date_time = '20260420082000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocytes [#/volume] in Blood', cwe_3='LN')
        obx.obx_5 = '7.2'
        obx.units = CWE(cwe_1='10*3/uL', cwe_2='thousand per microliter', cwe_3='UCUM')
        obx.reference_range = '4.5-11.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260420082000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrocytes [#/volume] in Blood', cwe_3='LN')
        obx_2.obx_5 = '4.65'
        obx_2.units = CWE(cwe_1='10*6/uL', cwe_2='million per microliter', cwe_3='UCUM')
        obx_2.reference_range = '4.00-5.50'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260420082000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin [Mass/volume] in Blood', cwe_3='LN')
        obx_3.obx_5 = '13.8'
        obx_3.units = CWE(cwe_1='g/dL', cwe_2='grams per deciliter', cwe_3='UCUM')
        obx_3.reference_range = '12.0-16.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260420082000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrit [Volume Fraction] of Blood', cwe_3='LN')
        obx_4.obx_5 = '41.2'
        obx_4.units = CWE(cwe_1='%', cwe_2='percent', cwe_3='UCUM')
        obx_4.reference_range = '36.0-46.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260420082000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV [Entitic volume]', cwe_3='LN')
        obx_5.obx_5 = '88.6'
        obx_5.units = CWE(cwe_1='fL', cwe_2='femtoliter', cwe_3='UCUM')
        obx_5.reference_range = '80.0-100.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260420082000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='785-6', cwe_2='MCH [Entitic mass]', cwe_3='LN')
        obx_6.obx_5 = '29.7'
        obx_6.units = CWE(cwe_1='pg', cwe_2='picogram', cwe_3='UCUM')
        obx_6.reference_range = '27.0-33.0'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260420082000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='786-4', cwe_2='MCHC [Mass/volume]', cwe_3='LN')
        obx_7.obx_5 = '33.5'
        obx_7.units = CWE(cwe_1='g/dL', cwe_2='grams per deciliter', cwe_3='UCUM')
        obx_7.reference_range = '32.0-36.0'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260420082000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelets [#/volume] in Blood', cwe_3='LN')
        obx_8.obx_5 = '245'
        obx_8.units = CWE(cwe_1='10*3/uL', cwe_2='thousand per microliter', cwe_3='UCUM')
        obx_8.reference_range = '150-400'
        obx_8.interpretation_codes = CWE(cwe_1='N')
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20260420082000'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='770-8', cwe_2='Neutrophils/100 leukocytes in Blood', cwe_3='LN')
        obx_9.obx_5 = '58.3'
        obx_9.units = CWE(cwe_1='%', cwe_2='percent', cwe_3='UCUM')
        obx_9.reference_range = '40.0-70.0'
        obx_9.interpretation_codes = CWE(cwe_1='N')
        obx_9.observation_result_status = 'F'
        obx_9.date_time_of_the_observation = '20260420082000'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'NM'
        obx_10.observation_identifier = CWE(cwe_1='736-9', cwe_2='Lymphocytes/100 leukocytes in Blood', cwe_3='LN')
        obx_10.obx_5 = '30.1'
        obx_10.units = CWE(cwe_1='%', cwe_2='percent', cwe_3='UCUM')
        obx_10.reference_range = '20.0-40.0'
        obx_10.interpretation_codes = CWE(cwe_1='N')
        obx_10.observation_result_status = 'F'
        obx_10.date_time_of_the_observation = '20260420082000'

        # .. build the OBSERVATION group ..
        observation_10 = OruR01Observation()
        observation_10.obx = obx_10

        # .. build OBX ..
        obx_11 = OBX()
        obx_11.set_id_obx = '11'
        obx_11.value_type = 'NM'
        obx_11.observation_identifier = CWE(cwe_1='5905-5', cwe_2='Monocytes/100 leukocytes in Blood', cwe_3='LN')
        obx_11.obx_5 = '7.4'
        obx_11.units = CWE(cwe_1='%', cwe_2='percent', cwe_3='UCUM')
        obx_11.reference_range = '2.0-8.0'
        obx_11.interpretation_codes = CWE(cwe_1='N')
        obx_11.observation_result_status = 'F'
        obx_11.date_time_of_the_observation = '20260420082000'

        # .. build the OBSERVATION group ..
        observation_11 = OruR01Observation()
        observation_11.obx = obx_11

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='BSWMC', hd_2='2.16.840.1.113883.3.787', hd_3='ISO')
        msh.receiving_application = HD(hd_1='RAD_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260421101500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260421101500004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN40567890', cx_4='BSWMC', cx_5='MR')
        pid.pid_5 = 'Balderas^Hector^Ernesto^^Mr.^'
        pid.date_time_of_birth = '19820730'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='2908 Swiss Ave', xad_3='Dallas', xad_4='TX', xad_5='75204', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^214^5558193'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '743-26-8051'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='0012', pl_3='01', pl_4='BSWMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '5678901234^Pemberton^Elena^C^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='RAD', xcn_2='Radiology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260421004', cx_4='BSWMC', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD50001', ei_2='EPIC')
        orc.placer_order_group_number = EI(ei_1='GRP50001', ei_2='EPIC')
        orc.date_time_of_order_event = '20260421100000'
        orc.orc_12 = '5678901234^Pemberton^Elena^C^^^MD^^^^NPI'
        orc.orc_17 = 'BSWMC^Baylor Scott and White Medical Center'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD50001', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='74178', cwe_2='CT abdomen and pelvis with contrast', cwe_3='CPT4')
        obr.observation_date_time = '20260421100000'
        obr.obr_15 = '5678901234^Pemberton^Elena^C^^^MD^^^^NPI'
        obr.result_status = '1^Routine^HL70065'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R10.9', cwe_2='Unspecified abdominal pain', cwe_3='I10')
        dg1.diagnosis_date_time = '20260421'
        dg1.diagnosis_type = CWE(cwe_1='A')

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
        nte.comment = 'Patient reports persistent right lower quadrant pain for 3 days. Rule out appendicitis.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UTSW', hd_2='2.16.840.1.113883.3.8765', hd_3='ISO')
        msh.receiving_application = HD(hd_1='PATH_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260422160030'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260422160030005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN50678901', cx_4='UTSW', cx_5='MR')
        pid.pid_5 = 'Banerjee^Aditi^Meera^^Ms.^'
        pid.date_time_of_birth = '19730412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='6201 Harry Hines Blvd', xad_3='Dallas', xad_4='TX', xad_5='75235', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^214^5554082'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '284-59-7103'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PATH', pl_2='0005', pl_3='01', pl_4='UTSW', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '6789012345^Ashford^Rajiv^K^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='PAT', xcn_2='Pathology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260422005', cx_4='UTSW', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD60001', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='FIL60001', ei_2='PATH')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260422120000')
        orc.orc_11 = '6789012345^Ashford^Rajiv^K^^^MD^^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD60001', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='FIL60001', ei_2='PATH')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='Surgical pathology', cwe_3='CPT4')
        obr.observation_date_time = '20260420090000'
        obr.obr_16 = '6789012345^Ashford^Rajiv^K^^^MD^^^^NPI'
        obr.results_rpt_status_chng_date_time = '20260422155000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Pathology Report', cwe_3='AUSPDI')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKFBhdGhvbG9neSBSZXBvcnQpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAw'
            'MDAwMCA2NTUzNSBmIAo='
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260422155000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='22634-0', cwe_2='Pathology report final diagnosis', cwe_3='LN')
        obx_2.obx_5 = (
            'Specimen: Left breast, excisional biopsy\\.br\\Diagnosis: Fibroadenoma, benign\\.br\\Margins: Negative for malignancy\\.br\\Comment: No evidence'
            ' of atypia or carcinoma'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260422155000'

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='MHH', hd_2='2.16.840.1.113883.3.4422', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260423110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20260423110000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260423105500'
        evn.evn_5 = 'WAVERLY^Waverly^Corinne^A^^^RN'
        evn.event_occurred = '20260423105500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN60789012', cx_4='MHH', cx_5='MR')
        pid.pid_5 = 'Quarles^Terrence^Donovan^^Mr.^'
        pid.date_time_of_birth = '19550812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='9422 Main St', xad_3='Houston', xad_4='TX', xad_5='77030', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^713^5551894'
        pid.pid_14 = '^WPN^PH^^1^713^5557743'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '360-14-8729'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'Memorial Hermann Hospital^^^^NPI'
        pd1.pd1_4 = '7890123456^Kensington^Patricia^L^^^MD^^^^NPI'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Quarles', xpn_2='Lucille', xpn_3='Yvette', xpn_5='Mrs.')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='9422 Main St', xad_3='Houston', xad_4='TX', xad_5='77030', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^713^5551895'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='2304', pl_3='01', pl_4='MHH', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '7890123456^Kensington^Patricia^L^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='MED', xcn_2='Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260420006', cx_4='MHH', cx_5='VN')
        pv1.current_patient_balance = '20260420163000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='MCARE001')
        in1.insurance_company_id = CX(cx_1='00451', cx_2='Medicare')
        in1.in1_4 = 'Centers for Medicare^^Baltimore^MD^21244'
        in1.group_name = XON(xon_1='MCAREGRP')
        in1.plan_type = CWE(cwe_1='Quarles', cwe_2='Terrence', cwe_3='Donovan')
        in1.name_of_insured = XPN(xpn_1='SE', xpn_2='Self', xpn_3='HL70063')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19550812')
        in1.insureds_date_of_birth = '9422 Main St^^Houston^TX^77030^US'
        in1.insureds_address = XAD(xad_1='Y')
        in1.coordination_of_benefits = CWE(cwe_1='1')
        in1.company_plan_code = CWE(cwe_1='MCAREPOL123456')

        # .. build IN2 ..
        in2 = IN2()
        in2.military_handicapped_program = CWE(cwe_1='Quarles', cwe_2='Terrence', cwe_3='Donovan')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1
        insurance.in2 = in2

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='BSWMC', hd_2='2.16.840.1.113883.3.787', hd_3='ISO')
        msh.receiving_application = HD(hd_1='SCHED_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260424091000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG20260424091000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APPT70001', ei_2='EPIC')
        sch.appointment_reason = CWE(cwe_1='MRI', cwe_2='MRI Brain with contrast', cwe_3='L')
        sch.appointment_type = CWE(cwe_1='30', cwe_2='MIN')
        sch.sch_9 = 'MIN^Minutes^ISO+'
        sch.appointment_duration_units = CNE(cne_4='20260428140000', cne_6='30', cne_7='MIN')
        sch.placer_contact_location = PL(pl_1='8901234567', pl_2='Forsythe', pl_3='Terence', pl_4='T', pl_7='MD', pl_11='NPI')
        sch.sch_16 = '^PRN^PH^^1^214^5553210'
        sch.sch_21 = '8901234567^Forsythe^Terence^T^^^MD^^^^NPI'
        sch.placer_order_number = EI(ei_1='Booked')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN70890123', cx_4='BSWMC', cx_5='MR')
        pid.pid_5 = 'Pennington^Brooke^Elaine^^Ms.^'
        pid.date_time_of_birth = '19880605'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='3315 Oak Lawn Ave', xad_3='Dallas', xad_4='TX', xad_5='75219', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^214^5559471'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '805-42-6137'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='MRI1', pl_3='01', pl_4='BSWMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '8901234567^Forsythe^Terence^T^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='RAD', xcn_2='Radiology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260424007', cx_4='BSWMC', cx_5='VN')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.resource_group_id = CWE(cwe_1='RAD_MRI')

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='70553', cwe_2='MRI Brain with and without contrast', cwe_3='CPT4')
        ais.start_date_time = '20260428140000'
        ais.duration = '30^MIN'
        ais.duration_units = CNE(cne_1='MIN', cne_2='Minutes', cne_3='ISO+')
        ais.filler_status_code = CWE(cwe_1='Confirmed')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.resource_id = CWE(cwe_1='8901234567', cwe_2='Forsythe', cwe_3='Terence', cwe_4='T', cwe_7='MD', cwe_11='NPI')
        aig.start_date_time = '20260428140000'
        aig.duration = '30^MIN'

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SiuS12GeneralResource()
        general_resource.aig = aig

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='RAD', pl_2='MRI1', pl_3='01', pl_4='BSWMC')
        ail.start_date_time_offset_units = CNE(cne_1='20260428140000')
        ail.allow_substitution_code = CWE(cwe_1='30', cwe_2='MIN')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Patient has history of migraines. No contrast allergy reported.'

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail
        location_resource.nte = nte

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.general_resource = general_resource
        resources.location_resource = location_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UTSW', hd_2='2.16.840.1.113883.3.8765', hd_3='ISO')
        msh.receiving_application = HD(hd_1='PHARM_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260425143000'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'MSG20260425143000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN80901234', cx_4='UTSW', cx_5='MR')
        pid.pid_5 = 'Renteria^Catalina^Ximena^^Mrs.^'
        pid.date_time_of_birth = '19690318'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='7701 Forest Ln', xad_3='Dallas', xad_4='TX', xad_5='75230', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^469^5558342'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '917-62-3084'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ENDO', pl_2='0003', pl_3='01', pl_4='UTSW', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '9012345678^Hargrove^Diego^R^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='END', xcn_2='Endocrinology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260425008', cx_4='UTSW', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = RdeO11PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = RdeO11Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD80001', ei_2='EPIC')
        orc.placer_order_group_number = EI(ei_1='GRP80001', ei_2='EPIC')
        orc.date_time_of_order_event = '20260425142000'
        orc.orc_12 = '9012345678^Hargrove^Diego^R^^^MD^^^^NPI'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '1^BID^HL70335'
        rxe.give_code = CWE(cwe_1='6809', cwe_2='Metformin 500mg tablet', cwe_3='NDC')
        rxe.give_amount_minimum = '500'
        rxe.give_amount_maximum = '500'
        rxe.give_units = CWE(cwe_1='mg', cwe_2='milligrams', cwe_3='ISO+')
        rxe.give_dosage_form = CWE(cwe_1='TAB', cwe_2='Tablet', cwe_3='HL70292')
        rxe.dispense_units = CWE(cwe_1='30')
        rxe.number_of_refills = 'EA^each^ISO+'
        rxe.rxe_14 = '9012345678^Hargrove^Diego^R^^^MD^^^^NPI'
        rxe.give_indication = CWE(cwe_1='2', cwe_2='Refills')

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')

        # .. build the ORDER group ..
        order = RdeO11Order()
        order.orc = orc
        order.rxe = rxe
        order.rxr = rxr

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E11.9', cwe_2='Type 2 diabetes mellitus without complications', cwe_3='I10')
        dg1.diagnosis_date_time = '20260425'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = RDE_O11()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [dg1]

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='MHH', hd_2='2.16.840.1.113883.3.4422', hd_3='ISO')
        msh.receiving_application = HD(hd_1='DOC_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260426170000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG20260426170000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260426165500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN91012345', cx_4='MHH', cx_5='MR')
        pid.pid_5 = 'Hollingsworth^Gerald^Raymond^^Mr.^'
        pid.date_time_of_birth = '19470929'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='1214 Montrose Blvd', xad_3='Houston', xad_4='TX', xad_5='77019', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^713^5556734'
        pid.marital_status = CWE(cwe_1='W', cwe_2='Widowed', cwe_3='HL70002')
        pid.pid_19 = '592-41-7836'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='5108', pl_3='01', pl_4='MHH', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '0123456789^Maitland^Carmen^A^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='CAR', xcn_2='Cardiology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260422009', cx_4='MHH', cx_5='VN')
        pv1.current_patient_balance = '20260422083000'
        pv1.total_charges = '20260426160000'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Discharge Summary', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Text^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260426165000')
        txa.transcriptionist_code_name = XCN(xcn_1='DOC9001', xcn_2='MHH')
        txa.unique_document_file_name = 'AU^Authenticated^HL70271'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='11490-0', cwe_2='Discharge summarization note', cwe_3='LN')
        obx.obx_5 = (
            'DISCHARGE SUMMARY\\.br\\Patient: Hollingsworth, Gerald Raymond\\.br\\DOB: 09/29/1947\\.br\\Admission: 04/22/2026\\.br\\Discharge: 04/26/2026\\.b'
            'r\\\\.br\\PRINCIPAL DIAGNOSIS: Acute myocardial infarction, STEMI, LAD\\.br\\\\.br\\HOSPITAL COURSE:\\.br\\Patient presented to ED with acute su'
            'bsternal chest pain. ECG showed ST elevation in leads V1-V4. Emergent cardiac catheterization revealed 95% LAD stenosis. PCI performed with '
            'drug-eluting stent placement. Post-procedure course uncomplicated.\\.br\\\\.br\\MEDICATIONS AT DISCHARGE:\\.br\\1. Aspirin 81mg daily\\.br\\2. C'
            'lopidogrel 75mg daily\\.br\\3. Atorvastatin 80mg daily\\.br\\4. Metoprolol succinate 50mg daily\\.br\\5. Lisinopril 10mg daily\\.br\\\\.br\\FOLL'
            'OW-UP: Cardiology clinic in 2 weeks.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260426165000'

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='BSWMC', hd_2='2.16.840.1.113883.3.787', hd_3='ISO')
        msh.receiving_application = HD(hd_1='FIN_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260427080000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'MSG20260427080000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20260427075500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN01123456', cx_4='BSWMC', cx_5='MR')
        pid.pid_5 = 'Trang^Mai^Phuong^^Ms.^'
        pid.date_time_of_birth = '19950114'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='5602 Greenville Ave', xad_3='Dallas', xad_4='TX', xad_5='75206', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^469^5551237'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '426-83-1957'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='0001', pl_3='T3', pl_4='BSWMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '1234509876^Stratton^David^W^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='EM', xcn_2='Emergency Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260426010', cx_4='BSWMC', cx_5='VN')
        pv1.current_patient_balance = '20260426221500'
        pv1.total_charges = '20260427040000'

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_date = DR(dr_1='20260426221500')
        ft1.transaction_posting_date = '20260427040000'
        ft1.transaction_type = CWE(cwe_1='CG', cwe_2='Charge', cwe_3='HL70017')
        ft1.transaction_code = CWE(cwe_1='99285', cwe_2='ED visit level 5', cwe_3='CPT4')
        ft1.ft1_9 = '1'
        ft1.assigned_patient_location = PL(pl_1='ED', pl_2='0001', pl_3='T3', pl_4='BSWMC')
        ft1.ft1_21 = '1234509876^Stratton^David^W^^^MD^^^^NPI'

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_date = DR(dr_1='20260426230000')
        ft1_2.transaction_posting_date = '20260426230000'
        ft1_2.transaction_type = CWE(cwe_1='CG', cwe_2='Charge', cwe_3='HL70017')
        ft1_2.transaction_code = CWE(cwe_1='71046', cwe_2='Chest X-ray 2 views', cwe_3='CPT4')
        ft1_2.ft1_9 = '1'
        ft1_2.assigned_patient_location = PL(pl_1='RAD', pl_2='0001', pl_3='01', pl_4='BSWMC')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build FT1 ..
        ft1_3 = FT1()
        ft1_3.set_id_ft1 = '3'
        ft1_3.transaction_date = DR(dr_1='20260426233000')
        ft1_3.transaction_posting_date = '20260426233000'
        ft1_3.transaction_type = CWE(cwe_1='CG', cwe_2='Charge', cwe_3='HL70017')
        ft1_3.transaction_code = CWE(cwe_1='93010', cwe_2='ECG interpretation', cwe_3='CPT4')
        ft1_3.ft1_9 = '1'
        ft1_3.assigned_patient_location = PL(pl_1='ED', pl_2='0001', pl_3='T3', pl_4='BSWMC')

        # .. build the FINANCIAL group ..
        financial_3 = DftP03Financial()
        financial_3.ft1 = ft1_3

        # .. build FT1 ..
        ft1_4 = FT1()
        ft1_4.set_id_ft1 = '4'
        ft1_4.transaction_date = DR(dr_1='20260427010000')
        ft1_4.transaction_posting_date = '20260427010000'
        ft1_4.transaction_type = CWE(cwe_1='CG', cwe_2='Charge', cwe_3='HL70017')
        ft1_4.transaction_code = CWE(cwe_1='36556', cwe_2='Central venous catheter insertion', cwe_3='CPT4')
        ft1_4.ft1_9 = '1'
        ft1_4.assigned_patient_location = PL(pl_1='ED', pl_2='0001', pl_3='T3', pl_4='BSWMC')

        # .. build the FINANCIAL group ..
        financial_4 = DftP03Financial()
        financial_4.ft1 = ft1_4

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonia unspecified organism', cwe_3='I10')
        dg1.diagnosis_date_time = '20260426'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the DIAGNOSIS group ..
        diagnosis = DftP03Diagnosis()
        diagnosis.dg1 = dg1

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='J96.01', cwe_2='Acute respiratory failure with hypoxia', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20260426'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. build the DIAGNOSIS group ..
        diagnosis_2 = DftP03Diagnosis()
        diagnosis_2.dg1 = dg1_2

        # .. assemble the full message ..
        msg = DFT_P03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.visit = visit
        msg.financial = [financial, financial_2, financial_3, financial_4]
        msg.diagnosis = [diagnosis, diagnosis_2]

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UTSW', hd_2='2.16.840.1.113883.3.8765', hd_3='ISO')
        msh.receiving_application = HD(hd_1='IMMTRAC2')
        msh.receiving_facility = HD(hd_1='TX_DSHS')
        msh.date_time_of_message = '20260428103000'
        msh.message_type = MSG(msg_1='VXU', msg_2='V04', msg_3='VXU_V04')
        msh.message_control_id = 'MSG20260428103000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'ER'
        msh.application_acknowledgment_type = 'AL'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN11234567', cx_4='UTSW', cx_5='MR')
        pid.pid_5 = 'Ishikawa^Kenji^Takeshi^^Master^'
        pid.date_time_of_birth = '20240215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='4801 Harry Hines Blvd', xad_3='Dallas', xad_4='TX', xad_5='75235', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^214^5553890'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = '2345670987^Merriweather^Sarah^E^^^MD^^^^NPI'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Ishikawa', xpn_2='Yumiko', xpn_3='Harumi', xpn_5='Mrs.')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='4801 Harry Hines Blvd', xad_3='Dallas', xad_4='TX', xad_5='75235', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^214^5553890'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PED', pl_2='0002', pl_3='01', pl_4='UTSW', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '2345670987^Merriweather^Sarah^E^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='PED', xcn_2='Pediatrics', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260428011', cx_4='UTSW', cx_5='VN')

        # .. build the PATIENT_VISIT group ..
        patient_visit = VxuV04PatientVisit()
        patient_visit.pv1 = pv1

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD11001', ei_2='EPIC')
        orc.placer_order_group_number = EI(ei_1='GRP11001', ei_2='EPIC')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260428102000')
        orc.orc_11 = '2345670987^Merriweather^Sarah^E^^^MD^^^^NPI'

        # .. build RXA ..
        rxa = RXA()
        rxa.give_sub_id_counter = '0'
        rxa.administration_sub_id_counter = '1'
        rxa.date_time_start_of_administration = '20260428102000'
        rxa.administered_code = CWE(cwe_1='141', cwe_2='Influenza injectable preservative free', cwe_3='CVX')
        rxa.administered_amount = '0.25'
        rxa.administered_units = CWE(cwe_1='mL', cwe_2='milliliters', cwe_3='ISO+')
        rxa.administration_notes = CWE(cwe_1='00', cwe_2='New immunization record', cwe_3='NIP001')
        rxa.rxa_15 = '49281-0421-10^^NDC'
        rxa.completion_status = 'CP^Complete^HL70322'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IM', cwe_2='Intramuscular', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='RT', cwe_2='Right Thigh', cwe_3='HL70163')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='64994-7', cwe_2='Vaccine funding program eligibility category', cwe_3='LN')
        obx.obx_5 = 'V02^VFC eligible Medicaid/Medicaid Managed Care^HL70064'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = VxuV04Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TS'
        obx_2.observation_identifier = CWE(cwe_1='29768-9', cwe_2='Date vaccine information statement published', cwe_3='LN')
        obx_2.obx_5 = '20230810'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = VxuV04Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TS'
        obx_3.observation_identifier = CWE(cwe_1='29769-7', cwe_2='Date vaccine information statement presented', cwe_3='LN')
        obx_3.obx_5 = '20260428'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = VxuV04Observation()
        observation_3.obx = obx_3

        # .. build the ORDER group ..
        order = VxuV04Order()
        order.orc = orc
        order.rxa = rxa
        order.rxr = rxr
        order.observation = observation
        order.observation_2 = observation_2
        order.observation_3 = observation_3

        # .. assemble the full message ..
        msg = VXU_V04()
        msg.msh = msh
        msg.pid = pid
        msg.pd1 = pd1
        msg.nk1 = nk1
        msg.patient_visit = patient_visit
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
    """ Based on live/us-texas/us-texas-epic.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='MHH', hd_2='2.16.840.1.113883.3.4422', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260429020000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20260429020000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260429015500'
        evn.evn_5 = 'LOCKWOOD^Lockwood^Rosa^M^^^RN'
        evn.event_occurred = '20260429015500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN12345678', cx_4='MHH', cx_5='MR')
        pid.pid_5 = 'Spearman^Devonte^Lamar^^Mr.^'
        pid.date_time_of_birth = '20000601'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='3818 Almeda Rd', xad_3='Houston', xad_4='TX', xad_5='77004', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^832^5559012'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '738-21-4056'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Spearman', xpn_2='Nadine', xpn_3='Celeste', xpn_5='Mrs.')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='3818 Almeda Rd', xad_3='Houston', xad_4='TX', xad_5='77004', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^832^5559013'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='0001', pl_3='T8', pl_4='MHH', pl_8='N')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.pv1_7 = '3456780123^Endicott^Chijioke^N^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='EM', xcn_2='Emergency Medicine', xcn_3='HL70069')
        pv1.ambulatory_status = CWE(cwe_1='A', cwe_2='Accident', cwe_3='HL70007')
        pv1.pv1_20 = 'VN20260429012^^^MHH^VN'
        pv1.discharge_date_time = '20260429015500'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Right ankle injury, possible fracture')
        pv2.visit_protection_indicator = '3^Urgent^HL70217'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='S82.891A', cwe_2='Other fracture of right lower leg initial encounter', cwe_3='I10')
        dg1.diagnosis_date_time = '20260429'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.dg1 = dg1

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='BSWMC', hd_2='2.16.840.1.113883.3.787', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260429140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'MSG20260429140000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20260429135500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN13456789', cx_4='BSWMC', cx_5='MR'), CX(cx_1='653-28-9174', cx_4='USSSA', cx_5='SS')]
        pid.pid_5 = 'Alaniz^Veronica^Marisol^^Mrs.^'
        pid.date_time_of_birth = '19850224'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='1122 Elm St', xad_3='Fort Worth', xad_4='TX', xad_5='76102', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^817^5554567'
        pid.pid_14 = '^WPN^PH^^1^817^5558890'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '653-28-9174'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'Baylor Scott and White Fort Worth^^^^NPI'
        pd1.pd1_4 = '4567801234^Thornbury^Maria^L^^^MD^^^^NPI'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Alaniz', xpn_2='Ignacio', xpn_3='Rafael', xpn_5='Mr.')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='1122 Elm St', xad_3='Fort Worth', xad_4='TX', xad_5='76102', xad_6='US')
        nk1.nk1_5 = '^PRN^PH^^1^817^5554568'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build NK1 ..
        nk1_2 = NK1()
        nk1_2.set_id_nk1 = '2'
        nk1_2.name = XPN(xpn_1='Alaniz', xpn_2='Dolores', xpn_3='Consuelo', xpn_5='Mrs.')
        nk1_2.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1_2.address = XAD(xad_1='908 Magnolia Ave', xad_3='Fort Worth', xad_4='TX', xad_5='76104', xad_6='US')
        nk1_2.nk1_5 = '^PRN^PH^^1^817^5553201'
        nk1_2.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin_2 = AdtA05NextOfKin()
        next_of_kin_2.nk1 = nk1_2

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = [next_of_kin, next_of_kin_2]

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UTSW', hd_2='2.16.840.1.113883.3.8765', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260430093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'MSG20260430093000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260430092500'
        evn.evn_5 = 'FAIRCHILD^Fairchild^Barbara^K^^^HIM'
        evn.event_occurred = '20260430092500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN14567890', cx_4='UTSW', cx_5='MR')
        pid.pid_5 = 'Buckner^Clayton^Everett^^Mr.^'
        pid.date_time_of_birth = '19710808'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='2501 Inwood Rd', xad_3='Dallas', xad_4='TX', xad_5='75235', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^469^5553678'
        pid.marital_status = CWE(cwe_1='D', cwe_2='Divorced', cwe_3='HL70002')
        pid.pid_19 = '841-07-5293'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='MRN14567891', cx_4='UTSW', cx_5='MR')
        mrg.prior_patient_name = XPN(xpn_1='Buckner', xpn_2='Clayton', xpn_3='E')

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='MHH', hd_2='2.16.840.1.113883.3.4422', hd_3='ISO')
        msh.receiving_application = HD(hd_1='RAD_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260501091500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260501091500015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN15678901', cx_4='MHH', cx_5='MR')
        pid.pid_5 = 'Lim^Soo-Yeon^Grace^^Ms.^'
        pid.date_time_of_birth = '19810320'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2028-9', cwe_2='Asian', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='5023 Bellaire Blvd', xad_3='Houston', xad_4='TX', xad_5='77401', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^713^5554938'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '193-76-4028'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='CT01', pl_3='01', pl_4='MHH', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '5670123456^Standridge^Arun^S^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='RAD', xcn_2='Radiology', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260501015', cx_4='MHH', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD15001', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='FIL15001', ei_2='RAD')
        orc.order_status = 'CM^Complete^HL70038'
        orc.parent_order = EIP(eip_1='20260430160000')
        orc.orc_11 = '5670123456^Standridge^Arun^S^^^MD^^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD15001', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='FIL15001', ei_2='RAD')
        obr.universal_service_identifier = CWE(cwe_1='71260', cwe_2='CT chest with contrast', cwe_3='CPT4')
        obr.observation_date_time = '20260430160000'
        obr.obr_16 = '5670123456^Standridge^Arun^S^^^MD^^^^NPI'
        obr.results_rpt_status_chng_date_time = '20260501090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='36643-5', cwe_2='Chest CT impression', cwe_3='LN')
        obx.obx_5 = (
            'IMPRESSION:\\.br\\1. No pulmonary embolism identified.\\.br\\2. Small bilateral pleural effusions.\\.br\\3. Subcentimeter mediastinal lymph node'
            's, likely reactive.\\.br\\4. No suspicious pulmonary nodules.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260501090000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Radiology Report', cwe_3='AUSPDI')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8Ci9NYXJrZWQgdHJ1ZQo+PgovU3RydWN0VHJlZVJvb3QgMyAwIFIK'
            'Pj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFs0IDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5'
            'cGUgL1N0cnVjdFRyZWVSb290Ci9LIFtdCi9QYXJlbnRUcmVlIDUgMCBSCj4+CmVuZG9iago0IDAgb2JqCjw8Ci9UeXBlIC9QYWdlCi9QYXJlbnQgMiAwIFIKL0NvbnRlbnRzIDYgMCBS'
            'Ci9SZXNvdXJjZXMgPDwKL0ZvbnQgPDwKL0YxIDcgMCBSCj4+Cj4+Cj4+CmVuZG9iago='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260501090000'

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='BSWMC', hd_2='2.16.840.1.113883.3.787', hd_3='ISO')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260501143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MSG20260501143000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260501142500'
        evn.evn_5 = 'STOCKDALE^Stockdale^Brittany^L^^^RN'
        evn.event_occurred = '20260501142500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN16789012', cx_4='BSWMC', cx_5='MR')
        pid.pid_5 = 'Blackwell^Damien^Chukwudi^^Mr.^'
        pid.date_time_of_birth = '19600115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2054-5', cwe_2='Black or African American', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='9210 White Rock Trail', xad_3='Dallas', xad_4='TX', xad_5='75238', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^214^5552847'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '672-30-8491'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SDU', pl_2='2105', pl_3='01', pl_4='BSWMC', pl_8='N')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent', cwe_3='HL70007')
        pv1.pv1_7 = '6781234567^Whitfield^Marco^J^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='MED', xcn_2='Medicine', xcn_3='HL70069')
        pv1.ambulatory_status = CWE(cwe_1='T', cwe_2='Transfer', cwe_3='HL70007')
        pv1.pv1_20 = 'VN20260428016^^^BSWMC^VN'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Post-cardiac surgery monitoring')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UTSW', hd_2='2.16.840.1.113883.3.8765', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MPI_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260502100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'MSG20260502100000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260502095500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN17890123', cx_4='UTSW', cx_5='MR')
        pid.pid_5 = 'Ontiveros^Luciana^Pilar^^Mrs.^'
        pid.date_time_of_birth = '19780422'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='1850 N Beckley Ave', xad_3='Dallas', xad_4='TX', xad_5='75203', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^214^5551204'
        pid.pid_14 = '^WPN^PH^^1^469^5557788'
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '514-80-3269'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='CDCREC')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'UT Southwestern Medical Center^^^^NPI'
        pd1.pd1_4 = '7892345678^Prescott^Antonio^C^^^MD^^^^NPI'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='BSWMC', hd_2='2.16.840.1.113883.3.787', hd_3='ISO')
        msh.receiving_application = HD(hd_1='MF_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260502160000'
        msh.message_type = MSG(msg_1='MFN', msg_2='M02', msg_3='MFN_M02')
        msh.message_control_id = 'MSG20260502160000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build MFI ..
        mfi = MFI()
        mfi.master_file_identifier = CWE(cwe_1='PRA', cwe_2='Practitioner master file', cwe_3='HL70175')
        mfi.file_level_event_code = 'UPD^Update^HL70180'
        mfi.response_level_code = 'NE'

        # .. build MFE ..
        mfe = MFE()
        mfe.record_level_event_code = 'MAD^Add record to master file^HL70180'
        mfe.mfn_control_id = '20260502155500'
        mfe.mfe_4 = '8903456789^Beaumont^Patricia^Ann^^MD'
        mfe.primary_key_value_type = 'CWE'

        # .. build STF ..
        stf = STF()
        stf.primary_key_value_stf = CWE(cwe_1='8903456789')
        stf.staff_identifier_list = CX(cx_1='U8903456789')
        stf.staff_name = XPN(xpn_1='Beaumont', xpn_2='Patricia', xpn_3='Ann', xpn_5='MD')
        stf.administrative_sex = CWE(cwe_1='F')
        stf.date_time_of_birth = '19750830'
        stf.active_inactive_flag = 'A^Active^HL70183'
        stf.stf_12 = '^WPN^PH^^1^214^5559102'

        # .. build PRA ..
        pra = PRA()
        pra.primary_key_value_pra = CWE(cwe_1='8903456789', cwe_2='Beaumont', cwe_3='Patricia', cwe_4='Ann', cwe_6='MD')
        pra.practitioner_group = CWE(cwe_1='BSWMC', cwe_2='Baylor Scott and White Medical Center')
        pra.practitioner_category = CWE(cwe_1='I', cwe_2='Institution', cwe_3='HL70186')
        pra.date_entered_practice = '207RC0000X^Internal Medicine Cardiovascular Disease^NUCC'

        # .. build the MF_STAFF group ..
        mf_staff = MfnM02MfStaff()
        mf_staff.mfe = mfe
        mf_staff.stf = stf
        mf_staff.pra = pra

        # .. assemble the full message ..
        msg = MFN_M02()
        msg.msh = msh
        msg.mfi = mfi
        msg.mf_staff = mf_staff

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ADT_RECV')
        msh.sending_facility = HD(hd_1='TX_HIE')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='BSWMC', hd_2='2.16.840.1.113883.3.787', hd_3='ISO')
        msh.date_time_of_message = '20260503080000'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'MSG20260503080000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MSG20260415093012001'
        msa.expected_sequence_number = '0'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/us-texas/us-texas-epic.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='MHH', hd_2='2.16.840.1.113883.3.4422', hd_3='ISO')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='TX_HIE')
        msh.date_time_of_message = '20260503110000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260503110000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN20012345', cx_4='MHH', cx_5='MR')
        pid.pid_5 = 'Summerfield^Carolyn^Renee^^Ms.^'
        pid.date_time_of_birth = '19830927'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='CDCREC')
        pid.patient_address = XAD(xad_1='2410 Kirby Dr', xad_3='Houston', xad_4='TX', xad_5='77019', xad_6='US', xad_7='H')
        pid.pid_13 = '^PRN^PH^^1^713^5558471'
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '247-58-9013'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='CDCREC')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='0003', pl_3='01', pl_4='MHH', pl_8='N')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.pv1_7 = '9014567890^Rutherford^Anthony^R^^^MD^^^^NPI'
        pv1.consulting_doctor = XCN(xcn_1='IM', xcn_2='Internal Medicine', xcn_3='HL70069')
        pv1.visit_number = CX(cx_1='VN20260503020', cx_4='MHH', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='ORD20001', ei_2='EPIC')
        orc.placer_order_group_number = EI(ei_1='GRP20001', ei_2='EPIC')
        orc.date_time_of_order_event = '20260503103000'
        orc.orc_12 = '9014567890^Rutherford^Anthony^R^^^MD^^^^NPI'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20001', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='80053', cwe_2='Comprehensive metabolic panel', cwe_3='CPT4')
        obr.observation_date_time = '20260503103000'
        obr.obr_15 = '9014567890^Rutherford^Anthony^R^^^MD^^^^NPI'
        obr.result_status = '1^Routine^HL70065'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E11.65', cwe_2='Type 2 diabetes mellitus with hyperglycemia', cwe_3='I10')
        dg1.diagnosis_date_time = '20260503'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='I10', cwe_2='Essential primary hypertension', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20260503'
        dg1_2.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1
        order_detail.dg1_2 = dg1_2

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Annual wellness visit. Patient fasting since midnight.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
