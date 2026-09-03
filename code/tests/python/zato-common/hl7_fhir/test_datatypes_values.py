# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.hl7.mappings.concepts import cwe_to_codeable_concept, cwe_to_language_concept, sn_to_observation_value, \
    tag_coding_systems
from zato.hl7.mappings.config import _new_config
from zato.hl7.mappings.datatypes import dtm_to_date, dtm_to_datetime, xtn_to_contact_points

# Local
from conftest import rep

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

def one(points:'anylist') -> 'stranydict':
    """ Returns the only contact point from a list, asserting there is exactly one.
    """
    assert len(points) == 1

    out = points[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestXTN:
    """ XTN fields become FHIR contact points.
    """

    def test_full_telephone(self, default_config:'any_') -> 'None':
        out = xtn_to_contact_points(rep('(555)555-1234^PRN^PH'), default_config)

        assert out == [{
            'value': '(555)555-1234',
            'use': 'home',
            'system': 'phone',
        }]

# ################################################################################################################################

    def test_email(self, default_config:'any_') -> 'None':
        point = one(xtn_to_contact_points(rep('^NET^Internet^john@example.com'), default_config))

        assert point['value'] == 'john@example.com'
        assert point['system'] == 'email'

# ################################################################################################################################

    def test_number_built_from_parts(self, default_config:'any_') -> 'None':
        point = one(xtn_to_contact_points(rep('^WPN^PH^^1^555^5551234^99'), default_config))

        assert point['value'] == '+1 555 5551234 x99'
        assert point['use'] == 'work'

# ################################################################################################################################

    def test_unformatted_number_in_xtn_12(self, default_config:'any_') -> 'None':

        # French senders put the whole number into XTN-12 and nothing else.
        point = one(xtn_to_contact_points(rep('^PRN^PH^^^^^^^^^0388521476'), default_config))

        assert point == {
            'value': '0388521476',
            'use': 'home',
            'system': 'phone',
        }

# ################################################################################################################################

    def test_cellular_phone(self, default_config:'any_') -> 'None':
        # A cellular phone is a phone whose use is mobile - mobile is not a FHIR system.
        point = one(xtn_to_contact_points(rep('555-0000^PRN^CP'), default_config))

        assert point['system'] == 'phone'
        assert point['use'] == 'mobile'

# ################################################################################################################################

    def test_telephone_number_in_the_extension_component(self, default_config:'any_') -> 'None':
        # The whole number can arrive in XTN-8 - with no local number
        # before it, it is the number itself, not an extension.
        point = one(xtn_to_contact_points(rep('^PRN^PH^^^^^030-2345678'), default_config))

        assert point['value'] == '030-2345678'
        assert point['system'] == 'phone'
        assert point['use'] == 'home'

# ################################################################################################################################

    def test_equipment_code_in_the_email_component(self, default_config:'any_') -> 'None':
        # A second equipment code can arrive in XTN-4 - it refines the use,
        # it does not become the value, which comes from the number components.
        point = one(xtn_to_contact_points(rep('^PRN^PH^CP^^^076^5142233'), default_config))

        assert point['value'] == '076 5142233'
        assert point['system'] == 'phone'
        assert point['use'] == 'mobile'

# ################################################################################################################################

    def test_telephone_number_in_the_email_component(self, default_config:'any_') -> 'None':
        # A plain telephone number can arrive in XTN-4 - the equipment type decides.
        point = one(xtn_to_contact_points(rep('^^PH^0302531847'), default_config))

        assert point['value'] == '0302531847'
        assert point['system'] == 'phone'

# ################################################################################################################################

    def test_telephone_and_email_in_one_repetition(self, default_config:'any_') -> 'None':
        # One repetition can carry a phone in XTN-1 and an email in XTN-4 -
        # both become their own contact points.
        out = xtn_to_contact_points(rep('070-5553241^PRN^PH^b.miller@example.com'), default_config)

        phone_point = out[0]
        email_point = out[1]

        assert phone_point == {'value': '070-5553241', 'use': 'home', 'system': 'phone'}
        assert email_point == {'value': 'b.miller@example.com', 'use': 'home', 'system': 'email'}

# ################################################################################################################################

    def test_telephone_and_email_with_internet_equipment(self, default_config:'any_') -> 'None':
        # The NET/Internet equipment type describes the email side of the
        # repetition - the telephone number stays a phone.
        out = xtn_to_contact_points(rep('040-2839174^NET^Internet^p.walker@example.com'), default_config)

        phone_point = out[0]
        email_point = out[1]

        assert phone_point['value'] == '040-2839174'
        assert phone_point['system'] == 'phone'

        assert email_point['value'] == 'p.walker@example.com'
        assert email_point['system'] == 'email'

# ################################################################################################################################

    def test_equipment_codes_in_the_number_components(self, default_config:'any_') -> 'None':
        # NET and Internet can arrive in the country and area code
        # components - they refine the system, they are not number parts.
        out = xtn_to_contact_points(rep('^^^j.carter@example.com^NET^Internet'), default_config)

        point = one(out)

        assert point['value'] == 'j.carter@example.com'
        assert point['system'] == 'email'

# ################################################################################################################################

    def test_default_use(self, default_config:'any_') -> 'None':
        point = one(xtn_to_contact_points(rep('555-0000'), default_config, default_use='home'))
        assert point['use'] == 'home'

# ################################################################################################################################

    def test_empty_xtn(self, default_config:'any_') -> 'None':
        assert xtn_to_contact_points(rep(''), default_config) == []

# ################################################################################################################################
# ################################################################################################################################

class TestCWE:
    """ CWE fields become FHIR codeable concepts.
    """

    def test_full_cwe(self, default_config:'any_') -> 'None':
        out = cwe_to_codeable_concept(rep('Z00.0^Routine health check^I10'), default_config)

        assert out == {
            'coding': [{'code': 'Z00.0', 'display': 'Routine health check', 'system': 'http://hl7.org/fhir/sid/icd-10'}],
            'text': 'Routine health check',
        }

# ################################################################################################################################

    def test_alternate_coding(self, default_config:'any_') -> 'None':
        out = cwe_to_codeable_concept(rep('Z00.0^Routine health check^I10^171207006^Health assessment^SCT'), default_config)

        codings = out['coding']
        alternate_coding = codings[1]

        assert len(codings) == 2
        assert alternate_coding == {
            'code': '171207006',
            'display': 'Health assessment',
            'system': 'http://snomed.info/sct',
        }

# ################################################################################################################################

    def test_original_text_wins(self, default_config:'any_') -> 'None':
        out = cwe_to_codeable_concept(rep('Z00.0^Routine health check^I10^^^^^^Original wording'), default_config)
        assert out['text'] == 'Original wording'

# ################################################################################################################################

    def test_display_only_alternate(self, default_config:'any_') -> 'None':
        # An alternate display can arrive with no alternate code - it still
        # becomes a coding and provides the concept text when nothing else does.
        out = cwe_to_codeable_concept(rep('11502-2^^LN^^Laboratory Report'), default_config)

        codings = out['coding']
        alternate_coding = codings[1]

        assert alternate_coding == {'display': 'Laboratory Report'}
        assert out['text'] == 'Laboratory Report'

# ################################################################################################################################

    def test_text_only(self, default_config:'any_') -> 'None':
        out = cwe_to_codeable_concept(rep('^Free text only'), default_config)
        assert out == {'text': 'Free text only'}

# ################################################################################################################################

    def test_hl7_table_system(self, default_config:'any_') -> 'None':
        out = cwe_to_codeable_concept(rep('M^Married^HL70002'), default_config)

        codings = out['coding']
        coding = codings[0]

        assert coding['system'] == 'http://terminology.hl7.org/CodeSystem/v2-0002'

# ################################################################################################################################

    def test_empty_cwe(self, default_config:'any_') -> 'None':
        assert cwe_to_codeable_concept(rep(''), default_config) is None

# ################################################################################################################################
# ################################################################################################################################

class TestLanguageCWE:
    """ CWE fields holding spoken languages become BCP-47 codeable concepts.
    """

    def test_bare_two_letter_code(self, default_config:'any_') -> 'None':

        # A bare ISO 639-1 code becomes a lowercase BCP-47 coding.
        out = cwe_to_language_concept(rep('EN'), default_config)

        assert out == {
            'coding': [{'system': 'urn:ietf:bcp:47', 'code': 'en'}],
            'text': 'EN',
        }

# ################################################################################################################################

    def test_bare_three_letter_code(self, default_config:'any_') -> 'None':

        # A bare ISO 639-2 code becomes a lowercase BCP-47 coding too.
        out = cwe_to_language_concept(rep('ENG^English'), default_config)

        assert out == {
            'coding': [{'system': 'urn:ietf:bcp:47', 'code': 'eng', 'display': 'English'}],
            'text': 'English',
        }

# ################################################################################################################################

    def test_coded_system_stays(self, default_config:'any_') -> 'None':

        # A coding that already names its system arrived fully specified and stays as it is.
        out = cwe_to_language_concept(rep('en^English^ISO639'), default_config)

        codings = out['coding']
        coding = codings[0]

        assert coding == {'system': 'urn:ietf:bcp:47', 'code': 'en', 'display': 'English'}

# ################################################################################################################################

    def test_non_language_shape_stays(self, default_config:'any_') -> 'None':

        # A code that is not shaped like ISO 639 stays exactly as it arrived.
        out = cwe_to_language_concept(rep('en-GB'), default_config)

        codings = out['coding']
        coding = codings[0]

        assert coding == {'code': 'en-GB'}

# ################################################################################################################################

    def test_empty_language(self, default_config:'any_') -> 'None':
        assert cwe_to_language_concept(rep(''), default_config) is None

# ################################################################################################################################
# ################################################################################################################################

class TestTagCodingSystems:
    """ System-less codings gain the system of the vocabulary map that covers their code.
    """

    def test_covered_code_gains_the_system(self, default_config:'any_') -> 'None':
        concept = cwe_to_codeable_concept(rep('SPO^Spouse'), default_config)
        tag_coding_systems(concept, 'personal_relationship', default_config)

        assert concept == {
            'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v2-0063', 'code': 'SPO', 'display': 'Spouse'}],
            'text': 'Spouse',
        }

