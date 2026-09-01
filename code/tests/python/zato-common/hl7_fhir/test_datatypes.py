# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.hl7.mappings.config import Insurer_Authority_Systems, _new_config
from zato.hl7.mappings.datatypes import cwe_to_codeable_concept, cwe_to_language_concept, cx_to_identifier, dtm_to_date, \
    dtm_to_datetime, ei_to_identifier, sn_to_observation_value, tag_coding_systems, xad_to_address, \
    xcn_to_name_and_identifier, xpn_to_human_name, xtn_to_contact_points

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

class TestCX:
    """ CX fields become FHIR identifiers.
    """

    def test_full_cx(self, default_config:'any_') -> 'None':
        out = cx_to_identifier(rep('12345^^^MYHOSP^MR'), default_config)

        assert out == {
            'value': '12345',
            'system': 'urn:zato:hl7v2:authority:MYHOSP',
            'type': {'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v2-0203', 'code': 'MR'}]},
        }

# ################################################################################################################################

    def test_iso_universal_id(self, default_config:'any_') -> 'None':
        out = cx_to_identifier(rep('12345^^^MYHOSP&2.16.840.1.113883.19&ISO^MR'), default_config)
        assert out['system'] == 'urn:oid:2.16.840.1.113883.19'

# ################################################################################################################################

    def test_uuid_universal_id(self, default_config:'any_') -> 'None':
        out = cx_to_identifier(rep('12345^^^MYHOSP&A1B2C3D4-0000-0000-0000-000000000000&UUID'), default_config)
        assert out['system'] == 'urn:uuid:a1b2c3d4-0000-0000-0000-000000000000'

# ################################################################################################################################

    def test_empty_cx(self, default_config:'any_') -> 'None':
        assert cx_to_identifier(rep(''), default_config) is None

# ################################################################################################################################

    def test_value_only(self, default_config:'any_') -> 'None':
        out = cx_to_identifier(rep('12345'), default_config)
        assert out == {'value': '12345'}

# ################################################################################################################################

    def test_land_authority_nhs(self, default_config:'any_') -> 'None':

        # A land authority maps to its official identifier system URI.
        out = cx_to_identifier(rep('9434765919^^^NHS^NH'), default_config)

        assert out['value'] == '9434765919'
        assert out['system'] == 'https://fhir.nhs.uk/Id/nhs-number'

# ################################################################################################################################

    def test_land_authority_bsn(self, default_config:'any_') -> 'None':
        out = cx_to_identifier(rep('999911120^^^NLMINBIZA^NNNLD'), default_config)

        assert out['value'] == '999911120'
        assert out['system'] == 'http://fhir.nl/fhir/NamingSystem/bsn'

# ################################################################################################################################

    def test_land_authority_gmc(self, default_config:'any_') -> 'None':
        out = cx_to_identifier(rep('7512345^^^GMC'), default_config)

        assert out['value'] == '7512345'
        assert out['system'] == 'https://fhir.hl7.org.uk/Id/gmc-number'

# ################################################################################################################################

    def test_config_overrides_land_authority(self) -> 'None':

        # A per-config identifier system wins over the built-in land entry.
        config = _new_config()
        config.identifier_systems['NHS'] = 'https://example.com/nhs'

        out = cx_to_identifier(rep('9434765919^^^NHS^NH'), config)

        assert out['system'] == 'https://example.com/nhs'

# ################################################################################################################################

    def test_land_authority_registries(self, default_config:'any_') -> 'None':

        # Practitioner and provider registries map to their official URIs too.
        big = cx_to_identifier(rep('19012345601^^^BIG'), default_config)
        npi = cx_to_identifier(rep('1234567893^^^NPI'), default_config)

        assert big['system'] == 'http://fhir.nl/fhir/NamingSystem/big'
        assert npi['system'] == 'http://hl7.org/fhir/sid/us-npi'

