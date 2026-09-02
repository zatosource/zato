# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings.config import Insurer_Authority_Systems, _new_config
from zato.hl7.mappings.datatypes import cx_to_identifier, ei_to_identifier, xad_to_address, \
    xcn_to_name_and_identifier, xpn_to_human_name

# Local
from conftest import rep

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

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

    def test_land_authority_fr_patient(self, default_config:'any_') -> 'None':

        # The French INS patient identifiers resolve to the OID URIs from hl7.fhir.fr.core.
        ins_nir = cx_to_identifier(rep('160117510705741^^^INS-NIR^INS'), default_config)
        ins_nia = cx_to_identifier(rep('260127510705785^^^ASIP-SANTE-INS-NIA^INS'), default_config)
        ins_c = cx_to_identifier(rep('160117510705741^^^INS-C^INS'), default_config)

        assert ins_nir['system'] == 'urn:oid:1.2.250.1.213.1.4.8'
        assert ins_nia['system'] == 'urn:oid:1.2.250.1.213.1.4.9'
        assert ins_c['system'] == 'urn:oid:1.2.250.1.213.1.4.2'

# ################################################################################################################################

    def test_land_authority_fr_registries(self, default_config:'any_') -> 'None':

        # The French practitioner and facility registries resolve to their official URIs.
        rpps = cx_to_identifier(rep('10101898741^^^RPPS'), default_config)
        adeli = cx_to_identifier(rep('751234567^^^ADELI'), default_config)
        finess = cx_to_identifier(rep('750712184^^^FINESS'), default_config)
        national_ps = cx_to_identifier(rep('810101898741^^^ASIP-SANTE-PS'), default_config)
        national_st = cx_to_identifier(rep('10750712184^^^ASIP-SANTE-ST'), default_config)

        assert rpps['system'] == 'https://rpps.esante.gouv.fr'
        assert adeli['system'] == 'https://adeli.esante.gouv.fr'
        assert finess['system'] == 'https://finess.esante.gouv.fr'
        assert national_ps['system'] == 'urn:oid:1.2.250.1.71.4.2.1'
        assert national_st['system'] == 'urn:oid:1.2.250.1.71.4.2.2'

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
