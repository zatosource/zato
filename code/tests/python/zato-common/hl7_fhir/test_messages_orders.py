# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# Zato
from zato.hl7v2 import parse_hl7

# Local
from conftest import Samples_Dir, Test_Conversions_Dir, convert, load_message, one_resource, resources_of_type

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

MSH_ORU = 'MSH|^~\\&|LAB|LABFAC|EHR|EHRFAC|20240517143055||ORU^R01|MSG00002|P|2.5'
MSH_ORM = 'MSH|^~\\&|EHR|EHRFAC|LAB|LABFAC|20240517143055||ORM^O01|MSG00003|P|2.5'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M'

# ################################################################################################################################
# ################################################################################################################################

def _convert_fixture(file_path:'str') -> 'any_':
    """ Parses one fixture message and converts it to a bundle.
    """
    raw = load_message(file_path)
    msg = parse_hl7(raw, validate=False)

    out = msg.to_fhir()
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestORUGrouping:
    """ ORC/OBR/OBX/SPM/NTE grouping in result messages.
    """

    def test_obr_opens_report_and_service_request(self) -> 'None':
        orc = 'ORC|RE|ORD-1^EHR|FIL-1^LAB|||||||||1234^Welby^Marcus'
        obr = 'OBR|1|ORD-1^EHR|FIL-1^LAB|24331-1^Lipid panel^LN||||||||||||||||||20240517150000|||F'
        obx = 'OBX|1|NM|2093-3^Cholesterol^LN||180|mg/dL^^UCUM||N|||F'

        bundle = convert(MSH_ORU, PID, orc, obr, obx)

        service_request = one_resource(bundle, 'ServiceRequest')
        report = one_resource(bundle, 'DiagnosticReport')

        # There is exactly one observation in the bundle.
        one_resource(bundle, 'Observation')

        # The order code carried over.
        request_code = service_request['code']
        assert request_code['text'] == 'Lipid panel'

        # The report is based on the service request.
        bundle_dict = bundle.to_dict()
        request_url = None

        for entry in bundle_dict['entry']:
            resource = entry['resource']
            if resource['resourceType'] == 'ServiceRequest':
                request_url = entry['fullUrl']

        assert report['basedOn'] == [{'reference': request_url}]

        # The report collects the observation as its result.
        observation_url = None

        for entry in bundle_dict['entry']:
            resource = entry['resource']
            if resource['resourceType'] == 'Observation':
                observation_url = entry['fullUrl']

        assert report['result'] == [{'reference': observation_url}]

        # F means the report is final.
        assert report['status'] == 'final'

# ################################################################################################################################

    def test_non_datetime_results_reported_value_is_preserved(self) -> 'None':
        # Other values can arrive in the OBR-22 results-reported slot -
        # those cannot become the issued time but they are not dropped either.
        obr = 'OBR|1|ORD-1^EHR|FIL-1^LAB|24331-1^Lipid panel^LN||||||||||||||||||LAB'

        bundle = convert(MSH_ORU, PID, obr)
        report = one_resource(bundle, 'DiagnosticReport')

        assert 'issued' not in report

        extensions = report['extension']

        assert {'url': 'urn:zato:hl7v2:extension/unmapped/OBR-22', 'valueString': 'LAB'} in extensions

# ################################################################################################################################

    def test_multiple_obr_groups(self) -> 'None':
        obr_first = 'OBR|1|ORD-1^EHR||24331-1^Lipid panel^LN'
        obx_first = 'OBX|1|NM|2093-3^Cholesterol^LN||180|mg/dL^^UCUM||N|||F'
        obr_second = 'OBR|2|ORD-2^EHR||58410-2^CBC panel^LN'
        obx_second = 'OBX|1|NM|718-7^Hemoglobin^LN||14|g/dL^^UCUM||N|||F'

        bundle = convert(MSH_ORU, PID, obr_first, obx_first, obr_second, obx_second)

        reports = resources_of_type(bundle, 'DiagnosticReport')
        observations = resources_of_type(bundle, 'Observation')

        assert len(reports) == 2
        assert len(observations) == 2

        # Each report holds exactly the observation from its own group.
        first_report = reports[0]
        second_report = reports[1]

        first_results = first_report['result']
        second_results = second_report['result']

        assert len(first_results) == 1
        assert len(second_results) == 1
        assert first_results != second_results

