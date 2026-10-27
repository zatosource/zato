# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from hashlib import new as new_hash
from io import BytesIO

# cryptography
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA1, SHA256

# lxml
from lxml.etree import ElementTree, SubElement

# Zato
from zato.common.b2b.ebms2.common import MSHService, new_party_id, NS
from zato.common.b2b.ebms2.header import parse_manifest, parse_message_header
from zato.common.b2b.ebms2.inbound import receive
from zato.common.b2b.ebms2.message import collect_elements, parse_envelope, serialize
from zato.common.b2b.ebms2.outbound import SendOptions
from zato.common.b2b.ebms2.packaging import normalize_content_id, package, Package, Payload, unpack
from zato.common.b2b.ebms2.signature import canonicalize_envelope, DigestAlgorithm, sign_envelope, SignatureAlgorithm, \
    XPath_Transform
from zato.common.b2b.ebms2.xml_ import eb_tag
from zato.common.test.b2b_cpa import new_settings
from zato.common.test.b2b_ebms2 import new_local_keys, resolve, send, Start_Time
from zato.common.typing_ import cast_
from zato.common.util.xml_.constants import Algorithm
from zato.common.util.xml_.core import qname
from zato.common.util.xml_.xmlsec import encode_base64

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
    from cryptography.x509 import Certificate
    from zato.common.b2b.ebms2.header import HeaderParty, MessageHeader
    from zato.common.b2b.ebms2.inbound import InboundResult
    from zato.common.b2b.ebms2.message import MessageElements
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    from zato.common.b2b.ebms2.packaging import payload_list
    from zato.common.test.b2b_cpa import AgreementSettings, PartySettings
    from zato.common.test.b2b_ebms2 import Exchange
    from zato.common.test.b2b_pki import TestParties, TestParty
    from zato.common.typing_ import any_, strlist, strstrdict
    any_ = any_
    RSAPublicKey = RSAPublicKey
    AgreementSettings = AgreementSettings
    Certificate = Certificate
    Exchange = Exchange
    HeaderParty = HeaderParty
    InboundResult = InboundResult
    MessageElements = MessageElements
    MessageHeader = MessageHeader
    OutboundMessage = OutboundMessage
    PartySettings = PartySettings
    payload_list = payload_list
    strlist = strlist
    strstrdict = strstrdict
    TestParties = TestParties
    TestParty = TestParty

# ################################################################################################################################
# ################################################################################################################################

strbytesdict = dict[str, bytes]

# The namespace of the extension elements of the fixtures.
Extension_Namespace = 'urn:zato:b2b:test:extension'

# The file name suffix of a fixture.
Fixture_Suffix = '.xml'

# The prefix the XPath filter of a signature may declare for the SOAP envelope namespace on ds:XPath itself.
Declared_XPath_Prefix = 'SOAP-ENV'

# The media type of a payload that a test does not give one to.
Default_Payload_Content_Type = 'application/xml'

_payload_template = '<Record xmlns="urn:zato:b2b:test:records"><Position>{}</Position></Record>'

_message_header_path = './/' + eb_tag('MessageHeader')
_manifest_path = './/' + eb_tag('Manifest')
_acknowledgment_path = './/' + eb_tag('Acknowledgment')

_ds_signed_info = qname(NS.DS, 'SignedInfo')
_ds_canonicalization_method = qname(NS.DS, 'CanonicalizationMethod')
_ds_signature_method = qname(NS.DS, 'SignatureMethod')
_ds_reference = qname(NS.DS, 'Reference')
_ds_transform = qname(NS.DS, 'Transform')
_ds_xpath = qname(NS.DS, 'XPath')
_ds_xpath_path = './/' + _ds_xpath
_ds_digest_method = qname(NS.DS, 'DigestMethod')
_ds_digest_value = qname(NS.DS, 'DigestValue')
_ds_signature_value = qname(NS.DS, 'SignatureValue')
_ds_key_info = qname(NS.DS, 'KeyInfo')
_ds_key_value = qname(NS.DS, 'KeyValue')
_ds_rsa_key_value = qname(NS.DS, 'RSAKeyValue')
_ds_modulus = qname(NS.DS, 'Modulus')
_ds_exponent = qname(NS.DS, 'Exponent')
_ds_x509_data = qname(NS.DS, 'X509Data')
_ds_x509_certificate = qname(NS.DS, 'X509Certificate')

# The hash each signature algorithm signs with.
_signature_hashes = {
    SignatureAlgorithm.RSA_SHA1:   SHA1,
    SignatureAlgorithm.RSA_SHA256: SHA256,
}

