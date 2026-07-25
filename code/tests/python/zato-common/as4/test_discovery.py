# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# cryptography
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.x509 import Name, NameAttribute
from cryptography.x509.oid import NameOID

# pytest
import pytest

# Zato
from zato.common.as4.common import AS4Exception
from zato.common.as4.discovery import lookup_endpoint, participant_dns_name, SML_Domain_Test, \
    Transport_Profile_Peppol_AS4

from .conftest import _rsa_key_size, _rsa_public_exponent, make_certificate, sign_smp_metadata

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# The SMP metadata for one participant and document type, as a Peppol SMP publishes it before signing.
SMP_Metadata = b'''<?xml version="1.0" encoding="UTF-8"?>
<smp:SignedServiceMetadata xmlns:smp="http://busdox.org/serviceMetadata/publishing/1.0/">
  <smp:ServiceMetadata>
    <smp:ServiceInformation>
      <smp:ProcessList>
        <smp:Process>
          <smp:ServiceEndpointList>
            <smp:Endpoint transportProfile="peppol-transport-as4-v2_0">
              <wsa:EndpointReference xmlns:wsa="http://www.w3.org/2005/08/addressing">
                <wsa:Address>https://ap.example.com/as4</wsa:Address>
              </wsa:EndpointReference>
              <smp:Certificate>dGVzdC1jZXJ0aWZpY2F0ZS1ieXRlcw==</smp:Certificate>
            </smp:Endpoint>
          </smp:ServiceEndpointList>
        </smp:Process>
      </smp:ProcessList>
    </smp:ServiceInformation>
  </smp:ServiceMetadata>
</smp:SignedServiceMetadata>'''

Document_Type = 'busdox-docid-qns::urn:oasis:names:specification:ubl:schema:xsd:Invoice-2'

# ################################################################################################################################
# ################################################################################################################################

