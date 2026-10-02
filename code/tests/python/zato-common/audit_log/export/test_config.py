# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from unittest import TestCase

# Zato
from zato.common.audit_log.common import AuditSource
from zato.common.audit_log.export.api import AuditExport, ModuleCtx as APICtx
from zato.common.audit_log.export.config import get_export_config, is_compression_on, parse_pairs, ModuleCtx
from zato.common.audit_log.export.sender import sender_by_protocol, GRPCSender, HTTPSender

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# Every variable the export reads
_all_names = (
    ModuleCtx.Env_Endpoint,
    ModuleCtx.Env_Protocol,
    ModuleCtx.Env_Headers,
    ModuleCtx.Env_SSL_CA_File,
    ModuleCtx.Env_SSL_Cert_File,
    ModuleCtx.Env_SSL_Key_File,
    ModuleCtx.Env_SSL_Verify,
    ModuleCtx.Env_Timeout_Ms,
    ModuleCtx.Env_Batch_Size,
    ModuleCtx.Env_Max_Batch_Size,
    ModuleCtx.Env_Flush_Interval_Ms,
    ModuleCtx.Env_Queue_Size,
    ModuleCtx.Env_Compression,
    ModuleCtx.Env_Sources,
    ModuleCtx.Env_Environment,
    ModuleCtx.Env_Resource_Attributes,
    ModuleCtx.Env_Max_Payload_Size,
)

# The variables other OpenTelemetry tooling reads and the export never does
_otel_names = {
    'OTEL_EXPORTER_OTLP_ENDPOINT': 'https://other.example.com:4318',
    'OTEL_EXPORTER_OTLP_HEADERS': 'Authorization=Bearer other',
    'OTEL_EXPORTER_OTLP_PROTOCOL': 'grpc',
    'OTEL_RESOURCE_ATTRIBUTES': 'service.name=other,deployment.environment.name=other',
    'OTEL_SERVICE_NAME': 'other-service',
}

_endpoint = 'https://otel.example.com:4318'

# ################################################################################################################################
# ################################################################################################################################

class _EnvTestCase(TestCase):
    """ Clears the export's variables around each test and restores the environment afterwards.
    """

    def setUp(self) -> 'None':
        self.saved:'stranydict' = {}

        for name in _all_names + tuple(_otel_names):
            self.saved[name] = os.environ.pop(name, None)

    def tearDown(self) -> 'None':
        for name, value in self.saved.items():
            if value is None:
                _ = os.environ.pop(name, None)
            else:
                os.environ[name] = value

    def set_env(self, values:'strstrdict') -> 'None':
        for name, value in values.items():
            os.environ[name] = value

# ################################################################################################################################
# ################################################################################################################################

class TestNames(TestCase):

    def test_every_variable_follows_the_audit_log_naming(self) -> 'None':

        for name in _all_names:
            self.assertTrue(name.startswith('Zato_Audit_Log_Export_'), name)

        self.assertEqual(ModuleCtx.Env_Endpoint, 'Zato_Audit_Log_Export_Endpoint')
        self.assertEqual(ModuleCtx.Env_Protocol, 'Zato_Audit_Log_Export_Protocol')
        self.assertEqual(ModuleCtx.Env_Headers, 'Zato_Audit_Log_Export_Headers')
        self.assertEqual(ModuleCtx.Env_SSL_CA_File, 'Zato_Audit_Log_Export_SSL_CA_File')
        self.assertEqual(ModuleCtx.Env_SSL_Cert_File, 'Zato_Audit_Log_Export_SSL_Cert_File')
        self.assertEqual(ModuleCtx.Env_SSL_Key_File, 'Zato_Audit_Log_Export_SSL_Key_File')
        self.assertEqual(ModuleCtx.Env_SSL_Verify, 'Zato_Audit_Log_Export_SSL_Verify')
        self.assertEqual(ModuleCtx.Env_Timeout_Ms, 'Zato_Audit_Log_Export_Timeout_Ms')
        self.assertEqual(ModuleCtx.Env_Batch_Size, 'Zato_Audit_Log_Export_Batch_Size')
        self.assertEqual(ModuleCtx.Env_Max_Batch_Size, 'Zato_Audit_Log_Export_Max_Batch_Size')
        self.assertEqual(ModuleCtx.Env_Flush_Interval_Ms, 'Zato_Audit_Log_Export_Flush_Interval_Ms')
        self.assertEqual(ModuleCtx.Env_Queue_Size, 'Zato_Audit_Log_Export_Queue_Size')
        self.assertEqual(ModuleCtx.Env_Compression, 'Zato_Audit_Log_Export_Compression')
        self.assertEqual(ModuleCtx.Env_Sources, 'Zato_Audit_Log_Export_Sources')
        self.assertEqual(ModuleCtx.Env_Environment, 'Zato_Audit_Log_Export_Environment')
        self.assertEqual(ModuleCtx.Env_Resource_Attributes, 'Zato_Audit_Log_Export_Resource_Attributes')
        self.assertEqual(ModuleCtx.Env_Max_Payload_Size, 'Zato_Audit_Log_Export_Max_Payload_Size')

