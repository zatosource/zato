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
from zato.hl7v2.v2_9.datatypes import CQ, CWE, CX, DLD, EI, FC, HD, MSG, OG, PL, PT, VID, XAD, XCN, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01NextOfKin, AdtA39Patient, AdtA44Patient, AdtA45MergeInfo, MdmT01CommonOrder, MdmT02CommonOrder, MdmT02Observation, \
    OmiO23Order, OmiO23Patient, OmiO23PatientVisit, OmiO23Timing, OrmO01Patient, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, \
    OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A03, ADT_A21, ADT_A39, ADT_A44, ADT_A45, ADT_A50, MDM_T01, MDM_T02, OMI_O23, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import EVN, GT1, IPC, MRG, MSH, NK1, OBR, OBX, ORC, PID, PV1, ROL, TQ1, TXA
from zato.hl7v2.z_segments import ZDS

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('at', 'at-synedra.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/at/at-synedra.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='TILAK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250401083000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'SYNMSG202504010830000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250401083000'
        evn.evn_5 = 'ADM001^Stadler^Renate^^^Mag.^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TK00198734', cx_4='TILAK', cx_5='PI'), CX(cx_1='1234050378', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Kapferer', xpn_2='Florian', xpn_3='Leopold', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kaiserjagerstrasse 18', xad_3='Innsbruck', xad_5='6020', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4351250412345^PRN^PH~+436641234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '1234050378^^^SV-AT'
        pid.birth_place = 'AT'
        pid.taxonomic_classification_code = CWE(
            cwe_2='PRN',
            cwe_3='CP',
            cwe_4='florian.kapferer@email.at',
            cwe_5='0043',
            cwe_6='0512',
            cwe_7='89059',
            cwe_12='+4351289059',
        )

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Kapferer', xpn_2='Barbara', xpn_4='Frau', xpn_5='')
        nk1.address = XAD(xad_1='+436641234568', xad_2='PRN', xad_3='CP')
        nk1.nk1_6 = 'SPO'
        nk1.administrative_sex = CWE(cwe_1='M')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='AMB-RAD-1', pl_3='2', pl_4='TILAK')
        pv1.pv1_7 = 'TK0042^Praxmarer^Heinrich^^^Univ.Prof.Dr.^MD'
        pv1.pv1_8 = 'TK0088^Zangerle^Margit^^^PD.Dr.^MD'
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = 'TK0042^Praxmarer^Heinrich^^^Univ.Prof.Dr.^MD'
        pv1.patient_type = CWE(cwe_1='OUT')
        pv1.financial_class = FC(fc_1='OEGK')
        pv1.diet_type = CWE(cwe_1='TILAK')
        pv1.prior_temporary_location = PL(pl_1='20250401083000')
        pv1.total_payments = 'V00198734^^^TILAK'
        pv1.alternate_visit_id = CX(cx_1='V')

        # .. build ROL ..
        rol = ROL()
        rol.rol_2 = 'LI'
        rol.rol_3 = 'CP'
        rol.rol_4 = 'TK0102^Neururer^Armin^^^Dr.^MD'

        # .. build GT1 ..
        gt1 = GT1()
        gt1.set_id_gt1 = '1'
        gt1.guarantor_name = XPN(xpn_1='Kapferer', xpn_2='Florian', xpn_4='Herr')
        gt1.guarantor_address = XAD(xad_1='Kaiserjagerstrasse 18', xad_3='Innsbruck', xad_5='6020', xad_6='AT')
        gt1.guarantor_date_time_of_birth = '19780503'
        gt1.guarantor_ssn = '1234050378'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.rol_2 = rol
        msg.gt1 = gt1

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
    """ Based on live/at/at-synedra.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='LKHHALL')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='LKHHALL')
        msh.date_time_of_message = '20250515091500+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'SYNMSG202505150915000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250515091500'
        evn.evn_5 = 'ADM010^Wimmer^Elfriede^^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TK00276543', cx_4='LKHHALL', cx_5='PI'), CX(cx_1='2345120485', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Kirchmair', xpn_2='Sabine', xpn_3='Anita', xpn_5='Frau')
        pid.date_time_of_birth = '19851204'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Unterer Stadtplatz 9', xad_3='Hall in Tirol', xad_5='6060', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4352231234^PRN^PH'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '2345120485^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM1', pl_2='105', pl_3='A', pl_4='LKHHALL', pl_9='INNMED1')
        pv1.pv1_7 = 'TK0110^Koller^Theodor^^^Prim.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='TK0110', cwe_2='Koller', cwe_3='Theodor', cwe_6='Prim.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.diet_type = CWE(cwe_1='LKHHALL')
        pv1.prior_temporary_location = PL(pl_1='20250515091500')
        pv1.total_payments = 'V00276543^^^LKHHALL'
        pv1.alternate_visit_id = CX(cx_1='V')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/at/at-synedra.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='TILAK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250610104500+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'SYNMSG202506101045000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250610104500'
        evn.operator_id = XCN(xcn_1='SYS', xcn_2='System', xcn_3='SAP')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TK00345678', cx_4='TILAK', cx_5='PI'), CX(cx_1='3456080772', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Reiter', xpn_2='Manfred', xpn_3='Erich', xpn_5='Herr')
        pid.date_time_of_birth = '19720807'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Schmerlingstrasse 4', xad_3='Innsbruck', xad_5='6020', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4351250434567^PRN^PH~+436769876543^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '3456080772^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCH', pl_2='U201', pl_3='B', pl_4='TILAK')
        pv1.pv1_7 = 'TK0205^Binder^Siegmund^^^Univ.Prof.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='UCH')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='TK0205', cwe_2='Binder', cwe_3='Siegmund', cwe_6='Univ.Prof.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='BVAEB')
        pv1.discharged_to_location = DLD(dld_1='TILAK')
        pv1.pending_location = PL(pl_1='20250607090000')
        pv1.total_adjustments = 'V00345678^^^TILAK'
        pv1.total_payments = 'V'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/at/at-synedra.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='LKHHALL')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='LKHHALL')
        msh.date_time_of_message = '20250522150000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'SYNMSG202505221500000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250522150000'
        evn.evn_5 = 'ADM020^Fink^Sonja^^^^RN'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TK00276543', cx_4='LKHHALL', cx_5='PI'), CX(cx_1='2345120485', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Kirchmair', xpn_2='Sabine', xpn_3='Anita', xpn_5='Frau')
        pid.date_time_of_birth = '19851204'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM1', pl_2='105', pl_3='A', pl_4='LKHHALL')
        pv1.pv1_7 = 'TK0110^Koller^Theodor^^^Prim.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='TK0110', cwe_2='Koller', cwe_3='Theodor', cwe_6='Prim.Dr.', cwe_7='MD')
        pv1.admitting_doctor = XCN(xcn_1='IN')
        pv1.visit_number = CX(cx_1='OEGK')
        pv1.diet_type = CWE(cwe_1='LKHHALL')
        pv1.prior_temporary_location = PL(pl_1='20250515091500')
        pv1.current_patient_balance = '20250522150000'
        pv1.alternate_visit_id = CX(cx_1='V00276543', cx_4='LKHHALL')
        pv1.visit_indicator = CWE(cwe_1='V')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/at/at-synedra.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='TILAK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250401100000+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SYNORD202504011000000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TK00198734', cx_4='TILAK', cx_5='PI'), CX(cx_1='1234050378', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Kapferer', xpn_2='Florian', xpn_3='Leopold', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Kapferer', xpn_2='Barbara', xpn_4='Frau', xpn_5='')
        nk1.address = XAD(xad_1='+436641234568', xad_2='PRN', xad_3='CP')
        nk1.nk1_6 = 'SPO'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='AMB-RAD-1', pl_3='2', pl_4='TILAK')
        pv1.pv1_7 = 'TK0042^Praxmarer^Heinrich^^^Univ.Prof.Dr.^MD'

        # .. build ROL ..
        rol = ROL()
        rol.rol_2 = 'LI'
        rol.rol_3 = 'CP'
        rol.rol_4 = 'TK0102^Neururer^Armin^^^Dr.^MD'

        # .. build GT1 ..
        gt1 = GT1()
        gt1.set_id_gt1 = '1'
        gt1.guarantor_name = XPN(xpn_1='Kapferer', xpn_2='Florian', xpn_4='Herr')
        gt1.guarantor_address = XAD(xad_1='Kaiserjagerstrasse 18', xad_3='Innsbruck', xad_5='6020', xad_6='AT')
        gt1.guarantor_date_time_of_birth = '19780503'
        gt1.guarantor_ssn = '1234050378'

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='SYNORD20250401001')
        orc.filler_order_number = EI(ei_1='SYNFIL20250401001')
        orc.order_status = 'SC'
        orc.orc_7 = '1^1^1^20250401100000+0200^^R'
        orc.orc_10 = 'TK0042^Praxmarer^Heinrich^^^Univ.Prof.Dr.^MD'
        orc.orc_12 = 'TK0042^Praxmarer^Heinrich^^^Univ.Prof.Dr.^MD'
        orc.enterers_location = PL(pl_4='TILAK')
        orc.call_back_phone_number = XTN(xtn_2='PRN', xtn_3='CP', xtn_5='0043', xtn_6='0512', xtn_7='89059', xtn_12='+4351289059')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SYNORD20250401001')
        obr.filler_order_number = EI(ei_1='SYNFIL20250401001')
        obr.universal_service_identifier = CWE(cwe_1='74178', cwe_2='CT Abdomen mit KM', cwe_3='SYNRAD')
        obr.observation_date_time = '20250401100000+0200'
        obr.obr_15 = 'TK0042^Praxmarer^Heinrich^^^Univ.Prof.Dr.^MD'
        obr.obr_16 = '^PRN^CP^^0043^0512^89059^^^^^+4351289059'
        obr.obr_17 = 'ACC20250401001'
        obr.diagnostic_serv_sect_id = 'CT'
        obr.obr_35 = '74178^CT Abdomen mit KM^SYNRAD'

        # .. build ZDS ..
        zds = ZDS()
        zds.zds_1 = '1.2.40.0.34.1.1.99.20250401.100000.001'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.extra_segments = [nk1, pv1, rol, gt1, orc, obr, zds]

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
    """ Based on live/at/at-synedra.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='TILAK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250401103000+0200'
        msh.message_type = MSG(msg_1='OMI', msg_2='O23', msg_3='OMI_O23')
        msh.message_control_id = 'SYNOMI202504011030000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TK00198734', cx_4='TILAK', cx_5='PI'), CX(cx_1='1234050378', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Kapferer', xpn_2='Florian', xpn_3='Leopold', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='AMB-RAD-1', pl_3='2', pl_4='TILAK')
        pv1.pv1_7 = 'TK0042^Praxmarer^Heinrich^^^Univ.Prof.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='RAD')
        pv1.visit_number = CX(cx_1='V00198734', cx_4='TILAK')
        pv1.financial_class = FC(fc_1='V')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmiO23PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OmiO23Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='SYNORD20250401001')
        orc.filler_order_number = EI(ei_1='SYNFIL20250401001')
        orc.order_status = 'SC'
        orc.orc_10 = 'TK0042^Praxmarer^Heinrich^^^Univ.Prof.Dr.^MD'
        orc.orc_12 = 'TK0042^Praxmarer^Heinrich^^^Univ.Prof.Dr.^MD'
        orc.enterers_location = PL(pl_4='TILAK')

        # .. build TQ1 ..
        tq1 = TQ1()
        tq1.set_id_tq1 = '1'
        tq1.service_duration = CQ(cq_1='1')
        tq1.start_datetime = '20250401103000+0200'
        tq1.priority = CWE(cwe_1='R')

        # .. build the TIMING group ..
        timing = OmiO23Timing()
        timing.tq1 = tq1

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SYNORD20250401001')
        obr.filler_order_number = EI(ei_1='SYNFIL20250401001')
        obr.universal_service_identifier = CWE(cwe_1='74178', cwe_2='CT Abdomen mit KM', cwe_3='SYNRAD')
        obr.obr_16 = 'TK0042^Praxmarer^Heinrich^^^Univ.Prof.Dr.^MD'
        obr.order_callback_phone_number = XTN(xtn_2='PRN', xtn_3='CP', xtn_5='0043', xtn_6='0512', xtn_7='89059', xtn_12='+4351289059')
        obr.transport_logistics_of_collected_sample = CWE(cwe_1='74178', cwe_2='CT Abdomen mit KM', cwe_3='SYNRAD')

        # .. build IPC ..
        ipc = IPC()
        ipc.accession_identifier = EI(ei_1='ACC20250401001')
        ipc.requested_procedure_id = EI(ei_1='RP20250401001')
        ipc.study_instance_uid = EI(ei_1='1.2.40.0.34.1.1.99.20250401.100000.001')
        ipc.modality = CWE(cwe_1='SPS20250401001')
        ipc.protocol_code = CWE(cwe_1='CT')
        ipc.ipc_7 = 'P74178^CT Abdomen KM^^TILAK^CT Abdomen mit Kontrastmittel'
        ipc.action_code = 'CT-TILAK01'

        # .. build the ORDER group ..
        order = OmiO23Order()
        order.orc = orc
        order.timing = timing
        order.obr = obr
        order.ipc = ipc

        # .. assemble the full message ..
        msg = OMI_O23()
        msg.msh = msh
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
    """ Based on live/at/at-synedra.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='TILAK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250405143000+0200'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'SYNMDM202504051430000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='TK00198734', cx_4='TILAK', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Kapferer', xpn_2='Florian', xpn_3='Leopold', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.visit_number = CX(cx_1='V00198734', cx_4='TILAK')
        pv1.alternate_visit_id = CX(cx_1='V')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.observation_date_time = '20250405140000+0200'
        obr.placer_field_1 = 'ACC20250401001'
        obr.obr_23 = 'RAD^Radiologie^TILAK'

        # .. build the COMMON_ORDER group ..
        common_order = MdmT02CommonOrder()
        common_order.obr = obr

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='RAD', cwe_2='Radiologischer Befund', cwe_3='TILAK')
        txa.document_content_presentation = 'TX^text^TILAK'
        txa.origination_date_time = '20250405140000+0200'
        txa.txa_9 = 'TK0042^Praxmarer^Heinrich^^^Univ.Prof.Dr.^MD^^^^^^^^^TILAK&2.16.840.1.113883.2.16.1.4&ISO^A'
        txa.unique_document_number = EI(ei_1='BEF-2025-00198734')
        txa.unique_document_file_name = 'Befund_CT_Abdomen_Kapferer_20250405.pdf'
        txa.document_completion_status = 'AU'
        txa.distributed_copies_code_and_name_of_recipients = XCN(xcn_1='BEF-CNT-2025-001', xcn_3='TILAK')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0Nv'
            'dW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8'
            'PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDcyIDcyMCBUZCAoQmVmdW5kIENUIEFi'
            'ZG9tZW4gVGlyb2wpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2Jq'
            'CnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxNSAwMDAwMCBuIAowMDAwMDAwMDY2IDAwMDAwIG4gCjAwMDAwMDAxMjUgMDAwMDAgbiAKMDAwMDAwMDMzOSAwMDAw'
            'MCBuIAowMDAwMDAwNDQzIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNTQyCiUlRU9GCg=='
        )
        obx.interpretation_codes = CWE(cwe_1='F')
        obx.observation_result_status = '20250405140000+0200'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.pid = pid
        msg.pv1 = pv1
        msg.common_order = common_order
        msg.txa = txa
        msg.observation = observation

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
    """ Based on live/at/at-synedra.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='TILAK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250405150000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SYNORU202504051500000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='TK00198734', cx_4='TILAK', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Kapferer', xpn_2='Florian', xpn_3='Leopold', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.visit_number = CX(cx_1='V00198734', cx_4='TILAK')
        pv1.alternate_visit_id = CX(cx_1='V')

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
        obr.observation_date_time = '20250405145000+0200'
        obr.specimen_action_code = 'F'
        obr.placer_field_1 = 'ACC20250401001'
        obr.obr_23 = 'RAD^Radiologie^TILAK'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(
            cwe_1='BEFUND-CT-001',
            cwe_2='CT Abdomen Befund',
            cwe_4='BEF-CNT-CT-001',
            cwe_5='CT Abdomen Container',
            cwe_6='RIS',
            cwe_8='Befund_CT_Abdomen.pdf',
        )
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            '^text^plain^Base64^'
            'Q1QgQWJkb21lbiBtaXQgS00NCg0KS2xpbmlzY2hlIEFuZ2FiZTogQmF1Y2hzY2htZXJ6ZW4gcmVjaHRlciBVbnRlcmJhdWNoDQoNCkJlZnVuZDoNCkxlYmVyOiBOb3JtYWwgZ3Jvc3Ms'
            'IGhvbW9nZW5lcy1QYXJlbmNoeW0uDQpHYWxsZW5ibGFzZTogU3RlaW5mcmVpLg0KUGFua3JlYXM6IFVuYXVmZmFlbGxpZy4NCkFwcGVuZGl4OiBWZXJkaWNrdCBhdWYgMTJtbSwgcGVy'
            'aWFwcGVuZGl6aXRpc2NoZSBGbHVlc3NpZ2tlaXQuDQoNCkJldXJ0ZWlsdW5nOiBBa3V0ZSBBcHBlbmRpeml0aXMu'
        )
        obx.interpretation_codes = CWE(cwe_1='interpretationCode', cwe_2='Befund')
        obx.nature_of_abnormal_test = 'F'
        obx.user_defined_access_checks = '20250405145000+0200'

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
    """ Based on live/at/at-synedra.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='TILAK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250801100000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'SYNMSG202508011000000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250801100000'
        evn.evn_5 = 'ADM040^Huber^Michaela^^^^ADM'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TK00456789', cx_4='TILAK', cx_5='PI'), CX(cx_1='4567220695', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Pichler', xpn_2='Silvia', xpn_3='Helga', xpn_5='Frau')
        pid.date_time_of_birth = '19950622'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Leopoldstrasse 3', xad_3='Innsbruck', xad_5='6020', xad_6='AT', xad_7='H')
        pid.pid_13 = '+436501234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '4567220695^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='TK00456790', cx_4='TILAK', cx_5='PI')

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
    """ Based on live/at/at-synedra.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='TILAK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250815110000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A47', msg_3='ADT_A44')
        msh.message_control_id = 'SYNMSG202508151100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A47'
        evn.recorded_date_time = '20250815110000'
        evn.evn_5 = 'ADM050^Eder^Karin^^^^ADM'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TK00567890', cx_4='TILAK', cx_5='PI'), CX(cx_1='5678050382', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Leitner', xpn_2='Kurt', xpn_3='Erwin', xpn_5='Herr')
        pid.date_time_of_birth = '19820503'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hofgasse 8', xad_3='Innsbruck', xad_5='6020', xad_6='AT', xad_7='H')
        pid.pid_13 = '+4351250456789^PRN^PH'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '5678050382^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='TK00567891', cx_4='TILAK', cx_5='PI')

        # .. build the PATIENT group ..
        patient = AdtA44Patient()
        patient.pid = pid
        patient.mrg = mrg

        # .. assemble the full message ..
        msg = ADT_A44()
        msg.msh = msh
        msg.evn = evn
        msg.patient = patient

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
    """ Based on live/at/at-synedra.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='LKHHALL')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='LKHHALL')
        msh.date_time_of_message = '20250520140000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A50', msg_3='ADT_A50')
        msh.message_control_id = 'SYNMSG202505201400000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A50'
        evn.recorded_date_time = '20250520140000'
        evn.evn_5 = 'ADM055^Lang^Brunhilde^^^^ADM'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TK00276543', cx_4='LKHHALL', cx_5='PI'), CX(cx_1='2345120485', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Kirchmair', xpn_2='Sabine', xpn_3='Anita', xpn_5='Frau')
        pid.date_time_of_birth = '19851204'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_visit_number = CX(cx_1='V00276543', cx_4='LKHHALL')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM1', pl_2='105', pl_3='A', pl_4='LKHHALL')
        pv1.pv1_7 = 'TK0110^Koller^Theodor^^^Prim.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='MED')
        pv1.discharged_to_location = DLD(dld_1='LKHHALL')
        pv1.prior_temporary_location = PL(pl_1='V00276544', pl_4='LKHHALL')
        pv1.admit_date_time = 'V'

        # .. assemble the full message ..
        msg = ADT_A50()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.mrg = mrg
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
    """ Based on live/at/at-synedra.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='TILAK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250901093000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A45', msg_3='ADT_A45')
        msh.message_control_id = 'SYNMSG202509010930000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A45'
        evn.recorded_date_time = '20250901093000'
        evn.evn_5 = 'ADM060^Moser^Gisela^^^^ADM'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TK00678901', cx_4='TILAK', cx_5='PI'), CX(cx_1='6789180275', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Aigner', xpn_2='Engelbert', xpn_3='Gottfried', xpn_5='Herr')
        pid.date_time_of_birth = '19750218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Sillgasse 12', xad_3='Innsbruck', xad_5='6020', xad_6='AT', xad_7='H')
        pid.pid_13 = '+436641234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '6789180275^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_visit_number = CX(cx_1='V00678901', cx_4='TILAK')

        # .. build the MERGE_INFO group ..
        merge_info = AdtA45MergeInfo()
        merge_info.mrg = mrg

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Aigner', xpn_2='Adelheid', xpn_4='Frau', xpn_5='')
        nk1.address = XAD(xad_1='+436641234568', xad_2='PRN', xad_3='CP')
        nk1.nk1_6 = 'SPO'

        # .. build GT1 ..
        gt1 = GT1()
        gt1.set_id_gt1 = '1'
        gt1.guarantor_name = XPN(xpn_1='Aigner', xpn_2='Engelbert', xpn_4='Herr')
        gt1.guarantor_address = XAD(xad_1='Sillgasse 12', xad_3='Innsbruck', xad_5='6020', xad_6='AT')
        gt1.guarantor_date_time_of_birth = '19750218'
        gt1.guarantor_ssn = '6789180275'

        # .. assemble the full message ..
        msg = ADT_A45()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.merge_info = merge_info
        msg.extra_segments = [nk1, gt1]

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
    """ Based on live/at/at-synedra.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='TILAK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250905150000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A23', msg_3='ADT_A21')
        msh.message_control_id = 'SYNMSG202509051500000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A23'
        evn.recorded_date_time = '20250905150000'
        evn.evn_5 = 'ADM065^Fischer^Roland^^^^ADM'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TK00789012', cx_4='TILAK', cx_5='PI'), CX(cx_1='7890051095', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Winkler', xpn_2='Hartmut', xpn_3='Dietrich', xpn_5='Herr')
        pid.date_time_of_birth = '19950510'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCH', pl_2='U201', pl_3='B', pl_4='TILAK')
        pv1.pv1_7 = 'TK0205^Binder^Siegmund^^^Univ.Prof.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='UCH')
        pv1.discharged_to_location = DLD(dld_1='TILAK')
        pv1.prior_temporary_location = PL(pl_1='V00789012', pl_4='TILAK')
        pv1.admit_date_time = 'V'

        # .. assemble the full message ..
        msg = ADT_A21()
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
    """ Based on live/at/at-synedra.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='TILAK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250910100000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A29', msg_3='ADT_A21')
        msh.message_control_id = 'SYNMSG202509101000000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A29'
        evn.recorded_date_time = '20250910100000'
        evn.evn_5 = 'ADM070^Berger^Ottilie^^^^ADM'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TK00789012', cx_4='TILAK', cx_5='PI'), CX(cx_1='7890051095', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Winkler', xpn_2='Hartmut', xpn_3='Dietrich', xpn_5='Herr')
        pid.date_time_of_birth = '19950510'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. assemble the full message ..
        msg = ADT_A21()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid

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
    """ Based on live/at/at-synedra.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EventServer')
        msh.sending_facility = HD(hd_1='TILAK', hd_2='TILAK', hd_3='L')
        msh.receiving_application = HD(hd_1='SAPISH')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250401153000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SYNREF202504011530000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.sequence_number = '1'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='TK00198734', cx_4='TILAK', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Kapferer', xpn_2='Florian', xpn_3='Leopold', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD')
        pv1.pv1_7 = 'TK0042^Praxmarer^Heinrich^^^Univ.Prof.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='RAD')
        pv1.visit_number = CX(cx_1='V00198734', cx_4='TILAK')
        pv1.financial_class = FC(fc_1='V')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'OP'
        orc.placer_order_number = EI(ei_1='SYNORD20250401001')
        orc.filler_order_number = EI(ei_1='SYNFIL20250401001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SYNORD20250401001')
        obr.filler_order_number = EI(ei_1='SYNFIL20250401001')
        obr.universal_service_identifier = CWE(cwe_1='74178', cwe_2='CT Abdomen mit KM', cwe_3='SYNRAD')
        obr.observation_date_time = '20250401153000+0200'
        obr.obr_17 = 'ACC20250401001'
        obr.filler_field_2 = '20250401153000+0200'
        obr.obr_23 = 'RAD^Radiologie^TILAK'
        obr.diagnostic_serv_sect_id = 'F'
        obr.transport_arrangement_responsibility = CWE(cwe_1='ManufacturerModelName', cwe_2='SOMATOM Force')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'RP'
        obx.observation_identifier = CWE(cwe_1='1.2.40.0.34.1.1.99.20250401.100000.001', cwe_2='CT Abdomen mit KM', cwe_3='SYNRAD', cwe_4='12345678')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'https://syngo.tilak.at/share/study/1.2.40.0.34.1.1.99.20250401.100000.001^^DICOM'
        obx.units = CWE(cwe_1='CT', cwe_2='MR')
        obx.reference_range = '5'
        obx.probability = 'F'
        obx.effective_date_of_reference_range = '20250401153000+0200'
        obx.date_time_of_the_observation = 'TILAK^Tirol Kliniken^TILAK^^Tirol Kliniken'

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
    """ Based on live/at/at-synedra.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='TILAK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250406090000+0200'
        msh.message_type = MSG(msg_1='MDM', msg_2='T09', msg_3='MDM_T01')
        msh.message_control_id = 'SYNMDM202504060900000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='TK00198734', cx_4='TILAK', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Kapferer', xpn_2='Florian', xpn_3='Leopold', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.visit_number = CX(cx_1='V00198734', cx_4='TILAK')
        pv1.alternate_visit_id = CX(cx_1='V')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.observation_date_time = '20250406085000+0200'
        obr.placer_field_1 = 'ACC20250401001'
        obr.obr_23 = 'RAD^Radiologie^TILAK'

        # .. build the COMMON_ORDER group ..
        common_order = MdmT01CommonOrder()
        common_order.obr = obr

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='RAD', cwe_2='Radiologischer Befund', cwe_3='TILAK')
        txa.activity_date_time = 'TX^text^TILAK'
        txa.transcription_date_time = '20250406085000+0200'
        txa.txa_10 = 'TK0042^Praxmarer^Heinrich^^^Univ.Prof.Dr.^MD^^^^^^^^^TILAK&2.16.840.1.113883.2.16.1.4&ISO^A'
        txa.parent_document_number = EI(ei_1='BEF-2025-00198734')
        txa.document_completion_status = 'Befund_CT_Abdomen_Kapferer_20250405_v2.pdf'
        txa.document_confidentiality_status = 'IP'
        txa.agreed_due_date_time = 'BEF-CNT-2025-001^^TILAK'
        txa.creating_specialty = CWE(cwe_1='Aktualisierter Befund')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.observation_sub_id = OG(og_1='1')
        obx.interpretation_codes = CWE(cwe_1='NR', cwe_2='Normal')
        obx.date_time_of_the_observation = '20250406085000+0200'

        # .. assemble the full message ..
        msg = MDM_T01()
        msg.msh = msh
        msg.pid = pid
        msg.pv1 = pv1
        msg.common_order = common_order
        msg.txa = txa
        msg.extra_segments = [obx]

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
    """ Based on live/at/at-synedra.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='TILAK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250407100000+0200'
        msh.message_type = MSG(msg_1='MDM', msg_2='T10', msg_3='MDM_T02')
        msh.message_control_id = 'SYNMDM202504071000000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='TK00198734', cx_4='TILAK', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Kapferer', xpn_2='Florian', xpn_3='Leopold', xpn_5='Herr')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.visit_number = CX(cx_1='V00198734', cx_4='TILAK')
        pv1.alternate_visit_id = CX(cx_1='V')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.observation_date_time = '20250407095000+0200'
        obr.placer_field_1 = 'ACC20250401001'
        obr.obr_23 = 'RAD^Radiologie^TILAK'

        # .. build the COMMON_ORDER group ..
        common_order = MdmT02CommonOrder()
        common_order.obr = obr

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='RAD', cwe_2='Radiologischer Befund', cwe_3='TILAK')
        txa.activity_date_time = 'TX^text^TILAK'
        txa.transcription_date_time = '20250407095000+0200'
        txa.txa_10 = 'TK0042^Praxmarer^Heinrich^^^Univ.Prof.Dr.^MD^^^^^^^^^TILAK&2.16.840.1.113883.2.16.1.4&ISO^A'
        txa.parent_document_number = EI(ei_1='BEF-2025-00198734')
        txa.document_completion_status = 'Befund_CT_Abdomen_Kapferer_v3.pdf'
        txa.document_confidentiality_status = 'AU'
        txa.agreed_due_date_time = 'BEF-CNT-2025-001^^TILAK'
        txa.creating_specialty = CWE(cwe_1='Finaler Befund')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSA+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUz'
            'NSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDQgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4'
            'cmVmCjIwNgolJUVPRgo='
        )
        obx.interpretation_codes = CWE(cwe_1='F')
        obx.observation_result_status = '20250407095000+0200'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.pid = pid
        msg.pv1 = pv1
        msg.common_order = common_order
        msg.txa = txa
        msg.observation = observation

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
    """ Based on live/at/at-synedra.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='TILAK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250910140000+0200'
        msh.message_type = MSG(msg_1='MDM', msg_2='T11', msg_3='MDM_T01')
        msh.message_control_id = 'SYNMDM202509101400000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='TK00789012', cx_4='TILAK', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Winkler', xpn_2='Hartmut', xpn_3='Dietrich', xpn_5='Herr')
        pid.date_time_of_birth = '19950510'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.visit_number = CX(cx_1='V00789012', cx_4='TILAK')
        pv1.alternate_visit_id = CX(cx_1='V')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.observation_date_time = '20250910135000+0200'
        obr.placer_field_1 = 'ACC20250910001'
        obr.obr_23 = 'UCH^Unfallchirurgie^TILAK'

        # .. build the COMMON_ORDER group ..
        common_order = MdmT01CommonOrder()
        common_order.obr = obr

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='UCH', cwe_2='Chirurgischer Befund', cwe_3='TILAK')
        txa.activity_date_time = 'TX^text^TILAK'
        txa.transcription_date_time = '20250910135000+0200'
        txa.unique_document_number = EI(ei_1='BEF-2025-00789012')
        txa.unique_document_file_name = 'Befund_Roentgen_Winkler.pdf'
        txa.document_completion_status = 'AU'
        txa.txa_25 = 'BEF-CNT-2025-789^^TILAK'

        # .. assemble the full message ..
        msg = MDM_T01()
        msg.msh = msh
        msg.pid = pid
        msg.pv1 = pv1
        msg.common_order = common_order
        msg.txa = txa

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
    """ Based on live/at/at-synedra.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='TILAK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250912100000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SYNORU202509121000000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='TK00789012', cx_4='TILAK', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Winkler', xpn_2='Hartmut', xpn_3='Dietrich', xpn_5='Herr')
        pid.date_time_of_birth = '19950510'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.visit_number = CX(cx_1='V00789012', cx_4='TILAK')
        pv1.alternate_visit_id = CX(cx_1='V')

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
        obr.observation_date_time = '20250912095000+0200'
        obr.specimen_action_code = 'D'
        obr.diagnostic_serv_sect_id = 'UCH^Unfallchirurgie^TILAK'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.observation_identifier = CWE(
            cwe_1='BEFUND-UCH-001',
            cwe_2='Chirurgischer Befund',
            cwe_4='BEF-CNT-UCH-001',
            cwe_6='RIS',
            cwe_8='Befund_Roentgen_v2.pdf',
        )
        obx.observation_sub_id = OG(og_1='1')
        obx.interpretation_codes = CWE(cwe_1='interpretationCode')
        obx.nature_of_abnormal_test = 'D'
        obx.user_defined_access_checks = '20250912095000+0200'

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
    """ Based on live/at/at-synedra.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAPISH')
        msh.sending_facility = HD(hd_1='TILAK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TILAK')
        msh.date_time_of_message = '20250920133000+0200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A42', msg_3='ADT_A39')
        msh.message_control_id = 'SYNMSG202509201330000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.message_profile_identifier = EI(ei_1='UNICODE UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A42'
        evn.recorded_date_time = '20250920133000'
        evn.evn_5 = 'ADM080^Holzer^Norbert^^^^ADM'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='TK00678901', cx_4='TILAK', cx_5='PI'), CX(cx_1='6789180275', cx_4='SV-AT', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='Aigner', xpn_2='Engelbert', xpn_3='Gottfried', xpn_5='Herr')
        pid.date_time_of_birth = '19750218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Sillgasse 12', xad_3='Innsbruck', xad_5='6020', xad_6='AT', xad_7='H')
        pid.pid_13 = '+436641234567^PRN^CP'
        pid.primary_language = CWE(cwe_1='DE')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '6789180275^^^SV-AT'
        pid.birth_place = 'AT'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_visit_number = CX(cx_1='V00678902', cx_4='TILAK')

        # .. build the PATIENT group ..
        patient = AdtA39Patient()
        patient.pid = pid
        patient.mrg = mrg

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Aigner', xpn_2='Adelheid', xpn_4='Frau', xpn_5='')
        nk1.address = XAD(xad_1='+436641234568', xad_2='PRN', xad_3='CP')
        nk1.nk1_6 = 'SPO'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM1', pl_2='110', pl_3='A', pl_4='TILAK')
        pv1.pv1_7 = 'TK0110^Koller^Theodor^^^Prim.Dr.^MD'
        pv1.consulting_doctor = XCN(xcn_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.delete_account_date = 'TILAK'
        pv1.account_status = CWE(cwe_1='V00678901', cwe_4='TILAK')
        pv1.pending_location = PL(pl_1='V')

        # .. build ROL ..
        rol = ROL()
        rol.rol_2 = 'LI'
        rol.rol_3 = 'CP'
        rol.rol_4 = 'TK0102^Neururer^Armin^^^Dr.^MD'

        # .. build GT1 ..
        gt1 = GT1()
        gt1.set_id_gt1 = '1'
        gt1.guarantor_name = XPN(xpn_1='Aigner', xpn_2='Engelbert', xpn_4='Herr')
        gt1.guarantor_address = XAD(xad_1='Sillgasse 12', xad_3='Innsbruck', xad_5='6020', xad_6='AT')
        gt1.guarantor_date_time_of_birth = '19750218'
        gt1.guarantor_ssn = '6789180275'

        # .. assemble the full message ..
        msg = ADT_A39()
        msg.msh = msh
        msg.evn = evn
        msg.patient = patient
        msg.extra_segments = [nk1, pv1, rol, gt1]

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