# ################################################################################################################################

    def test_translating_map_changes_the_code(self, default_config:'any_') -> 'None':

        # The subscriber-relationship map translates table 0063 codes rather than keeping them.
        concept = cwe_to_codeable_concept(rep('SPO^Spouse'), default_config)
        tag_coding_systems(concept, 'subscriber_relationship', default_config)

        codings = concept['coding']
        coding = codings[0]

        assert coding['code'] == 'spouse'
        assert coding['system'] == 'http://terminology.hl7.org/CodeSystem/subscriber-relationship'

# ################################################################################################################################

    def test_coded_system_stays(self, default_config:'any_') -> 'None':

        # A coding that already names its system arrived fully specified and stays as it is.
        concept = cwe_to_codeable_concept(rep('SPO^Spouse^HL70063'), default_config)
        tag_coding_systems(concept, 'subscriber_relationship', default_config)

        codings = concept['coding']
        coding = codings[0]

        assert coding['code'] == 'SPO'
        assert coding['system'] == 'http://terminology.hl7.org/CodeSystem/v2-0063'

# ################################################################################################################################

    def test_unknown_code_stays(self, default_config:'any_') -> 'None':
        concept = cwe_to_codeable_concept(rep('NK^Next of kin'), default_config)
        tag_coding_systems(concept, 'personal_relationship', default_config)

        assert concept == {
            'coding': [{'code': 'NK', 'display': 'Next of kin'}],
            'text': 'Next of kin',
        }