# ################################################################################################################################

    def test_protocol_values_are_the_otel_ones(self) -> 'None':

        self.assertEqual(ModuleCtx.Protocol_HTTP, 'http/protobuf')
        self.assertEqual(ModuleCtx.Protocol_GRPC, 'grpc')
        self.assertEqual(ModuleCtx.Compression_Gzip, 'gzip')
        self.assertEqual(ModuleCtx.Compression_None, 'none')

# ################################################################################################################################
# ################################################################################################################################

class TestDefaults(_EnvTestCase):

    def test_no_endpoint_means_no_export(self) -> 'None':

        self.assertIsNone(get_export_config())

        self.set_env({ModuleCtx.Env_Protocol: ModuleCtx.Protocol_GRPC, ModuleCtx.Env_Batch_Size: '5'})
        self.assertIsNone(get_export_config())

# ################################################################################################################################

    def test_every_default(self) -> 'None':

        self.set_env({ModuleCtx.Env_Endpoint: _endpoint})

        config = get_export_config()
        self.assertIsNotNone(config)

        if config:
            self.assertEqual(config.endpoint, _endpoint + '/v1/logs')
            self.assertEqual(config.protocol, ModuleCtx.Protocol_HTTP)
            self.assertEqual(config.headers, {})
            self.assertEqual(config.compression, ModuleCtx.Compression_Gzip)
            self.assertEqual(config.timeout_ms, 10000)

            self.assertEqual(config.ssl_ca_file, '')
            self.assertEqual(config.ssl_cert_file, '')
            self.assertEqual(config.ssl_key_file, '')
            self.assertIs(config.ssl_verify, True)

            self.assertEqual(config.batch_size, 64)
            self.assertEqual(config.max_batch_size, 1024)
            self.assertEqual(config.flush_interval_ms, 1000)
            self.assertEqual(config.queue_size, 20000)

            self.assertEqual(config.sources, set())
            self.assertEqual(config.max_payload_size, 65536)

            self.assertEqual(config.environment, '')
            self.assertEqual(config.resource_attributes, {})

            self.assertTrue(is_compression_on(config))

        # The defaults the module names are the ones that came out
        self.assertEqual(ModuleCtx.Default_Protocol, ModuleCtx.Protocol_HTTP)
        self.assertEqual(ModuleCtx.Default_Compression, ModuleCtx.Compression_Gzip)
        self.assertEqual(ModuleCtx.Default_Timeout_Ms, 10000)
        self.assertEqual(ModuleCtx.Default_Batch_Size, 64)
        self.assertEqual(ModuleCtx.Default_Max_Batch_Size, 1024)
        self.assertEqual(ModuleCtx.Default_Flush_Interval_Ms, 1000)
        self.assertEqual(ModuleCtx.Default_Queue_Size, 20000)
        self.assertEqual(ModuleCtx.Default_Max_Payload_Size, 65536)
        self.assertIs(ModuleCtx.Default_SSL_Verify, True)

