# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from gzip import compress
from http.client import MULTIPLE_CHOICES, OK
from typing import Protocol
from urllib.parse import urlparse

# grpc
import grpc

# requests
from requests import Session

# OpenTelemetry
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceResponse

# Zato
from zato.common.audit_log.export.config import is_compression_on, ModuleCtx as ConfigCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.export.config import ExportConfig
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # What an OTLP request travels as over HTTP
    Content_Type = 'application/x-protobuf'
    Content_Encoding_Gzip = 'gzip'

    # How hard a batch is compressed
    Compress_Level = 6

    # The gRPC method of the OTLP logs service
    GRPC_Method = '/opentelemetry.proto.collector.logs.v1.LogsService/Export'

    # The scheme of a gRPC endpoint that is to use TLS
    GRPC_TLS_Scheme = 'https'

# ################################################################################################################################
# ################################################################################################################################

def _read_file(path:'str') -> 'bytes':
    """ Returns the contents of a certificate or key file.
    """
    with open(path, 'rb') as file_:
        out = file_.read()

    return out

# ################################################################################################################################

def _as_bytes(serialized:'bytes') -> 'bytes':
    """ Hands an already serialized request to gRPC as it is.
    """
    return serialized

# ################################################################################################################################
# ################################################################################################################################

class Sender(Protocol):
    """ What the queue expects of a sender - one prepared body per batch, one attempt per call and a clean close.
    """

    def prepare(self, serialized:'bytes') -> 'bytes':
        ...

    def send(self, body:'bytes') -> 'str':
        ...

    def close(self) -> 'None':
        ...

# ################################################################################################################################
# ################################################################################################################################

class HTTPSender:
    """ Posts serialized OTLP requests to a collector's HTTP endpoint.
    """
    def __init__(self, config:'ExportConfig') -> 'None':

        self.endpoint = config.endpoint
        self.timeout = config.timeout_ms / 1000
        self.is_compressed = is_compression_on(config)

        self.session = Session()
        self.session.headers['Content-Type'] = ModuleCtx.Content_Type

        if self.is_compressed:
            self.session.headers['Content-Encoding'] = ModuleCtx.Content_Encoding_Gzip

        self.session.headers.update(config.headers)

        # Verification is against the CA file if there is one, the system store otherwise, and off only when so configured ..
        if config.ssl_ca_file:
            self.session.verify = config.ssl_ca_file
        else:
            self.session.verify = config.ssl_verify

        # .. and a client certificate is presented when given.
        if config.ssl_cert_file:
            self.session.cert = (config.ssl_cert_file, config.ssl_key_file)

# ################################################################################################################################

    def prepare(self, serialized:'bytes') -> 'bytes':
        """ Turns a serialized request into the body that is posted, done once per batch however many times it is sent.
        """
        if self.is_compressed:
            out = compress(serialized, compresslevel=ModuleCtx.Compress_Level, mtime=0)
        else:
            out = serialized

        return out

# ################################################################################################################################

    def send(self, body:'bytes') -> 'str':
        """ Posts one body and returns why the collector did not accept it, or an empty string if it did.
        """
        try:
            response = self.session.post(self.endpoint, data=body, timeout=self.timeout)
        except Exception as e:
            out = str(e)
        else:
            status = response.status_code
            is_accepted = OK <= status < MULTIPLE_CHOICES

            if is_accepted:
                out = ''
            else:
                out = f'HTTP {status} {response.reason}'

        return out

# ################################################################################################################################

    def close(self) -> 'None':
        self.session.close()

# ################################################################################################################################
# ################################################################################################################################

class GRPCSender:
    """ Sends serialized OTLP requests to a collector's gRPC endpoint.
    """
    def __init__(self, config:'ExportConfig') -> 'None':

        self.timeout = config.timeout_ms / 1000

        parsed = urlparse(config.endpoint)
        target = f'{parsed.hostname}:{parsed.port}'

        if is_compression_on(config):
            self.compression = grpc.Compression.Gzip
        else:
            self.compression = grpc.Compression.NoCompression

        # Headers travel as call metadata, whose keys are lowercase ..
        self.metadata:'anylist' = []

        for key, value in config.headers.items():
            self.metadata.append((key.lower(), value))

        # .. the scheme decides whether the channel uses TLS ..
        if parsed.scheme == ModuleCtx.GRPC_TLS_Scheme:
            credentials = self._build_credentials(config)
            self.channel = grpc.secure_channel(target, credentials)
        else:
            self.channel = grpc.insecure_channel(target)

        # .. and the batch is handed over as the bytes it already is.
        self.export:'any_' = self.channel.unary_unary(
            ModuleCtx.GRPC_Method,
            request_serializer=_as_bytes,
            response_deserializer=ExportLogsServiceResponse.FromString,
        )

# ################################################################################################################################

    def _build_credentials(self, config:'ExportConfig') -> 'grpc.ChannelCredentials':
        """ Builds the TLS credentials of the channel from the configured files, the system store standing in for a CA file.
        """
        root_certificates = None
        private_key = None
        certificate_chain = None

        if config.ssl_ca_file:
            root_certificates = _read_file(config.ssl_ca_file)

        if config.ssl_cert_file:
            certificate_chain = _read_file(config.ssl_cert_file)
            private_key = _read_file(config.ssl_key_file)

        out = grpc.ssl_channel_credentials(
            root_certificates=root_certificates,
            private_key=private_key,
            certificate_chain=certificate_chain,
        )

        return out

# ################################################################################################################################

    def prepare(self, serialized:'bytes') -> 'bytes':
        """ The channel compresses on its own, so the serialized request is sent as it is.
        """
        return serialized

# ################################################################################################################################

    def send(self, body:'bytes') -> 'str':
        """ Sends one request and returns why the collector did not accept it, or an empty string if it did.
        """
        try:
            _ = self.export(body, timeout=self.timeout, metadata=self.metadata, compression=self.compression)
        except grpc.RpcError as e:
            out = f'{e.code().name} {e.details()}'
        else:
            out = ''

        return out

# ################################################################################################################################

    def close(self) -> 'None':
        self.channel.close()

# ################################################################################################################################
# ################################################################################################################################

# The sender of each protocol
sender_by_protocol = {
    ConfigCtx.Protocol_HTTP: HTTPSender,
    ConfigCtx.Protocol_GRPC: GRPCSender,
}

# ################################################################################################################################
# ################################################################################################################################
