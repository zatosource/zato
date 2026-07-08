# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# lxml
from lxml import etree

# requests
import requests

# Zato
from zato.common.soap.addressing import add_addressing, AddressingInfo, parse_addressing
from zato.common.soap.common import Content_Type, SOAPVersion
from zato.common.soap.ebxml import build_message as build_ebxml_message, encrypt_payload, parse_message_header, sign_payload
from zato.common.soap.envelope import attach_body, build_envelope, get_security_header, parse_body, parse_envelope, \
    raise_for_fault, to_bytes
from zato.common.soap.message import SOAPMessage
from zato.common.soap.mtom import build_mtom, build_swa, parse_message, to_bytes_map
from zato.common.soap.security.wss import apply_wss, keystore_from_config
from zato.common.util.xml_.keystore import new_keystore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strnone
    from zato.common.util.xml_.keystore import Keystore
    from zato.common.util.xml_.mime_ import part_list
    any_ = any_
    anydict = anydict
    anylist = anylist
    Keystore = Keystore
    part_list = part_list
    stranydict = stranydict
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# The SOAPAction is carried differently by each SOAP version - a header in 1.1,
# a Content-Type parameter in 1.2.
_soap_action_header = 'SOAPAction'

# ################################################################################################################################
# ################################################################################################################################

class SOAPClient:
    """ A reusable SOAP client - one connection's worth of configuration in, dot-accessed
    messages out. It builds the operation from a SOAPMessage, injects whatever credentials,
    addressing and packaging the configuration calls for, sends the request over HTTP(S)
    with optional mutual TLS, and parses the reply back into a SOAPMessage.
    """
    def __init__(self, config:'stranydict') -> 'None':
        self.config = config

        self.address      = config['address']
        self.soap_version = config.get('soap_version', SOAPVersion.V12)
        self.soap_action  = config.get('soap_action', '')
        self.timeout      = float(config.get('timeout') or 0) or None
        self.content_type = config.get('content_type')
        self.ping_method  = config.get('ping_method', 'HEAD')

        # WS-Security, WS-Addressing, MTOM and body-credential injection are each optional.
        self.security         = config.get('security')
        self.use_ws_addressing = config.get('use_ws_addressing', False)
        self.use_mtom          = config.get('use_mtom', False)
        self.body_credentials  = config.get('body_credentials')

        self.session = requests.Session()

# ################################################################################################################################

    def _verify(self) -> 'any_':
        """ Returns what to pass to requests as its TLS verification - True to verify against
        the system trust store, False to skip it, or a path to a CA bundle to verify against.
        """
        out = self.config.get('validate_tls', True)
        return out

# ################################################################################################################################

    def _client_cert(self) -> 'any_':
        """ Returns what to pass to requests as the client certificate - a single PEM path holding
        both the certificate and its key, a (certificate, key) path pair, or None.
        """
        client_cert = self.config.get('tls_client_cert')

        if not client_cert:
            return None

        if client_key := self.config.get('tls_client_key'):
            out = (client_cert, client_key)
        else:
            out = client_cert

        return out

# ################################################################################################################################

    def _content_type(self) -> 'str':
        """ Returns the Content-Type of a bare envelope of the configured SOAP version.
        """
        if self.content_type:
            out = self.content_type
        else:
            out = Content_Type[self.soap_version]

        return out

# ################################################################################################################################

    def _inject_body_credentials(self, operation:'any_') -> 'None':
        """ Injects the configured credentials as child elements of the operation element -
        by default as its first children in mapping order, or at explicit 1-based positions.
        The elements inherit the operation's namespace, so they sit in the message like any
        other field, which is what body-authenticated endpoints such as CDC IIS require.
        """
        namespace = None
        if operation.tag.startswith('{'):
            namespace = operation.tag[1:].partition('}')[0]

        mappings = self.body_credentials.get('mappings') or [
            {'name': 'username', 'source': 'username'},
            {'name': 'password', 'source': 'password'},
        ]

        # Rows without a position prepend in mapping order, positioned rows slot in afterwards.
        default_rows = [row for row in mappings if not row.get('position')]
        positioned_rows = [row for row in mappings if row.get('position')]

        for offset, row in enumerate(default_rows):
            element = self._new_credential_element(row, namespace)
            operation.insert(offset, element)

        for row in sorted(positioned_rows, key=lambda row: row['position']):
            element = self._new_credential_element(row, namespace)
            operation.insert(row['position'] - 1, element)