# ################################################################################################################################

    def test_every_variable(self) -> 'None':

        self.set_env({
            ModuleCtx.Env_Endpoint: 'https://otel.example.com:4318/custom/logs',
            ModuleCtx.Env_Protocol: ModuleCtx.Protocol_HTTP,
            ModuleCtx.Env_Headers: 'Authorization=Bearer abc, X-Scope-OrgID = tenant-1',
            ModuleCtx.Env_SSL_CA_File: '/etc/ssl/ca.pem',
            ModuleCtx.Env_SSL_Cert_File: '/etc/ssl/client.pem',
            ModuleCtx.Env_SSL_Key_File: '/etc/ssl/client.key',
            ModuleCtx.Env_SSL_Verify: 'false',
            ModuleCtx.Env_Timeout_Ms: '2500',
            ModuleCtx.Env_Batch_Size: '32',
            ModuleCtx.Env_Max_Batch_Size: '256',
            ModuleCtx.Env_Flush_Interval_Ms: '750',
            ModuleCtx.Env_Queue_Size: '5000',
            ModuleCtx.Env_Compression: ModuleCtx.Compression_None,
            ModuleCtx.Env_Sources: 'mcp, rest-channel,rest-outgoing',
            ModuleCtx.Env_Environment: 'production',
            ModuleCtx.Env_Resource_Attributes: 'team=billing,region=eu-west-1',
            ModuleCtx.Env_Max_Payload_Size: '1024',
        })

        config = get_export_config()
        self.assertIsNotNone(config)

        if config:
            self.assertEqual(config.endpoint, 'https://otel.example.com:4318/custom/logs')
            self.assertEqual(config.protocol, ModuleCtx.Protocol_HTTP)
            self.assertEqual(config.headers, {'Authorization': 'Bearer abc', 'X-Scope-OrgID': 'tenant-1'})
            self.assertEqual(config.compression, ModuleCtx.Compression_None)
            self.assertEqual(config.timeout_ms, 2500)

            self.assertEqual(config.ssl_ca_file, '/etc/ssl/ca.pem')
            self.assertEqual(config.ssl_cert_file, '/etc/ssl/client.pem')
            self.assertEqual(config.ssl_key_file, '/etc/ssl/client.key')
            self.assertIs(config.ssl_verify, False)

            self.assertEqual(config.batch_size, 32)
            self.assertEqual(config.max_batch_size, 256)
            self.assertEqual(config.flush_interval_ms, 750)
            self.assertEqual(config.queue_size, 5000)

            self.assertEqual(config.sources, {AuditSource.MCP, AuditSource.REST_Channel, AuditSource.REST_Outgoing})
            self.assertEqual(config.max_payload_size, 1024)

            self.assertEqual(config.environment, 'production')
            self.assertEqual(config.resource_attributes, {'team': 'billing', 'region': 'eu-west-1'})

            self.assertFalse(is_compression_on(config))

# ################################################################################################################################
# ################################################################################################################################

class TestEndpoint(_EnvTestCase):

    def test_http_endpoint_without_a_path_gets_the_logs_path(self) -> 'None':

        for given, expected in (
            ('https://otel.example.com:4318', 'https://otel.example.com:4318/v1/logs'),
            ('https://otel.example.com:4318/', 'https://otel.example.com:4318/v1/logs'),
            ('http://localhost:4318', 'http://localhost:4318/v1/logs'),
        ):
            self.set_env({ModuleCtx.Env_Endpoint: given})
            config = get_export_config()

            if config:
                self.assertEqual(config.endpoint, expected, given)

# ################################################################################################################################

    def test_http_endpoint_with_a_path_is_used_as_given(self) -> 'None':

        for given in (
            'https://otel.example.com:4318/v1/logs',
            'https://ingest.example.com/otlp/v1/logs',
            'https://otel.example.com:4318/api/v2/otlp/v1/logs',
        ):
            self.set_env({ModuleCtx.Env_Endpoint: given})
            config = get_export_config()

            if config:
                self.assertEqual(config.endpoint, given, given)

# ################################################################################################################################

    def test_grpc_endpoint_is_never_changed(self) -> 'None':

        for given in ('https://otel.example.com:4317', 'http://localhost:4317', 'https://otel.example.com:4317/'):

            self.set_env({ModuleCtx.Env_Endpoint: given, ModuleCtx.Env_Protocol: ModuleCtx.Protocol_GRPC})
            config = get_export_config()

            if config:
                self.assertEqual(config.endpoint, given, given)
                self.assertEqual(config.protocol, ModuleCtx.Protocol_GRPC)

