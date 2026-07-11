# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.as4.common import AS4Exception
from zato.common.as4.discovery import lookup_endpoint, participant_dns_name, SML_Domain_Test, \
    Transport_Profile_Peppol_AS4

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The SMP metadata for one participant and document type, as a Peppol SMP would return it.
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

    def test_lookup_happy_path(self) -> 'None':
        urls_requested = []

        def naptr_lookup(dns_name:'any_') -> 'any_':
            assert dns_name.endswith(SML_Domain_Test)
            return ['https://smp.example.com']

        def http_get(url:'any_') -> 'any_':
            urls_requested.append(url)
            return SMP_Metadata

        endpoint = lookup_endpoint(
            'iso6523-actorid-upis',
            '0192:991825827',
            'busdox-docid-qns::urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
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

    def test_no_smp_in_dns_raises(self) -> 'None':
        def naptr_lookup(dns_name:'any_') -> 'any_':
            return []

        def http_get(url:'any_') -> 'any_':
            return b''

        with pytest.raises(AS4Exception):
            _ = lookup_endpoint(
                'iso6523-actorid-upis', '0192:991825827', 'doc-type',
                naptr_lookup=naptr_lookup, http_get=http_get,
            )

# ################################################################################################################################

    def test_no_matching_transport_profile_raises(self) -> 'None':
        def naptr_lookup(dns_name:'any_') -> 'any_':
            return ['https://smp.example.com']

        def http_get(url:'any_') -> 'any_':
            return SMP_Metadata

        with pytest.raises(AS4Exception):
            _ = lookup_endpoint(
                'iso6523-actorid-upis', '0192:991825827', 'doc-type',
                transport_profile='some-other-profile',
                naptr_lookup=naptr_lookup, http_get=http_get,
            )

# ################################################################################################################################
# ################################################################################################################################