# ################################################################################################################################
# ################################################################################################################################

class TestDTM:
    """ DTM fields become FHIR dates and datetimes.
    """

    # The DTM precision matrix - every input length the standard defines.
    precision_matrix = [
        ('2024',                     '2024'),
        ('202405',                   '2024-05'),
        ('20240517',                 '2024-05-17'),
        ('2024051714',               '2024-05-17T14:00:00+00:00'),
        ('202405171430',             '2024-05-17T14:30:00+00:00'),
        ('20240517143055',           '2024-05-17T14:30:55+00:00'),
        ('20240517143055.1234',      '2024-05-17T14:30:55.1234+00:00'),
        ('20240517143055+0200',      '2024-05-17T14:30:55+02:00'),
        ('20240517143055-0500',      '2024-05-17T14:30:55-05:00'),
        ('20240517143055.99+0100',   '2024-05-17T14:30:55.99+01:00'),
    ]

    @pytest.mark.parametrize('value,expected', precision_matrix)
    def test_precision_matrix(self, value:'any_', expected:'any_', default_config:'any_') -> 'None':
        assert dtm_to_datetime(value, default_config) == expected

# ################################################################################################################################

    def test_empty_value(self, default_config:'any_') -> 'None':
        assert dtm_to_datetime(None, default_config) is None
        assert dtm_to_datetime('', default_config) is None
        assert dtm_to_datetime('  ', default_config) is None