# ################################################################################################################################

    def _new_credential_element(self, row:'anydict', namespace:'strnone') -> 'any_':
        """ Builds one credential element out of a mapping row and the configured credentials.
        """
        source = row.get('source') or row['name']
        value = self.body_credentials[source]

        if namespace:
            element = etree.Element(f'{{{namespace}}}{row["name"]}')
        else:
            element = etree.Element(row['name'])

        element.text = value

        return element

# ################################################################################################################################

    def _addressing_info(self) -> 'AddressingInfo':
        """ Builds the WS-Addressing headers an outgoing request needs - the Action defaults
        to the SOAPAction and the destination to the connection's address.
        """
        out = AddressingInfo()
        out.action = self.config.get('wsa_action') or self.soap_action
        out.to = self.config.get('wsa_to') or self.address
        out.reply_to = self.config.get('wsa_reply_to')

        return out

# ################################################################################################################################

    def _build_request(self, operation:'str', message:'SOAPMessage') -> 'any_':
        """ Builds the request body bytes and their Content-Type from a message - applying
        credential injection, WS-Security, WS-Addressing and MTOM packaging as configured.
        """
        envelope = build_envelope(self.soap_version)

        # MTOM turns bytes values into xop:Include references and collects their bytes as parts.
        xop_parts:'part_list | None' = [] if self.use_mtom else None

        operation_element = attach_body(envelope, message, operation, xop_parts=xop_parts)

        # Body credentials go in before signing so a signature covers the final body.
        if self.body_credentials:
            self._inject_body_credentials(operation_element)

        if self.security:
            apply_wss(envelope, self.security)

        if self.use_ws_addressing:
            add_addressing(envelope, self._addressing_info())

        envelope_bytes = to_bytes(envelope)

        # With parts collected, the request is an MTOM package, otherwise a bare envelope.
        if xop_parts:
            body, content_type = build_mtom(envelope_bytes, xop_parts, self.soap_version)
        else:
            body = envelope_bytes
            content_type = self._request_content_type()

        out = (body, content_type)
        return out

# ################################################################################################################################

    def _request_content_type(self) -> 'str':
        """ Returns the Content-Type for a bare-envelope request, carrying the SOAPAction
        as a parameter for SOAP 1.2 the way that version prescribes.
        """
        out = self._content_type()

        if self.soap_version == SOAPVersion.V12 and self.soap_action:
            out = f'{out}; action="{self.soap_action}"'

        return out

# ################################################################################################################################

    def _request_headers(self, content_type:'str') -> 'stranydict':
        """ Returns the request headers - the Content-Type plus a SOAPAction header for SOAP 1.1.
        """
        headers = {'Content-Type': content_type}

        # SOAP 1.1 carries the action in its own header, always quoted.
        if self.soap_version == SOAPVersion.V11:
            headers[_soap_action_header] = f'"{self.soap_action}"'

        return headers

# ################################################################################################################################

    def _post(self, body:'bytes', content_type:'str') -> 'any_':
        """ Sends one request and returns the raw requests response.
        """
        headers = self._request_headers(content_type)

        out = self.session.post(
            self.address,
            data=body,
            headers=headers,
            verify=self._verify(),
            cert=self._client_cert(),
            timeout=self.timeout,
        )

        return out

