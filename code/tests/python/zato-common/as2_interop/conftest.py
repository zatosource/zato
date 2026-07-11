# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

# cryptography
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.hazmat.primitives.hashes import SHA1, SHA256
from cryptography.hazmat.primitives.serialization import PrivateFormat
from cryptography.hazmat.primitives.serialization.pkcs12 import PBES, PKCS12Certificate, serialize_key_and_certificates
from cryptography.x509 import BasicConstraints, CertificateBuilder, Name, NameAttribute, random_serial_number
from cryptography.x509.oid import NameOID

# pytest
import pytest

# Zato
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.as2.inbound import handle, InboundResult
from zato.common.as2.partnership import new_partnership
from zato.common.util.xml_.keystore import new_keystore

# live_as2
from live_as2.containers import ensure_image, extract_config_template, is_docker_available, restore_ownership, \
    start_openas2, stop_openas2, ModuleCtx as ContainerCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
    from cryptography.x509 import Certificate
    from zato.common.as2.partnership import Partnership, partnership_list
    from zato.common.typing_ import any_, strstrdict
    from zato.common.util.xml_.keystore import Keystore

    any_ = any_
    strstrdict = strstrdict

    strgen = Iterator[str]
    wiregen = Iterator['InteropWire']

# ################################################################################################################################
# ################################################################################################################################

inbound_result_list = list[InboundResult]

# ################################################################################################################################
# ################################################################################################################################

# The AS2 identities of the two sides - ours and the counterparty's.
our_identifier  = 'ZatoRetail'
peer_identifier = 'OpenAS2Peer'

# The keystore aliases the counterparty's partnerships refer to.
_our_alias  = 'zatoretail'
_peer_alias = 'openas2peer'

# The configuration template the image ships reads the keystore with this password.
_keystore_password = 'testas2'

# RSA parameters for throwaway test keys.
_rsa_public_exponent = 65537
_rsa_key_size = 2048

# ################################################################################################################################
# ################################################################################################################################