# ################################################################################################################################

    def test_holder_specific_authority(self, default_config:'any_') -> 'None':

        # Vektis runs both the UZOVI insurer register and the AGB care provider register,
        # so the same authority resolves by who holds the identifier.
        insurer = cx_to_identifier(rep('3311^^^VEKTIS'), default_config, Insurer_Authority_Systems)
        practitioner = xcn_to_name_and_identifier(rep('01004567^Smith^A^^^^^^VEKTIS'), default_config)

        assert insurer['system'] == 'http://fhir.nl/fhir/NamingSystem/uzovi'

        practitioner_identifier = practitioner['identifier']
        assert practitioner_identifier['system'] == 'http://fhir.nl/fhir/NamingSystem/agb-z'

# ################################################################################################################################

    def test_holderless_authority_stays_a_urn(self, default_config:'any_') -> 'None':

        # Without a holder-specific map the authority derives a URN as any other does.
        out = cx_to_identifier(rep('3311^^^VEKTIS'), default_config)

        assert out['system'] == 'urn:zato:hl7v2:authority:VEKTIS'

# ################################################################################################################################
# ################################################################################################################################

class TestEI:
    """ EI fields become FHIR identifiers.
    """

    def test_full_ei(self, default_config:'any_') -> 'None':
        out = ei_to_identifier(rep('ORD-1^LAB^2.16.840.1.113883.19.5^ISO'), default_config)

        assert out == {
            'value': 'ORD-1',
            'system': 'urn:oid:2.16.840.1.113883.19.5',
        }

# ################################################################################################################################

    def test_namespace_only(self, default_config:'any_') -> 'None':
        out = ei_to_identifier(rep('ORD-1^LAB'), default_config)
        assert out['system'] == 'urn:zato:hl7v2:authority:LAB'

# ################################################################################################################################

    def test_empty_ei(self, default_config:'any_') -> 'None':
        assert ei_to_identifier(rep(''), default_config) is None

# ################################################################################################################################
# ################################################################################################################################

class TestXPN:
    """ XPN fields become FHIR human names.
    """

    def test_full_xpn(self, default_config:'any_') -> 'None':
        out = xpn_to_human_name(rep('Smith^John^Q^Jr^Dr^MD^L'), default_config)

        assert out == {
            'family': 'Smith',
            'given': ['John', 'Q'],
            'suffix': ['Jr', 'MD'],
            'prefix': ['Dr'],
            'use': 'official',
        }

# ################################################################################################################################

    def test_maiden_name_use(self, default_config:'any_') -> 'None':
        out = xpn_to_human_name(rep('Jones^Mary^^^^^M'), default_config)
        assert out['use'] == 'maiden'

# ################################################################################################################################

    def test_birth_name_use(self, default_config:'any_') -> 'None':
        # The birth name type code maps to the official use.
        out = xpn_to_human_name(rep('Jones^Mary^^^^^B'), default_config)
        assert out['use'] == 'official'

# ################################################################################################################################

    def test_own_surname_subcomponents(self, default_config:'any_') -> 'None':
        # The full surname can be empty while the FN own-surname prefix
        # and own-surname subcomponents carry the name.
        out = xpn_to_human_name(rep('&van&Cleef^Lee'), default_config)

        assert out['family'] == 'van Cleef'
        assert out['given'] == ['Lee']

# ################################################################################################################################

    def test_family_only(self, default_config:'any_') -> 'None':
        out = xpn_to_human_name(rep('Smith'), default_config)
        assert out == {'family': 'Smith'}

# ################################################################################################################################

    def test_empty_xpn(self, default_config:'any_') -> 'None':
        assert xpn_to_human_name(rep(''), default_config) is None

# ################################################################################################################################
# ################################################################################################################################

