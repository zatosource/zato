# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings import get_conversion_warnings

# Local
from conftest import convert, one_resource, resources_of_type

# ################################################################################################################################
# ################################################################################################################################

MSH_REF = 'MSH|^~\\&|GP|CLINIC|HOSP|HOSPFAC|20240517143055||REF^I12|MSG00030|P|2.5'
MSH_RRI = 'MSH|^~\\&|HOSP|HOSPFAC|GP|CLINIC|20240518090000||RRI^I12|MSG00031|P|2.5'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M'

# ################################################################################################################################
# ################################################################################################################################

class TestRF1:
    """ RF1 makes the ServiceRequest a referral message is about.
    """

    def test_rf1_becomes_a_service_request(self) -> 'None':
        rf1 = 'RF1|P|R|MED^Medical^HL70281|||REF-1^GP|20240517|20240617|20240516|' + \
            'CHRONIC^Chronic condition management^L|EXT-9^HIE'

        bundle = convert(MSH_REF, rf1, PID)
        service_request = one_resource(bundle, 'ServiceRequest')

        # P means the referral is still pending, a draft.
        assert service_request['status'] == 'draft'

        # R means routine priority.
        assert service_request['priority'] == 'routine'

        # The referral type is the requested code.
        request_code = service_request['code']
        assert request_code['text'] == 'Medical'

        coding = request_code['coding'][0]
        assert coding['code'] == 'MED'
        assert coding['system'] == 'http://terminology.hl7.org/CodeSystem/v2-0281'

        # The originating and the external referral identifiers both carried over.
        identifiers = service_request['identifier']
        assert {'value': 'REF-1', 'system': 'urn:zato:hl7v2:authority:GP'} in identifiers
        assert {'value': 'EXT-9', 'system': 'urn:zato:hl7v2:authority:HIE'} in identifiers

        # The effective and expiration dates make the occurrence period.
        assert service_request['occurrencePeriod'] == {'start': '2024-05-17', 'end': '2024-06-17'}

        # The process date is when the referral was authored.
        assert service_request['authoredOn'] == '2024-05-16'

        # The referral reason carried over.
        reason = service_request['reasonCode'][0]
        assert reason['text'] == 'Chronic condition management'

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_subject_is_the_patient_that_follows(self) -> 'None':
        # The RF1 precedes the PID in a referral message, so the subject
        # can only be known once the whole message was walked.
        rf1 = 'RF1|A|R|GI^Gastroenterology^L|||REF-2^GP'

        bundle = convert(MSH_REF, rf1, PID)
        service_request = one_resource(bundle, 'ServiceRequest')

        bundle_dict = bundle.to_dict()
        patient_url = None

        for entry in bundle_dict['entry']:
            resource = entry['resource']
            if resource['resourceType'] == 'Patient':
                patient_url = entry['fullUrl']

        assert service_request['subject'] == {'reference': patient_url}

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_unknown_status_maps_to_the_default_and_is_preserved(self) -> 'None':
        rf1 = 'RF1|SS|R|GI^Gastroenterology^L|||REF-3^GP'

        bundle = convert(MSH_REF, rf1, PID)
        service_request = one_resource(bundle, 'ServiceRequest')

        assert service_request['status'] == 'unknown'

        extensions = service_request['extension']
        assert {'url': 'urn:zato:hl7v2:extension/unmapped/RF1-1', 'valueString': 'SS'} in extensions

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_disposition_and_category_are_preserved(self) -> 'None':
        rf1 = 'RF1|A|R|GI^Gastroenterology^L|WR^Send Written Report^HL70282|O^Outpatient^HL70284|REF-4^GP'

        bundle = convert(MSH_REF, rf1, PID)
        service_request = one_resource(bundle, 'ServiceRequest')

        extensions = service_request['extension']

        preserved = {}
        for extension in extensions:
            preserved[extension['url']] = extension['valueString']

        assert preserved['urn:zato:hl7v2:extension/unmapped/RF1-4'] == 'WR^Send Written Report^HL70282'
        assert preserved['urn:zato:hl7v2:extension/unmapped/RF1-5'] == 'O^Outpatient^HL70284'

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################