# The hashlib name of each digest algorithm.
_digest_names = {
    DigestAlgorithm.SHA1:   'sha1',
    DigestAlgorithm.SHA256: 'sha256',
}

# ################################################################################################################################
# ################################################################################################################################

class FixtureDirectory:
    """ The directory of the SOAP parts that the interoperability tests read.
    """
    def __init__(self, path:'str') -> 'None':
        self.path = path

    def names(self) -> 'strlist':
        """ Returns the file names of every fixture, in alphabetical order.
        """
        out:'strlist' = []

        names = os.listdir(self.path)

        for name in sorted(names):
            if name.endswith(Fixture_Suffix):
                out.append(name)

        return out

    def load(self, name:'str') -> 'bytes':
        path = os.path.join(self.path, name)

        with open(path, 'rb') as data_file:
            out = data_file.read()

        return out

# ################################################################################################################################
# ################################################################################################################################

def read_header(data:'bytes') -> 'MessageHeader':
    """ Returns the MessageHeader of a SOAP part.
    """
    envelope = parse_envelope(data)
    element = envelope.find(_message_header_path)

    out = parse_message_header(element)
    return out

# ################################################################################################################################

def _apply_party(settings:'PartySettings', party:'HeaderParty') -> 'None':
    """ Gives a party of an agreement the identifiers and the role that a message names it with.
    """
    first_party_id = party.party_ids[0]

    settings.party_id = first_party_id.value
    settings.party_id_type = first_party_id.id_type

    for party_id in party.party_ids[1:]:
        other_party_id = new_party_id(party_id.value, party_id.id_type)
        settings.other_party_ids.append(other_party_id)

    if party.role:
        settings.role = party.role

# ################################################################################################################################

def settings_for(parties:'TestParties', data:'bytes', *, is_answer:'bool'=False) -> 'AgreementSettings':
    """ Returns the settings of an unsigned agreement under which a SOAP part is exchanged. The From of a message
    is the sender of the agreement, unless the message answers one that the sender sent, in which case it is the receiver.
    """
    header = read_header(data)

    out = new_settings(parties, Start_Time)
    out.cpa_id = header.cpa_id
    out.is_signed = False

    if is_answer:
        _apply_party(out.receiver, header.from_party)
        _apply_party(out.sender, header.to_party)
    else:
        _apply_party(out.sender, header.from_party)
        _apply_party(out.receiver, header.to_party)

    # A business message names the service of the agreement, while a message service handler message
    # leaves the agreement with its default service.
    if header.service != MSHService.Service:
        out.service = header.service
        out.service_type = header.service_type
        out.action = header.action

    return out

# ################################################################################################################################
# ################################################################################################################################

def new_fixture_payload(content_id:'str', position:'int', content_type:'str'=Default_Payload_Content_Type) -> 'Payload':
    """ Returns a payload that a manifest reference names, with a body of its own.
    """
    body = _payload_template.format(position)

    out = Payload()
    out.content_id = content_id
    out.content_type = content_type
    out.data = body.encode('utf-8')

    return out

# ################################################################################################################################

def manifest_payloads(data:'bytes') -> 'payload_list':
    """ Returns one payload for each cid: reference of the manifest of a SOAP part, in manifest order.
    """
    out:'payload_list' = []

    envelope = parse_envelope(data)

    if (element := envelope.find(_manifest_path)) is not None:

        manifest = parse_manifest(element)

        for reference in manifest.references:
            if reference.href.startswith('cid:'):
                content_id = normalize_content_id(reference.href)
                position = len(out)
                payload = new_fixture_payload(content_id, position)
                out.append(payload)

    return out

# ################################################################################################################################

def package_message(data:'bytes', payloads:'payload_list | None'=None) -> 'Package':
    """ Returns a SOAP part with its payloads as the multipart/related message that travels over HTTP.
    The payloads are the ones its manifest names unless they are given.
    """
    if payloads is None:
        payloads = manifest_payloads(data)

    out = package(data, payloads)
    return out

# ################################################################################################################################

def receive_message(exchange:'Exchange', message:'Package') -> 'InboundResult':
    """ Passes a packaged message to the receiver of an exchange.
    """
    receiver = exchange.receiver

    out = receive(exchange.agreement, receiver.local_keys, message.headers, message.body, receiver.store, exchange.clock)
    return out

# ################################################################################################################################

def reply_package(result:'InboundResult') -> 'Package':
    """ Returns the signal a received message was answered with, asynchronously or in the HTTP response.
    """
    if async_signal := result.async_signal:
        out = async_signal.package
    else:
        out = Package()
        out.headers = result.response.headers
        out.body = result.response.body

    return out