# ################################################################################################################################

    def test_orc_after_obr_enriches_the_same_order(self) -> 'None':
        # In OUL-style result messages the ORC follows the OBR of its own order group.
        obr = 'OBR|1|ORD-1^EHR||24331-1^Lipid panel^LN'
        orc = 'ORC|RE|ORD-1^EHR|||||||20240517150000'
        obx = 'OBX|1|NM|2093-3^Cholesterol^LN||180|mg/dL^^UCUM||N|||F'

        bundle = convert(MSH_ORU, PID, obr, orc, obx)

        # The trailing ORC never became a second order of its own.
        service_request = one_resource(bundle, 'ServiceRequest')

        # Its transaction time reached the one request the OBR made.
        assert service_request['authoredOn'] == '2024-05-17T15:00:00+00:00'

# ################################################################################################################################

    def test_nte_attaches_to_observation(self) -> 'None':
        obr = 'OBR|1|ORD-1^EHR||24331-1^Lipid panel^LN'
        obx = 'OBX|1|NM|2093-3^Cholesterol^LN||180|mg/dL^^UCUM||N|||F'
        nte = 'NTE|1||Great result, keep it up'

        bundle = convert(MSH_ORU, PID, obr, obx, nte)
        observation = one_resource(bundle, 'Observation')

        assert observation['note'] == [{'text': 'Great result, keep it up'}]

# ################################################################################################################################

    def test_priority_word_in_the_interval_component(self) -> 'None':
        # The spelled-out priority can arrive in the TQ interval component.
        obr = 'OBR|1|ORD-1^EHR||24331-1^Lipid panel^LN|||||||||||||||||||||||^STAT'

        bundle = convert(MSH_ORM, PID, obr)
        service_request = one_resource(bundle, 'ServiceRequest')

        assert service_request['priority'] == 'stat'

# ################################################################################################################################

    def test_nte_keeps_unescaped_separators(self) -> 'None':
        # Comment text can carry raw carets without escaping them.
        obr = 'OBR|1|ORD-1^EHR||24331-1^Lipid panel^LN'
        obx = 'OBX|1|NM|2093-3^Cholesterol^LN||180|mg/dL^^UCUM||N|||F'
        nte = 'NTE|1||Culture >10^5 CFU/mL, monomicrobial'

        bundle = convert(MSH_ORU, PID, obr, obx, nte)
        observation = one_resource(bundle, 'Observation')

        assert observation['note'] == [{'text': 'Culture >10^5 CFU/mL, monomicrobial'}]

# ################################################################################################################################

    def test_text_observation_keeps_unescaped_separators(self) -> 'None':
        obr = 'OBR|1|ORD-1^EHR||24331-1^Lipid panel^LN'
        obx = 'OBX|1|TX|48767-8^Comment^LN||Ratio 1^2 confirmed||||||F'

        bundle = convert(MSH_ORU, PID, obr, obx)
        observation = one_resource(bundle, 'Observation')

        assert observation['valueString'] == 'Ratio 1^2 confirmed'

# ################################################################################################################################

    def test_reference_pointer_keeps_all_repetitions(self) -> 'None':
        # When the encoding characters make backslash the repetition separator,
        # a URL with escape sequences splits into several repetitions - all of them
        # stay in the value.
        obr = 'OBR|1|ORD-1^EHR||24331-1^Lipid panel^LN'
        obx = 'OBX|34|RP|PDFLINK^^EHR|34|https://example.com/a?b=1~T~c=2~T~d=3||||||F'

        bundle = convert(MSH_ORU, PID, obr, obx)
        observation = one_resource(bundle, 'Observation')

        assert observation['valueString'] == 'https://example.com/a?b=1~T~c=2~T~d=3'