class TestPRD:
    """ PRD wires the referral's practitioners up.
    """

    def test_referring_provider_is_the_requester(self) -> 'None':
        rf1 = 'RF1|A|R|GI^Gastroenterology^L|||REF-5^GP'
        prd_referring = 'PRD|RP|Morrison^Karen^^^Dr|12 High Street^^Springfield^IL^62701^USA||' + \
            '0217555010^WPN^PH||1234567^MEDICARE'
        prd_referred_to = 'PRD|RT|Gupta^Anil^^^Dr|200 Hospital Road^^Springfield^IL^62702^USA||||7654321^MEDICARE'

        bundle = convert(MSH_REF, rf1, prd_referring, prd_referred_to, PID)
        service_request = one_resource(bundle, 'ServiceRequest')

        practitioners = resources_of_type(bundle, 'Practitioner')
        assert len(practitioners) == 2

        # The referring provider requested the referral ..
        referring = practitioners[0]
        assert referring['name'] == [{'family': 'Morrison', 'given': ['Karen'], 'prefix': ['Dr']}]
        assert referring['identifier'] == [{'value': '1234567', 'type': {'text': 'MEDICARE'}}]

        address = referring['address'][0]
        assert address['line'] == ['12 High Street']
        assert address['city'] == 'Springfield'

        telecom = referring['telecom'][0]
        assert telecom['value'] == '0217555010'
        assert telecom['system'] == 'phone'

        # .. and the referred-to provider will perform it.
        referred_to = practitioners[1]
        assert referred_to['name'] == [{'family': 'Gupta', 'given': ['Anil'], 'prefix': ['Dr']}]

        bundle_dict = bundle.to_dict()
        practitioner_urls = []

        for entry in bundle_dict['entry']:
            resource = entry['resource']
            if resource['resourceType'] == 'Practitioner':
                practitioner_urls.append(entry['fullUrl'])

        assert service_request['requester'] == {'reference': practitioner_urls[0]}
        assert service_request['performer'] == [{'reference': practitioner_urls[1]}]

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_other_roles_stay_on_the_practitioner(self) -> 'None':
        rf1 = 'RF1|A|R|GI^Gastroenterology^L|||REF-6^GP'
        prd = 'PRD|CP|Rahman^Farid^^^Dr'

        bundle = convert(MSH_REF, rf1, prd, PID)
        service_request = one_resource(bundle, 'ServiceRequest')
        practitioner = one_resource(bundle, 'Practitioner')

        # A consulting provider is neither the requester nor a performer,
        # its role stays on the practitioner as-is.
        assert 'requester' not in service_request
        assert 'performer' not in service_request

        extensions = practitioner['extension']
        assert {'url': 'urn:zato:hl7v2:extension/unmapped/PRD-1', 'valueString': 'CP'} in extensions

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_unmapped_prd_fields_are_preserved(self) -> 'None':
        rf1 = 'RF1|A|R|GI^Gastroenterology^L|||REF-7^GP'
        prd = 'PRD|RP|Morrison^Karen^^^Dr|||||||HEALTHLINK^EDI001234'

        bundle = convert(MSH_REF, rf1, prd, PID)
        practitioner = one_resource(bundle, 'Practitioner')

        extensions = practitioner['extension']
        assert {'url': 'urn:zato:hl7v2:extension/unmapped/PRD-9', 'valueString': 'HEALTHLINK^EDI001234'} in extensions

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################

class TestRRI:
    """ RRI - the response to a referral - maps the same way the referral itself does.
    """

    def test_rri_carries_the_referral_back(self) -> 'None':
        msa = 'MSA|AA|MSG00030'
        rf1 = 'RF1|A|R|GI^Gastroenterology^L|||REF-8^GP'

        bundle = convert(MSH_RRI, msa, rf1, PID)
        service_request = one_resource(bundle, 'ServiceRequest')

        # A means the referral was accepted, an active request.
        assert service_request['status'] == 'active'

        identifiers = service_request['identifier']
        assert {'value': 'REF-8', 'system': 'urn:zato:hl7v2:authority:GP'} in identifiers

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################
