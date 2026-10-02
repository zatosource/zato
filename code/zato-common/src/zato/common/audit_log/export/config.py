# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from urllib.parse import urlparse

# Zato
from zato.common.audit_log.common import AuditSource
from zato.common.util.api import as_bool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strset, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The environment variables configuring the export
    Env_Endpoint            = 'Zato_Audit_Log_Export_Endpoint'
    Env_Protocol            = 'Zato_Audit_Log_Export_Protocol'
    Env_Headers             = 'Zato_Audit_Log_Export_Headers'
    Env_SSL_CA_File         = 'Zato_Audit_Log_Export_SSL_CA_File'
    Env_SSL_Cert_File       = 'Zato_Audit_Log_Export_SSL_Cert_File'
    Env_SSL_Key_File        = 'Zato_Audit_Log_Export_SSL_Key_File'
    Env_SSL_Verify          = 'Zato_Audit_Log_Export_SSL_Verify'
    Env_Timeout_Ms          = 'Zato_Audit_Log_Export_Timeout_Ms'
    Env_Batch_Size          = 'Zato_Audit_Log_Export_Batch_Size'
    Env_Max_Batch_Size      = 'Zato_Audit_Log_Export_Max_Batch_Size'
    Env_Flush_Interval_Ms   = 'Zato_Audit_Log_Export_Flush_Interval_Ms'
    Env_Queue_Size          = 'Zato_Audit_Log_Export_Queue_Size'
    Env_Compression         = 'Zato_Audit_Log_Export_Compression'
    Env_Sources             = 'Zato_Audit_Log_Export_Sources'
    Env_Environment         = 'Zato_Audit_Log_Export_Environment'
    Env_Resource_Attributes = 'Zato_Audit_Log_Export_Resource_Attributes'
    Env_Max_Payload_Size    = 'Zato_Audit_Log_Export_Max_Payload_Size'

    # The protocols an endpoint can be reached over
    Protocol_HTTP = 'http/protobuf'
    Protocol_GRPC = 'grpc'

    # The compression a batch can travel with
    Compression_Gzip = 'gzip'
    Compression_None = 'none'

    # What is used when a variable is not set
    Default_Protocol          = Protocol_HTTP
    Default_SSL_Verify        = True
    Default_Timeout_Ms        = 10_000
    Default_Batch_Size        = 64
    Default_Max_Batch_Size    = 1024
    Default_Flush_Interval_Ms = 1000
    Default_Queue_Size        = 20_000
    Default_Compression       = Compression_Gzip
    Default_Max_Payload_Size  = 65_536

    # The path an HTTP endpoint given without one receives logs under
    HTTP_Logs_Path = '/v1/logs'

# ################################################################################################################################
# ################################################################################################################################

_all_protocols    = (ModuleCtx.Protocol_HTTP, ModuleCtx.Protocol_GRPC)
_all_compressions = (ModuleCtx.Compression_Gzip, ModuleCtx.Compression_None)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ExportConfig:

    # Where the records go and how
    endpoint:    str
    protocol:    str
    headers:     'strstrdict'
    compression: str
    timeout_ms:  int

    # TLS
    ssl_ca_file:   str
    ssl_cert_file: str
    ssl_key_file:  str
    ssl_verify:    bool

    # Batching and the queue
    batch_size:        int
    max_batch_size:    int
    flush_interval_ms: int
    queue_size:        int

    # What is exported
    sources:          'strset'
    max_payload_size: int

    # What the resource carries on top of the process identity
    environment:         str
    resource_attributes: 'strstrdict'

# ################################################################################################################################
# ################################################################################################################################

def get_all_sources() -> 'strset':
    """ Returns every source name the audit log knows.
    """
    out:'strset' = set()

    for name, value in vars(AuditSource).items():
        if name.startswith('_'):
            continue
        if isinstance(value, str):
            out.add(value)

    return out

# ################################################################################################################################

def _get_int(name:'str', default:'int') -> 'int':
    """ Returns an integer variable, or the default when it is not set.
    """
    if value := os.environ.get(name, ''):
        out = int(value)
    else:
        out = default

    return out

# ################################################################################################################################

def _get_str(name:'str', default:'str') -> 'str':
    """ Returns a string variable, or the default when it is not set.
    """
    if value := os.environ.get(name, ''):
        out = value
    else:
        out = default

    return out

# ################################################################################################################################

def _get_bool(name:'str', default:'bool') -> 'bool':
    """ Returns a boolean variable, or the default when it is not set.
    """
    if value := os.environ.get(name, ''):
        out = as_bool(value)
    else:
        out = default

    return out

