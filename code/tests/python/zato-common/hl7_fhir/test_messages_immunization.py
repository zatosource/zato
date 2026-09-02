# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from conftest import convert, convert_fixture, one_resource, organization_named, resources_of_type

# ################################################################################################################################
# ################################################################################################################################

MSH_VXU = 'MSH|^~\\&|EHR|EHRFAC|REGISTRY|REGFAC|20240517143055||VXU^V04|MSG00005|P|2.5'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M'

# ################################################################################################################################
# ################################################################################################################################

class TestVXUImmunization:
    """ VXU messages become Immunization resources.
    """

    def test_immunization_core_fields(self) -> 'None':
        orc = 'ORC|RE||IMM-1^REGISTRY'
        rxa = 'RXA|0|1|20240517103000||08^Hepatitis B vaccine^CVX|0.5|mL^^UCUM|||1234^Welby^Marcus|||||LOT-9|20250101|GHC^Good Health Vaccines^MVX|||CP'
        rxr = 'RXR|IM^Intramuscular^HL70162|LD^Left deltoid^HL70163'

        bundle = convert(MSH_VXU, PID, orc, rxa, rxr)
        immunization = one_resource(bundle, 'Immunization')

        # CP means the immunization is complete.
        assert immunization['status'] == 'completed'

        vaccine_code = immunization['vaccineCode']
        vaccine_codings = vaccine_code['coding']
        vaccine_coding = vaccine_codings[0]

        assert vaccine_coding == {
            'code': '08',
            'display': 'Hepatitis B vaccine',
            'system': 'http://hl7.org/fhir/sid/cvx',
        }

        assert immunization['occurrenceDateTime'] == '2024-05-17T10:30:00+00:00'

        assert immunization['doseQuantity'] == {
            'value': 0.5,
            'code': 'mL',
            'system': 'http://unitsofmeasure.org',
            'unit': 'mL',
        }

        assert immunization['lotNumber'] == 'LOT-9'
        assert immunization['expirationDate'] == '2025-01-01'

        # The ORC filler number identifies the immunization.
        identifiers = immunization['identifier']
        identifier = identifiers[0]

        assert identifier['value'] == 'IMM-1'

        # The manufacturer became an Organization.
        organization = organization_named(bundle, 'Good Health Vaccines')
        assert organization['name'] == 'Good Health Vaccines'

        # The RXR route and site joined the immunization.
        route = immunization['route']
        route_codings = route['coding']
        route_coding = route_codings[0]

        assert route_coding['code'] == 'IM'

        site = immunization['site']
        site_codings = site['coding']
        site_coding = site_codings[0]

        assert site_coding['code'] == 'LD'

# ################################################################################################################################

    def test_ig_vxu_v04(self) -> 'None':
        bundle = convert_fixture('VXU_V04.hl7')

        # The message carries three RXA groups.
        immunizations = resources_of_type(bundle, 'Immunization')
        assert len(immunizations) == 3

        # Each immunization belongs to the patient from the same bundle.
        bundle_dict = bundle.to_dict()
        patient_url = None

        for entry in bundle_dict['entry']:
            resource = entry['resource']
            if resource['resourceType'] == 'Patient':
                patient_url = entry['fullUrl']

        for immunization in immunizations:
            patient_reference = immunization['patient']
            assert patient_reference == {'reference': patient_url}

# ################################################################################################################################
# ################################################################################################################################

class TestVaccinationQueries:
    """ VXQ and QRY vaccination queries and their responses map like immunization messages.
    """

    def test_vxq_query_stays_preserved(self) -> 'None':
        msh = 'MSH|^~\\&|CLINIC|CLINFAC|REGISTRY|REGFAC|20240517143055||VXQ^V01^VXQ_V01|MSG00021|P|2.5'
        qrd = 'QRD|20240517143000|R|I|Q-1|||1^RD|12345^^^MYHOSP^MR|VXI^Vaccine History^HL70048'
        qrf = 'QRF|REGISTRY|20200101|20240517'

        bundle = convert(msh, qrd, qrf)
        bundle_dict = bundle.to_dict()

        # A query has no patient of its own - the QRD and QRF stay whole as Basic resources.
        basics = resources_of_type(bundle, 'Basic')
        assert len(basics) == 2

        for entry in bundle_dict['entry']:
            resource = entry['resource']
            assert resource['resourceType'] != 'Patient'

        qrd_resource = basics[0]
        assert qrd_resource['code']['coding'][0]['code'] == 'QRD'