# ################################################################################################################################
# ################################################################################################################################

class TestRefusals(_EnvTestCase):

    def test_unknown_source(self) -> 'None':

        self.set_env({ModuleCtx.Env_Endpoint: _endpoint, ModuleCtx.Env_Sources: 'mcp,no-such-source'})

        with self.assertRaises(Exception) as ctx:
            _ = get_export_config()

        self.assertIn('no-such-source', str(ctx.exception))
        self.assertIn(ModuleCtx.Env_Sources, str(ctx.exception))

# ################################################################################################################################

    def test_every_known_source_is_accepted(self) -> 'None':

        names = []
        for name, value in vars(AuditSource).items():
            if name.startswith('_'):
                continue
            if isinstance(value, str):
                names.append(value)

        self.set_env({ModuleCtx.Env_Endpoint: _endpoint, ModuleCtx.Env_Sources: ','.join(names)})

        config = get_export_config()

        if config:
            self.assertEqual(config.sources, set(names))

# ################################################################################################################################

    def test_unknown_protocol(self) -> 'None':

        self.set_env({ModuleCtx.Env_Endpoint: _endpoint, ModuleCtx.Env_Protocol: 'http/json'})

        with self.assertRaises(Exception) as ctx:
            _ = get_export_config()

        self.assertIn('http/json', str(ctx.exception))

# ################################################################################################################################

    def test_unknown_compression(self) -> 'None':

        self.set_env({ModuleCtx.Env_Endpoint: _endpoint, ModuleCtx.Env_Compression: 'brotli'})

        with self.assertRaises(Exception) as ctx:
            _ = get_export_config()

        self.assertIn('brotli', str(ctx.exception))

# ################################################################################################################################

    def test_pair_without_a_value(self) -> 'None':

        with self.assertRaises(Exception) as ctx:
            _ = parse_pairs('Authorization')

        self.assertIn('Authorization', str(ctx.exception))

# ################################################################################################################################

    def test_pairs(self) -> 'None':

        self.assertEqual(parse_pairs(''), {})
        self.assertEqual(parse_pairs(' , '), {})
        self.assertEqual(parse_pairs('a=1'), {'a': '1'})
        self.assertEqual(parse_pairs(' a = 1 , b=x=y '), {'a': '1', 'b': 'x=y'})

# ################################################################################################################################
# ################################################################################################################################

class TestOTELVariables(_EnvTestCase):

    def test_otel_variables_change_nothing(self) -> 'None':

        self.set_env({ModuleCtx.Env_Endpoint: _endpoint, ModuleCtx.Env_Environment: 'production'})
        before = get_export_config()

        self.set_env(_otel_names)
        after = get_export_config()

        self.assertIsNotNone(before)
        self.assertIsNotNone(after)

        if before:
            if after:
                self.assertEqual(before, after)
                self.assertEqual(after.endpoint, _endpoint + '/v1/logs')
                self.assertEqual(after.headers, {})
                self.assertEqual(after.protocol, ModuleCtx.Protocol_HTTP)
                self.assertEqual(after.resource_attributes, {})

# ################################################################################################################################

    def test_otel_variables_do_not_turn_the_export_on(self) -> 'None':

        self.set_env(_otel_names)
        self.assertIsNone(get_export_config())

# ################################################################################################################################

    def test_resource_ignores_otel_variables(self) -> 'None':

        self.set_env({ModuleCtx.Env_Endpoint: _endpoint, ModuleCtx.Env_Environment: 'production'})
        self.set_env(_otel_names)

        config = get_export_config()
        self.assertIsNotNone(config)

        if config:
            export = AuditExport(config, service_name=APICtx.Service_Server, server_name='server1', cluster_name='cluster1',
                instance_id='deploy-1', version='4.1')

            attributes = {}
            for key_value in export.queue.resource.attributes:
                attributes[key_value.key] = key_value.value.string_value or key_value.value.int_value

            self.assertEqual(attributes['service.name'], APICtx.Service_Server)
            self.assertEqual(attributes['service.namespace'], 'cluster1')
            self.assertEqual(attributes['service.instance.id'], 'deploy-1')
            self.assertEqual(attributes['service.version'], '4.1')
            self.assertEqual(attributes['zato.server.name'], 'server1')
            self.assertEqual(attributes['zato.cluster.name'], 'cluster1')
            self.assertEqual(attributes['deployment.environment.name'], 'production')
            self.assertEqual(attributes['process.pid'], os.getpid())
            self.assertIn('host.name', attributes)

            self.assertNotIn('other-service', attributes.values())
            self.assertNotIn('other', attributes.values())

            export.queue.sender.close()