# ################################################################################################################################

    def _parse_response(self, response:'any_') -> 'SOAPMessage':
        """ Parses a raw response into a SOAPMessage, resolving MTOM parts, raising SOAP faults,
        and exposing the WS-Addressing headers and attachments as reserved attributes.
        """
        envelope_bytes, parts = parse_message(response.content, response.headers.get('Content-Type', ''))

        envelope = parse_envelope(envelope_bytes)

        # A fault surfaces as the one SOAPFault exception before anything else is read.
        raise_for_fault(envelope)

        parts_map = to_bytes_map(parts) if parts else None
        body = parse_body(envelope, parts_map)

        # The addressing headers and attachments ride along as reserved attributes a service may read.
        object.__setattr__(body, 'addressing', parse_addressing(envelope))
        object.__setattr__(body, 'attachments', parts)

        return body

# ################################################################################################################################

    def invoke(self, operation:'str', message:'SOAPMessage') -> 'SOAPMessage':
        """ Invokes a SOAP operation - builds the request from the message, sends it and returns
        the parsed response body. The operation name becomes the single child of soap:Body.
        """
        body, content_type = self._build_request(operation, message)

        logger.info('SOAP out -> %s %s; len=%d', operation, self.address, len(body))

        response = self._post(body, content_type)

        logger.info('SOAP out <- %s; %s len=%d', operation, response.status_code, len(response.content))

        out = self._parse_response(response)
        return out

# ################################################################################################################################

    def invoke_ebxml(
        self,
        info:'any_',
        parts:'part_list',
        sign:'bool'=False,
        encrypt:'bool'=False,
        ) -> 'any_':
        """ Sends an ebXML Message Service message - the envelope carries the message header
        and a manifest, the payloads travel as MIME parts, each optionally signed and encrypted
        for the recipient. Returns the parsed EbXMLInfo of the reply.
        """
        keystore = self._ebxml_keystore()

        # Each payload is signed first so the signature covers the plaintext, then encrypted.
        signatures = []
        encrypted_keys = []

        for part in parts:
            if sign:
                signatures.append(sign_payload(part, keystore))
            if encrypt:
                encrypted_keys.append(encrypt_payload(part, keystore))

        envelope = build_ebxml_message(info, parts)

        # Any payload signatures and wrapped keys travel in the security header.
        if signatures or encrypted_keys:
            self._add_ebxml_security(envelope, signatures, encrypted_keys)

        envelope_bytes = to_bytes(envelope)
        body, content_type = build_swa(envelope_bytes, parts, SOAPVersion.V11)

        response = self._post(body, content_type)

        response_envelope_bytes, _ = parse_message(response.content, response.headers.get('Content-Type', ''))
        response_envelope = parse_envelope(response_envelope_bytes)

        raise_for_fault(response_envelope)

        out = parse_message_header(response_envelope)
        return out

# ################################################################################################################################

    def _ebxml_keystore(self) -> 'Keystore':
        """ Returns the keystore an ebXML exchange uses - the WS-Security material of the
        connection when one is configured, otherwise an empty keystore.
        """
        if self.security:
            out = keystore_from_config(self.security)
        else:
            out = new_keystore()

        return out

# ################################################################################################################################

    def _add_ebxml_security(self, envelope:'any_', signatures:'anylist', encrypted_keys:'anylist') -> 'None':
        """ Places payload signatures and wrapped content keys in the message's security header.
        """
        security = get_security_header(envelope)

        for encrypted_key in encrypted_keys:
            security.append(encrypted_key)

        for signature in signatures:
            security.append(signature)

# ################################################################################################################################

    def ping(self) -> 'int':
        """ Pings the endpoint with the configured method and returns the HTTP status code.
        """
        response = self.session.request(
            self.ping_method,
            self.address,
            verify=self._verify(),
            cert=self._client_cert(),
            timeout=self.timeout,
        )

        out = response.status_code
        return out

# ################################################################################################################################

    def close(self) -> 'None':
        """ Releases the underlying HTTP session.
        """
        self.session.close()

# ################################################################################################################################
# ################################################################################################################################