# ################################################################################################################################

    def test_qry_r02_query_stays_preserved(self) -> 'None':

        # The QRY^R02 results query shares the QRY structure of MSH, QRD and QRF.
        msh = 'MSH|^~\\&|LIS|LISFAC|LAB|LABFAC|20240517143055||QRY^R02^QRY_R02|MSG00025|P|2.5'
        qrd = 'QRD|20240517143000|R|I|Q-9|||25^RD|12345^^^MYHOSP^MR|RES|ALL'
        qrf = 'QRF|INSTMGR|20240517000000|20240517235959'

        bundle = convert(msh, qrd, qrf)

        basics = resources_of_type(bundle, 'Basic')
        assert len(basics) == 2

        qrd_resource = basics[0]
        qrf_resource = basics[1]

        assert qrd_resource['code']['coding'][0]['code'] == 'QRD'
        assert qrf_resource['code']['coding'][0]['code'] == 'QRF'

# ################################################################################################################################

    def test_vxr_history_becomes_immunizations(self) -> 'None':
        msh = 'MSH|^~\\&|REGISTRY|REGFAC|CLINIC|CLINFAC|20240517143055||VXR^V03^VXR_V03|MSG00022|P|2.5'
        msa = 'MSA|AA|Q-1|Record found'
        qrd = 'QRD|20240517143000|R|I|Q-1|||1^RD|12345^^^MYHOSP^MR|VXI^Vaccine History^HL70048'
        rxa_first = 'RXA|0|1|20230110|20230110|08^Hepatitis B vaccine^CVX|0.5|mL^^UCUM||00||||||||||CP'
        rxa_second = 'RXA|0|2|20230312|20230312|20^DTaP^CVX|0.5|mL^^UCUM||00||||||||||CP'

        bundle = convert(msh, msa, qrd, PID, rxa_first, rxa_second)

        # Each RXA in the history is an Immunization of the queried patient.
        immunizations = resources_of_type(bundle, 'Immunization')
        assert len(immunizations) == 2

        first = immunizations[0]

        assert first['status'] == 'completed'
        assert first['vaccineCode']['coding'][0]['code'] == '08'
        assert first['occurrenceDateTime'] == '2023-01-10'

        patient = one_resource(bundle, 'Patient')
        assert patient['name'][0]['family'] == 'Smith'

# ################################################################################################################################

    def test_rsp_immunization_response_becomes_immunizations(self) -> 'None':
        msh = 'MSH|^~\\&|REGISTRY|REGFAC|CLINIC|CLINFAC|20240517143055||RSP^K11^RSP_K11|MSG00023|P|2.5'
        msa = 'MSA|AA|MSG00020'
        qak = 'QAK|Q-2|OK|Z34^Request Immunization History^CDCPHINVS'
        qpd = 'QPD|Z34^Request Immunization History^CDCPHINVS|Q-2|12345^^^MYHOSP^MR'
        rxa = 'RXA|0|1|20230110|20230110|08^Hepatitis B vaccine^CVX|0.5|mL^^UCUM||00||||||||||CP'

        bundle = convert(msh, msa, qak, qpd, PID, rxa)

        # The CDC query profile in the QPD marks the response as immunization history.
        immunization = one_resource(bundle, 'Immunization')

        assert immunization['status'] == 'completed'
        assert immunization['vaccineCode']['coding'][0]['code'] == '08'

# ################################################################################################################################

    def test_rsp_without_cdc_profile_stays_generic(self) -> 'None':
        msh = 'MSH|^~\\&|EHR|EHRFAC|CLINIC|CLINFAC|20240517143055||RSP^K11^RSP_K11|MSG00024|P|2.5'
        msa = 'MSA|AA|MSG00020'
        qpd = 'QPD|Q22^Find Candidates^HL70471|Q-3|12345^^^MYHOSP^MR'
        rxa = 'RXA|0|1|20230110|20230110|1191^Aspirin^NDC|100|mg^^UCUM'

        bundle = convert(msh, msa, qpd, PID, rxa)

        # Without the CDC profile an RXA records a medication administration.
        administration = one_resource(bundle, 'MedicationAdministration')
        assert administration['medicationCodeableConcept']['coding'][0]['code'] == '1191'

# ################################################################################################################################
# ################################################################################################################################
