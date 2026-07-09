# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.hl7.mappings.datatypes import cwe_to_codeable_concept, cx_to_identifier, dtm_to_date, dtm_to_datetime, \
    ei_to_identifier, sn_to_observation_value, xad_to_address, xcn_to_name_and_identifier, xpn_to_human_name, \
    xtn_to_contact_point

# Local
from conftest import rep

# ################################################################################################################################
# ################################################################################################################################

class TestCX:

    def test_full_cx(self, default_config):
        out = cx_to_identifier(rep('12345^^^MYHOSP^MR'), default_config)

        assert out == {
            'value': '12345',
            'system': 'urn:zato:hl7v2:authority:MYHOSP',
            'type': {'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v2-0203', 'code': 'MR'}]},
        }

    def test_iso_universal_id(self, default_config):
        out = cx_to_identifier(rep('12345^^^MYHOSP&2.16.840.1.113883.19&ISO^MR'), default_config)
        assert out['system'] == 'urn:oid:2.16.840.1.113883.19'

    def test_uuid_universal_id(self, default_config):
        out = cx_to_identifier(rep('12345^^^MYHOSP&A1B2C3D4-0000-0000-0000-000000000000&UUID'), default_config)
        assert out['system'] == 'urn:uuid:a1b2c3d4-0000-0000-0000-000000000000'

    def test_empty_cx(self, default_config):
        assert cx_to_identifier(rep(''), default_config) is None

    def test_value_only(self, default_config):
        out = cx_to_identifier(rep('12345'), default_config)
        assert out == {'value': '12345'}

# ################################################################################################################################
# ################################################################################################################################

class TestEI:

    def test_full_ei(self, default_config):
        out = ei_to_identifier(rep('ORD-1^LAB^2.16.840.1.113883.19.5^ISO'), default_config)

        assert out == {
            'value': 'ORD-1',
            'system': 'urn:oid:2.16.840.1.113883.19.5',
        }

    def test_namespace_only(self, default_config):
        out = ei_to_identifier(rep('ORD-1^LAB'), default_config)
        assert out['system'] == 'urn:zato:hl7v2:authority:LAB'

    def test_empty_ei(self, default_config):
        assert ei_to_identifier(rep(''), default_config) is None

# ################################################################################################################################
# ################################################################################################################################

class TestXPN:

    def test_full_xpn(self, default_config):
        out = xpn_to_human_name(rep('Smith^John^Q^Jr^Dr^MD^L'), default_config)

        assert out == {
            'family': 'Smith',
            'given': ['John', 'Q'],
            'suffix': ['Jr', 'MD'],
            'prefix': ['Dr'],
            'use': 'official',
        }

    def test_maiden_name_use(self, default_config):
        out = xpn_to_human_name(rep('Jones^Mary^^^^^M'), default_config)
        assert out['use'] == 'maiden'

    def test_family_only(self, default_config):
        out = xpn_to_human_name(rep('Smith'), default_config)
        assert out == {'family': 'Smith'}

    def test_empty_xpn(self, default_config):
        assert xpn_to_human_name(rep(''), default_config) is None

# ################################################################################################################################
# ################################################################################################################################

class TestXAD:

    def test_full_xad(self, default_config):
        out = xad_to_address(rep('123 Main St^Apt 4^Springfield^IL^62701^USA^H'), default_config)

        assert out == {
            'line': ['123 Main St', 'Apt 4'],
            'city': 'Springfield',
            'state': 'IL',
            'postalCode': '62701',
            'country': 'USA',
            'use': 'home',
        }

    def test_office_use(self, default_config):
        out = xad_to_address(rep('1 Work Rd^^Metropolis^NY^10001^USA^B'), default_config)
        assert out['use'] == 'work'

    def test_empty_xad(self, default_config):
        assert xad_to_address(rep(''), default_config) is None

# ################################################################################################################################
# ################################################################################################################################

class TestXTN:

    def test_full_telephone(self, default_config):
        out = xtn_to_contact_point(rep('(555)555-1234^PRN^PH'), default_config)

        assert out == {
            'value': '(555)555-1234',
            'use': 'home',
            'system': 'phone',
        }

    def test_email(self, default_config):
        out = xtn_to_contact_point(rep('^NET^Internet^john@example.com'), default_config)

        assert out['value'] == 'john@example.com'
        assert out['system'] == 'email'

    def test_number_built_from_parts(self, default_config):
        out = xtn_to_contact_point(rep('^WPN^PH^^1^555^5551234^99'), default_config)

        assert out['value'] == '+1 555 5551234 x99'
        assert out['use'] == 'work'

    def test_cellular_system(self, default_config):
        out = xtn_to_contact_point(rep('555-0000^PRN^CP'), default_config)
        assert out['system'] == 'mobile'

    def test_default_use(self, default_config):
        out = xtn_to_contact_point(rep('555-0000'), default_config, default_use='home')
        assert out['use'] == 'home'

    def test_empty_xtn(self, default_config):
        assert xtn_to_contact_point(rep(''), default_config) is None

# ################################################################################################################################
# ################################################################################################################################