# ################################################################################################################################

    def test_nte_attaches_to_service_request_without_observation(self) -> 'None':
        orc = 'ORC|NW|ORD-1^EHR'
        nte = 'NTE|1||Patient prefers morning appointments'

        bundle = convert(MSH_ORM, PID, orc, nte)
        service_request = one_resource(bundle, 'ServiceRequest')

        assert service_request['note'] == [{'text': 'Patient prefers morning appointments'}]

# ################################################################################################################################

    def test_spm_attaches_to_report(self) -> 'None':
        obr = 'OBR|1|ORD-1^EHR||24331-1^Lipid panel^LN'
        spm = 'SPM|1|SPEC-1||119361006^Plasma^SCT|||||||||||||20240517120000'

        bundle = convert(MSH_ORU, PID, obr, spm)

        specimen = one_resource(bundle, 'Specimen')
        report = one_resource(bundle, 'DiagnosticReport')

        specimen_identifiers = specimen['identifier']
        specimen_identifier = specimen_identifiers[0]

        assert specimen_identifier['value'] == 'SPEC-1'

        specimen_type = specimen['type']
        type_codings = specimen_type['coding']
        type_coding = type_codings[0]

        assert type_coding['code'] == '119361006'
        assert specimen['collection'] == {'collectedDateTime': '2024-05-17T12:00:00+00:00'}

        # The report points at the specimen from its group.
        bundle_dict = bundle.to_dict()
        specimen_url = None

        for entry in bundle_dict['entry']:
            resource = entry['resource']
            if resource['resourceType'] == 'Specimen':
                specimen_url = entry['fullUrl']

        assert report['specimen'] == [{'reference': specimen_url}]

# ################################################################################################################################
# ################################################################################################################################

class TestORMOrders:
    """ Order messages produce ServiceRequests without DiagnosticReports.
    """

    def test_orc_obr_pair(self) -> 'None':
        orc = 'ORC|NW|ORD-1^EHR|FIL-1^LAB||IP||||20240517100000|||1234^Welby^Marcus'
        obr = 'OBR|1|ORD-1^EHR|FIL-1^LAB|24331-1^Lipid panel^LN'

        bundle = convert(MSH_ORM, PID, orc, obr)
        service_request = one_resource(bundle, 'ServiceRequest')

        assert service_request['intent'] == 'order'

        # IP maps through the order status table.
        assert service_request['status'] == 'active'

        assert service_request['authoredOn'] == '2024-05-17T10:00:00+00:00'

        # Both order numbers made it into the identifiers.
        identifiers = service_request['identifier']
        identifier_values = set()

        for identifier in identifiers:
            identifier_values.add(identifier['value'])

        assert identifier_values == {'ORD-1', 'FIL-1'}

        # The ordering provider is the requester.
        requester = service_request['requester']
        requester_url = requester['reference']

        assert requester_url.startswith('urn:uuid:')

        # An order message produces no report.
        reports = resources_of_type(bundle, 'DiagnosticReport')
        assert reports == []

# ################################################################################################################################

    def test_orc_without_obr(self) -> 'None':
        orc = 'ORC|NW|ORD-1^EHR'

        bundle = convert(MSH_ORM, PID, orc)
        service_request = one_resource(bundle, 'ServiceRequest')

        identifiers = service_request['identifier']
        identifier = identifiers[0]

        assert identifier['value'] == 'ORD-1'

# ################################################################################################################################

    def test_tq1_between_orc_and_obr(self) -> 'None':
        # In OML-style messages the TQ1 timing comes before the OBR it belongs to.
        orc = 'ORC|NW|ORD-1^EHR'
        tq1 = 'TQ1|1||||||20240601090000|20240601100000|R'
        obr = 'OBR|1|ORD-1^EHR||24331-1^Lipid panel^LN'

        bundle = convert(MSH_ORM, PID, orc, tq1, obr)
        service_request = one_resource(bundle, 'ServiceRequest')

        # The held-back TQ1 applied to the order once the OBR arrived.
        assert service_request['occurrencePeriod'] == {
            'start': '2024-06-01T09:00:00+00:00',
            'end': '2024-06-01T10:00:00+00:00',
        }

        assert service_request['priority'] == 'routine'

        # The TQ1 never became a standalone preserved segment.
        basics = resources_of_type(bundle, 'Basic')
        assert basics == []