class TestXAD:
    """ XAD fields become FHIR addresses.
    """

    def test_full_xad(self, default_config:'any_') -> 'None':
        out = xad_to_address(rep('123 Main St^Apt 4^Springfield^IL^62701^USA^H'), default_config)

        assert out == {
            'line': ['123 Main St', 'Apt 4'],
            'city': 'Springfield',
            'state': 'IL',
            'postalCode': '62701',
            'country': 'USA',
            'use': 'home',
        }

# ################################################################################################################################

    def test_office_use(self, default_config:'any_') -> 'None':
        out = xad_to_address(rep('1 Work Rd^^Metropolis^NY^10001^USA^B'), default_config)
        assert out['use'] == 'work'

# ################################################################################################################################

    def test_empty_xad(self, default_config:'any_') -> 'None':
        assert xad_to_address(rep(''), default_config) is None

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

class TestXCN:
    """ XCN fields become names paired with identifiers.
    """

    def test_full_xcn(self, default_config:'any_') -> 'None':
        out = xcn_to_name_and_identifier(rep('1234^Welby^Marcus^J^Jr^Dr^MD^^MYHOSP&1.2.3&ISO^^^^NPI'), default_config)

        assert out['identifier'] == {
            'value': '1234',
            'system': 'urn:oid:1.2.3',
            'type': {'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v2-0203', 'code': 'NPI'}]},
        }

        assert out['name'] == {
            'family': 'Welby',
            'given': ['Marcus', 'J'],
            'suffix': ['Jr', 'MD'],
            'prefix': ['Dr'],
        }

# ################################################################################################################################

    def test_name_only(self, default_config:'any_') -> 'None':
        out = xcn_to_name_and_identifier(rep('^Welby^Marcus'), default_config)

        assert 'identifier' not in out
        assert out['name'] == {'family': 'Welby', 'given': ['Marcus']}

# ################################################################################################################################

    def test_empty_xcn(self, default_config:'any_') -> 'None':
        assert xcn_to_name_and_identifier(rep(''), default_config) is None

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

        assert out == ('valueQuantity', {
            'value': 120.0,
            'code': 'mg/dL',
            'system': 'http://unitsofmeasure.org',
            'unit': 'mg/dL',
        })

# ################################################################################################################################

    def test_comparator(self, default_config:'any_') -> 'None':
        result = sn_to_observation_value(rep('>^120'), default_config, None)
        assert result is not None

        field, value = result

        assert field == 'valueQuantity'
        assert value == {'value': 120.0, 'comparator': '>'}

# ################################################################################################################################

    def test_range(self, default_config:'any_') -> 'None':
        result = sn_to_observation_value(rep('^3^-^5'), default_config, None)
        assert result is not None

        field, value = result

        assert field == 'valueRange'
        assert value == {'low': {'value': 3.0}, 'high': {'value': 5.0}}

# ################################################################################################################################

    def test_ratio_colon(self, default_config:'any_') -> 'None':
        result = sn_to_observation_value(rep('^1^:^128'), default_config, None)
        assert result is not None

        field, value = result

        assert field == 'valueRatio'
        assert value == {'numerator': {'value': 1.0}, 'denominator': {'value': 128.0}}

# ################################################################################################################################

    def test_ratio_slash(self, default_config:'any_') -> 'None':
        result = sn_to_observation_value(rep('^1^/^128'), default_config, None)
        assert result is not None

        field, _ = result
        assert field == 'valueRatio'

# ################################################################################################################################

    def test_categorical_plus(self, default_config:'any_') -> 'None':
        out = sn_to_observation_value(rep('^2^+'), default_config, None)
        assert out == ('valueString', '2+')

# ################################################################################################################################

    def test_string_when_not_numeric(self, default_config:'any_') -> 'None':
        out = sn_to_observation_value(rep('^abc'), default_config, None)
        assert out == ('valueString', 'abc')

# ################################################################################################################################

    def test_empty_sn(self, default_config:'any_') -> 'None':
        assert sn_to_observation_value(rep(''), default_config, None) is None

# ################################################################################################################################
# ################################################################################################################################