# ################################################################################################################################

def reply_elements(result:'InboundResult') -> 'MessageElements':
    """ Returns the ebMS elements of the signal a received message was answered with.
    """
    package = reply_package(result)
    unpacked = unpack(package.headers, package.body)
    envelope = parse_envelope(unpacked.envelope)

    out = collect_elements(envelope)
    return out

# ################################################################################################################################

def outbound_answered(exchange:'Exchange', message_id:'str', action:'str'='') -> 'OutboundMessage':
    """ Returns the message of the sender that a signal of the receiver answers, under the MessageId the signal names.
    A Ping or a StatusRequest is a message service handler message, and any other action is a business one.
    """
    options = SendOptions()
    options.message_id = message_id

    if action:
        binding = resolve(exchange, action, is_msh=True)
        out = send(exchange, [], options, binding)
    else:
        out = send(exchange, None, options)

    return out

# ################################################################################################################################
# ################################################################################################################################

def sign_message(
    data:'bytes',
    payloads:'payload_list',
    party:'TestParty',
    signature_algorithm:'str'=SignatureAlgorithm.RSA_SHA256,
    digest_algorithm:'str'=DigestAlgorithm.SHA256,
    ) -> 'any_':
    """ Signs a SOAP part and its payloads with the key of a test party, and returns the envelope and the signature.
    """
    envelope = parse_envelope(data)
    local_keys = new_local_keys(party)

    signature = sign_envelope(envelope, payloads, local_keys, signature_algorithm, digest_algorithm)

    out = (envelope, signature)
    return out

# ################################################################################################################################

def signed_message(
    data:'bytes',
    payloads:'payload_list',
    party:'TestParty',
    signature_algorithm:'str'=SignatureAlgorithm.RSA_SHA256,
    digest_algorithm:'str'=DigestAlgorithm.SHA256,
    ) -> 'bytes':
    """ Returns a SOAP part signed with the key of a test party.
    """
    envelope, _ = sign_message(data, payloads, party, signature_algorithm, digest_algorithm)

    out = serialize(envelope)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _digest(data:'bytes', digest_algorithm:'str') -> 'str':
    hash_name = _digest_names[digest_algorithm]
    digest = new_hash(hash_name, data)
    digest_bytes = digest.digest()

    out = encode_base64(digest_bytes)
    return out

# ################################################################################################################################

def refresh_digests(envelope:'any_', signature:'any_', payloads:'payload_list') -> 'None':
    """ Recomputes the DigestValue of every reference of a signature that names the envelope or a payload,
    after the envelope or the transforms of a reference were changed.
    """
    data_by_uri:'strbytesdict' = {}

    for payload in payloads:
        payload_uri = f'cid:{payload.content_id}'
        data_by_uri[payload_uri] = payload.data

    signed_info = signature.find(_ds_signed_info)

    for reference in signed_info.iter(_ds_reference):

        uri = reference.get('URI')
        digest_method = reference.find(_ds_digest_method)
        digest_algorithm = digest_method.get('Algorithm')

        if uri == '':
            apply_xpath_filter = False
            for transform in reference.iter(_ds_transform):
                if transform.get('Algorithm') == XPath_Transform:
                    apply_xpath_filter = True
            data = canonicalize_envelope(envelope, signature, apply_xpath_filter=apply_xpath_filter)

        # A reference to a Content-ID that no payload has keeps the digest it was given.
        elif (data := data_by_uri.get(uri)) is None:
            continue

        digest_value = reference.find(_ds_digest_value)
        digest_value.text = _digest(data, digest_algorithm)

# ################################################################################################################################

def _canonicalize_signed_info(signed_info:'any_') -> 'bytes':
    """ Returns the SignedInfo of a signature in the canonical form its CanonicalizationMethod names.
    """
    canonicalization_method = signed_info.find(_ds_canonicalization_method)
    is_exclusive = canonicalization_method.get('Algorithm') == Algorithm.C14N_Exclusive

    buffer = BytesIO()
    tree = ElementTree(signed_info)
    tree.write_c14n(buffer, exclusive=is_exclusive, with_comments=False)

    out = buffer.getvalue()
    return out

# ################################################################################################################################

def sign_signed_info(signature:'any_', party:'TestParty') -> 'None':
    """ Recomputes the SignatureValue of a signature over its SignedInfo as it now stands.
    """
    signed_info = signature.find(_ds_signed_info)
    signature_method = signed_info.find(_ds_signature_method)
    signature_algorithm = signature_method.get('Algorithm')

    hash_class = _signature_hashes[signature_algorithm]
    hash_algorithm = hash_class()
    padding = PKCS1v15()

    canonical_signed_info = _canonicalize_signed_info(signed_info)
    signature_bytes = party.key.sign(canonical_signed_info, padding, hash_algorithm)

    signature_value = signature.find(_ds_signature_value)
    signature_value.text = encode_base64(signature_bytes)