# ################################################################################################################################

    def test_two_orders_in_one_message(self) -> 'None':
        orc_first = 'ORC|NW|ORD-1^EHR'
        obr_first = 'OBR|1|ORD-1^EHR||24331-1^Lipid panel^LN'
        orc_second = 'ORC|NW|ORD-2^EHR'
        obr_second = 'OBR|2|ORD-2^EHR||58410-2^CBC panel^LN'

        bundle = convert(MSH_ORM, PID, orc_first, obr_first, orc_second, obr_second)

        service_requests = resources_of_type(bundle, 'ServiceRequest')
        assert len(service_requests) == 2

# ################################################################################################################################
# ################################################################################################################################

class TestIGOrderConversions:
    """ The IG's agreed order and result test conversion messages.
    """

    def test_oru_r01(self) -> 'None':
        fixture_path = os.path.join(Test_Conversions_Dir, 'ORU_R01.hl7')
        bundle = _convert_fixture(fixture_path)

        report = one_resource(bundle, 'DiagnosticReport')
        observations = resources_of_type(bundle, 'Observation')

        # There is exactly one service request in the bundle.
        one_resource(bundle, 'ServiceRequest')

        # The message carries three OBX segments and the report collects them all.
        assert len(observations) == 3

        results = report['result']
        assert len(results) == 3

        assert report['status'] == 'final'

# ################################################################################################################################

    def test_orm_o01(self) -> 'None':
        fixture_path = os.path.join(Test_Conversions_Dir, 'ORM_O01.hl7')
        bundle = _convert_fixture(fixture_path)

        service_request = one_resource(bundle, 'ServiceRequest')
        assert service_request['intent'] == 'order'

        reports = resources_of_type(bundle, 'DiagnosticReport')
        assert reports == []

# ################################################################################################################################

    def test_oml_o21(self) -> 'None':
        fixture_path = os.path.join(Test_Conversions_Dir, 'OML_O21.hl7')
        bundle = _convert_fixture(fixture_path)

        service_request = one_resource(bundle, 'ServiceRequest')
        assert service_request['intent'] == 'order'

        # There is exactly one specimen in the bundle.
        one_resource(bundle, 'Specimen')

# ################################################################################################################################
# ################################################################################################################################

def _order_sample_paths() -> 'anylist':
    """ All the ORU, ORM and OML messages from the samples fixture tree.
    """
    out = []

    for file_name in sorted(os.listdir(Samples_Dir)):
        if file_name.startswith(('ORU', 'ORM', 'OML')):
            if file_name.endswith('.hl7'):
                full_path = os.path.join(Samples_Dir, file_name)
                out.append(full_path)

    return out

# ################################################################################################################################

_order_paths = _order_sample_paths()

# ################################################################################################################################

@pytest.mark.parametrize('file_path', _order_paths, ids=os.path.basename)
def test_order_samples_end_to_end(file_path:'any_') -> 'None':
    """ Every order and result sample converts to a bundle with a patient.
    """
    raw = load_message(file_path)
    msg = parse_hl7(raw, validate=False)

    bundle = msg.to_fhir()
    bundle_dict = bundle.to_dict()

    assert bundle_dict['type'] == 'transaction'

    patients = resources_of_type(bundle, 'Patient')
    assert len(patients) == 1

    # Result messages carry at least one report with its results attached.
    file_name = os.path.basename(file_path)

    if file_name.startswith('ORU'):
        reports = resources_of_type(bundle, 'DiagnosticReport')
        assert len(reports) >= 1

# ################################################################################################################################
# ################################################################################################################################