def _lookup(metadata:'bytes', trust_anchors:'any_', smp_uri:'str'='https://smp.example.com') -> 'any_':
    """ Runs one discovery with DNS and HTTP replaced by what the test supplies.
    """
    def naptr_lookup(dns_name:'any_') -> 'any_':
        return [smp_uri]

    def http_get(url:'any_') -> 'any_':
        return metadata

    out = lookup_endpoint(
        'iso6523-actorid-upis',
        '0192:991825827',
        Document_Type,
        trust_anchors,
        sml_domain=SML_Domain_Test,
        naptr_lookup=naptr_lookup,
        http_get=http_get,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def signed_metadata(rsa_parties:'TestParties') -> 'bytes':
    """ SMP metadata signed by a certificate the test CA issued.
    """
    signing_key = rsa_parties.sender.signing_key
    certificate = rsa_parties.sender.signing_certificate_chain[0]

    out = sign_smp_metadata(SMP_Metadata, signing_key, certificate)
    return out

# ################################################################################################################################

@pytest.fixture
def foreign_metadata() -> 'bytes':
    """ SMP metadata signed with a self-issued certificate belonging to no network.
    """
    signing_key = generate_private_key(_rsa_public_exponent, _rsa_key_size)
    name = Name([NameAttribute(NameOID.COMMON_NAME, 'as4-outside-the-network')])

    certificate = make_certificate('as4-outside-the-network', signing_key.public_key(), name, signing_key, SHA256())

    out = sign_smp_metadata(SMP_Metadata, signing_key, certificate)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestParticipantDNSName:

    def test_dns_name_shape(self) -> 'None':
        name = participant_dns_name('iso6523-actorid-upis', '0192:991825827', SML_Domain_Test)

        hash_part, scheme_part, rest = name.split('.', 2)

        # BDXL: unpadded lowercase base32 of a SHA-256 hash is always 52 characters.
        assert len(hash_part) == 52
        assert hash_part == hash_part.lower()
        assert scheme_part == 'iso6523-actorid-upis'
        assert rest == SML_Domain_Test

# ################################################################################################################################

    def test_dns_name_is_case_insensitive(self) -> 'None':
        name_lower = participant_dns_name('iso6523-actorid-upis', '0192:abcdef', SML_Domain_Test)
        name_upper = participant_dns_name('iso6523-actorid-upis', '0192:ABCDEF', SML_Domain_Test)

        assert name_lower == name_upper

# ################################################################################################################################

    def test_dns_name_known_value(self) -> 'None':
        # Computed independently: base32(sha256('0192:991825827')) without padding, lowercased.
        name = participant_dns_name('iso6523-actorid-upis', '0192:991825827', 'edelivery.tech.ec.europa.eu')

        expected_hash = '7i2243uolq5qzb6jxfvi6yei4iq7sfipkv55htzfnr6s54y6yufa'
        assert name == f'{expected_hash}.iso6523-actorid-upis.edelivery.tech.ec.europa.eu'

# ################################################################################################################################
# ################################################################################################################################

class TestLookupEndpoint:

    def test_lookup_happy_path(self, signed_metadata:'bytes', rsa_parties:'TestParties') -> 'None':
        urls_requested = []

        def naptr_lookup(dns_name:'any_') -> 'any_':
            assert dns_name.endswith(SML_Domain_Test)
            return ['https://smp.example.com']

        def http_get(url:'any_') -> 'any_':
            urls_requested.append(url)
            return signed_metadata

        endpoint = lookup_endpoint(
            'iso6523-actorid-upis',
            '0192:991825827',
            Document_Type,
            [rsa_parties.ca_certificate],
            sml_domain=SML_Domain_Test,
            naptr_lookup=naptr_lookup,
            http_get=http_get,
        )

        assert endpoint.url == 'https://ap.example.com/as4'
        assert endpoint.certificate_der == b'test-certificate-bytes'
        assert endpoint.transport_profile == Transport_Profile_Peppol_AS4

        # Both the participant and the document type are percent-encoded in the SMP URL.
        assert len(urls_requested) == 1
        url = urls_requested[0]
        assert url.startswith('https://smp.example.com/iso6523-actorid-upis%3A%3A0192%3A991825827/services/')
        assert 'busdox-docid-qns%3A%3A' in url

# ################################################################################################################################

    def test_no_smp_in_dns_raises(self, rsa_parties:'TestParties') -> 'None':
        def naptr_lookup(dns_name:'any_') -> 'any_':
            return []

        def http_get(url:'any_') -> 'any_':
            return b''

        with pytest.raises(AS4Exception):
            _ = lookup_endpoint(
                'iso6523-actorid-upis', '0192:991825827', 'doc-type', [rsa_parties.ca_certificate],
                naptr_lookup=naptr_lookup, http_get=http_get,
            )

# ################################################################################################################################

    def test_no_matching_transport_profile_raises(self, signed_metadata:'bytes', rsa_parties:'TestParties') -> 'None':
        def naptr_lookup(dns_name:'any_') -> 'any_':
            return ['https://smp.example.com']

        def http_get(url:'any_') -> 'any_':
            return signed_metadata

        with pytest.raises(AS4Exception):
            _ = lookup_endpoint(
                'iso6523-actorid-upis', '0192:991825827', 'doc-type', [rsa_parties.ca_certificate],
                transport_profile='some-other-profile',
                naptr_lookup=naptr_lookup, http_get=http_get,
            )

# ################################################################################################################################
# ################################################################################################################################

class TestMetadataSignature:
    """ The endpoint URL and the certificate published in SMP metadata decide where a message is
    delivered and who can read it, so what the metadata says is used only once its signature over
    that metadata has been verified.
    """

    def test_unsigned_metadata_is_refused(self, rsa_parties:'TestParties') -> 'None':
        with pytest.raises(AS4Exception) as raised:
            _ = _lookup(SMP_Metadata, [rsa_parties.ca_certificate])

        assert 'not signed' in str(raised.value)

# ################################################################################################################################

    def test_metadata_signed_outside_the_network_is_refused(
        self,
        foreign_metadata:'bytes',
        rsa_parties:'TestParties',
        ) -> 'None':

        # Metadata signed with a certificate the network's anchor did not issue.
        with pytest.raises(AS4Exception) as raised:
            _ = _lookup(foreign_metadata, [rsa_parties.ca_certificate])

        assert 'signature did not verify' in str(raised.value)

# ################################################################################################################################

    def test_metadata_altered_after_signing_is_refused(self, signed_metadata:'bytes', rsa_parties:'TestParties') -> 'None':

        # The endpoint URL is what an alteration would aim at.
        altered = signed_metadata.replace(b'https://ap.example.com/as4', b'https://other.example.com/as4')

        with pytest.raises(AS4Exception) as raised:
            _ = _lookup(altered, [rsa_parties.ca_certificate])

        assert 'signature did not verify' in str(raised.value)

# ################################################################################################################################

    def test_metadata_is_refused_when_no_anchors_are_configured(self, signed_metadata:'bytes') -> 'None':
        with pytest.raises(AS4Exception) as raised:
            _ = _lookup(signed_metadata, [])

        assert 'No trust anchors' in str(raised.value)

# ################################################################################################################################
# ################################################################################################################################

class TestSMPScheme:

    def test_a_plain_http_smp_is_refused(self, signed_metadata:'bytes', rsa_parties:'TestParties') -> 'None':
        with pytest.raises(AS4Exception) as raised:
            _ = _lookup(signed_metadata, [rsa_parties.ca_certificate], smp_uri='http://smp.example.com')

        assert 'https' in str(raised.value)

# ################################################################################################################################

    def test_an_smp_uri_without_a_scheme_is_refused(self, signed_metadata:'bytes', rsa_parties:'TestParties') -> 'None':
        with pytest.raises(AS4Exception) as raised:
            _ = _lookup(signed_metadata, [rsa_parties.ca_certificate], smp_uri='smp.example.com')

        assert 'no scheme' in str(raised.value)

# ################################################################################################################################
# ################################################################################################################################