# ################################################################################################################################

    def test_unparseable_length(self, default_config:'any_') -> 'None':
        assert dtm_to_datetime('202405171', default_config) is None

# ################################################################################################################################

    def test_configured_timezone(self, default_config:'any_') -> 'None':
        config = _new_config()
        config.default_timezone = '+02:00'

        assert dtm_to_datetime('202405171430', config) == '2024-05-17T14:30:00+02:00'

# ################################################################################################################################

    def test_dtm_to_date(self) -> 'None':
        assert dtm_to_date('20240517143055') == '2024-05-17'
        assert dtm_to_date('20240517') == '2024-05-17'
        assert dtm_to_date('202405') == '2024-05'
        assert dtm_to_date('2024') == '2024'
        assert dtm_to_date('') is None
        assert dtm_to_date('202') is None

# ################################################################################################################################
# ################################################################################################################################

class TestSN:
    """ SN fields become quantities, ranges, ratios or strings.
    """

    units = {'coding': [{'code': 'mg/dL', 'system': 'http://unitsofmeasure.org'}], 'text': 'mg/dL'}

    def test_plain_number(self, default_config:'any_') -> 'None':
        out = sn_to_observation_value(rep('^120'), default_config, self.units)
        assert out is not None

        assert out.field_name == 'valueQuantity'
        assert out.content == {
            'value': 120.0,
            'code': 'mg/dL',
            'system': 'http://unitsofmeasure.org',
            'unit': 'mg/dL',
        }
        assert out.is_exact

# ################################################################################################################################

    def test_units_without_system_carry_no_code(self, default_config:'any_') -> 'None':

        # qty-3 - a Quantity code needs a system, so local units keep the unit text only.
        units = {'coding': [{'code': 'TAB'}], 'text': 'tablet'}
        out = sn_to_observation_value(rep('^2'), default_config, units)
        assert out is not None

        assert out.content == {'value': 2.0, 'unit': 'tablet'}

# ################################################################################################################################

    def test_inexact_number(self, default_config:'any_') -> 'None':

        # Twenty digits do not survive a float, which the result says.
        out = sn_to_observation_value(rep('^12345678901234567890'), default_config, None)
        assert out is not None

        assert out.field_name == 'valueQuantity'
        assert not out.is_exact

# ################################################################################################################################

    def test_comparator(self, default_config:'any_') -> 'None':
        out = sn_to_observation_value(rep('>^120'), default_config, None)
        assert out is not None

        assert out.field_name == 'valueQuantity'
        assert out.content == {'value': 120.0, 'comparator': '>'}

# ################################################################################################################################

    def test_range(self, default_config:'any_') -> 'None':
        out = sn_to_observation_value(rep('^3^-^5'), default_config, None)
        assert out is not None

        assert out.field_name == 'valueRange'
        assert out.content == {'low': {'value': 3.0}, 'high': {'value': 5.0}}

# ################################################################################################################################

    def test_ratio_colon(self, default_config:'any_') -> 'None':
        out = sn_to_observation_value(rep('^1^:^128'), default_config, None)
        assert out is not None

        assert out.field_name == 'valueRatio'
        assert out.content == {'numerator': {'value': 1.0}, 'denominator': {'value': 128.0}}

# ################################################################################################################################

    def test_ratio_slash(self, default_config:'any_') -> 'None':
        out = sn_to_observation_value(rep('^1^/^128'), default_config, None)
        assert out is not None

        assert out.field_name == 'valueRatio'

# ################################################################################################################################

    def test_categorical_plus(self, default_config:'any_') -> 'None':
        out = sn_to_observation_value(rep('^2^+'), default_config, None)
        assert out is not None

        assert out.field_name == 'valueString'
        assert out.content == '2+'

# ################################################################################################################################

    def test_string_when_not_numeric(self, default_config:'any_') -> 'None':
        out = sn_to_observation_value(rep('^abc'), default_config, None)
        assert out is not None

        assert out.field_name == 'valueString'
        assert out.content == 'abc'

# ################################################################################################################################

    def test_empty_sn(self, default_config:'any_') -> 'None':
        assert sn_to_observation_value(rep(''), default_config, None) is None

# ################################################################################################################################
# ################################################################################################################################