# ################################################################################################################################

def parse_pairs(value:'str') -> 'strstrdict':
    """ Parses comma-separated key=value pairs, with whitespace around keys and values ignored.
    """
    out:'strstrdict' = {}

    for pair in value.split(','):

        pair = pair.strip()

        if not pair:
            continue

        if '=' not in pair:
            raise Exception(f'Expected a key=value pair, got `{pair}`')

        key, pair_value = pair.split('=', 1)
        out[key.strip()] = pair_value.strip()

    return out

# ################################################################################################################################

def _parse_sources(value:'str') -> 'strset':
    """ Parses the comma-separated list of sources to export, raising an exception for a name the audit log does not know.
    """
    out:'strset' = set()

    all_sources = get_all_sources()

    for name in value.split(','):

        name = name.strip()

        if not name:
            continue

        if name not in all_sources:
            raise Exception(f'Unknown audit log source in {ModuleCtx.Env_Sources}: `{name}`')

        out.add(name)

    return out

# ################################################################################################################################

def _build_endpoint(endpoint:'str', protocol:'str') -> 'str':
    """ Adds the logs path to an HTTP endpoint given without a path, and leaves anything else as it is.
    """
    if protocol != ModuleCtx.Protocol_HTTP:
        return endpoint

    parsed = urlparse(endpoint)

    if parsed.path in ('', '/'):
        out = endpoint.rstrip('/') + ModuleCtx.HTTP_Logs_Path
    else:
        out = endpoint

    return out

# ################################################################################################################################

def get_export_config() -> 'ExportConfig | None':
    """ Returns the export configuration from the environment, or None when no endpoint is set and the export is off.
    """

    # No endpoint means no export ..
    if not (endpoint := os.environ.get(ModuleCtx.Env_Endpoint, '')):
        return None

    # .. the protocol decides what the endpoint looks like ..
    protocol = _get_str(ModuleCtx.Env_Protocol, ModuleCtx.Default_Protocol)

    if protocol not in _all_protocols:
        raise Exception(f'Unknown protocol in {ModuleCtx.Env_Protocol}: `{protocol}`, must be one of `{_all_protocols}`')

    compression = _get_str(ModuleCtx.Env_Compression, ModuleCtx.Default_Compression)

    if compression not in _all_compressions:
        raise Exception(
            f'Unknown compression in {ModuleCtx.Env_Compression}: `{compression}`, must be one of `{_all_compressions}`')

    # .. and everything else comes from its own variable.
    out = ExportConfig()

    out.endpoint    = _build_endpoint(endpoint, protocol)
    out.protocol    = protocol
    out.headers     = parse_pairs(os.environ.get(ModuleCtx.Env_Headers, ''))
    out.compression = compression
    out.timeout_ms  = _get_int(ModuleCtx.Env_Timeout_Ms, ModuleCtx.Default_Timeout_Ms)

    out.ssl_ca_file   = os.environ.get(ModuleCtx.Env_SSL_CA_File, '')
    out.ssl_cert_file = os.environ.get(ModuleCtx.Env_SSL_Cert_File, '')
    out.ssl_key_file  = os.environ.get(ModuleCtx.Env_SSL_Key_File, '')
    out.ssl_verify    = _get_bool(ModuleCtx.Env_SSL_Verify, ModuleCtx.Default_SSL_Verify)

    out.batch_size        = _get_int(ModuleCtx.Env_Batch_Size, ModuleCtx.Default_Batch_Size)
    out.max_batch_size    = _get_int(ModuleCtx.Env_Max_Batch_Size, ModuleCtx.Default_Max_Batch_Size)
    out.flush_interval_ms = _get_int(ModuleCtx.Env_Flush_Interval_Ms, ModuleCtx.Default_Flush_Interval_Ms)
    out.queue_size        = _get_int(ModuleCtx.Env_Queue_Size, ModuleCtx.Default_Queue_Size)

    out.sources          = _parse_sources(os.environ.get(ModuleCtx.Env_Sources, ''))
    out.max_payload_size = _get_int(ModuleCtx.Env_Max_Payload_Size, ModuleCtx.Default_Max_Payload_Size)

    out.environment         = os.environ.get(ModuleCtx.Env_Environment, '')
    out.resource_attributes = parse_pairs(os.environ.get(ModuleCtx.Env_Resource_Attributes, ''))

    return out

# ################################################################################################################################

def is_compression_on(config:'ExportConfig') -> 'bool':
    """ Whether batches are compressed on their way to the collector.
    """
    out = config.compression == ModuleCtx.Compression_Gzip
    return out

# ################################################################################################################################
# ################################################################################################################################