# The counterparty's trading configuration - one partnership per direction. The outgoing one polls
# its outbox directory and delivers to our listener on the host, requesting a signed synchronous MDN.
_partnerships_template = """<partnerships>
    <partner name="OpenAS2Peer" as2_id="OpenAS2Peer" x509_alias="openas2peer" email="edi@zatointerop.example.com"/>
    <partner name="ZatoRetail" as2_id="ZatoRetail" x509_alias="zatoretail" email="edi@zatointerop.example.com"/>

    <partnership name="ZatoRetail-to-OpenAS2Peer">
        <sender name="ZatoRetail"/>
        <receiver name="OpenAS2Peer"/>
        <attribute name="protocol" value="as2"/>
    </partnership>

    <partnership name="OpenAS2Peer-to-ZatoRetail">
        <sender name="OpenAS2Peer"/>
        <receiver name="ZatoRetail"/>
        <pollerConfig enabled="true"/>
        <attribute name="protocol" value="as2"/>
        <attribute name="content_transfer_encoding" value="binary"/>
        <attribute name="compression_type" value="ZLIB"/>
        <attribute name="subject" value="File $attributes.filename$ from $sender.name$ to $receiver.name$"/>
        <attribute name="as2_url" value="http://host.docker.internal:{listener_port}"/>
        <attribute name="as2_mdn_to" value="edi@zatointerop.example.com"/>
        <attribute name="as2_mdn_options"
            value="signed-receipt-protocol=optional, pkcs7-signature; signed-receipt-micalg=optional, $attribute.sign$"/>
        <attribute name="encrypt" value="AES256"/>
        <attribute name="sign" value="SHA-256"/>
        <attribute name="resend_max_retries" value="1"/>
    </partnership>
</partnerships>
"""

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def audit_db_env(tmp_path:'Path') -> 'strgen':
    """ Points the audit database at a per-test SQLite file, so the live send and receive
    pipelines record their audit events on an isolated database.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = db_path

    yield db_path

    _ = os.environ.pop(AuditLogCtx.Env_Type, None)
    _ = os.environ.pop(AuditLogCtx.Env_Name, None)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _Identity:
    """ One party's key with its self-signed certificate.
    """
    key: 'RSAPrivateKey'
    certificate: 'Certificate'

# ################################################################################################################################
# ################################################################################################################################

def _make_identity(common_name:'str') -> '_Identity':
    """ Issues a throwaway self-signed certificate valid around the current moment.
    """
    key = generate_private_key(_rsa_public_exponent, _rsa_key_size)
    name = Name([NameAttribute(NameOID.COMMON_NAME, common_name)])
    now = datetime.now(timezone.utc)

    builder = CertificateBuilder()
    builder = builder.subject_name(name)
    builder = builder.issuer_name(name)
    builder = builder.public_key(key.public_key())
    builder = builder.serial_number(random_serial_number())
    builder = builder.not_valid_before(now - timedelta(days=1))
    builder = builder.not_valid_after(now + timedelta(days=365))
    builder = builder.add_extension(BasicConstraints(ca=False, path_length=None), critical=True)

    certificate = builder.sign(key, SHA256())

    out = _Identity()
    out.key = key
    out.certificate = certificate

    return out

# ################################################################################################################################

def _write_keystore(path:'str', peer:'_Identity', ours:'_Identity') -> 'None':
    """ Writes the PKCS12 keystore the counterparty reads - its own key pair under one alias
    plus our certificate as a trusted entry under another.
    """
    password = _keystore_password.encode('ascii')

    # The counterparty runs on Java, whose keystore code reads this long-established
    # PKCS12 encryption everywhere - the modern default is not a given there.
    encryption_builder = PrivateFormat.PKCS12.encryption_builder()
    encryption_builder = encryption_builder.kdf_rounds(50_000)
    encryption_builder = encryption_builder.key_cert_algorithm(PBES.PBESv1SHA1And3KeyTripleDESCBC)
    encryption_builder = encryption_builder.hmac_hash(SHA1())
    encryption = encryption_builder.build(password)

    # Our certificate travels as a trusted entry whose friendly name is the alias
    # the counterparty's partnership configuration points at.
    alias = _our_alias.encode('ascii')
    trusted_entry = PKCS12Certificate(ours.certificate, alias)

    peer_alias = _peer_alias.encode('ascii')
    content = serialize_key_and_certificates(peer_alias, peer.key, peer.certificate, [trusted_entry], encryption)

    with open(path, 'wb') as file_:
        _ = file_.write(content)

# ################################################################################################################################
# ################################################################################################################################

class _InboundServer(ThreadingHTTPServer):
    """ The local HTTP listener our inbound pipeline runs behind - the counterparty
    delivers its messages here and receives our MDNs on the response.
    """
    daemon_threads = True

    partnerships: 'partnership_list'
    keystore: 'Keystore'
    results: 'inbound_result_list'

# ################################################################################################################################
# ################################################################################################################################

def _read_chunked(rfile:'any_') -> 'bytes':
    """ Reads a request body delivered with chunked transfer encoding.
    """
    body = bytearray()

    while True:

        # Each chunk announces its own size in hex ..
        size_line = rfile.readline().strip()
        size = int(size_line, 16)

        # .. a zero-sized chunk concludes the body ..
        if size == 0:
            _ = rfile.readline()
            break

        # .. and every other chunk carries data followed by its trailing CRLF.
        body += rfile.read(size)
        _ = rfile.readline()

    out = bytes(body)
    return out

# ################################################################################################################################
# ################################################################################################################################

class _InboundHandler(BaseHTTPRequestHandler):
    """ Passes every POST through the real inbound pipeline and answers with whatever it decided.
    """
    protocol_version = 'HTTP/1.1'

    server: '_InboundServer'

    def do_POST(self) -> 'None':

        # The peer chooses the framing, so both must be readable ..
        transfer_encoding = self.headers.get('Transfer-Encoding', '')

        if transfer_encoding.lower() == 'chunked':
            body = _read_chunked(self.rfile)
        else:
            length = int(self.headers['Content-Length'])
            body = self.rfile.read(length)

        # .. the pipeline expects plain header dicts ..
        headers:'strstrdict' = {}

        for name, value in self.headers.items():
            headers[name] = value

        # .. run the real inbound processing and remember what it decided ..
        result = handle(body, headers, self.server.partnerships, self.server.keystore)
        self.server.results.append(result)

        # .. and the MDN rides back on the HTTP response.
        self.send_response(result.status_code)

        for name, value in result.headers.items():
            self.send_header(name, value)

        body_length = len(result.body)
        self.send_header('Content-Length', str(body_length))
        self.end_headers()

        _ = self.wfile.write(result.body)

# ################################################################################################################################

    def log_message(self, format:'str', *args:'any_') -> 'None':
        """ The default implementation prints every request to stderr, which only obscures test output.
        """

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class InteropWire:
    """ Everything a test needs to exchange messages with the live counterparty -
    our side of the partnership, our keystore, the counterparty's storage directory
    on the host and everything our own listener decided so far.
    """
    partnership: 'Partnership'
    keystore: 'Keystore'
    data_dir: 'Path'
    results: 'inbound_result_list'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def wire() -> 'wiregen':
    """ Builds the whole interop rig once per session - certificates for both sides,
    the counterparty in docker with our partnership configuration mounted in
    and our own inbound listener the counterparty delivers to.
    """
    if not is_docker_available():
        pytest.skip('Docker is not available')

    ensure_image()

    # Each side runs with its own self-signed identity.
    peer = _make_identity('openas2-interop-peer')
    ours = _make_identity('zato-retail-interop')

    # Our keystore - we sign and decrypt with our key, the counterparty's certificate
    # verifies its signatures and receives our encryption.
    keystore = new_keystore()
    keystore.signing_key = ours.key
    keystore.signing_certificate_chain = [ours.certificate]
    keystore.decryption_key = ours.key
    keystore.peer_encryption_certificate = peer.certificate
    keystore.peer_signing_certificate = peer.certificate

    # Our side of the relationship - one partnership serves both directions.
    partnership = new_partnership()
    partnership.as2_from = our_identifier
    partnership.as2_to = peer_identifier
    partnership.endpoint_url = f'http://localhost:{ContainerCtx.Host_Receiver_Port}'
    partnership.compress = True

    # Our own listener starts first because the counterparty's configuration needs its port.
    results:'inbound_result_list' = []

    server = _InboundServer(('0.0.0.0', 0), _InboundHandler)
    server.partnerships = [partnership]
    server.keystore = keystore
    server.results = results

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    listener_port = server.server_address[1]

    # The counterparty runs with the pristine upstream configuration template,
    # overridden only in its partnerships and its keystore.
    config_dir = mkdtemp(prefix='zato-as2-interop-config-')
    data_dir = mkdtemp(prefix='zato-as2-interop-data-')

    extract_config_template(config_dir)

    partnerships_path = os.path.join(config_dir, 'partnerships.xml')
    partnerships = _partnerships_template.format(listener_port=listener_port)

    with open(partnerships_path, 'w') as file_:
        _ = file_.write(partnerships)

    keystore_path = os.path.join(config_dir, 'as2_certs.p12')
    _write_keystore(keystore_path, peer, ours)

    # The outbox its poller watches is named after the receiving side of its outgoing
    # partnership - us - and is pre-created so the host user can drop files into it.
    outbox_dir = os.path.join(data_dir, 'outbox', our_identifier)
    os.makedirs(outbox_dir)

    start_openas2(config_dir, data_dir)

    out = InteropWire()
    out.partnership = partnership
    out.keystore = keystore
    out.data_dir = Path(data_dir)
    out.results = results

    yield out

    stop_openas2()
    server.shutdown()

    # The container ran as root, so its files have to be handed back before removal.
    restore_ownership(config_dir)
    restore_ownership(data_dir)

    rmtree(config_dir, ignore_errors=True)
    rmtree(data_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
