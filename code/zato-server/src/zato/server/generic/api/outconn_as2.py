# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import ssl
from logging import getLogger
from traceback import format_exc
from urllib.parse import urlsplit

# httpx
import httpx

# typing-extensions
from typing_extensions import TypeAlias

# Zato
from zato.common.api import AS2
from zato.common.as2.audit import record_send_result
from zato.common.as2.common import AS2Exception
from zato.common.as2.config import build_keystore, build_partnership
from zato.common.as2.outbound import send as outbound_send, send_payload
from zato.common.as2.partnership import HTTPAuth
from zato.common.as2.reconcile import MDNReconciler
from zato.common.typing_ import cast_
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.outbound import SendResult
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import strnone
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer
    send_payload = send_payload
    SendResult = SendResult

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# What a service may hand over for delivery - one document, several of them, or a string
# that serializes itself, the way X12 and EDIFACT interchange objects do.
as2_payload:TypeAlias = 'str | send_payload'

# ################################################################################################################################
# ################################################################################################################################

# The TCP ports the ping handshake connects to when the endpoint URL does not name one.
_default_port_by_scheme = {
    'http':  80,
    'https': 443,
}

# How many seconds to wait for a pooled AS2 connection, which covers the window
# while the connection queue is still being built at startup.
_as2_block_timeout = 30

# ################################################################################################################################
# ################################################################################################################################

# Defaults applied by the config manager when the create path does not supply a field,
# e.g. when an outconn is created directly through zato.generic.connection.create.
outconn_as2_config_defaults:'dict[str, object]' = {

    # The AS2 identities and the partner's EDI addressing.
    'as2_from': '',
    'as2_to': '',
    'isa_qualifier': '',
    'isa_id': '',
    'gs_id': '',
    'unb_id': '',

    # Where outgoing messages go and how they travel.
    'endpoint_url': '',
    'sign_algorithm': '',
    'encryption_algorithm': '',
    'mdn_mode': '',
    'async_mdn_url': '',
    'subject': '',
    'content_type': '',
    'as2_version': '',
    'content_transfer_encoding': '',
    'http_transfer_mode': '',
    'inbound_topic': '',
    'inbound_service': '',

    # The security toggles, with the same defaults the partnership itself has.
    'sign': True,
    'encrypt': True,
    'compress': False,
    'compress_before_signing': True,
    'mdn_signed': True,
    'preserve_filename': False,
    'verify_tls': True,
    'force_base64': False,
    'prevent_canonicalization': False,
    'warn_on_duplicate_filename': False,

    # Whether this connection's exchanges are recorded in the audit log.
    'is_audit_log_active': True,

    # A zero means the partnership's own numeric default stays in place.
    'http_timeout_seconds': 0,
    'chunked_threshold_bytes': 0,
    'ack_overdue_after': 0,
    'resend_max_retries': 0,

    # The partner's certificate rotation fields, pasted as PEM.
    'as2_partner_cert': '',
    'as2_partner_next_cert': '',
    'as2_partner_next_cert_from': '',

    # Our own keystore material, pasted as PEM, with the private keys encrypted at rest.
    # The next-decryption pair keeps messages encrypted to our old certificate readable
    # while a rotation of our own key is under way.
    'as2_signing_key': '',
    'as2_signing_cert_chain': '',
    'as2_decryption_key': '',
    'as2_next_decryption_key': '',
    'as2_next_decryption_cert': '',
    'as2_peer_signing_cert': '',
    'as2_peer_encryption_cert': '',
    'as2_trust_anchors': '',

    # The connection queue fields - the secret is the HTTP basic authentication
    # password when a username is configured, changed through the Dashboard.
    'username': '',
    'secret': '',
    'pool_size': AS2.Default.Pool_Size,
}

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_as2_int_config_keys = ('http_timeout_seconds', 'chunked_threshold_bytes', 'ack_overdue_after',
    'resend_max_retries', 'pool_size')

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_as2_bool_config_keys = ('sign', 'encrypt', 'compress', 'compress_before_signing', 'mdn_signed',
    'preserve_filename', 'verify_tls', 'force_base64', 'prevent_canonicalization', 'warn_on_duplicate_filename',
    'is_audit_log_active')

# ################################################################################################################################
# ################################################################################################################################

class _AS2Connection:
    """ One pooled AS2 connection - the partnership and keystore of one trading relationship
    plus the HTTP client its messages are delivered over.
    """

    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        self.config = config
        self.name = config['name']

        # Audit events of this connection's exchanges are recorded under the server's name.
        self.server_name = server.name

        # The partnership is who the two parties are and how their messages are secured -
        # its certificate rotation lists are consulted per message, at send time,
        # so an activation date crossing takes effect without a pool rebuild ..
        self.partnership = build_partnership(config)

        # .. the keystore holds our own keys and the partner's certificates -
        # the private keys are decrypted only at this point ..
        self.keystore = build_keystore(config, server.decrypt)

        # .. and a username turns on HTTP basic authentication, with the connection's
        # own secret as the password, changed through the Dashboard.
        if username := config['username']:
            http_auth = HTTPAuth()
            http_auth.username = username
            http_auth.password = server.decrypt(config['secret'])
            self.partnership.http_auth = http_auth

        # One HTTP client is shared by all exchanges over this connection.
        self.http_client = httpx.Client(
            verify=self.partnership.verify_tls,
            timeout=self.partnership.http_timeout_seconds,
        )