# ################################################################################################################################
# ################################################################################################################################

class TestSenders(_EnvTestCase):

    def test_http_protocol_builds_the_http_sender(self) -> 'None':

        self.set_env({
            ModuleCtx.Env_Endpoint: _endpoint,
            ModuleCtx.Env_Headers: 'Authorization=Bearer abc',
            ModuleCtx.Env_SSL_Verify: 'false',
        })

        config = get_export_config()

        if config:
            self.assertIs(sender_by_protocol[config.protocol], HTTPSender)

            sender = HTTPSender(config)

            self.assertEqual(sender.session.headers['Content-Type'], 'application/x-protobuf')
            self.assertEqual(sender.session.headers['Content-Encoding'], 'gzip')
            self.assertEqual(sender.session.headers['Authorization'], 'Bearer abc')
            self.assertIs(sender.session.verify, False)

            # What is prepared is gzip, what is sent is what was prepared
            body = sender.prepare(b'serialized-request')
            self.assertEqual(body[:2], b'\x1f\x8b')

            sender.close()

# ################################################################################################################################

    def test_http_sender_without_compression_and_with_a_ca_file(self) -> 'None':

        self.set_env({
            ModuleCtx.Env_Endpoint: _endpoint,
            ModuleCtx.Env_Compression: ModuleCtx.Compression_None,
            ModuleCtx.Env_SSL_CA_File: '/etc/ssl/ca.pem',
            ModuleCtx.Env_SSL_Cert_File: '/etc/ssl/client.pem',
            ModuleCtx.Env_SSL_Key_File: '/etc/ssl/client.key',
        })

        config = get_export_config()

        if config:
            sender = HTTPSender(config)

            self.assertNotIn('Content-Encoding', sender.session.headers)
            self.assertEqual(sender.session.verify, '/etc/ssl/ca.pem')
            self.assertEqual(sender.session.cert, ('/etc/ssl/client.pem', '/etc/ssl/client.key'))

            self.assertEqual(sender.prepare(b'serialized-request'), b'serialized-request')

            sender.close()

# ################################################################################################################################

    def test_grpc_protocol_builds_the_grpc_sender(self) -> 'None':

        self.set_env({
            ModuleCtx.Env_Endpoint: 'http://localhost:4317',
            ModuleCtx.Env_Protocol: ModuleCtx.Protocol_GRPC,
            ModuleCtx.Env_Headers: 'Authorization=Bearer abc',
        })

        config = get_export_config()

        if config:
            self.assertIs(sender_by_protocol[config.protocol], GRPCSender)

            sender = GRPCSender(config)

            self.assertIsNotNone(sender.channel)
            self.assertEqual(sender.metadata, [('authorization', 'Bearer abc')])
            self.assertEqual(sender.timeout, 10.0)
            self.assertEqual(sender.prepare(b'serialized-request'), b'serialized-request')

            sender.close()

# ################################################################################################################################

    def test_the_export_builds_its_sender_by_protocol(self) -> 'None':

        for protocol, sender_class in ((ModuleCtx.Protocol_HTTP, HTTPSender), (ModuleCtx.Protocol_GRPC, GRPCSender)):

            self.set_env({ModuleCtx.Env_Endpoint: 'http://localhost:4318', ModuleCtx.Env_Protocol: protocol})
            config = get_export_config()

            if config:
                export = AuditExport(config, service_name=APICtx.Service_Server, server_name='server1', cluster_name='',
                    instance_id='deploy-1', version='4.1')

                self.assertIsInstance(export.queue.sender, sender_class)
                self.assertEqual(export.queue.address, 'http://localhost:4318')

                export.queue.sender.close()

# ################################################################################################################################
# ################################################################################################################################
