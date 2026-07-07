# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b32encode
from dataclasses import dataclass
from hashlib import sha256
from urllib.parse import quote

# httpx
import httpx

# lxml
from lxml import etree

# Zato
from zato.common.as4.common import AS4Exception
from zato.common.util.xml_.xmlsec import decode_base64

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callnone, strlist
    any_ = any_
    callnone = callnone
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The SML zones for the Peppol network - participants are found under these DNS domains.
SML_Domain_Production = 'edelivery.tech.ec.europa.eu'
SML_Domain_Test       = 'acc.edelivery.tech.ec.europa.eu'

# The DNS NAPTR service tag that marks an SMP record per the BDXL specification.
_naptr_service_meta_smp = 'Meta:SMP'

# The Peppol SMP publishing namespace.
_ns_smp = 'http://busdox.org/serviceMetadata/publishing/1.0/'

# The WS-Addressing namespace used for endpoint addresses inside SMP metadata.
_ns_wsa = 'http://www.w3.org/2005/08/addressing'

# The transport profile identifier of Peppol AS4.
Transport_Profile_Peppol_AS4 = 'peppol-transport-as4-v2_0'

# HTTP timeout for SMP metadata requests.
_http_timeout_seconds = 60

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class EndpointInfo:
    """ Where and how to reach one participant for one document type.
    """
    url: str = ''

    # The DER bytes of the certificate the endpoint will use, as published in the SMP.
    certificate_der: bytes = b''

    transport_profile: str = ''

# ################################################################################################################################
# ################################################################################################################################

def participant_dns_name(participant_scheme:'str', participant_id:'str', sml_domain:'str') -> 'str':
    """ Returns the DNS name under which a participant's SMP is published,
    following the BDXL naming scheme - a base32 SHA-256 hash of the lowercase identifier.
    """
    normalized = participant_id.lower().encode('utf-8')
    digest = sha256(normalized).digest()

    # BDXL uses unpadded lowercase base32.
    encoded = b32encode(digest).decode('ascii').rstrip('=').lower()

    out = f'{encoded}.{participant_scheme}.{sml_domain}'
    return out

# ################################################################################################################################

def _default_naptr_lookup(dns_name:'str') -> 'strlist':
    """ Resolves the NAPTR records of a DNS name into their replacement URIs,
    keeping only the SMP metadata records.
    """
    # Imported here so that fully offline callers, such as tests,
    # never need the resolver module at all.
    from dns.resolver import resolve

    out:'strlist' = []

    answer = resolve(dns_name, 'NAPTR')

    for record in answer:
        service = record.service.decode('ascii')

        if service == _naptr_service_meta_smp:

            # The regexp field has the form !^.*$!https://smp.example.com! - the URI
            # is the middle part between the delimiter characters.
            regexp = record.regexp.decode('ascii')
            delimiter = regexp[0]
            uri = regexp.split(delimiter)[2]
            out.append(uri)

    return out

# ################################################################################################################################

def _default_http_get(url:'str') -> 'bytes':
    """ Fetches SMP metadata over HTTP.
    """
    with httpx.Client(timeout=_http_timeout_seconds) as client:
        response = client.get(url)

    if not response.is_success:
        raise AS4Exception(f'SMP request to `{url}` failed with HTTP {response.status_code}')

    out = response.content
    return out

# ################################################################################################################################

def _parse_smp_metadata(data:'bytes', transport_profile:'str') -> 'EndpointInfo':
    """ Extracts the endpoint matching a transport profile from SMP service metadata.
    """
    root = etree.fromstring(data)

    # The metadata may or may not be wrapped in SignedServiceMetadata.
    for endpoint in root.iter(f'{{{_ns_smp}}}Endpoint'):

        if endpoint.get('transportProfile') != transport_profile:
            continue

        out = EndpointInfo()
        out.transport_profile = transport_profile

        # The address lives in a WS-Addressing EndpointReference.
        for address in endpoint.iter(f'{{{_ns_wsa}}}Address'):
            out.url = address.text or ''
            break

        certificate = endpoint.find(f'{{{_ns_smp}}}Certificate')
        if certificate is not None:
            out.certificate_der = decode_base64(certificate.text or '')

        return out

    raise AS4Exception(f'No endpoint with transport profile `{transport_profile}` found in SMP metadata')

# ################################################################################################################################

def lookup_endpoint(
    participant_scheme:'str',
    participant_id:'str',
    document_type:'str',
    sml_domain:'str'=SML_Domain_Production,
    transport_profile:'str'=Transport_Profile_Peppol_AS4,
    naptr_lookup:'callnone'=None,
    http_get:'callnone'=None,
    ) -> 'EndpointInfo':
    """ Discovers where to send documents for a participant: an SML DNS lookup
    finds their SMP, and the SMP's service metadata names the AS4 endpoint
    and its certificate for the given document type.

    The naptr_lookup and http_get callables exist so tests can run fully offline -
    production use leaves them empty and gets real DNS and HTTP.
    """
    if not naptr_lookup:
        naptr_lookup = _default_naptr_lookup

    if not http_get:
        http_get = _default_http_get

    # First find the participant's SMP through DNS ..
    dns_name = participant_dns_name(participant_scheme, participant_id, sml_domain)
    smp_uris = naptr_lookup(dns_name)

    if not smp_uris:
        raise AS4Exception(f'No SMP found in DNS for `{participant_scheme}::{participant_id}` under `{sml_domain}`')

    # .. then ask the SMP for the service metadata of this document type ..
    participant_part = quote(f'{participant_scheme}::{participant_id}', safe='')
    document_part = quote(document_type, safe='')

    metadata_url = f'{smp_uris[0]}/{participant_part}/services/{document_part}'
    metadata = http_get(metadata_url)

    # .. and read the AS4 endpoint out of it.
    out = _parse_smp_metadata(metadata, transport_profile)
    return out

# ################################################################################################################################
# ################################################################################################################################