# ################################################################################################################################

    def send(self, cid:'str', payload:'as2_payload', filename:'strnone'=None, *, needs_audit:'bool'=True) -> 'SendResult':
        """ Delivers one AS2 message to the partnership's endpoint and reconciles
        the synchronous MDN when one was requested. Every delivery is recorded
        in the audit log as non-repudiation evidence, unless the caller records
        the attempt itself, the way an operator resend does.
        """
        # A string payload serializes itself into bytes - X12 and EDIFACT objects arrive this way.
        if isinstance(payload, str):
            payload = payload.encode('utf8')

        # A connection whose audit log was turned off explicitly records no events either
        if needs_audit:
            needs_audit = self.partnership.is_audit_log_active

        logger.info('AS2 out -> %s; name:%s; cid:%s', self.partnership.endpoint_url, self.name, cid)

        out = outbound_send(self.partnership, self.keystore, payload, filename, client=self.http_client)

        # The delivery and its synchronous MDN, when one arrived, become audit events -
        # the clear payload is stored only for a single document, which is what
        # a later resend runs on, while the raw MIME preserves everything either way.
        if needs_audit:

            if isinstance(payload, bytes):
                clear_payload = payload.decode('utf8', 'replace')
            else:
                clear_payload = ''

            if filename is None:
                stored_filename = ''
            else:
                stored_filename = filename

            reconciler = MDNReconciler(self.server_name)

            record_send_result(
                reconciler,
                self.partnership.as2_from,
                self.partnership.as2_to,
                out,
                payload=clear_payload,
                filename=stored_filename,
                async_mdn_url=self.partnership.async_mdn_url,
                cid=cid,
            )

        # A delivery whose MDN did not reconcile is worth a warning in the log,
        # while the result itself carries everything the caller needs to react.
        if not out.is_ok:
            logger.warning('AS2 delivery not confirmed over `%s` (HTTP %d); message id:%s; cid:%s',
                self.name, out.http_status, out.message_id, cid)

        return out

# ################################################################################################################################

    def ping(self) -> 'None':
        """ Validates the endpoint without posting anything - a TCP connection
        plus, over HTTPS, the TLS handshake against the endpoint's certificate.
        """
        endpoint_url = self.partnership.endpoint_url

        if not endpoint_url:
            raise AS2Exception(f'No endpoint URL is configured for AS2 connection `{self.name}`')

        parts = urlsplit(endpoint_url)
        host = parts.hostname

        if not host:
            raise AS2Exception(f'No host in endpoint URL `{endpoint_url}` of AS2 connection `{self.name}`')

        # An explicit port wins over the scheme's default one.
        port = parts.port
        if not port:
            port = _default_port_by_scheme[parts.scheme]

        # Connect at the TCP level first ..
        connection = socket.create_connection((host, port), self.partnership.http_timeout_seconds)

        try:
            # .. and over HTTPS, run the TLS handshake too, verifying the endpoint's
            # certificate unless the partnership turns the verification off.
            if parts.scheme == 'https':

                context = ssl.create_default_context()

                if not self.partnership.verify_tls:
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE

                tls_connection = context.wrap_socket(connection, server_hostname=host)
                tls_connection.close()

        finally:
            connection.close()

# ################################################################################################################################

    def zato_delete_impl(self) -> 'None':
        self.http_client.close()

# ################################################################################################################################
# ################################################################################################################################

class OutconnAS2Wrapper(Wrapper):
    """ Wraps a queue of outgoing AS2 connections.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        config.auth_url = config['endpoint_url']
        super(OutconnAS2Wrapper, self).__init__(config, 'AS2', server)

# ################################################################################################################################

    def add_client(self) -> 'None':

        try:
            conn = _AS2Connection(self.config, self.server)
            _ = self.client.put_client(conn)

        # A genuinely broad boundary - building a connection parses user-pasted PEM material
        # and decrypts keys, and any failure here must not break the connection pool.
        except Exception:
            logger.warning('Caught an exception while adding an AS2 client (%s); e:`%s`',
                self.config['name'], format_exc())

# ################################################################################################################################

    def send(self, cid:'str', payload:'as2_payload', filename:'strnone'=None, *, needs_audit:'bool'=True) -> 'SendResult':
        """ Delivers one AS2 message through a pooled connection, blocking to cover
        the window while the connection queue is still being built at startup.
        """
        with self.client(should_block=True, block_timeout=_as2_block_timeout) as client:
            client = cast_('_AS2Connection', client)
            out = client.send(cid, payload, filename, needs_audit=needs_audit)

        return out

# ################################################################################################################################

    def ping(self) -> 'None':
        with self.client(should_block=True, block_timeout=_as2_block_timeout) as client:
            client = cast_('_AS2Connection', client)
            client.ping()

# ################################################################################################################################
# ################################################################################################################################