class TestCWE:

    def test_full_cwe(self, default_config):
        out = cwe_to_codeable_concept(rep('Z00.0^Routine health check^I10'), default_config)

        assert out == {
            'coding': [{'code': 'Z00.0', 'display': 'Routine health check', 'system': 'http://hl7.org/fhir/sid/icd-10'}],
            'text': 'Routine health check',
        }

    def test_alternate_coding(self, default_config):
        out = cwe_to_codeable_concept(rep('Z00.0^Routine health check^I10^171207006^Health assessment^SCT'), default_config)

        codings = out['coding']
        alternate_coding = codings[1]

        assert len(codings) == 2
        assert alternate_coding == {
            'code': '171207006',
            'display': 'Health assessment',
            'system': 'http://snomed.info/sct',
        }

    def test_original_text_wins(self, default_config):
        out = cwe_to_codeable_concept(rep('Z00.0^Routine health check^I10^^^^^^Original wording'), default_config)
        assert out['text'] == 'Original wording'

    def test_text_only(self, default_config):
        out = cwe_to_codeable_concept(rep('^Free text only'), default_config)
        assert out == {'text': 'Free text only'}

    def test_hl7_table_system(self, default_config):
        out = cwe_to_codeable_concept(rep('M^Married^HL70002'), default_config)

        codings = out['coding']
        coding = codings[0]

        assert coding['system'] == 'http://terminology.hl7.org/CodeSystem/v2-0002'

    def test_empty_cwe(self, default_config):
        assert cwe_to_codeable_concept(rep(''), default_config) is None

# ################################################################################################################################
# ################################################################################################################################

class TestXCN:

    def test_full_xcn(self, default_config):
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

    def test_name_only(self, default_config):
        out = xcn_to_name_and_identifier(rep('^Welby^Marcus'), default_config)

        assert 'identifier' not in out
        assert out['name'] == {'family': 'Welby', 'given': ['Marcus']}

    def test_empty_xcn(self, default_config):
        assert xcn_to_name_and_identifier(rep(''), default_config) is None

# ################################################################################################################################
# ################################################################################################################################

class TestDTM:

    # The DTM precision matrix - every input length the standard defines
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
    def test_precision_matrix(self, value, expected, default_config):
        assert dtm_to_datetime(value, default_config) == expected

    def test_empty_value(self, default_config):
        assert dtm_to_datetime(None, default_config) is None
        assert dtm_to_datetime('', default_config) is None
        assert dtm_to_datetime('  ', default_config) is None

    def test_unparseable_length(self, default_config):
        assert dtm_to_datetime('202405171', default_config) is None

    def test_configured_timezone(self, default_config):
        from zato.hl7.mappings.config import _new_config

        config = _new_config()
        config.default_timezone = '+02:00'

        assert dtm_to_datetime('202405171430', config) == '2024-05-17T14:30:00+02:00'

    def test_dtm_to_date(self):
        assert dtm_to_date('20240517143055') == '2024-05-17'
        assert dtm_to_date('20240517') == '2024-05-17'
        assert dtm_to_date('202405') == '2024-05'
        assert dtm_to_date('2024') == '2024'
        assert dtm_to_date('') is None
        assert dtm_to_date('202') is None

# ################################################################################################################################
# ################################################################################################################################

class TestSN:

    units = {'coding': [{'code': 'mg/dL', 'system': 'http://unitsofmeasure.org'}], 'text': 'mg/dL'}

    def test_plain_number(self, default_config):
        out = sn_to_observation_value(rep('^120'), default_config, self.units)

        assert out == ('valueQuantity', {
            'value': 120.0,
            'code': 'mg/dL',
            'system': 'http://unitsofmeasure.org',
            'unit': 'mg/dL',
        })

    def test_comparator(self, default_config):
        field, value = sn_to_observation_value(rep('>^120'), default_config, None)

        assert field == 'valueQuantity'
        assert value == {'value': 120.0, 'comparator': '>'}

    def test_range(self, default_config):
        field, value = sn_to_observation_value(rep('^3^-^5'), default_config, None)

        assert field == 'valueRange'
        assert value == {'low': {'value': 3.0}, 'high': {'value': 5.0}}

    def test_ratio_colon(self, default_config):
        field, value = sn_to_observation_value(rep('^1^:^128'), default_config, None)

        assert field == 'valueRatio'
        assert value == {'numerator': {'value': 1.0}, 'denominator': {'value': 128.0}}

    def test_ratio_slash(self, default_config):
        field, value = sn_to_observation_value(rep('^1^/^128'), default_config, None)
        assert field == 'valueRatio'

    def test_categorical_plus(self, default_config):
        out = sn_to_observation_value(rep('^2^+'), default_config, None)
        assert out == ('valueString', '2+')

    def test_fallback_string(self, default_config):
        out = sn_to_observation_value(rep('^abc'), default_config, None)
        assert out == ('valueString', 'abc')

    def test_empty_sn(self, default_config):
        assert sn_to_observation_value(rep(''), default_config, None) is None

# ################################################################################################################################
# ################################################################################################################################