# ################################################################################################################################
# ################################################################################################################################

def _encode_integer(value:'int') -> 'str':
    """ Returns an integer as the base64 of its big-endian octets, which is the ds:CryptoBinary form.
    """
    bit_length = value.bit_length()
    byte_length = (bit_length + 7) // 8
    octets = value.to_bytes(byte_length, 'big')

    out = encode_base64(octets)
    return out

# ################################################################################################################################

def add_key_value(signature:'any_', certificate:'Certificate', *, is_before_x509_data:'bool', has_modulus:'bool'=True) -> 'None':
    """ Adds a ds:KeyValue with the RSA key of a certificate to the KeyInfo of a signature, before or after its X509Data.
    """
    public_key = certificate.public_key()
    rsa_public_key = cast_('RSAPublicKey', public_key)
    public_numbers = rsa_public_key.public_numbers()

    key_info = signature.find(_ds_key_info)
    x509_data = key_info.find(_ds_x509_data)

    key_value = SubElement(key_info, _ds_key_value)
    rsa_key_value = SubElement(key_value, _ds_rsa_key_value)

    if has_modulus:
        modulus = SubElement(rsa_key_value, _ds_modulus)
        modulus.text = _encode_integer(public_numbers.n)

    exponent = SubElement(rsa_key_value, _ds_exponent)
    exponent.text = _encode_integer(public_numbers.e)

    if is_before_x509_data:
        x509_data.addprevious(key_value)

# ################################################################################################################################

def clear_x509_data(signature:'any_') -> 'None':
    """ Leaves the X509Data of a signature in place without any certificate in it.
    """
    key_info = signature.find(_ds_key_info)
    x509_data = key_info.find(_ds_x509_data)

    for certificate_element in x509_data.findall(_ds_x509_certificate):
        x509_data.remove(certificate_element)

# ################################################################################################################################

def declare_xpath_prefix(signature:'any_', prefix:'str'=Declared_XPath_Prefix, *, is_declared:'bool'=True) -> 'None':
    """ Writes the XPath filter of a signature with another prefix for the SOAP envelope namespace, declared on ds:XPath
    itself or not declared at all.
    """
    xpath = signature.find(_ds_xpath_path)
    transform = xpath.getparent()
    expression = xpath.text.replace('SOAP:actor', f'{prefix}:actor')

    if is_declared:
        nsmap = {prefix: NS.SOAP}
    else:
        nsmap = {}

    replacement = SubElement(transform, _ds_xpath, nsmap=nsmap)
    replacement.text = expression

    transform.remove(xpath)

# ################################################################################################################################

def remove_xpath_transform(signature:'any_') -> 'None':
    """ Leaves the reference to the envelope with the enveloped-signature and the canonicalization transforms only.
    """
    xpath = signature.find(_ds_xpath_path)
    transform = xpath.getparent()
    transforms = transform.getparent()

    transforms.remove(transform)

# ################################################################################################################################

def set_canonicalization(signature:'any_', algorithm:'str') -> 'None':
    signed_info = signature.find(_ds_signed_info)
    canonicalization_method = signed_info.find(_ds_canonicalization_method)
    canonicalization_method.set('Algorithm', algorithm)

# ################################################################################################################################

def retarget_reference(signature:'any_', uri:'str', new_uri:'str') -> 'None':
    """ Points a reference of a signature at another URI, leaving its digest as it was.
    """
    signed_info = signature.find(_ds_signed_info)

    for reference in signed_info.iter(_ds_reference):
        if reference.get('URI') == uri:
            reference.set('URI', new_uri)

# ################################################################################################################################
# ################################################################################################################################

def echo_digests(data:'bytes', sent_digests:'strstrdict') -> 'bytes':
    """ Fills the ds:Reference elements of the Acknowledgment of a SOAP part with the digests of the message it acknowledges,
    each one by its URI.
    """
    envelope = parse_envelope(data)
    acknowledgment = envelope.find(_acknowledgment_path)

    for reference in acknowledgment.iter(_ds_reference):
        uri = reference.get('URI')
        digest_value = reference.find(_ds_digest_value)
        digest_value.text = sent_digests[uri]

    out = serialize(envelope)
    return out

# ################################################################################################################################
# ################################################################################################################################
